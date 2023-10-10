from datetime import datetime
import re
from pydantic import PositiveInt
from fastapi import FastAPI, HTTPException
from .model import Order
from uuid import uuid1

app = FastAPI()


@app.post("/orders/")
def create_order(
    datestamp: str,
    buyer: str,
    apples: PositiveInt = None,
    oranges: PositiveInt = None,
):
    # create an order on date "date", from buyer "buyer" that is buying "sale";
    # generate unique id
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

    # if everything ok, make an order
    order_id = uuid1().int
    order = Order(
        id=order_id, datestamp=datestamp, buyer=buyer, apples=apples, oranges=oranges
    )
    return order


# @app.put("/orders/{order_id}")
# def update_order(
#     order_id: int,
#     datestamp: str,
#     buyer: str,
#     apples: PositiveInt = None,
#     oranges: PositiveInt = None,
# ):
#     # update order with ID "order_id"
#     order = Order(datestamp=datestamp, buyer=buyer, apples=apples, oranges=oranges)
#     return {"order_id": order_id, "order": order}


# @app.get("/orders/{order_id}")
# def read_order(order_id: int):
#     # get data of order with ID "order_id"
#     return {"item_id": order_id, "order": order_id}
