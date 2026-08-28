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

# ── §3 build from the paper
md("""
---

## 🔄 3 · Build it from the paper <a id="build"></a>

Zero to one hundred, and we start where you would actually start: with what the
authors wrote. Here is Daniel and Moskowitz describing their construction.

> *"To form the momentum portfolios, we first rank stocks based on their
> cumulative returns from 12 months before to one month before the formation
> date (i.e., the t−12 to t−2 month returns). We use a one month gap between the
> end of the ranking period and the start of the holding period to avoid the
> short-term reversals documented by Jegadeesh (1990) and Lehmann (1990). In
> particular we will focus on the 10% and 90% quantiles of the signal
> distribution."*

That paragraph is the entire specification. Build it.

<details>
<summary><b>Stuck? The recipe in words</b> — but try the prompt first</summary>

<br>

1. Keep common shares on the three main exchanges — `shrcd` in (10, 11), `exchcd` in (1, 2, 3).
2. For each stock, compound its returns over a window of months.
3. Step the window back so the most recent completed month is not in it.
4. Each month, rank stocks on that signal and cut into ten groups on NYSE breakpoints.
5. Value-weight inside each group, then take the top group minus the bottom group.

`panel` has `permno`, `date`, `ret`, `me`, `exchcd`, `shrcd`, and `ret_fwd` — the
return earned in the month *after* `date`, so tradability is already handled for
you. Every decision left is about the signal.

</details>
""")

co('''
# === YOUR TURN ===
MY_PROMPT = """
                                    ← write your prompt here
"""

# ---- paste the AI's code below, then compare with the cell after ----
''')

md('''
> **🤔 Before you run the check.** Write down the Sharpe ratio you expect. The
> shipped `Mom12m` long-short earns about 20% a year, so you have an anchor.
''')

co('''
#@title 🔒 Reference implementation — four steps
p = panel[panel.shrcd.isin([10, 11]) & panel.exchcd.isin([1, 2, 3])].copy()
p = p.sort_values(['permno', 'date'])
p['1+ret'] = p['ret'] + 1

# --- 1 --- compound each stock's returns over 11 months: (1+r)(1+r)...(1+r)
p['cumret'] = (p.groupby('permno')['1+ret']
                 .rolling(11, min_periods=11).apply(np.prod, raw=True)
                 .reset_index(level=0, drop=True))

# --- 2 --- step it back one month: the clause everyone drops (see below)
p['signal'] = p.groupby('permno')['cumret'].shift(1)

# --- 3 --- each month, cut into deciles on NYSE breakpoints (Lecture 3)
d = p.dropna(subset=['signal', 'ret_fwd', 'me'])
def deciles(x):
    edges = np.unique(np.quantile(x.loc[x.exchcd == 1, 'signal'], np.linspace(0, 1, 11)))
    edges[0], edges[-1] = -np.inf, np.inf
    return pd.cut(x['signal'], edges, labels=False, duplicates='drop')
d = d.assign(group=d.groupby('date', group_keys=False).apply(deciles))

# --- 4 --- value-weight inside each decile, then top minus bottom
dec  = d.groupby(['date', 'group']).apply(lambda x: np.average(x.ret_fwd, weights=x.me)).unstack()
mine = (dec[9] - dec[0]).dropna()
mine.index = mine.index + pd.offsets.MonthEnd(1)     # date it by the month EARNED

print(f"  ours      mean {mine.mean()*12:+.1%}/yr   Sharpe {sharpe(mine):.2f}")
print(f"  shipped   mean {L['Mom12m'].mean()*12:+.1%}/yr   Sharpe {sharpe(L['Mom12m']):.2f}")
print(f"  correlation {pd.concat([mine, L['Mom12m']], axis=1).dropna().corr().iloc[0,1]:.3f}")
''')

md("""
### Wrap it, so the decisions become arguments

Those four steps are the whole recipe, and every choice we are about to argue
about is one of them. So put them in a function and let the choices be
**arguments** — then changing your mind is one keystroke, not one edit.

Two functions, because step 3 and 4 are not about momentum at all. Sorting a
signal into weighted portfolios is what we did to book-to-market in Lecture 3 and
what you will do to your own signal in a moment.
""")

co("""
#@title 🔒 The two functions we use for the rest of the lecture
def sort_portfolios(df, signal='signal', ngroups=10, weights='value', breakpoints='nyse'):
    \"\"\"Rank a signal into ngroups each month, weight inside each, return top minus bottom.
    Works on ANY signal column — this is Lecture 3's recipe, wrapped.\"\"\"
    d = df.dropna(subset=[signal, 'ret_fwd', 'me']).copy()
    def bucket(x):
        ref = x.loc[x.exchcd == 1, signal] if breakpoints == 'nyse' else x[signal]
        e = np.unique(np.quantile(ref, np.linspace(0, 1, ngroups + 1)))
        e[0], e[-1] = -np.inf, np.inf
        return pd.cut(x[signal], e, labels=False, duplicates='drop')
    d['group'] = d.groupby('date', group_keys=False).apply(bucket)
    w = (lambda x: np.average(x.ret_fwd, weights=x.me)) if weights == 'value' else \\
        (lambda x: x.ret_fwd.mean())
    dec = d.groupby(['date', 'group']).apply(w).unstack()
    ls = (dec[ngroups - 1] - dec[0]).dropna()
    ls.index = ls.index + pd.offsets.MonthEnd(1)      # date it by the month EARNED
    return ls

def momentum(df, lookback=11, skip=1, **kwargs):
    \"\"\"Cumulative return over `lookback` months, ending `skip` months before formation.
    lookback=11, skip=1 is the standard: the signal spans t-12 to t-2 counting from
    the month whose return you earn.\"\"\"
    d = df.copy()
    d['cumret'] = (d.groupby('permno')['1+ret']
                     .rolling(lookback, min_periods=lookback).apply(np.prod, raw=True)
                     .reset_index(level=0, drop=True))
    d['signal'] = d.groupby('permno')['cumret'].shift(skip)
    return sort_portfolios(d, **kwargs)

std = momentum(p)                      # the standard construction, ~2 seconds
print(f"momentum(lookback=11, skip=1)   mean {std.mean()*12:+.1%}/yr   Sharpe {sharpe(std):.2f}")
""")

md('''
### Did your version skip the month?

If it did not, you are in good company — it is one subordinate clause in the
middle of a long sentence, and it reads like housekeeping. It is not.

**Leaving that month in costs 0.32 of Sharpe ratio: 1.03 becomes 0.70.**

And notice what the skip is *not* for. It is not about making the strategy
tradable — `ret_fwd` already does that, and every version we have built is
implementable. The month is dropped for an economic reason, and the authors say
it outright: **to avoid the short-term reversals.**

So look at what the discarded month does on its own. Sort stocks on last month's
return, hold for one month.
''')

co('''
#@title 🔒 The month momentum throws away, traded on its own
print("buy last month's LOSERS, short last month's winners  (D1 - D10)\\n")
for w in ['value', 'equal']:
    for bp in ['nyse', 'all']:
        r = -sort_portfolios(p.assign(signal=p['ret']), weights=w, breakpoints=bp)
        print(f"  {w:5s}-weighted, {bp:4s} breakpoints    mean {r.mean()*12:+7.1%}   "
              f"Sharpe {sharpe(r):+.2f}")
''')

md('''
### Momentum and reversal are opposite bets one month apart

Last month's losers beat last month's winners. Equal-weighted that is a **1.54**
Sharpe ratio — one of the largest numbers in this course — and it is one of our
29 strategies, `STreversal`.

Value-weighted it is **0.08**, essentially nothing. Reversal lives in small,
illiquid stocks, where much of what looks like a price move is the bid-ask spread
bouncing. Weight by market cap and it disappears.

Now put the two together. A momentum signal that includes last month is a
momentum bet **plus** a reversal bet pointing the other way. If that is the
mechanism, the skip should be worth more exactly where reversal is stronger.
''')

co('''
#@title 🔒 Does the cost of not skipping track the strength of reversal?
p['no_skip'] = (p.groupby('permno')['1+ret']
                  .rolling(12, min_periods=12).apply(np.prod, raw=True)
                  .reset_index(level=0, drop=True))
print(f"{'construction':22s}{'reversal':>10s}{'skip':>8s}{'no skip':>9s}{'cost':>8s}")
for w in ['value', 'equal']:
    for bp in ['nyse', 'all']:
        rev = sharpe(-sort_portfolios(p.assign(signal=p['ret']), weights=w, breakpoints=bp))
        a   = sharpe(sort_portfolios(p, weights=w, breakpoints=bp))
        b   = sharpe(sort_portfolios(p.assign(signal=p['no_skip']), weights=w, breakpoints=bp))
        print(f"  {w+'/'+bp:20s}{rev:>10.2f}{a:>8.2f}{b:>9.2f}{b-a:>8.2f}")
''')

md('''
Reversal runs from 0.08 to 1.56 across the four constructions, and the cost of
leaving the month in runs from −0.30 to −0.58, in the same order. The mechanism
is not asserted, it is visible.

> **📌 One clause in an abstract was worth a third of the strategy.**
>
> Not because of a coding rule, but because a different anomaly lives in that
> month and points the other way. You cannot get that from the code, and you
> cannot get it from a prompt that says *"compute 12-month momentum"*. You get it
> from reading why the authors did what they did.

One thing the skip is *not* is an excuse to skip more. Month t−1 is contaminated;
month t−2 is signal — and §4 puts a number on that too.
''')

md("""
### Three other ways to misread the same sentence

The skip is the clause people drop. These are the ones they get wrong without
noticing — same instruction, same valid-looking code.
""")

co("""
#@title 🔒 Same request, four readings
print("«Compute 12-month momentum for each stock»\\n")
for lb, sk, lab in [(11,  1, "t-12 to t-2  (the standard)"),
                    (12,  1, "t-12 to t-1  (12 months, still skipped)"),
                    (11, -1, "shift(-1) instead of shift(1)")]:
    r = momentum(p, lookback=lb, skip=sk)
    print(f"  {lab:42s} mean {r.mean()*12:+8.1%}   Sharpe {sharpe(r):+.2f}")

q = p.copy()
q['cumret'] = (q.groupby('permno')['ret'].rolling(11, min_periods=11).sum()
                .reset_index(level=0, drop=True))
q['signal'] = q.groupby('permno')['cumret'].shift(1)
r = sort_portfolios(q)
print(f"  {'sums returns instead of compounding':42s} mean {r.mean()*12:+8.1%}   Sharpe {sharpe(r):+.2f}")
""")

md("""
### A Sharpe ratio of 6.58 is not a discovery

The third row is `shift(-1)` where the standard is `shift(1)`. One character. It
ranks stocks on a window running one month into the future, so the signal partly
contains the return it is predicting.

It does not raise. It does not warn. It returns a clean DataFrame and a track
record of **+144% a year**.

> **⚠️ No test catches this.** You catch it because 6.58 is not a number this
> strategy produces, and you knew that before you ran it. That is the whole
> argument for writing down your expected answer first.
""")

md("""
---

## 4 · The decision tree, priced <a id="tree"></a>

Now the choices. Each is defensible, each has a literature behind it, and each is
one argument to `momentum()`. Nothing below is precomputed — every number comes
from the function you just read, called in a loop.
""")

co("""
#@title 🔒 How far back? Sharpe against the lookback window  (~20 seconds)
J  = [1, 3, 6, 9, 11, 17, 23, 35, 47, 59]
sh = [sharpe(momentum(p, lookback=j, skip=1)) for j in J]

fig, ax = plt.subplots()
ax.plot(J, sh, 'o-', color='#333333', lw=1.4, ms=5)
ax.axvline(11, color='#b03030', ls='--', lw=0.9)
ax.annotate('the standard\\n(11 months)', xy=(11, max(sh)), xytext=(6, -34),
            textcoords='offset points', fontsize=9, color='#b03030')
ax.set_xlabel('lookback window, months'); ax.set_ylabel('Sharpe ratio')
ax.set_title('Same recipe, different window', loc='left', fontsize=11)
plt.tight_layout(); plt.show()

for j, v in zip(J, sh): print(f"  lookback = {j:2d} months   Sharpe {v:+.2f}")
""")

md("""
The peak is at eleven months, exactly where Jegadeesh and Titman put it, and it
falls off hard on both sides. Six months gets you 0.71; seventeen months gets you
0.51. **Half the effect lives in the choice of window** — and that is on top of
the 0.32 the skip was worth in §3.

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
#@title 🔒 Weighting, breakpoints, and how many buckets  (~15 seconds)
variants = {
 'VW, NYSE bp, deciles'      : dict(),
 'EW, NYSE bp, deciles'      : dict(weights='equal'),
 'VW, ALL-stock bp, deciles' : dict(breakpoints='all'),
 'EW, ALL-stock bp, deciles' : dict(weights='equal', breakpoints='all'),
 'VW, NYSE bp, terciles'     : dict(ngroups=3),
 'VW, NYSE bp, quintiles'    : dict(ngroups=5),
 'VW, NYSE bp, 20 groups'    : dict(ngroups=20),
}
rows = {}
for lab, kw in variants.items():
    r = momentum(p, **kw)
    rows[lab] = {'mean/yr': r.mean()*12, 'vol': r.std()*np.sqrt(12), 'Sharpe': sharpe(r)}
t = pd.DataFrame(rows).T
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

## 5 · Within industries, or across them? <a id="ind"></a>

A real question about what momentum *is*. When the winner decile beats the loser
decile, which of these are you actually being paid for?

- **Across industries.** Some *industries* went up and their stocks came along.
  Your winner decile is full of whatever sector ran, and you are making a sector
  bet with extra steps.
- **Within industries.** Inside every industry, the stocks that beat their own
  peers keep beating them. Your winner decile is full of relative winners, and
  the industry mix is incidental.

These are different trades with different costs, and they are not the same
strategy at all.

The question matters for trading. If it is across, you can run the whole thing
with 49 liquid industry ETFs instead of a thousand single stocks, at a fraction
of the cost. If it is within, you cannot.

Moskowitz and Grinblatt (1999) asked exactly this. We will do it twice — first
the easy way, with industry portfolios, then properly, at the stock level.

### 5a · Across industries — the easy half
""")

co("""
#@title 🔒 Industry momentum — same rule, 49 portfolios instead of 3,000 stocks
lr49 = np.log1p(ind49.clip(lower=-0.9999))
sig49 = np.expm1(lr49.rolling(11).sum().shift(1))       # identical t-12..t-2 rule
rank  = sig49.rank(axis=1, ascending=False)
IM = (ind49.where(rank <= 5).mean(axis=1) -             # top 5 industries
      ind49.where(rank >= 45).mean(axis=1)).dropna()    # short bottom 5

SM = std.dropna()                                       # from the function above
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
### Stock momentum survives industry momentum. It does not work the other way.

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

### 5b · Within industries — the half that needs stock-level data

That test compared two *portfolios*. It cannot tell us whether the stock-level
effect is peers-beating-peers, because it never looked inside an industry.

For that you need to know each stock's industry, which the panel does not carry.
We ship it separately: `industry_labels.parquet` gives an industry for **about
950 stocks a month across 48 industries**, recovered from a standard
characteristics dataset.

**That is a smaller universe than the panel, and the difference is not small.**
Check it before interpreting anything.
""")

# ── §5 crashes
co("""
#@title 🔒 First: what does restricting the universe cost?
lab = pd.read_parquet(f"{BASE}/industry_labels.parquet")

# give the panel a plain momentum column, same rule as everywhere else
p['cumret'] = (p.groupby('permno')['1+ret']
                 .rolling(11, min_periods=11).apply(np.prod, raw=True)
                 .reset_index(level=0, drop=True))
p['mom'] = p.groupby('permno')['cumret'].shift(1)

m    = p.merge(lab, on=['permno','date'], how='inner').dropna(subset=['mom','ret_fwd','me'])
same = p[p.date.isin(m.date.unique())].dropna(subset=['mom','ret_fwd','me'])

print(f"  all stocks         {same.groupby('date').permno.nunique().median():.0f}/month   "
      f"Sharpe {sharpe(sort_portfolios(same, signal='mom')):.2f}")
print(f"  labelled universe  {m.groupby('date').permno.nunique().median():.0f}/month   "
      f"Sharpe {sharpe(sort_portfolios(m, signal='mom')):.2f}")
""")

md("""
**0.99 against 0.42.** Same dates, same construction, same everything — the only
difference is that one runs on 5,400 stocks and the other on the largest 950.

**Momentum is largely a small- and mid-cap phenomenon.** That is a finding in its
own right, it is the reason the industry numbers below look modest, and it is the
first thing your project should check about your own signal. It also matters
enormously for next lecture: the place momentum works best is the place it costs
most to trade.

From here everything runs on the 950-stock universe, so every number is
comparable to every other number.
""")

md("""
### 🎯 Prompt it — build industry-neutral momentum <a id="prompt2"></a>

> **🤔 The question.** You have `m` with columns `mom`, `ind`, `date`, `ret_fwd`
> and `me`. Ask for **momentum that is neutral to industry** — the strategy that
> buys stocks beating their own peers rather than stocks in industries that ran.
>
> Write the prompt. There is more than one defensible construction, and the
> weighting decision changes the answer's *sign*.
""")

co("""
# === YOUR TURN ===
MY_PROMPT = \"\"\"
                                    ← write your prompt here
\"\"\"

# ---- paste the AI's code below ----

""")

co("""
#@title 🔒 Check — four ways to slice it, both weightings
D = pd.read_parquet(f"{BASE}/momentum_industry.parquet")
tab = pd.DataFrame({k: {'VW mean': D[f'{k}_VW'].mean()*12, 'VW Sharpe': sharpe(D[f'{k}_VW']),
                        'EW mean': D[f'{k}_EW'].mean()*12, 'EW Sharpe': sharpe(D[f'{k}_EW'])}
                    for k in ['plain', 'neutral', 'within', 'across']}).T
print(tab.to_string(formatters={'VW mean': '{:+.1%}'.format, 'EW mean': '{:+.1%}'.format,
                                'VW Sharpe': '{:.2f}'.format, 'EW Sharpe': '{:.2f}'.format}))
for line in ["  plain    rank all stocks on raw momentum",
             "  neutral  subtract the industry mean momentum, then rank all stocks",
             "  within   rank inside each industry, top third minus bottom third, averaged",
             "  across   rank the 48 industries, top 8 minus bottom 8"]:
    print(line)
""")

md("""
### Equal-weighted, taking the industry bet out makes momentum better

**0.83 for industry-neutral against 0.60 for plain.** You are not giving up a
source of return by neutralising — you are removing noise.

**Value-weighted, the gain vanishes: 0.41 against 0.42.**

So the answer to "is momentum within or across industries?" depends on a
weighting choice that has nothing to do with industries. Both weightings are
standard, neither is wrong, and this is the same problem as §4 turning up inside
a question you might have thought was about economics.

Run the ladder on the equal-weighted versions, where the effect is strong enough
to test.
""")

co("""
#@title 🔒 The ladder, at the stock level
for y, x in [('neutral_EW', 'across_EW'), ('across_EW', 'neutral_EW'), ('plain_EW', 'neutral_EW')]:
    r = sm.OLS(D[y], sm.add_constant(D[x])).fit()
    print(f"  {y:11s} on {x:11s} alpha {r.params.iloc[0]*12:+7.1%}/yr   t {r.tvalues.iloc[0]:+.2f}")
print(f"\\n  correlation(neutral, across) = {D[['neutral_EW','across_EW']].corr().iloc[0,1]:.2f}")
""")

md("""
### The same asymmetry, and one more step

Within-industry momentum survives across-industry momentum: **+6.1%/yr, t = 2.77**.
Across-industry momentum does not survive within: +1.5%/yr, t = 0.48. Same
direction as §5a, now measured at the stock level.

The third line goes further. **Plain momentum has no alpha against
industry-neutral momentum** — −1.2%/yr, t = −0.41. Once you own the
within-industry version, the ordinary version adds nothing.

> **📌 Momentum is stocks beating their peers. The industry bet that comes along
> with it is not paying you — and at equal weights it is costing you.**

Which is a practical conclusion, not just a classification. If you run momentum,
you should probably run it industry-neutral: same idea, better Sharpe ratio, and
you stop making a sector bet you never intended to make.

> **⚠️ Two caveats, and they are real.** The whole of §5b runs on 950 large
> stocks, where momentum is weak to begin with — none of these Sharpe ratios is
> the 1.03 from earlier. And the gain disappears if you value-weight. What we
> can say is that within and across are genuinely different strategies and the
> within one is not the passenger. What we cannot say is that this holds on the
> full universe, because we cannot label the full universe.
""")

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
mysig = p.merge(sig, on=['permno', 'date'], how='inner').rename(columns={MY_SIGNAL: 'signal'})
print(f"{MY_SIGNAL}: {len(mysig):,} stock-months")

# sort_portfolios takes ANY signal column — yours included.
mine_nyse = ____      # hint: sort_portfolios(mysig)
mine_all  = ____      # hint: same, with breakpoints='all'

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
rows = {}
for j_ in [1, 3, 6, 9, 11, 17, 23, 35, 47, 59]:
    rows[f'lookback {j_:2d}'] = momentum(p, lookback=j_, skip=1)
for k_ in [0, 2, 3, 6]:
    rows[f'skip {k_}']       = momentum(p, lookback=11, skip=k_)
for lab, kw in variants.items():
    rows[lab]                = momentum(p, **kw)
tab = pd.DataFrame({k: {'mean/yr': v.mean()*12, 'vol': v.std()*np.sqrt(12),
                        'Sharpe': sharpe(v)} for k, v in rows.items()}).T
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
