"""CSV parsing for the survey-insights-dashboard.

Reads the fictional sample survey CSV using only the Python standard
library. Likert responses are validated to be integers in the range 1-5.
"""

import csv

LIKERT_ITEMS = ["confidence", "engagement", "perceived_fairness", "genai_usefulness"]

REQUIRED_COLUMNS = ["respondent_id", "intervention_group"] + LIKERT_ITEMS + ["open_ended"]


class SurveyParseError(ValueError):
    """Raised when the survey CSV is malformed or contains invalid values."""


def load_survey(path):
    """Load a survey CSV and return a list of response dicts.

    Each dict has keys: respondent_id (str), intervention_group (str),
    one int per Likert item in LIKERT_ITEMS, and open_ended (str).
    Rows with a missing/invalid Likert value raise SurveyParseError.
    """
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise SurveyParseError("CSV file is empty")
        missing = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
        if missing:
            raise SurveyParseError(f"Missing required columns: {missing}")

        rows = []
        for line_no, raw in enumerate(reader, start=2):
            row = {
                "respondent_id": (raw["respondent_id"] or "").strip(),
                "intervention_group": (raw["intervention_group"] or "").strip(),
                "open_ended": (raw["open_ended"] or "").strip(),
            }
            if not row["respondent_id"]:
                raise SurveyParseError(f"Line {line_no}: missing respondent_id")
            if not row["intervention_group"]:
                raise SurveyParseError(f"Line {line_no}: missing intervention_group")
            for item in LIKERT_ITEMS:
                value = (raw[item] or "").strip()
                try:
                    score = int(value)
                except ValueError:
                    raise SurveyParseError(
                        f"Line {line_no}: {item}={value!r} is not an integer"
                    ) from None
                if not 1 <= score <= 5:
                    raise SurveyParseError(
                        f"Line {line_no}: {item}={score} is outside the 1-5 Likert range"
                    )
                row[item] = score
            rows.append(row)
    return rows


def group_counts(rows):
    """Return {intervention_group: number of respondents}."""
    counts = {}
    for row in rows:
        counts[row["intervention_group"]] = counts.get(row["intervention_group"], 0) + 1
    return counts
