import json, pathlib
def md(s): return {"cell_type":"markdown","metadata":{},"source":s.splitlines(keepends=True)}
def code(s): return {"cell_type":"code","execution_count":None,"metadata":{},"outputs":[],
                     "source":s.splitlines(keepends=True)}
C=[]
C.append(md("""# Assignment 1 — Diversification, and Your First Sort

**Due Thursday 17 September, midnight, on Brightspace.**
Graded on completion. Work in your group of three; each of you submits your own copy.

---

**Group members**

- Name / NYU email:
- Name / NYU email:
- Name / NYU email:

---

Two parts. **Part 1** is the same for everybody and answers a question Lecture 2
deliberately left open. **Part 2** is where your group's own strategy starts —
everything you do for the rest of the term builds on it.

Use AI freely. You will be asked to explain what you did."""))

C.append(md("## 🛠️ Setup"))
C.append(code("""import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
%matplotlib inline
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = [10, 4]
import warnings; warnings.filterwarnings('ignore')

BASE  = "https://raw.githubusercontent.com/amoreira2/UG54/refs/heads/main/assets/data"
panel = pd.read_parquet(f"{BASE}/panel_backbone_1980_2000.parquet")
menu  = pd.read_csv(f"{BASE}/signal_menu.csv")

print(f"{len(panel):,} stock-months, {panel.permno.nunique():,} stocks, "
      f"{panel.date.nunique()} months")
print(f"{len(menu)} signals on the menu")"""))

# ── PART 1 ───────────────────────────────────────────────────────────
C.append(md("""---

# Part 1 — How much does diversification actually buy you?

In Lecture 2 we found that a typical stock runs about **52% volatility a year**
while the whole market runs **15.5%**, and left two questions hanging. This is
the first one:

> There are roughly 6,000 stocks. If they moved independently, averaging them
> would drive volatility to almost nothing. It stops at 15.5%. **Why?**

You are going to answer it by measuring, not by being told."""))

C.append(md("""### Q1 — A clean set of stocks to work with

Comparing portfolios of different sizes only makes sense if every portfolio
covers the same months. Build a **wide** table — dates down the rows, one column
per stock, returns in the cells — keeping only stocks that are present for the
**entire** sample.

> **📝 Spec.** From `panel`, produce a DataFrame `W` indexed by `date` with one
> column per `permno`, containing `ret`. Drop any stock that has a missing month.
> Report how many stocks survive.

> **🤖 A prompt that gets you close:** *"Pivot a long DataFrame with columns
> permno, date, ret into a wide DataFrame indexed by date with one column per
> permno, then drop every column that contains any NaN."*"""))
C.append(code("""# Your work here


W = ____          # wide table: dates x stocks
print(f"{W.shape[1]} stocks with a complete {W.shape[0]}-month history")"""))

C.append(md("""### Q2 — The volatility of an equal-weighted portfolio of N stocks

Write a function that takes a number of stocks `N`, picks `N` of them **at
random** from `W`, forms the equal-weighted portfolio, and returns its
**annualized** volatility.

Two things to be careful about. An equal-weighted portfolio of a set of columns
is just their average, row by row. And annualizing a monthly volatility means
multiplying by √12, not by 12."""))
C.append(code("""rng = np.random.default_rng(0)      # so your answers are reproducible

def port_vol(N):
    \"\"\"Annualized volatility of an equal-weighted portfolio of N random stocks.\"\"\"
    ____

print(f"one draw of 10 stocks: {port_vol(10):.1%}")"""))

C.append(md("""### Q3 — Average over many draws

One draw is noise — you might happen to pick ten utilities. Write
`avg_port_vol(N, n_draws=100)` that repeats Q2 `n_draws` times and returns the
average."""))
C.append(code("""def avg_port_vol(N, n_draws=100):
    ____

print(f"N=10, averaged over 100 draws: {avg_port_vol(10):.1%}")"""))

C.append(md("""### Q4 — The curve

Compute `avg_port_vol` for **N = 1, 2, 5, 10, 20, 50, 100, 200** and plot it
against N. Put N on a log scale — the interesting action is at small N."""))
C.append(code("""NS = [1, 2, 5, 10, 20, 50, 100, 200]

# Your work here
"""))

C.append(md("""### Q5 — Two reference lines

The plot on its own does not tell you what it *should* have looked like. Add
two lines.

**Line A — what you would get if stocks were independent.** If N stocks each had
volatility σ and were uncorrelated, the equal-weighted portfolio's volatility
would be σ/√N. Use the average single-stock volatility in `W` for σ, and draw
that curve across the same range of N.

**Line B — the market.** Compute the value-weighted market return from `panel`
(you built this in Lecture 2: weight by `me`, earn `ret_fwd`) and draw its
annualized volatility as a horizontal line.

> **⚠️ Careful.** Line A is *not* a fitted line or a prediction. It is what the
> arithmetic gives you under an assumption you have every reason to doubt. The
> point of drawing it is to see how badly the assumption fails."""))
C.append(code("""# Your work here
"""))

C.append(md("""### Q6 — Read your own plot

> **📝 Answer in the cell below — a short paragraph each, no code.**
>
> **(a)** Roughly where does your curve stop falling? Give an N.
>
> **(b)** The independent line keeps going down and your curve does not. Describe
> the gap between them at N = 200 and say, in your own words, what is in that
> gap. What is it about real stocks that the independent calculation ignores?
>
> **(c)** Look at where your curve levels off relative to the market line. Is
> that a coincidence? What would have to be true for a large equal-weighted
> portfolio to end up at the market's volatility?
>
> **(d)** You are about to build a long-short portfolio out of roughly 600
> stocks per leg. Given this plot, what does that buy you — and what does it
> *not* protect you from?"""))
C.append(md("""**(a)**

**(b)**

**(c)**

**(d)**"""))

# ── PART 2 ───────────────────────────────────────────────────────────
C.append(md("""---

# Part 2 — Your strategy

From here on this is your group's project. Whatever you pick now, you will carry
through the term — you may change it later, but pick something you find
interesting enough to argue about."""))

C.append(md("""### Q7 — Pick a signal, and commit to a story first

Look at the menu. Pick **one** signal.

Then, **before you compute anything**, write two or three sentences on why it
might predict returns. Is it compensation for a risk somebody is unwilling to
bear, or is it a mistake other investors are making? You are not being graded on
being right. You are being graded on having said something falsifiable before
you saw the answer."""))
C.append(code("""pd.set_option('display.max_rows', 40, 'display.width', 200)
menu[['Acronym','Authors','Year','Cat.Economic','T-Stat']].sort_values('Cat.Economic')"""))
C.append(code("""MY_SIGNAL = "____"        # ← your pick

sig = pd.read_parquet(f"{BASE}/signals/{MY_SIGNAL}.parquet")
row = menu.loc[menu.Acronym == MY_SIGNAL].iloc[0]
print(f"{MY_SIGNAL} — {row.Authors} ({row.Year}), published t = {row['T-Stat']:+.2f}")
print(f"{len(sig):,} stock-months\\n")
print(row.LongDescription[:400])"""))
C.append(md("""**Why might this signal predict returns?** *(write before you run anything)*

"""))

C.append(md("""### Q8 — Run the standard sort

Everyone in the class uses the same convention so results are comparable:
**NYSE breakpoints, value-weighted, top decile minus bottom decile, `ret_fwd`.**

> **📝 Spec.** Merge your signal onto `panel`. Drop rows missing the signal,
> `ret_fwd` or `me`, **before** ranking. Each month, compute the 10th and 90th
> percentile of the signal **using NYSE stocks only** (`exchcd == 1`), then apply
> those cutoffs to **every** stock. Value-weight within each leg using `me`.
> Return the monthly series of top-minus-bottom.

Lecture 3 has a working version of this. You may reuse it — but read it first
and make sure you can say what each line does."""))
C.append(code("""# Your work here


ls = ____        # monthly long-short return series
print(f"{len(ls)} months")"""))

C.append(md("""### Q9 — Report it honestly

Report, for your long-short: annualized mean return, annualized volatility,
Sharpe ratio, and the t-statistic. Then report **each leg separately** — a
spread built entirely from a collapsing short leg is a different claim from one
where both sides contribute. Finally, put your t-statistic next to the one the
original authors published."""))
C.append(code("""# Your work here
"""))

C.append(md("""### Q10 — Look at the shape, not just the spread

Plot the annualized mean return of all ten deciles as a bar chart.

A **monotone** staircase — each decile beating the one below — is much stronger
evidence than a large gap between two extremes with a flat middle. The second
pattern usually means two small groups of unusual firms are doing all the work."""))
C.append(code("""# Your work here
"""))

C.append(md("""### Q11 — The memo

> **📝 Maximum eight sentences. This is the part I will actually read.**
>
> Your PM asks whether this signal is worth pursuing. Answer them.
>
> Cover: what you found; whether it replicated the published result and what you
> make of it if it didn't; whether the sort is monotone; which leg is doing the
> work; and one specific thing you would want to check before putting money on
> it.
>
> If your signal did not work, say so plainly. **Most signals do not work, and a
> project that establishes that honestly is a good project.** You will not be
> penalised for a negative result — only for pretending you didn't get one."""))
C.append(md("""**Memo:**

"""))

C.append(md("""---

## 📌 What comes next

You now have a return series for your strategy. What you do **not** yet know is
whether that return is skill or exposure — whether you have found something, or
just rediscovered a bet the market already sells cheaply.

That is Assignment 2, once Lectures 4–6 have given you factor models. It will
ask you to regress this series on the market and then on the six-factor model,
read the loadings before the alpha, and work out what a mandate to hold a
particular beta would force you to do.

Keep your notebook. You will reuse `ls` directly."""))

nb={"cells":C,"metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},
    "language_info":{"name":"python","version":"3.11"}},"nbformat":4,"nbformat_minor":5}
out=pathlib.Path("chapters/Assignments/A1_Diversification_and_Sorts_AI.ipynb")
json.dump(nb, open(out,'w'), indent=1, ensure_ascii=False); open(out,'a').write("\n")
print(f"✅ {out}  —  {len(C)} cells")
