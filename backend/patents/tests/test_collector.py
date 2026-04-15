import tempfile
from io import StringIO
from pathlib import Path
from unittest import mock

from django.core.management import CommandError, call_command
from django.test import TestCase

from patents import opendata
from patents.management.commands.collect_patents import parse_shards
from patents.models import Patent, Topic
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
            {dataset.slug: dataset.patents.count() for dataset in Topic.objects.all()},
            {"drones": 2, "autonomous-driving": 1, "cybersecurity": 1},
        )
        drone = Topic.objects.get(slug="drones").patents.get(application_number="US-201816000001-A")
        self.assertEqual((drone.patent_id, drone.is_granted), ("US-10000001-B2", True))
        self.assertEqual(Topic.objects.get(slug="drones").source_revision, "abc123")
        self.assertIn("Drones: 2 patents", out.getvalue())

    def test_counts_the_applications_citing_each_patent(self):
        call_command("collect_patents", stdout=StringIO())

        cited = dict(Patent.objects.values_list("patent_id", "cited_by"))
        # cited by the coffee machine (via its A1) and by the parcel locker (via its B2)
        self.assertEqual(cited["US-10000001-B2"], 2)
        self.assertEqual(cited["US-2021000002-A1"], 1)
        self.assertEqual(cited["US-2022000006-A1"], 0)

    def test_command_can_collect_one_topic(self):
        call_command("collect_patents", "--topic", "cybersecurity", stdout=StringIO())

        collected = {topic.slug: topic.patents.count() for topic in Topic.objects.all()}
        self.assertEqual(collected, {"drones": 0, "autonomous-driving": 0, "cybersecurity": 1})
        self.assertEqual(Topic.objects.get(slug="drones").source_revision, "")

    def test_command_collects_topics_added_from_the_dashboard(self):
        call_command("collect_patents", "--topic", "drones", stdout=StringIO())
        lockers = Topic(name="Lockers", slug="lockers")
        lockers.set_keywords(["locker"])
        lockers.save()

        call_command("collect_patents", "--topic", "lockers", stdout=StringIO())

        self.assertEqual(list(lockers.patents.values_list("patent_id", flat=True)), ["US-2022000006-A1"])
        self.assertEqual(Topic.objects.get(slug="lockers").status, Topic.READY)

    def test_unknown_topic(self):
        with self.assertRaises(CommandError):
            call_command("collect_patents", "--topic", "nope", stdout=StringIO())

    def test_run_collector_collects_topics_of_an_older_revision(self):
        call_command("collect_patents", stdout=StringIO())
        Topic.objects.filter(slug="drones").update(source_revision="older")

        out = StringIO()
        call_command("run_collector", "--once", stdout=out)

        self.assertIn("Revision abc123: collecting Drones", out.getvalue())
        self.assertEqual(Topic.objects.get(slug="drones").source_revision, "abc123")

    def test_if_changed_skips_a_revision_already_collected(self):
        call_command("collect_patents", stdout=StringIO())
        Topic.objects.filter(slug="drones").update(name="Kept")

        out = StringIO()
        call_command("collect_patents", "--if-changed", stdout=out)

        self.assertIn("Up to date with revision abc123", out.getvalue())
        self.assertEqual(Topic.objects.get(slug="drones").name, "Kept")

    def test_if_changed_collects_a_new_revision(self):
        call_command("collect_patents", stdout=StringIO())
        Topic.objects.filter(slug="drones").update(source_revision="older")

        call_command("collect_patents", "--if-changed", stdout=StringIO())

        self.assertEqual(Topic.objects.get(slug="drones").source_revision, "abc123")


class ShardArgumentTests(TestCase):
    def test_ranges_and_lists(self):
        self.assertEqual(parse_shards("0-3,7"), [0, 1, 2, 3, 7])

    def test_invalid(self):
        with self.assertRaises(CommandError):
            parse_shards("a-b")


class ConnectionTests(TestCase):
    def test_stalled_reads_time_out_after_minutes(self):
        from patents.collector import connect

        connection = connect()
        timeout = connection.execute("SELECT current_setting('http_timeout')").fetchone()[0]

        self.assertEqual(int(timeout), 120)  # seconds


class ScanThreadsTests(TestCase):
    def test_threads_follow_the_memory(self):
        from patents.collector import scan_threads

        self.assertEqual(scan_threads(1 * 2**30), 8)
        self.assertEqual(scan_threads(6 * 2**30), 24)
        self.assertEqual(scan_threads(64 * 2**30), 64)
