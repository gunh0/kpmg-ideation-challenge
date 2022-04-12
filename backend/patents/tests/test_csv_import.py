from datetime import date
from pathlib import Path

from django.test import SimpleTestCase

from patents.csv_import import CSVFormatError, parse_date, parse_export

FIXTURE = Path(__file__).parent / "fixtures" / "export.csv"


class ParseExportTests(SimpleTestCase):
    def test_reads_search_url_and_rows(self):
        result = parse_export(FIXTURE.read_text())

        self.assertEqual(result.search_url, "https://patents.google.com/?q=(drone+delivery)&before=priority:20200101")
        self.assertEqual([row["patent_id"] for row in result.rows], ["ZZ-0000001-B2", "ZZ-0000002-A1", "ZZ-0000003-B1"])
        self.assertEqual(result.skipped, 1)

    def test_maps_columns_to_model_fields(self):
        row = parse_export(FIXTURE.read_text()).rows[0]

        self.assertEqual(row["assignee"], "Example Robotics Inc.")
        self.assertEqual(row["inventors"], "Jane Doe, John Roe")
        self.assertEqual(row["priority_date"], date(2016, 3, 14))
        self.assertEqual(row["grant_date"], date(2019, 8, 20))
        self.assertTrue(row["figure_link"].endswith("ZZ0000001B2.png"))

    def test_missing_dates_become_none(self):
        row = parse_export(FIXTURE.read_text()).rows[1]

        self.assertIsNone(row["grant_date"])
        self.assertEqual(row["figure_link"], "")

    def test_accepts_byte_order_mark_and_no_search_url_line(self):
        text = "﻿id,title\nZZ-1-A1,Only the required columns\n"

        result = parse_export(text)

        self.assertEqual(result.search_url, "")
        self.assertEqual(result.rows[0]["title"], "Only the required columns")
        self.assertIsNone(result.rows[0]["publication_date"])

    def test_rejects_files_without_required_columns(self):
        with self.assertRaisesMessage(CSVFormatError, "missing column(s): id, title"):
            parse_export("name,value\na,b\n")

    def test_parse_date(self):
        self.assertEqual(parse_date("2021-12-31"), date(2021, 12, 31))
        self.assertIsNone(parse_date(""))
        self.assertIsNone(parse_date("31/12/2021"))

    def test_links_must_be_http(self):
        text = "id,title,result link,representative figure link\nZZ-1-A1,T,javascript:alert(1),HTTPS://example.org/f.png\n"

        row = parse_export(text).rows[0]

        self.assertEqual(row["result_link"], "")
        self.assertEqual(row["figure_link"], "HTTPS://example.org/f.png")
