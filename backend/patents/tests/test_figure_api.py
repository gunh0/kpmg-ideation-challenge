from unittest import mock

from rest_framework.test import APITestCase

from patents import figures
from patents.models import Patent
from patents.store import store_topic
from patents.tests.test_store import record
from patents.topics import get_topic

THUMB = "https://patentimages.storage.googleapis.com/aa/US1-D00000.png"
FULL = "https://patentimages.storage.googleapis.com/bb/US1-D00000.png"


class FigureApiTests(APITestCase):
    def setUp(self):
        store_topic(get_topic("drones"), [record("US-1-B2"), record("US-2-A1")], "abc123")
        self.first, self.second = Patent.objects.order_by("patent_id")

    def test_looks_up_unchecked_figures_once(self):
        with mock.patch.object(figures, "fetch_figure", return_value=(THUMB, FULL)) as fetch:
            response = self.client.get(f"/api/figures/?ids={self.second.pk},{self.first.pk}")
            self.client.get(f"/api/figures/?ids={self.second.pk},{self.first.pk}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            [
                {"id": self.second.pk, "thumbnail": THUMB, "figure": FULL, "checked": True},
                {"id": self.first.pk, "thumbnail": THUMB, "figure": FULL, "checked": True},
            ],
        )
        self.assertEqual(fetch.call_count, 2)

    def test_patent_list_includes_known_thumbnails(self):
        Patent.objects.filter(pk=self.first.pk).update(thumbnail_link=THUMB)

        results = self.client.get("/api/patents/?ordering=patent_id").json()["results"]

        self.assertEqual(results[0]["thumbnail_link"], THUMB)

    def test_ids_are_required(self):
        self.assertEqual(self.client.get("/api/figures/?ids=x").status_code, 400)
