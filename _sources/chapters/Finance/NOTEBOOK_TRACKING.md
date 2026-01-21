# Notebook Revamp Tracking

This file tracks new libraries and concepts introduced in each revamped notebook.

---

## 1. IntrotoReturns_c.ipynb — "Introduction to Asset Returns"

### Libraries Introduced
| Library | First Used | Description |
|---------|------------|-------------|
| `numpy` | Setup | Numerical computing (arrays, math operations) |
| `pandas` | Setup | Data manipulation and analysis (DataFrames) |
| `matplotlib` | Setup | Plotting and visualization |

### Concepts Introduced
- Total return formula: $R_t = (P_t + D_t - P_{t-1}) / P_{t-1}$
- Excess returns: $R^e = R - R^f$
- Risk premium: $E[R^e]$
- Sharpe Ratio: Risk premium / Volatility
- Annualization: Mean × 252, Std × √252 (daily to annual)
- Cumulative returns via `.cumprod()`

---

## 2. TheChoiceofFrequency_c.ipynb — "The Choice of Frequency and Annualization of Returns"

### Libraries Introduced
*No new libraries — uses core libraries from notebook 1*

### 🐍 Python Functions Introduced
| Function | Description |
|----------|-------------|
| `df.groupby()` | Split-Apply-Combine pattern for aggregating data by groups |
| `.prod()` | Product of values (used with groupby for compounding returns) |
| `.index.year` | Extract year from DatetimeIndex for grouping |
| `.index.to_period('Q')` | Convert to quarterly period for grouping |

### Concepts Introduced
- Frequency choices (daily, monthly, annual)
- Standard annualization formulas:
  - Mean: $\mu_A = 12 \times \mu_M$
  - Std: $\sigma_A = \sqrt{12} \times \sigma_M$
- Why approximation works (and when it doesn't)
- Exact aggregation with `groupby().prod()`
- Compounding: $(1+R_1)(1+R_2)\cdots - 1$

---

## 3. UsingAPI_c.ipynb — "Data APIs"

### Libraries Introduced
| Library | First Used | Description |
|---------|------------|-------------|
| `fredapi` | FRED section | Python wrapper for Federal Reserve Economic Data API. Downloads macro/financial time series directly into pandas. |
| `pytrends` | Google Trends section | Unofficial Google Trends API. Scrapes search interest data for keywords over time. |
| `wallstreet` | WallStreet section | Real-time stock and options data. Provides current prices and historical data without API key. |
| `pandas_datareader` | Ken French section | Connects to multiple financial data sources. Key feature: access to Ken French's 297 factor datasets. |
| `wrds` | WRDS section | Official Python interface for WRDS (Wharton Research Data Services). Requires academic account. |
| `psycopg2` | WRDS section | PostgreSQL adapter needed for WRDS database connections. |

### Concepts Introduced
- API keys and authentication
- Alternative data (Google Trends as sentiment proxy)
- Ken French data library structure (multiple tables per dataset)
- SQL queries for WRDS
- CRSP variables: `ret`, `prc`, `shrout`, `vol`

---

## 4. FactorModels_c.ipynb — "Factor Models"

### Libraries Introduced
| Library | First Used | Description |
|---------|------------|-------------|
| `statsmodels` | Regression section | Statistical modeling library for Python. Provides OLS regression, hypothesis testing, and model diagnostics. We use `statsmodels.api` and `statsmodels.formula.api` for running factor regressions. |

### Concepts Introduced
- Factor model equation: $r^e = \alpha + \beta \cdot f + \epsilon$
- Alpha ($\alpha$): Asset-specific return (skill/mispricing)
- Beta ($\beta$): Sensitivity to factor
- Risk models vs Expected return models
- Tracking portfolio: $\beta \times f$ (replicates factor exposure)
- Hedged portfolio (portable alpha): $r^e - \beta \cdot f = \alpha + \epsilon$
- Variance decomposition: $\text{Var}(r^e) = \beta^2 \text{Var}(f) + \text{Var}(\epsilon)$
- Risk budgets and position sizing: $x = \text{budget} / \sigma$
- Sharpe Ratio: $E[r^e] / \sigma(r^e)$
- Appraisal Ratio: $\alpha / \sigma(\epsilon)$ (Sharpe of hedged portfolio)
- R-squared as factor risk share

---

## 5. MarketTiming_c.ipynb — "Expected Returns Timing"

### Libraries Introduced
*No new libraries — uses `statsmodels` (from notebook 4) with HAC standard errors*

### Concepts Introduced
- Return predictability: Why dividend yields might forecast stock returns
- Forecasting regressions: $r_{t+h} = a + b \cdot \text{signal}_t + u_{t+h}$
- Overlapping returns problem and HAC (Newey-West) correction
- Out-of-sample R²: $R^2_{OOS} = 1 - \frac{\sum(r - \hat{r})^2}{\sum(r - \mu_{benchmark})^2}$
- Estimation vs test sample split
- Timing strategy weights: $x_t = \frac{\mu_t}{\gamma \sigma^2}$
- Evaluating timing with alpha (same-beta benchmark)
- Persistent signals and effective sample size

---

## 6. Volatilitytiming_c.ipynb — "Volatility Timing"

### Libraries Introduced
*No new libraries — uses core libraries*

### Concepts Introduced
- Mean-variance optimal weight: $x_t = \frac{E_t[r^e]}{\gamma \cdot \text{Var}_t(r^e)}$
- Realized variance from daily data: $RV_t = \sum (r_d - \bar{r})^2 / N$
- Price of risk: $E[r]/\text{Var}(r)$ and how it varies with volatility
- Volatility-managed portfolios: $w_t = c / RV_t$
- Lagging signals to avoid look-ahead bias
- Leverage constraints in practice
- Variance scaling vs volatility scaling
- Moreira & Muir (2017) reference

---

## 7. PortfolioMath_c.ipynb — "Portfolios"

### Libraries Introduced
*No new libraries — uses core libraries from notebook 1*

### 🐍 Python Functions Introduced
| Function | Description |
|----------|-------------|
| `@` operator | Matrix multiplication / dot product |
| `df.cov()` | Compute covariance matrix of DataFrame columns |
| `np.ones()` | Create array of ones (used for equal weights) |

### Concepts Introduced
- Portfolio weights: $w_j = \text{Dollars in } j / \text{Total value}$
- Weights sum to 1: $\sum w_j = 1$ or $\mathbf{1}'W = 1$
- Portfolio return: $R_p = W'R$
- Portfolio expected return: $E[R_p] = W'E[R]$
- Portfolio variance: $\text{Var}(R_p) = W'\Sigma W$
- Diversification benefits with imperfect correlation
- Mean-variance frontier
- Long-only vs short vs leveraged positions

---

## 8. linear_algebra1_c.ipynb — "Linear Algebra Review" (scientific folder)

### Libraries Introduced
*No new libraries — uses NumPy*

### 🐍 Python Functions Introduced
| Function | Description |
|----------|-------------|
| `np.eye()` | Create identity matrix |
| `np.linalg.inv()` | Compute matrix inverse |
| `.T` or `.transpose()` | Matrix transpose |

### Concepts Introduced
- Vectors as 1D arrays, matrices as 2D arrays
- Element-wise vs scalar operations
- Dot product: $x \cdot y = \sum x_i y_i$
- Matrix multiplication and shape compatibility
- Transpose: $A^T_{ij} = A_{ji}$
- Identity matrix: $AI = IA = A$
- Inverse: $AA^{-1} = I$
- Solving linear systems: $x = A^{-1}b$

---

## 9. CapitalAllocationI_c.ipynb — "Capital Allocation"

### Libraries Introduced
*No new libraries — uses core libraries + statsmodels (from notebook 4)*

### 🐍 Python Functions Introduced
| Function | Description |
|----------|-------------|
| `np.linalg.inv()` | Matrix inverse (used for MVE portfolio weights) |
| `sm.OLS().fit()` | Ordinary Least Squares regression fitting |

### Concepts Introduced
- Capital allocation problem: Allocate wealth between risky and risk-free assets
- Quadratic utility: $u(W) = W - \frac{\gamma}{2} W^2$
- Optimal risky asset weight: $x^* = \frac{E[r^e]}{\gamma \cdot \text{Var}(r)}$
- Mean-variance efficient (MVE) portfolio: $W^* = \frac{1}{\gamma} \Sigma^{-1} E[r^e]$
- Two-fund separation: All investors hold same risky portfolio, just different amounts
- "All you need is Sharpe": MVE portfolio maximizes Sharpe ratio
- Alpha bets: Deviations from benchmark based on stock-specific views
- Portable alpha: $r_{\text{hedged}} = \alpha + \epsilon$ (market-neutral alpha extraction)
- Factor regression for hedge ratio: Estimate $\beta$ to construct market-neutral position

---

## Progress Tracker

| # | Notebook | Status | Date |
|---|----------|--------|------|
| 1 | IntrotoReturns_c.ipynb | ✅ Complete | Jan 2026 |
| 2 | TheChoiceofFrequency_c.ipynb | ✅ Complete | Jan 2026 |
| 3 | UsingAPI_c.ipynb | ✅ Complete | Jan 2026 |
| 4 | FactorModels_c.ipynb | ✅ Complete | Jan 2026 |
| 5 | MarketTiming_c.ipynb | ✅ Complete | Jan 2026 |
| 6 | Volatilitytiming_c.ipynb | ✅ Complete | Jan 2026 |
| 7 | PortfolioMath_c.ipynb | ✅ Complete | Jan 2026 |
| 8 | linear_algebra1_c.ipynb | ✅ Complete | Jan 2026 |
| 9 | CapitalAllocationI_c.ipynb | ✅ Complete | Jan 2026 |
| 10 | FactorModelEstimation_c.ipynb | ⏳ Pending | - |
| 11 | Timing_c.ipynb | ✅ Complete | Jan 2026 |
| 12 | crosssectionalequitystrategies_c.ipynb | ⏳ Pending | - |
| 13 | Momentum_c.ipynb | ⏳ Pending | - |
| 14 | Factors_c.ipynb | ⏳ Pending | - |
| 15 | CapitalAllocationII_c.ipynb | ⏳ Pending | - |
| 16 | Performance_evaluation_c.ipynb | ⏳ Pending | - |
| 17 | MachineLearning_c.ipynb | ⏳ Pending | - |
| 18 | MultiFactorModels_c.ipynb | ⏳ Pending | - |
| 19 | InterpretingFactorModels_c.ipynb | ⏳ Pending | - |
| 20 | RiskManagement_c.ipynb | ⏳ Pending | - |
| 21 | TradingCosts_c.ipynb | ⏳ Pending | - |
| 21 | LeverageandShorting_c.ipynb | ⏳ Pending | - |
| 22 | LLMs_c.ipynb | ⏳ Pending | - |
