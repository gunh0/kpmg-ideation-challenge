# Contributing

## Setup

```bash
python3.13 -m venv backend/.venv && . backend/.venv/bin/activate
make install
make backend      # terminal 1
make frontend     # terminal 2 -> http://localhost:3000
```

A test export to play with: `backend/patents/tests/fixtures/export.csv` (fictional `ZZ-` patents).

## Before opening a pull request

```bash
make lint
make test
```

CI runs the same commands for each app (`.github/workflows/`) and `make smoke`, which builds the Docker images and checks the running stack. Run it too when you touch a Dockerfile, `nginx.conf` or `docker-compose.yml`.

- **Backend**: add or update a test in `backend/patents/tests/` for every behaviour change. A model change needs a migration (`python manage.py makemigrations`); `make check` fails otherwise.
- **Frontend**: tests live next to the code (`*.test.js[x]`, `__tests__/`) and run with Vitest and Testing Library. Prefer queries by role and label, as users and screen readers find elements. ESLint (`eslint.config.js`) includes the React Compiler rules: derive values during render instead of copying props into state from an effect.
- **API responses** that are not models get a serializer in `patents/serializers.py` for the OpenAPI schema; `make check` fails on schema warnings.
- Keep the API and the dashboard in step: a new filter goes into `PatentFilter` (backend), the URL parameters of the patent list (frontend) and the table in `backend/README.md`.

## Conventions

- Commit messages follow `type: summary` — `feat`, `fix`, `test`, `docs`, `build`, `ci`, `perf`, `refactor`, `chore`.
- Data from uploaded files is untrusted: render links through `safeUrl()`, never with `dangerouslySetInnerHTML`, and keep exported cells escaped (`patents/export.py`).
- Colors of chart series come from `--series-*` in `frontend/src/index.css`, with separate light and dark steps.
- Images may only come from Google's patent image host; widen the Content-Security-Policy in `frontend/security-headers.conf` if that changes.
