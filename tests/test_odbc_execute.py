from demo_fastapi.odbc_execute import odbc_execute_command


def test_odbc_insert(db_connection):
    conn = db_connection.connection
    params = ("2011/12/02", "ana", 86, 9812, 147909898)

    command = "INSERT INTO ShoppingList VALUES (?,?,?,?,?)"
    # this should raise exceptions if it fails
    odbc_execute_command(conn, command, *params)


def test_odbc_update(db_connection):
    conn = db_connection.connection
    params = ("2011/12/02", "ana", 86, 9812, 147909898)

    command = (
        "UPDATE ShoppingList SET datestamp = ?, buyer = ?, apples = ?, oranges= "
        "? WHERE id = ?"
    )
    # this should raise exceptions if it fails
    odbc_execute_command(conn, command, *params)


def test_odbc_select(db_connection):
    conn = db_connection.connection
    params = (12345,)

    command = "SELECT * FROM ShoppingList WHERE id=?"
    # this should raise exceptions if it fails
    odbc_execute_command(conn, command, *params)
