# Mini Project 4 — Technical Report (Track B: Build Hub)

INF601 - Advanced Programming in Python
Kyle Horn
Mini Project 4

## 1. What I built and why

**What:** `buildhub`, a small data-processing toolkit and command-line tool, implemented
against the instructor's fixed Build Hub specification. It has five functions in
`buildhub/datakit.py` and a CLI in `buildhub/__main__.py`:

| Function | Purpose |
|---|---|
| `load_records(path)` | Read a `.csv` (values as strings) or `.json` (values keep types) file into a list of row dicts; any other extension raises `ValueError` |
| `filter_records(records, **criteria)` | Keep rows where every `field=value` matches, compared as `str(row[field]) == str(value)` |
| `summarize(records, group_by, value, agg, decimals=2)` | Group rows and compute `count` (int), `sum`/`min`/`max` (float), or `mean` (float, rounded to `decimals`); unknown `agg` raises `ValueError` |
| `top_n(records, key, n)` | The `n` rows with the largest numeric `key`, descending |
| `to_report(summary)` | Sorted `key: value` lines joined by `"\n"`, no trailing newline |

The CLI provides `python -m buildhub summarize ...` and `python -m buildhub top ...`.

**Why:** Mini Project 4 asks us to use Claude Code *as an agent*, not as autocomplete, to
build a tool end-to-end, and then report honestly on how it went. Track B gives a fixed
spec and a hidden autograder that varies its parameters per student (via `BUILD_SEED`),
so the goal was a **general, spec-exact implementation**, not one tuned to pass the public
tests. The project was also a hands-on test of Week 7's "loop engineering": giving the
agent an objective pass/fail signal (pytest), a clear "done" condition, a retry cap,
and a human review point.

**Constraints from the spec:** standard library only (`csv`, `json`, `statistics`;
`argparse` and `sys` for the CLI), `buildhub/` at the repo root, and a required header on
every `.py` file.

## 2. Design decisions

| Decision | Why |
|---|---|
| **Compare filters as `str()` on both sides** | The spec requires it, and it makes CSV (`"1"`) and JSON (`1`) data behave the same. In Python, `1 == "1"` is `False`. |
| **Check `agg` before grouping** in `summarize` | A bad `agg` fails immediately, even on an empty list, instead of silently returning `{}`. |
| **`count` never calls `float()`** | Counting rows doesn't need numbers, so `count` works on text columns too. |
| **`statistics.mean` + `round(x, decimals)`** for `mean` | The spec names the `statistics` module, and `statistics.mean` is computed exactly before rounding. |
| **`sorted(..., key=float(...), reverse=True)`** in `top_n` | Sorting as numbers avoids the classic trap where text `"9"` sorts above `"100"`. `sorted()` doesn't modify the caller's list, and Python's sort is stable, so ties keep their file order. |
| **`ranked[:max(n, 0)]`** | Slicing handles `n` larger than the data. `max(n, 0)` makes a negative `n` return `[]` instead of Python's "all but the last" slice. The spec doesn't define negative `n`, so this is a defensive choice. |
| **`sorted(summary)` (keys only)** in `to_report` | Sorts by key as the spec says, and `"\n".join` guarantees no trailing newline. |
| **`encoding="utf-8-sig"`** when opening files | Reads normal UTF-8 identically, but also strips the hidden BOM that Excel/Notepad can add (see §4). |
| **`records` is positional-only (`/`)** in `filter_records` | Lets a data column literally named `records` be used as a filter (see §5 for the trade-off). |
| **argparse subcommands, `--agg` limited to the 5 choices, `main(argv=None)`** | Clear usage and errors, and `main([...])` can be called from tests without a terminal. |
| **CLI catches `ValueError`/`OSError`/`KeyError`** | Prints one short `error: ...` line and exits with code 1, instead of a traceback. The library functions still raise exactly as the spec requires. Only the CLI softens the message. |
| **`top` prints each row with `print(row)`** | The spec only says "prints each row… one per line," so I chose the most literal reading. |
| **Extra tests in `tests/extra/`, instructor files untouched** | Plain `pytest` still runs exactly the instructor's setup. `pytest tests` runs everything. |

## 3. What the agent did vs. what I did

**How the work was divided:** Claude Code (Claude Opus 5.5) wrote all of the code, tests and
first drafts of the documentation. I set the direction, made the decisions, reviewed
every change and controlled git. Every step followed one loop that we agreed on at the start:

> **Goal → agent writes code → agent runs pytest → if it fails, agent fixes and re-runs
> (max 3 tries, then asks me) → I review → I commit.**

| | Claude Code (agent) | Me |
|---|---|---|
| **Research and planning** | Read the starter files, spec and rubric; proposed the 7-step plan and a rubric-to-deliverable checklist | Did the research myself, including reading the provided instructions, grading rubric and Build Hub folder, so we knew how to plan; approved and adjusted the plan |
| **Setup** | Created the `.venv` and installed pytest; ran the baseline (7 failed, as expected) | Chose Track B, got my BUILD_SEED, created the GitHub repo, `git init` and remote; activated the venv in VS Code and confirmed the baseline myself |
| **Code** | Wrote every function and the CLI, with a comment on every line (at my request) | Required line-by-line comments and a plain-language explanation of each step so I could explain every line |
| **Testing** | Wrote 36 extra tests with WHY/CHECK/HOW notes; ran edge-case probes, a clean-clone run and a randomized cross-check | Ran the CLI and test suites in my own terminal; asked for clearer test explanations when some were confusing |
| **Audits** | Found 2 bugs in an edge-case audit; ran a full rubric audit; replayed the README step by step | Asked for the audits, and decided which findings to fix and which to keep |
| **Key decisions** | Proposed options with recommendations | Fix the bugs as a separate commit; add short CLI errors; **don't modify the instructor's test files or `pytest.ini`** (this changed the agent's plan); keep the `/` trade-off |
| **Git** | Never committed or pushed | Made every commit and push in the history, and reworded the commit messages myself |
| **Docs** | Drafted README, this report and AGENTIC_WORKFLOW.md in chat for approval | Supplied the README format from earlier projects; reviewed and approved every draft before it was written to a file |

**Mistakes the agent made (and how they were caught):**
1. **A wrong expected value in its own test.** It expected `round(32.5, 0)` to be `32.5`,
   but Python gives `32.0`, because exact halves round to the even number. pytest caught it
   on the first run. The agent correctly fixed the **test**, not the code (retry 1 of 3).
2. **It introduced a hidden character into two comments.** While writing a comment about
   the BOM bug, its edit inserted a real invisible BOM character instead of the text
   `\ufeff`. The final audit found it. The first repair attempt failed silently (the shell
   converted the escape back), and a byte-level check caught that, so it was fixed on
   attempt 2 of 3.
3. **It missed a side effect of its own fix.** Adding `/` to `filter_records` broke the
   (unusual) call style `filter_records(records=rows, ...)`. The agent didn't notice when
   it made the change. It found the problem later, during the final audit.
4. **Its first plan would have edited the instructor's `pytest.ini`.** I stopped that,
   and we put our tests in a separate folder instead.

## 4. How I tested it

**Results (Python 3.14.7, pytest 9.1.1, Windows 11):**

| Check | Result |
|---|---|
| Instructor's public tests (`pytest`) | **7 / 7 pass** |
| Our extra tests (`pytest tests/extra`) | **36 / 36 pass** |
| Everything (`pytest tests`) | **43 / 43 pass** |
| Same suites from a **fresh clone** of the committed code | 7 / 7 and 43 / 43, so nothing depends on local-only files |
| Randomized cross-check: 20,000 random datasets vs. a simple independent reference | **0 mismatches in 120,000 comparisons** (all 5 aggregations with `decimals` 0–6, plus `top_n` with `n` 0–12), and 0 mismatches in 20,000 `to_report` checks |
| Every README command replayed on a fresh copy | All outputs matched the README exactly |

**What the 36 extra tests cover** (each has a WHY / CHECK / HOW note):
- **Parameters the hidden grader varies:** `mean` at `decimals` 0–4 and the default of 2;
  `top_n` at `n` = 0, 1, 3, 5 and 10.
- **Spec details:** CSV values are strings and JSON values keep their types; output types
  (`count` is `int`, the others are `float`); bad `agg` and bad file extension raise
  `ValueError`; `to_report` is sorted with no trailing newline.
- **Traps:** numbers sorted as numbers, not text (`"100"` vs `"9"`); ties keep file order;
  `top_n` doesn't modify the caller's list; JSON `1` matches the filter `"1"`.
- **Regression tests for the 2 audit bugs**, plus the CLI's output and its error/exit codes.

**Bugs found by testing before submission:**

| Bug | Symptom | Fix |
|---|---|---|
| Files saved with a BOM (Excel/Notepad) | CSV: first key became `'\ufeffname'` → `KeyError: 'name'`. JSON: `JSONDecodeError` | Open files with `encoding="utf-8-sig"` |
| A data column named `records` | `filter_records(rows, records="x")` → `TypeError: got multiple values` | Make `records` positional-only with `/` |

**Documentation audit findings (fixed):** the README's step 3 is blocked by PowerShell's
default execution policy, so I added the fix inline; and one Help message didn't match the
real error text, so I corrected it.

## 5. Limitations

- **The hidden autograder is unverified.** Public and extra tests pass, but only the
  instructor's grader can confirm the final score. I am not claiming full marks.
- **`/` trade-off:** `filter_records(records=rows, ...)` (passing the list *by name*) raises
  `TypeError`. The spec's examples pass it by position, so I kept the fix.
- **Mean rounding method:** `round(statistics.mean(...), d)` and `round(sum/len, d)` agreed
  in 19,997 of 20,000 random cases. The other 3 were exact `.xx5` averages where float
  precision tips the rounding (e.g. 22.59 vs 22.58). If the grader used `sum/len`, a case
  like that could differ.
- **Banker's rounding:** Python's `round()` sends exact halves to the even digit
  (`round(32.5) == 32`). This is standard Python behavior, but it may surprise users.
- **Encoding:** non-UTF-8 files (e.g. Windows cp1252 with `é`) raise `UnicodeDecodeError`.
- **Strict errors by design:** a missing field raises `KeyError`, and a non-numeric value in
  a math aggregation raises `ValueError`, rather than skipping rows silently.
- **Mixed key types:** if a JSON column mixes numbers and text (`1` and `"2"`), grouping
  works, but `to_report` can't sort the keys, because Python can't compare `int` and `str`.
- **CLI `top` format:** rows print as Python dicts. The spec doesn't fix a format.
- **Platforms:** tested only on Windows 11 with Python 3.14.7. The Linux/macOS commands
  and the "Python 3.8+" minimum are unverified.

## 6. Next steps

- Add a `--format json` option to `top` for machine-readable output.
- Add a `filter` CLI subcommand, or `--where field=value` options.
- Optional encoding fallback (e.g. retry with cp1252) or an `--encoding` flag.
- Decide on a policy for bad rows (skip and warn, or fail) and make it configurable.
- Run the tests on several Python versions and on Linux/macOS (e.g. GitHub Actions CI).
- Replace the `/` with a design that supports both call styles, if that ever matters.

## 7. Reflection: loop engineering in practice

Week 7 described the ladder **prompt → context → harness → loop**. This project used each one:

- **Prompt:** a clear goal per step ("implement `summarize`, comment every line, run the
  tests, stop for my review").
- **Context:** after the instruction files were deleted, the agent kept the full spec and
  rubric in its persistent memory, and every step was checked against it.
- **Harness:** Claude Code's tools (read/edit files, run PowerShell and pytest) and its
  permission model. The agent never committed or pushed; that stayed with me.
- **Loop:**
  - **Verification as feedback:** pytest's pass/fail, which the agent can't fake.
  - **Testable termination:** "these specific tests pass."
  - **Stopping logic:** a 3-try cap, plus a mandatory stop for my review and commit.
  - **Recovery:** both agent mistakes in §3 were caught by real checks, not by the
    agent's own confidence.

The biggest lesson is that **the trajectory mattered more than any single response**.
The agent's first versions were usually right, but not always: a test expectation, a
comment edit and a side effect were all wrong at first. Real feedback (tests, byte checks,
audits) plus human review turned those into fixes instead of shipped bugs.

### My reflection

The most useful thing I did was slow the agent down. I asked it to plan before coding, to
comment every line, to stop before every commit, and to explain each step simply, so I
could verify my own learning instead of just accepting working code. That paid off: when
I questioned the plan, I caught that we were about to modify the instructor's test setup,
and asking for audits found real bugs that the public tests never would have shown. What
surprised me most was that the agent made mistakes too — a wrong test, a hidden character,
a missed side effect — and that the tests and audits, not the agent's confidence, were what
caught them. Next time I would ask for an audit after every step instead of only near the
end, so problems like the `/` side effect get caught when they are introduced.
