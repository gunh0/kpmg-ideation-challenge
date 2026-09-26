import os
import time

from django.core.management.base import BaseCommand
from django.utils import timezone

from patents import jobs, opendata
from patents.models import Topic


class Command(BaseCommand):
    help = (
        "Keep collecting: topics queued from the dashboard right away, and all topics again when the "
        "public data has a new revision (checked every PATENTS_COLLECT_INTERVAL seconds, default a day)."
    )

    def add_arguments(self, parser):
        parser.add_argument("--poll", type=int, default=30, help="seconds between looks at the queue")
        parser.add_argument("--once", action="store_true", help="one round, then exit")

    def handle(self, *args, poll, once, **options):
        interval = int(os.environ.get("PATENTS_COLLECT_INTERVAL", 86400))
        checked = None
        while True:
            if checked is None or (timezone.now() - checked).total_seconds() >= interval:
                self.queue_new_revision()
                checked = timezone.now()
            jobs.process_queue()
            if once:
                return
            time.sleep(poll)

    def queue_new_revision(self):
        try:
            revision = opendata.source_revision()
        except OSError as error:
            self.stderr.write(f"Could not check the public data: {error}")
            return
        stale = list(Topic.objects.exclude(source_revision=revision).exclude(status__in=[Topic.QUEUED, Topic.COLLECTING]))
        if stale:
            self.stdout.write(f"Revision {revision[:12]}: collecting {', '.join(t.name for t in stale)}")
            jobs.enqueue(stale)
