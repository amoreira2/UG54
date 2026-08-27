import json, pathlib
def md(s): return {"cell_type":"markdown","metadata":{},"source":s.splitlines(keepends=True)}
def code(s): return {"cell_type":"code","execution_count":None,"metadata":{},"outputs":[],
                     "source":s.splitlines(keepends=True)}
C=[]
C.append(md("""# Assignment 3 — Beta, Alpha, and Whether You Have Either

**Due Thursday 24 September, midnight, on Brightspace.**
Graded on completion. Groups of three; each of you submits your own copy.

---

**Group members:**

---

Two parts, add-ons first.

**Part 1** is the same for everyone and runs on the 49-industry file from
Assignment 1 — small enough that you can see every number. It is about what beta
is *for*: hitting a mandate, hedging a position, and deciding whether a large
alpha is a trade.

**Part 2** takes your group's own strategy up the factor ladder and asks the
question the whole block has been building to: **is your return skill, or is it
exposure you could have bought for five basis points?**"""))

C.append(md("## 🛠️ Setup"))
C.append(code("""import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt
%matplotlib inline
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = [10, 4]
import warnings; warnings.filterwarnings('ignore')

BASE = "https://raw.githubusercontent.com/amoreira2/UG54/refs/heads/main/assets/data"
XLS  = f"{BASE}/Assignment1.xlsx"      # the 49 industries, from Assignment 1

print("ready")"""))

C.append(md("""---

# Part 1 — What beta is actually for

### Q1 — Guess before you measure

Rebuild the industry excess returns from Assignment 1 — you already wrote this
code, so reuse it. Then pick **ten** industries, and plot their monthly excess
returns against the market's on the same axes.

> **(a)** Just by looking, which one has the highest beta? Which the lowest?
> Write your guess down before running a single regression.
>
> **(b)** Why does it matter to measure beta *correctly*? Be concrete: you hold
> a position in one of these industries and you have a view on it. Explain how
> knowing its beta lets you improve that trade."""))
C.append(code("""# Rebuild `d` (49 industries, excess returns) and `M` (market excess return)
# from Assignment 1, then plot ten of them against M.

"""))
C.append(md("""**(a)** highest beta guess: · lowest beta guess:

**(b)**"""))

C.append(md("""### Q2 — Now measure

Regress **each** of the 49 industries on the market excess return, with an
intercept. Collect the betas, the annualized alphas, and the t-statistics on the
alphas.

Report: the highest and lowest beta industries, the median beta, and the
industries with the highest and lowest alpha.

Then one number that matters more than any of those: **how many of the 49 have
an alpha more than two standard errors from zero?**

> **⚠️** You are running 49 regressions. At a 5% threshold you would expect
> about two or three to look significant even if every true alpha were exactly
> zero. Hold that thought — it is Assignment 4."""))
C.append(code("""# your code here

"""))
C.append(md("""**How many clear |t| > 2, out of 49? What do you make of that number?**"""))

C.append(md("""### Q3 — Hit a mandate

You are a fund manager. Your mandate says: **keep your portfolio beta at 0.5.**
Not lower, not higher — that is what you were hired to deliver.

Using the betas from Q2, construct **five different portfolios of these
industries that all have a beta of 0.5.** At least one of them must hold **more
than one** industry.

For each, report the weights and verify the resulting beta.

> **🤔 Then answer this.** You just produced five portfolios that a mandate
> would treat as identical. Are they identical? What differs between them that
> your client would care about, and which of the five would you actually run?"""))
C.append(code("""# your code here

"""))
C.append(md("""**Are the five identical? Which would you run, and why?**"""))

C.append(md("""### Q4 — Hedge them out

For each of your five mandate portfolios, construct the **beta-hedged** return:
hold the portfolio and short β units of the market, so

$$r^{\\text{hedged}}_t = r_t - \\beta \\, r_{m,t}$$

Plot the five hedged series against the market — market on the x-axis, hedged
return on the y — and report each one's correlation with the market and its
annualized volatility.

> **(a)** Do the five hedged portfolios co-move with each other? With the market?
>
> **(b)** Their market exposure is zero by construction. Can you therefore call
> them **risk-free**? In what sense are they free of risk, and in what sense are
> they emphatically not?
>
> **(c)** Compare each hedged portfolio's volatility to its unhedged volatility.
> What did hedging buy you, and what did it cost?"""))
C.append(code("""# your code here

"""))
C.append(md("""**(a)**

**(b)**

**(c)**"""))

C.append(md("""### Q5 — The highest alpha is not the best trade

From Q2, find the industry with the **largest** alpha and the one with the
**smallest**.

> **(a)** If you could put on exactly one trade, is buying the highest-alpha
> industry the best you can do? Argue it either way, but commit.
>
> **(b)** Name at least three things that matter for choosing the trade that the
> alpha *by itself* does not tell you. For each, say how you would measure it
> with what you already have.
>
> **(c)** Suppose you pick the best single trade by whatever criterion you just
> defended. Is that the best you can do overall? Describe — you do not have to
> implement it — how you would build something better out of these 49 assets."""))
C.append(code("""# your code here

"""))
C.append(md("""**(a)**

**(b)**

**(c)**"""))

C.append(md("""---

# Part 2 — Your strategy: skill or exposure?

In Assignment 2 you built a long-short return series for your group's signal.
You reported its Sharpe ratio and left it there. A Sharpe ratio cannot tell you
whether you found something or rediscovered something the market already sells
in an ETF. That is what a factor model is for.

Rebuild your long-short series from Assignment 2 — same convention: **NYSE
breakpoints, value-weighted, D10−D1, `ret_fwd`.** Call it `ls`, and remember to
shift its index forward one month so it is dated by the month the return was
*earned*, not the month you formed the portfolio."""))
C.append(code("""BASE = "https://raw.githubusercontent.com/amoreira2/UG54/refs/heads/main/assets/data"
panel = pd.read_parquet(f"{BASE}/panel_backbone_1980_2000.parquet")

MY_SIGNAL = "____"        # ← the same signal as Assignment 2

# rebuild your long-short (reuse your Assignment 2 code)
ls = ____
print(f"{MY_SIGNAL}: {len(ls)} months, raw return {ls.mean()*12:+.2%}/yr")"""))

C.append(md("""### Q6 — Against the market alone

Fetch the Fama-French factors and regress your long-short on `Mkt-RF` with an
intercept. Report annualized alpha, its t-statistic, beta, R², and the
**appraisal ratio** (annualized alpha over annualized residual volatility).

> **🤔 Predict first.** A long-short is long some stocks and short others, so it
> ought to be roughly market-neutral. Do you expect a beta near zero? Commit
> before you run it — and if your beta is *not* near zero, that is a finding
> about your signal, not a bug."""))
C.append(code("""import pandas_datareader.data as web

f5  = web.DataReader('F-F_Research_Data_5_Factors_2x3','famafrench',start='1980-01-01')[0]/100
umd = web.DataReader('F-F_Momentum_Factor','famafrench',start='1980-01-01')[0]/100
for x in (f5, umd):
    x.index = pd.to_datetime(x.index.to_timestamp()) + pd.offsets.MonthEnd(0)
umd.columns = ['UMD']
FF = f5.join(umd, how='inner').loc['1980-01-31':'2000-12-31']

# your regression here
"""))
C.append(md("""**Predicted beta:** · **Actual:**"""))

C.append(md("""### Q7 — Up the ladder

Run the same regression against four models, all on the same months:

| model | factors |
|---|---|
| CAPM | Mkt-RF |
| FF3 | + SMB, HML |
| FF5 | + RMW, CMA |
| FF6 | + UMD |

Produce one table: annualized alpha, its t-statistic, and R² for each rung."""))
C.append(code("""MODELS = {'CAPM': ['Mkt-RF'],
          'FF3' : ['Mkt-RF','SMB','HML'],
          'FF5' : ['Mkt-RF','SMB','HML','RMW','CMA'],
          'FF6' : ['Mkt-RF','SMB','HML','RMW','CMA','UMD']}

# your code here
"""))

C.append(md("""### Q8 — Read the loadings before the alpha

Print the full set of loadings for the FF6 regression.

> **(a)** Which factor has the largest loading? What does that say about what
> your strategy is actually holding — in plain language, not factor names.
>
> **(b)** Where on the ladder did your alpha change the most, and which factor
> entered at that rung? Alpha falling means the model explains your return;
> alpha *rising* means you were negatively exposed to something that paid, and
> the raw return was understating you. Which happened to you?
>
> **(c)** R² rises as you add factors. Is a high R² good news or bad news for
> you specifically? Say why in one sentence."""))
C.append(code("""# your code here
"""))
C.append(md("""**(a)**

**(b)**

**(c)**"""))

C.append(md("""### Q9 — Is your alpha distinguishable from zero?

A point estimate on its own is not a result. For each rung of the ladder,
report the **standard error** of the annualized alpha and its **95% confidence
interval**, $\\hat\\alpha \\pm 1.96 \\times SE(\\hat\\alpha)$.

Then say, for each model, whether that interval contains zero.

> **📌** This is the same calculation as the standard error of a mean —
> $\\sigma/\\sqrt{T}$ — and it is why the t-statistic keeps appearing. With
> ~250 months, an annualized alpha needs to be roughly 4% or more before the
> interval clears zero. Most published anomalies are not far above that line.

> **(a)** At which rungs does your interval exclude zero?
>
> **(b)** Take the widest interval you produced. State its two endpoints as
> annual returns and describe what each would mean for the strategy. Are they
> the same investment decision?"""))
C.append(code("""# your code here
"""))
C.append(md("""**(a)**

**(b)**"""))

C.append(md("""### Q10 — The memo

> **📝 Maximum ten sentences.**
>
> Your PM read Assignment 2 and saw a Sharpe ratio. Now tell them what it was
> made of.
>
> Cover: whether your return survives the factor model and at which rung it
> stops; which factor does the damage and what that means about the positions
> you are holding; whether the alpha is distinguishable from zero; and what you
> would charge for this strategy — a fee on alpha, a fee on beta, or nothing.
>
> If your alpha vanished at FF3, say so and say what that tells you. **A signal
> that turns out to be a repackaged value tilt is a real finding**, and knowing
> it now is worth more than discovering it in December."""))
C.append(md("""**Memo:**

"""))

C.append(md("""---

## 📌 What comes next

You now know whether your strategy has alpha **relative to a model you chose
after looking at the data**. That is the weakness in everything above, and it is
not a small one: you ran your signal up four rungs and reported what you found.

Assignment 4 asks the harder question. How many signals did your group try
before settling on this one? How much of what survives is a real effect and how
much is the natural consequence of looking at enough series? You saw a preview
in Q2 — five of forty-nine industries cleared |t| > 2, and pure chance predicts
about two or three."""))

nb={"cells":C,"metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},
    "language_info":{"name":"python","version":"3.11"}},"nbformat":4,"nbformat_minor":5}
out=pathlib.Path("chapters/Assignments/A3_Beta_and_Alpha_AI.ipynb")
json.dump(nb, open(out,'w'), indent=1, ensure_ascii=False); open(out,'a').write("\n")
print(f"✅ {out}  —  {len(C)} cells, 10 questions")
