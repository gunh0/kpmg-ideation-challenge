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


def memory_bytes():
    """Memory available to this process: the container's limit if there is
    one, else the machine's."""
    try:
        with open("/sys/fs/cgroup/memory.max") as file:
            limit = file.read().strip()
        if limit.isdigit():
            return int(limit)
    except OSError:
        pass
    return os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")


def scan_threads(memory=None):
    """DuckDB reads a file's row groups with one thread each, and a remote
    scan waits on the network rather than the CPU, so many threads pay off.
    Each holds a decompressed column chunk, though — about 100 MB for the
    abstracts — so their number follows the memory: 8 per 2 GB, 8 to 64."""
    memory = memory if memory is not None else memory_bytes()
    return max(8, min(64, int(memory / 2**30 * 4)))


def connect():
    connection = duckdb.connect(config=duckdb_config())
    # Remote reads over a long scan meet the odd timeout; retry them. Order
    # does not matter to the collector, and keeping it costs memory.
    connection.execute(
        f"SET threads = {scan_threads()}; SET memory_limit = '{int(memory_bytes() * 0.6)}B'; "
        "SET preserve_insertion_order = false; SET http_retries = 8; SET http_timeout = 120000"
    )
    return connection


def read_shard(url, topics, since):
    connection = connect()
    try:
        return opendata.read_topics(opendata.direct_url(url), topics, since, connection)
    finally:
        connection.close()


def read_citations(url, numbers):
    connection = connect()
    try:
        return citations.citing_pairs(opendata.direct_url(url), numbers, connection)
    finally:
        connection.close()


def collect(topics=TOPICS, shards=None, workers=1, since=SINCE, revision=None, progress=None):
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
