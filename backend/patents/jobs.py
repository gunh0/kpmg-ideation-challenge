"""Collection jobs.

A topic that needs collecting is queued (status "queued"). A worker claims
all queued topics at once — a single UPDATE, so two processes never claim the
same topic — collects them in one pass over the public data and reports its
progress on them. The backend runs a worker thread when topics are added or
edited; the collector service runs one on its schedule.
"""
import logging
import threading
import uuid
from datetime import timedelta

from django.db import close_old_connections
from django.utils import timezone

from .collector import collect
from .models import Topic

logger = logging.getLogger(__name__)

# A job that has not reported progress for this long died with its process.
STALE_AFTER = timedelta(minutes=15)


def enqueue(topics):
    Topic.objects.filter(pk__in=[topic.pk for topic in topics]).update(
        status=Topic.QUEUED, progress=0, progress_total=0, error="", job="", status_changed_at=timezone.now()
    )


def requeue_stale():
    return Topic.objects.filter(status=Topic.COLLECTING, status_changed_at__lt=timezone.now() - STALE_AFTER).update(
        status=Topic.QUEUED, job=""
    )


def claim():
    """Take all queued topics for one job; returns them (empty if none)."""
    token = uuid.uuid4().hex
    Topic.objects.filter(status=Topic.QUEUED).update(
        status=Topic.COLLECTING, job=token, progress=0, progress_total=0, status_changed_at=timezone.now()
    )
    return list(Topic.objects.filter(job=token, status=Topic.COLLECTING))


def run(topics, **options):
    """Collect claimed `topics`; their state follows the job unless they were
    edited (queued again) or deleted meanwhile."""
    token = topics[0].job
    mine = Topic.objects.filter(job=token, status=Topic.COLLECTING)

    def progress(done, total):
        mine.update(progress=done, progress_total=total, status_changed_at=timezone.now())

    try:
        collect(topics, progress=progress, **options)
    except Exception as error:  # the job must not die silently: the topic shows why
        logger.exception("collecting %s failed", ", ".join(topic.name for topic in topics))
        mine.update(status=Topic.FAILED, error=str(error)[:500] or error.__class__.__name__, job="")
        return False
    mine.update(status=Topic.READY, job="", status_changed_at=timezone.now())
    return True


def process_queue(**options):
    """Collect queued topics until none is left; returns the number of jobs."""
    requeue_stale()
    jobs = 0
    while topics := claim():
        run(topics, **options)
        jobs += 1
    return jobs


_lock = threading.Lock()
_worker = None


def start_worker():
    """Process the queue in a thread of this process unless one is running;
    returns True when a thread was started."""
    global _worker
    with _lock:
        if _worker is not None:
            return False
        _worker = threading.Thread(target=_work, name="topic-collector", daemon=True)
        _worker.start()
        return True


def _work():
    global _worker
    try:
        while True:
            process_queue()
            with _lock:
                # A topic queued after the last claim is picked up here.
                if not Topic.objects.filter(status=Topic.QUEUED).exists():
                    _worker = None
                    return
    except Exception:
        logger.exception("the topic worker stopped")
        with _lock:
            _worker = None
    finally:
        close_old_connections()
