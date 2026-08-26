#!/usr/bin/env python3
"""
Grade whichever lecture's challenge is currently due.

Designed to be run unattended (cron, launchd, or a Claude scheduled task).
Prints a short human summary and exits non-zero on any setup problem, so a
scheduler can tell the difference between "nothing to do" and "broken".

    python3 grade_latest.py              # grade whatever is due today
    python3 grade_latest.py L3_Sorts_AI  # grade one lecture explicitly
    python3 grade_latest.py --dry-run    # read the sheet, grade, write nothing

Needs, once:
    pip install gspread google-auth anthropic
    chapters/Finance/service_account.json   (gitignored)
    export ANTHROPIC_API_KEY=...
"""
import os, subprocess, sys, datetime as dt
from pathlib import Path

HERE  = Path(__file__).resolve().parent
SHEET = "UG54 Submissions (Responses)"

# Challenges are started in class and due before the NEXT lecture, so each
# entry is (date the challenge stops accepting new work, assignment name).
# Dates are the Fall 2026 meeting dates from PLAN.md.
DUE = [
    ("2026-09-09", "L1_Returns_AI"),
    ("2026-09-14", "L2_Portfolios_AI"),
    ("2026-09-16", "L3_Sorts_AI"),
    ("2026-09-21", "L4_PerfEval_AI"),
    ("2026-09-23", "L5_FactorZoo_AI"),
    ("2026-09-28", "L6_MultiFactor_AI"),
    ("2026-09-30", "L7_Decomposition_AI"),
]


def preflight() -> list[str]:
    problems = []
    if not (HERE / "service_account.json").exists():
        problems.append(
            "service_account.json is missing from chapters/Finance/.\n"
            "     Google Cloud Console -> IAM -> Service Accounts -> create key (JSON),\n"
            "     save it there, then share the Sheet with that account's email."
        )
    for mod in ("gspread",):
        try:
            __import__(mod)
        except ImportError:
            problems.append(f"{mod} is not installed:  pip install {mod}")
    return problems


def due_today(today: dt.date) -> str | None:
    """The most recent challenge whose due date has passed."""
    past = [(dt.date.fromisoformat(d), a) for d, a in DUE if dt.date.fromisoformat(d) <= today]
    return past[-1][1] if past else None


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry  = "--dry-run" in sys.argv

    problems = preflight()
    if problems:
        print("Cannot grade yet:\n")
        for p in problems:
            print(f"  ❌ {p}\n")
        return 2

    today = dt.date.today()
    assignment = args[0] if args else due_today(today)
    if assignment is None:
        print(f"{today}: no challenge is due yet. Nothing to grade.")
        return 0

    tab = "Grades_" + assignment.split("_")[0]
    print(f"{today}: grading {assignment} -> tab '{tab}'\n")
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("(no ANTHROPIC_API_KEY — numeric answers graded automatically, "
              "memos written out for grading)\n")

    cmd = [sys.executable, str(HERE / "auto_evaluator_form.py"),
           "--sheet", SHEET, "--grades-tab", tab, "--assignment", assignment]
    if dry:
        cmd.append("--dry-run")
    return subprocess.run(cmd, cwd=HERE).returncode


if __name__ == "__main__":
    sys.exit(main())
