from pathlib import Path

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework.test import APITestCase

from patents.importer import import_export

FIXTURE = Path(__file__).parent / "fixtures" / "export.csv"


class ReadOnlyTests(APITestCase):
    def setUp(self):
        self.dataset = import_export(FIXTURE.read_text()).dataset

    def test_config_reports_the_mode(self):
        self.assertEqual(self.client.get("/api/config/").json(), {"read_only": False})
        with override_settings(PATENTS_READ_ONLY=True):
            self.assertEqual(self.client.get("/api/config/").json(), {"read_only": True})

    @override_settings(PATENTS_READ_ONLY=True)
    def test_uploads_and_deletions_are_refused(self):
        upload = SimpleUploadedFile("export.csv", FIXTURE.read_bytes(), content_type="text/csv")

        created = self.client.post("/api/datasets/", {"file": upload}, format="multipart")
        deleted = self.client.delete(f"/api/datasets/{self.dataset.pk}/")

        self.assertEqual(created.status_code, 403)
        self.assertIn("read-only", created.json()["detail"])
        self.assertEqual(deleted.status_code, 403)

    @override_settings(PATENTS_READ_ONLY=True)
    def test_reading_still_works(self):
        self.assertEqual(self.client.get("/api/datasets/").status_code, 200)
        self.assertEqual(self.client.get("/api/patents/").json()["count"], 3)
        self.assertEqual(self.client.get("/api/patents/export/").status_code, 200)
