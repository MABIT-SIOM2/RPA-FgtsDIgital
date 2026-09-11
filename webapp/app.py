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
from fpdf import FPDF

# Força UTF-8 no console do Windows para evitar erro 'charmap' com emojis nos logs
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Adiciona o diretório raiz ao path para importar DatabaseHandler
# Dentro do bundle PyInstaller, __file__ é _MEIPASS/webapp/app.py → subimos um nível para _MEIPASS
if getattr(sys, 'frozen', False):
    # Modo executável: adiciona _MEIPASS ao path
    _app_root = sys._MEIPASS
else:
    # Modo desenvolvimento: sobe um nível a partir de webapp/
    _app_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _app_root not in sys.path:
    sys.path.insert(0, _app_root)

from src.utils.database_handler import DatabaseHandler

class PDF(FPDF):
    def header(self):
        # Background no cabeçalho (largura paisagem = 297mm)
        self.set_fill_color(37, 99, 235) # Azul Primário Mabit (#2563eb)
        self.rect(0, 0, 297, 30, 'F')
        
        self.set_font('Arial', 'B', 16)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, 'FGTS DIGITAL - RELATÓRIO DE CONSULTA', 0, 1, 'C')
        
        self.set_font('Arial', 'I', 10)
        data_hora = datetime.now().strftime('%d/%m/%Y %H:%M')
        self.cell(0, 5, f'Gerado em: {data_hora}', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Página {self.page_no()}/{{nb}}', 0, 0, 'C')

app = Flask(__name__)
CORS(app)

# Carrega as configurações do MySQL do arquivo config_multi.json
def get_db_config():
    """Busca config_multi.json em múltiplos locais para suportar tanto o
    executável PyInstaller (COLLECT) quanto o ambiente de desenvolvimento.

    Ordem de busca:
    1. Ao lado do .exe (usuário pode editar manualmente)
    2. Dentro de _internal / _MEIPASS (cópia embutida no bundle)
    3. Raiz do projeto (desenvolvimento)
    """
    if getattr(sys, 'frozen', False):
        # Modo executável PyInstaller
        candidate_dirs = [
            os.path.dirname(sys.executable),  # pasta raiz do dist (ao lado do .exe)
            sys._MEIPASS,                      # _internal (onde datas '.' são copiados)
        ]
    else:
        # Modo desenvolvimento
        candidate_dirs = [
            os.path.abspath(os.path.join(os.path.dirname(__file__), '..')),
        ]

    for base in candidate_dirs:
        config_path = os.path.join(base, 'config_multi.json')
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
            db_config = config.get('mysql_config').copy()
            if 'pass' in db_config:
                db_config['password'] = db_config.pop('pass')
            return db_config

    raise FileNotFoundError(
        f"config_multi.json não encontrado. Locais verificados: {candidate_dirs}"
    )

# Helper: converte 'MM/AAAA' para ISO 'AAAA-MM-01'
def competencia_para_iso(comp_str):
    if not comp_str:
        return None
    s = str(comp_str).strip()
    if '/' in s:
        parts = s.split('/')
        if len(parts) == 2:
            mes, ano = parts
            return f"{ano}-{mes.zfill(2)}-01"
    return s if s else None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/companies', methods=['GET'])
def get_companies():
    """Retorna empresas filtradas por competência.
    ?competencia=MM/AAAA → filtra pelo mês específico.
    Sem parâmetro → retorna a competência mais recente de cada empresa.
    """
    comp_param = request.args.get('competencia')  # ex: '09/2026'
    comp_iso = competencia_para_iso(comp_param)     # ex: '2026-09-01'

    db_config = get_db_config()
    db = DatabaseHandler(db_config)
    companies = db.obter_empresas_pendentes(competencia=comp_iso)
    return jsonify(companies)

@app.route('/api/competencias', methods=['GET'])
def get_competencias():
    """Retorna lista de competências disponíveis no banco, formato MM/AAAA, ordem decrescente."""
    db_config = get_db_config()
    db = DatabaseHandler(db_config)
    competencias = db.obter_competencias_disponiveis()
    return jsonify(competencias)

@app.route('/api/groups', methods=['GET'])
def get_groups():
    db_config = get_db_config()
    db = DatabaseHandler(db_config)
    
    # Extrai carteiras da competência mais recente
    companies = db.obter_empresas_pendentes()
    groups = sorted(list(set(c.get('carteira') for c in companies if c.get('carteira'))))
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
    comp_param = data.get('competencia')  # ex: '09/2026' (opcional)
    
    if empresa_id is None or novo_status is None:
        return jsonify({'success': False, 'message': 'Dados incompletos'}), 400
        
    db_config = get_db_config()
    db = DatabaseHandler(db_config)
    success = db.toggle_empresa_status(empresa_id, novo_status, competencia=comp_param)
    
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Erro ao atualizar status'}), 500

@app.route('/api/batch-toggle-status', methods=['POST'])
def batch_toggle_status():
    data = request.json
    ids = data.get('ids')
    novo_status = data.get('status')
    comp_param = data.get('competencia')  # ex: '09/2026' (opcional)
    
    if not ids or novo_status is None:
        return jsonify({'success': False, 'message': 'Dados incompletos'}), 400
        
    db_config = get_db_config()
    db = DatabaseHandler(db_config)
    success = db.atualizar_status_lote(ids, novo_status, competencia=comp_param)
    
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
            
            # Sincroniza dados básicos da empresa (Carteira, Código, Razão)
            dados_empresa = {}
            if 'CARTEIRA' in df.columns:
                 dados_empresa['carteira'] = str(row.get('CARTEIRA', '')).strip()
            if 'CODIGO' in df.columns:
                 dados_empresa['codigo'] = str(row.get('CODIGO', '')).strip()
            if 'NOME_EMPRESA' in df.columns or 'RAZAO_SOCIAL' in df.columns:
                 nome_col = 'NOME_EMPRESA' if 'NOME_EMPRESA' in df.columns else 'RAZAO_SOCIAL'
                 dados_empresa['razao'] = str(row.get(nome_col, '')).strip()
            
            if dados_empresa:
                db.atualizar_empresa(empresa['id'], dados_empresa)

            # Mapeamento direcionado apenas para valores BASE e Competência
            comp_ini = parse_comp(row.get('COMPETENCIA', row.get('COMP_INICIAL', row.get('COMPETENCIA_INICIAL', row.get('COMPETENC', row.get('COMP', ''))))))
            comp_fim = parse_comp(row.get('COMPETENCIA_FINAL', row.get('COMP_FINAL', '')))

            # Fallback: Se não tem comp_fim, usa a comp_ini
            if not comp_fim:
                comp_fim = comp_ini

            dados_update = {
                'competenciaInicial': comp_ini,
                'competenciaFinal': comp_fim,
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
                print(f"✅ Line {index+2}: {empresa['razao']} -> {comp_ini} (Saved as DATE)")
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
        # Pega o grupo e a competência dos parâmetros da query
        selected_group = request.args.get('group')
        comp_param = request.args.get('competencia')  # ex: '09/2026'
        comp_iso = competencia_para_iso(comp_param)
        
        db_config = get_db_config()
        db = DatabaseHandler(db_config)
        companies = db.obter_empresas_pendentes(competencia=comp_iso)
        
        if not companies:
            return jsonify({'success': False, 'message': 'Nenhuma empresa encontrada para exportar'}), 404
            
        # Converte para DataFrame
        df = pd.DataFrame(companies)
        
        # Filtra pelo grupo se fornecido
        if selected_group and selected_group != 'all':
            df = df[df['carteira'] == selected_group]
            
        if df.empty:
             return jsonify({'success': False, 'message': f'Nenhuma empresa encontrada no grupo {selected_group}'}), 404

        # Mapeamento de colunas para nomes amigáveis em Português
        column_mapping = {
            'codigo': 'Código',
            'cnpj': 'CNPJ',
            'razao': 'Razão Social',
            'carteira': 'Carteira',
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
            'status': 'Status',
            'vencimentoGuia': 'Vencimento'
        }
        
        # Filtra e renomeia apenas as colunas que existem no mapping
        df_export = df[list(column_mapping.keys())].rename(columns=column_mapping)
        
        # Mapeia o status numérico para texto
        status_map = {0: 'Pendente', 1: 'A consultar', 2: 'Concluído', 3: 'Erro'}
        df_export['Status'] = df_export['Status'].map(status_map)
        
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

@app.route('/api/export-pdf', methods=['GET'])
def export_pdf():
    try:
        selected_group = request.args.get('group')
        comp_param = request.args.get('competencia')  # ex: '09/2026'
        comp_iso = competencia_para_iso(comp_param)
        db_config = get_db_config()
        db = DatabaseHandler(db_config)
        companies = db.obter_empresas_pendentes(competencia=comp_iso)
        
        if not companies:
            return jsonify({'success': False, 'message': 'Nenhuma empresa encontrada para exportar'}), 404
            
        df = pd.DataFrame(companies)
        if selected_group and selected_group != 'all':
            df = df[df['carteira'] == selected_group]
        
        nome_grupo_display = selected_group if selected_group and selected_group != 'all' else 'Todos os Grupos'
        
        if df.empty:
            return jsonify({'success': False, 'message': f'Nenhuma empresa encontrada para o grupo: {nome_grupo_display}'}), 404

        # Mapeamento amigável
        status_map = {0: 'Pendente', 1: 'A consultar', 2: 'Concluido', 3: 'Erro'}
        df['status_txt'] = df['status'].map(status_map)

        pdf = PDF(orientation='L', unit='mm', format='A4')  # Paisagem para mais espaço
        pdf.alias_nb_pages()
        pdf.add_page()
        
        # --- SUMÁRIO ---
        pdf.set_font('Arial', 'B', 12)
        pdf.set_text_color(37, 99, 235)
        pdf.cell(0, 10, f'Relatório: {nome_grupo_display}', 0, 1)
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 10, 'Sumário de Resultados', 0, 1)
        
        total = len(df)
        sucesso = len(df[df['status'] == 2])
        erros = len(df[df['status'] == 3])
        pendentes = total - sucesso - erros
        
        # Soma das colunas da tabela = 277mm (60+35+18+28+28+25+23+60)
        # Dividido em 4 quadros: 69+69+69+70 = 277mm
        pdf.set_font('Arial', '', 10)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(69, 8, f'Total: {total}', 1, 0, 'C')
        pdf.set_text_color(22, 101, 52) # Verde
        pdf.cell(69, 8, f'Sucesso: {sucesso}', 1, 0, 'C')
        pdf.set_text_color(153, 27, 27) # Vermelho
        pdf.cell(69, 8, f'Erros: {erros}', 1, 0, 'C')
        pdf.set_text_color(0, 0, 0)
        pdf.cell(70, 8, f'Pendentes: {pendentes}', 1, 1, 'C')
        pdf.ln(5)

        # --- TABELA ---
        pdf.set_font('Arial', 'B', 8)
        pdf.set_fill_color(248, 250, 252) # Fundo Light Mabit (#f8fafc)
        pdf.set_text_color(37, 99, 235) # Texto Azul Mabit
        
        # Colunas e Larguras (Total ~277mm em paisagem A4 com margens de 10mm)
        cols = [
            ('Razão Social', 60),
            ('CNPJ', 35),
            ('Comp.', 18),
            ('Base', 28),
            ('Guia', 28),
            ('Venc.', 25),
            ('Status', 23),
            ('Observação', 60)
        ]
        
        for col, width in cols:
            pdf.cell(width, 10, col, 1, 0, 'C', True)
        pdf.ln()

        pdf.set_font('Arial', '', 8)
        pdf.set_text_color(0, 0, 0)
        
        fill = False
        for _, row in df.iterrows():
            # Razão Social (Trunca se for muito grande)
            razao = str(row['razao'])[:30]
            
            pdf.cell(60, 8, razao, 1, 0, 'L', fill)
            pdf.cell(35, 8, str(row['cnpj']), 1, 0, 'C', fill)
            
            # Formata Competência (MM/AAAA)
            comp_raw = str(row['competenciaFinal'] or '-')
            comp = comp_raw
            if '-' in comp_raw and len(comp_raw) >= 10:
                try:
                    parts = comp_raw.split(' ')[0].split('-')
                    if len(parts) == 3:
                        comp = f"{parts[1]}/{parts[0]}"
                except:
                    pass
            pdf.cell(18, 8, comp, 1, 0, 'C', fill)
            
            # Formata moeda - Total Base
            v_base = f"{float(row['totalBase'] or 0):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            pdf.cell(28, 8, v_base, 1, 0, 'R', fill)

            # Formata moeda - Total Guia
            v_guia = f"{float(row['totalGuia'] or 0):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            pdf.cell(28, 8, v_guia, 1, 0, 'R', fill)
            
            # Vencimento (Tenta formatar para BR se for ISO)
            venc_raw = str(row['vencimentoGuia'] or '-')
            venc = venc_raw
            if '-' in venc_raw and len(venc_raw) >= 10:
                try:
                    parts = venc_raw.split(' ')[0].split('-')
                    if len(parts) == 3:
                        venc = f"{parts[2]}/{parts[1]}/{parts[0]}"
                except:
                    pass
            
            pdf.cell(25, 8, venc, 1, 0, 'C', fill)

            # Status com cor
            s = row['status']
            if s == 2: pdf.set_text_color(22, 101, 52)
            elif s == 3: pdf.set_text_color(153, 27, 27)
            else: pdf.set_text_color(0, 0, 0)
            
            pdf.cell(23, 8, str(row['status_txt']), 1, 0, 'C', fill)
            pdf.set_text_color(0, 0, 0)
            
            # Obs (60mm de largura, cabe ~40 caracteres com fonte 8)
            obs_texto = str(row.get('obs', '') or '')
            if obs_texto.lower() == 'nan': obs_texto = ''
            obs_texto = obs_texto[:45]
            pdf.cell(60, 8, obs_texto, 1, 1, 'L', fill)
            
            fill = not fill

        # Output
        pdf_output = io.BytesIO()
        # fpdf2 usa output() que retorna os bytes ou escreve no arquivo. 
        # No fpdf2 moderno, podemos usar output(dest='S') ou output() dependendo da versão. 
        # Vamos usar bytearray(pdf.output()) se for fpdf2.
        pdf_bytes = pdf.output()
        pdf_output.write(pdf_bytes)
        pdf_output.seek(0)

        nome_grupo = selected_group if selected_group and selected_group != 'all' else 'Geral'
        filename = f"Relatorio_FGTS_{nome_grupo}_{datetime.now().strftime('%d_%m_%Y_%H%M')}.pdf"
        
        return send_file(
            pdf_output,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f"Erro ao gerar PDF: {str(e)}"}), 500

if __name__ == '__main__':
    # Executa migration de schema na inicialização (idempotente)
    try:
        _db_config = get_db_config()
        _db = DatabaseHandler(_db_config)
        _db.executar_migration()
    except Exception as _e:
        print(f"⚠️ Não foi possível executar migration: {_e}")

    app.run(debug=True, port=5001)
