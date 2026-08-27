"""
Build L7_Portfolio_Decomposition_AI.ipynb — new Lecture 7.

"Decomposing a Portfolio: Three Approaches"   (multi-asset factor models)

This is the multi-asset lecture. Everything until now regressed ONE return
series. Here we go to r = alpha + Bf + eps across many assets, portfolio
exposures b = B'w, the covariance decomposition Omega = B Omega_f B' + Omega_e,
top-down vs bottom-up, and characteristic-adjusted returns.

Worked example: BERKSHIRE HATHAWAY, real 13F holdings from WRDS
(tr_13f.s34type3, mgrno 8350), cached to assets/data/brk_13f_holdings.csv by
build_brk_holdings.py. All numbers verified 2026-08-07.

The lecture is about METHOD, not about a verdict on Buffett. Three routes to
"what is this portfolio exposed to", each with different data requirements and
different failure modes:

  A  TOP-DOWN     regress the fund's own returns
                  CAPM: beta 0.68 (se 0.26), R2 0.15, n=41
                  FF6 : Mkt 0.62 (se 0.35), HML +2.08 (se 0.61), CMA -2.20 (se 1.01)
                  -> loadings are UNSTABLE and the SEs say so. Show them.

  B  BOTTOM-UP    betas of each holding, weighted:  b = B'w
                  CAPM: 1.08     FF6: Mkt 1.51, HML +0.18, CMA +0.80
                  risk: factor 17.7% / specific 10.6% / total 20.6%, 73% factor
                  Coca-Cola alone is 67% of SPECIFIC variance

  C  CHARACTERISTIC-ADJUSTED   no betas at all; portfolio z-scores x FM premia
                  logME +2.45, BM -1.65, GP +0.72, Mom -0.27
                  implied return -16.4%/yr  <- the disclosed book scores as
                  GIANT and EXPENSIVE by 1999

C is the surprise and the best discussion in the lecture: the famous value
investor's 1999 holdings look like *growth* on characteristics, because he
bought them cheap in the 1980s and held. A characteristic snapshot tells you
what you own now, not what you paid. Direct callback to L3's MSFT migration.

MOTIVATION (§1): Berkshire's disclosed book visibly moves --
  1993  Coca-Cola 37%, Gillette 13%, Capital Cities 11%
  1996  Coca-Cola 56%, Gillette 20%, Wells Fargo 11%
  1999  Coca-Cola 41%, American Express 30%, Gillette 14%
top-3 concentration ranges 63%-96%. So a single time-series regression averages
over a moving target: it recovers true exposure only if (i) positions are stable
AND (ii) the firms' own betas are stable. Neither holds. We show this and move
on -- no proof needed.
"""

import json
from pathlib import Path

OUT = Path(__file__).parent / "L7_Portfolio_Decomposition_AI.ipynb"
BASE = "https://raw.githubusercontent.com/amoreira2/UG54/refs/heads/main/assets/data"


def md(t): return {"cell_type": "markdown", "metadata": {}, "source": t.splitlines(keepends=True)}
def code(t): return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": t.splitlines(keepends=True)}


cells = []

cells.append(md("""# Decomposing a Portfolio: Three Approaches
## Lecture 7

## 🎯 Learning Objectives

By the end of today you will be able to:

1. **Write the factor model for many assets at once** — `r = α + Bf + ε` — and
   compute a portfolio's factor exposures as `b = B′w`
2. **Split portfolio risk** into factor and specific components using
   `Ω = BΩ_f B′ + Ω_ε`
3. **Run all three decomposition routes** — top-down, bottom-up, and
   characteristic-adjusted — on the same portfolio
4. **Say what each route needs, and how each one fails**
5. **Explain why they disagree**, and which disagreements are economics rather
   than noise"""))

cells.append(md("""## 📋 Today's Plan

1. [Why one regression isn't enough](#motivation)
2. [The portfolio: Berkshire, 1999](#snapshot)
3. [Pitfall checklist](#pitfalls)
4. [Approach A — top-down](#topdown)
5. [Approach B — bottom-up](#bottomup)
6. [Splitting the risk](#risk)
7. [Approach C — characteristic-adjusted](#chars)
8. [The trade-offs](#tradeoffs)
9. [🎯 Challenge](#challenge) — *homework*
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
HOLD  = pd.read_csv(f"{{BASE}}/brk_13f_holdings.csv", parse_dates=['fdate'])

f5  = web.DataReader('F-F_Research_Data_5_Factors_2x3','famafrench',start='1980-01-01')[0]/100
umd = web.DataReader('F-F_Momentum_Factor','famafrench',start='1980-01-01')[0]/100
for x in (f5, umd):
    x.index = pd.to_datetime(x.index.to_timestamp()) + pd.offsets.MonthEnd(0)
umd.columns = ['UMD']
FF = f5.join(umd, how='inner')

funds = pd.read_pickle('https://raw.githubusercontent.com/amoreira2/Fin418/'
                       'main/assets/data/df_WarrenBAndCathieW_monthly.pkl')
funds.columns = [c.strip() for c in funds.columns]

print(f"13F holdings: {{len(HOLD)}} position-dates over {{HOLD.fdate.nunique()}} quarterly filings")
print(f"  {{HOLD.fdate.min().date()}} to {{HOLD.fdate.max().date()}}")"""))

# ─── 1. motivation ────────────────────────────────────────────────────
cells.append(md("""---

## 1. Why One Regression Isn't Enough <a id="motivation"></a>

In Lecture 4 you regressed Berkshire's returns on six factors and read off its
exposures. One regression, one set of betas, done.

That answer is only right if **two things are true at once**:

1. The portfolio held roughly the same positions across the whole window
2. Those firms' own betas were roughly stable across the whole window

Let's look at the first one. Berkshire files a **13F** every quarter — a public
disclosure of its US equity holdings. Here is what it actually held."""))

cells.append(code("""top3 = HOLD.groupby('fdate').apply(lambda g: g.nlargest(3,'weight').weight.sum())
npos = HOLD.groupby('fdate').size()

fig, ax = plt.subplots(1, 2, figsize=(13, 4))
ax[0].plot(top3.index, top3.values, marker='o', ms=3, color='steelblue')
ax[0].set_ylabel('weight in top 3'); ax[0].set_ylim(0, 1)
ax[0].set_title('Concentration of the disclosed book', fontweight='bold')
ax[1].plot(npos.index, npos.values, marker='o', ms=3, color='darkorange')
ax[1].set_ylabel('positions reported')
ax[1].set_title('Number of disclosed positions', fontweight='bold')
plt.tight_layout(); plt.show()

for dt in ['1993-12-31','1996-12-31','1999-12-31']:
    g = HOLD[HOLD.fdate == dt].nlargest(4, 'weight')
    print(f"{dt}:  " + ",  ".join(f"{r.comnam.title()[:22]} {r.weight:.0%}" for _, r in g.iterrows()))"""))

cells.append(md("""### The portfolio is not a fixed object

Coca-Cola runs from 37% of the book in 1993 to **56%** in 1996 and back to 41%
in 1999. Capital Cities is a major position and then vanishes — Disney bought it
in 1996. Wells Fargo appears, then goes. American Express grows to nearly a
third.

> **📌 So what does a single time-series regression measure?**
>
> An **average** over all of that. It is not Berkshire's exposure in 1999; it is
> a blend of every portfolio Berkshire held during the window, weighted by
> nothing in particular.
>
> That is fine if you want a summary of the past. It is the wrong tool if you
> want to know what you are exposed to **now** — which is what a risk manager
> needs.

> **⚠️ Caution: the position count is a data artifact, not turnover**
>
> The right-hand panel drops to **5 positions** in 1997–98 and rises to 29 by
> end-2000. Berkshire's portfolio did not do that. Managers can request
> confidential treatment for positions they are still building, and Thomson's
> coverage varies. Wells Fargo and Freddie Mac were both large Berkshire
> holdings that are missing from some filings entirely.
>
> **You can only decompose what was disclosed.** Hold that thought — it comes
> back at the end."""))

# ─── 2. snapshot ──────────────────────────────────────────────────────
cells.append(md("""---

## 2. The Portfolio: Berkshire, December 1999 <a id="snapshot"></a>

So instead of averaging, take a **snapshot**. One date, one set of weights, and
ask what that portfolio is exposed to."""))

cells.append(code("""S = HOLD[HOLD.fdate == '1999-12-31'].copy()
S['w'] = S.weight / S.weight.sum()
S = S.sort_values('w', ascending=False)

print(f"{len(S)} disclosed positions, ${S.value.sum()/1e9:.1f}B\\n")
print(f"{'':30s}{'weight':>9s}")
for _, r in S.iterrows():
    print(f"  {r.comnam.title()[:28]:30s}{r.w:>8.1%}")
print(f"\\ntop 3 = {S.w.head(3).sum():.0%} of the book")"""))

cells.append(md(r"""### The multi-asset factor model

Everything so far regressed **one** return series. Now we need all of them at
once:

$$r_t = \alpha + B f_t + \varepsilon_t$$

| | shape | what it is |
|---|---|---|
| $r_t$ | n×1 | the n assets' excess returns |
| $B$ | n×m | **loadings matrix** — one row per asset, one column per factor |
| $f_t$ | m×1 | the m factor returns |
| $\varepsilon_t$ | n×1 | idiosyncratic returns, assumed uncorrelated across assets |

And a portfolio with weights $w$ has return $w'r_t$, so its **factor exposure**
is

$$b = B'w$$

an m-vector: the portfolio's loading on each factor, built from the loadings of
what it holds. That single expression is what makes the rest of today possible."""))

# ─── pitfalls ─────────────────────────────────────────────────────────
cells.append(md("""---

## 🛡️ Pitfall Checklist for Portfolio Decomposition <a id="pitfalls"></a>

| | Pitfall | What goes wrong | 🔍 How to detect |
|---|---|---|---|
| 1 | **Treating a time-series beta as current exposure** | It's an average over a portfolio that changed | Did the holdings move during the window? |
| 2 | **Reading 13F as the whole portfolio** | It's US-listed equity only, quarterly, and incomplete | Does the disclosed value match the fund's size? |
| 3 | **Reading position-count changes as turnover** | Confidential treatment and coverage gaps look identical to selling | Is the change plausible as a trade? |
| 4 | **Reporting loadings without standard errors** | On a short window with correlated factors they're barely identified | Is |coefficient| > 2×SE? |
| 5 | **Weights that don't sum to 1 after dropping unmatched names** | Silently rescales your whole decomposition | Renormalize after every merge |
| 6 | **Assuming specific risk diversifies in a concentrated book** | 16 names is not 16 independent bets | What share of specific variance is the top name? |

> **🤖 AI-Era Insight**
>
> Pitfall 4 is today's. Ask for a six-factor attribution on 41 months of data
> and you will get six numbers to two decimal places. Some of them will have
> standard errors as large as the coefficients. The output looks identical
> either way — print the SEs."""))

# ─── A: top-down ──────────────────────────────────────────────────────
cells.append(md("""---

## 3. Approach A — Top-Down <a id="topdown"></a>

The simplest route, and the one from Lecture 4: **regress the fund's own return
series on the factors.** You need nothing but the fund's returns.

> **📝 Spec**
>
> Take Berkshire's monthly excess returns over 1995–1999. Regress on CAPM, then
> on FF6. Report each loading **with its standard error**, plus R² and the
> number of months."""))

cells.append(code("""SPECS = {'CAPM': ['Mkt-RF'],
         'FF6' : ['Mkt-RF','SMB','HML','RMW','CMA','UMD']}
W0, W1 = '1995-01-31', '1999-12-31'

w5  = funds.loc[W0:W1]
brk = (w5['BRK'] - w5['RF']).dropna()

TD = {}
for nm, cols in SPECS.items():
    c = ['Mom' if x == 'UMD' else x for x in cols]          # Ken French calls it Mom
    m = sm.OLS(brk, sm.add_constant(w5.loc[brk.index, c])).fit()
    TD[nm] = pd.Series(m.params[c].values, index=cols)
    print(f"{nm}  (n = {len(brk)} months,  R² = {m.rsquared:.2f})")
    for f, cc in zip(cols, c):
        est, se = m.params[cc], m.bse[cc]
        flag = "" if abs(est) > 2*se else "   ← not 2 SE from zero"
        print(f"   {f:8s}{est:+7.2f}   (se {se:.2f}){flag}")
    print()"""))

cells.append(md("""### Look at the standard errors

The CAPM beta is **0.68 with a standard error of 0.26**. So the data is
comfortable with anything from about 0.16 to 1.20. That is not a precise
measurement.

FF6 is worse. **HML +2.08** and **CMA −2.20** are enormous loadings, and they
have standard errors of 0.61 and 1.01. With 41 months, six factors, and HML and
CMA strongly correlated with each other, the regression is being asked to
separate things it cannot separate.

> **⚠️ Caution: do not read those FF6 numbers as economics**
>
> A loading of +2.08 on value and −2.20 on investment does not mean Berkshire ran
> a levered value book against an investment short. It means the regression
> found a nearly-collinear pair and split them arbitrarily. Re-estimate on a
> slightly different window and both numbers will move a lot.
>
> This is a real limitation of the top-down approach and it gets worse as you
> add factors. More factors means more precision about *less*."""))

# ─── B: bottom-up ─────────────────────────────────────────────────────
cells.append(md("""---

## 4. Approach B — Bottom-Up <a id="bottomup"></a>

Now use the information the regression didn't have: **we know what it holds.**

Estimate a beta for each holding separately, then aggregate with the portfolio
weights:

$$b = B'w = \\sum_i w_i \\beta_i$$

Each row of $B$ is estimated from that stock's own 60 months of returns, so
every one gets its own regression with far more data per parameter than the
fund-level regression had."""))

cells.append(code("""def holding_betas(snap, cols, w0=W0, w1=W1, min_months=48):
    rows = {}
    for _, r in snap.iterrows():
        s = panel[panel.permno == r.permno].set_index('date')['ret'].loc[w0:w1]
        y = (s - FF['RF']).dropna()
        if len(y) < min_months:
            continue
        m = sm.OLS(y, sm.add_constant(FF.loc[y.index, cols])).fit()
        rows[r.comnam.title()[:20]] = dict(w=r.w, rv=m.resid.var(),
                                           **{f: m.params[f] for f in cols})
    B = pd.DataFrame(rows).T
    B['w'] = B.w / B.w.sum()                      # renormalize (pitfall 5)
    return B

BU, BMAT = {}, {}
for nm, cols in SPECS.items():
    B = holding_betas(S, cols)
    BMAT[nm] = B
    BU[nm] = (B[cols].mul(B.w, axis=0)).sum()     # b = B'w
    print(f"{nm}  ({len(B)} of {len(S)} holdings had enough history)")
    print("   " + "   ".join(f"{f}={BU[nm][f]:+.2f}" for f in cols) + "\\n")

print("Individual market betas, largest positions:")
for k, v in BMAT['CAPM'].nlargest(5,'w').iterrows():
    print(f"   {k:22s} w={v.w:5.1%}   beta={v['Mkt-RF']:+.2f}")"""))

cells.append(md("""> **💡 Key Insight: bottom-up tells you about *today***
>
> This number describes the portfolio **as it stands on 31 December 1999**. It
> doesn't average over anything. If Berkshire sold Coca-Cola tomorrow, the
> bottom-up exposure changes tomorrow; the top-down regression wouldn't notice
> for years.
>
> That is why risk systems are built bottom-up. A risk manager needs today's
> exposure, not a five-year average."""))

# ─── risk ─────────────────────────────────────────────────────────────
cells.append(md(r"""---

## 5. Splitting the Risk <a id="risk"></a>

Because $\varepsilon$ is uncorrelated with the factors *and* (by assumption)
across assets, the covariance matrix of returns splits:

$$\Omega = B\,\Omega_f\,B' + \Omega_\varepsilon$$

and the variance of a portfolio splits with it:

$$\underbrace{w'\Omega w}_{\text{total}} = \underbrace{b'\Omega_f b}_{\text{factor risk}} + \underbrace{\sum_i w_i^2 \sigma^2_{\varepsilon,i}}_{\text{specific risk}}$$

The first term is risk you share with everyone. The second is risk specific to
the names you happen to own — the part that would diversify away if you held
enough of them."""))

cells.append(code("""cols = SPECS['FF6']; B = BMAT['FF6']; b = BU['FF6']
Omega_f = FF.loc[W0:W1, cols].cov()

fac_var  = float(b.values @ Omega_f.values @ b.values)
spec_var = float((B.w**2 * B.rv).sum())

print(f"{'factor risk':18s}{np.sqrt(fac_var*12):>8.1%}")
print(f"{'specific risk':18s}{np.sqrt(spec_var*12):>8.1%}")
print(f"{'total (predicted)':18s}{np.sqrt((fac_var+spec_var)*12):>8.1%}")
print(f"\\nshare of variance that is factor risk: {fac_var/(fac_var+spec_var):.0%}")

share = (B.w**2 * B.rv) / spec_var
print(f"\\nWho supplies the specific risk?")
for k, v in share.nlargest(4).items():
    print(f"   {k:22s}{v:>7.0%}")"""))

cells.append(md("""### Two things worth pausing on

**73% of the variance is factor risk.** Even a 16-stock portfolio, hand-picked
by the most famous stock-picker alive, is mostly moving because the market and
the style factors moved.

**Coca-Cola alone is 67% of the *specific* risk.** Specific risk is supposed to
be the diversifiable part — but with 41% of the book in one name, $w_i^2$ does
the damage. Sixteen positions is not sixteen bets.

> **📌 Remember**
>
> Specific risk diversifies **only if the weights are spread**. The $w_i^2$ in
> the formula means a 41% position contributes 0.41² = 17% of the weight-squared,
> and the top three names supply 99% of the specific variance between them."""))

# ─── C: characteristics ───────────────────────────────────────────────
cells.append(md("""---

## 6. Approach C — Characteristic-Adjusted <a id="chars"></a>

A third route, and it needs **no betas at all.**

From Lecture 6, a Fama-MacBeth regression gives the premium earned by each
characteristic — the return to being one standard deviation cheap, or small, or
profitable. So:

1. Compute the portfolio's **characteristic scores**: `Σᵢ wᵢ zᵢ`
2. Multiply each by its estimated premium
3. Add them up — that's the return the portfolio's *characteristics* imply

Subtract it from the actual return and you have a **characteristic-adjusted
return**. It is hedging, without ever estimating a time-series beta."""))

cells.append(code("""d = panel.copy()
for s_ in ['BM','GP','Mom12m']:
    d = d.merge(pd.read_parquet(f"{BASE}/signals/{s_}.parquet"), on=['permno','date'], how='left')
d['logME'] = np.log(d['me'])
CH = ['logME','BM','GP','Mom12m']
d = d.dropna(subset=CH + ['ret_fwd'])
for c in CH:
    d[c+'_z'] = d.groupby('date')[c].transform(
        lambda v: (v.clip(v.quantile(.01), v.quantile(.99)) - v.mean())/v.std())
Z = [c+'_z' for c in CH]

# Fama-MacBeth premia (Lecture 6)
G = pd.DataFrame([sm.OLS(g['ret_fwd'], sm.add_constant(g[Z])).fit().params
                  for _, g in d.groupby('date') if len(g) > 100])
prem = G[Z].mean()

snap = d[d.date == '1999-12-31'].merge(S[['permno','w']], on='permno', how='inner')
pc = (snap[Z].mul(snap.w, axis=0)).sum() / snap.w.sum()

print(f"{len(snap)} of {len(S)} holdings have characteristics\\n")
print(f"{'characteristic':14s}{'portfolio z':>13s}{'premium/yr':>13s}{'contribution':>14s}")
print("-"*54)
for c in Z:
    print(f"{c[:-2]:14s}{pc[c]:>13.2f}{prem[c]*12:>12.2%}{pc[c]*prem[c]*12:>13.2%}")
print("-"*54)
print(f"{'implied return':14s}{'':>13s}{'':>13s}{(pc*prem).sum()*12:>13.2%}")"""))

cells.append(md("""### The value investor was holding growth

Read the z-scores. The portfolio is **+2.45 standard deviations on size** — these
are enormous companies. And **−1.65 on book-to-market**, which means *expensive*.
On profitability it is +0.72, genuinely high quality.

Put those through the premia and the characteristics imply Berkshire's disclosed
book should have **underperformed by about 16% a year**.

> **💡 Key Insight: a characteristic tells you what you own, not what you paid**
>
> Buffett bought Coca-Cola in 1988 at a price that looked cheap. By 1999 it had
> compounded for eleven years and traded at a large multiple of book. The
> *position* was a spectacular value investment. The *stock*, measured in
> December 1999, scores as expensive mega-cap growth.
>
> This is the MSFT migration from Lecture 3, seen from the other side. Buy-and-hold
> means your holdings drift across characteristic buckets while you do nothing.
> A snapshot of characteristics describes the portfolio you have, and says
> nothing about the prices you paid.

> **⚠️ Caution: coverage**
>
> Only 8 of the 16 positions have characteristics — the smaller and stranger
> names (Wesco, GATX) aren't in the signal files. We renormalized the weights
> over what's left, which quietly turns this into a decomposition of the *large*
> holdings only."""))

# ─── trade-offs ───────────────────────────────────────────────────────
cells.append(md("""---

## 7. The Trade-Offs <a id="tradeoffs"></a>

Three routes, three answers. The market beta comes out at **0.68 top-down** and
**1.08 bottom-up**; the FF6 loadings barely agree at all.

None of them is "the right one." They answer slightly different questions from
different data, and they fail differently.

| | **A. Top-down** | **B. Bottom-up** | **C. Characteristic** |
|---|---|---|---|
| **You need** | the fund's returns | holdings + a beta per name | holdings + characteristics + premia |
| **Tells you about** | the past window, averaged | today's portfolio | today's portfolio |
| **Available for** | anything with a track record | only disclosed holdings | only disclosed holdings |
| **Main failure** | averages over a changing portfolio; unstable with many factors | you only see what's disclosed | ignores covariances; needs a premium estimate |
| **Estimation error in** | m loadings from T months | n×m betas | the premia |
| **Reacts to a trade** | eventually | immediately | immediately |

### Why A and B disagree here — three reasons, ranked

**1. Disclosure.** A 13F covers US-listed equities. Berkshire is an insurance
conglomerate: GEICO was bought outright in 1996, and there are the operating
businesses, the float and the leverage. The disclosed equity book is a *part* of
Berkshire, and it is the more volatile part — which is why bottom-up gets a
higher beta than the fund's own returns show.

**2. Estimation noise.** The top-down FF6 loadings have standard errors up to
1.01. Some of that "disagreement" is a regression that couldn't identify its own
coefficients.

**3. The two assumptions from Section 1.** The window is 1995–1999 and the
portfolio changed materially inside it. So does each firm's beta.

> **📌 Remember: use the one that matches the question**
>
> - *What was this manager doing over the last five years?* → **top-down**. It's
>   the only one that works when you can't see holdings.
> - *What am I exposed to right now, and what happens if I sell Coke?* →
>   **bottom-up**. This is what risk systems compute.
> - *Is this portfolio tilted toward things that have historically paid?* →
>   **characteristic**. No betas needed, adapts instantly.
>
> Professionals compute all three and treat disagreement as information about
> the portfolio, not as a problem with the arithmetic."""))

# ─── Challenge ────────────────────────────────────────────────────────
cells.append(md("""---

## 🎯 Challenge: The 1996 Book <a id="challenge"></a>

*Homework — due before Lecture 8.*

Section 1 showed the portfolio was a different thing in 1996: Coca-Cola at 56%,
and **Wells Fargo** in the book, which is gone by 1999.

Redo the bottom-up decomposition on the **1996-12-31** snapshot, estimating
betas over **1992-01-31 to 1996-12-31**, and compare.

### Q1 — Exposure and concentration

> **📌 Required variable names:**
> ```python
> bu_beta_96    = ____   # bottom-up CAPM beta, b = B'w, at 1996-12-31
> top3_share_96 = ____   # weight in the top 3 positions
> ```"""))

cells.append(code("""# Your work here


# Required outputs — fill these in:
bu_beta_96    = ____
top3_share_96 = ____

print(f"1996 bottom-up beta : {bu_beta_96:.2f}")
print(f"1996 top-3 weight   : {top3_share_96:.1%}")"""))

cells.append(md("""### Q2 — Risk split

Using the FF6 model on the same snapshot and window:

> **📌 Required variable names:**
> ```python
> factor_share_96 = ____   # factor variance / total variance
> top_name_spec_96 = ____  # largest single contribution to SPECIFIC variance
> ```"""))

cells.append(code("""# Your work here


# Required outputs — fill these in:
factor_share_96  = ____
top_name_spec_96 = ____

print(f"factor share of variance      : {factor_share_96:.0%}")
print(f"largest name's share of specific: {top_name_spec_96:.0%}")"""))

cells.append(md("""### Q3 — The memo

> **📝 Your task — maximum 6 sentences**
>
> Your risk committee asks: *"we already regress the fund's returns on factors —
> why should we pay for a holdings-based system?"*
>
> Use your 1996 and the lecture's 1999 numbers. Say what bottom-up gives you that
> top-down cannot, what it costs, and name one situation where top-down is the
> only option available. Be specific about the Berkshire example — including
> what a 13F does not show you."""))

cells.append(code('''MEMO = """
Write your memo here. Don't delete the surrounding triple quotes.
"""
print(MEMO)'''))

cells.append(md("---\n\n## 📤 Submission <a id=\"submit\"></a>"))

cells.append(code('''# === 📤 SUBMISSION CELL — Run this last ===
import json, base64, hashlib, datetime as dt

required = ["bu_beta_96", "top3_share_96", "factor_share_96",
            "top_name_spec_96", "MEMO"]
missing = [v for v in required if v not in dir()]
if missing:
    raise NameError(f"\\n❌ Missing before submission: {missing}")

payload = {
    "assignment": "L7_Decomposition_AI",
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

1. **`b = B′w`** — a portfolio's factor exposure is the weighted average of its
   holdings' loadings. That one expression is the whole multi-asset toolkit.

2. **`Ω = BΩ_f B′ + Ω_ε`** — portfolio variance splits into factor risk and
   specific risk, cleanly, because ε is uncorrelated with f.

3. **A time-series regression measures an average over a changing portfolio.**
   It's only current exposure if positions *and* betas were stable. For
   Berkshire, neither was.

4. **Print standard errors on loadings.** Six factors on 41 months gave HML
   +2.08 (se 0.61) and CMA −2.20 (se 1.01) — precision about nothing.

5. **73% of Berkshire's disclosed-book variance was factor risk**, even for the
   most famous stock-picker alive.

6. **Specific risk only diversifies if weights are spread.** Coca-Cola at 41% of
   the book supplied 67% of specific variance; the top three supplied 99%.

7. **Characteristics describe what you own, not what you paid.** In 1999 the
   great value investor's book scored as giant and expensive — because he bought
   cheap in 1988 and held.

8. **You can only decompose what is disclosed.** A 13F is US-listed equity,
   quarterly, and incomplete. GEICO and the float never appear.

9. **Three routes, three questions.** Past behaviour → top-down. Current
   exposure → bottom-up. Style tilt without betas → characteristics. Disagreement
   between them is information.

---

### Next class

We have now decomposed a portfolio every way we know how, always **in sample**.
Next: what happens when you take the same freedom to a strategy you're about to
trade — and how you would ever know whether the result is real."""))

cells.append(md("---\n\n## 📎 Appendix <a id=\"appendix\"></a>"))

cells.append(code(f'''# ═══════════════════════════════════════════════════════════════════════
# 📎 APPENDIX — where the holdings come from
# ═══════════════════════════════════════════════════════════════════════
# Berkshire's 13F filings, from WRDS:
#     tr_13f.s34type3, mgrno = 8350  (BERKSHIRE HATHAWAY INC)
# joined to CRSP via ncusip for permno, and priced with crsp.msf.
# Built once by chapters/Finance/build_brk_holdings.py and cached at
#     {BASE}/brk_13f_holdings.csv
#
# Thomson has 13F coverage from 1980-03-31 -- the first quarter the filing was
# required -- and Berkshire appears in every quarter since.
#
# TWO CONVENTIONS THAT BITE:
#  1. Thomson reports shares in ACTUAL units, not thousands. Check any total
#     against a known figure before you trust it; Berkshire's disclosed book at
#     end-1999 should come to roughly $28B, not $28 trillion.
#  2. CRSP prc is NEGATIVE when the close is a bid/ask midpoint, so take abs()
#     before computing position values.
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
