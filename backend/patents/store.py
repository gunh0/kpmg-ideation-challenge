"""Save collected topics.

A patent is stored once and linked to every topic it matches. Collecting a
topic replaces its links; patents are created or updated in place, so the
figures looked up for them stay, and patents no topic links to any more are
deleted.
"""
import logging

from django.db import transaction
from django.utils import timezone

from .models import Patent, Topic

logger = logging.getLogger(__name__)

# Fields a collection writes; the figure fields belong to the lookups.
COLLECTED = (
    "application_number", "family_id", "title", "abstract", "assignee", "assignee_country", "inventors",
    "priority_date", "filing_date", "publication_date", "grant_date", "result_link", "publication_numbers",
)


def upsert_patents(records):
    """Create or update the patents of `records`; returns {patent_id: pk}."""
    by_number = {record["patent_id"]: record for record in records}
    # Read all rather than filter by tens of thousands of numbers, which is
    # more than SQLite takes as parameters of one query.
    existing = {patent.patent_id: patent for patent in Patent.objects.iterator() if patent.patent_id in by_number}
    changed = []
    for number, patent in existing.items():
        record = by_number[number]
        for field in COLLECTED:
            if field in record:
                setattr(patent, field, record[field])
        changed.append(patent)
    Patent.objects.bulk_update(changed, [field for field in COLLECTED], batch_size=500)
    Patent.objects.bulk_create(
        (Patent(**record) for number, record in by_number.items() if number not in existing), batch_size=1000
    )
    return {number: pk for number, pk in Patent.objects.values_list("patent_id", "pk") if number in by_number}


def link(topic, patent_ids):
    """Make `patent_ids` (pks) the patents of `topic`."""
    Membership = Patent.topics.through
    Membership.objects.filter(topic=topic).delete()
    Membership.objects.bulk_create(
        (Membership(topic_id=topic.pk, patent_id=pk) for pk in patent_ids), batch_size=1000
    )


def delete_orphans():
    return Patent.objects.filter(topics=None).delete()[0]


@transaction.atomic
def store_topics(topics, records_by_topic, revision, collected_at=None):
    """Replace the patents of each of `topics` with its records
    ({slug: [record, ...]}, as from records.merge). Returns the topics."""
    records = {record["patent_id"]: record for slug in records_by_topic for record in records_by_topic[slug]}
    pks = upsert_patents(list(records.values()))
    stored = []
    for topic in topics:
        if isinstance(topic, Topic):
            # A stored topic keeps its name and keywords, which may have been
            # edited meanwhile; one deleted during its collection stays deleted.
            if not Topic.objects.filter(pk=topic.pk).update(source_revision=revision,
                                                             collected_at=collected_at or timezone.now()):
                continue
            link(topic, {pks[record["patent_id"]] for record in records_by_topic.get(topic.slug, [])})
            stored.append(topic)
            continue
        stored_topic, _ = Topic.objects.update_or_create(
            slug=topic.slug,
            defaults={
                "name": topic.name,
                "description": topic.description,
                "keywords": ",".join(topic.keywords) if isinstance(topic.keywords, (list, tuple)) else topic.keywords,
                "pattern": topic.pattern,
                "source_revision": revision,
                "collected_at": collected_at or timezone.now(),
            },
        )
        link(stored_topic, {pks[record["patent_id"]] for record in records_by_topic.get(topic.slug, [])})
        logger.info("stored %d patents for topic %s (source %s)",
                    len(records_by_topic.get(topic.slug, [])), topic.slug, revision[:12])
        stored.append(stored_topic)
    delete_orphans()
    return stored


def store_topic(topic, records, revision, collected_at=None):
    return store_topics([topic], {topic.slug: records}, revision, collected_at)[0]
