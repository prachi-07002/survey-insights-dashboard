"""Descriptive statistics for Likert-scale survey data.

Standard library only (statistics module). All functions take the list of
response dicts produced by csv_parser.load_survey.
"""

import statistics

LIKERT_SCALE = (1, 2, 3, 4, 5)


def mean(values):
    """Arithmetic mean of a non-empty sequence of numbers."""
    if not values:
        raise ValueError("mean() requires at least one value")
    return statistics.fmean(values)


def median(values):
    """Median of a non-empty sequence of numbers."""
    if not values:
        raise ValueError("median() requires at least one value")
    return statistics.median(values)


def std(values):
    """Sample standard deviation; 0.0 for a single value."""
    if not values:
        raise ValueError("std() requires at least one value")
    if len(values) == 1:
        return 0.0
    return statistics.stdev(values)


def distribution(values):
    """Return {score: count} for every score on the 1-5 Likert scale."""
    counts = {score: 0 for score in LIKERT_SCALE}
    for value in values:
        if value not in counts:
            raise ValueError(f"Value {value} is outside the 1-5 Likert scale")
        counts[value] += 1
    return counts


def summarize_item(rows, item):
    """Summary stats for one Likert item across all respondents.

    Returns dict with n, mean, median, std, and distribution {1..5: count}.
    """
    values = [row[item] for row in rows]
    return {
        "item": item,
        "n": len(values),
        "mean": mean(values),
        "median": median(values),
        "std": std(values),
        "distribution": distribution(values),
    }


def summarize_all(rows, items):
    """Return {item: summarize_item(...)} for every item in ``items``."""
    return {item: summarize_item(rows, item) for item in items}


def group_breakdown(rows, items):
    """Per-group summaries: {group: {item: summarize_item(...)}}."""
    groups = {}
    for row in rows:
        groups.setdefault(row["intervention_group"], []).append(row)
    return {
        group: {item: summarize_item(members, item) for item in items}
        for group, members in groups.items()
    }


def group_comparison(breakdown, item):
    """Compare groups on one item.

    Returns dict with per-group means, the highest/lowest group names,
    and the max-min mean difference (the headline group gap).
    """
    means = {group: summary[item]["mean"] for group, summary in breakdown.items()}
    highest = max(means, key=means.get)
    lowest = min(means, key=means.get)
    return {
        "item": item,
        "means": means,
        "highest_group": highest,
        "lowest_group": lowest,
        "difference": means[highest] - means[lowest],
    }


def compare_all_groups(breakdown, items):
    """Return {item: group_comparison(...)} for every item."""
    return {item: group_comparison(breakdown, item) for item in items}
