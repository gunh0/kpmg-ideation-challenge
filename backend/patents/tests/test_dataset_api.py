from datetime import datetime, timezone

from rest_framework.test import APITestCase

from patents.tests.factories import example_dataset


class DatasetApiTests(APITestCase):
    def setUp(self):
        self.dataset = example_dataset(
            name="Drones",
            slug="drones",
            description="Unmanned aerial vehicles.",
            pattern=r"\bdrones?\b",
            source_revision="abc123",
            collected_at=datetime(2026, 2, 1, 2, 17, tzinfo=timezone.utc),
        )

    def test_lists_topics_with_their_source(self):
        self.assertEqual(
            self.client.get("/api/datasets/").json(),
            [
                {
                    "id": self.dataset.pk,
                    "slug": "drones",
                    "name": "Drones",
                    "description": "Unmanned aerial vehicles.",
                    "pattern": r"\bdrones?\b",
                    "source_revision": "abc123",
                    "collected_at": "2026-02-01T02:17:00Z",
                    "patent_count": 3,
                }
            ],
        )

    def test_detail(self):
        self.assertEqual(self.client.get(f"/api/datasets/{self.dataset.pk}/").json()["patent_count"], 3)

    def test_topics_cannot_be_changed_through_the_api(self):
        url = f"/api/datasets/{self.dataset.pk}/"
        self.assertEqual(self.client.post("/api/datasets/", {}).status_code, 405)
        self.assertEqual(self.client.patch(url, {"name": "x"}, format="json").status_code, 405)
        self.assertEqual(self.client.delete(url).status_code, 405)
