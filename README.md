# Demo FastAPI
A demo repository to practice making packages with poetry, git hooks and FastAPI. \
Following the [API tutorial](https://github.com/Naeemedmo/python-playground) by [Naeemedmo](https://github.com/Naeemedmo).

## About
We made an API called **sales** that takes orders and saves them in a relational database. \
More specifically, API takes orders of apples and oranges, assigns a unique id to each order and saves it to the SQL database at a MS SQL docker container.

Orders contain:

- **When**: Required - e.g. 2023/04/19 (Given date is in string format YYYY/MM/DD happened after 2000/01/01)
- **Who**: Required - e.g. Ana (Name cannot contain numbers)
- **What**: Optional (at least one of them) - e.g. 2 Apples 3 Oranges Or 2 Apples Or 3 Oranges

Technicalities:
- API is created using [FastAPI](https://fastapi.tiangolo.com/) and [pydantic](https://docs.pydantic.dev/latest/)
- The database is saved on a MS SQL docker container using [latest docker image](https://hub.docker.com/_/microsoft-mssql-server)
- We utilize [poetry](https://python-poetry.org/) to install all dependencies and run the API within a virtual environment

## Requirements
Full list of requirements can be found in `pyproject.toml` and/or `poetry.lock` files.

## Usage
### Install using `make`
- Run `make api` to install and run the application
- Run `make test` to run tests

### Install and run API from command line
- [Optional, if not available] Deploy the docker container:
```
docker pull mcr.microsoft.com/mssql/server:latest
docker run -e "ACCEPT_EULA=Y" -e "MSSQL_SA_PASSWORD=Kend@llStr0ng!" -e "MSSQL_PID=Evaluation" -p 1433:1433  --name sql1 --hostname sql1 -d mcr.microsoft.com/mssql/server:latest
```
- Run the MS SQL container in the background
```
docker start sql1
```
- Install the requirements and start the virtual environment**:
```
poetry install
poetry shell
```
- Within the poetry shell, run the API in the background using `uvicorn` and open the API docs in the browser:
```
uvicorn demo_fastapi.sales:app --reload --host 0.0.0.0 &
sleep 5  # optional: waits for uvicorn to start
xdg-open http://0.0.0.0:8000/docs
```
** Sometimes `poetry shell` does not work as it should; instead run
```
source "$( poetry env list --full-path | grep Activated | cut -d' ' -f1 )/bin/activate"
```

## License
This project is licensed under the terms of the MIT license.
