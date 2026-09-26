"""The snapshot of topics and patents that ships with the app.

A full collection reads the whole public dataset and takes a while, so the
repository carries its result: a new instance loads it on its first start
and shows a complete dashboard right away. It is loaded into an empty
database only, so topics deleted from the dashboard do not come back.
"""
import gzip
import json
from collections import defaultdict
from datetime import date
from pathlib import Path

from django.db import transaction
from django.utils.dateparse import parse_datetime

from .models import Patent, Topic

SEED_FILE = Path(__file__).parent / "seed" / "patents.json.gz"
FORMAT = 2
FIELDS = (
    "patent_id", "application_number", "family_id", "title", "abstract", "assignee", "assignee_country", "inventors",
    "priority_date", "filing_date", "publication_date", "grant_date", "result_link",
    "thumbnail_link", "figure_link", "figure_checked_at", "publication_numbers", "cited_by",
)
DATES = ("priority_date", "filing_date", "publication_date", "grant_date")
DATETIMES = ("figure_checked_at",)


def encode(field, value):
    return value.isoformat() if field in DATES + DATETIMES and value else value


def decode(field, value):
    if field in DATES:
        return date.fromisoformat(value)
    if field in DATETIMES:
        return parse_datetime(value)
    return value


def dump(path=SEED_FILE):
    """Write all topics and patents; returns (topics, patents) counted."""
    topics = list(Topic.objects.order_by("slug"))
    slugs = {topic.pk: topic.slug for topic in topics}
    memberships = defaultdict(list)
    for patent, topic in Patent.topics.through.objects.values_list("patent_id", "topic_id"):
        memberships[patent].append(slugs[topic])
    document = {
        "format": FORMAT,
        "topics": [
            {
                "slug": topic.slug,
                "name": topic.name,
                "description": topic.description,
                "keywords": topic.keyword_list,
                "source_revision": topic.source_revision,
                "collected_at": topic.collected_at.isoformat() if topic.collected_at else None,
            }
            for topic in topics
        ],
        # Fields left at their default are omitted, which keeps the file small.
        "patents": [
            {
                **{field: encode(field, getattr(patent, field)) for field in FIELDS
                   if getattr(patent, field) not in ("", None, 0)},
                "topics": sorted(memberships[patent.pk]),
            }
            for patent in Patent.objects.order_by("patent_id")
        ],
    }
    # A fixed name and mtime keep the file identical when the data is.
    with open(path, "wb") as raw, gzip.GzipFile("patents.json", "wb", fileobj=raw, mtime=0) as file:
        file.write(json.dumps(document, ensure_ascii=False, separators=(",", ":")).encode())
    return len(document["topics"]), len(document["patents"])


@transaction.atomic
def load(path=SEED_FILE, force=False):
    """Load the snapshot into an empty database (with `force`, replace what is
    there); returns the topics loaded, or None when nothing was done."""
    if Topic.objects.exists() or Patent.objects.exists():
        if not force:
            return None
        Topic.objects.all().delete()
        Patent.objects.all().delete()
    with gzip.open(path, "rt", encoding="utf-8") as file:
        document = json.load(file)
    if document.get("format") != FORMAT:
        raise ValueError(f"{path} is not a snapshot of format {FORMAT}")

    topics = {}
    for values in document["topics"]:
        topic = Topic(
            slug=values["slug"],
            name=values["name"],
            description=values["description"],
            source_revision=values["source_revision"],
            collected_at=parse_datetime(values["collected_at"]) if values["collected_at"] else None,
        )
        topic.set_keywords(values["keywords"])
        topic.save()
        topics[topic.slug] = topic

    Patent.objects.bulk_create(
        (Patent(**{field: decode(field, value) for field, value in values.items() if field != "topics"})
         for values in document["patents"]),
        batch_size=1000,
    )
    pks = dict(Patent.objects.values_list("patent_id", "pk"))
    Patent.topics.through.objects.bulk_create(
        (Patent.topics.through(patent_id=pks[values["patent_id"]], topic_id=topics[slug].pk)
         for values in document["patents"] for slug in values["topics"]),
        batch_size=2000,
    )
    return list(topics.values())
