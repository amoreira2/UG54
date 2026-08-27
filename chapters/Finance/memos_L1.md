# Memos to grade — L1_Returns_AI

Score each 0–5 against the rubric, then paste the scores into the 'Grades_L1' tab.

## Rubric

```
You are grading a first-week memo from an undergraduate. This is Lecture 1 --
they have NOT yet seen factor models, beta, or alpha. Grade what they can
reasonably notice, not what a finance PhD would say.

THE QUESTION: GE's annualized Sharpe ratio was 0.773 over 1980-2000 vs the
market's 0.601. Does that prove Jack Welch was an exceptional manager?

GROUND TRUTH:
- GE's volatility was 22.2% vs the market's 15.6% -- about 40% MORE volatile.
- So GE took more risk. Some of the extra return is compensation for that risk,
  not skill. A student who spots this has got the main point.
- The Sharpe ratio already adjusts for TOTAL volatility, so GE's higher Sharpe
  is genuinely something -- it is not nothing. The honest answer is "suggestive,
  not proof."
- What you'd want next: how much of GE's return is explained by simply being a
  levered bet on the market (its beta), and what is left over. That is exactly
  what Lecture 4 does. A student who gestures at this -- even without the words
  "beta" or "alpha" -- deserves full credit.
- Other good observations: 20 years is one sample and GE was SELECTED because it
  was famous (survivorship / hindsight); conglomerates are diversified so this
  may be a portfolio effect; GE Capital made GE partly a financial firm.

GRADE THE REASONING, NOT THE ARITHMETIC. Quoting 22.2% vs 15.6% is evidence a
student looked, but it is not the skill being tested and it earns no credit on
its own. A memo that argues correctly in words scores exactly the same as one
that cites the figures. Never deduct for not quoting numbers.

Grade 0-5:
  5 = Recognizes that a higher Sharpe is suggestive but not decisive, AND names
      something that would settle it -- a risk difference the Sharpe ratio does
      not capture, market exposure, a proper benchmark, or the fact that GE was
      chosen because it was famous.
  4 = Recognizes the comparison is incomplete and reasons correctly about why,
      but stops short of saying what would settle it.
  3 = Gestures at risk but the argument is thin, one-sided, or asserted rather
      than reasoned.
  2 = Answers the question while ignoring risk entirely -- e.g. "yes, higher
      Sharpe means he was better."
  1 = Restates the numbers or the question without an argument.
  0 = Empty or off-topic.

DO NOT penalize a student for not using the words "alpha", "beta", or "CAPM" --
they have not been taught yet. A student who says "riskier in a way volatility
doesn't capture" has made exactly the right move and should be graded as such.
DO reward noticing that the comparison is incomplete.

For picked_fund return "neither" (not applicable).
For cited_appraisal_or_alpha return True if the memo argues that the Sharpe
comparison is incomplete -- whether by pointing at the risk difference, asking
for a benchmark or risk-adjusted comparison, or raising selection bias -- else
False. Do not require that any number be quoted.

Output via the `grade_memo` tool.
```

---

## [0] Alan Moreira  <am16634@nyu.edu>   ✅ already graded

GE had a higher realized SR in the period than the market. This is consistent with the market underappreciating how good Welch was a manager at the start of the sample. But it is also consistent with GE being substantially riskier in a way that is not captured by it's volatility

**Score:** 5/5
**Feedback:** Strong. You see that the same higher Sharpe is consistent with two different stories -- skill, or risk the ratio can't see -- and you don't pick one without more evidence. "Riskier in a way not captured by its volatility" is exactly the right instinct: it points at the systematic-risk question we take up in Lecture 4. To sharpen it, name what you'd look at next (how much of GE's return is just a levered version of the market), and note that GE was picked because it was famous.

---

## [1] Alan Moreira  <am16634@nyu.edu>   ✅ already graded

GE had a higher realized SR in the period than the market. This is consistent with the market underappreciating how good Welch was a manager at the start of the sample. But it is also consistent with GE being substantially riskier in a way that is not captured by it's volatility

**Score:** 5/5
**Feedback:** Strong. You see that the same higher Sharpe is consistent with two different stories -- skill, or risk the ratio can't see -- and you don't pick one without more evidence. "Riskier in a way not captured by its volatility" is exactly the right instinct: it points at the systematic-risk question we take up in Lecture 4. To sharpen it, name what you'd look at next (how much of GE's return is just a levered version of the market), and note that GE was picked because it was famous.

---

## [2] Late Student  <late.student@stern.nyu.edu>

Sorry this is late. GE's Sharpe was higher but it was much more volatile, so I don't think one number settles it.

**Score:** _/5
**Feedback:** 

---

