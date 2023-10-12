from fastapi.testclient import TestClient
from demo_fastapi.sales import app


def test_create_order_apples():
    """This should create a new order that orders only apples (oranges = NULL)"""
    with TestClient(app) as client:
        # first, create a new order
        response = client.post(
            "/orders/",
            params={"datestamp": "2011/12/02", "buyer": "ana", "apples": 12},
        )
        assert response.status_code == 200
        id = response.json()["id"]  # unique id
        assert response.json() == {
            "id": id,
            "datestamp": "2011/12/02",
            "buyer": "ana",
            "apples": 12,
            "oranges": None,
        }
        # second, delete it cos it's only a test
        response = client.delete("/orders/", params={"order_id": id})
        assert response.status_code == 200
        assert response.json() == {
            "id": id,
            "datestamp": "2011/12/02",
            "buyer": "ana",
            "apples": 12,
            "oranges": None,
        }


def test_create_order_oranges():
    """This should create a new order that orders only oranges (apples = NULL)"""
    with TestClient(app) as client:
        # first, create a new order
        response = client.post(
            "/orders/",
            params={"datestamp": "2011/12/02", "buyer": "ana", "oranges": 456},
        )
        assert response.status_code == 200
        id = response.json()["id"]  # unique id
        assert response.json() == {
            "id": id,
            "datestamp": "2011/12/02",
            "buyer": "ana",
            "apples": None,
            "oranges": 456,
        }


def test_create_order_apples_oranges():
    """This should create a new order that orders apples and oranges"""
    with TestClient(app) as client:
        # first, create a new order
        response = client.post(
            "/orders/",
            params={
                "datestamp": "2011/12/02",
                "buyer": "ana",
                "apples": 86,
                "oranges": 9812,
            },
        )
        assert response.status_code == 200
        id = response.json()["id"]  # unique id
        assert response.json() == {
            "id": id,
            "datestamp": "2011/12/02",
            "buyer": "ana",
            "apples": 86,
            "oranges": 9812,
        }


def test_create_order_bad_date_format():
    """This should not create an order because the order date in a wrong format"""
    with TestClient(app) as client:
        response = client.post(
            "/orders/",
            params={"datestamp": "2011-12-02", "buyer": "ana", "apples": 12},
        )
        assert response.status_code == 422
        assert response.json() == {
            "detail": "Date in wrong format! It should be yyyy/mm/dd (no spaces)."
        }


def test_create_order_bad_date_length():
    """This should not create an order because the order date is not a real date"""
    with TestClient(app) as client:
        response = client.post(
            "/orders/",
            params={"datestamp": "2011/123/02", "buyer": "ana", "apples": 12},
        )
        assert response.status_code == 422
        assert response.json() == {
            "detail": "Date in wrong format! It should be yyyy/mm/dd (no spaces). "
            + "Perhaps check for typos?"
        }


def test_create_order_too_old():
    """This should not create an order because the order date is before 2000/01/01"""
    with TestClient(app) as client:
        response = client.post(
            "/orders/",
            params={"datestamp": "1987/12/02", "buyer": "ana", "apples": 12},
        )
        assert response.status_code == 422
        assert response.json() == {
            "detail": "We only track orders after 1 January 2000. "
            + "Please enter only valid orders."
        }


def test_create_order_bad_buyer():
    """This should not create an order because the buyer's name contains numbers"""
    with TestClient(app) as client:
        response = client.post(
            "/orders/",
            params={"datestamp": "2011/12/02", "buyer": "ana1", "apples": 12},
        )
        assert response.status_code == 422
        assert response.json() == {"detail": "Buyer's name cannot contain numbers!"}


def test_create_order_bad_sale():
    """This should not create an order because no apples nor oranges were ordered"""
    with TestClient(app) as client:
        response = client.post(
            "/orders/",
            params={"datestamp": "2011/12/02", "buyer": "ana"},
        )
        assert response.status_code == 422
        assert response.json() == {
            "detail": "No sale has been made! Order at least one apple or orange."
        }


def test_read_order():
    """This should read an order with (unique) order id that is in database already"""
    with TestClient(app) as client:
        response = client.get("/orders/", params={"order_id": 12345})
        assert response.status_code == 200
        assert response.json() == {
            "id": 12345,
            "datestamp": "2022/02/02",
            "buyer": "johanna",
            "apples": 12,
            "oranges": 34,
        }


def test_update_order():
    """This should update an order by changing the buyer name"""
    with TestClient(app) as client:
        # first get the current value
        response = client.get("/orders/", params={"order_id": 12345})
        assert response.status_code == 200
        buyer = response.json()["buyer"]

        # second try to change the buyer name
        response = client.put(
            "/orders/", params={"order_id": 12345, "buyer": "ingeborg"}
        )
        assert response.status_code == 200
        assert response.json() == {
            "id": 12345,
            "datestamp": "2022/02/02",
            "buyer": "ingeborg",
            "apples": 12,
            "oranges": 34,
        }

        # third return to original buyer
        response = client.put("/orders/", params={"order_id": 12345, "buyer": buyer})
        assert response.status_code == 200
        assert response.json() == {
            "id": 12345,
            "datestamp": "2022/02/02",
            "buyer": buyer,
            "apples": 12,
            "oranges": 34,
        }
