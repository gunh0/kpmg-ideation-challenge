"""Aggregates for the dashboard, computed over an already filtered queryset."""
from collections import defaultdict

from django.db.models import Count
from django.db.models.functions import ExtractYear

YEAR_FIELDS = {"filed": "filing_date", "published": "publication_date", "granted": "grant_date"}


def patents_by_year(queryset):
    """Filings, publications and grants per calendar year, oldest first."""
    years = defaultdict(lambda: dict.fromkeys(YEAR_FIELDS, 0))
    for key, field in YEAR_FIELDS.items():
        rows = (
            queryset.exclude(**{f"{field}__isnull": True})
            .annotate(year=ExtractYear(field))
            .values("year")
            .annotate(n=Count("id"))
            .order_by()
        )
        for row in rows:
            years[row["year"]][key] = row["n"]
    return [{"year": year, **counts} for year, counts in sorted(years.items())]


def summary(queryset):
    return {
        "total": queryset.count(),
        "granted": queryset.filter(grant_date__isnull=False).count(),
        "by_year": patents_by_year(queryset),
    }
