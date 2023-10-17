# copyright https://github.com/max-pfeiffer/python-poetry/blob/main/build/Dockerfile
# using Python 3.10 as base image
ARG OFFICIAL_PYTHON_IMAGE=python:3.10-slim
FROM ${OFFICIAL_PYTHON_IMAGE} as build-stage
ARG POETRY_VERSION=1.6.1

SHELL ["/bin/bash", "-c"]

# References for variables below:
# https://pip.pypa.io/en/stable/topics/caching/#avoiding-caching
# https://pip.pypa.io/en/stable/cli/pip/?highlight=PIP_NO_CACHE_DIR#cmdoption-no-cache-dir
# https://pip.pypa.io/en/stable/cli/pip/?highlight=PIP_DISABLE_PIP_VERSION_CHECK#cmdoption-disable-pip-version-check
# https://pip.pypa.io/en/stable/cli/pip/?highlight=PIP_DEFAULT_TIMEOUT#cmdoption-timeout
# https://pip.pypa.io/en/stable/topics/configuration/#environment-variables
# https://python-poetry.org/docs/#installation
# https://refspecs.linuxfoundation.org/FHS_2.3/fhs-2.3.html#OPTADDONAPPLICATIONSOFTWAREPACKAGES

ENV PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=${POETRY_VERSION} \
    POETRY_HOME="/opt/poetry"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# base build (install essentials like gcc and g++, gnupg, curl, lsb-release and odbc driver dev
ENV ACCEPT_EULA=Y
RUN apt-get update \
    && apt-get install --no-install-recommends -y build-essential gnupg curl lsb-release unixodbc-dev

# install ms odbc driver for sql server and tools
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
  && curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list \
  && apt-get update \
  && apt-get install -y --no-install-recommends --allow-unauthenticated msodbcsql17 mssql-tools \
  && echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bash_profile \
  && echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc

# install poetry
# https://python-poetry.org/docs/#installing-manually
RUN python -m venv ${POETRY_HOME}
RUN ${POETRY_HOME}/bin/pip install -U pip setuptools
RUN ${POETRY_HOME}/bin/pip install "poetry==${POETRY_VERSION}"

# setup a poetry venv
ENV PATH="${PATH}:/opt/poetry/bin" \
    POETRY_VIRTUALENVS_IN_PROJECT=true

# install requirements and poetry venv (w/o requiring root directory of the project)
COPY poetry.lock pyproject.toml $HOME/
RUN poetry install --no-interaction --no-root --with dev

# Provide a known path for the virtual environment by creating a symlink
RUN ln -s $(poetry env info --path) /var/my-venv

# Hide virtual env prompt
ENV VIRTUAL_ENV_DISABLE_PROMPT=1

# Start virtual env when bash starts
RUN echo "source /var/my-venv/bin/activate" >> ~/.bashrc

# environment important variables to run the database (from other docker container)
ENV DATABASE_SERVER="172.17.0.3" \
    DATABASE_PORT="1433" \
    DATABASE_USERNAME="SA" \
    DATABASE_PWD="Kend@llStr0ng!"

FROM build-stage as test-stage

# i like bash
SHELL ["/bin/bash", "-c"]

# install requirements (only for test stage! ergo "--with test") and poetry venv
RUN poetry install --no-interaction --no-root --with test

# copy the app files
COPY /demo_fastapi /demo_fastapi
COPY /tests /tests

# set work directory where the app test files are
WORKDIR /tests

# Provide a known path for the virtual environment by creating a symlink
RUN ln -s $(poetry env info --path) /var/my-venv

# Hide virtual env prompt
ENV VIRTUAL_ENV_DISABLE_PROMPT=1

# Start virtual env when bash starts
RUN echo "source /var/my-venv/bin/activate" >> ~/.bashrc

# database info necessary to run tests
ENV DATABASE_NAME="TestDB"

FROM build-stage as production-stage
ARG APPLICATION_SERVER_PORT=8000

# i like bash
SHELL ["/bin/bash", "-c"]

# copy app files
COPY /demo_fastapi /demo_fastapi
COPY /README.md /README.md

# install project with poetry (only production stage requirements! ergo "--with") TODO
RUN poetry install --no-interaction

# Hide virtual env prompt
ENV VIRTUAL_ENV_DISABLE_PROMPT=1

# Start virtual env when bash starts
RUN echo "source /var/my-venv/bin/activate" >> ~/.bashrc

# set work dir where app files are
WORKDIR /demo_fastapi

# Document the exposed port
# https://docs.docker.com/engine/reference/builder/#expose
EXPOSE ${APPLICATION_SERVER_PORT}

# database info necessary to run tests
ENV DATABASE_NAME="ShoppingDB"

# Run the uvicorn application server.
# CMD exec uvicorn --host 0.0.0.0 --port $APPLICATION_SERVER_PORT --reload sales:app

