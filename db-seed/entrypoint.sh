#! /bin/sh

poetry run ./migrate.sh upgrade head
poetry run python seed-db.py
