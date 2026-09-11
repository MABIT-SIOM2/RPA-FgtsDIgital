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

    # =========================================================================
    # MIGRATION - Garante UNIQUE KEY composta (empresaId, competenciaInicial)
    # =========================================================================

    def executar_migration(self):
        """
        Verifica se a UNIQUE KEY composta (empresaId, competenciaInicial) já existe.
        Se não existir, limpa duplicatas e adiciona a constraint.
        Deve ser chamado uma vez na inicialização da aplicação.
        """
        if not self.connect():
            print("⚠️ Migration: não foi possível conectar ao banco.")
            return False

        try:
            cursor = self.connection.cursor(dictionary=True)
            db_name = self.config.get('database', self.config.get('db', ''))

            # 1. Verifica se a UNIQUE KEY já existe
            cursor.execute("""
                SELECT COUNT(*) as cnt
                FROM information_schema.TABLE_CONSTRAINTS
                WHERE TABLE_SCHEMA = %s
                  AND TABLE_NAME = 'roboFgts'
                  AND CONSTRAINT_NAME = 'uq_empresa_comp'
                  AND CONSTRAINT_TYPE = 'UNIQUE'
            """, (db_name,))
            row = cursor.fetchone()
            if row and row['cnt'] > 0:
                print("✅ Migration: UNIQUE KEY uq_empresa_comp já existe. Nada a fazer.")
                cursor.close()
                return True

            print("🔄 Migration: Criando UNIQUE KEY composta (empresaId, competenciaInicial)...")

            # 2. Remove duplicatas mantendo o registro mais recente (id MAX)
            cursor.execute("""
                DELETE r1 FROM roboFgts r1
                INNER JOIN roboFgts r2
                    ON r1.empresaId = r2.empresaId
                    AND r1.competenciaInicial = r2.competenciaInicial
                    AND r1.id < r2.id
            """)
            deleted = cursor.rowcount
            if deleted > 0:
                print(f"🧹 Migration: {deleted} registro(s) duplicado(s) removido(s).")

            # 3. Adiciona a UNIQUE KEY composta
            cursor.execute("""
                ALTER TABLE roboFgts
                ADD UNIQUE KEY uq_empresa_comp (empresaId, competenciaInicial)
            """)
            self.connection.commit()
            cursor.close()
            print("✅ Migration: UNIQUE KEY uq_empresa_comp criada com sucesso.")
            return True

        except Error as e:
            print(f"❌ Erro na migration: {e}")
            self.connection.rollback()
            return False
        finally:
            self.disconnect()

    # =========================================================================
    # CONSULTAS
    # =========================================================================

    def obter_empresas_pendentes(self, competencia=None):
        """
        Retorna empresas com seus dados de roboFgts.
        
        - competencia=None  → retorna a competência mais recente de cada empresa.
        - competencia='AAAA-MM-DD' → retorna apenas os registros dessa competência.
        """
        if not self.connect():
            return []

        try:
            cursor = self.connection.cursor(dictionary=True)

            if competencia:
                # Filtra pela competência exata informada (formato ISO: AAAA-MM-DD)
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
                    WHERE r.competenciaInicial = %s
                """
                cursor.execute(query, (competencia,))
            else:
                # Retorna somente a competência mais recente por empresa
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
                        AND r.competenciaInicial = (
                            SELECT MAX(r2.competenciaInicial)
                            FROM roboFgts r2
                            WHERE r2.empresaId = e.id
                        )
                    LEFT JOIN empresa_departamento ed
                        ON ed.empresaId = e.id AND ed.departamentoId = 2
                """
                cursor.execute(query)

            resultados = cursor.fetchall()
            cursor.close()
            return resultados
        except Error as e:
            print(f"❌ Erro ao buscar empresas: {e}")
            return []
        finally:
            self.disconnect()

    def obter_competencias_disponiveis(self):
        """
        Retorna lista de competências únicas disponíveis no banco,
        ordenadas da mais recente para a mais antiga.
        Formato de retorno: lista de strings 'MM/AAAA'.
        """
        if not self.connect():
            return []

        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT DISTINCT competenciaInicial
                FROM roboFgts
                WHERE competenciaInicial IS NOT NULL
                ORDER BY competenciaInicial DESC
            """)
            rows = cursor.fetchall()
            cursor.close()

            competencias = []
            for (data,) in rows:
                # Converte de date/string ISO para MM/AAAA
                s = str(data)
                if len(s) >= 7 and '-' in s:
                    parts = s.split('-')
                    if len(parts) == 3:
                        competencias.append(f"{parts[1]}/{parts[0]}")
                    else:
                        competencias.append(s)
                else:
                    competencias.append(s)

            return competencias
        except Error as e:
            print(f"❌ Erro ao buscar competências: {e}")
            return []
        finally:
            self.disconnect()

    # =========================================================================
    # ATUALIZAÇÃO DE DADOS (upsert por empresa + competência)
    # =========================================================================

    def atualizar_dados_guia(self, empresa_id, dados):
        """
        Insere ou atualiza dados na tabela roboFgts de forma dinâmica,
        usando a chave composta (empresaId, competenciaInicial).

        O campo 'competenciaInicial' DEVE estar presente em 'dados'.
        Se ausente, retorna False com aviso.
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

            # 2. Processar e limpar valores
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
                            elif "-" in val_str and len(val_str) >= 10: # Já é ISO (AAAA-MM-DD)
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
                    if key in ['statusOnvio', 'obs']: # Texto
                        cleaned_dados[db_col] = val
                    else:
                        cleaned_dados[db_col] = clean_val(val)

            if not cleaned_dados:
                return True  # Nada para atualizar

            # 3. Valida que competenciaInicial está presente (obrigatória para upsert histórico)
            if 'competenciaInicial' not in cleaned_dados or cleaned_dados['competenciaInicial'] is None:
                print(f"⚠️ atualizar_dados_guia: 'competenciaInicial' ausente para empresa_id={empresa_id}. Usando fallback (UPDATE no mais recente).")
                # Fallback: atualiza o registro mais recente da empresa
                set_clause = ", ".join([f"{col} = %s" for col in cleaned_dados.keys()])
                params = list(cleaned_dados.values()) + [empresa_id]
                query = f"""
                    UPDATE roboFgts SET {set_clause}
                    WHERE empresaId = %s
                    ORDER BY competenciaInicial DESC
                    LIMIT 1
                """
                cursor.execute(query, params)
                self.connection.commit()
                cursor.close()
                return True

            # 4. UPSERT: INSERT ... ON DUPLICATE KEY UPDATE
            # Garante que empresaId está incluído
            cleaned_dados['empresaId'] = empresa_id

            cols = list(cleaned_dados.keys())
            placeholders = ", ".join(["%s"] * len(cols))
            insert_cols = ", ".join(cols)

            # Campos que podem ser atualizados em caso de duplicata (exclui a chave composta)
            update_fields = [col for col in cols if col not in ('empresaId', 'competenciaInicial')]
            if update_fields:
                update_clause = ", ".join([f"{col} = VALUES({col})" for col in update_fields])
            else:
                update_clause = "status = VALUES(status)"  # fallback mínimo

            query = f"""
                INSERT INTO roboFgts ({insert_cols})
                VALUES ({placeholders})
                ON DUPLICATE KEY UPDATE {update_clause}
            """
            params = list(cleaned_dados.values())
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

    # =========================================================================
    # STATUS — afeta apenas a competência correta
    # =========================================================================

    def _resolver_competencia(self, cursor, empresa_id, competencia):
        """
        Retorna a data ISO da competência a usar.
        Se 'competencia' for None, retorna a competência mais recente da empresa.
        """
        if competencia:
            # Normaliza para ISO
            val_str = str(competencia).strip()
            if "/" in val_str:
                parts = val_str.split("/")
                if len(parts) == 2:
                    mes, ano = parts
                    return f"{ano}-{mes.zfill(2)}-01"
                elif len(parts) == 3:
                    dia, mes, ano = parts
                    return f"{ano}-{mes.zfill(2)}-{dia.zfill(2)}"
            return val_str
        else:
            cursor.execute(
                "SELECT MAX(competenciaInicial) as max_comp FROM roboFgts WHERE empresaId = %s",
                (empresa_id,)
            )
            row = cursor.fetchone()
            if row:
                val = row['max_comp'] if isinstance(row, dict) else row[0]
                return str(val) if val else None
            return None

    def marcar_status_erro(self, empresa_id, mensagem, competencia=None):
        """
        Marca status = 3 (Erro) para a competência informada.
        Se competencia=None, aplica à competência mais recente da empresa.
        """
        if not self.connect(): return False
        try:
            cursor = self.connection.cursor(dictionary=True)
            comp_iso = self._resolver_competencia(cursor, empresa_id, competencia)
            if not comp_iso:
                print(f"⚠️ marcar_status_erro: nenhuma competência encontrada para empresa_id={empresa_id}")
                cursor.close()
                return False

            query = "UPDATE roboFgts SET status = 3 WHERE empresaId = %s AND competenciaInicial = %s"
            cursor.execute(query, (empresa_id, comp_iso))
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"❌ Erro ao marcar status de erro: {e}")
            return False
        finally:
            self.disconnect()

    def toggle_empresa_status(self, empresa_id, novo_status, competencia=None):
        """
        Alterna o status da empresa para a competência informada.
        Se competencia=None, aplica à competência mais recente da empresa.
        """
        if not self.connect(): return False
        try:
            cursor = self.connection.cursor(dictionary=True)
            comp_iso = self._resolver_competencia(cursor, empresa_id, competencia)
            if not comp_iso:
                print(f"⚠️ toggle_empresa_status: nenhuma competência encontrada para empresa_id={empresa_id}")
                cursor.close()
                return False

            query = "UPDATE roboFgts SET status = %s WHERE empresaId = %s AND competenciaInicial = %s"
            cursor.execute(query, (novo_status, empresa_id, comp_iso))
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"❌ Erro ao alternar status: {e}")
            return False
        finally:
            self.disconnect()

    def atualizar_status_lote(self, ids, novo_status, competencia=None):
        """
        Atualiza o status de múltiplas empresas de uma vez.
        Se competencia=None, aplica à competência mais recente de cada empresa.
        """
        if not ids or not self.connect(): return False
        try:
            cursor = self.connection.cursor(dictionary=True)

            if competencia:
                # Normaliza para ISO uma única vez
                val_str = str(competencia).strip()
                if "/" in val_str:
                    parts = val_str.split("/")
                    if len(parts) == 2:
                        mes, ano = parts
                        comp_iso = f"{ano}-{mes.zfill(2)}-01"
                    else:
                        comp_iso = val_str
                else:
                    comp_iso = val_str

                format_strings = ','.join(['%s'] * len(ids))
                query = f"""
                    UPDATE roboFgts SET status = %s
                    WHERE empresaId IN ({format_strings})
                    AND competenciaInicial = %s
                """
                cursor.execute(query, [novo_status] + ids + [comp_iso])
            else:
                # Atualiza o mais recente de cada empresa individualmente
                for empresa_id in ids:
                    comp_iso = self._resolver_competencia(cursor, empresa_id, None)
                    if comp_iso:
                        cursor.execute(
                            "UPDATE roboFgts SET status = %s WHERE empresaId = %s AND competenciaInicial = %s",
                            (novo_status, empresa_id, comp_iso)
                        )

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