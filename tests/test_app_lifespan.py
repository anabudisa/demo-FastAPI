from demo_fastapi.sales import app
from fastapi.testclient import TestClient


def test_startup_shutdown():
    """
    Testing application startup and shutdown. It should successfully connect to the SQL database via pyodbc
    """
    with TestClient(app) as client:
        # I guess the app should just start and stop when we call TestClient(app);
        # And it should give an error if the start and shutdown processes failed
        assert True
