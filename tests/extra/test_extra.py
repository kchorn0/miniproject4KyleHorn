# INF601 - Advanced Programming in Python
# Kyle Horn
# Mini Project 4
"""Our own extra tests, beyond the instructor's public ones.

Run them with:  pytest tests/extra      (or  pytest tests  to run everything)
They try many values of `decimals` and `n` because the hidden grader varies those.
"""
import os  # for building file paths that work on Windows and macOS/Linux

import pytest  # the test framework (gives us pytest.raises and parametrize)

from buildhub import datakit as dk  # the five functions we are testing
from buildhub.__main__ import main  # the CLI entry point, so we can call it like a function

# Paths to the instructor's sample files (we only READ them, never change them)
FIX = os.path.join(os.path.dirname(__file__), "..", "..", "fixtures")
CSV = os.path.join(FIX, "sample.csv")  # values are strings, e.g. "10"
JSON = os.path.join(FIX, "sample.json")  # values keep types, e.g. 10


def names(rows):
    """Helper: turn a list of rows into just their names, e.g. ["Eve", "Dee"]."""
    return [row["name"] for row in rows]  # pick the "name" field from each row


# ---------------------------------------------------------------- load_records

def test_csv_values_are_strings():
    rows = dk.load_records(CSV)  # read the CSV file
    assert rows[0]["points"] == "10"  # CSV gives text, not the number 10


def test_json_keeps_number_types():
    rows = dk.load_records(JSON)  # read the JSON file
    assert rows[0]["points"] == 10  # JSON keeps the real number 10


def test_unknown_extension_raises_value_error():
    with pytest.raises(ValueError):  # the test passes only if ValueError happens
        dk.load_records("data.txt")  # .txt is not .csv or .json


def test_uppercase_extension_works(tmp_path):
    path = tmp_path / "DATA.CSV"  # tmp_path is a temporary folder pytest makes for us
    path.write_text("name,points\nAna,10\n")  # write a tiny CSV file
    assert dk.load_records(path) == [{"name": "Ana", "points": "10"}]  # .CSV still loads


def test_csv_with_bom(tmp_path):
    path = tmp_path / "bom.csv"  # a temporary file
    path.write_text("name,points\nAna,10\n", encoding="utf-8-sig")  # save WITH a BOM, like Excel
    assert dk.load_records(path)[0]["name"] == "Ana"  # key is "name", not "﻿name"


def test_json_with_bom(tmp_path):
    path = tmp_path / "bom.json"  # a temporary file
    path.write_text('[{"name": "Ana"}]', encoding="utf-8-sig")  # save WITH a BOM
    assert dk.load_records(path) == [{"name": "Ana"}]  # loads without a JSON error


# -------------------------------------------------------------- filter_records

def test_filter_two_criteria():
    rows = dk.load_records(CSV)  # load the sample data
    assert names(dk.filter_records(rows, team="red", level="1")) == ["Eve"]  # red AND level 1


def test_filter_no_criteria_returns_all():
    rows = dk.load_records(CSV)  # load the sample data
    assert dk.filter_records(rows) == rows  # no conditions -> every row comes back


def test_filter_no_match_returns_empty():
    rows = dk.load_records(CSV)  # load the sample data
    assert dk.filter_records(rows, team="green") == []  # nobody is on team green


def test_filter_json_number_matches_string():
    rows = dk.load_records(JSON)  # JSON level is the number 1
    assert names(dk.filter_records(rows, level="1")) == ["Ben", "Eve"]  # str(1) == "1"


def test_filter_field_named_records():
    rows = [{"records": "x"}, {"records": "y"}]  # a column literally named "records"
    assert dk.filter_records(rows, records="x") == [{"records": "x"}]  # no TypeError


# ------------------------------------------------------------------- summarize

# parametrize runs this test once per (decimals, red, blue) line: 5 tests in one
@pytest.mark.parametrize("decimals, expected_red, expected_blue", [
    (0, 32.0, 32.0),  # 0 places: Python's round() sends an exact .5 to the EVEN number (32.5 -> 32)
    (1, 31.7, 32.5),  # the spec's own example
    (2, 31.67, 32.5),  # the default
    (3, 31.667, 32.5),
    (4, 31.6667, 32.5),
])
def test_mean_rounds_to_decimals(decimals, expected_red, expected_blue):
    rows = dk.load_records(CSV)  # red: 10, 30, 55 -> 31.666... ; blue: 25, 40 -> 32.5
    result = dk.summarize(rows, "team", "points", "mean", decimals=decimals)  # average per team
    assert result["red"] == expected_red  # rounded to the right number of places
    assert result["blue"] == expected_blue  # same for blue


def test_mean_default_is_two_decimals():
    rows = dk.load_records(CSV)  # load the sample data
    assert dk.summarize(rows, "team", "points", "mean")["red"] == 31.67  # no decimals given -> 2


def test_min_and_max_are_floats():
    rows = dk.load_records(CSV)  # load the sample data
    assert dk.summarize(rows, "team", "points", "min") == {"red": 10.0, "blue": 25.0}  # smallest
    assert dk.summarize(rows, "team", "points", "max") == {"red": 55.0, "blue": 40.0}  # largest
    assert isinstance(dk.summarize(rows, "team", "points", "min")["red"], float)  # float, not str


def test_count_is_int_and_sum_is_float():
    rows = dk.load_records(CSV)  # load the sample data
    assert isinstance(dk.summarize(rows, "team", "points", "count")["red"], int)  # count -> int
    assert isinstance(dk.summarize(rows, "team", "points", "sum")["red"], float)  # sum -> float


def test_summarize_json_matches_csv():
    csv_sum = dk.summarize(dk.load_records(CSV), "team", "points", "sum")  # sum from CSV strings
    json_sum = dk.summarize(dk.load_records(JSON), "team", "points", "sum")  # sum from JSON numbers
    assert csv_sum == json_sum == {"red": 95.0, "blue": 65.0}  # same answer either way


def test_bad_agg_raises_value_error():
    rows = dk.load_records(CSV)  # load the sample data
    with pytest.raises(ValueError):  # passes only if ValueError happens
        dk.summarize(rows, "team", "points", "median")  # "median" is not allowed


def test_bad_agg_raises_even_when_empty():
    with pytest.raises(ValueError):  # passes only if ValueError happens
        dk.summarize([], "team", "points", "avg")  # no rows, but the agg is still checked


# ----------------------------------------------------------------------- top_n

# Runs once per n; each line is (n, the names we expect, in order)
@pytest.mark.parametrize("n, expected", [
    (0, []),  # ask for nothing, get nothing
    (1, ["Eve"]),  # Eve has the most points (55)
    (3, ["Eve", "Dee", "Cy"]),
    (5, ["Eve", "Dee", "Cy", "Ben", "Ana"]),  # every row, highest to lowest
    (10, ["Eve", "Dee", "Cy", "Ben", "Ana"]),  # more than exist -> just all of them
])
def test_top_n_various_n(n, expected):
    rows = dk.load_records(CSV)  # load the sample data
    assert names(dk.top_n(rows, "points", n)) == expected  # right rows in the right order


def test_top_n_sorts_as_numbers_not_text():
    rows = [{"name": "a", "p": "9"}, {"name": "b", "p": "100"}, {"name": "c", "p": "55"}]
    # As text, "9" would come first; as numbers, 100 > 55 > 9
    assert names(dk.top_n(rows, "p", 3)) == ["b", "c", "a"]


def test_top_n_ties_keep_file_order():
    rows = [{"name": "a", "p": "5"}, {"name": "b", "p": "7"}, {"name": "c", "p": "5"}]
    assert names(dk.top_n(rows, "p", 3)) == ["b", "a", "c"]  # a stays before c (both are 5)


def test_top_n_does_not_change_original():
    rows = dk.load_records(CSV)  # load the sample data
    dk.top_n(rows, "points", 2)  # run top_n (we ignore the result here)
    assert names(rows)[0] == "Ana"  # the original list is still in file order


# ------------------------------------------------------------------- to_report

def test_report_sorted_with_no_trailing_newline():
    report = dk.to_report({"red": 3, "blue": 2})  # unsorted input
    assert report == "blue: 2\nred: 3"  # sorted A->Z, joined by "\n"
    assert not report.endswith("\n")  # nothing extra at the end


def test_report_empty_dict():
    assert dk.to_report({}) == ""  # no entries -> empty string


# ------------------------------------------------------------------------- CLI

def test_cli_summarize(capsys):
    # capsys captures what main() prints so we can check it
    code = main(["summarize", CSV, "--group-by", "team", "--value", "points",
                 "--agg", "mean", "--decimals", "1"])  # same as typing it in the terminal
    assert code == 0  # 0 means success
    assert capsys.readouterr().out == "blue: 32.5\nred: 31.7\n"  # print() adds the final "\n"


def test_cli_summarize_default_decimals(capsys):
    main(["summarize", CSV, "--group-by", "team", "--value", "points", "--agg", "mean"])
    assert "red: 31.67" in capsys.readouterr().out  # no --decimals -> 2 places


def test_cli_top(capsys):
    code = main(["top", CSV, "--key", "points", "--n", "2"])  # top 2 rows
    lines = capsys.readouterr().out.splitlines()  # split the printed text into lines
    assert code == 0  # success
    assert len(lines) == 2  # one line per row
    assert "'Eve'" in lines[0] and "'Dee'" in lines[1]  # highest first


def test_cli_bad_file_gives_short_error(capsys):
    code = main(["top", "data.txt", "--key", "points", "--n", "2"])  # unsupported file type
    err = capsys.readouterr().err  # error text goes to stderr
    assert code == 1  # 1 means failure
    assert err.startswith("error:")  # one short line, not a traceback
