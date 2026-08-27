# L8 · Backtesting Protocol — design note

**Slot:** Meeting 8, Wed 30 Sep. **Feeds:** A4, due Thu 8 Oct.
**Status:** planned, not built.

---

## The one idea

> **A backtest is not evidence. The protocol you followed *before you looked* is
> what turns it into evidence.**

Everything in L1–L7 has been in-sample. Students have now run their own signal up
four rungs of a factor ladder and reported what they found. L8 is where that gets
audited.

---

## What the old notebooks give us, and what they cost

Two exist: `Performance_evaluation.ipynb` (original, 4,470 md words) and
`Performance_evaluation_c.ipynb` (curated, 2,833 words, 339 code lines).
**The curated one is already 2.0 lectures of prose** on our calibration. Neither
can be lifted; both need surgery.

### The blocking problem

Both are organised around **"Alpha Testing: the pod manager problem"** and
**"MVE Example: Overfitting in Action"** — and the MVE example needs
`Σ⁻¹μ`, which is **L13**. Our L8 sits five lectures earlier. So the spine of both
old notebooks is unusable here.

That is the real reason they feel heavy: they are a *capital-allocation* lecture
wearing a backtesting title.

### Verdict on each section

| Old section | L8? | Why |
|---|---|---|
| Alpha Testing: the pod manager problem | ✗ **skip** | Needs a fund-management frame students don't have. Better in L14 or dropped. |
| When to fire a pod / abandon a strategy | ✗ appendix | Good material, wrong audience at meeting 8. |
| MVE Example: Overfitting in Action | ✗ **→ L14** | Needs mean-variance. This is exactly L14's fragility lecture. |
| The basic problem of overfitting | ✓ **core** | Rewrite around sorts, not MVE. |
| Be clear about your goal | ✓ **core**, short | One paragraph. |
| Sharpe ratio standard error | ✓ **core** | Needs only a Sharpe. Cheap and load-bearing. |
| "Fraction to half" | ✗ appendix | Interesting, not essential. |
| The complete diagnostics function | ✗ appendix | 60 lines of code that reads as a black box. |
| Adjusting for multiple testing | ◐ **plant here, deliver in L9** | See boundary below. |
| Sample splitting strategies | ✓ **core** | The whole point of the lecture. |
| Application 1: momentum + value combination | ◐ maybe | Good, but it is a second demo and we will be over. |
| Application 2: fine-tuning the look-back | ✓ **core** | The best demo in the old notebook — keep. |
| Publication bias | ✗ **→ L9** | Belongs with anomalies. |
| Literature | ✗ appendix | |

---

## The L8 / L9 boundary

They overlap badly if we are not deliberate. Proposed split:

- **L8 is about *your own* research process.** You have one history, you will try
  several things on it, and here is the discipline that keeps your answer honest.
  Leakage, splitting, the standard error of a Sharpe ratio.
- **L9 is about *the literature's* research process.** 300 published anomalies,
  publication bias, formal multiple-testing corrections, what survives
  replication.

L8 plants multiple testing with one number and hands it to L9. L9 does not
re-teach splitting.

---

## Proposed structure

Same shape as L1–L7: objectives → plan → setup → sections → pitfall checklist →
live demo with a prompt moment → hands-on → challenge → takeaways → appendix.

### §1 · You already have the problem

Open on what they did in A3: every group ran their signal up four models and
reported the interesting rung. Ask how many signals the group looked at before
choosing one. **That is the lecture.**

### §2 · The demo — pick the winner, then look

The central exhibit, verified on our own data. Split the panel at 1990, rank all
29 signals by in-sample Sharpe, pick the best, then look at 1991–2000:

| | in-sample | out-of-sample |
|---|---|---|
| **IdioVol3F** — the in-sample winner | **1.37** | **0.24** |
| top-5 average | 1.25 | 0.62 |
| all 29, average | 0.49 | 0.35 |
| rank correlation IS vs OOS | | **+0.53** |

The +0.53 is what makes this honest rather than nihilistic: **there is real
signal here.** The average strategy holds most of its Sharpe. What does not
survive is *the winner's margin* — the thing that made you pick it.

Then the calibration that makes it quantitative. Simulate 29 **worthless**
strategies over the same 131 months:

> max Sharpe by pure chance: **median 0.60, 95th percentile 0.89**

So a searched-for Sharpe of 0.9 is unremarkable. 1.37 is genuinely above the
noise floor — and still lost three quarters of itself.

### §3 · Leakage — using data you could not have had

Paleologo's one-line rule (EQI §4.1), which is worth quoting:

> *"Never use data in a backtest on a certain date that we are not able to use
> in production today."*

Four instances, three of which are callbacks students already own:

1. **`ret` instead of `ret_fwd`** — L2's P3, now quantified: for STreversal that
   single off-by-one turns t = −0.4 into **+70**.
2. **Survivorship** — L2's CRSP section.
3. **Financial statements dated to the quarter they describe** rather than the
   day they were released. New.
4. **Split-adjusted prices** — new, from EQI, and the best of the four because
   nobody sees it coming: *a low price in the distant past tells you the stock
   split later, which tells you it went up.* The adjusted price series contains
   the future. Use adjusted prices for returns; use as-of-date prices for
   signals.

### §4 · The protocol — decide before you look

- Train / holdout, with a **buffer** between them (EQI §4.2.1)
- Walk-forward, in one picture
- **The rule that does the work:** the universe, the dataset and the protocol are
  fixed *before* the first backtest. Changing your inclusion rule because of a
  backtest result is itself leakage (EQI is explicit about this).
- **Have a theory** — pre-register the prediction. This is already wired in:
  A2 Q7 makes them commit to an economic story before computing anything, and
  this is where we tell them why.

### §5 · Two numbers you can actually compute

- **Standard error of a Sharpe ratio:** `SE(SR) ≈ sqrt((1 + SR²/2) / T)`.
  At T = 250 months and SR = 0.5, that is ~0.065 annualised — so a Sharpe of 0.5
  and a Sharpe of 0.7 are not distinguishable.
- **How long to establish a Sharpe of 0.5 at 95% confidence?** Invert it. The
  answer is uncomfortable and it is the point.

### §6 · Fine-tuning, live (old Application 2)

Tune one parameter in-sample — the momentum look-back, or the number of buckets
from L3 — show the in-sample optimum, then reveal the holdout. Short.

---

## The prompt-it moment

**One, and it is a good one: the train/test split.**

> *"We want to test this out of sample. Split the data."*

Ask an AI to split a dataset for validation and the overwhelmingly common answer
is `train_test_split(..., shuffle=True)` — a **random** split. On a time series
that trains on 1997 and tests on 1985. Every serial correlation, every regime,
leaks backwards.

- **Wrong:** random split → OOS Sharpe close to in-sample, because it is not out
  of sample at all.
- **Right:** chronological split with a buffer → the 1.37 → 0.24 collapse.

The check cell prints both. Numbers to be measured when building.

---

## Appendix (new page, not lectured)

- the complete diagnostics function from `Performance_evaluation_c`
- "fraction to half"
- the pod-manager alpha test
- cross-validation folds in detail
- literature list

---

## On EQI Chapter 4

Genuinely useful, and **not to be followed structurally** — it is a practitioner
checklist, not a lecture.

**Take:** the leakage definition (one sentence); split-adjusted prices; financial
statement timing; point-in-time vs restated; "have a theory"; "define the
protocol and dataset beforehand"; train/holdout with a buffer.

**Skip:** all of §4.1's data-sourcing checklist (vendor provenance, quality
assurance, exploring alternatives) — real, and meaningless to someone who has
never bought data. **Skip §4.3 entirely**: the Rademacher Anti-Serum is a
uniform finite-sample bound on the Sharpe ratio over a strategy family. It is the
chapter's contribution and it is a graduate topic.

---

## Length budget

Target **1,400 lectured words**, which is one session. The curated old notebook
is 2,833. The block L1–L7 already runs 15.3 lectures in 7 slots; L8 should not
add to the debt.

Discipline: §2 is the lecture. §3 is four bullets and a quote. §5 is two
formulas. If §6 does not fit, it becomes the Hands-On.
