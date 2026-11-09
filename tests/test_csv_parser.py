"""Tests for CSV parsing."""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from csv_parser import SurveyParseError, group_counts, load_survey

HEADER = ("respondent_id,intervention_group,confidence,engagement,"
          "perceived_fairness,genai_usefulness,open_ended\n")


def _write_tmp(content):
    fd, path = tempfile.mkstemp(suffix=".csv")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(content)
    return path


class TestLoadSurvey(unittest.TestCase):
    def test_loads_valid_rows(self):
        path = _write_tmp(HEADER + "R001,GenAI in Project Management,4,5,3,5,Helpful.\n"
                                   "R002,PMaster Game,3,4,4,2,Fun game.\n")
        try:
            rows = load_survey(path)
        finally:
            os.unlink(path)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["respondent_id"], "R001")
        self.assertEqual(rows[0]["confidence"], 4)
        self.assertEqual(rows[0]["genai_usefulness"], 5)
        self.assertEqual(rows[1]["intervention_group"], "PMaster Game")
        self.assertEqual(rows[1]["open_ended"], "Fun game.")

    def test_loads_real_sample_file(self):
        here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        rows = load_survey(os.path.join(here, "data", "sample_survey.csv"))
        self.assertEqual(len(rows), 50)
        groups = group_counts(rows)
        self.assertEqual(groups["GenAI in Project Management"], 18)
        self.assertEqual(groups["Social Justice in Calculus"], 16)
        self.assertEqual(groups["PMaster Game"], 16)

    def test_rejects_likert_out_of_range(self):
        path = _write_tmp(HEADER + "R001,PMaster Game,6,4,4,2,Too high.\n")
        try:
            with self.assertRaises(SurveyParseError):
                load_survey(path)
        finally:
            os.unlink(path)

    def test_rejects_non_integer_likert(self):
        path = _write_tmp(HEADER + "R001,PMaster Game,four,4,4,2,Bad.\n")
        try:
            with self.assertRaises(SurveyParseError):
                load_survey(path)
        finally:
            os.unlink(path)

    def test_rejects_missing_column(self):
        path = _write_tmp("respondent_id,intervention_group,confidence\nR001,PMaster Game,4\n")
        try:
            with self.assertRaises(SurveyParseError):
                load_survey(path)
        finally:
            os.unlink(path)

    def test_group_counts(self):
        rows = [
            {"intervention_group": "A"}, {"intervention_group": "A"},
            {"intervention_group": "B"},
        ]
        self.assertEqual(group_counts(rows), {"A": 2, "B": 1})


if __name__ == "__main__":
    unittest.main()
