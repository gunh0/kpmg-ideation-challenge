from django.test import TestCase

from patents.keywords import topic_pattern
from patents.matcher import match_stored
from patents.models import Patent, Topic
from patents.tests.factories import make_dataset


class MatchStoredTests(TestCase):
    def setUp(self):
        make_dataset("Drones", [
            {"patent_id": "ZZ-1-B1", "title": "Parcel drone", "abstract": "Delivers parcels to lockers."},
            {"patent_id": "ZZ-2-B1", "title": "Quadcopter frame", "abstract": "A foldable frame."},
        ])

    def topic(self, keywords):
        topic = Topic.objects.create(name="Lockers")
        topic.set_keywords(keywords)
        topic.save()
        return topic

    def test_links_the_stored_patents_that_match_in_title_or_abstract(self):
        topic = self.topic(["locker", "frame"])

        self.assertEqual(match_stored(topic), 2)
        self.assertEqual(sorted(topic.patents.values_list("patent_id", flat=True)), ["ZZ-1-B1", "ZZ-2-B1"])

    def test_replaces_the_links_and_drops_patents_no_topic_keeps(self):
        Drones = Topic.objects.get(name="Drones")
        topic = self.topic(["locker"])
        match_stored(topic)
        Drones.delete()

        topic.set_keywords(["battery"])
        match_stored(topic)

        self.assertEqual(topic.patents.count(), 0)
        self.assertFalse(Patent.objects.exists())

    def test_keywords_are_words_not_substrings(self):
        topic = self.topic(["parcel lock"])

        self.assertEqual(match_stored(topic), 0)
        self.assertEqual(topic_pattern(["parcel lock"]), topic.pattern)
