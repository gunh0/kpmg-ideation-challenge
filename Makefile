# Patent Attorney Without Borders
#
#   make up         build and start everything in Docker   -> http://localhost:8080
#   make backend    API dev server (Python 3.10)           -> http://localhost:8000/api/
#   make frontend   React dev server, proxies /api          -> http://localhost:3000

.PHONY: up down logs backend frontend install test lint

up:
	docker compose up -d --build
	@echo "Open http://localhost:8080"

down:
	docker compose down

logs:
	docker compose logs -f

backend:
	$(MAKE) -C backend run

frontend:
	cd frontend && npm run dev

install:
	$(MAKE) -C backend install
	cd frontend && npm ci

test:
	$(MAKE) -C backend test
	cd frontend && npm test

lint:
	$(MAKE) -C backend check
	cd frontend && npm run lint
