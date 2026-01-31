"""Addresses on patents.google.com."""
import re

# US-2021229811-A1: a pre-grant publication, year plus serial number
US_PUBLICATION = re.compile(r"^US-(\d{4})(\d{1,7})-(A\d)$")


def patent_url(publication_number):
    """US-10186348-B2 -> https://patents.google.com/patent/US10186348B2/en

    Google writes US application publications with a seven-digit serial
    (US20210229811A1), the public data without the leading zero.
    """
    match = US_PUBLICATION.match(publication_number)
    if match:
        year, serial, kind = match.groups()
        compact = f"US{year}{serial.zfill(7)}{kind}"
    else:
        compact = publication_number.replace("-", "")
    return f"https://patents.google.com/patent/{compact}/en"
