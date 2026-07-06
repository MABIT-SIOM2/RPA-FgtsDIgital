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
            
        if self.config:
            self.config['use_pure'] = True

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

    def obter_empresas_pendentes(self):
        """
        Executa a query fornecida pelo usuário para buscar empresas pendentes.
        """
        if not self.connect():
            return []

        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT 
                    e.id as empresa_id,
                    e.codigo,
                    e.cnpj,
                    e.razao,
                    ed.carteira,
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
                    r.vencimentoGuia,
                    r.obs
                FROM empresas e
                INNER JOIN roboFgts r
                    ON r.empresaId = e.id
                LEFT JOIN empresa_departamento ed
                    ON ed.empresaId = e.id AND ed.departamentoId = 2
            """
            
            # Sem filtros adicionais de Onvio
            
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
                'vencimentoGuia': 'vencimentoGuia',
                'obs': 'obs'
            }

            # 2. Processar valores especiais (datas)
            cleaned_dados = {}
            for key, val in dados.items():
                if key not in mapping:
                    continue
                
                db_col = mapping[key]

                # Lógica unificada para campos de DATA (DATE no MySQL)
                if key in ['competenciaInicial', 'competenciaFinal', 'vencimentoGuia'] and val:
                    val_str = str(val).strip()
                    if val_str and val_str.lower() != 'none':
                        try:
                            # Formato DD/MM/AAAA ou MM/AAAA
                            if "/" in val_str:
                                parts = val_str.split("/")
                                if len(parts) == 3: # DD/MM/AAAA
                                    dia, mes, ano = parts
                                    cleaned_dados[db_col] = f"{ano}-{mes.zfill(2)}-{dia.zfill(2)}"
                                elif len(parts) == 2: # MM/AAAA
                                    mes, ano = parts
                                    cleaned_dados[db_col] = f"{ano}-{mes.zfill(2)}-01"
                                else:
                                    cleaned_dados[db_col] = val_str
                            elif "-" in val_str and len(val_str) >= 10: # Já é ISO (AAAA-MM-DD...)
                                cleaned_dados[db_col] = val_str.split(" ")[0]
                            else:
                                cleaned_dados[db_col] = val_str
                        except:
                            cleaned_dados[db_col] = val_str
                    else:
                        cleaned_dados[db_col] = None
                elif key == 'status':
                    cleaned_dados[db_col] = val
                else:
                    # Campos numéricos
                    if key in ['statusOnvio', 'obs']: # Texto
                        cleaned_dados[db_col] = val
                    else:
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


    def atualizar_empresa(self, empresa_id, dados):
        """
        Atualiza campos na tabela empresas e empresa_departamento de forma dinâmica.
        Apenas as chaves presentes no dicionário 'dados' serão atualizadas.
        """
        if not self.connect():
            return False

        try:
            cursor = self.connection.cursor()
            
            # Mapeamento de chaves permitidas para a tabela 'empresas'
            mapping_empresas = {
                'codigo': 'codigo',
                'cnpj': 'cnpj',
                'razao': 'razao'
            }

            dados_empresas = {}
            for key, val in dados.items():
                if key in mapping_empresas:
                    dados_empresas[mapping_empresas[key]] = val

            # Atualiza tabela empresas
            if dados_empresas:
                set_clause = ", ".join([f"{col} = %s" for col in dados_empresas.keys()])
                params = list(dados_empresas.values()) + [empresa_id]
                query = f"UPDATE empresas SET {set_clause} WHERE id = %s"
                cursor.execute(query, params)

            # Atualiza tabela empresa_departamento para a chave 'carteira' no departamentoId 2
            if 'carteira' in dados:
                cursor.execute("SELECT id FROM empresa_departamento WHERE empresaId = %s AND departamentoId = 2", (empresa_id,))
                if cursor.fetchone():
                    cursor.execute("UPDATE empresa_departamento SET carteira = %s WHERE empresaId = %s AND departamentoId = 2", (dados['carteira'], empresa_id))
                else:
                    cursor.execute("INSERT INTO empresa_departamento (empresaId, departamentoId, carteira) VALUES (%s, 2, %s)", (empresa_id, dados['carteira']))

            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            self.connection.rollback()
            print(f"❌ Erro ao atualizar dados da empresa: {e}")
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