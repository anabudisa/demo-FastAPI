# copyright https://github.com/max-pfeiffer/python-poetry/blob/main/build/Dockerfile
# using Python 3.10 as base image
ARG OFFICIAL_PYTHON_IMAGE=3.10-slim-bookworm
FROM ${OFFICIAL_PYTHON_IMAGE} as build-stage
ARG POETRY_VERSION=1.6.1

# References:
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

# base build
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        build-essential

# install poetry
# https://python-poetry.org/docs/#installing-manually
RUN python -m venv ${POETRY_HOME}
RUN ${POETRY_HOME}/bin/pip install -U pip setuptools
RUN ${POETRY_HOME}/bin/pip install "poetry==${POETRY_VERSION}"

# setup a poetry venv
ENV PATH="$PATH:/root/.local/bin" \
    POETRY_CACHE_DIR="/.cache" \
    VIRTUAL_ENVIRONMENT_PATH="/.venv" \
    APPLICATION_SERVER_PORT=$APPLICATION_SERVER_PORT \
    POETRY_VIRTUALENVS_IN_PROJECT=true \

# install requirements and poetry venv
COPY poetry.lock pyproject.toml ./
RUN poetry install --no-interaction

# Provide a known path for the virtual environment by creating a symlink
RUN ln -s $(poetry env info --path) /var/my-venv

# Hide virtual env prompt
ENV VIRTUAL_ENV_DISABLE_PROMPT=1

# Start virtual env when bash starts
RUN echo "source /var/my-venv/bin/activate" >> ~/.bashrc

FROM ${OFFICIAL_PYTHON_IMAGE} as test-stage

ENV PATH="/opt/poetry/bin:$PATH"

# make sure poetry is available that is built in build-stage
COPY --from=build-stage /opt/poetry /opt/poetry/

# copy the app files??
COPY /demo_fastapi /demo
COPY /tests /tests
# work directory where the app files are
WORKDIR /tests

# run tests
RUN pytest .

FROM ${OFFICIAL_PYTHON_IMAGE} as production-stage
ARG APPLICATION_SERVER_PORT=8000

COPY --from=test-stage /opt/poetry /opt/poetry
COPY --from=test-stage /demo /demo

WORKDIR /demo

# Document the exposed port
# https://docs.docker.com/engine/reference/builder/#expose
EXPOSE ${APPLICATION_SERVER_PORT}

# Run the uvicorn application server.
CMD exec uvicorn --host 0.0.0.0 --port $APPLICATION_SERVER_PORT --reload sales:app
