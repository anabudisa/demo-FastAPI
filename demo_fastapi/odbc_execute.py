import pyodbc
from fastapi import HTTPException


def odbc_errors(err):
    if err.args[0] == "42000":
        raise HTTPException(
            status_code=422,
            detail="Error in SQL command syntax or the database does not exist. "
            "Check the full message below: \n" + str(err.args[1]),
        )
    elif err.args[0] == "42S02":
        raise HTTPException(
            status_code=422,
            detail="Error in SQL command, probably the table does not exist."
            "Check the full message below: \n" + str(err.args[1]),
        )
    elif err.args[0] == "42S22":
        raise HTTPException(
            status_code=422,
            detail="Error in SQL command, probably the table does not contain"
            " the queried column. Check the full message below: \n" + str(err.args[1]),
        )
    elif err.args[0] == "28000":
        raise HTTPException(
            status_code=422,
            detail="Error in SQL Server connection, probably the username or "
            "password were incorrect. Check the full message below: \n"
            + str(err.args[1]),
        )
    elif err.args[0] == "08S01":
        raise HTTPException(
            status_code=422,
            detail="Error in SQL Server connection, try again later. "
            "If repeated error, check if the connection to the server is on "
            "and check the full message below: \n" + str(err.args[1]),
        )
    elif err.args[0] == "HYT00":
        raise HTTPException(
            status_code=422,
            detail="Error in SQL Server connection, probably the server is down. "
            "If repeated error, check if the connection to the server is on "
            "and check the full message below: \n" + str(err.args[1]),
        )
    else:
        raise HTTPException(
            status_code=422,
            detail="Error in SQL command, probably the cursor connection was "
            "closed. Check the full message below: \n" + str(err.args[1]),
        )


def odbc_execute_command(connection_: pyodbc.Connection, command: str, *params):
    """Execute sql insert command with necessary via pyodbc connection"""
    # get a cursor to the database
    cursor = connection_.cursor()

    # try executing the command or raise HTTP error in the app
    try:
        cursor.execute(command, *params)
    except (
        pyodbc.ProgrammingError,
        pyodbc.InterfaceError,
        pyodbc.OperationalError,
    ) as err:
        odbc_errors(err)

    # return cursor if successful
    return cursor
