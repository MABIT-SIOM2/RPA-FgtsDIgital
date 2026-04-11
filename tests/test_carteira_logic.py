import sys
import os

# Adiciona o diretório raiz ao sys.path para importar DatabaseHandler
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.database_handler import DatabaseHandler
import json

def test_date_and_carteira_logic():
    # Carrega config para teste
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config_multi.json')
    if not os.path.exists(config_path):
        print("❌ Arquivo config_multi.json não encontrado.")
        return

    with open(config_path, 'r') as f:
        config = json.load(f).get('mysql_config')
    
    db = DatabaseHandler(config)
    if not db.connect():
        print("❌ Erro ao conectar ao banco.")
        return

    print("🔍 Iniciando teste de lógica de CARTEIRA e DATAS (DATE type compatibility)...")
    
    try:
        # 1. Buscar uma empresa para teste
        cursor = db.connection.cursor(dictionary=True)
        cursor.execute("SELECT id, razao FROM empresas LIMIT 1")
        empresa_base = cursor.fetchone()
        
        if not empresa_base:
            print("⚠️ Nenhuma empresa encontrada no banco para teste.")
            return
        
        empresa_id = empresa_base['id']
        print(f"🏢 Testando com empresa: {empresa_base['razao']} (ID: {empresa_id})")

        # Garante que existe na roboFgts
        cursor.execute("SELECT id FROM roboFgts WHERE empresaId = %s", (empresa_id,))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO roboFgts (empresaId, status) VALUES (%s, 1)", (empresa_id,))
            db.connection.commit()
        
        # 2. Testar atualização simultânea (Carteira + Competência em formato amigável)
        nova_carteira = "G_TEST_ISO"
        comp_amigavel = "03/2026"
        venc_amigavel = "20/04/2026"

        print(f"📝 Atualizando Carteira para: {nova_carteira}")
        db.atualizar_empresa(empresa_id, {'carteira': nova_carteira})
        
        print(f"📝 Atualizando Competência para: {comp_amigavel} (deve virar 2026-03-01)")
        print(f"📝 Atualizando Vencimento para: {venc_amigavel} (deve virar 2026-04-20)")
        
        db.atualizar_dados_guia(empresa_id, {
            'competenciaInicial': comp_amigavel,
            'competenciaFinal': comp_amigavel,
            'vencimentoGuia': venc_amigavel
        })
        
        # 3. Verificar resultados via JOIN
        empresas_pos = db.obter_empresas_pendentes()
        verif = next((e for e in empresas_pos if e['empresa_id'] == empresa_id), None)
        
        if not verif:
            print("❌ Erro: Empresa não encontrada após atualização.")
            return

        # Validação Carteira
        if verif['carteira'] == nova_carteira:
            print("✅ CARTEIRA: OK")
        else:
            print(f"❌ CARTEIRA: FALHA (Esperado {nova_carteira}, Recebido {verif['carteira']})")

        # Validação Datas (O DatabaseHandler retorna como objeto date ou string dependendo do driver)
        # Vamos converter para string para comparar se o formatador funcionou
        comp_db = str(verif['competenciaInicial'])
        venc_db = str(verif['vencimentoGuia'])
        
        if comp_db.startswith("2026-03-01"):
            print(f"✅ COMPETÊNCIA: OK ({comp_db})")
        else:
            print(f"❌ COMPETÊNCIA: FALHA (Esperado 2026-03-01, Recebido {comp_db})")

        if venc_db.startswith("2026-04-20"):
            print(f"✅ VENCIMENTO: OK ({venc_db})")
        else:
            print(f"❌ VENCIMENTO: FALHA (Esperado 2026-04-20, Recebido {venc_db})")

    finally:
        db.disconnect()

if __name__ == "__main__":
    test_date_and_carteira_logic()
