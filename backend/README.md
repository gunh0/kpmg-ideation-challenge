# Backend

Django REST API that collects the US patents of technology topics — defined by keywords, in the dashboard or here — from Google Patents Public Data and serves them, with their representative figures, citations and assignee countries, to the dashboard.

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
| `PATENTS_COLLECT_INTERVAL` | `86400` | `run_collector`: seconds between checks for a new revision of the data |
| `PATENTS_ALLOW_TOPIC_EDITS` | `1` | `0` refuses adding, editing and deleting topics through the API (the API has no accounts) |
| `PATENTS_MAX_TOPICS` | `20` | how many topics may exist |
| `PATENTS_COLLECT_IN_BACKEND` | `1` | collect added or edited topics in a thread of the web process; `0` in Compose, where the `collector` service does it |

## Data

A topic is a name, a description and keywords — words or phrases, matched as whole words in the lower-cased title and abstract of US publications since 2015, the last word also in its plural (`delivery` finds "deliveries"). Keywords are validated and escaped ([`keywords.py`](patents/keywords.py)) and reach DuckDB as query parameters, never as SQL. The defaults of a new instance are in [`topics.py`](patents/topics.py).

A patent is stored once and linked to every topic it matches; collecting a topic replaces its links and deletes patents no topic keeps.

| Command | |
|---|---|
| `python manage.py collect_patents [--topic drones] [--if-changed]` | collects the stored topics (an empty database gets the defaults first) from [Google Patents Public Data](https://console.cloud.google.com/marketplace/product/google_patents_public_datasets/google-patents-public-data), read from its [Parquet copy](https://huggingface.co/datasets/labofsahil/patents-publications-dataset) with DuckDB, then counts the applications citing each patent; `--if-changed` skips topics collected from the current revision |
| `python manage.py run_collector` | keeps collecting: topics queued from the dashboard (looks every 30 s) and all topics when the data has a new revision; the Compose `collector` service |
| `python manage.py fetch_figures [--latest 12]` | looks up figures for each topic's latest patents on Google Patents |
| `python manage.py dump_seed` / `load_seed [--force]` | writes / loads [`patents/seed/patents.json.gz`](patents/seed); loading only fills an empty database unless forced |
| `make collect seed` | collect, fetch figures, write the snapshot |

Topics wait in a queue (`status` queued → collecting → ready or failed, with `progress` of `progress_total` files); a worker claims all waiting topics with one UPDATE and collects them in one pass. A pass reads titles, abstracts and citations of 56 files, about 90 GB, which takes one to two hours on a laptop. DuckDB gets as many threads as the memory allows, about 100 MB each for the abstracts. A topic added in the dashboard is matched against the stored patents at once, so it is not empty meanwhile.

Figures of other patents are looked up when the dashboard first shows them (`/api/figures/`) and stored; publications since August 2025 have no image on Google yet.

## API

| Method | Path | |
|---|---|---|
| `GET` | `/api/topics/` | topics: `slug`, `name`, `description`, `keywords`, `pattern`, `patent_count`, `source_revision`, `collected_at`, `status`, `progress`, `progress_total`, `error` |
| `POST` | `/api/topics/` | `{"name", "keywords", "description"}` (keywords as a list or comma-separated): adds a topic, matched at once and queued for collection |
| `GET`, `PATCH`, `DELETE` | `/api/topics/{id}/` | new keywords are matched and collected again; deleting drops patents no other topic keeps |
| `POST` | `/api/topics/{id}/collect/` | queue the topic again, e.g. after a failure |
| `GET` | `/api/patents/` | paginated (`page`, `page_size` ≤ 200); each patent lists its `topics` and, with `?topics=`, how many of them it `matched` |
| `GET` | `/api/patents/{id}/` | |
| `GET` | `/api/patents/export/` | CSV in the column layout of Google Patents' download, named `patents-<topics>-<date>.csv` |
| `GET` | `/api/figures/?ids=1,2` | representative figures (`thumbnail`, `figure`, `checked`); unchecked ones are looked up first, up to 25 per request |
| `GET` | `/api/stats/` | `total`, `granted`, `by_year` (filed / published / granted), `top_assignees` (with their `granted` count), `top_inventors`, `top_countries`, `by_topic` (publications per year of up to 8 topics) (`top` = 1–50) |
| `GET` | `/api/assignees/` | assignee names and counts for suggestions (`topics`, `search`) |
| `GET` | `/api/config/` | `topic_edits`, `max_topics` |
| `GET` | `/api/health/` | `{"status": "ok"}` when the database answers |
| `GET` | `/api/schema/` | OpenAPI 3 description of all of the above |

Writes take JSON only, so a form on another site cannot post to the API.

`/api/patents/`, `/api/patents/export/` and `/api/stats/` share the filters:

| Parameter | |
|---|---|
| `topics` | topic ids, `1,2,3`: patents of any of them |
| `match` | `all`: only patents matching all of `topics` |
| `search` | id, title, abstract, assignee or inventor contains |
| `assignee` | exact name, case-insensitive |
| `inventor` | one of the inventors, whole name, case-insensitive |
| `country` | assignee country, e.g. `KR` |
| `granted` | `true` / `false` |
| `year_from`, `year_to` | publication year |
| `has_figure` | `true` / `false`: the representative figure is known |
| `ordering` | `matched` (with `topics`), `publication_date`, `priority_date`, `filing_date`, `grant_date`, `cited_by`, `patent_id`, `title`, `-` for descending; patents without the date come last |

Exported values that a spreadsheet would run as a formula (starting with `=`, `+`, `-`, `@`) are prefixed with `'`.
