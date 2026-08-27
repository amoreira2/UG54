# Factor Models II — Estimation — In-Class Run Sheet

**Notebook:** `FactorModels_II_AI.ipynb`
**Duration:** 75 min
**Pre-class assigned:** *(optional)* Class Book Ch. 8 §1 only
**Pre-class state:** Factor Models I covered; students know α, β, hedged portfolio, appraisal ratio.

---

## 🎬 Cold open (3 min) — 0:00

> "Last class we computed MSFT's beta on the full sample. We got 1.19. We treated that like a fact.
>
> Here's the problem: MSFT in 2000 was a cyclical tech bubble stock with beta over 1.5. MSFT in 2015 was a cash-cow utility with beta under 1. The 'true' beta moved by 50% over the period. **And we collapsed it to one number.**
>
> Today is about what to do about that, and the much bigger problem behind it: **all of our regression estimates are noisy, and some of them are misleading.** By the end of class, you'll have a checklist that tells the difference between real skill and a lucky 5-year run."

---

## 1️⃣ Rolling beta demo (15 min) — 0:03

**Notebook cells:** Run setup (3-4) silently before class.

**Run cells 5-6** (load MSFT). Skim the pitfall checklist (cell 7) — pick 3:
- **#9 Window too short** — "60-day beta is mostly noise"
- **#11 Look-ahead** — "Used today's data to compute today's beta"
- **#14 No persistence check** — "Full-sample alpha can hide that all the alpha came in one year"

**Then the demo — project cell 8 (the spec) and read it.**

**AI MOMENT 1:** Paste into Gemini:

```
I have df_eret (MSFT daily excess returns) and MKT (daily market excess
returns). Compute a rolling 252-day OLS beta of df_eret on MKT. The result
should be a pandas Series of betas indexed by date, first 251 values NaN. Plot it.
```

**Run whatever Gemini produces.** Compare to cell 9.

**Discussion points on the plot:**
- "Beta is between 0.7 and 1.6. What was happening in 2000? In 2010? In 2020?"
- "If you'd hedged MSFT in 2003 using the 2000 beta, what would have happened?"

---

## 2️⃣ Window-size tradeoff (8 min) — 0:18

**Notebook cells:** Run cell 11 (three-window plot). Don't dwell on code — focus on the picture.

**The teaching moment** (point at the plot):
- "63-day window flips through 1.5 and 0.5 in months. **That's not real beta movement, that's noise.**"
- "1260-day window is smooth but takes years to register COVID. Stale."
- "There's no right answer. Pod shops use 60-125 days because they re-hedge daily. Long-horizon investors use 3-5 years."

**Ask:** "If you had to pick *one* window length for a textbook example, what would you choose?" (252 — the year mark — is the conventional answer)

---

## 3️⃣ Look-ahead bias — AI moment 2 (12 min) — 0:26

**This is the operational meat of the lecture. Slow down here.**

**Notebook cells:** Project cell 13 (the table comparing the two options).

**Drive the question:**
- "On 2020-03-15, the market crashed. What MSFT beta do you have *at the open*?"
- "You only have data up through 2020-03-14, right? So you can NOT use 2020-03-15 returns to compute the 2020-03-15 beta. That would be using the future."

**AI MOMENT 2:** Project cell 14 (the spec). Then paste into Gemini:

```
Given df_eret (MSFT excess), MKT, and rolling_beta (252-day rolling),
construct (a) hedge_lookahead = df_eret - rolling_beta * MKT,
(b) hedge_realtime = df_eret - rolling_beta.shift(1) * MKT.
Plot cumulative returns of both on one chart. Report each one's mean and Sharpe.
```

**Run the code (cell 15).** Look at the plot.

**Pose the question to the class:**
- "Which line is higher? Why?"
- "The shift() looks tiny but moves the Sharpe by 0.1-0.3. Where does that come from?"
- Answer: "By not shifting, you're letting tomorrow's beta inform today's hedge — peeking at the answer."

**Land the punchline (cell 16):**
> "When a backtest looks too good, the first thing to check is whether *any* input has data the strategy wouldn't have had in real time. The shift is your friend."

---

## 4️⃣ Statistical significance of α (8 min) — 0:38

**Notebook cells:** 18-20.

**Run cell 19.** Look at the alpha SE and confidence interval.

**Teach:**
- "Annualized α = X%. Sounds great. **What's the standard error?**"
- "The 95% CI is what your CIO actually wants. 'Alpha is 5% [±10%]' is a different story from 'Alpha is 5% [±1%]'."
- "Rule of thumb: |t| > 2 → 'statistically significant'. |t| < 1 → 'indistinguishable from zero'."

**Briefly mention multiple testing:**
> "If you try 100 strategies, 5 will show t > 2 by pure chance. Harvey and Liu's 'factor zoo' paper catalogs 300+ supposedly significant factors. Most won't replicate."

---

## 5️⃣ Why means are uniquely hard (6 min) — 0:46

**Notebook cells:** 21-23 (the "Only time will tell" section).

**The setup:**
- "For betas and variances, more observations help — sampling every minute beats every day."
- "**For means, that's not true.** The SE only shrinks with calendar time."

**Run cell 22 (the years-to-confidence table).** Read out two rows:
- "Sharpe of 0.4 (market-like) → 17 years for 95% confidence"
- "Sharpe of 2.0 (rare) → less than a year"

**Land the punchline:**
> "One reason high-Sharpe strategies are prized is that you can *detect* them with limited data. A 0.5-Sharpe alpha needs ~10 years for 95% confidence — that's hard to sell to investors."

---

## 6️⃣ Persistence test (3 min) — 0:52

**Notebook cells:** 24 (the persistence test concept) — quick read.

- "Cheapest sanity check on an alpha: split the sample. If alpha collapses or flips in half 2, the full-sample number was a regime."
- "Sophisticated investors use bootstrap or walk-forward. Split-sample is the *minimum*."

---

## 7️⃣ How alpha is actually found (5 min) — 0:55

**Notebook cells:** 25-26 (the three buckets).

**This is the connective tissue to cross-sectional strategies. Don't skip.**

**Quick walkthrough:**
- "If we can't reliably estimate alpha from history, where does it come from?"
- "**Three sources**, none of them are 'regress on factor zoo':"
  - **Valuation** — Buffett, Einhorn on Lehman
  - **Liquidity provision** — Citadel, Millennium (forced sellers create reversals)
  - **Proprietary data** — Satellite, credit card panels

**The closing point** (this is critical):
> "Real alpha is being right + early + able to scale before everyone else catches on. A crowded trade can yield NEGATIVE alpha even when the original idea was right. This is why you can read about Buffett's strategy and still not be Buffett."

---

## 8️⃣ Challenge (15 min) — 1:00

**Notebook cells:** Project cell 24 (the setup).

**Sell it (1 min):**
> "Two managers. Both have 10-year track records. **Both have nearly identical full-sample alphas — about 4% a year.** You have one offer to extend. Pair up. You have 10 minutes."

**During (10 min):** Walk the room. Listen for:
- Did they remember to subtract RF?
- For Q2, did they pick the right midpoint? (`len(mgrs) // 2`)
- Are they noticing that Y's half-1 is *huge* (~10%)?

**Common mistakes:**
- Stopping at Q1 ("they're the same!") and not doing the split
- Confusing the t-stat of full-sample alpha with the persistence test
- Forgetting that the *intercept* is alpha (some students use a no-intercept regression)

**Cold-call (4 min):**
- "Who's got Mgr X's full-sample alpha?" (~4.4%)
- "Who's got Mgr Y's?" (~4.2%) — "Same, right?"
- "Now: who's got Mgr Y's HALF-1 alpha?" (~+10%) — *big reveal*
- "And Y's half-2?" (~-1%) — "What happened?"

**The reveal:** "X earned 4.5% then 4.2% — that's real persistence. Y earned 10% then -1% — that's regression to the mean. Y was lucky, not skilled. **Hire X. Do not hire Y, even though their full-sample number looks identical.**"

---

## 🎯 Wrap (3 min) — 1:15

**Pick 2 from the takeaways (cell 35):**
1. "**Static beta is a fiction.** And so is static alpha. Every estimate has noise; some have hidden drift."
2. "**The persistence test is the cheapest insurance against being fooled.** You don't need a PhD in statistics — split the sample, compare, decide."

**Preview:** "Next class: portfolios. Once you can estimate a beta, you can estimate a *covariance matrix*. Once you have a covariance matrix, you can build a portfolio. And once you build a portfolio, you discover that the covariance matrix estimation we just talked about determines whether the portfolio works or blows up."

**Assignment reminder:** Submit Q1-Q5 by midnight Sunday. Submission cell at the bottom of the notebook.

---

## 🆘 If you fall behind

Cut in this order:
1. ✂️ The window-size comparison plot (cell 11) — just verbalize the tradeoff
2. ✂️ Q4 in the challenge (rolling beta std) — it's a sanity check, not the main point
3. ✂️ The multiple-testing aside
4. ✂️ Compress "how alpha is found" to 2 min (just name the 3 buckets)

**Do NOT cut:**
- The look-ahead bias demo (live AI moment #2)
- The "years-to-confidence" table — this is the punchline of the lecture
- The challenge
- The "how alpha is found" section if at all possible — it bridges to the next 4 lectures

---

## 📋 Pre-class checklist

- [ ] Notebook open in Colab, setup cells run (libraries loaded)
- [ ] Gemini panel open
- [ ] This run sheet on second screen
- [ ] Both AI prompts copied to a scratch file
- [ ] Challenge URL works (test load `Estimation_AI_challenge.csv`)
- [ ] You remember: the answer is X, the diagnostic is persistence
