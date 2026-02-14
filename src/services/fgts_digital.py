import pyautogui
import time
import pyperclip
import os
from src.utils.automation import resource_path, localizar_imagem, verificar_parada, esperar, StopExecution
from src.services.browser import abrir_navegador_e_pagina, voltar_para_pagina_inicial   

def localizar_login_dominio():
    return localizar_imagem(resource_path("src/assets/dominio/login_dominio.png"), confianca=0.7)

def localizar_input_user_dominio():
    return localizar_imagem(resource_path("src/assets/dominio/input_user_dominio.png"), confianca=0.7)

def localizar_guia_relatorios():
    return localizar_imagem(resource_path("src/assets/dominio/guia_relatorios.png"), confianca=0.7)



def consultar_fgts_digital(cnpj, nome_empresa, codigo, competencia, pasta_destino, abrir_navegador=False, primeira_pasta=False, check_stop_callback=None, tipo_consulta="FGTS Digital", caminho_xlsx=None):
    verificar_parada(check_stop_callback)
    print(f"\n🚀 Iniciando a consulta para o CNPJ: {cnpj}")
    time.sleep(5)
    pyautogui.press("win")
    pyautogui.write("Dominio Folha", interval=0.1)
    time.sleep(2)
    pyautogui.press("enter")
    esperar(10, check_stop_callback)
    verificar_parada(check_stop_callback)

    pos_login_dominio = localizar_login_dominio()
    pyautogui.click(pos_login_dominio)
    esperar(2, check_stop_callback)
    verificar_parada(check_stop_callback)

    for i in range(10):
        pyautogui.press("delete")

    pyautogui.write("856413", interval=0.1)
    pyautogui.press("enter")
    time.sleep(3)
    pyautogui.press("esc")
    esperar(20, check_stop_callback)
    verificar_parada(check_stop_callback)
    
    pyautogui.press("esc")
    esperar(10, check_stop_callback)
    verificar_parada(check_stop_callback)

    pyautogui.press("F8")
    esperar(2, check_stop_callback)
    verificar_parada(check_stop_callback)

    pyautogui.write(codigo, interval=0.1)
    pyautogui.press("enter")
    esperar(10, check_stop_callback)
    verificar_parada(check_stop_callback)

    pos_guia_relatorios = localizar_guia_relatorios()
    pyautogui.click(pos_guia_relatorios)
    esperar(1, check_stop_callback)
    verificar_parada(check_stop_callback)

    # Avança para opção guias
    for i in range(5):
        pyautogui.press("down", interval=0.1)
    
    pyautogui.press("right")

    # Avança para guias FGTS Digital
    for i in range(5):
        pyautogui.press("down", interval=0.1)
    pyautogui.press("enter")
    esperar(2, check_stop_callback)
    verificar_parada(check_stop_callback)

    



    
    return True 
