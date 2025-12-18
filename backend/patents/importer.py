"""Store parsed Google Patents exports as datasets."""
import logging
from dataclasses import dataclass
from urllib.parse import parse_qs, urlparse

from django.db import transaction
from django.utils import timezone

from .csv_import import parse_export
from .models import Dataset, Patent

logger = logging.getLogger(__name__)


@dataclass
class ImportResult:
    dataset: Dataset
    imported: int
    duplicates: int
    skipped: int


def dataset_name(search_url):
    """Name a dataset after the query of its search URL, e.g. "(drone delivery)"."""
    query = parse_qs(urlparse(search_url).query).get("q")
    if query and query[0].strip():
        return query[0].strip()[:200]
    return f"Import {timezone.now():%Y-%m-%d %H:%M}"


@transaction.atomic
def import_export(text, name=""):
    """Parse an export and store it as a new dataset.

    A patent listed more than once in the same export is stored once, with the
    values of its last row.
    """
    parsed = parse_export(text)
    dataset = Dataset.objects.create(
        name=name.strip() or dataset_name(parsed.search_url),
        search_url=parsed.search_url,
    )

    rows = {}
    for row in parsed.rows:
        rows[row["patent_id"]] = row
    Patent.objects.bulk_create(Patent(dataset=dataset, **row) for row in rows.values())
    logger.info(
        "imported %d patents into dataset %d (%d duplicates, %d rows skipped)",
        len(rows), dataset.pk, len(parsed.rows) - len(rows), parsed.skipped,
    )

    return ImportResult(
        dataset=dataset,
        imported=len(rows),
        duplicates=len(parsed.rows) - len(rows),
        skipped=parsed.skipped,
    )
