from datetime import date, datetime, timezone

from django.test import TestCase

from patents.models import Topic
from patents.store import store_topic, store_topics
from patents.topics import get_topic


def record(number, **values):
    fields = {
        "patent_id": number,
        "application_number": f"APP-{number}",
        "family_id": "1",
        "title": "Drone delivery of parcels",
        "assignee": "Example Robotics Inc.",
        "inventors": "Jane Doe, John Roe",
        "priority_date": date(2017, 3, 1),
        "filing_date": date(2018, 3, 5),
        "publication_date": date(2019, 1, 3),
        "grant_date": None,
    }
    fields.update(values)
    return fields


class StoreTopicTests(TestCase):
    def test_creates_the_topic_dataset(self):
        when = datetime(2026, 1, 20, tzinfo=timezone.utc)

        dataset = store_topic(get_topic("drones"), [record("US-1-B2"), record("US-2-A1")], "abc123", collected_at=when)

        self.assertEqual((dataset.slug, dataset.name), ("drones", "Drones"))
        self.assertEqual(dataset.source_revision, "abc123")
        self.assertEqual(dataset.collected_at, when)
        self.assertIn("aerial", dataset.pattern)
        self.assertEqual(dataset.patents.count(), 2)

    def test_replaces_the_patents_of_the_topic_only(self):
        store_topic(get_topic("drones"), [record("US-1-B2"), record("US-2-A1")], "abc123")
        store_topic(get_topic("cybersecurity"), [record("US-9-B1")], "abc123")

        store_topic(get_topic("drones"), [record("US-3-A1")], "def456")

        self.assertEqual(Topic.objects.count(), 2)
        drones = Topic.objects.get(slug="drones")
        self.assertEqual(list(drones.patents.values_list("patent_id", flat=True)), ["US-3-A1"])
        self.assertEqual(drones.source_revision, "def456")
        self.assertEqual(Topic.objects.get(slug="cybersecurity").patents.count(), 1)

    def test_keeps_figures_already_looked_up(self):
        store_topic(get_topic("drones"), [record("US-1-B2"), record("US-2-A1")], "abc123")
        Topic.objects.get(slug="drones").patents.filter(patent_id="US-1-B2").update(
            thumbnail_link="https://patentimages.storage.googleapis.com/t.png",
            figure_checked_at=datetime(2026, 1, 21, tzinfo=timezone.utc),
        )

        store_topic(get_topic("drones"), [record("US-1-B2", title="New title"), record("US-3-A1")], "def456")

        kept = Topic.objects.get(slug="drones").patents.get(patent_id="US-1-B2")
        self.assertEqual(kept.title, "New title")
        self.assertEqual(kept.thumbnail_link, "https://patentimages.storage.googleapis.com/t.png")
        self.assertIsNone(Topic.objects.get(slug="drones").patents.get(patent_id="US-3-A1").figure_checked_at)

    def test_stored_topics_keep_their_names_and_deleted_ones_stay_deleted(self):
        mine = Topic.objects.create(name="My lockers", slug="my-lockers", keywords="locker")
        gone = Topic.objects.create(name="Gone", slug="gone")
        Topic.objects.filter(pk=gone.pk).delete()

        stored = store_topics([mine, gone], {"my-lockers": [record("US-5-A1")], "gone": [record("US-6-A1")]}, "rev9")

        self.assertEqual(stored, [mine])
        mine.refresh_from_db()
        self.assertEqual((mine.name, mine.source_revision), ("My lockers", "rev9"))
        self.assertEqual(list(mine.patents.values_list("patent_id", flat=True)), ["US-5-A1"])
        self.assertFalse(Topic.objects.filter(slug="gone").exists())
