"""Test data: datasets with patents, created directly."""
from datetime import date

from patents.models import Topic, Patent

# Fictional ZZ- numbers, so no test depends on a real patent.
EXAMPLE_PATENTS = [
    {
        "patent_id": "ZZ-0000001-B2",
        "title": "Parcel release mechanism for an unmanned aerial vehicle",
        "assignee": "Example Robotics Inc.",
        "inventors": "Jane Doe, John Roe",
        "priority_date": date(2016, 3, 14),
        "filing_date": date(2017, 3, 10),
        "publication_date": date(2019, 8, 20),
        "grant_date": date(2019, 8, 20),
        "result_link": "https://patents.google.com/patent/ZZ0000001B2/en",
        "figure_link": "https://patentimages.storage.googleapis.com/example/ZZ0000001B2.png",
    },
    {
        "patent_id": "ZZ-0000002-A1",
        "title": "Landing pad with charging contacts for delivery drones",
        "assignee": "Example Logistics Corp.",
        "inventors": "Mary Major",
        "priority_date": date(2018, 11, 2),
        "filing_date": date(2019, 10, 30),
        "publication_date": date(2020, 5, 7),
        "result_link": "https://patents.google.com/patent/ZZ0000002A1/en",
    },
    {
        "patent_id": "ZZ-0000003-B1",
        "title": "Route planning for aerial parcel delivery",
        "assignee": "Example Robotics Inc.",
        "inventors": "John Roe, Richard Miles",
        "priority_date": date(2017, 6, 1),
        "filing_date": date(2018, 5, 29),
        "publication_date": date(2020, 1, 14),
        "grant_date": date(2020, 1, 14),
        "result_link": "https://patents.google.com/patent/ZZ0000003B1/en",
    },
]


def make_dataset(name, patents, **fields):
    """A topic with `patents` (dicts of Patent fields); patents that exist
    already are linked, not created again."""
    topic = Topic.objects.create(name=name, **fields)
    for values in patents:
        values = dict(values)
        patent, _ = Patent.objects.get_or_create(patent_id=values.pop("patent_id"), defaults=values)
        patent.topics.add(topic)
    return topic


def example_dataset(name="Drone delivery", **fields):
    return make_dataset(name, EXAMPLE_PATENTS, **fields)
