# INF601 - Advanced Programming in Python
# Kyle Horn
# Mini Project 4
"""datakit — a tiny data-processing toolkit.

YOUR JOB: implement every function below so it matches SPEC.md. Drive Claude Code
to help, but you must understand and be able to explain each line. Run the public
tests as you go:  pytest tests/public
"""
from __future__ import annotations

import csv  # standard-library CSV reader (gives us csv.DictReader)
import json  # standard-library JSON parser


def load_records(path):
    """Load a .csv or .json file into a list of dict rows.

    - .csv  -> use csv.DictReader (every value is a str)
    - .json -> a list of objects (returned as-is)
    - anything else -> raise ValueError
    """
    # str() lets callers pass a pathlib.Path too; lower() makes ".CSV" work like ".csv"
    name = str(path).lower()

    if name.endswith(".csv"):
        # newline="" is what the csv module docs require so quoted line breaks parse correctly.
        # utf-8-sig reads normal UTF-8 the same as utf-8, but also strips the hidden BOM bytes
        # Excel/Notepad may add at the start; otherwise the first key would be '﻿name'.
        with open(path, newline="", encoding="utf-8-sig") as f:
            # DictReader uses the header row as keys; each row becomes a dict of strings.
            # list() reads every row now, before the with-block closes the file.
            return list(csv.DictReader(f))

    if name.endswith(".json"):
        # utf-8-sig strips a BOM if present; plain json.load would fail with "Unexpected UTF-8 BOM"
        with open(path, encoding="utf-8-sig") as f:
            # The file holds a list of objects; json.load returns it with JSON types kept
            # (numbers stay int/float, not strings), so we return it as-is.
            return json.load(f)

    # Any other extension is not supported, per the spec
    raise ValueError(f"Unsupported file type (expected .csv or .json): {path}")


# The "/" makes `records` positional-only, so a data field that happens to be named
# "records" can still be used as a criterion: filter_records(rows, records="x").
# Without it, Python raises TypeError: "got multiple values for argument 'records'".
def filter_records(records, /, **criteria):
    """Return only the rows where, for every field=value pair passed as a keyword
    argument, str(row[field]) == str(value)."""
    # Keep a row only if ALL criteria match. all() of an empty criteria dict is True,
    # so calling with no criteria returns every row. Comparing as str() means a JSON
    # int 3 matches the criterion "3", and a CSV "3" matches the criterion 3.
    return [
        row
        for row in records
        if all(str(row[field]) == str(value) for field, value in criteria.items())
    ]


def summarize(records, group_by, value, agg, decimals=2):
    """Group rows by the `group_by` field and aggregate the numeric `value` field.

    agg is one of:
      "count" -> number of rows in the group (int)
      "sum"   -> sum of the values (float)
      "mean"  -> mean of the values, rounded to `decimals` places (float)
      "min"   -> smallest value (float)
      "max"   -> largest value (float)
    Return a dict mapping each group value to its aggregate. Unknown agg -> ValueError.
    """
    raise NotImplementedError


def top_n(records, key, n):
    """Return the `n` rows with the largest numeric `key`, sorted descending."""
    raise NotImplementedError


def to_report(summary):
    """Render a {key: value} dict as lines 'key: value', one per line, sorted
    ascending by key, joined with '\\n' (no trailing newline)."""
    raise NotImplementedError
