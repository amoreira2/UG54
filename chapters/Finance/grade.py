#!/usr/bin/env python3
"""
Grade everything in the sheet that has not been graded yet.

    python3 grade.py                    # whatever is outstanding, any lecture
    python3 grade.py L3_Sorts_AI        # force one lecture, graded or not
    python3 grade.py --dry-run

No dates, no arguments, safe to run as often as you like. A submission counts as
graded once its (email, submission timestamp) appears in that lecture's grades
tab, so late work is picked up automatically on the next run.
"""
import argparse, base64, hashlib, json, os, re, subprocess, sys

HERE  = os.path.dirname(os.path.abspath(__file__))
SHEET = "UG54 Submissions (Responses)"

# Only used to mark work as LATE in the grades tab -- not to decide what to grade.
DUE = [
    ("2026-09-09", "L1_Returns_AI"),
    ("2026-09-14", "L2_Portfolios_AI"),
    ("2026-09-16", "L3_Sorts_AI"),
    ("2026-09-21", "L4_PerfEval_AI"),
    ("2026-09-23", "L5_FactorZoo_AI"),
    ("2026-09-28", "L6_MultiFactor_AI"),
    ("2026-09-30", "L7_Decomposition_AI"),
]

TOKEN_RE = re.compile(r"UG54::([0-9a-f]{8})::([A-Za-z0-9+/=\s]+)")


def peek(token: str):
    """Which lecture is this, and when was it produced? Cheap, no validation."""
    m = TOKEN_RE.search(token or "")
    if not m:
        return None, None
    body = re.sub(r"\s+", "", m.group(2)).rstrip("=")
    body += "=" * (-len(body) % 4)
    try:
        d = json.loads(base64.b64decode(body.encode()).decode())
        return d.get("assignment"), d.get("ts")
    except Exception:
        return None, None


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("assignment", nargs="?")
    p.add_argument("--sheet", default=SHEET)
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args()

    key = os.path.join(HERE, "service_account.json")
    if not os.path.exists(key):
        print(f"❌ {key} not found — see the setup steps in TODO.md."); return 2
    try:
        import gspread
    except ImportError:
        print("❌ gspread not installed:  pip install gspread"); return 2

    gc   = gspread.service_account(filename=key)
    book = gc.open(a.sheet)
    responses = book.worksheet("Form Responses 1").get_all_records()
    if not responses:
        print("No submissions in the sheet yet."); return 0

    # What is in the sheet, and what has already been graded?
    pending, undecodable = {}, 0
    for r in responses:
        asg, ts = peek(r.get("Submission token") or r.get("Token") or "")
        if not asg:
            undecodable += 1
            continue
        pending.setdefault(asg, []).append((r.get("Email Address") or r.get("Email"), ts))

    todo = []
    print(f"{len(responses)} submission(s) in the sheet\n")
    for asg in sorted(pending):
        tab = "Grades_" + asg.split("_")[0]
        try:
            done = {(x.get("email"), x.get("submission_ts"))
                    for x in book.worksheet(tab).get_all_records()}
        except Exception:
            done = set()
        new = [x for x in pending[asg] if x not in done]
        mark = "→ grading" if new else "up to date"
        print(f"  {asg:22s} {len(pending[asg]):>3d} submitted, "
              f"{len(new):>3d} ungraded   {mark}")
        if new:
            todo.append(asg)

    if undecodable:
        print(f"\n  {undecodable} submission(s) whose token could not be read — "
              "these are graded too, and flagged in the sheet.")
        for asg in pending:                      # attribute them to every lecture run
            if asg not in todo:
                todo.append(asg)
        if not pending:
            todo = [a.assignment] if a.assignment else []

    if a.assignment:
        todo = [a.assignment]
        print(f"\n(forced: {a.assignment})")

    if not todo:
        print("\nNothing to do — everything is graded.")
        return 0

    rc = 0
    for asg in todo:
        print(f"\n{'='*60}\n{asg}\n{'='*60}")
        cmd = [sys.executable, os.path.join(HERE, "auto_evaluator_form.py"),
               "--sheet", a.sheet, "--grades-tab", "Grades_" + asg.split("_")[0],
               "--assignment", asg]
        if a.dry_run:
            cmd.append("--dry-run")
        rc |= subprocess.run(cmd, cwd=HERE).returncode
    return rc


if __name__ == "__main__":
    sys.exit(main())
