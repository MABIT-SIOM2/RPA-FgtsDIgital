import json
import sys

# Força UTF-8 para evitar erro de charmap
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

from src.bot_pyautogui import executar_consulta_em_lote

# Tenta replicar o que gui.py faz
config_file = "config_multi.json"
with open(config_file, "r") as f:
    config = json.load(f)

mysql_config = config.get("mysql_config", {})
# Igual ao que está em gui.py:
mysql_conf = {
    'host': mysql_config.get("host", ""),
    'port': int(mysql_config.get("port", "3306")),
    'user': mysql_config.get("user", ""),
    'password': mysql_config.get("pass", ""),
    'database': mysql_config.get("database", "")
}

print(f"Conf passada: {mysql_conf}")
executar_consulta_em_lote(
    mysql_conf,
    "pasta_teste",
    tipo_consulta="FGTS Digital Site"
)
