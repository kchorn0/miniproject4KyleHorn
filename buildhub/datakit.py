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
import statistics  # standard-library math helpers (we use statistics.mean)

# The aggregations summarize() accepts; anything else is a ValueError
AGGREGATES = {"count", "sum", "mean", "min", "max"}


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
    # Check agg FIRST, so a bad agg raises ValueError even if records is empty
    if agg not in AGGREGATES:
        raise ValueError(f"Unknown agg {agg!r}; expected one of {sorted(AGGREGATES)}")

    # groups maps each group value to the list of that group's rows,
    # e.g. {"red": [Ana_row, Cy_row, Eve_row], "blue": [Ben_row, Dee_row]}
    groups = {}
    for row in records:
        # setdefault creates an empty list the first time we see a group, then we append to it
        groups.setdefault(row[group_by], []).append(row)

    # Build the result one group at a time; dicts keep insertion order,
    # so groups appear in the order they first show up in the data
    result = {}
    for group, rows in groups.items():
        if agg == "count":
            # count only needs the number of rows (an int), so we never touch the value field
            result[group] = len(rows)
            continue
        # Every other agg is math, so turn each value into a float first
        # (CSV values arrive as strings like "10"; JSON values may be ints)
        numbers = [float(row[value]) for row in rows]
        if agg == "sum":
            # sum() of floats is already a float, e.g. 10.0 + 30.0 + 55.0 = 95.0
            result[group] = sum(numbers)
        elif agg == "mean":
            # statistics.mean gives the average; round() trims it to `decimals` places
            result[group] = round(statistics.mean(numbers), decimals)
        elif agg == "min":
            # smallest float in the group
            result[group] = min(numbers)
        else:  # agg == "max" (the only option left after the check at the top)
            # largest float in the group
            result[group] = max(numbers)
    return result


def top_n(records, key, n):
    """Return the `n` rows with the largest numeric `key`, sorted descending."""
    raise NotImplementedError


def to_report(summary):
    """Render a {key: value} dict as lines 'key: value', one per line, sorted
    ascending by key, joined with '\\n' (no trailing newline)."""
    raise NotImplementedError
