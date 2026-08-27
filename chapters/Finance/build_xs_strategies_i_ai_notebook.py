"""Build CrossSectional_I_AI.ipynb — Lecture 13.
Topic: characteristic-based long-short portfolios. Value strategy as the running example.
Challenge: build a B/M long-short and report its Sharpe + alpha vs CAPM.
"""
import json
from pathlib import Path
OUT = Path(__file__).parent / "CrossSectional_I_AI.ipynb"
def md(t): return {"cell_type":"markdown","metadata":{},"source":t.splitlines(keepends=True)}
def code(t): return {"cell_type":"code","execution_count":None,"metadata":{},"outputs":[],"source":t.splitlines(keepends=True)}

cells = []
cells.append(md("""# Cross-Sectional Strategies I — The Recipe
## 🎯 Learning Objectives

By the end of this notebook, you will be able to:

1. **Construct characteristic-based portfolios** — sort stocks on a characteristic, form quintile portfolios
2. **Build a long-short portfolio** — top quintile minus bottom quintile, the workhorse of empirical asset pricing
3. **Test whether a characteristic predicts returns** — by regressing portfolio returns on factor models
4. **Distinguish a *risk* premium from an *anomaly*** — what the alpha vs. R² split tells you
5. **Audit AI-generated portfolio-construction code** — survivorship bias, lookahead, rebalancing logic"""))

cells.append(md("""## 📋 TOC
1. [Setup](#setup)  2. [The Recipe](#recipe)  3. [Pitfall Checklist](#pitfalls)
4. [Worked Example: Book-to-Market Sorts](#bm)  5. [The Long-Short Portfolio](#ls)
6. [Is It Alpha or Beta?](#alphabeta)  7. [🎯 Challenge: Build a Value Strategy](#challenge)
8. [Submission](#submit)  9. [Key Takeaways](#takeaways)"""))

cells.append(md("---\n## 🛠️ Setup <a id=\"setup\"></a>"))
cells.append(code("""#@title Setup
import numpy as np, pandas as pd, matplotlib.pyplot as plt, statsmodels.api as sm
%matplotlib inline
plt.style.use('seaborn-v0_8-whitegrid'); plt.rcParams['figure.figsize']=[10,5]; plt.rcParams['font.size']=11
import warnings; warnings.filterwarnings('ignore')
print("✅ Loaded")"""))

cells.append(md("""---
## The Recipe <a id="recipe"></a>

Every characteristic-based strategy follows the same 5-step recipe:

1. **Pick a characteristic** $X_{i,t}$ (book-to-market, momentum, size, etc.) observable at time $t$
2. **Each rebalance date**, sort firms by $X$ into N portfolios (typically N=5 quintiles or N=10 deciles)
3. **Inside each portfolio**, weight stocks (equal-weight or value-weight)
4. **Hold to the next rebalance date**, compute the portfolio's return
5. **Long-short:** subtract the bottom-N portfolio return from the top-N portfolio return

**The output is a single return time series** that you can regress against
factor models, compute Sharpe ratios for, etc."""))

cells.append(md("""---
## 🛡️ Pitfall Checklist <a id="pitfalls"></a>

| | Pitfall | What goes wrong | 🔍 How to detect |
|---|---------|-----------------|-------------------|
| 1 | **Lookahead in the characteristic** | Using $X_{i,t+1}$ to predict $r_{i,t+1}$ | Always lag $X$ by at least one period |
| 2 | **Survivorship bias** | Sample includes only firms that survived to today | CRSP is survivorship-free if you use it; Yahoo Finance is NOT |
| 3 | **Equal-weight without size filter** | Tiny firms dominate the EW portfolio; results don't translate to investable strategies | Restrict to top 80% by market cap, or value-weight |
| 4 | **Rebalancing too often** | Quintile portfolios rebalanced daily = huge transaction costs | Annual or monthly rebalancing is standard |
| 5 | **Look-ahead in the breakpoints** | Using full-sample quintile cutoffs to assign past observations | Compute breakpoints using ONLY data up to that date |
| 6 | **Comparing returns to wrong benchmark** | Comparing to the S&P 500 when your strategy is small-cap-tilted | Always regress against an appropriate factor model |

> **🤖 AI-Era Insight**
>
> AI is great at writing the sorting + grouping code. AI is bad at noticing
> survivorship bias or asking "did you lag the characteristic?". Always audit."""))

cells.append(md("""---
## Worked Example: Book-to-Market Sorts <a id="bm"></a>

We use a small pre-cleaned panel of US stocks with monthly returns and
book-to-market ratios (1995-2020). The data is stacked: one row per
(permno, month)."""))

cells.append(code("""# Load the stacked panel
url = 'https://raw.githubusercontent.com/amoreira2/UG54/refs/heads/main/assets/data/wrds_tour_chars_xs.csv'
# This is a single-month cross-section — for full panel we'd need a bigger pull.
# For class purposes, we'll DEMONSTRATE the methodology on a single snapshot.
xs = pd.read_csv(url)
print(f"Cross-section: {len(xs)} firms")
print(f"Columns: {list(xs.columns)}")
xs.head(3)"""))

cells.append(code("""# Sort by book-to-market (B/M = ce_compustat / market_cap_M)
xs = xs.dropna(subset=['ce_compustat', 'market_cap_M', 'ret']).copy()
xs['bm'] = xs['ce_compustat'] / xs['market_cap_M']
xs = xs[(xs['bm'] > 0) & (xs['bm'] < 10)]   # drop extreme outliers

# Form quintile portfolios
xs['quintile'] = pd.qcut(xs['bm'], 5, labels=['Q1 (growth)', 'Q2', 'Q3', 'Q4', 'Q5 (value)'])
quintile_ret = xs.groupby('quintile')['ret'].mean()
quintile_n   = xs.groupby('quintile').size()
print("\\nMean return by B/M quintile:")
print(quintile_ret.to_frame('mean_ret').assign(n=quintile_n).round(4))"""))

cells.append(md("""> **🤔 Interpretation**
>
> If high-B/M (value) stocks have higher mean returns than low-B/M (growth)
> stocks IN A SINGLE MONTH, that's noise. The "value premium" is the claim
> that, **averaged over many months and many decades**, value beats growth.
>
> With a single cross-section we can't test it. In practice you'd run this
> recipe every month for 50+ years and average the long-short returns."""))

cells.append(md("""---
## The Long-Short Portfolio <a id="ls"></a>

$$r^{LS}_t = r^{Q5}_t - r^{Q1}_t$$

This is **dollar-neutral** by construction (longs $1 of value, shorts $1 of
growth). Its return is the *premium* on the characteristic, controlling for
the overall market level.

The Sharpe ratio of $r^{LS}_t$ over a long sample is the standard test of
whether the characteristic earns a premium."""))

cells.append(code("""# What a single-cross-section "long-short" would have given that month
ls_ret = quintile_ret['Q5 (value)'] - quintile_ret['Q1 (growth)']
print(f"Q5 minus Q1 return (single cross-section): {ls_ret:+.2%}")
print("\\n(In a real analysis you'd repeat this every month and look at the time series.)")"""))

cells.append(md("""---
## Is It Alpha or Beta? <a id="alphabeta"></a>

Once you have a long-short return series, run a factor regression:

$$r^{LS}_t = \\alpha + \\beta^{MKT} \\cdot MKT_t + \\beta^{SMB} \\cdot SMB_t + \\ldots + \\epsilon_t$$

If $\\alpha = 0$ but R² is high, the long-short is just exposure to known
factors → not novel.

If $\\alpha > 0$ and significant, you've found a new factor (or true alpha).
This is the **standard test** for whether a "new" strategy is anything more
than re-packaged size/value/momentum exposure."""))

# Challenge
cells.append(md("""---
## 🎯 Challenge: Build a Value Strategy <a id="challenge"></a>

> **Setup.** Apply the recipe in the cross-section data `xs` already loaded.

### Q1 — Quintile returns

Compute the mean return in each B/M quintile (Q1 = growth, Q5 = value).
Report Q1 and Q5 means.

> **📌 Required variables:**
> ```python
> q1_growth_return = ____   # mean return of Q1 (lowest B/M)
> q5_value_return  = ____
> ```"""))

cells.append(code("""# Your work here


q1_growth_return = ____
q5_value_return  = ____
print(f"Q1 (growth): {q1_growth_return:+.2%}")
print(f"Q5 (value):  {q5_value_return:+.2%}")"""))

cells.append(md("""### Q2 — Long-short return

> **📌 Required variable:**
> ```python
> long_short_return = ____   # Q5 minus Q1
> ```"""))

cells.append(code("""# Your work here


long_short_return = ____
print(f"Long-short (value minus growth): {long_short_return:+.2%}")"""))

cells.append(md("""### Q3 — Average B/M in each tail

What's the mean B/M ratio in Q1 and in Q5? (Useful to characterize how
extreme each quintile actually is.)

> **📌 Required variables:**
> ```python
> mean_bm_growth = ____
> mean_bm_value  = ____
> ```"""))

cells.append(code("""# Your work here


mean_bm_growth = ____
mean_bm_value  = ____
print(f"Mean B/M in growth quintile: {mean_bm_growth:.2f}")
print(f"Mean B/M in value  quintile: {mean_bm_value:.2f}")"""))

cells.append(md("""### Q4 — The Memo

Max 5 sentences:
1. Did value beat growth in this single cross-section?
2. What would you need to do to credibly test the "value premium" claim?
3. What's the single biggest pitfall in claiming you've discovered a new strategy?"""))

cells.append(code("""MEMO = \"\"\"
Write your memo here.
\"\"\"
print(MEMO)"""))

cells.append(md("---\n## 📤 Submission <a id=\"submit\"></a>"))
cells.append(code("""# === 📤 SUBMISSION CELL ===
import json, base64, hashlib, datetime as dt
required = ["q1_growth_return", "q5_value_return", "long_short_return",
            "mean_bm_growth", "mean_bm_value", "MEMO"]
missing = [v for v in required if v not in dir()]
if missing: raise NameError(f"\\n❌ Missing: {missing}")
payload = {"assignment": "CrossSectional_I_AI",
    "ts": dt.datetime.utcnow().isoformat(timespec="seconds") + "Z",
    "answers": {k: float(eval(k)) for k in required if k != "MEMO"},
    "memo": MEMO.strip()}
blob = json.dumps(payload, sort_keys=True)
token = f"UG54::{hashlib.sha256(blob.encode()).hexdigest()[:8]}::{base64.b64encode(blob.encode()).decode()}"
print("="*72); print(token); print("="*72)"""))

cells.append(md("""---
## 🧠 Key Takeaways <a id="takeaways"></a>

1. **The recipe is universal:** characteristic → sort → portfolios → long-short → factor regression.
2. **Single cross-section ≠ premium.** A premium requires averaging across many periods.
3. **Long-short is dollar-neutral by construction** — its return is the characteristic's premium, free of market exposure.
4. **Alpha vs R² in the factor regression** tells you whether the strategy is novel.
5. **Pitfalls: lookahead, survivorship, breakpoint contamination.** AI catches none of these — you must."""))

notebook = {"cells": cells, "metadata": {"colab":{"provenance":[],"toc_visible":True},"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},"language_info":{"name":"python"}}, "nbformat": 4, "nbformat_minor": 5}
OUT.write_text(json.dumps(notebook, indent=1))
print(f"✅ Wrote {OUT} ({len(cells)} cells)")
