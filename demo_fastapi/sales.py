from datetime import date
import re
from pydantic import BaseModel, PositiveInt, field_validator, model_validator
from fastapi import FastAPI, HTTPException
from uuid import uuid1

# init API for orders
app = FastAPI()


class Order(BaseModel):
    id: int
    datestamp: str
    buyer: str
    apples: PositiveInt | None = None
    oranges: PositiveInt | None = None

    @field_validator("datestamp")
    @classmethod
    def check_date_format(cls, ymd: str) -> str:
        # check if the datetime is in format yyyy/mm/dd and after the date 2000/01/01
        r = re.compile("\d{4}/\d{2}/\d{2}")
        assert (
            len(ymd) == 10
        ), "Date in wrong format! It should be yyyy/mm/dd (no spaces)."
        assert r.match(
            ymd
        ), "Date in wrong format! It should be yyyy/mm/dd (no spaces)."
        date_ = date(year=int(ymd[:4]), month=int(ymd[5:7]), day=int(ymd[8:10]))
        assert date_ >= date(2000, 1, 1), "We only track orders after 1 January 2000"
        return ymd

    @field_validator("buyer")
    @classmethod
    def check_for_numbers(cls, x: str) -> str:
        # check if the string contains any numbers
        assert not any(
            char.isdigit() for char in x
        ), "Buyer's name cannot contain numbers!"
        return x

    @model_validator(mode="after")
    def check(self) -> "Order":
        if self.apples is None and self.oranges is None:
            raise ValueError(
                "No sale has been made! Order at least one apple or orange."
            )
        return self


@app.post("/orders/")
def create_order(
    datestamp: str,
    buyer: str,
    apples: PositiveInt = None,
    oranges: PositiveInt = None,
):
    # create an order on date "date", from buyer "buyer" that is buying "sale"; generate unique id
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
            detail="Date in wrong format! It should be yyyy/mm/dd (no spaces). Perhaps check for typos?",
        )
    if not r.match(datestamp):
        raise HTTPException(
            status_code=422,
            detail="Date in wrong format! It should be yyyy/mm/dd (no spaces).",
        )

    date_ = date(
        year=int(datestamp[:4]), month=int(datestamp[5:7]), day=int(datestamp[8:10])
    )  # FIXME: out of range dates?
    if date_ < date(2000, 1, 1):
        raise HTTPException(
            status_code=422,
            detail="We only track orders after 1 January 2000. Please enter only valid orders.",
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
