import pyautogui
import time
import pyperclip
import os
import re
import datetime
from src.utils.automation import resource_path, localizar_imagem, verificar_parada, esperar, StopExecution
from src.services.browser import abrir_navegador_e_pagina, voltar_para_pagina_inicial   
from src.utils.excel_handler import salvar_dados_detalhados, atualizar_valor_guia_original, marcar_guia_nao_encontrada, marcar_status_validacao
from src.utils.database_handler import DatabaseHandler

def localizar_btn_entrar_gov():
    return localizar_imagem(resource_path("src/assets/site/btn_entrar_gov.png"), confianca=0.7)

def localizar_btn_entrar_certificado():
    return localizar_imagem(resource_path("src/assets/site/login_certificado.png"), confianca=0.7)   

def localizar_label_perfil():   
    return localizar_imagem(resource_path("src/assets/site/label_perfil.png"), confianca=0.7)

def localizar_input_cnpj():
    return localizar_imagem(resource_path("src/assets/site/input_cnpj.png"), confianca=0.7)

def localizar_btn_definir():
    return localizar_imagem(resource_path("src/assets/site/btn_definir.png"), confianca=0.7)  

def localizar_guia_parametrizada():
    return localizar_imagem(resource_path("src/assets/site/guia_parametrizada.png"), confianca=0.7)

def localizar_gestao_guias():
    return localizar_imagem(resource_path("src/assets/site/gestao_guias.png"), confianca=0.7)

def localizar_btn_aceitar_cookies():
    return localizar_imagem(resource_path("src/assets/site/btn_aceitar_cookies.png"), confianca=0.7)

def localizar_competencia_inicial():
    return localizar_imagem(resource_path("src/assets/site/competencia_inicial.png"), confianca=0.7) 

def localizar_competencia_final():
    return localizar_imagem(resource_path("src/assets/site/competencia_final.png"), confianca=0.7) 

def localizar_vencimento_debito():
    return localizar_imagem(resource_path("src/assets/site/vencimento_debito.png"), confianca=0.7) 

def localizar_parametros():
    return localizar_imagem(resource_path("src/assets/site/parametros.png"), confianca=0.7) 

def localizar_itens_para_guia():
    return localizar_imagem(resource_path("src/assets/site/itens_para_guia.png"), confianca=0.7)

def localizar_btn_pesquisar():
    return localizar_imagem(resource_path("src/assets/site/btn_pesquisar.png"), confianca=0.7)

def localizar_adicionar_a_guia():
    return localizar_imagem(resource_path("src/assets/site/btn_adicionar_a_guia.png"), confianca=0.7)

def localizar_btn_avancar(deve_quebrar=True):
    return localizar_imagem(resource_path("src/assets/site/btn_avancar.png"), tentativas=2, confianca=0.7, deve_quebrar=deve_quebrar)

def localizar_resumo_guia():
    return localizar_imagem(resource_path("src/assets/site/resumo_guia.png"), confianca=0.7)

def localizar_btn_emitir(deve_quebrar=True):
    return localizar_imagem(resource_path("src/assets/site/btn_emitir.png"),tentativas=3, confianca=0.7, deve_quebrar=deve_quebrar)

def localizar_pdf_existe(deve_quebrar=True):
    return localizar_imagem(resource_path("src/assets/arquivo/pdf_existe.png"), confianca=0.7, deve_quebrar=deve_quebrar)

def localizar_btn_fgts_digital():
    return localizar_imagem(resource_path("src/assets/site/btn_fgts_digital.png"), confianca=0.7)

def localizar_btn_trocar_perfil():
    return localizar_imagem(resource_path("src/assets/site/btn_trocar_perfil.png"), confianca=0.7)

def localizar_label_perfil2():
    return localizar_imagem(resource_path("src/assets/site/label_perfil2.png"), confianca=0.7)

def localizar_confirmar_sobreescrever():
    return localizar_imagem(resource_path("src/assets/arquivo/confirmar_sobreescrever.png"), confianca=0.7)

def localizar_alerta_item_nao_encontrado():
    return localizar_imagem(resource_path("src/assets/site/alerta_item_nao_encontrado.png"), tentativas=4, confianca=0.7, deve_quebrar=False)

def localizar_alerta_sem_consignado():
    return localizar_imagem(resource_path("src/assets/site/alerta_sem_consignado.png"), tentativas=5, confianca=0.7, deve_quebrar=False)

def localizar_desmarcar_sem_guia_emitida():
    return localizar_imagem(resource_path("src/assets/site/desmarcar_sem_guia_emitida.png"), confianca=0.7, deve_quebrar=False)

def localizar_data_vencimento():
    return localizar_imagem(resource_path("src/assets/site/vencimento_debito.png"), confianca=0.7, deve_quebrar=False)

def localizar_data_pagamento():
    # Usando vencimento como base ou fallback se não houver um binário específico
    return localizar_imagem(resource_path("src/assets/site/vencimento_debito.png"), confianca=0.7, deve_quebrar=False)

def localizar_itens_consignado():
    return localizar_imagem(resource_path("src/assets/site/itens_consignado.png"), confianca=0.7, deve_quebrar=False)

def localizar_competencia_inicial_consignado():
    return localizar_imagem(resource_path("src/assets/site/competencia_inicial_consignado.png"), confianca=0.7, deve_quebrar=False)

def localizar_competencia_final_consignado():
    return localizar_imagem(resource_path("src/assets/site/competencia_final_consignado.png"), confianca=0.7, deve_quebrar=False)

def localizar_quadro_competencia():
    return localizar_imagem(resource_path("src/assets/site/quadro_competencia.png"), confianca=0.7, deve_quebrar=False)

def localizar_nao_ha_debitos():
    return localizar_imagem(resource_path("src/assets/site/nao_ha_debitos.png"),tentativas=5, confianca=0.7, deve_quebrar=False)

def localizar_btn_ajuda():
    return localizar_imagem(resource_path("src/assets/site/btn_ajuda.png"), confianca=0.7, deve_quebrar=False)

def localizar_quadro_competencia_consignado():
    return localizar_imagem(resource_path("src/assets/site/quadro_competencia_consignado.png"), confianca=0.7, deve_quebrar=False)

def localizar_quadro_competencia_13():
    return localizar_imagem(resource_path("src/assets/site/quadro_competencia_13.png"), confianca=0.7, deve_quebrar=False)

def extrair_dados_tabela_detalhada(check_stop_callback=None, alerta_ativo=False):
    """
    Copia o conteúdo da tela e extrai os dados da tabela detalhada usando Regex.
    Retorna uma tupla (lista_de_resultados, total_geral).
    Se alerta_ativo (sem consignado), usa o padrão de 8 colunas e busca "Total".
    Se não, usa o padrão de 9 colunas e busca "Total da Guia".
    """
    print(f"📋 Copiando dados da tela para extração (Modo: {'Sem Consignado' if alerta_ativo else 'Padrão - Com Consignado'})...")
    pyautogui.hotkey('ctrl', 'a')
    esperar(0.5, None)
    pyautogui.hotkey('ctrl', 'c')
    esperar(1, None)

    # Clicar no centro dinâmico da tela para desfazer seleção
    largura, altura = pyautogui.size()
    print(f"🖱️ Clicando no centro da tela ({largura//2}, {altura//2}) para desmarcar...")
    pyautogui.click(largura // 2, altura // 2)
    esperar(0.5, check_stop_callback)
    pyautogui.press('esc')
    esperar(1, check_stop_callback)
    
    texto = pyperclip.paste()
    if not texto:
        print("⚠️ Área de transferência vazia.")
        return [], 0.0

    print(f"📄 Tamanho do texto capturado: {len(texto)} caracteres.")
    
    # Normalizar para busca de valores
    texto_padronizado = texto.replace('.', '').replace(',', '.')
    
    # --- 1. Extração das Linhas (Individual) ---
    if alerta_ativo:
        # Padrão 8 colunas
        padrao_linhas = r'(\d{2}º?/\d{4})\s+(\d{2}/\d{2}/\d{4})\s+(\d+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)'
    else:
        # Padrão flexível: 9 colunas (Competência de Referência pode vir opcional ou vazia no texto)
        padrao_linhas = r'(\d{2}º?/\d{4})\s+(?:(\d{2}º?/\d{4})\s+)?(\d{2}/\d{2}/\d{4})\s+(\d+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)'
    
    matches = list(re.finditer(padrao_linhas, texto_padronizado))
    print(f"🔎 Encontradas {len(matches)} linhas de dados na tabela.")
    resultados = []

    for match in matches:
        if alerta_ativo:
            dados = {
                "Competencia Apuracao": match.group(1),
                "Vencimento": match.group(2),
                "Quantidade Trabalhadores": match.group(3),
                "Total Individual": match.group(8)
            }
        else:
            # No modo flexível, o grupo 2 (Ref) pode ser None. Os índices mantêm-se por parênteses.
            comp_apuracao = match.group(1)
            comp_referencia = match.group(2) if match.group(2) else "N/A"
            vencimento = match.group(3)
            qtd = match.group(4)
            total_ind = match.group(9)

            dados = {
                "Competencia Apuracao": comp_apuracao,
                "Competencia Referencia": comp_referencia,
                "Vencimento": vencimento,
                "Quantidade Trabalhadores": qtd,
                "Total Individual": total_ind
            }
        resultados.append(dados)
    
    # --- 2. Extração de Valores Consolidados (Resumo) ---
    resumo_valores = {
        'total_guia': 0.0,
        'valor_fgts': 0.0,
        'valor_fgts13': 0.0,
        'valor_consignado': 0.0,
        'vencimento_guia': None
    }

    # Regex para buscar valores específicos no resumo
    # Buscamos por palavras-chave próximas aos valores
    padroes_resumo = {
        'total_guia': [r'Total da Guia\s+(?:R\$\s*)?([\d.]+)', r'Total a recolher\s+(?:R\$\s*)?([\d.]+)'],
        'valor_fgts': [r'FGTS\s+Mensal\s+(?:R\$\s*)?([\d.]+)', r'Valor\s+da\s+Guia\s+FGTS\s+(?:R\$\s*)?([\d.]+)', r'FGTS\s+Digital\s+Mensal\s+(?:R\$\s*)?([\d.]+)'],
        'valor_fgts13': [r'FGTS\s+13º\s+(?:R\$\s*)?([\d.]+)', r'Valor\s+da\s+Guia\s+FGTS\s+13º\s+(?:R\$\s*)?([\d.]+)', r'FGTS\s+Digital\s+13º\s+(?:R\$\s*)?([\d.]+)'],
        'valor_consignado': [r'Empr.stimo\s+Consignado\s+(?:R\$\s*)?([\d.]+)', r'(?:Valor\s+)?Consignado\s+(?:R\$\s*)?([\d.]+)', r'Empr.stimos\s+Consignados\s+(?:R\$\s*)?([\d.]+)']
    }

    for chave, lista_padroes in padroes_resumo.items():
        for p in lista_padroes:
            matches_resumo = list(re.finditer(p, texto_padronizado, re.IGNORECASE))
            if matches_resumo:
                ultimo_match = matches_resumo[-1]
                resumo_valores[chave] = float(ultimo_match.group(1))
                print(f"💰 {chave} detectado: {resumo_valores[chave]} (Padrão: {p})")
                break
    
    # --- 3. Extração da Data de Vencimento da Guia ---
    # No site aparece como "Vencimento da Guia: DD/MM/AAAA"
    padrao_vencimento = r'Vencimento\s+da\s+Guia:\s*(\d{2}/\d{2}/\d{4})'
    # Buscamos no texto original (sem remover pontos/vírgulas para garantir a data)
    match_vencimento = re.search(padrao_vencimento, texto, re.IGNORECASE)
    if match_vencimento:
        resumo_valores['vencimento_guia'] = match_vencimento.group(1)
        print(f"📅 Vencimento da Guia extraído: {resumo_valores['vencimento_guia']}")
    else:
        # Tenta no texto padronizado caso o regex acima falhe
        match_vencimento = re.search(padrao_vencimento, texto_padronizado, re.IGNORECASE)
        if match_vencimento:
            resumo_valores['vencimento_guia'] = match_vencimento.group(1)
            print(f"📅 Vencimento da Guia extraído (via texto padronizado): {resumo_valores['vencimento_guia']}")
    
    # Fallback para o total se os específicos não forem encontrados mas o total sim
    if resumo_valores['total_guia'] == 0.0:
        # Tenta um padrão mais genérico
        p_total = r'Total\s+(?:R\$\s*)?([\d.]+)'
        match_total = list(re.finditer(p_total, texto_padronizado, re.IGNORECASE))
        if match_total:
            resumo_valores['total_guia'] = float(match_total[-1].group(1))

    if resumo_valores['total_guia'] == 0.0:
        print("❌ Erro: Não foi possível localizar o Valor Total no texto capturado.")
        print(f"🔎 Fragmento final do texto: {texto_padronizado[-500:]}")

    return resultados, resumo_valores

def extrair_data_pagamento_guia(check_stop_callback=None):
    """
    Copia o conteúdo da tela da guia emitida e extrai a data de vencimento.
    Busca pelo texto 'Pagar este documento até' seguido de uma data.
    """
    print("📅 Extraindo data de pagamento do documento...")
    # duplo click na tela 
    pyautogui.doubleClick()
    esperar(0.5, None)

    pyautogui.hotkey('ctrl', 'a')
    esperar(0.5, None)
    pyautogui.hotkey('ctrl', 'c')
    esperar(1, None)

    # Clicar no centro para desmarcar
    largura, altura = pyautogui.size()
    pyautogui.click(largura // 2, altura // 2)
    esperar(0.5, check_stop_callback)

    texto = pyperclip.paste()
    if not texto:
        print("⚠️ Área de transferência vazia na extração da data.")
        return None

    # Regex para buscar "Pagar este documento até" seguido de data DD/MM/AAAA
    padrao_data = r'Pagar este documento até\s+(\d{2}/\d{2}/\d{4})'
    match = re.search(padrao_data, texto, re.IGNORECASE)

    if match:
        data_encontrada = match.group(1)
        print(f"✅ Data de pagamento extraída: {data_encontrada}")
        return data_encontrada
    else:
        print("❌ Não foi possível localizar a data de pagamento ('Pagar este documento até') no texto.")
        return None



def localizar_sem_debitos_consignados():
    return localizar_imagem(resource_path("src/assets/site/sem_debitos_consignados.png"), tentativas=10, confianca=0.7)

def consultar_fgts_digital_site(empresa_id, db_config, pasta_destino, abrir_navegador=False, primeira_pasta=False, check_stop_callback=None, tipo_consulta="FGTS Digital Site", caminho_xlsx=None, empresa_id_db=None, total_base_esperado=0.0, primeira_execucao_efetiva=True):
    """
    Realiza consulta FGTS Digital via site gov.br.
    Consulta o banco de dados para obter informações da empresa.
    Processa apenas empresas com status = 1 (Selecionado).
    """
    
    # Consultar banco de dados para obter informações da empresa
    if db_config is None or empresa_id is None:
        print("❌ Erro: db_config e empresa_id são obrigatórios")
        return False
    
    db = DatabaseHandler(db_config)
    if not db.connect():
        print("❌ Erro ao conectar ao banco de dados")
        return False
    
    try:
        cursor = db.connection.cursor(dictionary=True)
        query = """
            SELECT 
                e.codigo,
                e.cnpj,
                e.razao as nome_empresa,
                r.competenciaInicial,
                r.competenciaFinal,
                r.valorFgts,
                r.valorFgts13,
                r.valorConsignado,
                r.totalBase,
                r.status,
                r.vencimentoGuia
            FROM empresas e
            INNER JOIN roboFgts r ON r.empresaId = e.id
            WHERE e.id = %s AND r.status = 1
        """
        cursor.execute(query, (empresa_id,))
        empresa_data = cursor.fetchone()
        cursor.close()
        
        if not empresa_data:
            print(f"⏭️ Empresa ID {empresa_id} não está com status 1 (Selecionado) - pulando")
            return False
        
        # Extrair dados
        codigo = empresa_data['codigo']
        cnpj = empresa_data['cnpj']
        nome_empresa = empresa_data['nome_empresa']
        competencia = empresa_data['competenciaInicial']  # Usando apenas inicial por enquanto
        try:
            # Pegamos o valor da coluna totalBase do banco de dados (que deve bater com o FGTS da guia)
            total_base_esperado = float(empresa_data.get('totalBase') or 0)
        except ValueError:
            total_base_esperado = 0.0
        vencimentoGuia = empresa_data['vencimentoGuia']
        
        # ----------------------------------------------------
        # Normalização de Competência (Garantir String MM/AAAA)
        # ----------------------------------------------------
        # Se vier como objeto date/datetime
        if hasattr(competencia, 'strftime'):
            competencia = competencia.strftime('%m/%Y')
        # Se vier como string YYYY-MM-DD
        elif competencia and '-' in str(competencia):
            try:
                ano, mes, dia = str(competencia).split('-')
                competencia = f"{mes}/{ano}"
            except:
                pass # Mantém original se falhar
        # ----------------------------------------------------

        # Formatar vencimento se necessário (de YYYY-MM-DD para DD/MM/YYYY)
        if vencimentoGuia and '-' in str(vencimentoGuia):
            try:
                ano, mes, dia = str(vencimentoGuia).split('-')
                vencimentoGuia = f"{dia}/{mes}/{ano}"
            except:
                pass
        
        print(f"📊 Dados obtidos do banco:")
        print(f"   Código: {codigo}")
        print(f"   CNPJ: {cnpj}")
        print(f"   Nome: {nome_empresa}")
        print(f"   Competência Inicial: {empresa_data['competenciaInicial']}")
        print(f"   Competência Final: {empresa_data['competenciaFinal']}")
        print(f"   Total Base (DB): {empresa_data.get('totalBase')}")
        print(f"   Valor Consignado (DB): {empresa_data.get('valorConsignado')}")
        print(f"   Total Final Esperado: {total_base_esperado}")
        print(f"   Vencimento: {vencimentoGuia}")
        
    except Exception as e:
        print(f"❌ Erro ao consultar banco de dados: {e}")
        return False
    finally:
        db.disconnect()
    
    # Resto da função - continua com a automação usando as variáveis locais
    verificar_parada(check_stop_callback)
    print(f"\n🚀 Iniciando a consulta para o CNPJ: {cnpj}")

    # Preparar Navegador
    if abrir_navegador:
        abrir_navegador_e_pagina(tipo_consulta)
        verificar_parada(check_stop_callback)

        # Localiza o botão entrar com gov.br
        time.sleep(5)
        print("🔑 Localizando botão Entrar com gov.br...")
        pos_btn_entar_gov = localizar_btn_entrar_gov()
        pyautogui.click(pos_btn_entar_gov)
        esperar(9, check_stop_callback)
        verificar_parada(check_stop_callback)

        # Localiza o botão de login com certificado digital
        print("🔑 Localizando opção de login com Certificado Digital...")
        pos_entrar_certificado = localizar_btn_entrar_certificado()
        pyautogui.click(pos_entrar_certificado)
        
        esperar(9, check_stop_callback)
        verificar_parada(check_stop_callback)

        print("📝 Digitando o certificado digital...")
        pyautogui.write("MABIT CONTABILIDADE", interval=0.1)
        pyautogui.press("enter")
        esperar(4, check_stop_callback)
        verificar_parada(check_stop_callback)
         
        #   Importante aceitas os cookies
        print("🍪 Verificando cookies...")
        try:
            pos_btn_aceitar_cookies = localizar_btn_aceitar_cookies()
            pyautogui.click(pos_btn_aceitar_cookies)
            verificar_parada(check_stop_callback)
            time.sleep(3)
            pos_label_perfil = localizar_label_perfil()
            pyautogui.click(pos_label_perfil)
            esperar(3, check_stop_callback)
            pyautogui.press("down")
            pyautogui.press("enter")
            esperar(3, check_stop_callback)

            # Insere o CNPJ do cliente
            print(f"🏢 Inserindo CNPJ do cliente: {cnpj}")
            pos_input_cnpj = localizar_input_cnpj()
            pyautogui.click(pos_input_cnpj)
            time.sleep(3)
     
            pyautogui.write(cnpj, interval=0.1)
            verificar_parada(check_stop_callback)

            print(" Clicando em Definir para avançar...")
            # Localiza e clica no botão definir para prosseguir
            pos_btn_definir = localizar_btn_definir()
            pyautogui.click(pos_btn_definir)
            esperar(5, check_stop_callback)
            verificar_parada(check_stop_callback)

        except:
            print("ℹ️ Botão de cookies não encontrado ou já aceito.")
        print("👤 Trocando perfil para o CNPJ de procurado...")
        
    else:
        print("🔄 Reutilizando navegador e mantendo posição para próxima consulta.")
        verificar_parada(check_stop_callback)
    #   Localiza  o input do perfil
    if not primeira_execucao_efetiva:
        # A partir da segunda consulta já inicia desse ponto
        print("👤 Trocando perfil para o CNPJ de procurado...")
        pos_label_perfil2 = localizar_label_perfil2()
        pyautogui.click(pos_label_perfil2)
        esperar(3, check_stop_callback)
    
        pyautogui.press("down")
        pyautogui.press("enter")
        esperar(3, check_stop_callback)

        # Insere o CNPJ do cliente
        print(f"🏢 Inserindo CNPJ do cliente: {cnpj}")
        pos_input_cnpj = localizar_input_cnpj()
        pyautogui.click(pos_input_cnpj)
        time.sleep(3)
     
        pyautogui.write(cnpj, interval=0.1)
        verificar_parada(check_stop_callback)
    
        print(" Clicando em Definir para avançar...")
        # Localiza e clica no botão definir para prosseguir
        pos_btn_definir = localizar_btn_definir()
        pyautogui.click(pos_btn_definir)
        esperar(5, check_stop_callback)
        verificar_parada(check_stop_callback)

    # Localiza gestão de guias
    print("📁 Localizando gestão de guias...")
    pos_gestao_guias = localizar_gestao_guias()
    pyautogui.click(pos_gestao_guias)
    esperar(5, check_stop_callback)
    verificar_parada(check_stop_callback)

    # Guia parametrizada, mouse já está na posição certa, apenas clica
    print("📁 Clicando em guia parametrizada...")
    pyautogui.click(pos_gestao_guias)
    esperar(3, check_stop_callback)
    verificar_parada(check_stop_callback)
    time.sleep(3)

    pos_nao_ha_debitos = localizar_nao_ha_debitos()
    if pos_nao_ha_debitos:
        print("❌ Não há débitos para emitir guia.")
        if caminho_xlsx:
            marcar_status_validacao(caminho_xlsx, cnpj, "NÃO HÁ DÉBITOS")
        
        if empresa_id_db and isinstance(caminho_xlsx, (str, dict)):
            is_mysql_call = False
            if isinstance(caminho_xlsx, dict):
                is_mysql_call = True
            elif isinstance(caminho_xlsx, str) and caminho_xlsx.startswith("mysql://"):
                is_mysql_call = True

            if is_mysql_call:
                db = DatabaseHandler(caminho_xlsx)
                db.marcar_status_erro(empresa_id_db, "NÃO HÁ DÉBITOS")
        
        print("🔄 Resetando estado para a próxima consulta...")
        # Localiza botao fgts digital
        pos_btn_fgts_digital = localizar_btn_fgts_digital()
        if pos_btn_fgts_digital:
            pyautogui.click(pos_btn_fgts_digital)
            esperar(3, check_stop_callback)
            
            # Localiza botao trocar perfil
            pos_btn_trocar_perfil = localizar_btn_trocar_perfil()
            if pos_btn_trocar_perfil:
                pyautogui.click(pos_btn_trocar_perfil)
                esperar(5, check_stop_callback)
        
        return True

    time.sleep(3)
    # Rolar scroll para baixo
    print("📁 Rolar scroll para baixo...")
    pyautogui.scroll(-600)
    esperar(3, check_stop_callback)
    verificar_parada(check_stop_callback)

    pos_btn_ajuda = localizar_btn_ajuda()
    if pos_btn_ajuda:
        pyautogui.moveTo(pos_btn_ajuda)
        esperar(3, check_stop_callback)
        verificar_parada(check_stop_callback)

    # Lógica para garantir que 12/2025 e 13º/2025 sejam extraídos juntos
    competencia_in = competencia
    competencia_fi = competencia
    
    if competencia == "12/2025":
        print("📅 Detectada competência 12/2025. Expandindo pesquisa para incluir 13º/2025.")
        competencia_fi = "13º/2025" # No site, usamos 13º/2025
    
    
    pos_quadro_competencia = localizar_quadro_competencia()
    
    if pos_quadro_competencia:
        pyautogui.click(pos_quadro_competencia[0] - 150, pos_quadro_competencia[1] + 50)
        esperar(3, check_stop_callback)
        verificar_parada(check_stop_callback)
        pyperclip.copy(competencia_in)
        pyautogui.hotkey('ctrl', 'v')
        pyautogui.press("enter")
        esperar(3, check_stop_callback)
        verificar_parada(check_stop_callback)

        pyautogui.click(pos_quadro_competencia[0] + 150, pos_quadro_competencia[1] + 50)
        esperar(3, check_stop_callback)
        verificar_parada(check_stop_callback)
        pyperclip.copy(competencia_fi)
        pyautogui.hotkey('ctrl', 'v')
        pyautogui.press("enter")
        esperar(2, check_stop_callback)
        verificar_parada(check_stop_callback)
    else:
        print("❌ Verificando modelo quadro 13º/2025.")
        # localizar quadro competencia 13º/2025
        pos_quadro_competencia_13 = localizar_quadro_competencia_13()
        if pos_quadro_competencia_13:
            pyautogui.click(pos_quadro_competencia_13[0] - 150, pos_quadro_competencia_13[1] + 50)
            esperar(2, check_stop_callback)
            verificar_parada(check_stop_callback)
            pyperclip.copy(competencia_in)
            pyautogui.hotkey('ctrl', 'v')
            pyautogui.press("enter")
            esperar(2, check_stop_callback)
            verificar_parada(check_stop_callback)

            pyautogui.click(pos_quadro_competencia_13[0] + 150, pos_quadro_competencia_13[1] + 50)
            esperar(2, check_stop_callback)
            verificar_parada(check_stop_callback)
            pyperclip.copy(competencia_fi)
            pyautogui.hotkey('ctrl', 'v')
            pyautogui.press("enter")
            esperar(2, check_stop_callback)
            verificar_parada(check_stop_callback)
        else:
            print("❌ Quadro de competência 13º/2025 não encontrado.")
            return False
    
    # Localiza parametrização e desmarca
    print("📁 Localizando parametrização...")
    pos_parametrizacao = localizar_parametros()
    pyautogui.click(pos_parametrizacao[0] - 630, pos_parametrizacao[1] + 20)
    esperar(1.5, check_stop_callback)
    verificar_parada(check_stop_callback)

    pyautogui.click(pos_parametrizacao[0] - 215, pos_parametrizacao[1] + 20)
    esperar(1.5, check_stop_callback)
    verificar_parada(check_stop_callback)

    pyautogui.click(pos_parametrizacao[0] + 50, pos_parametrizacao[1] + 20)
    esperar(1.5, check_stop_callback)
    verificar_parada(check_stop_callback)

    # Scroll para baixo
    pyautogui.scroll(-100)
    esperar(2, check_stop_callback)
    verificar_parada(check_stop_callback)

    # localizar botão pesquisar
    pos_btn_pesquisar = localizar_btn_pesquisar()
    pyautogui.click(pos_btn_pesquisar[0] + 200, pos_btn_pesquisar[1])
    esperar(4, check_stop_callback)
    verificar_parada(check_stop_callback)

    # Localizar alerta de item nao encontrado
    print("🔍 Verificando se há alertas de 'item não encontrado'...")
    pos_alerta = localizar_alerta_item_nao_encontrado()
    if pos_alerta:
        print("⚠️ Alerta de 'item não encontrado' detectado, mas prosseguindo com o fluxo conforme solicitado...")
        # Se desejar marcar na planilha sem abortar, descomente abaixo:
        # if caminho_xlsx: marcar_guia_nao_encontrada(caminho_xlsx, cnpj)
    else:
        print("✅ Nenhum alerta detectado. Seguindo com a seleção de guias...")
    
       
    # localizar itens para guia (aqui é selecionado todas as guias)
    pos_itens_para_guia = localizar_itens_para_guia()
    pyautogui.click(pos_itens_para_guia[0] - 805, pos_itens_para_guia[1] - 15)
    esperar(4, check_stop_callback)
    verificar_parada(check_stop_callback)
    
    # localizar botão adicionar a guia
    pos_btn_adicionar_a_guia = localizar_adicionar_a_guia()
    pyautogui.click(pos_btn_adicionar_a_guia)
    esperar(4, check_stop_callback)
    verificar_parada(check_stop_callback)

    # Scroll para baixo para aparecer o botao avançar
    pyautogui.scroll(-300)
    esperar(4, check_stop_callback)
    verificar_parada(check_stop_callback)

    # Adicionar lógica para acionar scroll para baixo até identificar o botão avançar
    print("🖱️ Iniciando scroll para localizar o botão Avançar...")
    max_scrolls = 25
    scroll_count = 0

    # 1. Localizar botão avançar (Seleção de Débitos)
    loop_avancar_encontrado = False
    while scroll_count < max_scrolls:
        pos_btn_avancar = localizar_btn_avancar(deve_quebrar=False)
        if pos_btn_avancar:
            print(f"✅ Botão Avançar localizado na tentativa {scroll_count + 1}!")
            pyautogui.click(pos_btn_avancar)
            esperar(2, check_stop_callback)
            loop_avancar_encontrado = True
            break
        
        print(f"Rolando para baixo ({scroll_count + 1}/{max_scrolls})...")
        pyautogui.scroll(-250)
        scroll_count += 1
        esperar(1, check_stop_callback)
        verificar_parada(check_stop_callback)
    
    if not loop_avancar_encontrado:
        print("❌ Botão Avançar não foi encontrado após o limite de scrolls.")
        raise Exception("Falha ao localizar o botão Avançar na seleção de débitos.")

    # 2. Verificar Alerta Sem Consignado (esta tela aparece após o primeiro avançar)
    pos_alerta_sem_consignado = localizar_alerta_sem_consignado()
    if pos_alerta_sem_consignado:
        print("⚠️ Alerta sem consignado detectado! Clicando em Avançar novamente...")
        # Se o alerta aparece, precisamos clicar em Avançar novamente para chegar no resumo
        scroll_count = 0 # Reiniciando contagem para nova busca
        loop_avancar_encontrado = False
        while scroll_count < max_scrolls:
            pos_btn_avancar = localizar_btn_avancar(deve_quebrar=False)
            if pos_btn_avancar:
                print(f"✅ Botão Avançar (Pós Alerta) localizado!")
                pyautogui.click(pos_btn_avancar)
                esperar(2, check_stop_callback)
                loop_avancar_encontrado = True
                break
            pyautogui.scroll(-250)
            scroll_count += 1
            esperar(1, check_stop_callback)
            verificar_parada(check_stop_callback)
        
        if not loop_avancar_encontrado:
             raise Exception("Falha ao localizar o botão Avançar após o alerta sem consignado.")


    else:
        print("✅ Alerta sem consignado não detectado, preenchendo débitos adicionais...")
        # [Fluxo Normal de Débitos Adicionais/Consignado]
        # Localiza competencia inicial
        # Scroll para baixo
        pyautogui.scroll(-150)
        esperar(2, check_stop_callback)
        verificar_parada(check_stop_callback)
        
        pos_quadro_competencia_consignado = localizar_quadro_competencia_consignado()
        pyautogui.click(pos_quadro_competencia_consignado[0] - 150, pos_quadro_competencia_consignado[1] + 50)
        esperar(2, check_stop_callback)
        verificar_parada(check_stop_callback)
        pyperclip.copy(competencia_in)
        pyautogui.hotkey('ctrl', 'v')
        pyautogui.press("enter")
        esperar(2, check_stop_callback)
        verificar_parada(check_stop_callback)

        pyautogui.click(pos_quadro_competencia_consignado[0] + 150, pos_quadro_competencia_consignado[1] + 50)
        esperar(3, check_stop_callback)
        verificar_parada(check_stop_callback)
        pyperclip.copy(competencia_in)
        pyautogui.hotkey('ctrl', 'v')
        pyautogui.press("enter")
        esperar(3, check_stop_callback)
        verificar_parada(check_stop_callback)

        pos_desmarcar_sem_guia_emitida = localizar_desmarcar_sem_guia_emitida()
        if pos_desmarcar_sem_guia_emitida:
            pyautogui.click(pos_desmarcar_sem_guia_emitida)
            esperar(1, check_stop_callback)
        
        pyautogui.scroll(-250)  
        verificar_parada(check_stop_callback)

        pos_btn_pesquisar = localizar_btn_pesquisar()
        if pos_btn_pesquisar:
            pyautogui.click(pos_btn_pesquisar[0] + 200, pos_btn_pesquisar[1])
            esperar(3, check_stop_callback)

        pos_itens_consignado = localizar_itens_consignado()
        if pos_itens_consignado:
            pyautogui.click(pos_itens_consignado[0] - 810, pos_itens_consignado[1] - 5)
            esperar(1, check_stop_callback)

        pos_btn_adicionar_a_guia = localizar_adicionar_a_guia()
        if pos_btn_adicionar_a_guia:
            pyautogui.click(pos_btn_adicionar_a_guia)
            esperar(2, check_stop_callback)


        # 3. Localizar botão avançar final (após adicionar consignados)
        loop_avancar_encontrado = False
        scroll_count = 0
        while scroll_count < max_scrolls:
            pos_btn_avancar = localizar_btn_avancar(deve_quebrar=False)
            if pos_btn_avancar:
                print(f"✅ Botão Avançar final localizado na tentativa {scroll_count + 1}!")
                pyautogui.click(pos_btn_avancar)
                esperar(3, check_stop_callback)
                loop_avancar_encontrado = True
                break
            
            print(f"Rolando para baixo ({scroll_count + 1}/{max_scrolls})...")
            pyautogui.scroll(-250)
            scroll_count += 1
            esperar(1, check_stop_callback)
            verificar_parada(check_stop_callback)
        
        if not loop_avancar_encontrado:
            print("❌ Botão Avançar final não foi encontrado após o limite de scrolls.")
            raise Exception("Falha ao localizar o botão Avançar após adicionar consignados.")
        
        # scroll para baixo para garantir que o botao avancar esteja visivel
        pyautogui.scroll(-250)
        esperar(1, check_stop_callback)
    print("✅ Scroll para baixo para garantir que o botao avancar esteja visivel")
    #scroll para baixo para garantir que o botao avancar esteja visivel
    pyautogui.scroll(-450)
    esperar(1, check_stop_callback)
    time.sleep(2)
    #clicando no botao avançar (Explícito como no código funcionando do usuário)
    pos_btn_avancar = localizar_btn_avancar()
    pyautogui.click(pos_btn_avancar)
    esperar(3, check_stop_callback) 

    # logica de extração de dados
    print("📊 Iniciando extração de dados da tabela...")
    validacao_sucesso = False
    try:
        # Redetecta o alerta na tela de resumo para ter certeza do modo de extração
        alerta_sem_consignado_presente = True if localizar_alerta_sem_consignado() else False

        # Garante visão da tabela e do total antes de copiar
        pyautogui.scroll(-400) 
        esperar(2, check_stop_callback)
        
        dados_linhas, resumo_extraido = extrair_dados_tabela_detalhada(check_stop_callback, alerta_ativo=alerta_sem_consignado_presente)
        total_extraido_final = resumo_extraido['total_guia']

        
        if total_extraido_final > 0:
            # Organiza os valores individuais por competência para a planilha
            mapa_valores = {}
            for item in dados_linhas:
                comp = item['Competencia Apuracao']
                valor_ind = float(item['Total Individual'])
                mapa_valores[comp] = valor_ind

            # Adicionamos o "Total Geral" ao mapa para que o excel_handler use como valor consolidado
            mapa_valores["TOTAL_CONSOLIDADO"] = total_extraido_final

            print(f"💰 Valores extraídos: {mapa_valores}")

            # --- LÓGICA DE VALIDAÇÃO ---
            valor_fgts_extraido = round(resumo_extraido.get('valor_fgts', 0) + resumo_extraido.get('valor_fgts13', 0), 2)
            valor_consignado_extraido = resumo_extraido.get('valor_consignado', 0)
            
            # Comparamos o totalBase (DB) com o totalGuia (Extraído Total) conforme solicitado
            print(f"⚖️ Validando: totalBase(DB)={total_base_esperado} vs totalGuia(Extraído)={total_extraido_final}")
            valor_divergente = abs(total_base_esperado - total_extraido_final) > 0.02
            
            if valor_divergente:
                print(f"⚠️ DIVERGÊNCIA DETECTADA! Total Extraído: {total_extraido_final} | totalBase DB: {total_base_esperado}")
                print(f"   Breakdown Extração: FGTS={valor_fgts_extraido}, Consignado={valor_consignado_extraido}")
                status_final = 3 # Erro/Divergência
                validacao_sucesso = False
            else:
                print(f"✅ VALORES CONFEREM! (Total extraído bate com totalBase do banco)")
                
                # --- LÓGICA DE VALIDAÇÃO DA DATA (NOVA REGRA) ---
                data_venc_str = resumo_extraido.get('vencimento_guia')
                data_valida = False
                
                if data_venc_str:
                    try:
                        data_venc = datetime.datetime.strptime(data_venc_str, "%d/%m/%Y")
                        agora = datetime.datetime.now()
                        
                        # Verifica se é o mês e ano atual
                        if data_venc.month == agora.month and data_venc.year == agora.year:
                            # Verifica se o dia é 18, 19 ou 20
                            if data_venc.day in [18, 19, 20]:
                                data_valida = True
                                print(f"✅ Data de vencimento ({data_venc_str}) válida para emissão.")
                            else:
                                print(f"❌ Data de vencimento ({data_venc_str}) INVÁLIDA: Dia deve ser 18, 19 ou 20.")
                        else:
                            print(f"❌ Data de vencimento ({data_venc_str}) INVÁLIDA: Deve ser do mês/ano atual.")
                    except Exception as e:
                        print(f"⚠️ Erro ao processar data de vencimento: {e}")
                else:
                    print("❌ Data de vencimento não localizada para validação.")
                
                if data_valida:
                    status_final = 2 # Concluído
                    validacao_sucesso = True
                else:
                    status_final = 3 # Erro/Divergência (ou data fora do prazo)
                    validacao_sucesso = False
                    print("⚠️ A emissão será bloqueada devido à data de vencimento inválida.")

            # Se houver caminho da planilha original, atualiza e valida (Excel mode)
            if caminho_xlsx and isinstance(caminho_xlsx, str) and not caminho_xlsx.startswith("mysql://"):
                validacao_sucesso = atualizar_valor_guia_original(caminho_xlsx, cnpj, mapa_valores)
            
            # Atualização no MySQL
            if empresa_id_db:
                print(f"🔌 Atualizando resultados no MySQL para empresa ID {empresa_id_db} (Status: {status_final})...")
                # Usar db_config que é garantido como o dicionário de conexão
                db = DatabaseHandler(db_config if db_config else caminho_xlsx)
            
                # Mapeamento detalhado
                dados_db = {
                    'valorGuiaFgts': resumo_extraido.get('valor_fgts', 0),
                    'valorGuiaFgts13': resumo_extraido.get('valor_fgts13', 0),
                    'valorGuiaConsignado': resumo_extraido.get('valor_consignado', 0),
                    'totalGuia': total_extraido_final,
                    'vencimentoGuia': resumo_extraido.get('vencimento_guia'),
                    'status': status_final
                }
                
                # Fallback se os campos específicos vierem zerados
                if dados_db['valorGuiaFgts'] == 0:
                    dados_db['valorGuiaFgts'] = mapa_valores.get(competencia, 0)
                if dados_db['valorGuiaFgts13'] == 0:
                    dados_db['valorGuiaFgts13'] = mapa_valores.get("13º/2025", 0)

                # Define statusOnvio se houve divergência
                if status_final == 3: # Erro/Divergência
                    dados_db['statusOnvio'] = 'Divergente'

                print(f"🔌 Payload para atualização no DB: {dados_db}")
                db.atualizar_dados_guia(empresa_id_db, dados_db)
    except Exception as e:
        print(f"❌ Erro durante a extração/salvamento: {e}")
        # Tenta atualizar status para Erro no banco
        if empresa_id_db:
             try:
                db = DatabaseHandler(db_config if db_config else caminho_xlsx)
                db.atualizar_status_onvio(empresa_id_db, "Erro")
             except: pass
    else:
        # Se não houve exceção, mas o total foi 0, também devemos registrar o erro no banco
        if total_extraido_final == 0 and empresa_id_db:
             try:
                print(f"🔌 Atualizando erro de extração (valor 0) no MySQL para empresa ID {empresa_id_db}...")
                db = DatabaseHandler(db_config if db_config else caminho_xlsx)
                db.marcar_status_erro(empresa_id_db, 3) # 3 = Erro/Falha
                db.atualizar_status_onvio(empresa_id_db, "Erro")
             except Exception as e_db:
                print(f"❌ Erro ao registrar falha no banco: {e_db}")

    print("\n✅ Fluxo de extração concluído!")

    # Clicar no centro dinâmico da tela para desfazer seleção
    largura, altura = pyautogui.size()
    print(f"🖱️ Clicando no centro da tela ({largura//2}, {altura//2}) para desmarcar...")
    pyautogui.click(largura // 2, altura // 2)
    esperar(0.5, check_stop_callback)
    verificar_parada(check_stop_callback)
    # Se a validação foi SIM, prossegue para emitir a guia
    if validacao_sucesso:
        print("🎫 Validação bem-sucedida! Prosseguindo para emitir a guia...")
        # localizar botao emitir
        time.sleep(3)
       
        # Localizando botão emitir com scroll
        print("🎫 Localizando botão Emitir com scroll...")
        scroll_count = 0
        max_scrolls = 15
        btn_emitir_encontrado = False
        
        while scroll_count < max_scrolls:
            pos_btn_emitir = localizar_btn_emitir(deve_quebrar=False)
            if pos_btn_emitir:
                print(f"✅ Botão Emitir localizado!")
                pyautogui.click(pos_btn_emitir)
                btn_emitir_encontrado = True
                break
            
            print(f"Rolando para baixo para buscar botão Emitir ({scroll_count + 1}/{max_scrolls})...")
            pyautogui.scroll(-300)
            scroll_count += 1
            esperar(1, check_stop_callback)
            verificar_parada(check_stop_callback)
            
        if not btn_emitir_encontrado:
             raise Exception("Falha ao localizar o botão Emitir após o limite de scrolls.")
        
        esperar(5, check_stop_callback)
        verificar_parada(check_stop_callback)
        
        print("🖨️ Iniciando processo de impressão (PDF)...")
        esperar(2, check_stop_callback)
        
        # Tenta focar na página antes do Ctrl+P
        pyautogui.click(largura // 2, altura // 2)
        esperar(0.5, check_stop_callback)

        pyautogui.hotkey("ctrl", "p")
        esperar(5, check_stop_callback) # Aumentado tempo para carregar diálogo do browser
        pyautogui.press("enter")
        esperar(3, check_stop_callback)


        # Normaliza o caminho para usar barras normais (evita erro com barras invertidas)
        pasta_destino_corrigida = os.path.abspath(pasta_destino).replace('/', '\\')
        pyperclip.copy(pasta_destino_corrigida)
        time.sleep(1)

        # corrigir competencia substituir barra po _
        competencia_corrigida = competencia.replace('/', '_')
        try:
            # Foca na barra de endereços (Ctrl + L)
            pyautogui.hotkey("ctrl", "l")
            time.sleep(2)
            pyautogui.hotkey("ctrl", "v")
            time.sleep(2)
            pyautogui.press("enter")
            time.sleep(2)
            # Foca no nome do arquivo
            pyautogui.hotkey("ctrl", "f")
            time.sleep(2)
            pyautogui.hotkey("alt", "n")
            time.sleep(2)
        except Exception as e:
            print(f"⚠️ Erro ao forçar pasta no explorador: {e}")

        # Digita o nome do arquivo
        print(f"📄 Salvando arquivo: {nome_empresa}.pdf")
        pyperclip.copy(f"{codigo}-{competencia_corrigida}Guia FGTS Digital Mensal.pdf")
        time.sleep(1)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(2)
        pyautogui.press("enter")
        time.sleep(2)

        pos_pdf_existe = localizar_pdf_existe(deve_quebrar=False)
        if pos_pdf_existe:
            print("📁 Arquivo já existe, procedendo com a substituição...")
            pyautogui.click(pos_pdf_existe)
            verificar_parada(check_stop_callback)

            pos_confirmar_sobreescrever = localizar_confirmar_sobreescrever()
            pyautogui.click(pos_confirmar_sobreescrever)
            verificar_parada(check_stop_callback)
        else:
            print("✅ Documento salvo com sucesso.")
        
        # Sucesso no salvamento do PDF -> Atualizar Status Onvio para "A publicar"
        if empresa_id_db:
            try:
                print(f"🔌 Atualizando statusOnvio para 'A publicar' no MySQL (ID {empresa_id_db})...")
                db = DatabaseHandler(db_config if db_config else caminho_xlsx)
                db.atualizar_status_onvio(empresa_id_db, "A publicar")
            except Exception as e:
                print(f"⚠️ Erro ao atualizar statusOnvio para 'A publicar': {e}")

        time.sleep(3)

        # fechar a guia
        pyautogui.hotkey("ctrl", "w")
        time.sleep(3)
    else:
        print("⚠️ Validação falhou ou divergente. A guia NÃO será emitida ou impressa automaticamente.")
        # A lógica continua normalmente abaixo para fechar e trocar de perfil

    
    # Localiza botao fgts digital
    pos_btn_fgts_digital = localizar_btn_fgts_digital()
    pyautogui.click(pos_btn_fgts_digital)
    verificar_parada(check_stop_callback)
    time.sleep(3)


    # Localiza botao trocar perfil
    pos_btn_trocar_perfil = localizar_btn_trocar_perfil()
    pyautogui.click(pos_btn_trocar_perfil)
    verificar_parada(check_stop_callback)
    time.sleep(5)

   



    return True 
