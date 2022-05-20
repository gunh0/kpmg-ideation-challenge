# Backend

Django REST API that stores [Google Patents](https://patents.google.com) search result exports and serves them to the dashboard.

## Run

```bash
python -m venv .venv && . .venv/bin/activate
make install
make run                      # http://localhost:8000/api/
make import CSV=export.csv    # or upload through the API / dashboard
make test
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

## Getting data

On patents.google.com, run a search and choose **Download (CSV)** above the results. The file starts with the search URL, followed by one row per result:

```
search URL:,https://patents.google.com/?q=(drone+delivery)
id,title,assignee,inventor/author,priority date,filing/creation date,publication date,grant date,result link,representative figure link
```

Each upload becomes a **dataset** named after the search query. A patent listed twice in one file is stored once; rows without an id or title are skipped.

## API

| Method | Path | |
|---|---|---|
| `GET` | `/api/datasets/` | datasets with `patent_count` |
| `POST` | `/api/datasets/` | multipart `file` (+ optional `name`): import an export, returns the dataset and an `import` summary |
| `GET`, `DELETE` | `/api/datasets/{id}/` | |
| `PATCH` | `/api/datasets/{id}/` | `{"name": "..."}` renames a dataset |
| `GET` | `/api/patents/` | paginated (`page`, `page_size` ≤ 200) |
| `GET` | `/api/patents/{id}/` | |
| `GET` | `/api/patents/export/` | CSV in the Google Patents layout; can be imported again |
| `GET` | `/api/stats/` | `total`, `granted`, `by_year` (filed / published / granted), `top_assignees` (with their `granted` count), `top_inventors` (`top` = 1–50) |
| `GET` | `/api/assignees/` | assignee names and counts for suggestions (`dataset`, `search`) |
| `GET` | `/api/health/` | `{"status": "ok"}` when the database answers |

`/api/patents/`, `/api/patents/export/` and `/api/stats/` share the filters:

| Parameter | |
|---|---|
| `dataset` | dataset id |
| `search` | id, title, assignee or inventor contains |
| `assignee` | exact name, case-insensitive |
| `inventor` | one of the inventors, whole name, case-insensitive |
| `granted` | `true` / `false` |
| `year_from`, `year_to` | publication year |
| `ordering` | `publication_date`, `priority_date`, `filing_date`, `grant_date`, `patent_id`, `title`, `-` for descending; patents without the date come last |

Exported values that a spreadsheet would run as a formula (starting with `=`, `+`, `-`, `@`) are prefixed with `'`, which is removed again on import.
