"""Parsing of Google Patents search result exports.

The "Download (CSV)" button on patents.google.com produces a file whose first
line holds the search URL and whose second line is the header:

    search URL:,https://patents.google.com/?q=...
    id,title,assignee,inventor/author,priority date,filing/creation date,publication date,grant date,result link,representative figure link
"""
import csv
import io
from dataclasses import dataclass, field
from datetime import date

COLUMNS = {
    "id": "patent_id",
    "title": "title",
    "assignee": "assignee",
    "inventor/author": "inventors",
    "priority date": "priority_date",
    "filing/creation date": "filing_date",
    "publication date": "publication_date",
    "grant date": "grant_date",
    "result link": "result_link",
    "representative figure link": "figure_link",
}
DATE_FIELDS = ("priority_date", "filing_date", "publication_date", "grant_date")
REQUIRED = ("id", "title")


class CSVFormatError(ValueError):
    """The file is not a Google Patents export."""


@dataclass
class ParsedExport:
    search_url: str = ""
    rows: list = field(default_factory=list)
    skipped: int = 0


def parse_date(value):
    value = (value or "").strip()
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def parse_export(text):
    """Parse the text of an export into patent dicts keyed by model field."""
    text = text.lstrip("﻿")
    lines = text.splitlines()
    result = ParsedExport()

    if lines and lines[0].lower().startswith("search url"):
        first = next(csv.reader([lines[0]]))
        result.search_url = first[1].strip() if len(first) > 1 else ""
        lines = lines[1:]

    reader = csv.DictReader(io.StringIO("\n".join(lines)))
    header = [name.strip().lower() for name in reader.fieldnames or []]
    missing = [name for name in REQUIRED if name not in header]
    if missing:
        raise CSVFormatError(f"missing column(s): {', '.join(missing)}")
    reader.fieldnames = header

    for record in reader:
        row = {
            model_field: (record.get(column) or "").strip()
            for column, model_field in COLUMNS.items()
        }
        if not row["patent_id"] or not row["title"]:
            result.skipped += 1
            continue
        for name in DATE_FIELDS:
            row[name] = parse_date(row[name])
        result.rows.append(row)
    return result
