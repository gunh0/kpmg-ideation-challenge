"""US patents from Google Patents Public Data, read without an account.

Google publishes every publication it indexes as the BigQuery table
patents-public-data.patents.publications (CC BY 4.0). A copy of that table is
kept as Parquet files on Hugging Face, which anyone can read over HTTPS. DuckDB
reads such files remotely and only fetches the columns and row groups a query
needs, so matching a topic against all titles does not download the full text
of every patent.
"""
import json
import urllib.error
import urllib.request

import duckdb

REPOSITORY = "labofsahil/patents-publications-dataset"
API = f"https://huggingface.co/api/datasets/{REPOSITORY}"
FILES = f"https://huggingface.co/datasets/{REPOSITORY}/resolve"
LICENSE = "CC BY 4.0, Google Patents Public Data by IFI CLAIMS Patent Services and Google"

COLUMNS = """
    publication_number, application_number, kind_code, family_id,
    title_localized[1].text AS title, abstract_localized[1].text AS abstract,
    priority_date, filing_date, publication_date, grant_date,
    assignee, assignee_harmonized[1].country_code AS assignee_country, inventor
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


class _KeepRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def direct_url(url, timeout=30):
    """The CDN address behind a Hugging Face file URL.

    Every request to /resolve/ counts against a rate limit of a few thousand
    per five minutes, and DuckDB sends one range request per column chunk.
    Asking once where the file lives and reading from there avoids the limit.
    """
    if not url.startswith(("https://", "http://")):
        return url  # a local file
    request = urllib.request.Request(url, method="HEAD")
    try:
        urllib.request.build_opener(_KeepRedirect).open(request, timeout=timeout)
    except urllib.error.HTTPError as redirect:
        if 300 <= redirect.code < 400 and redirect.headers.get("Location"):
            return redirect.headers["Location"]
        raise
    return url


def topic_query(source, topics, since):
    """SQL and parameters that return the US publications of `source` whose
    title or abstract matches a topic, with the slugs of all matching topics
    in `topics`. Patterns and slugs are passed as parameters."""
    cases = ", ".join("CASE WHEN regexp_matches(text, ?) THEN ? END" for _ in topics)
    parameters = [value for topic in topics for value in (topic.pattern, topic.slug)]
    source = str(source).replace("'", "''")
    sql = f"""
        SELECT * EXCLUDE (text) FROM (
            SELECT list_filter([{cases}], slug -> slug IS NOT NULL) AS topics, *
            FROM (SELECT {COLUMNS}, lower(coalesce(title_localized[1].text, '') || ' '
                         || coalesce(abstract_localized[1].text, '')) AS text
                  FROM read_parquet('{source}')
                  WHERE country_code = 'US' AND publication_date >= ?)
        )
        WHERE len(topics) > 0
    """
    return sql, parameters + [int(since)]


def read_topics(source, topics, since, connection=None):
    """Matching publications of one Parquet file (a path or a URL) as dicts."""
    connection = connection or duckdb.connect()
    sql, parameters = topic_query(source, topics, since)
    result = connection.execute(sql, parameters)
    names = [column[0] for column in result.description]
    return [dict(zip(names, row)) for row in result.fetchall()]
