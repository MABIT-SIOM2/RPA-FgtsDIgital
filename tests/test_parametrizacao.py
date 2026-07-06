import pyautogui
import sys
import os
import time
import pyperclip

# Adiciona o diretório raiz ao path para permitir importações do src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.fgts_digital_site import localizar_parametros, localizar_btn_pesquisar2, localizar_competencia_inicial, localizar_competencia_final, localizar_desmarcar_sem_guia_emitida, localizar_itens_consignado, localizar_adicionar_a_guia, localizar_quadro_competencia, extrair_data_pagamento_guia, localizar_vencimento_debito
from src.utils.automation import esperar, verificar_parada
from src.services.fgts_digital_site import localizar_itens_para_guia

def check_stop_callback():
    """Mock callback para o teste"""
    return False

def test_fluxo_final():
    time.sleep(7)
    try:
        print("📁 Localizando parametrização...")
        pos_parametrizacao = localizar_parametros()
        pyautogui.click(pos_parametrizacao[0] - 610, pos_parametrizacao[1] + 20)
        esperar(1.5, check_stop_callback)
        verificar_parada(check_stop_callback)

        pyautogui.click(pos_parametrizacao[0] - 630, pos_parametrizacao[1] + 40)
        esperar(1.5, check_stop_callback)
        verificar_parada(check_stop_callback)

        pyautogui.click(pos_parametrizacao[0] - 40, pos_parametrizacao[1] + 20)
        esperar(1.5, check_stop_callback)
        verificar_parada(check_stop_callback)

        pyautogui.click(pos_parametrizacao[0] + 210, pos_parametrizacao[1] + 20)
        esperar(1.5, check_stop_callback)
        verificar_parada(check_stop_callback)  
        time.sleep(2)

        # pos_btn_pesquisar = localizar_btn_pesquisar2()
        # if pos_btn_pesquisar:
        #     pyautogui.click(pos_btn_pesquisar[0] + 150, pos_btn_pesquisar[1])
        #     esperar(3, check_stop_callback)

        try:
            print("📁 Localizando itens consignado...")
            # pos_itens_consignado = localizar_itens_consignado()
            # if pos_itens_consignado:
            #     pyautogui.click(pos_itens_consignado[0] - 810, pos_itens_consignado[1] - 10)
            #     esperar(1, check_stop_callback)
        except Exception as e:
            print(f"⚠️ Erro ao extrair ou salvar data de pagamento: {e}")
        

        
           
    except Exception as e:
        print(f"💥 Erro inesperado: {e}")

if __name__ == "__main__":
    test_fluxo_final()
