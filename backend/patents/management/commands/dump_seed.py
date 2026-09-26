from pathlib import Path

from django.core.management.base import BaseCommand

from patents.seed import SEED_FILE, dump


class Command(BaseCommand):
    help = "Write all topics and patents to patents/seed/patents.json.gz, the snapshot new instances start from."

    def add_arguments(self, parser):
        parser.add_argument("--file", type=Path, default=SEED_FILE)

    def handle(self, *args, file, **options):
        file.parent.mkdir(parents=True, exist_ok=True)
        topics, patents = dump(file)
        self.stdout.write(self.style.SUCCESS(f"{topics} topics, {patents} patents written to {file}"))
