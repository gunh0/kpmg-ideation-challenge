"""CSV export in the column layout of Google Patents' own CSV download."""
import csv

COLUMNS = {
    "id": "patent_id",
    "title": "title",
    "assignee": "assignee",
    "inventor/author": "inventors",
    "priority date": "priority_date",
    "filing/creation date": "filing_date",
    "publication date": "publication_date",
    "grant date": "grant_date",
    "result link": "result_link",
    "representative figure link": "figure_link",
}
# Characters that make a spreadsheet treat a cell as a formula.
FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


class Echo:
    """File-like object whose write() returns the value, for streaming csv rows."""

    def write(self, value):
        return value


def cell(value):
    """Neutralise values a spreadsheet would run as a formula (CSV injection):
    titles and names come from third-party data."""
    if value is None:
        return ""
    value = str(value)
    if value.startswith(FORMULA_PREFIXES):
        return "'" + value
    return value


def export_rows(queryset):
    writer = csv.writer(Echo())
    yield writer.writerow(COLUMNS.keys())
    for patent in queryset.iterator():
        yield writer.writerow([cell(getattr(patent, field)) for field in COLUMNS.values()])
