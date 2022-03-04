from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from patents.csv_import import CSVFormatError
from patents.importer import import_export


class Command(BaseCommand):
    help = "Import a Google Patents CSV export as a new dataset."

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=Path, help="file saved with 'Download (CSV)' on patents.google.com")
        parser.add_argument("--name", default="", help="dataset name (default: the search query)")

    def handle(self, *args, csv_file, name, **options):
        try:
            text = csv_file.read_text(encoding="utf-8")
        except OSError as exc:
            raise CommandError(f"cannot read {csv_file}: {exc}") from exc
        try:
            result = import_export(text, name=name)
        except CSVFormatError as exc:
            raise CommandError(f"{csv_file} is not a Google Patents export: {exc}") from exc

        self.stdout.write(self.style.SUCCESS(
            f"Imported {result.imported} patents into dataset #{result.dataset.pk} \"{result.dataset.name}\""
            f" ({result.duplicates} duplicates, {result.skipped} rows skipped)"
        ))
