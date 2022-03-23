"""CSV export in the Google Patents column layout, so exports can be re-imported."""
import csv

from .csv_import import COLUMNS


class Echo:
    """File-like object whose write() returns the value, for streaming csv rows."""

    def write(self, value):
        return value


def export_rows(queryset):
    writer = csv.writer(Echo())
    yield writer.writerow(COLUMNS.keys())
    for patent in queryset.iterator():
        yield writer.writerow(
            [
                "" if getattr(patent, field) is None else getattr(patent, field)
                for field in COLUMNS.values()
            ]
        )
