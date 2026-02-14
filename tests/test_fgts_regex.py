import re
import datetime

def validar_vencimento_logica(data_venc_str):
    try:
        data_venc = datetime.datetime.strptime(data_venc_str, "%d/%m/%Y")
        agora = datetime.datetime.now()
        
        # Verifica se é o mês e ano atual
        if data_venc.month == agora.month and data_venc.year == agora.year:
            # Verifica se o dia é 18, 19 ou 20
            if data_venc.day in [18, 19, 20]:
                return True, "✅ Válida"
            else:
                return False, f"❌ Inválida (Dia {data_venc.day} não é 18, 19 ou 20)"
        else:
            return False, f"❌ Inválida (Mês/Ano {data_venc.month}/{data_venc.year} não é o atual)"
    except Exception as e:
        return False, f"⚠️ Erro: {e}"

def test_regex():
    # Exemplo de texto que seria capturado pelo Ctrl+A/Ctrl+C
    texto_exemplo = """
    Todos os valores exibidos estão expressos em reais (R$).
    Vencimento da Guia: 20/02/2026
    12/2025 20/01/2026 1 105,24 0,00 0,00 0,00 105,24
    """
    
    # 1. Teste Vencimento da Guia
    padrao_vencimento = r'Vencimento\s+da\s+Guia:\s*(\d{2}/\d{2}/\d{4})'
    match_venc = re.search(padrao_vencimento, texto_exemplo, re.IGNORECASE)
    
    if match_venc:
        data_ext = match_venc.group(1)
        print(f"Data extraída: {data_ext}")
        valido, msg = validar_vencimento_logica(data_ext)
        print(f"Resultado Validação: {msg}")
    
    # Testes unitários da lógica
    dates_to_test = ["18/02/2026", "19/02/2026", "20/02/2026", "17/02/2026", "21/02/2026", "18/03/2026"]
    print("\n--- Testes em Lote ---")
    for d in dates_to_test:
        v, m = validar_vencimento_logica(d)
        print(f"{d}: {m}")

if __name__ == "__main__":
    test_regex()
