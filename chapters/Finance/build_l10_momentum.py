"""Build L10 · Momentum — from chapters/Finance/L10_DESIGN.md"""
import json, re
C=[]
def md(s): C.append(("markdown", s.strip("\n")))
def co(s): C.append(("code", s.strip("\n")))

md("""
# Momentum: One Signal, All the Way Down

## 🎯 Learning Objectives

By the end of today you will be able to:

1. **Say where a trading signal comes from** — the data, the source, the choices — for the main families
2. **Build a momentum signal from raw returns**, and check it against a reference
3. **Price the construction choices** — lookback, skip, weighting, breakpoints, bucket count
4. **Test whether an effect lives at the stock or the industry level**
5. **Explain why momentum crashes**, and when its market beta turns negative
6. **Specify a signal precisely enough** that a one-character error cannot hide
""")

md("""
## 📋 Today's Plan

1. [Where signals come from](#where)
2. [The claim](#claim)
3. [🔄 Build it from raw returns](#build)
4. [🎯 Prompt it: compute 12-month momentum](#prompt)
5. [The decision tree, priced](#tree)
6. [Stocks or industries?](#ind)
7. [Crashes](#crash)
8. [🛠️ Hands-On: your signal's decision tree](#ho1)
9. [🎯 Challenge: the other end of the horizon](#challenge) — *homework*
10. [Key takeaways](#takeaways)
""")

md("""
---

## 🛠️ Setup
""")

co("""
#@title Setup — run this first
import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt
%matplotlib inline
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = [11, 4]
import warnings; warnings.filterwarnings('ignore')

BASE = "https://raw.githubusercontent.com/amoreira2/UG54/refs/heads/main/assets/data"

panel = pd.read_parquet(f"{BASE}/panel_backbone_1980_2000.parquet")   # raw CRSP
grid  = pd.read_parquet(f"{BASE}/momentum_grid.parquet")              # today's variants, cached
ind49 = pd.read_csv(f"{BASE}/industry49_monthly.csv", index_col=0, parse_dates=True)
ff    = pd.read_csv(f"{BASE}/ff_monthly.csv", index_col=0, parse_dates=True)
L     = pd.read_parquet(f"{BASE}/longshort_29.parquet")

sharpe = lambda x: x.mean() / x.std() * np.sqrt(12)
print(f"panel  {panel.shape[0]:,} stock-months, {panel.date.min():%Y-%m} to {panel.date.max():%Y-%m}")
print(f"UMD    {ff.index[0]:%Y-%m} to {ff.index[-1]:%Y-%m}  (runs past the panel — we need that later)")
""")

# ── §0
md("""
---

## 1 · Where signals come from <a id="where"></a>

For nine lectures you have used signals somebody else built. Today you build one.
First, briefly, the landscape — because your project needs a signal and you
should know what building each family actually costs.

| Family | Example signal | What data | Where | The choices that bite |
|---|---|---|---|---|
| **Value** | book/market, E/P, EV/EBITDA | annual accounting + price | Compustat + CRSP | which fundamental; **when the filing became knowable**; annual or monthly rebalance |
| **Profitability** | gross profit / assets | income statement | Compustat | which profit line; which denominator |
| **Investment** | asset growth | balance sheet | Compustat | over what horizon; scaled by what |
| **Issuance** | change in shares outstanding | share count | CRSP or Compustat | split adjustment — last lecture's leakage trap |
| **Return-based** | momentum, reversal, volatility | **prices only** | CRSP | today |

Two things are true of all of them.

**Signal construction is art, not science.** The recipe *after* the signal —
rank, bucket, weight, go long the top and short the bottom — is the same for
everything, and you learned it in Lecture 3. The signal itself is where any edge
lives, and there is no procedure for it.

**Value's structure is the general one.** A value signal is
`W ∝ F/P` — a fundamental over a price. Buy cheap, sell expensive. Every family
above is an argument about which `F` you believe: book value, earnings, gross
profit, invested capital.

Momentum is the odd one out, and that is exactly why we use it today: **it needs
only prices.** No accounting, no filing dates, no restatements. Which means every
choice we make is a choice about *construction*, not about data — and that is the
subject.
""")

# ── §1
md("""
---

## 2 · The claim <a id="claim"></a>

Momentum is the fact that stocks that have performed **relatively** well in the
past continue to perform **relatively** well, and stocks that have performed
**relatively** poorly continue to perform poorly. Jegadeesh and Titman (1993)
found that ranking on the past 6 to 12 months and holding the top decile against
the bottom earned about 12% a year.

Note the contrast with value, because they are closer than they look. A price
already contains the entire history of returns — that is what a price *is*. So a
valuation ratio is a signal about the *whole* past, and it says buy what has
fallen. Momentum looks at only the last twelve months, and says buy what has
risen.

**Same kind of bet, different windows, opposite directions.** Which window is
right is an empirical question, and by the end of today you will have the answer
for every window between one month and five years.

Here is the construction everybody quotes, from Daniel and Moskowitz:

> *"To form the momentum portfolios, we first rank stocks based on their
> cumulative returns from 12 months before to one month before the formation date
> (i.e., the t−12 to t−2 month returns). We use a one month gap between the end
> of the ranking period and the start of the holding period to avoid the
> short-term reversals documented by Jegadeesh (1990) and Lehmann (1990)."*

Every clause in that sentence is a decision. We are going to take them one at a
time and find out what each is worth.
""")

# ── §2 build
md("""
---

## 🔄 3 · Build it from raw returns <a id="build"></a>

Zero to one hundred. We start from the CRSP panel — `permno`, `date`, `ret`,
`me` — and finish with a monthly track record.

> **🤔 Predict first.** Our shipped `Mom12m` long-short earns about 20% a year.
> When we rebuild it from scratch, how close do you expect to get?
""")

co("""
#@title 🔒 Raw panel to long-short, in one pass
p = panel[panel.shrcd.isin([10, 11]) & panel.exchcd.isin([1, 2, 3])].copy()
p = p.sort_values(['permno', 'date'])

# 1. log returns compound by adding
p['lr'] = np.log1p(p['ret'].clip(lower=-0.9999))

# 2. cumulative return t-12 to t-2: 11 months, then step back one more
p['mom'] = np.expm1(p.groupby('permno')['lr']
                     .transform(lambda s: s.rolling(11).sum().shift(1)))

# 3. rank into deciles each month, on NYSE breakpoints (Lecture 3)
d = p.dropna(subset=['mom', 'ret_fwd', 'me'])
def deciles(x):
    ref = x.loc[x.exchcd == 1, 'mom']
    edges = np.unique(np.quantile(ref, np.linspace(0, 1, 11)))
    edges[0], edges[-1] = -np.inf, np.inf
    return pd.cut(x['mom'], edges, labels=False, duplicates='drop')
d = d.assign(q=d.groupby('date', group_keys=False).apply(deciles))

# 4. value-weight inside each decile, then D10 - D1
dec  = d.groupby(['date', 'q']).apply(lambda x: np.average(x.ret_fwd, weights=x.me)).unstack()
mine = (dec[9] - dec[0]).dropna()

print(f"  ours      mean {mine.mean()*12:+.1%}/yr   Sharpe {sharpe(mine):.2f}")
print(f"  shipped   mean {L['Mom12m'].mean()*12:+.1%}/yr   Sharpe {sharpe(L['Mom12m']):.2f}")
print(f"\\n  correlation with the shipped series: "
      f"{pd.concat([mine, L['Mom12m']], axis=1).dropna().corr().iloc[0,1]:.3f}")
""")

md("""
### Same mean, same Sharpe ratio, correlation 0.11

Stop on that. The two series agree on every summary statistic and disagree
month by month. If you had built this and seen 0.11, you would reasonably
conclude you had built a *different* strategy.

You have not. You have built the same strategy with a different date on it.

Our `mine` is indexed by the month the portfolio was **formed**. The shipped
series is indexed by the month the return was **earned** — one month later,
because `ret_fwd` at date *t* is the return you collect during *t+1*.
""")

co("""
#@title 🔒 Move the index one month and look again
mine.index = mine.index + pd.offsets.MonthEnd(1)          # date it by the month EARNED
j = pd.concat([mine.rename('ours'), L['Mom12m'].rename('shipped')], axis=1).dropna()
print(f"  correlation after aligning: {j.corr().iloc[0,1]:.3f}   ({len(j)} months)")
print(j.head(3).to_string())
""")

md("""
> **📌 Two series can match on every statistic and still be misaligned.**
>
> A correlation is the only summary that notices. Whenever you build something
> that should replicate a reference, correlate it — do not compare means. This is
> the `ret_fwd` question from Lecture 2, arriving as a bug rather than a warning.
""")

# ── prompt moment
md("""
### 🎯 Prompt it — compute 12-month momentum <a id="prompt"></a>

Everything below depends on this one signal being right, so it is worth being
slow about.

> **🤔 The question.** *"Compute 12-month momentum for each stock."*
>
> Write the prompt. There are at least four decisions buried in that sentence,
> and one of them is a one-character error that will not raise, warn, or look
> wrong.
""")

co("""
# === YOUR TURN ===
MY_PROMPT = \"\"\"
                                    ← write your prompt here
\"\"\"

# ---- paste the AI's code below ----

""")

co("""
#@title 🔒 Check — five readings, all of them valid code
def build(sig_series):
    dd = p.assign(s=sig_series).dropna(subset=['s', 'ret_fwd', 'me'])
    def cut(x):
        ref = x.loc[x.exchcd == 1, 's']
        e = np.unique(np.quantile(ref, np.linspace(0, 1, 11))); e[0], e[-1] = -np.inf, np.inf
        return pd.cut(x['s'], e, labels=False, duplicates='drop')
    dd = dd.assign(q=dd.groupby('date', group_keys=False).apply(cut))
    r  = dd.groupby(['date', 'q']).apply(lambda x: np.average(x.ret_fwd, weights=x.me)).unstack()
    return (r[9] - r[0]).dropna()

g = p.groupby('permno')
readings = {
 "t-12 to t-2  (11 months, skip 1)": np.expm1(g['lr'].transform(lambda s: s.rolling(11).sum().shift(1))),
 "t-12 to t-1  (12 months, no skip)": np.expm1(g['lr'].transform(lambda s: s.rolling(12).sum().shift(1))),
 "t-11 to t     (includes this month)": np.expm1(g['lr'].transform(lambda s: s.rolling(12).sum())),
 "sums simple returns, not compounded": g['ret'].transform(lambda s: s.rolling(11).sum().shift(1)),
 "shift(-1) instead of shift(1)":      np.expm1(g['lr'].transform(lambda s: s.rolling(11).sum().shift(-1))),
}
print("«Compute 12-month momentum for each stock»\\n")
for lab, s in readings.items():
    r = build(s)
    print(f"  {lab:38s} mean {r.mean()*12:+8.1%}   Sharpe {sharpe(r):+.2f}")
""")

md("""
### A Sharpe ratio of 6.58 is not a discovery

The last row is `shift(-1)` where the standard is `shift(1)`. One character. It
ranks stocks on a window that runs one month into the future, so the "signal"
partly contains the return it is predicting.

It does not raise. It does not warn. It returns a clean DataFrame and a track
record of **+144% a year**.

The other three are not errors at all — they are defensible readings of the same
English sentence, and they span a Sharpe ratio from 0.70 to 1.03. Including the
current month costs you a third of the strategy, which is the short-term reversal
Daniel and Moskowitz skip the month to avoid.

> **⚠️ The only defence against `shift(-1)` is knowing roughly what the answer
> should be before you compute it.** No test catches it. No error message
> mentions it. You catch it because 6.58 is not a number this strategy produces,
> and you knew that in advance.
""")

# ── §3 the grid
md("""
---

## 4 · The decision tree, priced <a id="tree"></a>

Now the choices. Each one is defensible, each has a literature behind it, and we
can put a number on all of them. These are precomputed — the code is the same
`build()` you just ran, in a loop.
""")

co("""
#@title 🔒 How far back? Sharpe against the lookback window
J = [1, 3, 6, 9, 11, 17, 23, 35, 47, 59]
sh = [sharpe(grid[f'J{j}_s1'].dropna()) for j in J]

fig, ax = plt.subplots()
ax.plot(J, sh, 'o-', color='#333333', lw=1.4, ms=5)
ax.axvline(11, color='#b03030', ls='--', lw=0.9)
ax.annotate('the standard\\n(11 months)', xy=(11, max(sh)), xytext=(6, -34),
            textcoords='offset points', fontsize=9, color='#b03030')
ax.set_xlabel('lookback window, months'); ax.set_ylabel('Sharpe ratio')
ax.set_title('Same recipe, different window', loc='left', fontsize=11)
plt.tight_layout(); plt.show()

for j, s in zip(J, sh): print(f"  J = {j:2d} months   Sharpe {s:+.2f}")
""")

md("""
The peak is at eleven months, exactly where Jegadeesh and Titman put it, and it
falls off hard on both sides. Six months gets you 0.71; seventeen months gets you
0.51. **Half the effect lives in the choice of window.**

Now the part worth arguing about. The textbook picture of this chart is a *wave*:
reversal at short horizons, continuation in the middle, and reversal again at
three to five years — DeBondt and Thaler (1985), winners eventually lose.

**We do not see that.** At 35, 47 and 59 months our Sharpe ratios are +0.37,
+0.47 and +0.48 — weaker than the peak, but still *positive*, still buying past
winners. Nothing turns over.

Three possibilities, and it is Lecture 9's list arriving on a chart you built
yourself: the long-horizon reversal was never there; it was there and has decayed
since DeBondt and Thaler's 1926–1982 sample; or our construction differs from
theirs in a way that matters. **The homework makes you take a position.**
""")

co("""
#@title 🔒 What is the skip month worth?
for k in [0, 1, 2, 3, 6]:
    s = grid[f'J11_s{k}'].dropna()
    star = "   <- the standard" if k == 1 else ""
    print(f"  skip {k} month(s)   mean {s.mean()*12:+7.1%}   Sharpe {sharpe(s):+.2f}{star}")
""")

md("""
**Not skipping costs 38% of the Sharpe ratio** — 0.64 against 1.03. That is one
`.shift()`, and it is the single most valuable line in the construction.

Skipping *more* than one month costs you too, and for the opposite reason: by
month six you have thrown away the signal along with the noise.
""")

co("""
#@title 🔒 Weighting, breakpoints, and how many buckets
cols = ['VW, NYSE bp, deciles', 'EW, NYSE bp, deciles',
        'VW, ALL-stock bp, deciles', 'EW, ALL-stock bp, deciles',
        'VW, NYSE bp, terciles', 'VW, NYSE bp, quintiles', 'VW, NYSE bp, 20 groups']
t = pd.DataFrame({c: {'mean/yr': grid[c].mean()*12, 'vol': grid[c].std()*np.sqrt(12),
                      'Sharpe': sharpe(grid[c])} for c in cols}).T
print(t.to_string(formatters={'mean/yr': '{:+.1%}'.format, 'vol': '{:.1%}'.format,
                              'Sharpe': '{:+.2f}'.format}))
print(f"\\n  best {t.Sharpe.max():.2f}   worst {t.Sharpe.min():.2f}   "
      f"range {t.Sharpe.max()-t.Sharpe.min():.2f}")
""")

md("""
### Same signal. Same data. Sharpe ratio from 0.45 to 1.13.

Nothing in that table is a mistake. Every row appears in published work.

Two of them are worth naming:

- **All-stock breakpoints beat NYSE breakpoints** — 1.13 against 1.03 — and the
  volatility goes from 19.5% to 25.1%. Cutting deciles on every listed stock puts
  the microcaps in the extreme buckets, which is Lecture 3's warning with a price
  on it. You are being paid for illiquidity, not momentum.
- **Terciles 0.45, deciles 1.03, twenty groups 1.09.** Finer buckets mean a purer
  signal and fewer stocks to diversify across. The gain flattens after deciles,
  which is why deciles are the convention.

> **📌 The construction is not a detail, it is most of the result.**
>
> And now count: seven constructions, all defensible, all tried. Lecture 8's
> Bonferroni bar was for the number of things you *tried*, not the number you
> report. If you search this grid and report the best cell, you have run seven
> tests and must say so.
""")

# ── §4 industries
md("""
---

## 5 · Stocks or industries? <a id="ind"></a>

A real question about what momentum *is*. When the winner decile beats the loser
decile, is that a hundred individual stocks with individual momentum — or is it
mostly that some *industries* went up and their stocks came along?

The question matters for trading. If it is industries, you can run it with 49
liquid industry portfolios instead of a thousand single stocks, at a fraction of
the cost.

Moskowitz and Grinblatt (1999) asked exactly this. Let us build it.
""")

co("""
#@title 🔒 Industry momentum — same rule, 49 portfolios instead of 3,000 stocks
lr49 = np.log1p(ind49.clip(lower=-0.9999))
sig49 = np.expm1(lr49.rolling(11).sum().shift(1))       # identical t-12..t-2 rule
rank  = sig49.rank(axis=1, ascending=False)
IM = (ind49.where(rank <= 5).mean(axis=1) -             # top 5 industries
      ind49.where(rank >= 45).mean(axis=1)).dropna()    # short bottom 5

SM = grid['J11_s1'].dropna()
j  = pd.concat([SM.rename('stock'), IM.rename('industry')], axis=1).dropna()

print(f"  stock momentum      Sharpe {sharpe(j.stock):.2f}   mean {j.stock.mean()*12:+.1%}/yr")
print(f"  industry momentum   Sharpe {sharpe(j.industry):.2f}   mean {j.industry.mean()*12:+.1%}/yr")
print(f"  correlation         {j.corr().iloc[0,1]:.2f}")
""")

md("""
Both work, and they are **0.73 correlated**. So they are largely the same trade,
and the interesting question is which one is the passenger.

That is the factor ladder from Lecture 4, and it runs in both directions.
""")

co("""
#@title 🔒 Run the ladder both ways
a = sm.OLS(j.stock,    sm.add_constant(j.industry)).fit()
b = sm.OLS(j.industry, sm.add_constant(j.stock)).fit()
X = pd.concat([j.industry, ff.loc[j.index, ['Mkt-RF', 'SMB', 'HML']]], axis=1)
c = sm.OLS(j.stock, sm.add_constant(X)).fit()

print(f"  {'stock on industry':32s} alpha {a.params.iloc[0]*12:+7.1%}/yr   t {a.tvalues.iloc[0]:+.2f}")
print(f"  {'industry on stock':32s} alpha {b.params.iloc[0]*12:+7.1%}/yr   t {b.tvalues.iloc[0]:+.2f}")
print(f"  {'stock on industry + FF3':32s} alpha {c.params.iloc[0]*12:+7.1%}/yr   t {c.tvalues.iloc[0]:+.2f}")
""")

md("""
### The asymmetry is the answer

Stock momentum survives controlling for industry momentum: **+11.5% a year,
t = 3.76**, and it holds up with the Fama-French three-factor model on top
(+14.4%, t = 4.47).

Industry momentum does **not** survive controlling for stock momentum: −2.7% a
year, t = −0.88. Once you own individual momentum, industry momentum adds
nothing.

> **📌 Momentum is a stock effect that shows up at the industry level — not an
> industry effect that shows up in stocks.**

**And we just got the opposite of the published paper.** Moskowitz and Grinblatt
concluded that industry momentum *subsumes* individual momentum. We find the
reverse, with the same test.

Do not paper over that. Last lecture had three explanations for a gap like this
and no way to choose between them, and this one has some candidates we can
actually name: our sample is 1980–2000 and theirs was 1963–1995; we use 49
industries and they used 20; and they industry-adjust returns at the stock level
while we compare two portfolios. Any of the three could do it.

Which means the honest statement is that we do not know — and that finding out
would be a real piece of work, not a rerun.

> **⚠️ What we cannot do with this data.** *Industry-neutral* momentum — ranking
> each stock against its own industry peers rather than against everything —
> needs a stock-level industry code, and our panel does not carry one. That is a
> data limitation, not a result. If your project wants it, you need SIC codes.
""")

# ── §5 crashes
md("""
---

## 6 · Crashes <a id="crash"></a>

Our panel stops in 2000, which is a problem, because the thing you most need to
know about momentum happened in 2009. The Fama-French momentum factor runs to
2026, so we use that.
""")

co("""
#@title 🔒 The 2009 crash
umd, mkt = ff['UMD'].dropna(), ff['Mkt-RF']
cum = (1 + umd).cumprod(); dd = cum / cum.cummax() - 1

print(f"  UMD {umd.index[0]:%Y-%m} to {umd.index[-1]:%Y-%m}:  "
      f"mean {umd.mean()*12:+.1%}/yr   Sharpe {sharpe(umd):.2f}   maxDD {dd.min():.1%}\\n")
for y in ['2001', '2009', '2023']:
    print(f"    {y}:  momentum {(1+umd.loc[y]).prod()-1:+7.1%}    "
          f"market {(1+mkt.loc[y]).prod()-1:+7.1%}")
print(f"\\n  worst single month: {umd.min():.1%} in {umd.idxmin():%Y-%m}")
""")

md("""
**2009: momentum lost 52.9% while the market gained 28.3%.** And it happened
again in 2023, smaller and the same shape.

Here is the mechanism, and it is not bad luck. After a market crash, the losers —
the short leg — are beaten-down high-beta stocks. When the market turns, those
are exactly the stocks that scream. So a strategy that is market-neutral *on
average* turns out to be **short the market** at the one moment being short the
market is fatal.
""")

co("""
#@title 🔒 Momentum's beta depends on the state you are in
bear = ((1 + mkt).rolling(24).apply(np.prod, raw=True) - 1) < 0
for lab, mask in [('after a 24-month BEAR market', bear), ('after a 24-month BULL market', ~bear)]:
    m_, k_ = umd[mask.fillna(False)], mkt[mask.fillna(False)]
    beta = sm.OLS(m_, sm.add_constant(k_)).fit().params.iloc[1]
    print(f"  {lab:30s} n={len(m_):4d}   beta {beta:+.2f}   Sharpe {sharpe(m_):+.2f}")

vs = (umd / umd.rolling(6).std().shift(1) * umd.std()).dropna()   # scale by trailing vol
c2 = (1 + vs).cumprod()
print(f"\\n  plain momentum        Sharpe {sharpe(umd):.2f}   maxDD {dd.min():.1%}")
print(f"  scaled by trailing vol Sharpe {sharpe(vs):.2f}   maxDD {(c2/c2.cummax()-1).min():.1%}")
""")

md("""
**−0.75 after a bear market, +0.06 after a bull market.** The average beta of
roughly zero is an average of two very different regimes, and reporting it hides
the only thing that matters.

That is Lecture 9 in return space. Momentum pays you for holding something that
loses badly in exactly the state where losses hurt — and the premium is the
payment for that, not a free lunch with an occasional bad year.

Dividing the position by its own trailing volatility takes the Sharpe ratio from
0.43 to 0.73 and cuts the drawdown by twenty points. One line, and it is the
crude version of what we will do properly at meeting 19.
""")

# ── hands-on
md("""
---

## 🛠️ Hands-On: Your Signal's Decision Tree <a id="ho1"></a>

Your group's signal came pre-built. Somebody made every choice in §4 on your
behalf and did not tell you.

> **🤔 Predict first.** If you re-cut your signal on all-stock breakpoints instead
> of NYSE breakpoints, does the Sharpe ratio go up or down? Why?
""")

co("""
# === EDIT + YOUR TURN ===
MY_SIGNAL = "GP"      # ← your group's signal

sig = pd.read_parquet(f"{BASE}/signals/{MY_SIGNAL}.parquet")
print(sig.columns.tolist(), sig.shape)

# Merge your signal onto the panel, then rebuild the long-short two ways:
# NYSE breakpoints and all-stock breakpoints. Reuse build() from earlier.
mine_nyse = ____      # hint: adapt build(), which already uses NYSE breakpoints
mine_all  = ____      # hint: cut on x['s'] instead of x.loc[x.exchcd==1,'s']

print(f"  NYSE breakpoints      Sharpe {sharpe(mine_nyse):+.2f}")
print(f"  all-stock breakpoints Sharpe {sharpe(mine_all):+.2f}")
""")

md("""
### Compare with the room

- **Which way did it move, and how far?** For momentum the gap was 1.03 to 1.13,
  and the volatility went up 6 points. If yours moves more, your signal is more
  concentrated in small stocks than momentum is.
- **How many constructions have you now tried?** Count honestly. That number goes
  in your project report, and it moves the bar your result has to clear.
- **Which one will you report?** Decide the rule before you look, which is the
  whole of Lecture 8.
""")

# ── challenge
md("""
---

## 🎯 Challenge: The Other End of the Horizon <a id="challenge"></a>

*Homework — due before the next class.*

In class the lookback chart stayed positive all the way out to five years, which
is not what the literature says should happen. Settle it properly.

**Long-term reversal** (DeBondt and Thaler, 1985): rank stocks on their
cumulative return from **t−60 to t−13** — five years back, ending one year ago,
so the momentum window is excluded entirely — and go long the losers, short the
winners. Note the sign is flipped relative to momentum: **D1 minus D10**.

If the textbook holds in our sample, this should make money.

Use the cached `grid` where you can; build what you cannot. Everything is
value-weighted on NYSE breakpoints unless stated.

### Q1 — Does the long horizon reverse?

Build the t−60 to t−13 signal from the panel — a 48-month window, skipped by 12 —
and report the **Sharpe ratio of the D1 − D10 long-short** (losers minus winners).

Report what you get, including if it is negative or near zero. A null is a result
here, and it is the one the memo has to deal with.

> **📌 Required variable names:**
> ```python
> ltr_sharpe = ____   # Sharpe ratio of the D1 - D10 long-term reversal strategy
> ```
""")
co("""
# Your work here


ltr_sharpe = ____

print(f"long-term reversal Sharpe: {ltr_sharpe:.2f}")
""")

md("""
### Q2 — Is it just momentum with a minus sign?

Regress your long-term reversal series on **momentum** (`grid['J11_s1']`) and
report the **alpha, annualised, as a decimal** (0.05 means +5%/yr).

If reversal is simply the opposite of momentum, the alpha should be near zero
once you control for it. Find out.

> **📌 Required variable names:**
> ```python
> ltr_alpha = ____    # annualised alpha vs momentum, decimal
> ```
""")
co("""
# Your work here


ltr_alpha = ____

print(f"alpha vs momentum: {ltr_alpha:+.1%}/yr")
""")

md("""
### Q3 — The skip, again

Rebuild the same 48-month window with **no skip at all** — t−48 to t−1 — and
report its Sharpe ratio, still D1 − D10.

For momentum the skip was worth 0.39 of Sharpe ratio. Predict before you run it
whether a skip matters *more* or *less* at a four-year horizon — you are dropping
12 months out of 48 rather than 1 out of 12, so the discarded fraction is much
larger, but so is what remains. The reason for what you find is worth more than
the number.

> **📌 Required variable names:**
> ```python
> ltr_noskip = ____   # Sharpe of the no-skip version, D1 - D10
> ```
""")
co("""
# Your work here


ltr_noskip = ____

print(f"no-skip long-term reversal Sharpe: {ltr_noskip:.2f}")
""")

md("""
### Q4 — The memo

> **📝 Your task — maximum eight sentences.**
>
> Your PM has read that "momentum and reversal are the same trade at different
> horizons" and wants to know whether to run both.
>
> Say what you found at the five-year horizon and whether it survives controlling
> for momentum. Say what the skip did here compared with what it did at twelve
> months, and give the reason, not just the number. Then take a position on the
> disagreement: **the published result says long-horizon losers beat winners, and
> our sample does not show it — is that decay, a construction difference, or was
> it never there?** Say which you favour and what evidence would change your mind.
> Finish with the practical question: you have now built this strategy at ten
> horizons, two skip settings and two sets of breakpoints. What t-statistic would
> you need before believing any single one of them?
""")
co("""
MEMO = \"\"\"
Write your memo here. Don't delete the surrounding triple quotes.
\"\"\"
print(MEMO)
""")

md("""
---

## 📤 Submission <a id="submit"></a>
""")
co("""
# === 📤 SUBMISSION CELL — Run this last ===
import json, base64, hashlib, datetime as dt

required = ["ltr_sharpe", "ltr_alpha", "ltr_noskip", "MEMO"]
missing = [v for v in required if v not in globals()]
if missing:
    raise NameError(f"\\n❌ Missing before submission: {missing}")

payload = {
    "assignment": "L10_Momentum_AI",
    "ts": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
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
print("Submission form: https://forms.gle/yazZ8bbatL87jdJi7")
""")

md("""
---

## 🧠 Key Takeaways <a id="takeaways"></a>

1. **The recipe is the same for every signal** — rank, bucket, weight, long the
   top, short the bottom. The signal is where the edge is, and there is no
   procedure for finding one.

2. **Momentum needs only prices**, which is why it has a hundred variants: no
   accounting data means nothing to blame but your construction.

3. **Momentum and value are the same bet on different windows.** A price contains
   the whole return history; momentum looks at twelve months.

4. **Same signal, same data, Sharpe 0.45 to 1.13.** Lookback, skip, weighting,
   breakpoints, bucket count. None of them is a mistake.

5. **The skip month is worth 0.39 of Sharpe ratio** — one `.shift()`, and the
   line an AI will not write unless asked.

6. **A Sharpe of 6.58 is a bug, not a discovery.** `shift(-1)` for `shift(1)`
   does not raise. You catch it by knowing the answer's rough size in advance.

7. **Momentum is a stock effect that appears at the industry level**, not the
   reverse — alpha +11.5%/yr against industry momentum, while industry momentum
   has none against it. Which is the opposite of the published paper, and we
   cannot say why.

8. **Momentum's beta is −0.75 after a bear market and +0.06 after a bull one.**
   The average of zero describes neither. 2009: −52.9% while the market made
   +28.3%.

9. **The lookback chart does not reverse at long horizons in our sample** —
   +0.48 at five years where the textbook says negative. Decay, construction, or
   never there: the same three explanations, and the same inability to choose.

10. **Two series can agree on every statistic and be misaligned.** Correlate, do
    not compare means.

---

### Next class

You have priced the construction choices. Next we price the *trading* — what it
costs to actually hold a portfolio that turns over this fast, and what is left of
a 20% return once you pay for it.
""")

md("""
---

## 📎 Appendix <a id="appendix"></a>
""")
co("""
# ═══════════════════════════════════════════════════════════════════════
# 📎 APPENDIX — every variant in one table
# ═══════════════════════════════════════════════════════════════════════
tab = pd.DataFrame({c: {'mean/yr': grid[c].mean()*12,
                        'vol': grid[c].std()*np.sqrt(12),
                        'Sharpe': sharpe(grid[c].dropna())} for c in grid.columns}).T
print(tab.to_string(formatters={'mean/yr': '{:+.1%}'.format, 'vol': '{:.1%}'.format,
                                'Sharpe': '{:+.2f}'.format}))
""")

nb={"cells":[{"cell_type":t,"metadata":{},"source":s.splitlines(keepends=True),
              **({"outputs":[],"execution_count":None} if t=="code" else {})} for t,s in C],
    "metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},
                "language_info":{"name":"python","version":"3.11"}},
    "nbformat":4,"nbformat_minor":5}
p="chapters/Finance/L10_Momentum_AI.ipynb"
json.dump(nb,open(p,"w"),indent=1)
w=sum(len(re.findall(r"[A-Za-z'-]+",s)) for t,s in C if t=="markdown")
cut=next(i for i,(t,s) in enumerate(C) if '## 🎯 Challenge' in s)
lec=sum(len(re.findall(r"[A-Za-z'-]+",s)) for t,s in C[:cut] if t=="markdown")
print(f"✅ {p}  {len(C)} cells  {w} md words total")
print(f"   lectured {lec} = {lec/1417:.2f} sessions")
