#!/usr/bin/env python3
"""
Render per-student feedback emails from a Grades tab. PREVIEW ONLY --
this script has no ability to send anything.

    python3 draft_feedback_emails.py L1                 # print to screen
    python3 draft_feedback_emails.py L1 --out drafts/   # one .txt per student

To actually send, take the drafts to your mail client, or use Brightspace.
"""
import argparse, sys
from pathlib import Path

HERE  = Path(__file__).resolve().parent
SHEET = "UG54 Submissions (Responses)"
TITLES = {"L1": "Lecture 1 — Returns, Excess Returns and the Sharpe Ratio"}

p = argparse.ArgumentParser()
p.add_argument("tag")
p.add_argument("--sheet", default=SHEET)
p.add_argument("--out", default=None)
a = p.parse_args()

import gspread
gc = gspread.service_account(filename=str(HERE / "service_account.json"))
ws = gc.open(a.sheet).worksheet(f"Grades_{a.tag}")
rows = ws.get_all_records()
if not rows:
    sys.exit(f"Grades_{a.tag} is empty.")

def render(r) -> tuple[str, str, str]:
    first = (r.get("name") or "").split(" ")[0] or "there"
    oks   = {k[:-3]: v for k, v in r.items() if k.endswith("_ok")}
    wrong = [q for q, v in oks.items() if str(v).upper() != "TRUE"]

    L = [f"Hi {first},", "", f"Feedback on your {TITLES.get(a.tag, a.tag)} challenge.", ""]

    if r.get("status") != "GRADED":
        L += ["I couldn't read your submission — the pasted code didn't decode.",
              "Copy just the line starting UG54:: (not the ==== rules around it)",
              "and resubmit. No penalty.", "", "— Prof. Moreira"]
        return r.get("email", ""), f"UG54 — {a.tag} challenge: please resubmit", "\n".join(L)

    n_ok = len(oks) - len(wrong)
    L += [f"NUMBERS   {n_ok} of {len(oks)} correct"]
    if wrong:
        L += ["          check: " + ", ".join(wrong),
              "          (the notebook recomputes these — rerun it and compare)"]
    L += ["", f"MEMO      {r.get('memo_score','')}/5", ""]
    for line in str(r.get("feedback", "")).split(". "):
        if line.strip():
            L.append("          " + line.strip().rstrip(".") + ".")
    L += ["", f"OVERALL   {r.get('overall','')}%",
          "          (70% the numbers, 30% the memo)", "",
          "Bring any questions to office hours or the start of Wednesday's class.",
          "", "— Prof. Moreira"]
    return r.get("email", ""), f"UG54 — {a.tag} challenge feedback", "\n".join(L)

out = Path(a.out).expanduser() if a.out else None
if out: out.mkdir(parents=True, exist_ok=True)

for r in rows:
    to, subj, body = render(r)
    if out:
        (out / f"{a.tag}_{(r.get('name') or to).replace(' ','_')}.txt").write_text(
            f"To: {to}\nSubject: {subj}\n\n{body}\n", encoding="utf-8")
    else:
        print("=" * 68)
        print(f"To:      {to}\nSubject: {subj}")
        print("=" * 68)
        print(body)
        print()

print(f"{len(rows)} draft(s) rendered." + (f" -> {out}" if out else " Nothing sent."))
