# Contributing

## Setup

```bash
python3.13 -m venv backend/.venv && . backend/.venv/bin/activate
make install
make backend      # terminal 1
make frontend     # terminal 2 -> http://localhost:3000
```

`make backend` loads the bundled snapshot into an empty database, so the dashboard has data from the start.

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
- Patent data comes from a third party and is untrusted: render links through `safeUrl()`, never with `dangerouslySetInnerHTML`, and keep exported cells escaped (`patents/export.py`).
- Tests never touch the network: the collector reads a small Parquet file written by `patents/tests/opendata_fixture.py`, and figure lookups are mocked. Try a real collection on one file with `python manage.py collect_patents --shards 0` against a scratch database (`DJANGO_DB_PATH=/tmp/try.db`).
- Topics are data, added in the dashboard. Only a change of the **default** topics goes into `patents/topics.py`, with a refreshed snapshot (`make -C backend collect seed`) in the same pull request.
- Anything typed into a topic reaches the collector through `keywords.parse_keywords` and `topic_pattern`, and DuckDB as a query parameter. Keep it that way: no string formatting of user input into SQL or expressions.
- Collection jobs change topic state only through `jobs.py` (queue, claim, progress), so that the backend thread and the collector service never collect the same topic twice.
- Colors of chart series come from `--series-*` in `frontend/src/index.css`, with separate light and dark steps.
- Images may only come from Google's patent image host; widen the Content-Security-Policy in `frontend/security-headers.conf` if that changes.
