PYTHON ?= python

.PHONY: install run migrate test check schema import

install:
	$(PYTHON) -m pip install -r requirements.txt

run: migrate
	$(PYTHON) manage.py runserver 0.0.0.0:8000

migrate:
	$(PYTHON) manage.py migrate

test:
	$(PYTHON) manage.py test --parallel auto --shuffle

# Fails when a model change has no migration yet.
check:
	$(PYTHON) manage.py check
	$(PYTHON) manage.py makemigrations --check --dry-run
	$(PYTHON) manage.py spectacular --validate --fail-on-warn --file /dev/null

# OpenAPI description of the API, also served at /api/schema/
schema:
	$(PYTHON) manage.py spectacular --validate --file openapi.yaml

# make import CSV=gp-search-20220301.csv [NAME="Drone delivery"]
import:
	$(PYTHON) manage.py import_patents "$(CSV)" --name "$(NAME)"
