# Builds the two Conditional Strategies notebooks. Concepts live in the slides; code lives here.
#   python chapters/Finance/build_conditional_strategies_notebooks.py
# Overwrites both notebooks. If a notebook was edited by hand, port the edit here first.
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
FORM = "https://forms.gle/yazZ8bbatL87jdJi7"


def build(fname, prefix, cells):
    out = []
    for k, (kind, src) in enumerate(cells):
        lines = src.strip('\n').split('\n')
        cell = {"cell_type": kind, "id": f"{prefix}-{k:02d}", "metadata": {},
                "source": [l + '\n' for l in lines[:-1]] + [lines[-1]]}
        if kind == 'code':
            cell.update(execution_count=None, outputs=[])
        out.append(cell)
    nb = {"cells": out,
          "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                       "language_info": {"name": "python"}},
          "nbformat": 4, "nbformat_minor": 5}
    with open(OUT / fname, 'w') as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
        f.write('\n')
    print('wrote', fname, len(out), 'cells')


def submission(required, assignment):
    return f'''
# === 📤 SUBMISSION CELL — Run this last ===
import json, base64, hashlib, datetime as dt

required = {required!r}
missing = [v for v in required if v not in globals()]
if missing:
    raise NameError(f"\\n❌ Missing before submission: {{missing}}")

payload = {{
    "assignment": "{assignment}",
    "ts": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
    "answers": {{k: float(eval(k)) for k in required if k != "MEMO"}},
    "memo": MEMO.strip(),
}}
blob = json.dumps(payload, sort_keys=True)
checksum = hashlib.sha256(blob.encode()).hexdigest()[:8]
token = f"UG54::{{checksum}}::{{base64.b64encode(blob.encode()).decode()}}"

print("=" * 72)
print("📋  COPY THE LINE BELOW AND PASTE INTO THE SUBMISSION FORM")
print("=" * 72)
print(token)
print("=" * 72)
print("Submission form: {FORM}")
'''


MEMO_CELL = '''
MEMO = """
Write your answer here. Don't delete the surrounding triple quotes.
"""
print(MEMO)
'''


def slides(n, title):
    return f"""
📑 **Slides for this class:** [{title} (PDF)](https://amoreira2.github.io/UG54/slides/conditional_strategies_{n}.pdf)

<iframe src="../../slides/conditional_strategies_{n}.pdf" width="100%" height="520" style="border: 1px solid #ddd;"></iframe>
"""


# ═══════════════════════════════════════════════════════════════════ CONDITIONAL STRATEGIES I: TIMING RISK
cs1 = [
('markdown', """
# Conditional Strategies I: Timing Risk

The ideas are in the slides. Here you measure volatility from daily data, check whether it predicts returns, and build the
volatility-managed version of the market, of the other five factors, and of the best mix of all six.

**The plan**, one section per exercise in the slides

1. Realized variance from daily returns
2. 🎯 Sort the months by last month's volatility
3. 🎯 The volatility-managed market: your turn
4. All six factors
5. 🎯 Time the best mix. Then back to the slides
6. 🎯 Challenge (homework): one number and three sentences
"""),
('markdown', slides(1, "Conditional Strategies I")),
('code', """
#@title Setup — run this first
import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt
%matplotlib inline
plt.rcParams['figure.figsize'] = [11, 4]
import warnings; warnings.filterwarnings('ignore')

BASE = "https://raw.githubusercontent.com/amoreira2/UG54/refs/heads/main/assets/data"

mkt = pd.read_parquet(f"{BASE}/factors_daily_1926.parquet")['Mkt-RF']   # daily market excess return, from 1926
D   = pd.read_parquet(f"{BASE}/ff6_daily_1963.parquet")      # daily excess returns on the six factors, from 1963

sharpe = lambda x: x.mean() / x.std() * np.sqrt(12)        # annualized Sharpe ratio of a monthly series

print(f"market:      {mkt.index[0]:%Y-%m-%d} to {mkt.index[-1]:%Y-%m-%d}, {len(mkt):,} days")
print(f"six factors: {D.index[0]:%Y-%m-%d} to {D.index[-1]:%Y-%m-%d}, {len(D):,} days")
print(D.columns.tolist())
"""),
('markdown', """
---

## 1. Realized variance from daily returns

A month has about 21 trading days. Their spread tells you how risky the month was: add up the squared deviations of the
daily returns from their average. That is the month's **realized variance**. Square root, times $\\sqrt{12}$, and you have a
volatility a year.

We need two things for each month: its return, and last month's realized variance, which you know before the month starts.
"""),
('code', """
daily = mkt                                                 # start with the market, 1926-2026

month = daily.index + pd.offsets.MonthEnd(0)                # label each day with the last day of its month
rv = daily.groupby(month).apply(lambda x: ((x - x.mean()) ** 2).sum())   # realized variance of each month
r  = (1 + daily).groupby(month).prod() - 1                  # the month's return: compound its days

M = pd.DataFrame({'r': r, 'rv': rv})
M['rv_lag'] = M['rv'].shift(1)                              # LAST month's variance: known when this month starts
M = M.dropna()

vol = np.sqrt(M['rv'] * 12)                                 # volatility, a year
vol.plot(title='realized volatility of the market, a year'); plt.show()

print(f"median volatility {vol.median():.1%}, highest {vol.max():.1%} in {vol.idxmax():%Y-%m}")
print(f"correlation of this month's volatility with last month's: {np.corrcoef(np.log(M.rv), np.log(M.rv_lag))[0, 1]:.2f}  (logs)")
print(f"correlation of this month's RETURN with last month's volatility: {np.corrcoef(M.r, M.rv_lag)[0, 1]:.3f}")
"""),
('markdown', """
- Find the four highest spikes on the plot. Which events are they?
- One correlation is large and one is about zero. Which is which, and why is that the whole idea of today?
- Why `shift(1)`? What would go wrong without it?
"""),
('markdown', """
---

## 2. 🎯 Sort the months by last month's volatility

Put the months in five groups, from the calmest last month to the most volatile, and look at what happened *next*.
The full sample, 1926–2026: the same months as the slides.
"""),
('code', """
group = pd.qcut(M['rv_lag'], 5, labels=['1 calm', '2', '3', '4', '5 volatile'])   # five equal groups of months

table = pd.DataFrame({
    'volatility next month': M['r'].groupby(group).std() * np.sqrt(12),
    'return next month':     M['r'].groupby(group).mean() * 12,
})
table['Sharpe ratio next month'] = table['return next month'] / table['volatility next month']
print(table.round(3).to_string())

table.plot.bar(subplots=True, layout=(1, 3), figsize=(13, 3.5), legend=False, rot=0); plt.show()
"""),
('markdown', """
- After a volatile month, is the next month riskier? Is it more rewarding?
- If the return rose one for one with the variance, what would the Sharpe ratio column look like? What does it look like?
- Rerun the sort on `M.loc['1963':]`, the years of the next sections. Is the pattern as clear?
"""),
('markdown', """
---

## 3. 🎯 The volatility-managed market

Hold less after a volatile month: the weight is $c / \\text{RV}_{t-1}$. The constant $c$ only sets the scale. We pick it so
the managed strategy is exactly as volatile as the market, so the two can be compared directly.

From here on we use **1963–2026**, the years we have for all six factors, so the market can be compared with the others
in sections 4 and 5. `M63` is `M` from August 1963, the same months as those sections.

Three steps. The first is done for you.

1. `w_raw = 1 / M63['rv_lag']`
2. `c`: the market's volatility divided by the volatility of `w_raw * M63['r']`. Use `.std()` on each
3. `managed`: this month's return on the position, `c * w_raw * M63['r']`
"""),
('code', """
# === YOUR TURN ===
M63 = M.loc['1963-08':]           # the same months as sections 4-5: their data start July 1963, and July has no last month

w_raw = 1 / M63['rv_lag']         # step 1: less weight after a volatile month

c       = ____                    # step 2
managed = ____                    # step 3
"""),
('code', """
#@title 🔒 Check: the volatility-managed market
w_ref = 1 / M63['rv_lag']
c_ref = M63['r'].std() / (w_ref * M63['r']).std()
mgd   = c_ref * w_ref * M63['r']
weight = c_ref * w_ref                                      # the weight on the market each month

try:
    print("yours matches" if np.allclose(managed, mgd) else "yours differs: compare with the numbers below", "\\n")
except Exception as e:
    print("yours: not built yet:", type(e).__name__, "\\n")

fit = sm.OLS(mgd, sm.add_constant(M63['r'])).fit()         # managed return on the market's
print(f"market            Sharpe {sharpe(M63['r']):.2f}   volatility {M63['r'].std() * np.sqrt(12):.1%}")
print(f"managed           Sharpe {sharpe(mgd):.2f}   volatility {mgd.std() * np.sqrt(12):.1%}")
print(f"alpha on the market {fit.params['const'] * 12:.1%} a year, t = {fit.tvalues['const']:.1f}\\n")

for a, b in [('1963', '1979'), ('1980', '2014'), ('2015', '2026')]:
    print(f"{a}-{b}: market {sharpe(M63['r'].loc[a:b]):.2f}, managed {sharpe(mgd.loc[a:b]):.2f}")

print(f"\\nweight: median {weight.median():.2f}, largest {weight.max():.1f} in {weight.idxmax():%Y-%m}, above 2 in {np.mean(weight > 2):.0%} of months")
weight.plot(logy=True, title='weight on the market'); plt.axhline(1, color='k', lw=0.5); plt.show()
"""),
('markdown', """
- Same volatility, so the Sharpe ratios can be compared directly. Did timing help the market since 1963?
- Look at the weights. What would you need to run this, and what would your risk manager say?
"""),
('markdown', """
---

## 4. All six factors

The same three steps, in a loop over the six factors.
"""),
('code', """
rows = {}
for f in D.columns.drop('RF'):
    daily = D[f]
    month = daily.index + pd.offsets.MonthEnd(0)
    X = pd.DataFrame({'r':  (1 + daily).groupby(month).prod() - 1,
                      'rv': daily.groupby(month).apply(lambda x: ((x - x.mean()) ** 2).sum())})
    X['rv_lag'] = X['rv'].shift(1)
    X = X.dropna()

    w   = 1 / X['rv_lag']                                   # step 1
    c   = X['r'].std() / (w * X['r']).std()                 # step 2
    mgd = c * w * X['r']                                    # step 3
    fit = sm.OLS(mgd, sm.add_constant(X['r'])).fit()

    calm     = X['rv_lag'] <= X['rv_lag'].quantile(0.4)        # the calmest 40% of last months
    volatile = X['rv_lag'] >= X['rv_lag'].quantile(0.6)        # the most volatile 40%
    rows[f] = {'Sharpe': sharpe(X['r']), 'Sharpe managed': sharpe(mgd),
               'alpha': fit.params['const'] * 12, 't': fit.tvalues['const'],
               'Sharpe after calm': sharpe(X['r'][calm]), 'Sharpe after volatile': sharpe(X['r'][volatile])}

print(pd.DataFrame(rows).T.round(3).to_string())
"""),
('markdown', """
- Which factors gain? Which lose?
- Look at the last two columns. What is different about the factors that lose? Connect it to the formula on the slides.
"""),
('markdown', """
---

## 5. 🎯 Time the best mix

Section 4 timed each factor on its own. An investor who has read *Capital Allocation I* holds the best mix of all six. Does
timing still help once the factors already diversify each other?

1. The tangency weights: invert the covariance matrix of the six factors' monthly returns, times their means
2. The mix's **daily** return, so it has a realized variance of its own
3. The same three steps as section 3, on the mix

The weights use the whole sample, so the mix itself is in sample. We only ask whether timing it adds anything.
"""),
('code', """
factors = D.columns.drop('RF')
month = D.index + pd.offsets.MonthEnd(0)

# step 1: the best mix, from monthly returns: (covariance matrix)^-1 x means, then scaled
R = (1 + D[factors]).groupby(month).prod() - 1           # each factor's monthly return
cov = R.cov()                                             # covariance matrix, 6 x 6
W = np.linalg.inv(cov) @ R.mean()                         # the inverse times the mean returns
W = W / np.abs(W).sum()                                   # scale so the absolute weights add to one
print(pd.Series(W, index=factors).round(3).to_string(), "\\n")

# step 2: the mix's daily return
mix = D[factors] @ W                                      # each day, the weighted sum of the six

# step 3: the same three steps as before
X = pd.DataFrame({'r':  (1 + mix).groupby(month).prod() - 1,
                  'rv': mix.groupby(month).apply(lambda x: ((x - x.mean()) ** 2).sum())})
X['rv_lag'] = X['rv'].shift(1)
X = X.dropna()
w   = 1 / X['rv_lag']
c   = X['r'].std() / (w * X['r']).std()
mgd = c * w * X['r']
fit = sm.OLS(mgd, sm.add_constant(X['r'])).fit()

print(f"best mix          Sharpe {sharpe(X['r']):.2f}")
print(f"best mix, managed Sharpe {sharpe(mgd):.2f}   alpha {fit.params['const'] * 12:.1%} a year, t = {fit.tvalues['const']:.1f}\\n")
for a, b in [('1963', '1979'), ('1980', '2014'), ('2015', '2026')]:
    print(f"{a}-{b}: {sharpe(X['r'].loc[a:b]):.2f} -> {sharpe(mgd.loc[a:b]):.2f}")
"""),
('markdown', """
- The mix already has a Sharpe ratio above 1. Does timing still add? How does the gain compare with the single factors?
- Which factors carry the mix? Given section 4, would you have expected timing to help it?
- The weights saw the whole sample. Why does that matter less for the timing question than for the mix itself?
"""),
('markdown', """
---

## ⏸ Back to the slides

For the takeaways. The challenge below is homework.
"""),
('markdown', """
---

## 🎯 Challenge: cap the leverage

*Homework — due before the next class. It should take ten minutes.*

The managed strategies above sometimes hold ten or more times the factor. Most investors cannot.

Take **momentum** (`UMD`), build the volatility-managed strategy exactly as in section 4, then cap the weight at 2:
after step 2, use `(c * w).clip(upper=2)` as the weight. Report the Sharpe ratio of the capped strategy, 1963–2026.

Then, in at most three sentences: did the cap cost anything? Why or why not?

> **📌 Required variable names:**
> ```python
> umd_cap2_sharpe = ____   # Sharpe ratio of volatility-managed UMD with the weight capped at 2
> MEMO = \"\"\"...\"\"\"     # at most three sentences
> ```
"""),
('code', """
# Your work here


umd_cap2_sharpe = ____

print(f"capped at 2: Sharpe {umd_cap2_sharpe:.2f}")
"""),
('code', MEMO_CELL),
('markdown', """
---

## 📤 Submission
"""),
('code', submission(["umd_cap2_sharpe", "MEMO"], "L14_ConditionalStrategiesI_AI")),
]

# ═══════════════════════════════════════════════════════════════════ CONDITIONAL STRATEGIES II: TIMING EXPECTED RETURNS
cs2 = [
('markdown', r"""
# Conditional Strategies II: Timing Expected Returns

The ideas are in the slides. Here you test the most famous timing signal for the market, the dividend yield: in sample,
then the honest way, out of sample, and then as a strategy against buy and hold. Then the same three steps for four
factors, each with its own price signal, the value spread. Then a search over 24 more signals, and how many survive.
Last, the other market signals from the slides, one at a time.

**The plan**, one section per exercise in the slides

1. The dividend yield, at three horizons
2. Out of sample
3. The timing strategy, against buy and hold
4. 🎯 Each factor's value spread: your turn
5. Timing the six factors: 24 tries
6. Pick a predictor: any of the signals from the slides. Then back to the slides
7. 🎯 Challenge (homework): one number and three sentences

> 🧩 **Every section stands alone.** Run the Setup cell once, then jump to any section, in any order. Within a section,
> run the cells from the top.
"""),
('markdown', slides(2, "Conditional Strategies II")),
('code', r"""
#@title Setup — run this first
import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt
%matplotlib inline
plt.rcParams['figure.figsize'] = [11, 4]
import warnings; warnings.filterwarnings('ignore')

BASE = "https://raw.githubusercontent.com/amoreira2/UG54/refs/heads/main/assets/data"

# ── the market: its return, the T-bill rate and the dividend yield, 1926-2024
crsp  = pd.read_csv(f"{BASE}/Markettiming_data1.csv", parse_dates=['date'], index_col='date')
crsp.index = crsp.index + pd.offsets.MonthEnd(0)
tbill = pd.read_parquet(f"{BASE}/factors_monthly_1926.parquet")[['RF']]

market = crsp.merge(tbill, on='date').dropna()
market['ret']          = market['vwretd'] - market['RF']                        # the market's excess return
market['log_ret']      = np.log1p(market['vwretd']) - np.log1p(market['RF'])    # the same in logs: these add up across months
market['dp']           = market['dp'].rolling(12).sum()                         # dividend yield: last 12 months of dividends over today's price
market['next_ret']     = market['ret'].shift(-1)                                # NEXT month's return, on this month's row
market['next_log_ret'] = market['log_ret'].shift(-1)
market = market[['dp', 'ret', 'log_ret', 'next_ret', 'next_log_ret']]

# ── the factors
four_factors = pd.read_parquet(f"{BASE}/value_spreads_monthly_1926.parquet")    # HML, SMB, RMW, CMA, and the book-to-market of their legs
six_factors  = pd.read_csv(f"{BASE}/ff_monthly.csv", parse_dates=['date'], index_col='date')
six_factors  = six_factors[['Mkt-RF', 'SMB', 'HML', 'RMW', 'CMA', 'UMD']].dropna()   # monthly returns, 1980-2026

# ── the other market signals from the slides, for section 6: Goyal and Welch's data, updated to 2025, and VIX
goyal = pd.read_csv(f"{BASE}/goyal_welch_monthly_2025.csv", parse_dates=['date'], index_col='date')
vix   = pd.read_csv(f"{BASE}/vix_monthly_fred.csv", parse_dates=['date'], index_col='date')   # last close of each month

price_level       = (1 + goyal['infl']).cumprod()                               # consumer prices, from monthly inflation
real_earnings_10y = (goyal['E12'] / price_level).rolling(120).mean()            # ten years of S&P 500 earnings, in constant dollars

goyal['E/P']               = goyal['E12'] / goyal['Index']                      # S&P 500 earnings over the last 12 months, over price
goyal['1/CAPE']            = real_earnings_10y / (goyal['Index'] / price_level) # Shiller's CAPE, turned into a yield like D/P
goyal['book-to-market']    = goyal['b/m']                                       # Dow Jones Industrials: book value over market value
goyal['short rate']        = goyal['tbl']                                       # 3-month T-bill yield
goyal['term spread']       = goyal['lty'] - goyal['tbl']                        # long-term government bond yield minus the T-bill
goyal['default spread']    = goyal['BAA'] - goyal['AAA']                        # Baa minus Aaa corporate bond yields
goyal['realized variance'] = goyal['svar']                                      # sum of squared daily S&P 500 returns in the month
goyal['net issuance']      = goyal['ntis']                                      # net equity issued by NYSE firms over 12 months, over their value
goyal = goyal[['E/P', '1/CAPE', 'book-to-market', 'short rate', 'term spread', 'default spread',
               'realized variance', 'net issuance']]

predictors = market[['dp']].rename(columns={'dp': 'D/P'})                       # one row per month of the market
predictors = predictors.merge(goyal, on='date', how='left')
predictors = predictors.merge(vix.rename(columns={'vix': 'VIX'}), on='date', how='left')
predictors = predictors.loc['1927':]


def sharpe(ret):
    # Sharpe ratio a year, from monthly excess returns
    return ret.mean() / ret.std() * np.sqrt(12)


def out_of_sample(data, signal, start):
    # The loop of section 2, for any signal. `data` has the signal and `next_ret`, next month's return, on the same row.
    # Each month from `start`: fit next month's return on the signal using the past only, then forecast.
    data = data[[signal, 'next_ret']].dropna()
    rows = []
    for t in data.loc[start:].index:
        past = data.loc[:t].iloc[:-1]                         # the months whose next return was already known at t
        fit  = sm.OLS(past['next_ret'], sm.add_constant(past[signal])).fit()
        rows.append({'date':     t,
                     'ret':      data.loc[t, 'next_ret'],                                          # what happened next month
                     'forecast': fit.params['const'] + fit.params[signal] * data.loc[t, signal],   # what the signal said
                     'average':  past['next_ret'].mean()})                                         # what the historical average said
    return pd.DataFrame(rows).set_index('date')


def r2_out_of_sample(forecasts):
    # 1 - (squared errors of the signal's forecast) / (squared errors of the historical average)
    error_signal  = forecasts['ret'] - forecasts['forecast']
    error_average = forecasts['ret'] - forecasts['average']
    return 1 - (error_signal ** 2).sum() / (error_average ** 2).sum()


print(f"market {market.index[0]:%Y-%m} to {market.index[-1]:%Y-%m}; four factors {four_factors.index[0]:%Y-%m} to "
      f"{four_factors.index[-1]:%Y-%m}; six factors {six_factors.index[0]:%Y-%m} to {six_factors.index[-1]:%Y-%m}; "
      f"{predictors.shape[1]} market signals to {predictors.index[-1]:%Y-%m}")
"""),
('markdown', r"""
**What Setup gives you.** Every table has one row per month, and every return is over T-bills.

| name | what is in it |
|---|---|
| `market` | `dp`: the dividend yield. `ret`: the market's return this month. `next_ret`: the market's return **next** month, on this month's row. `log_ret`, `next_log_ret`: the same two in logs |
| `four_factors` | the returns of `HML`, `SMB`, `RMW` and `CMA`, and the book-to-market of each one's long and short legs |
| `six_factors` | the returns of the six factors, 1980–2026 |
| `predictors` | ten market signals, one column each, on the same months as `market` |
| `out_of_sample(data, signal, start)` | the loop of section 2: one forecast a month, each fitted on the past only |
| `r2_out_of_sample(forecasts)` | the out-of-sample $R^2$ of those forecasts |
| `sharpe(ret)` | the Sharpe ratio a year of a monthly return |

A signal known this month has to forecast the return of next month. So every regression below puts this month's signal
and `next_ret` on the same row.
"""),
('markdown', r"""
---

## 1. The dividend yield, at three horizons

> 🧩 **Stands alone.** Needs only the Setup cell: you can start here.

When prices are low relative to dividends, either dividends are about to fall, or future returns are high. First compare
the dividend yield with the return over the *next* five years.
"""),
('code', r"""
next_5_years = market['log_ret'].rolling(60).sum().shift(-60) / 5      # the return over the next 60 months, a year

ax = market['dp'].plot(label='dividend yield', legend=True)
next_5_years.plot(ax=ax, secondary_y=True, label='return over the next five years, a year', legend=True)
plt.show()

print(f"correlation: {market['dp'].corr(next_5_years):.2f}")
"""),
('markdown', r"""
Now the forecasting regression,

$$r_{t \to t+h} = a + b \cdot \text{D/P}_t + u,$$

run for the next month, the next year and the next five years. Two sets of $t$-statistics: the usual ones, and HAC ones
that allow for the overlap.
"""),
('code', r"""
table = {}
for months in [1, 12, 60]:
    data = market[['dp']].copy()
    data['next_ret'] = market['log_ret'].rolling(months).sum().shift(-months) * 12 / months   # the return over the next `months` months, a year
    data = data.dropna()

    X = sm.add_constant(data['dp'])
    usual = sm.OLS(data['next_ret'], X).fit()                                                 # as if every month were new
    hac   = sm.OLS(data['next_ret'], X).fit(cov_type='HAC', cov_kwds={'maxlags': months})     # allows for the overlap

    table[f"next {months} months"] = {'b': usual.params['dp'], 'usual t': usual.tvalues['dp'], 'HAC t': hac.tvalues['dp'],
                                      'R2': usual.rsquared, 'observations': len(data), 'do not overlap': len(data) // months}
print(pd.DataFrame.from_dict(table, orient='index').round(3).to_string())
"""),
('markdown', r"""
- When was the dividend yield highest? What came next?
- The $R^2$ and the usual $t$ both grow with the horizon. Should you believe the five-year regression most?
- Two consecutive five-year returns share 59 of their 60 months. How many truly separate five-year periods are there?
  Which $t$-statistic would you report?
"""),
('markdown', r"""
---

## 2. Out of sample

> 🧩 **Stands alone.** Needs only the Setup cell: you can start here.

The honest test: stand in each month $t$, using only what you knew then.

- fit the regression of next month's return on D/P, using only months whose next return you have already seen
- forecast next month's return with today's D/P
- the benchmark: the historical average return up to $t$, which is what you would use with no signal

The loop below does this every month from 1950. Read it before you run it.
"""),
('code', r"""
data = market[['dp', 'next_ret']].dropna()                # this month's D/P and next month's return, on the same row

rows = []
for t in data.loc['1950':].index:
    past = data.loc[:t].iloc[:-1]                         # the months whose next return was already known at t
    fit  = sm.OLS(past['next_ret'], sm.add_constant(past['dp'])).fit()
    rows.append({'date':     t,
                 'ret':      data.loc[t, 'next_ret'],                                       # what happened next month
                 'forecast': fit.params['const'] + fit.params['dp'] * data.loc[t, 'dp'],    # what D/P said
                 'average':  past['next_ret'].mean()})                                      # what the historical average said
forecasts = pd.DataFrame(rows).set_index('date')
forecasts.head()
"""),
('markdown', r"""
The out-of-sample $R^2$ compares the squared errors of the two forecasts:

$$R^2_{\text{OOS}} = 1 - \frac{\sum (r - \text{forecast})^2}{\sum (r - \text{average})^2}$$

Positive: D/P beat the historical average. Negative: you would have done better without it.
"""),
('code', r"""
error_dp      = forecasts['ret'] - forecasts['forecast']      # how far off D/P's forecast was
error_average = forecasts['ret'] - forecasts['average']       # how far off the historical average was

r2_oos = 1 - (error_dp ** 2).sum() / (error_average ** 2).sum()
print(f"out-of-sample R2, 1950-2024: {r2_oos:.2%}")

for first, last in [('1950', '1979'), ('1980', '1999'), ('2000', '2024')]:
    r2_period = 1 - (error_dp.loc[first:last] ** 2).sum() / (error_average.loc[first:last] ** 2).sum()
    print(f"   {first}-{last}: {r2_period:.2%}")
"""),
('markdown', r"""
- In which of the three periods did D/P beat the historical average?
- In sample, D/P explained 0.3% of next month's return. Out of sample it explains less than nothing. How can both be true?
- Why is the benchmark the historical average, and not a forecast of zero?

Setup has these two steps as functions, `out_of_sample()` and `r2_out_of_sample()`. They are the same lines, and the
sections below use them.
"""),
('markdown', r"""
---

## 3. The timing strategy, against buy and hold

> 🧩 **Stands alone.** Needs only the Setup cell: you can start here.

The formula from *Capital Allocation I* with a forecast in it: weight $= \text{forecast} / (\gamma \sigma^{2})$. We hold
$\sigma$ fixed at its value before 1950, so all the timing comes from the forecast.

What do you compare it with? Buy and hold **with the same average weight**. Then the two strategies hold the same amount
of the market on average, and the only difference is *when*.
"""),
('code', r"""
forecasts = out_of_sample(market, 'dp', '1950')           # section 2's forecasts

gamma    = 3
variance = market.loc[:'1949', 'ret'].var()               # the market's monthly variance before 1950, held fixed

forecasts['weight']       = forecasts['forecast'] / (gamma * variance)       # the weight on the market: negative means short
forecasts['timing']       = forecasts['weight'] * forecasts['ret']           # next month's return on that weight
forecasts['buy and hold'] = forecasts['weight'].mean() * forecasts['ret']    # the same average weight, never changed

print(f"Sharpe ratio:      timing {sharpe(forecasts['timing']):.2f}, buy and hold {sharpe(forecasts['buy and hold']):.2f}")
print(f"volatility a year: timing {forecasts['timing'].std() * np.sqrt(12):.1%}, buy and hold {forecasts['buy and hold'].std() * np.sqrt(12):.1%}")
print(f"average weight {forecasts['weight'].mean():.2f}, short in {np.mean(forecasts['weight'] < 0):.0%} of months\n")
for first, last in [('1950', '1979'), ('1980', '1999'), ('2000', '2024')]:
    period = forecasts.loc[first:last]
    print(f"{first}-{last}: timing {sharpe(period['timing']):.2f}, buy and hold {sharpe(period['buy and hold']):.2f}")

(1 + forecasts[['timing', 'buy and hold']]).cumprod().plot(logy=True, title='cumulative return: timing on D/P, and buy and hold with the same average weight')
plt.show()
forecasts['weight'].plot(title='weight on the market'); plt.axhline(0, color='k', lw=0.5); plt.show()
"""),
('markdown', r"""
- When does timing lose ground to buy and hold? What was D/P doing then?
- Timing ends above buy and hold, yet its Sharpe ratio is lower. How can both be true? Look at the two volatilities.
- In which period did timing win, and in which did it lose badly?
- Would changing `gamma` change the Sharpe ratio? Try it.
- Why compare with buy and hold at the same average weight, and not with one dollar in the market?
"""),
('markdown', r"""
---

## 4. 🎯 Each factor's value spread

> 🧩 **Stands alone.** Needs only the Setup cell: you can start here.

D/P is the market's price against its fundamentals. A long-short factor has one too: how cheap the stocks it buys are
against the stocks it sells,

$$\text{VS}_t = \log \frac{B}{M}\Big|_{\text{long},\,t} - \log \frac{B}{M}\Big|_{\text{short},\,t}.$$

`four_factors` has four factors from Ken French's 2×3 sorts: each one's monthly return (`HML`, `SMB`, `RMW`, `CMA`) and
the book-to-market of its long and short legs (`HML_bm_long`, `HML_bm_short`, and so on). HML and SMB start in 1926, RMW
and CMA in 1963. Book is from the last fiscal year; the price is from last December.

**Your turn.** Build HML's value spread and call it `vs_hml`. `np.log` takes logs.
"""),
('code', r"""
# === YOUR TURN ===

vs_hml = ____
"""),
('code', r"""
#@title 🔒 Check: HML's value spread
hml_spread = np.log(four_factors['HML_bm_long']) - np.log(four_factors['HML_bm_short'])

try:
    print("yours matches" if np.allclose(vs_hml, hml_spread) else "yours differs: compare with the plot below", "\n")
except Exception as e:
    print("yours: not built yet:", type(e).__name__, "\n")

hml_next_5_years = four_factors['HML'].rolling(60).sum().shift(-60) / 5     # HML's return over the next five years, a year
ax = hml_spread.plot(label="HML's value spread", legend=True)
hml_next_5_years.plot(ax=ax, secondary_y=True, label='HML over the next five years, a year', legend=True)
plt.show()

print(f"median {hml_spread.median():.2f}, now {hml_spread.iloc[-1]:.2f} ({hml_spread.index[-1]:%Y-%m}); "
      f"correlation with the next five years: {hml_spread.corr(hml_next_5_years):.2f}")
"""),
('markdown', r"""
Now sections 1 to 3 again, in a loop over the four factors: the in-sample regression on next month's return, the
out-of-sample forecasts from 1980, and the timing strategy against buy and hold with the same average weight. The
variance is held at its value before 1980.
"""),
('code', r"""
table = {}
fig, axes = plt.subplots(2, 2, figsize=(13, 7))
for factor, ax in zip(['HML', 'SMB', 'RMW', 'CMA'], axes.flat):
    data = four_factors[[factor]].copy()
    data['spread']   = np.log(four_factors[f'{factor}_bm_long']) - np.log(four_factors[f'{factor}_bm_short'])   # this factor's value spread
    data['next_ret'] = data[factor].shift(-1)                 # next month's return, on this month's row
    data = data.dropna()

    # in sample, as in section 1
    fit = sm.OLS(data['next_ret'], sm.add_constant(data['spread'])).fit(cov_type='HAC', cov_kwds={'maxlags': 1})

    # out of sample from 1980, as in section 2
    forecasts = out_of_sample(data, 'spread', '1980')

    # the timing strategy against buy and hold, as in section 3
    variance = four_factors.loc[:'1979', factor].var()
    forecasts['weight']       = forecasts['forecast'] / (3 * variance)
    forecasts['timing']       = forecasts['weight'] * forecasts['ret']
    forecasts['buy and hold'] = forecasts['weight'].mean() * forecasts['ret']
    (1 + forecasts[['timing', 'buy and hold']]).cumprod().plot(ax=ax, logy=True, title=factor)

    table[factor] = {'from': data.index[0].year, 'HAC t': fit.tvalues['spread'], 'R2 in sample': fit.rsquared,
                     'R2 out of sample': r2_out_of_sample(forecasts),
                     'Sharpe, timing': sharpe(forecasts['timing']), 'Sharpe, buy and hold': sharpe(forecasts['buy and hold']),
                     'average weight': forecasts['weight'].mean(), 'months short': np.mean(forecasts['weight'] < 0)}
plt.suptitle('cumulative return: timing on the value spread, and buy and hold with the same average weight')
plt.tight_layout(); plt.show()

print(pd.DataFrame.from_dict(table, orient='index').round(3).to_string())
"""),
('markdown', r"""
- Which factors beat the historical average out of sample? Set them against D/P's $R^2$ in section 2.
- Where does timing pull ahead of buy and hold, and when? How often is that strategy short, and would you run it?
- The price in the book-to-market is last December's, not today's. What has the factor done since December, and why
  might that help the forecast?
"""),
('markdown', r"""
---

## 5. Timing the six factors: 24 tries

> 🧩 **Stands alone.** Needs only the Setup cell: you can start here.

Four simple signals for each factor: its own return last month, over the last 12 months, three to five years ago, and its
own volatility. Run the forecasting regression on 1980–2002 and again on 2003–2026. A real signal should work in both.
"""),
('code', r"""
daily = pd.read_parquet(f"{BASE}/ff6_daily_1963.parquet")[six_factors.columns]   # the six factors, daily
month = daily.index + pd.offsets.MonthEnd(0)                                     # the month each day belongs to
volatility = daily.groupby(month).apply(lambda days: np.sqrt(((days - days.mean()) ** 2).sum()))   # each factor's volatility, month by month
volatility.index.name = 'date'

rows = []
for factor in six_factors.columns:
    data = six_factors[[factor]].rename(columns={factor: 'ret'})
    data = data.merge(volatility[[factor]].rename(columns={factor: 'own volatility'}), on='date', how='left')
    data['last month']     = data['ret']
    data['last 12 months'] = data['ret'].rolling(12).sum()
    data['3-5 years ago']  = data['ret'].shift(12).rolling(48).sum()
    data['next_ret']       = data['ret'].shift(-1)            # next month's return, on this month's row

    for signal in ['last month', 'last 12 months', '3-5 years ago', 'own volatility']:
        row = {'factor': factor, 'signal': signal}
        for half, first, last in [('t, 1980-2002', '1980', '2002'), ('t, 2003-2026', '2003', '2026')]:
            period = data.loc[first:last, [signal, 'next_ret']].dropna()
            row[half] = sm.OLS(period['next_ret'], sm.add_constant(period[signal])).fit().tvalues[signal]
        rows.append(row)
tstats = pd.DataFrame(rows)
print(tstats.round(2).sort_values('t, 1980-2002', ascending=False).to_string(index=False))

plt.scatter(tstats['t, 1980-2002'], tstats['t, 2003-2026'])
plt.axhline(0, color='k', lw=0.5); plt.axvline(0, color='k', lw=0.5)
plt.xlabel('t, 1980-2002'); plt.ylabel('t, 2003-2026'); plt.show()
"""),
('markdown', r"""
- How many of the 24 have $|t| > 2$ in the first half? How many would you expect by luck alone?
- Take the five best from the first half. How many still work in the second?
- Which signal works for several factors in both halves? It has a name: factor momentum.
"""),
('markdown', r"""
---

## 6. Pick a predictor

> 🧩 **Stands alone.** Needs only the Setup cell: you can start here.

The slides list eleven signals people use to forecast the market. `predictors` has ten of them, one column each, on the
same months as `market`. Forward P/E is missing: it needs analysts' forecasts, which we do not have.

| column | what it is | from |
|---|---|---|
| `D/P` | dividends over the last 12 months, over price | 1927 |
| `E/P` | S&P 500 earnings over the last 12 months, over price | 1927 |
| `1/CAPE` | ten years of real earnings over the real price: Shiller's CAPE, as a yield | 1927 |
| `book-to-market` | book value over market value, Dow Jones Industrials | 1927 |
| `short rate` | 3-month T-bill yield | 1927 |
| `term spread` | long-term government bond yield minus the T-bill | 1927 |
| `default spread` | Baa minus Aaa corporate bond yields | 1927 |
| `realized variance` | sum of squared daily S&P 500 returns in the month | 1927 |
| `net issuance` | net equity issued over the last 12 months, over market value | 1927 |
| `VIX` | option-implied volatility of the S&P 500 | 1990 |

The valuation ratios are all yields, like D/P: a high value means a cheap market.

Set `PREDICTOR` to a column name and run the cell. It does sections 1 to 3 on that signal: the in-sample regression, the
out-of-sample forecasts from `START`, and the timing strategy against buy and hold.
"""),
('code', r"""
PREDICTOR = 'E/P'      # one of: 'D/P', 'E/P', '1/CAPE', 'book-to-market', 'short rate', 'term spread', 'default spread',
                       #         'realized variance', 'net issuance', 'VIX'
START     = '1950'     # the first month to forecast

data  = predictors[[PREDICTOR]].merge(market[['next_ret', 'next_log_ret']], on='date').dropna()   # this month's signal, next month's return
start = max(pd.Timestamp(START), data.index[0] + pd.DateOffset(years=10))      # at least ten years of data before the first forecast

# in sample, as in section 1
fit = sm.OLS(data['next_log_ret'], sm.add_constant(data[PREDICTOR])).fit(cov_type='HAC', cov_kwds={'maxlags': 1})

# out of sample, as in section 2
forecasts = out_of_sample(data, PREDICTOR, start)

# the timing strategy against buy and hold, as in section 3, with the variance held at its value before the first forecast
variance = market.loc[market.index < start, 'ret'].var()
forecasts['weight']       = forecasts['forecast'] / (3 * variance)
forecasts['timing']       = forecasts['weight'] * forecasts['ret']
forecasts['buy and hold'] = forecasts['weight'].mean() * forecasts['ret']

print(f"{PREDICTOR}, {data.index[0]:%Y-%m} to {data.index[-1]:%Y-%m}")
print(f"in sample:     b {fit.params[PREDICTOR]:.3f}, HAC t {fit.tvalues[PREDICTOR]:.2f}, R2 {fit.rsquared:.2%}")
print(f"out of sample: R2 {r2_out_of_sample(forecasts):.2%}, with forecasts from {start:%Y-%m}")
print(f"Sharpe ratio:  timing {sharpe(forecasts['timing']):.2f}, buy and hold {sharpe(forecasts['buy and hold']):.2f}; "
      f"average weight {forecasts['weight'].mean():.2f}, short in {np.mean(forecasts['weight'] < 0):.0%} of months")

fig, axes = plt.subplots(1, 2, figsize=(13, 3.6))
data[PREDICTOR].plot(ax=axes[0], title=PREDICTOR)
(1 + forecasts[['timing', 'buy and hold']]).cumprod().plot(ax=axes[1], logy=True, title='cumulative return: timing, and buy and hold with the same average weight')
plt.show()
"""),
('markdown', r"""
- Try `E/P`, the strongest in sample, then `short rate`. Which beats the historical average out of sample?
- Does it beat buy and hold: on the plot, and on the Sharpe ratio? If the two disagree, which do you believe?
- Try `VIX`. Its forecasts start in 2000, after ten years of data. Is that enough to estimate a slope?
- Pick a signal and set `START = '1980'`. Does the verdict change?
- Every one of these signals was published because it forecast well in some sample. Why might that make it look
  better in sample than it will do from here on?

The cell below runs the same three steps on all ten at once: the table in the slides.
"""),
('code', r"""
#@title All ten at once: the table in the slides
table = {}
for name in predictors.columns:
    data  = predictors[[name]].merge(market[['next_ret', 'next_log_ret']], on='date').dropna()
    start = max(pd.Timestamp('1950'), data.index[0] + pd.DateOffset(years=10))

    fit       = sm.OLS(data['next_log_ret'], sm.add_constant(data[name])).fit(cov_type='HAC', cov_kwds={'maxlags': 1})
    forecasts = out_of_sample(data, name, start)
    forecasts['timing'] = forecasts['forecast'] / (3 * market.loc[:'1949', 'ret'].var()) * forecasts['ret']

    table[name] = {'from': data.index[0].year, 'HAC t': fit.tvalues[name], 'forecasts from': start.year,
                   'R2 out of sample': r2_out_of_sample(forecasts), 'R2, 2000-2024': r2_out_of_sample(forecasts.loc['2000':]),
                   'Sharpe, timing': sharpe(forecasts['timing']), 'Sharpe, buy and hold': sharpe(forecasts['ret'])}

print(pd.DataFrame.from_dict(table, orient='index').round(4).to_string())
"""),
('markdown', r"""
---

## ⏸ Back to the slides

For the takeaways. The challenge below is homework.
"""),
('markdown', r'''
---

## 🎯 Challenge: start later

> 🧩 **Stands alone.** Needs only the Setup cell.

*Homework — due before the next class. It should take ten minutes.*

Section 2 started forecasting in 1950. Suppose you had only started in **1980**, the year the value spreads in section 4
start. Redo section 2 with forecasts from 1980 and everything else the same: change `'1950'` to `'1980'` in the loop, or
use `out_of_sample()` and `r2_out_of_sample()` from Setup. Report the out-of-sample $R^2$.

Then, in at most three sentences: would you trade D/P on this evidence? Set it against the value spreads in section 4.

> **📌 Required variable names:**
> ```python
> oos_r2_1980 = ____   # out-of-sample R2 with forecasts from 1980, a decimal (-0.01 means -1%)
> MEMO = """...""" # at most three sentences
> ```
'''),
('code', r"""
# Your work here


oos_r2_1980 = ____

print(f"out of sample R2 from 1980: {oos_r2_1980:.2%}")
"""),
('code', MEMO_CELL),
('markdown', r"""
---

## 📤 Submission
"""),
('code', submission(["oos_r2_1980", "MEMO"], "L15_ConditionalStrategiesII_AI")),
]

build("L14_ConditionalStrategiesI_AI.ipynb", "cs1", cs1)
build("L15_ConditionalStrategiesII_AI.ipynb", "cs2", cs2)
