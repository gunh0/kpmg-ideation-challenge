# Patent Attorney Without Borders

A dashboard of US patents in three technology fields — drones, autonomous driving and cybersecurity — with the representative figure of each patent: who files, how much, since when, and what the inventions look like. `docker compose up` starts it with the data in place, and it refreshes itself when the public patent data changes.

> Originally built for the **KPMG Ideation Challenge 2020** by team **Jackpop** — leader [gunh0](https://github.com/gunh0), crew Ji-hun Lim, Seung-jae Lee and Min-soo Kim. The idea: a "borderless patent attorney" that helps inventors and companies see who already holds patents around their idea before they file. See [History](#history) for how it got here.

![Dashboard](docs/dashboard.png)

## Features

- **Dashboard** per topic or across all: patents, grants and applications, the latest patents as cards with their figures, filings / publications / grants per year (as a chart or a table), top assignees with their grant rate, top inventors.
- **Representative figures** from Google Patents in the dashboard, the patent list and the details; a figure or card opens the patent on Google Patents.
- **Patent list** with full-text search, filters for assignee (with suggestions), inventor, grant status and publication years, sortable columns, 25–100 rows per page. Filters and the open patent live in the URL, so every view can be shared.
- **Assignee and inventor pages**: activity per year, grant rate, latest publications, co-inventors — every name in the app links to its page.
- **Topics page**: what each topic matches, how many patents it holds and when it was collected.
- **CSV export** of any filtered list, in the column layout of Google Patents' own download.
- Dark mode, small screens, printing and keyboard use (`/` jumps to the search). OpenAPI description of the REST API at `/api/schema/`.

## Quick start

```bash
docker compose up -d --build     # or: make up
open http://localhost:8080
```

The first start loads the bundled snapshot of about 20,000 patents, so the dashboard is complete right away. A `collector` service checks the public data once a day and collects the topics again when it has a new revision.

## Data

| | |
|---|---|
| Patents | [Google Patents Public Data](https://console.cloud.google.com/marketplace/product/google_patents_public_datasets/google-patents-public-data) (BigQuery table `patents.publications`, CC BY 4.0), read without an account from its [Parquet copy on Hugging Face](https://huggingface.co/datasets/labofsahil/patents-publications-dataset) with DuckDB |
| Scope | US publications since 2015 whose title matches a topic ([`topics.py`](backend/patents/topics.py)); an application and its grant become one patent |
| Figures | Looked up on each patent's Google Patents page — pages of single patents are open to crawlers, the search is not — the first time the patent is shown, then stored |
| Snapshot | [`backend/patents/seed/`](backend/patents/seed), refreshed with `make -C backend collect seed` |

Collecting all topics reads the title column of 56 Parquet files (about 1 TB in total, of which only the needed columns are fetched) and takes around 15 minutes.

## Development

Requirements: Python 3.12+ (3.13 in Docker and CI), Node.js 22+.

```bash
make dev-back       # terminal 1: Django API  http://localhost:8000/api/  (creates backend/.venv, loads the snapshot)
make dev-front      # terminal 2: React app   http://localhost:3000       (proxies /api)
make test           # backend and frontend tests
make lint           # Django checks, pending migrations, OpenAPI schema, ESLint
make smoke          # build the Docker stack and check it end to end
```

## Architecture

```
browser ──► nginx (frontend container, :8080)
              ├── /            React 19 app (Vite build)
              └── /api, /admin ─► gunicorn + Django 5.2 REST API (backend container)
                                      └── SQLite in the backend-data volume
                  collector container ──► Google Patents Public Data (Parquet over HTTPS, DuckDB)
                  backend, on demand  ──► patents.google.com/patent/… for figures
```

| Path | |
|---|---|
| [`backend/`](backend) | Django REST Framework API: topics, patents, stats, figures, export; collection and snapshot commands. [API reference](backend/README.md) |
| [`frontend/`](frontend) | React 19 + Vite: dashboard, patent list, assignee and inventor pages, topics. Charts are plain SVG. |
| [`docker-compose.yml`](docker-compose.yml) | backend, collector and frontend with health checks |
| [`.github/workflows/`](.github/workflows) | CI for both apps and a smoke test of the Docker stack |

### Security notes

- The API only reads; there are no user accounts. The Django admin keeps its own login.
- Patent data comes from a third party: links are only rendered when they are `http(s)`, figures only from Google's patent image host, and exported cells that a spreadsheet would run as a formula are escaped.
- Set `DJANGO_SECRET_KEY` and, behind TLS, `DJANGO_HTTPS=1` for any deployment. All settings are listed in the [backend README](backend/README.md#configuration).
- The containers run as unprivileged users on read-only file systems without Linux capabilities; nginx sends a Content-Security-Policy that only allows the app's own scripts and Google's patent images.

## History

**2020 — challenge prototype.** A Selenium script opened Google Patents for a keyword and clicked the CSV download; a Django app stored the rows and a React admin template (Shards Dashboard) displayed them.

![2020 prototype](https://user-images.githubusercontent.com/41619898/75223211-4f70a400-57e9-11ea-8147-6e865d20126d.png)

**2022 — rewrite.** Automating the Google Patents UI broke whenever the page changed and is not how the site is meant to be used, so the rebuilt app imported the CSV that users downloaded themselves. Backend and frontend were rewritten from scratch with tests, CI and Docker; the Selenium script, the bundled chromedriver binaries and both React templates were removed.

**2025 — upgrade.** Django 5.2 LTS on Python 3.13, React 19 with Vite 7 on Node.js 22, hardened containers, assignee and inventor pages.

**2026 — automatic data.** Downloading exports by hand kept the dashboard empty until someone did it. The app now collects its topics from Google Patents Public Data on its own, ships a snapshot so it starts complete, and shows the representative figures again, as the 2020 prototype did. The CSV import was removed.

## License

[Apache License 2.0](LICENSE)
