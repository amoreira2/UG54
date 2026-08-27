"""
Build L4_PerfEval_Factors_AI.ipynb — Lecture 4, Wed Sep 16 2026.

"Introduction to Performance Evaluation + Factor Models I"  (Columbia 2B)

Sources:
    L3's §5 "What to Measure"  (Sharpe + information ratio, moved here)
    FactorModels_c_AI.ipynb    (beta, alpha, hedging, variance decomposition)

The spine: L1 ended with an unanswered question — GE's Sharpe was 0.773 against
the market's 0.601 over twenty years, at 22% volatility versus 16%. Was Jack
Welch good, or was GE just a levered bet on a bull market? Students wrote a memo
about it in week 1 without the tools to settle it. Today they settle it.

    GE on the market, 1980-2000 (verified):
        alpha  +7.12%/yr, t = 2.19
        beta    1.07                     <- NOT a levered market bet
        R2      0.56
        total vol 22.16% = 16.65% market + 14.63% idiosyncratic
        Sharpe 0.773  ->  APPRAISAL 0.487

The naive intuition ("more volatile, so more market exposure") is wrong here,
and that is worth showing: GE's extra volatility was idiosyncratic, and the
alpha survives. But t = 2.19 over twenty years is marginal, and GE was chosen
BECAUSE it was famous -- which is the selection problem, flagged for L7/L8.

The value long-short makes the opposite point (beta -0.21, so stripping market
exposure IMPROVES it: Sharpe 0.39 but appraisal 0.54).

CHALLENGE (auto-graded, verified 2026-08-07): Exxon vs Pfizer.
    Exxon  SR 0.720 | alpha  +6.76% t=2.12 | beta 0.59 | idio 14.4% | AR 0.470
    Pfizer SR 0.718 | alpha +10.87% t=2.18 | beta 0.82 | idio 22.5% | AR 0.483
Nearly identical Sharpe AND nearly identical appraisal, assembled from
completely different parts. The memo asks what the ratios do and don't say.
"""

import json
from pathlib import Path

OUT = Path(__file__).parent / "L4_PerfEval_Factors_AI.ipynb"
BASE = "https://raw.githubusercontent.com/amoreira2/UG54/refs/heads/main/assets/data"


def md(t): return {"cell_type": "markdown", "metadata": {}, "source": t.splitlines(keepends=True)}
def code(t): return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": t.splitlines(keepends=True)}


cells = []

cells.append(md("""# Introduction to Performance Evaluation, and Factor Models
## Lecture 4

## 🎯 Learning Objectives

By the end of today you will be able to:

1. **Choose the right performance ratio for the question** — Sharpe, information,
   or appraisal — and say what each one assumes
2. **Run a factor regression** and read α, β, and R² correctly
3. **Split a return into what you could have bought cheaply and what you couldn't**
4. **Compute an appraisal ratio**, and show that Sharpe, information and
   appraisal are one formula against three different benchmarks
5. **Build a hedged portfolio** and explain why hedging buys you alpha capacity
6. **Answer the question from Lecture 1** — was General Electric skill, or beta?
7. **Take apart a real fund** — what ARKK and Berkshire were actually doing"""))

cells.append(md("""## 📋 Today's Plan

1. [Three questions, three ratios](#three)
2. [Sharpe, the information ratio, and endogenous benchmarks](#sharpe-ir)
3. [Pitfall checklist](#pitfalls)
4. [🔄 Live Demo: was GE skill or beta?](#demo)
5. [Decomposing risk, hedging, and the risk budget](#decomp)
6. [The appraisal ratio — and why there was only ever one ratio](#appraisal)
7. [Two famous funds: ARKK vs Berkshire](#funds)
8. [🛠️ Hands-On: does your signal have alpha?](#ho1)
9. [🎯 Challenge: Exxon vs Pfizer](#challenge) — *homework*
10. [Key takeaways](#takeaways)"""))

cells.append(md("---\n\n## 🛠️ Setup"))

cells.append(code(f"""#@title Setup — run this first
import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt
%matplotlib inline
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = [11, 4.5]
import warnings; warnings.filterwarnings('ignore')
import pandas_datareader.data as web

BASE  = "{BASE}"
panel = pd.read_parquet(f"{{BASE}}/panel_backbone_1980_2000.parquet")

ff = web.DataReader('F-F_Research_Data_Factors', 'famafrench', start='1980-01-01')[0] / 100
ff.index = pd.to_datetime(ff.index.to_timestamp()) + pd.offsets.MonthEnd(0)
ff = ff.loc['1980-01-31':'2000-12-31']

print(f"panel: {{len(panel):,}} rows")
print(f"factors: {{ff.index.min().date()}} to {{ff.index.max().date()}}, "
      f"columns {{list(ff.columns)}}")"""))

# ─── 1. three ratios ──────────────────────────────────────────────────
cells.append(md(r"""---

## 1. Three Questions, Three Ratios <a id="three"></a>

You have a return series. Is it any good?

That is not one question. It is three, and they have different answers.

| Question | Ratio |
|---|---|
| *Was it worth the risk at all?* | **Sharpe** |
| *Did I beat what I was hired to beat?* | **Information ratio** |
| *Was any of it something I couldn't have bought cheaply?* | **Appraisal ratio** |

The third one is the hardest and the most important, and it needs a tool we
don't have yet — a **factor model**. We'll do the first two now, build the
factor model, then come back for the third."""))

# ─── 2. Sharpe + IR ───────────────────────────────────────────────────
cells.append(md(r"""---

## 2. Sharpe, the Information Ratio, and Endogenous Benchmarks <a id="sharpe-ir"></a>

### Sharpe: return per unit of total risk

$$SR = \frac{\text{mean}(r)}{\text{sd}(r)} \times \sqrt{12}$$

For a **long-short** strategy there is no risk-free rate to subtract — the
weights sum to zero, so no capital was tied up and there is nothing to compare
against a T-bill. For a **long-only** position you use the excess return
$r - r_f$.

### Information ratio: return relative to a benchmark

Most money is not managed against cash. It is managed against a **mandate**.

$$IR = \frac{\text{mean}(r_p - r_b)}{\text{sd}(r_p - r_b)} \times \sqrt{12}$$

The numerator is **active return**; the denominator is **tracking error**. No
regression needed — you only have to decide what $r_b$ is.

That decision is not a technical one. Let's see how much it matters."""))

cells.append(code("""# A long-only value fund: top BM decile, NYSE breakpoints, value-weighted
bm = pd.read_parquet(f"{BASE}/signals/BM.parquet")
dv = panel.merge(bm, on=['permno','date'], how='inner').dropna(subset=['BM','ret_fwd','me'])
hi = dv[dv.exchcd == 1].groupby('date')['BM'].quantile(.9).rename('hi')
dv = dv.merge(hi, on='date')
fund = (dv[dv.BM >= dv.hi].groupby('date')
          .apply(lambda g: np.average(g['ret_fwd'], weights=g['me'])))

d0 = panel.dropna(subset=['ret_fwd','me'])
mkt_vw = d0.groupby('date').apply(lambda g: np.average(g['ret_fwd'], weights=g['me']))
mkt_ew = d0.groupby('date')['ret_fwd'].mean()
rf     = ff['RF'].reindex(mkt_vw.index)

def info_ratio(p, b):
    a = (p - b).dropna()
    return a.mean()*12, a.std()*np.sqrt(12), a.mean()/a.std()*np.sqrt(12)

print(f"Value fund: {fund.mean()*12:.2%}/yr, vol {fund.std()*np.sqrt(12):.2%}\\n")
print(f"{'benchmark':24s}{'active ret':>12s}{'tracking err':>14s}{'IR':>8s}")
print("-"*58)
for name, b in [('VW market', mkt_vw), ('EW market', mkt_ew), ('cash (risk-free)', rf)]:
    a, te, i = info_ratio(fund, b)
    print(f"{name:24s}{a:>11.2%}{te:>14.2%}{i:>8.2f}")"""))

cells.append(md(r"""### One fund. Three numbers.

The same portfolio, the same 252 months, scores **0.55**, **0.58**, or **0.83**
depending only on what you compare it to.

> **💡 Key Insight: the Sharpe ratio is the information ratio against cash**
>
> Look at the last row. When the benchmark is the risk-free rate, active return
> becomes $r_p - r_f$ and tracking error becomes the volatility of the excess
> return — which is the Sharpe ratio exactly. They are not two concepts. Sharpe
> is the special case where your mandate is "don't lose to a T-bill."

### Which benchmark is right?

Whichever one the manager was hired against. That is a contractual question:

| Mandate | Benchmark |
|---|---|
| US large-cap equity fund | S&P 500 |
| Value manager | Russell 1000 Value — *not* the S&P, or they get credit for the value tilt itself |
| Balanced / pension fund | 60% equities, 40% bonds |
| Liability-driven pension | Long-duration government bonds |
| Hedge fund, absolute return | Cash |

> **⚠️ Caution: benchmark choice is where performance gets manufactured**
>
> A value manager benchmarked against the *broad market* gets paid for simply
> being a value manager — the whole style tilt shows up as active return. The
> same manager benchmarked against a *value index* has to beat other value
> managers.
>
> Our fund's IR against the market is 0.55. Against a proper value benchmark it
> would be far lower, because most of that 5% active return **is** the value
> tilt.

That last point is the opening for today. "Most of the active return is the
value tilt" is a claim about *decomposition*, and a benchmark comparison can't
make it precisely. A regression can.

### Or: let the data build the benchmark

There is a third option nobody offers you in a mandate. Instead of picking a
benchmark off a list, **construct the combination of factors that best
replicates the fund**, and use that:

$$r^b_t = \sum_j \beta_j f_{j,t}$$

This is an **endogenous benchmark** — the fitted value of a factor regression.
Whatever mix of market, size and value the manager was actually running, the
regression finds it, and you measure them against that mix rather than against
a label.

> **💡 Key Insight: alpha is scarce, beta is plentiful — pay different prices**
>
> This is how large allocators actually think. Beta exposure is available for a
> few basis points in an ETF, so nobody should pay a performance fee for it.
> Alpha is hard to find and worth paying for. The whole job is telling them
> apart, and a factor regression is the tool that does it.
>
> The gains from beta come from **implementation** — getting it cheaply. The
> gains from alpha come from **selection** — finding someone who has it."""))

# ─── Pitfalls ─────────────────────────────────────────────────────────
cells.append(md("""---

## 🛡️ Pitfall Checklist for Factor Regressions <a id="pitfalls"></a>

| | Pitfall | What goes wrong | 🔍 How to detect |
|---|---|---|---|
| 1 | **Total returns on the left, excess on the right** | α absorbs the risk-free rate and is badly biased | Did you subtract `RF` from the stock's return? |
| 2 | **No intercept** | `sm.OLS(y, X)` without `add_constant` forces α = 0 and biases β | Is there a `const` row in the summary? |
| 3 | **Mixed frequencies** | Monthly returns on daily factors | Do both sides have the same number of rows? |
| 4 | **Reading a high R² as good** | R² measures how much is *market*, not how much is *skill* | R² near 1 means almost no alpha is possible |
| 5 | **Annualizing α wrong** | α is per-period; ×12 for monthly, not ×√12 | Volatility scales by √12, means by 12 |
| 6 | **Trusting α without its t-stat** | A big α on a short sample is noise | Is |t| > 2? Over how many months? |

> **🤖 AI-Era Insight**
>
> Pitfall 2 is the one to watch. `sm.OLS(y, x).fit()` runs perfectly happily
> without a constant and reports a beta — which is now wrong, because the
> regression line is forced through the origin. Nothing warns you. Always look
> for `const` in the output."""))

# ─── Live demo ────────────────────────────────────────────────────────
cells.append(md(r"""---

## 🔄 Live Demo: Was GE Skill, or Beta? <a id="demo"></a>

In Lecture 1 you found that General Electric returned 8,443% from 1980 to 2000
— a Sharpe ratio of **0.773** against the market's **0.601** — and I asked
whether that proved Jack Welch was exceptional. Most of you noticed GE was more
volatile: **22.2%** against the market's **15.6%**.

The natural suspicion is that GE was simply a *levered* bet on a bull market.
Sharpe cannot tell you. A regression can.

### The decomposition

$$r^e_t = \alpha + \beta \, r^e_{m,t} + \varepsilon_t$$

| Term | Meaning |
|---|---|
| $\beta \, r^e_m$ | The part you could have had by holding the market with leverage — cheap |
| $\alpha$ | Average return **not** explained by market exposure |
| $\varepsilon$ | Idiosyncratic noise — diversifiable, so nobody pays you for it |

### The same equation does two different jobs

Worth separating these, because they get conflated constantly:

| | **Risk model** | **Expected-return model** |
|---|---|---|
| Uses | $\beta$ and $\sigma_\varepsilon$ | $\alpha$ |
| Asks | how much will this move, and with what? | will this earn anything? |
| Concerns the | *second* moment | *first* moment |
| Used by | risk managers, portfolio construction | signal researchers, allocators |

A model can be excellent at one job and useless at the other. The market factor
explains 56% of GE's variance — a serviceable risk model. It says essentially
nothing about whether GE will earn anything next year.

> **📌 Remember**
>
> Never say "the model works." Say which job it is doing. A high R² is good news
> for the risk model and *bad* news for the alpha hunter, because it means less
> is left over.

### Step 1 — The specification

> **📝 Spec**
>
> Take GE (permno 12060) monthly returns 1980–2000 from the panel. Subtract the
> risk-free rate `RF` to get excess returns. Regress on `Mkt-RF` **with an
> intercept**, using statsmodels. Report α annualized (×12), β, R², the t-stat
> on α, and the standard deviation of the residuals annualized (×√12).

### Step 2 — Implementation

> **🤖 AI prompt:**
>
> *"Given a monthly Series of GE returns and a DataFrame ff with columns Mkt-RF
> and RF, compute GE's excess return, regress it on Mkt-RF with an intercept
> using statsmodels OLS, and print annualized alpha, beta, R-squared, the t-stat
> on alpha, and annualized residual volatility."*"""))

cells.append(code("""ge  = panel[panel.permno == 12060].set_index('date')['ret'].loc['1980-01-31':'2000-12-31']
y   = (ge - ff['RF']).dropna()                       # excess return (pitfall 1)
X   = sm.add_constant(ff.loc[y.index, 'Mkt-RF'])     # intercept (pitfall 2)
m   = sm.OLS(y, X).fit()

alpha_m, beta = m.params['const'], m.params['Mkt-RF']
idio = m.resid.std() * np.sqrt(12)

print(f"GE on the market, {len(y)} months\\n")
print(f"  alpha   {alpha_m*12:+.2%}/yr     t = {m.tvalues['const']:.2f}")
print(f"  beta    {beta:.2f}              t = {m.tvalues['Mkt-RF']:.1f}")
print(f"  R²      {m.rsquared:.2f}")
print(f"  idio vol {idio:.2%}/yr")"""))

cells.append(md("""### Step 3 — Validate, then read it

Check the pitfalls: excess returns on the left ✅, `const` present ✅, both
series monthly ✅, α annualized by ×12 ✅.

Now read it.

> **🤔 Before I say anything — what does β = 1.07 tell you?**

**GE was not a levered market bet.** Its beta is 1.07 — essentially the market.
If leverage had explained GE's higher volatility, β would have come in near 1.4.

So where did the extra volatility come from? Not the market. Let's split it."""))

# ─── decomposition ────────────────────────────────────────────────────
cells.append(md(r"""---

## 3. Decomposing Risk, Hedging, and the Risk Budget <a id="decomp"></a>

Because $\varepsilon$ is uncorrelated with the factor by construction, variance
splits cleanly in two:

$$\underbrace{\sigma^2}_{\text{total}} = \underbrace{\beta^2\sigma_m^2}_{\text{systematic}} + \underbrace{\sigma_\varepsilon^2}_{\text{idiosyncratic}}$$

Note it's *variances* that add, not volatilities — so the two pieces combine
like the sides of a right triangle, not like a sum."""))

cells.append(code("""tot_vol = y.std() * np.sqrt(12)
sys_vol = beta * ff['Mkt-RF'].std() * np.sqrt(12)

print(f"GE total volatility      {tot_vol:6.2%}")
print(f"  systematic (beta*mkt)  {sys_vol:6.2%}")
print(f"  idiosyncratic          {idio:6.2%}")
print(f"  check: sqrt({sys_vol:.4f}^2 + {idio:.4f}^2) = {np.sqrt(sys_vol**2 + idio**2):.2%}\\n")
print(f"share of variance from the market (= R²): {m.rsquared:.0%}")
print(f"share idiosyncratic:                      {1-m.rsquared:.0%}")"""))

cells.append(md("""> **💡 Key Insight: the volatility was real, and it wasn't the market**
>
> GE ran 22.2% volatility against the market's 15.6%. The excess did **not**
> come from levered market exposure — β is 1.07. It came from **14.6% of
> idiosyncratic volatility**, GE-specific risk that had nothing to do with the
> index.
>
> The week-1 suspicion was reasonable and it was wrong. This is why you run the
> regression instead of reasoning from volatility.

> **⚠️ Caution: R² is not a quality measure**
>
> GE's R² is 0.56. That is not "56% good." It says 56% of GE's variance was
> market movement. A *higher* R² would mean *less* room for alpha, not more. An
> index fund has R² ≈ 1.00 and zero alpha by construction."""))

# ─── hedging + risk budget ────────────────────────────────────────────
cells.append(md(r"""### Why anyone bothers: the hedged portfolio

The decomposition isn't just accounting. It tells you how to *build* something.

Hold GE and short $\beta$ units of the market. The systematic term cancels:

$$r^e - \beta r^e_m = \alpha + \varepsilon$$

You are left with alpha plus idiosyncratic noise, and **no market exposure at
all**. This is the hedged portfolio, and its volatility is $\sigma_\varepsilon$ —
14.6% instead of GE's 22.2%.

Now suppose your CIO gives you a **risk budget**: you may run \$5M of annualized
volatility in this position, no more. How much GE can you hold?"""))

cells.append(code("""BUDGET = 5_000_000       # $ of annualized volatility you're allowed to run

pos_unhedged = BUDGET / tot_vol      # $ position that uses the whole budget
pos_hedged   = BUDGET / idio

print(f"{'':22s}{'volatility':>12s}{'position':>16s}{'alpha P&L':>13s}")
print("-"*64)
for name, vol, pos in [('GE, unhedged', tot_vol, pos_unhedged),
                       ('GE, market-hedged', idio, pos_hedged)]:
    print(f"{name:22s}{vol:>12.2%}{pos:>16,.0f}{pos*alpha_m*12:>13,.0f}")

print(f"\\nHedging lets you hold {pos_hedged/pos_unhedged-1:.0%} more GE for the same risk budget,")
print(f"and therefore earn {pos_hedged/pos_unhedged-1:.0%} more alpha dollars.")"""))

cells.append(md("""> **💡 Key Insight: hedging converts risk budget into alpha capacity**
>
> Your risk budget is scarce. Every unit of it spent on market exposure — which
> you could have bought for five basis points — is a unit not spent on the thing
> you are actually being paid for.
>
> Strip the market out and the same budget carries a **50% larger** position in
> the part you have a view on. That is the entire economic case for hedging, and
> it is why the appraisal ratio (next section) is the number that matters when
> you already own the market.

> **📌 Remember: this is how the industry is organized**
>
> The split runs straight through the business. **Beta is plentiful and cheap** —
> index funds, futures, ETFs, a few basis points. **Alpha is scarce and dear** —
> hedge funds, 2-and-20, capacity-constrained.
>
> The reason those are separate products at separate prices is precisely the
> decomposition on this page. Anyone charging an alpha fee for something with
> β = 1.0 and α = 0 is selling you beta at an alpha price, and a regression is
> how you catch them. Which is what we'll do next."""))

# ─── appraisal ────────────────────────────────────────────────────────
cells.append(md(r"""---

## 4. The Appraisal Ratio <a id="appraisal"></a>

Now the third question: **was any of it something you couldn't have bought
cheaply?**

You can buy market exposure for about five basis points. So the part of GE's
return that came from β is not worth paying a manager for. What's left is α —
and the risk you had to carry to get it is the *idiosyncratic* risk, because the
systematic part was never yours in the first place.

$$AR = \frac{\alpha}{\sigma_\varepsilon}$$

That is the **appraisal ratio**: alpha per unit of the risk you couldn't
diversify or replicate."""))

cells.append(code("""sharpe_ge  = y.mean()/y.std()*np.sqrt(12)
mkt        = ff['Mkt-RF']
sharpe_mkt = mkt.mean()/mkt.std()*np.sqrt(12)

print(f"{'':22s}{'Sharpe':>9s}{'Appraisal':>12s}")
print("-"*43)
print(f"{'GE':22s}{sharpe_ge:>9.3f}{alpha_m*12/idio:>12.3f}")
print(f"{'The market':22s}{sharpe_mkt:>9.3f}{0.0:>12.3f}   <- by definition")"""))

cells.append(md(r"""### Why the appraisal ratio is lower than the Sharpe ratio

GE's Sharpe is 0.773; its appraisal ratio is 0.487.

The Sharpe ratio credits GE for *everything* it earned, including the part that
was just market exposure at β = 1.07. The appraisal ratio credits it only for α.
Strip out the free part and the number falls.

### They were never three ratios

Go back to the endogenous benchmark from Section 2 — the fitted value
$r^b = \sum_j \beta_j f_j$. Measure the information ratio against *that*:

$$r - r^b = \alpha + \varepsilon
\qquad\Longrightarrow\qquad
IR = \frac{\text{mean}(\alpha + \varepsilon)}{\text{sd}(\alpha + \varepsilon)} = \frac{\alpha}{\sigma_\varepsilon}$$

which **is** the appraisal ratio, exactly.

So there is one formula — active return over tracking error — and the only thing
that changes is what you benchmark against:

| | = information ratio against… | Use when |
|---|---|---|
| **Sharpe** | cash | this is your whole portfolio |
| **Information ratio** | your mandate | you were hired to beat something |
| **Appraisal ratio** | **the endogenous benchmark** | you already hold the factors |

> **📌 Remember**
>
> Picking a performance measure *is* picking a benchmark. Sharpe assumes your
> alternative was a T-bill. The appraisal ratio assumes your alternative was a
> cheap replicating portfolio of factors — which, for anyone who can buy ETFs,
> is the honest comparison.

### And it can reverse the ranking

Here is the value long-short from Lecture 3, run through the same regression."""))

cells.append(code("""q = dv[dv.exchcd == 1].groupby('date')['BM'].quantile([.1,.9]).unstack().rename(
        columns={0.1:'lo', 0.9:'hi'})
dl = panel.merge(bm, on=['permno','date'], how='inner').dropna(subset=['BM','ret_fwd','me'])
dl = dl.merge(q, on='date')
dl['g'] = np.where(dl.BM <= dl.lo, 0, np.where(dl.BM >= dl.hi, 9, np.nan))
dl = dl.dropna(subset=['g'])
pp = dl.groupby(['date','g']).apply(lambda g: np.average(g['ret_fwd'], weights=g['me'])).unstack()
ls = (pp[9] - pp[0]).dropna()
ls.index = ls.index + pd.offsets.MonthEnd(1)          # align to the month earned

j  = pd.concat([ls.rename('ls'), ff['Mkt-RF']], axis=1).dropna()
m2 = sm.OLS(j.ls, sm.add_constant(j['Mkt-RF'])).fit()
idio2 = m2.resid.std()*np.sqrt(12)

print(f"Value long-short (NYSE breakpoints, value-weighted)\\n")
print(f"  mean      {j.ls.mean()*12:+.2%}/yr")
print(f"  alpha     {m2.params['const']*12:+.2%}/yr   t = {m2.tvalues['const']:.2f}")
print(f"  beta      {m2.params['Mkt-RF']:+.2f}")
print(f"  R²        {m2.rsquared:.3f}\\n")
print(f"{'':22s}{'Sharpe':>9s}{'Appraisal':>12s}")
print("-"*43)
print(f"{'GE':22s}{sharpe_ge:>9.3f}{alpha_m*12/idio:>12.3f}")
print(f"{'Value long-short':22s}{j.ls.mean()/j.ls.std()*np.sqrt(12):>9.3f}"
      f"{m2.params['const']*12/idio2:>12.3f}")"""))

cells.append(md("""### The two ratios disagree

**Sharpe ranks GE well above the value strategy. Appraisal ranks the value
strategy above GE.**

The reason is in the beta. The value long-short has β = **−0.21** — it leans
slightly *against* the market. That negative exposure dragged on its raw return
during a twenty-year bull market, so its Sharpe looks mediocre. Strip the market
out and its alpha (**+7.2%/yr**) is actually *larger* than its raw return
(+5.3%/yr).

> **💡 Key Insight**
>
> For an investor who already owns the market, the appraisal ratio is the
> relevant number, and it says the value strategy is the better addition. For an
> investor choosing one single thing to own, Sharpe is right and GE wins.
>
> **The ratios don't disagree because one is wrong. They answer different
> questions.** Know which one you're asking."""))

cells.append(md("""> **⚠️ Caution: two things we are not doing today**
>
> GE's alpha has **t = 2.19** over twenty years — statistically marginal, and we
> haven't asked how many stocks we'd have to look at before finding one that
> good by chance. We also picked GE *because* it was famous.
>
> Both of those are serious problems, and both are Lectures 7 and 8."""))

# ─── ARKK vs Berkshire ────────────────────────────────────────────────
cells.append(md("""---

## 5. Two Famous Funds <a id="funds"></a>

Enough with single stocks. Let's point this at two managers you've heard of.

**Cathie Wood's ARK Innovation (ARKK)** — disruptive technology, genomics, AI.
Spectacular returns and a huge following.

**Warren Buffett's Berkshire Hathaway (BRK)** — the most famous track record in
finance.

Both against the six-factor model. Watch what separates them."""))

cells.append(code("""funds = pd.read_pickle('https://raw.githubusercontent.com/amoreira2/Fin418/'
                       'main/assets/data/df_WarrenBAndCathieW_monthly.pkl')
funds.columns = [c.strip() for c in funds.columns]      # 'Mom   ' has trailing spaces
FACT = ['Mkt-RF','SMB','HML','RMW','CMA','Mom']

rows = {}
for nm in ['ARKK','BRK']:
    d = funds.dropna(subset=[nm])
    y = d[nm] - d['RF']
    m = sm.OLS(y, sm.add_constant(d[FACT])).fit()
    iv = m.resid.std()*np.sqrt(12)
    rows[nm] = dict(months=len(y), ret=y.mean()*12, vol=y.std()*np.sqrt(12),
                    sharpe=y.mean()/y.std()*np.sqrt(12),
                    alpha=m.params['const']*12, t=m.tvalues['const'],
                    r2=m.rsquared, appraisal=m.params['const']*12/iv,
                    **{f: m.params[f] for f in FACT})
R = pd.DataFrame(rows).T

print(f"{'':12s}{'months':>8s}{'return':>9s}{'vol':>8s}{'Sharpe':>8s}")
for n in ['ARKK','BRK']:
    r = R.loc[n]
    print(f"{n:12s}{int(r.months):>8d}{r.ret:>8.1%}{r.vol:>8.1%}{r.sharpe:>8.2f}")
print(f"\\n{'':12s}{'alpha':>9s}{'t':>7s}{'R²':>7s}{'appraisal':>11s}")
for n in ['ARKK','BRK']:
    r = R.loc[n]
    print(f"{n:12s}{r.alpha:>8.1%}{r.t:>7.2f}{r.r2:>7.2f}{r.appraisal:>11.2f}")
print(f"\\n{'':12s}" + "".join(f"{f:>9s}" for f in FACT))
for n in ['ARKK','BRK']:
    print(f"{n:12s}" + "".join(f"{R.loc[n,f]:>+9.2f}" for f in FACT))"""))

cells.append(md("""### Read the loadings before the alpha

**ARKK has the better Sharpe ratio — 0.96 against 0.64.** On the Lecture 1
measure it wins comfortably. Now look at what it is made of.

`Mkt-RF = +1.54` — half again as much market exposure as the market itself.
`HML = −0.95` — a large *growth* tilt. `RMW = −0.81` — tilted toward
**unprofitable** firms. `CMA = −0.53` — toward heavy investors.

That is a recognizable style: **levered, small, unprofitable growth.** And
`R² = 0.84` says 84% of ARKK's month-to-month variation is that style, not
stock selection. Its alpha is +8.2%/yr with **t = 1.23** — not distinguishable
from zero.

Berkshire is the mirror image. `Mkt-RF = +0.69` — *defensive*, less market risk
than the market. `HML = +0.57` — value. `RMW = +0.35` — profitable, quality
firms. R² = 0.40, so most of what Berkshire did is *not* explained by the six
factors.

> **💡 Key Insight: the same tools, opposite readings**
>
> Buffett's reputation is stock-picking genius. The regression says a large part
> of it is a **systematic, describable style** — buy cheap, profitable, low-beta
> companies and hold them — which is now sold as a "quality" ETF. That is not a
> debunking. It is the discovery that his edge was a repeatable idea, decades
> before anyone packaged it.
>
> ARKK's returns are 84% a levered growth bet, over 59 months that happened to
> be a growth bull market.

> **⚠️ Caution: read the sample lengths**
>
> Berkshire has 279 months. ARKK has **59**. Neither alpha clears |t| > 2, and
> ARKK's window is a single regime. This is a demonstration of the *method*, not
> a verdict on either manager — and how to reason about that gap is Lecture 7."""))

# ─── Hands-On ─────────────────────────────────────────────────────────
cells.append(md("""---

## 🛠️ Hands-On: Does Your Signal Have Alpha? <a id="ho1"></a>

In Lecture 3 you each picked a signal and computed its long-short return. Now
run it through a factor regression and find out how much of it was market
exposure.

> **🤔 Predict first.** A long-short is roughly market-neutral by construction —
> you're long some stocks and short others. So do you expect β near zero? Commit
> before running."""))

cells.append(code("""# === EDIT THIS CELL: your signal from Lecture 3 ===
MY_SIGNAL = "GP"      # ← your pick

sig = pd.read_parquet(f"{BASE}/signals/{MY_SIGNAL}.parquet")
x = panel.merge(sig, on=['permno','date'], how='inner').dropna(subset=[MY_SIGNAL,'ret_fwd','me'])
qq = (x[x.exchcd == 1].groupby('date')[MY_SIGNAL].quantile([.1,.9]).unstack()
        .rename(columns={0.1:'lo', 0.9:'hi'}))
x = x.merge(qq, on='date')
x['g'] = np.where(x[MY_SIGNAL] <= x.lo, 0, np.where(x[MY_SIGNAL] >= x.hi, 9, np.nan))
x = x.dropna(subset=['g'])
px = x.groupby(['date','g']).apply(lambda g: np.average(g['ret_fwd'], weights=g['me'])).unstack()
r  = (px[9] - px[0]).dropna()
r.index = r.index + pd.offsets.MonthEnd(1)"""))

cells.append(code("""# === YOUR TURN ===
# Fill in the two blanks to regress your long-short on the market.

jj = pd.concat([r.rename('r'), ff['Mkt-RF']], axis=1).dropna()

mm = ____        # hint: sm.OLS(jj.r, sm.add_constant(jj['Mkt-RF'])).fit()
iv = ____        # hint: mm.resid.std() * np.sqrt(12)

print(f"{MY_SIGNAL}")
print(f"  raw return  {jj.r.mean()*12:+7.2%}/yr    Sharpe    {jj.r.mean()/jj.r.std()*np.sqrt(12):.2f}")
print(f"  alpha       {mm.params['const']*12:+7.2%}/yr    t = {mm.tvalues['const']:.2f}")
print(f"  beta        {mm.params['Mkt-RF']:+7.2f}")
print(f"  R²          {mm.rsquared:7.3f}")
print(f"  appraisal   {mm.params['const']*12/iv:+7.2f}")"""))

cells.append(md("""### Compare with the room

Two things to look for, and to say out loud:

- **Is your β near zero?** Most long-shorts are, but not all. A signal
  correlated with size or volatility often carries real market exposure without
  anyone intending it.
- **Is your alpha bigger or smaller than your raw return?** Bigger means
  negative beta was *hurting* you. Smaller means part of what looked like signal
  was just market."""))

# ─── Challenge ────────────────────────────────────────────────────────
cells.append(md("""---

## 🎯 Challenge: Exxon vs Pfizer <a id="challenge"></a>

*Homework — due before Lecture 5.*

Two of the largest US companies, both public for the whole 1980–2000 sample.
Their Sharpe ratios are **0.720** and **0.718** — indistinguishable.

Your CIO already holds the market and wants to add one satellite position. Run
the regressions and tell them which.

- **Exxon** is permno **11850**
- **Pfizer** is permno **21936**

### Q1 — Exxon

> **📌 Required variable names:**
> ```python
> xom_alpha_ann = ____   # annualized alpha, e.g. 0.05 for 5%/yr
> xom_beta      = ____
> xom_appraisal = ____   # annualized alpha / annualized idiosyncratic vol
> ```"""))

cells.append(code("""# Your work here


# Required outputs — fill these in:
xom_alpha_ann = ____
xom_beta      = ____
xom_appraisal = ____

print(f"Exxon: alpha {xom_alpha_ann:+.2%}/yr  beta {xom_beta:.2f}  appraisal {xom_appraisal:.3f}")"""))

cells.append(md("""### Q2 — Pfizer

> **📌 Required variable names:**
> ```python
> pfe_alpha_ann = ____
> pfe_beta      = ____
> pfe_appraisal = ____
> ```"""))

cells.append(code("""# Your work here


# Required outputs — fill these in:
pfe_alpha_ann = ____
pfe_beta      = ____
pfe_appraisal = ____

print(f"Pfizer: alpha {pfe_alpha_ann:+.2%}/yr  beta {pfe_beta:.2f}  appraisal {pfe_appraisal:.3f}")"""))

cells.append(md("""### Q3 — The memo

> **📝 Your task — maximum 6 sentences**
>
> Their Sharpe ratios are the same. Once you have the regressions, are these two
> positions interchangeable?
>
> Address: what is *different* about how each one earned its return; whether the
> appraisal ratio separates them; and what a CIO who already owns the market
> should care about that neither ratio captures.
>
> There is a defensible answer in either direction. I'm grading the reasoning."""))

cells.append(code('''MEMO = """
Write your memo here. Don't delete the surrounding triple quotes.
"""
print(MEMO)'''))

cells.append(md("---\n\n## 📤 Submission <a id=\"submit\"></a>"))

cells.append(code('''# === 📤 SUBMISSION CELL — Run this last ===
import json, base64, hashlib, datetime as dt

required = ["xom_alpha_ann", "xom_beta", "xom_appraisal",
            "pfe_alpha_ann", "pfe_beta", "pfe_appraisal", "MEMO"]
missing = [v for v in required if v not in dir()]
if missing:
    raise NameError(f"\\n❌ Missing before submission: {missing}")

payload = {
    "assignment": "L4_PerfEval_AI",
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
print("Submission form: https://forms.gle/YOUR_FORM_LINK_HERE")'''))

cells.append(md("""---

## 🧠 Key Takeaways <a id="takeaways"></a>

1. **Three ratios, three questions.** Sharpe: was it worth the risk? Information:
   did I beat my mandate? Appraisal: was any of it mine?

2. **Sharpe is the information ratio against cash.** Not a separate idea.

3. **The benchmark is a choice, and it manufactures performance.** A value
   manager measured against the broad market gets paid for the tilt itself.

4. **α is what the factor doesn't explain; β is what you could have bought
   cheaply.** That is the whole point of the regression.

5. **Variances add, volatilities don't:** σ² = β²σ²ₘ + σ²ε.

6. **R² is not a quality score.** High R² means *less* room for alpha.

7. **GE was skill, not leverage.** β = 1.07, α = +7.1%/yr. The extra volatility
   was idiosyncratic. The week-1 suspicion was reasonable and wrong — which is
   why you run the regression.

8. **A factor model does two separate jobs** — risk (β, σ_ε) and expected return
   (α). A high R² is good for the first and bad for the second.

9. **Hedging converts risk budget into alpha capacity.** Stripping GE's market
   exposure lets the same $5M vol budget carry ~50% more position.

10. **Alpha is scarce, beta is plentiful — pay different prices.** That split is
   why index funds and hedge funds are different products.

11. **ARKK had the better Sharpe and an R² of 0.84.** Most of it was a levered
   growth style. Buffett's R² was 0.40 — but much of *his* edge turned out to be
   a describable value-and-quality tilt too.

12. **Sharpe and appraisal can rank things differently**, and neither is wrong.
   The value long-short has a worse Sharpe and a better appraisal because its
   β is negative. Which matters depends on what you already own.

---

### Next class

Where do factors come from? We used the market because it was obvious. Next:
the other factors people use, where they came from, and how you'd choose."""))

cells.append(md("---\n\n## 📎 Appendix <a id=\"appendix\"></a>"))

cells.append(code(f'''# ═══════════════════════════════════════════════════════════════════════
# 📎 APPENDIX — Belt-and-Suspenders Data Loading
# ═══════════════════════════════════════════════════════════════════════
#   panel = pd.read_parquet(f"{{BASE}}/panel_backbone_1980_2000.parquet")
#
# Fama-French factors are fetched live from Ken French's library. Prompt:
# "Using pandas-datareader, fetch F-F_Research_Data_Factors monthly from the
#  famafrench source starting 1980, convert the PeriodIndex to month-end
#  timestamps, and divide by 100 to get decimals."
def fetch_ff_monthly():
    import pandas_datareader.data as web
    f = web.DataReader('F-F_Research_Data_Factors', 'famafrench', start='1980-01-01')[0]
    f.index = pd.to_datetime(f.index.to_timestamp()) + pd.offsets.MonthEnd(0)
    return f / 100

# Backup if Ken French is unreachable:
# ff = pd.read_csv("{BASE}/ff_monthly.csv", index_col=0, parse_dates=True)
'''))

notebook = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.11"},
        "colab": {"provenance": []},
    },
    "nbformat": 4, "nbformat_minor": 5,
}
OUT.write_text(json.dumps(notebook, indent=1))
print(f"✅ Wrote {OUT}  ({len(cells)} cells)")
