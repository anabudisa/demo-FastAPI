def test_connection(db_connection):
    try:
        cursor = db_connection.cursor()

        for row in cursor.execute("SELECT * from ShoppingList;"):
            print(row)

        db_connection.close()

    except Exception as e:
        print(f"Error: {str(e)}")
