"""Save collected topics: each topic is one dataset, replaced as a whole."""
import logging

from django.db import transaction
from django.utils import timezone

from .models import Dataset, Patent

logger = logging.getLogger(__name__)


@transaction.atomic
def store_topic(topic, records, revision, collected_at=None):
    """Replace the patents of `topic` with `records` (dicts of Patent fields).

    Readers see either the old or the new list, never a half-written one.
    """
    dataset, _ = Dataset.objects.update_or_create(
        slug=topic.slug,
        defaults={
            "name": topic.name,
            "description": topic.description,
            "pattern": topic.pattern,
            "source_revision": revision,
            "collected_at": collected_at or timezone.now(),
        },
    )
    # Figures were looked up one by one on Google Patents; keep them.
    figures = {
        patent_id: {"thumbnail_link": thumbnail, "figure_link": figure, "figure_checked_at": checked}
        for patent_id, thumbnail, figure, checked in dataset.patents.exclude(figure_checked_at=None).values_list(
            "patent_id", "thumbnail_link", "figure_link", "figure_checked_at"
        )
    }
    dataset.patents.all().delete()
    Patent.objects.bulk_create(
        (Patent(dataset=dataset, **{**figures.get(record["patent_id"], {}), **record}) for record in records),
        batch_size=1000,
    )
    logger.info("stored %d patents for topic %s (source %s)", len(records), topic.slug, revision[:12])
    return dataset
