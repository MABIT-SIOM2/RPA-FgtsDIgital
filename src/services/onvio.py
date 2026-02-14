import pyautogui
import time
import pyperclip
import os
import sys

# Adiciona a raiz do projeto ao sys.path para permitir a execução direta do script
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from src.utils.automation import resource_path, localizar_imagem, verificar_parada, esperar, StopExecution
from src.utils.database_handler import DatabaseHandler

# ---------------------------
# Funções de Localização de Imagem (Mapeamento)
# ---------------------------

def localizar_cliente():
    return localizar_imagem(resource_path("src/assets/onvio/btn_cliente.png"), confianca=0.7, refresh_after_block=True)

def localizar_pasta_pessoal():
    return localizar_imagem(resource_path("src/assets/onvio/pasta_pessoal.png"), confianca=0.7, refresh_after_block=True)

def localizar_pasta_folha_pagamento():
    return localizar_imagem(resource_path("src/assets/onvio/pasta_folha_pagamento.png"), confianca=0.7)

def localizar_btn_upload():
    return localizar_imagem(resource_path("src/assets/onvio/btn_upload.png"), confianca=0.7)

def localizar_pasta_mes():
    return localizar_imagem(resource_path("src/assets/onvio/pastaMes.png"), confianca=0.7)

def localizar_btn_novo():
    return localizar_imagem(resource_path("src/assets/onvio/btn_novo.png"), confianca=0.7)

def localizar_btn_gerenciar():
    return localizar_imagem(resource_path("src/assets/onvio/btn_gerenciar.png"), confianca=0.7)

def localizar_btn_definir_vencimento():
    return localizar_imagem(resource_path("src/assets/onvio/btn_definir_vencimento.png"), confianca=0.7)

def localizar_campo_data_vencimento():
    return localizar_imagem(resource_path("src/assets/onvio/campo_data_vencimento.png"), confianca=0.7)

def localizar_checkbox_calendario_impostos():
    return localizar_imagem(resource_path("src/assets/onvio/checkbox_calendario_imposto.png"), confianca=0.7)

def localizar_btn_salvar():
    return localizar_imagem(resource_path("src/assets/onvio/btn_salvar.png"), confianca=0.7)

def localizar_btn_entrar():
    return localizar_imagem(resource_path("src/assets/onvio/btn_entrar.png"), confianca=0.7)

# ---------------------------
# Fluxo Principal (Consultar Onvio)
# ---------------------------

def consultar_onvio(empresa_id, db_config, pasta_destino, abrir_navegador=False, primeira_pasta=False, check_stop_callback=None, tipo_consulta="ONVIO", caminho_xlsx=None):
    """
    Realiza o fluxo de login e navegação no ONVIO.
    Consulta o banco de dados para obter informações da empresa.
    Processa apenas empresas com statusOnvio = 'A publicar'.
    
    Args:
        empresa_id: ID da empresa na tabela 'empresas'
        db_config: Configuração do banco de dados (dict)
        pasta_destino: Caminho da pasta de destino
        abrir_navegador: Se deve abrir o navegador
        primeira_pasta: Se é a primeira pasta sendo processada
        check_stop_callback: Callback para verificar parada
        tipo_consulta: Tipo de consulta (sempre "ONVIO")
        caminho_xlsx: Caminho do arquivo Excel (para compatibilidade)
    
    Returns:
        bool: True se sucesso, False caso contrário
    """
    
    # Consultar banco de dados para obter informações da empresa
    if db_config is None or empresa_id is None:
        print("❌ Erro: db_config e empresa_id são obrigatórios para Onvio")
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
                e.onvioId,
                e.razao as nome_empresa,
                r.competenciaInicial as competencia,
                r.vencimentoGuia,
                r.statusOnvio
            FROM empresas e
            INNER JOIN roboFgts r ON r.empresaId = e.id
            WHERE e.id = %s AND r.statusOnvio = 'A publicar'
        """
        cursor.execute(query, (empresa_id,))
        empresa_data = cursor.fetchone()
        cursor.close()
        
        if not empresa_data:
            print(f"⏭️ Empresa ID {empresa_id} não está com status 'A publicar' - pulando")
            return False
        
        # Extrair dados
        codigo = empresa_data['codigo']
        cnpj = empresa_data['cnpj']
        onvio_id = empresa_data['onvioId']
        nome_empresa = empresa_data['nome_empresa']
        competencia = empresa_data['competencia']
        vencimentoGuia = empresa_data['vencimentoGuia']
        
        # Formatar vencimento se necessário (de YYYY-MM-DD para DD/MM/YYYY)
        if vencimentoGuia and '-' in str(vencimentoGuia):
            try:
                ano, mes, dia = str(vencimentoGuia).split('-')
                vencimentoGuia = f"{dia}/{mes}/{ano}"
            except:
                pass
        
        print(f"📊 Dados obtidos do banco:")
        print(f"   Código: {codigo}")
        print(f"   onvioId: {onvio_id}")
        print(f"   CNPJ: {cnpj}")
        print(f"   Nome: {nome_empresa}")
        print(f"   Competência: {competencia}")
        print(f"   Vencimento: {vencimentoGuia}")
        
    except Exception as e:
        print(f"❌ Erro ao consultar banco de dados: {e}")
        return False
    finally:
        db.disconnect()
    
    # Lógica de Inicialização e Login (Apenas se abrir_navegador for True)
    if abrir_navegador:
        time.sleep(6)
        pyautogui.press("win")
        pyautogui.write("firefox", interval=0.2)
        pyautogui.press("enter")
        time.sleep(2)
        pyautogui.hotkey("ctrl", "l")
        url = "https://onvio.com.br/staff/#/documents/client"
        pyperclip.copy(url)
        time.sleep(1)
        pyautogui.hotkey("ctrl", "v")
        pyautogui.press("enter")
        time.sleep(10)
        verificar_parada(check_stop_callback)

        pos_btn_entrar = localizar_btn_entrar()
        pyautogui.click(pos_btn_entrar)
        time.sleep(5)
        verificar_parada(check_stop_callback)

        pyautogui.press("down")
        time.sleep(1)
        pyautogui.press("enter")
        time.sleep(2)
        pyautogui.press("enter")
        time.sleep(1)
        verificar_parada(check_stop_callback)
        pyautogui.press("down")
        time.sleep(1)
        pyautogui.press("enter")
        time.sleep(1)
        pyautogui.press("enter")
        time.sleep(1)
        verificar_parada(check_stop_callback)

        # Aguarda a pagina carregar
        time.sleep(10)
        verificar_parada(check_stop_callback)
    else:
        print("🌐 Navegador já aberto. Pulando login e indo direto para localização de cliente...")
        # Dá um foco na janela do navegador por precaução (Alt+Tab ou clique)
        pyautogui.hotkey("alt", "tab")
        time.sleep(2)

    # Navegação Direta via onvioId
    print(f"� Navegando diretamente para o cliente: {onvio_id}")
    pyautogui.hotkey("ctrl", "l")
    time.sleep(1.5)
    url_cliente = f"https://onvio.com.br/staff/#/documents/client/{onvio_id}"
    pyperclip.copy(url_cliente)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(1)
    pyautogui.press("enter")
    
    # Aguarda carregamento do dashboard do cliente
    time.sleep(10)
    verificar_parada(check_stop_callback)

    pos_pasta_pessoal = localizar_pasta_pessoal()
    pyautogui.click(pos_pasta_pessoal)
    time.sleep(7)
    esperar(4, check_stop_callback)

    pos_pasta_folha_pagamento = localizar_pasta_folha_pagamento()
    pyautogui.click(pos_pasta_folha_pagamento)
    esperar(4, check_stop_callback)    
    time.sleep(4)
    verificar_parada(check_stop_callback)

    #botao upload é apenas referencia para o clique na pasta 2026
    pos_btn_upload = localizar_btn_upload()
    pyautogui.moveTo(pos_btn_upload[0], pos_btn_upload[1] +105)
    pyautogui.click()
    esperar(4, check_stop_callback)

    largura, altura = pyautogui.size()
    pyautogui.moveTo(largura // 2, altura // 2)
    esperar(4, check_stop_callback)
    pyautogui.scroll(-200)
    
    time.sleep(4)
    pos_pasta_mes = localizar_pasta_mes()
    pyautogui.click(pos_pasta_mes)
    esperar(4, check_stop_callback)    
    time.sleep(3)
    verificar_parada(check_stop_callback)

    #mover mouse para o centro da tela
    largura, altura = pyautogui.size()
    pyautogui.moveTo(largura // 2, altura // 2)
    esperar(4, check_stop_callback)

    pyautogui.click(pos_btn_upload)
    esperar(2, check_stop_callback)
    time.sleep(2)
    verificar_parada(check_stop_callback)
    
    # Força a correção do caminho para o padrão Windows
    pasta_destino_corrigida = pasta_destino.replace("/", "\\")
    print(f"📂 Forçando caminho da pasta no Explorador: {pasta_destino_corrigida}")
    
    pyperclip.copy(pasta_destino_corrigida)
    time.sleep(2)

    try:
        # Foca na barra de endereços (Ctrl + L)
        pyautogui.hotkey("ctrl", "l")
        time.sleep(1.5)
        # Limpa e Cola
        pyautogui.press("backspace")
        time.sleep(1.5)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(1.5)
        pyautogui.press("enter")
        time.sleep(1.5)
        
        # Sequência para garantir que o cursor vá para o campo de nome do arquivo (Alt + N)
        pyautogui.hotkey("alt", "n")
        time.sleep(1.5)
    except Exception as e:
        print(f"⚠️ Erro ao forçar pasta no explorador: {e}")

    # Corrigir competência: substituir barra por _
    competencia_corrigida = competencia.replace('/', '_')
    nome_arquivo = f"{codigo}-{competencia_corrigida}Guia FGTS Digital Mensal.pdf"
    
    print(f"📄 Selecionando arquivo: {nome_arquivo}")
    
    # --- VERIFICAÇÃO DE ARQUIVO ---
    caminho_completo_arquivo = os.path.join(pasta_destino_corrigida, nome_arquivo)
    if os.path.exists(caminho_completo_arquivo):
        print(f"✅ ARQUIVO ENCONTRADO NO DISCO: {caminho_completo_arquivo}")
    else:
        print(f"❌ ARQUIVO NÃO ENCONTRADO: {caminho_completo_arquivo}")
        print(f"📂 Conteúdo da pasta '{pasta_destino_corrigida}':")
        try:
            arquivos_na_pasta = os.listdir(pasta_destino_corrigida)
            if not arquivos_na_pasta:
                print("   (Pasta vazia)")
            else:
                sugestao = None
                from difflib import get_close_matches
                sugestao = get_close_matches(nome_arquivo, arquivos_na_pasta, n=1, cutoff=0.6)
                
                for f in arquivos_na_pasta:
                    print(f"   - {f}")
                
                if sugestao:
                    print(f"💡 Você quis dizer: {sugestao[0]}?")
        except Exception as e:
            print(f"⚠️ Erro ao listar pasta: {e}")
    # ------------------------------

    pyperclip.copy(nome_arquivo)
    time.sleep(2)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(2.5)
    pyautogui.press("enter")
    verificar_parada(check_stop_callback)
    # Aguarda o upload do arquivo
    time.sleep(15)

    #botao novo como referencia para selecionar o arquivo
    pos_btn_novo = localizar_btn_novo()
    pyautogui.click(pos_btn_novo[0] - 25, pos_btn_novo[1] + 100)
    esperar(4, check_stop_callback)
    time.sleep(4)
    verificar_parada(check_stop_callback)
    
    # Botão gerenciar arquivo
    pos_btn_gerenciar = localizar_btn_gerenciar()
    pyautogui.click(pos_btn_gerenciar)
    time.sleep(3)
    # Move o mouse para posição que possa usar o scroll para ficar visivel definir data de vencimento
    pyautogui.moveTo(pos_btn_gerenciar[0], pos_btn_gerenciar[1] + 100)
    esperar(4, check_stop_callback)
    time.sleep(3)
    # scroll para baixo
    pyautogui.scroll(-150)
    time.sleep(3)
    verificar_parada(check_stop_callback)

    # Botão definir vencimento
    pos_btn_definir_vencimento = localizar_btn_definir_vencimento()
    pyautogui.click(pos_btn_definir_vencimento)
    time.sleep(4)
    verificar_parada(check_stop_callback)
    time.sleep(4)
    # Marcar o checkbox 
    pos_checkbox_calendario_impostos = localizar_checkbox_calendario_impostos()
    pyautogui.click(pos_checkbox_calendario_impostos[0] - 220, pos_checkbox_calendario_impostos[1])
    time.sleep(4)
    verificar_parada(check_stop_callback)
    # Campo data de vencimento
    pos_campo_data_vencimento = localizar_campo_data_vencimento()
    pyautogui.click(pos_campo_data_vencimento)
    time.sleep(3)
    verificar_parada(check_stop_callback)
    pyautogui.write(vencimentoGuia, interval=0.2)
    time.sleep(4)
    verificar_parada(check_stop_callback)
    
    pos_btn_salvar = localizar_btn_salvar()
    pyautogui.click(pos_btn_salvar)
    time.sleep(4)
    verificar_parada(check_stop_callback)
    

    print("\n✅ Fluxo ONVIO iniciado com sucesso!")

    return True

