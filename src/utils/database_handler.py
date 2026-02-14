import mysql.connector
from mysql.connector import Error

class DatabaseHandler:
    def __init__(self, config):
        """
        Inicializa o handler com as configurações do banco.
        config: dicionário com {'user', 'password', 'host', 'port', 'database'}
        """
        self.config = config
        
        # Normalização de chaves para mysql.connector
        if self.config and 'pass' in self.config and 'password' not in self.config:
            self.config['password'] = self.config.pop('pass')

        self.connection = None

    def connect(self):
        try:
            if not self.config:
                return False
            self.connection = mysql.connector.connect(**self.config)
            return True
        except Error as e:
            print(f"❌ Erro ao conectar ao MySQL: {e}")
            return False

    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()

    def obter_empresas_pendentes(self, filtrar_onvio=False):
        """
        Executa a query fornecida pelo usuário para buscar empresas pendentes.
        Se filtrar_onvio=True, filtra apenas empresas com statusOnvio = 'A publicar'.
        """
        if not self.connect():
            return []

        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT 
                    e.id as empresa_id,
                    e.onvioId,
                    e.codigo,
                    e.cnpj,
                    e.razao,
                    e.grupo,
                    r.valorFgts,
                    r.valorFgts13,
                    r.valorConsignado,
                    r.totalBase,
                    r.valorGuiaFgts,
                    r.valorGuiaFgts13,
                    r.valorGuiaConsignado,
                    r.totalGuia,
                    r.status,
                    r.statusOnvio,
                    r.competenciaInicial,
                    r.competenciaFinal,
                    r.vencimentoGuia
                FROM empresas e
                INNER JOIN roboFgts r
                    ON r.empresaId = e.id
            """
            
            # Adiciona filtro se for para Onvio
            if filtrar_onvio:
                query += " WHERE r.statusOnvio = 'A publicar'"
            
            cursor.execute(query)
            resultados = cursor.fetchall()
            cursor.close()
            return resultados
        except Error as e:
            print(f"❌ Erro ao buscar empresas: {e}")
            return []
        finally:
            self.disconnect()

    def atualizar_dados_guia(self, empresa_id, dados):
        """
        Atualiza campos na tabela roboFgts de forma dinâmica.
        Apenas as chaves presentes no dicionário 'dados' serão atualizadas.
        """
        if not self.connect():
            return False

        try:
            cursor = self.connection.cursor()
            
            # 1. Limpeza de valores (garantir float 2 casas com arredondamento correto)
            def clean_val(v):
                try:
                    val_float = float(v)
                    return round(val_float, 2)
                except:
                    return 0.0

            # Mapeamento de chaves do dicionário para colunas do banco
            mapping = {
                'valorFgts': 'valorFgts',
                'valorFgts13': 'valorFgts13',
                'valorConsignado': 'valorConsignado',
                'totalBase': 'totalBase',
                'valorGuiaFgts': 'valorGuiaFgts',
                'valorGuiaFgts13': 'valorGuiaFgts13',
                'valorGuiaConsignado': 'valorGuiaConsignado',
                'totalGuia': 'totalGuia',
                'status': 'status',
                'statusOnvio': 'statusOnvio',
                'competenciaInicial': 'competenciaInicial',
                'competenciaFinal': 'competenciaFinal',
                'vencimentoGuia': 'vencimentoGuia'
            }

            # 2. Processar valores especiais (datas)
            cleaned_dados = {}
            for key, val in dados.items():
                if key not in mapping:
                    continue
                
                db_col = mapping[key]
                
                if key == 'vencimentoGuia' and val and "/" in str(val):
                    try:
                        dia, mes, ano = str(val).split("/")
                        cleaned_dados[db_col] = f"{ano}-{mes}-{dia}"
                    except:
                        cleaned_dados[db_col] = val
                elif key in ['status', 'statusOnvio', 'competenciaInicial', 'competenciaFinal', 'vencimentoGuia']:
                    cleaned_dados[db_col] = val
                else:
                    # Campos numéricos
                    cleaned_dados[db_col] = clean_val(val)

            if not cleaned_dados:
                return True # Nada para atualizar

            # 3. Verificar existência para decidir entre INSERT ou UPDATE
            cursor.execute("SELECT id FROM roboFgts WHERE empresaId = %s", (empresa_id,))
            existe = cursor.fetchone()

            if existe:
                # UPDATE DINÂMICO
                set_clause = ", ".join([f"{col} = %s" for col in cleaned_dados.keys()])
                params = list(cleaned_dados.values()) + [empresa_id]
                query = f"UPDATE roboFgts SET {set_clause} WHERE empresaId = %s"
            else:
                # INSERT
                cols = ["empresaId"] + list(cleaned_dados.keys())
                placeholders = ", ".join(["%s"] * len(cols))
                params = [empresa_id] + list(cleaned_dados.values())
                query = f"INSERT INTO roboFgts ({', '.join(cols)}) VALUES ({placeholders})"

            cursor.execute(query, params)
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"❌ Erro ao atualizar banco de dados: {e}")
            return False
        finally:
            self.disconnect()


    def marcar_status_erro(self, empresa_id, mensagem):
        """
        Pode ser usado para marcar um erro específico ou mudar o status para 'falha'.
        """
        if not self.connect(): return False
        try:
            cursor = self.connection.cursor()
            query = "UPDATE roboFgts SET status = 3 WHERE empresaId = %s" # 3 = Erro/Falha
            cursor.execute(query, (empresa_id,))
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"❌ Erro ao marcar status de erro: {e}")
            return False
        finally:
            self.disconnect()

    def toggle_empresa_status(self, empresa_id, novo_status):
        """
        Alterna o status da empresa entre Ativo (1) e Pendente (0).
        """
        if not self.connect(): return False
        try:
            cursor = self.connection.cursor()
            query = "UPDATE roboFgts SET status = %s WHERE empresaId = %s"
            cursor.execute(query, (novo_status, empresa_id))
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"❌ Erro ao alternar status: {e}")
            return False
        finally:
            self.disconnect()

    def atualizar_status_lote(self, ids, novo_status):
        """
        Atualiza o status de múltiplas empresas de uma vez.
        """
        if not ids or not self.connect(): return False
        try:
            cursor = self.connection.cursor()
            format_strings = ','.join(['%s'] * len(ids))
            query = f"UPDATE roboFgts SET status = %s WHERE empresaId IN ({format_strings})"
            cursor.execute(query, [novo_status] + ids)
            self.connection.commit()
            cursor.close()
            print(f"✅ Status atualizado para {len(ids)} empresas.")
            return True
        except Error as e:
            print(f"❌ Erro ao atualizar lote: {e}")
            return False
        finally:
            self.disconnect()


    def atualizar_status_onvio(self, empresa_id, novo_status):
        """
        Atualiza o statusOnvio de uma empresa específica.
        Valores comuns: 'A publicar', 'Publicado', 'Não publicado'
        """
        if not self.connect():
            return False
        try:
            cursor = self.connection.cursor()
            query = "UPDATE roboFgts SET statusOnvio = %s WHERE empresaId = %s"
            cursor.execute(query, (novo_status, empresa_id))
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"❌ Erro ao atualizar statusOnvio: {e}")
            return False
        finally:
            self.disconnect()

    def buscar_empresa_por_cnpj(self, cnpj):
        """
        Busca o ID e Razão Social da empresa pelo CNPJ.
        Retorna dicionário ou None.
        """
        if not self.connect(): return None
        try:
            # Limpa CNPJ para garantir match
            cnpj_limpo = ''.join(filter(str.isdigit, str(cnpj)))
            cursor = self.connection.cursor(dictionary=True)
            query = "SELECT id, razao FROM empresas WHERE REPLACE(REPLACE(REPLACE(cnpj, '.', ''), '/', ''), '-', '') = %s"
            cursor.execute(query, (cnpj_limpo,))
            resultado = cursor.fetchone()
            cursor.close()
            return resultado
        except Error as e:
            print(f"❌ Erro ao buscar empresa por CNPJ: {e}")
            return None
        finally:
            self.disconnect()
