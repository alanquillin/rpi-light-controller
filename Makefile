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
DOCKER_IMAGE_TAG_DEV ?= dev
DOCKER_SOURCE_IMAGE_TAG ?= latest
DOCKER := docker
DOCKER_BUILD := $(DOCKER) build $(DOCKER_BUILD_ARGS)
IMAGE_REPOSITORY := alanquillin
REPOSITORY_IMAGE_BASE ?= rpi-lights-controller
REPOSITORY_IMAGE_SERVICE ?= $(REPOSITORY_IMAGE_BASE)-service
REPOSITORY_IMAGE_MONITOR ?= $(REPOSITORY_IMAGE_BASE)-monitor

ifneq ("$(wildcard .env)","")
    include .env
	export $(shell sed 's/=.*//' .env)
endif

ifeq ("$(wildcard deploy/local-dev/.env)","")
    $(shell touch deploy/local-dev/.env)
endif


.PHONY: build build-dev docker-build format-py test run-rpi run-dev clean \
		test-sec lint-py lint-ts depends test-depends update-depends \
		build-db-seed rebuild-db-seed
		

# dependency targets

depends: 
	pushd ./service && $(POETRY_VARS) $(POETRY) install --no-dev --no-root && popd

test-depends: 
	pushd ./service && $(POETRY_VARS) $(POETRY) install --no-root && popd

update-depends:
	pushd ./service && $(POETRY_VARS) $(POETRY) update && popd

# Targets for building containers

# prod

build: build-service build-monitor

build-service:
	$(DOCKER_BUILD) --platform=linux/arm -t $(DOCKER_IMAGE_SERVICE):$(DOCKER_IMAGE_TAG) service

build-monitor:
	$(DOCKER_BUILD) --platform=linux/arm -t $(DOCKER_IMAGE_MONITOR):$(DOCKER_IMAGE_TAG) monitor

# dev

build-dev: build-service-dev build-monitor-dev build-db-seed

build-service-dev:
	$(DOCKER_BUILD) --build-arg build_for=dev -t $(DOCKER_IMAGE_SERVICE):$(DOCKER_IMAGE_TAG_DEV) service

build-monitor-dev:
	$(DOCKER_BUILD) --build-arg build_for=dev -t $(DOCKER_IMAGE_MONITOR):$(DOCKER_IMAGE_TAG_DEV) monitor

build-db-seed: build-service-dev
	$(DOCKER_BUILD) -t $(DOCKER_DB_SEED_IMAGE):$(DOCKER_IMAGE_TAG_DEV) db-seed

# Targets for publishing containers

tag-service: build-service
	$(DOCKER) tag $(DOCKER_IMAGE_SERVICE):$(DOCKER_SOURCE_IMAGE_TAG) $(IMAGE_REPOSITORY)/$(REPOSITORY_IMAGE_SERVICE):$(DOCKER_IMAGE_TAG)

tag-monitor: build-monitor
	$(DOCKER) tag $(DOCKER_IMAGE_MONITOR):$(DOCKER_SOURCE_IMAGE_TAG) $(IMAGE_REPOSITORY)/$(REPOSITORY_IMAGE_MONITOR):$(DOCKER_IMAGE_TAG)

tag: tag-service tag-monitor

publish-service: tag-service
	$(DOCKER) push $(IMAGE_REPOSITORY)/$(REPOSITORY_IMAGE_SERVICE):$(DOCKER_IMAGE_TAG)

publish-monitor: tag-monitor
	$(DOCKER) push $(IMAGE_REPOSITORY)/$(REPOSITORY_IMAGE_MONITOR):$(DOCKER_IMAGE_TAG)

publish: publish-service publish-monitor

# Testing and Syntax targets

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

# Targets for running the app

run-rpi:
	docker-compose --project-directory deploy/rpi pull && \
	docker-compose --project-directory deploy/rpi up

run-dev: build-dev
	docker-compose --project-directory deploy/local-dev up

run-db-migrations:
	./migrate.sh upgrade head

# Clean up targets

clean:
	docker-compose --project-directory deploy/local-dev down --volumes

clean-image:
	docker rmi $(DOCKER_IMAGE_SERVICE):$(DOCKER_IMAGE_TAG)
	docker rmi $(DOCKER_IMAGE_MONITOR):$(DOCKER_IMAGE_TAG)

clean-seed-image:
	docker rmi $(DOCKER_DB_SEED_IMAGE):$(DOCKER_IMAGE_TAG)

clean-images: clean-image clean-seed-image

clean-all: clean clean-images