#!/usr/bin/env python3
"""
Render per-student feedback emails from a Grades tab. PREVIEW ONLY --
this script has no ability to send anything.

    python3 draft_feedback_emails.py L1                 # print to screen
    python3 draft_feedback_emails.py L1 --out drafts/   # one .txt per student

To actually send, take the drafts to your mail client, or use Brightspace.
"""
import argparse, sys, textwrap
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

    L = [f"Hi {first},", ""]
    L += textwrap.wrap("Thanks for submitting the " + TITLES.get(a.tag, a.tag)
                       + " challenge.", 72)
    L += [
         "Your participation is registered — that is what counts for your",
         "participation grade. Everything below is feedback, not a score.", ""]

    if r.get("status") != "GRADED":
        L += ["One small thing: I couldn't read the code you pasted, so I can't",
              "give you feedback on the answers yet. Copy just the line that starts",
              "with UG54:: — not the ==== rules printed around it — and send it",
              "through the form again whenever you get a chance.", "",
              "Your participation still counts. Nothing to worry about.", "",
              "See you in class,", "Alan"]
        return r.get("email", ""), f"UG54 — {a.tag}: thanks, and one small thing", "\n".join(L)

    n_ok = len(oks) - len(wrong)
    if wrong:
        L += [f"On the numbers, you had {n_ok} of {len(oks)}. Worth a second look at:",
              "   " + ", ".join(wrong),
              "The notebook recomputes these, so rerunning it and comparing is the",
              "quickest way to see where it diverged.", ""]
    else:
        L += [f"All {len(oks)} numbers came out right.", ""]

    fb = str(r.get("feedback", "")).strip()
    if fb:
        L += ["On the memo:", ""]
        for line in fb.split(". "):
            if line.strip():
                L += textwrap.wrap(line.strip().rstrip(".") + ".", 69,
                                   initial_indent="   ", subsequent_indent="   ")
                L.append("")
        L.pop()
        L.append("")

    L += ["Bring any questions to office hours, or grab me at the start of class.",
          "", "See you Wednesday,", "Alan"]
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
