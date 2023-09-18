from demo_fastapi.sql_server import server, database, username, password
import pyodbc

connection_string = f"DRIVER=ODBC Driver 17 for SQL Server;SERVER={server};DATABASE={database};UID={username};PWD={password}"

try:
    cnxn = pyodbc.connect(connection_string)

    cursor = cnxn.cursor()

    for row in cursor.execute("SELECT * from ShoppingList;"):
        print(row)

    cnxn.close()

except Exception as e:
    print(f"Error: {str(e)}")
