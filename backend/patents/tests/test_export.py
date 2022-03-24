import csv
import io
from pathlib import Path

from rest_framework.test import APITestCase

from patents.csv_import import parse_export
from patents.importer import import_export

FIXTURE = Path(__file__).parent / "fixtures" / "export.csv"


class ExportTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.dataset = import_export(FIXTURE.read_text()).dataset

    def export(self, query=""):
        response = self.client.get(f"/api/patents/export/?{query}")
        self.assertEqual(response.status_code, 200)
        return b"".join(response.streaming_content).decode()

    def test_download_headers(self):
        response = self.client.get("/api/patents/export/")

        self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8")
        self.assertEqual(response["Content-Disposition"], 'attachment; filename="patents.csv"')

    def test_applies_filters_and_ordering(self):
        rows = list(csv.reader(io.StringIO(self.export("granted=true&ordering=patent_id"))))

        self.assertEqual(rows[0][:2], ["id", "title"])
        self.assertEqual([row[0] for row in rows[1:]], ["ZZ-0000001-B2", "ZZ-0000003-B1"])

    def test_export_can_be_imported_again(self):
        original = parse_export(FIXTURE.read_text()).rows

        again = parse_export(self.export("ordering=patent_id")).rows

        self.assertEqual(sorted(original, key=lambda row: row["patent_id"]), again)
