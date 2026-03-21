from django.core.management.base import BaseCommand, CommandError

from patents import opendata
from patents.collector import collect, up_to_date
from patents.topics import TOPICS, get_topic


def parse_shards(value):
    """"0-3,7" -> [0, 1, 2, 3, 7]"""
    shards = []
    for part in value.split(","):
        start, _, end = part.partition("-")
        try:
            shards.extend(range(int(start), int(end or start) + 1))
        except ValueError:
            raise CommandError(f"invalid --shards value: {value!r}")
    return shards


class Command(BaseCommand):
    help = "Collect the topics' US patents from Google Patents Public Data and store them."

    def add_arguments(self, parser):
        parser.add_argument("--topic", action="append", choices=[t.slug for t in TOPICS],
                            help="collect only this topic (repeatable; default: all)")
        parser.add_argument("--shards", type=parse_shards,
                            help="only read these Parquet files, e.g. 0-3 (for trying it out: the topics keep only what they contain)")
        parser.add_argument("--if-changed", action="store_true",
                            help="do nothing when the topics were collected from the current revision of the data")
        parser.add_argument("--workers", type=int, default=1,
                            help="files read in parallel (default 1; each uses the threads the memory allows)")

    def handle(self, *args, topic, shards, workers, if_changed, **options):
        topics = [get_topic(slug) for slug in topic] if topic else TOPICS
        revision = opendata.source_revision()
        if if_changed and up_to_date(topics, revision):
            self.stdout.write(f"Up to date with revision {revision[:12]}, nothing to collect.")
            return
        for dataset in collect(topics, shards=shards, workers=workers, revision=revision):
            self.stdout.write(self.style.SUCCESS(f"{dataset.name}: {dataset.patents.count()} patents"))
