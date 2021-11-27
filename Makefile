#!make
ROOT_PY3 := python3

POETRY := $(shell which poetry)
POETRY_VARS :=
ifeq ($(shell uname -s),Darwin)
	HOMEBREW_OPENSSL_DIR := $(shell brew --prefix openssl)
	POETRY_VARS += CFLAGS="-I$(HOMEBREW_OPENSSL_DIR)/include"
	POETRY_VARS += LDFLAGS="-L$(HOMEBREW_OPENSSL_DIR)/lib"
endif

BANDIT := $(POETRY) run bandit
BLACK := $(POETRY) run black
ISORT := $(POETRY) run isort
PIP := $(POETRY) run pip
PYLINT := $(POETRY) run pylint
PYTEST := $(POETRY) run pytest
PYTHON := $(POETRY) run python3

TESTS ?= tests/
PYTEST_ARGS += --disable-warnings --log-level DEBUG
DOCKER_IMAGE_BASE ?= rpi-lts-ctrl
DOCKER_IMAGE_SERVICE ?= $(DOCKER_IMAGE_BASE)-service
DOCKER_IMAGE_MONITOR ?= $(DOCKER_IMAGE_BASE)-monitor
DOCKER_DB_SEED_IMAGE ?= $(DOCKER_IMAGE_BASE)-db-seed
DOCKER_IMAGE_TAG ?= latest
DOCKER := docker
DOCKER_BUILD := $(DOCKER) build $(DOCKER_BUILD_ARGS)

include .env
export $(shell sed 's/=.*//' .env)


.PHONY: build build-dev docker-build format-py test run-rpi run-dev clean \
		test-sec lint-py lint-ts depends test-depends update-depends \
		build-db-seed rebuild-db-seed
		

depends: 
	pushd ./service && $(POETRY_VARS) $(POETRY) install --no-dev --no-root && popd

test-depends: 
	pushd ./service && $(POETRY_VARS) $(POETRY) install --no-root && popd

update-depends:
	pushd ./service && $(POETRY_VARS) $(POETRY) update && popd


build: build-service build-monitor build-db-seed

build-service:
	$(DOCKER_BUILD) -t $(DOCKER_IMAGE_SERVICE):$(DOCKER_IMAGE_TAG) service

build-monitor:
	$(DOCKER_BUILD) -t $(DOCKER_IMAGE_MONITOR):$(DOCKER_IMAGE_TAG) monitor

build-dev: build-service-dev build-monitor-dev build-db-seed

build-service-dev:
	$(DOCKER_BUILD) --build-arg build_for=dev -t $(DOCKER_IMAGE_SERVICE):$(DOCKER_IMAGE_TAG) service

build-monitor-dev:
	$(DOCKER_BUILD) --build-arg build_for=dev -t $(DOCKER_IMAGE_MONITOR):$(DOCKER_IMAGE_TAG) monitor

build-db-seed:
	$(DOCKER_BUILD) -t $(DOCKER_DB_SEED_IMAGE):$(DOCKER_IMAGE_TAG) db-seed

rebuild-db-seed:
	$(DOCKER_BUILD) -t $(DOCKER_DB_SEED_IMAGE):$(DOCKER_IMAGE_TAG) --no-cache db-seed

#test: update-git-depends ci

# test-py:
# 	CONFIG_PATH=pytest.json CONFIG_BASE_DIR=$(CONFIG_BASE_DIR) \
# 	$(PYTEST) ${PYTEST_ARGS} ${TESTS}

test-sec:
	$(BANDIT) -r service/api --exclude test

lint-py:
	$(ISORT) --check-only service/api
	$(PYLINT) api
	$(BLACK) --check service/api

lint-ts:
	yarn run lint

format-py:
	$(ISORT) service/api tests deploy
	$(BLACK) service/api tests deploy

run-rpi:
	docker-compose --project-directory deploy/rpi up

run-dev: build-dev build-db-seed
	docker-compose --project-directory deploy/local-dev up

run-db-migrations:
	./migrate.sh upgrade head

clean:
	docker-compose --project-directory deploy/local-dev down --volumes

clean-image:
	docker rmi $(DOCKER_IMAGE_SERVICE):$(DOCKER_IMAGE_TAG)
	docker rmi $(DOCKER_IMAGE_MONITOR):$(DOCKER_IMAGE_TAG)

clean-seed-image:
	docker rmi $(DOCKER_DB_SEED_IMAGE):$(DOCKER_IMAGE_TAG)

clean-images: clean-image clean-seed-image

clean-all: clean clean-images
