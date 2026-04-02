from datetime import datetime, timezone
from unittest import mock

from rest_framework.test import APITestCase

from patents.models import Patent, Topic
from patents.tests.factories import example_dataset, make_dataset


class TopicApiTests(APITestCase):
    def setUp(self):
        self.dataset = example_dataset(
            name="Drones",
            slug="drones",
            description="Unmanned aerial vehicles.",
            keywords="drone",
            pattern=r"\bdrones?\b",
            source_revision="abc123",
            collected_at=datetime(2026, 2, 1, 2, 17, tzinfo=timezone.utc),
        )

    def test_lists_topics_with_their_source(self):
        self.assertEqual(
            self.client.get("/api/topics/").json(),
            [
                {
                    "id": self.dataset.pk,
                    "slug": "drones",
                    "name": "Drones",
                    "description": "Unmanned aerial vehicles.",
                    "keywords": ["drone"],
                    "pattern": r"\bdrones?\b",
                    "source_revision": "abc123",
                    "collected_at": "2026-02-01T02:17:00Z",
                    "patent_count": 3,
                    "status": "ready",
                    "progress": 0,
                    "progress_total": 0,
                    "error": "",
                }
            ],
        )

    def test_detail(self):
        self.assertEqual(self.client.get(f"/api/topics/{self.dataset.pk}/").json()["patent_count"], 3)

    def test_the_old_datasets_address_still_lists_them(self):
        self.assertEqual(self.client.get("/api/datasets/").json()[0]["slug"], "drones")


@mock.patch("patents.jobs.start_worker")
class TopicEditTests(APITestCase):
    def setUp(self):
        self.drones = make_dataset("Drones", [
            {"patent_id": "ZZ-1-B1", "title": "Parcel drone", "abstract": "Delivers parcels to lockers."},
            {"patent_id": "ZZ-2-B1", "title": "Quadcopter frame", "abstract": "A foldable frame."},
        ], slug="drones", keywords="drone,quadcopter")

    def post(self, data):
        return self.client.post("/api/topics/", data, format="json")

    def test_a_new_topic_shows_stored_matches_and_is_queued(self, start_worker):
        with self.captureOnCommitCallbacks(execute=True):
            response = self.post({"name": "Parcel lockers", "keywords": "locker, parcel box"})

        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertEqual((body["slug"], body["keywords"], body["patent_count"]), ("parcel-lockers", ["locker", "parcel box"], 1))
        self.assertEqual(body["status"], "queued")
        start_worker.assert_called_once()

    def test_keywords_are_validated(self, start_worker):
        response = self.post({"name": "Bad", "keywords": "dr.ne"})

        self.assertEqual(response.status_code, 400)
        self.assertIn("letters and digits", response.json()["keywords"][0])
        self.assertEqual(self.post({"name": "drones", "keywords": ["drone"]}).json()["name"],
                         ["A topic with this name exists already."])
        self.assertFalse(Topic.objects.filter(name="Bad").exists())

    def test_the_number_of_topics_is_limited(self, start_worker):
        with self.settings(PATENTS_MAX_TOPICS=1):
            response = self.post({"name": "Lockers", "keywords": ["locker"]})

        self.assertEqual(response.status_code, 400)
        self.assertIn("the most allowed", response.json()["detail"])

    def test_new_keywords_are_matched_and_collected_again(self, start_worker):
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.patch(f"/api/topics/{self.drones.pk}/", {"keywords": ["frame"]}, format="json")

        self.assertEqual((response.json()["keywords"], response.json()["patent_count"]), (["frame"], 1))
        self.assertEqual(response.json()["status"], "queued")
        start_worker.assert_called_once()

    def test_renaming_does_not_collect(self, start_worker):
        response = self.client.patch(f"/api/topics/{self.drones.pk}/", {"name": "UAVs"}, format="json")

        self.assertEqual((response.json()["name"], response.json()["status"]), ("UAVs", "ready"))
        start_worker.assert_not_called()

    def test_deleting_removes_the_patents_no_topic_keeps(self, start_worker):
        self.assertEqual(self.client.delete(f"/api/topics/{self.drones.pk}/").status_code, 204)

        self.assertFalse(Topic.objects.exists())
        self.assertFalse(Patent.objects.exists())

    def test_collect_again(self, start_worker):
        Topic.objects.filter(pk=self.drones.pk).update(status=Topic.FAILED, error="HTTP 503")

        with self.captureOnCommitCallbacks(execute=True):
            body = self.client.post(f"/api/topics/{self.drones.pk}/collect/").json()

        self.assertEqual((body["status"], body["error"]), ("queued", ""))
        start_worker.assert_called_once()

    def test_forms_are_refused(self, start_worker):
        response = self.client.post("/api/topics/", {"name": "Lockers", "keywords": "locker"})

        self.assertEqual(response.status_code, 415)

    def test_edits_can_be_turned_off(self, start_worker):
        self.assertEqual(self.client.get("/api/config/").json(), {"topic_edits": True, "max_topics": 20})
        with self.settings(PATENTS_ALLOW_TOPIC_EDITS=False):
            response = self.post({"name": "Lockers", "keywords": ["locker"]})
            self.assertEqual(self.client.get("/api/topics/").status_code, 200)
            self.assertFalse(self.client.get("/api/config/").json()["topic_edits"])

        self.assertEqual(response.status_code, 403)
        self.assertIn("PATENTS_ALLOW_TOPIC_EDITS", response.json()["detail"])
