"""Tests for Likert statistics: mean, median, std, distribution,
group breakdowns, and group comparisons on known small data."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stats import (
    compare_all_groups,
    distribution,
    group_breakdown,
    group_comparison,
    mean,
    median,
    std,
    summarize_item,
)

ITEMS = ["confidence", "engagement", "perceived_fairness", "genai_usefulness"]

SMALL = [
    {"intervention_group": "A", "confidence": 1, "engagement": 2,
     "perceived_fairness": 3, "genai_usefulness": 4},
    {"intervention_group": "A", "confidence": 3, "engagement": 4,
     "perceived_fairness": 5, "genai_usefulness": 2},
    {"intervention_group": "B", "confidence": 5, "engagement": 5,
     "perceived_fairness": 5, "genai_usefulness": 5},
]


class TestBasicStats(unittest.TestCase):
    def test_mean_known_values(self):
        self.assertAlmostEqual(mean([1, 2, 3, 4, 5]), 3.0)
        self.assertAlmostEqual(mean([4, 4, 4]), 4.0)
        self.assertAlmostEqual(mean([1, 5]), 3.0)

    def test_mean_requires_values(self):
        with self.assertRaises(ValueError):
            mean([])

    def test_median_odd_and_even(self):
        self.assertEqual(median([1, 2, 3]), 2)
        self.assertEqual(median([1, 2, 3, 4]), 2.5)

    def test_std_known_values(self):
        # Sample std of [1,2,3,4,5] is sqrt(2.5)
        self.assertAlmostEqual(std([1, 2, 3, 4, 5]), 2.5 ** 0.5)
        self.assertEqual(std([3, 3, 3]), 0.0)
        self.assertEqual(std([5]), 0.0)

    def test_distribution_counts_all_scores(self):
        self.assertEqual(distribution([1, 2, 2, 5, 5, 5]),
                         {1: 1, 2: 2, 3: 0, 4: 0, 5: 3})

    def test_distribution_rejects_out_of_range(self):
        with self.assertRaises(ValueError):
            distribution([0, 3])

    def test_summarize_item(self):
        s = summarize_item(SMALL, "confidence")
        self.assertEqual(s["n"], 3)
        self.assertAlmostEqual(s["mean"], 3.0)
        self.assertEqual(s["median"], 3)
        self.assertEqual(s["distribution"], {1: 1, 2: 0, 3: 1, 4: 0, 5: 1})


class TestGroupStats(unittest.TestCase):
    def test_group_breakdown(self):
        bd = group_breakdown(SMALL, ITEMS)
        self.assertAlmostEqual(bd["A"]["confidence"]["mean"], 2.0)
        self.assertAlmostEqual(bd["B"]["confidence"]["mean"], 5.0)
        self.assertEqual(bd["A"]["engagement"]["n"], 2)
        self.assertEqual(bd["B"]["engagement"]["n"], 1)

    def test_group_comparison(self):
        bd = group_breakdown(SMALL, ITEMS)
        comp = group_comparison(bd, "confidence")
        self.assertEqual(comp["highest_group"], "B")
        self.assertEqual(comp["lowest_group"], "A")
        self.assertAlmostEqual(comp["difference"], 3.0)
        self.assertAlmostEqual(comp["means"]["A"], 2.0)
        self.assertAlmostEqual(comp["means"]["B"], 5.0)

    def test_compare_all_groups(self):
        bd = group_breakdown(SMALL, ITEMS)
        comps = compare_all_groups(bd, ITEMS)
        self.assertEqual(set(comps), set(ITEMS))
        self.assertAlmostEqual(comps["engagement"]["difference"], 2.0)


if __name__ == "__main__":
    unittest.main()
