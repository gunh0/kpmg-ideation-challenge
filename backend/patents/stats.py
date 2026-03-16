"""Aggregates for the dashboard, computed over an already filtered queryset."""
from collections import Counter, defaultdict

from django.db.models import Count, Q
from django.db.models.functions import ExtractYear

from .models import Patent

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


def top_assignees(queryset, limit):
    rows = (
        queryset.exclude(assignee="")
        .values("assignee")
        .annotate(count=Count("id"), granted=Count("id", filter=Q(grant_date__isnull=False)))
        .order_by("-count", "assignee")[:limit]
    )
    return [{"name": row["assignee"], "count": row["count"], "granted": row["granted"]} for row in rows]


def top_inventors(queryset, limit):
    """Inventors are stored comma-separated, so they are counted in Python."""
    counts = Counter()
    for inventors in queryset.exclude(inventors="").values_list("inventors", flat=True):
        counts.update({name.strip() for name in inventors.split(",") if name.strip()})
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:limit]
    return [{"name": name, "count": count} for name, count in ranked]


def top_countries(queryset, limit):
    """Countries of the first assignees, e.g. [{"code": "KR", "count": 72, "granted": 50}]."""
    rows = (
        queryset.exclude(assignee_country="")
        .values("assignee_country")
        .annotate(count=Count("id"), granted=Count("id", filter=Q(grant_date__isnull=False)))
        .order_by("-count", "assignee_country")[:limit]
    )
    return [{"code": row["assignee_country"], "count": row["count"], "granted": row["granted"]} for row in rows]


def topics_by_year(queryset, limit=8):
    """Publications per year of each topic, for the topics with the most
    patents in the selection (at most `limit`, the colours a chart can tell
    apart)."""
    memberships = Patent.topics.through.objects.filter(patent__in=queryset)
    top = list(
        memberships.values("topic_id", "topic__name").annotate(count=Count("id")).order_by("-count", "topic__name")[:limit]
    )
    rows = (
        memberships.filter(topic_id__in=[row["topic_id"] for row in top], patent__publication_date__isnull=False)
        .annotate(year=ExtractYear("patent__publication_date"))
        .values("topic_id", "year")
        .annotate(n=Count("id"))
        .order_by()
    )
    years = defaultdict(dict)
    for row in rows:
        years[row["topic_id"]][row["year"]] = row["n"]
    return [
        {
            "id": row["topic_id"],
            "name": row["topic__name"],
            "count": row["count"],
            "by_year": [{"year": year, "published": n} for year, n in sorted(years[row["topic_id"]].items())],
        }
        for row in top
    ]


def summary(queryset, limit=10):
    return {
        "total": queryset.count(),
        "granted": queryset.filter(grant_date__isnull=False).count(),
        "by_year": patents_by_year(queryset),
        "top_assignees": top_assignees(queryset, limit),
        "top_inventors": top_inventors(queryset, limit),
        "top_countries": top_countries(queryset, limit),
        "by_topic": topics_by_year(queryset),
    }
