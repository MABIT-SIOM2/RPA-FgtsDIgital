import re

def test_regex():
    # Test cases: (input_text, expected_results)
    test_cases = [
        (
            "FGTS Mensal R$ 100,50 FGTS 13º R$ 50,25 Empréstimo Consignado R$ 20,10 Total da Guia R$ 170,85",
            {'valor_fgts': 100.5, 'valor_fgts13': 50.25, 'valor_consignado': 20.1, 'total_guia': 170.85}
        ),
        (
            "VALOR DA GUIA FGTS 500,00 VALOR DA GUIA FGTS 13º 250,00 VALOR CONSIGNADO 75,00 TOTAL A RECOLHER 825,00",
            {'valor_fgts': 500.0, 'valor_fgts13': 250.0, 'valor_consignado': 75.0, 'total_guia': 825.0}
        ),
        (
            "FGTS Digital Mensal 123,45 FGTS Digital 13º 0,00 Consignado 10,00 Total da Guia 133,45",
            {'valor_fgts': 123.45, 'valor_fgts13': 0.0, 'valor_consignado': 10.0, 'total_guia': 133.45}
        ),
        (
             "Item sem acento: Emprestimo Consignado 44,44",
             {'valor_consignado': 44.44}
        ),
        (
             "Plural: Empréstimos Consignados 99,99",
             {'valor_consignado': 99.99}
        )
    ]

    padroes_resumo = {
        'total_guia': [r'Total da Guia\s+(?:R\$\s*)?([\d.]+)', r'Total a recolher\s+(?:R\$\s*)?([\d.]+)'],
        'valor_fgts': [r'FGTS\s+Mensal\s+(?:R\$\s*)?([\d.]+)', r'Valor\s+da\s+Guia\s+FGTS\s+(?:R\$\s*)?([\d.]+)', r'FGTS\s+Digital\s+Mensal\s+(?:R\$\s*)?([\d.]+)'],
        'valor_fgts13': [r'FGTS\s+13º\s+(?:R\$\s*)?([\d.]+)', r'Valor\s+da\s+Guia\s+FGTS\s+13º\s+(?:R\$\s*)?([\d.]+)', r'FGTS\s+Digital\s+13º\s+(?:R\$\s*)?([\d.]+)'],
        'valor_consignado': [r'Empr.stimo\s+Consignado\s+(?:R\$\s*)?([\d.]+)', r'(?:Valor\s+)?Consignado\s+(?:R\$\s*)?([\d.]+)', r'Empr.stimos\s+Consignados\s+(?:R\$\s*)?([\d.]+)']
    }

    for text, expected in test_cases:
        print(f"\n--- Testing text: {text}")
        # Normalize as in the original code
        text_norm = text.replace('.', '').replace(',', '.')
        
        results = {}
        for key, patterns in padroes_resumo.items():
            for p in patterns:
                matches = list(re.finditer(p, text_norm, re.IGNORECASE))
                if matches:
                    results[key] = float(matches[-1].group(1))
                    break
        
        for key, exp_val in expected.items():
            got_val = results.get(key)
            if got_val == exp_val:
                print(f"✅ {key}: {got_val} == {exp_val}")
            else:
                print(f"❌ {key}: Got {got_val}, Expected {exp_val}")

if __name__ == "__main__":
    test_regex()
