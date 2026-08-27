"""
Build L1_Welcome_Returns_AI.ipynb — Lecture 1, Wed Sep 2 2026.

Merges two existing notebooks into one 75-minute class:
    CourseIntro_AI.ipynb      (mechanics, the AI shift, Specify/Implement/Validate)
    IntrotoReturns_c_AI.ipynb (returns, excess returns, Sharpe)

CUT relative to the sources (moved to appendix or dropped):
  - exact groupby calendar-year aggregation  (approximation vs exact comparison)
  - cumulative-wealth plot
  - rolling Sharpe / rolling() vs for-loop section
  - Exercises 1-3 with <details> solutions
  - the old SPY calendar-year challenge (replaced; see below)

KEPT and merged:
  - the "stock since you were born" hands-on -> becomes Live Demo 1
  - the RF-units detective work (core pitfall)
  - excess returns as self-financed long-short  (seeds L3)

CHALLENGE (auto-graded, everyone same data):
  General Electric (permno 12060) vs the market, 1980-2000, from the course panel.
  Verified against the built panel + Ken French monthly factors:
      ge_total_return  84.43   (i.e. +8443%)
      ge_ann_excess    0.1713
      ge_ann_vol       0.2216
      ge_sharpe        0.773
      mkt_sharpe       0.601
  GE beat the market on Sharpe over 20 years -- but its vol is 22% vs the
  market's 16%. The memo asks whether that proves skill, which is exactly the
  question L4 (factor models) answers. Do not resolve it here.
"""

import json
from pathlib import Path

OUT = Path(__file__).parent / "L1_Welcome_Returns_AI.ipynb"
RAW = ("https://raw.githubusercontent.com/amoreira2/UG54/refs/heads/main/"
       "assets/data/panel_backbone_1980_2000.parquet")


def md(t): return {"cell_type": "markdown", "metadata": {}, "source": t.splitlines(keepends=True)}
def code(t): return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": t.splitlines(keepends=True)}


cells = []

cells.append(md("""# Welcome to UG54 — Data-Driven Investing
## Lecture 1: The Workflow, and What a Return Is

## 🎯 Learning Objectives

By the end of today you will be able to:

1. **Explain how AI changes the job** — and what is left that is actually hard
2. **Write a precise specification** before asking an AI for code, and audit what comes back
3. **Compute a return correctly** — total vs price, and why dividends are not optional
4. **Convert to excess returns** without falling into the units trap that breaks a Sharpe ratio by 100×
5. **Read a Sharpe ratio** and say what it does and does not tell you about skill"""))

cells.append(md("""## 📋 Today's Plan

1. [Course mechanics](#mechanics) — how this class works (5 min)
2. [Why this course, why now](#why) — the AI shift (8 min)
3. [Specify → Implement → Validate](#workflow) (8 min)
4. [Setup: Colab + Gemini](#setup) (7 min)
5. [What is a return?](#returns) (10 min)
6. [Pitfall checklist](#pitfalls) (3 min)
7. [🔄 Live Demo: your stock since you were born](#demo) (12 min)
8. [Excess returns and the units trap](#excess) (8 min)
9. [The Sharpe ratio](#sharpe) (4 min)
10. [🎯 Challenge: GE vs the market](#challenge) (8 min, finish at home)
11. [Key takeaways](#takeaways) (2 min)

> **📌 Day-one note.** The challenge is *started* in class and finished at home
> — it's due before Lecture 2. Setup always runs long on the first day, and
> you don't have groups yet."""))

cells.append(md("---\n\n## 🛠️ Setup <a id=\"setup-cell\"></a>"))

cells.append(code("""#@title Setup — run this first
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
%matplotlib inline
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = [11, 4.5]
plt.rcParams['font.size'] = 11
import warnings; warnings.filterwarnings('ignore')

print("✅ Setup works — you're ready")"""))

# ─── 1. Mechanics ─────────────────────────────────────────────────────
cells.append(md("""---

## 1. How This Class Works <a id="mechanics"></a>

### What you'll actually do

You will build a **real trading strategy** and spend the semester finding out
whether it works. Not a case study — an actual signal, applied to 20 years of
US stock data, tested the way a quant fund would test it.

Most of you will find that your strategy does **not** work. That is the correct
outcome for most strategies, and a project that establishes it honestly is a
good project.

### Grading

| Component | Weight |
|---|---|
| Assignments (7, completion-only) | 20% |
| Midterm | 10–20% |
| Final exam | 25–35% |
| Final project (group) | 20% |
| Attendance + participation | 15% |

Midterm/final weights flex in your favour — a bad day on one means the other
carries more.

### Two kinds of work

| | What | Graded |
|---|---|---|
| **In class** | A short challenge at the end of most lectures. Everyone works with the same data, so there's a right answer. | Auto-graded |
| **Assignments** | The same technique applied to **your group's own strategy**. | Completion |

- **Groups of 3**, formed by next class. Submit your own copy.
- 7 assignments, **drop one** — only 6 count. Late = zero.
- Two 5-minute project pitches to the class (Oct 7, Nov 18), then final
  presentations in December.

### AI policy

**Use AI. Actively.** Gemini in Colab, ChatGPT, Claude — this course is built
around it.

**But:** if you submit work you cannot explain, that's a problem. I will
cold-call you to walk through a decision — why this approach, what alternatives
you considered, why you rejected them. A large part of what I'm assessing is
the explanation, not the code.

### Logistics

- Bring your laptop, charged.
- **WRDS account signup starts today** — you'll need it for one assignment later.
- No photos or video of class (FERPA)."""))

# ─── 2. Why now ───────────────────────────────────────────────────────
cells.append(md("""---

## 2. Why This Course, Why Now <a id="why"></a>

### The old workflow

For thirty years, the first year of a junior quant job looked like:

> *"Pull the data, write the regression, format the output, sanity-check, hand to the PM."*

**Roughly 60% of that was writing code.** Remembering `pd.merge()` syntax,
recalling whether the risk-free rate came in percent or decimal, formatting
tables. That was the job.

### What changed

AI writes that code now, in seconds, on demand. This is good news — the tedious
part is automated. But it moves where your value comes from:

| Old skill | New skill |
|-----------|-----------|
| Remember the API | **Specify** what you want precisely |
| Write the regression | **Audit** it for silent bugs |
| Format the output | **Interpret** it and decide |
| Be fast at typing | Be sharp at **judgment** |

> **💡 Key Insight**
>
> AI-generated code usually *runs*. That is the problem. Code that crashes tells
> you it's wrong; code that returns a plausible number does not. The skill this
> course builds is catching the second kind.

### The uncomfortable part

Everyone in this room has the same AI. So does everyone applying for the same
job. What differentiates you is whether you can tell when the output is wrong,
and whether you can explain why to someone who has to make a decision."""))

# ─── 3. The workflow ──────────────────────────────────────────────────
cells.append(md(r"""---

## 3. Specify → Implement → Validate <a id="workflow"></a>

Every analysis in this course follows the same three steps.

| Step | What you do | Who does the work |
|------|------------|-------------------|
| **1. Specify** | Write a precise English description of what you want | **You** |
| **2. Implement** | Generate the code | **AI**, mostly |
| **3. Validate** | Apply a domain-specific checklist; sanity-check the output | **You** |

### A bad spec produces buggy code, every time

Same task, three prompts:

> 🔴 **Vague:** *"Compute the Sharpe ratio of SPY."*
>
> Will silently pick a frequency, may use total instead of excess returns, and
> will annualize differently each time you run it.

> 🟡 **Better:** *"Compute the annualized Sharpe ratio of SPY using daily data."*
>
> Still doesn't say excess vs total, still doesn't say what to do with missing days.

> 🟢 **Precise:** *"Using daily SPY total returns from 1993-01-01 to 2024-12-31,
> subtract the daily risk-free rate from Ken French to get excess returns.
> Compute the annualized Sharpe ratio as mean(excess)/std(excess) × √252. Drop
> rows with missing values before computing."*

Same task. Completely different reliability.

> **🤖 AI-Era Insight**
>
> The vague prompt doesn't fail loudly. It returns a number. You will get
> something like 0.61, and it looks fine, and you have no way to know it used
> total returns instead of excess and is therefore wrong by about 40%."""))

# ─── 4. Setup ─────────────────────────────────────────────────────────
cells.append(md("""---

## 4. Setup: Colab + Gemini <a id="setup"></a>

> **🛠️ Do this now — I'll walk through it.**

1. **Open in Colab** — click the rocket icon at the top of this notebook
2. **Save your own copy** — File → Save a Copy in Drive, so your edits persist
3. **Turn on Gemini** — click the ✨ sparkle icon in the right sidebar
   (or Tools → Gemini) and accept the terms
4. **Verify** — run the setup cell above. If it printed "Setup works", you're set.

> **📌 If anything here doesn't work, raise your hand now.** Not the night
> before the first assignment."""))

# ─── 5. Returns ───────────────────────────────────────────────────────
cells.append(md(r"""---

## 5. What Is a Return? <a id="returns"></a>

### Why returns and not prices

A share of Berkshire costs about \$700,000. A share of Ford costs about \$11.
That tells you nothing about which was the better investment. Prices aren't
comparable across stocks; **returns are**.

$$r_t = \frac{P_t - P_{t-1} + D_t}{P_{t-1}}$$

| Symbol | Meaning |
|--------|---------|
| $P_t$ | Price at the end of period $t$ |
| $D_t$ | Any dividend paid during period $t$ |
| $r_t$ | The **total return** — what you actually earned |

### Total return vs price return

Drop the $D_t$ and you get the **price return**, which is not what you earned.
Over long horizons this is not a rounding error: dividends have historically
been roughly a third of total US equity returns. Over 20 years, ignoring them
can understate your result by 50% or more.

> **⚠️ Caution: this is the single most common silent bug in AI-generated code**
>
> Ask for "returns" and you may get price returns. In `yfinance`, the `Close`
> column is a price; `Adj Close` (or `auto_adjust=True`) reflects dividends and
> splits. In CRSP, `ret` is the total return and `retx` excludes dividends.
> Nothing errors either way.

### Compounding

Returns chain multiplicatively, not additively:

$$1 + R_{0\to T} = \prod_{t=1}^{T}(1 + r_t)$$

A stock that falls 50% then rises 50% has *not* broken even — it's down 25%."""))

# ─── Pitfall checklist ────────────────────────────────────────────────
cells.append(md("""---

## 🛡️ Pitfall Checklist for Returns <a id="pitfalls"></a>

Use this every time an AI hands you return code.

| | Pitfall | What goes wrong | 🔍 How to detect |
|---|---|---|---|
| 1 | **Price returns instead of total returns** | Dividends silently dropped; long-horizon results far too low | Did it use `Adj Close` / `ret`, not `Close` / `retx`? |
| 2 | **Risk-free rate in percent, returns in decimal** | Excess returns and Sharpe off by ~100× | Print `rf.mean()`. Is it 0.004 or 0.4? |
| 3 | **Total instead of excess returns in a Sharpe** | Sharpe overstated, badly, in high-rate periods | Was anything subtracted at all? |
| 4 | **Adding returns instead of compounding** | Wrong cumulative return; error grows with horizon | Use `(1+r).prod()-1`, not `r.sum()` |
| 5 | **Wrong annualization factor** | 12 vs 252 vs 52 — silently wrong by √21 | Does the factor match the data frequency? |
| 6 | **Survivorship: only stocks that still exist** | Returns biased upward; the failures are missing | Does the data include delisted firms? |

> **🤖 AI-Era Insight**
>
> Every one of these produces a number. None throws an error. Pitfall 2 is the
> one that bites hardest — a Sharpe ratio of 43 instead of 0.43 looks obviously
> wrong, but 0.43 instead of 0.0043 does not."""))

# ─── Live Demo ────────────────────────────────────────────────────────
cells.append(md("""---

## 🔄 Live Demo: Your Stock Since You Were Born <a id="demo"></a>

> **The question:** if your parents had put \\$1,000 into one stock on the day
> you were born, what would it be worth now?

Pick a company you know that was public when you were born — AAPL, MSFT, KO,
JPM, WMT, DIS.

### Step 1 — Specify

Fill this in before touching any code."""))

cells.append(code("""# === EDIT THIS CELL — your specification ===
STOCK      = "AAPL"        # ← your pick
BIRTH_DATE = "2005-09-14"  # ← your actual birth date
END_DATE   = "2025-01-31"
INVESTMENT = 1000

print(f"${INVESTMENT:,} in {STOCK} from {BIRTH_DATE} to {END_DATE}")"""))

cells.append(md("""**What might your spec silently miss?**

- Should the return include dividends? *(If you didn't say, you don't know what you'll get.)*
- What if the stock hadn't IPO'd yet on your birth date?
- What about stock splits?

### Step 2 — Implement

> **🤖 AI prompt** *(paste into Gemini, then edit):*
>
> *"Using yfinance, download daily data for {STOCK} from {BIRTH_DATE} to
> {END_DATE} with auto_adjust=True so prices reflect dividends and splits.
> Compute the total cumulative return and the final value of a $1,000
> investment made at the first close. Print both, and plot the growth of
> $1,000 over the period."*"""))

cells.append(code("""# Paste and run Gemini's code here
"""))

cells.append(md("""### Step 3 — Validate

Do not trust the number until you've walked this.

| Check | Why it matters | How |
|---|---|---|
| **Did it adjust for dividends?** | Otherwise you're missing a third of the return | Look for `auto_adjust=True` or `Adj Close` |
| **Does the start date match?** | Off-by-one and "market was closed" errors are easy | Print the first date in the data |
| **Is the magnitude plausible?** | Rough sanity bound | \\$1,000 → \\$5k–\\$40k over 20 years is normal for a large US stock |
| **Did it compound, not sum?** | Summing returns is wrong and the error grows | Look for `.prod()` or `cumprod()`, not `.sum()` |

> **🤔 Compare with your neighbour**
>
> Different stocks? Different answers? Who would have done better — and could
> either of you have known that in advance? Hold onto that question; it's most
> of the course."""))

# ─── 6. Excess returns ────────────────────────────────────────────────
cells.append(md(r"""---

## 6. Excess Returns and the Units Trap <a id="excess"></a>

You could always have earned the risk-free rate by holding Treasury bills. So
the return that reflects the *risk you took* is the **excess return**:

$$r^e_t = r_t - r^f_t$$

Everything in this course — Sharpe ratios, factor models, alphas — is built on
excess returns, not raw returns.

### The trap

The risk-free rate arrives from different sources in different units. Ken
French's data library serves factors in **percent** (so 0.42 means 0.42%, i.e.
0.0042). Your stock returns are usually in **decimal**. Subtract one from the
other without checking and every downstream number is wrong by a factor of 100.

> **📌 Remember: always print the mean before you subtract.**
>
> A monthly risk-free rate should be roughly **0.003 to 0.005** in decimal
> (about 4%/year). If you see 0.4, you're in percent. If you see 0.00004,
> something else is wrong."""))

cells.append(code("""# Load Fama-French monthly factors (this is where the risk-free rate comes from)
import pandas_datareader.data as web

ff = web.DataReader('F-F_Research_Data_Factors', 'famafrench', start='1980-01-01')[0]
ff.index = pd.to_datetime(ff.index.to_timestamp()) + pd.offsets.MonthEnd(0)

print("RAW, straight from Ken French:")
print(ff[['Mkt-RF', 'RF']].head(3).to_string())
print(f"\\n  mean RF = {ff['RF'].mean():.4f}   ← too big for a monthly decimal rate")
print("  → these are PERCENT. Divide by 100.\\n")

ff = ff / 100
print(f"After /100:  mean RF = {ff['RF'].mean():.5f}  ({ff['RF'].mean()*12:.2%} per year) ✅")"""))

cells.append(md(r"""### Excess returns are long-short strategies

This is worth sitting with, because we'll build on it in Lecture 3.

When you compute $r^e = r - r^f$, you are describing an actual trading
position: **borrow at the risk-free rate, buy the stock.** You put up no money
of your own — the long and the short cancel.

> **💡 Key Insight**
>
> A portfolio whose weights sum to **zero** is *self-financed*. It costs nothing
> to enter, so its return is pure spread, not a return on capital. Every
> long-short strategy in this course is one of these, starting with the excess
> return you just computed."""))

# ─── 7. Sharpe ────────────────────────────────────────────────────────
cells.append(md(r"""---

## 7. The Sharpe Ratio <a id="sharpe"></a>

Return alone is not a measure of quality — you can always get more return by
taking more risk, or by borrowing. The Sharpe ratio prices return **per unit of
volatility**:

$$SR = \frac{\text{mean}(r^e)}{\text{sd}(r^e)}$$

Annualize by multiplying the mean by the number of periods per year and the
standard deviation by its square root:

$$SR_{\text{annual}} = \frac{\bar r^e \times 12}{\text{sd}(r^e) \times \sqrt{12}}
= SR_{\text{monthly}} \times \sqrt{12}$$

> **📌 Remember: rough benchmarks (annualized)**
>
> | Sharpe | Read as |
> |---|---|
> | ~0.4 | The US stock market, long run |
> | 0.5–0.8 | A good active strategy |
> | 1.0+ | Excellent — and worth checking for a bug |
> | 2.0+ | Almost certainly a bug, look-ahead, or ignored costs |

> **⚠️ Caution**
>
> A high Sharpe is not the same as skill. A strategy with twice the market's
> volatility and twice its return has the *same* Sharpe as the market and has
> added nothing. Working out what counts as skill is Lecture 4."""))

# ─── Challenge ────────────────────────────────────────────────────────
cells.append(md("""---

## 🎯 Challenge: General Electric vs the Market <a id="challenge"></a>

From 1980 to 2000, Jack Welch ran General Electric and it was the most admired
company in America. Let's check the record.

You'll use **the course panel** — the dataset you'll work with all semester.
It's US stock returns, monthly, 1980–2000, straight from CRSP."""))

cells.append(code(f"""# The course panel — monthly US stock returns, 1980-2000
URL = ("{RAW}")
panel = pd.read_parquet(URL)

print(f"{{len(panel):,}} rows | {{panel.permno.nunique():,}} stocks | "
      f"{{panel.date.nunique()}} months")
print(f"{{panel.date.min().date()}} to {{panel.date.max().date()}}")
print("\\ncolumns:", list(panel.columns))
panel.head(3)"""))

cells.append(md("""> **🐍 Python Insight: `permno`**
>
> CRSP identifies a company by a permanent number, not a ticker. Tickers get
> reused — when a company dies, its ticker can be reassigned to something else
> entirely. `permno` never changes and never gets recycled. **General Electric
> is permno 12060.**

### Q1 — GE's total return

Pull GE's monthly returns from the panel over the full sample and compound them
into a single cumulative total return.

> **📌 Required variable names:**
> ```python
> ge_total_return = ____   # cumulative return, e.g. 3.5 means +350%
> ```"""))

cells.append(code("""# Your work here


# Required output — fill this in:
ge_total_return = ____

print(f"GE total return, 1980-2000: {ge_total_return:.1%}")
print(f"$1,000 would have become: ${1000*(1+ge_total_return):,.0f}")"""))

cells.append(md("""### Q2 — Excess return, volatility, Sharpe

Merge in the risk-free rate from `ff` (already loaded and already divided by
100). Compute GE's **annualized** mean excess return, **annualized** volatility,
and Sharpe ratio.

> **⚠️ Check pitfall 2 before you start.** Are both series in decimal?
>
> **📌 Required variable names:**
> ```python
> ge_ann_excess = ____   # annualized mean excess return, e.g. 0.12
> ge_ann_vol    = ____   # annualized volatility
> ge_sharpe     = ____   # annualized Sharpe ratio
> ```"""))

cells.append(code("""# Your work here


# Required outputs — fill these in:
ge_ann_excess = ____
ge_ann_vol    = ____
ge_sharpe     = ____

print(f"GE:  excess {ge_ann_excess:6.2%}/yr   vol {ge_ann_vol:6.2%}   Sharpe {ge_sharpe:.3f}")"""))

cells.append(md("""### Q3 — The benchmark

Compute the same annualized Sharpe ratio for **the market** over the identical
period, using the `Mkt-RF` column in `ff` (already an excess return — nothing to
subtract).

> **📌 Required variable name:**
> ```python
> mkt_sharpe = ____
> ```"""))

cells.append(code("""# Your work here


# Required output — fill this in:
mkt_sharpe = ____

print(f"Market Sharpe: {mkt_sharpe:.3f}")
print(f"GE Sharpe:     {ge_sharpe:.3f}")"""))

cells.append(md("""### Q4 — The memo

GE's Sharpe ratio beat the market's over twenty years.

> **📝 Your task — maximum 5 sentences**
>
> Does that prove Jack Welch was an exceptional manager? Compare GE's volatility
> to the market's before you answer, and say what *else* you would need to know
> to make the case either way.
>
> There is no single right answer here. I'm looking for whether you notice the
> problem."""))

cells.append(code('''MEMO = """
Write your memo here. Don't delete the surrounding triple quotes.
"""
print(MEMO)
print(f"\\nSentences: ~{MEMO.count('.')}")'''))

# ─── Submission ───────────────────────────────────────────────────────
cells.append(md("""---

## 📤 Submission <a id="submit"></a>"""))

cells.append(code('''# === 📤 SUBMISSION CELL — Run this last ===
import json, base64, hashlib, datetime as dt

required = ["ge_total_return", "ge_ann_excess", "ge_ann_vol",
            "ge_sharpe", "mkt_sharpe", "MEMO"]
missing = [v for v in required if v not in dir()]
if missing:
    raise NameError(f"\\n❌ Missing before submission: {missing}")

payload = {
    "assignment": "L1_Returns_AI",
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
print(f"\\nLength: {len(token)} chars")
print("Submission form: https://forms.gle/YOUR_FORM_LINK_HERE")'''))

# ─── Takeaways ────────────────────────────────────────────────────────
cells.append(md("""---

## 🧠 Key Takeaways <a id="takeaways"></a>

1. **AI writes the code; you own the spec, the audit, and the interpretation.**
   That's the whole shape of this course.

2. **Code that runs is not code that's right.** Every pitfall on today's
   checklist returns a plausible number and throws no error.

3. **Total return, not price return.** Dividends are roughly a third of long-run
   US equity returns.

4. **Print the mean of the risk-free rate before you subtract it.** Percent vs
   decimal is the single most common way a Sharpe ratio ends up 100× wrong.

5. **Compound returns, don't add them.** `(1+r).prod()-1`.

6. **An excess return is a self-financed long-short position** — weights summing
   to zero. Every strategy we build from Lecture 3 onward is one of these.

7. **A high Sharpe is not proof of skill.** GE beat the market's Sharpe over
   twenty years with 40% more volatility. Whether that's skill is Lecture 4.

---

### Before Wednesday

- **Form your group of 3** and email me the names.
- **Start your WRDS account signup** — you'll need it later in the term.
- Next class: where this data actually comes from, and how to turn a pile of
  stock returns into a portfolio."""))

# ─── Appendix ─────────────────────────────────────────────────────────
cells.append(md("""---

## 📎 Appendix — Belt-and-Suspenders Data Loading <a id="appendix"></a>"""))

cells.append(code(f'''# ═══════════════════════════════════════════════════════════════════════
# 📎 APPENDIX — where today's data comes from
# ═══════════════════════════════════════════════════════════════════════

# ─── 1. The course panel ───────────────────────────────────────────────
# Built once from CRSP by chapters/Finance/build_course_panel.py, with
# delisting returns merged in. Loaded from the repo, so no WRDS needed:
#     panel = pd.read_parquet("{RAW}")
#
# Column note: `ret` is the return DURING the month. `ret_fwd` is the return
# over the FOLLOWING month -- the one you earn by acting on information you
# had at the end of this month. Using the wrong one is look-ahead bias.
# We'll use `ret_fwd` heavily starting in Lecture 3.

# ─── 2. Fama-French factors: live fetch ────────────────────────────────
# Prompt: "Using pandas-datareader, fetch F-F_Research_Data_Factors monthly
#  from the famafrench source starting 1980. Convert the PeriodIndex to
#  month-end timestamps and divide by 100 to get decimals."
def fetch_ff_monthly():
    import pandas_datareader.data as web
    f = web.DataReader('F-F_Research_Data_Factors', 'famafrench', start='1980-01-01')[0]
    f.index = pd.to_datetime(f.index.to_timestamp()) + pd.offsets.MonthEnd(0)
    return f / 100

# ─── 3. Backup path if Ken French is unreachable ───────────────────────
# ff_backup = pd.read_csv(
#     "https://raw.githubusercontent.com/amoreira2/UG54/refs/heads/main/"
#     "assets/data/ff_monthly.csv", index_col=0, parse_dates=True)
'''))

notebook = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.11"},
        "colab": {"provenance": []},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

OUT.write_text(json.dumps(notebook, indent=1))
print(f"✅ Wrote {OUT}  ({len(cells)} cells)")
