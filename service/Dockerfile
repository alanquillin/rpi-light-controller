# NodeJS base
# ############################################################
FROM node:16-buster-slim as node-base

RUN yarn global add @angular/cli
COPY ui/angular.json ui/tsconfig.app.json ui/tsconfig.json ui/package.json /ui/
WORKDIR /ui
RUN yarn install --non-interactive
COPY ui/src /ui/src

# Python base
# ############################################################
FROM python:3.8-slim-buster as python-base

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc build-essential libpq-dev libffi-dev libssl-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install -U pip 
RUN pip install setuptools wheel
ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1
RUN pip install "cryptography<3.5"
RUN pip install "poetry>=1.1.11"

RUN poetry config virtualenvs.in-project true
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-interaction --no-ansi --no-dev --no-root
RUN poetry run pip install psycopg2-binary rpi.gpio

RUN apt-get purge -y --auto-remove gcc build-essential libffi-dev libssl-dev

# Angular build
# ############################################################
FROM node-base as node-build

ARG build_for=prod
RUN yarn run build:${build_for}

# Final build
# ############################################################
FROM python-base as final

ARG build_for=prod

ENV CONFIG_PATH=${CONFIG_PATH}
ENV PYTHONUNBUFFERED=1
ENV CONFIG_BASE_DIR=/rpi-lights-controller/config
ENV RUN_ENV=${build_for}

COPY --from=node-build /ui/dist/rpi-lts-ctrl /rpi-lights-controller/api/static/

COPY api /rpi-lights-controller/api
COPY entrypoint.sh /rpi-lights-controller/api

WORKDIR /rpi-lights-controller/api

EXPOSE 5000

ENTRYPOINT ["/bin/sh", "entrypoint.sh"]
