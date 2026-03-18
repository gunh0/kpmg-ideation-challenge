"""Match a topic against the patents already stored.

Collecting a new topic from the public data takes a while; matching it
against the patents of the other topics takes a second, so a new topic shows
what is already known right away and grows when its collection is done.
"""
import re

from django.db import transaction

from .models import Patent
from .store import delete_orphans, link


def matching_patents(pattern):
    """Keys of the stored patents whose title or abstract match `pattern`
    (a topic pattern, see keywords.topic_pattern)."""
    expression = re.compile(pattern)
    return [
        pk
        for pk, title, abstract in Patent.objects.values_list("pk", "title", "abstract").iterator(chunk_size=2000)
        if expression.search(f"{title} {abstract}".lower())
    ]


@transaction.atomic
def match_stored(topic):
    """Link `topic` to the stored patents its keywords match, replacing its
    links; returns how many there are."""
    pks = matching_patents(topic.pattern)
    link(topic, pks)
    delete_orphans()
    return len(pks)
