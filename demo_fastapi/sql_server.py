import pyodbc

server = "172.17.0.2,1433"
database = "ShoppingDB"
username = "sa"
password = "Kend@llStr0ng!"

connection_string = f"DRIVER=ODBC Driver 17 for SQL Server;SERVER={server};DATABASE={database};UID={username};PWD={password}"

try:
    cnxn = pyodbc.connect(connection_string)

    cursor = cnxn.cursor()

    cursor.execute("SELECT * from ShoppingList;")
    row = cursor.fetchone()
    while row:
        print(f"{row.datestamp=}, {row.buyer=}, {row.apples=}, {row.oranges=}")
        row = cursor.fetchone()

    # for row in cursor.execute("SELECT * from ShoppingList;"):
    #     print(row)

    cnxn.close()

except Exception as e:
    print(f"Error: {str(e)}")
