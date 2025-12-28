# Patent Attorney Without Borders

Explore [Google Patents](https://patents.google.com) search results by assignee, inventor and year: import the CSV export of any search and get a searchable patent list and a dashboard of filings, grants and the most active players.

> Originally built for the **KPMG Ideation Challenge 2020** by team **Jackpop** — leader [gunh0](https://github.com/gunh0), crew Ji-hun Lim, Seung-jae Lee and Min-soo Kim. The idea: a "borderless patent attorney" that helps inventors and companies see who already holds patents around their idea before they file. Rebuilt in 2022 as a maintainable web app (see [History](#history)).

## Features

- **Import** the CSV that Google Patents' *Download (CSV)* button produces — drag and drop in the browser, or `make import` on the command line. Each file becomes a dataset named after its search query.
- **Patent list** with full-text search, filters for assignee (with suggestions), inventor, grant status and publication years, sortable columns and pagination. Filters live in the URL, so every view can be bookmarked or shared.
- **Details panel** with inventors, priority / filing / publication / grant dates, the representative figure and a link to the patent on Google Patents. The open patent is part of the URL, so it can be shared.
- **Dashboard**: filings, publications and grants per year (as a chart or a table), top assignees with their grant rate, top inventors.
- **Assignee and inventor pages**: activity per year, grant rate, latest publications, co-inventors — every name in the app links to its page.
- **CSV export** of any filtered list, in the Google Patents layout so it can be imported again.
- Dark mode, small screens, printing and keyboard use (`/` jumps to the search).
- **OpenAPI** description of the REST API at `/api/schema/`.
- **Read-only mode** for public demos (`PATENTS_READ_ONLY=1`).

## Quick start

```bash
docker compose up -d --build     # or: make up
open http://localhost:8080
```

Then go to **Datasets** and import a file:

1. Search on [patents.google.com](https://patents.google.com), e.g. `(drone delivery)`.
2. Click **Download (CSV)** above the results.
3. Drop the file on the import area.

## Development

Requirements: Python 3.13, Node.js 22.

```bash
make install        # backend requirements + frontend packages
make backend        # Django API        http://localhost:8000/api/
make frontend       # React dev server  http://localhost:3000  (proxies /api)
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
```

| Path | |
|---|---|
| [`backend/`](backend) | Django REST Framework API: CSV import, patents, datasets, stats, export. [API reference](backend/README.md) |
| [`frontend/`](frontend) | React 19 + Vite: dashboard, patent list, assignee and inventor pages, datasets. Charts are plain SVG. |
| [`docker-compose.yml`](docker-compose.yml) | backend + frontend with health checks |
| [`.github/workflows/`](.github/workflows) | CI for both apps and a smoke test of the Docker stack |

### Security notes

- There are no user accounts: run it locally or behind your own authentication, or enable `PATENTS_READ_ONLY=1` for a public read-only instance. The Django admin keeps its own login.
- Uploaded files are data from a third party: links are only rendered when they are `http(s)`, and exported cells that a spreadsheet would run as a formula are escaped.
- Set `DJANGO_SECRET_KEY` and, behind TLS, `DJANGO_HTTPS=1` for any deployment. All settings are listed in the [backend README](backend/README.md#configuration).
- The containers run as unprivileged users on read-only file systems without Linux capabilities; nginx sends a Content-Security-Policy that only allows the app's own scripts and Google's patent images.

## History

**2020 — challenge prototype.** A Selenium script opened Google Patents for a keyword and clicked the CSV download; a Django app stored the rows and a React admin template (Shards Dashboard) displayed them.

![2020 prototype](https://user-images.githubusercontent.com/41619898/75223211-4f70a400-57e9-11ea-8147-6e865d20126d.png)

**2022 — rewrite.** Automating the Google Patents UI broke whenever the page changed and is not how the site is meant to be used, so the app now imports the CSV that users download themselves. Backend and frontend were rewritten from scratch with tests, CI and Docker; the Selenium script, the bundled chromedriver binaries and both React templates were removed.

**2025 — upgrade.** Django 5.2 LTS on Python 3.13, React 19 with Vite 7 on Node.js 22, hardened containers, assignee and inventor pages.

## License

[Apache License 2.0](LICENSE)
