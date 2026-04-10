from django.test import TestCase
from django.urls import reverse


class SchemaTests(TestCase):
    def test_describes_every_endpoint(self):
        response = self.client.get(reverse("schema"), HTTP_ACCEPT="application/vnd.oai.openapi+json")

        self.assertEqual(response.status_code, 200)
        schema = response.json()
        self.assertEqual(schema["info"]["title"], "Patent Attorney Without Borders API")
        for path in ("/api/patents/", "/api/topics/", "/api/stats/", "/api/assignees/", "/api/figures/", "/api/config/"):
            self.assertIn(path, schema["paths"])

    def test_stats_share_the_patent_filters(self):
        schema = self.client.get(reverse("schema"), HTTP_ACCEPT="application/vnd.oai.openapi+json").json()

        names = {parameter["name"] for parameter in schema["paths"]["/api/stats/"]["get"]["parameters"]}
        self.assertLessEqual({"topics", "match", "country", "assignee", "inventor", "granted", "year_from", "top"}, names)
