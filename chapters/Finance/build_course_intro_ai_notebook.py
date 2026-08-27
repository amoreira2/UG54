"""
Build CourseIntro_AI.ipynb — Lecture 1 of UG54 (Spring 2026).

This is the very first class. Goals:
  1. Establish course mechanics (5 min in person)
  2. Pitch the AI shift and the new skill (10 min)
  3. Introduce Specify → Implement → Validate (10 min)
  4. Hands-on Colab + Gemini setup (15 min)
  5. First taste: "How much would $1000 of [stock] be worth today?" (25 min)
  6. Preview next class + assignment 1 (10 min)
"""

import json
from pathlib import Path

OUT = Path(__file__).parent / "CourseIntro_AI.ipynb"


def md(text):
    return {"cell_type": "markdown", "metadata": {},
            "source": text.splitlines(keepends=True)}


def code(text):
    return {"cell_type": "code", "execution_count": None, "metadata": {},
            "outputs": [], "source": text.splitlines(keepends=True)}


cells = []

# ─── Title ────────────────────────────────────────────────────────────
cells.append(md("""# Welcome to UG54 — Data-Driven Investing with Python (AI Edition)
## Spring 2026 — Prof. Alan Moreira

---

> *"It is a capital mistake to theorize before one has data."*
> — Sherlock Holmes

This is the **first class.** By the end of these 75 minutes you will:

1. Know how this course is graded and what's expected of you
2. Understand why we're running it differently than any UG54 before
3. Have a working Colab + AI setup on your laptop
4. Have used AI to answer a real finance question — and audited its answer"""))

# ─── TOC ──────────────────────────────────────────────────────────────
cells.append(md("""## 📋 Today's Plan

1. [Course mechanics](#mechanics) — what to expect (5 min)
2. [Why this course, why now](#why) — the AI shift in finance (10 min)
3. [The new workflow: Specify → Implement → Validate](#workflow) (10 min)
4. [Hands-on: Colab + Gemini setup](#setup) (15 min)
5. [Your first AI-assisted analysis](#hands-on) (25 min)
6. [What's next + Assignment 1](#next) (10 min)"""))

# ─── 1. Mechanics ─────────────────────────────────────────────────────
cells.append(md("""---

## 1. Course Mechanics <a id="mechanics"></a>

### What we'll do
You'll learn how professional investors analyze data: factor models, portfolio construction, performance evaluation, machine learning, and LLMs in finance. We do it all in Python in Colab, with AI assistance.

### How you'll be graded

| Component | Weight |
|---|---|
| Assignments (7, completion-only) | 20% |
| Midterm (in class, March 11) | 10–20% |
| Final exam (cumulative) | 25–35% |
| Final project (group, presented in April) | 20% |
| Class attendance + participation | 15% |

The midterm/final weights flex automatically in your favor — bad day on one, the other carries more weight.

### Assignments
- 7 of them, group of 3 OK, **submit your own copy**
- Completion-only grading: if it runs and looks like you tried, you get full credit
- **Late = zero.** You can drop one — only 6/7 needed for full score
- Submission via a **Google Form** I'll show you today. **No more file uploads.**

### AI policy
**You are encouraged to use AI** (Gemini in Colab, ChatGPT, Claude). This course is built around it.

**But:** if you submit work where you couldn't explain what the code does, that's a problem. The skill we're teaching is *directing* AI and *auditing* its output — not blindly trusting it.

### Class conduct
- Bring your laptop. Charged.
- **Don't post pictures/video of class to social media** (FERPA).
- Name cards for the first month so I learn names."""))

# ─── 2. Why this course, why now ──────────────────────────────────────
cells.append(md("""---

## 2. Why This Course, Why Now <a id="why"></a>

### The old finance workflow

For 30 years, the job of a junior analyst at a quant fund looked like:

> *"Pull the data, write the regression, format the output, sanity-check, present to PM."*

**60% of the work was writing code.** Knowing `pd.merge()` syntax, remembering whether RF was in percent or decimal, formatting tables — that's what you got paid for in your first year.

### What changed in 2024–2025

AI now writes that code in seconds. Gemini, Copilot, ChatGPT — pick your tool. They generate plausible-looking pandas / statsmodels / sklearn code on demand.

**This is good news.** The annoying part of the job is automated.

**But it changes what you actually need to be good at:**

| Old skill | New skill |
|-----------|-----------|
| Remember the API | Specify what you want precisely |
| Write the regression | Audit the regression for silent bugs |
| Format the output | Interpret the output and decide |
| Be fast at typing | Be sharp at judgment |

> **💡 Key Insight**
>
> In an AI-assisted workflow, **your value comes from the spec, the audit, and the interpretation** — not from the typing. This course is structured around exactly that shift.

### What this means for you in the job market

Funds are already triaging junior hires on a different test: can you spot when a model is wrong? Can you write a one-paragraph memo that drives a decision? Can you tell a CIO why the AI's answer is misleading?

This class trains all three."""))

# ─── 3. The new workflow ──────────────────────────────────────────────
cells.append(md("""---

## 3. The New Workflow: Specify → Implement → Validate <a id="workflow"></a>

We'll use this framework in every lecture.

| Step | What you do | Why it matters | Who does the work |
|------|------------|----------------|-------------------|
| **1. Specify** | Write a precise English description of what you want | Closes the door on silent assumptions (units, frequency, edge cases) | **You** |
| **2. Implement** | Generate the code — AI or yourself | Syntax is cheap. | **AI** (mostly) |
| **3. Validate** | Apply a domain-specific checklist; sanity-check outputs | This is where the bugs hide. | **You** |

### A bad spec produces buggy code, every time

The same task, three prompts:

> 🔴 **Vague:** *"Compute the Sharpe ratio of SPY."*
> ⚠️ Will silently pick a frequency, may use total instead of excess returns, will annualize differently each time you run it.

> 🟡 **Better:** *"Compute the annualized Sharpe ratio of SPY using daily data."*
> ⚠️ Still doesn't specify excess vs total, doesn't say what to do with NaN.

> 🟢 **Precise:** *"Using daily SPY total returns from 2010-01-01 to 2024-12-31, subtract the daily risk-free rate from FRED to get excess returns. Compute the annualized Sharpe ratio as `mean(excess) / std(excess) × √252`. Drop NaN rows before computing."*

**Same task. Different reliability.** Writing precise specs is the habit we'll practice all semester.

### Every lecture has a pitfall checklist

Each topic comes with a list of bugs AI will silently produce. Examples you'll see in the next 5 weeks:

- Risk-free rate in percent instead of decimal → Sharpe is 100× off
- Regression without intercept → α is forced to zero
- Rolling beta using future data → backtest looks great, live trade blows up
- Persistence not tested → "alpha" was a regime, not skill

Keep these checklists handy when you're working on an assignment."""))

# ─── 4. Setup ─────────────────────────────────────────────────────────
cells.append(md("""---

## 4. Hands-on: Colab + Gemini Setup <a id="setup"></a>

> **🛠️ Do this now** — I'll walk you through it.

### Step 1 — Open Colab
Go to **colab.research.google.com** and sign in with your **NYU Google account**.

### Step 2 — Open this notebook
You're already looking at it. (If you copied this from Brightspace, click **File → Save a Copy in Drive** so your edits persist.)

### Step 3 — Turn on Gemini
- Click the **✨ sparkle icon** in the right sidebar (or **Tools → Gemini**)
- If prompted, accept the Gemini terms
- A panel opens on the right where you can chat

### Step 4 — Verify the setup works

Run the cell below. If it prints "Setup works ✓" then everything is wired up."""))

cells.append(code("""# Verify setup
import sys, pandas as pd, numpy as np
print(f"Python:      {sys.version.split()[0]}")
print(f"pandas:      {pd.__version__}")
print(f"numpy:       {np.__version__}")
print("\\nSetup works ✓")"""))

cells.append(md("""### Step 5 — Confirm Gemini sees your notebook

In the Gemini panel, type:

> *"What variables are defined in this notebook right now?"*

It should be able to answer. If it can't, raise your hand."""))

# ─── 5. Hands-on AI exercise ──────────────────────────────────────────
cells.append(md("""---

## 5. Your First AI-Assisted Analysis <a id="hands-on"></a>

### The question

> **Suppose your parents had bought $1,000 of one stock on the day you were born. What would it be worth today?**

Pick a stock you know. AAPL if you were born after 1990. MSFT, KO, JPM, NVDA — anyone with a long-enough public history.

### Step 1 — Specify

Before touching code, write a precise specification. Edit the cell below:

```
STOCK:      AAPL
BIRTH_DATE: 2005-09-14   ← your actual birth date
END_DATE:   2025-01-31   ← today (or pick a date)
INVESTMENT: $1000
QUESTION:   What is the cumulative total return (including dividends),
            and what would $1000 grow to over this period?
```

**Things your spec might silently miss:**
- Should the return include dividends? (Yes — total return, not price return.)
- What if the stock hadn't IPO'd yet on your birth date? (Pick the first trading day.)
- What about stock splits? (Adjusted close handles this automatically.)
- What currency? (USD — for now.)"""))

cells.append(md("""**Your specification — edit this cell:**

```
STOCK:      ____
BIRTH_DATE: ____
END_DATE:   ____
INVESTMENT: $1000
QUESTION:   What is the cumulative total return, and what would $1000 grow to?
```"""))

cells.append(md("""### Step 2 — Implement

Copy your spec above into Gemini. Try this prompt as a starting point:

> *"Using yfinance, download adjusted-close daily data for [STOCK] from [BIRTH_DATE] to [END_DATE]. Compute the total cumulative return assuming a $1000 investment at the first close and reinvested dividends. Plot the growth of $1000 over the period. Print the final value."*

Run whatever Gemini gives you in the cell below.

> **🐍 Python Insight: `yfinance`**
>
> A free library that pulls historical stock prices from Yahoo Finance. Install it in Colab with `!pip install yfinance` if needed. The 'Adj Close' column already accounts for splits and dividends — that's why it's the right column for total return.

> **⚠️ AI will probably:**
> - Forget to install yfinance the first time
> - Use 'Close' instead of 'Adj Close' (miss dividends)
> - Use the wrong column names if Yahoo updates its API
>
> Be ready to fix."""))

cells.append(code("""# Paste / run AI-generated code here

"""))

cells.append(md("""### Step 3 — Validate

Before you trust the answer, audit it. Walk through this checklist:

| Check | Why | How |
|-------|-----|-----|
| **Did it use `Adj Close`?** | 'Close' ignores splits & dividends — answer will be wrong | Read the code; look for `'Adj Close'` or `auto_adjust=True` |
| **Is the start date right?** | Off-by-one or wrong-day errors are easy | Check the printed first date matches your spec |
| **Is the final number plausible?** | Sanity test against rough rule of thumb | $1000 → $5–$30k over 20 years is typical for a major stock |
| **Did it handle non-trading days?** | yfinance skips weekends/holidays automatically — but verify | Index should have ~252 days per year |
| **Did dividends get reinvested?** | The point of total return | `Adj Close` does this implicitly |

> **🤔 Cold-call question** *(I'll ask one of you):*
>
> If your stock returned, say, 4000% over 20 years, what's the annualized return? *(Hint: $(40)^{1/20} - 1$.)* And — does that beat the market over the same period?

### Compare with your neighbor

- Did you both pick the same stock? Different answers? Why?
- If you picked different stocks, who would have done better?
- Was the answer surprising? What does that tell you about stock-picking?"""))

# ─── 6. What's next ───────────────────────────────────────────────────
cells.append(md("""---

## 6. What's Next <a id="next"></a>

### Wednesday (Lecture 2): Asset Returns — properly

Today we computed *a* return. Wednesday we'll cover:
- Total return vs price return vs excess return — what's the difference, when does it matter
- Annualization rules (mean × N, vol × √N)
- The risk-free rate and the **risk premium**
- The **Sharpe ratio** — why it determines optimal portfolio weights
- A new pitfall checklist (this time for returns)
- A challenge similar to today's, but harder

### Assignment 1 — due next Monday (Jan 26)

Posted on Brightspace. It's a single notebook: extend today's "stock since you were born" analysis with:
1. Three stocks instead of one (your pick)
2. Compute their **annualized** returns
3. Plot all three cumulative growth lines on one chart
4. Compute the correlation matrix of their daily returns
5. Submit via the Google Form (link in Brightspace)

The submission cell at the bottom of your notebook will bundle everything into one line for you. Just paste that line into the form.

### Reading
- Class book Ch. 4 (Returns) — skim before Wednesday
- Math notes Ch. 1 (review of stats) — review before Friday's class

### Office hours
- Posted on Brightspace
- **Don't email me the night before an assignment is due** asking how to do the assignment. I won't respond. Plan ahead."""))

cells.append(md("""---

## 🧠 Today's Key Takeaways

1. **AI changes what you need to be good at.** The skill is the spec, the audit, and the interpretation. Not the typing.

2. **Every analysis follows the same loop:** Specify → Implement → Validate.

3. **Each topic has an audit checklist** of silent bugs AI tends to produce. Use them when you're working on an assignment.

4. **Use AI freely.** But never trust output you can't explain.

5. **Get setup working today.** If your Colab or Gemini isn't working by end of class, raise your hand. We fix it now, not the night before Assignment 1.

---

### See you Wednesday."""))

# ─── Write notebook ───────────────────────────────────────────────────
notebook = {
    "cells": cells,
    "metadata": {
        "colab": {"provenance": [], "toc_visible": True},
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python"},
    },
    "nbformat": 4, "nbformat_minor": 5,
}
OUT.write_text(json.dumps(notebook, indent=1))
print(f"✅ Wrote {OUT} ({len(cells)} cells)")
