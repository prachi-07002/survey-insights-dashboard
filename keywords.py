"""Open-ended response keyword summary.

Simple tokenization + frequency counting only — no NLP dependencies.
Lowercases, strips punctuation, drops a small English stopword list, and
counts the remaining words. Also supports per-group keyword breakdowns.
"""

import re
from collections import Counter

STOPWORDS = frozenset(
    """
    a an the and or but if then else when while of to in on for with by at from
    as is are was were be been being am i me my we our you your he she it its
    they them their this that these those there here what which who whom how
    why not no yes do does did done have has had will would can could should
    may might must very just so too also more most other some any all each
    about into over under after before between through during without within
    upon per via etc
    """.split()
)

_TOKEN_RE = re.compile(r"[a-z]+(?:'[a-z]+)?")


def tokenize(text):
    """Lowercase a string and split it into words, dropping stopwords."""
    words = _TOKEN_RE.findall(text.lower())
    return [w for w in words if w not in STOPWORDS]


def keyword_counts(texts):
    """Return a Counter of non-stopword tokens across a list of texts."""
    counts = Counter()
    for text in texts:
        counts.update(tokenize(text))
    return counts


def top_keywords(texts, n=10):
    """Return the n most common keywords as [(word, count), ...]."""
    return keyword_counts(texts).most_common(n)


def keyword_summary(rows, n=10):
    """Overall keyword summary plus a per-group top-n list.

    Returns {"overall": [(word, count), ...],
             "by_group": {group: [(word, count), ...]}}.
    """
    overall = top_keywords([r["open_ended"] for r in rows], n=n)
    groups = {}
    for row in rows:
        groups.setdefault(row["intervention_group"], []).append(row["open_ended"])
    by_group = {group: top_keywords(texts, n=n) for group, texts in groups.items()}
    return {"overall": overall, "by_group": by_group}
