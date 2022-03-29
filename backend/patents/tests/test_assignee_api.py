from pathlib import Path

from rest_framework.test import APITestCase

from patents.importer import import_export

FIXTURE = Path(__file__).parent / "fixtures" / "export.csv"


class AssigneeApiTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.dataset = import_export(FIXTURE.read_text()).dataset
        cls.other = import_export("id,title,assignee\nZZ-9-A1,Antenna,Example Robotics Inc.\nZZ-8-A1,No assignee,\n").dataset

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
