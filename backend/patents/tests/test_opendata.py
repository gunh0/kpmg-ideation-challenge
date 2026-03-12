import tempfile
from pathlib import Path
from unittest import mock

from django.test import SimpleTestCase

from patents import opendata
from patents.tests import opendata_fixture
from patents.topics import TOPICS, get_topic


class ReadTopicsTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tmp = tempfile.TemporaryDirectory()
        cls.source = opendata_fixture.write(Path(cls.tmp.name) / "publications.parquet")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()
        super().tearDownClass()

    def test_keeps_recent_us_publications_matching_a_topic_in_title_or_abstract(self):
        rows = opendata.read_topics(self.source, TOPICS, since=20150101)

        self.assertEqual(
            sorted((row["publication_number"], row["topics"]) for row in rows),
            [
                ("US-10000001-B2", ["drones"]),
                ("US-2019000001-A1", ["drones"]),
                ("US-2021000002-A1", ["autonomous-driving", "cybersecurity"]),
                ("US-2022000006-A1", ["drones"]),
            ],
        )

    def test_patterns_are_parameters_not_sql(self):
        sql, parameters = opendata.topic_query("x.parquet", TOPICS, since=20150101)

        self.assertNotIn("drone", sql)
        self.assertIn(get_topic("drones").pattern, parameters)
        self.assertEqual(parameters[-1], 20150101)

    def test_returns_the_columns_the_store_needs(self):
        row = next(
            row for row in opendata.read_topics(self.source, TOPICS, since=20150101)
            if row["publication_number"] == "US-10000001-B2"
        )

        self.assertEqual(row["title"], "Drone delivery of parcels to balconies")
        self.assertEqual(row["application_number"], "US-201816000001-A")
        self.assertEqual((row["filing_date"], row["grant_date"]), (20180305, 20200602))
        self.assertEqual(row["inventor"], ["DOE, JANE", "ROE, JOHN"])
        self.assertEqual(row["abstract"], "A drone lowers parcels onto balconies.")
        self.assertEqual(row["assignee_country"], "US")


class SourceTests(SimpleTestCase):
    def test_shards_are_pinned_to_the_revision(self):
        tree = [
            {"type": "file", "path": ".gitattributes"},
            {"type": "file", "path": "patents-publications-000000000001.parquet"},
            {"type": "file", "path": "patents-publications-000000000000.parquet"},
        ]
        with mock.patch.object(opendata, "get_json", return_value=tree) as get_json:
            urls = opendata.shard_urls("abc123")

        get_json.assert_called_once_with(f"{opendata.API}/tree/abc123")
        self.assertEqual(
            urls,
            [
                f"{opendata.FILES}/abc123/patents-publications-000000000000.parquet",
                f"{opendata.FILES}/abc123/patents-publications-000000000001.parquet",
            ],
        )

    def test_revision_is_the_repository_commit(self):
        with mock.patch.object(opendata, "get_json", return_value={"sha": "abc123", "id": opendata.REPOSITORY}):
            self.assertEqual(opendata.source_revision(), "abc123")
