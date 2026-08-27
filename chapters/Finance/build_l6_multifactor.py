"""
Build L6_MultiFactor_AI.ipynb — Lecture 6, Wed Sep 23 2026.

"Factor Models III — Multi-Factor Estimation"  (Columbia 3B)

Sources:
    FactorModels_II_AI.ipynb   (estimation)
    MultiFactorModels_c.ipynb  (FF3/FF5/FF6, time-series vs cross-sectional)
    NEW: Fama-MacBeth  (flagged in the audit as genuinely absent)

The spine is one table — the same four long-shorts run up the factor ladder.
Four completely different stories, all verified:

  BM      CAPM +7.15% (t=2.45) -> FF3 -1.16% (t=-0.70)   alpha DIES
          HML loading 1.21, R2 0.06 -> 0.71. Value IS the factor.
  GP      CAPM +6.30% -> FF3 +9.31% (t=3.95) -> FF5 +5.87%   alpha GROWS then shrinks
          Profitable firms are expensive, so controlling for value HELPS it.
  Mom12m  CAPM +18.2% -> FF5 +22.4% -> FF6 +3.46% (t=1.75)   survives 5, dies at 6
          UMD loading 1.46, R2 0.12 -> 0.84.
  NOA     t = 4.15 -> 2.48 -> 3.10 -> 2.72                    survives everything

Lesson: alpha is not a property of a strategy. It is a property of a strategy
RELATIVE TO A MODEL. That extends L4's benchmark-choice point from the
information ratio into the regression setting.

Fama-MacBeth, verified (251 monthly cross-sections, ~3,878 stocks each,
characteristics winsorized and z-scored so slopes are comparable):
    intercept  14.96%/yr  t= 3.56
    logME      -3.16%/yr  t=-1.81
    BM         +5.55%/yr  t= 4.99
    GP         +2.77%/yr  t= 3.79
    Mom12m     +5.56%/yr  t= 3.68

CHALLENGE (auto-graded): run momentum up the ladder.
"""

import json
from pathlib import Path

OUT = Path(__file__).parent / "L6_MultiFactor_AI.ipynb"
BASE = "https://raw.githubusercontent.com/amoreira2/UG54/refs/heads/main/assets/data"


def md(t): return {"cell_type": "markdown", "metadata": {}, "source": t.splitlines(keepends=True)}
def code(t): return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": t.splitlines(keepends=True)}


cells = []

cells.append(md("""# Multi-Factor Models
## Lecture 6

## 🎯 Learning Objectives

By the end of today you will be able to:

1. **Run and read a multi-factor regression** — CAPM, FF3, FF5, FF6
2. **Explain why alpha changes when you add a factor**, in both directions
3. **Argue that alpha is a property of a model, not of a strategy**
4. **Distinguish the time-series and cross-sectional approaches** to estimating
   the same thing
5. **Run a Fama-MacBeth regression** and interpret its slopes as portfolio returns"""))

cells.append(md("""## 📋 Today's Plan

1. [From one factor to many](#many)
2. [Pitfall checklist](#pitfalls)
3. [🔄 Live Demo: the alpha ladder](#demo)
4. [Alpha is relative to a model](#relative)
5. [Two ways to estimate the same thing](#twoways)
6. [Fama-MacBeth](#fm)
7. [🛠️ Hands-On: run your signal up the ladder](#ho1)
8. [🎯 Challenge: momentum](#challenge) — *homework*
9. [Key takeaways](#takeaways)"""))

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

f5  = web.DataReader('F-F_Research_Data_5_Factors_2x3','famafrench',start='1980-01-01')[0]/100
umd = web.DataReader('F-F_Momentum_Factor','famafrench',start='1980-01-01')[0]/100
for x in (f5, umd):
    x.index = pd.to_datetime(x.index.to_timestamp()) + pd.offsets.MonthEnd(0)
umd.columns = ['UMD']
FF = f5.join(umd, how='inner').loc['1980-01-31':'2000-12-31']

print(f"{{len(FF)}} months, factors: {{[c for c in FF.columns if c != 'RF']}}")"""))

# ─── 1. many factors ──────────────────────────────────────────────────
cells.append(md(r"""---

## 1. From One Factor to Many <a id="many"></a>

In Lecture 4 you regressed on the market alone:

$$r^e_t = \alpha + \beta \, r^e_{m,t} + \varepsilon_t$$

That model says the only thing you can buy cheaply is market exposure. Lecture 5
said otherwise: there are whole families of characteristics that have paid, and
you can buy any of them in an ETF for a few basis points.

So the honest model has more terms:

$$r^e_t = \alpha + \sum_{k} \beta_k f_{k,t} + \varepsilon_t$$

### The standard ladder

| Model | Factors | Source |
|---|---|---|
| **CAPM** | Mkt-RF | Sharpe (1964) |
| **FF3** | + SMB (size), HML (value) | Fama-French (1993) |
| **FF5** | + RMW (profitability), CMA (investment) | Fama-French (2015) |
| **FF6** | + UMD (momentum) | Carhart (1997) |

Each factor is a **long-short portfolio** — exactly the thing you built in
Lecture 3. HML is long high book-to-market, short low. That is why the ladder
matters: every factor added is a bet somebody is already selling cheaply, and
your α has to be something *else*.

> **📌 Remember what α means now**
>
> α is the average return your strategy earned that **none of the factors in the
> model** can explain. Change the model, change the α. It is not a fixed
> property of your strategy."""))

# ─── pitfalls ─────────────────────────────────────────────────────────
cells.append(md("""---

## 🛡️ Pitfall Checklist for Multi-Factor Regressions <a id="pitfalls"></a>

| | Pitfall | What goes wrong | 🔍 How to detect |
|---|---|---|---|
| 1 | **Reporting α without saying which model** | "Our alpha is 6%" is meaningless alone | Always write "α relative to FF3" |
| 2 | **Adding factors until α disappears** | You can kill any α with enough factors — that's not a finding | Did you pick the model *before* looking? |
| 3 | **Correlated factors** | HML and CMA overlap; loadings get unstable and hard to read | Check the factor correlation matrix |
| 4 | **Comparing α across different samples** | FF5 starts later than FF3 in some datasets | Are all models fitted on identical months? |
| 5 | **Reading a loading as a claim about holdings** | β on HML = 1.2 doesn't mean you hold HML | It means your returns *co-move* with it |
| 6 | **Ignoring the t-stat on α while celebrating its size** | Big α on 60 months is noise | |t| > 2, and how many months? |

> **🤖 AI-Era Insight**
>
> Pitfall 2 is the subtle one. Ask an AI to "test whether this strategy has
> alpha" and it will pick a model for you — usually FF3 — without telling you
> that the choice determines the answer. You'll see today that the same strategy
> has α of +18% or +3% depending only on which model you asked for."""))

# ─── Live demo ────────────────────────────────────────────────────────
cells.append(md("""---

## 🔄 Live Demo: The Alpha Ladder <a id="demo"></a>

Take the value long-short from Lecture 3 and run it up the ladder.

> **📝 Spec**
>
> Build the BM long-short (NYSE breakpoints, value-weighted, D10−D1, `ret_fwd`,
> shifted to the month earned). Regress it on CAPM, then FF3, then FF5, then
> FF6, all on the same months, each with an intercept. Report annualized α, its
> t-stat, R², and the loadings.

> **🤔 Predict.** As you add factors, does α go up, down, or stay put?"""))

cells.append(code("""def long_short(sig):
    s = pd.read_parquet(f"{BASE}/signals/{sig}.parquet")
    d = panel.merge(s, on=['permno','date'], how='inner').dropna(subset=[sig,'ret_fwd','me'])
    q = (d[d.exchcd == 1].groupby('date')[sig].quantile([.1,.9]).unstack()
           .rename(columns={0.1:'lo', 0.9:'hi'}))
    d = d.merge(q, on='date')
    d['g'] = np.where(d[sig] <= d.lo, 0, np.where(d[sig] >= d.hi, 9, np.nan))
    d = d.dropna(subset=['g'])
    p = d.groupby(['date','g']).apply(lambda g: np.average(g['ret_fwd'], weights=g['me'])).unstack()
    r = (p[9] - p[0]).dropna()
    r.index = r.index + pd.offsets.MonthEnd(1)
    return r

MODELS = {'CAPM': ['Mkt-RF'],
          'FF3' : ['Mkt-RF','SMB','HML'],
          'FF5' : ['Mkt-RF','SMB','HML','RMW','CMA'],
          'FF6' : ['Mkt-RF','SMB','HML','RMW','CMA','UMD']}

def ladder(sig, show=True):
    r = long_short(sig)
    j = pd.concat([r.rename('y'), FF], axis=1).dropna()
    out = {}
    if show:
        print(f"{sig} long-short — raw return {j.y.mean()*12:+.2%}/yr, "
              f"{len(j)} months\\n")
        print(f"{'model':7s}{'alpha/yr':>11s}{'t':>7s}{'R²':>7s}   loadings")
        print("-"*72)
    for name, cols in MODELS.items():
        m = sm.OLS(j.y, sm.add_constant(j[cols])).fit()
        out[name] = m
        if show:
            ld = "  ".join(f"{c}={m.params[c]:+.2f}" for c in cols)
            print(f"{name:7s}{m.params['const']*12:>10.2%}{m.tvalues['const']:>7.2f}"
                  f"{m.rsquared:>7.2f}   {ld}")
    return out

_ = ladder('BM')"""))

cells.append(md("""### The alpha didn't shrink. It vanished.

CAPM says value earned **+7.15%/yr with t = 2.45** — a real anomaly. FF3 says
**−1.16%, t = −0.70** — nothing at all.

Look at the loading that did it: **HML = 1.21**, and R² jumps from 0.06 to 0.71.

That is not surprising once you see it. HML *is* a value long-short — Fama and
French built it by sorting on book-to-market, which is exactly what we did. We
have rediscovered HML and then asked whether it beats HML.

> **💡 Key Insight**
>
> The regression is not saying value doesn't work. It is saying value doesn't
> work **beyond what you could already buy in a value ETF**. Those are different
> claims, and only the second one justifies a fee."""))

# ─── relative ─────────────────────────────────────────────────────────
cells.append(md("""---

## 2. Alpha Is Relative to a Model <a id="relative"></a>

If adding factors always killed alpha, this would be a simple story. It doesn't.
Here are three more signals up the same ladder."""))

cells.append(code("""for s in ['GP', 'Mom12m', 'NOA']:
    _ = ladder(s); print()"""))

cells.append(md("""### Four signals, four completely different stories

| | CAPM → FF6 | What happened |
|---|---|---|
| **BM** | +7.2% → −0.7% | **Dies.** HML loading 1.21 — it *is* the factor |
| **GP** | +6.3% → **+9.3%** at FF3 → +5.9% at FF5 | **Grows, then shrinks** |
| **Mom12m** | +18.2% → +22.4% at FF5 → **+3.5%** at FF6 | **Survives five factors, dies at the sixth** |
| **NOA** | +11.8% → +6.8%, t stays above 2.4 throughout | **Survives everything** |

**Why GP's alpha grows.** Profitable firms tend to be *expensive* — GP loads
**−0.43** on HML. So under FF3 the model expects GP to lose money on its value
exposure. It didn't, so the unexplained part gets *bigger*. Controlling for a
factor you're negatively exposed to makes you look better, not worse.

**Why momentum dies only at FF6.** UMD loading is **1.46** and R² jumps from
0.12 to 0.84. UMD is a momentum long-short. Same story as BM and HML, one rung
later on the ladder.

> **💡 Key Insight: "does this strategy have alpha?" is not a well-posed question**
>
> Momentum has an α of +18% or +3% depending only on whether the person asking
> includes UMD. Neither number is wrong. **α is a property of the pair
> (strategy, model)** — you cannot report one without the other.
>
> This is the same lesson as the information ratio in Lecture 4, in regression
> form. There the benchmark was a choice; here the model is a choice. Both
> determine the answer.

> **⚠️ Caution: which model should *you* use?**
>
> The defensible rule is to fix the model **before** you look, and to justify it
> by what an investor could actually buy cheaply. If a low-cost momentum ETF
> exists, UMD belongs in your model, and momentum's α is 3.5% not 18%.
>
> The indefensible version is running all four and reporting whichever is
> biggest. That is pitfall 2, and it is depressingly common."""))

# ─── two ways ─────────────────────────────────────────────────────────
cells.append(md(r"""---

## 3. Two Ways to Estimate the Same Thing <a id="twoways"></a>

Everything so far ran **one regression per strategy, through time**:

$$r_{p,t} = \alpha + \beta' f_t + \varepsilon_t \qquad t = 1 \dots T$$

That is the **time-series** approach. It needs the factor returns $f_t$ to
already exist — someone had to build HML before you could regress on it.

There is a second way. Run **one regression per month, across stocks**:

$$r_{i,t+1} = \gamma_{0,t} + \gamma_t' x_{i,t} + e_{i,t+1} \qquad i = 1 \dots N$$

Here $x_{i,t}$ is stock *i*'s characteristic — its book-to-market, its size —
and the *slope* $\gamma_t$ is estimated fresh every month.

| | Time-series | Cross-sectional |
|---|---|---|
| One regression per | strategy | month |
| You must supply | factor **returns** | firm **characteristics** |
| You estimate | betas, α | the factor return itself |
| Runs on | ~250 months | ~250 × 4,000 firm-months |

> **💡 Key Insight: the slope IS a portfolio return**
>
> $\gamma_t$ is the return, in month *t*, of a portfolio with one unit of
> exposure to that characteristic and zero exposure to the others. It is a
> **pure play** — the closest thing to "what did value pay this month, holding
> size and profitability fixed."
>
> A decile sort can't do that. Sorting on book-to-market also sorts, partly, on
> size. A cross-sectional regression controls for the others by construction.

This is **Fama-MacBeth** (1973), and it is one of the most-used procedures in
empirical finance."""))

# ─── Fama-MacBeth ─────────────────────────────────────────────────────
cells.append(md("""---

## 4. Fama-MacBeth <a id="fm"></a>

The procedure is two steps and no more:

1. **Every month**, regress next month's returns across stocks on this month's
   characteristics. Keep the slopes.
2. **Average the slopes over time.** The t-statistic comes from the *time series*
   of monthly slopes — not from any single regression.

Step 2 is the clever part. Each monthly regression has thousands of observations
and would report absurdly tight standard errors, but those observations are
correlated within the month. Using the variation of the slope **across months**
sidesteps that entirely."""))

cells.append(code("""d = panel.dropna(subset=['ret_fwd','me']).copy()
for s in ['BM','GP','Mom12m']:
    d = d.merge(pd.read_parquet(f"{BASE}/signals/{s}.parquet"), on=['permno','date'], how='left')
d['logME'] = np.log(d['me'])

CH = ['logME','BM','GP','Mom12m']
d  = d.dropna(subset=CH + ['ret_fwd'])

# winsorize + z-score each month so the slopes are comparable across characteristics
for c in CH:
    d[c+'_z'] = d.groupby('date')[c].transform(
        lambda v: (v.clip(v.quantile(.01), v.quantile(.99)) - v.mean()) / v.std())
Z = [c+'_z' for c in CH]

# STEP 1 — one cross-sectional regression per month
slopes = []
for _, g in d.groupby('date'):
    if len(g) < 100: continue
    slopes.append(sm.OLS(g['ret_fwd'], sm.add_constant(g[Z])).fit().params)
G = pd.DataFrame(slopes)

print(f"Step 1: {len(G)} monthly cross-sectional regressions, "
      f"~{len(d)/d.date.nunique():.0f} stocks each\\n")

# STEP 2 — average the slopes; t-stat from their time-series variation
print(f"{'characteristic':16s}{'slope/month':>13s}{'annualized':>12s}{'t-stat':>9s}")
print("-"*50)
for c in ['const'] + Z:
    v = G[c]
    print(f"{('intercept' if c=='const' else c[:-2]):16s}"
          f"{v.mean():>13.5f}{v.mean()*12:>11.2%}{v.mean()/v.std()*np.sqrt(len(v)):>9.2f}")"""))

cells.append(code("""fig, ax = plt.subplots(figsize=(11, 4))
ax.plot(G.index if not isinstance(G.index, pd.RangeIndex) else range(len(G)),
        G['BM_z'].values, linewidth=0.9, label='BM slope')
ax.axhline(G['BM_z'].mean(), color='crimson', ls='--',
           label=f"mean {G['BM_z'].mean()*12:+.1%}/yr")
ax.axhline(0, color='black', lw=0.8)
ax.set_ylabel('monthly slope'); ax.set_title(
    'The value slope, month by month — the t-stat comes from THIS variation',
    fontweight='bold')
ax.legend(); plt.tight_layout(); plt.show()

print(f"months the value slope was positive: {(G['BM_z']>0).mean():.0%}")"""))

cells.append(md("""### Reading the output

Each row is the return to a portfolio that is **+1 standard deviation** of that
characteristic and **flat on the other three**.

- **BM: +5.55%/yr, t = 4.99.** Value pays, controlling for size, profitability
  and momentum.
- **Mom12m: +5.56%/yr, t = 3.68.** So does momentum.
- **GP: +2.77%/yr, t = 3.79.** Smaller, but very reliable.
- **logME: −3.16%/yr, t = −1.81.** Bigger firms earn less — the size effect,
  and it doesn't clear |t| > 2 in this sample. Consistent with Lecture 3.

> **📌 Remember: the intercept is not alpha**
>
> The 14.96% intercept is the return of a stock with *average* values of every
> characteristic. It is roughly the market return, not a mispricing.

> **📎 What you do with it next**
>
> The time-series model gave you a *hedge*: hold the asset, short β units of the
> factor, and the systematic part cancels (Lecture 4). The cross-sectional model
> has an exact counterpart — compute the return your portfolio's
> **characteristics** imply, and subtract it. That's a **characteristic-adjusted
> return**, and it's hedging without ever estimating a time-series beta.
>
> It needs the multi-asset machinery, so it's Lecture 7.

> **🤔 Compare with the sort**
>
> In Lecture 3, the BM decile sort gave +5.27%/yr. Fama-MacBeth gives +5.55%/yr
> — close, but not identical, and the FM version *holds size, profitability and
> momentum fixed* while the sort does not. When they disagree sharply, it means
> your sort was picking up something other than the characteristic you sorted
> on."""))

# ─── Hands-On ─────────────────────────────────────────────────────────
cells.append(md("""---

## 🛠️ Hands-On: Run Your Signal Up the Ladder <a id="ho1"></a>

You have followed one signal since Lecture 3. Time to find out what it really
has.

> **🤔 Predict.** Given what you learned in Lecture 5 about your signal's
> nearest neighbours — does it load on one of the FF factors? Which one?"""))

cells.append(code("""# === EDIT + YOUR TURN ===
MY_SIGNAL = "GP"       # ← your pick

res = ____             # hint: ladder(MY_SIGNAL)   — it prints the table for you

a_capm = res['CAPM'].params['const']*12
a_ff6  = res['FF6'].params['const']*12
print(f"\\n{MY_SIGNAL}: alpha falls from {a_capm:+.2%} (CAPM) to {a_ff6:+.2%} (FF6)")
print(f"  that is {1 - a_ff6/a_capm:.0%} of the CAPM alpha explained by the other five factors")
print(f"  biggest loading in FF6: "
      f"{res['FF6'].params.drop('const').abs().idxmax()}")"""))

cells.append(md("""### What to say out loud

- **Which factor took the biggest bite?** If it's HML your signal is a value
  play; if UMD, a momentum play; if RMW, profitability.
- **Did your α survive FF6 with |t| > 2?** If yes, you have something the
  standard model can't explain — which is genuinely interesting and also the
  moment to get suspicious. Lectures 7 and 8.
- **Did your α get bigger?** Then you're negatively exposed to a factor that
  paid, and the raw return understated you."""))

# ─── Challenge ────────────────────────────────────────────────────────
cells.append(md("""---

## 🎯 Challenge: Momentum <a id="challenge"></a>

*Homework — due before Lecture 7.*

Momentum is the most profitable signal in our whole menu — **+19.9%/yr** raw.
Your PM wants to know whether to pay for a momentum manager.

Run `Mom12m` up the full ladder and report.

### Q1 — The alpha ladder

> **📌 Required variable names:**
> ```python
> mom_alpha_capm = ____   # annualized alpha vs CAPM
> mom_alpha_ff3  = ____
> mom_alpha_ff5  = ____
> mom_alpha_ff6  = ____
> ```"""))

cells.append(code("""# Your work here


# Required outputs — fill these in:
mom_alpha_capm = ____
mom_alpha_ff3  = ____
mom_alpha_ff5  = ____
mom_alpha_ff6  = ____

for n, a in [('CAPM',mom_alpha_capm),('FF3',mom_alpha_ff3),
             ('FF5',mom_alpha_ff5),('FF6',mom_alpha_ff6)]:
    print(f"  {n:5s} alpha {a:+7.2%}/yr")"""))

cells.append(md("""### Q2 — What did it

Report momentum's UMD loading and R² under FF6.

> **📌 Required variable names:**
> ```python
> mom_umd_beta = ____   # loading on UMD in the FF6 regression
> mom_r2_ff6   = ____   # R-squared of the FF6 regression
> ```"""))

cells.append(code("""# Your work here


# Required outputs — fill these in:
mom_umd_beta = ____
mom_r2_ff6   = ____

print(f"UMD loading {mom_umd_beta:+.2f}   R² {mom_r2_ff6:.2f}")"""))

cells.append(md("""### Q3 — The memo

> **📝 Your task — maximum 6 sentences**
>
> Should your PM pay for a momentum manager?
>
> The α is +18% against CAPM and +3.5% against FF6. Say which number you'd put
> in front of the investment committee and defend it. Explain what the UMD
> loading of 1.46 means in plain language. And say what would have to be true
> about the market for the CAPM number to be the right one."""))

cells.append(code('''MEMO = """
Write your memo here. Don't delete the surrounding triple quotes.
"""
print(MEMO)'''))

cells.append(md("---\n\n## 📤 Submission <a id=\"submit\"></a>"))

cells.append(code('''# === 📤 SUBMISSION CELL — Run this last ===
import json, base64, hashlib, datetime as dt

required = ["mom_alpha_capm", "mom_alpha_ff3", "mom_alpha_ff5",
            "mom_alpha_ff6", "mom_umd_beta", "mom_r2_ff6", "MEMO"]
missing = [v for v in required if v not in dir()]
if missing:
    raise NameError(f"\\n❌ Missing before submission: {missing}")

payload = {
    "assignment": "L6_MultiFactor_AI",
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

1. **Every factor in the model is a long-short portfolio** — the thing you built
   in Lecture 3. Adding one asks "can you beat *that* too?"

2. **α is a property of (strategy, model), not of a strategy.** Momentum's α is
   +18% or +3.5% depending only on whether UMD is in the model.

3. **Never report an alpha without naming the model.**

4. **Alpha can grow when you add a factor.** GP's α rises under FF3 because it
   loads *negatively* on HML.

5. **Fix the model before you look.** Justify it by what an investor could
   actually buy cheaply. Running all four and reporting the best is not analysis.

6. **Two estimation routes to the same object.** Time-series needs factor
   returns and gives you betas; cross-sectional needs characteristics and gives
   you the factor return.

7. **A Fama-MacBeth slope is a portfolio return** — a pure play on one
   characteristic, holding the others fixed. That's something a sort cannot do.

8. **The FM t-stat comes from variation across months**, not from the thousands
   of stocks inside any single month.

---

### Next class

Everything so far has been in-sample. We have run the same data through four
models and picked the interesting results. Next: what that does to a t-statistic,
and how you would ever know whether any of it is real."""))

cells.append(md("---\n\n## 📎 Appendix <a id=\"appendix\"></a>"))

cells.append(code(f'''# ═══════════════════════════════════════════════════════════════════════
# 📎 APPENDIX — Belt-and-Suspenders Data Loading
# ═══════════════════════════════════════════════════════════════════════
#   panel = pd.read_parquet(f"{{BASE}}/panel_backbone_1980_2000.parquet")
#
# Factors come live from Ken French. Prompt:
# "Using pandas-datareader fetch F-F_Research_Data_5_Factors_2x3 and
#  F-F_Momentum_Factor, monthly, from 1980. Convert PeriodIndex to month-end,
#  divide by 100, and join them."
def fetch_ff6():
    import pandas_datareader.data as web
    f5  = web.DataReader('F-F_Research_Data_5_Factors_2x3','famafrench',start='1980-01-01')[0]/100
    umd = web.DataReader('F-F_Momentum_Factor','famafrench',start='1980-01-01')[0]/100
    for x in (f5, umd):
        x.index = pd.to_datetime(x.index.to_timestamp()) + pd.offsets.MonthEnd(0)
    umd.columns = ['UMD']
    return f5.join(umd, how='inner')

# Note: Ken French labels the momentum factor 'Mom   ' with trailing spaces in
# some releases. We rename to 'UMD' on load rather than trusting the label.
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
