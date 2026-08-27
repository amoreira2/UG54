"""
Build CapitalAllocationI_AI.ipynb — Lecture 7.

REBUILT to preserve source notebook (CapitalAllocationI_cc.ipynb) content:
  - Same data: FF6 monthly factor returns (Mkt-RF, SMB, HML, RMW, CMA, MOM)
  - Same conceptual arc: two decisions → single-asset weight → all-you-need-is-Sharpe
    → five optimization problems → MVE math → Two-Fund Separation + CML
    → alpha bets and portable alpha → combined Sharpe
  - Same exercises rolled into a unified data-driven challenge

What I ADD on top:
  - Pitfall checklist for optimization
  - Two Live AI Moments with loose vs precise prompts
  - Variable-stub challenge + submission cell

What I LEAVE OUT (aside content per the source):
  - Detailed scipy.optimize numerical approach (math approach is canonical)
  - Bloomberg/Taylor Swift state-of-the-world aside
  - In-class question text (rolled into challenge)
"""

import json
from pathlib import Path

OUT = Path(__file__).parent / "CapitalAllocationI_AI.ipynb"

def md(t): return {"cell_type":"markdown","metadata":{},"source":t.splitlines(keepends=True)}
def code(t): return {"cell_type":"code","execution_count":None,"metadata":{},"outputs":[],"source":t.splitlines(keepends=True)}

cells = []

# ─── Title + LOs (preserve source) ────────────────────────────────────
cells.append(md("""# Capital Allocation I
## 🎯 Learning Objectives

By the end of this notebook, you will be able to:

1. **Formulate** the capital allocation problem for an investor maximizing expected utility
2. **Derive** the mean-variance efficient (MVE) portfolio weights for risky assets
3. **Understand** the two-fund separation theorem and its practical implications
4. **Explain** how "all you need is Sharpe" simplifies portfolio construction
5. **Construct** alpha bets and portable alpha strategies in Python
6. **Audit AI-generated optimization code** — units, leverage, sign of weights, normality assumptions"""))

cells.append(md("""## 📋 Table of Contents

1. [Setup](#setup)
2. [The Capital Allocation Problem](#problem)
3. [The Optimal Weight on a Single Asset](#single)
4. [Pitfall Checklist for Optimization](#pitfalls)
5. [Factor Data: FF6](#data)
6. [Live Demo 1: Per-Factor Optimal Weight](#demo1)
7. [All You Need Is Sharpe?](#sharpe)
8. [Five Optimization Problems](#five)
9. [The MVE Formula](#mve)
10. [Live Demo 2: Computing MVE Weights](#demo2)
11. [Two-Fund Separation and the Capital Market Line](#tfs)
12. [Alpha Bets and Portable Alpha](#alpha)
13. [Combining Hedged Alpha with the Market](#combine)
14. [🎯 Challenge: Build the MVE + Alpha Combination](#challenge)
15. [Submission](#submit)
16. [Key Takeaways](#takeaways)"""))

# ─── Setup ────────────────────────────────────────────────────────────
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
print("✅ Libraries loaded")"""))

cells.append(code("""#@title 📦 Helper: download FF6 monthly factor data
from pandas_datareader.data import DataReader

def get_factors_ff6_monthly():
    \"\"\"Download Fama-French 6 factors (monthly, decimal).\"\"\"
    ff  = DataReader("F-F_Research_Data_Factors", "famafrench", start="1921-01-01")[0]
    ff5 = DataReader("F-F_Research_Data_5_Factors_2x3", "famafrench", start="1921-01-01")[0]
    mom = DataReader("F-F_Momentum_Factor", "famafrench", start="1921-01-01")[0]
    df = ff[['RF', 'Mkt-RF', 'SMB', 'HML']].copy()
    df = df.merge(ff5[['RMW', 'CMA']], on='Date', how='outer')
    df = df.merge(mom, on='Date', how='outer')
    df.columns = ['RF', 'Mkt-RF', 'SMB', 'HML', 'RMW', 'CMA', 'MOM']
    df.index = pd.to_datetime(df.index.to_timestamp()) + pd.offsets.MonthEnd(0)
    return df / 100"""))

# ─── The Capital Allocation Problem (preserve from source) ────────────
cells.append(md("""---

## The Capital Allocation Problem <a id="problem"></a>

Every investor faces two fundamental questions:

1. **How much risk should I take?** (Allocation between risky and risk-free)
2. **How should I spread that risk?** (Allocation across risky assets)

> **💡 Key Insight**
>
> A fundamental insight of portfolio theory is that these two decisions are
> **separable**:
> 1. First, find the portfolio with the best risk-return properties
> 2. Then, decide how much to allocate to it vs. the risk-free asset

### Who decides how much risk to take?

If you're investing your own money (the **principal**), your optimal portfolio
depends on:

| Factor | Examples |
|--------|----------|
| **Risk tolerance** | How terrible you feel if you have less than expected |
| **Investment horizon** | Retirement in 5 years vs 30 years |
| **Financial goals** | Minimum retirement income, college fund, property purchase |
| **Background risk** | Other income sources, job security |"""))

# ─── Single Asset Optimal Weight (preserve derivation) ────────────────
cells.append(md("""---

## The Optimal Weight on a Single Asset <a id="single"></a>

We model preferences using **mean-variance utility**:

$$\\max_w \\; w \\cdot E[r_p] - \\frac{\\gamma}{2} w^2 \\cdot \\text{Var}(r_p)$$

where $w$ is the weight on the risky portfolio, $\\gamma$ is risk aversion, and
$r_p$ is the risky portfolio's excess return.

Taking the derivative with respect to $w$ and setting to zero:

$$\\boxed{\\; w^* = \\frac{1}{\\gamma} \\cdot \\frac{E[r_p]}{\\text{Var}(r_p)} \\;}$$

> **💡 Key Insight**
>
> Your optimal weight is proportional to the **risk-return trade-off**. Equivalently,
> your optimal portfolio volatility is:
>
> $$w^* \\cdot \\sigma(r_p) = \\frac{1}{\\gamma} \\cdot \\text{Sharpe Ratio}$$
>
> So Sharpe ratio maps directly to **how much vol you should run**."""))

# ─── Pitfall checklist ────────────────────────────────────────────────
cells.append(md("""---

## 🛡️ Pitfall Checklist for Optimization <a id="pitfalls"></a>

| | Pitfall | What goes wrong | 🔍 How to detect |
|---|---------|-----------------|-------------------|
| 1 | **Risk aversion units** | $\\gamma$ has units of $1/\\text{return}^2$. A "reasonable" $\\gamma$ for *annual* returns in decimals is 1-10 | If $w^* > 5$ or $< -5$, double-check units |
| 2 | **Total vs excess returns** | Optimal weight uses excess return $\\mu$; total return inflates by RF | Sanity: $w^*$ for market should be ~0.5-1.0 at $\\gamma$=3, not 5-10 |
| 3 | **Annualization inconsistency** | Mixing monthly $\\mu$ with annual $\\Sigma$ → answer is off by $\\sqrt{12}$ | Always annualize both or neither; sanity-check the result against a known number |
| 4 | **Near-singular $\\Sigma$** | With $N$ assets and few observations, $\\Sigma^{-1}$ explodes | Print condition number of $\\Sigma$; if > 100, your weights are noise |
| 5 | **Unbounded weights** | Unconstrained solution can demand $w > 5$ (leverage), $w < -2$ (large shorts) | Print weights before deploying; clip or constrain if needed |
| 6 | **In-sample $\\mu$ for OOS allocation** | Backtest $\\hat{\\mu}$ overstates true $\\mu$ — weights are too aggressive | See Capital Allocation II — use shrinkage or fractional Kelly |

> **🤖 AI-Era Insight**
>
> AI will happily compute `np.linalg.inv(Sigma) @ mu` and return a number. It
> rarely tells you whether $\\mu$ is monthly or annual, whether weights are
> deployable, or whether $\\Sigma$ is well-conditioned. You audit."""))

# ─── Factor Data (preserve table + smart beta context) ────────────────
cells.append(md("""---

## Factor Data: FF6 <a id="data"></a>

We'll work with the **Fama-French 6 factors**:

| Factor | Description |
|--------|-------------|
| **Mkt-RF** | Market excess return |
| **SMB** | Small minus Big (size) |
| **HML** | High minus Low (value) |
| **RMW** | Robust minus Weak (profitability) |
| **CMA** | Conservative minus Aggressive (investment) |
| **MOM** | Momentum |

> **📌 How these factors are built**
>
> - All portfolios are **market-cap-weighted**: once we isolate the stocks for
>   each side (long or short), we weight them by market cap.
> - The long and short sides are the same size, so all these portfolios represent
>   **excess returns**.
> - Putting aside (very important) frictions in taking leverage, these portfolios
>   are **costless to implement** — you fund your longs with your shorts.
> - Except the market (where the short side is risk-free), all the others are
>   **market-neutral cross-sectional bets** — you're not taking a view on the
>   market as a whole, only one segment against another.
> - These portfolios are the core of the **smart-beta** industry. BlackRock, AQR,
>   Invesco, Dimensional, Vanguard, and State Street supply these factors in
>   easy-to-trade wrappers (ETFs or mutual funds)."""))

cells.append(code("""# Load FF6 factor data
df = get_factors_ff6_monthly().dropna()
print(f"Data range: {df.index[0].strftime('%Y-%m')} to {df.index[-1].strftime('%Y-%m')}")
print(f"Months: {len(df)}")
df.head()"""))

cells.append(code("""# Separate risk-free and factor (excess return) columns
rf      = df['RF']
factors = df.drop(columns=['RF'])

# Annualized summary
summary = pd.DataFrame({
    'Mean (ann)':     factors.mean()  * 12,
    'Vol (ann)':      factors.std()   * np.sqrt(12),
    'Sharpe':         (factors.mean() * 12) / (factors.std() * np.sqrt(12)),
    'Freq >3σ events': (factors.abs() / factors.std() > 3).mean(),
})
summary.round(3)"""))

# ─── Live Demo 1: per-factor optimal weight ───────────────────────────
cells.append(md("""---

## 🔄 Live Demo 1: Per-Factor Optimal Weight <a id="demo1"></a>

If you could invest in **only one** factor (plus the risk-free asset), what
weight would you put on each? Apply $w^* = \\mu / (\\gamma \\sigma^2)$ for $\\gamma = 4$.

### 🔴 Loose prompt — what NOT to do

> *"For each factor in `factors`, compute the optimal weight assuming risk
> aversion 4."*

**What AI is likely to produce:**

```python
gamma = 4
for col in factors.columns:
    w = factors[col].mean() / (gamma * factors[col].var())
    print(f"{col}: w = {w:.2f}")
```

**The bugs:**
- ❌ Uses **monthly** mean and variance — but the conventional $\\gamma$ scale assumes
  annual. The result will be ~12× too small.
- ❌ No sanity check on the magnitudes — silent error.
- ❌ Doesn't report resulting *portfolio volatility* — which is the more
  interpretable number ($w^* \\sigma = SR/\\gamma$).

### 🟢 Precise prompt — the pattern that works

> *"For each column in `factors` (monthly excess returns), compute the
> **annualized** mean ($\\bar\\mu \\times 12$) and variance ($\\bar\\sigma^2 \\times 12$).
> With risk aversion $\\gamma = 4$, compute the optimal weight $w^* = \\mu_{ann} / (\\gamma \\sigma^2_{ann})$.
> Also report the resulting annualized portfolio volatility, $w^* \\cdot \\sigma_{ann}$.
> Present the results in a single DataFrame."*"""))

cells.append(code("""# 🟢 The precise version
gamma = 4
mu_ann  = factors.mean() * 12
var_ann = factors.var()  * 12
vol_ann = factors.std()  * np.sqrt(12)

w_star  = mu_ann / (gamma * var_ann)
vol_p   = w_star.abs() * vol_ann

per_factor = pd.DataFrame({
    'mu_ann':  mu_ann,
    'vol_ann': vol_ann,
    'Sharpe':  mu_ann / vol_ann,
    'w*':      w_star,
    'portfolio vol': vol_p,
})
per_factor.round(3)"""))

cells.append(md("""> **🤔 Look at the output**
>
> Notice that the *portfolio volatility* column is just $SR/\\gamma$ — the
> factor with the highest Sharpe gets the highest portfolio vol allocation.
> The weight itself depends on the factor's own variance: factors with low
> variance (like MOM after RMW) get larger weights to achieve the same vol exposure."""))

# ─── All You Need Is Sharpe? ──────────────────────────────────────────
cells.append(md("""---

## All You Need Is Sharpe? <a id="sharpe"></a>

The Sharpe ratio is powerful because:
- Higher SR → more growth per unit of risk
- For the same growth, you need less risk
- Higher expected growth → fewer large losses

> **⚠️ Caution**
>
> Sharpe ratio is "all you need" **only if**:
>
> 1. You have mean-variance preferences
> 2. Returns are normally distributed
>
> **Normality.** Check the realized tails of your portfolio. Look at the
> *"Freq >3σ events"* column in the summary table above — under normality this
> should be ~0.3%. For most factors it's 0.5-1.5%. Tails are fatter than normal.
>
> **Preferences.** Do you care about all returns equally? Or is a bad return
> *worse* in some states of the world (job loss, market crash)? If you have
> "background risk" (e.g. you work at a bank), you may want to underweight
> assets correlated with your job."""))

cells.append(code("""# Visualize the Sharpe ratios
fig, ax = plt.subplots(figsize=(10, 4.5))
summary['Sharpe'].sort_values().plot(kind='barh', ax=ax, color='steelblue')
ax.axvline(0, color='black', linewidth=0.5)
ax.set_xlabel('Sharpe ratio (annualized)')
ax.set_title('FF6 factor Sharpe ratios', fontweight='bold')
plt.tight_layout(); plt.show()"""))

# ─── Five Optimization Problems (preserve framing) ────────────────────
cells.append(md("""---

## Five Optimization Problems <a id="five"></a>

When you have multiple risky assets, "the best portfolio" depends on what you
mean by best:

| # | Problem | Math |
|---|---------|------|
| 1 | Max mean-variance | $\\max_W E[W'R^e] - \\frac{\\gamma}{2}\\text{Var}(W'R^e)$ |
| 2 | Max return given variance budget | $\\max_W E[W'R^e]$ s.t. $\\text{Var}(W'R^e) \\le \\bar{V}$ |
| 3 | Min variance given return target | $\\min_W \\text{Var}(W'R^e)$ s.t. $E[W'R^e] \\ge \\bar{r}$ |
| 4 | Min variance (no return constraint) | $\\min_W \\text{Var}(W'R^e)$ |
| 5 | Max Sharpe ratio | $\\max_W E[W'R^e] / \\sqrt{\\text{Var}(W'R^e)}$ |

> **💡 Key Insight**
>
> Problems 1, 2, 3, and 5 all produce portfolios with the **same relative
> weights** — they all want the **highest Sharpe ratio**, and use it to achieve
> different goals. Problem 4 is the exception — it ignores expected return entirely
> and just minimizes variance.

You can solve these three ways: (a) grid search, (b) numerical optimizer, or
(c) **the math approach** (closed form). We focus on the math — it's exact and
gives intuition. (Grids and numerical solvers are good when you have constraints
like "weights ≥ 0" that break the closed form.)"""))

# ─── MVE Math (preserve derivation) ───────────────────────────────────
cells.append(md("""---

## The MVE Formula <a id="mve"></a>

Start with the mean-variance problem (multi-asset):

$$\\max_W \\; W' E[R^e] - \\frac{\\gamma}{2} W' \\text{Var}(R^e) W$$

Differentiating with respect to $W$ and setting to zero:

$$E[R^e] - \\gamma \\, \\text{Var}(R^e) \\, W = 0$$

> 👉 This is the **marginal-benefit-equals-zero** condition: at the optimum, the
> marginal increase in expected return from adding more of any asset equals the
> marginal increase in variance (scaled by $\\gamma$).

Solving for $W$:

$$\\boxed{\\; W^* = \\frac{1}{\\gamma} \\, \\text{Var}(R^e)^{-1} E[R^e] \\;}$$

> **💡 Key Insight**
>
> This is the **MVE (Mean-Variance Efficient) portfolio.** Plug in forward-looking
> $E[R^e]$ and $\\text{Var}(R^e)$, and you get the optimal weights.
>
> The catch — and it is a big catch — is that both inputs must be **forward-looking**
> estimates. Estimating them is hard (see Factor Models II). Capital Allocation II
> tackles what to do when you don't trust your estimates."""))

cells.append(md("""> **🐍 Python Insight: `np.linalg.inv()`**
>
> ```python
> Sigma_inv = np.linalg.inv(Sigma)
> ```
> For numerical stability with near-singular matrices, use `np.linalg.pinv()`
> (pseudo-inverse).
>
> Intuition: just as $2 \\cdot 2^{-1} = 1$, the matrix inverse satisfies
> $\\Sigma \\Sigma^{-1} = I$ (identity)."""))

# ─── Live Demo 2: MVE computation ─────────────────────────────────────
cells.append(md("""---

## 🔄 Live Demo 2: Computing MVE Weights <a id="demo2"></a>

### 🔴 Loose prompt

> *"Compute the optimal portfolio weights for the FF6 factors."*

**What AI is likely to produce:**

```python
W = np.linalg.inv(factors.cov()) @ factors.mean()
```

**The bugs:**
- ❌ No risk aversion $\\gamma$ — so this is the *unscaled* MVE direction, not a
  weight for any specific investor. Fine if you're going to scale to a target vol,
  but **must be flagged**.
- ❌ Monthly $\\mu$ paired with monthly $\\Sigma^{-1}$ — the answer has units; that's
  fine as long as you understand them, but the weight isn't dimensionless.
- ❌ No reporting of resulting portfolio Sharpe / vol.

### 🟢 Precise prompt

> *"Estimate $\\hat\\mu$ (mean) and $\\hat\\Sigma$ (covariance) from `factors`
> (monthly excess returns). Compute the unscaled MVE direction
> $W_{MVE} = \\hat\\Sigma^{-1} \\hat\\mu$. Report the resulting portfolio's annualized
> expected return, volatility, and Sharpe ratio. Note that the absolute weight
> level is a leverage choice — to get a γ-specific weight, scale by $1/\\gamma$."*"""))

cells.append(code("""# Estimate moments from the sample
mu_hat    = factors.mean()    # monthly expected excess returns
Sigma_hat = factors.cov()     # monthly covariance matrix

print("Monthly expected excess returns:")
print(mu_hat.round(4))
print("\\nMonthly covariance matrix:")
print(Sigma_hat.round(6))"""))

cells.append(code("""# MVE direction (unscaled by γ)
Sigma_inv = np.linalg.inv(Sigma_hat.values)
W_mve = Sigma_inv @ mu_hat.values

print("MVE weights (unscaled — multiply by 1/γ to get γ-specific weights):")
print(pd.Series(W_mve, index=factors.columns).round(2))

# Portfolio statistics — annualized
mve_ret_m = (W_mve @ mu_hat.values)
mve_var_m = (W_mve @ Sigma_hat.values @ W_mve)
mve_vol_m = np.sqrt(mve_var_m)
mve_sr    = (mve_ret_m * 12) / (mve_vol_m * np.sqrt(12))

print(f"\\nMVE portfolio (annualized):")
print(f"  Expected return: {mve_ret_m * 12:.2%}")
print(f"  Volatility:      {mve_vol_m * np.sqrt(12):.2%}")
print(f"  Sharpe ratio:    {mve_sr:.2f}")"""))

# ─── Two-Fund Separation + CML ────────────────────────────────────────
cells.append(md("""---

## Two-Fund Separation and the Capital Market Line <a id="tfs"></a>

The maximum-Sharpe portfolio is:

$$W_{SR} = \\Sigma^{-1} E[R^e]$$

This portfolio is also called:
- **MVE** (Mean-Variance Efficient) portfolio
- **Tangency** portfolio (tangent to the CML in mean-vol space)

> **💡 Key Insight: Leverage doesn't change Sharpe**
>
> $$SR(\\lambda W' R) = \\frac{\\lambda E[W' R]}{\\sigma(\\lambda W' R)} = \\frac{E[W' R]}{\\sigma(W' R)}$$
>
> If $W$ is MVE, then $\\lambda W$ is also MVE for any $\\lambda > 0$.

> **💡 Key Insight: Two-Fund Separation**
>
> All investors — regardless of risk aversion — hold the **same risky portfolio**.
> They differ only in **how much** of it they hold:
> - Risk-averse: small position in MVE + large position in risk-free
> - Risk-tolerant: large (possibly leveraged) position in MVE
>
> A risk-averse investor does **not** hold safer assets — they hold a **safer
> portfolio** that includes a little of MVE and a lot of the risk-free asset."""))

cells.append(code("""# Trace the Capital Market Line: scaled MVE portfolio over a range of leverage
leverage_grid = np.linspace(0, 0.6, 100)
frontier = []
for lev in leverage_grid:
    W = lev * W_mve
    er  = (W @ mu_hat.values) * 12
    vol = np.sqrt(W @ Sigma_hat.values @ W) * np.sqrt(12)
    frontier.append([lev, vol, er])
frontier = pd.DataFrame(frontier, columns=['Leverage', 'Volatility', 'Expected_Return'])

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(frontier['Volatility'], frontier['Expected_Return'], linewidth=2, color='steelblue', label='CML')
ax.scatter([0], [0], s=100, color='green',  zorder=5, label='Risk-free (0% vol)')
ax.scatter([frontier.iloc[33]['Volatility']], [frontier.iloc[33]['Expected_Return']],
           s=100, color='orange', zorder=5, label='Conservative investor')
ax.scatter([frontier.iloc[66]['Volatility']], [frontier.iloc[66]['Expected_Return']],
           s=100, color='red',    zorder=5, label='Aggressive investor')
ax.set_xlabel('Annualized Volatility'); ax.set_ylabel('Annualized Expected Excess Return')
ax.set_title('Capital Market Line — all investors on the same line', fontweight='bold')
ax.legend(); plt.tight_layout(); plt.show()"""))

# ─── Alpha Bets and Portable Alpha ────────────────────────────────────
cells.append(md("""---

## Alpha Bets and Portable Alpha <a id="alpha"></a>

It is useful to decompose your allocation into **factor bets** and **alpha bets**.

For an alpha portfolio with $N$ hedged strategies:
- Alphas $\\alpha$ ($N \\times 1$): the expected excess returns *after* hedging out factor exposure
- Idiosyncratic covariance $\\Sigma_\\epsilon$ ($N \\times N$): variance-covariance of the residuals

The optimal alpha-portfolio weights (analog of MVE):

$$W = \\Sigma_\\epsilon^{-1} \\alpha$$

And the factor hedge (so the combined book has zero factor exposure):

$$W_f = -W'\\beta$$

### When residuals are uncorrelated

If the factors strip out all co-movement, $\\Sigma_\\epsilon$ is diagonal:

$$W_i = \\frac{\\alpha_i}{\\sigma^2_{\\epsilon,i}}$$

Rewriting in **volatility-allocation** terms:

$$W_i \\sigma_{\\epsilon,i} = \\frac{\\alpha_i}{\\sigma_{\\epsilon,i}} = \\text{Appraisal Ratio of strategy } i$$

> **💡 Key Insight**
>
> The **volatility allocation** to each hedged strategy equals its appraisal ratio.
> Strategies with higher hedged-Sharpe deserve more vol budget. Strategies with
> negative or near-zero appraisal ratio get little or nothing."""))

cells.append(code("""# Estimate alpha and beta of each non-market factor relative to MKT
assets = ['SMB', 'HML', 'RMW', 'CMA', 'MOM']
market = 'Mkt-RF'

results = []
residuals_list = []
hedged_list    = []
for asset in assets:
    X = sm.add_constant(df[market])
    y = df[asset]
    model = sm.OLS(y, X).fit()
    results.append({
        'Asset':           asset,
        'Alpha (ann)':     model.params['const'] * 12,
        'Beta':            model.params[market],
        'Idio vol (ann)':  model.resid.std() * np.sqrt(12),
        'Appraisal (ann)': (model.params['const'] / model.resid.std()) * np.sqrt(12),
    })
    residuals_list.append(model.resid)
    # 'Hedged return' = alpha + residual (i.e., factor return with market exposure removed)
    hedged_list.append(model.params['const'] + model.resid)

results_df       = pd.DataFrame(results).set_index('Asset')
residuals_matrix = np.vstack(residuals_list).T
hedged_matrix    = np.vstack(hedged_list).T
Sigma_eps        = np.cov(residuals_matrix.T)
results_df.round(3)"""))

cells.append(code("""# Optimal alpha-portfolio weights
Alpha_m = results_df['Alpha (ann)'].values / 12    # back to monthly
W_alpha = np.linalg.inv(Sigma_eps) @ Alpha_m
print("Optimal alpha-portfolio weights (unscaled):")
print(pd.Series(W_alpha, index=assets).round(2))"""))

# ─── Combining hedged + market ────────────────────────────────────────
cells.append(md("""---

## Combining Hedged Alpha with the Market <a id="combine"></a>

If your mandate allows it, you can combine the alpha portfolio with the market.

The hedged alpha portfolio has, by construction, **zero covariance** with the
market — we stripped out beta. So the joint covariance matrix is diagonal:

$$\\text{Var}(R^e) = \\begin{bmatrix} \\sigma^2_{MKT} & 0 \\\\ 0 & \\sigma^2_{\\text{Hedged}} \\end{bmatrix}$$

and the optimal weights decouple:

$$W^* = \\begin{bmatrix} E[R^e_{MKT}] / \\sigma^2_{MKT} \\\\ \\alpha_{\\text{Hedged}} / \\sigma^2_{\\text{Hedged}} \\end{bmatrix}$$

> **💡 Sharpe Pythagoras**
>
> When two strategies are orthogonal (uncorrelated):
>
> $$SR_\\text{combined} = \\sqrt{SR_A^2 + SR_B^2}$$
>
> Adding an uncorrelated alpha stream of equal Sharpe to a market exposure
> multiplies the combined Sharpe by $\\sqrt{2}$. Adding the 10th uncorrelated
> Sharpe-equal stream still helps — by $\\sqrt{1 + 1/9}$."""))

cells.append(code("""# Combined Sharpe (Pythagoras) on real data
hedged_returns = hedged_matrix @ W_alpha
hedged_er  = hedged_returns.mean() * 12
hedged_vol = hedged_returns.std()  * np.sqrt(12)
hedged_sr  = hedged_er / hedged_vol

mkt_er  = df[market].mean() * 12
mkt_vol = df[market].std()  * np.sqrt(12)
mkt_sr  = mkt_er / mkt_vol

combined_sr = np.sqrt(mkt_sr**2 + hedged_sr**2)

print(f"Market Sharpe (annualized):           {mkt_sr:.2f}")
print(f"Alpha-portfolio Sharpe (hedged, ann): {hedged_sr:.2f}")
print(f"Combined Sharpe (Pythagoras):         {combined_sr:.2f}")
print(f"\\nThe alpha portfolio adds {combined_sr - mkt_sr:.2f} Sharpe-points on top of the market.")"""))

# ─── Challenge ────────────────────────────────────────────────────────
cells.append(md("""---

## 🎯 Challenge: Build the MVE + Alpha Combination <a id="challenge"></a>

> **Setup.** Using `factors` (FF6 monthly excess returns) already loaded:

### Q1 — Per-factor optimal weight

For risk aversion $\\gamma = 4$, compute the optimal weight on each factor
*individually*. Report the factor with the **highest** optimal weight.

> **📌 Required variable names:**
> ```python
> gamma = 4
> best_factor_individual_weight = ____   # the largest w* across the 6 factors
> ```"""))

cells.append(code("""# Your work here (use annualized mu and var)


gamma = 4
best_factor_individual_weight = ____

print(f"Best per-factor weight at γ=4: {best_factor_individual_weight:.2f}")"""))

cells.append(md("""### Q2 — MVE portfolio annualized Sharpe

Compute the MVE multi-asset Sharpe ratio across all 6 factors (annualized).
*(Hint: the Sharpe of the MVE portfolio doesn't depend on $\\gamma$ — it's just
$\\sqrt{\\mu' \\Sigma^{-1} \\mu}$ annualized.)*

> **📌 Required variable name:**
> ```python
> mve_annual_sharpe = ____
> ```"""))

cells.append(code("""# Your work here


mve_annual_sharpe = ____
print(f"MVE Sharpe (annualized): {mve_annual_sharpe:.2f}")"""))

cells.append(md("""### Q3 — Target-volatility scaling (Two-Fund Separation in practice)

You want to run the MVE portfolio at **15% annualized volatility**. By two-fund
separation, the *only* decision is how much to scale.

If the unscaled MVE portfolio has annualized volatility $\\sigma_{MVE}$ and
expected return $\\mu_{MVE}$, then to hit 15% vol:

$$\\lambda = \\frac{0.15}{\\sigma_{MVE}}, \\qquad \\text{Expected return at 15% vol} = \\lambda \\cdot \\mu_{MVE}$$

> **📌 Required variable names:**
> ```python
> target_vol_leverage          = ____   # the scalar λ
> target_vol_expected_return   = ____   # annualized expected excess return at 15% vol
> ```"""))

cells.append(code("""target_vol = 0.15
# Your work here (compute σ_MVE and μ_MVE first, then solve for λ)


target_vol_leverage        = ____
target_vol_expected_return = ____

print(f"Leverage λ to hit 15% vol:         {target_vol_leverage:.2f}")
print(f"Annualized expected return at 15%: {target_vol_expected_return:.2%}")"""))

cells.append(md("""### Q4 — Hedged alpha portfolio Sharpe

Build the alpha portfolio using SMB, HML, RMW, CMA, MOM regressed on MKT.
Compute the annualized Sharpe of the resulting hedged portfolio
($\\text{alpha + idiosyncratic noise}$).

> **📌 Required variable name:**
> ```python
> hedged_alpha_sharpe = ____
> ```"""))

cells.append(code("""# Your work here (use the residuals-based construction above as a guide)


hedged_alpha_sharpe = ____
print(f"Hedged alpha portfolio Sharpe: {hedged_alpha_sharpe:.2f}")"""))

cells.append(md("""### Q5 — Combined Sharpe (Market + Hedged Alpha)

Apply Sharpe Pythagoras: $SR_{combined} = \\sqrt{SR_{MKT}^2 + SR_{Hedged}^2}$.

> **📌 Required variable name:**
> ```python
> combined_sharpe_market_plus_alpha = ____
> ```"""))

cells.append(code("""# Your work here


combined_sharpe_market_plus_alpha = ____
print(f"Combined Sharpe: {combined_sharpe_market_plus_alpha:.2f}")"""))

cells.append(md("""### Q6 — The Memo

Max 5 sentences. Address your CIO:

1. What's the Sharpe improvement from adding the alpha portfolio on top of the market?
2. What's the one assumption that drives the "uncorrelated → Pythagoras" math (and could fail)?
3. What's your single biggest concern about deploying this in real money?"""))

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
    "best_factor_individual_weight",
    "mve_annual_sharpe",
    "target_vol_leverage",
    "target_vol_expected_return",
    "hedged_alpha_sharpe",
    "combined_sharpe_market_plus_alpha",
    "MEMO",
]
missing = [v for v in required if v not in dir()]
if missing: raise NameError(f"\\n❌ Missing: {missing}")

payload = {
    "assignment": "CapitalAllocationI_AI",
    "ts": dt.datetime.utcnow().isoformat(timespec="seconds") + "Z",
    "answers": {k: float(eval(k)) for k in required if k != "MEMO"},
    "memo": MEMO.strip(),
}
blob = json.dumps(payload, sort_keys=True)
checksum = hashlib.sha256(blob.encode()).hexdigest()[:8]
token = f"UG54::{checksum}::{base64.b64encode(blob.encode()).decode()}"
print("="*72); print(token); print("="*72)
print(f"Length: {len(token)} chars")"""))

# ─── Takeaways (preserve source) ──────────────────────────────────────
cells.append(md("""---

## 🧠 Key Takeaways <a id="takeaways"></a>

1. **Separate the two decisions** — first find the best risk-return portfolio,
   then decide how much risk to take.

2. **MVE formula:** $W^* = \\frac{1}{\\gamma} \\Sigma^{-1} E[R^e]$. The weights have
   a closed-form solution.

3. **Two-fund separation** — all investors hold the same risky portfolio (MVE),
   in different amounts. Their risk aversion determines the leverage, not the
   mix of risky assets.

4. **Portable alpha** — separate factor exposure (beta) from alpha by hedging.
   The optimal alpha portfolio is $W = \\Sigma_\\epsilon^{-1} \\alpha$.

5. **Sharpe Pythagoras** — uncorrelated strategies combine as $\\sqrt{\\sum SR_i^2}$.
   Higher appraisal ratios → bigger contribution.

| Concept | Formula |
|---------|---------|
| Single-asset weight | $w^* = \\frac{1}{\\gamma} \\frac{\\mu}{\\sigma^2}$ |
| Single-asset vol allocation | $w^* \\sigma = \\frac{SR}{\\gamma}$ |
| MVE weights | $W = \\Sigma^{-1} \\mu$ (unscaled) |
| Alpha portfolio | $W = \\Sigma_\\epsilon^{-1} \\alpha$ |
| Combined Sharpe (uncorrelated) | $SR = \\sqrt{SR_1^2 + SR_2^2}$ |

6. **AI does the matrix algebra. You verify units, sanity-check magnitudes, and
   decide whether the prescribed weights are deployable.**"""))

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
