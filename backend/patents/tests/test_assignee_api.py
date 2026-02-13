from rest_framework.test import APITestCase

from patents.tests.factories import example_dataset, make_dataset


class AssigneeApiTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.dataset = example_dataset()
        cls.other = make_dataset(
            "Other",
            [
                {"patent_id": "ZZ-9-A1", "title": "Antenna", "assignee": "Example Robotics Inc."},
                {"patent_id": "ZZ-8-A1", "title": "No assignee"},
            ],
        )

    def get(self, query=""):
        return self.client.get(f"/api/assignees/?{query}").json()

    def test_ranks_assignees_by_patent_count(self):
        self.assertEqual(
            self.get(),
            [{"name": "Example Robotics Inc.", "count": 3}, {"name": "Example Logistics Corp.", "count": 1}],
        )

    def test_limits_to_a_dataset(self):
        self.assertEqual(self.get(f"dataset={self.other.pk}"), [{"name": "Example Robotics Inc.", "count": 1}])

    def test_matches_part_of_the_name(self):
        self.assertEqual([row["name"] for row in self.get("search=LOGIS")], ["Example Logistics Corp."])

    def test_ignores_an_invalid_dataset(self):
        self.assertEqual(len(self.get("dataset=abc")), 2)
