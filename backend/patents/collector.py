"""Collect the topics from the public data and store them."""
import logging
from concurrent.futures import ThreadPoolExecutor

import duckdb

from . import opendata
from .records import merge
from .store import store_topic
from .topics import SINCE, TOPICS

logger = logging.getLogger(__name__)


def read_shard(url, topics, since):
    connection = duckdb.connect()
    # DuckDB fetches row groups with one thread each, and a remote scan waits
    # on the network, not the CPU: with as many threads as a file has row
    # groups (about 50) one file takes seconds instead of minutes on 2 cores.
    # Remote reads over a long scan meet the odd timeout; retry them.
    connection.execute("SET threads = 64; SET http_retries = 8; SET http_timeout = 120000")
    try:
        return opendata.read_topics(opendata.direct_url(url), topics, since, connection)
    finally:
        connection.close()


def collect(topics=TOPICS, shards=None, workers=2, since=SINCE, revision=None):
    """Scan the Parquet files for `topics` and replace each topic's patents.

    `shards` limits the scan to some files (indexes), for trying things out;
    the stored topics then only hold what those files contain.
    """
    revision = revision or opendata.source_revision()
    urls = opendata.shard_urls(revision)
    if shards is not None:
        urls = [urls[i] for i in shards]
    logger.info("collecting %s from %d files of revision %s", ", ".join(t.slug for t in topics), len(urls), revision[:12])

    rows = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for done, batch in enumerate(pool.map(lambda url: read_shard(url, topics, since), urls), start=1):
            rows.extend(batch)
            logger.info("file %d/%d: %d matches", done, len(urls), len(batch))

    merged = merge(rows)
    return [store_topic(topic, merged.get(topic.slug, []), revision) for topic in topics]

