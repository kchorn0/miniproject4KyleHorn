# miniproject4KyleHorn

INF601 - Advanced Programming in Python
Kyle Horn
Mini Project 4

Track: B

## Build Hub — `buildhub` Data Toolkit

A small data-processing toolkit and command-line tool, built end-to-end with Claude Code
working as an agent, against the fixed Build Hub specification for Mini Project 4 (Track B).

## Description

`buildhub` reads a data file (CSV or JSON), then filters, groups, summarizes, ranks and
reports on its rows. It uses **only the Python standard library** (`csv`, `json`,
`statistics`, `argparse`). No third-party packages are needed to run it; `pytest` is only
used to run the tests.

The toolkit has five functions in `buildhub/datakit.py`:

| Function | What it does | Example |
|---|---|---|
| `load_records(path)` | Loads a `.csv` (all values are strings) or `.json` (values keep their types) file into a list of row dictionaries. Any other file type raises `ValueError`. | `load_records("fixtures/sample.csv")` |
| `filter_records(records, **criteria)` | Keeps only rows that match **every** `field=value` given (compared as text). | `filter_records(rows, team="red")` → Ana, Cy, Eve |
| `summarize(records, group_by, value, agg, decimals=2)` | Groups rows and calculates `count`, `sum`, `mean` (rounded to `decimals`), `min` or `max` for each group. Unknown `agg` raises `ValueError`. | `summarize(rows, "team", "points", "sum")` → `{"red": 95.0, "blue": 65.0}` |
| `top_n(records, key, n)` | Returns the `n` rows with the largest numeric `key`, highest first. | `top_n(rows, "points", 2)` → Eve, Dee |
| `to_report(summary)` | Turns a summary dict into sorted `key: value` text lines. | `"blue: 2\nred: 3"` |

A command-line interface in `buildhub/__main__.py` runs these from the terminal
(`summarize` and `top` commands).

The project is graded by a hidden autograder that uses each student's `BUILD_SEED` to vary
values such as the `decimals` used for `mean` and the `n` used for `top_n`. The code is
written to work for **any** values — nothing is hard-coded to the sample data — so the seed
is not needed to run anything in this repo.

### Project structure

```
miniproject4KyleHorn/
├── buildhub/
│   ├── __init__.py          package marker
│   ├── __main__.py          command-line interface (summarize, top)
│   └── datakit.py           the five toolkit functions
├── fixtures/
│   ├── sample.csv           sample data (provided by the instructor)
│   └── sample.json          same data in JSON (provided by the instructor)
├── tests/
│   ├── public/test_smoke.py the instructor's 7 public tests (unchanged except the required header)
│   └── extra/test_extra.py  our 36 additional edge-case tests
├── REPORT.md                technical write-up
├── AGENTIC_WORKFLOW.md      how Claude Code was directed (goal → tool calls → review)
├── transcript/              exported Claude Code session transcript
├── pytest.ini               test settings (provided by the instructor)
├── requirements.txt         pytest (only needed for testing)
└── README.md
```

## Getting Started

### Dependencies

* Python 3.8 or newer (developed and tested on Python 3.14.7)
* `pip` (comes with Python)
* `pytest` 8.0 or newer — only for running the tests; installed from `requirements.txt` below
* No internet access, API keys or environment variables are needed
* Works on Windows (PowerShell) and Linux/macOS (bash). Commands for both are given below.

### Installing

1. Clone the repository:

Windows (PowerShell) and Linux/macOS (bash) — same command:
```
git clone https://github.com/kchorn0/miniproject4KyleHorn.git
cd miniproject4KyleHorn
```

2. Create a virtual environment:

Windows (PowerShell):
```
python -m venv .venv
```
Linux/macOS (bash):
```
python3 -m venv .venv
```

3. Activate the virtual environment:

Windows (PowerShell):
```
.\.venv\Scripts\Activate.ps1
```
Linux/macOS (bash):
```
source .venv/bin/activate
```
Your prompt should now start with `(.venv)`.

4. Install the required packages (with the venv activated):

Windows and Linux/macOS — same command:
```
pip install -r requirements.txt
```

No files or folders need to be created or edited by hand.

### Executing program

All commands are run from the project's root folder with the venv activated.
(On Linux/macOS, use `python3` if `python` is not found.)

**1. Summarize — group rows and calculate a value per group**
```
python -m buildhub summarize fixtures/sample.csv --group-by team --value points --agg mean --decimals 2
```
Output:
```
blue: 32.5
red: 31.67
```
* `--agg` can be `count`, `sum`, `mean`, `min` or `max`
* `--decimals` is optional (default `2`) and only affects `mean`
* Works the same on `fixtures/sample.json`

**2. Top — show the N rows with the largest value**
```
python -m buildhub top fixtures/sample.csv --key points --n 3
```
Output:
```
{'name': 'Eve', 'team': 'red', 'points': '55', 'level': '1'}
{'name': 'Dee', 'team': 'blue', 'points': '40', 'level': '3'}
{'name': 'Cy', 'team': 'red', 'points': '30', 'level': '2'}
```

**3. Built-in help**
```
python -m buildhub --help
python -m buildhub summarize --help
```

**4. Using the functions from Python**
```python
from buildhub import datakit as dk

rows = dk.load_records("fixtures/sample.csv")
red = dk.filter_records(rows, team="red")
summary = dk.summarize(rows, "team", "points", "count")
print(dk.to_report(summary))      # blue: 2 / red: 3
```

### Running the tests

| Command | What it runs | Expected result |
|---|---|---|
| `pytest` | The instructor's 7 public tests | `7 passed` |
| `pytest tests/extra` | Our 36 extra edge-case tests | `36 passed` |
| `pytest tests` | Everything | `43 passed` |
| `pytest tests -v` | Everything, listing each test by name | 43 × `PASSED` |

The extra tests check cases the public tests don't — for example `mean` at
`decimals` 0–4, `top_n` at `n` 0–10, numbers sorted as numbers (not text), files saved
with a BOM, the CLI's output and its error messages. Each test has a WHY / CHECK / HOW
comment. The instructor's test files and `pytest.ini` were not modified (only the
required header was added).

## Help

* **`ModuleNotFoundError: No module named 'pytest'`** — the venv isn't activated or the
  packages weren't installed. Re-run steps 3 and 4 of Installing.
* **`No module named buildhub`** — you're not in the project's root folder. `cd` into
  `miniproject4KyleHorn` (the folder that contains `buildhub/`) and try again.
* **`running scripts is disabled on this system`** (Windows only) — PowerShell is blocking
  `Activate.ps1`. Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, or skip
  activating and use `.\.venv\Scripts\python.exe -m buildhub ...` instead.
* **`error: Unsupported file type (expected .csv or .json)`** — only `.csv` and `.json`
  files are supported.
* **`error: [Errno 2] No such file or directory`** — check the file path you typed.
* **`error: field 'xyz' not found in ...`** — the `--key`, `--group-by` or `--value` name
  doesn't match a column in the file (names are case-sensitive).
* **`error: could not convert string to float`** — `sum`, `mean`, `min`, `max` and `top`
  need a numeric column (e.g. `points`, not `name`).
* **`invalid choice` for `--agg`** — use one of `count`, `sum`, `mean`, `min`, `max`.

## Authors

Kyle Horn ([kchorn@mail.fhsu.edu](mailto:kchorn@mail.fhsu.edu))

## Acknowledgments

* INF601 Mini Project 4 — Build Hub starter files and specification (instructor-provided:
  stub package, public tests, sample data, `pytest.ini`, `requirements.txt`)
* Python documentation: [csv](https://docs.python.org/3/library/csv.html),
  [json](https://docs.python.org/3/library/json.html),
  [statistics](https://docs.python.org/3/library/statistics.html),
  [argparse](https://docs.python.org/3/library/argparse.html)
* [pytest documentation](https://docs.pytest.org/) — `parametrize`, `tmp_path`, `capsys`
* [Claude Code](https://claude.com/claude-code) by Anthropic — the AI coding agent used to build this project

## AI Usage

This project was built with **Claude Code (Claude Opus 5.5)** working as an agent, which
was the point of the assignment. Full details are in [REPORT.md](REPORT.md),
[AGENTIC_WORKFLOW.md](AGENTIC_WORKFLOW.md) and the session transcript in `transcript/`.

**How we worked:** every step followed the same loop —
goal → the agent writes code → the agent runs `pytest` → if it fails, the agent fixes and
re-runs (max 3 tries, then asks me) → I review → I commit.

**What Claude Code did (AI-assisted):**
* Read the assignment, spec and starter files, and proposed the step-by-step plan
* Wrote all code in `buildhub/datakit.py` and `buildhub/__main__.py`, with a comment on every line
* Wrote all 36 extra tests in `tests/extra/test_extra.py`, with WHY / CHECK / HOW notes
* Ran the tests and CLI after every change, and fixed its own mistakes (e.g. a wrong
  expected value in a rounding test; a comment fix that didn't apply on the first try)
* Ran an edge-case audit that found 2 bugs (files saved with a BOM; a field named `records`)
  and a final audit of the whole repository against the rubric
* Drafted this README, REPORT.md and AGENTIC_WORKFLOW.md

**What I did (hand-done / my decisions):**
* Did the research for this project myself, including reading the provided instructions,
  grading rubric and Build Hub folder, so we knew how to plan the project
* Chose Track B, computed my BUILD_SEED, set up the GitHub repo, `git init` and the remote
* Made **every commit and push** myself after reviewing each change, and reworded the
  commit messages in my own words
* Directed the agent step by step and approved each step before it continued
* Required line-by-line comments so I could review and explain every line
* Caught that we should not modify the instructor's test files or `pytest.ini`, which
  changed the plan (extra tests went in their own folder)
* Decided to fix the BOM and `records` bugs as a separate commit, to add short CLI error
  messages, and to keep the `/` trade-off in `filter_records` after the audit
* Ran the CLI commands and test suites myself in my own terminal to verify the results

**What was not AI-verified:** the hidden autograder. The public tests (7/7) and our extra
tests (36/36) pass, but the hidden checks can only be confirmed by the instructor.

I reviewed all AI-generated code and can explain every line.
