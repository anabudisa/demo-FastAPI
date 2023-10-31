from datetime import datetime
from pydantic import BaseModel, PositiveInt, field_validator, model_validator
import re


class Order(BaseModel):
    id: int | None = None
    datestamp: str | None = None
    buyer: str | None = None
    apples: PositiveInt | None = None
    oranges: PositiveInt | None = None

    @field_validator("datestamp")
    @classmethod
    def check_date_format(cls, ymd: str | None) -> str | None:
        if ymd is not None:
            # check if the datetime is in format yyyy/mm/dd and after the date
            # 2000/01/01
            r = re.compile(r"\d{4}/\d{2}/\d{2}")
            assert (
                len(ymd) == 10
            ), "Date in wrong format! It should be yyyy/mm/dd (no spaces)."
            assert r.match(
                ymd
            ), "Date in wrong format! It should be yyyy/mm/dd (no spaces)."
            date_ = datetime(year=int(ymd[:4]), month=int(ymd[5:7]), day=int(ymd[8:10]))
            assert date_ >= datetime(
                2000, 1, 1
            ), "We only track orders after 1 January 2000"
        return ymd

    @field_validator("buyer")
    @classmethod
    def check_for_numbers(cls, x: str | None) -> str | None:
        if x is not None:
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
