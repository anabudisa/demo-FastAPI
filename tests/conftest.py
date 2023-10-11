from demo_fastapi.sql_server import server, username, password
import pyodbc
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

    cnxn = pyodbc.connect(connection_string)
    cnxn.autocommit = True

    return cnxn


@pytest.fixture(autouse=True)
def _mock_db_connection(mocker, db_connection):
    """
    This will alter application database connection settings,
    for all the test in the tests module
    :param mocker: pytest-mock plugin fixture
    :param db_connection: connection class
    :return: True if successful monkey-patching
    """
    mocker.patch(
        "demo_fastapi.sales.app.state.connection_manager.connection", db_connection
    )
    return True
