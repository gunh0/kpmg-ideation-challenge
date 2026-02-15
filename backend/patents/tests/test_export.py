import csv
import io

from django.utils import timezone
from rest_framework.test import APITestCase

from patents.tests.factories import example_dataset, make_dataset


class ExportTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.dataset = example_dataset()

    def export(self, query=""):
        response = self.client.get(f"/api/patents/export/?{query}")
        self.assertEqual(response.status_code, 200)
        return b"".join(response.streaming_content).decode()

    def test_download_headers(self):
        response = self.client.get("/api/patents/export/")

        self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8")
        today = timezone.localdate().isoformat()
        self.assertEqual(response["Content-Disposition"], f'attachment; filename="patents-{today}.csv"')

    def test_file_is_named_after_the_dataset(self):
        response = self.client.get(f"/api/patents/export/?dataset={self.dataset.pk}")

        today = timezone.localdate().isoformat()
        self.assertEqual(response["Content-Disposition"], f'attachment; filename="patents-drone-delivery-{today}.csv"')

    def test_applies_filters_and_ordering(self):
        rows = list(csv.reader(io.StringIO(self.export("granted=true&ordering=patent_id"))))

        self.assertEqual(rows[0][:2], ["id", "title"])
        self.assertEqual([row[0] for row in rows[1:]], ["ZZ-0000001-B2", "ZZ-0000003-B1"])

    def test_rows_hold_every_column(self):
        rows = list(csv.reader(io.StringIO(self.export("ordering=patent_id"))))

        self.assertEqual(
            rows[1],
            [
                "ZZ-0000001-B2",
                "Parcel release mechanism for an unmanned aerial vehicle",
                "Example Robotics Inc.",
                "Jane Doe, John Roe",
                "2016-03-14",
                "2017-03-10",
                "2019-08-20",
                "2019-08-20",
                "https://patents.google.com/patent/ZZ0000001B2/en",
                "https://patentimages.storage.googleapis.com/example/ZZ0000001B2.png",
            ],
        )

    def test_formula_like_values_are_neutralised(self):
        make_dataset("Hostile", [{"patent_id": "ZZ-7-A1", "title": '=HYPERLINK("http://x")', "assignee": "@Evil Corp"}])

        row = list(csv.reader(io.StringIO(self.export("search=ZZ-7"))))[1]

        self.assertEqual(row[1], "'=HYPERLINK(\"http://x\")")
        self.assertEqual(row[2], "'@Evil Corp")
