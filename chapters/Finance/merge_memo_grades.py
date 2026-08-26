#!/usr/bin/env python3
"""
Read the scores written into memos_<L#>.md and merge them into the Grades tab.

    python3 grade.py L1_Returns_AI     # numeric grades + memos_L1.md
    # ...fill in **Score:** and **Feedback:** in memos_L1.md...
    python3 merge_memo_grades.py L1           # push them into the sheet

Overall = 0.7 x numeric + 0.3 x (memo/5).  Rows still marked _/5 are left alone,
so you can grade in batches.
"""
import argparse, re, sys
from pathlib import Path

HERE  = Path(__file__).resolve().parent
SHEET = "UG54 Submissions (Responses)"

p = argparse.ArgumentParser()
p.add_argument("tag", help="L1, L2, ...")
p.add_argument("--sheet", default=SHEET)
p.add_argument("--dry-run", action="store_true")
a = p.parse_args()

mp = HERE / f"memos_{a.tag}.md"
if not mp.exists():
    sys.exit(f"{mp.name} not found -- run grade.py first.")

text = mp.read_text(encoding="utf-8")
blocks = re.split(r"^## \[(\d+)\] (.+?)$", text, flags=re.M)[1:]
graded, ungraded = {}, []
for i in range(0, len(blocks), 3):
    idx, who, body = int(blocks[i]), blocks[i+1].strip(), blocks[i+2]
    sm = re.search(r"\*\*Score:\*\*\s*([0-5])\s*/\s*5", body)
    fm = re.search(r"\*\*Feedback:\*\*\s*(.*?)(?:\n---|\Z)", body, re.S)
    if not sm:
        ungraded.append(who); continue
    graded[idx] = (int(sm.group(1)), (fm.group(1).strip() if fm else ""))

if not graded:
    sys.exit(f"No scores filled in yet in {mp.name} (looking for '**Score:** N/5').")

import gspread
gc   = gspread.service_account(filename=str(HERE / "service_account.json"))
ws   = gc.open(a.sheet).worksheet(f"Grades_{a.tag}")
vals = ws.get_all_values()
hdr  = vals[0]
col  = {h: k for k, h in enumerate(hdr)}
for need in ("numeric_pct", "memo_score", "overall", "feedback", "flag"):
    if need not in col:
        sys.exit(f"Grades tab has no '{need}' column -- re-run grade.py.")

changed = 0
for idx, (score, fb) in sorted(graded.items()):
    r = idx + 1                                   # header occupies row 0
    if r >= len(vals):
        print(f"  ! row {idx} not in the sheet, skipping"); continue
    row = vals[r]
    try:    num = float(row[col["numeric_pct"]] or 0)
    except ValueError: num = 0.0
    overall = round(0.7 * num + 0.3 * (score / 5 * 100), 1)
    row[col["memo_score"]] = score
    row[col["overall"]]    = overall
    row[col["feedback"]]   = fb
    row[col["flag"]]       = str(overall < 50 or score == 0)
    print(f"  {row[col['name']] or row[col['email']]:24s} numeric {num:5.1f}  "
          f"memo {score}/5  ->  overall {overall}")
    changed += 1

print(f"\n{changed} row(s) updated, {len(ungraded)} still ungraded"
      + (f": {', '.join(ungraded)}" if ungraded else ""))
if a.dry_run:
    print("(dry run -- nothing written)")
else:
    ws.update(vals)
    print(f"Written to '{ws.title}'.")
