# Backend

Django REST API that collects US patents of a few technology topics from Google Patents Public Data and serves them, with their representative figures, to the dashboard.

## Run

```bash
python -m venv .venv && . .venv/bin/activate
make install
make run                      # loads the snapshot if the database is empty -> http://localhost:8000/api/
make test
make check                    # system checks, pending migrations, OpenAPI schema
```

With Docker: `docker build -t patent-backend . && docker run -p 8000:8000 -e DJANGO_SECRET_KEY=... patent-backend`

## Configuration

| Variable | Default | |
|---|---|---|
| `DJANGO_DEBUG` | `1` | `0` in the Docker image |
| `DJANGO_SECRET_KEY` | development key | required when debug is off |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | comma-separated |
| `DJANGO_CORS_ALLOWED_ORIGINS` | `http://localhost:3000,http://127.0.0.1:3000` | the frontend dev server |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | – | e.g. `https://patents.example.com` for the admin |
| `DJANGO_HTTPS` | `0` | `1` behind a TLS proxy: secure cookies, HSTS, HTTPS redirect |
| `DJANGO_DB_PATH` | `db.sqlite3` | `/data/db.sqlite3` in the Docker image |
| `DJANGO_LOG_LEVEL` | `INFO` | Django and app messages on stdout |
| `GUNICORN_WORKERS`, `GUNICORN_THREADS` | `3`, `4` | Docker image only, see `gunicorn.conf.py` |
| `DUCKDB_EXTENSION_DIRECTORY` | DuckDB's default | set in the image, where DuckDB's httpfs is installed at build time |
| `PATENTS_COLLECT_INTERVAL` | `86400` | Compose `collector` service: seconds between checks for new data |

## Data

The topics are defined in [`patents/topics.py`](patents/topics.py): a name, a description and a regular expression matched against the lower-cased titles of US publications since 2015.

| Command | |
|---|---|
| `python manage.py collect_patents [--topic drones] [--if-changed]` | reads [Google Patents Public Data](https://console.cloud.google.com/marketplace/product/google_patents_public_datasets/google-patents-public-data) from its [Parquet copy](https://huggingface.co/datasets/labofsahil/patents-publications-dataset) with DuckDB, merges each application with its grant and replaces the topics' patents; `--if-changed` does nothing when the data has the revision collected last time |
| `python manage.py fetch_figures [--latest 12]` | looks up the representative figures of each topic's latest patents on Google Patents |
| `python manage.py dump_seed` / `load_seed [--force]` | writes / loads the snapshot in [`patents/seed/`](patents/seed) |
| `make collect seed` | all of it: collect, fetch figures, write the snapshot |

Collection reads only the columns it needs from 56 Parquet files, two at a time with many range requests each, and takes around 15 minutes. Figures of other patents are looked up when the dashboard first shows them (`/api/figures/`) and stored; publications since August 2025 have no image on Google yet.

## API

| Method | Path | |
|---|---|---|
| `GET` | `/api/datasets/` | the topics: `slug`, `name`, `description`, `pattern`, `source_revision`, `collected_at`, `patent_count` |
| `GET` | `/api/datasets/{id}/` | |
| `GET` | `/api/patents/` | paginated (`page`, `page_size` ≤ 200) |
| `GET` | `/api/patents/{id}/` | |
| `GET` | `/api/patents/export/` | CSV in the column layout of Google Patents' download, named `patents-<topic>-<date>.csv` |
| `GET` | `/api/figures/?ids=1,2` | representative figures (`thumbnail`, `figure`, `checked`); unchecked ones are looked up first, up to 25 per request |
| `GET` | `/api/stats/` | `total`, `granted`, `by_year` (filed / published / granted), `top_assignees` (with their `granted` count), `top_inventors` (`top` = 1–50) |
| `GET` | `/api/assignees/` | assignee names and counts for suggestions (`dataset`, `search`) |
| `GET` | `/api/health/` | `{"status": "ok"}` when the database answers |
| `GET` | `/api/schema/` | OpenAPI 3 description of all of the above (`make schema` writes it to `openapi.yaml`) |

`/api/patents/`, `/api/patents/export/` and `/api/stats/` share the filters:

| Parameter | |
|---|---|
| `dataset` | topic id |
| `search` | id, title, assignee or inventor contains |
| `assignee` | exact name, case-insensitive |
| `inventor` | one of the inventors, whole name, case-insensitive |
| `granted` | `true` / `false` |
| `year_from`, `year_to` | publication year |
| `has_figure` | `true` / `false`: the representative figure is known |
| `ordering` | `publication_date`, `priority_date`, `filing_date`, `grant_date`, `patent_id`, `title`, `-` for descending; patents without the date come last |

Exported values that a spreadsheet would run as a formula (starting with `=`, `+`, `-`, `@`) are prefixed with `'`.
