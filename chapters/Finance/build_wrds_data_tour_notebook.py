"""
Build WRDS_Data_Tour_AI.ipynb — Lecture 3, Week 2.

Goal: students directly use WRDS. Forces account setup + first login.

Pedagogical engine: for each major data pull, show TWO prompts —
  - 🔴 LOOSE prompt that an AI will mishandle (silent bugs, wrong tables,
       missing filters, SELECT *, etc.)
  - 🟢 PRECISE prompt that produces working SQL

Students run the precise version, see the output, and learn the pattern.

Topic arc:
  1. Why WRDS (vs FRED/Yahoo)
  2. Connecting to WRDS for the first time
  3. The query workflow (Specify -> Implement -> Validate, applied to SQL)
  4. Demo 1: Single stock pull (AAPL monthly) — loose vs precise
  5. The retx trick + share issuance
  6. Demo 2: Cross-section pull — loose vs precise
  7. What's in the cross-section: share codes, exchanges, negative prices
  8. Demo 3: Compustat fundamentals — loose vs precise
  9. Compute book/market, value premium teaser
  10. Final Challenge: pull your own stock + compute simple metrics
  11. Submission
"""

import json
from pathlib import Path

OUT = Path(__file__).parent / "WRDS_Data_Tour_AI.ipynb"


def md(text):
    return {"cell_type": "markdown", "metadata": {},
            "source": text.splitlines(keepends=True)}


def code(text):
    return {"cell_type": "code", "execution_count": None, "metadata": {},
            "outputs": [], "source": text.splitlines(keepends=True)}


cells = []

# ─── Title ────────────────────────────────────────────────────────────
cells.append(md("""# WRDS — Pulling Data Like a Pro
## 🎯 Learning Objectives

By the end of this notebook, you will be able to:

1. **Connect to WRDS from Colab** and execute SQL queries against CRSP and Compustat
2. **Write precise SQL prompts** — telling AI exactly which table, which columns, which filters
3. **Distinguish a good prompt from a bad one** — and predict what bugs each will produce
4. **Pull a stock's full CRSP history** — returns, prices, shares outstanding, dividends
5. **Pull and join Compustat fundamentals** to compute book-to-market and other ratios
6. **Recognize and handle CRSP quirks**: share codes, negative prices, permno vs ticker"""))

cells.append(md("""## 📋 Table of Contents

1. [Setup](#setup)
2. [Why WRDS?](#why)
3. [Your First WRDS Connection](#connect)
4. [Querying WRDS: Loose vs Precise Prompts](#workflow)
5. [Demo 1 — Single Stock (AAPL Monthly)](#demo1)
6. [The `retx` Trick + Share Issuance](#retx)
7. [Demo 2 — A Cross-Section](#demo2)
8. [What's IN the Cross-Section: Share Codes, Exchanges, Negative Prices](#xs)
9. [Demo 3 — Compustat Fundamentals](#demo3)
10. [Book-to-Market and the Value Premium Teaser](#value)
11. [🎯 Final Challenge: Pull YOUR Own Stock](#challenge)
12. [Submission](#submit)
13. [Key Takeaways](#takeaways)"""))

# ─── Setup ────────────────────────────────────────────────────────────
cells.append(md("""---

## 🛠️ Setup <a id="setup"></a>

We'll need `wrds` (the official client library), plus the usual `pandas` /
`numpy` / `matplotlib` stack."""))

cells.append(code("""#@title Setup — run this first
# Uncomment in Colab; on your local machine it's likely already installed
# !pip install wrds -q

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
%matplotlib inline

plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = [10, 5]
plt.rcParams['font.size'] = 11

import warnings
warnings.filterwarnings('ignore')

print("✅ Libraries loaded")"""))

# ─── Why WRDS ─────────────────────────────────────────────────────────
cells.append(md("""---

## Why WRDS? <a id="why"></a>

You have three data tools at your disposal in this class:

| Source | Strengths | Limits |
|--------|-----------|--------|
| **FRED** (St. Louis Fed) | Free macro: GDP, CPI, Fed Funds, yields | Macro only, no stocks |
| **Yahoo Finance** (yfinance) | Free daily prices, easy in Colab | Survivorship-biased, inconsistent splits/dividends, no fundamentals |
| **WRDS** (CRSP + Compustat) | Survivorship-free, standardized, gold standard for research | Institutional access required |

NYU pays for WRDS. **You're going to use it today.** You should have your account
approved by now — if not, raise your hand and we sort it out before continuing."""))

# ─── Connect ──────────────────────────────────────────────────────────
cells.append(md("""---

## Your First WRDS Connection <a id="connect"></a>

Two ways to authenticate:

| Method | When to use |
|--------|-------------|
| **Interactive prompt** | First time in Colab — type password when asked |
| **`.pgpass` file** | If you ran it once and saved credentials (persists between sessions on local machine, not in Colab) |

Run the cell below. The first time you run it in a Colab session, it asks
for your **WRDS username** and **password**. After that, it's a `db` object
you can query."""))

cells.append(code("""import wrds

# Replace 'your-netid-here' with your WRDS username
# (Often this is your NYU NetID, but check your WRDS welcome email)
db = wrds.Connection(wrds_username='your-netid-here')

print("✅ Connected to WRDS")"""))

cells.append(md("""### Sanity check: what tables are available?

WRDS exposes hundreds of databases — CRSP, Compustat, IBES, OptionMetrics,
TAQ, etc. Each is a **schema**; tables live under those schemas."""))

cells.append(code("""# How many tables in the crsp schema?
crsp_tables = db.list_tables(library='crsp')
print(f"CRSP schema has {len(crsp_tables)} tables.")
print(f"\\nThe ones we'll use today:")
for t in ['msf', 'dsf', 'stocknames']:
    if t in crsp_tables:
        print(f"  ✅ crsp.{t}")
    else:
        print(f"  ❌ crsp.{t} not found")"""))

cells.append(md("""> **💡 Key tables to know**
>
> | Table | What it is |
> |-------|------------|
> | `crsp.msf` | Monthly stock file — one row per (permno, month-end) |
> | `crsp.dsf` | Daily stock file — same but daily (huge — careful with date ranges) |
> | `crsp.stocknames` | Lookup: ticker ↔ permno ↔ name over time |
> | `comp.funda` | Compustat annual fundamentals — revenue, assets, equity, etc. |
> | `comp.fundq` | Compustat quarterly fundamentals |
> | `crsp.ccmxpf_lnkhist` | Link table — joins CRSP permno to Compustat gvkey |

> **⚠️ If the connection fails**
>
> Possible reasons:
> 1. **Account not yet approved** — check email from WRDS, contact NYU IT
> 2. **Wrong username** — usually NetID, sometimes different; check WRDS welcome email
> 3. **Network blocking** — corporate VPNs sometimes block port 9737
>
> **Emergency fallback for today only:** if WRDS won't connect, run the
> hidden cell at the bottom of this notebook called "FALLBACK_LOAD_CSVS" — it
> loads pre-pulled samples so you can still follow along. Then sort out your
> WRDS access after class."""))

# ─── Query workflow ───────────────────────────────────────────────────
cells.append(md("""---

## Querying WRDS: Loose vs Precise Prompts <a id="workflow"></a>

Querying WRDS is mostly writing **SQL** against PostgreSQL. You can have AI
write the SQL — but only if you give it enough to work with. **This is
where Specify → Implement → Validate matters most.**

A loose prompt produces SQL with predictable bugs:
- Wrong table name (the AI guesses)
- `SELECT *` (slow, fetches columns you don't need)
- Missing filters → query returns millions of rows or times out
- Wrong date format → empty result
- Ticker-based filter instead of permno → wrong stock (tickers reuse!)

A precise prompt produces SQL that works the first time:
- Names the exact table
- Names the columns you need
- Names the filters with units (date format, integer codes)
- Names the order

> **🤖 AI-Era Insight**
>
> When you ask AI for SQL against WRDS, you're effectively delegating the
> *schema knowledge* to the AI. **AI does not actually know the WRDS schema
> well** — it's seen many SQL queries online, but the specific column names,
> data types, and join patterns of CRSP/Compustat are quirky. You have to
> tell it. We'll show the pattern three times today."""))

# ─── Demo 1 ───────────────────────────────────────────────────────────
cells.append(md("""---

## Demo 1 — Single Stock (AAPL Monthly) <a id="demo1"></a>

**Goal:** pull AAPL's monthly returns from 2010 to 2024.

### 🔴 Loose prompt — what NOT to do

> *"Get Apple's stock returns from WRDS"*

**What an AI is likely to produce:**

```python
data = db.raw_sql("SELECT * FROM crsp.msf WHERE ticker='AAPL'")
```

**The bugs:**
- ❌ `SELECT *` pulls every column — wasteful, slow
- ❌ Filtering by `ticker='AAPL'` works for AAPL, but tickers can change or be reused. **`permno` is the only stable ID** — but AI doesn't know that unless you say it.
- ❌ No date range — pulls AAPL's *entire* history (40+ years), most of which you don't need
- ❌ No `ORDER BY` — results come back in arbitrary order
- ❌ No `date_cols` argument — date column comes back as a string, not a datetime

### 🟢 Precise prompt — the pattern that works

> *"Using `db.raw_sql`, query `crsp.msf` for permno=14593 (AAPL) between
> 2010-01-01 and 2024-12-31. Return only these columns: date, ret, retx, prc,
> shrout, ticker. Order by date. Pass `date_cols=['date']` to parse the date
> column."*

The precise version names:
1. The exact function (`db.raw_sql`)
2. The exact table (`crsp.msf`)
3. The exact filter (`permno=14593`, not ticker)
4. The exact columns
5. The exact date range
6. The ordering
7. The date parsing"""))

cells.append(code("""# 🟢 The precise version — this is the canonical pattern
aapl = db.raw_sql(\"\"\"
    SELECT date, ret, retx, prc, shrout, ticker
    FROM crsp.msf
    WHERE permno = 14593
      AND date BETWEEN '2010-01-01' AND '2024-12-31'
    ORDER BY date
\"\"\", date_cols=['date'])

print(f"AAPL monthly: {len(aapl)} months, {aapl['date'].min().date()} to {aapl['date'].max().date()}")
aapl.head(3)"""))

cells.append(md("""> **💡 How do you find a stock's permno?**
>
> Use `crsp.stocknames`. We'll do this in the challenge — but for famous
> stocks you'll see permnos in academic papers (AAPL=14593, MSFT=10107,
> JPM=47896 are common ones to memorize)."""))

# ─── retx trick ───────────────────────────────────────────────────────
cells.append(md("""---

## The `retx` Trick + Share Issuance <a id="retx"></a>

CRSP gives you BOTH `ret` (with dividends) and `retx` (without). The
difference is the dividend yield for that month:

$$\\text{dividend yield}_t = \\text{ret}_t - \\text{retx}_t$$

This is a useful CRSP feature — most other data sources give you only one
return number. Let's extract Apple's dividend history:"""))

cells.append(code("""aapl['div_yield'] = aapl['ret'] - aapl['retx']
div_months = aapl[aapl['div_yield'] > 0.001].copy()
print(f"Months with dividend: {len(div_months)} of {len(aapl)}")

# Quick plot
fig, ax = plt.subplots(figsize=(12, 3.5))
ax.scatter(aapl['date'], aapl['div_yield'] * 100, s=12, alpha=0.7)
ax.set_ylabel('Monthly dividend yield (%)')
ax.set_title("AAPL dividend yield by month — notice when Tim Cook reinstated dividends",
             fontweight='bold')
plt.tight_layout(); plt.show()"""))

cells.append(md("""### Share issuance from the data

Compare price growth to market cap growth. The difference is share
issuance (or buybacks, if negative)."""))

cells.append(code("""aapl['abs_prc'] = aapl['prc'].abs()
aapl['mktcap'] = aapl['abs_prc'] * aapl['shrout'] / 1000  # millions

p0, p1 = aapl['abs_prc'].iloc[0],  aapl['abs_prc'].iloc[-1]
m0, m1 = aapl['mktcap'].iloc[0],   aapl['mktcap'].iloc[-1]
s0, s1 = aapl['shrout'].iloc[0],   aapl['shrout'].iloc[-1]

print(f"AAPL 2010-01 → 2024-12:")
print(f"  Price growth:    {p1/p0:>6.2f}x")
print(f"  Mktcap growth:   {m1/m0:>6.2f}x")
print(f"  Share count:     {s1/s0:>6.2f}x   ← <1 means NET BUYBACKS")
print(f"  ⇒ Apple repurchased {(1 - s1/s0)*100:.1f}% of its shares over the period")"""))

cells.append(md("""> **🤔 The buyback story**
>
> Apple's market cap grew far faster than its share count fell. Looking at
> price alone misses how much of the per-share growth came from buybacks
> versus from business growth. Decomposing the two requires the share-count
> series — which is why `shrout` over time is one of CRSP's underrated
> columns."""))

# ─── Demo 2 ───────────────────────────────────────────────────────────
cells.append(md("""---

## Demo 2 — A Cross-Section <a id="demo2"></a>

**Goal:** pull every US common stock that was trading at the end of June 2020.

### 🔴 Loose prompt

> *"Get all stocks from CRSP for June 2020"*

**What AI is likely to produce:**

```python
data = db.raw_sql("SELECT * FROM crsp.msf WHERE date BETWEEN '2020-06-01' AND '2020-06-30'")
```

**The bugs:**
- ❌ `BETWEEN '2020-06-01' AND '2020-06-30'` — but CRSP monthly dates are
   *always month-end*. This filter may return **zero rows** (depending on
   whether 6/30/2020 falls in the range).
- ❌ No `shrcd` filter — you'll get ETFs (18), ADRs (71), closed-end funds (73)
  mixed in with common stock
- ❌ `SELECT *` again
- ❌ No `date_cols`

### 🟢 Precise prompt

> *"Query `crsp.msf` for the specific month-end date 2020-06-30. Filter to
> `shrcd IN (10, 11)` for US common stocks only. Return permno, ticker, prc,
> shrout, ret, exchcd. Pass `date_cols=['date']`."*"""))

cells.append(code("""xs = db.raw_sql(\"\"\"
    SELECT permno, ticker, prc, shrout, ret, exchcd
    FROM crsp.msf
    WHERE date = '2020-06-30'
      AND shrcd IN (10, 11)
\"\"\", date_cols=[])

print(f"Universe on 2020-06-30: {len(xs):,} US common stocks")
xs.head(3)"""))

# ─── What's in the cross-section ──────────────────────────────────────
cells.append(md("""---

## What's IN the Cross-Section: Share Codes, Exchanges, Negative Prices <a id="xs"></a>

Three things to know about the CRSP universe before you start using it:

### Share codes (`shrcd`) define the universe

| `shrcd` | What it is |
|---------|------------|
| 10 | US common stock — hasn't paid a dividend yet |
| 11 | US common stock — pays dividends (most firms) |
| 12 | US common stock — incorporated outside US |
| 18 | ETF |
| 71 | ADR (foreign stock listed in US) |
| 73 | Closed-end fund |

> **The academic-finance default is `shrcd IN (10, 11)`.** Use this unless you
> have a specific reason not to.

### Exchanges (`exchcd`)"""))

cells.append(code("""print("Exchange breakdown:")
exch_names = {1: 'NYSE', 2: 'AMEX', 3: 'NASDAQ'}
for exch, count in xs['exchcd'].value_counts().items():
    print(f"  {exch_names.get(exch, f'code {exch}'):>6}: {count:>4}")"""))

cells.append(md("""### Negative prices — a CRSP convention

CRSP marks `prc` **negative** when there was no actual trade at the close —
the value is the bid-ask midpoint instead. Common for thinly-traded small-caps."""))

cells.append(code("""neg = xs[xs['prc'] < 0]
print(f"Stocks with negative-flagged prices: {len(neg)} ({len(neg)/len(xs):.1%})")
print("\\nBy exchange:")
for exch in [1, 2, 3]:
    total = (xs['exchcd'] == exch).sum()
    neg_count = ((xs['exchcd'] == exch) & (xs['prc'] < 0)).sum()
    name = exch_names.get(exch, str(exch))
    print(f"  {name:>6}: {neg_count:>3} of {total:>4}  ({neg_count/max(total,1):.1%})")"""))

cells.append(md("""> **⚠️ AMEX dominates because it hosts small, illiquid names**
>
> NYSE and NASDAQ require minimum-liquidity to stay listed. AMEX doesn't.
> Stocks that don't trade on their closing day get a midpoint quote instead
> of a transaction price — hence the negative flag.
>
> **What to do:** use `abs(prc)` for the value; consider whether to drop
> negative-flagged rows entirely. Common research papers exclude them; others
> use them with a footnote. **Your call. But you have to make one.**"""))

# ─── Demo 3 ───────────────────────────────────────────────────────────
cells.append(md("""---

## Demo 3 — Compustat Fundamentals <a id="demo3"></a>

**Goal:** pull Apple's annual revenue, total assets, and book equity from Compustat.

This is the hardest of the three demos because Compustat uses its OWN identifier
(`gvkey`), not CRSP's `permno`. You either look up the gvkey directly, or use the
CRSP-Compustat link table to join.

### 🔴 Loose prompt

> *"Get Apple's revenue and assets from Compustat"*

**What AI is likely to produce:**

```python
data = db.raw_sql("SELECT * FROM comp.funda WHERE tic = 'AAPL'")
```

**The bugs:**
- ❌ `tic` in `comp.funda` is the *most recent* ticker. Reliable for AAPL
  today; fails for any firm whose ticker has changed (which is many).
- ❌ `comp.funda` has multiple rows per fiscal year for the same company,
  because it stores multiple data formats. **Always filter** `indfmt='INDL'`,
  `datafmt='STD'`, `popsrc='D'`, `consol='C'`. Without these you get ~4x
  the rows.
- ❌ `SELECT *` — Compustat has ~700 columns. You don't need all of them.
- ❌ No date range — pulls 40 years.

### 🟢 Precise prompt

> *"Query `comp.funda` for Apple. AAPL's Compustat `gvkey` is `'001690'`
> (note: 6-character zero-padded string). Filter to indfmt='INDL',
> datafmt='STD', popsrc='D', consol='C' to deduplicate. Return: datadate,
> fyear, revt (revenue, $M), at (total assets, $M), ceq (book common equity,
> $M). Order by datadate. Pass date_cols=['datadate']."*"""))

cells.append(code("""aapl_fund = db.raw_sql(\"\"\"
    SELECT datadate, fyear, revt, at, ceq
    FROM comp.funda
    WHERE gvkey = '001690'
      AND indfmt = 'INDL'
      AND datafmt = 'STD'
      AND popsrc = 'D'
      AND consol = 'C'
    ORDER BY datadate
\"\"\", date_cols=['datadate'])

print(f"AAPL fundamentals: {len(aapl_fund)} fiscal years")
aapl_fund.tail(5)"""))

cells.append(md("""> **💡 The 4-filter pattern is the most common Compustat foot-gun**
>
> Forgetting `indfmt`, `datafmt`, `popsrc`, `consol` is THE most common bug
> in Compustat queries. Your data will look fine — just 4x too many rows per
> firm-year. Your subsequent analysis will be silently wrong. Keep these
> four filters handy for any Compustat query."""))

# ─── Value premium ────────────────────────────────────────────────────
cells.append(md("""---

## Book-to-Market and the Value Premium Teaser <a id="value"></a>

Now combine: AAPL's **book equity** (from Compustat) divided by its **market
equity** (from CRSP) = the book-to-market ratio.

For most of Apple's history this ratio has been very *low* — Apple is a
classic "growth" stock (priced far above book value). Fama and French's
famous result: high-B/M ("value") stocks earn ~3-5%/year more than low-B/M
("growth") stocks, on average, over decades."""))

cells.append(code("""# Compute AAPL's recent book/market
# Book equity: latest fiscal year from Compustat
latest = aapl_fund.iloc[-1]
book_equity_M = latest['ceq']
print(f"AAPL fiscal year {int(latest['fyear'])}: book equity = ${book_equity_M:,.0f}M")

# Market equity: latest from CRSP
latest_mkt = aapl.iloc[-1]
market_equity_M = latest_mkt['mktcap']
print(f"AAPL market cap as of {latest_mkt['date'].date()}: ${market_equity_M:,.0f}M")

bm = book_equity_M / market_equity_M
print(f"\\nBook-to-Market ratio: {bm:.4f}")
print(f"  → Apple is priced at {1/bm:.1f}x book value")
print(f"  → That makes it a deep 'growth' stock by F-F standards")"""))

cells.append(md("""> **📌 The teaser**
>
> A high B/M ratio (cheap relative to book) historically earns higher returns.
> Apple — at 0.05ish B/M — has the opposite. **We'll spend Weeks 8-9 unpacking
> exactly how to test, exploit, and worry about this pattern.** Today you just
> learned how to compute it for any firm in WRDS."""))

# ─── Final Challenge ──────────────────────────────────────────────────
cells.append(md("""---

## 🎯 Final Challenge: Pull YOUR Own Stock <a id="challenge"></a>

> **The point of this challenge** is to verify you can independently use WRDS
> end-to-end. Pick a stock (NOT AAPL), look up its permno, pull 5 years of
> data, and report some basic facts.

### Step 1 — Find your stock's permno

Pick a ticker. Examples: MSFT, JPM, KO, BA, F, TSLA, NVDA, JNJ.

Use `crsp.stocknames` to look up the permno. The right query:"""))

cells.append(code("""# Look up YOUR stock's permno
MY_TICKER = "____"  # ← replace with your ticker

lookup = db.raw_sql(f\"\"\"
    SELECT permno, ticker, comnam, namedt, nameenddt
    FROM crsp.stocknames
    WHERE ticker = '{MY_TICKER}'
    ORDER BY namedt
\"\"\")
print(f"Permno history for ticker {MY_TICKER}:")
print(lookup.to_string(index=False))

# Pick the permno of the firm we care about (usually the latest entry)
my_permno = ____  # ← fill in the permno (int) from the lookup above
print(f"\\nWill use permno = {my_permno}")"""))

cells.append(md("""> **⚠️ Tickers get recycled.** If your lookup returns multiple permnos,
> they may be totally different companies that used the same ticker at
> different times. Pick the one whose name (`comnam`) and date range match
> the company you actually want."""))

cells.append(md("""### Step 2 — Pull 5 years of monthly data

Adapt the precise prompt pattern from Demo 1. Pull monthly data from
2019-01-01 to 2024-12-31 for your permno."""))

cells.append(code("""# Pull the data — adapt the precise query pattern
mine = db.raw_sql(f\"\"\"
    SELECT date, ret, retx, prc, shrout, ticker
    FROM crsp.msf
    WHERE permno = {my_permno}
      AND date BETWEEN '2019-01-01' AND '2024-12-31'
    ORDER BY date
\"\"\", date_cols=['date'])

print(f"Pulled {len(mine)} months of data")
mine.head(3)"""))

cells.append(md("""### Step 3 — Compute the required outputs

> **📌 Required variable names** (the submission cell expects these):
> ```python
> my_ticker           = "____"   # your ticker as a string
> my_permno           = ____     # the permno you used (int)
> months_of_data      = ____     # number of months pulled
> latest_mktcap_M     = ____     # last row's price × shrout / 1000 (millions)
> cum_return          = ____     # cumulative total return over the period
> avg_monthly_return  = ____     # mean of ret column
> ```"""))

cells.append(code("""# Your work here


# Required outputs:
my_ticker          = "____"
my_permno          = ____
months_of_data     = ____
latest_mktcap_M    = ____
cum_return         = ____
avg_monthly_return = ____

print(f"Stock:               {my_ticker} (permno {my_permno})")
print(f"Months of data:      {months_of_data}")
print(f"Latest market cap:   ${latest_mktcap_M:,.0f}M")
print(f"Cumulative return:   {cum_return:+.1%}")
print(f"Avg monthly return:  {avg_monthly_return:+.2%}")"""))

cells.append(md("""### Step 4 — Note (2 sentences)

Anything you noticed about your stock? Anything that surprised you about
running the WRDS query?"""))

cells.append(code("""NOTE = \"\"\"
Two sentences about your stock and/or the WRDS experience.
Keep the triple quotes.
\"\"\"
print(NOTE)"""))

# ─── Submission ───────────────────────────────────────────────────────
cells.append(md("""---

## 📤 Submission <a id="submit"></a>

Run the cell below. Copy the line starting with `UG54::` into the
submission form: **https://forms.gle/YOUR_FORM_LINK_HERE**

Completion-only — any plausible values + a real note will get full credit."""))

cells.append(code("""# === 📤 SUBMISSION CELL — Run this last ===
import json, base64, hashlib, datetime as dt

required = [
    "my_ticker", "my_permno", "months_of_data", "latest_mktcap_M",
    "cum_return", "avg_monthly_return", "NOTE",
]
missing = [v for v in required if v not in dir()]
if missing:
    raise NameError(f"\\n❌ Missing: {missing}")

payload = {
    "assignment": "WRDS_Tour_AI",
    "ts": dt.datetime.utcnow().isoformat(timespec="seconds") + "Z",
    "answers": {
        "my_ticker":          str(my_ticker),
        "my_permno":          int(my_permno),
        "months_of_data":     int(months_of_data),
        "latest_mktcap_M":    float(latest_mktcap_M),
        "cum_return":         float(cum_return),
        "avg_monthly_return": float(avg_monthly_return),
    },
    "memo": NOTE.strip(),
}
blob = json.dumps(payload, sort_keys=True)
checksum = hashlib.sha256(blob.encode()).hexdigest()[:8]
token = f"UG54::{checksum}::{base64.b64encode(blob.encode()).decode()}"

print("=" * 72)
print("📋  COPY THE LINE BELOW AND PASTE INTO THE SUBMISSION FORM")
print("=" * 72)
print(token)
print("=" * 72)
print(f"\\nLength: {len(token)} chars")
print("Submission form: https://forms.gle/YOUR_FORM_LINK_HERE")"""))

# ─── Key Takeaways ────────────────────────────────────────────────────
cells.append(md("""---

## 🧠 Key Takeaways <a id="takeaways"></a>

1. **WRDS is queryable from Colab in 5 lines.** `pip install wrds`, `wrds.Connection()`, `db.raw_sql(...)` — done.

2. **`permno` is the right identifier**, not ticker. Tickers change and get reused.

3. **The CRSP `ret` / `retx` split is useful.** Lets you separate price-only return from total return — equivalent to extracting the dividend yield.

4. **Cross-section queries: always filter `shrcd IN (10, 11)`** for US common stock. Otherwise you get ETFs and ADRs mixed in.

5. **Negative prices in CRSP are bid-ask midpoints, not errors.** Use `abs(prc)`; consider dropping them depending on your analysis.

6. **Compustat: ALWAYS include the four filters.** `indfmt='INDL'`, `datafmt='STD'`, `popsrc='D'`, `consol='C'`. Without them you get 4x rows per firm-year.

7. **Loose prompts produce subtly wrong SQL.** Precise prompts name the table, columns, filters, and ordering explicitly. **AI will not guess WRDS schema correctly** — it has to be told.

8. **The Specify → Implement → Validate loop applies to SQL too.** Spec out your query in English; let AI write the SQL; verify columns and row count before trusting the data."""))

# ─── Fallback CSVs (emergency) ────────────────────────────────────────
cells.append(md("""---

## 🚨 FALLBACK_LOAD_CSVS (use only if WRDS connection fails)

If your WRDS connection isn't working *during class*, run this cell to load
pre-pulled equivalents of the data the demos use. **You still need to sort
out your WRDS access after class** — but this lets you follow along."""))

cells.append(code("""#@title 🚨 Fallback: load pre-pulled CSVs in place of WRDS queries
# Only run this if `db.raw_sql(...)` is failing for you today.

base = 'https://raw.githubusercontent.com/amoreira2/UG54/refs/heads/main/assets/data'
aapl = pd.read_csv(f'{base}/wrds_tour_aapl_full.csv', parse_dates=['date'])
aapl = aapl[(aapl['date'] >= '2010-01-01') & (aapl['date'] <= '2024-12-31')].reset_index(drop=True)
xs = pd.read_csv(f'{base}/wrds_tour_crsp_xs.csv', parse_dates=['date'])
# Compustat sample is provided as a single-firm history of AAPL fundamentals
# stub — you should still pull your own from WRDS to complete the challenge
print("✅ Fallback data loaded. Continue with the demos using `aapl` and `xs`.")
print("⚠️ The CHALLENGE still requires WRDS — get your access working before next class.")"""))

# ─── Write notebook ───────────────────────────────────────────────────
notebook = {
    "cells": cells,
    "metadata": {
        "colab": {"provenance": [], "toc_visible": True},
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python"},
    },
    "nbformat": 4, "nbformat_minor": 5,
}
OUT.write_text(json.dumps(notebook, indent=1))
print(f"✅ Wrote {OUT} ({len(cells)} cells)")
