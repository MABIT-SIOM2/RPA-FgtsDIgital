import pandas as pd
import re

# Mock da função de parsing para teste isolado
def parse_comp(val):
    if pd.isna(val) or val is None: return ''
    s = str(val).strip()
    if not s or s.lower() == 'nan' or s == '-': return ''
    
    # Limpeza: Remove timestamps residuais (ex: 2025-12-01 00:00:00 -> 2025-12-01)
    s = s.split(' ')[0]
    
    # Se já estiver em MM/AAAA
    if re.match(r'^\d{2}/\d{4}$', s): return s
    
    # Se for apenas MM/AA (ex: 12/25), converte para MM/20AA
    if re.match(r'^\d{2}/\d{2}$', s):
        m, a = s.split('/')
        return f"{m}/20{a}"

    try:
        # Tenta converter via Pandas (datas ISO, etc)
        dt = pd.to_datetime(s, errors='coerce')
        if pd.notna(dt):
            return dt.strftime('%m/%Y')
    except:
        pass
    
    # Se falhou mas tem o formato numérico do Excel (ex: 45657)
    if s.isdigit() and len(s) >= 5:
        try:
            dt = pd.to_datetime(int(s), unit='D', origin='1899-12-30')
            return dt.strftime('%m/%Y')
        except:
            pass

    return s

def test():
    test_cases = [
        ("12/2025", "12/2025"),
        ("2025-12-01 00:00:00", "12/2025"),
        ("12/25", "12/2025"),
        ("01/2024", "01/2024"),
        ("45657", "01/2025"), # 45657 no Excel é +- Jan/2025
        (None, ""),
        ("-", ""),
        ("nan", "")
    ]

    print("🧪 Iniciando testes de parsing de competência...")
    all_passed = True
    for val, expected in test_cases:
        result = parse_comp(val)
        if result == expected:
            print(f"✅ Input: '{val}' -> Result: '{result}'")
        else:
            print(f"❌ Input: '{val}' -> Expected: '{expected}', Got: '{result}'")
            all_passed = False
    
    if all_passed:
        print("\n✨ Todos os testes passaram!")
    else:
        print("\n🛑 Alguns testes falharam.")

if __name__ == "__main__":
    test()
