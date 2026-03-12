from datetime import date

from django.test import SimpleTestCase

from patents.records import merge, person_name, to_date


def publication(number, kind, published, granted=0, **values):
    row = {
        "topics": ["drones"],
        "publication_number": number,
        "application_number": "US-201816000001-A",
        "kind_code": kind,
        "family_id": "1",
        "title": "Drone delivery of parcels",
        "priority_date": 20170301,
        "filing_date": 20180305,
        "publication_date": published,
        "grant_date": granted,
        "assignee": ["Example Robotics Inc."],
        "inventor": ["DOE, JANE", "ROE, JOHN"],
    }
    row.update(values)
    return row


class NameTests(SimpleTestCase):
    def test_last_first_becomes_first_last(self):
        self.assertEqual(person_name("MOLNAR, DEZSO"), "Dezso Molnar")
        self.assertEqual(person_name("DUKE, LOWELL L."), "Lowell L. Duke")
        self.assertEqual(person_name("Akbar, Zehra"), "Zehra Akbar")

    def test_names_without_a_comma_are_kept(self):
        self.assertEqual(person_name("Madonna"), "Madonna")
        self.assertEqual(person_name("  VAN DER BERG, JAN , JR  "), "Jan Jr Van Der Berg")

    def test_dates(self):
        self.assertEqual(to_date(20200818), date(2020, 8, 18))
        self.assertIsNone(to_date(0))
        self.assertIsNone(to_date(None))


class MergeTests(SimpleTestCase):
    def test_application_and_grant_become_one_granted_record(self):
        rows = [
            publication("US-10000001-B2", "B2", 20200602, 20200602, title="Drone delivery of parcels to balconies"),
            publication("US-2019000001-A1", "A1", 20190103),
        ]

        [record] = merge(rows)["drones"]

        self.assertEqual(record["patent_id"], "US-10000001-B2")
        self.assertEqual(record["title"], "Drone delivery of parcels to balconies")
        self.assertEqual(record["publication_date"], date(2019, 1, 3))
        self.assertEqual(record["grant_date"], date(2020, 6, 2))
        self.assertEqual(record["inventors"], "Jane Doe, John Roe")
        self.assertEqual(record["assignee"], "Example Robotics Inc.")
        self.assertEqual(record["result_link"], "https://patents.google.com/patent/US10000001B2/en")

    def test_html_entities_are_decoded(self):
        rows = [publication("US-2019000001-A1", "A1", 20190103, title="Controlling vehicles based on edge servers&#39; load",
                            assignee=["Smith &amp; Sons"], inventor=["O&#39;BRIEN, PAT"])]

        [record] = merge(rows)["drones"]

        self.assertEqual(record["title"], "Controlling vehicles based on edge servers' load")
        self.assertEqual(record["assignee"], "Smith & Sons")
        self.assertEqual(record["inventors"], "Pat O'Brien")

    def test_pending_application_keeps_its_publication_number(self):
        [record] = merge([publication("US-2019000001-A1", "A1", 20190103)])["drones"]

        self.assertEqual(record["patent_id"], "US-2019000001-A1")
        self.assertIsNone(record["grant_date"])

    def test_a_record_is_listed_under_every_topic_it_matches(self):
        rows = [
            publication("US-2019000001-A1", "A1", 20190103, topics=["drones"]),
            publication("US-10000001-B2", "B2", 20200602, 20200602, topics=["drones", "cybersecurity"]),
        ]

        topics = merge(rows)

        self.assertEqual(sorted(topics), ["cybersecurity", "drones"])
        self.assertIs(topics["drones"][0], topics["cybersecurity"][0])

    def test_records_are_grouped_by_topic(self):
        rows = [
            publication("US-2019000001-A1", "A1", 20190103),
            publication("US-2021000002-A1", "A1", 20210304, application_number="US-202016000002-A", topics=["cybersecurity"],
                        assignee=[], inventor=[]),
        ]

        topics = merge(rows)

        self.assertEqual(sorted(topics), ["cybersecurity", "drones"])
        self.assertEqual(topics["cybersecurity"][0]["assignee"], "")
        self.assertEqual(topics["cybersecurity"][0]["inventors"], "")
