from pathlib import Path

from rest_framework.test import APITestCase

from patents.importer import import_export

FIXTURE = Path(__file__).parent / "fixtures" / "export.csv"


class PatentApiTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.dataset = import_export(FIXTURE.read_text()).dataset
        cls.other = import_export("id,title,assignee\nZZ-9-A1,Unrelated antenna,Other Corp.\n", name="Other").dataset

    def ids(self, query=""):
        response = self.client.get(f"/api/patents/?{query}")
        self.assertEqual(response.status_code, 200)
        return [patent["patent_id"] for patent in response.json()["results"]]

    def test_list_is_paginated_and_newest_first(self):
        body = self.client.get("/api/patents/").json()

        self.assertEqual(body["count"], 4)
        self.assertEqual(body["results"][0]["patent_id"], "ZZ-0000002-A1")

    def test_detail_serializes_inventors_and_grant_status(self):
        patent = self.dataset.patents.get(patent_id="ZZ-0000001-B2")

        body = self.client.get(f"/api/patents/{patent.pk}/").json()

        self.assertEqual(body["inventors"], ["Jane Doe", "John Roe"])
        self.assertTrue(body["is_granted"])
        self.assertEqual(body["publication_date"], "2019-08-20")

    def test_filter_by_dataset(self):
        self.assertEqual(self.ids(f"dataset={self.other.pk}"), ["ZZ-9-A1"])

    def test_search_matches_title_assignee_inventors_and_id(self):
        self.assertEqual(self.ids("search=antenna"), ["ZZ-9-A1"])
        self.assertEqual(self.ids("search=logistics"), ["ZZ-0000002-A1"])
        self.assertEqual(self.ids("search=richard"), ["ZZ-0000003-B1"])
        self.assertEqual(self.ids("search=ZZ-0000001"), ["ZZ-0000001-B2"])

    def test_filter_by_assignee_ignores_case(self):
        self.assertEqual(self.ids("assignee=EXAMPLE ROBOTICS INC.&ordering=patent_id"), ["ZZ-0000001-B2", "ZZ-0000003-B1"])

    def test_filter_by_grant_status(self):
        self.assertEqual(self.ids(f"dataset={self.dataset.pk}&granted=false"), ["ZZ-0000002-A1"])
        self.assertEqual(len(self.ids("granted=true")), 2)

    def test_filter_by_publication_year_range(self):
        self.assertEqual(self.ids("year_from=2020&ordering=patent_id"), ["ZZ-0000002-A1", "ZZ-0000003-B1"])
        self.assertEqual(self.ids("year_to=2019"), ["ZZ-0000001-B2"])

    def test_ordering_and_page_size(self):
        body = self.client.get("/api/patents/?ordering=priority_date&page_size=1").json()

        self.assertEqual([p["patent_id"] for p in body["results"]], ["ZZ-0000001-B2"])
        self.assertIsNotNone(body["next"])

    def test_api_is_read_only(self):
        self.assertEqual(self.client.post("/api/patents/", {"title": "x"}).status_code, 405)

    def test_filter_by_inventor_matches_whole_names(self):
        self.assertEqual(self.ids("inventor=john roe&ordering=patent_id"), ["ZZ-0000001-B2", "ZZ-0000003-B1"])
        self.assertEqual(self.ids("inventor=Roe"), [])
        self.assertEqual(self.ids("inventor=Mary Major"), ["ZZ-0000002-A1"])

    def test_search_finds_numbers_written_without_dashes(self):
        self.assertEqual(self.ids("search=ZZ0000001B2"), ["ZZ-0000001-B2"])
        self.assertEqual(self.ids("search=zz0000003b1"), ["ZZ-0000003-B1"])
        self.assertEqual(self.ids(f"search=ZZ0000001B2&dataset={self.other.pk}"), [])

    def test_stats_use_the_same_search(self):
        self.assertEqual(self.client.get("/api/stats/?search=ZZ0000002A1").json()["total"], 1)
