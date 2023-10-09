.ONESHELL:
SHELL=/bin/bash
.SILENT:

api: poetry	## third run the app
	uvicorn demo_fastapi.sales:app --reload --host 0.0.0.0 &
	sleep 10
	xdg-open http://0.0.0.0:8000/docs

poetry: container	## second activate poetry shell
	poetry install; \
	source "$$( poetry env list --full-path | grep Activated | cut -d' ' -f1 )/bin/activate"
	pytest tests/test_app_lifespan.py

container: ## Run the docker container
	if docker start sql1; then \
		echo -e "\033[0;32mSuccessfully deployed MS SQL docker container\033[0m"; \
	else \
		echo -e "\033[0;31mNo container for SQL database found. Deploying a new one...\033[0m"; \
		docker pull mcr.microsoft.com/mssql/server:latest; \
		docker run -e "ACCEPT_EULA=Y" -e "MSSQL_SA_PASSWORD=Kend@llStr0ng!" -e "MSSQL_PID=Evaluation" -p 1433:1433  --name sql1 --hostname sql1 -d mcr.microsoft.com/mssql/server:latest; \
		docker start sql1; \
		echo -e "\033[0;32m...Done.\033[0m"; \
	fi

test: poetry ## Run tests
	pytest tests

clean: ## Deactivate virtual env and docker container
	-deactivate
	docker stop sql1
help:
	echo -e "Run \033[0;31mmake api\033[0m to run the application or \033[0;31mmake test\033[0m to run tests"
