"""
Build Timing_AI.ipynb — Lecture 8.

REBUILT to preserve the content of BOTH source notebooks:
  - MarketTiming_c.ipynb (expected returns timing)
  - Volatilitytiming_c.ipynb (volatility timing)

The original syllabus dedicated 2 lectures to these. We compress to one tight
lecture by:
  - PART I: The market-timing conceptual setup (predictability puzzle, DP regression,
    HAC for overlap, OOS evaluation, signal-to-weight)
  - PART II: Volatility timing as the practical alternative

Real data preserved:
  - Markettiming_data1.csv (vwretd, vwretx, dp from CRSP)
  - Live FF daily for realized variance
"""

import json
from pathlib import Path

OUT = Path(__file__).parent / "Timing_AI.ipynb"

def md(t): return {"cell_type":"markdown","metadata":{},"source":t.splitlines(keepends=True)}
def code(t): return {"cell_type":"code","execution_count":None,"metadata":{},"outputs":[],"source":t.splitlines(keepends=True)}

cells = []

# ─── Title + LOs (preserve both source notebooks) ─────────────────────
cells.append(md("""# Timing Strategies
## 🎯 Learning Objectives

By the end of this notebook, you will be able to:

1. **Distinguish two timing strategies** — predicting expected returns vs. responding to volatility
2. **Run forecasting regressions** with HAC standard errors for overlapping returns
3. **Evaluate predictability out-of-sample** with a simple train/test split
4. **Construct a market-timing strategy** by converting a signal into portfolio weights
5. **Construct a volatility-timed strategy** that scales allocation inversely to recent variance
6. **Audit AI-generated timing code** — look-ahead bias, overlap correction, weight blow-ups"""))

cells.append(md("""## 📋 Table of Contents

This notebook is designed for **two class sessions**. Class 1 covers Part I,
Class 2 covers Part II + the comparison challenge.

1. [Setup](#setup)
2. [Two Kinds of Timing](#two)
3. [Pitfall Checklist for Timing](#pitfalls)

**Part I — Market Timing (expected-return timing) — Class 1**

4. [The Predictability Puzzle](#puzzle)
5. [Dividend Yield as a Signal](#dy)
6. [Live Demo 1: Forecasting Regression with HAC](#demo1)
7. [Out-of-Sample Evaluation](#oos)
8. [From Signal to Weights](#weight)
9. [🛠️ Hands-On 1: Pick Your Own Predictor from FRED](#ho1)

**Part II — Volatility Timing — Class 2**

10. [When Volatility Timing Works](#voltheory)
11. [Realized Variance from Daily Data](#rv)
12. [Live Demo 2: Building the Vol-Timed Strategy](#demo2)
13. [🛠️ Hands-On 2: VIX² as a Forward-Looking Variance Forecast](#ho2)

14. [🎯 Challenge: Comparing Four Timing Approaches](#challenge)
15. [Submission](#submit)
16. [Key Takeaways](#takeaways)"""))

cells.append(md("---\n\n## 🛠️ Setup <a id=\"setup\"></a>"))
cells.append(code("""#@title 🛠️ Setup: Run this cell first
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
%matplotlib inline
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = [10, 6]
plt.rcParams['font.size'] = 12
import warnings; warnings.filterwarnings('ignore')

from pandas_datareader.data import DataReader
def get_factors(freq='daily'):
    suffix = '' if freq == 'monthly' else '_' + freq
    ff = DataReader(f"F-F_Research_Data_Factors{suffix}", "famafrench", start="1921-01-01")[0]
    if freq == 'monthly':
        ff.index = pd.to_datetime(ff.index.to_timestamp()) + pd.offsets.MonthEnd(0)
    else:
        ff.index = pd.to_datetime(ff.index)
    return ff / 100
print("✅ Loaded")"""))

# ─── Two kinds of timing ──────────────────────────────────────────────
cells.append(md("""---

## Two Kinds of Timing <a id="two"></a>

"Timing the market" means changing your allocation over time based on something
you observe. There are **two fundamentally different versions** of this idea:

### 1. Expected Return Timing (Market Timing)
*"The market is cheap right now — I'll add exposure."*

Find some signal $X_t$ that predicts next-period expected excess return:

$$r^e_{t+1} = a + b \\cdot X_t + u_{t+1}$$

Classic signals: **dividend yield**, earnings yield, the term-structure slope.

### 2. Risk Timing (Volatility Timing)
*"The market is volatile right now — I'll reduce exposure."*

Skip the question of expected returns. Just respond to risk:

$$w_t = \\frac{c}{\\hat\\sigma_{t+1}^2}$$

where $\\hat\\sigma_{t+1}^2$ is a forecast of next period's variance (e.g.
last month's realized variance).

> **💡 Key Insight**
>
> Expected-return timing requires forecasting something *hard* ($\\mu_{t+1}$).
> Volatility timing only requires forecasting something *easier* ($\\sigma^2_{t+1}$).
> The two strategies have very different track records — and the academic
> evidence favors the volatility version."""))

# ─── Pitfall checklist ────────────────────────────────────────────────
cells.append(md("""---

## 🛡️ Pitfall Checklist for Timing <a id="pitfalls"></a>

| | Pitfall | What goes wrong | 🔍 How to detect |
|---|---------|-----------------|-------------------|
| 1 | **Look-ahead in signal construction** | Using time-$t+1$ data to compute the signal at $t$ | Always `.shift(1)` your signal explicitly |
| 2 | **Overlapping returns inflate t-stats** | Regressing 5-year forward returns gives 59-month overlap; OLS standard errors are wildly understated | Use HAC (Newey-West) standard errors with `maxlags = horizon × frequency` |
| 3 | **In-sample R² looks great** | OLS fit to the full sample fits any noise | The OOS R² is what matters; it's often *negative* for return predictability |
| 4 | **Weight blow-ups in vol timing** | $1/\\sigma^2$ explodes when vol is low; demand leverage > 5x | Clip weights or scale so average weight is 1 |
| 5 | **Transaction costs ignored** | High-turnover strategies look great gross | Always estimate turnover × spread |
| 6 | **Structural breaks** | Dividend yield's mean shifted post-1980s (buyback era) | Plot the signal series; look for regime shifts |

> **🤖 AI-Era Insight**
>
> AI will happily fit `smf.ols('ret ~ dy', data=df)` and report a t-stat. It
> rarely catches the overlap problem; it never asks about regime shifts in the
> signal; it treats in-sample R² as evidence. **The audit is the work.**"""))

# ─── PART I: Market Timing ────────────────────────────────────────────
cells.append(md("""---
# Part I — Market Timing
---

## The Predictability Puzzle <a id="puzzle"></a>

One of the most famous findings in finance:

> **High dividend yield periods are followed by above-average returns.**

This finding (Campbell-Shiller, 1988) earned Shiller a share of the 2013 Nobel.

### Why is this surprising?

When prices are low relative to dividends (high D/P), you might expect:
- ❌ Future dividends will fall — "bad news is priced in"

But what actually happens:
- ✅ Future *prices* go up — **expected returns** were high

### The Gordon growth framing

$$P = \\frac{D}{r - g} \\quad\\Longrightarrow\\quad \\frac{D}{P} = r - g$$

A low D/P ratio means either:
- Expected returns $r$ are low, **OR**
- Expected dividend growth $g$ is high

Shiller's empirical finding: most of the variation in D/P reflects variation in
**expected returns**, not in growth. This suggests expected returns are
*time-varying* and *forecastable*.

> **💡 Key Insight**
>
> If expected returns vary predictably with D/P, you can build a **timing
> strategy** that invests more when expected returns are high."""))

# ─── Load dividend yield data ─────────────────────────────────────────
cells.append(md("""---

## Dividend Yield as a Signal <a id="dy"></a>"""))

cells.append(code("""# Load CRSP market data with dividend yield
url = 'https://raw.githubusercontent.com/amoreira2/UG54/refs/heads/main/assets/data/Markettiming_data1.csv'
crsp = pd.read_csv(url, parse_dates=['date'], index_col='date')
crsp.index = crsp.index + pd.offsets.MonthEnd(0)

print(f"Range: {crsp.index.min().date()} to {crsp.index.max().date()}")
print("Columns:")
print("  vwretd: value-weighted market return (with dividends)")
print("  vwretx: value-weighted market return (without dividends)")
print("  dp:     dividend yield (dividend / price)")
crsp.head()"""))

cells.append(code("""# Plot annualized 12-month average dividend yield
fig, ax = plt.subplots(figsize=(12, 4))
dp_annual = crsp['dp'].rolling(window=12).mean() * 12
ax.plot(dp_annual, linewidth=1.5)
ax.set_ylabel('Annualized Dividend Yield')
ax.set_title('Market dividend yield over time', fontweight='bold')
plt.tight_layout(); plt.show()"""))

cells.append(md("""> **📌 Remember**
>
> Dividend yields ranged from 4-7% in the 1930s to ~2% today. This secular
> decline matters for interpretation:
> - Firms increasingly return capital via *buybacks* instead of dividends
> - So D/P alone may understate the true cash-return yield of the market
> - Many academic papers replace D/P with the **CAPE** ratio (Shiller's earnings yield) or with total-payout yield to handle the structural shift"""))

# ─── Live Demo 1: forecasting regression with HAC ─────────────────────
cells.append(md("""---

## 🔄 Live Demo 1: Forecasting Regression with HAC <a id="demo1"></a>

Test whether dividend yield predicts the *next 5-year* market return.

### 🔴 Loose prompt — what NOT to do

> *"Test if dividend yield predicts future market returns."*

**What AI is likely to produce:**

```python
X = sm.add_constant(crsp['dp'])
y = crsp['vwretd']
model = sm.OLS(y, X).fit()
print(model.summary())
```

**The bugs:**
- ❌ Regressed *contemporaneous* returns on D/P — that's not a *forecast*; you need a future return on the left
- ❌ Picked monthly returns; for D/P the right horizon is multi-year (the variable is slow-moving)
- ❌ Used `sm.OLS` standard errors — when returns *do* overlap (multi-year horizon), these will be ~5-10× too small
- ❌ No `.dropna()` — `.fit()` will silently drop missing values without warning

### 🟢 Precise prompt — the pattern that works

> *"Compute the **5-year forward annualized return** of `crsp['vwretd']` for
> each month: take the rolling 60-month product of (1+ret), shift -60 months
> so the observation date aligns with the *start* of the forward window, take
> the 60th root and subtract 1.
> Construct the predictor as a smoothed annualized dividend yield:
> `crsp['dp'].rolling(12).mean() * 12`.
> Regress future-returns on lagged D/P using HAC (Newey-West) standard errors
> with `maxlags = 5*12 = 60` to correct for overlap. Print the summary."*"""))

cells.append(code("""# 🟢 Precise version
years = 5

# 5-year forward annualized return
crsp['R_future'] = (
    (1 + crsp['vwretd']).rolling(window=years*12).apply(np.prod)
    .shift(-years*12) ** (1/years) - 1
)
# Annualized smoothed dividend yield
crsp['dp_avg'] = crsp['dp'].rolling(window=12).mean() * 12

reg_df = crsp[['R_future', 'dp_avg']].dropna()
print(f"Sample correlation: {reg_df['dp_avg'].corr(reg_df['R_future']):.3f}")
print(f"Observations:       {len(reg_df)}")"""))

cells.append(code("""# Naive OLS — INFLATED t-stat (overlapping returns problem)
X = sm.add_constant(reg_df['dp_avg'])
y = reg_df['R_future']
model_naive = sm.OLS(y, X).fit()
print("===== Naive OLS =====")
print(f"  Slope (b):  {model_naive.params['dp_avg']:.3f}")
print(f"  t-stat:     {model_naive.tvalues['dp_avg']:.2f}    ← INFLATED")
print(f"  R²:         {model_naive.rsquared:.3f}\\n")

# HAC-corrected — the honest standard error
model_hac = sm.OLS(y, X).fit(cov_type='HAC', cov_kwds={'maxlags': years*12})
print("===== HAC (Newey-West) =====")
print(f"  Slope (b):  {model_hac.params['dp_avg']:.3f}")
print(f"  t-stat:     {model_hac.tvalues['dp_avg']:.2f}    ← honest")
print(f"  R²:         {model_hac.rsquared:.3f}")"""))

cells.append(md("""> **⚠️ Overlap inflates standard errors**
>
> The naive t-stat and the HAC t-stat differ by a factor of 2-3x. Both
> regressions fit the same line; only the inference about *whether the slope
> is different from zero* changes.
>
> Rule: **use HAC whenever your dependent variable is a multi-period return.**
> `maxlags` should be at least the number of overlapping periods (here, 60)."""))

# ─── Out-of-Sample Evaluation ─────────────────────────────────────────
cells.append(md("""---

## Out-of-Sample Evaluation <a id="oos"></a>

In-sample fit is one thing. The question that matters for trading: **does this
predict OUT OF SAMPLE?**

The simplest split: estimate the regression on early data, forecast on later
data, see if the forecast tracks realized returns."""))

cells.append(code("""# Train: 1950-1990. Test: 1991+.
estimation = crsp.loc['1950':'1990'].copy()
test       = crsp.loc['1991':].copy()

X_est = sm.add_constant(estimation['dp_avg'])
y_est = estimation['R_future']
m_est = sm.OLS(y_est, X_est, missing='drop').fit(
    cov_type='HAC', cov_kwds={'maxlags': years*12})

# Forecast for the test period using ESTIMATION-SAMPLE coefficients
test['forecast'] = m_est.params['const'] + m_est.params['dp_avg'] * test['dp_avg']

fig, ax = plt.subplots(figsize=(12, 4))
test[['R_future', 'forecast']].plot(ax=ax, linewidth=1.5)
ax.set_title("Forecast vs realized 5-year-ahead returns (out-of-sample)", fontweight='bold')
ax.set_ylabel("Annualized return")
plt.tight_layout(); plt.show()"""))

cells.append(code("""# OOS R-squared vs the in-sample mean (the proper benchmark)
r_past_avg = estimation['R_future'].mean()
ss_residual = ((test['R_future'] - test['forecast'])**2).sum()
ss_baseline = ((test['R_future'] - r_past_avg)**2).sum()
oos_r2 = 1 - ss_residual / ss_baseline
print(f"Out-of-sample R²: {oos_r2:.3f}")
print(f"  (Negative = the in-sample mean predicts BETTER than the regression.)")"""))

cells.append(md("""> **💡 Key Insight**
>
> A negative OOS R² is the dirty secret of the predictability literature. Even
> when the in-sample t-stat is significant, the out-of-sample forecast often
> performs *worse* than the long-run mean. Suggests the relationship may be
> unstable across regimes.
>
> **What could be going wrong?**
> - Structural breaks (buybacks era, secular decline in yields)
> - One-off shift in the risk premium with mean reversion around a new average
> - Look-ahead in how the model was selected in published papers"""))

# ─── Signal to weight ─────────────────────────────────────────────────
cells.append(md("""---

## From Signal to Weights <a id="weight"></a>

Even with imperfect forecasts, you can still construct a strategy. By the
single-asset MVE formula:

$$x_t = \\frac{\\mu_t}{\\gamma \\sigma^2} = \\frac{a + b \\cdot DP_t}{\\gamma \\sigma^2}$$

where $\\mu_t$ is the forecasted premium, $\\gamma$ is risk aversion, and
$\\sigma$ is volatility (assumed constant for now)."""))

cells.append(code("""# Strategy parameters
gamma = 2
vol   = 0.16  # constant 16%/yr vol assumption

test['weight']    = test['forecast'] / (gamma * vol**2)

# Get RF for the test period
ff_m = get_factors(freq='monthly')[['RF']]
test_with_rf = test.merge(ff_m, left_index=True, right_index=True, how='left')
test_with_rf['ret_timing'] = test_with_rf['RF'] + test_with_rf['weight'] * (
    test_with_rf['vwretd'] - test_with_rf['RF'])
test_with_rf = test_with_rf.dropna(subset=['ret_timing'])

# Cumulative
fig, ax = plt.subplots(figsize=(12, 5))
(1 + test_with_rf['ret_timing']).cumprod().plot(ax=ax, label='Mean-timing strategy', linewidth=2)
(1 + test_with_rf['vwretd']).cumprod().plot(ax=ax, label='Buy & hold', linewidth=2)
ax.set_yscale('log'); ax.set_ylabel('Growth of $1 (log)')
ax.set_title('Mean-timing strategy vs buy-and-hold', fontweight='bold')
ax.legend(); plt.tight_layout(); plt.show()

excess_timing = test_with_rf['ret_timing'] - test_with_rf['RF']
excess_mkt    = test_with_rf['vwretd']    - test_with_rf['RF']
sr_timing = (excess_timing.mean()*12) / (excess_timing.std()*np.sqrt(12))
sr_mkt    = (excess_mkt.mean()*12)    / (excess_mkt.std()*np.sqrt(12))
print(f"Sharpe (mean-timing):  {sr_timing:.3f}")
print(f"Sharpe (buy & hold):   {sr_mkt:.3f}")"""))

cells.append(md("""> **💡 Key Insight**
>
> Even when the OOS R² is small or negative, the **trading strategy** can
> still beat buy-and-hold on Sharpe. Why? Because the strategy uses the signal
> to *time the average exposure* — small but positive correlation between
> forecast and future returns translates into a Sharpe edge.
>
> This is the central puzzle of mean-timing: t-stats look bad, OOS R² looks
> bad, but Sharpe improvements sometimes appear anyway. **Trust the Sharpe,
> not the R².**"""))

# ─── HANDS-ON 1: Pick Your Own Predictor ──────────────────────────────
cells.append(md("""---

## 🛠️ Hands-On 1: Pick Your Own Predictor from FRED <a id="ho1"></a>

You've seen dividend yield as a predictor. **Your job: pick a different
macro/financial variable from FRED and test whether it predicts the market.**

### Why this is open-ended

There's no "right" predictor of stock returns. Researchers have proposed dozens
over the decades. Some work in some samples and fail in others. Your task is to
pick something *you think plausibly predicts equity returns* and run the same
test we ran for D/P.

### A menu of suggestions

These are all classic candidates. **Pick one, or find your own on FRED:**

| FRED series ID | Variable | Why it might predict |
|---|---|---|
| `T10Y3M` | 10Y − 3M Treasury yield spread | Steep curve at recovery starts |
| `T10Y2Y` | 10Y − 2Y Treasury yield spread | Same idea, different short rate |
| `BAA10Y` | Baa corporate − 10Y Treasury (credit spread) | Wide credit spread at stress peaks |
| `T10YIE` | 10-year breakeven inflation | Inflation expectations / real rates |
| `UNRATE` | US unemployment rate (monthly) | Labor-market / business cycle |
| `VIXCLS` | VIX (option-implied vol) | Risk premium proxy (we'll use this in Part II too) |
| `DGS10` | 10-year Treasury yield | Discount rate |

Browse the catalogue at https://fred.stlouisfed.org if none of these inspire you.

> **📌 Pick now.** Edit the cell below with your choice."""))

cells.append(code("""# === EDIT THIS CELL: your predictor of choice ===
MY_PREDICTOR_ID   = "T10Y3M"   # ← change to whatever FRED series ID you picked
MY_PREDICTOR_NAME = "Term spread (10Y − 3M)"  # ← human-readable label for plots

# ⚠️ Don't pick anything that contains stock returns directly (e.g., SP500). That's circular.

print(f"You picked: {MY_PREDICTOR_NAME}  (FRED ID: {MY_PREDICTOR_ID})")"""))

cells.append(md("""### Step 1 — Fetch your series from FRED

We use `pandas-datareader` to pull from the St. Louis Fed (free, no API key needed).
Plot the series and inspect: is it persistent? Does it spike around crises?"""))

cells.append(code("""# Fetch your chosen series from FRED
from pandas_datareader.data import DataReader
raw = DataReader(MY_PREDICTOR_ID, 'fred', start='1980-01-01').dropna()
raw.columns = ['signal']

# Many FRED series are in percent (yield, inflation, etc.). Convert to decimal
# unless your variable is naturally a level (e.g., unemployment rate stays in %).
# Rule of thumb: if the average value is > 1, divide by 100 to express in decimal.
# We'll do that here automatically — feel free to override.
if raw['signal'].mean() > 1:
    raw['signal'] = raw['signal'] / 100
    print(f"Auto-scaled by 100 (mean > 1 → likely in %)")

# Convert to monthly (end-of-month observation)
sig_monthly = raw.resample('ME').last()
print(f"Range: {sig_monthly.index.min().date()} to {sig_monthly.index.max().date()}")
print(f"Months: {len(sig_monthly)}")

# Plot
fig, ax = plt.subplots(figsize=(12, 4))
ax.plot(sig_monthly, linewidth=1.5)
ax.set_ylabel(MY_PREDICTOR_NAME)
ax.set_title(f'{MY_PREDICTOR_NAME} ({MY_PREDICTOR_ID})', fontweight='bold')
plt.tight_layout(); plt.show()"""))

cells.append(md("""### Step 2 — Merge with future returns and check correlation

Merge with the same 5-year-forward return we computed from CRSP earlier.
Sample will shrink to whatever years your predictor is available for."""))

cells.append(code("""# Merge your predictor with R_future
sig_reg = crsp[['R_future']].merge(sig_monthly, left_index=True, right_index=True, how='inner').dropna()
print(f"Regression sample: {len(sig_reg)} months "
      f"({sig_reg.index.min().date()} to {sig_reg.index.max().date()})")
print(f"Correlation between {MY_PREDICTOR_NAME} and 5y forward return: "
      f"{sig_reg['signal'].corr(sig_reg['R_future']):.3f}")"""))

cells.append(md("""### Step 3 — Run the HAC regression

Same setup as the D/P regression — use HAC with `maxlags = 60` (the overlap length)."""))

cells.append(code("""X = sm.add_constant(sig_reg['signal'])
y = sig_reg['R_future']
m_my = sm.OLS(y, X).fit(cov_type='HAC', cov_kwds={'maxlags': years*12})
print(f"=== {MY_PREDICTOR_NAME} regression (HAC) ===")
print(f"  Slope:  {m_my.params['signal']:.3f}")
print(f"  t-stat: {m_my.tvalues['signal']:.2f}")
print(f"  R²:     {m_my.rsquared:.3f}")

# Compare to D/P from earlier
print(f"\\nD/P benchmark (full sample, HAC):")
print(f"  Slope:  {model_hac.params['dp_avg']:.3f}")
print(f"  t-stat: {model_hac.tvalues['dp_avg']:.2f}")"""))

cells.append(md("""### Step 4 — Build the timing strategy

Pick an OOS split (e.g., midpoint of your sample) and train on the early half,
test on the late half. Use the same template as for D/P."""))

cells.append(code("""# Split at the midpoint of YOUR sample
mid_date = sig_reg.index[len(sig_reg) // 2]
print(f"Splitting at: {mid_date.date()}")
sig_est  = sig_reg.loc[:mid_date].copy()
sig_test = sig_reg.loc[mid_date:].copy()

m_est = sm.OLS(sig_est['R_future'], sm.add_constant(sig_est['signal']),
               missing='drop').fit(cov_type='HAC', cov_kwds={'maxlags': years*12})
sig_test['forecast'] = m_est.params['const'] + m_est.params['signal'] * sig_test['signal']

# Convert to weights (same γ, σ as for D/P)
gamma, vol = 2, 0.16
sig_test['weight'] = sig_test['forecast'] / (gamma * vol**2)

# Merge with market returns + RF for strategy P&L
sig_test_full = (
    sig_test
    .merge(crsp[['vwretd']], left_index=True, right_index=True, how='left')
    .merge(get_factors(freq='monthly')[['RF']], left_index=True, right_index=True, how='left')
    .dropna(subset=['vwretd', 'RF', 'weight'])
)
sig_test_full['ret_timing'] = sig_test_full['RF'] + sig_test_full['weight'] * (
    sig_test_full['vwretd'] - sig_test_full['RF'])

# Sharpes (OOS test window)
sr_my  = ((sig_test_full['ret_timing'] - sig_test_full['RF']).mean() * 12) / (
    (sig_test_full['ret_timing'] - sig_test_full['RF']).std() * np.sqrt(12))
sr_bh_my = ((sig_test_full['vwretd'] - sig_test_full['RF']).mean() * 12) / (
    (sig_test_full['vwretd'] - sig_test_full['RF']).std() * np.sqrt(12))

print(f"\\n{MY_PREDICTOR_NAME} timing Sharpe (OOS): {sr_my:.2f}")
print(f"Buy-and-hold Sharpe over same OOS window:   {sr_bh_my:.2f}")"""))

cells.append(md("""> **🤔 Reflect on what you found**
>
> Three questions to think about (you'll write a memo on these at the end):
>
> 1. **Did your predictor beat buy-and-hold on Sharpe?** Some classic predictors
>    DO and some DON'T. There's no single right answer — that's part of the
>    lesson.
> 2. **Is it really a useful predictor, or is the result driven by one episode?**
>    Plot the cumulative wealth of your strategy vs buy-and-hold — does the
>    outperformance come gradually, or from one or two big bets?
> 3. **Does it capture something different from D/P?** Or just the same business
>    cycle in a different disguise?
>
> Compare notes with a neighbor who picked a different predictor."""))

# ─── PART II: Volatility Timing ───────────────────────────────────────
cells.append(md("""---
# Part II — Volatility Timing
---

## When Volatility Timing Works <a id="voltheory"></a>

Same MVE formula:

$$x_t = \\frac{E_t[r^e_{t+1}]}{\\gamma \\cdot \\text{Var}_t(r^e_{t+1})}$$

Two extreme cases:

| Case | What you time | Allocation rule |
|------|---------------|-----------------|
| **$\\sigma^2$ varies, $\\mu$ constant** | Variance | $x_t = \\frac{\\mu}{\\gamma \\text{Var}_t}$ |
| **$\\mu$ varies, $\\sigma^2$ constant** | Expected returns | $x_t = \\frac{\\mu_t}{\\gamma \\sigma^2}$ |

### The decomposition

If the risk premium is itself a function of variance, $E_t[r^e] = a + b \\cdot \\text{Var}_t$, then:

$$x_t = \\frac{a + b \\cdot \\text{Var}_t}{\\gamma \\cdot \\text{Var}_t} = \\underbrace{\\frac{a}{\\gamma \\cdot \\text{Var}_t}}_{\\text{vol timing}} + \\underbrace{\\frac{b}{\\gamma}}_{\\text{constant}}$$

> **💡 Key Insight**
>
> - If $a = 0$ (premium is **proportional** to variance): NO benefit from vol timing — they cancel
> - If $b = 0$ (premium is **constant** in variance): MAXIMUM benefit from vol timing
> - Reality is somewhere in between, but **closer to $b = 0$** for most factors empirically
>
> Translation: high-vol months have similar *expected* returns to low-vol
> months, but enormously different *realized variance*. So reducing exposure
> when vol is high is unambiguously good.

> **📌 Caveat**
>
> Vol timing only helps if the factor has a positive premium to begin with.
> If $E[r^e] = 0$, no amount of vol-scaling raises the Sharpe."""))

# ─── Realized variance ────────────────────────────────────────────────
cells.append(md("""---

## Realized Variance from Daily Data <a id="rv"></a>

Estimate variance using **daily** returns within each month:

$$RV_t = \\sum_{d \\in \\text{days in month } t} (r_d - \\bar{r})^2$$

This is a non-parametric, no-model variance estimate. Use the previous month's
$RV$ to forecast next month's — empirically, vol is persistent."""))

cells.append(code("""# Load FF daily market factor
ff_daily = get_factors(freq='daily')
mkt_d = ff_daily['Mkt-RF']

# Monthly realized variance: sum of squared daily returns within each month
rv = mkt_d.groupby(mkt_d.index.to_period('M')).apply(lambda x: (x**2).sum())
rv.index = rv.index.to_timestamp(how='end').normalize()
rv.name = 'RV'

# Plot annualized realized vol
fig, ax = plt.subplots(figsize=(12, 4))
np.sqrt(rv * 12).plot(ax=ax)
ax.set_ylabel('Annualized realized vol')
ax.set_title('Market realized volatility (annualized) — clearly time-varying',
             fontweight='bold')
plt.tight_layout(); plt.show()"""))

cells.append(code("""# Verify persistence: regress RV on its own lag
rv_df = pd.concat([rv.rename('RV_t'), rv.shift(1).rename('RV_lag')], axis=1).dropna()
X = sm.add_constant(rv_df['RV_lag'])
m_ar1 = sm.OLS(rv_df['RV_t'], X).fit()
print(f"AR(1) on RV: slope = {m_ar1.params['RV_lag']:.3f}, t = {m_ar1.tvalues['RV_lag']:.1f}")
print(f"R²: {m_ar1.rsquared:.3f}")
print(f"\\n→ Last month's RV explains ~{m_ar1.rsquared:.0%} of this month's RV. Strong persistence.")"""))

# ─── Live Demo 2: vol-timed strategy ──────────────────────────────────
cells.append(md("""---

## 🔄 Live Demo 2: Building the Vol-Timed Strategy <a id="demo2"></a>

### 🔴 Loose prompt

> *"Scale market exposure inversely to realized variance."*

**What AI is likely to produce:**

```python
w = 1 / rv
strat = w * mkt_excess
```

**The bugs:**
- ❌ No **lag** on `rv` — uses time-$t$ realized variance to decide time-$t$ position. Look-ahead.
- ❌ Raw weight $1/RV$ has no average target. May average to 50%, may average to 500%.
- ❌ No clipping for the extreme low-vol months (`1/RV` can blow up).
- ❌ Mixes monthly and daily data without aligning.

### 🟢 Precise prompt

> *"Align market monthly excess returns with realized variance. Lag RV by one
> period so weight at time $t$ uses information available at $t-1$. Compute
> raw weight = $1 / RV_{t-1}$. Rescale so the average weight equals 1 (then
> the strategy is "same risk on average" as buy-and-hold). Clip the weight at
> 3 to avoid blow-ups. Compute strategy returns and report Sharpe vs.
> buy-and-hold."*"""))

cells.append(code("""# Align monthly market excess returns with realized variance
mkt_m   = get_factors(freq='monthly')['Mkt-RF']
both    = pd.concat([mkt_m.rename('ret'), rv], axis=1).dropna()
both['rv_lag'] = both['RV'].shift(1)
both    = both.dropna()

# Raw weight = 1 / RV(t-1); scale so mean weight = 1; clip at 3
raw_w   = 1.0 / both['rv_lag']
c       = 1.0 / raw_w.mean()
both['w'] = (c * raw_w).clip(upper=3.0)
both['strat'] = both['w'] * both['ret']

# Sharpe comparison
sr_bh = (both['ret'].mean()   / both['ret'].std())   * np.sqrt(12)
sr_vt = (both['strat'].mean() / both['strat'].std()) * np.sqrt(12)

# Cumulative wealth
fig, ax = plt.subplots(figsize=(12, 5))
(1 + both['ret']).cumprod().plot(ax=ax, label=f'Buy & hold (SR={sr_bh:.2f})', linewidth=2)
(1 + both['strat']).cumprod().plot(ax=ax, label=f'Vol-timed (SR={sr_vt:.2f})', linewidth=2)
ax.set_yscale('log'); ax.set_ylabel('Growth of $1 (log)')
ax.set_title('Vol-timed market vs buy-and-hold', fontweight='bold')
ax.legend(); plt.tight_layout(); plt.show()

print(f"\\nBuy-and-hold Sharpe:  {sr_bh:.2f}")
print(f"Vol-timed   Sharpe:   {sr_vt:.2f}")
print(f"Improvement:          {(sr_vt/sr_bh - 1)*100:.1f}%")"""))

cells.append(md("""> **💡 Key Insight**
>
> Vol-timing typically delivers a **10-30% Sharpe improvement** over buy-and-hold —
> and it does it without any forecasting of *expected returns*. You're just
> responding to risk. The empirical fact that $b \\approx 0$ (premia don't scale
> with variance) makes this work.
>
> Compare to the mean-timing strategy from Part I, which depended on a noisy
> forecast of expected returns. Vol timing is the **easier, more reliable**
> version of timing."""))

# ─── HANDS-ON 2: VIX ──────────────────────────────────────────────────
cells.append(md("""---

## 🛠️ Hands-On 2: VIX² as a Forward-Looking Variance Forecast <a id="ho2"></a>

So far we used **realized variance** (RV) — the variance computed from *past*
daily returns. There's a competing forecast available off-the-shelf: the **VIX**.

**VIX** is the market's option-implied 30-day expected vol of the S&P 500. It's
computed from option prices and updated continuously. Key properties:

- It's **forward-looking** (options price expected future vol, not past vol)
- It typically **spikes BEFORE** RV does (options price stress before it happens)
- It carries a **variance risk premium** — VIX² tends to exceed subsequent realized
  variance by 1-3 percentage points (vol-squared), which is itself tradable
- It's only available from **1990 onward**

**Your job:** fetch VIX from FRED, square it to get implied variance, build
the same vol-timing strategy using VIX² instead of RV, compare."""))

cells.append(md("""### Step 1 — Fetch VIX from FRED"""))

cells.append(code("""# VIX from FRED (series ID: VIXCLS) — daily close, in PERCENT
vix_daily = DataReader('VIXCLS', 'fred', start='1990-01-01').dropna()
vix_daily.columns = ['vix']
# Convert to decimal (annualized vol) and take month-end
vix_monthly = vix_daily.resample('ME').last() / 100
print(f"VIX range: {vix_monthly.index.min().date()} to {vix_monthly.index.max().date()}")
print(f"Months: {len(vix_monthly)}")

# Plot — compare to realized vol from Part II
fig, ax = plt.subplots(figsize=(12, 4))
vix_monthly.plot(ax=ax, label='VIX (option-implied vol)', linewidth=1.5)
np.sqrt(rv * 12).plot(ax=ax, label='Realized vol (annualized)', linewidth=1.5, alpha=0.7)
ax.set_ylabel('Annualized volatility')
ax.set_title('VIX vs realized vol — note VIX spikes ahead of realized', fontweight='bold')
ax.legend(); plt.tight_layout(); plt.show()"""))

cells.append(md("""### Step 2 — Convert VIX to monthly variance forecast

VIX is in *annualized* vol units. To compare with our monthly RV:

- VIX² = annualized implied variance
- VIX² / 12 = monthly implied variance"""))

cells.append(code("""# Monthly implied variance
vix_monthly['ivar_monthly'] = vix_monthly['vix']**2 / 12

# Compare to RV — should be highly correlated
both_vol = pd.concat([rv.rename('RV'), vix_monthly['ivar_monthly']], axis=1).dropna()
corr = both_vol['RV'].corr(both_vol['ivar_monthly'])
print(f"Corr(RV, VIX²/12): {corr:.3f}")

# And: VIX² > RV on average? (variance risk premium)
print(f"\\nMean monthly RV:        {both_vol['RV'].mean():.5f}")
print(f"Mean monthly VIX²/12:   {both_vol['ivar_monthly'].mean():.5f}")
print(f"Difference (VRP, monthly): {(both_vol['ivar_monthly'] - both_vol['RV']).mean():.5f}")
print(f"→ VIX² systematically overpredicts realized variance — that's the variance risk premium.")"""))

cells.append(md("""### Step 3 — Build VIX-based timing strategy

Same template as Part II, but use **VIX²_{t-1}** instead of **RV_{t-1}** as the
inverse-weight signal. Lag by one period (VIX is observed end-of-month; we
trade at the start of the next month)."""))

cells.append(code("""# Align market monthly excess returns with VIX
both_vix = pd.concat([mkt_m.rename('ret'), vix_monthly[['ivar_monthly']]], axis=1).dropna()
both_vix['ivar_lag'] = both_vix['ivar_monthly'].shift(1)
both_vix = both_vix.dropna()

raw_w_vix = 1.0 / both_vix['ivar_lag']
c_vix     = 1.0 / raw_w_vix.mean()
both_vix['w']     = (c_vix * raw_w_vix).clip(upper=3.0)
both_vix['strat'] = both_vix['w'] * both_vix['ret']

# Sharpe comparison
sr_bh_v   = (both_vix['ret'].mean()   / both_vix['ret'].std())   * np.sqrt(12)
sr_vix    = (both_vix['strat'].mean() / both_vix['strat'].std()) * np.sqrt(12)

# Also recompute RV-based Sharpe on the SAME (post-1990) sample for apples-to-apples
both_aligned = both.loc[both_vix.index.min():]    # restrict to VIX-available period
sr_rv_aligned = (both_aligned['strat'].mean()/both_aligned['strat'].std()) * np.sqrt(12)

print(f"=== Same sample (post-1990) ===")
print(f"Buy-and-hold:          {sr_bh_v:.2f}")
print(f"Vol-timing with RV:    {sr_rv_aligned:.2f}")
print(f"Vol-timing with VIX²:  {sr_vix:.2f}")"""))

cells.append(code("""# Cumulative wealth comparison
fig, ax = plt.subplots(figsize=(12, 5))
(1 + both_vix['ret']).cumprod().plot(ax=ax, label=f'Buy & hold (SR={sr_bh_v:.2f})', linewidth=2)
(1 + both_aligned['strat']).cumprod().plot(ax=ax,
    label=f'Vol-timed (RV-based, SR={sr_rv_aligned:.2f})', linewidth=2)
(1 + both_vix['strat']).cumprod().plot(ax=ax,
    label=f'Vol-timed (VIX²-based, SR={sr_vix:.2f})', linewidth=2)
ax.set_yscale('log'); ax.set_ylabel('Growth of $1 (log)')
ax.set_title('Vol timing: RV vs VIX² (post-1990)', fontweight='bold')
ax.legend(); plt.tight_layout(); plt.show()"""))

cells.append(md("""> **🤔 Compare RV vs VIX²**
>
> The two strategies are *very similar* in structure but use different vol
> forecasts:
>
> | Metric | RV (realized) | VIX² (implied) |
> |--------|---------------|----------------|
> | **Information used** | Past month's daily returns | Today's option prices |
> | **Type** | Backward-looking | Forward-looking |
> | **Coverage** | Available whenever you have daily data (~1926+) | Only 1990+ |
> | **Bias** | Slight underestimate during crises | Carries variance risk premium |
> | **Spikes** | After the event | Before the event |
> | **Reliability** | Smooth, persistent | More volatile, occasional jumps |
>
> Either typically gives a 10-20% Sharpe boost. The relative performance depends
> on the sample and the type of crisis. **You don't need to pick one — most
> practitioners use both, combined via averaging or shrinkage.**"""))

# ─── Challenge ────────────────────────────────────────────────────────
cells.append(md("""---

## 🎯 Challenge: Comparing Four Timing Approaches <a id="challenge"></a>

> **Setup.** Across the lecture you've now built four different timing strategies:
> 1. **D/P-based mean timing** (Part I demo, post-1991 OOS)
> 2. **Your-chosen-FRED-predictor mean timing** (Hands-On 1)
> 3. **RV-based vol timing** (Part II demo, full sample)
> 4. **VIX²-based vol timing** (Hands-On 2, post-1990)
>
> Plus a **buy-and-hold** baseline.
>
> Collect the Sharpe ratios for each and write a memo comparing them.

### Q1 — Buy-and-hold Sharpe (post-1991)

> **📌 Required:**
> ```python
> sharpe_buyhold = ____   # use the post-1991 sample from test_with_rf
> ```"""))

cells.append(code("""# Your work here


sharpe_buyhold = ____
print(f"Buy-and-hold Sharpe (post-1991): {sharpe_buyhold:.2f}")"""))

cells.append(md("""### Q2 — D/P-based mean-timing Sharpe (post-1991 OOS)

> **📌 Required:**
> ```python
> sharpe_mean_timing_dp = ____
> ```"""))

cells.append(code("""# Your work here


sharpe_mean_timing_dp = ____
print(f"Mean-timing Sharpe (D/P, post-1991 OOS): {sharpe_mean_timing_dp:.2f}")"""))

cells.append(md("""### Q3 — Your-predictor mean-timing Sharpe (OOS)

From the `sig_test_full` DataFrame you built in Hands-On 1 (using YOUR chosen
FRED predictor).

> **📌 Required:**
> ```python
> my_predictor_id              = "____"   # the FRED ID you picked (e.g., "T10Y3M")
> sharpe_mean_timing_predictor = ____     # the OOS Sharpe for your predictor's strategy
> ```"""))

cells.append(code("""# Your work here


my_predictor_id              = "____"
sharpe_mean_timing_predictor = ____
print(f"My predictor: {my_predictor_id}")
print(f"Mean-timing Sharpe ({my_predictor_id}, OOS): {sharpe_mean_timing_predictor:.2f}")"""))

cells.append(md("""### Q4 — RV-based vol-timing Sharpe (full sample)

From the `both` DataFrame in Part II.

> **📌 Required:**
> ```python
> sharpe_vol_timing_rv = ____
> ```"""))

cells.append(code("""# Your work here


sharpe_vol_timing_rv = ____
print(f"Vol-timing Sharpe (RV, full sample): {sharpe_vol_timing_rv:.2f}")"""))

cells.append(md("""### Q5 — VIX²-based vol-timing Sharpe (post-1990)

From the `both_vix` DataFrame in Hands-On 2.

> **📌 Required:**
> ```python
> sharpe_vol_timing_vix = ____
> ```"""))

cells.append(code("""# Your work here


sharpe_vol_timing_vix = ____
print(f"Vol-timing Sharpe (VIX², post-1990): {sharpe_vol_timing_vix:.2f}")"""))

cells.append(md("""### Q6 — The Memo

Write a memo (max 6 sentences) addressed to your CIO. Cover:

1. **Which timing approach delivered the largest Sharpe improvement?**
2. **Mean timing vs vol timing** — why does one work better than the other in
   practice? (Hint: think about which is easier to forecast — $\\mu_t$ or
   $\\sigma_t^2$ — and why.)
3. **Within mean timing**: D/P vs your-chosen-predictor — are they capturing
   different information? What's the case for using both?
4. **Within vol timing**: RV (backward-looking) vs VIX² (forward-looking) —
   what are the practical pros and cons of each?
5. **Your recommendation** — if you could deploy ONE timing overlay on your
   fund's market exposure, which would you pick and why?"""))

cells.append(code("""MEMO = \"\"\"
Write your 5-sentence-max memo here.
\"\"\"
print(MEMO)"""))

# ─── Submission ───────────────────────────────────────────────────────
cells.append(md("""---

## 📤 Submission <a id="submit"></a>

Run the cell below. Copy the line that starts with `UG54::` into the submission
form: **https://forms.gle/YOUR_FORM_LINK_HERE**"""))

cells.append(code("""# === 📤 SUBMISSION CELL — Run this last ===
import json, base64, hashlib, datetime as dt

required = [
    "sharpe_buyhold",
    "sharpe_mean_timing_dp",
    "sharpe_mean_timing_predictor",   # YOUR chosen FRED predictor
    "sharpe_vol_timing_rv",
    "sharpe_vol_timing_vix",
    "MEMO",
]
# my_predictor_id is a string — bundle separately so it survives JSON serialization
missing = [v for v in required if v not in dir()]
if missing: raise NameError(f"\\n❌ Missing: {missing}")

payload = {
    "assignment": "Timing_AI",
    "ts": dt.datetime.utcnow().isoformat(timespec="seconds") + "Z",
    "answers": {k: float(eval(k)) for k in required if k != "MEMO"},
    "memo": MEMO.strip(),
    "my_predictor_id": str(my_predictor_id),
}
blob = json.dumps(payload, sort_keys=True)
checksum = hashlib.sha256(blob.encode()).hexdigest()[:8]
token = f"UG54::{checksum}::{base64.b64encode(blob.encode()).decode()}"
print("="*72); print(token); print("="*72)"""))

# ─── Takeaways ────────────────────────────────────────────────────────
cells.append(md("""---

## 🧠 Key Takeaways <a id="takeaways"></a>

1. **Two flavors of timing:** mean timing (forecast $\\mu$) and vol timing (forecast $\\sigma^2$). They are different problems and have different track records.

2. **Mean timing is hard.** Even the famous D/P regression has OOS R² near zero. The Sharpe improvement is small and unreliable.

3. **Vol timing is easier and works.** $\\sigma^2$ is highly persistent (AR(1) R² ≈ 50-70%); you don't need to forecast $\\mu$.

4. **The math is the same MVE formula.** $x_t = \\mu_t/(\\gamma \\sigma_t^2)$ — but which input you let vary determines which strategy you're running.

5. **Always HAC for multi-period forecasts.** Overlapping windows inflate t-stats by 2-3x. Use Newey-West with `maxlags ≥ horizon`.

6. **Always lag your signal.** `.shift(1)` is the line between honest backtest and look-ahead bias.

7. **AI writes the regression. You catch the lookahead, choose the HAC lags, and decide whether the strategy is deployable after costs.**"""))

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
