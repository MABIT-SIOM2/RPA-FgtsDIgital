import pyautogui
import time
import os
import sys

# ---------------------------
# Função para encontrar arquivos no executável
# ---------------------------
def resource_path(relative_path):
    """Obtém o caminho absoluto para o recurso, funciona para dev e para PyInstaller"""
    try:
        # PyInstaller cria uma pasta temporária e armazena o caminho em _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# ---------------------------
# Função genérica para localizar imagens na tela
# ---------------------------
def localizar_imagem(caminho_img, tentativas=10, confianca=0.55, deve_quebrar=True, refresh_after_block=False):
    print(f"\n🟦 Procurando imagem: {caminho_img} ...")
    
    total_blocos = 3
    for bloco in range(1, total_blocos + 1):
        for i in range(1, tentativas + 1):
            print(f"🔎 Tentando localizar (Bloco {bloco}/{total_blocos} - Tentativa {i}/{tentativas})...")

            try:
                pos = pyautogui.locateCenterOnScreen(caminho_img, confidence=confianca)
            except pyautogui.ImageNotFoundException:
                pos = None
            except Exception as e:
                print(f"⚠ Erro inesperado: {e}")
                pos = None

            if pos:
                print(f"✔ Imagem encontrada em {pos}")
                return pos

            # Pausa curta entre tentativas do mesmo bloco
            time.sleep(0.5)

        if bloco < total_blocos:
            print(f"⏳ Bloco {bloco} finalizado sem sucesso. Aguardando 3 segundos para iniciar o próximo bloco...")
            
            if refresh_after_block:
                print("🔄 refresh_after_block=True: Pressionando Ctrl+F5 para atualizar a página...")
                pyautogui.hotkey('ctrl', 'f5')
                time.sleep(10) # Aguarda um pouco mais para a página recarregar
            else:
                time.sleep(3)

    if deve_quebrar:
        raise Exception(f"❌ Não foi possível localizar a imagem após {total_blocos} blocos de {tentativas} tentativas: {caminho_img}")
        pyautogui.hotkey('ctrl', 'f5')
    
    print(f"⚠️ Imagem não localizada (deve_quebrar=False): {caminho_img}")
    return None

# ---------------------------
# Exceção personalizada para parada
# ---------------------------
class StopExecution(Exception):
    pass

def verificar_parada(callback):
    if callback and callback():
        raise StopExecution("Execução interrompida pelo usuário")

def esperar(segundos, callback):
    """Espera por um tempo determinado, verificando periodicamente se deve parar"""
    steps = int(segundos / 0.1)
    for _ in range(steps):
        if callback and callback():
            raise StopExecution("Execução interrompida pelo usuário")
        time.sleep(0.1)
