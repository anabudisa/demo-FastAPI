from datetime import datetime
from fastapi import FastAPI, HTTPException
from .model import Order
from .connection_manager import get_db
from .odbc_execute import odbc_execute_command
from contextlib import asynccontextmanager
import random


@asynccontextmanager
async def lifespan(application: FastAPI):
    # At startup - start connection to the SQL server
    connection_manager = get_db()
    application.state.connection_manager = connection_manager
    yield
    # At shutdown - close the connection
    connection_manager.disconnect()


app = FastAPI(lifespan=lifespan)


@app.post("/orders/")
def create_order(order: Order):
    """
    Create an order on date "datestamp", from buyer "buyer" that is buying
    "apples" and "oranges";
    """
    # establish connection to the database
    cnxn = app.state.connection_manager.connection

    # check if date is provided
    if order.datestamp is None:
        raise HTTPException(
            status_code=422,
            detail="Please provide date of the order in format yyyy/mm/dd",
        )
    # check if buyer's name is provided
    if order.buyer is None:
        raise HTTPException(
            status_code=422,
            detail="Please enter buyer's name "
            "(max 50 characters, without numbers in the name).",
        )

    # if everything ok, make an order
    order_id = random.randrange(10**8)
    order.id = order_id

    # save to the database
    command = "INSERT INTO ShoppingList VALUES (?,?,?,?,?)"
    odbc_execute_command(
        cnxn,
        command,
        order.datestamp,
        order.buyer,
        order.apples,
        order.oranges,
        order.id,
    )

    return order


@app.put("/orders/")
def update_order(order: Order):
    """update order with ID = order_id"""
    # establish connection to the database
    cnxn = app.state.connection_manager.connection

    # check what were the old values for the order with id = order.id
    command = "SELECT * FROM ShoppingList WHERE id = ?"
    cursor = odbc_execute_command(cnxn, command, order.id)
    row = cursor.fetchone()
    if row is None:
        raise HTTPException(
            status_code=422,
            detail="Provided order (id) is not in the database table ShoppingList. "
            "Please provide another id!",
        )

    # update with new value from input variable order, or keep the previous value
    datestamp = order.datestamp or row.datestamp
    buyer = order.buyer or row.buyer
    apples = order.apples or row.apples
    oranges = order.oranges or row.oranges

    # update working table
    command = (
        "UPDATE ShoppingList SET datestamp = ?, buyer = ?, apples = ?, oranges "
        "= ? WHERE id = ?"
    )
    odbc_execute_command(cnxn, command, datestamp, buyer, apples, oranges, order.id)

    # if the change passed, log the last version in the log table
    date_changed = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    command = "INSERT INTO ShoppingListLog VALUES (?,?,?,?,?,?)"
    odbc_execute_command(
        cnxn,
        command,
        row.datestamp,
        row.buyer,
        row.apples,
        row.oranges,
        row.id,
        date_changed,
    )

    return Order(
        id=order.id, datestamp=datestamp, buyer=buyer, apples=apples, oranges=oranges
    )


@app.get("/orders/")
def read_order(order_id: int):
    """Read the order with ID = order_id from the database and print it in the app"""
    # establish connection
    cnxn = app.state.connection_manager.connection

    # read the order values from the database table
    cursor = odbc_execute_command(
        cnxn, "SELECT * FROM ShoppingList WHERE id = ?", order_id
    )
    row = cursor.fetchone()
    if row is None:
        raise HTTPException(
            status_code=422,
            detail="Provided order (id) is not in the database table ShoppingList. "
            "Please provide another id!",
        )

    return Order(
        id=row.id,
        datestamp=row.datestamp,
        buyer=row.buyer,
        apples=row.apples,
        oranges=row.oranges,
    )


@app.delete("/orders/", include_in_schema=False)
def delete_order(order_id: int):
    """Delete the order with ID = order_id from the database and print it in the app"""
    # establish connection and database cursor
    cnxn = app.state.connection_manager.connection

    # find the order in the database
    cursor = odbc_execute_command(
        cnxn, "SELECT * FROM ShoppingList WHERE id = ?", order_id
    )
    row = cursor.fetchone()
    if row is None:
        raise HTTPException(
            status_code=422,
            detail="Provided order (id) is not in the database table ShoppingList. "
            "Please provide another id!",
        )
    # and delete it from the database table
    odbc_execute_command(cnxn, "DELETE FROM ShoppingList WHERE id = ?", order_id)

    return Order(
        id=row.id,
        datestamp=row.datestamp,
        buyer=row.buyer,
        apples=row.apples,
        oranges=row.oranges,
    )
