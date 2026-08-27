"""
Build L3_Sorts_AI.ipynb — Lecture 3, Mon Sep 14 2026.

Sources:
    crosssectionalequitystrategies.ipynb  (the sort recipe, groupby, long-short)
    FactorModels_c_AI.ipynb               (Sharpe / appraisal / information ratio)

NOT here (moved):
    WRDS intro -> start of L4
    appraisal + information ratio are DEFINED here but not computed: both need
    alpha from a factor model, which is L4. Only Sharpe is computed.

The spine of this lecture is one finding: sorting on firm size, 1980-2000,
with four equally defensible implementation choices, gives

    all-stock deciles, EW   +20.7%/yr   t =  3.94     <- a spectacular anomaly
    all-stock deciles, VW    +9.2%/yr   t =  1.90
    NYSE breakpoints,  EW    -2.1%/yr   t = -0.56
    NYSE breakpoints,  VW    -6.4%/yr   t = -1.93     <- the opposite sign

Same signal, same data, same 252 months. That is the whole lesson: the
implementation choices ARE the result. It also explains what NYSE breakpoints
are for -- the all-stock bottom decile is 597 of the tiniest firms in America,
equally weighted and completely uninvestable, while NYSE breakpoints define
"small" relative to NYSE and sweep in 3,106 names.

Live demo uses BM (value), which is robust to these choices, so students see a
clean monotone sort BEFORE they see one fall apart.

CHALLENGE (auto-graded, verified 2026-08-06): reproduce all four size numbers.
"""

import json
from pathlib import Path

OUT = Path(__file__).parent / "L3_Sorts_AI.ipynb"
BASE = "https://raw.githubusercontent.com/amoreira2/UG54/refs/heads/main/assets/data"


def md(t): return {"cell_type": "markdown", "metadata": {}, "source": t.splitlines(keepends=True)}
def code(t): return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": t.splitlines(keepends=True)}


cells = []

cells.append(md("""# Sorts, Breakpoints, and Long-Short Portfolios
## Lecture 3

## 🎯 Learning Objectives

By the end of today you will be able to:

1. **Turn any firm characteristic into a portfolio** using the sort recipe —
   rank, bucket, weight, average, spread
2. **Build a long-short portfolio** and explain why its weights sum to zero
3. **Explain what NYSE breakpoints are for** and why nearly every published
   paper uses them
4. **Show that implementation choices change the answer** — including the sign
5. **Recognize when a spread is an artifact of your implementation** rather than
   a property of the signal"""))

cells.append(md("""## 📋 Today's Plan

1. [The sort recipe](#recipe) (8 min)
2. [Pitfall checklist](#pitfalls) (3 min)
3. [🔄 Live Demo: sorting on value](#demo) (10 min)
4. [Breakpoints, and the size disaster](#breakpoints) (14 min)
5. [Why ten buckets?](#tradeoff) (7 min)
6. [A real bug in real data](#infinities) (7 min)
7. [🛠️ Hands-On: pick your own signal](#ho1)
8. [🎯 Challenge: size, four ways](#challenge) — *homework*
9. [Key takeaways](#takeaways)

> **📎 Winsorizing and z-scoring** live in the Appendix —
> `chapters/Appendix/SignalHygiene_AI.ipynb`. Ranking is scale-free so a sort
> doesn't need them, but you will if you combine two signals for Assignment 1.
>
> **📎 Sharpe and information ratios** moved to Lecture 4, *Introduction to
> Performance Evaluation*, where they sit with the appraisal ratio once a
> factor model gives you alpha."""))

cells.append(md("---\n\n## 🛠️ Setup"))

cells.append(code(f"""#@title Setup — run this first
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
%matplotlib inline
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = [11, 4.5]
plt.rcParams['font.size'] = 11
import warnings; warnings.filterwarnings('ignore')

BASE = "{BASE}"
panel = pd.read_parquet(f"{{BASE}}/panel_backbone_1980_2000.parquet")
menu  = pd.read_csv(f"{{BASE}}/signal_menu.csv")

print(f"panel: {{len(panel):,}} rows, {{panel.date.nunique()}} months")
print(f"menu : {{len(menu)}} signals available\\n")
menu[['Acronym', 'Authors', 'Year', 'Cat.Economic']].head(8).to_string(index=False)"""))

# ─── 1. The recipe ────────────────────────────────────────────────────
cells.append(md(r"""---

## 1. The Sort Recipe <a id="recipe"></a>

Last week you built one portfolio holding everything. Today you build a
portfolio that expresses a **view**.

The setup: you have a number for every stock in every month — a *signal*. Book-
to-market, past return, profitability, anything. You believe stocks with a high
value of that number will outperform stocks with a low value. How do you turn
that belief into a portfolio?

> **The recipe — five steps, and it never changes**
>
> 1. **Rank** every stock each month by the signal
> 2. **Bucket** them into groups (deciles is standard)
> 3. **Weight** within each bucket (equal or value)
> 4. **Average** each bucket's `ret_fwd` to get that bucket's return
> 5. **Spread** — go long the top bucket, short the bottom

Every factor you have ever heard of — value, momentum, quality, low-volatility
— is this recipe applied to a different column. That is genuinely all there is
to it.

### Why decile portfolios and not just a regression?

You could regress returns on the signal. Sorting has three advantages that
matter in practice:

- It is **non-parametric** — no assumption that the relationship is linear
- It shows you the **shape** — is the effect in the extremes, or monotone?
- The output **is a portfolio**, with a return you could actually have earned

### Step 5 is a self-financed position

Long the top decile, short the bottom, in equal dollars. The weights sum to
**zero** — exactly the structure you met in Lecture 1 when you computed an
excess return. It costs nothing to enter, so what comes out is a *spread*, not
a return on capital. That's why we can compare it across strategies of
different sizes.

### From names to characteristics

This is the move that defines quantitative investing.

A discretionary analyst says *"I like Apple, because tariffs will hurt its
competitors more."* A quant says *"build a tariff-exposure characteristic, sort
every stock on it, and hold the whole top decile."*

The second version is the same idea, made diversified and repeatable. You are
no longer betting on a company; you are betting on a **property**, held across
hundreds of companies at once, and you find out whether the property pays.

> **💡 Key Insight: the portfolios churn, and that's the point**
>
> Sorting doesn't buy a fixed list of firms. Membership turns over as companies
> change, which is exactly what makes it a bet on the characteristic rather than
> on the names.
>
> Microsoft is the standard illustration. Small in the early 80s, so it sat in
> the small-cap bucket. Gigantic by the late 90s, so it moved to the large-cap
> bucket. Priced enormously above book value during the tech boom → the *growth*
> (low book-to-market) portfolio. Valuation collapsed after 2000 → it migrated
> into the *value* portfolio. Now, with AI, it's back in growth.
>
> One company. Four decades. It has been in nearly every bucket we sort on. A
> value strategy held it when it was cheap and dropped it when it wasn't —
> without anyone forming an opinion about Microsoft."""))

# ─── Pitfalls ─────────────────────────────────────────────────────────
cells.append(md("""---

## 🛡️ Pitfall Checklist for Sorts <a id="pitfalls"></a>

| | Pitfall | What goes wrong | 🔍 How to detect |
|---|---|---|---|
| 1 | **Sorting on the signal at *t*, measuring `ret` at *t*** | Look-ahead. Inflates everything, sometimes enormously | Are you using `ret_fwd`? |
| 2 | **Equal-count deciles over all stocks** | The bottom decile becomes ~600 microcaps that no one could trade | How many stocks are in the extreme buckets, and how big are they? |
| 3 | **Equal-weighting inside buckets** | Tiny firms get the same weight as Apple | Is a `weights=` argument present? |
| 4 | **Ranking across the whole panel instead of within each month** | You compare 1985's book-to-market to 1999's | Is `groupby('date')` in the ranking step? |
| 5 | **Dropping missing signal values after bucketing** | Bucket sizes become unequal and the spread is mismeasured | Drop first, then rank |
| 6 | **Reporting only the spread** | A "great" long-short may be entirely a bad short leg you couldn't execute | Always print both legs separately |

> **🤖 AI-Era Insight**
>
> Ask for "a decile sort on this signal" and you will get `pd.qcut(x, 10)` over
> the full cross-section, equal-weighted, every time. That is pitfalls 2 and 3
> together, and as you'll see in Section 3 it can flip the sign of your
> result."""))

# ─── Live demo ────────────────────────────────────────────────────────
cells.append(md("""---

## 🔄 Live Demo: Sorting on Value <a id="demo"></a>

Book-to-market — book value divided by market value. High means the market
prices the firm cheaply relative to its accounting value. Graham and Dodd in
1934, Stattman in 1980, Fama and French in 1992.

### Step 1 — The specification

> **📝 Spec**
>
> Merge the `BM` signal onto the panel. Within **each month**, rank stocks by
> `BM` and cut into 10 equal-count buckets. For each bucket and month, compute
> the equal-weighted average of `ret_fwd`. Report each decile's annualized mean
> return and the annualized decile-10-minus-decile-1 spread with its t-statistic.
> Drop rows with missing `BM`, `ret_fwd`, or `me` before ranking.

### Step 2 — Implementation

> **🤖 AI prompt:**
>
> *"Merge signal df onto panel on permno and date. Drop missing. Within each
> date, use pd.qcut on the signal to make 10 buckets labelled 0-9. Group by date
> and bucket, take the mean of ret_fwd. Compute the time series of bucket 9
> minus bucket 0, and report its annualized mean and Newey-West-free t-stat."*"""))

cells.append(code("""bm = pd.read_parquet(f"{BASE}/signals/BM.parquet")
d = panel.merge(bm, on=['permno','date'], how='inner').dropna(subset=['BM','ret_fwd','me'])

# rank WITHIN each month (pitfall 4)
d['decile'] = d.groupby('date')['BM'].transform(
    lambda x: pd.qcut(x, 10, labels=False, duplicates='drop'))

bucket = d.groupby(['date','decile'])['ret_fwd'].mean().unstack()
ls = (bucket[9] - bucket[0]).dropna()

print("Annualized mean return by book-to-market decile (1 = growth, 10 = value)")
for k in range(10):
    print(f"  D{k+1:<2d} {bucket[k].mean()*12:7.2%}")
print(f"\\nD10 - D1 : {ls.mean()*12:.2%}/yr")
print(f"t-stat   : {ls.mean()/ls.std()*np.sqrt(len(ls)):.2f}")
print(f"months   : {len(ls)}")"""))

cells.append(code("""fig, ax = plt.subplots(1, 2, figsize=(13, 4))
ax[0].bar(range(1,11), bucket.mean()*12, color='steelblue')
ax[0].set_xlabel('Book-to-market decile'); ax[0].set_ylabel('Mean return, annualized')
ax[0].set_title('The sort', fontweight='bold')
ax[1].plot(ls.index, (1+ls).cumprod(), color='darkorange', linewidth=1.8)
ax[1].set_ylabel('Growth of $1'); ax[1].set_title('Long-short D10 - D1', fontweight='bold')
plt.tight_layout(); plt.show()"""))

cells.append(md("""### Step 3 — Validate

> **🤔 Read the bar chart before the t-stat.**
>
> Is the pattern **monotone** — does each decile beat the one below it? A
> monotone sort is much stronger evidence than a big spread between the two
> extremes. If only D10 and D1 are unusual and the middle is flat, you may be
> looking at two small groups of odd firms rather than a pervasive relationship.

Also check both legs separately (pitfall 6): a spread built entirely from a
disastrous short leg is a different claim from one where both sides contribute."""))

# ─── Breakpoints ──────────────────────────────────────────────────────
cells.append(md("""---

## 2. Breakpoints, and the Size Disaster <a id="breakpoints"></a>

We used `pd.qcut` — equal-count deciles over every stock in the market. That
seems like the neutral choice. It is not.

Recall from last week: there are about 6,000 stocks in this market, and the
largest 10 are 20% of total market value. The market is enormously skewed. So
an equal-count bottom decile is **600 of the smallest companies in America** —
firms worth a few million dollars, trading a few thousand dollars a day.

### The fix: NYSE breakpoints

Compute the cutoffs using **only NYSE-listed stocks**, then apply those cutoffs
to everything. NYSE firms are larger and more established, so the resulting
buckets are defined relative to a sane benchmark rather than relative to the
microcap tail.

This is what Fama and French do, and what almost every published paper does.
It is not a cosmetic choice.

### Watch what it does to the size effect

Banz (1981) reported that small stocks outperform. Let's test that four ways —
each one a defensible choice a competent analyst might make."""))

cells.append(code("""d0 = panel.dropna(subset=['ret_fwd','me'])

def size_spread(breakpoints, weighting):
    \"\"\"Small-minus-big, 1980-2000. Returns (annualized mean, vol, t, n_small).\"\"\"
    d = d0.copy()
    if breakpoints == 'nyse':
        q = (d[d.exchcd == 1].groupby('date')['me']
               .quantile([.1, .9]).unstack().rename(columns={0.1:'lo', 0.9:'hi'}))
        d = d.merge(q, on='date')
        d['g'] = np.where(d.me <= d.lo, 'S', np.where(d.me >= d.hi, 'B', None))
    else:
        dec = d.groupby('date')['me'].transform(
            lambda x: pd.qcut(x, 10, labels=False, duplicates='drop'))
        d['g'] = np.where(dec == 0, 'S', np.where(dec == 9, 'B', None))
    d = d[d.g.notna()]
    agg = ((lambda g: np.average(g['ret_fwd'], weights=g['me'])) if weighting == 'vw'
           else (lambda g: g['ret_fwd'].mean()))
    p = d.groupby(['date','g']).apply(agg).unstack()
    r = (p['S'] - p['B']).dropna()
    n = d[d.g == 'S'].groupby('date').size().mean()
    return r.mean()*12, r.std()*np.sqrt(12), r.mean()/r.std()*np.sqrt(len(r)), n

print("SMALL MINUS BIG, 1980-2000 — four defensible implementations\\n")
print(f"{'breakpoints':16s}{'weights':10s}{'return/yr':>11s}{'vol':>8s}{'t-stat':>9s}{'n small':>10s}")
print("-"*64)
for bp, lbl in [('all','all stocks'), ('nyse','NYSE only')]:
    for w in ['ew','vw']:
        m, v, t, n = size_spread(bp, w)
        print(f"{lbl:16s}{w.upper():10s}{m:>10.1%}{v:>8.1%}{t:>9.2f}{n:>10.0f}")"""))

cells.append(md("""### Sit with that table

The same signal. The same 6,000 stocks. The same 252 months. And the answer runs
from **+20.7% a year with a t-statistic of 3.94** — which would be one of the
great anomalies in finance — to **−6.4% a year with t = −1.93**, which says the
opposite.

Nobody cheated. All four are choices a competent analyst might defend.

> **💡 Key Insight**
>
> The implementation choices *are* the result. When someone shows you a
> long-short return, "what were your breakpoints and how did you weight?" is
> not a technical footnote — it can be the entire finding.

### Why it happens

Look at the last column. With all-stock deciles the small bucket holds about
**597** firms — the very tiniest in the market. Equal-weighted, that portfolio
is dominated by companies worth a few million dollars.

With NYSE breakpoints, "small" means small *relative to NYSE*, which sweeps in
about **3,106** names — half the market — and the extreme microcap tail no
longer drives the average.

> **⚠️ Caution: the +20.7% is real in the data and uninvestable in the world**
>
> Nothing is wrong with the arithmetic. That portfolio requires buying equal
> dollar amounts of 600 of the smallest listed companies in America and
> rebalancing monthly. The bid-ask spreads alone would consume most of it, and
> that's before you ask whether you could buy at all. We quantify this in
> Lecture 15.

This is also the answer to something you saw last week: equal-weighting lost to
value-weighting over these twenty years. The size premium Banz published in
1981 does not survive contact with sensible implementation choices over
1980–2000.

### A second piece of evidence: the extremes didn't trade

There is an independent way to see that the extreme buckets are not real
portfolios. CRSP records a **negative price** when a stock did not trade on the
last day of the month — the number it reports is then a bid/ask midpoint, not a
price anyone transacted at."""))

cells.append(code("""d0['traded'] = d0['prc'] > 0
print(f"Stock-months with a negative price (no trade that day): "
      f"{(~d0.traded).mean():.1%} of the panel")
print(f"  median market cap, no-trade : ${d0.loc[~d0.traded,'me'].median()/1e3:>8,.1f}M")
print(f"  median market cap, traded   : ${d0.loc[ d0.traded,'me'].median()/1e3:>8,.1f}M\\n")

share = d.groupby('decile').apply(lambda g: (g.prc < 0).mean())
print("Share of the bucket that DIDN'T TRADE, by book-to-market decile:")
for k, v in share.items():
    bar = '█' * int(v*60)
    print(f"  D{int(k)+1:<2d} {v:5.1%}  {bar}")"""))

cells.append(md("""### Look at the shape of that

Roughly **32% of decile 1 and 33% of decile 10** are stocks that did not trade
on the formation date — against about 16% in the middle deciles. The extremes
are twice as contaminated as the middle.

Sorting on *any* characteristic pushes illiquid microcaps to the ends, because
extreme characteristic values and extreme illiquidity travel together. So a
third of both legs of your long-short is priced at a quote nobody hit.

> **⚠️ Caution: your backtest assumed you bought at that price**
>
> The return you computed for the extreme deciles is measured between two
> bid/ask midpoints. In reality you would have paid the ask and sold at the bid,
> on stocks with a median market cap of $10.8M.
>
> This is a *different* mechanism from the breakpoint problem — nothing to do
> with how you cut the buckets — and it points the same way. Two independent
> reasons the extreme portfolios are less real than they look.

> **🤔 A question worth holding onto**
>
> Should you drop non-traded stock-months before sorting? It's defensible. But
> notice you'd be dropping a quarter of the panel, concentrated in exactly the
> stocks the strategy wants to hold — which is itself a decision that changes
> the answer. Add it to the list from the four-way table."""))

cells.append(md("""---

## 3. Why Ten Buckets? <a id="tradeoff"></a>

Why deciles? Why not 100 buckets, so the top portfolio has a far more extreme
signal? Or simply buy the single highest-signal stock?

Because a portfolio return is an *estimate*, and estimates have standard errors.

Individual stocks have annual volatility of **40–80%**. To measure an expected
return to within a percentage point you need $\\sigma/\\sqrt{T}$ small — and with
σ = 60%, that takes centuries. Averaging across stocks in a bucket cuts the
volatility fast, which is what makes the bucket's mean return measurable at all.

So there is a genuine trade-off:

| More buckets | Fewer buckets |
|---|---|
| Stronger signal in the extremes | Weaker signal |
| Fewer stocks each → noisier | More stocks → more precise |
| Higher turnover, worse capacity | Cheaper to trade |

Ten is a convention that balances these. Let's check whether it's a good one."""))

cells.append(code("""for n in [5, 10, 20, 50]:
    x = panel.merge(bm, on=['permno','date'], how='inner').dropna(subset=['BM','ret_fwd','me'])
    x['g'] = x.groupby('date')['BM'].transform(
        lambda v: pd.qcut(v, n, labels=False, duplicates='drop'))
    p = x.groupby(['date','g'])['ret_fwd'].mean().unstack()
    r = (p[n-1] - p[0]).dropna()
    n_stocks = x[x.g == n-1].groupby('date').size().mean()
    print(f"{n:>3d} buckets: spread {r.mean()*12:>6.1%}/yr   "
          f"t = {r.mean()/r.std()*np.sqrt(len(r)):>4.1f}   "
          f"{n_stocks:>5.0f} stocks in the top bucket")"""))

cells.append(md("""> **💡 Key Insight**
>
> Cutting finer **does** widen the spread — monotonically, from 16% at quintiles
> to 29% at 50 buckets. The top 2% of stocks by book-to-market really are
> cheaper than the top 10%, and they really do earn more.
>
> But look at the t-statistic. It rises to about 7.2 at 20 buckets and then
> **falls**. Past that point each bucket holds so few stocks that the extra
> signal is swamped by the extra noise — you are paying in precision faster than
> you are gaining in strength.
>
> That is the trade-off, visible in four lines of output. Deciles sit
> essentially at the top of the curve, which is why the literature settled
> there — not because ten is a round number."""))

# ─── The infinity trap ────────────────────────────────────────────────
cells.append(md("""---

## 4. A Real Bug in Real Data <a id="infinities"></a>

Everything above assumed the numbers are numbers. Let's check.

Many of these characteristics are **log ratios** — log book-to-market, log
issuance. When the denominator is zero or negative, the log is not a large
number. It is `-inf`.

Five of our thirty signals arrived from Open Source Asset Pricing with
infinities in them. We ship the cleaned versions, but the raw file is in the
repo so you can see what this does."""))

cells.append(code("""raw = pd.read_parquet(f"{BASE}/signals_raw/CompositeDebtIssuance.parquet")
v = raw['CompositeDebtIssuance'].to_numpy()
print("CompositeDebtIssuance — raw, exactly as delivered\\n")
print(f"  rows          : {len(raw):,}")
print(f"  +inf          : {np.isposinf(v).sum():,}")
print(f"  -inf          : {np.isneginf(v).sum():,}   ({np.isinf(v).mean():.2%} of the file)")
print(f"  finite min/max: {np.nanmin(v[np.isfinite(v)]):.2f} / {np.nanmax(v[np.isfinite(v)]):.2f}")
print(f"\\n  mean          : {v.mean()}")
print(f"  std           : {v.std()}")
print("\\nBoth signs of infinity are present, so the mean is not large — it is nan.")
print("Every summary statistic of this signal is now undefined, and nothing errored.")"""))

cells.append(md("""### Now sort on it — two ways

Both of the following are reasonable implementations of "decile sort". They
fail differently, and neither raises anything."""))

cells.append(code("""rd = panel.merge(raw, on=['permno','date'], how='inner').dropna(subset=['ret_fwd','me'])

# --- Implementation A: pd.qcut, the obvious choice -------------------
rd['dec'] = rd.groupby('date')['CompositeDebtIssuance'].transform(
    lambda x: pd.qcut(x, 10, labels=False, duplicates='drop'))

print("A) pd.qcut(x, 10, duplicates='drop')\\n")
print("   deciles that exist:", sorted(int(x) for x in rd['dec'].dropna().unique()))
print(f"   months in which decile 9 exists: {rd[rd.dec==9].date.nunique()} of {rd.date.nunique()}")
print(f"   rows assigned no decile at all : {rd['dec'].isna().sum():,}")
print("\\n   Deciles 0 and 9 — your short leg and your long leg — DO NOT EXIST.")
print("   qcut couldn't place the infinities, and 'duplicates=drop' quietly")
print("   collapsed the bin edges. A long-short with no long and no short.")"""))

cells.append(code("""# --- Implementation B: explicit quantile cutoffs ----------------------
q = (rd[rd.exchcd == 1].groupby('date')['CompositeDebtIssuance']
       .quantile([.1, .9]).unstack().rename(columns={0.1:'lo', 0.9:'hi'}))
rb = rd.merge(q, on='date')
rb['g'] = np.where(rb['CompositeDebtIssuance'] <= rb.lo, 0,
            np.where(rb['CompositeDebtIssuance'] >= rb.hi, 9, np.nan))
rb = rb.dropna(subset=['g'])

for leg, name in [(9, 'long leg  (top)'), (0, 'short leg (bottom)')]:
    x = rb[rb.g == leg]
    print(f"B) {name}: {len(x):>8,} rows, "
          f"{np.isinf(x['CompositeDebtIssuance']).mean():>6.1%} infinite")
print("\\n   Here the comparison `x <= lo` works fine on infinities, so they all")
print("   land in the extreme buckets. You get a full portfolio and a t-stat —")
print("   built largely from stocks whose signal could not be computed.")"""))

cells.append(md("""### Two implementations, two failures, zero errors

| | What happened | What you'd see |
|---|---|---|
| **A** `pd.qcut` | Infinities can't be binned; `duplicates='drop'` collapses the edges | Deciles 0 and 9 vanish. Your long-short has no legs. An empty result, or a `KeyError` you'd "fix" by dropping months. |
| **B** explicit quantiles | Comparisons on `inf` work, so infinities sort into both extremes | A complete portfolio, a return series, a t-statistic — all built on missing data |

> **🤖 AI-Era Insight: this is the whole course in one cell**
>
> Ask an AI to "sort stocks into deciles on this signal" and you will get
> version A or version B. Both run. Neither warns you. Version B in particular
> hands you a result that looks exactly like every other result in this
> notebook.
>
> The bug is not in the code. The code is fine. The bug was in the data, and
> the only way to catch it was to look at the data first.

### The fix, and the habit

```python
x = x.replace([np.inf, -np.inf], np.nan)   # infinities are missing data
x = x.dropna()                             # then drop them
```

Two lines. But the habit that matters comes before them: **describe your signal
before you sort on it.** A single `.describe()` shows `inf` in the min or max
immediately, and it takes three seconds."""))

cells.append(code("""clean = pd.read_parquet(f"{BASE}/signals/CompositeDebtIssuance.parquet")
print(f"raw   : {len(raw):,} rows")
print(f"clean : {len(clean):,} rows   ({1-len(clean)/len(raw):.1%} removed)\\n")

def spread_from(sig_df, col):
    \"\"\"Standard implementation: NYSE breakpoints, value-weighted, D10 - D1.\"\"\"
    x = panel.merge(sig_df, on=['permno','date'], how='inner').dropna(subset=['ret_fwd','me'])
    q = (x[x.exchcd == 1].groupby('date')[col]
           .quantile([.1,.9]).unstack().rename(columns={0.1:'lo', 0.9:'hi'}))
    x = x.merge(q, on='date')
    x['g'] = np.where(x[col] <= x.lo, 0, np.where(x[col] >= x.hi, 9, np.nan))
    x = x.dropna(subset=['g'])
    p = x.groupby(['date','g']).apply(
            lambda g: np.average(g['ret_fwd'], weights=g['me'])).unstack()
    return (p[9] - p[0]).dropna()

for label, frame in [('with infinities', raw), ('cleaned', clean)]:
    r = spread_from(frame, 'CompositeDebtIssuance')
    print(f"{label:18s} return {r.mean()*12:+7.2%}/yr   "
          f"t = {r.mean()/r.std()*np.sqrt(len(r)):+.2f}")"""))

cells.append(md("""> **📌 Remember**
>
> Published t-statistic for this signal: **+8.59**. Cleaned, over 1980–2000, we
> get roughly **−0.3**. The infinities were never the reason it fails to
> replicate — but you could not have known that until you removed them.
>
> Fixing a data bug does not always rescue a result. Sometimes it just lets you
> see the real one.

---

## 🛠️ Hands-On: Pick Your Own Signal <a id="ho1"></a>

You have **30 signals**, each from a published paper, each with the t-statistic
the original authors reported. Pick one and test it.

> **📌 Everyone uses the same convention** so the class results are comparable:
> **NYSE breakpoints, value-weighted, top decile minus bottom decile,
> `ret_fwd`.** That is the standard implementation.

### Your task

1. Pick a signal from the menu
2. Run the sort
3. Report your t-statistic next to the published one
4. Be ready to say out loud whether it replicated"""))

cells.append(code("""# The menu — 30 published signals
pd.set_option('display.max_rows', 40, 'display.width', 200)
menu[['Acronym','Authors','Year','Cat.Economic','T-Stat']].sort_values('Cat.Economic').to_string(index=False)"""))

cells.append(code("""# === EDIT THIS CELL: your signal ===
MY_SIGNAL = "GP"      # ← pick any Acronym from the menu above

sig = pd.read_parquet(f"{BASE}/signals/{MY_SIGNAL}.parquet")
print(f"{MY_SIGNAL}: {len(sig):,} stock-months")
print(menu.loc[menu.Acronym == MY_SIGNAL, 'LongDescription'].iloc[0][:300])"""))

cells.append(code("""# === YOUR TURN ===
# Fill in the two blanks to complete the standard sort.

def long_short(signal_name, breakpoints='nyse', weighting='vw'):
    s = pd.read_parquet(f"{BASE}/signals/{signal_name}.parquet")
    d = panel.merge(s, on=['permno','date'], how='inner')
    d = d.dropna(subset=[signal_name, 'ret_fwd', 'me'])          # drop FIRST

    if breakpoints == 'nyse':
        q = (d[d.exchcd == 1].groupby('date')[signal_name]
               .quantile([.1,.9]).unstack().rename(columns={0.1:'lo', 0.9:'hi'}))
        d = d.merge(q, on='date')
        d['g'] = np.where(d[signal_name] <= d.lo, 0,
                   np.where(d[signal_name] >= d.hi, 9, np.nan))
    else:
        d['g'] = ____        # hint: d.groupby('date')[signal_name].transform(
                             #        lambda x: pd.qcut(x,10,labels=False,duplicates='drop'))
    d = d.dropna(subset=['g'])
    d = d[d.g.isin([0, 9])]

    agg = ((lambda g: np.average(g['ret_fwd'], weights=g['me'])) if weighting == 'vw'
           else (lambda g: g['ret_fwd'].mean()))
    p = d.groupby(['date','g']).apply(agg).unstack()
    r = ____                 # hint: (p[9] - p[0]).dropna()   — long top, short bottom
    return r

r = long_short(MY_SIGNAL)
t = r.mean()/r.std()*np.sqrt(len(r))
pub = menu.loc[menu.Acronym == MY_SIGNAL, 'T-Stat'].iloc[0]

print(f"{MY_SIGNAL}")
print(f"  return   {r.mean()*12:+.2%}/yr")
print(f"  vol      {r.std()*np.sqrt(12):.2%}")
print(f"  Sharpe   {r.mean()/r.std()*np.sqrt(12):.2f}")
print(f"  t-stat   {t:+.2f}      published: {pub:+.2f}")
print(f"  verdict  {'REPLICATES' if abs(t) > 2 else 'does not clear |t| > 2'}")"""))

cells.append(md("""### What did the room find?

Compare with your neighbours. Some of you have a t-statistic above 4. Some have
one near zero on a signal whose authors reported 8.

Both are honest results from the same code.

> **🤔 Before we move on**
>
> Your sample is 1980–2000. Look up the sample period the original paper used —
> it's in `menu`. If your window barely overlaps theirs, what exactly have you
> tested? And if a published t-statistic of 8 becomes 1 in a different window,
> which number should you believe?

Hold that question. It is Lecture 7 and Lecture 8, and for several of you it
will be your project."""))

# ─── Challenge ────────────────────────────────────────────────────────
cells.append(md("""---

## 🎯 Challenge: Size, Four Ways <a id="challenge"></a>

You are a junior analyst. Your PM read that small stocks outperform and asks
you to check whether it's true.

Reproduce all four versions of the size sort and then decide what you would
actually tell them.

Use `size_spread()` from Section 2, or write your own.

### Q1 — The four t-statistics

> **📌 Required variable names:**
> ```python
> t_ew_all  = ____   # all-stock deciles, equal-weighted
> t_vw_all  = ____   # all-stock deciles, value-weighted
> t_ew_nyse = ____   # NYSE breakpoints, equal-weighted
> t_vw_nyse = ____   # NYSE breakpoints, value-weighted
> ```"""))

cells.append(code("""# Your work here


# Required outputs — fill these in:
t_ew_all  = ____
t_vw_all  = ____
t_ew_nyse = ____
t_vw_nyse = ____

print(f"all stocks, EW : t = {t_ew_all:+.2f}")
print(f"all stocks, VW : t = {t_vw_all:+.2f}")
print(f"NYSE bp,    EW : t = {t_ew_nyse:+.2f}")
print(f"NYSE bp,    VW : t = {t_vw_nyse:+.2f}")"""))

cells.append(md("""### Q2 — How many stocks are in the small bucket?

Report the average monthly number of stocks in the **small** bucket under each
breakpoint scheme. This is the mechanism behind the table.

> **📌 Required variable names:**
> ```python
> n_small_all  = ____   # average stocks in the small bucket, all-stock deciles
> n_small_nyse = ____   # average stocks in the small bucket, NYSE breakpoints
> ```"""))

cells.append(code("""# Your work here


# Required outputs — fill these in:
n_small_all  = ____
n_small_nyse = ____

print(f"all-stock deciles : {n_small_all:.0f} stocks in the small bucket")
print(f"NYSE breakpoints  : {n_small_nyse:.0f} stocks in the small bucket")"""))

cells.append(md("""### Q3 — The memo

> **📝 Your task — maximum 6 sentences**
>
> Write to your PM. Does the size effect exist over 1980–2000?
>
> A strong memo will:
> - Give **one** answer, not four
> - Say which specification you'd stand behind and **why**
> - Explain what drives the difference between the two extremes
> - Note something about the +20.7% version beyond "it's a bigger number"
>
> There is no answer key here. I'm grading whether you understood that the
> choice had to be made and defended."""))

cells.append(code('''MEMO = """
Write your memo here. Don't delete the surrounding triple quotes.
"""
print(MEMO)'''))

cells.append(md("---\n\n## 📤 Submission <a id=\"submit\"></a>"))

cells.append(code('''# === 📤 SUBMISSION CELL — Run this last ===
import json, base64, hashlib, datetime as dt

required = ["t_ew_all", "t_vw_all", "t_ew_nyse", "t_vw_nyse",
            "n_small_all", "n_small_nyse", "MEMO"]
missing = [v for v in required if v not in dir()]
if missing:
    raise NameError(f"\\n❌ Missing before submission: {missing}")

payload = {
    "assignment": "L3_Sorts_AI",
    "ts": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
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
print(f"\\nLength: {len(token)} chars")
print("Submission form: https://forms.gle/YOUR_FORM_LINK_HERE")'''))

cells.append(md("""---

## 🧠 Key Takeaways <a id="takeaways"></a>

1. **The sort recipe is five steps and never changes:** rank, bucket, weight,
   average, spread. Every factor you've heard of is this applied to a different
   column.

2. **Rank within each month**, never across the whole panel.

3. **A long-short portfolio is self-financed** — weights sum to zero, no capital
   tied up, so no risk-free rate to subtract.

4. **Read the monotonicity, not just the spread.** A clean staircase across
   deciles is much stronger evidence than two unusual extremes.

5. **NYSE breakpoints exist for a reason.** Equal-count deciles over the whole
   market put ~600 microcaps in the bottom bucket. That portfolio is real in the
   data and untradeable in the world.

6. **Implementation choices can flip the sign.** Size over 1980–2000 runs from
   +20.7%/yr (t = 3.94) to −6.4%/yr (t = −1.93) across four defensible
   specifications. Always ask what the breakpoints and weights were.

7. **A spread is not yet a result.** You have a return series; you do not yet
   know whether it is skill, market exposure, or noise. Measuring that starts
   Wednesday.

---

### Next class

Where the data really comes from — CRSP, Compustat, and how you'd pull it
yourself — and then factor models: the tool that separates "this strategy earns
a return" from "this strategy earns a return *you couldn't have got for free*."""))

cells.append(md("---\n\n## 📎 Appendix <a id=\"appendix\"></a>"))

cells.append(code(f'''# ═══════════════════════════════════════════════════════════════════════
# 📎 APPENDIX — Belt-and-Suspenders Data Loading
# ═══════════════════════════════════════════════════════════════════════
# Everything today loads from the repo — no WRDS account needed.
#
#   panel  = pd.read_parquet(f"{{BASE}}/panel_backbone_1980_2000.parquet")
#   signal = pd.read_parquet(f"{{BASE}}/signals/<Acronym>.parquet")
#   menu   = pd.read_csv(f"{{BASE}}/signal_menu.csv")
#
# The 30 signals come from Open Source Asset Pricing (Chen & Zimmermann),
# which replicates 300+ published cross-sectional predictors:
#     https://www.openassetpricing.com
#
# TWO CONVENTIONS BAKED INTO THE SIGNAL FILES — worth knowing:
#
# 1. PRE-SIGNED. OSAP ships the raw characteristic plus a Sign column; 18 of
#    our 30 have Sign = -1. We flipped those on write, so for every signal
#    here HIGH = predicted HIGH return and the long-short is always D10 - D1.
#    The original direction is in signal_menu.csv.
#
# 2. Use `ret_fwd`, not `ret`. Sorting on a signal at t and measuring ret at t
#    is look-ahead. For short-term reversal that single error turns a t-stat
#    of -0.4 into +70.
#
# To rebuild any of this from scratch: chapters/Finance/build_course_panel.py
'''))

notebook = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.11"},
        "colab": {"provenance": []},
    },
    "nbformat": 4, "nbformat_minor": 5,
}
OUT.write_text(json.dumps(notebook, indent=1))
print(f"✅ Wrote {OUT}  ({len(cells)} cells)")
