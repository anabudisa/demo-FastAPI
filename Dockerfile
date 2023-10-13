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

# install requirements and poetry venv (without requiring root directory of the project)
COPY poetry.lock pyproject.toml $HOME/
# COPY /demo_fastapi /demo_fastapi
# RUN poetry install --no-interaction
RUN poetry install --no-interaction --no-root

# Provide a known path for the virtual environment by creating a symlink
RUN ln -s $(poetry env info --path) /var/my-venv

# Hide virtual env prompt
ENV VIRTUAL_ENV_DISABLE_PROMPT=1

# Start virtual env when bash starts
RUN echo "source /var/my-venv/bin/activate" >> ~/.bashrc

FROM ${OFFICIAL_PYTHON_IMAGE} as test-stage

# i like bash
SHELL ["/bin/bash", "-c"]

# for poetry command to work
ENV PATH="/opt/poetry/bin:$PATH" \
    POETRY_VIRTUALENVS_IN_PROJECT=true

# Add the dependencies for the odbc lib (for some reason they need to be reinstalled??)
ENV ACCEPT_EULA=Y
RUN apt-get update && apt-get install -y unixodbc-dev
# Copy dependencies from the build image
# to avoid errors like ('01000', "[01000] [unixODBC][Driver Manager]Can't open lib 'SQL Server' : file not found (0) (SQLDriverConnect)")
COPY --from=build-stage  /usr/lib  /usr/lib
COPY --from=build-stage /etc/odbcinst.ini /etc/odbcinst.ini
# to avoid errors like ('01000', "[01000] [unixODBC][Driver Manager]Can't open lib '/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.10.so.5.1' : file not found (0) (SQLDriverConnect)")
COPY --from=build-stage /opt/microsoft/ /opt/microsoft/

# make sure poetry is available which is built in build-stage
COPY --from=build-stage /opt/poetry /opt/poetry/
COPY --from=build-stage /var /var

# activate poetry venv
# install requirements (only for test stage! ergo "--with test") and poetry venv
COPY --from=build-stage ./poetry.lock ./pyproject.toml $HOME/
RUN poetry install --no-interaction --no-root --with test
RUN source $(poetry env info --path)/bin/activate

# copy the app files??
COPY /demo_fastapi /demo_fastapi
COPY /tests /tests

# set work directory where the app test files are
WORKDIR /tests
# run tests
RUN poetry run pytest .

FROM ${OFFICIAL_PYTHON_IMAGE} as production-stage
ARG APPLICATION_SERVER_PORT=8000

# i like bash
SHELL ["/bin/bash", "-c"]

# for poetry command to work
ENV PATH="/opt/poetry/bin:$PATH" \
    POETRY_VIRTUALENVS_IN_PROJECT=true

# copy poetry files (for poetry command to work) and app files
COPY --from=build-stage /opt/poetry /opt/poetry
COPY /demo_fastapi /demo_fastapi
COPY /README.md /README.md

# install project with poetry (only production stage requirements! ergo "--with") TODO
COPY --from=build-stage ./poetry.lock ./pyproject.toml $HOME/
RUN poetry install --no-interaction --no-root
RUN source $(poetry env info --path)/bin/activate

# Hide virtual env prompt
ENV VIRTUAL_ENV_DISABLE_PROMPT=1

# Start virtual env when bash starts
RUN echo "source /var/my-venv/bin/activate" >> ~/.bashrc

# set work dir where app files are FIXME
WORKDIR /demo_fastapi

# Document the exposed port
# https://docs.docker.com/engine/reference/builder/#expose
EXPOSE ${APPLICATION_SERVER_PORT}

# Run the uvicorn application server.
CMD exec uvicorn --host 0.0.0.0 --port $APPLICATION_SERVER_PORT --reload sales:app

