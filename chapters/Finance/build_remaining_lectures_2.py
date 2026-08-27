"""
Second batch:
  L19 Risk Management (variance estimation + factor risk limits)
  L20 Implementation (trading costs, leverage, shorting) — NEW
  L21 Machine Learning I (penalized regression)
  L22 Machine Learning II (trees, neural nets)
  L23 LLMs in Finance
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
# L19 — Risk Management (with variance estimation)
# ═══════════════════════════════════════════════════════════════════════
c = []
c.append(md("""# Risk Management — Variance Forecasts and Factor Risk Limits
## 🎯 Learning Objectives

By the end of this notebook, you will be able to:

1. **Estimate and forecast portfolio volatility** using realized variance and AR(1)
2. **Understand VIX** as the market's implied vol — compare it to historical realized vol
3. **Apply factor risk limits** — how pod shops constrain exposure to individual factors
4. **Compute Value-at-Risk (VaR) and Expected Shortfall** for a portfolio
5. **Audit AI-generated risk metrics** — frequency consistency, tail-distribution assumptions"""))

c.append(md("""## 📋 TOC
1. [Setup](#setup)  2. [Variance Forecasting Basics](#variance)
3. [Pitfall Checklist](#pitfalls)  4. [Realized Variance and AR(1)](#realized)
5. [VIX and Implied Vol](#vix)  6. [Factor Risk Limits](#limits)
7. [VaR and Expected Shortfall](#var)  8. [🎯 Challenge: Risk-Budget a Portfolio](#challenge)
9. [Submission](#submit)  10. [Key Takeaways](#takeaways)"""))

c.append(md("---\n## 🛠️ Setup <a id=\"setup\"></a>"))
c.append(setup_cell())

c.append(md("""---
## Variance Forecasting Basics <a id="variance"></a>

We deferred this from the Estimation lecture (L5). Now we tackle it.

**The good news about variances:** unlike means, variances are *forecastable*.
The empirical regularity: high-vol months are followed by high-vol months,
and low-vol by low-vol. This is **volatility clustering**.

Robert Engle won the 2003 Nobel for ARCH/GARCH models that exploit this.
You don't need ARCH/GARCH to capture most of it — a simple AR(1) on
realized variance does ~80% of the work."""))

c.append(md("""---
## 🛡️ Pitfall Checklist <a id="pitfalls"></a>

| | Pitfall | What goes wrong | 🔍 How to detect |
|---|---------|-----------------|-------------------|
| 1 | **Confusing variance with vol** | Annualization: σ × √N, σ² × N | Compute both ways, sanity-check magnitudes |
| 2 | **Overlapping rolling windows** | 252-day rolling vol uses 251 shared days from yesterday | Use non-overlapping windows for hypothesis tests |
| 3 | **Tail assumption: normality** | VaR from normal under-predicts tail losses by 2-3x | Compare actual 1st percentile to normal model |
| 4 | **Stale prices in idiosyncratic vol** | When you use beta from one period and residuals from another | Recompute beta inside the window |
| 5 | **Factor risk added linearly** | Factor exposures don't add — they correlate | Use the covariance matrix, not absolute sums |"""))

c.append(md("""---
## Realized Variance and AR(1) <a id="realized"></a>

For each month, **realized variance** = sum of squared daily returns within that month:

$$RV_t = \\sum_{d \\in \\text{month } t} r_d^2$$

Then forecast next month's RV from last month's:

$$RV_{t+1} = a + b \\cdot RV_t + \\epsilon_{t+1}$$

Typically $b \\approx 0.5-0.8$ — strong persistence."""))

c.append(code("""# Build realized variance for the market, fit AR(1)
from pandas_datareader.data import DataReader
ff = DataReader("F-F_Research_Data_Factors_daily", "famafrench", start="1990-01-01")[0] / 100
mkt_d = ff['Mkt-RF']

# Monthly RV
rv = mkt_d.groupby(mkt_d.index.to_period('M')).apply(lambda x: (x**2).sum())
rv.index = rv.index.to_timestamp(how='end').normalize()
rv.name = 'RV'

# AR(1) regression
X = sm.add_constant(rv.shift(1).dropna())
y = rv.loc[X.index]
ar1 = sm.OLS(y, X).fit()
print(ar1.summary().tables[1])
print(f"\\nR² of AR(1) on monthly RV: {ar1.rsquared:.3f}")"""))

c.append(md("""---
## VIX and Implied Vol <a id="vix"></a>

The **VIX** is the market's **risk-neutral** expectation of S&P 500 vol
over the next 30 days. It's computed from option prices, and you can read
it off Bloomberg in real time.

**VIX vs realized vol:**
- VIX tends to be **higher** than subsequent realized vol on average — this is the **variance risk premium**, which is itself tradable
- VIX **spikes BEFORE** realized vol does, because options price in expected future shocks
- VIX is your best forward-looking variance forecast for short horizons"""))

c.append(md("""---
## Factor Risk Limits <a id="limits"></a>

Pod shops enforce **factor risk limits** to keep individual managers from
inadvertently making a market or sector bet:

$$\\text{Vol contribution from factor } k = |\\beta_k| \\cdot \\sigma_k$$

Each manager has caps like:
- Total portfolio vol ≤ 8%
- Factor (MKT, sector) vol contribution ≤ 1%
- Single-name vol contribution ≤ 0.5%

These constraints force the manager to **hedge any factor exposure they
didn't intend** — which is the whole point of factor-neutral trading."""))

c.append(md("""---
## VaR and Expected Shortfall <a id="var"></a>

**Value-at-Risk (VaR)** at α: the loss level such that P(loss > VaR) = α.

Common: 1-day 95% VaR. If your portfolio's 1-day VaR is $1M, then 5% of
days you'll lose more than $1M.

**Expected Shortfall (ES)**: the average loss *conditional on* exceeding VaR:

$$ES_\\alpha = E[L \\mid L > VaR_\\alpha]$$

ES is **always larger** than VaR — it measures the *severity* of tail losses,
not just their frequency. Banks and hedge funds increasingly use ES instead
of VaR because VaR understates tail risk."""))

c.append(code("""# Compute 1-day 95% VaR for SPY from history
spy = mkt_d   # use Mkt-RF as proxy for SPY excess
var_95 = spy.quantile(0.05)
es_95  = spy[spy <= var_95].mean()

print(f"Daily VaR (95%): {var_95:.2%}    (5% of days you lose more than this)")
print(f"Expected Shortfall (95%): {es_95:.2%}    (average loss on those bad days)")
print(f"\\nNote ES is ~{abs(es_95/var_95):.1f}× larger than VaR — tail asymmetry.")"""))

# Challenge
c.append(md("""---
## 🎯 Challenge: Risk-Budget a Portfolio <a id="challenge"></a>

> **Setup.** Your portfolio:
> - $50M long the market (β=1.0)
> - $20M long a value strategy (β=0.3 to MKT, σ_idio = 8%)
> - Portfolio vol target: 12% annualized

### Q1 — Total portfolio vol assuming independence

Assume market vol = 18%, value-strategy idiosyncratic vol = 8%, uncorrelated.

> **📌 Required:**
> ```python
> w_market   = 0.50    # $50M / $100M total NAV (assume $100M NAV for simplicity)
> w_value    = 0.20
> sig_market = 0.18
> sig_value_idio = 0.08
> portfolio_vol = ____   # sqrt( (w_m * sig_m)^2 + (w_v * sig_v_idio)^2 ), uncorrelated
> ```"""))
c.append(code("""w_market = 0.50
w_value  = 0.20
sig_market     = 0.18
sig_value_idio = 0.08

portfolio_vol = ____
print(f"Portfolio vol (uncorrelated approx): {portfolio_vol:.2%}")"""))

c.append(md("""### Q2 — VaR

Assuming normal returns, 1-day 95% VaR ≈ $NAV × portfolio_vol / √252 × 1.65.

> **📌 Required:**
> ```python
> nav        = 100_000_000
> daily_vol  = portfolio_vol / np.sqrt(252)
> var_95_dollars = ____   # nav * daily_vol * 1.65
> ```"""))
c.append(code("""nav = 100_000_000

daily_vol = portfolio_vol / np.sqrt(252)
var_95_dollars = ____
print(f"Daily 95% VaR: ${var_95_dollars:,.0f}")"""))

c.append(md("""### Q3 — Are you within vol budget?

> **📌 Required:**
> ```python
> vol_target = 0.12
> within_budget = ____    # 1.0 if portfolio_vol <= vol_target, else 0.0
> ```"""))
c.append(code("""vol_target = 0.12

within_budget = ____
print(f"Within {vol_target:.0%} budget? {bool(within_budget)}")"""))

c.append(md("""### Q4 — Memo

Max 5 sentences. State (i) portfolio vol, (ii) daily VaR, (iii) whether
within budget and (if not) what you would scale back."""))
c.append(code("""MEMO = \"\"\"Write your memo here.\"\"\"
print(MEMO)"""))

c.append(md("---\n## 📤 Submission <a id=\"submit\"></a>"))
c.append(submission_cell("RiskManagement_AI",
    ["portfolio_vol", "var_95_dollars", "within_budget"]))

c.append(md("""---
## 🧠 Key Takeaways <a id="takeaways"></a>
1. **Variance is forecastable.** A simple AR(1) on realized variance captures most of the persistence.
2. **VIX is forward-looking** and tends to overpredict realized vol — the variance risk premium.
3. **Factor risk limits** constrain managers to take only the risks they intended.
4. **VaR is incomplete.** Expected Shortfall captures tail severity.
5. **AI computes the numbers. You interpret them in context.**"""))

write_nb("RiskManagement_AI.ipynb", c)


# ═══════════════════════════════════════════════════════════════════════
# L20 — Implementation (NEW) — Trading Costs, Leverage, Shorting
# ═══════════════════════════════════════════════════════════════════════
c = []
c.append(md("""# Implementation — Trading Costs, Leverage, Shorting
## 🎯 Learning Objectives

By the end of this notebook, you will be able to:

1. **Estimate transaction costs** (spread, market impact) for a strategy
2. **Compute implementation shortfall** — paper return vs realized return
3. **Apply leverage** correctly, accounting for borrowing cost
4. **Understand the mechanics of shorting** — borrow cost, hard-to-borrow names
5. **Audit AI-generated backtests** for naive cost handling"""))

c.append(md("""## 📋 TOC
1. [Setup](#setup)  2. [Why Implementation Matters](#why)
3. [Pitfall Checklist](#pitfalls)  4. [Transaction Costs](#costs)
5. [Implementation Shortfall](#shortfall)  6. [Leverage and Borrowing](#leverage)
7. [Shorting](#shorting)  8. [🎯 Challenge: Net Sharpe](#challenge)
9. [Submission](#submit)  10. [Key Takeaways](#takeaways)"""))

c.append(md("---\n## 🛠️ Setup <a id=\"setup\"></a>"))
c.append(setup_cell())

c.append(md("""---
## Why Implementation Matters <a id="why"></a>

Backtests show gross returns. Real returns are net of:
- **Spread** — half the bid-ask, paid every time you trade
- **Market impact** — the price moves against you as you trade
- **Borrowing cost** for leverage
- **Borrowing cost for short positions** (sometimes negative — you earn rebate on the cash)
- **Financing** for futures/forwards
- **Taxes** (we mostly ignore in academic work; matters for taxable accounts)

**A strategy with 4% gross return and 3% total cost has only 1% net.** This is
the difference between paper alpha and tradeable alpha."""))

c.append(md("""---
## 🛡️ Pitfall Checklist <a id="pitfalls"></a>

| | Pitfall | What goes wrong | 🔍 How to detect |
|---|---------|-----------------|-------------------|
| 1 | **Backtesting at close prices** | Real fills happen at midpoint or worse; backtests overstate returns by ~5bps/trade | Use midpoint or apply explicit spread cost |
| 2 | **Ignoring market impact** | A $10M trade in a small-cap moves the price 50bp+; backtests assume infinite liquidity | Estimate impact using ADV (avg daily volume) |
| 3 | **Quoting Sharpe without specifying capacity** | A strategy works on $10M may not work on $1B | Always report Sharpe at multiple capital levels |
| 4 | **Forgetting financing in long-short** | Long $X, short $X has zero net capital — but you pay financing on $X | Long-short P&L net of financing is what matters |
| 5 | **Hard-to-borrow names** | Some short positions cost 5-20% to maintain | Always check borrow rate before backtesting a short |"""))

c.append(md("""---
## Transaction Costs <a id="costs"></a>

Simplest model: **cost ≈ half_spread × turnover**

Large-cap stocks (SPY, AAPL): half-spread ≈ 1 bp
Mid-cap: 3-10 bp
Small-cap: 10-50 bp
Emerging markets: 30-100 bp

For high-turnover strategies (momentum, statistical arbitrage), this is the
dominant cost item.

**Market impact** adds non-linearly with trade size:

$$\\text{Impact} \\approx \\eta \\cdot \\sigma \\cdot \\sqrt{Q / ADV}$$

where Q is trade size, ADV is average daily volume, η ≈ 0.1-0.5 (estimated).

For trades < 1% of ADV, impact is small. For trades > 10% of ADV, it dominates."""))

c.append(md("""---
## Implementation Shortfall <a id="shortfall"></a>

The **implementation shortfall** measures the gap between paper P&L and realized P&L:

$$IS = P_{\\text{decision}} \\cdot Q - P_{\\text{fill}} \\cdot Q$$

You wanted to buy 1000 shares of AAPL when it was $150. By the time you
finished filling, the average price was $150.20. IS = $200 — that's your
cost.

This is the **single most-watched metric** at execution desks. Algorithm
performance is graded on IS reduction."""))

c.append(md("""---
## Leverage and Borrowing <a id="leverage"></a>

Leverage = (Long + Short Notional) / NAV. A market-neutral fund with $100M
long and $100M short has 2x leverage, 0 net market exposure.

You borrow to fund leverage. Borrow rate depends:
- Broker: typically O/N rate + 50-100 bp
- Repo: O/N rate + 10-30 bp (for sov bonds, etc.)
- Securities lending: variable

**Net excess return** = (gross strategy return × leverage) − (financing cost × leverage − 1)

A 4% gross strategy at 2x leverage with 6% financing cost on the second
dollar = 4×2 − 6×1 = 2% net excess. **Higher leverage isn't always better.**"""))

c.append(md("""---
## Shorting <a id="shorting"></a>

To short a stock, you:
1. Borrow it from a long holder (via your prime broker)
2. Sell it
3. Receive cash → put it in an account (earns short rebate)
4. Eventually buy it back to return the borrow

**Costs:**
- **Borrow fee**: 25 bp/yr typical for liquid names, can spike to 50-100%+ for
  hard-to-borrow (GME during 2021)
- **Recall risk**: if the lender wants their shares back, you must close

**Most quant strategies require shorting.** Long-only versions exist but
typically capture half the premium and double the risk."""))

# Challenge
c.append(md("""---
## 🎯 Challenge: Net Sharpe <a id="challenge"></a>

> **Setup.** Your momentum strategy has these backtest stats:
> - Gross annual return: 8%
> - Annual volatility: 12%
> - Annual turnover: 150%
> - You'll deploy with 2x leverage. Financing cost: 6% per year on excess capital.
> - Trading cost: 8 bp per turn (round-trip).
> - 30% of positions are short. Average borrow cost: 50 bp/yr on shorts.

### Q1 — Trading cost drag

> **📌 Required:**
> ```python
> turnover    = 1.50
> cost_per_turn_bp = 8
> trading_cost_drag = ____   # turnover * cost_per_turn_bp / 10000
> ```"""))
c.append(code("""turnover = 1.50
cost_per_turn_bp = 8

trading_cost_drag = ____
print(f"Trading cost drag: {trading_cost_drag:.2%}")"""))

c.append(md("""### Q2 — Financing drag

You're at 2x leverage. You borrow 1x at 6%.

> **📌 Required:**
> ```python
> leverage     = 2
> financing_cost = 0.06
> financing_drag = ____   # (leverage - 1) * financing_cost
> ```"""))
c.append(code("""leverage = 2
financing_cost = 0.06

financing_drag = ____
print(f"Financing drag: {financing_drag:.2%}")"""))

c.append(md("""### Q3 — Short borrow drag

30% of leveraged book is short, paying 50bp on the short notional.

> **📌 Required:**
> ```python
> short_fraction  = 0.30
> short_borrow_bp = 50
> short_drag      = ____   # leverage * short_fraction * short_borrow_bp / 10000
> ```"""))
c.append(code("""short_fraction  = 0.30
short_borrow_bp = 50

short_drag = ____
print(f"Short-borrow drag: {short_drag:.2%}")"""))

c.append(md("""### Q4 — Net Sharpe

Total drag = trading + financing + short. Net annual return = leveraged
gross − total drag. Net Sharpe = net return / leveraged vol.

> **📌 Required:**
> ```python
> gross_return = 0.08
> annual_vol   = 0.12
> leveraged_gross = leverage * gross_return
> leveraged_vol   = leverage * annual_vol
> total_drag      = trading_cost_drag + financing_drag + short_drag
> net_return      = ____
> net_sharpe      = ____
> ```"""))
c.append(code("""gross_return = 0.08
annual_vol   = 0.12

leveraged_gross = leverage * gross_return
leveraged_vol   = leverage * annual_vol
total_drag      = trading_cost_drag + financing_drag + short_drag

net_return = ____
net_sharpe = ____

print(f"Gross Sharpe (unlevered):  {gross_return / annual_vol:.2f}")
print(f"Total drag:                 {total_drag:.2%}")
print(f"Net return (post-cost):     {net_return:.2%}")
print(f"Net Sharpe:                 {net_sharpe:.2f}")"""))

c.append(md("""### Q5 — Memo

Max 5 sentences. Decide whether to deploy. Cite (i) the gross vs net Sharpe,
(ii) the single biggest cost item, (iii) what could change your mind (e.g.,
lower turnover via better signal design, lower financing cost)."""))
c.append(code("""MEMO = \"\"\"Write your memo here.\"\"\"
print(MEMO)"""))

c.append(md("---\n## 📤 Submission <a id=\"submit\"></a>"))
c.append(submission_cell("Implementation_AI",
    ["trading_cost_drag", "financing_drag", "short_drag", "net_return", "net_sharpe"]))

c.append(md("""---
## 🧠 Key Takeaways <a id="takeaways"></a>
1. **Net = Gross − Costs.** Always report both.
2. **Trading cost ≈ turnover × spread.** A 150%-turnover strategy at 10bp loses 15bp/year base.
3. **Leverage isn't free.** Financing cost on the borrowed dollar eats into the return.
4. **Shorting is asymmetric.** Most names are cheap to short; some (meme stocks) are catastrophically expensive.
5. **AI's backtest will quote gross numbers. You must layer in realistic costs before deploying.**"""))

write_nb("Implementation_AI.ipynb", c)


# ═══════════════════════════════════════════════════════════════════════
# L21 — Machine Learning I (penalized regression)
# ═══════════════════════════════════════════════════════════════════════
c = []
c.append(md("""# Machine Learning I — Predicting Returns with Many Characteristics
## 🎯 Learning Objectives

By the end of this notebook, you will be able to:

1. **Frame return prediction as a regression problem** with many characteristics
2. **Apply Lasso, Ridge, and Elastic Net** for feature selection and shrinkage
3. **Use cross-validation** for hyperparameter tuning without lookahead
4. **Compare ML predictions to the OLS baseline**
5. **Audit AI-generated ML code** — train/test split timing, leakage, hyperparam grids"""))

c.append(md("""## 📋 TOC
1. [Setup](#setup)  2. [The ML Problem in Finance](#problem)
3. [Pitfall Checklist](#pitfalls)  4. [Lasso, Ridge, Elastic Net](#linear)
5. [Cross-Validation Without Lookahead](#cv)  6. [🎯 Challenge: Tune a Predictor](#challenge)
7. [Submission](#submit)  8. [Key Takeaways](#takeaways)"""))

c.append(md("---\n## 🛠️ Setup <a id=\"setup\"></a>"))
c.append(setup_cell())

c.append(md("""---
## The ML Problem in Finance <a id="problem"></a>

You have $N$ stocks, each with $K$ characteristics (B/M, momentum, profitability,
size, idio vol, accruals, ...). You want to predict next-month return.

$$r_{i,t+1} = f(X_{i,t}^{(1)}, X_{i,t}^{(2)}, \\ldots, X_{i,t}^{(K)}) + \\epsilon_{i,t+1}$$

With $K = 100+$ characteristics and $T = 240$ months, naive OLS overfits.
ML methods exist to shrink or select among the K coefficients."""))

c.append(md("""---
## 🛡️ Pitfall Checklist <a id="pitfalls"></a>

| | Pitfall | What goes wrong | 🔍 How to detect |
|---|---------|-----------------|-------------------|
| 1 | **Standard CV with time-series data** | Random k-fold contaminates train with test | Use **walk-forward** or **time-series CV** |
| 2 | **Leakage in feature normalization** | Z-scoring with full-sample mean/std uses future info | Normalize within each cross-section |
| 3 | **Y included in feature engineering** | Computing target-encoded features uses Y → leakage | Audit every feature for Y dependency |
| 4 | **Hyperparameter overfit** | Tuning over 1000 grid points eventually picks one that "works" by chance | Hold out a final test set never seen during tuning |
| 5 | **Reporting in-sample R²** | OLS / Lasso R² always positive. The OOS R² is what matters and can be negative. | Always report OOS metrics |
| 6 | **Sklearn API has surprising defaults** | `Lasso(alpha=1)` is very different from `LassoCV()` | Read the doc; check selected alpha vs the grid endpoints |"""))

c.append(md("""---
## Lasso, Ridge, Elastic Net <a id="linear"></a>

Three penalized regressions:

| Method | Penalty | Effect |
|--------|---------|--------|
| **Ridge** ($L_2$) | $\\lambda \\sum \\beta_j^2$ | Shrinks all coefficients toward zero |
| **Lasso** ($L_1$) | $\\lambda \\sum |\\beta_j|$ | Sets some coefficients exactly to zero (sparse) |
| **Elastic Net** | mix of both | Sparse + stable when features are correlated |

In return prediction, **elastic net** usually wins because financial
features are highly correlated (book-to-market, earnings-to-price, etc.
all measure similar things)."""))

c.append(code("""from sklearn.linear_model import LinearRegression, Lasso, Ridge, ElasticNet
from sklearn.preprocessing import StandardScaler
np.random.seed(42)

# Simulate: 50 features, only 3 actually matter
N, K = 500, 50
X = np.random.normal(0, 1, (N, K))
true_betas = np.zeros(K)
true_betas[[0, 5, 10]] = [0.2, -0.1, 0.15]
y = X @ true_betas + np.random.normal(0, 0.5, N)

# Train/test split
X_train, X_test = X[:400], X[400:]
y_train, y_test = y[:400], y[400:]

# OLS for comparison
ols = LinearRegression().fit(X_train, y_train)
ols_r2 = ols.score(X_test, y_test)

# Penalized methods
lasso = Lasso(alpha=0.05).fit(X_train, y_train)
ridge = Ridge(alpha=1.0).fit(X_train, y_train)
enet  = ElasticNet(alpha=0.05, l1_ratio=0.5).fit(X_train, y_train)

print(f"OOS R²:")
print(f"  OLS:         {ols.score(X_test, y_test):.3f}")
print(f"  Lasso:       {lasso.score(X_test, y_test):.3f}")
print(f"  Ridge:       {ridge.score(X_test, y_test):.3f}")
print(f"  Elastic Net: {enet.score(X_test, y_test):.3f}")
print(f"\\nLasso selected {(lasso.coef_ != 0).sum()} of {K} features.")"""))

c.append(md("""---
## Cross-Validation Without Lookahead <a id="cv"></a>

**Standard k-fold CV is WRONG for time series** because it randomly splits
your data — meaning your training folds can contain *future* data relative
to your validation fold. This gives optimistic OOS estimates.

**Walk-forward CV** instead:
1. Train on months 1-60, validate on month 61
2. Train on months 1-61, validate on month 62
3. ... etc.

Or **time-series CV** with expanding/rolling windows. Sklearn has `TimeSeriesSplit`."""))

c.append(md("""---
## 🎯 Challenge: Tune a Predictor <a id="challenge"></a>

> **Setup.** Using the simulated data above (X, y), find the best regularization
> parameter for Elastic Net via 5-fold CV.

### Q1 — Best alpha for Elastic Net

> **📌 Required:**
> ```python
> from sklearn.linear_model import ElasticNetCV
> enet_cv  = ElasticNetCV(alphas=____, l1_ratio=0.5, cv=5, max_iter=10000).fit(X_train, y_train)
> best_alpha = ____   # enet_cv.alpha_
> ```"""))
c.append(code("""from sklearn.linear_model import ElasticNetCV
alphas_grid = np.logspace(-3, 0, 50)

enet_cv = ElasticNetCV(alphas=alphas_grid, l1_ratio=0.5, cv=5, max_iter=10000).fit(X_train, y_train)
best_alpha = ____    # extract from enet_cv
print(f"Best alpha: {best_alpha:.4f}")"""))

c.append(md("""### Q2 — OOS R² of tuned Elastic Net

> **📌 Required:**
> ```python
> oos_r2 = ____   # enet_cv.score(X_test, y_test)
> ```"""))
c.append(code("""oos_r2 = ____
print(f"OOS R² of tuned ENet: {oos_r2:.3f}")"""))

c.append(md("""### Q3 — Feature selection

How many features did the tuned model select (non-zero coefficient)?

> **📌 Required:**
> ```python
> n_selected = ____    # (enet_cv.coef_ != 0).sum()
> ```"""))
c.append(code("""n_selected = ____
print(f"Selected {n_selected} of {K} features. True nonzero = 3.")"""))

c.append(md("""### Q4 — Memo

Max 5 sentences. Comment on (i) whether ML beat OLS, (ii) whether the tuned
model recovered the 3 true features, (iii) what could go wrong if you applied
this to real return data instead of simulated."""))
c.append(code("""MEMO = \"\"\"Write your memo here.\"\"\"
print(MEMO)"""))

c.append(md("---\n## 📤 Submission <a id=\"submit\"></a>"))
c.append(submission_cell("ML_I_AI",
    ["best_alpha", "oos_r2", "n_selected"]))

c.append(md("""---
## 🧠 Key Takeaways <a id="takeaways"></a>
1. **Penalized regression beats OLS** when you have many correlated features.
2. **Elastic Net usually wins** for finance because features are highly correlated.
3. **Time-series CV is mandatory** for any backtest involving model tuning.
4. **OOS R² is the only honest metric.** In-sample numbers always look good.
5. **AI writes the sklearn boilerplate. You design the train/test split and audit for leakage.**"""))

write_nb("ML_I_AI.ipynb", c)


# ═══════════════════════════════════════════════════════════════════════
# L22 — Machine Learning II (trees, neural nets)
# ═══════════════════════════════════════════════════════════════════════
c = []
c.append(md("""# Machine Learning II — Trees, Forests, and Neural Nets
## 🎯 Learning Objectives

By the end of this notebook, you will be able to:

1. **Apply random forests and gradient boosted trees** for return prediction
2. **Compare tree-based methods to penalized regression** on the same data
3. **Understand the "no free lunch"** — when each method is best
4. **Read feature importance** outputs and avoid misinterpreting them
5. **Audit AI-generated ML code** — tree depth limits, ensemble size, evaluation metrics"""))

c.append(md("""## 📋 TOC
1. [Setup](#setup)  2. [Why Trees](#why)
3. [Pitfall Checklist](#pitfalls)  4. [Random Forest](#rf)
5. [Gradient Boosted Trees](#gbt)  6. [Neural Net Footnote](#nn)
7. [🎯 Challenge: Tree vs Linear](#challenge)
8. [Submission](#submit)  9. [Key Takeaways](#takeaways)"""))

c.append(md("---\n## 🛠️ Setup <a id=\"setup\"></a>"))
c.append(setup_cell())

c.append(md("""---
## Why Trees <a id="why"></a>

Linear methods (OLS, Lasso) assume the relationship between $X$ and $r$ is
linear. In finance, this is often wrong:
- Momentum's effect is non-linear (huge wins for top-decile, modest for mid)
- Size effect saturates (mega-caps and small-caps behave differently)
- Feature interactions matter (value × momentum > value + momentum)

**Trees capture non-linearity and interactions automatically.** Their downside:
prone to overfitting unless you constrain depth or use ensembles."""))

c.append(md("""---
## 🛡️ Pitfall Checklist <a id="pitfalls"></a>

| | Pitfall | What goes wrong | 🔍 How to detect |
|---|---------|-----------------|-------------------|
| 1 | **Unconstrained tree depth** | Trees memorize the training set | Cap depth ≤ 10; require min samples per leaf |
| 2 | **Too few trees in the ensemble** | Random forest needs 100+ trees for stable predictions | Plot performance vs n_estimators |
| 3 | **Feature importance ≠ predictive value** | Importance can be high for noise features in small samples | Compare to a permutation-importance test |
| 4 | **Test set contamination via feature engineering** | Same as Lecture 21 but worse with trees because they're flexible | Build features, then split |
| 5 | **Confusing classification with regression** | Some sklearn calls default to classification when you wanted regression | Always set `RandomForestRegressor` explicitly |"""))

c.append(md("""---
## Random Forest <a id="rf"></a>

A **random forest** is an ensemble of decision trees. Each tree:
1. Is trained on a bootstrap sample of the training set
2. At each split, considers a random subset of features

The prediction is the average across trees. **Key hyperparameters:**
- `n_estimators` — number of trees (100-500 typical)
- `max_depth` — depth of each tree (5-15 typical)
- `min_samples_leaf` — minimum observations per leaf (10-100)"""))

c.append(code("""from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
np.random.seed(42)

# Simulate non-linear: y depends on x1 * x2 + sin(x3)
N, K = 1000, 10
X = np.random.normal(0, 1, (N, K))
y = X[:, 0] * X[:, 1] + np.sin(X[:, 2]) + np.random.normal(0, 0.5, N)

X_tr, X_te = X[:800], X[800:]
y_tr, y_te = y[:800], y[800:]

ols = LinearRegression().fit(X_tr, y_tr)
rf  = RandomForestRegressor(n_estimators=200, max_depth=8, min_samples_leaf=20, random_state=42).fit(X_tr, y_tr)

print(f"OLS OOS R²:  {ols.score(X_te, y_te):.3f}")
print(f"RF  OOS R²:  {rf.score(X_te, y_te):.3f}")
print(f"\\nTrees can detect non-linear/interaction effects OLS cannot.")"""))

c.append(md("""---
## Gradient Boosted Trees <a id="gbt"></a>

**Gradient boosting** builds trees sequentially, where each tree fits the
residual of the previous trees. Better OOS performance than random forest
when tuned correctly, but more prone to overfit.

Modern implementations: **XGBoost, LightGBM, CatBoost** — all fast and well-tested."""))

c.append(code("""from sklearn.ensemble import GradientBoostingRegressor
gbt = GradientBoostingRegressor(n_estimators=200, max_depth=4, learning_rate=0.05).fit(X_tr, y_tr)
print(f"GBT OOS R²: {gbt.score(X_te, y_te):.3f}")"""))

c.append(md("""---
## Neural Net Footnote <a id="nn"></a>

Deep neural nets exist and can outperform trees on huge datasets. For return
prediction, **the data isn't big enough** for neural nets to consistently
beat tree-based methods.

Gu, Kelly & Xiu (2020) is the standard reference — they compared 11 methods
on US stock returns and found GBT and neural nets approximately tied.

> **💡 Practical note**
>
> For 95% of return-prediction problems, **gradient boosted trees** are the
> right default. Use neural nets only if you have lots of data and a clear
> reason to believe the additional flexibility matters."""))

c.append(md("""---
## 🎯 Challenge: Tree vs Linear <a id="challenge"></a>

> **Setup.** Using simulated data with interactions and non-linearity.

### Q1 — OLS baseline

> **📌 Required:**
> ```python
> ols_oos_r2 = ____    # ols.score(X_te, y_te)
> ```"""))
c.append(code("""ols_oos_r2 = ____
print(f"OLS R²: {ols_oos_r2:.3f}")"""))

c.append(md("""### Q2 — Random Forest

> **📌 Required:**
> ```python
> rf_oos_r2 = ____    # rf.score(X_te, y_te) from above
> ```"""))
c.append(code("""rf_oos_r2 = ____
print(f"RF R²: {rf_oos_r2:.3f}")"""))

c.append(md("""### Q3 — GBT

> **📌 Required:**
> ```python
> gbt_oos_r2 = ____   # gbt.score(X_te, y_te) from above
> ```"""))
c.append(code("""gbt_oos_r2 = ____
print(f"GBT R²: {gbt_oos_r2:.3f}")"""))

c.append(md("""### Q4 — Best method
> **📌 Required:**
> ```python
> best_method_r2 = ____   # max of the three R² above
> ```"""))
c.append(code("""best_method_r2 = ____
print(f"Best method R²: {best_method_r2:.3f}")"""))

c.append(md("""### Q5 — Memo

Max 5 sentences. (i) Which method won? (ii) Why does it make sense given the data structure? (iii) What's the risk of using GBT in production?"""))
c.append(code("""MEMO = \"\"\"Write your memo here.\"\"\"
print(MEMO)"""))

c.append(md("---\n## 📤 Submission <a id=\"submit\"></a>"))
c.append(submission_cell("ML_II_AI",
    ["ols_oos_r2", "rf_oos_r2", "gbt_oos_r2", "best_method_r2"]))

c.append(md("""---
## 🧠 Key Takeaways <a id="takeaways"></a>
1. **Trees capture non-linearity and interactions automatically.** OLS / Lasso can't.
2. **Random forests are stable;** gradient boosted trees can be better-tuned but riskier.
3. **Neural nets rarely help in finance** because the data isn't big enough.
4. **Cap tree depth; use ensembles.** Single deep trees overfit catastrophically.
5. **AI fits the model in 3 lines. You design the experiment, choose the metric, and resist over-tuning.**"""))

write_nb("ML_II_AI.ipynb", c)


# ═══════════════════════════════════════════════════════════════════════
# L23 — LLMs in Finance
# ═══════════════════════════════════════════════════════════════════════
c = []
c.append(md("""# LLMs in Finance
## 🎯 Learning Objectives

By the end of this notebook, you will be able to:

1. **Use an LLM to extract structured information** from earnings transcripts and Fed statements
2. **Build a sentiment / tone score** from a 10-K or call transcript
3. **Recognize look-ahead bias** in LLM-based features (training data ends after your "investment date")
4. **Compare LLM-extracted signals** to traditional NLP (dictionary methods)
5. **Audit LLM output** — hallucination, sycophancy, model version sensitivity"""))

c.append(md("""## 📋 TOC
1. [Setup](#setup)  2. [Why LLMs for Finance](#why)
3. [Pitfall Checklist](#pitfalls)  4. [Earnings Call: Tone Extraction](#tone)
5. [FOMC: Hawkish / Dovish](#fomc)  6. [The Look-Ahead Trap](#lookahead)
7. [🎯 Challenge: Score Three Transcripts](#challenge)
8. [Submission](#submit)  9. [Key Takeaways](#takeaways)"""))

c.append(md("---\n## 🛠️ Setup <a id=\"setup\"></a>"))
c.append(setup_cell())

c.append(md("""---
## Why LLMs for Finance <a id="why"></a>

Half of financial information is **text** — earnings calls, 10-Ks, press releases,
Fed statements, news articles. Pre-LLM, extracting structured features from
text required:
- Dictionary methods (Loughran-McDonald sentiment lists)
- Regex parsing
- Naïve Bayes / SVM classifiers

LLMs make this dramatically easier:
- Pass the text, ask a question, get a structured answer
- No training data required for most tasks
- Zero-shot performance on previously hard tasks (entity extraction, summary, tone)

**The catch:** look-ahead bias, hallucination, and prompt sensitivity. We
cover these next."""))

c.append(md("""---
## 🛡️ Pitfall Checklist <a id="pitfalls"></a>

| | Pitfall | What goes wrong | 🔍 How to detect |
|---|---------|-----------------|-------------------|
| 1 | **Training data lookahead** | LLM was trained on 2024 data; you ask it about 2018 events with retrospective knowledge | Always ask "what was known at the time" or use a model frozen before your date |
| 2 | **Entity confusion** | LLM confuses parent company with subsidiary, or two firms with similar names | Specify CIK / ticker; verify the entity in output |
| 3 | **Hallucination** | LLM makes up a CEO name or a number that wasn't in the text | Ground every fact in the source text; reject anything you can't trace back |
| 4 | **Prompt sensitivity** | Rewording the question gives different answers | Run the same prompt 5x; check for consistency |
| 5 | **Sycophancy** | LLM tells you what you want to hear ("Yes, this is bullish") | Always use neutrally-worded prompts; ask for evidence |
| 6 | **Cost at scale** | $0.01/call × 10000 firms × 4 quarters × 30 years = $$$ | Use smaller / faster models for batch; reserve big models for nuance |"""))

c.append(md("""---
## Earnings Call: Tone Extraction <a id="tone"></a>

The classic financial-NLP task: given an earnings call transcript, extract:
- **Tone** (positive / negative / neutral)
- **Forward-looking statements** (guidance, expectations)
- **Surprises** (what's different from last quarter)

Pre-LLM: Loughran-McDonald dictionary count of positive/negative words.
With LLM: pass the transcript and ask.

> **🤖 AI prompt:**
>
> *"Below is a transcript of an earnings call for [TICKER] on [DATE]. Identify:
> (1) the 3 most positive forward-looking statements, (2) the 3 most negative
> or cautious statements, (3) one statement that surprised relative to prior guidance.
> Quote the exact text for each. Do not infer beyond what's stated."*"""))

c.append(md("""---
## FOMC: Hawkish / Dovish <a id="fomc"></a>

Same workflow, different domain. Fed statements are short (1-2 pages) but
each word matters — markets move 5-10 bps off a single word change.

**Hawkish** = more inflation-focused, more likely to raise rates.
**Dovish** = more growth-focused, more likely to cut rates.

LLM can read both the latest statement and the prior one, then highlight
the **differences** in tone — exactly what bond traders do manually."""))

c.append(md("""---
## The Look-Ahead Trap <a id="lookahead"></a>

This is the **most important** pitfall for LLMs in finance:

If you ask GPT-4 about Apple's earnings in Q3 2018, **GPT-4 was trained on
data through 2023**. It knows what happened next.

If you use its analysis to backtest a Q3 2018 trading strategy, you have a
massive lookahead bias.

**Mitigations:**
- Use models with a known cutoff before your data
- Explicitly prompt: "Pretend it's [DATE]. Don't use information from after this date."
- For research, use frozen historical models (some providers offer dated snapshots)

> **⚠️ This is THE bias to watch for**
>
> Every academic paper using LLMs on historical data has to defend against
> this. Many fail to."""))

c.append(md("""---
## 🎯 Challenge: Score Three Transcripts <a id="challenge"></a>

> **Setup.** You have three fake snippets — score each one for tone.
> (In a real workflow you'd pass each to an LLM. For class purposes we provide
> ground-truth scores and have you do the bookkeeping.)

### Q1 — Score each snippet

The snippets are below. Assign each a tone score from -1 (very negative) to +1 (very positive).

> **📌 Required:**
> ```python
> # Snippet 1: "We exceeded guidance by 20%. Customer demand is the strongest in our history."
> # Snippet 2: "We faced material headwinds. Some segments declined double digits. We're rebuilding."
> # Snippet 3: "Revenue was in line. We expect similar growth next quarter."
>
> tone_snippet_1 = ____   # in [-1, 1]
> tone_snippet_2 = ____
> tone_snippet_3 = ____
> ```"""))
c.append(code("""tone_snippet_1 = ____
tone_snippet_2 = ____
tone_snippet_3 = ____
print(f"Snippet 1 tone: {tone_snippet_1:+.2f}")
print(f"Snippet 2 tone: {tone_snippet_2:+.2f}")
print(f"Snippet 3 tone: {tone_snippet_3:+.2f}")"""))

c.append(md("""### Q2 — Composite tone

If you bought all 3 stocks equally, what's the average tone you'd hold?

> **📌 Required:**
> ```python
> avg_tone = ____   # (s1 + s2 + s3) / 3
> ```"""))
c.append(code("""avg_tone = ____
print(f"Average tone: {avg_tone:+.2f}")"""))

c.append(md("""### Q3 — Lookahead check
Suppose your LLM was trained on data through 2024-12. You're applying it
to score 2020 earnings calls. Is there look-ahead risk?

> **📌 Required:**
> ```python
> lookahead_risk = ____    # 1.0 if yes, 0.0 if no
> ```"""))
c.append(code("""lookahead_risk = ____
print(f"Look-ahead risk present? {bool(lookahead_risk)}")"""))

c.append(md("""### Q4 — Memo

Max 5 sentences. State (i) the average tone, (ii) the look-ahead concern,
(iii) one mitigation you'd use in a real backtest."""))
c.append(code("""MEMO = \"\"\"Write your memo here.\"\"\"
print(MEMO)"""))

c.append(md("---\n## 📤 Submission <a id=\"submit\"></a>"))
c.append(submission_cell("LLMs_AI",
    ["tone_snippet_1", "tone_snippet_2", "tone_snippet_3", "avg_tone", "lookahead_risk"]))

c.append(md("""---
## 🧠 Key Takeaways <a id="takeaways"></a>
1. **LLMs make text-feature extraction dramatically easier** — earnings calls, Fed statements, 10-Ks.
2. **Look-ahead bias is THE big risk.** The model knows what happened after your "investment date."
3. **Audit every fact** the LLM gives you against the source text.
4. **Prompt sensitivity is real** — wording matters; consistency-test by re-running.
5. **You direct the LLM. You verify the output. You're responsible for the answer.**"""))

write_nb("LLMs_AI.ipynb", c)


print("\n=== Second batch (L19-L23) complete ===")
