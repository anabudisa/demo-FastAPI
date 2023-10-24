import pytest

from demo_fastapi.model import Order
from pydantic import ValidationError


def test_create_order_bad_date_format():
    """This should not create an order because the order date in a wrong format"""
    with pytest.raises(ValidationError) as excinfo:
        Order(datestamp="2011-12-02", buyer="ana", apples=12)
    exception = str(excinfo.value).split("\n")

    assert exception[2] == (
        "  Assertion failed, Date in wrong format! It should be "
        "yyyy/mm/dd (no spaces). [type=assertion_error, "
        "input_value='2011-12-02', input_type=str]"
    )


def test_create_order_bad_date_length():
    """This should not create an order because the order date is not a real date"""
    with pytest.raises(ValidationError) as excinfo:
        Order(datestamp="2011/123/02", buyer="ana", apples=12)
    exception = str(excinfo.value).split("\n")

    assert exception[2] == (
        "  Assertion failed, Date in wrong format! It should be"
        " yyyy/mm/dd (no spaces). [type=assertion_error, "
        "input_value='2011/123/02', input_type=str]"
    )


def test_create_order_too_old():
    """This should not create an order because the order date is before 2000/01/01"""
    with pytest.raises(ValidationError) as excinfo:
        Order(datestamp="1987/12/02", buyer="ana", apples=12)
    exception = str(excinfo.value).split("\n")

    assert exception[2] == (
        "  Assertion failed, We only track orders after 1 January"
        " 2000 [type=assertion_error, input_value='1987/12/02',"
        " input_type=str]"
    )


def test_create_order_bad_buyer():
    """This should not create an order because the buyer's name contains numbers"""
    with pytest.raises(ValidationError) as excinfo:
        Order(datestamp="2011/12/02", buyer="ana1", apples=12)
    exception = str(excinfo.value).split("\n")

    assert exception[2] == (
        "  Assertion failed, Buyer's name cannot contain numbers!"
        " [type=assertion_error, input_value='ana1',"
        " input_type=str]"
    )


def test_create_order_bad_sale():
    """This should not create an order because no apples nor oranges were ordered"""
    with pytest.raises(ValidationError) as excinfo:
        Order(datestamp="2011/12/02", buyer="ana")
    exception = str(excinfo.value).split("\n")

    assert exception[1] == (
        "  Value error, No sale has been made! Order at least "
        "one apple or orange. [type=value_error, "
        "input_value={'datestamp': '2011/12/02', 'buyer': 'ana'},"
        " input_type=dict]"
    )
