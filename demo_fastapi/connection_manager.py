from .sql_server import connection_string
import pyodbc


class ConnectionManager:
    def __init__(self, connstring: str):
        self.connection_string = connstring
        self.connection = None

    def connect(self):
        try:
            self.connection = pyodbc.connect(self.connection_string)
        except pyodbc.Error as err:
            # sqlstate = err.args[1]
            print(str(err))

    def disconnect(self):
        self.connection.close()


def get_db():
    connection_manager = ConnectionManager(connection_string)
    connection_manager.connect()
    return connection_manager


if __name__ == "__main__":
    print()
