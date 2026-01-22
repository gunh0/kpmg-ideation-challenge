"""The technology fields the dashboard follows.

Each topic is a regular expression matched against the lower-cased English
title of US publications. Titles are short and specific, so a title match
keeps the lists on topic without the noise of abstract matches.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Topic:
    slug: str
    name: str
    description: str
    pattern: str


TOPICS = (
    Topic(
        slug="drones",
        name="Drones",
        description="Unmanned aerial vehicles: flight control, delivery, inspection and counter-drone systems.",
        pattern=r"\b(drones?|unmanned aerial|uavs?|multicopter|quadcopter)\b",
    ),
    Topic(
        slug="autonomous-driving",
        name="Autonomous driving",
        description="Self-driving vehicles: perception, planning, control and remote operation.",
        pattern=r"\b(autonomous (driving|vehicles?)|self-driving|driverless)\b",
    ),
    Topic(
        slug="cybersecurity",
        name="Cybersecurity",
        description="Detecting and stopping attacks: malware, intrusion detection, ransomware and phishing.",
        pattern=r"\b(malware|intrusion detection|ransomware|phishing|cyber ?attacks?|cybersecurity)\b",
    ),
)

# US publications from this date on; older ones add volume but little to the trends.
SINCE = 20150101


def get_topic(slug):
    for topic in TOPICS:
        if topic.slug == slug:
            return topic
    raise KeyError(slug)
