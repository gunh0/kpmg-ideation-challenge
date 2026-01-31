from django.test import SimpleTestCase

from patents.google import patent_url


class PatentUrlTests(SimpleTestCase):
    def test_grants_and_designs(self):
        self.assertEqual(patent_url("US-10186348-B2"), "https://patents.google.com/patent/US10186348B2/en")
        self.assertEqual(patent_url("US-D912345-S1"), "https://patents.google.com/patent/USD912345S1/en")

    def test_application_publications_get_a_seven_digit_serial(self):
        self.assertEqual(patent_url("US-2021229811-A1"), "https://patents.google.com/patent/US20210229811A1/en")
        self.assertEqual(patent_url("US-20210229811-A1"), "https://patents.google.com/patent/US20210229811A1/en")
