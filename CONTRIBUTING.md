# Contributing

## Setup

```bash
python3.10 -m venv backend/.venv && . backend/.venv/bin/activate
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

CI runs the same commands for each app (`.github/workflows/`).

- **Backend**: add or update a test in `backend/patents/tests/` for every behaviour change. A model change needs a migration (`python manage.py makemigrations`); `make check` fails otherwise.
- **Frontend**: tests live next to the code (`*.test.js[x]`, `__tests__/`) and run with Vitest and Testing Library. Prefer queries by role and label, as users and screen readers find elements.
- Keep the API and the dashboard in step: a new filter goes into `PatentFilter` (backend), the URL parameters of the patent list (frontend) and the table in `backend/README.md`.

## Conventions

- Commit messages follow `type: summary` — `feat`, `fix`, `test`, `docs`, `build`, `ci`, `perf`, `refactor`, `chore`.
- Data from uploaded files is untrusted: render links through `safeUrl()`, never with `dangerouslySetInnerHTML`, and keep exported cells escaped (`patents/export.py`).
- Colors of chart series come from `--series-*` in `frontend/src/index.css`, with separate light and dark steps.
