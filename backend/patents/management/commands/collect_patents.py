from django.core.management.base import BaseCommand, CommandError

from patents.collector import collect
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
        parser.add_argument("--workers", type=int, default=2, help="files read in parallel (default 2)")

    def handle(self, *args, topic, shards, workers, **options):
        topics = [get_topic(slug) for slug in topic] if topic else TOPICS
        for dataset in collect(topics, shards=shards, workers=workers):
            self.stdout.write(self.style.SUCCESS(f"{dataset.name}: {dataset.patents.count()} patents"))
