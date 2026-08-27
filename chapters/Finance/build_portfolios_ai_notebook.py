"""
Build Portfolios_AI.ipynb — Lecture 6.

REBUILT to preserve the source notebook (PortfolioMath_c.ipynb) content:
  - Same dataset: GlobalFinMonthly.csv (US + International + Emerging + bonds)
  - Same key example: US vs International for the diversification point
  - Same equations: R_p = W'R, E[R_p] = W'E[R], Var(R_p) = W'ΣW
  - Same mean-variance frontier visualization
  - Same exercises rolled into a unified challenge

What I ADD on top (the AI-format layer):
  - Pitfall checklist specific to portfolio math
  - Two Live AI Moments, each with a 🔴 loose prompt + 🟢 precise prompt
  - Variable-stub challenge cells + submission cell
  - Submission cell follows the standard paste-token pattern

What I do NOT add:
  - "Diversification gain" formula (not in source)
  - Three-portfolio (equal/minvar/maxSharpe) framework (not in source)
  - SPY/WMT/JPM single-stock examples (source uses asset classes)
"""

import json
from pathlib import Path

OUT = Path(__file__).parent / "Portfolios_AI.ipynb"


def md(t): return {"cell_type": "markdown", "metadata": {}, "source": t.splitlines(keepends=True)}
def code(t): return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": t.splitlines(keepends=True)}


cells = []

# ─── Title + LOs (preserve from source) ───────────────────────────────
cells.append(md("""# Portfolios
## 🎯 Learning Objectives

By the end of this notebook, you will be able to:

1. **See risk through a portfolio lens** — grasp Markowitz's insight that an asset's danger depends on what it adds to the *whole* mix, not on its stand-alone volatility
2. **Express returns, means, and variance with matrix algebra** — $R_p = W'R$, $E[R_p]=W'E[R]$, $\\text{Var}(R_p) = W'\\Sigma W$ scale from 2 assets to hundreds
3. **Quantify diversification benefits** — see how adding a *higher*-volatility asset can *lower* portfolio variance when correlations are below one
4. **Compute and interpret portfolio weights** — long-only, short, leveraged; weights summing to one
5. **Audit AI-generated portfolio math** — covariance vs correlation, dimension mismatches, annualization, weights sum"""))

cells.append(md("""## 📋 Table of Contents

1. [Setup](#setup)
2. [Why Think in Portfolios?](#why)
3. [Portfolio Weights](#weights)
4. [Our Dataset](#data)
5. [Pitfall Checklist for Portfolio Math](#pitfalls)
6. [Live Demo 1: Portfolio Returns](#demo1)
7. [Portfolio Expected Returns](#expected)
8. [Portfolio Variance — Two Forms](#variance)
9. [Live Demo 2: The Diversification Test](#demo2)
10. [The Mean-Variance Frontier](#frontier)
11. [🎯 Challenge: Building a Global Portfolio](#challenge)
12. [Submission](#submit)
13. [Key Takeaways](#takeaways)"""))

# ─── Setup ────────────────────────────────────────────────────────────
cells.append(md("---\n\n## 🛠️ Setup <a id=\"setup\"></a>"))
cells.append(code("""#@title 🛠️ Setup: Run this cell first
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
%matplotlib inline

plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = [10, 6]
plt.rcParams['font.size'] = 12

import warnings; warnings.filterwarnings('ignore')
print("✅ Libraries loaded")"""))

# ─── Why portfolios (preserve Markowitz framing) ──────────────────────
cells.append(md("""---

## Why Think in Portfolios? <a id="why"></a>

Harry Markowitz's great insight was to think of risk in terms of **what an
asset adds to your portfolio**, not its stand-alone volatility.

> **💡 Key Insight**
>
> Just like sugar can be good for you if you're not eating any, but terrible
> if you're eating a lot of it — what investors should care about is their
> **final diet**.
>
> If a stock brings a lot of what you already have, it will be **risky for you**.

**Why volatility alone is misleading:**

- If you have only 1% in a stock and it drops to zero, you lose only 1% of your portfolio
- The stock's standalone volatility barely matters at small positions
- As you buy more, it **becomes** risky **for you** because your portfolio moves more like it
- If this stock moves *together with* your other holdings, even a small position can feel very risky

> **📌 Remember**
>
> The **covariance** across stocks is a key determinant of how much we can
> hold volatile stocks without adding much overall risk."""))

# ─── Portfolio weights (preserve table) ───────────────────────────────
cells.append(md("""---

## Portfolio Weights <a id="weights"></a>

The portfolio weight for asset $j$, denoted $w_j$, is the fraction of
portfolio value held in asset $j$:

$$w_j = \\frac{\\text{Dollars held in asset } j}{\\text{Total portfolio value}}$$

> **📌 Remember**
>
> Portfolio weights sum to one:
>
> $$\\sum_{j=1}^N w_j = 1 \\qquad \\text{or in matrix form:} \\qquad \\mathbf{1}'W = 1$$
>
> This doesn't mean you can't borrow — just that negative weights offset positive ones.

If we separate the risk-free asset out:

$$\\sum_{j=1}^N w_j + w_{rf} = 1 \\qquad \\Longrightarrow \\qquad \\sum_{j=1}^N w_j = 1 - w_{rf}$$

| Type | Description | Example |
|------|-------------|---------|
| **Long-only** | All weights $\\geq 0$ | $W=[0.6, 0.3]$, $w_{rf}=0.1$ |
| **Short** | Some $w_i < 0$ | $W=[1.2, -0.4]$, $w_{rf}=0.2$ |
| **Leveraged** | Risky weights sum to $> 1$ | $W=[1.5, 0.5]$, $w_{rf}=-1$ |

> **Note** — when we work with excess returns (asset return minus risk-free), each
> weight implicitly represents a long-risky / short-risk-free trade. Weights then
> need not sum to one."""))

# ─── Our Dataset (use the actual source data) ─────────────────────────
cells.append(md("""---

## Our Dataset <a id="data"></a>

We work with monthly **excess returns** for five major asset classes
(1963–2016) from a curated CRSP / global-asset-class panel:

| Asset | Description |
|-------|-------------|
| **MKT** | US equity market |
| **WorldxUSA** | International developed equities (ex-USA) |
| **EmergingMarkets** | Emerging-market equities |
| **USA30yearGovBond** | US Treasury long bond |
| **WorldxUSAGovBond** | International government bonds (ex-USA) |

This is the canonical multi-asset dataset for studying diversification."""))

cells.append(code("""#@title 📊 Load Data
url = "https://raw.githubusercontent.com/amoreira2/UG54/main/assets/data/GlobalFinMonthly.csv"
Data = pd.read_csv(url, parse_dates=['Date']).set_index('Date')

# Replace sentinel values (e.g. -99) with NaN before any computation
Data = Data[Data > -1].dropna()
print(f"Data shape: {Data.shape}")
print(f"Date range: {Data.index[0].strftime('%Y-%m')} to {Data.index[-1].strftime('%Y-%m')}")
Data.head()"""))

cells.append(code("""# Convert to excess returns (subtract RF)
Rf = Data['RF']
Data = Data.drop(columns=['RF']).subtract(Rf, axis=0).dropna()
print("Now `Data` contains monthly excess returns:")
Data.head()"""))

# ─── Pitfall checklist ────────────────────────────────────────────────
cells.append(md("""---

## 🛡️ Pitfall Checklist for Portfolio Math <a id="pitfalls"></a>

| | Pitfall | What goes wrong | 🔍 How to detect |
|---|---------|-----------------|-------------------|
| 1 | **Covariance vs correlation** | `df.corr()` where you needed `df.cov()` — same shape, wrong units | Diagonal of `cov()` matches `var()`; diagonal of `corr()` is 1 |
| 2 | **Dimensions misaligned** | $W' \\Sigma W$ blows up if $W$ is $N \\times 1$ but $\\Sigma$ is unaligned | Print shapes; the answer should be a scalar |
| 3 | **Forgetting to annualize** | Monthly variance × √12 is wrong; vol scales with √, variance with × | Mean ×12; vol ×√12; variance ×12 |
| 4 | **Weights not summing to 1 (when they should)** | Long-only portfolio that doesn't add to 100% → return scaled wrong | `print(W.sum())` |
| 5 | **Mixing total and excess returns** | Computing Sharpe on a total-return portfolio without subtracting RF | Sharpe of bonds ≈ 0 if computed correctly on excess |
| 6 | **Sentinel values not cleaned** | -99 placeholder treated as a return | Always filter / replace before computation |

> **🤖 AI-Era Insight**
>
> AI will happily compute $W' \\Sigma W$ and return a number. It probably
> won't tell you whether $\\Sigma$ is in monthly or annual units, whether
> you used `corr` instead of `cov`, or whether you cleaned -99 sentinels.
> Your job is to annualize, check dimensions, and sanity-check magnitudes."""))

# ─── Demo 1: Portfolio returns (loose vs precise) ─────────────────────
cells.append(md("""---

## 🔄 Live Demo 1: Portfolio Returns <a id="demo1"></a>

The portfolio return formula:

$$r_p = \\sum_{j=1}^N w_j r_j = W'R$$

Let's compute the equal-weighted global portfolio. Two ways to ask AI for this.

### 🔴 Loose prompt — what NOT to do

> *"Compute the return of an equal-weight portfolio of `Data`."*

**What AI is likely to produce:**

```python
ret = Data.mean(axis=1)
```

**The bugs:**
- ❌ This averages returns *cross-sectionally each date* — that happens to be
  the right number for *equal weights*, but ONLY because $w_j = 1/N$ for all $j$.
  Change to unequal weights and this method silently breaks.
- ❌ No explicit weights vector, so you can't audit "did it really use 1/N?"
- ❌ No verification that weights sum to 1.
- ❌ No annualization.

### 🟢 Precise prompt — the pattern that works

> *"Build a numpy column vector `W` with equal weights $1/N$ for the $N=5$
> asset classes in `Data`. Confirm that W.sum() = 1. Compute portfolio
> returns as `Rp = Data @ W`. Plot the cumulative growth of $1 invested in
> this portfolio."*"""))

cells.append(code("""# 🟢 The precise version
N = len(Data.columns)
W = np.ones((N, 1)) / N

print(f"Number of risky asset classes: {N}")
print(f"Weights:        {W.flatten()}")
print(f"Weights sum:    {W.sum():.4f}    (should be 1.0)")

# Compute portfolio returns for all dates at once
Rp = Data @ W

fig, ax = plt.subplots(figsize=(10, 5))
(1 + Rp).cumprod().plot(ax=ax, linewidth=2, legend=False)
ax.set_title("Equal-weighted global portfolio — growth of $1 (excess of RF)", fontweight='bold')
ax.set_ylabel("Growth of $1"); plt.tight_layout(); plt.show()"""))

cells.append(md("""> **🐍 Python Insight: `@`**
>
> `Data @ W` does matrix multiplication. `Data` is $T \\times N$, `W` is $N \\times 1$,
> so the result is $T \\times 1$ — one portfolio return per date.
> This replaces nested for-loops with a single line."""))

# ─── Expected returns ─────────────────────────────────────────────────
cells.append(md("""---

## Portfolio Expected Returns <a id="expected"></a>

Since expectations are linear:

$$E[r_p^e] = E\\left[\\sum_{j=1}^N w_j r_j^e\\right] = \\sum_{j=1}^N w_j E[r_j^e] = W'E[R^e]$$"""))

cells.append(code("""# Estimate expected returns from history
E_hat = Data.mean()
print("Monthly expected excess returns:")
print(E_hat.round(4))
print("\\nAnnualized:")
print((E_hat * 12).round(4))"""))

cells.append(code("""# Two equivalent ways to compute portfolio expected return
E_rp_matrix = (W.T @ E_hat.values).item()
E_rp_direct = Rp.mean().item()
print(f"Via W'E[R]:        {E_rp_matrix:.6f}")
print(f"Via mean(Rp):      {E_rp_direct:.6f}")
print(f"\\nAnnualized:       {E_rp_matrix * 12:.2%}")"""))

# ─── Portfolio variance ───────────────────────────────────────────────
cells.append(md("""---

## Portfolio Variance — Two Forms <a id="variance"></a>

Portfolio variance is **not** a weighted average of individual variances. The
two-asset case makes this clear:

$$\\text{Var}(r_p^e) = w_1^2 \\text{Var}(r_1^e) + 2 w_1 w_2 \\text{Cov}(r_1^e, r_2^e) + w_2^2 \\text{Var}(r_2^e)$$

The middle term — twice the weighted covariance — is what makes
diversification possible.

For $N$ assets:

$$\\text{Var}(r_p^e) = \\sum_{j=1}^N \\sum_{i=1}^N w_j w_i \\text{Cov}(r_j^e, r_i^e) = W' \\Sigma W$$

> **💡 Key Insight**
>
> For 50 assets, the sum has 50 variance terms and **2,450 covariance terms**.
> Matrix algebra saves us from quintuple-nested loops."""))

cells.append(code("""# Estimate the covariance matrix
Cov_hat = Data.cov().to_numpy()
print("Annualized covariance matrix:")
print(pd.DataFrame(Cov_hat * 12, index=Data.columns, columns=Data.columns).round(4))"""))

cells.append(code("""# Two equivalent ways to get portfolio variance
Var_rp_direct = Rp.var().item()
Var_rp_matrix = (W.T @ Cov_hat @ W).item()
print(f"Via Var(Rp):       {Var_rp_direct:.6f}")
print(f"Via W'ΣW:          {Var_rp_matrix:.6f}")
print(f"\\nAnnualized vol:    {np.sqrt(Var_rp_matrix * 12):.2%}")"""))

# ─── Demo 2: Diversification (US vs International) ────────────────────
cells.append(md("""---

## 🔄 Live Demo 2: The Diversification Test <a id="demo2"></a>

The famous advice: **"Don't put all your eggs in one basket."**

Let's examine this from a US investor's perspective considering international equities."""))

cells.append(code("""# Correlation and volatility of US vs International
print("Correlation between MKT and WorldxUSA:")
print(Data[['MKT', 'WorldxUSA']].corr().round(3))

print("\\nAnnualized volatilities:")
print((Data[['MKT', 'WorldxUSA']].std() * np.sqrt(12)).round(4))"""))

cells.append(md("""> **🤔 Question before you compute anything**
>
> International equities (WorldxUSA) are *more* volatile than US equities.
> Which portfolio do you expect to have the **lowest** volatility?
> - 100% US?
> - 100% International?
> - Something in between?
>
> Make a prediction, then check below.

### 🔴 Loose prompt

> *"Plot how portfolio volatility changes as I shift between US and
> international."*

**What AI is likely to produce:** something with `np.linspace`, a `for` loop, a
plot — but probably:
- ❌ no clear formula (does the AI use $\\text{Var} = W' \\Sigma W$ or the 2-asset shortcut?)
- ❌ inconsistent units (mixing daily/monthly/annual)
- ❌ no labeling of the minimum

### 🟢 Precise prompt

> *"Subset `Data` to columns ['MKT', 'WorldxUSA'] as DataFrame D. Compute its
> covariance matrix `Cov_2`. For w_intl from 0 to 1 in steps of 0.01, build
> $W = [1-w_{intl}, w_{intl}]^T$, compute portfolio variance $W'\\Sigma W$,
> annualize the volatility by $\\sqrt{12}$. Store (w_intl, vol) in a DataFrame.
> Plot vol vs w_intl. Mark the minimum with a horizontal red dashed line and
> label the pure-US and pure-international endpoints."*"""))

cells.append(code("""# Build a 2-asset universe and its covariance
D = Data[['MKT', 'WorldxUSA']]
Cov_2 = D.cov().to_numpy()

# Trace volatility across all weight combinations
results = []
for w_intl in np.arange(0, 1.01, 0.01):
    W_2 = np.array([[1 - w_intl], [w_intl]])
    var = (W_2.T @ Cov_2 @ W_2).item()
    vol_annual = np.sqrt(var) * np.sqrt(12)
    results.append([w_intl, vol_annual])
results = pd.DataFrame(results, columns=['Weight_Intl', 'Volatility'])

# Plot
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(results['Weight_Intl'], results['Volatility'], linewidth=2, color='steelblue')
ax.axhline(y=results['Volatility'].min(), color='red', linestyle='--', alpha=0.7,
           label=f"Minimum vol: {results['Volatility'].min():.2%}")
ax.scatter([0, 1], [results.iloc[0]['Volatility'], results.iloc[-1]['Volatility']],
           s=100, zorder=5, color='darkred')
ax.annotate('100% US',   (0, results.iloc[0]['Volatility']),
            xytext=(0.04, results.iloc[0]['Volatility'] + 0.003))
ax.annotate('100% Intl', (1, results.iloc[-1]['Volatility']),
            xytext=(0.84, results.iloc[-1]['Volatility'] + 0.003))
ax.set_xlabel('Weight on International'); ax.set_ylabel('Annualized Volatility')
ax.set_title('Diversification: US + International', fontweight='bold')
ax.legend(); plt.tight_layout(); plt.show()"""))

cells.append(md("""> **💡 Key Insight**
>
> Adding a **more volatile** asset can **reduce** portfolio volatility when
> correlations are below one! This is exactly Markowitz's insight: risk is
> about the *covariance structure*, not about individual assets.
>
> The minimum is somewhere strictly between 0% and 100% international — that's
> the optimal diversification point for the lowest-volatility portfolio."""))

# ─── Mean-Variance Frontier (preserve the colored scatter) ────────────
cells.append(md("""---

## The Mean-Variance Frontier <a id="frontier"></a>

Now bring expected returns back in. The frontier traces (volatility,
expected return) combinations as you vary the weight on international."""))

cells.append(code("""# Mean-variance frontier (US + International)
E_2 = D.mean() * 12        # annualized expected returns

frontier = []
for w_intl in np.arange(0, 1.01, 0.01):
    W_2 = np.array([[1 - w_intl], [w_intl]])
    er = (W_2.T @ E_2.values).item()
    var = (W_2.T @ Cov_2 @ W_2).item()
    vol = np.sqrt(var) * np.sqrt(12)
    frontier.append([w_intl, vol, er])
frontier = pd.DataFrame(frontier, columns=['Weight_Intl', 'Volatility', 'Expected_Return'])

fig, ax = plt.subplots(figsize=(10, 6))
scatter = ax.scatter(frontier['Volatility'], frontier['Expected_Return'],
                     c=frontier['Weight_Intl'], cmap='coolwarm', s=50)
plt.colorbar(scatter, label='Weight on International')
ax.scatter([frontier.iloc[0]['Volatility']],  [frontier.iloc[0]['Expected_Return']],
           s=150, color='blue', marker='s', zorder=5, label='100% US')
ax.scatter([frontier.iloc[-1]['Volatility']], [frontier.iloc[-1]['Expected_Return']],
           s=150, color='red',  marker='s', zorder=5, label='100% Intl')
ax.set_xlabel('Annualized Volatility'); ax.set_ylabel('Annualized Expected Excess Return')
ax.set_title('Mean-Variance Frontier: US + International', fontweight='bold')
ax.legend(); plt.tight_layout(); plt.show()"""))

# ─── Challenge (built on source exercises, uses real data) ────────────
cells.append(md("""---

## 🎯 Challenge: Building a Global Portfolio <a id="challenge"></a>

> **Setup.** Your CIO wants to consider three diversification candidates for
> the equity portion of a global mandate: **US (MKT)**, **International
> developed (WorldxUSA)**, and **Emerging Markets**. Use the full `Data`
> DataFrame already loaded above.

### Q1 — Custom mixed portfolio

Build a portfolio with **50% MKT, 30% WorldxUSA, 20% EmergingMarkets**.
(So the weights sum to 1 across these three equity asset classes — ignore
bonds for this exercise.)

Compute:

> **📌 Required variable names:**
> ```python
> custom_annual_mean   = ____   # annualized expected excess return (decimal)
> custom_annual_vol    = ____   # annualized volatility
> custom_annual_sharpe = ____   # mean / vol
> ```"""))

cells.append(code("""# Your work here — extract the 3 columns, build W, compute via W'E and W'ΣW


custom_annual_mean   = ____
custom_annual_vol    = ____
custom_annual_sharpe = ____

print(f"Custom portfolio: mean = {custom_annual_mean:.2%}/yr")
print(f"                  vol  = {custom_annual_vol:.2%}/yr")
print(f"                  Sharpe = {custom_annual_sharpe:.2f}")"""))

cells.append(md("""### Q2 — Minimum-variance US/International mix

Repeat the 2-asset (MKT + WorldxUSA) frontier sweep. Find the **weight on
WorldxUSA that minimizes** portfolio volatility.

> **📌 Required variable names:**
> ```python
> w_intl_min_var       = ____   # optimal weight on WorldxUSA (decimal between 0 and 1)
> min_var_annual_vol   = ____   # the minimum annualized vol achieved
> us_only_annual_vol   = ____   # annualized vol of 100% US (for comparison)
> ```"""))

cells.append(code("""# Your work here — scan w_intl from 0 to 1, find the min


w_intl_min_var     = ____
min_var_annual_vol = ____
us_only_annual_vol = ____

print(f"Optimal int'l weight: {w_intl_min_var:.2%}")
print(f"Min portfolio vol:    {min_var_annual_vol:.2%}/yr")
print(f"US-only vol:          {us_only_annual_vol:.2%}/yr")
print(f"Vol reduction from diversifying: {(us_only_annual_vol - min_var_annual_vol)/us_only_annual_vol:.1%}")"""))

cells.append(md("""### Q3 — Adding Emerging Markets

Now add EmergingMarkets as a third asset. Build a grid of weights
$(w_{US}, w_{Intl}, w_{EM})$ that sum to 1 (e.g. each in [0, 1] in steps
of 0.05). Among all combinations, find the one with the **highest Sharpe ratio** (annualized mean / annualized vol).

> **📌 Required variable names:**
> ```python
> best_sharpe_3asset  = ____   # the maximum annualized Sharpe achievable
> w_us_best           = ____   # optimal weight on MKT
> w_intl_best         = ____   # optimal weight on WorldxUSA
> w_em_best           = ____   # optimal weight on EmergingMarkets
> ```"""))

cells.append(code("""# Your work here — grid search over (w_us, w_intl, w_em) with sum = 1


best_sharpe_3asset = ____
w_us_best          = ____
w_intl_best        = ____
w_em_best          = ____

print(f"Best 3-asset Sharpe:  {best_sharpe_3asset:.2f}")
print(f"Optimal weights — US: {w_us_best:.0%}, Intl: {w_intl_best:.0%}, EM: {w_em_best:.0%}")"""))

cells.append(md("""### Q4 — The Memo

Max 5 sentences. Address your CIO:

1. Does adding international/emerging exposure help, vs holding only US?
2. Cite the **one diagnostic** that proves it (e.g. min-vol reduction, Sharpe gain).
3. Name one **risk** of this analysis (e.g. correlations may rise in stress; sample period; in-sample optimization)."""))

cells.append(code("""MEMO = \"\"\"
Write your 5-sentence-max memo here.
\"\"\"
print(MEMO)"""))

# ─── Submission ───────────────────────────────────────────────────────
cells.append(md("""---

## 📤 Submission <a id="submit"></a>

Run the cell below. Copy the line that starts with `UG54::` into the
submission form: **https://forms.gle/YOUR_FORM_LINK_HERE**"""))

cells.append(code("""# === 📤 SUBMISSION CELL — Run this last ===
import json, base64, hashlib, datetime as dt

required = [
    "custom_annual_mean", "custom_annual_vol", "custom_annual_sharpe",
    "w_intl_min_var", "min_var_annual_vol", "us_only_annual_vol",
    "best_sharpe_3asset", "w_us_best", "w_intl_best", "w_em_best",
    "MEMO",
]
missing = [v for v in required if v not in dir()]
if missing:
    raise NameError(f"\\n❌ Missing: {missing}")

payload = {
    "assignment": "Portfolios_AI",
    "ts": dt.datetime.utcnow().isoformat(timespec="seconds") + "Z",
    "answers": {k: float(eval(k)) for k in required if k != "MEMO"},
    "memo": MEMO.strip(),
}
blob = json.dumps(payload, sort_keys=True)
checksum = hashlib.sha256(blob.encode()).hexdigest()[:8]
token = f"UG54::{checksum}::{base64.b64encode(blob.encode()).decode()}"
print("=" * 72)
print(token)
print("=" * 72)
print(f"Length: {len(token)} chars")"""))

# ─── Takeaways (preserve from source) ────────────────────────────────
cells.append(md("""---

## 🧠 Key Takeaways <a id="takeaways"></a>

1. **Matrix algebra is your friend.** A single line replaces nested loops for $R_p$, $E[R_p]$, $\\text{Var}(R_p)$.

2. **Diversification is all about correlations.** Pairing volatile but imperfectly correlated assets can cut overall risk more than simply holding the lower-volatility asset alone.

3. **How risky is an asset depends on the portfolio of who's asking.** Markowitz's central insight.

4. **The key formulas:**

| Quantity | Formula |
|----------|---------|
| Portfolio return | $R_p = W'R$ |
| Expected return | $E[R_p] = W'E[R]$ |
| Variance | $\\text{Var}(R_p) = W' \\Sigma W$ |

5. **AI computes the matrix algebra. You check dimensions, units, sentinel cleaning, and whether the result is sensible.**"""))

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
