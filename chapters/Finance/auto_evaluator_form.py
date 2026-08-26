"""
Auto-evaluator (paste-string variant).

Reads a Google Sheet that's the destination of a Google Form. Each row
is one student submission containing a base64-encoded JSON payload they
pasted from the notebook.

This is dramatically simpler than the notebook-execution approach:
  - No file uploads
  - No notebook execution
  - No path issues
  - The payload is self-validating (checksum + base64)
  - Memo is graded by Claude; numeric answers by direct comparison

Setup:
    pip install gspread google-auth anthropic
    # Place a service-account JSON at ./service_account.json
    # Share the destination Sheet with the service-account email
    export ANTHROPIC_API_KEY=sk-...

Usage:
    python auto_evaluator_form.py \\
        --sheet "UG54 Submissions" \\
        --responses-tab "Form Responses 1" \\
        --grades-tab "Grades_FactorModels" \\
        --assignment FactorModels_AI
"""

import argparse
import base64
import hashlib
import json
import sys
from datetime import datetime

def decode_token(token: str) -> tuple[dict, str | None]:
    """Decode UG54::<checksum>::<base64> → payload dict. Returns (payload, error)."""
    token = token.strip()
    if not token.startswith("UG54::"):
        return {}, f"Bad prefix (got: {token[:20]!r})"
    try:
        _, checksum, encoded = token.split("::", 2)
    except ValueError:
        return {}, "Token doesn't split into 3 parts"
    try:
        blob = base64.b64decode(encoded.encode()).decode()
    except Exception as e:
        return {}, f"Base64 decode failed: {e}"
    expected = hashlib.sha256(blob.encode()).hexdigest()[:8]
    if expected != checksum:
        return {}, f"Checksum mismatch (got {checksum}, expected {expected}) — payload tampered or truncated"
    try:
        return json.loads(blob), None
    except Exception as e:
        return {}, f"JSON parse failed: {e}"


def main():
    # Lazy imports — only needed when actually running, not when testing decode_token
    import os
    import gspread
    from auto_evaluator import ANSWER_KEY, MEMO_RUBRICS, grade_numeric, grade_wrds_tour

    p = argparse.ArgumentParser()
    p.add_argument("--sheet", required=True, help="Google Sheet name")
    p.add_argument("--responses-tab", default="Form Responses 1")
    p.add_argument("--grades-tab", required=True, help="Tab to write grades into (created if missing)")
    p.add_argument("--assignment", required=True)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    if args.assignment not in ANSWER_KEY:
        sys.exit(f"No answer key for {args.assignment}")
    key = ANSWER_KEY[args.assignment]

    gc = gspread.service_account(filename="service_account.json")
    book = gc.open(args.sheet)
    responses = book.worksheet(args.responses_tab).get_all_records()

    # Find or create the grades tab
    try:
        grades_ws = book.worksheet(args.grades_tab)
    except gspread.WorksheetNotFound:
        grades_ws = book.add_worksheet(args.grades_tab, rows=200, cols=20)

    # Memos are graded by the Anthropic API when a key is present. Without one
    # they are written to a markdown file next to the rubric, to be graded by
    # hand or by an assistant already reading this repo. Numeric answers are
    # always graded here, deterministically.
    use_api = bool(os.environ.get("ANTHROPIC_API_KEY"))
    client = None
    if use_api:
        from anthropic import Anthropic
        from auto_evaluator import grade_memo
        client = Anthropic()
    else:
        print("No ANTHROPIC_API_KEY — numeric answers graded here, "
              "memos written out for grading.\n")
    rows, memos = [], []
    skipped = 0

    for resp in responses:
        # Expected columns from the Google Form: Timestamp, Email, Token, ...
        email = resp.get("Email Address") or resp.get("Email") or "(unknown)"
        name  = resp.get("Name") or ""
        token = resp.get("Submission token") or resp.get("Token") or ""
        ts = resp.get("Timestamp", "")

        payload, err = decode_token(token)
        if err:
            rows.append({
                "ts": ts, "name": name, "email": email, "status": "DECODE_ERROR",
                "error": err, "numeric_pct": 0, "memo_score": 0, "overall": 0,
                "flag": True,
            })
            print(f"❌ {email}: {err}")
            continue

        # One form serves the whole term, so the sheet holds every lecture's
        # submissions. Rows for other lectures are not errors -- skip them.
        if payload.get("assignment") != args.assignment:
            skipped += 1
            continue

        if key == "_dynamic_" and args.assignment == "WRDS_Tour_AI":
            numeric = grade_wrds_tour(payload["answers"])
        else:
            numeric = grade_numeric(payload["answers"], key)
        memo_txt = payload.get("memo", "")
        if use_api:
            memo_grade = grade_memo(client, memo_txt, args.assignment)
        else:
            memo_grade = {"score": "", "picked_fund": "", "feedback": "(graded separately)"}
            memos.append((name or email, memo_txt.strip()))

        n_ok = sum(1 for r in numeric.values() if r["correct"])
        pct = n_ok / len(numeric) * 100
        if use_api:
            overall = round(0.7 * pct + 0.3 * (memo_grade["score"] / 5 * 100), 1)
            flag = overall < 50 or memo_grade["score"] == 0
        else:
            overall, flag = "", pct < 50

        rows.append({
            "ts": ts, "name": name, "email": email, "status": "GRADED",
            "submission_ts": payload.get("ts", ""),
            "numeric_pct": round(pct, 1),
            "memo_score": memo_grade["score"],
            "overall": overall,
            "flag": flag,
            "feedback": memo_grade["feedback"],
            **{f"{q}_ok": r["correct"] for q, r in numeric.items()},
        })
        who = name or email
        if use_api:
            print(f"✅ {who}: numeric={pct:.0f}%  memo={memo_grade['score']}/5  overall={overall:.0f}")
        else:
            print(f"✅ {who}: numeric={pct:.0f}%")

    if skipped:
        print(f"\n(skipped {skipped} submission(s) for other lectures)")
    if not rows:
        print(f"No submissions found for {args.assignment}.")
        return

    if args.dry_run:
        print(f"\n(dry run) Would write {len(rows)} rows.")
        return

    # Write to the grades tab
    header = list(rows[0].keys())
    # Pad rows so they all have the same columns
    for r in rows:
        for h in header:
            r.setdefault(h, "")
    grades_ws.clear()
    grades_ws.update([header] + [[r[h] for h in header] for r in rows])
    print(f"\n✅ Wrote {len(rows)} grades to '{args.grades_tab}'")

    if memos:
        from pathlib import Path
        mp = Path(__file__).resolve().parent / f"memos_{args.assignment.split('_')[0]}.md"
        with open(mp, "w", encoding="utf-8") as fh:
            fh.write(f"# Memos to grade — {args.assignment}\n\nScore each 0–5 "
                     "against the rubric, then paste the scores into the "
                     f"'{args.grades_tab}' tab.\n\n## Rubric\n\n```\n"
                     + MEMO_RUBRICS.get(args.assignment, "(no rubric)").strip()
                     + "\n```\n\n---\n\n")
            for who, m in memos:
                fh.write(f"## {who}\n\n{m or '_(no memo submitted)_'}\n\n"
                         "**Score:** _/5\n**Feedback:**\n\n---\n\n")
        print(f"✅ Wrote {len(memos)} memo(s) to {mp.name} — grade these next")

    flagged = [r for r in rows if r["flag"]]
    if flagged:
        print(f"\n🚩 {len(flagged)} flagged for review:")
        for r in flagged:
            print(f"   {r['email']}: {r['status']} ({r.get('error') or 'low score'})")


if __name__ == "__main__":
    main()
