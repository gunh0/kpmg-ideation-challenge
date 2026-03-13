"""Snapshots of the collected topics that ship with the app.

A full collection reads the whole public dataset and takes a while, so the
repository carries its result: a fresh instance loads the snapshot on its
first start and shows a complete dashboard right away.
"""
import gzip
import json
from datetime import date
from pathlib import Path

from django.utils.dateparse import parse_datetime

from .models import Dataset
from .store import store_topic
from .topics import TOPICS

SEED_DIR = Path(__file__).parent / "seed"
FIELDS = (
    "patent_id", "application_number", "family_id", "title", "abstract", "assignee", "assignee_country", "inventors",
    "priority_date", "filing_date", "publication_date", "grant_date", "result_link",
    "thumbnail_link", "figure_link", "figure_checked_at", "publication_numbers", "cited_by",
)
DATES = ("priority_date", "filing_date", "publication_date", "grant_date")
DATETIMES = ("figure_checked_at",)


def seed_path(topic, directory=SEED_DIR):
    return Path(directory) / f"{topic.slug}.json.gz"


def dump(dataset, path):
    def value(patent, field):
        value = getattr(patent, field)
        return value.isoformat() if field in DATES + DATETIMES and value else value

    # Fields left at their default are omitted, which keeps the files small.
    patents = [
        {field: value(patent, field) for field in FIELDS if getattr(patent, field) not in ("", None)}
        for patent in dataset.patents.order_by("patent_id")
    ]
    document = {
        "topic": dataset.slug,
        "source_revision": dataset.source_revision,
        "collected_at": dataset.collected_at.isoformat() if dataset.collected_at else None,
        "patents": patents,
    }
    # mtime=0 keeps the file identical when the data is.
    with gzip.GzipFile(path, "wb", mtime=0) as file:
        file.write(json.dumps(document, ensure_ascii=False, separators=(",", ":")).encode())
    return len(patents)


def load(topic, path, force=False):
    """Store the snapshot of `topic`; returns the dataset, or None when the
    topic already has data and `force` is off."""
    if not force and Dataset.objects.filter(slug=topic.slug).exists():
        return None
    with gzip.open(path, "rt", encoding="utf-8") as file:
        document = json.load(file)
    def parse(field, value):
        if field in DATES:
            return date.fromisoformat(value)
        if field in DATETIMES:
            return parse_datetime(value)
        return value

    records = [{field: parse(field, value) for field, value in patent.items()} for patent in document["patents"]]
    collected_at = parse_datetime(document["collected_at"]) if document["collected_at"] else None
    return store_topic(topic, records, document["source_revision"], collected_at=collected_at)


def load_all(directory=SEED_DIR, force=False):
    return [dataset for topic in TOPICS if seed_path(topic, directory).exists()
            for dataset in [load(topic, seed_path(topic, directory), force)] if dataset]
