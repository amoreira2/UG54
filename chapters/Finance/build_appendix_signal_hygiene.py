"""
Build chapters/Appendix/SignalHygiene_AI.ipynb

Moved out of L3 (which ran 24 minutes over) into the Appendix chapter, where it
gets room to do the thing it actually exists for: COMBINING two signals.

Referenced from Assignment A1 — students need winsorize + z-score to build
their own signal properly, so this works better as assignment support than as
lecture time.

Content:
  1. Why raw signal levels aren't comparable across months (BM drifts 0.87 over
     the sample, so "BM = 0.5" is a different statement in 1980 vs 1999)
  2. z-scoring within month
  3. Winsorization — outliers destroy a z-score before it can help
  4. The payoff: combining value + profitability into one composite signal,
     which is the Buffett "quality at a reasonable price" trade and is
     impossible without standardization

The combining example answers a question the pre-AI cross-sectional notebook
posed and never resolved: "What about interactions of characteristics? How do
you buy profitable firms at a good value, like Warren likes?"
"""

import json
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "Appendix" / "SignalHygiene_AI.ipynb"
OUT.parent.mkdir(parents=True, exist_ok=True)
BASE = "https://raw.githubusercontent.com/amoreira2/UG54/refs/heads/main/assets/data"


def md(t): return {"cell_type": "markdown", "metadata": {}, "source": t.splitlines(keepends=True)}
def code(t): return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": t.splitlines(keepends=True)}


cells = []

cells.append(md("""# Appendix — Signal Hygiene: Winsorize, Then Standardize

**Reference notebook.** Not lectured — work through it before Assignment 1.

## 🎯 What this is for

Lecture 3 sorted stocks on a raw signal and it worked fine, because **ranking is
scale-free**: `pd.qcut` only cares about order, so any monotone transformation
of a signal gives identical deciles.

The moment you want to do anything *other* than a pure sort, that stops being
true. This notebook covers the two operations that make a signal usable:

1. **Winsorizing** — clipping the extremes so outliers stop dominating
2. **Standardizing (z-scoring)** — putting every month on the same scale

And then the thing they unlock: **combining two signals into one**."""))

cells.append(md("---\n\n## 🛠️ Setup"))

cells.append(code(f"""import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
%matplotlib inline
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = [11, 4.5]
import warnings; warnings.filterwarnings('ignore')

BASE  = "{BASE}"
panel = pd.read_parquet(f"{{BASE}}/panel_backbone_1980_2000.parquet")
bm    = pd.read_parquet(f"{{BASE}}/signals/BM.parquet")     # value
gp    = pd.read_parquet(f"{{BASE}}/signals/GP.parquet")     # gross profitability

d = (panel.merge(bm, on=['permno','date'], how='inner')
          .merge(gp, on=['permno','date'], how='inner')
          .dropna(subset=['BM','GP','ret_fwd','me']))
print(f"{{len(d):,}} stock-months with both signals")"""))

# ─── 1. drift ─────────────────────────────────────────────────────────
cells.append(md("""---

## 1. Raw Signal Levels Drift

Book-to-market in 1980 does not mean what it means in 1999. The whole
cross-section moves as valuations rise and fall."""))

cells.append(code("""yr = d.groupby(d.date.dt.year)['BM'].agg(['mean','std'])
print("Cross-sectional mean of raw BM, by year")
for y in [1980, 1985, 1990, 1995, 1999]:
    print(f"  {y}:  mean {yr.loc[y,'mean']:+7.3f}    sd {yr.loc[y,'std']:.3f}")
print(f"\\nThe cross-section drifts {yr['mean'].max()-yr['mean'].min():.2f} over the sample.")
print("A stock at BM = -0.2 is expensive in 1980 and cheap in 1999.")"""))

cells.append(md(r"""### The fix: z-score within each month

$$z_{i,t} = \frac{x_{i,t} - \text{mean}_t(x)}{\text{sd}_t(x)}$$

Subtract the cross-sectional mean and divide by the cross-sectional standard
deviation, **separately in every month**. Every month now has mean 0 and
standard deviation 1, so `z = +1.5` means "one and a half standard deviations
cheap *relative to the market that month*" — a statement that means the same
thing in every year."""))

# ─── 2. winsorize ─────────────────────────────────────────────────────
cells.append(md("""---

## 2. Outliers Destroy a z-Score

A mean and a standard deviation are not robust. One absurd value moves both, so
a single bad observation compresses every other stock toward zero.

**Winsorize first**: clip to a percentile (1% and 99% is standard). The ordering
survives — that stock is still the most extreme — but it stops setting the
scale."""))

cells.append(code("""def zscore(df, col, winsor=None):
    \"\"\"Cross-sectional z-score within each date, optionally winsorized first.\"\"\"
    x = df.groupby('date')[col].transform(
            lambda v: v.clip(v.quantile(winsor), v.quantile(1-winsor))) if winsor else df[col]
    return x.groupby(df['date']).transform(lambda v: (v - v.mean()) / v.std())

d['bm_z']    = zscore(d, 'BM')
d['bm_wz']   = zscore(d, 'BM', winsor=0.01)

print(f"{'':26s}{'mean':>8s}{'sd':>7s}{'min':>9s}{'max':>8s}")
print(f"{'raw BM':26s}{d.BM.mean():>8.2f}{d.BM.std():>7.2f}{d.BM.min():>9.2f}{d.BM.max():>8.2f}")
print(f"{'z-scored':26s}{d.bm_z.mean():>8.2f}{d.bm_z.std():>7.2f}{d.bm_z.min():>9.2f}{d.bm_z.max():>8.2f}")
print(f"{'winsorized, then z':26s}{d.bm_wz.mean():>8.2f}{d.bm_wz.std():>7.2f}"
      f"{d.bm_wz.min():>9.2f}{d.bm_wz.max():>8.2f}")
print("\\nz-scoring alone leaves a -10 sigma observation. Winsorizing pulls the")
print("range to about +/- 3, which is what you want before averaging anything.")"""))

cells.append(code("""fig, ax = plt.subplots(1, 2, figsize=(13, 4))
ax[0].hist(d.bm_z.clip(-6, 6), bins=80, color='steelblue', alpha=0.75)
ax[0].set_title('z-scored only', fontweight='bold'); ax[0].set_xlabel('z')
ax[1].hist(d.bm_wz.clip(-6, 6), bins=80, color='darkorange', alpha=0.75)
ax[1].set_title('winsorized at 1/99, then z-scored', fontweight='bold'); ax[1].set_xlabel('z')
plt.tight_layout(); plt.show()"""))

cells.append(md("""> **📌 Remember: it does NOT change a sort**
>
> Raw, z-scored, and winsorized-then-z-scored all produce **identical deciles**,
> because all three are monotone transformations within each month. If a sort is
> all you're doing, none of this matters.
>
> It matters the moment you average, combine, or weight by signal strength."""))

# ─── 3. combining ─────────────────────────────────────────────────────
cells.append(md("""---

## 3. The Payoff: Combining Two Signals

Here is the question this whole notebook exists to answer.

Value says buy cheap firms. Profitability says buy firms that earn a lot per
dollar of assets. **Buffett's whole idea is doing both at once** — a good
business at a fair price.

So: how do you buy stocks that score well on *both*?

You cannot average a book-to-market of 0.8 with a gross profitability of 0.31.
They have different units, different scales, and different distributions. Adding
them is meaningless — whichever has the bigger numbers would dominate.

You *can* average two z-scores. That is the point of standardizing."""))

cells.append(code("""d['gp_wz'] = zscore(d, 'GP', winsor=0.01)
d['combo'] = (d.bm_wz + d.gp_wz) / 2          # equal-weight the two z-scores

def decile_ls(df, col):
    x = df.copy()
    x['g'] = x.groupby('date')[col].transform(
        lambda v: pd.qcut(v, 10, labels=False, duplicates='drop'))
    p = x.groupby(['date','g']).apply(
            lambda g: np.average(g['ret_fwd'], weights=g['me'])).unstack()
    r = (p[9] - p[0]).dropna()
    return r.mean()*12, r.std()*np.sqrt(12), r.mean()/r.std()*np.sqrt(len(r)), r

print(f"{'signal':32s}{'return/yr':>11s}{'vol':>8s}{'Sharpe':>9s}{'t':>7s}")
print("-"*67)
res = {}
for name, col in [('Value (BM)','bm_wz'), ('Profitability (GP)','gp_wz'),
                  ('Both, z-scored and averaged','combo')]:
    m, v, t, r = decile_ls(d, col); res[name] = r
    print(f"{name:32s}{m:>10.2%}{v:>8.1%}{m/v:>9.2f}{t:>7.2f}")

print(f"\\ncorrelation between the two long-shorts: "
      f"{res['Value (BM)'].corr(res['Profitability (GP)']):.2f}")"""))

cells.append(md("""### Why the combination helps

Look at the correlation between the two standalone long-shorts: it is
**negative**. Value and profitability don't merely fail to move together — they
actively offset. That makes sense, because cheap firms are very often
*unprofitable* firms, so the two signals disagree about a large share of stocks.

The result is a combination that beats both of its ingredients by a wide margin:

| | Sharpe |
|---|---|
| Value alone | 0.34 |
| Profitability alone | 0.58 |
| **Both, averaged as z-scores** | **0.78** |

The combined strategy has a *lower* volatility than either input while earning
more than both. That is not a coincidence — it is what negatively correlated
bets do.

> **💡 Key Insight**
>
> This is the same diversification argument from Lecture 2, applied to *signals*
> rather than *stocks*. Two imperfectly-correlated bets combine into something
> with a better Sharpe ratio than either one. We formalize it in Lecture 12.

> **⚠️ Caution: equal weights are a choice**
>
> We averaged the two z-scores 50/50 because it is simple and hard to overfit.
> You could optimize the weights on historical data — and you would get a better
> in-sample result and, very often, a worse out-of-sample one. Lecture 7."""))

cells.append(md("""---

## 🧠 Summary

1. **Ranking is scale-free.** If all you do is sort, raw signals are fine.
2. **Raw levels drift across time**, so they are not comparable across months.
3. **z-score within each month** to fix that: mean 0, sd 1, every month.
4. **Winsorize before you standardize** — one outlier otherwise sets the scale
   for everybody.
5. **Standardization is what makes signals combinable.** Two z-scores can be
   averaged; two raw characteristics cannot.
6. **Combining imperfectly-correlated signals improves Sharpe** — diversification
   across signals, not just across stocks.

### For Assignment 1

If your group is using a single signal, you can sort on it raw. If you plan to
combine two, winsorize and z-score both first, and say in your memo how you
weighted them.

> **Related:** BARRA-style risk models define their factor exposures as exactly
> this — winsorized, standardized characteristics. Lecture 14."""))

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
