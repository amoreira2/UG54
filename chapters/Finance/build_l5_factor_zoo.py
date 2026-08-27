"""
Build L5_Factor_Zoo_AI.ipynb — Lecture 5, Mon Sep 21 2026.

"Factor Models II — Where Factors Come From, and the Zoo"  (Columbia 3A)

Sources:
    Factors.ipynb                 (the taxonomy: value, momentum, quality, defensive)
    StatisticalFactors_AI.ipynb   (the three-kinds-of-factor-model framing)
    the 30-signal menu             (the empirical zoo)

The spine, computed from our own 29 long-shorts over 1980-2000:

    mean pairwise correlation  +0.05      <- the zoo looks huge and independent
    |corr| > 0.5 in only        8.6% of pairs
    BUT: mean |corr| WITHIN economic category  0.579
         mean |corr| ACROSS economic category  0.189      <- 3x difference

    IdioVol3F / MaxRet / RealizedVol   0.94 - 0.97   (one factor, three papers)
    Illiquidity / Size                 0.92

So: 300+ published predictors, far fewer distinct bets. That single fact sets up
multiple testing (L7-L8), statistical factors (L17), and crowding (L25), and it
gives students a principled reason to care about the taxonomy rather than
memorizing a list.
"""

import json
from pathlib import Path

OUT = Path(__file__).parent / "L5_Factor_Zoo_AI.ipynb"
BASE = "https://raw.githubusercontent.com/amoreira2/UG54/refs/heads/main/assets/data"


def md(t): return {"cell_type": "markdown", "metadata": {}, "source": t.splitlines(keepends=True)}
def code(t): return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": t.splitlines(keepends=True)}


cells = []

cells.append(md("""# Where Factors Come From, and the Factor Zoo
## Lecture 5

## 🎯 Learning Objectives

By the end of today you will be able to:

1. **Distinguish the three kinds of factor model** — and say what you have to
   specify in each
2. **Name the major factor families** and the economic story behind each
3. **Measure how much two signals overlap** rather than guessing from their names
4. **Show that the factor zoo is far smaller than its headcount suggests**
5. **Explain why that matters** for anyone testing a new signal"""))

cells.append(md("""## 📋 Today's Plan

1. [Three kinds of factor model](#three)
2. [The zoo: what people actually trade](#zoo)
3. [Pitfall checklist](#pitfalls)
4. [🔄 Live Demo: how much do these overlap?](#demo)
5. [The zoo is smaller than it looks](#smaller)
6. [🛠️ Hands-On: find your signal's twin](#ho1)
7. [🎯 Challenge: how many bets are there really?](#challenge) — *homework*
8. [Key takeaways](#takeaways)"""))

cells.append(md("---\n\n## 🛠️ Setup"))

cells.append(code(f"""#@title Setup — run this first
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import glob, os
%matplotlib inline
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = [11, 4.5]
import warnings; warnings.filterwarnings('ignore')

BASE  = "{BASE}"
panel = pd.read_parquet(f"{{BASE}}/panel_backbone_1980_2000.parquet")
menu  = pd.read_csv(f"{{BASE}}/signal_menu.csv")

print(f"{{len(menu)}} signals across {{menu['Cat.Economic'].nunique()}} economic categories")
menu.groupby('Cat.Economic').size().sort_values(ascending=False).to_string()"""))

# ─── 1. three kinds ───────────────────────────────────────────────────
cells.append(md(r"""---

## 1. Three Kinds of Factor Model <a id="three"></a>

Last class we regressed GE on the market. Where did "the market" come from? We
chose it. That choice is the model.

There are exactly three ways to build a factor model, and they differ in **what
you have to specify**:

| Type | You **specify** | You **estimate** | How | Example |
|---|---|---|---|---|
| **Time-series** | the factor *returns* | the betas | time-series regression | Fama-French — HML is a portfolio return you can look up |
| **Characteristic** (fundamental) | the *betas* | the factor returns | cross-sectional regression, each period | BARRA — book-to-market **is** the loading |
| **Statistical** | **nothing** | both | eigendecomposition of Σ | PCA |

> **💡 Key Insight: the same duality you already met**
>
> In Lecture 3 you sorted stocks on a characteristic to *make* a portfolio. In
> Lecture 4 you regressed a return on a portfolio to *get* a beta. Those are the
> two directions:
>
> - Make a portfolio from a characteristic → you now have a **factor return** →
>   time-series model
> - Take the characteristic as the exposure directly → estimate what that
>   exposure paid each month → **characteristic model**
>
> Same raw material, opposite plumbing.

Today is about the first two, and specifically about **which** characteristics
are worth turning into factors. The statistical route gets its own lecture (L17)
because it answers a different question: what if the ones we chose are wrong?"""))

# ─── 2. the zoo ───────────────────────────────────────────────────────
cells.append(md("""---

## 2. The Zoo: What People Actually Trade <a id="zoo"></a>

Over fifty years the literature has published **300+** characteristics that
predict the cross-section of returns. They are not 300 different ideas. They
cluster into a handful of families, each with an economic story.

| Family | The claim | Canonical signal | Why it might work |
|---|---|---|---|
| **Value** | Cheap firms outperform | Book-to-market (Stattman 1980) | Risk of distress, or over-extrapolation of bad news |
| **Momentum** | Recent winners keep winning | 12-month return, skip a month (Jegadeesh-Titman 1993) | Under-reaction to news, then over-shoot |
| **Profitability** | Profitable firms outperform | Gross profits / assets (Novy-Marx 2013) | Quality is under-priced relative to growth |
| **Investment** | Firms that grow assets fast underperform | Asset growth (Cooper et al. 2008) | Empire-building; over-investment at the peak |
| **Low risk** | Low-volatility, low-beta stocks outperform | Idiosyncratic vol (Ang et al. 2006) | Leverage-constrained investors bid up high-beta names |
| **Issuance** | Firms issuing equity underperform | Share issuance (Pontiff-Woodgate 2008) | Managers issue when the stock is expensive |
| **Liquidity** | Illiquid stocks earn a premium | Amihud (2002) | Compensation for not being able to get out |

> **📌 Every one of these is in your signal menu**, with the original paper and
> the t-statistic its authors reported.

### Two stories, and they are not the same

Every family above has *two* competing explanations, and which one you believe
changes what you expect next.

**Risk.** The premium is compensation for bearing something genuinely
unpleasant. If so it should persist — nobody is going to arbitrage away payment
for real risk.

**Mispricing.** Investors are making a systematic error. If so, the premium
should **shrink once the paper is published** and people trade against it.

> **🤔 Hold this question.** You saw in Lecture 3 that the size premium went
> negative over 1980–2000, right after Banz published it in 1981. Which story
> does that support? We test this properly in Lecture 8."""))

# ─── pitfalls ─────────────────────────────────────────────────────────
cells.append(md("""---

## 🛡️ Pitfall Checklist for Comparing Factors <a id="pitfalls"></a>

| | Pitfall | What goes wrong | 🔍 How to detect |
|---|---|---|---|
| 1 | **Assuming different names mean different bets** | You "diversify" across five signals that are one signal | Correlate the long-short returns, not the characteristics |
| 2 | **Correlating the signals instead of the strategies** | Raw characteristics can look unrelated while their portfolios move together | Always correlate the *return series* |
| 3 | **Comparing over different samples** | Two signals with different data coverage aren't comparable | Align on common months before correlating |
| 4 | **Reading a category label as an economic claim** | "Liquidity" and "size" are different words for overlapping things | Check the number, not the taxonomy |
| 5 | **Counting signals as evidence** | 300 papers finding predictability is not 300 independent confirmations | How many *distinct* bets are there? — today |

> **🤖 AI-Era Insight**
>
> Ask an AI to "build a diversified multi-factor strategy" and it will happily
> combine value, size, low-volatility and liquidity — three of which, as you're
> about to see, are close to the same trade in this sample. It has the names,
> not the correlation matrix."""))

# ─── Live demo ────────────────────────────────────────────────────────
cells.append(md("""---

## 🔄 Live Demo: How Much Do These Overlap? <a id="demo"></a>

We have 30 signals. Let's build every one of them as a long-short and look at
what they actually do.

> **📝 Spec**
>
> For each signal file, form the standard long-short — NYSE breakpoints, value
> weighted, top decile minus bottom decile, using `ret_fwd` — align all of them
> on common months, and compute the pairwise correlation matrix of the *return
> series*.

> **🤔 Predict.** 30 strategies from 30 different published papers. What do you
> expect the average pairwise correlation to be?"""))

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

SIGS = sorted(os.path.basename(f)[:-8] for f in glob.glob(f"{BASE}/signals/*.parquet"))
R = {}
for s in SIGS:
    try:
        r = long_short(s)
        if len(r) > 200: R[s] = r
    except Exception:
        pass
L = pd.DataFrame(R).dropna(how='all')
print(f"{L.shape[1]} long-short strategies over {len(L)} common months")"""))

cells.append(code("""C  = L.corr()
iu = np.triu_indices_from(C, 1)
v  = C.values[iu]

print(f"pairwise correlations across {L.shape[1]} strategies\\n")
print(f"  mean      {v.mean():+.3f}")
print(f"  median    {np.median(v):+.3f}")
print(f"  |corr|>0.5 in {(np.abs(v)>0.5).mean():.1%} of pairs\\n")

names = C.columns
pairs = sorted((C.values[i,j], names[i], names[j]) for i,j in zip(*iu))
print("Most POSITIVELY correlated pairs:")
for c,a,b in pairs[-5:][::-1]: print(f"  {a:22s} {b:22s} {c:+.2f}")
print("\\nMost NEGATIVELY correlated pairs:")
for c,a,b in pairs[:3]:        print(f"  {a:22s} {b:22s} {c:+.2f}")"""))

cells.append(code("""order = (menu.set_index('Acronym').loc[[c for c in C.columns], 'Cat.Economic']
           .sort_values().index.tolist())
fig, ax = plt.subplots(figsize=(9.5, 8))
im = ax.imshow(C.loc[order, order], cmap='RdBu_r', vmin=-1, vmax=1)
ax.set_xticks(range(len(order))); ax.set_xticklabels(order, rotation=90, fontsize=7)
ax.set_yticks(range(len(order))); ax.set_yticklabels(order, fontsize=7)
ax.set_title('Correlation of 29 long-short strategies, sorted by economic category',
             fontweight='bold')
plt.colorbar(im, fraction=0.046); plt.tight_layout(); plt.show()"""))

cells.append(md("""### Read the average first, then the picture

The **average pairwise correlation is about +0.05** — essentially zero. Taken at
face value that says the zoo is wonderfully diversified: thirty nearly
independent sources of return.

That is the wrong conclusion, and the heatmap shows why. Look at the blocks on
the diagonal."""))

# ─── smaller than it looks ────────────────────────────────────────────
cells.append(md("""---

## 3. The Zoo Is Smaller Than It Looks <a id="smaller"></a>

The average hides the structure. Split the pairs by whether the two signals come
from the **same economic category**."""))

cells.append(code("""cat = menu.set_index('Acronym')['Cat.Economic'].to_dict()
within, across = [], []
for i, j in zip(*iu):
    a, b = names[i], names[j]
    (within if cat.get(a) == cat.get(b) else across).append(abs(C.values[i,j]))

print(f"mean |correlation|\\n")
print(f"  WITHIN economic category   {np.mean(within):.3f}   (n = {len(within)} pairs)")
print(f"  ACROSS economic category   {np.mean(across):.3f}   (n = {len(across)} pairs)")
print(f"\\n  ratio: {np.mean(within)/np.mean(across):.1f}x")"""))

cells.append(md("""### Three papers, one factor

Look at the top of the correlation list:

| pair | correlation |
|---|---|
| MaxRet & RealizedVol | **+0.97** |
| IdioVol3F & RealizedVol | **+0.96** |
| IdioVol3F & MaxRet | **+0.94** |
| Illiquidity & Size | **+0.92** |

Those are separate publications, in separate journals, with separate names and
separate economic stories. At a correlation of 0.97 they are **the same trade**.
Whatever is being paid for, all three are collecting it.

And Illiquidity vs Size at 0.92: illiquid firms *are* small firms. The
"liquidity premium" and the "size premium" are not two findings in this sample.

> **💡 Key Insight: count bets, not papers**
>
> The zoo has 300+ entries and far fewer distinct positions. Signals inside a
> family are near-duplicates (mean |ρ| ≈ 0.58); signals across families are
> nearly independent (≈ 0.19).
>
> **Diversification comes from spanning families, not from collecting names.**

> **⚠️ Caution: this breaks a lot of published evidence**
>
> If 300 papers each report an independent-looking discovery, that seems like
> overwhelming support for cross-sectional predictability. If those 300 papers
> are really testing eight or ten distinct bets over and over on overlapping
> samples, it is much weaker support than the headcount suggests.
>
> That is one of the two big problems with the anomaly literature. We take it
> apart in Lecture 8, and Lecture 17 asks the sharper version: how many distinct
> factors can this data support *at all*?"""))

# ─── Hands-On ─────────────────────────────────────────────────────────
cells.append(md("""---

## 🛠️ Hands-On: Find Your Signal's Twin <a id="ho1"></a>

You picked a signal in Lecture 3 and regressed it in Lecture 4. Now find out
what else it is.

### Your task

Pull your signal's row out of the correlation matrix and look at its nearest
neighbours. Then check whether they're in the same economic category — if the
nearest neighbour is in a *different* family, that's worth knowing."""))

cells.append(code("""# === EDIT + YOUR TURN ===
MY_SIGNAL = "GP"        # ← your pick from Lecture 3

row = ____              # hint: C[MY_SIGNAL].drop(MY_SIGNAL).sort_values(ascending=False)

print(f"{MY_SIGNAL}  ({cat.get(MY_SIGNAL)})\\n")
print("closest 5:")
for s, c in row.head(5).items():
    flag = "  ← same family" if cat.get(s) == cat.get(MY_SIGNAL) else ""
    print(f"  {s:24s} {c:+.2f}   {cat.get(s):22s}{flag}")
print("\\nmost negatively correlated:")
for s, c in row.tail(3).items():
    print(f"  {s:24s} {c:+.2f}   {cat.get(s)}")"""))

cells.append(md("""### What to take from it

If your signal's nearest neighbour is above **+0.8**, you are not holding a
distinct bet — you're holding a version of something else, and any "confirmation"
from that other signal is not independent evidence.

If your closest neighbour is below **+0.3**, your signal is doing something the
rest of the zoo isn't. That is more interesting, and also more suspicious: check
that it isn't just noisier."""))

# ─── Challenge ────────────────────────────────────────────────────────
cells.append(md("""---

## 🎯 Challenge: How Many Bets Are There Really? <a id="challenge"></a>

*Homework — due before Lecture 6.*

You are briefing an investment committee that has been told "we run a
30-factor model, so we're extremely diversified."

Quantify how true that is.

### Q1 — The headline correlation numbers

> **📌 Required variable names:**
> ```python
> mean_pairwise_corr = ____   # mean of the off-diagonal correlations (signed)
> frac_high_corr     = ____   # fraction of pairs with |corr| > 0.5
> ```"""))

cells.append(code("""# Your work here


# Required outputs — fill these in:
mean_pairwise_corr = ____
frac_high_corr     = ____

print(f"mean pairwise correlation : {mean_pairwise_corr:+.3f}")
print(f"share of pairs |corr|>0.5 : {frac_high_corr:.1%}")"""))

cells.append(md("""### Q2 — Within versus across category

> **📌 Required variable names:**
> ```python
> within_cat_corr = ____   # mean |corr| for pairs in the SAME economic category
> across_cat_corr = ____   # mean |corr| for pairs in DIFFERENT categories
> ```"""))

cells.append(code("""# Your work here


# Required outputs — fill these in:
within_cat_corr = ____
across_cat_corr = ____

print(f"within category : {within_cat_corr:.3f}")
print(f"across category : {across_cat_corr:.3f}")
print(f"ratio           : {within_cat_corr/across_cat_corr:.1f}x")"""))

cells.append(md("""### Q3 — The memo

> **📝 Your task — maximum 6 sentences**
>
> Is a 30-factor model diversified?
>
> Use both numbers. The average correlation says one thing and the within/across
> split says another — explain the difference and say which one the committee
> should act on. Name at least one specific pair of signals that are effectively
> the same trade, and say what you'd actually recommend."""))

cells.append(code('''MEMO = """
Write your memo here. Don't delete the surrounding triple quotes.
"""
print(MEMO)'''))

cells.append(md("---\n\n## 📤 Submission <a id=\"submit\"></a>"))

cells.append(code('''# === 📤 SUBMISSION CELL — Run this last ===
import json, base64, hashlib, datetime as dt

required = ["mean_pairwise_corr", "frac_high_corr",
            "within_cat_corr", "across_cat_corr", "MEMO"]
missing = [v for v in required if v not in dir()]
if missing:
    raise NameError(f"\\n❌ Missing before submission: {missing}")

payload = {
    "assignment": "L5_FactorZoo_AI",
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

1. **Three kinds of factor model**, distinguished by what you specify:
   time-series (you name the factor returns), characteristic (you name the
   exposures), statistical (you name nothing).

2. **A sort makes a factor; a regression consumes one.** Same raw material,
   opposite direction.

3. **The zoo has families, not 300 ideas** — value, momentum, profitability,
   investment, low-risk, issuance, liquidity.

4. **Every family has two stories, risk and mispricing**, and they predict
   different futures. Mispricing implies the premium dies after publication.

5. **Correlate the strategies, never the signals.** Names and categories are not
   evidence.

6. **Within a family, mean |ρ| ≈ 0.58. Across families, ≈ 0.19.** Diversification
   comes from spanning families.

7. **Some "different" factors are the same trade.** MaxRet, RealizedVol and
   IdioVol3F correlate 0.94–0.97. Illiquidity and Size, 0.92.

8. **300 papers is not 300 pieces of evidence.** Which is a serious problem for
   the literature, and the subject of Lecture 8.

---

### Next class

We've been using one factor — the market. Next: how to run and read a model with
several, why alpha shrinks every time you add one, and the two different ways to
estimate the whole thing."""))

cells.append(md("---\n\n## 📎 Appendix <a id=\"appendix\"></a>"))

cells.append(code(f'''# ═══════════════════════════════════════════════════════════════════════
# 📎 APPENDIX — data
# ═══════════════════════════════════════════════════════════════════════
# Everything today comes from the repo:
#   panel  = pd.read_parquet(f"{{BASE}}/panel_backbone_1980_2000.parquet")
#   signal = pd.read_parquet(f"{{BASE}}/signals/<Acronym>.parquet")
#   menu   = pd.read_csv(f"{{BASE}}/signal_menu.csv")
#
# The 30 signals are replications from Open Source Asset Pricing
# (Chen & Zimmermann), which covers 300+ published cross-sectional predictors:
#     https://www.openassetpricing.com
# `signal_menu.csv` carries each one's authors, year, journal, economic
# category, and the t-statistic the ORIGINAL paper reported — which is what
# makes the replication comparison in Lecture 3 possible.
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
