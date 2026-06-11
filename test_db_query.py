import mysql.connector
import json

config = {
    "host": "mysql831.umbler.com",
    "port": 41890,
    "user": "vexmabit",
    "password": "vexmabit10",
    "database": "vex"
}

try:
    print("Conectando...")
    conn = mysql.connector.connect(**config)
    print("Conectado com sucesso!")
    
    cursor = conn.cursor(dictionary=True)
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
            r.vencimentoGuia
        FROM empresas e
        INNER JOIN roboFgts r
            ON r.empresaId = e.id
        LEFT JOIN empresa_departamento ed
            ON ed.empresaId = e.id AND ed.departamentoId = 2
    """
    print("Executando query...")
    cursor.execute(query)
    print("Buscando resultados...")
    resultados = cursor.fetchall()
    print(f"Empresas encontradas: {len(resultados)}")
    cursor.close()
    conn.close()
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"Erro: {e}")
