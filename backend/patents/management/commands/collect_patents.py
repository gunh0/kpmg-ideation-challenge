from django.core.management.base import BaseCommand, CommandError

from patents import jobs, opendata
from patents.models import Topic
from patents.topics import TOPICS


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
    help = (
        "Collect the stored topics (all, or --topic) from Google Patents Public Data. "
        "An empty database gets the default topics first."
    )

    def add_arguments(self, parser):
        parser.add_argument("--topic", action="append", metavar="SLUG",
                            help="collect only this topic (repeatable; default: all)")
        parser.add_argument("--shards", type=parse_shards,
                            help="only read these Parquet files, e.g. 0-3 (for trying it out: the topics keep only what they contain)")
        parser.add_argument("--if-changed", action="store_true",
                            help="skip topics collected from the current revision of the data")
        parser.add_argument("--workers", type=int, default=1,
                            help="files read in parallel (default 1; each uses the threads the memory allows)")

    def handle(self, *args, topic, shards, workers, if_changed, **options):
        if not Topic.objects.exists():
            for default in TOPICS:
                created = Topic(name=default.name, slug=default.slug, description=default.description)
                created.set_keywords(default.keywords)
                created.save()
        topics = Topic.objects.all()
        if topic:
            topics = topics.filter(slug__in=topic)
            missing = set(topic) - set(topics.values_list("slug", flat=True))
            if missing:
                raise CommandError(f"no such topic: {', '.join(sorted(missing))}")
        revision = opendata.source_revision()
        if if_changed:
            topics = topics.exclude(source_revision=revision)
            if not topics.exists():
                self.stdout.write(f"Up to date with revision {revision[:12]}, nothing to collect.")
                return
        jobs.enqueue(list(topics))
        jobs.process_queue(shards=shards, workers=workers, revision=revision)
        for collected in Topic.objects.filter(pk__in=[t.pk for t in topics]):
            if collected.status == Topic.FAILED:
                self.stderr.write(self.style.ERROR(f"{collected.name}: failed: {collected.error}"))
            else:
                self.stdout.write(self.style.SUCCESS(f"{collected.name}: {collected.patents.count()} patents"))
