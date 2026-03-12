"""Turn publications into one patent record per application.

An application is usually published twice: as an application (kind A1) about
18 months after filing, and again when it is granted (B1/B2, S1 for designs).
The dashboard counts inventions, so both publications become one record that
is known by its grant number once there is one.
"""
import html
from datetime import date

from .google import patent_url

GRANT_KINDS = ("B1", "B2", "E1", "S1", "P2", "P3")


def to_date(value):
    """20200818 -> date(2020, 8, 18); 0 or empty -> None."""
    if not value:
        return None
    value = int(value)
    return date(value // 10000, value // 100 % 100, value % 100)


def text(value):
    """Some titles and names carry HTML entities (&#39;, &amp;, &ldquo;)."""
    return " ".join(html.unescape(value or "").split())


def person_name(raw):
    """Inventors are listed as "MOLNAR, DEZSO"; show them as "Dezso Molnar"."""
    last, _, first = text(raw).partition(",")
    name = f"{first.strip()} {last.strip()}".strip()
    if name.isupper():
        name = name.title()
    return " ".join(name.replace(",", " ").split())


def merge(rows):
    """Group publication rows (dicts from opendata.read_topics) by application.

    Returns {topic slug: [record, ...]} where a record holds Patent fields; a
    record is listed under each topic it matches.
    """
    applications = {}
    for row in rows:
        applications.setdefault(row["application_number"], []).append(row)

    topics = {}
    for application, publications in applications.items():
        publications.sort(key=lambda row: row["publication_date"])
        latest = publications[-1]
        grants = [row for row in publications if row["kind_code"] in GRANT_KINDS or row["grant_date"]]
        number_from = grants[-1] if grants else latest
        inventors = [person_name(name) for name in latest["inventor"] or []]
        assignees = [text(name) for name in latest["assignee"] or [] if text(name)]
        record = {
            "patent_id": number_from["publication_number"],
            "application_number": application,
            "family_id": latest["family_id"] or "",
            "title": text(latest["title"]),
            "assignee": assignees[0] if assignees else "",
            "inventors": ", ".join(dict.fromkeys(name for name in inventors if name)),
            "priority_date": to_date(latest["priority_date"]),
            "filing_date": to_date(latest["filing_date"]),
            "publication_date": to_date(publications[0]["publication_date"]),
            "grant_date": max((to_date(row["grant_date"]) for row in grants if row["grant_date"]), default=None),
            "result_link": patent_url(number_from["publication_number"]),
        }
        # A patent belongs to every topic one of its publications matches.
        for slug in sorted({slug for row in publications for slug in row["topics"]}):
            topics.setdefault(slug, []).append(record)
    for records in topics.values():
        records.sort(key=lambda record: record["patent_id"])
    return topics
