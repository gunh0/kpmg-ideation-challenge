"""How often each stored patent is cited.

The public data lists, for every publication, the publications it cites. The
opposite direction — who cites a patent — is found by reading the citations
of all publications once and keeping those that name one of ours. An
application is published more than once (A1, then B2) and both may cite the
same patent, so citations are counted per citing application.
"""
import logging
from collections import defaultdict

import duckdb

from . import opendata
from .models import Patent

logger = logging.getLogger(__name__)

CITATIONS = """
    SELECT DISTINCT application_number AS citing, cited.publication_number AS cited
    FROM (SELECT application_number, unnest(citation) AS cited FROM read_parquet('{source}'))
    JOIN ours ON ours.number = cited.publication_number
"""


def ours(patents):
    """{publication number: patent pk} over all publications of `patents`."""
    numbers = {}
    for pk, patent_id, publications in patents.values_list("pk", "patent_id", "publication_numbers"):
        for number in filter(None, (publications or patent_id).split(",")):
            numbers[number] = pk
    return numbers


def citing_pairs(source, numbers, connection):
    """(citing application, cited publication) pairs of one Parquet file."""
    connection.execute("CREATE OR REPLACE TEMP TABLE ours AS SELECT unnest(?::VARCHAR[]) AS number", [list(numbers)])
    return connection.execute(CITATIONS.format(source=str(source).replace("'", "''"))).fetchall()


def count_citations(pairs, numbers):
    """{patent pk: number of citing applications}, ignoring self-citations
    between publications of the same application."""
    citing = defaultdict(set)
    for application, cited in pairs:
        citing[numbers[cited]].add(application)
    applications = dict(Patent.objects.filter(pk__in=list(citing)).values_list("pk", "application_number"))
    return {pk: len(apps - {applications.get(pk)}) for pk, apps in citing.items()}


def store_citations(counts, patents):
    """Set cited_by of `patents` from `counts` (0 when not cited)."""
    changed = []
    for patent in patents.only("pk", "cited_by"):
        value = counts.get(patent.pk, 0)
        if patent.cited_by != value:
            patent.cited_by = value
            changed.append(patent)
    Patent.objects.bulk_update(changed, ["cited_by"], batch_size=1000)
    return len(changed)
