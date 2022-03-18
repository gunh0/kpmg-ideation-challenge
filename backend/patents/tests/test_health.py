from unittest import mock

from django.db import OperationalError
from django.test import TestCase


class HealthTests(TestCase):
    def test_ok(self):
        response = self.client.get("/api/health/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_database_failure(self):
        with mock.patch("patents.health.connection.cursor", side_effect=OperationalError):
            response = self.client.get("/api/health/")

        self.assertEqual(response.status_code, 503)
