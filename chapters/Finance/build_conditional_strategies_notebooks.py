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
('markdown', """
# Conditional Strategies II: Timing Expected Returns

The ideas are in the slides. Here you test the most famous timing signal for the market, the dividend yield: in sample,
then the honest way, out of sample. Then the same test for four factors, each with its own price signal, the value
spread. Last, a search over 24 more signals, and how many survive.

**The plan**, one section per exercise in the slides

1. The dividend yield, at three horizons
2. 🎯 Out of sample: your turn
3. The timing strategy
4. 🎯 Each factor's value spread: your turn
5. Timing the six factors: 24 tries. Then back to the slides
6. 🎯 Challenge (homework): one number and three sentences
"""),
('markdown', slides(2, "Conditional Strategies II")),
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

crsp = pd.read_csv(f"{BASE}/Markettiming_data1.csv", parse_dates=['date'], index_col='date')   # CRSP market, with dividends
crsp.index = crsp.index + pd.offsets.MonthEnd(0)
rf = pd.read_parquet(f"{BASE}/factors_monthly_1926.parquet")['RF']                              # T-bill rate
V  = pd.read_parquet(f"{BASE}/value_spreads_monthly_1926.parquet")    # four factors, and the book-to-market of their legs
ff = pd.read_csv(f"{BASE}/ff_monthly.csv", index_col=0, parse_dates=True)                       # the six factors, 1980-2026
F  = ff[['Mkt-RF', 'SMB', 'HML', 'RMW', 'CMA', 'UMD']].dropna()

C = crsp.join(rf, how='inner').dropna()
C['ex'] = C['vwretd'] - C['RF']                             # the market's excess return
C['dp'] = C['dp'].rolling(12).sum()                         # dividend yield: last 12 months of dividends over today's price
C['lx'] = np.log1p(C['vwretd']) - np.log1p(C['RF'])         # log excess return: these add up across months

sharpe = lambda x: x.mean() / x.std() * np.sqrt(12)

print(f"market {C.index[0]:%Y-%m} to {C.index[-1]:%Y-%m}; value spreads {V.index[0]:%Y-%m} to {V.index[-1]:%Y-%m}; "
      f"six factors {F.index[0]:%Y-%m} to {F.index[-1]:%Y-%m}")
"""),
('markdown', """
---

## 1. The dividend yield, at three horizons

When prices are low relative to dividends, either dividends are about to fall, or future returns are high. First compare
the dividend yield with the return over the *next* five years.
"""),
('code', """
next5 = C['lx'].rolling(60).sum().shift(-60) / 5            # return over the next 60 months, a year

ax = C['dp'].plot(label='dividend yield', legend=True)
next5.plot(ax=ax, secondary_y=True, label='return over the next five years, a year', legend=True)
plt.show()

print(f"correlation: {C['dp'].corr(next5):.2f}")
"""),
('markdown', """
Now the forecasting regression,

$$r_{t \\to t+h} = a + b \\cdot \\text{D/P}_t + u,$$

run for the next month, the next year and the next five years. Two sets of $t$-statistics: the naive ones, and HAC ones
that allow for the overlap.
"""),
('code', """
rows = {}
for h in [1, 12, 60]:
    y = C['lx'].rolling(h).sum().shift(-h) * 12 / h        # return over the next h months, a year
    data = pd.DataFrame({'y': y, 'dp': C['dp']}).loc['1927':].dropna()
    X = sm.add_constant(data['dp'])

    naive = sm.OLS(data['y'], X).fit()                                                  # as if every month were new
    hac   = sm.OLS(data['y'], X).fit(cov_type='HAC', cov_kwds={'maxlags': max(h, 1)})  # allows for the overlap

    rows[f"{h} months"] = {'b': naive.params['dp'], 'naive t': naive.tvalues['dp'], 'HAC t': hac.tvalues['dp'],
                           'R2': naive.rsquared, 'observations': len(data), 'do not overlap': len(data) // h}
print(pd.DataFrame(rows).T.round(3).to_string())
"""),
('markdown', """
- When was the dividend yield highest? What came next?
- The $R^2$ and the naive $t$ both grow with the horizon. Should you believe the five-year regression most?
- Two consecutive five-year returns share 59 of their 60 months. How many truly separate five-year periods are there?
  Which $t$-statistic would you report?
"""),
('markdown', """
---

## 2. 🎯 Out of sample

The honest test: stand in each month $t$, using only what you knew then.

- fit the regression of next month's return on D/P, using only months whose next return you have already seen
- forecast next month's return with today's D/P
- the benchmark: the historical average return up to $t$, which is what you would use with no signal

The loop below does this every month from 1950. Read it before you run it.
"""),
('code', """
y = C['ex'].shift(-1)                      # next month's excess return, lined up with this month's D/P
rows = []
for t in C.loc['1950':].index[:-1]:
    known = pd.DataFrame({'y': y, 'dp': C['dp']}).loc['1927':t].iloc[:-1].dropna()   # pairs whose return is known at t
    b, a = np.polyfit(known['dp'], known['y'], 1)          # slope and intercept, from the past only
    rows.append({'date': t,
                 'r':        y.loc[t],                     # what happened next month
                 'forecast': a + b * C['dp'].loc[t],       # what D/P said
                 'average':  known['y'].mean()})           # what the historical average said
P = pd.DataFrame(rows).set_index('date')
P.head()
"""),
('markdown', """
**Your turn.** The out-of-sample $R^2$ compares the two forecasts' squared errors:

$$R^2_{\\text{OOS}} = 1 - \\frac{\\sum (r - \\text{forecast})^2}{\\sum (r - \\text{average})^2}$$

Positive: D/P beat the historical average. Negative: you would have done better without it. Call it `r2_oos`.
"""),
('code', """
# === YOUR TURN ===

r2_oos = ____
"""),
('code', """
#@title 🔒 Check: out of sample
r2 = lambda Q: 1 - ((Q['r'] - Q['forecast']) ** 2).sum() / ((Q['r'] - Q['average']) ** 2).sum()

try:
    print(f"yours: {r2_oos:.2%}")
except Exception as e:
    print("yours: not built yet:", type(e).__name__)

print(f"out of sample R2, 1950-2024: {r2(P):.2%}")
for a, b in [('1950', '1979'), ('1980', '1999'), ('2000', '2024')]:
    print(f"   {a}-{b}: {r2(P.loc[a:b]):.2%}")

gain = ((P['r'] - P['average']) ** 2 - (P['r'] - P['forecast']) ** 2).cumsum()   # rising when D/P forecasts better
gain.plot(title='cumulative gain from D/P over the historical average'); plt.axhline(0, color='k', lw=0.5); plt.show()
"""),
('markdown', """
- When did D/P stop working? Look at the plot.
- In sample, D/P explained 0.3% of next month's return. Out of sample it explains less than nothing. How can both be true?
"""),
('markdown', """
---

## 3. The timing strategy

The formula from *Capital Allocation I* with a forecast in it: weight $= \\text{forecast} / (\\gamma \\sigma^{2})$. We hold
$\\sigma$ fixed at its value before 1950, so all the timing comes from the forecast.
"""),
('code', """
sigma2 = C['ex'].loc[:'1949'].var()        # the market's monthly variance before 1950, held fixed
gamma  = 3
weight = P['forecast'] / (gamma * sigma2)  # the weight on the market each month: negative means short
timed  = weight * P['r']                   # this month's excess return on that weight

print(f"timing: Sharpe {sharpe(timed):.2f}    buy and hold: Sharpe {sharpe(P['r']):.2f}")
print(f"average weight {weight.mean():.2f}, short in {np.mean(weight < 0):.0%} of months\\n")
for a, b in [('1950', '1979'), ('1980', '1999'), ('2000', '2024')]:
    print(f"{a}-{b}: timing {sharpe(timed.loc[a:b]):.2f}, buy and hold {sharpe(P['r'].loc[a:b]):.2f}")

weight.plot(title='weight on the market'); plt.axhline(0, color='k', lw=0.5); plt.show()
"""),
('markdown', """
- Would changing `gamma` change the Sharpe ratio? Try it.
- In which period did timing win, and in which did it lose badly? Why then?
"""),
('markdown', """
---

## 4. 🎯 Each factor's value spread

D/P is the market's price against its fundamentals. A long-short factor has one too: how cheap the stocks it buys are
against the stocks it sells,

$$\\text{VS}_t = \\log \\frac{B}{M}\\Big|_{\\text{long},\\,t} - \\log \\frac{B}{M}\\Big|_{\\text{short},\\,t}.$$

`V` has four factors from Ken French's 2×3 sorts: each one's monthly return (`HML`, `SMB`, `RMW`, `CMA`) and the
book-to-market of its long and short legs (`HML_bm_long`, `HML_bm_short`, and so on). HML and SMB start in 1926, RMW and
CMA in 1963. Book is from the last fiscal year; the price is from last December.

**Your turn.** Build HML's value spread and call it `vs_hml`. `np.log` takes logs.
"""),
('code', """
# === YOUR TURN ===

vs_hml = ____
"""),
('code', """
#@title 🔒 Check: HML's value spread
vs_ref = np.log(V['HML_bm_long']) - np.log(V['HML_bm_short'])

try:
    print("yours matches" if np.allclose(vs_hml, vs_ref) else "yours differs: compare with the plot below", "\\n")
except Exception as e:
    print("yours: not built yet:", type(e).__name__, "\\n")

next5_hml = V['HML'].rolling(60).sum().shift(-60) / 5       # HML's return over the next five years, a year
ax = vs_ref.plot(label="HML's value spread", legend=True)
next5_hml.plot(ax=ax, secondary_y=True, label='HML over the next five years, a year', legend=True)
plt.show()

print(f"median {vs_ref.median():.2f}, now {vs_ref.iloc[-1]:.2f} ({vs_ref.index[-1]:%Y-%m}); "
      f"correlation with the next five years: {vs_ref.corr(next5_hml):.2f}")
"""),
('markdown', """
Now sections 1 to 3 again, in a loop over the four factors: the in-sample regression on next month's return, the
out-of-sample loop with forecasts from 1980, and the timing strategy with $\\sigma$ fixed at its value before 1980.
"""),
('code', """
rows = {}
for f in ['HML', 'SMB', 'RMW', 'CMA']:
    vs = (np.log(V[f'{f}_bm_long']) - np.log(V[f'{f}_bm_short'])).dropna()   # this factor's value spread
    ret_next = V[f].shift(-1)                              # next month's return, lined up with this month's spread
    data = pd.DataFrame({'y': ret_next, 'vs': vs}).dropna()

    # in sample, as in section 1
    fit = sm.OLS(data['y'], sm.add_constant(data['vs'])).fit(cov_type='HAC', cov_kwds={'maxlags': 1})

    # out of sample from 1980, as in section 2
    oos = []
    for t in vs.loc['1980':].index[:-1]:
        known = data.loc[:t].iloc[:-1]                     # pairs whose return is known at t
        b, a = np.polyfit(known['vs'], known['y'], 1)
        oos.append({'date': t, 'r': ret_next.loc[t], 'forecast': a + b * vs.loc[t], 'average': known['y'].mean()})
    Q = pd.DataFrame(oos).set_index('date')

    # the timing strategy, as in section 3
    weight = Q['forecast'] / (3 * V[f].loc[:'1979'].var())
    timed  = weight * Q['r']

    rows[f] = {'from': vs.index[0].year, 'HAC t': fit.tvalues['vs'], 'R2 in sample': fit.rsquared,
               'R2 out of sample': 1 - ((Q['r'] - Q['forecast']) ** 2).sum() / ((Q['r'] - Q['average']) ** 2).sum(),
               'Sharpe, buy and hold': sharpe(Q['r']), 'Sharpe, timed': sharpe(timed), 'months short': np.mean(weight < 0)}

print(pd.DataFrame(rows).T.round(3).to_string())
"""),
('markdown', """
- Which factors beat the historical average out of sample? Set them against D/P's $R^2$ in section 2.
- Where is the gain largest? How often is that strategy short, and would you run it?
- The price in the book-to-market is last December's, not today's. What has the factor done since December, and why
  might that help the forecast?
"""),
('markdown', """
---

## 5. Timing the six factors: 24 tries

Four simple signals for each factor: its own return last month, over the last 12 months, three to five years ago, and its
own volatility. Run the forecasting regression on 1980–2002 and again on 2003–2026. A real signal should work in both.
"""),
('code', """
d   = pd.read_parquet(f"{BASE}/ff6_daily_1963.parquet")                 # daily factors, for each factor's volatility
own_vol = d[F.columns].groupby(d.index + pd.offsets.MonthEnd(0)).apply(lambda x: np.sqrt(((x - x.mean()) ** 2).sum()))  # each month's volatility

rows = []
for f in F.columns:
    r = F[f]
    signals = {'last month':     r,
               'last 12 months': r.rolling(12).sum(),
               '3-5 years ago':  r.shift(12).rolling(48).sum(),
               'own volatility': own_vol[f].reindex(r.index)}
    for name, s in signals.items():
        data = pd.DataFrame({'y': r.shift(-1), 'x': s}).dropna()       # next month's return on this month's signal
        row = {'factor': f, 'signal': name}
        for half, sl in [('t, 1980-2002', slice('1980', '2002')), ('t, 2003-2026', slice('2003', '2026'))]:
            q = data.loc[sl]
            row[half] = sm.OLS(q['y'], sm.add_constant(q['x'])).fit().tvalues['x']
        rows.append(row)
T = pd.DataFrame(rows)
print(T.round(2).sort_values('t, 1980-2002', ascending=False).to_string(index=False))

plt.scatter(T['t, 1980-2002'], T['t, 2003-2026'])
plt.axhline(0, color='k', lw=0.5); plt.axvline(0, color='k', lw=0.5)
plt.xlabel('t, 1980-2002'); plt.ylabel('t, 2003-2026'); plt.show()
"""),
('markdown', """
- How many of the 24 have $|t| > 2$ in the first half? How many would you expect by luck alone?
- Take the five best from the first half. How many still work in the second?
- Which signal works for several factors in both halves? It has a name: factor momentum.
"""),
('markdown', """
---

## ⏸ Back to the slides

For the takeaways. The challenge below is homework.
"""),
('markdown', """
---

## 🎯 Challenge: start later

*Homework — due before the next class. It should take ten minutes.*

Section 2 started forecasting in 1950. Suppose you had only started in **1980**, the year the value spreads in section 4
start. Rerun the loop from section 2 with `C.loc['1980':]` instead of `C.loc['1950':]`, and everything else the same.
Report the out-of-sample $R^2$.

Then, in at most three sentences: would you trade D/P on this evidence? Set it against the value spreads in section 4.

> **📌 Required variable names:**
> ```python
> oos_r2_1980 = ____   # out-of-sample R2 with forecasts from 1980, a decimal (-0.01 means -1%)
> MEMO = \"\"\"...\"\"\" # at most three sentences
> ```
"""),
('code', """
# Your work here


oos_r2_1980 = ____

print(f"out of sample R2 from 1980: {oos_r2_1980:.2%}")
"""),
('code', MEMO_CELL),
('markdown', """
---

## 📤 Submission
"""),
('code', submission(["oos_r2_1980", "MEMO"], "L15_ConditionalStrategiesII_AI")),
]

build("L14_ConditionalStrategiesI_AI.ipynb", "cs1", cs1)
build("L15_ConditionalStrategiesII_AI.ipynb", "cs2", cs2)
