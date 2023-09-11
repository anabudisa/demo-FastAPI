from fastapi.testclient import TestClient
from demo_fastapi.sales import app

client = TestClient(app)


def test_create_order_apples():
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


def test_create_order_oranges():
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
    response = client.post(
        "/orders/",
        params={"datestamp": "2011-12-02", "buyer": "ana", "apples": 12},
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": "Date in wrong format! It should be yyyy/mm/dd (no spaces)."
    }


def test_create_order_bad_date_length():
    response = client.post(
        "/orders/",
        params={"datestamp": "2011/123/02", "buyer": "ana", "apples": 12},
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": "Date in wrong format! It should be yyyy/mm/dd (no spaces). Perhaps check for typos?"
    }


def test_create_order_too_old():
    response = client.post(
        "/orders/",
        params={"datestamp": "1987/12/02", "buyer": "ana", "apples": 12},
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": "We only track orders after 1 January 2000. Please enter only valid orders."
    }


def test_create_order_bad_buyer():
    response = client.post(
        "/orders/",
        params={"datestamp": "2011/12/02", "buyer": "ana1", "apples": 12},
    )
    assert response.status_code == 422
    assert response.json() == {"detail": "Buyer's name cannot contain numbers!"}


def test_create_order_bad_sale():
    response = client.post(
        "/orders/",
        params={"datestamp": "2011/12/02", "buyer": "ana"},
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": "No sale has been made! Order at least one apple or orange."
    }


# if __name__ == "__main__":
#     test_create_order_apples_oranges()
