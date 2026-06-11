import mysql.connector

config = {
    "host": "",
    "port": 41890,
    "user": "",
    "password": "",
    "database": ""
}

try:
    conn = mysql.connector.connect(**config)
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"Erro: {e}")
