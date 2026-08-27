"""
Build L2_Panel_Portfolios_AI.ipynb — Lecture 2, Wed Sep 9 2026.

Merges:
    WRDS_Data_Tour_AI.ipynb   (only the "what is this data" orientation --
                               the live-query material moves to end of L3
                               and into an assignment)
    PortfolioMath_c.ipynb     (weights, portfolio return, the @ operator)
    crosssectionalequitystrategies.ipynb  (market-cap weighted strategy,
                               stacked datasets, comparing to Ken French)

CUT / DEFERRED:
  - all live WRDS querying                    -> end of L3 + an assignment
  - portfolio VARIANCE, covariance matrix,
    diversification, mean-variance frontier   -> L12 (Capital Allocation I)
  - the AAPL fundamentals dive, buyback story,
    exchange breakdown                        -> dropped

The split of PortfolioMath_c is deliberate: sorts (L3) need only weights and
w'r. Variance and the frontier aren't needed until L12, and L12 already opens
with that material.

CHALLENGE (auto-graded, everyone same data): rebuild the CRSP value-weighted
market from the panel and check it against Ken French. Verified 2026-08-06:
    vw_mean_annual  0.1574     ew_mean_annual  0.1422
    vw_vol_annual   0.1553     ew_vol_annual   0.1856
    corr_vw_ff      1.0000     top10_share     0.2049
Correlation of exactly 1.0000 is the point: students get an unambiguous
"you did this right" signal, which almost no student exercise offers.
"""

import json
from pathlib import Path

OUT = Path(__file__).parent / "L2_Panel_Portfolios_AI.ipynb"
RAW = ("https://raw.githubusercontent.com/amoreira2/UG54/refs/heads/main/"
       "assets/data/panel_backbone_1980_2000.parquet")


def md(t): return {"cell_type": "markdown", "metadata": {}, "source": t.splitlines(keepends=True)}
def code(t): return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": t.splitlines(keepends=True)}


cells = []

cells.append(md("""# The Panel and Portfolio Mathematics
## Lecture 2

## 🎯 Learning Objectives

By the end of today you will be able to:

1. **Read a stacked panel** — why stock data is stored long, not wide, and why
   `groupby('date')` is the workhorse operation of this entire course
2. **Explain what CRSP is** and why delisted companies have to be in your data
3. **Compute a portfolio return** as a weighted average, `w′r`, in one line
4. **Distinguish value- from equal-weighting** and say what each one is a bet on
5. **Weight a portfolio without look-ahead** — using only information you had
   at the time
6. **Rebuild the US stock market from scratch** and check it against the
   official series"""))

cells.append(md("""## 📋 Today's Plan

1. [Where this data comes from](#data) (7 min)
2. [The stacked panel](#panel) (8 min)
3. [What returns actually look like](#distributions) (7 min)
4. [Pitfall checklist](#pitfalls) (3 min)
5. [Portfolio weights](#weights) (8 min)
6. [🔄 Live Demo: portfolio returns, `w′r`](#demo1) (12 min)
7. [Value- vs equal-weighting](#vwew) (4 min)
8. [🛠️ Hands-On: which one is bigger, and why?](#ho1) (12 min)
9. [🎯 Challenge: rebuild the market](#challenge) (12 min)
10. [Key takeaways](#takeaways) (2 min)"""))

cells.append(md("---\n\n## 🛠️ Setup"))

cells.append(code("""#@title Setup — run this first
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
%matplotlib inline
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = [11, 4.5]
plt.rcParams['font.size'] = 11
import warnings; warnings.filterwarnings('ignore')
print("✅ Ready")"""))

# ─── 1. Where the data comes from ─────────────────────────────────────
cells.append(md("""---

## 1. Where This Data Comes From <a id="data"></a>

Every number you will use this semester came from somewhere, and the choices
made in building it are already baked in before you write a line of code.

### CRSP

The **Center for Research in Security Prices** at Chicago maintains the standard
academic database of US stock returns — every US-listed common stock, monthly
and daily, back to 1926. It is the source for essentially every published paper
on US equity returns, and it is what your panel is built from.

Two things make CRSP the standard rather than, say, Yahoo Finance:

**It includes companies that no longer exist.** Enron is in CRSP. Lehman is in
CRSP. Every company that went bankrupt, got acquired, or was delisted for
failing to meet listing standards is still there, with its returns, right up to
the end.

> **⚠️ Caution: survivorship bias**
>
> Build a dataset from today's listed companies and you have automatically
> excluded every failure. Backtests on such data look wonderful and mean
> nothing. If you pull "all S&P 500 stocks" from a free API today and test a
> strategy back to 1990, you are testing "what if I had known in 1990 which
> companies would still be in the index in 2026."

**It handles the delisting return.** When a company is delisted, there is one
final return — sometimes −100%, sometimes a buyout premium — that is recorded
separately from the normal monthly series. Ignore it and you silently drop the
worst month of every failed company.

> **📌 Your panel already has this fixed.** The build merged 1,229 delisting
> returns into the monthly series. You'll see the code at the end of Lecture 3.

### Compustat

CRSP has prices and returns. It has no idea what a company *earns* or *owns*.
Accounting data — book value, earnings, assets, debt — comes from **Compustat**,
and joining the two is one of the standard chores of empirical finance. We'll
use pre-joined signals rather than doing that merge by hand."""))

# ─── 2. The panel ─────────────────────────────────────────────────────
cells.append(md("""---

## 2. The Stacked Panel <a id="panel"></a>"""))

cells.append(code(f"""URL = ("{RAW}")
panel = pd.read_parquet(URL)

print(f"{{len(panel):,}} rows")
print(f"{{panel.permno.nunique():,}} stocks over {{panel.date.nunique()}} months "
      f"({{panel.date.min().date()}} to {{panel.date.max().date()}})")
print(f"average of {{len(panel)/panel.date.nunique():.0f}} stocks per month\\n")
panel.head(5)"""))

cells.append(md("""### Long, not wide

Notice the shape: one row per **stock-month**, not one column per stock. This is
a *stacked* or *long* panel, and it is how essentially all cross-sectional
finance data is stored.

Why not a wide matrix with dates down and tickers across? Because the set of
stocks changes every month. Companies IPO, get acquired, go bankrupt. A wide
matrix would be mostly missing values and would need reshaping every time the
universe changed.

> **🐍 Python Insight: `groupby('date')`**
>
> Long format means "do something to each month's cross-section" is
> `df.groupby('date')`. That single operation — split by date, compute across
> stocks, recombine — is the workhorse of this entire course. Portfolio returns,
> sorts, breakpoints, factor construction: all of them are `groupby('date')`.

### The columns

| Column | What it is |
|---|---|
| `permno` | CRSP's permanent stock identifier — never reused, unlike tickers |
| `date` | Month end |
| `ret` | Total return **during** that month (dividends included) |
| `ret_fwd` | Total return over the **following** month |
| `me` | Market equity (price × shares outstanding), \\$thousands |
| `prc` | Price. **Can be negative** — CRSP flags a bid/ask midpoint that way |
| `exchcd` | 1 = NYSE, 2 = AMEX, 3 = NASDAQ |
| `shrcd` | Share code; 10/11 are ordinary common shares |

### Why there are two return columns

This is the most important thing in today's class.

`ret` is the return **during** month *t*. `me` is market equity at the **end** of
month *t*. If you weight by `me` at *t* and then claim the return `ret` at *t*,
you have used end-of-month information to earn a return that was already
happening. That is **look-ahead bias**, and it will make almost any strategy
look brilliant.

> **📌 Remember: the rule for every portfolio in this course**
>
> Form weights from information available at the end of month *t*. Earn
> `ret_fwd`, the return over month *t+1*. Nothing else."""))

cells.append(code("""# See it directly for one stock
ge = panel[panel.permno == 12060].head(4)[['date', 'ret', 'ret_fwd', 'me']]
print(ge.to_string(index=False))
print("\\nRow 0's ret_fwd equals row 1's ret — it's next month's return, shifted back.")
print("You decide at the end of January; you earn February.")"""))

cells.append(md("""### How `ret_fwd` was built, and the trap it hides

We gave you this column. When you build your own signal for the project you
will have to shift a series yourself, and there is a trap waiting.

The panel is **stacked** — one long column with every stock's history end to
end. A plain `df['ret'].shift(-1)` walks off the end of one stock and into the
beginning of the next, so the last month of stock *n* silently becomes the
first month of stock *n+1*."""))

cells.append(code("""# The wrong way and the right way, on the seam between two stocks
tiny = panel[panel.permno.isin([10000, 10001])].sort_values(['permno','date'])

tiny = tiny.assign(
    naive   = tiny['ret'].shift(-1),                       # ❌ ignores permno
    grouped = tiny.groupby('permno')['ret'].shift(-1))     # ✅ resets each stock

seam = tiny.groupby('permno').tail(1).head(1).index        # last row of stock 1
print(tiny.loc[seam[0]-1:seam[0]+2, ['permno','date','ret','naive','grouped']].to_string(index=False))
print("\\nOn the last row of the first stock, `naive` reaches across into the next")
print("company's first return. `grouped` correctly returns NaN.")"""))

cells.append(md("""> **⚠️ Caution: `groupby` before you `shift`**
>
> ```python
> df['ret_fwd'] = df.groupby('permno')['ret'].shift(-1)   # ✅
> df['ret_fwd'] = df['ret'].shift(-1)                     # ❌ crosses stocks
> ```
>
> The wrong version produces a full column of plausible numbers with a handful
> of nonsense values buried at every stock boundary — roughly 18,000 of them in
> this panel. Nothing errors, and the contamination is invisible in any summary
> statistic.
>
> Our build went further: it only fills `ret_fwd` when the next observation is
> the very **next calendar month**, so a gap in a stock's history never splices
> returns across a missing period either."""))

# ─── Return distributions ─────────────────────────────────────────────
cells.append(md("""---

## 3. What Returns Actually Look Like <a id="distributions"></a>

You now have 1.5 million monthly stock returns. Before building anything with
them, look at them.

Almost every formula you will meet this semester — Sharpe ratios, mean-variance
optimization, confidence intervals — behaves as though returns were normally
distributed. They are not, and the gap is not small."""))

cells.append(code("""from scipy import stats
r = panel['ret'].dropna()

print(f"{len(r):,} monthly stock returns")
print(f"  mean {r.mean():.4f}   sd {r.std():.4f}")
print(f"  skewness          {stats.skew(r):7.2f}    (normal: 0)")
print(f"  excess kurtosis   {stats.kurtosis(r):7.1f}    (normal: 0)\\n")

print("How often do big moves actually happen?\\n")
print(f"{'':12s}{'actual':>10s}{'if normal':>12s}{'ratio':>10s}")
for k in [3, 5, 10]:
    emp  = (np.abs(r - r.mean()) > k*r.std()).mean()
    theo = 2*stats.norm.sf(k)
    ratio = f"{emp/theo:,.0f}x" if theo > 1e-12 else "astronomical"
    print(f"  |r| > {k}sd {emp:>9.3%}{theo:>12.4%}{ratio:>10s}")

print(f"\\nworst single stock-month : {r.min():.1%}")
print(f"best  single stock-month : {r.max():.1%}")
print(f"stock-months losing > 50%: {(r < -0.5).sum():,}")"""))

cells.append(code("""fig, ax = plt.subplots(1, 2, figsize=(13, 4))
x = np.linspace(-0.6, 0.6, 300)
ax[0].hist(r[(r > -0.6) & (r < 0.6)], bins=120, density=True,
           alpha=0.65, color='steelblue', label='Actual returns')
ax[0].plot(x, stats.norm.pdf(x, r.mean(), r.std()), 'k--', lw=2, label='Normal')
ax[0].set_title('Individual stocks: too peaked, too fat', fontweight='bold')
ax[0].set_xlabel('Monthly return'); ax[0].legend()

mkt_pre = (panel.dropna(subset=['ret_fwd','me'])
             .groupby('date').apply(lambda g: np.average(g['ret_fwd'], weights=g['me'])))
ax[1].hist(mkt_pre, bins=40, density=True, alpha=0.65, color='darkorange', label='Market')
xm = np.linspace(mkt_pre.min(), mkt_pre.max(), 300)
ax[1].plot(xm, stats.norm.pdf(xm, mkt_pre.mean(), mkt_pre.std()), 'k--', lw=2, label='Normal')
ax[1].set_title('The market: much tamer, still not normal', fontweight='bold')
ax[1].set_xlabel('Monthly return'); ax[1].legend()
plt.tight_layout(); plt.show()

print(f"Market:  sd {mkt_pre.std():.4f}   skew {stats.skew(mkt_pre):.2f}   "
      f"excess kurtosis {stats.kurtosis(mkt_pre):.1f}")
print(f"worst month: {mkt_pre.min():.1%}  ({mkt_pre.idxmin().date()})")"""))

cells.append(md("""### Three stylized facts

**1. Fat tails.** A 5-standard-deviation monthly move should happen roughly
once in 3 million observations. In this data it happens in about 1 in 300.
That is not a small discrepancy — it is thousands of times too often.

**2. Positive skew in individual stocks, negative skew in the market.** A single
stock can go up 2,400% and can only fall 100%, so its distribution is skewed
right. The *market* is skewed **left** — crashes are sharper than rallies. The
worst month in this sample is October 1987, at −22.6%.

**3. Diversification tames the tails but does not remove them.** Individual
stocks have excess kurtosis of 374. The market portfolio, holding all 6,000 of
them, still has excess kurtosis above 3.

> **⚠️ Caution: what this costs you later**
>
> The Sharpe ratio summarizes a strategy with a mean and a standard deviation.
> That is a complete description **only** if returns are normal. They are not,
> so two strategies with identical Sharpe ratios can have very different odds of
> a catastrophic month. Keep this in mind every time you see one.

> **🐍 Python Insight: the −100% returns are real**
>
> `r.min()` is exactly −1.0. Those are delisting returns — companies that went
> to zero, kept in the data on purpose. A dataset without them would look
> better and be wrong."""))

# ─── Pitfall checklist ────────────────────────────────────────────────
cells.append(md("""---

## 🛡️ Pitfall Checklist for Building Portfolios <a id="pitfalls"></a>

| | Pitfall | What goes wrong | 🔍 How to detect |
|---|---|---|---|
| 1 | **Weighting by contemporaneous market cap** | Look-ahead — you weight by end-of-month size and claim that month's return | Are you pairing `me` at *t* with `ret_fwd`, not `ret`? |
| 2 | **Weights that don't sum to 1** | Your "portfolio return" is scaled by an arbitrary constant | `w.sum()` — is it 1.0? (Or 0.0 for a long-short.) |
| 3 | **Equal-weighting by accident** | `.mean()` instead of a weighted average silently makes a small-cap bet | Did you pass a `weights=` argument at all? |
| 4 | **Dropping NaNs after forming weights** | The surviving weights no longer sum to 1 | Drop first, then compute weights |
| 5 | **Survivorship in the universe** | Delisted firms missing → returns biased up | Does the stock count fall in bad years? It should. |
| 6 | **Misaligned month-ends** | Merging `2000-01-01` against `2000-01-31` silently drops everything | Check row counts before and after a merge |

> **🤖 AI-Era Insight**
>
> Ask an AI to "compute the value-weighted market return from this panel" and it
> will very often write `np.average(g['ret'], weights=g['me'])` — pitfall 1,
> exactly. The code is elegant, it runs, and the resulting market return is too
> high. You have to know to ask for `ret_fwd`."""))

# ─── 4. Weights ───────────────────────────────────────────────────────
cells.append(md(r"""---

## 4. Portfolio Weights <a id="weights"></a>

A portfolio is a vector of weights $w = (w_1, \dots, w_N)$, where $w_i$ is the
fraction of your capital in stock $i$.

$$\sum_{i=1}^{N} w_i = 1$$

That constraint says you invested all your money and no more. Three cases worth
naming:

| Weights | Meaning |
|---|---|
| $w_i = 1/N$ | **Equal-weighted** — same dollars in every stock |
| $w_i = ME_i / \sum_j ME_j$ | **Value-weighted** — proportional to company size |
| $\sum_i w_i = 0$ | **Long-short, self-financed** — the excess return from Lecture 1 |

That last row is the callback. When you computed $r - r^f$ last week you were
describing a portfolio with weights $(+1, -1)$ on the stock and the risk-free
asset. They sum to zero. It costs nothing to enter, so what it returns is a
spread, not a return on capital.

> **💡 Key Insight**
>
> Value-weighting is not a choice about which stocks you like. It is the only
> weighting that *everyone can hold at once*. If every investor tried to hold an
> equal-weighted portfolio, there would not be enough shares of the small
> companies to go around. The value-weighted portfolio **is** the market.

### And it costs nothing to maintain

Value weights have a property no other scheme has: **they rebalance themselves.**

If a stock doubles, its market cap doubles, and its correct weight doubles — but
so did the value of your holding. You trade nothing. Every other weighting
scheme drifts away from its target as prices move and has to be traded back.

That is the entire reason index funds work, and why the first one could charge
almost nothing. Hold this thought for Lecture 15, when we put a price on
turnover.

> **📌 Remember**
>
> Value-weighted → zero turnover from price moves.
> Equal-weighted → you must sell winners and buy losers every single month."""))

# ─── Live Demo 1 ──────────────────────────────────────────────────────
cells.append(md("""---

## 🔄 Live Demo: Portfolio Returns <a id="demo1"></a>

### Step 1 — The specification

> **📝 Spec**
>
> Using `panel`, for each month compute the return of a portfolio that holds
> every available stock, weighted by market equity `me` observed at that month
> end, and earns each stock's `ret_fwd`. Return a monthly series indexed by
> date. Drop stock-months where either `me` or `ret_fwd` is missing, **before**
> forming weights.

What's pinned down here, and what would a vague version have left open?
- ✅ Which return column — the whole ballgame (pitfall 1)
- ✅ Drop-then-weight ordering (pitfall 4)
- ✅ What the output looks like

### Step 2 — Implementation

> **🤖 AI prompt:**
>
> *"Given a long DataFrame `panel` with columns permno, date, ret_fwd, me, group
> by date and compute the market-cap-weighted average of ret_fwd using me as
> weights. Drop rows with missing ret_fwd or me first. Return a Series indexed
> by date."*"""))

cells.append(code("""# What competent AI-generated code looks like:
d = panel.dropna(subset=['ret_fwd', 'me'])          # drop FIRST (pitfall 4)

vw = d.groupby('date').apply(
        lambda g: np.average(g['ret_fwd'], weights=g['me']))
ew = d.groupby('date')['ret_fwd'].mean()

print(f"{len(vw)} monthly observations")
print(f"VW mean {vw.mean()*12:.2%}/yr   vol {vw.std()*np.sqrt(12):.2%}")
print(f"EW mean {ew.mean()*12:.2%}/yr   vol {ew.std()*np.sqrt(12):.2%}")"""))

cells.append(md(r"""### Step 3 — Validate

The weighted average above is exactly the matrix expression

$$r_p = w' r = \sum_i w_i r_i$$

Let's confirm that by doing it the explicit way for a single month — and check
the weights really do sum to one."""))

cells.append(code("""# One month, done explicitly
m = d[d.date == '1995-06-30'].copy()
w = m['me'] / m['me'].sum()                  # value weights

print(f"stocks in June 1995 : {len(m):,}")
print(f"weights sum to      : {w.sum():.10f}")
print(f"largest weight      : {w.max():.4%}")
print(f"smallest weight     : {w.min():.8%}")
print(f"\\nw' r  (explicit)   : {(w * m['ret_fwd']).sum():.6f}")
print(f"np.average         : {np.average(m['ret_fwd'], weights=m['me']):.6f}")
print(f"vw series          : {vw.loc['1995-06-30']:.6f}")"""))

cells.append(md("""> **🐍 Python Insight: `@` for the dot product**
>
> `(w * r).sum()` and `w @ r` compute the same thing. The `@` operator is matrix
> multiplication, and once portfolios have covariance matrices in them (Lecture
> 12) you'll want it. For now, either is fine.

> **🤔 Look at those weights before moving on.**
>
> The largest single weight is a few percent. The smallest is under a
> millionth. There are ~6,000 stocks, and the bottom half of them collectively
> barely register. Hold that thought."""))

# ─── VW vs EW ─────────────────────────────────────────────────────────
cells.append(md("""---

## 5. Value- vs Equal-Weighting <a id="vwew"></a>

Two portfolios, same 6,000 stocks, same months. The only difference is the
weights. They are not close to the same thing.

Equal-weighting puts the same dollars in the 3,000th-largest company as in
General Electric. Since there are far more small companies than large ones,
**an equal-weighted portfolio is overwhelmingly a bet on small stocks** — even
though nobody chose to make that bet."""))

# ─── Hands-On ─────────────────────────────────────────────────────────
cells.append(md("""---

## 🛠️ Hands-On: Which One Is Bigger, and Why? <a id="ho1"></a>

### Your task

You have `vw` and `ew`. Work out how concentrated the value-weighted portfolio
actually is: what share of the total market do the largest 10 stocks represent?
Then compare the two portfolios' returns and volatility.

> **🤔 Predict first.** Small stocks are riskier, and riskier things should earn
> more on average. So equal-weighting — which loads up on small stocks — should
> *beat* value-weighting over 20 years. Commit to yes or no before you run it."""))

cells.append(code("""# === YOUR TURN ===
# Fill in the two blanks.

last = d[d.date == d.date.max()]
top10_share = ____          # hint: last.nlargest(10,'me').me.sum() / last.me.sum()

print(f"Top 10 stocks are {top10_share:.1%} of total market cap")
print(f"...out of {len(last):,} stocks in the market that month\\n")

spread = ____               # hint: (ew - vw).mean() * 12   — annualized EW minus VW
print(f"EW mean:  {ew.mean()*12:7.2%}/yr    vol {ew.std()*np.sqrt(12):6.2%}")
print(f"VW mean:  {vw.mean()*12:7.2%}/yr    vol {vw.std()*np.sqrt(12):6.2%}")
print(f"EW - VW:  {spread:+7.2%}/yr")"""))

cells.append(code("""fig, ax = plt.subplots(figsize=(11, 4.5))
ax.plot(vw.index, (1+vw).cumprod(), label='Value-weighted', linewidth=1.8)
ax.plot(ew.index, (1+ew).cumprod(), label='Equal-weighted', linewidth=1.8)
ax.set_yscale('log'); ax.set_ylabel('Growth of $1 (log scale)')
ax.set_title('Same 6,000 stocks, two weighting schemes', fontweight='bold')
ax.legend(); plt.tight_layout(); plt.show()"""))

cells.append(md("""### What did you find?

Equal-weighting **lost** to value-weighting over 1980–2000 — by about 1.5% a
year — *and* it was substantially more volatile. More risk, less return.

That should bother you. The standard story says small stocks earn a premium.
Over these twenty years they did not.

> **💡 Key Insight**
>
> The size premium that Banz documented in 1981 largely disappeared from about
> the moment he published it. We'll look at this directly in Lecture 3, and it
> is a preview of one of the course's recurring themes: published anomalies have
> an unfortunate habit of dying once people know about them.

> **⚠️ Caution: the equal-weighted portfolio is not tradeable at scale**
>
> To hold it you would have to buy the same dollar amount of the 6,000th-largest
> US company as of GE — and many of those companies trade a few thousand dollars
> a day. Its measured return is real; your ability to capture it is not. That's
> Lecture 15."""))

# ─── Challenge ────────────────────────────────────────────────────────
cells.append(md("""---

## 🎯 Challenge: Rebuild the Market <a id="challenge"></a>

You just built the US stock market from 1.5 million rows of individual stock
returns. Now let's check it against the official series.

Ken French publishes the CRSP value-weighted market return, which is what
every asset-pricing paper uses as "the market." If your construction is right,
yours should match his almost exactly."""))

cells.append(code("""# Ken French's market return (already excess of the risk-free rate, so add RF back)
import pandas_datareader.data as web
ff = web.DataReader('F-F_Research_Data_Factors', 'famafrench', start='1980-01-01')[0] / 100
ff.index = pd.to_datetime(ff.index.to_timestamp()) + pd.offsets.MonthEnd(0)
ff_mkt = (ff['Mkt-RF'] + ff['RF']).rename('ff_mkt')

print(ff_mkt.head(3).to_string())"""))

cells.append(md("""### Q1 — Align and compare

Your `vw` series is indexed by the month in which you **formed** the portfolio,
but it holds the **next** month's return. Ken French's series is indexed by the
month the return was earned. Shift yours forward one month end, then join.

> **⚠️ If you skip the shift**, your correlation will be near zero and you'll
> think you did something wrong. You didn't — the series are just offset by one
> month.
>
> **📌 Required variable names:**
> ```python
> vw_mean_annual = ____   # annualized mean of your VW market return
> vw_vol_annual  = ____   # annualized volatility
> corr_vw_ff     = ____   # correlation with Ken French's series
> ```"""))

cells.append(code("""# Your work here


# Required outputs — fill these in:
vw_mean_annual = ____
vw_vol_annual  = ____
corr_vw_ff     = ____

print(f"Your VW market: {vw_mean_annual:.2%}/yr, vol {vw_vol_annual:.2%}")
print(f"Correlation with Ken French: {corr_vw_ff:.4f}")"""))

cells.append(md("""### Q2 — The equal-weighted comparison

Report the annualized mean and volatility of the equal-weighted portfolio over
the same aligned sample.

> **📌 Required variable names:**
> ```python
> ew_mean_annual = ____
> ew_vol_annual  = ____
> ```"""))

cells.append(code("""# Your work here


# Required outputs — fill these in:
ew_mean_annual = ____
ew_vol_annual  = ____

print(f"EW: {ew_mean_annual:.2%}/yr, vol {ew_vol_annual:.2%}")
print(f"VW: {vw_mean_annual:.2%}/yr, vol {vw_vol_annual:.2%}")"""))

cells.append(md("""### Q3 — Concentration

Report `top10_share` from the Hands-On above — the share of total market
capitalization held by the ten largest stocks in the final month.

> **📌 Required variable name:** `top10_share` *(already computed — just make
> sure it's still defined)*

### Q4 — The memo

> **📝 Your task — maximum 5 sentences**
>
> You built two portfolios from identical data and identical stocks. The
> equal-weighted one earned less with more volatility. Explain why the two
> differ so much, and argue for which of the two deserves to be called "the
> market." Mention one reason the equal-weighted return might overstate what an
> investor could actually have earned."""))

cells.append(code('''MEMO = """
Write your memo here. Don't delete the surrounding triple quotes.
"""
print(MEMO)'''))

cells.append(md("---\n\n## 📤 Submission <a id=\"submit\"></a>"))

cells.append(code('''# === 📤 SUBMISSION CELL — Run this last ===
import json, base64, hashlib, datetime as dt

required = ["vw_mean_annual", "vw_vol_annual", "corr_vw_ff",
            "ew_mean_annual", "ew_vol_annual", "top10_share", "MEMO"]
missing = [v for v in required if v not in dir()]
if missing:
    raise NameError(f"\\n❌ Missing before submission: {missing}")

payload = {
    "assignment": "L2_Portfolios_AI",
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

1. **Stock data is stored long, one row per stock-month**, because the universe
   changes every month. `groupby('date')` is the operation you will use more
   than any other this semester.

2. **CRSP includes companies that failed.** Any dataset built from today's
   survivors has already answered your research question for you, wrongly.

3. **A portfolio is a weight vector.** Weights summing to 1 means fully
   invested; summing to 0 means self-financed long-short.

4. **A portfolio return is `w′r`** — a weighted average, one line of code.

5. **Form weights at *t*, earn `ret_fwd`.** Pairing `me` at *t* with `ret` at
   *t* is look-ahead, and it is the most common way to accidentally invent a
   great strategy.

6. **Value-weighting is the market.** It's the only scheme all investors can
   hold simultaneously. Equal-weighting is an unintentional small-cap bet.

7. **Returns are not normal.** 5-sigma monthly moves happen thousands of times
   more often than a normal distribution allows. Diversification tames the tails
   but does not remove them — and the Sharpe ratio cannot see any of this.

8. **Over 1980–2000, equal-weighting lost by 1.5%/yr with more volatility.**
   The size premium died roughly when it was published — a theme we'll return
   to repeatedly.

---

### Next class

You can build *a* portfolio. Next: how to build one that's a **bet** — sorting
6,000 stocks on a signal and going long the top, short the bottom. Plus, at the
end, where this data really came from and how you'd pull it yourself."""))

cells.append(md("---\n\n## 📎 Appendix — Data Loading <a id=\"appendix\"></a>"))

cells.append(code(f'''# ═══════════════════════════════════════════════════════════════════════
# 📎 APPENDIX — Belt-and-Suspenders Data Loading
# ═══════════════════════════════════════════════════════════════════════
# The panel is built once from CRSP by chapters/Finance/build_course_panel.py
# and committed to the repo, so this notebook needs no WRDS account.
#
#     panel = pd.read_parquet("{RAW}")
#
# The build applies two corrections you should know about:
#   1. Delisting returns from crsp.msedelist are compounded into the monthly
#      return, so failed companies keep their final (often -100%) month.
#   2. ret_fwd is only defined when the next observation is the very next
#      calendar month, so a gap in a stock's history never silently splices
#      returns across a missing period.

# ─── Fama-French factors: live fetch ───────────────────────────────────
# Prompt: "Using pandas-datareader, fetch F-F_Research_Data_Factors monthly from
#  the famafrench source starting 1980, convert the PeriodIndex to month-end
#  timestamps, and divide by 100 to get decimals."
def fetch_ff_monthly():
    import pandas_datareader.data as web
    f = web.DataReader('F-F_Research_Data_Factors', 'famafrench', start='1980-01-01')[0]
    f.index = pd.to_datetime(f.index.to_timestamp()) + pd.offsets.MonthEnd(0)
    return f / 100
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
