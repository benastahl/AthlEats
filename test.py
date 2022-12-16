from json import loads
from pathlib import Path

sql_username = loads(Path("SECRET_TOKEN.json").read_text())["sql_username"]
sql_password = loads(Path("SECRET_TOKEN.json").read_text())["sql_password"]
sql_host = loads(Path("SECRET_TOKEN.json").read_text())["sql_host"]

google_password = loads(Path("SECRET_TOKEN.json").read_text())["google_password"]
google_username = loads(Path("SECRET_TOKEN.json").read_text())["google_username"]
drive_api_key = loads(Path("SECRET_TOKEN.json").read_text())["drive_api_key"]


print(sql_username, sql_password, sql_host, google_username)