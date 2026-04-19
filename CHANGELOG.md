# Changelog

## 3.0.0 — 2026-04-19

Topics are defined in the dashboard and combined: select the topics that describe an idea, and the patents matching most of them come first.

### Added

- Add, edit and delete topics on the Topics page: a name and keywords, matched as whole words in titles and abstracts, plurals included. A new topic shows the stored patents it matches at once and is then collected from the public data, with its progress, failures and a retry on the page. `PATENTS_ALLOW_TOPIC_EDITS` and `PATENTS_MAX_TOPICS` bound it; `/api/config/` tells the dashboard.
- Select several topics in the header; the patent list ranks patents by the number of selected topics they match, then by citations, or keeps only those matching all (`?topics=1,2&match=all`, ordering `matched`).
- Dashboard: the topics' publications per year side by side, assignee countries (narrowing the dashboard to one country), the most cited patents.
- Patents keep their abstract, the country of their first assignee and the number of applications citing them; search covers abstracts, the list filters by country and sorts by citations, the details show all of it.
- A collection queue (`jobs.py`) that the web process and the `run_collector` service share; the Compose collector picks up dashboard topics within 30 seconds.
- A hint to start the backend when the API cannot be reached.

### Changed

- Patents are stored once and linked to all topics they match (`Topic` replaces `Dataset`); `/api/topics/` replaces `/api/datasets/`, `?topics=` replaces `?dataset=`.
- Topics are matched in titles and abstracts: the snapshot holds 32,862 patents (was 20,152), 422 of them in more than one topic.
- The snapshot is one file with topics, keywords and links, loaded into an empty database only, so deleted topics stay deleted.
- DuckDB's threads follow the available memory (abstract chunks take about 100 MB each).
- Chart axes also round to 2.5 steps.

### Fixed

- A stalled HTTP read could hang a collection for a day: `http_timeout` is in seconds, not milliseconds.
- Plurals ending in -ies and -es are matched.

### Removed

- `/api/datasets/` and the `dataset` parameter.

## 2.0.0 — 2026-03-07

The dashboard fills itself: patents are collected from Google Patents Public Data instead of imported by hand.

### Added

- Topics — drones, autonomous driving, cybersecurity (`patents/topics.py`): US publications since 2015 whose title matches, one patent per application with its grant.
- `collect_patents` reads Google Patents Public Data (CC BY 4.0) from its Parquet copy with DuckDB, without an account; `--if-changed` skips a revision that was collected already.
- A snapshot of about 20,000 patents in `patents/seed/` (`dump_seed`, `load_seed`), loaded on the first start, so `docker compose up` shows a complete dashboard.
- A `collector` Compose service that checks the data daily and collects again when it changes.
- Representative figures from Google Patents: in the dashboard's latest patents, the patent list and the details, each opening the patent on Google Patents. `/api/figures/` looks up missing figures, `fetch_figures` prepares the dashboard's; filter `has_figure`.
- Topics page with each topic's description, pattern, patent count, collection date and the data source; a footer credits the data.
- Counts with thousands separators.

### Changed

- `/api/datasets/` lists the topics, read-only, with `slug`, `description`, `pattern`, `source_revision` and `collected_at`.
- The CSV export keeps the Google Patents column layout but is no longer meant to be imported.

### Removed

- The CSV import: upload, rename and delete of datasets, `import_patents`, and the read-only mode (`PATENTS_READ_ONLY`, `/api/config/`), as nothing is written through the API any more.

### Fixed

- HTML entities in titles and names of the public data (`&#39;`, `&amp;`) are decoded.
- Figures whose image Google does not serve yet (publications since August 2025) are not stored.

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
