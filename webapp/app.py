import os
import sys
import json
import re
import unicodedata
import io
from datetime import datetime
import pandas as pd
from flask import Flask, render_template, jsonify, request, send_file
from flask_cors import CORS

# Força UTF-8 no console do Windows para evitar erro 'charmap' com emojis nos logs
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Adiciona o diretório raiz ao path para importar DatabaseHandler
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.database_handler import DatabaseHandler

app = Flask(__name__)
CORS(app)

# Carrega as configurações do MySQL do arquivo config_multi.json
def get_db_config():
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config_multi.json'))
    with open(config_path, 'r') as f:
        config = json.load(f)
    db_config = config.get('mysql_config').copy()
    if 'pass' in db_config:
        db_config['password'] = db_config.pop('pass')
    return db_config

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/companies', methods=['GET'])
def get_companies():
    db_config = get_db_config()
    db = DatabaseHandler(db_config)
    
    # Vamos usar obter_empresas_pendentes como base, mas para o dashboard
    # talvez queiramos TODAS ou um subconjunto. Como obter_empresas_pendentes
    # já tem o JOIN com roboFgts, vamos usar ela.
    # Nota: Se r.status = 0 são apenas pendentes. No dashboard podemos querer mais.
    # Por enquanto, mantemos a lógica do DatabaseHandler.
    
    companies = db.obter_empresas_pendentes()
    return jsonify(companies)

@app.route('/api/groups', methods=['GET'])
def get_groups():
    db_config = get_db_config()
    db = DatabaseHandler(db_config)
    
    # Como não temos um método específico para grupos, vamos extrair dos dados
    companies = db.obter_empresas_pendentes()
    groups = sorted(list(set(c.get('grupo') for c in companies if c.get('grupo'))))
    return jsonify(groups)

@app.route('/api/update', methods=['POST'])
def update_company():
    data = request.json
    empresa_id = data.get('empresa_id')
    
    if not empresa_id:
        return jsonify({'success': False, 'message': 'ID da empresa não fornecido'}), 400
        
    # Proteção: Impede que colunas de extração (Guia) sejam atualizadas manualmente
    keys_to_remove = ['valorGuiaFgts', 'valorGuiaFgts13', 'valorGuiaConsignado', 'totalGuia']
    cleaned_data = {k: v for k, v in data.items() if k not in keys_to_remove}
    
    db_config = get_db_config()
    db = DatabaseHandler(db_config)
    
    # Atualiza usando o método existente
    success = db.atualizar_dados_guia(empresa_id, cleaned_data)
    
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Erro ao atualizar no banco de dados'}), 500

@app.route('/api/toggle-status', methods=['POST'])
def toggle_status():
    data = request.json
    empresa_id = data.get('empresa_id')
    novo_status = data.get('status')
    
    if empresa_id is None or novo_status is None:
        return jsonify({'success': False, 'message': 'Dados incompletos'}), 400
        
    db_config = get_db_config()
    db = DatabaseHandler(db_config)
    success = db.toggle_empresa_status(empresa_id, novo_status)
    
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Erro ao atualizar status'}), 500

@app.route('/api/batch-toggle-status', methods=['POST'])
def batch_toggle_status():
    data = request.json
    ids = data.get('ids')
    novo_status = data.get('status')
    
    if not ids or novo_status is None:
        return jsonify({'success': False, 'message': 'Dados incompletos'}), 400
        
    db_config = get_db_config()
    db = DatabaseHandler(db_config)
    success = db.atualizar_status_lote(ids, novo_status)
    
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Erro ao atualizar em lote'}), 500

@app.route('/api/upload-database', methods=['POST'])
def upload_database():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'Nenhum arquivo enviado'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'Nome de arquivo vazio'}), 400

    try:
        # Lê o arquivo Excel - Forçamos a leitura de todas as colunas como string para evitar 
        # interpretações errôneas do Pandas (como tratar 13.467,00 como float indesejado)
        df = pd.read_excel(file, dtype=str)
        
        # Função para normalizar nomes de colunas
        def normalize_col(name):
            n = str(name).strip().upper()
            n = unicodedata.normalize('NFKD', n).encode('ASCII', 'ignore').decode('ASCII')
            n = re.sub(r'[^A-Z0-9]', '_', n)
            return re.sub(r'_+', '_', n).strip('_')

        df.columns = [normalize_col(c) for c in df.columns]
        print(f"📊 DEBUG - Colunas Identificadas: {df.columns.tolist()}")
        
        if 'CNPJ' not in df.columns:
            return jsonify({'success': False, 'message': 'Coluna CNPJ não encontrada. Verifique o cabeçalho.'}), 400

        db_config = get_db_config()
        db = DatabaseHandler(db_config)
        
        results = {'updated': 0, 'errors': 0, 'details': []}
        
        # Função de parsing de valor monetário BR ultra-robusta
        def parse_br_valor(val):
            if pd.isna(val) or val is None: return 0.0
            
            s = str(val).strip().replace('R$', '').replace(' ', '')
            if not s or s.lower() == 'nan': return 0.0
            
            # Se já for um float puro (ex: "13467.0")
            if re.match(r'^\d+\.\d+$', s):
                return float(s)
            
            # Se estiver no formato BR "13.467,89" ou "13467,89"
            if ',' in s:
                # Remove pontos de milhar e troca vírgula por ponto decimal
                s = s.replace('.', '').replace(',', '.')
            
            # Remove qualquer caractere que não seja dígito ou ponto
            s = re.sub(r'[^0-9.]', '', s)
            
            try:
                val_float = float(s)
                return round(val_float, 2)
            except:
                return 0.0

        # Função para formatar competência (MM/AAAA)
        def parse_comp(val):
            if pd.isna(val) or val is None: return ''
            s = str(val).strip()
            if not s or s.lower() == 'nan' or s == '-': return ''
            
            # Formatos comuns: "12/2025", "2025-12-01 00:00:00", "45657" (data excel serial)
            # Se já estiver em MM/AAAA
            if re.match(r'^\d{2}/\d{4}$', s): return s
            
            try:
                # Tenta converter via Pandas (datas ISO, etc)
                dt = pd.to_datetime(s)
                return dt.strftime('%m/%Y')
            except:
                # Se for apenas MM/AA, tenta converter para MM/AAAA
                if re.match(r'^\d{2}/\d{2}$', s):
                    m, a = s.split('/')
                    return f"{m}/20{a}"
                return s

        print(f"🔄 Iniciando processamento de {len(df)} linhas...")

        for index, row in df.iterrows():
            cnpj_raw = str(row.get('CNPJ', '')).strip()
            if not cnpj_raw or cnpj_raw.lower() == 'nan':
                results['details'].append(f"Linha {index+2}: CNPJ vazio ou inválido.")
                continue
            
            cnpj = ''.join(filter(str.isdigit, cnpj_raw))
            empresa = db.buscar_empresa_por_cnpj(cnpj)
            
            if not empresa:
                results['errors'] += 1
                results['details'].append(f"Linha {index+2}: CNPJ {cnpj_raw} não localizado no cadastro de empresas.")
                continue
            
            # Sincroniza dados básicos da empresa (Grupo, Código, Razão)
            dados_empresa = {}
            if 'GRUPO' in df.columns:
                 dados_empresa['grupo'] = str(row.get('GRUPO', '')).strip()
            if 'CODIGO' in df.columns:
                 dados_empresa['codigo'] = str(row.get('CODIGO', '')).strip()
            if 'NOME_EMPRESA' in df.columns or 'RAZAO_SOCIAL' in df.columns:
                 nome_col = 'NOME_EMPRESA' if 'NOME_EMPRESA' in df.columns else 'RAZAO_SOCIAL'
                 dados_empresa['razao'] = str(row.get(nome_col, '')).strip()
            
            if dados_empresa:
                db.atualizar_empresa(empresa['id'], dados_empresa)

            # Mapeamento direcionado apenas para valores BASE e Competência
            dados_update = {
                'competenciaInicial': parse_comp(row.get('COMPETENC', row.get('COMP_INICIAL', row.get('COMPETENCIA_INICIAL', '')))),
                'competenciaFinal': parse_comp(row.get('COMPETENCIA_FINAL', row.get('COMP_FINAL', ''))),
                'valorFgts': parse_br_valor(row.get('VALOR_FGTS', row.get('VALOR_FGTS_BASE', 0))),
                'valorFgts13': parse_br_valor(row.get('VALOR_FGTS13', row.get('FGTS_13_BASE', row.get('FGTS_13_O_BASE', 0)))),
                'valorConsignado': parse_br_valor(row.get('VALOR_CONSIGNADO', row.get('CONSIGNADO_BASE', 0))),
                'totalBase': parse_br_valor(row.get('TOTAL', row.get('TOTAL_BASE', 0))),
                'vencimentoGuia': row.get('VENCIMENTO', row.get('VENCIMENTO_GUIA', row.get('VENC_GUIA', ''))),
                'status': 1 # Quando sobe da planilha, vai direto para "A Consultar"
                # IMPORTANTE: Colunas de extração (valorGuiaFgts, etc.) NÃO são incluídas aqui
            }
            
            # Recalcula totalBase se vier zerado
            if dados_update['totalBase'] == 0:
                soma = dados_update['valorFgts'] + dados_update['valorFgts13'] + dados_update['valorConsignado']
                dados_update['totalBase'] = round(soma, 2)

            if db.atualizar_dados_guia(empresa['id'], dados_update):
                results['updated'] += 1
            else:
                results['errors'] += 1
                results['details'].append(f"Linha {index+2}: Erro técnico ao atualizar {empresa['razao']}.")

        return jsonify({
            'success': True, 
            'message': f"Processamento concluído. {results['updated']} atualizadas, {results['errors']} falhas.",
            'results': results
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f"Erro crítico: {str(e)}"}), 500

@app.route('/api/export', methods=['GET'])
def export_report():
    try:
        # Pega o grupo do parâmetro da query
        selected_group = request.args.get('group')
        
        db_config = get_db_config()
        db = DatabaseHandler(db_config)
        companies = db.obter_empresas_pendentes()
        
        if not companies:
            return jsonify({'success': False, 'message': 'Nenhuma empresa encontrada para exportar'}), 404
            
        # Converte para DataFrame
        df = pd.DataFrame(companies)
        
        # Filtra pelo grupo se fornecido
        if selected_group and selected_group != 'all':
            df = df[df['grupo'] == selected_group]
            
        if df.empty:
             return jsonify({'success': False, 'message': f'Nenhuma empresa encontrada no grupo {selected_group}'}), 404

        # Mapeamento de colunas para nomes amigáveis em Português
        column_mapping = {
            'codigo': 'Código',
            'cnpj': 'CNPJ',
            'razao': 'Razão Social',
            'grupo': 'Grupo',
            'competenciaInicial': 'Comp. Inicial',
            'competenciaFinal': 'Comp. Final',
            'valorFgts': 'FGTS (Base)',
            'valorFgts13': 'FGTS 13º (Base)',
            'valorConsignado': 'Consignado (Base)',
            'totalBase': 'Total Base',
            'valorGuiaFgts': 'Guia FGTS',
            'valorGuiaFgts13': 'Guia FGTS 13º',
            'valorGuiaConsignado': 'Guia Consignado',
            'totalGuia': 'Total Guia',
            'status': '_status_num',
            'statusOnvio': 'Status',
            'vencimentoGuia': 'Vencimento'
        }
        
        # Filtra e renomeia apenas as colunas que existem no mapping
        df_export = df[list(column_mapping.keys())].rename(columns=column_mapping)
        
        # Mapeia o status numérico para texto como fallback se statusOnvio estiver vazio
        status_map = {0: 'Pendente', 1: 'A consultar', 2: 'Concluído', 3: 'Erro'}
        df_export['Status'] = df_export['Status'].fillna('').replace('', None)
        df_export['Status'] = df_export['Status'].where(
            df_export['Status'].notna(),
            df_export['_status_num'].map(status_map)
        )
        
        # Remove a coluna auxiliar do status numérico
        df_export.drop(columns=['_status_num'], inplace=True)
        
        # Cria um buffer de bytes para o arquivo Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_export.to_excel(writer, index=False, sheet_name='Relatório FGTS')
            
        output.seek(0)
        
        # Nome do arquivo personalizado com o grupo
        nome_grupo = selected_group if selected_group and selected_group != 'all' else 'Geral'
        filename = f"Relatorio_FGTS_{nome_grupo}_{datetime.now().strftime('%d_%m_%Y_%H%M')}.xlsx"
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )     
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f"Erro ao exportar: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
