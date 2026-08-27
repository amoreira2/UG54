import json, pathlib
def md(s): return {"cell_type":"markdown","metadata":{},"source":s.splitlines(keepends=True)}
def code(s, hide=False, title=None):
    if hide: s = f"#@title {title}\n" + s
    return {"cell_type":"code","execution_count":None,
            "metadata":({"tags":["hide-input"],"cellView":"form"} if hide else {}),
            "outputs":[],"source":s.splitlines(keepends=True)}
C=[]

C.append(md("""# Backtesting: Estimate, Tune, Test

## 🎯 Learning Objectives

By the end of today you will be able to:

1. **Split a sample three ways** — estimate, tune, test — and say what each one is for
2. **Tune a strategy honestly**, choosing its parameters on data you will not report on
3. **Run a walk-forward test** and read it on a risk-adjusted basis
4. **Recognise data leakage** in four forms, including one you cannot see
5. **Report a result properly** — standard errors, a bootstrap, and a fragility check
6. **Adjust a t-statistic for how many things you tried**"""))

C.append(md("""## 📋 Today's Plan

1. [One history, many attempts](#one)
2. [Pitfall checklist](#pitfalls)
3. [🔄 Live Demo: estimate → tune → test](#demo)
4. [Walk-forward](#walk)
5. [What you report at the end](#report)
6. [Leakage](#leak)
7. [You tried more than one](#bonf)
8. [🛠️ Hands-On: your strategy through the process](#ho1)
9. [🎯 Challenge: a different split](#challenge) — *homework*
10. [Key takeaways](#takeaways)"""))

C.append(md("---\n\n## 🛠️ Setup"))
C.append(code("""#@title Setup — run this first
import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt
from scipy.stats import norm
%matplotlib inline
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = [11, 4]
import warnings; warnings.filterwarnings('ignore')

BASE = "https://raw.githubusercontent.com/amoreira2/UG54/refs/heads/main/assets/data"

# The 29 standard long-shorts from Lecture 5, cached. NYSE breakpoints,
# value-weighted, D10-D1, ret_fwd, dated by the month the return was EARNED.
L  = pd.read_parquet(f"{BASE}/longshort_29.parquet")
ff = pd.read_csv(f"{BASE}/ff_monthly.csv", index_col=0, parse_dates=True)

sharpe = lambda x: x.mean() / x.std() * np.sqrt(12)
print(f"{L.shape[1]} strategies, {len(L)} months, "
      f"{L.index[0]:%Y-%m} to {L.index[-1]:%Y-%m}")"""))

# ─────────────────────────────────────────────── §1
C.append(md("""---

## 1. One History, Many Attempts <a id="one"></a>

In Assignment 3 you ran your signal against four models and reported what you
found. Before that you picked the signal, out of thirty.

So: **how many did your group look at before choosing?**

Everything you have computed so far has been in-sample. You had one history of
the US stock market, you tried several things on it, and you reported the
attempt that worked. That is not a criticism — it is the only history there is,
and trying things is how research works. But it means the number you reported is
not the number a new investor would earn, and the gap is not small.

Today is about the discipline that closes the gap. It is a **process**, not a
statistic: three samples, each with one job, and a rule about which one you are
allowed to look at when."""))

# ─────────────────────────────────────────────── pitfalls
C.append(md("""---

## 🛡️ Pitfall Checklist for Backtests <a id="pitfalls"></a>

| | Pitfall | What goes wrong | 🔍 How to detect |
|---|---|---|---|
| 1 | **Random train/test split on a time series** | Trains on 1997, tests on 1985. Not out of sample at all | Is the split chronological? |
| 2 | **Tuning on the sample you report** | The reported number includes the search | Did you choose parameters on data you then reported? |
| 3 | **Comparing strategies on raw return** | The riskier one wins by construction | Are the volatilities comparable? |
| 4 | **Changing the universe after seeing a result** | The inclusion rule is now part of the fit | Was the universe fixed before the first run? |
| 5 | **A single t-statistic after many attempts** | 1.96 is the threshold for *one* test | How many did you try? |
| 6 | **Reporting the mean without the standard error** | A Sharpe of 0.7 and one of 0.5 look different and are not | Print `SE(SR)` next to `SR` |

> **🤖 AI-Era Insight**
>
> Pitfall 1 is the one to watch today. Ask for a train/test split and you will
> get `train_test_split(..., shuffle=True)`, which is correct for photographs of
> cats and wrong for anything with a date on it."""))

# ─────────────────────────────────────────────── §2 demo
C.append(md("""---

## 🔄 Live Demo: Estimate → Tune → Test <a id="demo"></a>

We have 29 strategies. We want a rule for combining them into one portfolio, and
we want an honest estimate of how that rule performs.

The rule has two knobs:

- **N** — how many of the strategies to hold, taking the best N
- **W** — how to weight them: equally, by inverse volatility, or by past Sharpe

Nobody knows the right N and W in advance. So we have to choose them from data —
and *choosing from data* is exactly the thing that inflates a backtest. The
answer is to spend three separate slices of history:

| sample | what it decides | may you look at it? |
|---|---|---|
| **Estimate** 1980–89 | which strategies rank highest | yes |
| **Tune** 1990–94 | N and W | yes |
| **Test** 1995–2000 | nothing — it only reports | **once, at the end** |

> **🤔 Before we start.** Predict two things and write them down. Which N will
> tuning choose? And how much of the tuned Sharpe ratio do you expect to survive
> into the test sample?"""))

C.append(md("""### Step 1 — Say how to split it

> **🤔 The question.** *"Hold out some data so we can test out of sample."*
> Say that precisely enough for someone to implement. There is one word that
> decides whether the answer means anything."""))

C.append(code("""# === YOUR TURN ===
MY_PROMPT = \"\"\"
                                    ← write your prompt here
\"\"\"

# ---- paste the AI's code below ----
"""))

C.append(code("""# Two ways to hold out 30% of the data. Both "test out of sample".
from sklearn.model_selection import train_test_split
best = L.apply(sharpe).idxmax()          # one strategy, to keep it simple
x    = L[best]

rand_tr, rand_te = train_test_split(x, test_size=0.3, random_state=0)   # shuffled
cut = int(len(x)*0.7)
chron_tr, chron_te = x.iloc[:cut], x.iloc[cut:]

print(f"strategy: {best}\\n")
print(f"{'':28s}{'train':>9s}{'test':>9s}")
print(f"{'random split':28s}{sharpe(rand_tr):>9.2f}{sharpe(rand_te):>9.2f}")
print(f"{'chronological split':28s}{sharpe(chron_tr):>9.2f}{sharpe(chron_te):>9.2f}")
print(f"\\nrandom test months run {rand_te.index.min():%Y-%m} to {rand_te.index.max():%Y-%m}")
print(f"chronological test months run {chron_te.index.min():%Y-%m} to {chron_te.index.max():%Y-%m}")""",
 hide=True, title="🔒 Check — run after you've pasted yours"))

C.append(md("""### The random split is not a test

Look at the date ranges. The random split's "test set" runs across the whole
sample — it is interleaved with the training data, month by month. You trained
on 1997 and tested on 1985, and on the months either side of every month you
trained on.

A strategy's returns are not independent draws. Regimes persist, volatility
clusters, and the same market conditions appear on both sides of the split. So
the random test tells you almost nothing you did not already know from the
training set — which is why the two numbers come out close, and why that
closeness is meaningless.

> **📌 Remember**
>
> Out of sample means **out of time**. If the test data sits inside the period
> you fitted on, it is not a test.

### Step 2 — Run the process"""))

C.append(code("""#@title 🔒 Reference implementation — the three samples and the rule
EST = L.loc[:'1989-12-31']
TUN = L.loc['1989-12-31':'1994-12-31'].iloc[1:]
TST = L.loc['1994-12-31':].iloc[1:]

rank = EST.apply(sharpe).sort_values(ascending=False)     # decided on ESTIMATE only

def combo(sample, names, scheme):
    \"\"\"Hold `names`, weighted by `scheme`. Weights come from the ESTIMATE sample.\"\"\"
    w = {'ew'    : pd.Series(1.0, index=names),
         'ivol'  : 1 / EST[names].std(),
         'sharpe': EST[names].apply(sharpe).clip(lower=0)}[scheme]
    return (sample[names] * (w / w.sum())).sum(axis=1)

print(f"ESTIMATE {EST.index[0]:%Y-%m}–{EST.index[-1]:%Y-%m}  ({len(EST)} months)")
print(f"TUNE     {TUN.index[0]:%Y-%m}–{TUN.index[-1]:%Y-%m}  ({len(TUN)} months)")
print(f"TEST     {TST.index[0]:%Y-%m}–{TST.index[-1]:%Y-%m}  ({len(TST)} months)\\n")
print("top of the ESTIMATE ranking:")
for k, v in rank.head(4).items(): print(f"   {k:22s}{v:>6.2f}")"""))

C.append(code("""#@title 🔒 The tune grid — the only thing you are allowed to look at
NS = [1, 3, 5, 10, 20, 29]; WS = ['ew', 'ivol', 'sharpe']
tune = pd.DataFrame({w: {n: sharpe(combo(TUN, list(rank.index[:n]), w)) for n in NS}
                     for w in WS})
tune.index.name = 'N'
print("TUNE-sample Sharpe\\n"); print(tune.round(2).to_string())
bN, bW = tune.stack().idxmax()
print(f"\\n   -> the process picks N = {bN}, W = '{bW}'   (tune Sharpe {tune.loc[bN,bW]:.2f})")"""))

C.append(md("""### Step 3 — Now, and only now, the test sample"""))

C.append(code("""#@title 🔒 The reveal
test = pd.DataFrame({w: {n: sharpe(combo(TST, list(rank.index[:n]), w)) for n in NS}
                     for w in WS})
test.index.name = 'N'
print("TEST-sample Sharpe\\n"); print(test.round(2).to_string())
print(f"\\n{'the tuned choice  N=%d, %s' % (bN, bW):44s}{test.loc[bN,bW]:>6.2f}")
print(f"{'naive: the single best estimate-sample signal':44s}{test.loc[1,'ew']:>6.2f}")
print(f"{'no tuning at all: all 29, equal-weighted':44s}{test.loc[29,'ew']:>6.2f}")
print(f"{'average over the whole grid':44s}{test.values.mean():>6.2f}")"""))

C.append(md("""### Read the three numbers at the bottom

**The naive rule is the disaster.** `ShareIss5Y` had the highest Sharpe ratio in
the estimate sample — 1.17 — and delivers **−0.08** in the test. Ten years of
evidence, and the strategy it pointed at loses money on a risk-adjusted basis
for the next six.

**Tuning earned its keep.** N = 20, inverse-vol, chosen without ever seeing the
test data, delivers **1.13**.

**And the crudest rule available does well.** Hold all 29, weight them equally,
tune nothing: **0.85**. Most of what tuning bought over that was the inverse-vol
weighting, not the choice of N.

> **💡 Key Insight**
>
> The two ends of the grid are the story. Concentrating on the single best
> in-sample performer is the worst thing you can do with 29 candidates. Holding
> all of them, badly, beats it by 0.93 of a Sharpe ratio.

> **⚠️ Caution: one split is one draw**
>
> These are numbers from one choice of dates. Re-run with the estimate sample
> ending in 1987, 1988, 1990 or 1991 and the *ordering* never changes — tuned
> beats all-29 beats best-1 — but the levels move by 0.2 to 0.5. The ordering is
> the finding. The levels are not."""))

# ─────────────────────────────────────────────── §3 walk-forward
C.append(md("""---

## 2. Walk-Forward <a id="walk"></a>

The three-way split spends its whole test sample in one go. Once you have looked,
you have no clean data left.

**Walk-forward** reuses the idea repeatedly. Each year: rank on everything up to
five years ago, tune on the years since, invest for the next twelve months, then
roll everything forward. Every month of returns is earned on parameters chosen
before that month began, and stitching them gives a track record you could
actually have lived through."""))

C.append(code("""#@title 🔒 Reference implementation — re-rank and re-tune every year
tuned, naive, allsig = [], [], []
for yr in range(1990, 2001):
    E = L.loc[:f"{yr-5}-12-31"]
    T = L.loc[f"{yr-5}-12-31":f"{yr-1}-12-31"].iloc[1:]
    S = L.loc[f"{yr}-01-01":f"{yr}-12-31"]
    rk = E.apply(sharpe).sort_values(ascending=False)
    def cb(smp, nm, w):
        ww = {'ew': pd.Series(1.0, index=nm), 'ivol': 1/E[nm].std(),
              'sharpe': E[nm].apply(sharpe).clip(lower=0)}[w]
        return (smp[nm] * (ww/ww.sum())).sum(axis=1)
    grid = {(n, w): sharpe(cb(T, list(rk.index[:n]), w)) for n in NS for w in WS}
    n_, w_ = max(grid, key=grid.get)
    tuned.append(cb(S, list(rk.index[:n_]), w_))
    naive.append(cb(S, list(rk.index[:1]), 'ew'))
    allsig.append(cb(S, list(rk.index), 'ew'))

WF = {'re-tuned every year': pd.concat(tuned),
      'always the single best': pd.concat(naive),
      'always all 29, equal-weighted': pd.concat(allsig)}

print(f"1990-2000, {len(WF['re-tuned every year'])} months\\n")
print(f"{'':32s}{'return/yr':>11s}{'vol/yr':>9s}{'Sharpe':>9s}{'max DD':>9s}")
for k, x in WF.items():
    dd = ((1+x).cumprod() / (1+x).cumprod().cummax() - 1).min()
    print(f"{k:32s}{x.mean()*12:>10.1%}{x.std()*np.sqrt(12):>9.1%}{sharpe(x):>9.2f}{dd:>9.0%}")"""))

C.append(code("""#@title 🔒 The same three, as growth of $1
fig, ax = plt.subplots(1, 2, figsize=(13, 4))
for k, x in WF.items():
    ax[0].plot((1+x).cumprod(), label=k, linewidth=1.6)
    c = (1+x).cumprod()
    ax[1].plot(c/c.cummax() - 1, label=k, linewidth=1.2)
ax[0].set_ylabel('growth of $1'); ax[0].set_title('Walk-forward, 1990–2000', fontweight='bold')
ax[0].legend(fontsize=8)
ax[1].set_ylabel('drawdown'); ax[1].set_title('Drawdown', fontweight='bold')
plt.tight_layout(); plt.show()"""))

C.append(md("""### The trap in that table

Read the **return** column on its own and the naive rule wins comfortably —
**11.8% a year against 5.7%**. Pick the single best strategy every year and you
roughly double your money relative to the disciplined process.

Now read across. That 11.8% comes with **15.3% volatility and a 24% drawdown**,
against 4.0% and 4% for the tuned portfolio. On a Sharpe ratio it is **0.77
against 1.42**.

This is Lecture 1 arriving five lectures late: return alone is not a measure of
quality, because you can always buy more return with more risk. It is easy to
say and easy to forget — I built the first version of this table comparing mean
returns and concluded the naive rule was best.

> **📌 Remember**
>
> Never compare two strategies on return unless their volatilities are the same.
> If they are not, you are comparing leverage."""))

# ─────────────────────────────────────────────── §4 report
C.append(md("""---

## 3. What You Report at the End <a id="report"></a>

The test sample gets used once. So what you extract from it should be more than
a single number.

Six things, all computable from a return series:

| | What it answers |
|---|---|
| **Sharpe ratio** | return per unit of risk |
| **SE of the Sharpe**, and its t | how precisely do you know it? |
| **Bootstrap 5th percentile** | how bad is a bad draw, without assuming normality? |
| **Alpha, its SE, appraisal ratio** | is any of it unavailable cheaply? |
| **Fraction to half** | how many months carry the whole result? |
| **Max drawdown, tails** | what does holding it feel like? |"""))

C.append(code("""#@title 🔒 The six checks
def se_sharpe(R):
    \"\"\"Analytic SE of the annualized Sharpe ratio.\"\"\"
    s = R.mean()/R.std()
    return np.sqrt((1 + s**2/2) / (len(R)-1)) * np.sqrt(12)

def boot_sharpe(R, n=4000, seed=0):
    rng = np.random.default_rng(seed)
    v = np.array([sharpe(R.iloc[rng.integers(0, len(R), len(R))]) for _ in range(n)])
    return v.std(), np.percentile(v, 5)

def frac_to_half(R):
    \"\"\"Share of months you must delete, best first, to halve the Sharpe ratio.\"\"\"
    target = sharpe(R)/2; r = R.copy(); k = 0
    for i in R.sort_values(ascending=False).index:
        if sharpe(r) <= target or len(r) <= 2: break
        r = r.drop(i); k += 1
    return k/len(R)

def checks(R, label):
    j = pd.concat([R.rename('y'), ff['Mkt-RF']], axis=1).dropna()
    m = sm.OLS(j.y, sm.add_constant(j['Mkt-RF'])).fit()
    a, sa = m.params['const']*12, m.bse['const']*12
    iv = m.resid.std()*np.sqrt(12)
    dd = ((1+R).cumprod()/(1+R).cumprod().cummax() - 1).min()
    return dict(label=label, vol=R.std()*np.sqrt(12), SR=sharpe(R), SE=se_sharpe(R),
                t_SR=sharpe(R)/se_sharpe(R), boot5=boot_sharpe(R)[1],
                alpha=a, SE_a=sa, t_a=m.tvalues['const'], appraisal=a/iv,
                frac_half=frac_to_half(R), maxDD=dd)

rows = [checks(combo(TST, list(rank.index[:bN]), bW), 'tuned strategy'),
        checks(L.loc[TST.index,'Mom12m'], 'Mom12m alone'),
        checks(ff.loc[TST.index,'Mkt-RF'], 'the market')]
R6 = pd.DataFrame(rows).set_index('label')
print("TEST SAMPLE ONLY, 1995-2000\\n")
print(R6[['vol','SR','SE','t_SR','boot5']].round(2).to_string())
print()
print(R6[['alpha','SE_a','t_a','appraisal','frac_half','maxDD']].round(3).to_string())"""))

C.append(md("""### Two things in that table are worth stopping on

**The standard error of the Sharpe ratio barely moves.** It is roughly the same
for a strategy running 4% volatility and one running 20%. That looks wrong, and
it is not:

$$SE(SR) \;\\approx\; \\sqrt{\\frac{1 + SR^2/2}{T}}$$

There is no σ in it. The Sharpe ratio is a *ratio* — volatility appears in the
numerator and the denominator of the estimate and cancels. What is left depends
on how **long** you looked, not what you looked at. Simulate a true Sharpe of 0.5
over 250 months and the sampling standard deviation is 0.220 at 5% annual
volatility and 0.220 at 80%.

The instinct that a noisier strategy is harder to measure is right — it is just
right about the things measured in *return* units. Look at `SE_a`: the standard
error of alpha does scale with volatility, and across our strategies it runs
from 2.4% to 4.4% a year, tracking σ almost exactly.

> **💡 Key Insight**
>
> `SE(SR)` tells you about your **sample length**. `SE(alpha)` tells you about
> your **strategy**. Report both and you have said something about each.

**Fraction to half is a fragility test, not a performance test.** It asks how
many of your best months you would have to delete before the Sharpe ratio halves.
The market needs about 9% of its months removed. A strategy that needs 0.4% has
a result resting on two or three dates, and no amount of t-statistic fixes
that."""))

# ─────────────────────────────────────────────── §5 leakage
C.append(md("""---

## 4. Leakage <a id="leak"></a>

Everything above assumes the test sample is genuinely unseen. Leakage is when it
is not, and it usually arrives through the data rather than the code.

One rule covers all of it:

> **Never use data in a backtest, on a given date, that you could not have used
> in production that day.**
>
> — Paleologo, *The Elements of Quantitative Investing*, §4.1

Four ways it happens. You have met three of them:

1. **Using `ret` where you meant `ret_fwd`.** You sort at the end of month *t*
   and collect month *t*'s return. Lecture 2 measured this: for short-term
   reversal, that single off-by-one turns a t-statistic of −0.4 into **+70**.
2. **Survivorship.** A universe built from firms that still exist has already
   answered your question. Lecture 2 again.
3. **Financial statements dated to the quarter they describe.** A company's Q4
   numbers are not public in December. Date them by the *release* day, or you are
   trading on accounts nobody had yet.
4. **Split-adjusted prices.** This one is invisible.

> **⚠️ Caution: the adjusted price series contains the future**
>
> Prices are usually adjusted backwards for splits, so that a long history is
> comparable. But a stock splits *because it went up*. So a low adjusted price in
> 1985 tells you the stock split at some point after 1985 — which tells you it
> rose. Sort on adjusted price and you have sorted, partly, on future returns.
>
> The fix is a division of labour: **adjusted prices for computing returns,
> as-of-date prices for building signals.**

> **📌 Remember: the protocol is part of the data**
>
> Fix the universe, the sample, and the split **before** the first backtest.
> Changing your inclusion rule because of a result you did not like is leakage
> too — the rule is now fitted to the outcome, and no hold-out sample can
> detect it."""))

# ─────────────────────────────────────────────── §6 bonferroni
C.append(md("""---

## 5. You Tried More Than One <a id="bonf"></a>

A t-statistic of 2 means: *if nothing were there, I would see this about one time
in twenty.* That is a statement about **one** test. Run twenty and you should
expect to see it once for free.

The simplest correction is **Bonferroni** — divide your significance level by the
number of things you tried."""))

C.append(code("""#@title 🔒 The threshold, and what happens without it
print("t-statistic you need for 5% significance, having tried M signals\\n")
print(f"  {'M':>5s}{'t needed':>11s}")
for M in [1, 5, 10, 20, 29, 100, 300]:
    print(f"  {M:>5d}{norm.isf(0.025/M):>11.2f}")
print(f"\\n  Our menu is 29 signals -> the threshold is {norm.isf(0.025/29):.2f}, not 1.96.\\n")

rng = np.random.default_rng(0)
print("100 strategies with NO true edge, 24 months each, 2000 simulations:")
for cut, lbl in [(1.64,'t > 1.64'), (1.96,'t > 1.96'),
                 (norm.isf(0.025/100), f't > {norm.isf(0.025/100):.2f}  (Bonferroni)')]:
    c = [((lambda R: R.mean(0)/(R.std(0)/np.sqrt(24)))(
            rng.normal(0, 0.16/np.sqrt(12), (24,100))) > cut).sum() for _ in range(2000)]
    print(f"   {lbl:28s} look significant: {np.mean(c):>5.1f} of 100")"""))

C.append(code("""#@title 🔒 What the correction costs you
def trial(cut, months, ideas=100, sims=600, true_SR=1.0, seed=1):
    rng = np.random.default_rng(seed); ok = wrong = 0
    for _ in range(sims):
        R = rng.normal(0, 1, (months, ideas)); R[:,0] += true_SR/np.sqrt(12)
        t = R.mean(0)/(R.std(0)/np.sqrt(months))
        ok += t[0] > cut; wrong += (t[1:] > cut).sum()
    return ok/max(ok+wrong,1), ok/sims

print("One real signal (Sharpe 1.0) hidden among 100 worthless ones.\\n")
for months in (48, 120):
    print(f"  {months} months")
    print(f"   {'cutoff':>8s}{'hit rate':>11s}{'detection':>12s}")
    for cut in (1.96, 3.00, norm.isf(0.025/100)):
        h, d = trial(cut, months)
        print(f"   {cut:>8.2f}{h:>10.0%}{d:>12.0%}")
    print()"""))

C.append(md("""### There is no cutoff that fixes this

**Hit rate** is how much of what you flag is real. **Detection rate** is how often
you find the real thing at all.

At 48 months and the conventional 1.96, you detect the real signal about half the
time and **85% of everything you flag is noise**. Tighten to the Bonferroni
threshold and you are right most of the time — but you find the real signal once
in twelve.

Every cutoff trades one error against the other. What breaks the trade-off is not
a cleverer threshold: it is the second panel. At 120 months the same two cutoffs
give 26%/90% and 93%/41%. **Length of sample is the only thing that buys you
both**, which is a large part of why long histories are worth what they cost.

> **📎 Where this goes next**
>
> Bonferroni assumes your tests are independent. Ours are not — Lecture 5 showed
> signals inside a family correlate around 0.58 — so it is conservative here.
> Next class takes this to the published literature, where the number of things
> tried is not 29 but something nobody knows."""))

# ─────────────────────────────────────────────── Hands-On
C.append(md("""---

## 🛠️ Hands-On: Your Strategy Through the Process <a id="ho1"></a>

Your own long-short from Assignment 2 has only ever been evaluated in-sample.
Put it through the same three samples.

> **🤔 Predict first.** Your signal's full-sample Sharpe ratio is a number you
> already know. How much of it do you expect to survive in 1995–2000?"""))

C.append(code("""# === EDIT + YOUR TURN ===
MY_SIGNAL = "GP"      # ← your group's signal

mine = L[MY_SIGNAL]
est, tun, tst = mine.loc[:'1989-12-31'], mine.loc['1990-01-31':'1994-12-31'], mine.loc['1995-01-31':]

print(f"{MY_SIGNAL}")
print(f"  full sample  {sharpe(mine):>6.2f}")
print(f"  estimate     {sharpe(est):>6.2f}")
print(f"  tune         {sharpe(tun):>6.2f}")
print(f"  TEST         {sharpe(tst):>6.2f}")

# Now run the six checks on the TEST sample only.
mine_checks = ____        # hint: checks(tst, MY_SIGNAL)
pd.Series(mine_checks).to_frame(MY_SIGNAL).T"""))

C.append(md("""### Compare with the room

- **Did your Sharpe survive?** Most will fall. A few will rise, and that is worth
  as much attention — it means the estimate period was the unlucky one.
- **What is your fraction to half?** Under 2% and your result lives on a handful
  of months.
- **Where does your signal sit in the estimate-sample ranking?** If it was in the
  top five, ask yourself the uncomfortable version of today's question: would
  your group have picked it if it had ranked twentieth?"""))

# ─────────────────────────────────────────────── Challenge
C.append(md("""---

## 🎯 Challenge: A Different Split <a id="challenge"></a>

*Homework — due before Lecture 9.*

Your PM accepts the process and asks the obvious question: **how much of this
depends on where you cut the sample?**

Re-run the whole thing with the estimate sample ending **1987-12-31** and the
tune sample ending **1991-12-31**. Everything else identical — same 29
strategies, same grid of N and W, same ranking rule.

### Q1 — The tuned result

Tune on 1988–91, pick the best cell, and report its **test-sample Sharpe ratio**
over the remaining months.

> **📌 Required variable names:**
> ```python
> tuned_sharpe = ____   # test-sample Sharpe of the tuned choice
> ```"""))
C.append(code("""# Your work here


tuned_sharpe = ____

print(f"tuned choice, test sample: {tuned_sharpe:.2f}")"""))

C.append(md("""### Q2 — The two benchmarks

On the same test sample, report the naive rule (the single best estimate-sample
signal) and the no-tuning rule (all 29, equal-weighted).

> **📌 Required variable names:**
> ```python
> naive_sharpe = ____   # single best estimate-sample signal
> all29_sharpe = ____   # all 29, equal-weighted
> ```"""))
C.append(code("""# Your work here


naive_sharpe = ____
all29_sharpe = ____

print(f"naive (best single): {naive_sharpe:6.2f}")
print(f"all 29, equal-wtd  : {all29_sharpe:6.2f}")"""))

C.append(md("""### Q3 — The threshold

You searched a menu of 29 strategies. What t-statistic should you require before
calling any single one of them significant at the 5% level?

> **📌 Required variable name:**
> ```python
> bonf_t = ____
> ```"""))
C.append(code("""# Your work here


bonf_t = ____

print(f"Bonferroni threshold for 29 tests: {bonf_t:.2f}")"""))

C.append(md("""### Q4 — The memo

> **📝 Your task — maximum eight sentences.**
>
> Your PM has seen both splits now: the one from class and yours. Write them the
> recommendation.
>
> Say which of the three rules you would run and why. Say what changed between
> the two splits and what did not — and be precise about which of those two facts
> is the finding. Say what you would need to see before you would trust any
> single Sharpe ratio in either table. And answer the question they will actually
> ask: **if the naive rule earned 11.8% a year in the walk-forward and the tuned
> process earned 5.7%, why are you not recommending the naive rule?**"""))
C.append(code("""MEMO = \"\"\"
Write your memo here. Don't delete the surrounding triple quotes.
\"\"\"
print(MEMO)"""))

# ─────────────────────────────────────────────── Submission
C.append(md("---\n\n## 📤 Submission <a id=\"submit\"></a>"))
C.append(code("""# === 📤 SUBMISSION CELL — Run this last ===
import json, base64, hashlib, datetime as dt

required = ["tuned_sharpe", "naive_sharpe", "all29_sharpe", "bonf_t", "MEMO"]
missing = [v for v in required if v not in globals()]
if missing:
    raise NameError(f"\\n❌ Missing before submission: {missing}")

payload = {
    "assignment": "L8_Backtesting_AI",
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
print("Submission form: https://forms.gle/yazZ8bbatL87jdJi7")"""))

# ─────────────────────────────────────────────── Takeaways
C.append(md("""---

## 🧠 Key Takeaways <a id="takeaways"></a>

1. **Three samples, three jobs.** Estimate ranks, tune chooses parameters, test
   reports. The test sample is spent the moment you look at it.

2. **Out of sample means out of time.** A random split of a time series trains on
   1997 and tests on 1985, and the two numbers agree because it is not a test.

3. **Concentrating on the in-sample winner is the worst available choice.** The
   best estimate-sample signal delivered −0.08 in the test; all 29 held equally
   delivered 0.85.

4. **Walk-forward gives you a track record you could have lived through** —
   parameters always chosen before the returns they earn.

5. **Never compare strategies on return alone.** The naive rule earned 11.8%/yr
   against 5.7% and had half the Sharpe ratio and six times the drawdown.

6. **`SE(SR)` depends on how long you looked; `SE(alpha)` depends on what you
   looked at.** Report both.

7. **Fraction to half is a fragility test.** If deleting 2% of months halves your
   Sharpe ratio, a handful of dates is carrying the result.

8. **Leakage is a data problem, not a code problem.** Adjusted prices know the
   future; financial statements are not public on the day they describe.

9. **Twenty attempts need a t of 3.0, not 2.0** — and no threshold gives you both
   a high hit rate and a high detection rate. Only a longer sample does.

---

### Next class

We have been auditing *your* research process. Next: the published record. Three
hundred anomalies, a literature that only prints what worked, and the question of
how much survives when you apply today's correction to it."""))

C.append(md("---\n\n## 📎 Appendix <a id=\"appendix\"></a>"))
C.append(code("""# ═══════════════════════════════════════════════════════════════════════
# 📎 APPENDIX — data, and the full diagnostics function
# ═══════════════════════════════════════════════════════════════════════
#
# longshort_29.parquet is the 29 standard long-shorts from Lecture 5, cached so
# this notebook does not re-download 94 MB of signal files. Convention: NYSE
# breakpoints, value-weighted, D10-D1, ret_fwd, dated by the month EARNED.
# Rebuild with chapters/Finance/build_longshort_panel.py
#
#     L = pd.read_parquet(f"{BASE}/longshort_29.parquet")
#
# ff_monthly.csv is Ken French's FF5 + momentum + RF, monthly, in decimals.

def Diagnostics(R, benchmark=None, label="strategy"):
    \"\"\"Every check from today, on one return series. Returns a Series.

    R          monthly returns of the strategy
    benchmark  monthly excess return of the benchmark (defaults to Mkt-RF)
    \"\"\"
    if benchmark is None:
        benchmark = ff['Mkt-RF']
    j = pd.concat([R.rename('y'), benchmark.rename('b')], axis=1).dropna()
    m = sm.OLS(j.y, sm.add_constant(j.b)).fit()
    a, sa = m.params['const']*12, m.bse['const']*12
    iv = m.resid.std()*np.sqrt(12)
    cum = (1+R).cumprod()
    return pd.Series({
        'months'      : len(R),
        'return/yr'   : R.mean()*12,
        'vol/yr'      : R.std()*np.sqrt(12),
        'Sharpe'      : sharpe(R),
        'SE(Sharpe)'  : se_sharpe(R),
        't(Sharpe)'   : sharpe(R)/se_sharpe(R),
        'boot 5%'     : boot_sharpe(R)[1],
        'alpha/yr'    : a,
        'SE(alpha)'   : sa,
        't(alpha)'    : m.tvalues['const'],
        'appraisal'   : a/iv,
        'beta'        : m.params['b'],
        'R2'          : m.rsquared,
        'frac to half': frac_to_half(R),
        'tails >3sd'  : ((R-R.mean()).abs() > 3*R.std()).mean(),
        'max drawdown': (cum/cum.cummax() - 1).min(),
        'worst month' : R.min(),
    }, name=label)

# Example:
#   Diagnostics(combo(TST, list(rank.index[:20]), 'ivol'), label='tuned').to_frame()"""))

nb={"cells":C,"metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},
    "language_info":{"name":"python","version":"3.11"}},"nbformat":4,"nbformat_minor":5}
out=pathlib.Path("chapters/Finance/L8_Backtesting_AI.ipynb")
json.dump(nb, open(out,'w'), indent=1, ensure_ascii=False); open(out,'a').write("\n")
print(f"✅ {out} — {len(C)} cells")
