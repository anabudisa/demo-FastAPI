from datetime import date
from pydantic import BaseModel, PositiveInt, field_validator, model_validator
from fastapi import FastAPI

# init API for orders
app = FastAPI()


class Order(BaseModel):
    datestamp: date
    buyer: str
    apples: PositiveInt | None = None
    oranges: PositiveInt | None = None

    @field_validator("datestamp")
    @classmethod
    # FIXME: want format yyyy/mm/dd but '/' meanings other than char? problematic
    def check_date_format(cls, ymd: date) -> date:
        # check if the datetime is in the right format and after the date 2000-01-01
        assert ymd > date(2000, 1, 1), "Only input orders after 1 January 2000!"
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
                "No sales have been made! Order at least one apple or orange."
            )
        return self


@app.post("/orders/{order_id}")
def create_order(
    order_id: int,
    date: date,
    buyer: str,
    apples: PositiveInt = None,
    oranges: PositiveInt = None,
):
    # create an order with order ID "order_id", on date "date", from buyer "buyer" that is buying "sale"
    order = Order(datestamp=date, buyer=buyer, apples=apples, oranges=oranges)
    return {"order_id": order_id, "order": order}


@app.put("/orders/{order_id}")
def update_item(
    order_id: int,
    date: date,
    buyer: str,
    apples: PositiveInt = None,
    oranges: PositiveInt = None,
):
    # update order with ID "order_id"
    order = Order(datestamp=date, buyer=buyer, apples=apples, oranges=oranges)
    return {"order_id": order_id, "order": order}


@app.get("/orders/{order_id}")
def read_item(order_id: int):
    # get data of order with ID "order_id"
    return {"item_id": order_id, "order": order_id}
