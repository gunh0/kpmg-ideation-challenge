import re

from django.test import SimpleTestCase

from patents.topics import TOPICS, get_topic


class TopicTests(SimpleTestCase):
    def test_slugs_are_unique(self):
        self.assertEqual(len({topic.slug for topic in TOPICS}), len(TOPICS))

    def test_patterns_match_whole_words(self):
        cases = {
            "drones": (["Drone delivery improvements", "Battery for a UAV", "Unmanned aerial vehicle docking"], ["Hydrones in soil"]),
            "autonomous-driving": (["Driverless shuttle", "Control of an autonomous vehicle"], ["Autonomous robot vacuum"]),
            "cybersecurity": (["Ransomware recovery", "Detecting cyber attacks"], ["Malwarehouse shelving"]),
        }
        for slug, (hits, misses) in cases.items():
            pattern = re.compile(get_topic(slug).pattern)
            for title in hits:
                self.assertRegex(title.lower(), pattern)
            for title in misses:
                self.assertNotRegex(title.lower(), pattern)

    def test_unknown_topic(self):
        with self.assertRaises(KeyError):
            get_topic("nope")
