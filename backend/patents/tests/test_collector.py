import tempfile
from io import StringIO
from pathlib import Path
from unittest import mock

from django.core.management import CommandError, call_command
from django.test import TestCase

from patents import opendata
from patents.management.commands.collect_patents import parse_shards
from patents.models import Dataset
from patents.tests import opendata_fixture


class CollectTests(TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        source = str(opendata_fixture.write(Path(self.tmp.name) / "publications.parquet"))
        for name, value in (("source_revision", "abc123"), ("shard_urls", [source])):
            patcher = mock.patch.object(opendata, name, return_value=value)
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_command_stores_every_topic(self):
        out = StringIO()
        call_command("collect_patents", stdout=out)

        self.assertEqual(
            {dataset.slug: dataset.patents.count() for dataset in Dataset.objects.all()},
            {"drones": 1, "autonomous-driving": 0, "cybersecurity": 1},
        )
        drone = Dataset.objects.get(slug="drones").patents.get()
        self.assertEqual((drone.patent_id, drone.is_granted), ("US-10000001-B2", True))
        self.assertEqual(Dataset.objects.get(slug="drones").source_revision, "abc123")
        self.assertIn("Drones: 1 patents", out.getvalue())

    def test_command_can_collect_one_topic(self):
        call_command("collect_patents", "--topic", "cybersecurity", stdout=StringIO())

        self.assertEqual(list(Dataset.objects.values_list("slug", flat=True)), ["cybersecurity"])


    def test_if_changed_skips_a_revision_already_collected(self):
        call_command("collect_patents", stdout=StringIO())
        Dataset.objects.filter(slug="drones").update(name="Kept")

        out = StringIO()
        call_command("collect_patents", "--if-changed", stdout=out)

        self.assertIn("Up to date with revision abc123", out.getvalue())
        self.assertEqual(Dataset.objects.get(slug="drones").name, "Kept")

    def test_if_changed_collects_a_new_revision(self):
        call_command("collect_patents", stdout=StringIO())
        Dataset.objects.filter(slug="drones").update(source_revision="older")

        call_command("collect_patents", "--if-changed", stdout=StringIO())

        self.assertEqual(Dataset.objects.get(slug="drones").source_revision, "abc123")


class ShardArgumentTests(TestCase):
    def test_ranges_and_lists(self):
        self.assertEqual(parse_shards("0-3,7"), [0, 1, 2, 3, 7])

    def test_invalid(self):
        with self.assertRaises(CommandError):
            parse_shards("a-b")
