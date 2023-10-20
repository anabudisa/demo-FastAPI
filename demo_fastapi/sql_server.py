import os

server_name = os.environ.get("DATABASE_SERVER") or "localhost"
server_port = os.environ.get("DATABASE_PORT") or "1433"
server = server_name + "," + server_port
database = os.environ.get("DATABASE_NAME") or "ShoppingDB"
username = os.environ.get("DATABASE_USERNAME") or "sa"
password = os.environ.get("DATABASE_PWD") or "Kend@llStr0ng!"

connection_string = f"DRIVER=ODBC Driver 17 for SQL Server;SERVER={server};\
DATABASE={database};UID={username};PWD={password}"
