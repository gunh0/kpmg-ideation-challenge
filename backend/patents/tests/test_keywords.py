import re

from django.test import SimpleTestCase

from patents.keywords import MAX_KEYWORDS, parse_keywords, topic_pattern


class ParseKeywordsTests(SimpleTestCase):
    def test_splits_normalises_and_deduplicates(self):
        self.assertEqual(
            parse_keywords("Drone,  UAV\nunmanned   aerial , drone,"),
            ["drone", "uav", "unmanned aerial"],
        )
        self.assertEqual(parse_keywords(["Self-driving", "O'Hare"]), ["self-driving", "o'hare"])

    def test_rejects_expressions_and_symbols(self):
        for text in ("dr.ne", "a|b", "(drone)", "drone*", "x", "cyber--attack", "'drone"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                parse_keywords(text)

    def test_limits(self):
        with self.assertRaises(ValueError):
            parse_keywords(" , ")
        with self.assertRaises(ValueError):
            parse_keywords(",".join(f"word{i}" for i in range(MAX_KEYWORDS + 1)))
        with self.assertRaises(ValueError):
            parse_keywords("a" * 61)


class TopicPatternTests(SimpleTestCase):
    def matches(self, keywords, text):
        return re.search(topic_pattern(keywords), text.lower()) is not None

    def test_whole_words_with_plurals(self):
        self.assertTrue(self.matches(["drone"], "Swarms of drones for delivery"))
        self.assertTrue(self.matches(["uav"], "Charging UAVs"))
        self.assertFalse(self.matches(["drone"], "Hydrones in soil"))

    def test_phrases_accept_spaces_and_hyphens(self):
        self.assertTrue(self.matches(["cyber attack"], "Detecting cyber-attacks on grids"))
        self.assertTrue(self.matches(["self-driving"], "A self driving shuttle"))
        self.assertTrue(self.matches(["unmanned aerial"], "unmanned  aerial vehicle"))

    def test_characters_are_literal(self):
        self.assertTrue(self.matches(["o'hare"], "Flights at O'Hare"))
        self.assertIn(r"o'hare", topic_pattern(["o'hare"]).replace("\\'", "'"))
