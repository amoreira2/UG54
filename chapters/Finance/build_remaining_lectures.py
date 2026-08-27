"""
Build remaining UG54 AI lecture notebooks in one pass:
  L14 Cross-Sectional Strategies II
  L15 Momentum
  L16 Performance Evaluation
  L17 Capital Allocation II
  L18 Multi-Factor Models
  L19 Risk Management (variance estimation + factor risk limits)
  L20 Implementation (trading costs, leverage, shorting) — NEW
  L21 Machine Learning I
  L22 Machine Learning II
  L23 LLMs in Finance

Each follows the standard pattern: title + LOs, TOC, setup, pitfall checklist,
1-2 live AI moments, challenge with variable stubs + memo, submission, takeaways.

Run from chapters/Finance directory.
"""

import json
from pathlib import Path

HERE = Path(__file__).parent


def md(t): return {"cell_type":"markdown","metadata":{},"source":t.splitlines(keepends=True)}
def code(t): return {"cell_type":"code","execution_count":None,"metadata":{},"outputs":[],"source":t.splitlines(keepends=True)}


def write_nb(filename, cells):
    nb = {"cells": cells, "metadata": {
        "colab":{"provenance":[],"toc_visible":True},
        "kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},
        "language_info":{"name":"python"}}, "nbformat": 4, "nbformat_minor": 5}
    (HERE / filename).write_text(json.dumps(nb, indent=1))
    print(f"✅ {filename} ({len(cells)} cells)")


def submission_cell(assignment, required_vars):
    """Generate a standard submission cell for any assignment."""
    req_str = ", ".join(f'"{v}"' for v in required_vars)
    return code(f"""# === 📤 SUBMISSION CELL ===
import json, base64, hashlib, datetime as dt
required = [{req_str}, "MEMO"]
missing = [v for v in required if v not in dir()]
if missing: raise NameError(f"\\n❌ Missing: {{missing}}")
payload = {{"assignment": "{assignment}",
    "ts": dt.datetime.utcnow().isoformat(timespec="seconds") + "Z",
    "answers": {{k: float(eval(k)) for k in required if k != "MEMO"}},
    "memo": MEMO.strip()}}
blob = json.dumps(payload, sort_keys=True)
token = f"UG54::{{hashlib.sha256(blob.encode()).hexdigest()[:8]}}::{{base64.b64encode(blob.encode()).decode()}}"
print("="*72); print(token); print("="*72)""")


def setup_cell():
    return code("""#@title Setup
import numpy as np, pandas as pd, matplotlib.pyplot as plt
import statsmodels.api as sm
%matplotlib inline
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize']=[10,5]; plt.rcParams['font.size']=11
import warnings; warnings.filterwarnings('ignore')
print("✅ Loaded")""")


# ═══════════════════════════════════════════════════════════════════════
# L14 — Cross-Sectional Strategies II (implementation depth)
# ═══════════════════════════════════════════════════════════════════════
c = []
c.append(md("""# Cross-Sectional Strategies II — Implementation
## 🎯 Learning Objectives

By the end of this notebook, you will be able to:

1. **Combine multiple characteristics** into a composite signal
2. **Recognize when long-short premia are robust vs. fragile**
3. **Estimate transaction-cost impact** on a high-turnover strategy
4. **Recognize crowding effects** when many funds chase the same characteristic
5. **Audit AI-generated cross-sectional code** — z-score winsorization, signal aggregation, turnover"""))

c.append(md("""## 📋 TOC
1. [Setup](#setup)  2. [Combining Signals](#combine)
3. [Pitfall Checklist](#pitfalls)  4. [Turnover and Costs](#costs)
5. [Crowding](#crowding)  6. [🎯 Challenge: Robust Multi-Signal Strategy](#challenge)
7. [Submission](#submit)  8. [Key Takeaways](#takeaways)"""))

c.append(md("---\n## 🛠️ Setup <a id=\"setup\"></a>"))
c.append(setup_cell())

c.append(md("""---
## Combining Signals <a id="combine"></a>

A single characteristic is rarely the whole story. Real strategies combine
multiple signals — often via simple averaging of z-scores:

$$\\text{composite}_{i,t} = \\frac{1}{K} \\sum_{k=1}^K z(X^{(k)}_{i,t})$$

where $z()$ standardizes each characteristic to have mean 0 and standard
deviation 1 IN THE CROSS-SECTION at time $t$.

Why z-score before averaging? Because raw characteristics have different
units (B/M is a ratio, momentum is a return). Z-scoring puts them on
equal footing.

Why simple averaging? Because **complex weighting schemes are mostly
fitting noise**. The simple average often beats fancier alternatives
out-of-sample."""))

c.append(md("""---
## 🛡️ Pitfall Checklist <a id="pitfalls"></a>

| | Pitfall | What goes wrong | 🔍 How to detect |
|---|---------|-----------------|-------------------|
| 1 | **Z-scoring with the full sample** | Time-$t$ standardization uses time-$t+5$ data | Always z-score within each cross-section, not globally |
| 2 | **Outliers in characteristics** | Single extreme firms can dominate the strategy | Winsorize at 1st/99th percentile before z-scoring |
| 3 | **Missing data treated as zero** | NaN z-score = average | Drop firms with missing characteristics, don't impute zero |
| 4 | **Ignoring transaction costs** | High-turnover strategies look great pre-cost | Always report Sharpe NET of estimated costs |
| 5 | **Equal weighting tiny firms** | Microcap firms dominate equal-weight portfolios | Filter to firms above a minimum market cap (e.g., NYSE 20th percentile) |"""))

c.append(md("""---
## Turnover and Costs <a id="costs"></a>

**Turnover** = how much of the portfolio changes from one rebalance to the next.

$$\\text{Turnover}_t = \\frac{1}{2} \\sum_i |w_{i,t} - w_{i,t-1}|$$

A typical value strategy has 30-60% annual turnover. A momentum strategy
has 100-200%.

**Cost** ≈ turnover × spread, where typical liquid-stock spreads are
5-10 bps. A 100% turnover momentum strategy with 10bp costs loses 100 bps/year — meaningful relative to a 4-6% premium."""))

c.append(code("""# Quick illustration: turnover for two strategies
turnover_value     = 0.40   # 40% per year
turnover_momentum  = 1.50   # 150% per year
spread_bps         = 10     # 10 basis points round-trip

cost_value = turnover_value * spread_bps / 100  # in percent
cost_momentum = turnover_momentum * spread_bps / 100

print(f"Value strategy annual cost:    {cost_value:.2f}%")
print(f"Momentum strategy annual cost: {cost_momentum:.2f}%")
print("\\nMomentum costs ~3.75x more than value because of turnover.")"""))

c.append(md("""---
## Crowding <a id="crowding"></a>

When many funds chase the same characteristic, the premium shrinks. The
mechanism:
1. Funds enter, push up prices of "value" stocks and push down "growth"
2. The expected mean reversion ($r^{LS}$) shrinks
3. In extreme crowding, the trade reverses temporarily (a "factor crash")

**Quant momentum crashed in August 2007.** Value had a multi-year drought
2010-2019. Both are classic crowding patterns.

> **💡 Why this is hard**
>
> You can rarely observe crowding directly. By the time it shows up in
> performance, you've already taken the loss. The defenses are diversifying
> across many signals, sizing each modestly, and accepting that no signal
> is permanent."""))

c.append(md("""---
## 🎯 Challenge: Robust Multi-Signal Strategy <a id="challenge"></a>

> **Setup.** Suppose three characteristics each predict returns with
> independent Sharpe ratios of 0.4 (modest). Test what happens when you
> combine them.

### Q1 — Combined Sharpe (Pythagoras)

If the three signals are uncorrelated, what's the combined Sharpe?

> **📌 Required:**
> ```python
> sharpe_individual    = 0.4
> n_signals            = 3
> sharpe_combined      = ____   # sqrt(N) * sharpe (when uncorrelated)
> ```"""))
c.append(code("""sharpe_individual = 0.4
n_signals = 3

sharpe_combined = ____
print(f"Combined Sharpe (uncorrelated): {sharpe_combined:.2f}")"""))

c.append(md("""### Q2 — Effect of correlation
If signals are 50% correlated instead of uncorrelated, the combined Sharpe
formula changes:

$$SR_{\\text{combined}}^2 = \\frac{1}{N} \\cdot \\sum SR_i^2 + \\frac{2}{N(N-1)} \\sum_{i<j} \\rho_{ij} SR_i SR_j$$

Wait — that's wrong. The right formula for an equal-weighted combination is
that the variance of the average signal scales with $(1 + (N-1)\\rho)/N$.
For three signals each with Sharpe 0.4 and pairwise correlation 0.5:

$$SR_{\\text{combined}} = SR_i \\cdot \\sqrt{\\frac{N}{1 + (N-1)\\rho}}$$

> **📌 Required:**
> ```python
> correlation_assumed = 0.5
> sharpe_combined_correlated = ____   # use the formula above
> ```"""))
c.append(code("""correlation_assumed = 0.5
N = n_signals

sharpe_combined_correlated = ____
print(f"Combined Sharpe (50% correlation): {sharpe_combined_correlated:.2f}")
print(f"Loss from correlation: {(1 - sharpe_combined_correlated/sharpe_combined)*100:.1f}%")"""))

c.append(md("""### Q3 — Net Sharpe after costs
Your combined strategy has 80% turnover with 10bp costs. Annual cost = 0.8%. If the
gross combined return is 6%/year on a vol of 8%, what's the net Sharpe?

> **📌 Required:**
> ```python
> gross_return = 0.06
> annual_cost  = 0.008
> portfolio_vol = 0.08
> sharpe_net   = ____
> ```"""))
c.append(code("""gross_return = 0.06
annual_cost  = 0.008
portfolio_vol = 0.08

sharpe_net = ____
print(f"Gross Sharpe: {gross_return/portfolio_vol:.2f}")
print(f"Net Sharpe:   {sharpe_net:.2f}")"""))

c.append(md("""### Q4 — Memo
Max 5 sentences. Recommend to your CIO whether to deploy a 3-signal cross-sectional
strategy. Cite (i) the combined Sharpe gain, (ii) the correlation cost, (iii) the cost-after-trading."""))
c.append(code("""MEMO = \"\"\"Write your memo here.\"\"\"
print(MEMO)"""))

c.append(md("---\n## 📤 Submission <a id=\"submit\"></a>"))
c.append(submission_cell("CrossSectional_II_AI",
    ["sharpe_combined", "sharpe_combined_correlated", "sharpe_net"]))

c.append(md("""---
## 🧠 Key Takeaways <a id="takeaways"></a>
1. **Combine signals via z-score averaging.** Simple > clever for OOS.
2. **Correlation kills the Pythagoras gain.** Diversification benefits shrink fast as $\\rho$ rises.
3. **Always report Sharpe net of costs.** Pre-cost numbers are marketing.
4. **Crowding is real but invisible until it bites.** Size each signal modestly.
5. **AI will hand you a backtest. You have to subtract costs, check correlation, and confirm OOS.**"""))

write_nb("CrossSectional_II_AI.ipynb", c)


# ═══════════════════════════════════════════════════════════════════════
# L15 — Momentum
# ═══════════════════════════════════════════════════════════════════════
c = []
c.append(md("""# Momentum
## 🎯 Learning Objectives

By the end of this notebook, you will be able to:

1. **Construct a momentum signal** — the standard (12, 1) past return
2. **Build a long-short momentum portfolio** following the recipe from L13
3. **Diagnose momentum crashes** — the most important risk in the strategy
4. **Apply volatility scaling to momentum** to mitigate crash risk
5. **Audit AI-generated momentum code** — the 1-month skip, holding period, rebalancing"""))

c.append(md("""## 📋 TOC
1. [Setup](#setup)  2. [The Momentum Signal](#signal)
3. [Pitfall Checklist](#pitfalls)  4. [Live Demo: Building Momentum](#demo)
5. [Momentum Crashes](#crashes)  6. [Risk-Managed Momentum](#riskmgmt)
7. [🎯 Challenge: Crash Magnitudes](#challenge)
8. [Submission](#submit)  9. [Key Takeaways](#takeaways)"""))

c.append(md("---\n## 🛠️ Setup <a id=\"setup\"></a>"))
c.append(setup_cell())

c.append(md("""---
## The Momentum Signal <a id="signal"></a>

The **standard momentum signal**, dating to Jegadeesh & Titman (1993):

$$\\text{MOM}_{i,t} = \\text{cumulative return of stock } i \\text{ from month } t-12 \\text{ to month } t-2$$

Two key features:
- **12-month lookback** — captures medium-term trend
- **Skip the most recent month** — that one tends to *reverse* (short-term reversal)

Then form quintile portfolios on MOM each month and go long top minus bottom."""))

c.append(md("""---
## 🛡️ Pitfall Checklist <a id="pitfalls"></a>

| | Pitfall | What goes wrong | 🔍 How to detect |
|---|---------|-----------------|-------------------|
| 1 | **Forgetting the 1-month skip** | Including month $t-1$ flips the sign because of short-term reversal | Standard MOM = `cum_ret[t-12:t-2]`, not `[t-12:t-1]` |
| 2 | **Not lagging the signal vs return** | Computing portfolios on $t$ data, holding them at $t$ | Form portfolios at end of $t$, earn return in $t+1$ |
| 3 | **Holding period mismatch** | Signal computed monthly but portfolio held longer | Most academic momentum is monthly rebalanced |
| 4 | **Ignoring transaction costs** | Momentum has 150-200% turnover/year | Real-world momentum has slim margins after costs |
| 5 | **Backtest bias** | Looking only at recent decades misses 1932, 2009 crashes | Always include 1929 + 2008 if your data goes back that far |"""))

c.append(md("""---
## 🔄 Live Demo: Building Momentum <a id="demo"></a>

> **🤖 AI prompt:**
>
> *"Given a panel of monthly stock returns (long format: columns permno, date, ret),
> compute the (12, 1) momentum signal: for each (permno, date), the cumulative
> log-return from date-12 to date-2 months ago. Use shift(2) and rolling(11).sum()
> on log returns. Lag the signal by one month before sorting."*"""))

c.append(code("""# Simulated mini-panel demo (3 fake stocks over 60 months)
np.random.seed(42)
T, N = 60, 3
dates = pd.date_range('2020-01-31', periods=T, freq='ME')
data = []
for permno in [10001, 10002, 10003]:
    rets = np.random.normal(0.01, 0.06, T)
    for d, r in zip(dates, rets):
        data.append({'permno': permno, 'date': d, 'ret': r})
panel = pd.DataFrame(data).sort_values(['permno', 'date'])

# Log returns
panel['logret'] = np.log1p(panel['ret'])

# 12-1 momentum: cumulative log-return from t-12 to t-2 (so 11 months, skipping t-1)
def mom_signal(g):
    g = g.sort_values('date').copy()
    # shift(2) makes the window end at t-2; rolling(11).sum() captures 11 months
    g['mom'] = g['logret'].shift(2).rolling(11).sum()
    return g

panel = panel.groupby('permno', group_keys=False).apply(mom_signal)
print(panel.tail(10))"""))

c.append(md("""---
## Momentum Crashes <a id="crashes"></a>

Momentum has the most extreme drawdowns of any "anomaly":
- **November 2008**: -25% in a single month
- **March-April 2009**: ~-50% over 6 weeks
- **April 2020**: another sharp negative month

**Why?** Momentum buys winners and shorts losers. After a market crash,
the "losers" (deep cyclicals) rebound massively as investors pile back in.
Momentum is short these — and gets crushed.

Crashes are predictable in one sense: they happen after long market
drawdowns. Volatility is high. Correlations are high.

> **💡 The fundamental tradeoff**
>
> Momentum has a great long-run Sharpe (~0.5-1.0). But the drawdowns are
> brutal enough that many investors can't stomach it. **Real-world deploy
> requires risk management.**"""))

c.append(md("""---
## Risk-Managed Momentum <a id="riskmgmt"></a>

The simplest fix: **scale momentum exposure inversely to realized vol**:

$$w^{MOM}_t = c \\cdot \\frac{1}{\\hat{\\sigma}^{MOM}_{t-1}^2}$$

This is the same vol-timing logic from Lecture 8 — but applied to the
momentum factor instead of the market.

Barroso & Santa-Clara (2015) showed this single tweak cuts the maximum
drawdown roughly in half while keeping most of the Sharpe."""))

c.append(md("""---
## 🎯 Challenge: Crash Magnitudes <a id="challenge"></a>

The historical momentum factor (UMD from Ken French's data) has the following stylized facts in our sample:

- Mean annual return: ~7%
- Annual vol: ~15%
- Sharpe: ~0.47
- Worst month: ~-30%
- Skewness: -1.5 (heavily left-tailed)

### Q1 — Vol-scaled Sharpe improvement

Barroso-Santa-Clara found that vol-scaling raises momentum's Sharpe from
~0.47 to ~0.62 while cutting the worst month from -30% to ~-15%.

> **📌 Required:**
> ```python
> raw_sharpe          = 0.47
> raw_worst_month     = -0.30
> vol_scaled_sharpe   = ____   # Barroso-Santa-Clara number
> vol_scaled_worst    = ____
> ```"""))
c.append(code("""raw_sharpe       = 0.47
raw_worst_month  = -0.30

vol_scaled_sharpe = ____
vol_scaled_worst  = ____
print(f"Sharpe improvement: {raw_sharpe:.2f} → {vol_scaled_sharpe:.2f}")
print(f"Worst month:        {raw_worst_month:.2%} → {vol_scaled_worst:.2%}")"""))

c.append(md("""### Q2 — Premium per unit of crash risk

Crash risk = absolute value of the worst month. Compute the ratio of
annual mean to crash risk for both versions.

> **📌 Required:**
> ```python
> raw_return       = 0.07
> raw_crash_ratio  = ____   # raw_return / |raw_worst_month|
> scaled_crash_ratio = ____  # 0.07 * (vol_scaled_sharpe / raw_sharpe) / |vol_scaled_worst|
> ```"""))
c.append(code("""raw_return = 0.07

raw_crash_ratio    = ____
scaled_crash_ratio = ____
print(f"Raw return per unit crash:    {raw_crash_ratio:.2f}")
print(f"Scaled return per unit crash: {scaled_crash_ratio:.2f}")"""))

c.append(md("""### Q3 — Memo

Max 5 sentences. Recommend whether your fund should run momentum, and if so,
whether raw or vol-scaled. Cite (i) Sharpe, (ii) crash risk, (iii) what kind
of investor each version is appropriate for."""))
c.append(code("""MEMO = \"\"\"Write your memo here.\"\"\"
print(MEMO)"""))

c.append(md("---\n## 📤 Submission <a id=\"submit\"></a>"))
c.append(submission_cell("Momentum_AI",
    ["vol_scaled_sharpe", "vol_scaled_worst", "raw_crash_ratio", "scaled_crash_ratio"]))

c.append(md("""---
## 🧠 Key Takeaways <a id="takeaways"></a>
1. **Standard MOM = (12, 1) past return.** Skip the most recent month.
2. **Momentum's worst flaw is its crash risk.** -25% to -50% drawdowns in market reversals.
3. **Vol-scaling roughly halves crash risk** while keeping most of the Sharpe.
4. **Always lag the signal.** The recipe is: form portfolios at end of $t$, earn return in $t+1$.
5. **AI handles the rolling-window code. You catch the skip-month bug and the lookahead.**"""))

write_nb("Momentum_AI.ipynb", c)


# ═══════════════════════════════════════════════════════════════════════
# L16 — Performance Evaluation
# ═══════════════════════════════════════════════════════════════════════
c = []
c.append(md("""# Performance Evaluation
## 🎯 Learning Objectives

By the end of this notebook, you will be able to:

1. **Run alpha attribution against CAPM, FF3, and FF5**
2. **Tell when "alpha" is just exposure to a known factor**
3. **Detect overfitting** in claimed alphas by comparing in-sample to OOS
4. **Apply the Sharpe-ratio standard error formula** to know what's distinguishable from noise
5. **Audit AI-generated alpha claims** — multi-factor benchmarks, sample period choice, multiple testing"""))

c.append(md("""## 📋 TOC
1. [Setup](#setup)  2. [The Alpha-Attribution Workflow](#workflow)
3. [Pitfall Checklist](#pitfalls)  4. [Case: Cathie Wood / ARKK](#arkk)
5. [Case: Buffett / Berkshire](#brk)  6. [Sharpe SE and "Is this real?"](#se)
7. [🎯 Challenge: Grading a Fund](#challenge)
8. [Submission](#submit)  9. [Key Takeaways](#takeaways)"""))

c.append(md("---\n## 🛠️ Setup <a id=\"setup\"></a>"))
c.append(setup_cell())

c.append(md("""---
## The Alpha-Attribution Workflow <a id="workflow"></a>

You have a fund's return series. You want to answer: *does it have alpha?*

The standard test:

$$r_t^{\\text{fund}} = \\alpha + \\beta_1 \\cdot MKT_t + \\beta_2 \\cdot SMB_t + \\beta_3 \\cdot HML_t + \\beta_4 \\cdot RMW_t + \\beta_5 \\cdot CMA_t + \\beta_6 \\cdot MOM_t + \\epsilon_t$$

- **CAPM** (1 factor): MKT only
- **FF3** (3 factors): MKT, SMB, HML
- **FF5** (5 factors): adds RMW (profitability), CMA (investment)
- **FF6** (6 factors): adds MOM

**The alpha you find shrinks as you add factors.** A fund that has α=8% against
CAPM might have α=2% against FF6. That difference is *factor exposure being
re-classified* as "not alpha."

> **💡 Key principle**
>
> You should benchmark a strategy against factors **it could be plausibly
> exposed to**. Don't benchmark a stock-picker against the bond market;
> don't benchmark a quant equity strategy against the S&P 500 if it has
> small-cap exposure."""))

c.append(md("""---
## 🛡️ Pitfall Checklist <a id="pitfalls"></a>

| | Pitfall | What goes wrong | 🔍 How to detect |
|---|---------|-----------------|-------------------|
| 1 | **Single-factor benchmark** | Find "alpha" that's actually size or value loading | Always run FF3 or FF6 in parallel |
| 2 | **Sample-period cherry-picking** | A fund's alpha was 10% in 2010-2015, -3% in 2016-2020 | Always report stability across sub-samples |
| 3 | **Survivorship in the fund universe** | Studying surviving funds inflates the average alpha by 1-2% | Use vintage data or include discontinued funds |
| 4 | **Multiple testing** | Out of 500 funds, ~25 will show alpha with p<0.05 by chance | Apply Bonferroni or use the Harvey-Liu adjustments |
| 5 | **Reading R² wrong** | High R² doesn't mean no alpha — it means the factors capture most variance | Look at α and its t-stat, not just R² |
| 6 | **t-stat = significance ≠ economic** | t=3 on a 0.1%/yr alpha is meaningless economically | Always look at magnitude alongside t-stat |"""))

c.append(md("""---
## Case: Cathie Wood / ARKK <a id="arkk"></a>

ARKK had a wild ride: dominated 2020 (+150% return), then collapsed 2021-2022.
Alpha attribution typically shows:
- Huge positive **MKT** loading (it's leveraged tech)
- Huge positive **SMB** loading (small-cap tilt)
- Negative **HML** loading (anti-value, pro-growth)
- Negative **CMA** loading (high-investment / capex stocks)

After controlling for these, alpha against FF5 is approximately **zero or
negative** depending on the sample window. The "outperformance" was almost
entirely factor exposure."""))

c.append(md("""---
## Case: Buffett / Berkshire <a id="brk"></a>

Frazzini, Kabiller, and Pedersen (2018) decomposed Berkshire's returns:
- Positive **MKT** loading (~0.9)
- Strong **HML** loading (value-tilted)
- Strong **RMW** loading (high-profitability tilt)
- Modest **BAB** loading (Betting-Against-Beta: prefers low-beta stocks)

After controlling for these factors, Berkshire's alpha is **positive but
much smaller** than the raw return suggests. The bulk of Berkshire's
outperformance is **factor exposure that Buffett identified before
academics named the factors.**"""))

c.append(md("""---
## Sharpe SE and "Is this real?" <a id="se"></a>

Given a sample of $T$ observations with realized Sharpe $\\widehat{SR}$, the
standard error (approximate, large-sample) is:

$$\\text{SE}(\\widehat{SR}) \\approx \\sqrt{\\frac{1 + \\widehat{SR}^2 / 2}{T}}$$

So with 10 years of monthly data (T=120) and SR=1.0:

$$\\text{SE} \\approx \\sqrt{1.5 / 120} \\approx 0.11$$

A 1.0 Sharpe estimated over 10 years has SE ≈ 0.11 — so the 95% CI is
roughly [0.78, 1.22]. Plenty of room to be wrong about the magnitude."""))

c.append(code("""# Sharpe SE calculator
def sharpe_se(sharpe, T):
    return np.sqrt((1 + sharpe**2 / 2) / T)

for sharpe, years, freq in [(1.0, 10, 12), (0.5, 10, 12), (2.0, 5, 252), (0.3, 30, 12)]:
    T = years * freq
    se = sharpe_se(sharpe, T)
    print(f"Sharpe={sharpe}, T={T} ({years}y of {freq}/yr): SE = {se:.3f}, 95% CI = [{sharpe-1.96*se:.2f}, {sharpe+1.96*se:.2f}]")"""))

# Challenge
c.append(md("""---
## 🎯 Challenge: Grading a Fund <a id="challenge"></a>

> **Setup.** A fund manager pitches you their track record:
> - 5 years of monthly returns
> - Mean return: 18% / year
> - Volatility: 22% / year
> - CAPM alpha: 4.2%/yr (t-stat 1.8)
> - FF3 alpha: 1.1%/yr (t-stat 0.5)

### Q1 — Sharpe and its standard error

Assume a risk-free rate of 4%/year.

> **📌 Required:**
> ```python
> fund_sharpe        = ____   # (mean - rf) / vol
> fund_sharpe_se     = ____   # use the formula above with T = 60 months
> ```"""))
c.append(code("""mean_ret = 0.18
vol      = 0.22
rf       = 0.04
T = 5 * 12

fund_sharpe = ____
fund_sharpe_se = ____
print(f"Sharpe: {fund_sharpe:.2f} ± {fund_sharpe_se:.2f}")"""))

c.append(md("""### Q2 — Alpha shrinkage

Compute the difference between CAPM and FF3 alpha (in percentage points). This is the amount of "alpha" that was actually small/value loading.

> **📌 Required:**
> ```python
> capm_alpha  = 0.042
> ff3_alpha   = 0.011
> alpha_shrinkage = ____   # capm - ff3
> ```"""))
c.append(code("""capm_alpha = 0.042
ff3_alpha  = 0.011

alpha_shrinkage = ____
print(f"Alpha shrinkage from CAPM → FF3: {alpha_shrinkage:.2%}")"""))

c.append(md("""### Q3 — Statistical reality check

The CAPM alpha has t-stat 1.8 (close to "significant"). The FF3 alpha has t-stat 0.5 (essentially zero).

> **📌 Required:**
> ```python
> capm_alpha_significant = ____   # True/False — is |t| > 2?
> ff3_alpha_significant  = ____   # True/False
> ```

(Coerce True to 1.0 and False to 0.0 in the variable assignments so the
submission cell can encode them as floats.)"""))
c.append(code("""capm_t = 1.8
ff3_t  = 0.5

capm_alpha_significant = ____    # 1.0 if |capm_t| > 2 else 0.0
ff3_alpha_significant  = ____
print(f"CAPM alpha 'significant'? {bool(capm_alpha_significant)}")
print(f"FF3 alpha 'significant'?  {bool(ff3_alpha_significant)}")"""))

c.append(md("""### Q4 — Memo

Max 5 sentences. Recommend whether your fund should invest. Cite (i) Sharpe with uncertainty, (ii) where the alpha goes when you control for FF3, (iii) the appropriate benchmark for THIS fund."""))
c.append(code("""MEMO = \"\"\"Write your memo here.\"\"\"
print(MEMO)"""))

c.append(md("---\n## 📤 Submission <a id=\"submit\"></a>"))
c.append(submission_cell("PerformanceEval_AI",
    ["fund_sharpe", "fund_sharpe_se", "alpha_shrinkage",
     "capm_alpha_significant", "ff3_alpha_significant"]))

c.append(md("""---
## 🧠 Key Takeaways <a id="takeaways"></a>
1. **Alpha shrinks as you add factors.** Always benchmark against multi-factor models.
2. **Sharpe estimates have wide CIs.** A 1.0 Sharpe over 10 years has a CI of ~[0.78, 1.22].
3. **Single-factor benchmarks are inadequate** for any active fund with size/value tilts.
4. **Multiple testing is a real concern.** Out of 500 funds, ~25 will show "significant" alpha by chance.
5. **AI runs the regression. You decide what factors to include and how to interpret what's left.**"""))

write_nb("PerformanceEval_AI.ipynb", c)


# ═══════════════════════════════════════════════════════════════════════
# L17 — Capital Allocation II (under uncertainty)
# ═══════════════════════════════════════════════════════════════════════
c = []
c.append(md("""# Capital Allocation II — Under Uncertainty
## 🎯 Learning Objectives

By the end of this notebook, you will be able to:

1. **Quantify the sensitivity** of mean-variance weights to estimation error in $\\mu$ and $\\Sigma$
2. **Apply shrinkage** to expected returns and covariance matrices
3. **Apply Black-Litterman intuition** — mix views with a prior
4. **Apply a robust sizing rule** (the fractional Kelly criterion) under parameter uncertainty
5. **Audit AI-generated optimization outputs** for over-fitting"""))

c.append(md("""## 📋 TOC
1. [Setup](#setup)  2. [The Estimation-Error Problem](#problem)
3. [Pitfall Checklist](#pitfalls)  4. [Shrinkage Estimators](#shrinkage)
5. [Fractional Kelly](#kelly)  6. [🎯 Challenge: Robust Sizing](#challenge)
7. [Submission](#submit)  8. [Key Takeaways](#takeaways)"""))

c.append(md("---\n## 🛠️ Setup <a id=\"setup\"></a>"))
c.append(setup_cell())

c.append(md("""---
## The Estimation-Error Problem <a id="problem"></a>

In Capital Allocation I we derived $w^* = (1/\\gamma) \\Sigma^{-1} \\mu$.

In Factor Models II we showed that $\\mu$ has wide confidence intervals — even
10 years of data gives a Sharpe SE of ~0.1.

**Mean-variance optimization treats $\\hat{\\mu}$ as the truth.** The
optimal weights swing dramatically with small changes in the input. Real
deployments must use estimators that account for this uncertainty."""))

c.append(md("""---
## 🛡️ Pitfall Checklist <a id="pitfalls"></a>

| | Pitfall | What goes wrong | 🔍 How to detect |
|---|---------|-----------------|-------------------|
| 1 | **Plug-in optimization** | Using $\\hat{\\mu}$ as if it were $\\mu$ produces wildly leveraged weights | Sanity check: do weights exceed +/-2? Then optimization is unreliable |
| 2 | **Inverting a near-singular covariance matrix** | $\\Sigma$ with N assets has $N(N+1)/2$ parameters from $T$ observations; needs $T \\gg N^2$ for stable inverse | Compute condition number of $\\Sigma$; if > 100, inversion is unstable |
| 3 | **No shrinkage** | Sample $\\Sigma$ is noisy; shrinkage toward a structured target (identity or factor-based) is almost always better | Compare in-sample vs OOS MVE Sharpe — gap > 2x indicates overfitting |
| 4 | **Ignoring transaction costs in the optimization** | Optimal weights demand 100% turnover; real strategies need penalty | Add a cost penalty proportional to $|\\Delta w|$ |"""))

c.append(md("""---
## Shrinkage Estimators <a id="shrinkage"></a>

**Mean shrinkage** (James-Stein style): pull $\\hat{\\mu}$ toward a prior $\\mu_0$:

$$\\tilde{\\mu} = (1-w) \\hat{\\mu} + w \\mu_0$$

Common choice for $\\mu_0$: the **grand mean** (average across all assets) or
**zero**. Weight $w$ chosen to minimize MSE.

**Covariance shrinkage** (Ledoit-Wolf): pull $\\hat{\\Sigma}$ toward a structured
target (identity scaled to average variance, or factor-implied covariance):

$$\\tilde{\\Sigma} = (1-\\alpha) \\hat{\\Sigma} + \\alpha F$$

where $F$ is the target. Optimal $\\alpha$ has a closed form (Ledoit-Wolf).

> **💡 Why this helps**
>
> The sample mean and covariance are unbiased but high-variance. Shrinkage
> trades a small bias for a large variance reduction. The resulting
> portfolio weights are dramatically more stable, and OOS performance is
> almost always better."""))

c.append(md("""---
## Fractional Kelly <a id="kelly"></a>

The **Kelly criterion** says bet your wealth such that expected log-wealth
is maximized. For a single asset:

$$f^* = \\frac{\\mu}{\\sigma^2}$$

(This is the same as Merton's optimal weight with $\\gamma = 1$.)

**Full Kelly is too aggressive.** Even small estimation error in $\\mu$ can
lead to bankruptcy. Real practitioners use **fractional Kelly** — typically
1/2 Kelly or 1/4 Kelly:

$$f^* = \\frac{1}{2} \\cdot \\frac{\\hat{\\mu}}{\\hat{\\sigma}^2}$$

Why halve? Because if your $\\hat{\\mu}$ is biased upward by 50% (very
possible with small samples), full Kelly produces a 4x larger position than
optimal. Fractional Kelly is the **standard robust-sizing rule of thumb**."""))

c.append(code("""# Demonstrate: sensitivity of weight to noise in mu
np.random.seed(0)
true_mu = 0.05    # true expected excess return per period
true_sig = 0.15
T = 60   # 5 years monthly
gamma = 3

n_sims = 1000
weights_full = []
weights_half = []
for _ in range(n_sims):
    sample = np.random.normal(true_mu / 12, true_sig / np.sqrt(12), T)   # monthly
    mu_hat = sample.mean() * 12
    sig_hat = sample.std() * np.sqrt(12)
    w_full = mu_hat / (gamma * sig_hat**2)
    w_half = 0.5 * w_full
    weights_full.append(w_full)
    weights_half.append(w_half)

print(f"True optimal w = {true_mu / (gamma * true_sig**2):.2f}")
print(f"Full Kelly estimated weights: mean={np.mean(weights_full):.2f}, std={np.std(weights_full):.2f}")
print(f"Half Kelly estimated weights: mean={np.mean(weights_half):.2f}, std={np.std(weights_half):.2f}")
print(f"\\n→ Half Kelly cuts variance by 4x, at the cost of bias toward zero.")"""))

c.append(md("""---
## 🎯 Challenge: Robust Sizing <a id="challenge"></a>

> **Setup.** You ran a 3-year backtest of your strategy. It produced an
> annualized Sharpe of 1.2. You want to deploy. How much capital?

### Q1 — Naive plug-in size

Apply the plug-in formula $w = \\hat{\\mu}/(\\gamma \\hat{\\sigma}^2)$ with $\\gamma = 3$,
$\\hat{\\mu} = 0.12$/yr, $\\hat{\\sigma} = 0.10$/yr.

> **📌 Required:**
> ```python
> mu_hat       = 0.12
> sigma_hat    = 0.10
> gamma        = 3
> w_plugin     = ____
> ```"""))
c.append(code("""mu_hat    = 0.12
sigma_hat = 0.10
gamma     = 3

w_plugin = ____
print(f"Plug-in weight: {w_plugin:.2f}")"""))

c.append(md("""### Q2 — Estimate uncertainty

The Sharpe SE on a 3-year sample (T=36 months) with Sharpe=1.2 is:

$$SE = \\sqrt{(1 + 1.2^2/2) / 36}$$

> **📌 Required:**
> ```python
> sharpe_se = ____   # apply the formula
> ```"""))
c.append(code("""T = 3 * 12
realized_sharpe = 1.2

sharpe_se = ____
print(f"Sharpe SE: {sharpe_se:.2f}")
print(f"95% CI on Sharpe: [{realized_sharpe - 1.96*sharpe_se:.2f}, {realized_sharpe + 1.96*sharpe_se:.2f}]")"""))

c.append(md("""### Q3 — Half-Kelly size

Apply half-Kelly: multiply your plug-in by 0.5.

> **📌 Required:**
> ```python
> w_half_kelly = ____
> ```"""))
c.append(code("""w_half_kelly = ____
print(f"Half-Kelly weight: {w_half_kelly:.2f}")
print(f"vs Plug-in:        {w_plugin:.2f}")"""))

c.append(md("""### Q4 — Memo

Max 5 sentences. Recommend a sizing for the new strategy. Cite (i) the plug-in
weight, (ii) the half-Kelly alternative, (iii) the Sharpe uncertainty that
justifies the haircut."""))
c.append(code("""MEMO = \"\"\"Write your memo here.\"\"\"
print(MEMO)"""))

c.append(md("---\n## 📤 Submission <a id=\"submit\"></a>"))
c.append(submission_cell("CapitalAllocationII_AI",
    ["w_plugin", "sharpe_se", "w_half_kelly"]))

c.append(md("""---
## 🧠 Key Takeaways <a id="takeaways"></a>
1. **Mean-variance is fragile.** Optimal weights are very sensitive to $\\hat{\\mu}$.
2. **Shrinkage helps.** Both for means and covariances. Closed-form formulas exist.
3. **Half-Kelly is the practical sizing rule.** Bias toward zero is cheap; bankruptcy is not.
4. **Backtest Sharpe overstates expected OOS Sharpe.** Discount accordingly.
5. **AI will hand you the "optimal" weights. You decide how much to trust them.**"""))

write_nb("CapitalAllocationII_AI.ipynb", c)


# ═══════════════════════════════════════════════════════════════════════
# L18 — Multi-Factor Models
# ═══════════════════════════════════════════════════════════════════════
c = []
c.append(md("""# Multi-Factor Models
## 🎯 Learning Objectives

By the end of this notebook, you will be able to:

1. **Estimate factor loadings** of a portfolio against FF3, FF5, FF6
2. **Interpret factor loadings** — what does β=0.5 on SMB mean?
3. **Apply the "factor zoo" warning** — most published factors don't replicate
4. **Choose the right factor model** for the question you're asking
5. **Audit AI-generated multi-factor analyses** — sample windows, factor data versions"""))

c.append(md("""## 📋 TOC
1. [Setup](#setup)  2. [From One Factor to Many](#many)
3. [Pitfall Checklist](#pitfalls)  4. [The Standard Models](#standard)
5. [The Factor Zoo](#zoo)  6. [Choosing the Right Model](#choose)
7. [🎯 Challenge: Decompose a Fund](#challenge)
8. [Submission](#submit)  9. [Key Takeaways](#takeaways)"""))

c.append(md("---\n## 🛠️ Setup <a id=\"setup\"></a>"))
c.append(setup_cell())

c.append(md("""---
## From One Factor to Many <a id="many"></a>

Single-factor CAPM:

$$r_t^e = \\alpha + \\beta \\cdot MKT_t + \\epsilon_t$$

Multi-factor:

$$r_t^e = \\alpha + \\sum_{k=1}^K \\beta_k \\cdot F_{k,t} + \\epsilon_t$$

**Why add factors?** Because empirically, the market alone leaves systematic
patterns in returns. Small stocks earn more than large. Value stocks earn
more than growth. Recent winners earn more than recent losers. Multi-factor
models capture these patterns explicitly."""))

c.append(md("""---
## 🛡️ Pitfall Checklist <a id="pitfalls"></a>

| | Pitfall | What goes wrong | 🔍 How to detect |
|---|---------|-----------------|-------------------|
| 1 | **Wrong factor data version** | Ken French updates factors periodically; old data has slightly different SMB | Pull factors fresh from the source |
| 2 | **Daily vs monthly inconsistency** | Mixing daily fund returns with monthly factors | Use the same frequency throughout |
| 3 | **Time-zone / day-end mismatches** | Some factors use 4pm ET close; some use closing auction | Compute corr between MKT and SPY excess; should be ~0.99 |
| 4 | **Sample period changes everything** | A fund's HML loading may be +0.3 in one decade and -0.3 in another | Report rolling loadings, not just point estimates |
| 5 | **Confusing factor "tilt" with skill** | A fund with high HML loading earned the value premium, not alpha | If alpha disappears when you add HML, the "skill" was just exposure |"""))

c.append(md("""---
## The Standard Models <a id="standard"></a>

| Model | Factors | What they capture |
|-------|---------|-------------------|
| **CAPM** | MKT | Market exposure |
| **FF3** | MKT, SMB, HML | + Size, value |
| **FF5** | + RMW, CMA | + Profitability, investment |
| **FF6** | + MOM | + Momentum |
| **Q-Factor** | MKT, ME, I/A, ROE | Hou-Xue-Zhang alternative |
| **AQR 7-factor** | MKT, SMB, HML, MOM, BAB, QMJ, ... | Adds proprietary factors |

For **academic work**, FF6 is the default. For **practitioner work**, AQR's
or BlackRock's proprietary multi-factor models are common. The right model
depends on what's commercially available and what you're trying to explain."""))

c.append(md("""---
## The Factor Zoo <a id="zoo"></a>

Harvey, Liu & Zhu (2016) document **316+ "factors"** published in academic
journals. Their estimate: **most won't replicate.**

The reasons:
- **Multiple testing.** If you try 1000 random characteristics, ~50 will be
  "significant" by chance with no economic content.
- **Publication bias.** Negative results don't get published.
- **Data mining.** Researchers try variants until something works.

**Hou, Xue & Zhang (2020)** replicated 452 factors with stricter methodology;
~65% failed to clear the t-stat threshold.

> **🤖 AI-Era Insight**
>
> An LLM can readily list dozens of factor models. It can't tell you which
> ones have survived honest replication. **Be skeptical of any "new factor."**"""))

c.append(md("""---
## Choosing the Right Model <a id="choose"></a>

| If you're trying to ... | Use ... |
|-------------------------|---------|
| Evaluate a long-only equity fund | FF5 or FF6 |
| Evaluate a market-neutral hedge fund | FF6 + BAB; consider AQR 7-factor |
| Risk-manage a portfolio | Whatever covariance model is operational |
| Test a new "anomaly" | Both FF5 and HXZ q-factor to be defensive |
| Allocate across asset classes | Different model entirely (macro factors) |"""))

# Challenge
c.append(md("""---
## 🎯 Challenge: Decompose a Fund <a id="challenge"></a>

> **Setup.** A fund has the following loadings from a 10-year FF5 regression:
> - α = 1.5%/yr (t = 1.2)
> - β_MKT = 1.10 (t = 22)
> - β_SMB = 0.30 (t = 5.5)
> - β_HML = -0.20 (t = -3.2)
> - β_RMW = 0.15 (t = 2.8)
> - β_CMA = -0.10 (t = -1.6)
>
> Average factor premia over the same sample (annualized): MKT=8%, SMB=2%,
> HML=3%, RMW=4%, CMA=2%.

### Q1 — Decompose expected return into factor contributions

Each factor's contribution = β × factor premium.

> **📌 Required:**
> ```python
> contrib_MKT   = ____   # 1.10 * 0.08
> contrib_SMB   = ____
> contrib_HML   = ____
> contrib_RMW   = ____
> contrib_CMA   = ____
> ```"""))
c.append(code("""b_mkt, b_smb, b_hml, b_rmw, b_cma = 1.10, 0.30, -0.20, 0.15, -0.10
p_mkt, p_smb, p_hml, p_rmw, p_cma = 0.08, 0.02, 0.03, 0.04, 0.02

contrib_MKT = ____
contrib_SMB = ____
contrib_HML = ____
contrib_RMW = ____
contrib_CMA = ____

total_factor_return = (contrib_MKT + contrib_SMB + contrib_HML + contrib_RMW + contrib_CMA)
print(f"MKT contribution:  {contrib_MKT:+.2%}")
print(f"SMB contribution:  {contrib_SMB:+.2%}")
print(f"HML contribution:  {contrib_HML:+.2%}")
print(f"RMW contribution:  {contrib_RMW:+.2%}")
print(f"CMA contribution:  {contrib_CMA:+.2%}")
print(f"Total from factors: {total_factor_return:+.2%}")"""))

c.append(md("""### Q2 — Is the alpha real?

The alpha is 1.5%/yr with t-stat 1.2. Is that statistically distinguishable from zero?

> **📌 Required:**
> ```python
> alpha_is_significant = ____   # 1.0 if |t| > 2, 0.0 otherwise
> ```"""))
c.append(code("""alpha_t = 1.2

alpha_is_significant = ____
print(f"Alpha statistically significant? {bool(alpha_is_significant)}")"""))

c.append(md("""### Q3 — Total return decomposition

If the fund's total annual return was 12%, how much of it came from factor exposure vs alpha?

> **📌 Required:**
> ```python
> fraction_from_factors = ____   # total_factor_return / 0.12
> ```"""))
c.append(code("""total_return = 0.12

fraction_from_factors = ____
print(f"Fraction from factors: {fraction_from_factors:.1%}")"""))

c.append(md("""### Q4 — Memo

Max 5 sentences. Recommend whether to invest. Cite (i) which factor exposures
drive returns, (ii) whether alpha is significant, (iii) what the fund manager
should be paid for vs what's commodity beta."""))
c.append(code("""MEMO = \"\"\"Write your memo here.\"\"\"
print(MEMO)"""))

c.append(md("---\n## 📤 Submission <a id=\"submit\"></a>"))
c.append(submission_cell("MultiFactorModels_AI",
    ["contrib_MKT", "contrib_SMB", "contrib_HML", "contrib_RMW", "contrib_CMA",
     "alpha_is_significant", "fraction_from_factors"]))

c.append(md("""---
## 🧠 Key Takeaways <a id="takeaways"></a>
1. **FF6 is the academic default.** Adds size, value, profitability, investment, momentum to CAPM.
2. **Alpha shrinks as you add factors.** Most "alpha" is re-classified factor exposure.
3. **The factor zoo is mostly noise.** Be skeptical of new factors that haven't been independently replicated.
4. **Decomposition reveals what the manager actually does.** Often it's commodity factor exposure, not skill.
5. **AI runs the regression. You pick the right factors and interpret what's left.**"""))

write_nb("MultiFactorModels_AI.ipynb", c)


print("\n--- First batch (L14-L18) complete ---")
