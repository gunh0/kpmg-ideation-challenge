# Patent Attorney Without Borders
#
#   make up         build and start everything in Docker    -> http://localhost:8080
#   make down       stop it
#   make dev-back   API dev server in backend/.venv          -> http://localhost:8000/api/
#   make dev-front  React dev server, proxies /api           -> http://localhost:3000
#   make test       backend and frontend tests
#   make lint       Django checks, migrations, OpenAPI schema, ESLint
#   make smoke      start the Docker stack and check it end to end (as CI does)

.PHONY: up down smoke dev-back dev-front test lint

# Python 3.13 if installed, else the default python3 (3.12+ works).
PYTHON ?= $(shell command -v python3.13 || command -v python3)
VENV := backend/.venv
VENV_PYTHON := $(CURDIR)/$(VENV)/bin/python
NODE_MODULES := frontend/node_modules/.package-lock.json

up:
	docker compose up -d --build
	@echo "Open http://localhost:8080"

down:
	docker compose down

smoke:
	docker compose up -d --build --wait --wait-timeout 180
	scripts/smoke.sh

# The first run creates backend/.venv, installs the requirements and loads the
# bundled snapshot into backend/db.sqlite3; later runs start right away.
dev-back: $(VENV)/.installed
	$(MAKE) -C backend run PYTHON=$(VENV_PYTHON)

dev-front: $(NODE_MODULES)
	cd frontend && npm run dev

test: $(VENV)/.installed $(NODE_MODULES)
	$(MAKE) -C backend test PYTHON=$(VENV_PYTHON)
	cd frontend && npm test

lint: $(VENV)/.installed $(NODE_MODULES)
	$(MAKE) -C backend check PYTHON=$(VENV_PYTHON)
	cd frontend && npm run lint

$(VENV)/.installed: backend/requirements.txt
	test -d $(VENV) || $(PYTHON) -m venv $(VENV)
	$(VENV)/bin/pip install --quiet --upgrade pip
	$(VENV)/bin/pip install --quiet -r backend/requirements.txt
	touch $@

$(NODE_MODULES): frontend/package-lock.json
	cd frontend && npm ci --no-audit --no-fund
