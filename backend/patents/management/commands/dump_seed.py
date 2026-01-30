from pathlib import Path

from django.core.management.base import BaseCommand

from patents.models import Dataset
from patents.seed import SEED_DIR, dump, seed_path
from patents.topics import TOPICS


class Command(BaseCommand):
    help = "Write the collected topics to patents/seed/ as the snapshot new instances start from."

    def add_arguments(self, parser):
        parser.add_argument("--dir", type=Path, default=SEED_DIR)

    def handle(self, *args, dir, **options):
        dir.mkdir(parents=True, exist_ok=True)
        for topic in TOPICS:
            dataset = Dataset.objects.filter(slug=topic.slug).first()
            if dataset is None:
                self.stderr.write(f"{topic.slug}: not collected, skipped")
                continue
            count = dump(dataset, seed_path(topic, dir))
            self.stdout.write(self.style.SUCCESS(f"{topic.slug}: {count} patents"))
