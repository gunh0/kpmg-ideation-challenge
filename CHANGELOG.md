# Changelog

## 1.1.0 — 2025-12-31

### Added

- Assignee and inventor pages: yearly activity, grant rate, latest publications, co-inventors and assignees; names in rankings, the patent list and the details panel link to them.
- Shareable details: the open patent is kept in the URL (`?patent=<id>`).
- Patent list: 25, 50 or 100 rows per page, one button to clear all filters, stacked cards on small screens.
- The yearly chart can be shown as a table. Print styles for dashboards and profiles.
- OpenAPI schema at `/api/schema/` (drf-spectacular); `make check` validates it.
- CSV exports are named after the dataset and the day.
- Logging to stdout (`DJANGO_LOG_LEVEL`); imports are logged.
- `make smoke` and a CI job that builds both images and checks the running Compose stack.

### Changed

- Python 3.13, Django 5.2 LTS, DRF 3.16, django-filter 25, gunicorn 23 with threaded workers (`GUNICORN_WORKERS`, `GUNICORN_THREADS`).
- Node.js 22, React 19, React Router 7, Vite 7, Vitest 4, Testing Library 16, ESLint 9 with the React Compiler rules.
- SQLite runs in WAL mode with immediate transactions; the admin's static files are compressed and content-hashed.
- The containers run as unprivileged users on read-only file systems without capabilities; nginx is `nginx-unprivileged` 1.28 on port 8080.
- Dependabot is off; dependencies are upgraded in planned batches like this one.

### Fixed

- A trailing space in the search box was removed while typing.
- The frontend health check always failed: `localhost` resolved to `::1`, where nginx does not listen.
- Hashed assets were served without the security headers.
- Focus moves into the details panel and back to the row when it closes.

### Security

- Content-Security-Policy: scripts and styles from the app only, images also from Google's patent image host.

## 1.0.0 — 2022-05-30

First release of the rebuilt app.

### Added

- Django 4.0 REST API: import of Google Patents CSV exports as datasets (upload or `import_patents` command), patent list with search, filters (dataset, assignee, inventor, grant status, publication years), ordering and pagination, CSV export, stats and assignee suggestions, health check.
- React 18 dashboard: patent list with URL-based filters and a details panel, dataset import by drag and drop, rename and delete, yearly chart and top assignee / inventor rankings with grant rates.
- Read-only mode (`PATENTS_READ_ONLY`), HTTPS settings (`DJANGO_HTTPS`), Docker images for both apps, Docker Compose with health checks, GitHub Actions CI, Dependabot.

### Security

- Only `http(s)` links from imported files are stored and rendered.
- Exported cells that a spreadsheet would evaluate as formulas are escaped.
- Settings come from the environment; the production image refuses to start without `DJANGO_SECRET_KEY`.

### Removed

- The 2020 challenge prototype: Selenium crawler, bundled chromedriver binaries, the legacy Django project and both React dashboard templates.

## 0.1.0 — 2020-02

KPMG Ideation Challenge 2020 prototype (team Jackpop).
