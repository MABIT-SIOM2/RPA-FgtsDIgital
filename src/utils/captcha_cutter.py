import cv2
import os
import time

def recortar_captcha_completo(caminho_imagem, pasta_base="captchas_dataset"):
    """
    Recorta o texto de instrução (topo) e as 9 imagens da grade 3x3.
    """
    if not os.path.exists(caminho_imagem):
        print(f"Erro: Imagem {caminho_imagem} não encontrada.")
        return

    # Pastas de saída
    pasta_instrucoes = os.path.join(pasta_base, "instrucoes")
    pasta_tiles = os.path.join(pasta_base, "tiles")
    
    for p in [pasta_instrucoes, pasta_tiles]:
        if not os.path.exists(p):
            os.makedirs(p)

    # Carrega a imagem
    img = cv2.imread(caminho_imagem)
    height, width, _ = img.shape
    tstamp = int(time.time())

    # 1. Recortar Instrução (Geralmente os primeiros 15%~20% do topo)
    # Ajuste estas proporções conforme necessário
    h_instrucao = int(height * 0.20)
    instrucao_img = img[0:h_instrucao, 0:width]
    cv2.imwrite(os.path.join(pasta_instrucoes, f"titulo_{tstamp}.png"), instrucao_img)
    print("📝 Texto de instrução extraído.")

    # 2. Recortar Grade 3x3 (O restante da imagem)
    # Ignora o topo e foca na grade
    grade_img = img[h_instrucao:height, 0:width]
    g_h, g_w, _ = grade_img.shape
    
    h_step = g_h // 3
    w_step = g_w // 3

    for r in range(3):
        for c in range(3):
            y1, y2 = r * h_step, (r + 1) * h_step
            x1, x2 = c * w_step, (c + 1) * w_step
            tile = grade_img[y1:y2, x1:x2]
            cv2.imwrite(os.path.join(pasta_tiles, f"tile_{tstamp}_{r}_{c}.png"), tile)

    print(f"✅ Grade 3x3 recortada em 9 tiles em: {pasta_tiles}")

if __name__ == "__main__":
    # Ajuste o caminho para uma imagem capturada real
    caminho_teste = "path_para_seu_print.png"
    if os.path.exists(caminho_teste):
        recortar_captcha_completo(caminho_teste)
