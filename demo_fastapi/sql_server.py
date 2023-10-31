server = "172.17.0.2,1433"
database = "ShoppingDB"
test_database = "TestDB"
username = "sa"
password = "Kend@llStr0ng!"

connection_string = f"DRIVER=ODBC Driver 17 for SQL Server;SERVER={server};\
DATABASE={database};UID={username};PWD={password}"

test_connection_string = f"DRIVER=ODBC Driver 17 for SQL Server;SERVER={server};\
DATABASE={test_database};UID={username};PWD={password}"
