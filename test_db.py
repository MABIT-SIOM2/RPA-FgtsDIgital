import mysql.connector
import json

config = {
    "host": "mysql831.umbler.com",
    "port": "41890",
    "user": "vexmabit",
    "password": "vexmabit10",
    "database": "vex"
}

try:
    print("Conectando...")
    conn = mysql.connector.connect(**config)
    print("Conectado com sucesso!")
    conn.close()
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"Erro: {e}")
