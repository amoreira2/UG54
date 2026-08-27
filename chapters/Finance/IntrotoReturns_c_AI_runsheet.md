# Asset Returns I — In-Class Run Sheet

**Notebook:** `IntrotoReturns_c_AI.ipynb` (existing, 50 cells)
**Duration:** 75 min
**Pre-class state:** Students completed Lecture 1 (Course Intro). They've used Colab + Gemini once. They know about Specify → Implement → Validate.
**In-class scope:** Cells 0-33 + cell 49 (Key Takeaways). **Cells 34-48 (the 4 exercises) are assignment material — NOT in class.**

---

## 🎬 Cold open (3 min) — 0:00

> "On Monday we ran an AI prompt that told us $1000 of [your stock] would be
> worth $X today. Today we get serious about that number.
>
> **What exactly is a return?** What's the difference between the 'return' your
> broker shows you and the 'excess return' that hedge fund people obsess about?
> Why do statisticians care about whether returns are 'arithmetic' or 'log'?
> And how do you compute a Sharpe ratio without making the four most common
> mistakes that AI loves to make?
>
> All of that, in the next 75 minutes."

---

## 1️⃣ Total returns (10 min) — 0:03

**Notebook cells:** 3-13 (returns concept + pitfall checklist + Specify→Implement→Validate demo).

**Run the setup cell (3).** Then walk through the total-return formula (cell 4-5).

**Drive home the four properties of returns (cell 6):**
- Scale-free
- Composable (multiplicative)
- Stationary
- Comparable across assets

**Pitfall checklist (cell 7) — this is your most-referenced slide of the semester:**
- Read out 3 of the 6 rows
- "Print this. Tape it to your monitor."

**Live demo: Specify → Implement → Validate (cells 8-13):**
- Read the spec out loud (cell 9)
- Show the AI-generated code (cell 10)
- **Walk through the validation explicitly** — the manual check of a dividend day (cell 12) is the most underrated part of the workflow

**Punchline:**
> "**The code is the easy part.** Notice that we spent more time writing the spec and validating the answer than we did writing the code. **That's the job now.**"

---

## 2️⃣ Visualizing + annualization (5 min) — 0:13

**Notebook cells:** 14-17.

**Run cells 14-16** (time series plot + histogram + summary stats).

**Drive the annualization rules (cell 17):**
- Mean × N
- Vol × √N
- Sharpe × √N

> "These rules assume IID. They're approximations. Standard in the industry —
> use them unless you have a reason not to."

**Quick cold-call:** "If a daily Sharpe is 0.05, what's the annualized? *(Answer: 0.79)* If annualized Sharpe is 1.0, what's the daily? *(Answer: 0.063)*"

---

## 3️⃣ Excess returns + risk-free rate (8 min) — 0:18

**Notebook cells:** 18-25.

**Read cell 18** (the excess return concept). Run cell 20 (load Fama-French RF).

**The data unit trap (cell 21) is the demo of the day:**
- Print the raw RF mean
- Print mean × 252 → 1.something
- Print mean × 252 / 100 → 0.05
- "Reality check: Fed Funds in 2024 was ~5%. **The RF is in percentage points, not decimals.**"
- "An LLM will silently skip this check. Your job is to catch it."

**Run cell 23** (merge + compute excess returns).

**The vol of excess vs total is identical — why?** (Cell 24 insight: $R^f$ is nearly constant; subtracting a constant doesn't change variance.)

**Long-short interpretation (cell 25):**
- "Excess return = long the risky asset, short the risk-free."
- "Mortgages are leveraged long positions in your house."

---

## 4️⃣ Sharpe + cumulative returns (10 min) — 0:26

**Notebook cells:** 26-30.

**Run cell 27** (risk premium + Sharpe table for UNH).

**Drive the Sharpe interpretation (cell 28):**

| Sharpe | Interpretation |
|---|---|
| < 0.3 | Weak |
| 0.3–0.5 | Market-like |
| 0.5–1.0 | Good |
| > 1.0 | Exceptional — check your math |

**Run cell 29** (cumulative wealth on log scale).
- "The vertical gap between UNH and the risk-free line is the **cumulative
  excess return**. Decades of risk premium, compounded. That's why people
  hold equities."

---

## 5️⃣ Frequency primer (5 min) — 0:36

**Notebook cells:** 31-33.

**Walk through the frequency table.** Run cell 33 (exact aggregation: daily → annual).

**Three things to land:**
1. Approximation (mean × 252) is close to exact (compound) but not identical
2. **You can't add returns** — you compound them. $(1+R_1)(1+R_2)(1+R_3) - 1 \ne R_1 + R_2 + R_3$
3. `groupby` is the Python idiom for aggregation. Will use this constantly.

---

## 6️⃣ Wrap + assignment preview (5 min) — 0:41

**Skip cells 34-48 entirely in class.** They are Assignment 2 material (see below).

**Project the Key Takeaways (cell 49). Pick 3:**
1. "Always validate. Check data units, verify edge cases, compare to benchmarks."
2. "Sharpe = risk premium / volatility. The fundamental metric. Determines optimal portfolio weights — we'll see why next week."
3. "Annualize consistently: mean × N, vol × √N, Sharpe × √N."

**The new-skill summary (also cell 49):**
- Precise specification
- Careful validation
- Financial judgment

> "Those three are what we're graded on for the rest of the semester. And what you'll be graded on at work."

---

## 7️⃣ What's next + Assignment 2 (4 min) — 0:46

**Wednesday (Lecture 3):** "Where does this data actually come from? We'll tour
CRSP and Compustat — the gold-standard databases used in academic finance
research. You'll see the real schema of US stock data."

**Friday: WRDS account signup deadline.** Link on Brightspace.

**Assignment 2** (due next Monday):
- Cells 34-48 of this notebook ARE Assignment 2 — four exercises:
  1. Warm-up: basic return arithmetic (compounding)
  2. Audit: spot the bugs in this AI-generated Sharpe code
  3. Tail risk + VaR: write a memo on whether normal-VaR understates tail risk
  4. Three-prompt specification challenge: build a rolling Sharpe with the most precise prompt

> "These are *direct* applications of what we did in class. If you can follow
> today's lecture, you can do the exercises. The submission flow is the same
> Google Form as Assignment 1 — paste the token, submit memo, done."

---

## 🎯 Final 2 min — 0:50

**Three minute buffer for questions** — they will have them.

**Most likely questions:**
- "Why does Sharpe matter so much?" → "Determines optimal allocation. Coming next week."
- "What if my data is monthly not daily?" → "Same formulas, replace 252 with 12, √252 with √12."
- "When do we use log returns instead of arithmetic?" → "When compounding over long horizons. Not in this class until later."

---

## 🆘 If you fall behind

Cut in this order:
1. ✂️ Cell 23 (merging RF) — students can do at home
2. ✂️ Cells 25 (long-short interpretation) — interesting but not load-bearing
3. ✂️ Cumulative wealth chart (cell 29) — verbalize instead

**Do NOT cut:**
- The data unit trap (cell 21) — most important demo of the day
- The pitfall checklist (cell 7) — the syllabus in one slide
- The Sharpe interpretation table (cell 28) — students will reference this all semester

---

## 📋 Pre-class checklist

- [ ] Notebook open in Colab, Gemini panel visible
- [ ] Test the data URL once (Fama-French API can rate-limit during class hours)
- [ ] This run sheet on second screen
- [ ] Be ready: 1-2 cold-call quick-math questions about annualization

---

## 🗒️ Notes on Assignment 2 setup

Cells 34-48 of this notebook are the homework. If you want the auto-grader
to process them, you'll need to:

1. **Add a submission cell at the bottom** (after cell 48) following the same
   pattern as `FactorModels_c_AI.ipynb` — bundles answers into a token string
2. **Define an answer key** in `auto_evaluator.py` under
   `ANSWER_KEY["IntrotoReturns_AI"]` with the expected numeric values
3. **Define a memo rubric** for Exercise 3's tail-risk memo

I can build this when you're ready — the pattern is identical to the
Factor Models setup, just different keys.
