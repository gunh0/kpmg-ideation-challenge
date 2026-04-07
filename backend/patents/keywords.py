"""Topics are described by keywords; collecting needs a regular expression.

Keywords are words and phrases typed in the dashboard, so they are validated
and escaped here instead of being used as expressions: a topic can only ever
match whole words, and nothing a user types reaches SQL or the regex engine
as syntax.
"""
import re

MAX_KEYWORDS = 12
MAX_LENGTH = 60
# letters and digits, with single spaces, hyphens or apostrophes inside
KEYWORD = re.compile(r"^[a-z0-9]+(?:[ '\-][a-z0-9]+)*$")


def parse_keywords(value):
    """"Drone, UAVs\\nunmanned  aerial" -> ["drone", "uavs", "unmanned aerial"].

    Accepts a string (comma or newline separated) or a list; raises
    ValueError with a message for the user when a keyword is not usable.
    """
    items = re.split(r"[,\n]", value) if isinstance(value, str) else list(value)
    keywords = []
    for item in items:
        keyword = " ".join(str(item).lower().split())
        if not keyword or keyword in keywords:
            continue
        if len(keyword) > MAX_LENGTH:
            raise ValueError(f"“{keyword[:20]}…” is longer than {MAX_LENGTH} characters.")
        if len(keyword) < 2 or not KEYWORD.match(keyword):
            raise ValueError(f"“{keyword}”: use letters and digits, with spaces, hyphens or apostrophes between words.")
        keywords.append(keyword)
    if not keywords:
        raise ValueError("Give at least one keyword.")
    if len(keywords) > MAX_KEYWORDS:
        raise ValueError(f"Use at most {MAX_KEYWORDS} keywords.")
    return keywords


def plural(word):
    """The last word may be plural: battery -> batter(?:y|ies), box -> box(?:es)?,
    drone -> drone(?:s)?."""
    if len(word) > 2 and word.endswith("y") and word[-2] not in "aeiou":
        return re.escape(word[:-1]) + "(?:y|ies)"
    if word.endswith(("s", "x", "z", "ch", "sh")):
        return re.escape(word) + "(?:es)?"
    return re.escape(word) + "(?:s)?"


def keyword_pattern(keyword):
    """"cyber attack" -> cyber[\\s-]+attack(?:s)?: words may be joined by spaces
    or hyphens, and the last one may be plural."""
    words = re.split(r"[ \-]", keyword)
    return r"[\s\-]+".join([re.escape(word) for word in words[:-1]] + [plural(words[-1])])


def topic_pattern(keywords):
    """One expression matching any of the keywords as whole words, in text
    that was lower-cased. Understood by Python and by DuckDB (RE2)."""
    return r"\b(?:" + "|".join(keyword_pattern(keyword) for keyword in keywords) + r")\b"
