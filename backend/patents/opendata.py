"""US patents from Google Patents Public Data, read without an account.

Google publishes every publication it indexes as the BigQuery table
patents-public-data.patents.publications (CC BY 4.0). A copy of that table is
kept as Parquet files on Hugging Face, which anyone can read over HTTPS. DuckDB
reads such files remotely and only fetches the columns and row groups a query
needs, so matching a topic against all titles does not download the full text
of every patent.
"""
import json
import urllib.request

import duckdb

REPOSITORY = "labofsahil/patents-publications-dataset"
API = f"https://huggingface.co/api/datasets/{REPOSITORY}"
FILES = f"https://huggingface.co/datasets/{REPOSITORY}/resolve"
LICENSE = "CC BY 4.0, Google Patents Public Data by IFI CLAIMS Patent Services and Google"

COLUMNS = """
    publication_number, application_number, kind_code, family_id,
    title_localized[1].text AS title,
    priority_date, filing_date, publication_date, grant_date,
    assignee, inventor
"""


def get_json(url, timeout=30):
    with urllib.request.urlopen(url, timeout=timeout) as response:
        return json.load(response)


def source_revision():
    """The commit of the copy on Hugging Face; it changes when the data is refreshed."""
    return get_json(API)["sha"]


def shard_urls(revision):
    """URLs of the Parquet files, pinned to one revision so a collection reads
    a consistent snapshot even if the copy is updated meanwhile."""
    tree = get_json(f"{API}/tree/{revision}")
    names = sorted(item["path"] for item in tree if item["path"].endswith(".parquet"))
    return [f"{FILES}/{revision}/{name}" for name in names]


def topic_query(source, topics, since):
    """SQL that returns the US publications of `source` whose title matches a
    topic, with the slug of the first matching topic in `topic`."""
    cases = " ".join(f"WHEN regexp_matches(lower(title), '{topic.pattern}') THEN '{topic.slug}'" for topic in topics)
    return f"""
        SELECT * FROM (
            SELECT CASE {cases} END AS topic, *
            FROM (SELECT {COLUMNS} FROM read_parquet('{source}')
                  WHERE country_code = 'US' AND publication_date >= {int(since)})
        )
        WHERE topic IS NOT NULL
    """


def read_topics(source, topics, since, connection=None):
    """Matching publications of one Parquet file (a path or a URL) as dicts."""
    connection = connection or duckdb.connect()
    result = connection.execute(topic_query(source, topics, since))
    names = [column[0] for column in result.description]
    return [dict(zip(names, row)) for row in result.fetchall()]
