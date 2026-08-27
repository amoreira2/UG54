"""
Build FactorModels_II_AI.ipynb.

Factor Models II = the ESTIMATION lecture. Builds on Factor Models I.
Topic arc:
  - Why estimates drift (rolling beta)
  - The window-size tradeoff
  - Look-ahead bias in hedge ratios
  - Statistical significance of alpha (t-stat, intuition)
  - Persistence test (the right out-of-sample check)
  - Challenge: "Hire which manager?" — same full-sample alpha, different truth
"""

import json
from pathlib import Path

OUT = Path(__file__).parent / "FactorModels_II_AI.ipynb"


def md(text):
    return {"cell_type": "markdown", "metadata": {},
            "source": text.splitlines(keepends=True)}


def code(text):
    return {"cell_type": "code", "execution_count": None, "metadata": {},
            "outputs": [], "source": text.splitlines(keepends=True)}


cells = []

# ─── 0. Title + LOs ───────────────────────────────────────────────────
cells.append(md("""# Factor Models II — Estimation
## 🎯 Learning Objectives

By the end of this notebook, you will be able to:

1. **Estimate rolling betas and see them drift** — and explain why static beta is a fiction
2. **Diagnose the window-size tradeoff** — short = noisy, long = stale
3. **Avoid look-ahead bias** when using estimated betas in real-time
4. **Read a t-stat on alpha** and translate it into a hire/fire decision
5. **Run a persistence test** — the right out-of-sample check on a manager's track record
6. **Audit AI-generated estimation code** — using a checklist specific to time-varying parameters"""))

cells.append(md("""## 📋 Table of Contents

1. [Setup](#setup)
2. [Why Estimates Drift: Rolling Beta](#drift)
3. [Pitfall Checklist for Estimation](#pitfalls)
4. [Live Demo: Rolling Beta with AI](#demo1)
5. [The Window-Size Tradeoff](#tradeoff)
6. [Look-Ahead Bias in Hedge Ratios](#lookahead)
7. [Statistical Significance of Alpha](#tstat)
8. [The Persistence Test](#persistence)
9. [How Alpha Is Actually Found](#finding-alpha)
10. [🎯 Challenge: Hire Which Manager?](#challenge)
11. [Key Takeaways](#takeaways)
12. [Submission](#submit)"""))

cells.append(md("---\n\n## 🛠️ Setup <a id=\"setup\"></a>"))

cells.append(code("""#@title Setup (run first)
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
%matplotlib inline

plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = [10, 6]
plt.rcParams['font.size'] = 12

import warnings
warnings.filterwarnings('ignore')

from pandas_datareader.data import DataReader

def get_factors(freq='daily'):
    freq_label = '' if freq == 'monthly' else '_' + freq
    ff = DataReader(f"F-F_Research_Data_Factors{freq_label}", "famafrench", start="1921-01-01")
    df = ff[0][['RF', 'Mkt-RF']]
    df.index = pd.to_datetime(df.index)
    return df / 100

print("✅ Loaded")"""))

# ─── 1. Why Estimates Drift ───────────────────────────────────────────
cells.append(md("""---

## Why Estimates Drift: Rolling Beta <a id="drift"></a>

Last class we computed MSFT's beta on the full sample and got β ≈ 1.19. We
treated that number as if it were a property of MSFT.

**It isn't.** MSFT in 2000 was a cyclical tech-bubble stock with β > 1.5.
MSFT in 2015 was a cash-flow utility with β < 1. The "true" beta moves.

> **The question this lecture answers:** if beta moves, how do we estimate it
> at a moment in time — and how do we use that estimate without fooling ourselves?"""))

cells.append(code("""# Load MSFT and align with market factor
url_msft = 'https://raw.githubusercontent.com/amoreira2/UG54/refs/heads/main/assets/data/FactorModels_data2.csv'
df_returns = pd.read_csv(url_msft, parse_dates=['date'], index_col='date')
df_factor = get_factors()
df_returns, df_factor = df_returns.dropna().align(df_factor.dropna(), join='inner', axis=0)

df_eret = df_returns['MSFT'] - df_factor['RF']   # MSFT excess
MKT = df_factor['Mkt-RF']

print(f"Range: {df_eret.index.min().date()} to {df_eret.index.max().date()}")
print(f"Days: {len(df_eret)}")"""))

# ─── 2. Pitfall checklist ─────────────────────────────────────────────
cells.append(md("""---

## 🛡️ Pitfall Checklist for Estimation <a id="pitfalls"></a>

The pitfalls from Lecture I still apply. *These* are the new ones, specific to
time-varying estimation:

| | Pitfall | What goes wrong | 🔍 How to detect |
|---|---------|-----------------|-------------------|
| 9 | **Window too short** | Beta estimate is dominated by noise; flips around wildly | Plot rolling beta — if it looks like static, the window is too short |
| 10 | **Window too long** | Estimate is stale; doesn't reflect today's company | Compare 1y vs 5y rolling betas — if they diverge, you're stuck |
| 11 | **Look-ahead in rolling beta** | Using day-t beta to hedge day-t (you didn't have it yet) | Pretend to live-trade: did the regression use any data ≥ today? |
| 12 | **Confusing significance with importance** | t-stat > 2 → "real alpha" — but 3% alpha with 5% std error is significant AND barely useful | Look at the *magnitude* of the standard error, not just the t-stat |
| 13 | **Multiple testing** | Try 100 strategies; ~5 will show "significant" alpha by chance | Bonferroni: divide your p-value threshold by the number of tests |
| 14 | **No persistence check** | Full-sample alpha hides that all the alpha came in one regime | Split the sample. If the alphas don't agree, the alpha isn't real |

> **🤖 AI-Era Insight**
>
> The AI will happily fit a rolling regression with `pandas.rolling()` — and it
> will use TODAY'S data to compute TODAY'S beta. That's look-ahead. Your job
> is to ask: *would I have had this number in real time?*"""))

# ─── 3. Live demo 1: rolling beta ─────────────────────────────────────
cells.append(md("""---

## 🔄 Live Demo: Rolling Beta <a id="demo1"></a>

### Step 1: The Specification

> **📝 Spec**
>
> Estimate MSFT's beta using a **252-day rolling window** of daily excess
> returns regressed on the market factor. Plot the rolling beta over the
> full sample. The first 251 days should be NaN (no window yet).

### Step 2: Implementation

> **🤖 AI prompt:**
>
> *"I have `df_eret` (MSFT daily excess returns) and `MKT` (daily market
> excess returns). Compute a rolling 252-day OLS beta of df_eret on MKT.
> The result should be a pandas Series of betas indexed by date, with the
> first 251 values NaN. Plot it."*"""))

cells.append(code("""# Canonical rolling beta — using pandas .rolling() with covariance / variance
window = 252
rolling_beta = MKT.rolling(window).cov(df_eret) / MKT.rolling(window).var()

fig, ax = plt.subplots(figsize=(12, 5))
rolling_beta.plot(ax=ax, linewidth=1.5)
ax.axhline(rolling_beta.mean(), color='red', linestyle='--', alpha=0.5,
           label=f'Full-sample average = {rolling_beta.mean():.2f}')
ax.axhline(1.0, color='gray', linestyle=':', alpha=0.5, label='β = 1')
ax.set_ylabel('Rolling β (252-day window)')
ax.set_title('MSFT beta over time — it moves a lot', fontweight='bold')
ax.legend(); plt.tight_layout(); plt.show()

print(f"Min beta: {rolling_beta.min():.2f}  on {rolling_beta.idxmin().date()}")
print(f"Max beta: {rolling_beta.max():.2f}  on {rolling_beta.idxmax().date()}")"""))

cells.append(md("""### Step 3: Validate ✅

- ✅ **First 251 values NaN?** Check with `rolling_beta.head(255)`
- ✅ **Beta in a plausible range?** MSFT historical β has been 0.7–1.6. If you see 5 or -2, something is wrong.
- ✅ **No look-ahead?** `pandas.rolling().cov()` uses the **trailing** window — the value at date $t$ uses data from $t-251$ to $t$. That's OK for *historical analysis* but in Section 6 we'll see why it's NOT OK for *real-time hedging*."""))

# ─── 4. The window-size tradeoff ─────────────────────────────────────
cells.append(md("""---

## The Window-Size Tradeoff <a id="tradeoff"></a>

Why 252 days? Why not 63 days? Why not 1260 days?

| Window | What you get | What you lose |
|--------|--------------|---------------|
| **Short (e.g. 63 days)** | Picks up regime changes fast | Dominated by noise |
| **Long (e.g. 1260 days = 5 yrs)** | Tight estimate (low noise) | Misses structural changes |

This is the classic **bias-variance tradeoff**:
- Short window → low bias, high variance
- Long window → high bias (using stale data), low variance"""))

cells.append(code("""# Compare three window lengths side by side
fig, ax = plt.subplots(figsize=(12, 5))
for w, color in [(63, 'steelblue'), (252, 'orange'), (1260, 'red')]:
    rb = MKT.rolling(w).cov(df_eret) / MKT.rolling(w).var()
    rb.plot(ax=ax, label=f'{w}-day window', linewidth=1.2, color=color, alpha=0.8)
ax.axhline(1.0, color='gray', linestyle=':', alpha=0.5)
ax.set_ylabel('Rolling β')
ax.set_title('Window size: noise vs. staleness', fontweight='bold')
ax.legend(); plt.tight_layout(); plt.show()"""))

cells.append(md("""> **💡 Key Insight**
>
> Look at the **63-day** line — it spikes through 1.5 and 0.5 within months. Most
> of that is *noise*, not real beta movement.
>
> Look at the **1260-day** line — it's smooth, but in 2020 (COVID) it took years
> to adjust. If you'd used it to hedge in 2020, your hedge would be wrong.
>
> 252 days (1 year) is the common compromise. Pod shops use shorter (often 60–125)
> because they're rehedging daily; long-horizon investors use longer (3–5 years).
> **There is no right answer.**"""))

# ─── 5. Look-ahead bias ───────────────────────────────────────────────
cells.append(md("""---

## Look-Ahead Bias in Hedge Ratios <a id="lookahead"></a>

You want to hedge MSFT in real time. You decide to use a 252-day rolling beta.

Question: when you hedge on **2020-03-15** (COVID crash day), which beta do you
use?

| Option | What it means | OK in real time? |
|--------|---------------|------------------|
| `rolling_beta.loc['2020-03-15']` | Beta computed using data **up to and including** Mar 15 | ⚠️ Used Mar 15 returns to predict Mar 15 → look-ahead |
| `rolling_beta.shift(1).loc['2020-03-15']` | Beta computed using data **up to Mar 14** | ✅ Correct — only uses past data |

The shift looks tiny but it matters a LOT during volatile periods.

### 🔄 Specify → Implement → Validate (Round 2)

> **📝 Spec**
>
> Build TWO dynamic-hedge series:
> (i) `hedge_lookahead` = MSFT excess − rolling_beta × MKT (uses contemporaneous beta)
> (ii) `hedge_realtime`  = MSFT excess − rolling_beta.shift(1) × MKT (uses lagged beta)
>
> Plot the cumulative returns of both. They should be subtly different. The
> *lookahead* version will outperform the realtime one — that outperformance is
> the bias.

> **🤖 AI prompt:**
>
> *"Given `df_eret` (MSFT excess), `MKT`, and `rolling_beta` (252-day rolling),
> construct (a) `hedge_lookahead` = df_eret − rolling_beta × MKT,
> (b) `hedge_realtime` = df_eret − rolling_beta.shift(1) × MKT. Plot cumulative
> returns of both on one chart. Report each one's mean and Sharpe."*"""))

cells.append(code("""# Implementation
hedge_lookahead = df_eret - rolling_beta          * MKT
hedge_realtime  = df_eret - rolling_beta.shift(1) * MKT

both = pd.DataFrame({'hedge (look-ahead)': hedge_lookahead,
                     'hedge (real-time)':  hedge_realtime}).dropna()

fig, ax = plt.subplots(figsize=(12, 5))
(1 + both).cumprod().plot(ax=ax, linewidth=1.5)
ax.set_yscale('log'); ax.set_ylabel('Growth of \\$1')
ax.set_title('Look-ahead vs real-time hedge — gap is the bias', fontweight='bold')
plt.tight_layout(); plt.show()

print(f"Mean (look-ahead, ann.):  {hedge_lookahead.mean() * 252:.2%}")
print(f"Mean (real-time, ann.):   {hedge_realtime.mean()  * 252:.2%}")
print(f"Sharpe (look-ahead):      {hedge_lookahead.mean()/hedge_lookahead.std()*np.sqrt(252):.2f}")
print(f"Sharpe (real-time):       {hedge_realtime.mean() /hedge_realtime.std() *np.sqrt(252):.2f}")"""))

cells.append(md("""> **⚠️ Caution**
>
> Backtests that quietly use look-ahead inflate Sharpe ratios by 0.1–0.3 routinely.
> When a strategy looks "too good," the first thing to check is whether *any*
> input variable contains data the strategy wouldn't have had in real time.
> **The shift is your friend.**"""))

# ─── 6. Statistical significance of alpha ─────────────────────────────
cells.append(md("""---

## Statistical Significance of Alpha <a id="tstat"></a>

You run a regression. You see α = 5%/year. Is that real or luck?

The **standard error** of your alpha estimate tells you how much it would
move under a different random draw. The **t-statistic** is the ratio:

$$t = \\frac{\\hat\\alpha}{\\text{SE}(\\hat\\alpha)}$$

Rough guide:

| |t| | Interpretation |
|-----|----------------|
| < 1.0 | Indistinguishable from zero |
| 1.0 – 2.0 | Suggestive, not conclusive |
| 2.0 – 3.0 | "Statistically significant" (95% confidence) |
| > 3.0 | Strong evidence |

> **⚠️ Caution — significance ≠ importance**
>
> A 0.1%/year alpha with t = 4 is statistically significant but economically
> trivial. A 10%/year alpha with t = 1.2 is economically huge but statistically
> uncertain. **Both numbers matter.**

> **⚠️ Caution — multiple testing**
>
> If you try 100 random "strategies," 5 will show t > 2 by pure chance.
> Don't mistake fishing for skill. (Look up [Harvey, Liu & Zhu 2016](https://academic.oup.com/rfs/article/29/1/5/1843824) — "Of factors anything goes if you look at enough of them.")"""))

cells.append(code("""# Full-sample regression for MSFT — read the t-stat
X = sm.add_constant(MKT)
model = sm.OLS(df_eret, X).fit()

alpha_d = model.params['const']
se_alpha_d = model.bse['const']
t_alpha = model.tvalues['const']

print(f"Alpha (daily):           {alpha_d:.6f}")
print(f"SE of alpha (daily):     {se_alpha_d:.6f}")
print(f"t-stat on alpha:         {t_alpha:.2f}")
print(f"Alpha (annualized):      {alpha_d * 252:.2%}")
print(f"SE of alpha (annualized):{se_alpha_d * 252:.2%}")
print(f"\\n95% CI on annual α:     [{(alpha_d - 1.96*se_alpha_d)*252:+.2%}, {(alpha_d + 1.96*se_alpha_d)*252:+.2%}]")"""))

cells.append(md("""> **📌 Remember**
>
> The 95% confidence interval is what your CIO actually wants to see — it's the
> range the true alpha probably lives in. A point estimate of "5% alpha" with a
> CI of [-3%, +13%] is a different story from a point estimate of "5% alpha"
> with a CI of [4%, 6%]."""))

# ─── Why means are uniquely hard ──────────────────────────────────────
cells.append(md("""### Why Means Are Uniquely Hard

For most parameters (β, variance, correlations) the standard error shrinks
as you collect more observations — sampling more *frequently* helps.

**For means (and α is a mean!), this is not true.** The standard error of a
sample mean is:

$$\\text{SE}(\\hat{E}[r^e]) = \\sqrt{\\frac{\\text{Var}(r^e)}{T}}$$

Here $T$ is **calendar time**, not observation count. If you switch from
daily to minute data, both $\\text{Var}(r^e)$ and $T$ scale with frequency
and the SE doesn't budge.

> **💡 Key Insight: "Only time will tell"**
>
> Sampling more frequently doesn't help you estimate a mean. It helps for
> betas and variances, but not means. The only thing that helps a mean is
> *more calendar time*.

How many years do you need before you can be 95% confident a strategy's
alpha is positive? Setting the t-stat to 1.64:

$$T = \\left(\\frac{1.64}{\\text{Sharpe}}\\right)^2$$"""))

cells.append(code("""# Years of data needed to detect an alpha at the 95% level, by Sharpe
import numpy as np
for sharpe in [0.3, 0.5, 0.7, 1.0, 1.5, 2.0]:
    T = (1.64 / sharpe) ** 2
    print(f"Sharpe = {sharpe:>3.1f}   →   need {T:>5.1f} years for 95% confidence")"""))

cells.append(md("""> **💡 Why high-Sharpe strategies are valuable**
>
> A Sharpe-0.4 strategy (market-like) needs ~17 years before you can say
> with 95% confidence that it's not just luck. A Sharpe-2 strategy needs
> less than a year. So one reason high-Sharpe strategies are prized is
> that you can *detect* them quickly with limited data — not just that
> the performance itself is better.
>
> Corollary: opening a hedge fund with a Sharpe-0.5 alpha strategy is
> hard. Even if you're right, your investors need a decade of returns
> before they can statistically distinguish you from noise."""))

# ─── 7. Persistence test ──────────────────────────────────────────────
cells.append(md("""---

## The Persistence Test <a id="persistence"></a>

The t-stat tells you whether your estimate is far from zero. It does NOT tell
you whether the underlying alpha is **stable** — i.e., whether the manager
who earned alpha last decade will earn it next decade.

The simplest persistence test: **split the sample in half**. Compute alpha in
each half. Ask:

1. Are both halves' alphas significantly positive?
2. Are they roughly the **same magnitude**?

If yes to both: persistent skill. If alpha collapses or flips sign in the
second half: the full-sample number was driven by one lucky regime.

This is a coarse test (with only 2 sub-periods you can't say much). Better
tests exist — bootstrap, walk-forward — but the split-sample is the cheapest
sanity check, and it catches the most embarrassing mistakes."""))

# ─── How alpha is actually found ──────────────────────────────────────
cells.append(md("""---

## How Alpha Is Actually Found <a id="finding-alpha"></a>

We just spent a lecture showing that you **cannot reliably estimate alpha
from historical returns alone**. Sample sizes are tiny relative to the
required precision, and persistence is rare. So where does real alpha
come from in practice?

Three buckets:

### 1. Valuation / Business Judgment
You understand a company or industry better than the market does. Buffett's
entire edge. Einhorn shorting Lehman in 2008. Requires deep fundamental
research and often access to management (legal access — public meetings,
calls, conferences). The edge is being **right when others are wrong AND
understanding why others are wrong.**

### 2. Liquidity Provision
Forced sellers push prices below fundamentals. Common forced-seller events:
- A stock is dropped from the S&P 500 → index funds must sell
- A firm is downgraded → some funds can only hold investment-grade
- A mutual fund suffers outflows → must sell whatever it holds

You take the other side. The bet: the move is *not* driven by fundamentals,
so it will revert. Citadel, Millennium, market makers live here.

### 3. Proprietary Data
See the world before others do. Satellite imagery of retail parking lots,
shipping flows, credit card panels, web scraping, alt data. The edge isn't
the model — it's the **data nobody else has**.

> **⚠️ What's NOT on this list**
>
> Backtesting factor models on public data. ML-on-public-features. Optimization
> over historical returns. These discover *factor premia* (real but commoditized)
> — not alpha. The minute the trade is crowded, the alpha disappears.

> **📌 Remember: Crowded trades**
>
> A crowded trade can deliver **negative** alpha even when the original idea
> was correct. Being right + being early ≠ being profitable. Real alpha
> requires you to be right, early, AND able to size up before everyone else
> catches on. This is why you can read about Buffett's strategy and still
> not be Buffett."""))

# ─── 8. THE CHALLENGE ─────────────────────────────────────────────────
cells.append(md("""---

## 🎯 Challenge: Hire Which Manager? <a id="challenge"></a>

> **The setup**
>
> Your fund is hiring. Two managers are finalists: **Mgr X** and **Mgr Y**.
> Both have a 10-year daily track record (2015–2024). Their **full-sample
> alphas are essentially identical** — about 4%/year.
>
> You have one offer to extend. Who do you hire?

### 🤖 The new skill
You may use AI. Your value is in **knowing what test to run, auditing
the output, and writing the recommendation.**"""))

cells.append(code("""# Load the challenge data
url_chal = 'https://raw.githubusercontent.com/amoreira2/UG54/refs/heads/main/assets/data/Estimation_AI_challenge.csv'
mgrs = pd.read_csv(url_chal, parse_dates=['date'], index_col='date')
print(f"Range: {mgrs.index.min().date()} to {mgrs.index.max().date()}")
print(f"Columns: {list(mgrs.columns)}")
mgrs.head(3)"""))

cells.append(md("""> **📌 Data dictionary**
>
> | Column | Meaning |
> |--------|---------|
> | `MKT` | Market excess return (net of RF) |
> | `RF`  | Daily risk-free rate (decimal) |
> | `Mgr_X` | Manager X **total** daily return |
> | `Mgr_Y` | Manager Y **total** daily return |
>
> ⚠️ Subtract RF to get excess returns before regressing."""))

cells.append(md("""### Q1 — Full-sample alphas

Run a CAPM regression for each manager. Report annualized α, β, and the
**t-stat on α** for each. Confirm: the alphas are similar.

> **📌 Required variable names:**
> ```python
> alpha_x_full = ____   # annualized
> alpha_y_full = ____
> tstat_x_full = ____
> tstat_y_full = ____
> ```"""))

cells.append(code("""# Your work here


# Required outputs:
alpha_x_full = ____
alpha_y_full = ____
tstat_x_full = ____
tstat_y_full = ____

print(f"Mgr X: α = {alpha_x_full:+.2%}/yr   t-stat = {tstat_x_full:.2f}")
print(f"Mgr Y: α = {alpha_y_full:+.2%}/yr   t-stat = {tstat_y_full:.2f}")"""))

cells.append(md("""### Q2 — Split the sample

Split each manager's history into two halves (use `len(mgrs) // 2` as the
breakpoint). Compute α in each half.

> **📌 Required variable names:**
> ```python
> alpha_x_half1 = ____   # annualized α for Mgr X, first half
> alpha_x_half2 = ____   # annualized α for Mgr X, second half
> alpha_y_half1 = ____
> alpha_y_half2 = ____
> ```"""))

cells.append(code("""# Your work here


# Required outputs:
alpha_x_half1 = ____
alpha_x_half2 = ____
alpha_y_half1 = ____
alpha_y_half2 = ____

print(f"Mgr X:  half-1 α = {alpha_x_half1:+.2%}   half-2 α = {alpha_x_half2:+.2%}")
print(f"Mgr Y:  half-1 α = {alpha_y_half1:+.2%}   half-2 α = {alpha_y_half2:+.2%}")"""))

cells.append(md("""### Q3 — The persistence ratio

For each manager, compute the **persistence ratio**: half-2 α divided by
half-1 α. A value near +1 means the alpha persisted. A value near 0 or
negative means it didn't.

> **📌 Required variable names:**
> ```python
> persistence_x = ____   # alpha_x_half2 / alpha_x_half1
> persistence_y = ____   # alpha_y_half2 / alpha_y_half1
> ```"""))

cells.append(code("""# Your work here


# Required outputs:
persistence_x = ____
persistence_y = ____

print(f"Mgr X persistence ratio: {persistence_x:+.2f}")
print(f"Mgr Y persistence ratio: {persistence_y:+.2f}")"""))

cells.append(md("""### Q4 — Rolling beta sanity check

Compute the 252-day **rolling beta** for each manager. Report the
**standard deviation** of each one's rolling beta (excluding NaN).

A manager whose beta is wildly time-varying is harder to evaluate — you
can't trust a single beta number.

> **📌 Required variable names:**
> ```python
> beta_std_x = ____   # standard deviation of Mgr X's 252-day rolling beta
> beta_std_y = ____
> ```"""))

cells.append(code("""# Your work here


# Required outputs:
beta_std_x = ____
beta_std_y = ____

print(f"Mgr X rolling β std: {beta_std_x:.3f}")
print(f"Mgr Y rolling β std: {beta_std_y:.3f}")"""))

cells.append(md("""### Q5 — The Memo

Write a **single paragraph** (max 6 sentences) to your CIO.

1. Which manager do you hire (X, Y, or neither)?
2. Cite the **one diagnostic** that drove your decision.
3. Note one risk that could make you wrong.

> **What we're looking for:** financial + statistical judgment. The full-sample
> alphas are nearly identical; the right answer requires the persistence test.
> A memo that just compares full-sample α and t-stat is missing the point.

**Write your memo as a Python string below** (the submission cell pulls it from `MEMO`):"""))

cells.append(code("""MEMO = \"\"\"
Write your 6-sentence-max memo here. Don't delete the triple quotes.
\"\"\"
print(MEMO)"""))

# ─── Submission cell ──────────────────────────────────────────────────
cells.append(md("""---

## 📤 Submission <a id="submit"></a>

Run the cell below. Copy the line that starts with `UG54::` and paste it into
the submission form: **https://forms.gle/YOUR_FORM_LINK_HERE**"""))

cells.append(code("""# === 📤 SUBMISSION CELL — Run this last ===
import json, base64, hashlib, datetime as dt

required = [
    "alpha_x_full", "alpha_y_full", "tstat_x_full", "tstat_y_full",
    "alpha_x_half1", "alpha_x_half2", "alpha_y_half1", "alpha_y_half2",
    "persistence_x", "persistence_y",
    "beta_std_x", "beta_std_y",
    "MEMO",
]
missing = [v for v in required if v not in dir()]
if missing:
    raise NameError(
        f"\\n❌ Missing variables before submission: {missing}\\n"
        "Make sure each answer cell defines the variable name listed above."
    )

payload = {
    "assignment": "FactorModels_II_AI",
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
print(f"\\nLength: {len(token)} chars")
print("Submission form: https://forms.gle/YOUR_FORM_LINK_HERE")"""))

# ─── Key Takeaways ────────────────────────────────────────────────────
cells.append(md("""---

## 🧠 Key Takeaways <a id="takeaways"></a>

1. **Static beta is a fiction.** Companies change; their betas change.

2. **Window size is a tradeoff.** Short = noise, long = stale. 252 days is a
   common compromise; there's no universally right answer.

3. **Real-time hedging needs lagged inputs.** `rolling_beta.shift(1)` is the
   line between honest backtest and look-ahead bias.

4. **Significance ≠ importance ≠ persistence.** Always look at the *standard
   error* alongside the *point estimate*, and check whether the alpha shows
   up out of sample.

5. **Means are uniquely hard.** Only calendar time helps. Sharpe-0.5 alpha
   needs ~11 years to clear t > 1.64. High-Sharpe strategies are valuable
   partly because you can *detect* them quickly.

6. **The persistence test is the cheapest sanity check.** Split the sample.
   If alpha collapses or flips, the full-sample number was luck.

7. **Alpha isn't found by regression.** It comes from valuation, liquidity
   provision, or proprietary data. Backtests find factor premia, not alpha.
   Crowded trades destroy alpha even when the original idea was right.

8. **AI generates code, you generate judgment.** The full-sample regression
   is one line of code. Knowing *which extra tests to run* — and that no
   amount of estimation will substitute for understanding *why* an edge
   exists — is the skill."""))

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
