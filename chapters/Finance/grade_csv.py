#!/usr/bin/env python3
"""
Grade a downloaded Google Form responses CSV. No service account, no API key.

    # Sheet -> File -> Download -> Comma Separated Values
    python3 grade_csv.py ~/Downloads/responses.csv --assignment L1_Returns_AI

Writes two files next to the CSV:
    grades_<L#>.csv   one row per student: which answers were right, and why
    memos_<L#>.md     every memo, with the rubric, ready to be graded by hand
                      or by an assistant that is already reading this repo

Numeric answers are graded here, deterministically, against ANSWER_KEY in
auto_evaluator.py. Memos are NOT graded here on purpose -- see the .md file.
"""
import argparse, csv, sys
from pathlib import Path
from auto_evaluator import ANSWER_KEY, MEMO_RUBRICS, grade_numeric
from auto_evaluator_form import decode_token

p = argparse.ArgumentParser()
p.add_argument("csv_path")
p.add_argument("--assignment", required=True)
p.add_argument("--out-dir", default=None)
a = p.parse_args()

if a.assignment not in ANSWER_KEY:
    sys.exit(f"No answer key for {a.assignment}. Known: {', '.join(sorted(ANSWER_KEY))}")
key = ANSWER_KEY[a.assignment]
src = Path(a.csv_path).expanduser()
out = Path(a.out_dir).expanduser() if a.out_dir else src.parent
tag = a.assignment.split("_")[0]

rows, memos, skipped, broken = [], [], 0, 0
with open(src, newline="", encoding="utf-8-sig") as fh:
    for r in csv.DictReader(fh):
        name  = (r.get("Name") or "").strip()
        email = (r.get("Email Address") or r.get("Email") or "").strip()
        who   = name or email or "(unknown)"
        token = (r.get("Submission token") or r.get("Token") or "").strip()

        payload, err = decode_token(token)
        if err:
            broken += 1
            rows.append({"name": name, "email": email, "status": "BAD TOKEN",
                         "correct": 0, "out_of": len(key), "pct": 0, "detail": err})
            continue
        if payload.get("assignment") != a.assignment:
            skipped += 1
            continue

        res = grade_numeric(payload["answers"], key)
        ok  = sum(1 for v in res.values() if v["correct"])
        rows.append({
            "name": name, "email": email, "status": "graded",
            "correct": ok, "out_of": len(res), "pct": round(ok / len(res) * 100),
            "detail": "; ".join(f"{q}: {v['reason']}" for q, v in res.items() if not v["correct"]) or "all correct",
            **{f"{q}_ok": v["correct"] for q, v in res.items()},
        })
        memos.append((who, payload.get("memo", "").strip()))

if not rows:
    sys.exit(f"No {a.assignment} submissions in {src.name}"
             + (f" ({skipped} were for other lectures)" if skipped else ""))

hdr = sorted({k for r in rows for k in r}, key=lambda k: (k not in
      ("name","email","status","correct","out_of","pct","detail"), k))
gp = out / f"grades_{tag}.csv"
with open(gp, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=hdr); w.writeheader()
    for r in rows: w.writerow({k: r.get(k, "") for k in hdr})

mp = out / f"memos_{tag}.md"
with open(mp, "w", encoding="utf-8") as fh:
    fh.write(f"# Memos to grade — {a.assignment}\n\nScore each 0–5 against the rubric.\n\n")
    fh.write("## Rubric\n\n```\n" + (MEMO_RUBRICS.get(a.assignment, "(no rubric)")).strip() + "\n```\n\n---\n\n")
    for who, m in memos:
        fh.write(f"## {who}\n\n{m or '_(no memo submitted)_'}\n\n**Score:** _/5\n**Feedback:**\n\n---\n\n")

graded = [r for r in rows if r["status"] == "graded"]
print(f"{len(graded)} graded, {broken} bad token(s), {skipped} for other lectures\n")
print(f"{'student':22s}{'numeric':>9s}   what went wrong")
print("-" * 78)
for r in sorted(rows, key=lambda r: r["pct"]):
    print(f"{(r['name'] or r['email'])[:20]:22s}{r['correct']}/{r['out_of']:<7}   {r['detail'][:44]}")
if graded:
    print(f"\nclass average on the numbers: {sum(r['pct'] for r in graded)/len(graded):.0f}%")
print(f"\n  {gp}\n  {mp}")
