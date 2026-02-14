import pyautogui
import time
import pyperclip

# ---------------------------
# Abrir navegador e página (apenas primeira vez)
# ---------------------------
def abrir_navegador_e_pagina(tipo_consulta):
    print(f"\n[DEBUG] abrir_navegador_e_pagina chamado com tipo_consulta='{tipo_consulta}'")
    print("\n🌐 Abrindo navegador e carregando página...")
    time.sleep(5)
    # 1) Abrir menu iniciar
    pyautogui.press("win")
    time.sleep(1)

    # 2) Abrir Firefox
    pyautogui.write("firefox", interval=0.1)
    time.sleep(1)
    pyautogui.press("enter")
    
    # Aguarda o navegador abrir e tenta maximizar
    print("🖥️ Verificando janela do navegador...")
    time.sleep(3) # Tempo para o Firefox abrir
    
    try:
        janelas = pyautogui.getWindowsWithTitle("Mozilla Firefox")
        if not janelas:
             janelas = pyautogui.getWindowsWithTitle("Firefox")
             
        if janelas:
            # Pega a primeira janela encontrada (geralmente a ativa)
            browser_window = janelas[0]
            print(f"🖥️ Janela encontrada: {browser_window.title}")
            
            if not browser_window.isMaximized:
                print("🖥️ Janela não está maximizada. Maximizando...")
                browser_window.maximize()
                time.sleep(1) # Tempo para animação
            else:
                print("🖥️ Janela já está maximizada.")
        else:
            print("⚠️ Não foi possível encontrar a janela do Firefox para verificar maximização.")
            
    except Exception as e:
        print(f"⚠️ Erro ao tentar maximizar janela: {e}")

    # 3) Determinar URL baseada no tipo de consulta
    url = "https://fgtsdigital.sistema.gov.br/portal/login"
    print(f'📋 Abrindo URL para: FGTS Digital - {url}')

    time.sleep(1)
    # Garante o foco na barra de endereço
    pyautogui.hotkey("ctrl", "l")
    time.sleep(0.5)
    
    pyperclip.copy(url)
    pyautogui.hotkey("ctrl", "v")
    pyautogui.press("enter")

    print("🌐 Aguardando página carregar...")
    time.sleep(5)

# ---------------------------
# Voltar para página inicial (recarregar URL)
# ---------------------------
def voltar_para_pagina_inicial(tipo_consulta):
    print("\n🔄 Recarregando página...")
    
    # Determinar URL baseada no tipo de consulta
    url = "https://fgtsdigital.sistema.gov.br/portal/login"
    
    # Seleciona a barra de endereço
    pyautogui.hotkey("ctrl", "l")
    
    time.sleep(0.5)
    
    # Cola a URL novamente
    pyperclip.copy(url)
    pyautogui.hotkey("ctrl", "v")
    pyautogui.press("enter")
    
    print("🌐 Aguardando página carregar...")
    time.sleep(5)

# ---------------------------
# Fechar navegador
# ---------------------------
def fechar_navegador():
    print("\n🔒 Fechando navegador...")
    pyautogui.hotkey('alt', 'f4')
    time.sleep(2)
