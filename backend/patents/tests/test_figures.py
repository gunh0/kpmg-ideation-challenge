import io
import urllib.error
from datetime import date
from unittest import mock

from django.test import SimpleTestCase, TestCase

from patents import figures
from patents.models import Patent
from patents.store import store_topic
from patents.tests.test_store import record
from patents.topics import get_topic

PAGE = """
<section itemprop="description">...</section>
<li itemprop="images" itemscope repeat>
  <img itemprop="thumbnail" src="https://patentimages.storage.googleapis.com/66/1f/12/6508c4fc768597/US10186348-20190122-D00000.png">
  <meta itemprop="full" content="https://patentimages.storage.googleapis.com/2c/e0/93/a7e71a5d9dd1a6/US10186348-20190122-D00000.png">
</li>
<li itemprop="images" itemscope repeat>
  <img itemprop="thumbnail" src="https://patentimages.storage.googleapis.com/2b/3c/38/4a10b36ae264de/US10186348-20190122-D00001.png">
</li>
"""


def response(html):
    body = io.BytesIO(html.encode())
    body.__enter__ = lambda self=body: self
    body.__exit__ = lambda *args: None
    return body


class ParseTests(SimpleTestCase):
    def test_first_drawing_is_the_representative_figure(self):
        thumbnail, full = figures.parse_figure(PAGE)

        self.assertTrue(thumbnail.endswith("/6508c4fc768597/US10186348-20190122-D00000.png"))
        self.assertTrue(full.endswith("/a7e71a5d9dd1a6/US10186348-20190122-D00000.png"))

    def test_page_without_drawings(self):
        self.assertEqual(figures.parse_figure("<html></html>"), ("", ""))

    def test_images_from_other_hosts_are_ignored(self):
        page = '<img itemprop="thumbnail" src="https://evil.example/x.png">'
        self.assertEqual(figures.parse_figure(page), ("", ""))


class FetchTests(SimpleTestCase):
    def test_requests_the_google_patents_page(self):
        with mock.patch("urllib.request.urlopen", return_value=response(PAGE)) as urlopen:
            thumbnail, _ = figures.fetch_figure("US-10186348-B2")

        request = urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "https://patents.google.com/patent/US10186348B2/en")
        self.assertIn("PatentAttorneyWithoutBorders", request.get_header("User-agent"))
        self.assertTrue(thumbnail)

    def test_missing_page_means_no_figure(self):
        error = urllib.error.HTTPError("url", 404, "Not Found", {}, None)
        with mock.patch("urllib.request.urlopen", side_effect=error):
            self.assertEqual(figures.fetch_figure("US-1-B2"), ("", ""))


class FillTests(TestCase):
    def setUp(self):
        store_topic(get_topic("drones"), [record("US-10186348-B2"), record("US-2-A1")], "abc123")

    def test_stores_what_was_found_and_that_it_was_checked(self):
        pages = {"US10186348B2": PAGE, "US2A1": "<html></html>"}

        def urlopen(request, timeout):
            return response(pages[request.full_url.split("/")[-2]])

        with mock.patch("urllib.request.urlopen", side_effect=urlopen):
            figures.fill_figures(Patent.objects.all())

        found = Patent.objects.get(patent_id="US-10186348-B2")
        self.assertTrue(found.thumbnail_link.endswith("D00000.png"))
        self.assertIsNotNone(found.figure_checked_at)
        none = Patent.objects.get(patent_id="US-2-A1")
        self.assertEqual(none.thumbnail_link, "")
        self.assertIsNotNone(none.figure_checked_at)

    def test_network_errors_are_retried_later(self):
        with mock.patch("urllib.request.urlopen", side_effect=urllib.error.URLError("offline")):
            with self.assertLogs("patents.figures", level="WARNING"):
                figures.fill_figures(Patent.objects.all())

        self.assertFalse(Patent.objects.exclude(figure_checked_at=None).exists())

    def test_checked_patents_are_not_fetched_again(self):
        Patent.objects.update(figure_checked_at=date(2026, 1, 1))
        with mock.patch("urllib.request.urlopen") as urlopen:
            figures.fill_figures(Patent.objects.all())

        urlopen.assert_not_called()
