from json import loads
from pathlib import Path



sql_username = loads(Path("SECRET_TOKEN.json").read_text())["sql_username"]
sql_password = loads(Path("SECRET_TOKEN.json").read_text())["sql_password"]
sql_host = loads(Path("SECRET_TOKEN.json").read_text())["sql_host"]

print(sql_username, sql_password, sql_host)