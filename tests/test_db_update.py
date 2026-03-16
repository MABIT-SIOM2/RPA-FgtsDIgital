import sys
import os
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.database_handler import DatabaseHandler

def test_update_company():
    # Load config
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config_multi.json')
    if not os.path.exists(config_path):
        print("Config not found")
        return

    with open(config_path, 'r') as f:
        config = json.load(f)
    
    db_config = config.get('mysql_config')
    db = DatabaseHandler(db_config)
    
    # 1. Find a company to test
    print("Finding a company...")
    companies = db.obter_empresas_pendentes()
    if not companies:
        print("No companies found to test")
        return
    
    test_company = companies[0]
    original_group = test_company.get('grupo', '')
    empresa_id = test_company['empresa_id']
    cnpj = test_company['cnpj']
    
    print(f"Testing with company: {test_company['razao']} (ID: {empresa_id}, CNPJ: {cnpj})")
    print(f"Original Group: {original_group}")
    
    # 2. Update to a new group
    new_group = "TEST_GROUP_GI"
    print(f"Updating to: {new_group}...")
    success = db.atualizar_empresa(empresa_id, {'grupo': new_group})
    
    if success:
        print("Update call successful")
        # Verify
        db.disconnect() # Reconnect to be sure
        updated_companies = db.obter_empresas_pendentes()
        updated_company = next((c for c in updated_companies if c['empresa_id'] == empresa_id), None)
        
        if updated_company and updated_company['grupo'] == new_group:
            print(f"✅ VERIFIED: Group updated to {new_group}")
        else:
            print(f"❌ FAILED: Group is {updated_company['grupo'] if updated_company else 'N/A'}")
            
        # 3. Revert to original
        print(f"Reverting to original group: {original_group}...")
        db.atualizar_empresa(empresa_id, {'grupo': original_group})
    else:
        print("Update call failed")

if __name__ == "__main__":
    test_update_company()
