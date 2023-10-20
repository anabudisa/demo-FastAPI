import pyodbc
from pydantic import PositiveInt


def calculate_cost(
    cursor: pyodbc.Cursor,
    order_id: int,
    apples: PositiveInt | None,
    oranges: PositiveInt | None,
):
    """
    Auxiliary function that calculates how much the order with id = order_id costs;
    Current set price is 1$ per apple, 2$ per orange.
    :param cursor: pyodbc.Cursor, cursor to the database where the order-money table is
    :param order_id: int, order id
    :param apples: pydantic.PositiveInt, number of apples ordered
    :param oranges: pydantic.PositiveInt, number of oranges ordered
    """
    # price of apples and oranges; TODO set this somewhere else?
    price_apple = 1.0
    price_orange = 2.0

    # check if the table exists, else create it
    query = """
    IF NOT EXISTS (SELECT NAME FROM SYS.TABLES WHERE NAME='MoneyList')
    BEGIN
        CREATE TABLE MoneyList (id INT, cost FLOAT)
    END;
    """
    cursor.execute(query)
    cursor.commit()

    # compute the cost of the order
    cost = (apples or 0.0) * price_apple + (oranges or 0.0) * price_orange

    # check if the order exists in the table
    cursor.execute("SELECT cost FROM MoneyList WHERE id = ?", order_id)
    if cursor.fetchone() is None:
        # if order does not yet exist, write it to the table
        cursor.execute("INSERT INTO MoneyList VALUES (?,?)", order_id, cost)
    else:
        # if order exists, update order cost
        cursor.execute("UPDATE MoneyList SET cost = ? WHERE id = ?", cost, order_id)
    cursor.commit()
