import sys
import os

# Adiciona a raiz do projeto ao sys.path para permitir o import de 'src'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.database_handler import DatabaseHandler
import json

def testar_dados_mysql():
    print("🧪 Iniciando Teste de Retorno de Dados MySQL...")
    
    # ---------------------------------------------------------
    # PREENCHA AQUI SEUS DADOS PARA O TESTE
    # ---------------------------------------------------------
    config = {
        'host': 'mysql831.umbler.com',
        'port': 41890,
        'user': 'vexmabit',         # Insira seu usuário
        'password': 'vexmabit10', # Insira sua senha
        'database': 'vex'     # Insira o banco
    }
    # ---------------------------------------------------------

    handler = DatabaseHandler(config)
    
    print(f"🔗 Conectando ao host: {config['host']}:{config['port']}...")
    if handler.connect():
        print("✅ Conexão estabelecida!")
        
        print("🔍 Executando query de busca (status = 0)...")
        empresas = handler.obter_empresas_pendentes()
        
        if not empresas:
            print("⚠️ Nenhuma empresa pendente (status=0) foi encontrada ou acesso negado à tabela.")
        else:
            print(f"📊 Foram encontradas {len(empresas)} empresas pendentes.\n")
            
            # Cabeçalho expandido conforme a captura de tela
            header = f"{'id':<5} | {'codigo':<6} | {'cnpj':<15} | {'v_fgts':<10} | {'v_fgts13':<10} | {'v_consig':<10} | {'t_base':<10} | {'g_fgts':<10} | {'g_fgts13':<10} | {'g_consig':<10} | {'t_guia':<10} | {'st'}"
            print(header)
            print("-" * len(header))
            
            for e in empresas:
                print(f"{str(e.get('empresa_id')):<5} | "
                      f"{str(e.get('codigo')):<6} | "
                      f"{str(e.get('cnpj')):<15} | "
                      f"{str(e.get('valorFgts')):<10} | "
                      f"{str(e.get('valorFgts13')):<10} | "
                      f"{str(e.get('valorConsignado')):<10} | "
                      f"{str(e.get('totalBase')):<10} | "
                      f"{str(e.get('valorGuiaFgts')):<10} | "
                      f"{str(e.get('valorGuiaFgts13')):<10} | "
                      f"{str(e.get('valorGuiaConsignado')):<10} | "
                      f"{str(e.get('totalGuia')):<10} | "
                      f"{str(e.get('status'))}")
                
        handler.disconnect()
    else:
        print("❌ Falha na conexão. Verifique se o IP está liberado no firewall ou se os dados de acesso estão corretos.")

if __name__ == "__main__":
    testar_dados_mysql()
