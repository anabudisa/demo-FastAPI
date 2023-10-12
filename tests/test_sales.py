def test_create_order_apples(client_test):
    """This should create a new order that orders only apples (oranges = NULL)"""

    # first, create a new order
    response = client_test.post(
        "/orders/",
        params={"datestamp": "2011/12/02", "buyer": "ana", "apples": 12},
    )
    assert response.status_code == 200
    id_ = response.json()["id"]  # unique id
    assert response.json() == {
        "id": id_,
        "datestamp": "2011/12/02",
        "buyer": "ana",
        "apples": 12,
        "oranges": None,
    }


def test_create_order_oranges(client_test):
    """This should create a new order that orders only oranges (apples = NULL)"""
    # first, create a new order
    response = client_test.post(
        "/orders/",
        params={"datestamp": "2011/12/02", "buyer": "ana", "oranges": 456},
    )
    assert response.status_code == 200
    id_ = response.json()["id"]  # unique id
    assert response.json() == {
        "id": id_,
        "datestamp": "2011/12/02",
        "buyer": "ana",
        "apples": None,
        "oranges": 456,
    }


def test_create_order_apples_oranges(client_test):
    """This should create a new order that orders apples and oranges"""
    # first, create a new order
    response = client_test.post(
        "/orders/",
        params={
            "datestamp": "2011/12/02",
            "buyer": "ana",
            "apples": 86,
            "oranges": 9812,
        },
    )
    assert response.status_code == 200
    id_ = response.json()["id"]  # unique id
    assert response.json() == {
        "id": id_,
        "datestamp": "2011/12/02",
        "buyer": "ana",
        "apples": 86,
        "oranges": 9812,
    }


def test_create_order_bad_date_format(client_test):
    """This should not create an order because the order date in a wrong format"""
    response = client_test.post(
        "/orders/",
        params={"datestamp": "2011-12-02", "buyer": "ana", "apples": 12},
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": "Date in wrong format! It should be yyyy/mm/dd (no spaces)."
    }


def test_create_order_bad_date_length(client_test):
    """This should not create an order because the order date is not a real date"""
    response = client_test.post(
        "/orders/",
        params={"datestamp": "2011/123/02", "buyer": "ana", "apples": 12},
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": "Date in wrong format! It should be yyyy/mm/dd (no spaces). "
        + "Perhaps check for typos?"
    }


def test_create_order_too_old(client_test):
    """This should not create an order because the order date is before 2000/01/01"""
    response = client_test.post(
        "/orders/",
        params={"datestamp": "1987/12/02", "buyer": "ana", "apples": 12},
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": "We only track orders after 1 January 2000. "
        + "Please enter only valid orders."
    }


def test_create_order_bad_buyer(client_test):
    """This should not create an order because the buyer's name contains numbers"""
    response = client_test.post(
        "/orders/",
        params={"datestamp": "2011/12/02", "buyer": "ana1", "apples": 12},
    )
    assert response.status_code == 422
    assert response.json() == {"detail": "Buyer's name cannot contain numbers!"}


def test_create_order_bad_sale(client_test):
    """This should not create an order because no apples nor oranges were ordered"""
    response = client_test.post(
        "/orders/",
        params={"datestamp": "2011/12/02", "buyer": "ana"},
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": "No sale has been made! Order at least one apple or orange."
    }


def test_read_order(client_test):
    """This should read an order with (unique) order id that is in database already"""
    response = client_test.get("/orders/", params={"order_id": 12345})
    assert response.status_code == 200
    assert response.json() == {
        "id": 12345,
        "datestamp": "2022/02/02",
        "buyer": "johanna",
        "apples": 12,
        "oranges": 34,
    }


def test_update_order(client_test):
    """This should update an order by changing the buyer name"""
    # first get the current value
    response = client_test.get("/orders/", params={"order_id": 12345})
    assert response.status_code == 200
    buyer = response.json()["buyer"]

    # second try to change the buyer name
    response = client_test.put(
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
    response = client_test.put("/orders/", params={"order_id": 12345, "buyer": buyer})
    assert response.status_code == 200
    assert response.json() == {
        "id": 12345,
        "datestamp": "2022/02/02",
        "buyer": buyer,
        "apples": 12,
        "oranges": 34,
    }
