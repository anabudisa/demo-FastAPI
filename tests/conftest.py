from demo_fastapi.sql_server import server, username, password
from demo_fastapi.connection_manager import ConnectionManager
from fastapi.testclient import TestClient
from demo_fastapi.sales import app
import pytest


@pytest.fixture(scope="session")
def db_connection():
    """
    Establishes odbc connection for the whole session
    :return: pyodbc connection class
    """
    database = "TestDB"
    connection_string = f"DRIVER=ODBC Driver 17 for SQL Server;SERVER={server};\
    DATABASE={database};UID={username};PWD={password}"

    RED, RESET = "\033[31m", "\033[0m"
    print(f"{RED}DATABASE WITHIN PYTEST: \n" + connection_string + f"{RESET}")

    connection_manager = ConnectionManager(connection_string)
    connection_manager.connect()
    connection_manager.connection.autocommit = True

    # cursor = connection_manager.connection.cursor()
    # cursor.execute("create database TestDB; use TestDB;")

    return connection_manager


@pytest.fixture(scope="session")
def client_test(db_connection):
    client_ = TestClient(app)
    app.state.connection_manager = db_connection
    return client_
