from django.core.management.base import BaseCommand

from patents.figures import fill_figures
from patents.models import Topic

BATCH = 24


class Command(BaseCommand):
    help = "Find figures for each topic's latest patents, which the dashboard shows first."

    def add_arguments(self, parser):
        parser.add_argument("--latest", type=int, default=12, help="patents with a figure per topic (default 12)")
        parser.add_argument("--max-lookups", type=int, default=240,
                            help="give up on a topic after looking up this many patents (default 240)")

    def handle(self, *args, latest, max_lookups, **options):
        for dataset in Topic.objects.exclude(slug=None):
            # The newest publications often have no image yet, so walk back
            # from the latest until enough figures are found.
            patents = dataset.patents.order_by("-publication_date", "patent_id")
            looked_up = 0
            while looked_up < max_lookups and patents.exclude(thumbnail_link="").count() < latest:
                batch = list(patents.filter(figure_checked_at=None)[:BATCH])
                if not batch:
                    break
                fill_figures(batch)
                looked_up += len(batch)
            found = patents.exclude(thumbnail_link="").count()
            self.stdout.write(f"{dataset.name}: {found} patents with a figure ({looked_up} looked up)")
