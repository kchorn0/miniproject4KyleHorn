# Agentic Workflow — How I Directed Claude Code

INF601 - Advanced Programming in Python
Kyle Horn
Mini Project 4

This document shows **how** the project was built: the loop of
**goal → tool calls → review** that I used to direct Claude Code (Claude Opus 5.5)
from the starter files to the finished project. The full, unedited conversation is in
`transcript/`. Design and testing details are in [REPORT.md](REPORT.md).

## The loop we agreed on

Before any code was written, I set one rule for every coding step:

```
 ┌─► 1. GOAL     I give one clear, small goal (e.g. "implement summarize, comment every line")
 │   2. ACT      Agent reads files and edits code
 │   3. VERIFY   Agent runs pytest / the CLI / edge-case checks
 │   4. RECOVER  Fails? Agent diagnoses, fixes, re-runs (max 3 tries, then asks me)
 │   5. STOP     Agent stops and reports results; it never commits
 │   6. REVIEW   I read the code and results, ask questions, run it myself
 └── 7. COMMIT   I commit and push, then give the next goal
```

**Rules I set for the agent along the way:**
- No code until I approve the plan ("Do not code anything yet").
- A comment on every line, plus a simple explanation of each step.
- Stop before every commit; **I make all commits and pushes.**
- Draft documentation in chat first; nothing is written until I approve it.
- Don't modify the instructor's test files or `pytest.ini`.

## Harness: what the agent could and couldn't do

| The agent used | For |
|---|---|
| **Read / Glob / Grep** | Reading the instructions, spec, starter code and tests |
| **Edit / Write** | Changing code, tests and docs (only after my go-ahead) |
| **PowerShell / Bash** | Creating the venv, running `pytest`, running the CLI, git *read-only* checks (`log`, `status`, `diff`) |
| **Scratchpad folder** | Throwaway probe scripts, clean clones and README replays, so the project folder was never touched by experiments |
| **Persistent memory** | Saving the full spec and rubric after I deleted the instruction folder |

| The agent did **not** | Who did |
|---|---|
| Commit, push or change GitHub settings | Me |
| Decide which audit findings to fix | Me |
| Write anything before I approved the plan or draft | — |

## Timeline

### Phase 0: Understanding and planning (no code)
- **Goal (me):** "Read all the files… understand this project… plan it out… Do not code anything yet."
- **Tool calls (agent):** listed and read every file (the instructions, SPEC.md, README, stubs, tests, fixtures).
- **Result:** a rubric-to-deliverable plan and 5 clarifying questions.
- **Review (me):** answered the questions (Track B, `print(row)` for the CLI, transcript format, seed) and kept the agent from coding.
- **Context step:** I deleted the instruction folder, and the agent saved the full spec and rubric to its persistent memory so nothing was lost.

### Phase 1: Environment setup
- **Goal (me):** set up the venv and give me a test to confirm it.
- **Tool calls:** `git status/log/remote` (to confirm my GitHub setup), `python -m venv .venv`, `pip install -r requirements.txt`, `pytest`.
- **Verify:** `7 failed` (`NotImplementedError`), the expected baseline. `.venv` confirmed git-ignored.
- **Review (me):** activated the venv in VS Code and saw `7 failed` myself.
- **Goal (me):** add the 3 header lines to every `.py` file, then stop.
- **Commit (me):** `4ff1493 Initial starter files`

### Step 1: `load_records` + `filter_records`
- **Goal (me):** "Start with step 1… comment out each line so I can review."
- **Tool calls:** Edit `datakit.py` → `pytest` → spot checks (JSON filter, no criteria, `.txt`).
- **Verify:** `3 passed, 4 failed` (the 3 target tests pass). **First try.**
- **Review (me):** asked for beginner-friendly explanations of each function.
- **Commit (me):** `331ea42 function load_records and filter_records`

### Audit 1: edge cases
- **Goal (me):** "Audit our current 2 implementations against every requirement… find an issue that might throw an error."
- **Tool calls:** wrote a 25-case probe script in the scratchpad and ran it (no project files changed).
- **Found:** 🐛 BOM files crash (`KeyError` / `JSONDecodeError`); 🐛 a field named `records` → `TypeError`; ⚠ cp1252 files (documented, not fixed).
- **Decision (me):** fix both bugs as a **separate commit**.
- **Tool calls:** 3 edits → re-ran the probe → `pytest`.
- **Verify:** both bugs fixed, the other 22 cases unchanged. **First try.**
- **Commit (me):** `3bba58e Handle BOM-encoded files and allow filtering`

### Step 2: `summarize`
- **Goal (me):** "Start step 2 (summarize) like we planned."
- **Tool calls:** Edit → `pytest` → 16 probes (decimals 0–4, min/max/sum/count types, bad agg, empty list).
- **Verify:** `5 passed, 2 failed` (the target tests pass); spec example `{'red': 31.7, 'blue': 32.5}` exact. **First try.**
- **Review (me):** "Explain what this implementation did, simple!"
- **Commit (me):** `e26af82 Implement summarize`

### Step 3: `top_n` + `to_report`
- **Goal (me):** "Start step 3… be sure to audit our work!"
- **Tool calls:** Edit → `pytest` → 22 audit probes (`n` 0–10 and −1, the `"100"` vs `"9"` trap, ties, empty, no trailing newline).
- **Verify:** **7 / 7 public tests pass.** **First try.**
- **Commit (me):** `9da0c25 Implement top_n and to_report`

### Step 4: CLI
- **Goal (me):** "Start step 4… explain this step simple and short."
- **Tool calls:** Write `__main__.py` → ran both commands on the CSV and JSON, bad `--agg`, no subcommand, `main([...])`.
- **Verify:** correct output, exit codes 0/2. **First try.**
- **Review (me):** asked for 3 tests I could run myself, and ran them.
- **Found (agent, while testing):** a bad file type showed a long traceback. **Decision (me):** add short error messages, then stop so I could test.
- **Verify:** 4 error cases → one-line `error:` messages, exit code 1; `pytest` still 7 / 7.
- **Commit (me):** `606e736 Add argparse CLI and friendly error messages`

### Step 5: extra tests
- **Goal (me):** "Start step 5… We cannot and should not touch the testing files the instructor gave us."
- **Plan change (me):** the agent's original plan edited `pytest.ini`. **I stopped that**, and the tests went into a new `tests/extra/` folder instead.
- **Tool calls:** Write `tests/extra/test_extra.py` → `pytest tests`.
- **Verify: ❌ 42 passed, 1 failed.** The agent's test expected `round(32.5, 0) == 32.5`, but Python's banker's rounding gives `32.0`.
- **Recover (retry 1 of 3):** the agent diagnosed that **the test was wrong, not the code**, and fixed the test → ✅ **43 passed.**
- **Commit (me):** `5a1a9c3 Add extra edge-case tests`
- **Review (me):** "Some I don't understand… provide a deeper, clearer comment to each test."
- **Tool calls:** added WHY / CHECK / HOW notes to all tests → still 43 passed.
- **Commit (me):** `d137321 test explanations`

### Final audit + cleanup
- **Goal (me):** a full audit against the instructions, SPEC and rubric. "Do not modify any files… Be honest and specific."
- **Tool calls:** `git log/status/ls-files`, header check, fresh-clone test run, **randomized cross-check (120,000 comparisons, 0 mismatches)**, keyword-call probes, hidden-character scan.
- **Found:** README/report/workflow missing (the main risk); ⚠ the `/` fix had broken the `records=` keyword call (missed by the agent earlier); stale "YOUR JOB… SPEC.md" docstrings; **hidden BOM characters the agent itself had inserted into 2 comments.**
- **Decision (me):** keep the `/` trade-off; fix the docstrings and hidden characters.
- **Recover (attempt 2 of 3):** the first hidden-character fix silently failed (the shell converted the escape back); a byte-level check caught it, and the second attempt worked.
- **Commit (me):** `ee9dfba Clean up starter docstrings and hidden characters in comments`

### Step 6: README
- **Goal (me):** "Do not change any code yet… Would this [MP3 README format] be good… draft the sections thoroughly."
- **Tool calls:** draft in chat → my answers (rewording commits, my own research, keep the email) → Write `README.md`.
- **Audit (me):** "Audit the readme… if you follow our exact steps will you run into any errors?"
- **Tool calls:** replayed every README step on a fresh copy (venv, pip, every command, every Help message).
- **Found:** the repo is private (GitHub API 404); `Activate.ps1` is blocked by the default PowerShell policy; one Help message didn't match the real error text.
- **Decision (me):** fix the 2 README issues; make the repo public at submission.
- **Commits (me):** `e995b22 Add README`, `73ba44c Update README`

### Step 7a: Technical report
- **Goal (me):** draft in chat first, then approved.
- **Tool calls:** re-verified **every number** (test counts, versions, randomized check) from fresh output → Write `REPORT.md` → hidden-character scan.
- **Found and fixed (retry 1 of 3):** the same hidden-character problem happened again when writing the report; the same byte check caught it, and the fix worked on the first attempt.
- **Commits (me):** `1089a50 Added Report.md`, `a90426f Update Report`

### Step 7b–8: This document, transcript, final check
- This file was drafted in chat and approved before being written.
- The transcript is exported last, so it covers the whole session.
- Final check: fresh-clone tests, `git status`, every rubric line, and the repo made public.

## The loop by the numbers

| Measure | Count |
|---|---|
| Coding steps that passed verification on the **first try** | 5 of 7 (Steps 1–4 and the bug fix; Step 5 and the cleanup each needed a retry) |
| Retries used (of the 3 allowed per step) | 3 total: the rounding test, the hidden-character cleanup, and the hidden characters in the report |
| Times the agent had to stop and ask me after 3 failures | 0 |
| Bugs found by agent audits before submission | 2 code bugs + 1 side effect + 3 documentation issues |
| Agent mistakes caught by real checks (tests, byte scans, audits) | 4 |
| Times I changed the agent's plan or overrode a recommendation | Several (no `pytest.ini` edits, separate bug-fix commit, short CLI errors, README format, draft-first docs) |
| Commits | 14+, all by me |

## What worked, and what I'd change

**Worked:**
- **Small goals plus a pass/fail check.** Every step had a test that defined "done."
- **Mandatory stops.** Reviewing and committing each step myself kept me in control and let me learn each piece before moving on.
- **Asking for audits.** They found bugs the public tests never would have.
- **Draft-first documentation.** Nothing went into the repo that I hadn't read.

**I'd change:**
- **Audit after every step, not only near the end.** The `/` side effect would have been caught immediately.
- **Ask the agent to scan for hidden characters after every write.** That class of mistake happened twice.
