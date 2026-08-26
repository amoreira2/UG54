#!/usr/bin/env python3
"""
Confirm the service account can reach the submissions Sheet. Run this once,
right after setup, before you rely on any of it.

    python3 check_sheet_access.py
    python3 check_sheet_access.py --sheet-url "https://docs.google.com/spreadsheets/d/..."

Fails loudly and tells you which of the four setup steps went wrong.
"""
import argparse, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
KEY  = HERE / "service_account.json"

p = argparse.ArgumentParser()
p.add_argument("--sheet", default="UG54 Submissions")
p.add_argument("--sheet-url", default=None, help="more reliable than the name")
a = p.parse_args()

if not KEY.exists():
    sys.exit(f"❌ STEP 3 incomplete: {KEY} not found.\n"
             "   Download the service account's JSON key and save it there.")

try:
    email = json.load(open(KEY))["client_email"]
except Exception as e:
    sys.exit(f"❌ {KEY.name} is not a valid service-account key: {e}")
print(f"key file OK — service account is:\n   {email}\n")

try:
    import gspread
except ImportError:
    sys.exit("❌ gspread not installed:  pip install gspread")

gc = gspread.service_account(filename=str(KEY))
try:
    book = gc.open_by_url(a.sheet_url) if a.sheet_url else gc.open(a.sheet)
except Exception as e:
    msg = str(e)
    print(f"❌ Could not open the Sheet.\n   {type(e).__name__}: {msg[:300]}\n")
    if "PERMISSION_DENIED" in msg or "not found" in msg.lower() or "404" in msg:
        print("   Most likely STEP 4: share the Sheet with the address above,\n"
              "   and give it *Editor* (it has to write the grades tab).")
    if "Drive API has not been used" in msg or "drive.googleapis" in msg:
        print("   Or STEP 2: enable the Google Drive API — needed to open a Sheet\n"
              "   by NAME. Passing --sheet-url avoids that entirely.")
    if "Sheets API has not been used" in msg or "sheets.googleapis" in msg:
        print("   Or STEP 2: enable the Google Sheets API.")
    sys.exit(1)

print(f"✅ opened '{book.title}'")
print(f"   url: {book.url}\n")
for ws in book.worksheets():
    print(f"   tab '{ws.title}': {ws.row_count} rows x {ws.col_count} cols")

try:
    recs = book.worksheet("Form Responses 1").get_all_records()
    print(f"\n✅ {len(recs)} response(s) so far")
    if recs:
        cols = list(recs[0].keys())
        print(f"   columns: {cols}")
        for need in ("Submission token",):
            print(f"   {'✅' if need in cols else '❌'} column '{need}' "
                  f"{'found' if need in cols else 'MISSING — the grader needs this exact name'}")
except Exception as e:
    print(f"\n(no 'Form Responses 1' tab yet — that appears after the first submission)  {type(e).__name__}")

print("\n✅ Write access check: creating and deleting a scratch tab…")
try:
    t = book.add_worksheet("_access_test", rows=1, cols=1); book.del_worksheet(t)
    print("✅ Editor access confirmed — grading can write its results back.")
except Exception as e:
    print(f"❌ Read works but WRITE does not: {type(e).__name__}\n"
          "   Re-share the Sheet with the service account as *Editor*, not Viewer.")
    sys.exit(1)
