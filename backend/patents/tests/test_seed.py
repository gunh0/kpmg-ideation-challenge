import gzip
import json
import tempfile
from datetime import date, datetime, timezone
from io import StringIO
from pathlib import Path

from django.core.management import call_command
from django.test import TestCase

from patents.models import Patent, Topic
from patents.seed import load
from patents.store import store_topics
from patents.tests.test_store import record
from patents.topics import get_topic


class SeedTests(TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.file = Path(self.tmp.name) / "patents.json.gz"
        shared = record(
            "US-1-B2",
            grant_date=date(2020, 6, 2),
            thumbnail_link="https://patentimages.storage.googleapis.com/t.png",
            figure_checked_at=datetime(2026, 1, 21, 9, tzinfo=timezone.utc),
            abstract="A drone that detects intrusions.",
        )
        store_topics(
            [get_topic("drones"), get_topic("cybersecurity")],
            {"drones": [shared, record("US-2-A1", assignee="")], "cybersecurity": [shared]},
            "abc123",
            collected_at=datetime(2026, 1, 20, 12, tzinfo=timezone.utc),
        )
        Patent.objects.filter(patent_id="US-1-B2").update(cited_by=4)

    def dump(self):
        out = StringIO()
        call_command("dump_seed", "--file", self.file, stdout=out)
        return out.getvalue()

    def test_dump_and_load_round_trip(self):
        self.assertIn("2 topics, 2 patents", self.dump())
        Topic.objects.all().delete()
        Patent.objects.all().delete()

        out = StringIO()
        call_command("load_seed", "--file", self.file, stdout=out)

        drones = Topic.objects.get(slug="drones")
        self.assertEqual((drones.source_revision, drones.keyword_list[0]), ("abc123", "drone"))
        self.assertEqual(drones.collected_at, datetime(2026, 1, 20, 12, tzinfo=timezone.utc))
        shared = Patent.objects.get(patent_id="US-1-B2")
        self.assertEqual(sorted(shared.topics.values_list("slug", flat=True)), ["cybersecurity", "drones"])
        self.assertEqual((shared.grant_date, shared.cited_by), (date(2020, 6, 2), 4))
        self.assertEqual(shared.abstract, "A drone that detects intrusions.")
        self.assertEqual(shared.figure_checked_at, datetime(2026, 1, 21, 9, tzinfo=timezone.utc))
        pending = Patent.objects.get(patent_id="US-2-A1")
        self.assertEqual((pending.assignee, pending.grant_date, pending.cited_by), ("", None, 0))
        self.assertIn("Drones: 2 patents from the snapshot", out.getvalue())

    def test_loads_only_into_an_empty_database(self):
        self.dump()
        Topic.objects.filter(slug="drones").delete()  # deleted from the dashboard

        out = StringIO()
        call_command("load_seed", "--file", self.file, stdout=out)
        self.assertIn("nothing loaded", out.getvalue())
        self.assertFalse(Topic.objects.filter(slug="drones").exists())

        self.assertEqual(len(load(self.file, force=True)), 2)
        self.assertTrue(Topic.objects.filter(slug="drones").exists())

    def test_dump_is_reproducible_and_small(self):
        self.dump()
        first = self.file.read_bytes()
        self.dump()

        self.assertEqual(self.file.read_bytes(), first)
        document = json.loads(gzip.decompress(first))
        self.assertNotIn("cited_by", next(p for p in document["patents"] if p["patent_id"] == "US-2-A1"))
