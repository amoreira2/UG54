# Factor Models I — In-Class Run Sheet

**Notebook:** `FactorModels_c_AI.ipynb`
**Duration:** 75 min
**Pre-class assigned:** Ang Ch. 6 §2-3 (skim)
**You need open:** notebook in Colab + Gemini panel + this run sheet on second screen

---

## 🎬 Cold open (3 min) — 0:00

**The hook (memorize this, don't read):**

> "It's 9am. You're at Citadel. You bought $50M of MSFT yesterday. Your risk manager calls: 'How much of that risk is the market, and how much is MSFT-specific? You have 30 seconds.' If you can't split that bet into two pieces, you can't manage it. That's what today's class is about."

Then: "By the end of class you'll know how to answer that question for any stock, and you'll have a tool you can point at any fund manager's track record to figure out whether they're skilled or just lucky."

---

## 1️⃣ Motivate (12 min) — 0:03

**Notebook cells:** Run setup (cells 3-4) silently before class.

**Walk through:**
- Cell 6 (load SPY/WMT/JPM data) — 1 min, just show it loaded
- Cell 7 (scatter plots) — **STOP HERE.** Spend 5 min on this picture.

**Drive the discussion:**
- "Eyeball it. Which has higher beta — WMT or JPM?"
- "Why does that make sense?" (WMT = groceries = defensive; JPM = bank = cyclical)
- "What's the slope of the best-fit line through the JPM cloud? Roughly?" (Aim for ~1.5)
- "What's the spread *around* the line? Which one is tighter?"

**Then introduce the decomposition (cell 8):**
- Write `r^e = α + β·f + ε` on the board.
- "This is just statistics — *always* true. The whole class is about what each piece *means*."

---

## 2️⃣ Pitfall checklist (5 min) — 0:15

**Notebook cells:** Project cell 9 (the pitfall table). Don't read every row.

**Pick 3 to emphasize:**
- **#1 Total vs excess:** "If you forget to subtract RF, your alpha contains the risk-free rate. In 2024 with RF ≈ 5%, that's a huge contamination."
- **#2 No constant:** "AI loves to do `sm.OLS(y, X)` without `add_constant`. That forces alpha to zero. The beta you get back is garbage."
- **#7 Sharpe vs Appraisal:** "We'll come back to this. Most people get it wrong."

**Punchline:** "Your job is shifting. You used to write `pd.merge()`. Now you spec it, audit it, and explain it."

---

## 3️⃣ Live AI moment #1 — The WMT regression (10 min) — 0:20

**Notebook cells:** Project cell 10 (the spec).

**Steps:**
1. Read the spec out loud — emphasize what's specified (units, intercept, what to report).
2. **Switch to Gemini panel.** Paste this prompt (or have it pre-typed):

   ```
   Using the DataFrame `data` with columns SPY, WMT, JPM
   (daily excess returns), regress WMT on SPY using statsmodels
   with an intercept. Print alpha (daily and annualized), beta,
   R-squared, and the t-stat on alpha.
   ```

3. **Run whatever Gemini produces.** *(If it's broken, that's the lesson — fix it together.)*
4. Compare to cell 12 (the canonical answer).
5. **Audit out loud:** walk through cell 13's checklist.
   - "α annualized ≈ 5%. Is that real? Look at the t-stat."
   - "β = 0.67 — matches the scatter we eyeballed."

**If Gemini fails:** even better. Show students the failure mode and walk through fixing it. This is the most valuable demo of the day.

**Time check:** If you're behind, skip the audit checklist verbosity and just hit the t-stat and beta sanity check.

---

## 4️⃣ Risk vs expected return models (5 min) — 0:30

**Notebook cells:** 15, 16 (mostly conceptual).

**Just say:**
- "Two questions you might ask a factor model: 'How much risk is here?' vs 'What return should this earn?'"
- "Same equation, different metric. R² for the first, α for the second."
- "CAPM has R² ≈ 50% — decent risk model. CAPM has tiny but persistent α anomalies — failed return model."
- "Knowing which question you're asking is half the battle."

**Don't run any code.** Just talk.

---

## 5️⃣ Live AI moment #2 — Hedged portfolio (12 min) — 0:35

**This is the conceptual core of the lecture. Slow down here.**

**Notebook cells:** Run cell 18 (MSFT regression — quick), then stop at cell 19 (the spec).

**Walk through the spec.** Then prompt Gemini:

```
Given `df_eret` (MSFT excess returns) and `df_factor['Mkt-RF']`
(market factor), and beta = 1.19 from the regression, construct
(a) Tracking = beta × MKT, (b) Hedged = MSFT excess − Tracking.
Plot cumulative returns of all three on a log scale. Confirm
correlation of Hedged with MKT is ≈ 0.
```

**Run cells 20-21.** When the cumulative chart comes up:

**Ask the class (don't answer for them):**
- "What do you see in the hedged line?"
- "It's flatter. Why does that matter?"
- "If I have a $1M vol budget, can I put more money into MSFT directly or into the hedged version?"

**Land the punchline (cell 22 insight):**
> "Lower vol = bigger position = more alpha captured. This is the logic that factor-neutral hedge funds (Citadel, Millennium, Balyasny) are built around."

---

## 6️⃣ Position sizing + Sharpe vs Appraisal (8 min) — 0:47

**Notebook cells:** Run cells 24-29 in sequence. Don't dwell on the code.

**Key moments:**
- After cell 24: "The hedged position is 2-3× bigger. Same risk, more skill captured."
- After cell 27: "Sharpe and Appraisal are different. Sharpe ratio of unhedged MSFT includes the market premium. Appraisal ratio strips it out."
- "Active-management compensation usually keys off the appraisal-ratio analog (alpha after risk adjustment), not headline Sharpe."

---

## 7️⃣ Challenge (20 min) — 0:55

**Notebook cells:** Project cell 32 (the challenge setup).

**Set it up (2 min):**
> "You're at a fund-of-funds. CIO meeting tomorrow with Fund A and Fund B. You have 18 minutes to figure out who deserves capital. Use AI freely. Pair up."

**Tell them:** "Just do Q1, Q2, Q3 in class. Q4 and Q5 are homework."

**During (15 min):** Walk the room. Listen for:
- Did they remember to subtract RF?
- Are they using the right column names?
- Do they understand the Appraisal ratio?

**Common mistakes to be ready for:**
- Forgetting to subtract RF → α will be ~5% too high for both funds
- Comparing raw means → "Fund A wins, done!" — push back: "is that the right metric?"
- Confusing Sharpe with Appraisal

**Cold-call discussion (3 min):**
- "Who has Fund A's beta?" (should be ~0.6)
- "Who has Fund B's alpha?" (should be ~-12% annualized — *negative*)
- "So who's the better manager? Don't tell me who made more money. Tell me who has skill."

**The reveal:** Fund A has small but real α ≈ 3-5%, low idio vol → high appraisal. Fund B has *negative* α — it just rode high-beta exposure in a bull market. **Don't give them the capital.**

---

## 🎯 Wrap (5 min) — 1:15

**Notebook cells:** Project cell 41 (Key Takeaways).

**Pick 2 to emphasize:**
1. "The decomposition is always valid. *What you do with it* is the job."
2. "AI writes the code. You write the spec, audit the output, and make the decision."

**Preview next class:** "Next time we estimate factor exposures in real-time on real portfolios. The wrinkle: betas drift. We'll see what happens when you use stale ones."

**Assignment reminder:** Submit completed Q4 + Q5 to the Drive folder by midnight Sunday.

---

## 🆘 If you fall behind

Cut in this order:
1. ✂️ The position sizing section (cells 24-25) — students can do at home
2. ✂️ Variance decomposition (cells 30-31) — equivalent to R²
3. ✂️ Q3 in the challenge — leave for homework

**Do NOT cut:** the hedged portfolio demo (live AI moment #2), the challenge setup.

---

## 📋 Pre-class checklist (5 min before)

- [ ] Notebook open in Colab, cells 3-4 run (libraries loaded)
- [ ] Gemini side panel open
- [ ] This run sheet on second screen / printed
- [ ] Both AI prompts copied to a scratch text file (Gemini sometimes resets)
- [ ] Cumulative returns plot from cell 21 pre-rendered in case Gemini fails
- [ ] Challenge URL works (test load of `FactorModels_AI_challenge.csv`)
