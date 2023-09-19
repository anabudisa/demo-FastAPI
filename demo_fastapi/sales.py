from datetime import datetime
from pydantic import PositiveInt
from fastapi import FastAPI, HTTPException
from .model import Order
from uuid import uuid1
from .sql_server import connection_string
from contextlib import asynccontextmanager
import re
import pyodbc

cnxn = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # At startup - start connection to the SQL server
    global cnxn
    try:
        cnxn = pyodbc.connect(connection_string)
    except pyodbc.Error as err:
        sqlstate = err.args[1]
        print(sqlstate)
    yield
    # At shutdown - close the connection
    cnxn.close()


app = FastAPI(lifespan=lifespan)


@app.post("/orders/")
def create_order(
    datestamp: str,
    buyer: str,
    apples: PositiveInt = None,
    oranges: PositiveInt = None,
):
    """
    Create an order on date "date", from buyer "buyer" that is buying "sale";
    1. Check for errors in the input
    2. Generate unique id
    3. Save the order to the database
    """
    # check if any apples or oranges are ordered
    if apples is None and oranges is None:
        raise HTTPException(
            status_code=422,
            detail="No sale has been made! Order at least one apple or orange.",
        )

    # check if the name contains any numbers
    if any(char.isdigit() for char in buyer):
        raise HTTPException(
            status_code=422, detail="Buyer's name cannot contain numbers!"
        )

    # check date format and if it's after 1 January 2000
    r = re.compile("\d{4}/\d{2}/\d{2}")
    if len(datestamp) != 10:
        raise HTTPException(
            status_code=422,
            detail="Date in wrong format! It should be yyyy/mm/dd (no spaces). "
            + "Perhaps check for typos?",
        )
    if not r.match(datestamp):
        raise HTTPException(
            status_code=422,
            detail="Date in wrong format! It should be yyyy/mm/dd (no spaces).",
        )

    try:
        date_ = datetime.strptime(datestamp, "%Y/%m/%d")
    except ValueError as err:
        raise HTTPException(status_code=422, detail=str(err))

    if date_ < datetime(2000, 1, 1):
        raise HTTPException(
            status_code=422,
            detail="We only track orders after 1 January 2000. "
            + "Please enter only valid orders.",
        )

    # if everything ok, make an order TODO: is this still necessary?
    order_id = uuid1().int
    order = Order(
        id=order_id, datestamp=datestamp, buyer=buyer, apples=apples, oranges=oranges
    )

    # save to the database
    cursor = cnxn.cursor()
    cursor.execute(
        "INSERT INTO ShoppingList VALUES (?,?,?,?,?)",
        order_id,
        datestamp,
        buyer,
        apples,
        oranges,
    )

    return order


@app.put("/orders/")
def update_order(
    order_id: int,
    datestamp: str = None,
    buyer: str = None,
    apples: PositiveInt = None,
    oranges: PositiveInt = None,
):
    # update order with ID = order_id
    cursor = cnxn.cursor()
    cursor.execute("SELECT * FROM ShoppingList WHERE id = ?", order_id)
    row = cursor.fetchone()

    datestamp = datestamp if datestamp is not None else row.datestamp
    buyer = buyer if buyer is not None else row.buyer
    apples = apples if apples is not None else row.apples
    oranges = oranges if oranges is not None else row.oranges

    try:
        cursor.execute(
            "UPDATE ShoppingList SET datestamp = ?, buyer = ?, apples = ?, oranges = ? WHERE id = ?",
            datestamp,
            buyer,
            apples,
            oranges,
            order_id,
        )
    except pyodbc.DatabaseError as err:
        raise HTTPException(
            status_code=500,
            detail="Error updating database! Recheck your entries.\n" + str(err),
        )

    # order = Order(datestamp=datestamp, buyer=buyer, apples=apples, oranges=oranges)
    return Order(datestamp=datestamp, buyer=buyer, apples=apples, oranges=oranges)


@app.get("/orders/")
def read_order(order_id: int):
    # read the order with ID = order_id from the database and print it in the app
    cursor = cnxn.cursor()
    cursor.execute("SELECT * FROM ShoppingList WHERE id = ?", order_id)
    row = cursor.fetchone()

    return Order(
        id=order_id,
        datestamp=row.datestamp,
        buyer=row.buyer,
        apples=row.apples,
        oranges=row.oranges,
    )
