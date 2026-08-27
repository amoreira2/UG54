"""
Append a unified Final Challenge + Submission cell to IntrotoReturns_c_AI.ipynb.

The existing notebook has 4 exercises but no submission cell — students
can practice but can't submit a graded artifact. This patch inserts:
  - A Final Challenge section (SPY 2010-2024 analysis)
  - A submission cell that bundles answers into the standard token
"""

import json
from pathlib import Path

NB = Path(__file__).parent / "IntrotoReturns_c_AI.ipynb"


def md(text):
    return {"cell_type": "markdown", "metadata": {},
            "source": text.splitlines(keepends=True)}


def code(text):
    return {"cell_type": "code", "execution_count": None, "metadata": {},
            "outputs": [], "source": text.splitlines(keepends=True)}


nb = json.loads(NB.read_text())

# New cells to insert BEFORE the Key Takeaways section
new_cells = []

new_cells.append(md("""---

## 🎯 Final Challenge: How Stable is SPY's Sharpe Ratio? <a id="challenge"></a>

> **Setup.** You're advising a client who plans to put their entire retirement
> in SPY. They've heard "stocks return 10% per year" and figure that's enough.
> Pull SPY's history from 2010-01-01 to 2024-12-31, compute the standard
> risk-adjusted statistics, and decide whether the 10% number is reliable.

You may use AI freely. The skill being tested: writing the spec, auditing
the output, and turning numbers into a recommendation."""))

new_cells.append(code("""# Load SPY data from the same Yahoo / Fama-French sources we used earlier
import yfinance as yf
import pandas_datareader.data as pdr

spy = yf.download('SPY', start='2010-01-01', end='2024-12-31',
                  auto_adjust=True, progress=False)['Close']
spy_ret = spy.pct_change().dropna()

ff = pdr.DataReader('F-F_Research_Data_Factors_Daily', 'famafrench',
                    start='2010-01-01', end='2024-12-31')[0] / 100
ff.index = pd.to_datetime(ff.index)

# Align and compute excess returns
spy_ret.index = pd.to_datetime(spy_ret.index)
merged = pd.concat([spy_ret.rename('spy'), ff['RF'].rename('rf')], axis=1).dropna()
merged['spy_excess'] = merged['spy'] - merged['rf']
print(f"Loaded {len(merged)} trading days, {merged.index.min().date()} to {merged.index.max().date()}")
merged.head(3)"""))

new_cells.append(md("""### The required computations

> **📌 Required variable names** (the submission cell looks for these):
> ```python
> spy_annual_mean      = ____   # SPY's annualized TOTAL return (decimal, e.g. 0.13)
> spy_annual_vol       = ____   # annualized vol of total returns
> spy_annual_sharpe    = ____   # annualized Sharpe on EXCESS returns
> spy_worst_year       = ____   # worst calendar-year total return (e.g. -0.18 for -18%)
> spy_best_year        = ____   # best calendar-year total return
> spy_negative_years   = ____   # count of years with negative total return
> ```"""))

new_cells.append(code("""# Your work here (annualization, calendar-year aggregation)


# Required outputs:
spy_annual_mean    = ____
spy_annual_vol     = ____
spy_annual_sharpe  = ____
spy_worst_year     = ____
spy_best_year      = ____
spy_negative_years = ____

print(f"Annual mean (total):  {spy_annual_mean:.2%}")
print(f"Annual vol:           {spy_annual_vol:.2%}")
print(f"Annual Sharpe (excess):{spy_annual_sharpe:.2f}")
print(f"Worst year:           {spy_worst_year:.2%}")
print(f"Best year:            {spy_best_year:.2%}")
print(f"Negative years:       {spy_negative_years} of {(2024-2010+1)}")"""))

new_cells.append(md("""### The Memo

Write a **single paragraph** (max 5 sentences) advising your client.

1. Is "10% per year in SPY" a reasonable expectation based on the 2010-2024 sample?
2. What's the realistic downside they should plan for?
3. What's the one caveat (sample period, regime, etc.) that could make you wrong?"""))

new_cells.append(code("""MEMO = \"\"\"
Write your 5-sentence-max memo here. Don't delete the triple quotes.
\"\"\"
print(MEMO)"""))

new_cells.append(md("""---

## 📤 Submission <a id="submit"></a>

Run the cell below. Copy the line starting with `UG54::` into the submission
form: **https://forms.gle/YOUR_FORM_LINK_HERE**"""))

new_cells.append(code("""# === 📤 SUBMISSION CELL — Run this last ===
import json, base64, hashlib, datetime as dt

required = [
    "spy_annual_mean", "spy_annual_vol", "spy_annual_sharpe",
    "spy_worst_year", "spy_best_year", "spy_negative_years",
    "MEMO",
]
missing = [v for v in required if v not in dir()]
if missing:
    raise NameError(f"\\n❌ Missing: {missing}")

payload = {
    "assignment": "IntrotoReturns_AI",
    "ts": dt.datetime.utcnow().isoformat(timespec="seconds") + "Z",
    "answers": {k: float(eval(k)) for k in required if k != "MEMO"},
    "memo": MEMO.strip(),
}
blob = json.dumps(payload, sort_keys=True)
checksum = hashlib.sha256(blob.encode()).hexdigest()[:8]
token = f"UG54::{checksum}::{base64.b64encode(blob.encode()).decode()}"

print("=" * 72)
print("📋  COPY THE LINE BELOW AND PASTE INTO THE SUBMISSION FORM")
print("=" * 72)
print(token)
print("=" * 72)
print(f"\\nLength: {len(token)} chars")"""))

# Find insertion point: just before the "## 🧠 Key Takeaways" cell
insert_at = None
for i, c in enumerate(nb["cells"]):
    src = "".join(c["source"]) if isinstance(c["source"], list) else c["source"]
    if "Key Takeaways" in src and c["cell_type"] == "markdown":
        insert_at = i
        break

if insert_at is None:
    # Fallback: append at end
    insert_at = len(nb["cells"])

nb["cells"] = nb["cells"][:insert_at] + new_cells + nb["cells"][insert_at:]

NB.write_text(json.dumps(nb, indent=1))
print(f"✅ Inserted {len(new_cells)} cells at position {insert_at}. New total: {len(nb['cells'])} cells.")
