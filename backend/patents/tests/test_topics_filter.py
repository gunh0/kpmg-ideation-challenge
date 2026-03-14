from rest_framework.test import APITestCase

from patents.models import Patent
from patents.tests.factories import make_dataset


def patent(number, published):
    return {"patent_id": number, "title": f"Patent {number}", "publication_date": published}


class TopicFilterTests(APITestCase):
    """Several topics at once: patents matching more of them come first."""

    @classmethod
    def setUpTestData(cls):
        cls.drones = make_dataset("Drones", [patent("ZZ-1-B1", "2020-01-01"), patent("ZZ-2-B1", "2021-01-01"),
                                             patent("ZZ-3-B1", "2022-01-01")])
        cls.delivery = make_dataset("Delivery", [patent("ZZ-2-B1", "2021-01-01"), patent("ZZ-4-B1", "2023-01-01")])
        cls.locks = make_dataset("Locks", [patent("ZZ-2-B1", "2021-01-01"), patent("ZZ-3-B1", "2022-01-01")])

    def get(self, query):
        return self.client.get(f"/api/patents/?{query}").json()

    def test_a_patent_is_stored_once_for_all_its_topics(self):
        self.assertEqual(Patent.objects.count(), 4)
        shared = self.get("search=ZZ-2-B1")["results"][0]
        self.assertEqual(sorted(shared["topics"]), sorted([self.drones.pk, self.delivery.pk, self.locks.pk]))

    def test_best_matches_first(self):
        ids = f"{self.drones.pk},{self.delivery.pk},{self.locks.pk}"

        results = self.get(f"topics={ids}&ordering=-matched,-publication_date")["results"]

        self.assertEqual(
            [(row["patent_id"], row["matched"]) for row in results],
            [("ZZ-2-B1", 3), ("ZZ-3-B1", 2), ("ZZ-4-B1", 1), ("ZZ-1-B1", 1)],
        )

    def test_match_all(self):
        ids = f"{self.drones.pk},{self.locks.pk}"

        results = self.get(f"topics={ids}&match=all")["results"]

        self.assertEqual(sorted(row["patent_id"] for row in results), ["ZZ-2-B1", "ZZ-3-B1"])

    def test_counts_and_stats_follow_the_selection(self):
        ids = f"{self.delivery.pk},{self.locks.pk}"

        self.assertEqual(self.get(f"topics={ids}")["count"], 3)
        self.assertEqual(self.client.get(f"/api/stats/?topics={ids}").json()["total"], 3)
        self.assertEqual(self.client.get(f"/api/stats/?topics={ids}&match=all").json()["total"], 1)

    def test_ordering_by_matches_is_ignored_without_topics(self):
        self.assertEqual(self.get("ordering=-matched")["count"], 4)

    def test_search_and_topics_together(self):
        results = self.get(f"topics={self.drones.pk},{self.delivery.pk}&search=ZZ-2")["results"]

        self.assertEqual([(row["patent_id"], row["matched"]) for row in results], [("ZZ-2-B1", 2)])
