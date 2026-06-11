import openpyxl
import os
import time

# Importa utilitários compartilhados (re-exportando resource_path para compatibilidade com gui.py)
from src.utils.automation import StopExecution

# Importa serviços
from src.services.browser import fechar_navegador
from src.services.fgts_digital_site import consultar_fgts_digital_site
from src.utils.database_handler import DatabaseHandler

#---------------------------
# Função para consulta em lote (Orchestrator)
#---------------------------
def executar_consulta_em_lote(caminho_arquivo_xlsx, pasta_destino, tipo_consulta="Certidão SATE", check_stop_callback=None):

    #1: Leitura da fonte de dados (Excel ou MySQL)
    try:
        dados_empresas = []
        is_mysql = isinstance(caminho_arquivo_xlsx, dict)

        if is_mysql:
            print(f"🔌 Conectando ao MySQL (Umbler) para buscar empresas pendentes...")
            db = DatabaseHandler(caminho_arquivo_xlsx)
            
            # Define se deve filtrar por statusOnvio
            db_dados = db.obter_empresas_pendentes()
            
            for item in db_dados:
                cnpj = item['cnpj']
                nome = item.get('razao', 'Empresa via DB')
                codigo = item['codigo']
                carteira = item.get('carteira', '')
                
                # Para Onvio/FGTS, pegamos a competência do banco (competenciaInicial)
                competencia = item.get('competenciaInicial', '')
                vencimento = item.get('vencimentoGuia', '') # Pegamos o vencimento se existir
                total_base = item.get('totalBase', 0.0)
                
                # Armazenamos o ID da empresa para atualização posterior
                empresa_id = item['empresa_id']
                status_atual = item.get('status', 0)
                status_onvio = item.get('statusOnvio', '')  # Novo campo
                
                # Estrutura: [cnpj, nome, codigo, carteira, competencia, empresa_id, status_atual, total_base, vencimento, status_onvio]
                dados_empresas.append([str(cnpj), str(nome), str(codigo), carteira, str(competencia), empresa_id, status_atual, total_base, vencimento, status_onvio])
            
            print(f"✅ {len(dados_empresas)} empresas encontradas no MySQL.")

        else:
            if not caminho_arquivo_xlsx.endswith(".xlsx"):
                raise ValueError("Formato de arquivo inválido. Use .xlsx")
            
            wb = openpyxl.load_workbook(caminho_arquivo_xlsx, data_only=True)
            sheet = wb.active
            
            # Encontrar índices das colunas
            headers = {}
            for cell in sheet[1]:
                if cell.value:
                    headers[str(cell.value).upper()] = cell.column - 1
            
            if "CNPJ" not in headers:
                print("A coluna 'CNPJ' não foi encontrada na planilha.")
                return
                
            col_cnpj = headers["CNPJ"]
            col_nome = headers.get("NOME_EMPRESA")
            col_codigo = headers.get("CODIGO")
            col_competencia = headers.get("COMPETENCIA")
            col_carteira = headers.get("CARTEIRA")
            
            for row in sheet.iter_rows(min_row=2, values_only=True):
                cnpj = row[col_cnpj]
                if cnpj:
                    nome = row[col_nome] if col_nome is not None else "Sem Nome"
                    codigo = row[col_codigo] if col_codigo is not None else ""
                    carteira = row[col_carteira] if col_carteira is not None else ""
                    competencia = row[col_competencia] if col_competencia is not None else ""
                    
                    if carteira and str(carteira).strip():
                         carteira = str(carteira).strip()
                    else:
                         carteira = ""
                    
                    # Para Excel, o empresa_id e status são None (processa tudo), total_base e vencimento são 0/vazio, statusOnvio vazio
                    dados_empresas.append([str(cnpj), str(nome), str(codigo), carteira, str(competencia), None, None, 0.0, "", ""])

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Erro ao ler o arquivo: {e}")
        return
    
    #2: Criação da pasta de destino BASE (Se não existir)
    if not os.path.exists(pasta_destino):
        try:
            os.makedirs(pasta_destino)
            print(f"Pasta de destino base criada: {pasta_destino}")
        except Exception as e:
            print(f"Erro ao criar pasta base: {e}")
            return
    
    #3: Determinar função de consulta (Apenas FGTS Digital agora)
    if tipo_consulta == "FGTS Digital Site":
        funcao_consulta = consultar_fgts_digital_site
        print(f'📋 Tipo de consulta: FGTS Digital Site')
    else:
        print(f'⚠️ Selecione um tipo de consulta válido. (FGTS Digital Site suportado) ')
        return

    print(f"[DEBUG] executar_consulta_em_lote: tipo_consulta='{tipo_consulta}', funcao_consulta={funcao_consulta.__name__}")
    
    #4: Loop de Execução
    print(f'\n🚀 Iniciando processamento de {len(dados_empresas)} CNPJs...')
    
    # Variáveis para controle de troca de pasta
    ultima_pasta_usada = None
    
    # Controle para reiniciar navegador (Rate Limiting Federal)
    precisa_reabrir_navegador = False

    # FLAG: Controla se é a primeira vez que VAMOS REALMENTE executar uma consulta
    # (independente de quantos itens pulamos antes)
    primeira_execucao_efetiva = True

    # Controla se a parada foi solicitada

    for i, (cnpj, nome, codigo, carteira, competencia, empresa_id, status_v, total_base_esperado, vencimento, status_onvio) in enumerate(dados_empresas):
        # Verifica parada
        if check_stop_callback and check_stop_callback():
             print("\n🛑 Parada solicitada pelo usuário.")
             break

        # LÓGICA DE STATUS (MySQL Only)
        # Se for MySQL (empresa_id não é None) e o status não for 1 (Selecionado)
        if empresa_id is not None and status_v != 1:
             print(f"⏭️ Pulando {nome} (Status {status_v} - Não selecionado para consulta)")
             continue


        # Define a pasta de destino atual
        if carteira:
            pasta_destino_atual = os.path.join(pasta_destino, carteira)
        else:
            pasta_destino_atual = pasta_destino
            
        # Normaliza as barras para o padrão Windows
        pasta_destino_atual = pasta_destino_atual.replace("/", "\\")
            
        # Cria a subpasta se necessário
        if not os.path.exists(pasta_destino_atual):
            try:
                os.makedirs(pasta_destino_atual)
                print(f"Pasta de grupo criada: {pasta_destino_atual}")
            except Exception as e:
                print(f"Erro ao criar subpasta {carteira}: {e}")
                continue # Pula este CNPJ se não conseguir criar a pasta

        # Tratamento do CNPJ
        cnpj_limpo = ''.join(filter(str.isdigit, str(cnpj)))
        cnpj_limpo = cnpj_limpo.zfill(14)
        
        print(f"\n---------------------------------------------------")
        print(f"Processando {i+1}/{len(dados_empresas)}: {codigo} | {nome} | {carteira if carteira else '[Sem Carteira]'}")
        print(f"CNPJ: {cnpj_limpo}")
        print(f"---------------------------------------------------")

        # Define se deve abrir o navegador (Sempre no primeiro que entrar aqui, ou por flag de erro)
        abrir_navegador = primeira_execucao_efetiva or precisa_reabrir_navegador
        
        # Salva o estado para passar para a função. Se vamos abrir/reabrir o navegador,
        # deve ser tratado como a primeira execução daquela sessão (fazendo o login).
        flag_primeira = abrir_navegador

        # Consome as flags de abertura para os próximos itens
        if primeira_execucao_efetiva: primeira_execucao_efetiva = False
        if precisa_reabrir_navegador: precisa_reabrir_navegador = False
        
        # Verifica se é a primeira vez salvando NESTA pasta
        # Se mudou de pasta ou é a primeira execução global, o Windows Dialog pode precisar de redirecionamento.
        # Serviços como SATE usam 'primeira_pasta' para forçar Ctrl+L e colagem do caminho.
        if tipo_consulta == "Consulta Certidão Prefeitura MCP":
            primeira_pasta = abrir_navegador
        else:
            primeira_pasta = (pasta_destino_atual != ultima_pasta_usada)
        
        
        try:
            # FGTS Digital Site: passa empresa_id e db_config
            resultado = funcao_consulta(
                empresa_id=empresa_id,
                db_config=caminho_arquivo_xlsx if is_mysql else None,
                pasta_destino=pasta_destino_atual,
                abrir_navegador=abrir_navegador,
                primeira_pasta=primeira_pasta,
                check_stop_callback=check_stop_callback,
                tipo_consulta=tipo_consulta,
                caminho_xlsx=caminho_arquivo_xlsx,
                empresa_id_db=empresa_id,
                total_base_esperado=total_base_esperado,
                primeira_execucao_efetiva=flag_primeira
            )

            
            # Se o serviço retornou (sucesso ou falha controlada), atualizamos a referência da pasta
            if resultado:
                 ultima_pasta_usada = pasta_destino_atual
                 
        except StopExecution:
            print("\n🛑 Execução interrompida.")
            break
        except Exception as e:
            print(f"🔴 Erro ao processar CNPJ {cnpj}: {e}")
            
            # Se houve erro, aguarda 5 segundos e fecha o navegador para garantir
            # que a próxima consulta recomece do zero (login).
            print(f"⏳ Aguardando 5 segundos antes de fechar o navegador devido ao erro...")
            time.sleep(5)
            fechar_navegador()
            
            # Forçamos reabertura no próximo item.
            precisa_reabrir_navegador = True
            
    # Ao final do loop
    print("\n🏁 Processamento concluído.")


#---------------------------
# Função para consulta INDIVIDUAL
#---------------------------
def executar_consulta_individual(cnpj, nome, codigo, pasta_destino, competencia="", carteira="", tipo_consulta="Certidão SATE", check_stop_callback=None):
    
    # 1. Determinar função
    if tipo_consulta == "FGTS Digital Site":
        funcao_consulta = consultar_fgts_digital_site
    else:
        print(f'⚠️ Tipo de consulta inválido: {tipo_consulta}')
        return

    # 2. Definir e Criar pasta de destino (com lógica de grupo)
    if carteira and str(carteira).strip():
        pasta_destino_atual = os.path.join(pasta_destino, str(carteira).strip())
    else:
        pasta_destino_atual = pasta_destino

    # Normaliza as barras para o padrão Windows
    pasta_destino_atual = pasta_destino_atual.replace("/", "\\")

    if not os.path.exists(pasta_destino_atual):
        try:
            os.makedirs(pasta_destino_atual)
            print(f"Pasta criada: {pasta_destino_atual}")
        except Exception as e:
            print(f"Erro ao criar pasta: {e}")
            return

    # 3. Preparar dados
    # Remove caracteres não numéricos
    cnpj_limpo = ''.join(filter(str.isdigit, str(cnpj)))
    cnpj_limpo = cnpj_limpo.zfill(14)
    
    print(f"\n🚀 Iniciando CONSULTA INDIVIDUAL: {cnpj_limpo} / {nome}")
    print(f"📂 Pasta de destino: {pasta_destino_atual}")
    
    try:
        # Sempre abre o navegador e sempre considera "primeira pasta" (para navegar até ela)
        resultado = funcao_consulta(
            cnpj=cnpj_limpo, 
            nome_empresa=nome, 
            codigo=codigo,
            competencia=competencia,
            pasta_destino=pasta_destino_atual, 
            abrir_navegador=True, 
            primeira_pasta=True, 
            check_stop_callback=check_stop_callback,
            tipo_consulta=tipo_consulta,
            caminho_xlsx=None # Para individual, geralmente não passamos DB por enquanto, mas se for necessário, deveria vir do contexto
        )
        
        if resultado:
             print(f"🟢 Consulta Individual realizada com sucesso!")
        else:
             print(f"⚠️ Consulta finalizada, mas sem confirmação de sucesso.")

    except StopExecution:
        print("\n🛑 Execução interrompida pelo usuário.")
    except Exception as e:
        print(f"🔴 Erro na consulta individual: {e}")
    finally:
        # Sempre fecha o navegador ao final da consulta individual
        print("🔒 Fechando navegador comentado para manter o sistema aberto...")
        # try:
        #     pyautogui.hotkey("alt", "f4")
        #     time.sleep(1)
        # except: pass
