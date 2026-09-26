from datetime import timedelta
from unittest import mock

from django.test import TestCase
from django.utils import timezone

from patents import jobs
from patents.models import Topic


def topic(name, **fields):
    return Topic.objects.create(name=name, slug=name.lower(), **fields)


class QueueTests(TestCase):
    def test_claim_takes_every_queued_topic_once(self):
        drones, locks = topic("Drones"), topic("Locks")
        topic("Ready")
        jobs.enqueue([drones, locks])

        claimed = jobs.claim()

        self.assertEqual(sorted(t.name for t in claimed), ["Drones", "Locks"])
        self.assertEqual({t.job for t in claimed}, {claimed[0].job})
        self.assertEqual(jobs.claim(), [])

    def test_run_reports_progress_and_readiness(self):
        drones = topic("Drones")
        jobs.enqueue([drones])
        seen = []

        def collect(topics, progress, **options):
            progress(1, 4)
            seen.append(Topic.objects.get(pk=drones.pk).progress)

        with mock.patch.object(jobs, "collect", side_effect=collect):
            self.assertEqual(jobs.process_queue(), 1)

        drones.refresh_from_db()
        self.assertEqual(seen, [1])
        self.assertEqual((drones.status, drones.progress_total, drones.job), (Topic.READY, 4, ""))

    def test_failures_are_kept_on_the_topic(self):
        drones = topic("Drones")
        jobs.enqueue([drones])

        with mock.patch.object(jobs, "collect", side_effect=OSError("HTTP 503")), self.assertLogs("patents.jobs"):
            jobs.process_queue()

        drones.refresh_from_db()
        self.assertEqual((drones.status, drones.error), (Topic.FAILED, "HTTP 503"))

    def test_an_edit_during_the_job_queues_the_topic_again(self):
        drones = topic("Drones")
        jobs.enqueue([drones])
        runs = []

        def collect(topics, progress, **options):
            runs.append(len(runs))
            if len(runs) == 1:
                jobs.enqueue(topics)  # edited while collecting

        with mock.patch.object(jobs, "collect", side_effect=collect):
            self.assertEqual(jobs.process_queue(), 2)

        self.assertEqual(Topic.objects.get(pk=drones.pk).status, Topic.READY)

    def test_jobs_of_dead_processes_are_queued_again(self):
        drones = topic("Drones", status=Topic.COLLECTING, job="old",
                       status_changed_at=timezone.now() - timedelta(hours=1))
        topic("Busy", status=Topic.COLLECTING, job="live", status_changed_at=timezone.now())

        self.assertEqual(jobs.requeue_stale(), 1)
        drones.refresh_from_db()
        self.assertEqual(drones.status, Topic.QUEUED)


class WorkerTests(TestCase):
    def test_the_web_process_does_not_collect_when_turned_off(self):
        with self.settings(PATENTS_COLLECT_IN_BACKEND=False), mock.patch("threading.Thread") as thread:
            self.assertFalse(jobs.start_worker())
        thread.assert_not_called()
