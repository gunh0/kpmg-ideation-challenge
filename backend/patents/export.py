"""CSV export in the Google Patents column layout, so exports can be re-imported."""
import csv

from .csv_import import COLUMNS, FORMULA_PREFIXES


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
