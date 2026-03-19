"""Collect the topics from the public data and store them."""
import logging
import os
import tempfile
from concurrent.futures import ThreadPoolExecutor

import duckdb

from . import citations, opendata
from .models import Patent, Topic
from .records import merge
from .store import store_topics
from .topics import SINCE, TOPICS

logger = logging.getLogger(__name__)


def duckdb_config():
    """DuckDB keeps extensions and secrets under the home directory, which the
    app user of the image does not have. The image installs the httpfs
    extension at build time (DUCKDB_EXTENSION_DIRECTORY); /tmp could not hold
    it, as Docker mounts it without exec permission."""
    config = {"secret_directory": os.path.join(tempfile.gettempdir(), "duckdb-secrets")}
    if os.environ.get("DUCKDB_EXTENSION_DIRECTORY"):
        config["extension_directory"] = os.environ["DUCKDB_EXTENSION_DIRECTORY"]
        config["autoinstall_known_extensions"] = False
    return config


def read_shard(url, topics, since):
    connection = duckdb.connect(config=duckdb_config())
    # DuckDB fetches row groups with one thread each, and a remote scan waits
    # on the network, not the CPU: with as many threads as a file has row
    # groups (about 50) one file takes seconds instead of minutes on 2 cores.
    # Remote reads over a long scan meet the odd timeout; retry them.
    connection.execute("SET threads = 64; SET http_retries = 8; SET http_timeout = 120000")
    try:
        return opendata.read_topics(opendata.direct_url(url), topics, since, connection)
    finally:
        connection.close()


def read_citations(url, numbers):
    connection = duckdb.connect(config=duckdb_config())
    connection.execute("SET threads = 64; SET http_retries = 8; SET http_timeout = 120000")
    try:
        return citations.citing_pairs(opendata.direct_url(url), numbers, connection)
    finally:
        connection.close()


def collect(topics=TOPICS, shards=None, workers=2, since=SINCE, revision=None, progress=None):
    """Scan the Parquet files for `topics` and replace each topic's patents.

    `topics` are topics.Topic defaults or stored Topic rows. `shards` limits
    the scan to some files (indexes), for trying things out; the stored topics
    then only hold what those files contain. `progress(done, total)` is called
    after each file of the two passes.
    """
    progress = progress or (lambda done, total: None)
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
            progress(done, 2 * len(urls))
    stored = store_topics(topics, merge(rows), revision)

    # A second pass: who cites the patents of these topics.
    patents = Patent.objects.filter(topics__in=stored).distinct()
    numbers = citations.ours(patents)
    pairs = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for done, batch in enumerate(pool.map(lambda url: read_citations(url, numbers), urls), start=1):
            pairs.extend(batch)
            logger.info("citations %d/%d: %d", done, len(urls), len(batch))
            progress(len(urls) + done, 2 * len(urls))
    citations.store_citations(citations.count_citations(pairs, numbers), patents)
    return stored


def up_to_date(topics, revision):
    """True when every topic was collected from `revision` already."""
    stored = dict(Topic.objects.filter(slug__in=[t.slug for t in topics]).values_list("slug", "source_revision"))
    return all(stored.get(topic.slug) == revision for topic in topics)
