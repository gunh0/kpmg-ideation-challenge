# Changelog

## Unreleased

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
