import pyautogui
import sys
import os
import time
import pyperclip

# Adiciona o diretório raiz ao path para permitir importações do src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.fgts_digital_site import localizar_parametros, localizar_competencia_inicial, localizar_competencia_final, localizar_desmarcar_sem_guia_emitida, localizar_itens_consignado, localizar_adicionar_a_guia, localizar_quadro_competencia, extrair_data_pagamento_guia, localizar_vencimento_debito
from src.utils.automation import esperar, verificar_parada
from src.services.fgts_digital_site import localizar_itens_para_guia

def check_stop_callback():
    """Mock callback para o teste"""
    return False

def test_fluxo_final():
    time.sleep(7)
    try:
        print("📁 Localizando parametrização...")
        pos_vencimento_debito = localizar_vencimento_debito()
        pyautogui.click(pos_vencimento_debito[0] - 750, pos_vencimento_debito[1])
        esperar(3, check_stop_callback)
        verificar_parada(check_stop_callback)
        pyperclip.copy("03/2026")
        pyautogui.hotkey('ctrl', 'v')
        pyautogui.press("enter")
        esperar(3, check_stop_callback)
        verificar_parada(check_stop_callback)

        pyautogui.click(pos_vencimento_debito[0] - 520, pos_vencimento_debito[1])
        esperar(3, check_stop_callback)
        verificar_parada(check_stop_callback)
        pyperclip.copy("03/2026")
        pyautogui.hotkey('ctrl', 'v')
        pyautogui.press("enter")
        esperar(2, check_stop_callback)
        verificar_parada(check_stop_callback)

        # Localiza competencia inicial


        # competencia_in = "12/2025"
       
        # print("📁 Localizando competencia inicial...")
        # pos_competencia_inicial = localizar_competencia_inicial()
        # pyautogui.click(pos_competencia_inicial)
        # esperar(3, check_stop_callback)
        # verificar_parada(check_stop_callback)
        # # Insere a competencia inicial
        # print(f"📁 Inserindo competencia inicial: {competencia_in}")
        # pyperclip.copy(competencia_in)
        # pyautogui.hotkey('ctrl', 'v')
        # pyautogui.press("enter")
        # verificar_parada(check_stop_callback)

        # # Localiza competencia final
        # print("📁 Localizando competencia final...")
        # pos_competencia_final = localizar_competencia_final()
        # pyautogui.click(pos_competencia_final)
        # esperar(3, check_stop_callback)
        # verificar_parada(check_stop_callback)
        # # Insere a competencia final
        # print(f"📁 Inserindo competencia final: {competencia_in}")
        # pyperclip.copy(competencia_in)
        # pyautogui.hotkey('ctrl', 'v')
        # pyautogui.press("enter")
        # verificar_parada(check_stop_callback)

        # pos_desmarcar_sem_guia_emitida = localizar_desmarcar_sem_guia_emitida()
        # if pos_desmarcar_sem_guia_emitida:
        #     pyautogui.click(pos_desmarcar_sem_guia_emitida)
        #     esperar(3, check_stop_callback)
        # verificar_parada(check_stop_callback)

        # pos_itens_consignado = localizar_itens_consignado()
        # if pos_itens_consignado:
        #     pyautogui.click(pos_itens_consignado[0] - 810, pos_itens_consignado[1] - 30)
        #     esperar(3, check_stop_callback)
        # verificar_parada(check_stop_callback)

        # # localizar botão adicionar a guia
        # pos_btn_adicionar_a_guia = localizar_adicionar_a_guia()
        # pyautogui.click(pos_btn_adicionar_a_guia)
        # esperar(5, check_stop_callback)
        # verificar_parada(check_stop_callback)
        # competencia = "12/2025"
        # competencia_in = competencia
        # competencia_fi = competencia
    
        # if competencia == "12/2025":
        #     print("📅 Detectada competência 12/2025. Expandindo pesquisa para incluir 13º/2025.")
        #     competencia_fi = "13º/2025" # No site, usamos 13º/2025
        # codigo = "202"
        # competencia_corrigida = competencia.replace('/', '_')
        # nome_arquivo = f"{codigo}-{competencia_corrigida}-Guia FGTS Digital Mensal.pdf"
        # pyperclip.copy(nome_arquivo)
        # print(f"📋 Nome do arquivo copiado para o clipboard: {nome_arquivo}")
        
        # pos_quadro_competencia = localizar_quadro_competencia()
        # pyautogui.click(pos_quadro_competencia[0] - 150, pos_quadro_competencia[1] + 50)
        # esperar(3, check_stop_callback)
        # verificar_parada(check_stop_callback)
        # pyperclip.copy(competencia_in)
        # pyautogui.hotkey('ctrl', 'v')
        # pyautogui.press("enter")
        # esperar(3, check_stop_callback)
        # verificar_parada(check_stop_callback)

        # pyautogui.click(pos_quadro_competencia[0] + 150, pos_quadro_competencia[1] + 50)
        # esperar(3, check_stop_callback)
        # verificar_parada(check_stop_callback)
        # pyperclip.copy(competencia_fi)
        # pyautogui.hotkey('ctrl', 'v')
        # pyautogui.press("enter")
        # esperar(3, check_stop_callback)
        # verificar_parada(check_stop_callback)

        # try:
        #     pos_itens_consignado = localizar_itens_consignado()
        #     if pos_itens_consignado:
        #         pyautogui.click(pos_itens_consignado[0] - 810, pos_itens_consignado[1] - 10)
        #         esperar(1, check_stop_callback)
        # except Exception as e:
        #     print(f"⚠️ Erro ao extrair ou salvar data de pagamento: {e}")
        

        
           
    except Exception as e:
        print(f"💥 Erro inesperado: {e}")

if __name__ == "__main__":
    test_fluxo_final()
