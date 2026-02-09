import tempfile
from datetime import date, datetime, timezone
from io import StringIO
from pathlib import Path

from django.core.management import call_command
from django.test import TestCase

from patents.models import Dataset, Patent
from patents.store import store_topic
from patents.tests.test_store import record
from patents.topics import get_topic


class SeedTests(TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)
        store_topic(
            get_topic("drones"),
            [
                record(
                    "US-1-B2",
                    grant_date=date(2020, 6, 2),
                    thumbnail_link="https://patentimages.storage.googleapis.com/t.png",
                    figure_checked_at=datetime(2026, 1, 21, 9, tzinfo=timezone.utc),
                ),
                record("US-2-A1", assignee=""),
            ],
            "abc123",
            collected_at=datetime(2026, 1, 20, 12, tzinfo=timezone.utc),
        )

    def test_dump_and_load_round_trip(self):
        call_command("dump_seed", "--dir", self.dir, stdout=StringIO(), stderr=StringIO())
        Dataset.objects.all().delete()

        out = StringIO()
        call_command("load_seed", "--dir", self.dir, stdout=out)

        dataset = Dataset.objects.get(slug="drones")
        self.assertEqual(dataset.source_revision, "abc123")
        self.assertEqual(dataset.collected_at, datetime(2026, 1, 20, 12, tzinfo=timezone.utc))
        granted = Patent.objects.get(patent_id="US-1-B2")
        self.assertEqual(granted.grant_date, date(2020, 6, 2))
        self.assertEqual(granted.inventor_list, ["Jane Doe", "John Roe"])
        self.assertEqual(granted.thumbnail_link, "https://patentimages.storage.googleapis.com/t.png")
        self.assertEqual(granted.figure_checked_at, datetime(2026, 1, 21, 9, tzinfo=timezone.utc))
        pending = Patent.objects.get(patent_id="US-2-A1")
        self.assertEqual((pending.assignee, pending.grant_date, pending.figure_checked_at), ("", None, None))
        self.assertIn("Drones: 2 patents from the snapshot", out.getvalue())

    def test_load_keeps_topics_that_have_data(self):
        call_command("dump_seed", "--dir", self.dir, stdout=StringIO(), stderr=StringIO())
        Patent.objects.filter(patent_id="US-2-A1").delete()

        out = StringIO()
        call_command("load_seed", "--dir", self.dir, stdout=out)
        self.assertIn("Nothing to load.", out.getvalue())
        self.assertEqual(Patent.objects.count(), 1)

        call_command("load_seed", "--dir", self.dir, "--force", stdout=StringIO())
        self.assertEqual(Patent.objects.count(), 2)

    def test_dump_is_reproducible(self):
        call_command("dump_seed", "--dir", self.dir, stdout=StringIO(), stderr=StringIO())
        first = (self.dir / "drones.json.gz").read_bytes()
        call_command("dump_seed", "--dir", self.dir, stdout=StringIO(), stderr=StringIO())

        self.assertEqual((self.dir / "drones.json.gz").read_bytes(), first)
