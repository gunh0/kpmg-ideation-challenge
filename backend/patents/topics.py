"""The technology fields a new instance follows.

A topic is a list of keywords (see keywords.py) matched as whole words in
the titles and abstracts of US publications. These are the defaults the
bundled snapshot is collected for; more can be added from the dashboard.
"""
from dataclasses import dataclass

from .keywords import topic_pattern


@dataclass(frozen=True)
class Topic:
    slug: str
    name: str
    description: str
    keywords: tuple

    @property
    def pattern(self):
        return topic_pattern(self.keywords)


TOPICS = (
    Topic(
        slug="drones",
        name="Drones",
        description="Unmanned aerial vehicles: flight control, delivery, inspection and counter-drone systems.",
        keywords=("drone", "uav", "unmanned aerial", "multicopter", "quadcopter"),
    ),
    Topic(
        slug="autonomous-driving",
        name="Autonomous driving",
        description="Self-driving vehicles: perception, planning, control and remote operation.",
        keywords=("autonomous driving", "autonomous vehicle", "self-driving", "driverless"),
    ),
    Topic(
        slug="cybersecurity",
        name="Cybersecurity",
        description="Detecting and stopping attacks: malware, intrusion detection, ransomware and phishing.",
        keywords=("malware", "intrusion detection", "ransomware", "phishing", "cyber attack", "cyberattack",
                  "cybersecurity"),
    ),
)

# US publications from this date on; older ones add volume but little to the trends.
SINCE = 20150101


def get_topic(slug):
    for topic in TOPICS:
        if topic.slug == slug:
            return topic
    raise KeyError(slug)
