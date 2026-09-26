from pathlib import Path

from django.core.management.base import BaseCommand

from patents.seed import SEED_FILE, load


class Command(BaseCommand):
    help = "Load the bundled snapshot into an empty database (--force: replace all topics and patents)."

    def add_arguments(self, parser):
        parser.add_argument("--file", type=Path, default=SEED_FILE)
        parser.add_argument("--force", action="store_true")

    def handle(self, *args, file, force, **options):
        topics = load(file, force=force)
        if topics is None:
            self.stdout.write("The database has topics already, nothing loaded.")
            return
        for topic in topics:
            self.stdout.write(f"{topic.name}: {topic.patents.count()} patents from the snapshot")
