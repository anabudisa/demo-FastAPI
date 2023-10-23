from datetime import datetime
from fastapi import FastAPI, HTTPException
from .model import Order
from .connection_manager import get_db
from contextlib import asynccontextmanager
import pyodbc
import random


@asynccontextmanager
async def lifespan(app: FastAPI):
    # At startup - start connection to the SQL server
    connection_manager = get_db()
    app.state.connection_manager = connection_manager
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
    order_id = random.randrange(10**8)  # 12345  # uuid1().int
    order.id = order_id

    # save to the database
    cursor = cnxn.cursor()
    try:
        cursor.execute(
            "INSERT INTO ShoppingList VALUES (?,?,?,?,?)",
            order.datestamp,
            order.buyer,
            order.apples,
            order.oranges,
            order.id,
        )
        cursor.commit()
    except pyodbc.DatabaseError as err:
        raise HTTPException(
            status_code=500,
            detail="Error updating database! Recheck your entries.\n" + str(err),
        )

    return order


@app.put("/orders/")
def update_order(order: Order):
    """update order with ID = order_id"""
    cnxn = app.state.connection_manager.connection
    cursor = cnxn.cursor()
    cursor.execute("SELECT * FROM ShoppingList WHERE id = ?", order.id)
    row = cursor.fetchone()

    datestamp = order.datestamp or row.datestamp
    buyer = order.buyer or row.buyer
    apples = order.apples or row.apples
    oranges = order.oranges or row.oranges

    try:
        cursor.execute(
            "UPDATE ShoppingList SET datestamp = ?, buyer = ?, apples = ?, oranges = "
            "? WHERE id = ?",
            datestamp,
            buyer,
            apples,
            oranges,
            order.id,
        )
        cursor.commit()
    except pyodbc.DatabaseError as err:
        raise HTTPException(
            status_code=418,
            detail="Error updating database! Recheck your entries.\n" + str(err),
        )

    # if the change passed, log the last version in the log table
    date_changed = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO ShoppingListLog VALUES (?,?,?,?,?,?)",
        row.datestamp,
        row.buyer,
        row.apples,
        row.oranges,
        row.id,
        date_changed,
    )
    cursor.commit()

    return Order(
        id=order.id, datestamp=datestamp, buyer=buyer, apples=apples, oranges=oranges
    )


@app.get("/orders/")
def read_order(order_id: int):
    """Read the order with ID = order_id from the database and print it in the app"""
    cnxn = app.state.connection_manager.connection
    cursor = cnxn.cursor()
    try:
        cursor.execute("SELECT * FROM ShoppingList WHERE id = ?", order_id)
        # cursor.commit()
    except pyodbc.DatabaseError as err:
        raise HTTPException(
            status_code=418,
            detail="Error reading database! Recheck your entries.\n" + str(err),
        )
    row = cursor.fetchone()

    return Order(
        id=order_id,
        datestamp=row.datestamp,
        buyer=row.buyer,
        apples=row.apples,
        oranges=row.oranges,
    )


@app.delete("/orders/", include_in_schema=False)
def delete_order(order_id: int):
    """Delete the order with ID = order_id from the database and print it in the app"""
    cnxn = app.state.connection_manager.connection
    cursor = cnxn.cursor()
    try:
        cursor.execute("SELECT * FROM ShoppingList WHERE id = ?", order_id)
        row = cursor.fetchone()
        cursor.execute("DELETE FROM ShoppingList WHERE id = ?", order_id)
        cursor.commit()
    except pyodbc.DatabaseError as err:
        raise HTTPException(
            status_code=418,
            detail="Error reading database! Recheck your entries.\n" + str(err),
        )

    return Order(
        id=order_id,
        datestamp=row.datestamp,
        buyer=row.buyer,
        apples=row.apples,
        oranges=row.oranges,
    )
