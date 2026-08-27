"""
Build FactorModels_c_AI.ipynb from scratch.

Mirrors the structure of IntrotoReturns_c_AI.ipynb:
  - Specify -> Implement -> Validate workflow
  - Pitfall checklist students can audit AI output against
  - Live AI moments with pre-written prompts
  - A real-data challenge instead of toy exercises

Run from anywhere; writes to chapters/Finance/FactorModels_c_AI.ipynb.
"""

import json
from pathlib import Path

OUT = Path(__file__).parent / "FactorModels_c_AI.ipynb"


def md(text, cell_id=None):
    cell = {
        "cell_type": "markdown",
        "metadata": {},
        "source": text.splitlines(keepends=True),
    }
    if cell_id:
        cell["id"] = cell_id
    return cell


def code(text, cell_id=None):
    cell = {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": text.splitlines(keepends=True),
    }
    if cell_id:
        cell["id"] = cell_id
    return cell


cells = []

# ─── 0. Title + Learning Objectives ───────────────────────────────────
cells.append(md("""# Factor Models
## 🎯 Learning Objectives

By the end of this notebook, you will be able to:

1. **Decompose any return into α + β·f + ε** — and explain what each piece means in dollars
2. **Run and audit a factor regression** — with AI generating the code and you catching the bugs
3. **Build tracking and hedged portfolios** — to isolate "portable alpha" from market exposure
4. **Size positions under a volatility budget** — and see why hedging lets you deploy more capital
5. **Distinguish Sharpe from Appraisal ratio** — and use the right one to identify real skill
6. **Audit AI-generated factor model code** — with a checklist of pitfalls specific to regression"""))

# ─── 1. TOC ───────────────────────────────────────────────────────────
cells.append(md("""## 📋 Table of Contents

1. [Setup](#setup)
2. [The Big Idea: Co-movement and Decomposition](#bigidea)
3. [Pitfall Checklist for Factor Models](#pitfalls)
4. [Live Demo: Specify → Implement → Validate](#demo)
5. [Risk Model vs Expected Return Model](#twomodels)
6. [Alpha and Beta: How Wall Street Works](#wallstreet)
7. [Tracking and Hedged Portfolios](#hedging)
8. [Risk Budgets and Position Sizing](#risk-budget)
9. [Sharpe vs Appraisal Ratio](#sharpe)
10. [Variance Decomposition](#variance)
11. [🎯 Challenge: Two Funds, One Decision](#challenge)
12. [Key Takeaways](#takeaways)"""))

# ─── 2. Setup ─────────────────────────────────────────────────────────
cells.append(md("---\n\n## 🛠️ Setup <a id=\"setup\"></a>"))

cells.append(code("""#@title 🛠️ Setup: Run this cell first (click to expand)
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
import statsmodels.formula.api as smf
%matplotlib inline

plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = [10, 6]
plt.rcParams['font.size'] = 12

import warnings
warnings.filterwarnings('ignore')

print("✅ Libraries loaded successfully!")"""))

cells.append(code("""#@title Helper: Download Fama-French factor data (click to expand)
import datetime
from pandas_datareader.data import DataReader

def get_factors(factors='CAPM', freq='daily'):
    \"\"\"Download Fama-French factor data as decimals.\"\"\"
    freq_label = '' if freq == 'monthly' else '_' + freq
    ff = DataReader(f"F-F_Research_Data_Factors{freq_label}", "famafrench", start="1921-01-01")
    df_factor = ff[0][['RF', 'Mkt-RF']]
    if freq == 'monthly':
        df_factor.index = pd.to_datetime(df_factor.index.to_timestamp()) + pd.offsets.MonthEnd(0)
    else:
        df_factor.index = pd.to_datetime(df_factor.index)
    return df_factor / 100"""))

# ─── 3. The Big Idea ──────────────────────────────────────────────────
cells.append(md("""---

## The Big Idea: Co-movement and Decomposition <a id="bigidea"></a>

Stocks don't move independently — they ride the market together. But the
**degree of co-movement varies**:

- **Defensive stocks** (utilities, groceries) → less sensitive to market swings
- **Cyclical stocks** (luxury, banks) → more sensitive to market swings
- **High-leverage stocks** → particularly vulnerable in downturns

Look at it before we model it."""))

cells.append(code("""# Load excess returns for SPY, WMT, JPM
url = 'https://raw.githubusercontent.com/amoreira2/UG54/refs/heads/main/assets/data/FactorModels_data1.csv'
data = pd.read_csv(url, parse_dates=['date'], index_col='date').dropna()

print(f"Range: {data.index.min().date()} to {data.index.max().date()}")
print(f"Stocks: {list(data.columns)}")
data.tail(3)"""))

cells.append(code("""# Scatter plots: which stock moves MORE with the market?
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
for ax, ticker in zip(axes, ['WMT', 'JPM']):
    ax.scatter(data['SPY'], data[ticker], alpha=0.3, s=10)
    ax.axhline(0, color='gray', lw=0.5); ax.axvline(0, color='gray', lw=0.5)
    ax.set_xlabel('SPY excess return'); ax.set_ylabel(f'{ticker} excess return')
    ax.set_title(f'{ticker} vs SPY', fontweight='bold')
plt.tight_layout(); plt.show()"""))

cells.append(md("""> **🤔 Look first, math later**
>
> Before running any regression: which stock has the steeper cloud — WMT or JPM?
> That stock has the higher beta. *You can usually eyeball beta within ±0.3 just from the scatter.*"""))

cells.append(md("""### The Decomposition

We decompose any asset's excess return as:

$$r^e = \\alpha + \\beta \\cdot f + \\epsilon$$

| Symbol | Meaning |
|--------|---------|
| $r^e$ | Asset's excess return over the risk-free rate |
| $\\alpha$ | Intercept — "skill" or mispricing per unit time |
| $\\beta$ | Sensitivity to the factor |
| $f$ | Factor excess return (e.g., the market) |
| $\\epsilon$ | Idiosyncratic noise (asset-specific) |

> **💡 Key Insight**
>
> This decomposition is *always valid* — it's just statistics. The power is in **how you interpret each piece**:
> - $\\beta \\cdot f$ is the return you'd get by tracking the asset with the factor
> - $\\alpha + \\epsilon$ is what's left over after you strip the factor out"""))

# ─── 4. Pitfall checklist ─────────────────────────────────────────────
cells.append(md("""---

## 🛡️ Pitfall Checklist for Factor Models <a id="pitfalls"></a>

When an AI generates factor model code, it will often produce something that *runs without errors* but contains **silent bugs that break the economic interpretation**. This is your checklist:

| | Pitfall | What goes wrong | 🔍 How to detect |
|---|---------|-----------------|-------------------|
| 1 | **Total returns instead of excess** | Beta is fine, but alpha is contaminated by RF | Alpha looks suspiciously close to the risk-free rate |
| 2 | **No intercept added** | `sm.OLS(y, X)` without `add_constant` forces alpha = 0 | Beta is biased; R² may look wrong; no `const` row in summary |
| 3 | **Mixed frequencies** | Daily returns regressed on monthly factor | Beta is meaningless; R² collapses |
| 4 | **Unit mismatch** | RF or factors in percent when returns are decimals | Alpha is ~100× too big or too small |
| 5 | **Look-ahead in rolling betas** | Using future data in the window | Out-of-sample performance collapses |
| 6 | **Confusing R² with alpha** | "High R²" ≠ "good investment" | Re-read: R² is about *risk*, alpha is about *return* |
| 7 | **Confusing Sharpe with Appraisal** | Using total vol when you should use idio vol | Wrong position sizing for a hedged strategy |
| 8 | **Misreading the regression direction** | Regressing factor on asset instead of asset on factor | Beta is inverted; sanity check against the scatter |

> **🤖 AI-Era Insight**
>
> The AI will happily run `smf.ols('JPM ~ SPY', data=data).fit()` and tell you "beta is 1.4". Your job is to ask: *are these excess returns? Did it add a constant? Are SPY and JPM at the same frequency?* Print out this table and use it every time."""))

# ─── 5. Live Demo: Specify → Implement → Validate ─────────────────────
cells.append(md("""---

## 🔄 Live Demo: Specify → Implement → Validate <a id="demo"></a>

Rather than writing the regression from scratch, we'll practice the workflow you'll actually use on the job:

| Step | What you do | Why it matters |
|------|------------|----------------|
| **1. Specify** | Write a precise English description | Closes the door on silent assumptions |
| **2. Implement** | Let AI generate the code | Syntax is cheap |
| **3. Validate** | Use the pitfall checklist | Where the bugs hide |"""))

cells.append(md("""### Step 1: The Specification

> **📝 Spec**
>
> Using the DataFrame `data` (columns SPY, WMT, JPM — all **daily excess returns** over the risk-free rate, 1969-2024), run an OLS regression of WMT on SPY with an intercept. Report alpha (daily AND annualized × 252), beta, R², and the t-stat on alpha.

Is this specification complete? What still feels fuzzy?
- ✅ Data source and columns — specified
- ✅ Frequency and what kind of returns — specified
- ✅ Intercept required — specified
- ✅ What to report and units — specified
- ⚠️ Standard errors: OLS or HAC? — not addressed (defaults to OLS; OK for now)"""))

cells.append(md("""### Step 2: Implementation

> **🤖 AI prompt** *(copy-paste into Gemini in Colab):*
>
> *"Using the DataFrame `data` with columns SPY, WMT, JPM (daily excess returns), regress WMT on SPY using statsmodels with an intercept. Print alpha (daily and annualized), beta, R-squared, and the t-stat on alpha."*"""))

cells.append(code("""# What competent AI-generated code looks like:
X = sm.add_constant(data['SPY'])
y = data['WMT']
model_wmt = sm.OLS(y, X).fit()

alpha_d = model_wmt.params['const']
beta    = model_wmt.params['SPY']
t_alpha = model_wmt.tvalues['const']
r2      = model_wmt.rsquared

print(f"Alpha (daily):       {alpha_d:.6f}")
print(f"Alpha (annualized):  {alpha_d * 252:.4%}")
print(f"Beta:                {beta:.3f}")
print(f"R²:                  {r2:.3f}")
print(f"t-stat on alpha:     {t_alpha:.2f}")"""))

cells.append(md("""### Step 3: Validate ✅

Run through the checklist:

- ✅ **Excess returns?** Yes — `data` was loaded with that label. Confirm with `data.mean() * 252` (should be in ~5-10% range, not ~10-15%).
- ✅ **Intercept added?** Yes — `sm.add_constant`. Without it, alpha would be forced to zero.
- ✅ **Same frequency?** Yes — both daily.
- ✅ **Beta reasonable?** WMT is a defensive grocery retailer; β = 0.67 < 1 ✓ matches the scatter.
- ⚠️ **Is alpha statistically significant?** t-stat tells you. |t| < 2 → can't reject α = 0.
- ⚠️ **Is alpha economically significant?** Annualized α ≈ 5% is huge if real, modest if noisy."""))

cells.append(code("""# Sanity check: annualized mean of excess returns
data.mean() * 252"""))

# ─── 6. Risk Model vs Expected Return Model ───────────────────────────
cells.append(md("""---

## Risk Model vs Expected Return Model <a id="twomodels"></a>

Factor models serve two distinct purposes — and a model can be great for one and terrible for the other.

### 👉 Risk Model
- **Goal:** Explain *realized return variation*
- **Key metric:** R² (how much variance is explained?)
- **Use case:** Covariance estimation, risk management, hedging
- **A win looks like:** High R²

### 👉 Expected Return Model
- **Goal:** Explain *expected return differences across assets*
- **Key metric:** Alpha (is it close to zero?)
- **Use case:** Performance evaluation, asset pricing tests
- **A win looks like:** No significant alphas anywhere

> **💡 Key Insight**
>
> The CAPM has R² ≈ 0.4-0.7 for individual stocks (decent risk model) but explains essentially nothing about which stocks earn higher returns over the long run (failed expected return model). Knowing which question you're asking determines which metric matters."""))

# ─── 7. Alpha and Beta: How Wall Street Works ─────────────────────────
cells.append(md("""---

## Alpha and Beta: How Wall Street Works <a id="wallstreet"></a>

The α/β decomposition isn't just academic — it's the organizing principle of the industry:

- **Big bonuses** only come from perceived $\\alpha$ (skill)
- **Beta exposure** is close to a commodity — for the market it literally is one (SPY costs 3 bps)
- **Pod shops** require traders to be factor-neutral on dozens of factors at once:
  - [Citadel](https://www.wsj.com/finance/investing/citadel-ken-griffin-hedge-funds-c9ddf51d)
  - [Millennium](https://www.wsj.com/finance/investing-the-giant-hedge-fund-that-hates-risk-and-still-wins-1110e90a)
  - [Balyasny](https://www.bamfunds.com/)

Taking expectations of the factor model:

$$E[r] = r_f + \\alpha + \\beta \\cdot E[f]$$

| Piece | Interpretation | Who deserves credit |
|-------|----------------|---------------------|
| $r_f$ | Time value of money | The Fed |
| $\\beta \\cdot E[f]$ | Premium from factor exposure | The market |
| $\\alpha$ | Abnormal return | **You** (if real) |

> **⚠️ Caution**
>
> Significant α means one of two things: (1) you found skill or mispricing, OR (2) your factor model is missing something. **Always assume #2 first.**"""))

# ─── 8. Hedged Portfolios with second AI moment ───────────────────────
cells.append(md("""---

## Tracking and Hedged Portfolios <a id="hedging"></a>

We'll switch to MSFT to illustrate the hedging mechanics."""))

cells.append(code("""# Load MSFT and align with Fama-French market factor
url_msft = 'https://raw.githubusercontent.com/amoreira2/UG54/refs/heads/main/assets/data/FactorModels_data2.csv'
df_returns = pd.read_csv(url_msft, parse_dates=['date'], index_col='date')
df_factor = get_factors()
df_returns, df_factor = df_returns.dropna().align(df_factor.dropna(), join='inner', axis=0)

# Compute MSFT excess return
df_eret = df_returns['MSFT'] - df_factor['RF']

# Regress
X = sm.add_constant(df_factor['Mkt-RF'])
model = sm.OLS(df_eret, X).fit()
alpha = model.params['const']
beta  = model.params['Mkt-RF']
print(f"MSFT: α (daily) = {alpha:.6f}  |  α (ann) = {alpha*252:.2%}  |  β = {beta:.3f}  |  R² = {model.rsquared:.3f}")"""))

cells.append(md("""### Tracking vs Hedged Portfolios

The **tracking portfolio** replicates the factor-driven component:
$$\\text{Tracking}_t = \\beta \\cdot f_t$$

The **hedged portfolio** strips the factor out:
$$r^{\\text{hedged}}_t = r^e_t - \\beta \\cdot f_t = \\alpha + \\epsilon_t$$

Properties of the hedged portfolio:
- Mean return = α (pure skill)
- Volatility = $\\sigma_\\epsilon$ (idiosyncratic only — this is "tracking error")
- Beta = 0 by construction

### 🔄 Specify → Implement → Validate (Round 2)

> **📝 Spec**
>
> Using the MSFT excess return series `df_eret` and the market factor `df_factor['Mkt-RF']`, build the tracking and hedged portfolios. Verify:
> (i) the hedged portfolio has zero correlation with the market (within rounding), and
> (ii) the hedged portfolio's mean equals α from the regression.

> **🤖 AI prompt:**
>
> *"Given `df_eret` (MSFT excess returns), `df_factor['Mkt-RF']` (market factor), and the regression beta (1.19), construct (a) a tracking portfolio = beta × market, (b) a hedged portfolio = MSFT excess − tracking. Plot all three series' cumulative returns on one chart. Confirm correlation of hedged with market is ≈ 0."*"""))

cells.append(code("""# Implementation
MKT      = df_factor['Mkt-RF']
Tracking = beta * MKT
Hedged   = df_eret - Tracking

# Validate (i): correlation of hedged with market should be ~0
print(f"Corr(Hedged, MKT) = {Hedged.corr(MKT):.2e}    ← should be near 0")

# Validate (ii): mean of hedged should equal alpha
print(f"Mean(Hedged) (daily)  = {Hedged.mean():.6f}")
print(f"Alpha from regression = {alpha:.6f}")
print(f"Match: {np.isclose(Hedged.mean(), alpha)}")"""))

cells.append(code("""# Cumulative returns: MSFT vs tracking vs hedged
fig, ax = plt.subplots(figsize=(12, 6))
(1 + df_eret).cumprod().plot(ax=ax, label='MSFT excess', linewidth=2)
(1 + Tracking).cumprod().plot(ax=ax, label=f'Tracking (β·MKT)', linewidth=2)
(1 + Hedged).cumprod().plot(ax=ax, label='Hedged (α + ε)', linewidth=2)
ax.set_yscale('log')
ax.set_ylabel('Growth of \\$1 (log scale)')
ax.set_title('MSFT decomposed into tracking + hedged', fontweight='bold')
ax.legend(); plt.tight_layout(); plt.show()"""))

cells.append(md("""> **💡 Key Insight**
>
> Look at the hedged line. It still trends up — that's the cumulative α. But the *volatility* of the line is dramatically lower than MSFT itself. Lower vol means you can deploy more capital for the same risk budget — which is the logic behind factor-neutral hedge fund strategies."""))

# ─── 9. Risk Budgets and Position Sizing ──────────────────────────────
cells.append(md("""---

## Risk Budgets and Position Sizing <a id="risk-budget"></a>

You have a **\\$1M annual volatility budget** for an MSFT bet.

How much can you buy unhedged? How much can you buy hedged?

$$\\text{Position} = \\frac{\\text{Vol budget}}{\\text{Strategy vol}}$$"""))

cells.append(code("""# Annualize relevant moments
var_r = df_eret.var()           # total variance of MSFT excess
var_f = df_factor['Mkt-RF'].var()
var_e = model.resid.var()       # idiosyncratic variance
mu_f  = df_factor['Mkt-RF'].mean()

vol_unhedged = np.sqrt(var_r * 252)
vol_hedged   = np.sqrt(var_e * 252)
budget = 1_000_000

x_unh = budget / vol_unhedged
x_hed = budget / vol_hedged

print(f"Unhedged vol (annual): {vol_unhedged:.2%}")
print(f"Hedged vol (annual):   {vol_hedged:.2%}")
print(f"\\nUnhedged position:    ${x_unh:>14,.0f}")
print(f"Hedged position:      ${x_hed:>14,.0f}")
print(f"\\nHedging multiplier:   {x_hed / x_unh:.2f}x larger position")
print(f"\\nExpected annual P&L (risk-adjusted = alpha only):")
print(f"  Unhedged: ${x_unh * alpha * 252:>14,.0f}")
print(f"  Hedged:   ${x_hed * alpha * 252:>14,.0f}")"""))

cells.append(md("""> **📌 Remember**
>
> The hedged version isn't just safer — it lets you scale up your alpha bet. *If your alpha is real, hedging multiplies your P&L.* If your alpha is fake, hedging also magnifies your losses. The key word is **if**."""))

# ─── 10. Sharpe vs Appraisal ──────────────────────────────────────────
cells.append(md("""---

## Sharpe vs Appraisal Ratio <a id="sharpe"></a>

Two ratios. Same numerator-over-denominator structure. Different question.

| Ratio | Numerator | Denominator | Question |
|-------|-----------|-------------|----------|
| **Sharpe** | $E[r^e]$ | $\\sigma(r^e)$ | Compensation per unit of *total* risk |
| **Appraisal** | $\\alpha$ | $\\sigma(\\epsilon)$ | Compensation per unit of *idiosyncratic* risk |

The Appraisal ratio is the Sharpe of the *hedged* portfolio — the "true" skill measure."""))

cells.append(code("""sharpe_unh = (df_eret.mean() / df_eret.std()) * np.sqrt(252)
sharpe_hed = (Hedged.mean()  / Hedged.std())  * np.sqrt(252)
appraisal  = (alpha          / np.sqrt(var_e)) * np.sqrt(252)

print(f"Sharpe (unhedged):  {sharpe_unh:.3f}")
print(f"Sharpe (hedged):    {sharpe_hed:.3f}")
print(f"Appraisal ratio:    {appraisal:.3f}    ← same as Sharpe(hedged) by construction")"""))

cells.append(md("""> **⚠️ Caution**
>
> Hedging doesn't *always* improve the Sharpe ratio. If the factor has a high premium and your alpha is small, the factor exposure was carrying you. The appraisal ratio tells you what's left when you take that exposure away — that's what you should be paid for."""))

# ─── 11. Variance Decomposition ───────────────────────────────────────
cells.append(md("""---

## Variance Decomposition <a id="variance"></a>

$$\\text{Var}(r^e) = \\beta^2 \\cdot \\text{Var}(f) + \\text{Var}(\\epsilon)$$

The **factor risk share** is exactly the regression R²:

$$\\frac{\\beta^2 \\cdot \\text{Var}(f)}{\\text{Var}(r^e)} = R^2$$"""))

cells.append(code("""factor_var  = beta**2 * var_f
idio_var    = var_e
total_var   = var_r
factor_pct  = factor_var / total_var

print(f"Factor variance share:        {factor_pct:.1%}")
print(f"Idiosyncratic variance share: {1 - factor_pct:.1%}")
print(f"R² from regression:           {model.rsquared:.3f}    ← should match factor share above")"""))

# ─── 12. THE CHALLENGE ────────────────────────────────────────────────
cells.append(md("""---

## 🎯 Challenge: Two Funds, One Decision <a id="challenge"></a>

> **The setup**
>
> You're a junior allocator at a fund-of-funds. Your CIO is meeting with two managers tomorrow: **Fund A** and **Fund B**. Both have a 10-year daily return history (2015-2024). You have 90 minutes to write a 1-paragraph recommendation memo.
>
> Both funds returned positive money. The CIO's first instinct: "go with whoever made the most." You suspect that's wrong.

### 🤖 The new skill
You may use AI freely. Your value is in **the spec, the audit, and the interpretation** — *not* the typing."""))

cells.append(code("""# Load the challenge data
url_chal = 'https://raw.githubusercontent.com/amoreira2/UG54/refs/heads/main/assets/data/FactorModels_AI_challenge.csv'
funds = pd.read_csv(url_chal, parse_dates=['date'], index_col='date')

print(f"Range: {funds.index.min().date()} to {funds.index.max().date()}")
print(f"Columns: {list(funds.columns)}")
print("\\nFirst 3 rows:")
funds.head(3)"""))

cells.append(md("""> **📌 Data dictionary**
>
> | Column | Meaning |
> |--------|---------|
> | `MKT` | Market excess return (already net of RF) |
> | `RF` | Daily risk-free rate (decimal) |
> | `Fund_A` | Fund A daily **total** return |
> | `Fund_B` | Fund B daily **total** return |
>
> ⚠️ The fund returns are **total returns** — you must subtract `RF` to get excess returns before regressing."""))

cells.append(md("""### Q1 — The naive comparison

Plot the cumulative growth of \\$1 invested in each fund. Which one made more money? Compute each fund's **total cumulative return** over the full sample (e.g., 1.85 means +185%).

> **💡 Hint** — Have AI build this in 3 lines. The audit question: *did it use total or excess returns? Does it match the data dictionary?*
>
> **📌 Required variable names** (the submission cell looks for these exact names):
> ```python
> fund_a_total_return = ____   # cumulative total return of Fund A (e.g. 1.85)
> fund_b_total_return = ____   # cumulative total return of Fund B
> ```"""))

cells.append(code("""# Your work here (plot + computation)


# Required outputs — fill these in:
fund_a_total_return = ____
fund_b_total_return = ____

print(f"Fund A total return: {fund_a_total_return:.1%}")
print(f"Fund B total return: {fund_b_total_return:.1%}")"""))

cells.append(md("""### Q2 — The factor regression

Run a CAPM regression for each fund (excess return on MKT, with intercept). Report α (annualized), β, R², and t-stat on α for each.

> **🤖 AI prompt suggestion** *(refine it before using):*
> *"Using the DataFrame `funds`, for each of Fund_A and Fund_B, compute excess return = total return − RF, then regress excess return on MKT with intercept using statsmodels. Report alpha (daily and annualized × 252), beta, R-squared, and the t-stat on alpha."*
>
> **Audit checklist** before trusting the output:
> - Did it subtract RF? (Pitfall #1)
> - Did it `add_constant`? (Pitfall #2)
> - Same frequency on both sides? (Pitfall #3)
> - Are α magnitudes plausible (annual α between −20% and +20%)?
>
> **📌 Required variable names:**
> ```python
> alpha_a_annual = ____   # Fund A's annualized alpha (e.g. 0.033 for 3.3%)
> beta_a         = ____
> alpha_b_annual = ____
> beta_b         = ____
> ```"""))

cells.append(code("""# Your work here (regressions, summary printouts)


# Required outputs — fill these in:
alpha_a_annual = ____
beta_a         = ____
alpha_b_annual = ____
beta_b         = ____

print(f"Fund A: alpha = {alpha_a_annual:.2%}/yr   beta = {beta_a:.2f}")
print(f"Fund B: alpha = {alpha_b_annual:.2%}/yr   beta = {beta_b:.2f}")"""))

cells.append(md("""### Q3 — Skill or factor exposure?

Compute the **Sharpe ratio** and the **Appraisal ratio** for each fund (both annualized).

Which fund has the higher Sharpe? Which has the higher Appraisal? **Why are they different?** Write 2 sentences explaining what each fund is actually doing.

> **📌 Required variable names:**
> ```python
> sharpe_a    = ____   # Sharpe ratio of Fund A (annualized)
> sharpe_b    = ____
> appraisal_a = ____   # Appraisal ratio of Fund A (annualized)
> appraisal_b = ____
> ```"""))

cells.append(code("""# Your work here


# Required outputs — fill these in:
sharpe_a    = ____
sharpe_b    = ____
appraisal_a = ____
appraisal_b = ____

print(f"Fund A: Sharpe = {sharpe_a:.2f}   Appraisal = {appraisal_a:.2f}")
print(f"Fund B: Sharpe = {sharpe_b:.2f}   Appraisal = {appraisal_b:.2f}")"""))

cells.append(md("""**Your 2-sentence explanation** (edit this cell):

> ...
"""))

cells.append(md("""### Q4 — Position sizing under a hedge

Your CIO gives you a **\\$5M annual volatility budget**.

For each fund, assume you can hedge out the market exposure (long the fund, short β·MKT). Compute:
(a) the hedged volatility of each fund (annualized),
(b) the dollar position size you could take in each, and
(c) the expected annual P&L (risk-adjusted = α × position).

Which fund should get the larger allocation? Does this match the answer from Q1?

> **📌 Required variable names:**
> ```python
> position_a = ____   # dollar position in Fund A (e.g. 65_000_000)
> position_b = ____
> ```"""))

cells.append(code("""# Your work here (hedged vol, position, expected PnL)


# Required outputs — fill these in:
position_a = ____
position_b = ____

print(f"Fund A position: ${position_a:>14,.0f}")
print(f"Fund B position: ${position_b:>14,.0f}")"""))

cells.append(md("""### Q5 — The Memo

Write a **single paragraph** (max 6 sentences) addressed to your CIO. State:
1. Your recommendation (Fund A, Fund B, neither, or both).
2. The one number that drives the recommendation.
3. The one risk that could make you wrong.

> **What we're looking for:** financial judgment, not code. The memo is graded on whether it correctly identifies the *appraisal ratio* (not raw return) as the right metric, and whether it gives the right recommendation with appropriate caveats."""))

cells.append(md("""**Write your memo as a Python string in the cell below** so the submission cell can pick it up:"""))

cells.append(code("""MEMO = \"\"\"
Write your 6-sentence-max memo here. Don't delete the surrounding triple quotes.
\"\"\"
print(MEMO)"""))

# ─── Submission cell ──────────────────────────────────────────────────
cells.append(md("""---

## 📤 Submission <a id="submit"></a>

Run the cell below. It will:
1. Check that you have all required variables defined
2. Bundle your answers + memo into a single signed string
3. Print that string

**Copy the entire line that starts with `UG54::`** and paste it into the
submission form: **https://forms.gle/YOUR_FORM_LINK_HERE**

You will receive feedback within 24 hours."""))

cells.append(code("""# === 📤 SUBMISSION CELL — Run this last ===
import json, base64, hashlib, datetime as dt

# Rename your variables to match these names BEFORE running.
# (Or change the names here to match what you used — your call.)
required = [
    "fund_a_total_return", "fund_b_total_return",
    "alpha_a_annual", "beta_a", "alpha_b_annual", "beta_b",
    "appraisal_a", "appraisal_b",
    "position_a", "position_b",
    "MEMO",
]
missing = [v for v in required if v not in dir()]
if missing:
    raise NameError(
        f"\\n❌ Missing variables before submission: {missing}\\n"
        "Make sure each answer cell defines the variable name listed above.\\n"
        "Example: at the end of Q2, write  alpha_a_annual = alpha_a * 252"
    )

payload = {
    "assignment": "FactorModels_AI",
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


# ─── 13. Key Takeaways ────────────────────────────────────────────────
cells.append(md("""---

## 🧠 Key Takeaways <a id="takeaways"></a>

1. **The decomposition is always valid.** $r^e = \\alpha + \\beta f + \\epsilon$ — the interpretation is what matters.

2. **Two questions, two metrics.** Risk model → R². Expected return model → α.

3. **Hedging produces portable alpha.** The hedged portfolio has mean α, vol $\\sigma_\\epsilon$, β = 0.

4. **Hedging multiplies positions.** Smaller vol → bigger position for the same risk budget → more α captured.

5. **Sharpe ≠ Appraisal.** Use Sharpe to compare investments at face value; use Appraisal to identify skill.

6. **AI writes the code, you write the spec.** A complete spec — frequency, intercept, units, what to report — protects you from silent bugs.

---

### 🤖 Submission

Save your completed notebook as `FactorModels_<YourLastName>_<NetID>.ipynb` and upload it to the shared Google Drive folder (link on Brightspace) by **midnight on the due date**.

The auto-evaluator will check:
- Q1-Q4: code runs and produces correct numbers (±5% tolerance)
- Q5 memo: identifies the right fund and the right justifying metric

You'll receive feedback within 24 hours."""))

# ─── Write notebook ───────────────────────────────────────────────────
notebook = {
    "cells": cells,
    "metadata": {
        "colab": {"provenance": [], "toc_visible": True},
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

OUT.write_text(json.dumps(notebook, indent=1))
print(f"✅ Wrote {OUT} ({len(cells)} cells)")
