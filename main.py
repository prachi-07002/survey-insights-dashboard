"""Demo entry point: load the sample survey, compute stats, and
generate the static HTML report.

Usage:
    python main.py [--csv data/sample_survey.csv] [--out report.html]
"""

import argparse
import os
import sys

from csv_parser import LIKERT_ITEMS, group_counts, load_survey
from keywords import keyword_summary
from report import generate_report
from stats import compare_all_groups, group_breakdown, summarize_all

ITEM_LABELS = {
    "confidence": "Confidence",
    "engagement": "Engagement",
    "perceived_fairness": "Perceived fairness",
    "genai_usefulness": "GenAI usefulness",
}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Survey insights demo")
    here = os.path.dirname(os.path.abspath(__file__))
    parser.add_argument("--csv", default=os.path.join(here, "data", "sample_survey.csv"))
    parser.add_argument("--out", default=os.path.join(here, "report.html"))
    args = parser.parse_args(argv)

    rows = load_survey(args.csv)
    overall = summarize_all(rows, LIKERT_ITEMS)
    breakdown = group_breakdown(rows, LIKERT_ITEMS)
    comparisons = compare_all_groups(breakdown, LIKERT_ITEMS)
    keywords = keyword_summary(rows, n=10)

    print(f"Loaded {len(rows)} responses from {args.csv}")
    print(f"Groups: {group_counts(rows)}")
    print()
    print("Overall means (1-5 Likert scale):")
    for item, s in overall.items():
        print(f"  {ITEM_LABELS[item]:<20} mean={s['mean']:.2f}  "
              f"median={s['median']:.1f}  std={s['std']:.2f}")
    print()
    print("Largest group differences (max group mean - min group mean):")
    for item, comp in comparisons.items():
        print(f"  {ITEM_LABELS[item]:<20} gap={comp['difference']:.2f}  "
              f"({comp['highest_group']} vs {comp['lowest_group']})")
    print()
    print("Top open-ended keywords:")
    for word, count in keywords["overall"]:
        print(f"  {word}: {count}")

    generate_report(rows, overall, breakdown, comparisons, keywords, args.out)
    print(f"\nReport written to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
