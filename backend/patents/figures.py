"""Representative figures from Google Patents.

Pages of single patents are open to crawlers (robots.txt allows /patent/),
unlike the search, which is why the patents themselves come from the public
data. The first drawing of a page is the representative figure; Google serves
a thumbnail and the full image from its patent image host. Each patent is
looked up once and the result is stored, so the pages are fetched at the pace
people browse, a few at a time.
"""
import logging
import re
import threading
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

from django.utils import timezone

from .google import patent_url

logger = logging.getLogger(__name__)

USER_AGENT = "PatentAttorneyWithoutBorders/2.0 (+https://github.com/gunh0/kpmg-ideation-challenge)"
IMAGE_HOST = "https://patentimages.storage.googleapis.com/"
THUMBNAIL = re.compile(r'<img itemprop="thumbnail" src="([^"]+)"')
FULL = re.compile(r'<meta itemprop="full" content="([^"]+)"')
# Requests to Google in flight across all threads of this process.
_slots = threading.BoundedSemaphore(4)


def parse_figure(html):
    """(thumbnail URL, full image URL) of the first drawing, "" if there is none."""
    def first(pattern):
        match = pattern.search(html)
        url = match.group(1) if match else ""
        return url if url.startswith(IMAGE_HOST) else ""

    return first(THUMBNAIL), first(FULL)


def image_available(url, timeout=10):
    """Pages of the newest publications name images that Google does not
    serve yet (403), so a figure is only kept once its image loads."""
    request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status == 200
    except urllib.error.HTTPError as error:
        if error.code in (403, 404):
            return False
        raise


def fetch_figure(publication_number, timeout=10):
    """Look the figure up on the patent's page. Returns ("", "") when the page
    has no drawing, its image is not served or the page does not exist;
    raises on network errors."""
    request = urllib.request.Request(patent_url(publication_number), headers={"User-Agent": USER_AGENT})
    with _slots:
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                html = response.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as error:
            if error.code == 404:
                return "", ""
            raise
        thumbnail, full = parse_figure(html)
        if thumbnail and not image_available(thumbnail, timeout):
            return "", ""
    return thumbnail, full


def fill_figures(patents, workers=4):
    """Look up the figures of `patents` that were not checked yet and save them.

    A failed request leaves the patent unchecked, so it is tried again later.
    """
    todo = [patent for patent in patents if patent.figure_checked_at is None]

    def lookup(patent):
        try:
            return patent, fetch_figure(patent.patent_id)
        except (OSError, urllib.error.URLError) as error:
            logger.warning("figure of %s: %s", patent.patent_id, error)
            return patent, None

    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(lookup, todo))
    for patent, figure in results:
        if figure is None:
            continue
        patent.thumbnail_link, patent.figure_link = figure
        patent.figure_checked_at = timezone.now()
        patent.save(update_fields=["thumbnail_link", "figure_link", "figure_checked_at"])
    return patents
