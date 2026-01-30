from pathlib import Path

from django.core.management.base import BaseCommand

from patents.seed import SEED_DIR, load_all


class Command(BaseCommand):
    help = "Load the bundled snapshot for topics that have no data yet (--force: replace them)."

    def add_arguments(self, parser):
        parser.add_argument("--dir", type=Path, default=SEED_DIR)
        parser.add_argument("--force", action="store_true")

    def handle(self, *args, dir, force, **options):
        loaded = load_all(dir, force=force)
        for dataset in loaded:
            self.stdout.write(f"{dataset.name}: {dataset.patents.count()} patents from the snapshot")
        if not loaded:
            self.stdout.write("Nothing to load.")
