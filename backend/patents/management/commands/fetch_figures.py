from django.core.management.base import BaseCommand

from patents.figures import fill_figures
from patents.models import Dataset


class Command(BaseCommand):
    help = "Look up the figures of each topic's latest patents, which the dashboard shows first."

    def add_arguments(self, parser):
        parser.add_argument("--latest", type=int, default=24, help="patents per topic (default 24)")

    def handle(self, *args, latest, **options):
        for dataset in Dataset.objects.exclude(slug=None):
            patents = list(dataset.patents.order_by("-publication_date", "patent_id")[:latest])
            fill_figures(patents)
            found = sum(1 for patent in patents if patent.thumbnail_link)
            self.stdout.write(f"{dataset.name}: {found} of {len(patents)} latest patents have a figure")
