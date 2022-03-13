from pathlib import Path
from unittest import mock

from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase

from patents.importer import import_export
from patents.models import Dataset, Patent
from patents.serializers import DatasetUploadSerializer

FIXTURE = Path(__file__).parent / "fixtures" / "export.csv"


def upload(content, name="export.csv"):
    return SimpleUploadedFile(name, content, content_type="text/csv")


class DatasetApiTests(APITestCase):
    def test_upload_creates_a_dataset_and_reports_the_import(self):
        response = self.client.post("/api/datasets/", {"file": upload(FIXTURE.read_bytes())}, format="multipart")

        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertEqual(body["name"], "(drone delivery)")
        self.assertEqual(body["patent_count"], 3)
        self.assertEqual(body["import"], {"imported": 3, "duplicates": 0, "skipped": 1})

    def test_upload_accepts_a_name_and_a_byte_order_mark(self):
        content = "﻿id,title\nZZ-1-A1,Excel adds a BOM\n".encode("utf-8")

        response = self.client.post("/api/datasets/", {"file": upload(content), "name": "Mine"}, format="multipart")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["name"], "Mine")

    def test_upload_rejects_other_csv_files(self):
        response = self.client.post("/api/datasets/", {"file": upload(b"a,b\n1,2\n")}, format="multipart")

        self.assertEqual(response.status_code, 400)
        self.assertIn("Not a Google Patents export", response.json()["file"][0])
        self.assertFalse(Dataset.objects.exists())

    def test_upload_rejects_non_utf8_and_missing_files(self):
        response = self.client.post("/api/datasets/", {"file": upload(b"\xff\xfe\x00")}, format="multipart")
        self.assertEqual(response.json()["file"], ["The file is not UTF-8 text."])

        response = self.client.post("/api/datasets/", {}, format="multipart")
        self.assertEqual(response.status_code, 400)

    def test_upload_rejects_large_files(self):
        with mock.patch.object(DatasetUploadSerializer, "MAX_SIZE", 10):
            response = self.client.post("/api/datasets/", {"file": upload(FIXTURE.read_bytes())}, format="multipart")

        self.assertEqual(response.json()["file"], ["The file is larger than 10 MB."])

    def test_list_and_detail_count_patents(self):
        dataset = import_export(FIXTURE.read_text()).dataset

        self.assertEqual(self.client.get("/api/datasets/").json()[0]["patent_count"], 3)
        self.assertEqual(self.client.get(f"/api/datasets/{dataset.pk}/").json()["name"], "(drone delivery)")

    def test_delete_removes_the_patents(self):
        dataset = import_export(FIXTURE.read_text()).dataset

        self.assertEqual(self.client.delete(f"/api/datasets/{dataset.pk}/").status_code, 204)
        self.assertFalse(Patent.objects.exists())

    def test_datasets_cannot_be_edited(self):
        dataset = import_export(FIXTURE.read_text()).dataset

        self.assertEqual(self.client.patch(f"/api/datasets/{dataset.pk}/", {"name": "x"}).status_code, 405)
