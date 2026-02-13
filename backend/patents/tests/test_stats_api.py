from datetime import date

from rest_framework.test import APITestCase

from patents.tests.factories import example_dataset, make_dataset


class StatsApiTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.dataset = example_dataset()
        cls.other = make_dataset(
            "Other",
            [{"patent_id": "ZZ-9-A1", "title": "Unrelated antenna", "assignee": "Other Corp.", "inventors": "John Roe",
              "filing_date": date(2015, 4, 1)}],
        )

    def stats(self, query=""):
        response = self.client.get(f"/api/stats/?{query}")
        self.assertEqual(response.status_code, 200)
        return response.json()

    def test_totals(self):
        body = self.stats(f"dataset={self.dataset.pk}")

        self.assertEqual(body["total"], 3)
        self.assertEqual(body["granted"], 2)

    def test_by_year_counts_each_date_in_its_own_year(self):
        by_year = {row["year"]: row for row in self.stats(f"dataset={self.dataset.pk}")["by_year"]}

        self.assertEqual(list(by_year), [2017, 2018, 2019, 2020])
        self.assertEqual(by_year[2019], {"year": 2019, "filed": 1, "published": 1, "granted": 1})
        self.assertEqual(by_year[2020], {"year": 2020, "filed": 0, "published": 2, "granted": 1})

    def test_rankings(self):
        body = self.stats()

        self.assertEqual(body["top_assignees"][0], {"name": "Example Robotics Inc.", "count": 2, "granted": 2})
        self.assertEqual(body["top_assignees"][1], {"name": "Example Logistics Corp.", "count": 1, "granted": 0})
        self.assertEqual(body["top_inventors"][0], {"name": "John Roe", "count": 3})

    def test_stats_follow_the_patent_filters_and_search(self):
        self.assertEqual(self.stats("granted=false")["total"], 2)
        self.assertEqual(self.stats("search=antenna")["top_assignees"], [{"name": "Other Corp.", "count": 1, "granted": 0}])
        self.assertEqual(self.stats("year_from=2020")["total"], 2)

    def test_top_limits_the_rankings(self):
        self.assertEqual(len(self.stats("top=1")["top_inventors"]), 1)
        self.assertEqual(len(self.stats("top=0")["top_inventors"]), 1)
        self.assertEqual(len(self.stats("top=abc")["top_inventors"]), 4)  # default 10, four inventors exist

    def test_empty_selection(self):
        self.assertEqual(
            self.stats("search=nothing-matches"),
            {"total": 0, "granted": 0, "by_year": [], "top_assignees": [], "top_inventors": []},
        )
