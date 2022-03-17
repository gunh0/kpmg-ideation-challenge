from django.test import TestCase


class CorsTests(TestCase):
    def test_frontend_dev_server_is_allowed(self):
        response = self.client.get("/api/stats/", HTTP_ORIGIN="http://localhost:3000")

        self.assertEqual(response.headers.get("Access-Control-Allow-Origin"), "http://localhost:3000")

    def test_other_origins_are_not(self):
        response = self.client.get("/api/stats/", HTTP_ORIGIN="https://attacker.example")

        self.assertNotIn("Access-Control-Allow-Origin", response.headers)
