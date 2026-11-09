"""Tests for the open-ended keyword summary."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from keywords import keyword_counts, keyword_summary, tokenize, top_keywords


class TestTokenize(unittest.TestCase):
    def test_lowercases_and_strips_punctuation(self):
        self.assertEqual(tokenize("The Game, was FUN!"), ["game", "fun"])

    def test_drops_stopwords(self):
        self.assertEqual(tokenize("the project and the team"), ["project", "team"])

    def test_empty_text(self):
        self.assertEqual(tokenize(""), [])


class TestKeywordCounts(unittest.TestCase):
    def test_counts_across_texts(self):
        counts = keyword_counts(["game fun game", "project game"])
        self.assertEqual(counts["game"], 3)
        self.assertEqual(counts["fun"], 1)
        self.assertEqual(counts["project"], 1)

    def test_top_keywords_order(self):
        top = top_keywords(["game fun game", "project game"], n=2)
        self.assertEqual(top[0], ("game", 3))
        self.assertEqual(len(top), 2)

    def test_keyword_summary_overall_and_by_group(self):
        rows = [
            {"intervention_group": "A", "open_ended": "game fun game"},
            {"intervention_group": "A", "open_ended": "game project"},
            {"intervention_group": "B", "open_ended": "fairness math fairness"},
        ]
        summary = keyword_summary(rows, n=2)
        self.assertEqual(summary["overall"][0], ("game", 3))
        self.assertEqual(summary["by_group"]["A"][0], ("game", 3))
        self.assertEqual(summary["by_group"]["B"][0], ("fairness", 2))


if __name__ == "__main__":
    unittest.main()
