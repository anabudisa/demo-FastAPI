from demo_fastapi.model import Order


def test_create_order_apples(client_test):
    """This should create a new order that orders only apples (oranges = NULL)"""
    order = Order(datestamp="2011/12/02", buyer="ana", apples=12)
    response = client_test.post("/orders/", json=order.model_dump())
    # import pdb; pdb.set_trace()
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
    order = Order(datestamp="2011/12/02", buyer="ana", oranges=456)
    response = client_test.post("/orders/", json=order.model_dump())
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
    order = Order(datestamp="2011/12/02", buyer="ana", apples=86, oranges=9812)
    response = client_test.post("/orders/", json=order.model_dump())
    assert response.status_code == 200
    id_ = response.json()["id"]  # unique id
    assert response.json() == {
        "id": id_,
        "datestamp": "2011/12/02",
        "buyer": "ana",
        "apples": 86,
        "oranges": 9812,
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
    apples = response.json()["apples"]
    oranges = response.json()["oranges"]

    # second try to change the buyer name
    order = Order(id=12345, buyer="ingeborg", apples=apples, oranges=oranges)
    response = client_test.put("/orders/", json=order.model_dump())
    assert response.status_code == 200
    assert response.json() == {
        "id": 12345,
        "datestamp": "2022/02/02",
        "buyer": "ingeborg",
        "apples": 12,
        "oranges": 34,
    }

    # third return to original buyer
    order = Order(id=12345, buyer=buyer, apples=apples, oranges=oranges)
    response = client_test.put("/orders/", json=order.model_dump())
    assert response.status_code == 200
    assert response.json() == {
        "id": 12345,
        "datestamp": "2022/02/02",
        "buyer": buyer,
        "apples": 12,
        "oranges": 34,
    }
