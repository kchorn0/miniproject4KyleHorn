# INF601 - Advanced Programming in Python
# Kyle Horn
# Mini Project 4
"""Our own extra tests, beyond the instructor's public ones.

Run them with:  pytest tests/extra      (or  pytest tests  to run everything)

Why these exist: the instructor's hidden grader checks MORE than the 7 public tests,
and it changes `decimals` and `n` for each student. These tests try many values and
tricky cases so we find bugs before the grader does.

Every test below has a short note:
  WHY   - why this test matters
  CHECK - what it checks
  HOW   - how it checks it

Three pytest tools used here:
  pytest.raises(X)  -> the test passes ONLY if error X happens inside the "with" block
  parametrize       -> runs one test many times, once per line of values
  tmp_path / capsys -> pytest gives us a temporary folder / a way to capture printed text
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
    """Helper: turn a list of rows into just their names, e.g. ["Eve", "Dee"].
    Comparing short name lists is much easier to read than comparing whole dicts."""
    return [row["name"] for row in rows]  # pick the "name" field from each row


# ---------------------------------------------------------------- load_records

def test_csv_values_are_strings():
    """WHY:   The spec says CSV values must stay strings ("10", not 10).
    CHECK: Ana's points come back as the text "10".
    HOW:   Load the sample CSV and compare the first row's points to "10"."""
    rows = dk.load_records(CSV)  # read the CSV file
    assert rows[0]["points"] == "10"  # CSV gives text, not the number 10


def test_json_keeps_number_types():
    """WHY:   The spec says JSON values keep their real types.
    CHECK: Ana's points come back as the number 10 (not "10").
    HOW:   Load the sample JSON and compare the first row's points to 10."""
    rows = dk.load_records(JSON)  # read the JSON file
    assert rows[0]["points"] == 10  # JSON keeps the real number 10


def test_unknown_extension_raises_value_error():
    """WHY:   The spec says any file that isn't .csv or .json must raise ValueError.
    CHECK: Loading "data.txt" raises ValueError.
    HOW:   pytest.raises fails the test if ValueError does NOT happen.
           (The file doesn't even need to exist - we reject it by its name first.)"""
    with pytest.raises(ValueError):  # the test passes only if ValueError happens
        dk.load_records("data.txt")  # .txt is not .csv or .json


def test_uppercase_extension_works(tmp_path):
    """WHY:   Files saved on Windows are often named DATA.CSV in capitals.
    CHECK: A file ending in .CSV still loads like .csv.
    HOW:   Write a tiny CSV into pytest's temporary folder, load it, compare the result."""
    path = tmp_path / "DATA.CSV"  # tmp_path is a temporary folder pytest makes for us
    path.write_text("name,points\nAna,10\n")  # write a tiny CSV file
    assert dk.load_records(path) == [{"name": "Ana", "points": "10"}]  # .CSV still loads


def test_csv_with_bom(tmp_path):
    """WHY:   Excel/Notepad can add 3 hidden "BOM" bytes to the start of a file. Before
           our fix, the first column's key became "\\ufeffname" and row["name"] crashed.
    CHECK: A CSV saved WITH a BOM still has a normal "name" key.
    HOW:   Save a file using encoding="utf-8-sig" (that adds the BOM), then load it."""
    path = tmp_path / "bom.csv"  # a temporary file
    path.write_text("name,points\nAna,10\n", encoding="utf-8-sig")  # save WITH a BOM, like Excel
    assert dk.load_records(path)[0]["name"] == "Ana"  # key is "name", not "\ufeffname"


def test_json_with_bom(tmp_path):
    """WHY:   Same BOM problem for JSON: before our fix, json.load crashed on it.
    CHECK: A JSON file saved WITH a BOM loads normally.
    HOW:   Save a tiny JSON file with a BOM, load it, compare the result."""
    path = tmp_path / "bom.json"  # a temporary file
    path.write_text('[{"name": "Ana"}]', encoding="utf-8-sig")  # save WITH a BOM
    assert dk.load_records(path) == [{"name": "Ana"}]  # loads without a JSON error


# -------------------------------------------------------------- filter_records

def test_filter_two_criteria():
    """WHY:   The spec says a row must match EVERY condition, not just one.
    CHECK: team="red" AND level="1" returns only Eve.
           (Ana and Cy are red but not level 1; Ben is level 1 but blue.)
    HOW:   Filter with two conditions and compare the names."""
    rows = dk.load_records(CSV)  # load the sample data
    assert names(dk.filter_records(rows, team="red", level="1")) == ["Eve"]  # red AND level 1


def test_filter_no_criteria_returns_all():
    """WHY:   The spec says "with no criteria, return all rows."
    CHECK: Calling filter_records with no conditions gives back every row.
    HOW:   Compare the result to the full list we loaded."""
    rows = dk.load_records(CSV)  # load the sample data
    assert dk.filter_records(rows) == rows  # no conditions -> every row comes back


def test_filter_no_match_returns_empty():
    """WHY:   Asking for something that isn't there should give an empty list, not crash.
    CHECK: team="green" returns [].
    HOW:   Filter for a team that doesn't exist and compare to an empty list."""
    rows = dk.load_records(CSV)  # load the sample data
    assert dk.filter_records(rows, team="green") == []  # nobody is on team green


def test_filter_json_number_matches_string():
    """WHY:   In JSON, level is the NUMBER 1. In Python, 1 == "1" is False! The spec says
           compare with str(), so they should still match.
    CHECK: level="1" (text) finds the JSON rows where level is 1 (number): Ben and Eve.
    HOW:   Filter the JSON data with a text value and compare the names."""
    rows = dk.load_records(JSON)  # JSON level is the number 1
    assert names(dk.filter_records(rows, level="1")) == ["Ben", "Eve"]  # str(1) == "1"


def test_filter_field_named_records():
    """WHY:   Before our fix, a column named "records" clashed with the function's own
           `records` parameter and Python raised TypeError.
    CHECK: filter_records(rows, records="x") works and keeps only the "x" row.
    HOW:   Make two tiny rows with a "records" column, filter, compare the result."""
    rows = [{"records": "x"}, {"records": "y"}]  # a column literally named "records"
    assert dk.filter_records(rows, records="x") == [{"records": "x"}]  # no TypeError


# ------------------------------------------------------------------- summarize

# parametrize runs the test below once per line: (decimals, red answer, blue answer)
@pytest.mark.parametrize("decimals, expected_red, expected_blue", [
    (0, 32.0, 32.0),  # 0 places: Python's round() sends an exact .5 to the EVEN number (32.5 -> 32)
    (1, 31.7, 32.5),  # the spec's own example
    (2, 31.67, 32.5),  # the default
    (3, 31.667, 32.5),
    (4, 31.6667, 32.5),
])
def test_mean_rounds_to_decimals(decimals, expected_red, expected_blue):
    """WHY:   The hidden grader picks a different `decimals` for each student, so we must
           be right for ANY value, not just one.
    CHECK: The red and blue averages are rounded correctly for decimals 0, 1, 2, 3 and 4.
    HOW:   parametrize runs this test 5 times, once per line in the table above.
           Red = (10 + 30 + 55) / 3 = 31.666...   Blue = (25 + 40) / 2 = 32.5"""
    rows = dk.load_records(CSV)  # load the sample data
    result = dk.summarize(rows, "team", "points", "mean", decimals=decimals)  # average per team
    assert result["red"] == expected_red  # rounded to the right number of places
    assert result["blue"] == expected_blue  # same for blue


def test_mean_default_is_two_decimals():
    """WHY:   The spec says decimals defaults to 2 when you don't pass it.
    CHECK: Red's mean with no decimals given is 31.67.
    HOW:   Call summarize WITHOUT decimals and check red's answer."""
    rows = dk.load_records(CSV)  # load the sample data
    assert dk.summarize(rows, "team", "points", "mean")["red"] == 31.67  # no decimals given -> 2


def test_min_and_max_are_floats():
    """WHY:   min and max aren't in the public tests at all, so we need our own check.
           The spec also says they must be floats (10.0), not strings ("10").
    CHECK: The smallest and largest points per team are right, and they are floats.
    HOW:   Compare the min and max results to the expected dicts, then check the type."""
    rows = dk.load_records(CSV)  # load the sample data
    assert dk.summarize(rows, "team", "points", "min") == {"red": 10.0, "blue": 25.0}  # smallest
    assert dk.summarize(rows, "team", "points", "max") == {"red": 55.0, "blue": 40.0}  # largest
    assert isinstance(dk.summarize(rows, "team", "points", "min")["red"], float)  # float, not str


def test_count_is_int_and_sum_is_float():
    """WHY:   The spec's table says count -> int and sum -> float. Getting the type wrong
           could fail a grader check even if the number looks right.
    CHECK: count gives an int (3) and sum gives a float (95.0).
    HOW:   isinstance(x, int) asks Python "is x an int?" - True or False."""
    rows = dk.load_records(CSV)  # load the sample data
    assert isinstance(dk.summarize(rows, "team", "points", "count")["red"], int)  # count -> int
    assert isinstance(dk.summarize(rows, "team", "points", "sum")["red"], float)  # sum -> float


def test_summarize_json_matches_csv():
    """WHY:   CSV gives "10" (text) and JSON gives 10 (number). Our float() conversion
           should make both give the same answer.
    CHECK: Summing points per team is identical for the CSV and the JSON file.
    HOW:   Summarize both files and compare both results to the spec's example."""
    csv_sum = dk.summarize(dk.load_records(CSV), "team", "points", "sum")  # sum from CSV strings
    json_sum = dk.summarize(dk.load_records(JSON), "team", "points", "sum")  # sum from JSON numbers
    assert csv_sum == json_sum == {"red": 95.0, "blue": 65.0}  # same answer either way


def test_bad_agg_raises_value_error():
    """WHY:   The spec says any agg other than the 5 allowed ones raises ValueError.
    CHECK: agg="median" raises ValueError.
    HOW:   pytest.raises fails the test if ValueError does NOT happen."""
    rows = dk.load_records(CSV)  # load the sample data
    with pytest.raises(ValueError):  # passes only if ValueError happens
        dk.summarize(rows, "team", "points", "median")  # "median" is not allowed


def test_bad_agg_raises_even_when_empty():
    """WHY:   A sneaky case: with NO rows, a careless version would never reach the agg
           check and would quietly return {}. We check agg first, so it still errors.
    CHECK: An empty list with agg="avg" still raises ValueError.
    HOW:   Same pytest.raises idea as above, but with []."""
    with pytest.raises(ValueError):  # passes only if ValueError happens
        dk.summarize([], "team", "points", "avg")  # no rows, but the agg is still checked


# ----------------------------------------------------------------------- top_n

# parametrize runs the test below once per line: (n, names we expect, in order)
@pytest.mark.parametrize("n, expected", [
    (0, []),  # ask for nothing, get nothing
    (1, ["Eve"]),  # Eve has the most points (55)
    (3, ["Eve", "Dee", "Cy"]),
    (5, ["Eve", "Dee", "Cy", "Ben", "Ana"]),  # every row, highest to lowest
    (10, ["Eve", "Dee", "Cy", "Ben", "Ana"]),  # more than exist -> just all of them
])
def test_top_n_various_n(n, expected):
    """WHY:   The hidden grader picks a different `n` for each student, so we must be
           right for ANY n - including 0 and an n bigger than the data.
    CHECK: top_n returns exactly n rows (or all of them), highest points first.
    HOW:   parametrize runs this test 5 times, once per line in the table above."""
    rows = dk.load_records(CSV)  # load the sample data
    assert names(dk.top_n(rows, "points", n)) == expected  # right rows in the right order


def test_top_n_sorts_as_numbers_not_text():
    """WHY:   The most likely hidden trap. Sorted as TEXT, "9" beats "100" because the
           character "9" comes after "1". Sorted as NUMBERS, 100 is biggest.
    CHECK: The order is 100, 55, 9 (b, c, a).
    HOW:   Make 3 rows whose numbers would sort differently as text, then check the order."""
    rows = [{"name": "a", "p": "9"}, {"name": "b", "p": "100"}, {"name": "c", "p": "55"}]
    assert names(dk.top_n(rows, "p", 3)) == ["b", "c", "a"]  # 100 > 55 > 9


def test_top_n_ties_keep_file_order():
    """WHY:   When two rows have the same value, the result should be predictable.
           Python's sort is "stable": tied rows keep their original order.
    CHECK: a and c both have 5; a was first in the data, so a stays before c.
    HOW:   Make 3 rows with a tie and check the order."""
    rows = [{"name": "a", "p": "5"}, {"name": "b", "p": "7"}, {"name": "c", "p": "5"}]
    assert names(dk.top_n(rows, "p", 3)) == ["b", "a", "c"]  # a stays before c (both are 5)


def test_top_n_does_not_change_original():
    """WHY:   A function shouldn't secretly scramble the caller's data. If top_n used
           rows.sort() instead of sorted(rows), the original list would get reordered.
    CHECK: After calling top_n, the original list still starts with Ana (file order).
    HOW:   Call top_n, ignore its result, then look at the original list."""
    rows = dk.load_records(CSV)  # load the sample data
    dk.top_n(rows, "points", 2)  # run top_n (we ignore the result here)
    assert names(rows)[0] == "Ana"  # the original list is still in file order


# ------------------------------------------------------------------- to_report

def test_report_sorted_with_no_trailing_newline():
    """WHY:   The spec is strict: sorted A->Z by key, and NO "\\n" at the very end.
           An extra newline would make the grader's exact text comparison fail.
    CHECK: {"red": 3, "blue": 2} becomes exactly "blue: 2\\nred: 3".
    HOW:   Compare the whole string, then also check it doesn't end with "\\n"."""
    report = dk.to_report({"red": 3, "blue": 2})  # unsorted input
    assert report == "blue: 2\nred: 3"  # sorted A->Z, joined by "\n"
    assert not report.endswith("\n")  # nothing extra at the end


def test_report_empty_dict():
    """WHY:   An empty summary shouldn't crash.
    CHECK: to_report({}) returns an empty string.
    HOW:   Call it with {} and compare to ""."""
    assert dk.to_report({}) == ""  # no entries -> empty string


# ------------------------------------------------------------------------- CLI

def test_cli_summarize(capsys):
    """WHY:   The CLI is part of the spec, so we test it like a user would type it.
    CHECK: "summarize ... --agg mean --decimals 1" prints the spec's example and
           returns 0 (success).
    HOW:   Call main() with the same words you'd type in the terminal (as a list).
           capsys captures what was printed so we can compare it."""
    code = main(["summarize", CSV, "--group-by", "team", "--value", "points",
                 "--agg", "mean", "--decimals", "1"])  # same as typing it in the terminal
    assert code == 0  # 0 means success
    assert capsys.readouterr().out == "blue: 32.5\nred: 31.7\n"  # print() adds the final "\n"


def test_cli_summarize_default_decimals(capsys):
    """WHY:   --decimals is optional in the CLI; it must default to 2 like summarize().
    CHECK: Leaving out --decimals prints red's mean with 2 places (31.67).
    HOW:   Run main() without --decimals and look for "red: 31.67" in the output."""
    main(["summarize", CSV, "--group-by", "team", "--value", "points", "--agg", "mean"])
    assert "red: 31.67" in capsys.readouterr().out  # no --decimals -> 2 places


def test_cli_top(capsys):
    """WHY:   The spec says "top" prints each row on its own line.
    CHECK: --n 2 prints exactly 2 lines: Eve first, then Dee.
    HOW:   Capture the output, split it into lines, count them and check who's on each."""
    code = main(["top", CSV, "--key", "points", "--n", "2"])  # top 2 rows
    lines = capsys.readouterr().out.splitlines()  # split the printed text into lines
    assert code == 0  # success
    assert len(lines) == 2  # one line per row
    assert "'Eve'" in lines[0] and "'Dee'" in lines[1]  # highest first


def test_cli_bad_file_gives_short_error(capsys):
    """WHY:   We added friendly errors in Step 4; this makes sure they keep working.
    CHECK: A .txt file returns exit code 1 and prints one short "error: ..." line.
    HOW:   Run main() with a bad file, then read what was printed to stderr
           (the error stream) instead of stdout (the normal output)."""
    code = main(["top", "data.txt", "--key", "points", "--n", "2"])  # unsupported file type
    err = capsys.readouterr().err  # error text goes to stderr
    assert code == 1  # 1 means failure
    assert err.startswith("error:")  # one short line, not a traceback
