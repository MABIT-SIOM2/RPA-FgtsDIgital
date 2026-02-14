import sys
import os
import pyperclip
import time
# Adiciona o diretório raiz ao path para permitir importações do src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.fgts_digital_site import extrair_dados_tabela_detalhada

def test_extracao_manual():
    print("🧪 Iniciando Teste de Extração Manual...")
    print("Siga os passos:")
    print("1. Vá para o site do FGTS Digital na tela com a tabela aberta.")
    print("2. Pressione qualquer tecla aqui no terminal quando estiver pronto.")
    input("Aguardando... <ENTER>")
    time.sleep(3)
    print("\n--- TESTE 1: MODO COM CONSIGNADO (9 colunas, busca 'Total da Guia') ---")
    resultados, total = extrair_dados_tabela_detalhada(alerta_ativo=False)
    print(f"📊 Linhas extraídas: {len(resultados)}")
    for res in resultados:
        print(f"  - {res}")
    print(f"💰 Total capturado: {total}")
    
    valido_1 = len(resultados) > 0 and total > 0
    print(f"✅ VALIDAÇÃO TESTE 1: {'SUCESSO' if valido_1 else 'FALHA'}")

    print("\n--- TESTE 2: MODO SEM CONSIGNADO (8 colunas, busca 'Total' simples) ---")
    resultados_sem, total_sem = extrair_dados_tabela_detalhada(alerta_ativo=True)
    print(f"📊 Linhas extraídas: {len(resultados_sem)}")
    for res in resultados_sem:
        print(f"  - {res}")
    print(f"💰 Total capturado: {total_sem}")
    
    valido_2 = len(resultados_sem) > 0 and total_sem > 0
    print(f"✅ VALIDAÇÃO TESTE 2: {'SUCESSO' if valido_2 else 'FALHA'}")
    
    print("\n" + "="*40)
    print("🏁 RESUMO FINAL DO TESTE:")
    print(f"Modo Com Consignado: {'OK' if valido_1 else 'ERRO'}")
    print(f"Modo Sem Consignado: {'OK' if valido_2 else 'ERRO'}")
    print("="*40)

if __name__ == "__main__":
    test_extracao_manual()
