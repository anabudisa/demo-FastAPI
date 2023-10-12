from demo_fastapi.sql_server import server, username, password
from demo_fastapi.connection_manager import ConnectionManager
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

    connection_manager = ConnectionManager(connection_string)
    connection_manager.connect()
    connection_manager.connection.autocommit = True

    return connection_manager
