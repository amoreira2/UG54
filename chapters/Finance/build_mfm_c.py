#!/usr/bin/env python3
"""Build MultiFactorModels_c.ipynb — prettified version of MultiFactorModels.ipynb."""
import json, copy, re

with open('MultiFactorModels.ipynb') as f:
    old = json.load(f)

def src_lines(text):
    lines = text.split('\n')
    result = []
    for i, line in enumerate(lines):
        if i < len(lines) - 1:
            result.append(line + '\n')
        else:
            result.append(line)
    if result and result[-1] == '':
        result.pop()
    return result

def mk_md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": src_lines(text)}

def mk_code(text):
    return {"cell_type": "code", "metadata": {}, "source": src_lines(text),
            "execution_count": None, "outputs": []}

def old_code(i):
    """Return old cell i as a clean code cell (no outputs)."""
    c = copy.deepcopy(old['cells'][i])
    c['outputs'] = []
    c['execution_count'] = None
    return c

def old_src(i):
    """Get source text of old cell i."""
    return ''.join(old['cells'][i]['source'])

cells = []

# ============================================================
# SECTION A: Front Matter
# ============================================================

cells.append(mk_md("""# 📘 Multi-Factor Models

---"""))

# Learning objectives — keep from old cell 0, just reformatted
cells.append(mk_md("""## 🎯 Learning Objectives

By the end of this notebook, you will be able to:

1. **Understand why investors move beyond CAPM** — Articulate the limitations of a single-market factor
2. **Estimate multi-factor models** — Regress asset/fund returns on factor portfolios; interpret loadings, alphas, and $R^2$
3. **Evaluate fund performance** — Distinguish genuine alpha from factor exposure using factor regressions
4. **Decompose portfolio risk** — Use both top-down and bottom-up approaches to separate systematic from idiosyncratic components
5. **Estimate factor premia** — Run Fama–MacBeth cross-sectional regressions and interpret characteristic-based risk prices
6. **Construct characteristic-adjusted returns** — Separate skill from style for any portfolio"""))

# TOC
cells.append(mk_md("""## 📋 Table of Contents

1. [Why Multi-Factor Models?](#why-multi-factor)
2. [The Time-Series Approach](#time-series)
3. [Performance Attribution: Cathie Wood](#cathie-wood)
4. [Warren Buffett: Does He Beat the Market?](#warren-buffett)
5. [Bottom-Up vs Top-Down Decomposition](#bottom-up-top-down)
6. [The Cross-Sectional Approach](#cross-sectional)
7. [Exercises](#exercises)
8. [Key Takeaways](#key-takeaways)"""))

# Setup
cells.append(mk_md("""---

## 🛠️ Setup"""))

# pip install + import wrds
cells.append(mk_code("""#@title 🛠️ Setup: Run this cell first (click to expand)

!pip install wrds"""))

cells.append(mk_code("""import wrds"""))

# Main imports + helpers — keep old cell 4 content but add plt style
cells.append(mk_code("""import numpy as np
import pandas as pd
%matplotlib inline
import matplotlib.pyplot as plt
import statsmodels.api as sm
import pandas_datareader.data as web

plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = [10, 6]
plt.rcParams['font.size'] = 12

import warnings
warnings.filterwarnings('ignore')

def get_factors(factors='CAPM', freq='daily'):
    if freq == 'monthly':
        freq_label = ''
    else:
        freq_label = '_' + freq

    if factors == 'CAPM':
        fama_french = web.DataReader("F-F_Research_Data_Factors" + freq_label, "famafrench", start="1921-01-01")
        df_factor = fama_french[0][['RF', 'Mkt-RF']]
    elif factors == 'FF3':
        fama_french = web.DataReader("F-F_Research_Data_Factors" + freq_label, "famafrench", start="1921-01-01")
        df_factor = fama_french[0][['RF', 'Mkt-RF', 'SMB', 'HML']]
    elif factors == 'FF5':
        fama_french = web.DataReader("F-F_Research_Data_Factors" + freq_label, "famafrench", start="1921-01-01")
        df_factor = fama_french[0][['RF', 'Mkt-RF', 'SMB', 'HML']]
        fama_french2 = web.DataReader("F-F_Research_Data_5_Factors_2x3" + freq_label, "famafrench", start="1921-01-01")
        df_factor = df_factor.merge(fama_french2[0][['RMW', 'CMA']], on='Date', how='outer')
    else:
        fama_french = web.DataReader("F-F_Research_Data_Factors" + freq_label, "famafrench", start="1921-01-01")
        df_factor = fama_french[0][['RF', 'Mkt-RF', 'SMB', 'HML']]
        fama_french2 = web.DataReader("F-F_Research_Data_5_Factors_2x3" + freq_label, "famafrench", start="1921-01-01")
        df_factor = df_factor.merge(fama_french2[0][['RMW', 'CMA']], on='Date', how='outer')
        fama_french3 = web.DataReader("F-F_Momentum_Factor" + freq_label, "famafrench", start="1921-01-01")
        df_factor = df_factor.merge(fama_french3[0], on='Date')
        df_factor.columns = ['RF', 'Mkt-RF', 'SMB', 'HML', 'RMW', 'CMA', 'MOM']

    if freq == 'monthly':
        df_factor.index = pd.to_datetime(df_factor.index.to_timestamp())
    else:
        df_factor.index = pd.to_datetime(df_factor.index)

    return df_factor / 100

def get_daily_wrds_multiple_ticker(tickers, conn):
    permnos = conn.get_table(library='crsp', table='stocknames',
                             columns=['permno', 'ticker', 'namedt', 'nameenddt'])
    permnos['nameenddt'] = pd.to_datetime(permnos['nameenddt'])
    permnos = permnos[(permnos['ticker'].isin(tickers)) &
                      (permnos['nameenddt'] == permnos['nameenddt'].max())]
    permno_list = permnos['permno'].unique().tolist()
    print(f"Found PERMNOs: {permno_list}")

    query = f\"\"\"
        SELECT permno, date, ret, retx, prc
        FROM crsp.dsf
        WHERE permno IN ({','.join(map(str, permno_list))})
        ORDER BY date
    \"\"\"
    daily_returns = conn.raw_sql(query, date_cols=['date'])
    daily_returns = daily_returns.merge(permnos[['permno', 'ticker']], on='permno', how='left')
    daily_returns = daily_returns.pivot(index='date', columns='ticker', values='ret')
    daily_returns = daily_returns[tickers]
    return daily_returns

def get_permnos(tickers, conn):
    permnos = conn.get_table(library='crsp', table='stocknames',
                             columns=['permno', 'ticker', 'namedt', 'nameenddt'])
    permnos['nameenddt'] = pd.to_datetime(permnos['nameenddt'])
    permnos = permnos[permnos['ticker'].isin(tickers)]
    return permnos"""))

# ============================================================
# SECTION: Why Multi-Factor Models?
# ============================================================

cells.append(mk_md("""---

## Why Multi-Factor Models? <a id="why-multi-factor"></a>

So far we have focused on the market as our single factor. In practice, it is standard to use models with **many factors**. Additional factors:

- **Soak up risk** — making measures of alpha more precise
- **Difference out** other sources of expected excess returns that are easy to access
- **Allow for better risk management** across multiple dimensions

We extend the single-factor model by adding more regressors. With $m$ factors:

$$r_t^i = b_{i,1} f_t^1 + b_{i,2} f_t^2 + \\cdots + b_{i,m} f_t^m + \\epsilon_{i,t}$$

In matrix notation, stacking all $n$ assets:

$$R_t = B \\cdot F_t + U_t$$

where $B$ is $n \\times m$ (each row = one asset's exposures), $F_t$ is $m \\times 1$ (factor returns), and $U_t$ is the vector of idiosyncratic residuals."""))

cells.append(mk_md("""### "Endogenous" Benchmarking

Large allocators often set benchmarks for managers. The most common is the S&P 500 (≈ market return), but you can also construct **endogenous benchmarks**:

$$r^b_t = \\sum_j \\beta_j F_{j,t}$$

Use the multi-factor combination that best replicates the portfolio as the benchmark. This is typically done implicitly: you allocate to funds based on their **alpha** (hard to get) rather than their beta exposure (cheap to replicate).

> **💡 Key Insight:**
>
> Alpha is scarce; beta is plentiful. You should pay different prices for each.
> The gains from beta are in *implementation* (low cost); the gains from alpha are in *selection* (finding skill)."""))

# ============================================================
# SECTION: Time-Series Approach
# ============================================================

cells.append(mk_md("""---

## Estimating Multi-Factor Models: The Time-Series Approach <a id="time-series"></a>

We start with known factors and estimate betas using time-series regressions. This works especially well when factors are **excess returns** themselves.

For each asset, regress its excess returns on the factor excess returns:

$$r_t^{e,i} = \\alpha_i + \\beta_{i,1} f_t^1 + \\cdots + \\beta_{i,m} f_t^m + \\epsilon_{i,t}$$

### Application: What Do Momentum ETFs Actually Deliver?

We'll take the largest ETFs claiming to implement momentum and see what factor exposures they actually have."""))

# ETF data loading
cells.append(mk_code("""tickers = ["MTUM", "SPMO", "XMMO", "IMTM", "XSMO", "PDP", "JMOM", "DWAS", "VFMO", "XSVM", "QMOM"]
conn = wrds.Connection()

# Get daily returns and factor data
df_ETF = get_daily_wrds_multiple_ticker(tickers, conn)
df_factor = get_factors('FF6', 'daily')

# Align and compute excess returns
df_ETF, df_factor = df_ETF.align(df_factor, join='inner', axis=0)
df_ETF = df_ETF.subtract(df_factor['RF'], axis=0)"""))

# Single regression example
cells.append(mk_code("""# Example: full regression for QMOM
X = sm.add_constant(df_factor.drop(columns=['RF']))
y = df_ETF["QMOM"].dropna()
X = X.loc[y.index]
model = sm.OLS(y, X).fit()
print(model.summary())"""))

# All ETFs regression
cells.append(mk_code("""# Run the regression for all momentum ETFs
Results = pd.DataFrame([], index=tickers, columns=X.columns)
for ticker in tickers:
    y = df_ETF[ticker]
    X = sm.add_constant(df_factor.drop(columns=['RF']))
    X = X[y.isna() == False]
    y = y[y.isna() == False]
    model = sm.OLS(y, X).fit()
    Results.loc[ticker, :] = model.params
    Results.at[ticker, 't_alpha'] = model.tvalues['const']
    Results.at[ticker, 'ivol'] = model.resid.std() * 252**0.5
    Results.at[ticker, 'Sample size'] = y.shape[0] / 252

Results['const'] = Results['const'].astype(float) * 252
Results.rename(columns={'const': 'alpha'}, inplace=True)
Results = Results[['alpha', 't_alpha', 'Mkt-RF', 'SMB', 'HML', 'RMW', 'CMA', 'MOM', 'ivol', 'Sample size']]
Results"""))

cells.append(mk_md("""> **🤔 Think and Code:**
>
> 1. Which fund is "better"? Is it all about alpha in this case?
> 2. What other things should you look at beyond the alpha column?
> 3. Is this table providing a fair comparison, given different sample sizes?"""))

# ============================================================
# SECTION: Performance Attribution — Cathie Wood
# ============================================================

cells.append(mk_md("""---

## Performance Attribution: Cathie Wood <a id="cathie-wood"></a>

Factor models let us **decompose a manager's strategy**: what explains their returns? What tilts do they have? What kind of stocks do they like?

### Application: What Does Cathie Wood Like?

![Cathie Wood](https://github.com/amoreira2/Fin418/blob/main/assets/plots/CW_image.jfif?raw=1)

Cathie Wood is the founder of ARK Invest (~$60B AUM), investing in disruptive technologies — self-driving cars, genomics, AI. She gained fame for spectacular returns and unconventional stock picks."""))

cells.append(mk_code("""df = pd.read_pickle('https://raw.githubusercontent.com/amoreira2/Fin418/main/assets/data/df_WarrenBAndCathieW_monthly.pkl')
_temp = df.drop(['BRK'], axis=1).dropna()

Factors = _temp.drop(['RF', 'ARKK'], axis=1)
ArK = _temp.ARKK - _temp.RF

(ArK + 1).cumprod().plot(title='ARKK Cumulative Excess Return', figsize=(10, 5))
plt.ylabel('Growth of $1')
plt.tight_layout()
plt.show()

print(f"Annualized mean excess return: {ArK.mean()*252:.1%}")"""))

cells.append(mk_md("""The Fama-French factors capture different investment styles:

| Factor | Strategy |
|--------|----------|
| **HML** | Buy high book-to-market (value), sell low (growth) |
| **SMB** | Buy small caps, sell large caps |
| **RMW** | Buy high profitability, sell low profitability |
| **CMA** | Buy low investment (conservative), sell high investment (aggressive) |
| **MOM** | Buy recent winners, sell recent losers |

For now, think of these as important trading strategies that practitioners know well. We'll discuss their economics in detail later."""))

cells.append(mk_code("""# Multi-factor regression (annualized)
x = sm.add_constant(Factors * 252)
y = ArK * 252
results = sm.OLS(y, x).fit()
results.summary()"""))

cells.append(mk_md("""> **🤔 Think and Code:**
>
> 1. How much of ARKK's return behavior can we explain with factors?
> 2. What kind of stocks does Cathie Wood like? (Look at the factor loadings)
> 3. How much portfolio variance comes from market exposure alone vs. being anti-value?
> 4. What would the volatility of the hedged (residual) portfolio be?
> 5. When did she earn her alpha? Is it smooth or concentrated in a few periods?"""))

# ============================================================
# SECTION: Warren Buffett
# ============================================================

cells.append(mk_md("""---

## Warren Buffett: Does He Beat the Market? <a id="warren-buffett"></a>

![Warren Buffett](https://github.com/amoreira2/UG54/blob/main/assets/plots/WB_image.jpg?raw=1)

Warren Buffett is the chairman and CEO of Berkshire Hathaway. His top holdings include Apple, Bank of America, Chevron, Coca-Cola, and American Express. He's known for a long-term, value-oriented approach — large, blue-chip companies with strong balance sheets and attractive valuations.

Let's apply the same factor regression framework to Berkshire Hathaway."""))

cells.append(mk_code("""# Single-factor CAPM regression
BrK = df.BRK - df.RF
x = sm.add_constant(df['Mkt-RF'])
results = sm.OLS(BrK, x).fit()
results.summary()"""))

cells.append(mk_md("""- What do we learn? Is the alpha large economically? Statistically?
- How should we think about this alpha?

Now let's use the full multi-factor model:"""))

cells.append(mk_code("""# Multi-factor regression: FF5 + Momentum
Factors = df.drop(['BRK', 'RF', 'ARKK'], axis=1)
x = sm.add_constant(Factors)
y = df.BRK - df.RF
results = sm.OLS(y, x).fit()
results.summary()"""))

cells.append(mk_md("""> **🤔 Think and Code:**
>
> 1. Did adding factors change the alpha? By how much?
> 2. What kind of stocks does Warren like? (Look at the factor loadings)
> 3. What does this tell us about his investment *style* vs. his stock-picking *skill*?
> 4. How does his profile compare to Cathie Wood's?"""))

# ============================================================
# SECTION: Bottom-Up vs Top-Down
# ============================================================

cells.append(mk_md("""---

## Bottom-Up vs Top-Down Decomposition <a id="bottom-up-top-down"></a>

So far we estimated fund factor exposures by looking at how the fund's returns **co-move** with factors (top-down). An alternative: look *through* the fund at individual holdings (bottom-up).

If a portfolio with weights $X$ earns excess returns $r = X'R$, and each asset satisfies:

$$R = A + B \\cdot F + U$$

then the portfolio satisfies:

$$r = X'A + X'B \\cdot F + X'U$$

So the portfolio's exposure to factor $j$ is the **dollar-weighted average** of the asset betas:

$$\\beta_{p,j} = \\sum_i x_i \\, \\beta_{i,j}$$

> **💡 Key Insight:**
>
> For high-turnover portfolios, the bottom-up approach tracks exposures much better
> because it refreshes at the holding level. For stable portfolios, top-down regressions
> are simpler and avoid the noise of estimating individual-stock betas.

### Sample Portfolio: Tech → Retail Rotation"""))

# Portfolio construction
cells.append(mk_code("""import pandas as pd

date1, date2, date3 = '2014-12-31', '2015-12-31', '2016-12-31'

# Portfolio 1: Tech (2014-2015)
portfolio_data1 = {
    'date': [date1]*5,
    'ticker': ['AAPL', 'GOOGL', 'MSFT', 'NVDA', 'AMZN'],
    'weight': [0.2, 0.2, 0.2, 0.2, 0.2]
}
# Portfolio 2: Retail (2015-2016)
portfolio_data2 = {
    'date': [date2]*4,
    'ticker': ['COST', 'WMT', 'TGT', 'KR'],
    'weight': [0.25, 0.25, 0.25, 0.25]
}

portfolio_df1 = pd.DataFrame(portfolio_data1)
portfolio_df2 = pd.DataFrame(portfolio_data2)

# Expand to daily holdings
date_range1 = pd.date_range(start=date1, end=date2, freq='B')
date_range2 = pd.date_range(start=date2, end=date3, freq='B')

monthly_portfolio1 = pd.DataFrame(
    [(d, t, w) for d in date_range1 for t, w in zip(portfolio_df1['ticker'], portfolio_df1['weight'])],
    columns=['date', 'ticker', 'weight'])
monthly_portfolio2 = pd.DataFrame(
    [(d, t, w) for d in date_range2 for t, w in zip(portfolio_df2['ticker'], portfolio_df2['weight'])],
    columns=['date', 'ticker', 'weight'])

final_portfolio_df = pd.concat([monthly_portfolio1, monthly_portfolio2], ignore_index=True)
final_portfolio_df"""))

cells.append(mk_code("""# Get stock returns and factors
tickers = final_portfolio_df.ticker.unique().tolist()
df_stocks = get_daily_wrds_multiple_ticker(tickers, conn)
df_factor = get_factors('FF6', 'daily').dropna()
df_stocks = df_stocks.subtract(df_factor['RF'], axis=0)"""))

cells.append(mk_code("""# Merge portfolio weights with stock returns
df_merged = df_stocks.stack()
df_merged.name = 'eret'
df_merged = final_portfolio_df.merge(df_merged, left_on=['date', 'ticker'], right_index=True, how='left')
df_merged.head()"""))

# Top-down
cells.append(mk_md("""### Top-Down Approach

Construct the portfolio return first, then run the multi-factor regression:"""))

cells.append(mk_code("""fund_return = df_merged.groupby('date').apply(lambda x: (x['eret'] * x['weight']).sum())
df_factor, fund_return = df_factor.align(fund_return, join='inner', axis=0)"""))

cells.append(mk_code("""# Full-sample regression
y = fund_return.dropna()
X = sm.add_constant(df_factor.drop(columns=['RF']).loc[y.index])
model = sm.OLS(y, X).fit()
model.summary()"""))

cells.append(mk_md("""Now suppose you know the portfolio changed at end-2015. You can break the regression into two windows — but what do you lose in precision?"""))

cells.append(mk_code("""# Period 1: tech portfolio (2014-2015)
y1 = fund_return[:'2015-12-31'].dropna()
X1 = sm.add_constant(df_factor.drop(columns=['RF']).loc[y1.index])
model1 = sm.OLS(y1, X1).fit()
display(model1.summary())

# Period 2: retail portfolio (2016)
y2 = fund_return['2015-12-31':].dropna()
X2 = sm.add_constant(df_factor.drop(columns=['RF']).loc[y2.index])
model2 = sm.OLS(y2, X2).fit()
model2.summary()"""))

# Abnormal returns
cells.append(mk_md("""### Strategy Abnormal Returns

Armed with betas, we construct abnormal returns by stripping out factor-explained performance:

$$\\text{Abnormal}_t = R_t - \\sum_j \\beta_j \\, f_t^j$$"""))

cells.append(mk_code("""abnormal_return = fund_return - df_factor.drop(columns=['RF']) @ model.params[1:]

fig, ax = plt.subplots(figsize=(10, 5))
fund_return.cumsum().plot(ax=ax, label='Fund return')
abnormal_return.cumsum().plot(ax=ax, label='Abnormal return')
ax.set_title('Fund vs. Abnormal Cumulative Returns')
ax.legend()
plt.tight_layout()
plt.show()"""))

cells.append(mk_md("""> **🤔 Think and Code:**
>
> 1. How can you compute abnormal returns more easily from regression outputs?
>    *Hint:* which regression statistic equals the average abnormal return?
> 2. What does the pattern of abnormal returns tell you about the fund's skill?"""))

# Bottom-up
cells.append(mk_md("""### Bottom-Up Approach

Now we estimate factor betas for each *stock*, then use portfolio weights to compute fund exposures date-by-date:"""))

cells.append(mk_code("""# Estimate factor betas for each stock
df_factor, df_stocks = df_factor.align(df_stocks, join='inner', axis=0)
Xf = df_factor.drop(columns=['RF'])

B = pd.DataFrame([], index=tickers, columns=Xf.columns)
for ticker in df_stocks.columns:
    y = df_stocks[ticker].dropna()
    X = sm.add_constant(Xf.loc[y.index])
    model = sm.OLS(y, X).fit()
    B.loc[ticker, :] = model.params[1:]

B"""))

cells.append(mk_md("""With individual betas in hand, we can compute **fund-level exposures date by date** using current portfolio weights. This matters a lot for funds that trade frequently:"""))

cells.append(mk_code("""_temp = final_portfolio_df.merge(B, left_on='ticker', right_index=True, how='left')
Fund_B = _temp.groupby('date').apply(
    lambda x: pd.Series((x[Xf.columns].values * x['weight'].values.reshape(-1, 1)).sum(axis=0), index=Xf.columns))

Fund_B.plot(title='Fund Factor Exposures Over Time', figsize=(10, 5))
plt.ylabel('Beta')
plt.tight_layout()
plt.show()

Fund_B"""))

cells.append(mk_md("""> **📌 Remember:**
>
> There is no reason to believe asset betas are stable over time. The general recipe:
> - **Daily data**: 1–2 year estimation windows
> - **Monthly data**: ~5 year windows
>
> Long samples give precision if betas are constant; short samples capture time-variation."""))

# ============================================================
# SECTION: Cross-Sectional Approach
# ============================================================

cells.append(mk_md("""---

## The Cross-Sectional Approach <a id="cross-sectional"></a>

In the time-series approach, we start from *factors* and estimate betas. Now we **flip this**: start from *characteristics* (which are the betas) and estimate the returns associated with each characteristic.

### Time-Series vs. Cross-Sectional

| | Time-Series | Cross-Sectional |
|---|---|---|
| **Starts from** | Factor returns | Asset characteristics |
| **Estimates** | Betas (loadings) | Factor premia (returns to characteristics) |
| **Requires** | Traded factors | Large cross-section of stocks |
| **Best for** | Small number of well-defined factors | Many characteristics simultaneously |

### The Recipe

1. Get excess returns $R$ for all stocks at date $t$
2. Get characteristics $X$ for those stocks as of date $t-1$ (to avoid look-ahead bias!)
3. Normalize characteristics cross-sectionally (z-scores)
4. Run the cross-sectional regression: $R = X \\beta + \\epsilon$

From OLS: $\\beta = (X'X)^{-1}X'R$

> **💡 Key Insight:**
>
> The $\\beta$ coefficients are **excess returns themselves** — they are returns on
> "pure play" portfolios designed to have a loading of 1 on one characteristic
> and zero on all others. The weights $(X'X)^{-1}X'$ are the portfolio weights."""))

cells.append(mk_code("""# Load characteristics data
url = "https://github.com/amoreira2/Fin418/blob/main/assets/data/characteristics_raw.pkl?raw=true"
df_X = pd.read_pickle(url)
# Shift dates to end-of-month basis
df_X.set_index(['date', 'permno'], inplace=True)
df_X.head()"""))

cells.append(mk_code("""# Standardize characteristics cross-sectionally (z-scores by date)
X_std = (df_X.drop(columns=['re', 'rf', 'rme'])
         .groupby('date')
         .transform(lambda x: (x - x.mean()) / x.std()))"""))

cells.append(mk_code("""# Run the cross-sectional regression for a single month
date = '2006-09'
X = X_std.loc[date]
R = df_X.loc[date, 're']

# Multiply by 100 for percentage returns
model = sm.OLS(100 * R, X).fit()
print(model.summary())"""))

cells.append(mk_md("""**What does this mean?**

- The size coefficient means a portfolio with one standard deviation of size exposure (and zero of everything else) earned that return in this month
- Because we normalized, "one unit" means one cross-sectional standard deviation above the mean

What are the portfolios behind these coefficients?"""))

cells.append(mk_code("""# Portfolio weights for each characteristic "pure play"
# Rows = characteristics, columns = stocks
Characteristic_portfolio_weights = np.linalg.inv(X.T @ X) @ X.T
Characteristic_portfolio_weights.index = X.columns
Characteristic_portfolio_weights"""))

cells.append(mk_md("""### Applications

With these cross-sectional regressions we can:

1. **Compute characteristic-adjusted returns** for any portfolio — just subtract the returns implied by its characteristics
2. **Construct factor return time-series** — splice together the regression coefficients across dates to get $[\\beta_t, \\beta_{t+1}, \\ldots]$"""))

# Characteristic-adjusted returns
cells.append(mk_md("""### Constructing Characteristic-Adjusted Returns

We can get a portfolio's characteristics and compute the returns *implied* by those characteristics. Subtracting these from actual returns gives the **characteristic-adjusted return** — the equivalent of "hedging" but using characteristics instead of time-series betas."""))

cells.append(mk_code("""# Step 1: Define two sample portfolios (tech and retail)
portfolio_data1 = {'port': [1]*5,
    'ticker': ['AAPL', 'GOOG', 'MSFT', 'NVDA', 'AMZN'],
    'weight': [0.2, 0.2, 0.2, 0.2, 0.2]}

portfolio_data2 = {'port': [2]*4,
    'ticker': ['COST', 'WMT', 'TGT', 'KR'],
    'weight': [0.25, 0.25, 0.25, 0.25]}

portfolio_df = pd.concat([pd.DataFrame(portfolio_data1), pd.DataFrame(portfolio_data2)], ignore_index=True)
print(portfolio_df)"""))

cells.append(mk_code("""# Step 2: Get PERMNOs for ticker matching (our data uses PERMNOs, not tickers)
permno = get_permnos(portfolio_df.ticker.unique(), conn)
permno['namedt'] = pd.to_datetime(permno['namedt'])
permno['nameenddt'] = pd.to_datetime(permno['nameenddt'])

date = '2008-03'
d = pd.to_datetime(date)
# Get PERMNOs valid at this date (they can change over time!)
permno_d = permno[(permno['nameenddt'] >= d) & (permno['namedt'] <= d)]
portfolio_df = portfolio_df.merge(permno_d[['permno', 'ticker']], on='ticker', how='left')
portfolio_df"""))

cells.append(mk_code("""# Step 3: Merge portfolio with characteristics data
# Here we do it for one date; for multiple dates, add 'date' as a second identifier
X = X_std.loc[date].reset_index()
port_stocks_X = portfolio_df.merge(X, left_on='permno', right_on='permno', how='left')
port_stocks_X"""))

cells.append(mk_code("""# Step 4: Compute portfolio-level characteristics (weighted average)
X_names = X.drop(columns=['permno', 'date']).columns
port_X = port_stocks_X.groupby('port').apply(lambda x: x['weight'] @ x[X_names])
port_X"""))

cells.append(mk_code("""# Step 5: Estimate returns associated with each characteristic (full universe)
X = X_std.loc[date]
R = df_X.loc[date, 're']
model = sm.OLS(R, X).fit()
R_X = model.params
R_X"""))

cells.append(mk_code("""# Step 6: Characteristic-implied returns
# This is the equivalent of sum(beta_j * f_j), but using characteristics as "betas"
# and the cross-sectional regression coefficients as "factors"
port_characteristic_returns = port_X[X_names] @ R_X
print("Characteristic-implied returns:")
print(port_characteristic_returns)"""))

cells.append(mk_code("""# Step 7: Characteristic-adjusted returns = actual - implied
_temp = portfolio_df.merge(R.reset_index(), left_on='permno', right_on='permno')
R_port = _temp.groupby('port').apply(lambda x: x['weight'] @ x['re'])

print("Raw excess returns:")
print(R_port)
print("\\nCharacteristic-implied returns:")
print(port_characteristic_returns)
print("\\nCharacteristic-adjusted returns:")
print(R_port - port_characteristic_returns)"""))

# Pros and cons
cells.append(mk_md("""### Why Practitioners Like This

- **No time-series betas needed** — avoids all the issues with sample length and beta instability
- **Characteristics can change freely** — we estimate date-by-date, so the model adapts instantly
- **Scales to many factors** — just add columns to the regression (sector, country, currency, etc.)

### What Are the Issues?

- **Ignores covariances** — characteristic-neutral ≠ factor-neutral. A stock classified as "retail" might co-move with tech
- **Loads on small stocks** — OLS treats all observations equally, and most stocks are tiny. Fixes: weighted least squares (by market cap), or restrict to the largest 20% of stocks

> **⚠️ Caution:**
>
> The characteristic and factor-based approaches are **complements, not substitutes**.
> Characteristics are observable and easy to work with, but factors capture the
> actual return co-movement structure. Use both."""))

# ============================================================
# SECTION: Exercises
# ============================================================

cells.append(mk_md("""---

## 📝 Exercises <a id="exercises"></a>"""))

cells.append(mk_md("""### Exercise 1: Factor Attribution

> **🔧 Exercise:**
>
> Pick a fund or ETF of your choice (e.g., QQQ, XLF, ARKW).
> 1. Download its daily returns from WRDS
> 2. Run a multi-factor regression (FF5 + Momentum)
> 3. Report: alpha, t-stat, $R^2$, and the dominant factor exposures
> 4. In 2-3 sentences: what is this fund actually giving you?"""))

cells.append(mk_code("""# Your code here"""))

cells.append(mk_md("""### Exercise 2: Bottom-Up vs Top-Down

> **🤔 Think and Code:**
>
> Using the Tech → Retail portfolio from above:
> 1. Compare the fund betas from the top-down regression (full sample) to the bottom-up approach
> 2. Where do the biggest discrepancies appear? Why?
> 3. Which approach would you trust more for a high-turnover hedge fund?"""))

cells.append(mk_code("""# Your code here"""))

cells.append(mk_md("""### Exercise 3: Cross-Sectional Factors

> **🤔 Think and Code:**
>
> 1. Run the cross-sectional regression for 3 different months (e.g., a boom, a crash, and a calm period)
> 2. How stable are the characteristic premia across months?
> 3. Which characteristic has the most volatile premium? What might explain that?"""))

cells.append(mk_code("""# Your code here"""))

# ============================================================
# Key Takeaways
# ============================================================

cells.append(mk_md("""---

## 🧠 Key Takeaways <a id="key-takeaways"></a>

- **Multi-factor models are the industry workhorse.** They capture multiple rewarded risks simultaneously, delivering more realistic benchmarks and richer performance attribution.

- **Alpha is scarce; beta is plentiful.** Time-series regressions reveal that most "smart-beta" ETFs provide factor exposure, not outperformance — true skill shows up only in the intercept.

- **Bottom-up attribution excels for high-turnover managers.** Refreshing exposures at the holding level avoids the lag and instability that afflict purely return-based estimates.

- **Characteristic models broaden the toolkit but ignore covariances.** They neutralize portfolios on observed attributes quickly and at scale, yet leave hidden co-movement risks untouched — factor and characteristic views are complements, not substitutes.

---"""))


# ============================================================
# Build the notebook
# ============================================================

nb = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.11.0"
        }
    },
    "cells": cells
}

outpath = 'MultiFactorModels_c.ipynb'
with open(outpath, 'w') as f:
    json.dump(nb, f, indent=1)

print(f"Wrote {len(cells)} cells to {outpath}")
