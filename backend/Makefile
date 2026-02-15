PYTHON ?= python

.PHONY: install run migrate test check schema collect seed

install:
	$(PYTHON) -m pip install -r requirements.txt

run: migrate
	$(PYTHON) manage.py load_seed
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

# Collect the topics from Google Patents Public Data (about 15 minutes).
collect:
	$(PYTHON) manage.py collect_patents
	$(PYTHON) manage.py fetch_figures

# Replace the bundled snapshot with the current database.
seed:
	$(PYTHON) manage.py dump_seed
