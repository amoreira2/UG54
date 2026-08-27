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

**Corrected 2026-08-27.** My first pass wrote off the diagnostics as appendix
material. That was wrong. The MVE is only the *vehicle*; the **checks** are the
content, and almost every one of them works on any return series — including
each group's own long-short. They are the lecture.

| Old section | L8? | Why |
|---|---|---|
| Alpha Testing: the pod manager problem | ✗ skip | Needs a fund-management frame students don't have. |
| MVE Example: Overfitting in Action | ✗ **→ L14** | Needs `Σ⁻¹μ`. This is L14's fragility lecture. |
| The basic problem of overfitting | ✓ core | Rewrite around sorts, not MVE. |
| Be clear about your goal | ✓ core, one paragraph | *"The goal is not the highest in-sample performance. It is a process that reliably identifies genuine alpha."* |
| **Sharpe ratio standard error** — analytic **and bootstrap** | ✓ **core** | Needs only a return series. |
| **Fraction to half** | ✓ **core** | Best fragility test in the notebook. I was wrong to bench it. |
| **Tail behaviour** (±3σ vs the market) | ✓ core | One line. |
| **Drawdown** | ✓ core | One plot. |
| The complete `Diagnostics()` function | ◐ **appendix**, but ship it | 60 lines students should *use*, not read in class. |
| **Bonferroni** | ✓ **core** — moved into L8 | See boundary below. |
| **Hit rate vs detection rate simulation** | ✓ **core** | The best cell in either old notebook. |
| Sample splitting taxonomy | ✓ core, short | Four bullets. |
| Odd/even interleaved split | ◐ appendix | Clever; a second demo we cannot afford. |
| "Is 10 years enough?" power calculation | ◐ appendix | Good, and it needs the alpha/AR frame. |
| Application 2: fine-tuning the look-back | ◐ Hands-On | |
| Publication bias | ✗ **→ L9** | |

---

## The L8 / L9 boundary — revised

Bonferroni moves **into L8**, which makes the split cleaner, not messier:

- **L8 hands them the tools** — the corrected threshold, and the simulation that
  shows what the correction buys and costs. Applied to *their own* research.
- **L9 turns the tools on the literature** — 300 published anomalies, publication
  bias, what survives replication once you apply the correction L8 just taught.

---

## Proposed structure — revised

Target **1,400 lectured words**. Six sections is too many; five, with §1 kept to
a paragraph.

### §1 · You have one history, and you tried several things on it

Open on A3: every group ran their signal up four models and reported the
interesting rung. *How many signals did your group look at before choosing one?*

### §2 · Pick the winner, then look

Split the panel at 1990, rank all 29 signals by in-sample Sharpe, take the best,
then look at 1991–2000. **Verified:**

| | in-sample | out-of-sample |
|---|---|---|
| **IdioVol3F** — the winner | **1.37** | **0.24** |
| top-5 average | 1.25 | 0.62 |
| all 29 average | 0.49 | 0.35 |
| rank correlation | | **+0.53** |

The +0.53 keeps this honest rather than nihilistic: there *is* real signal, and
the average strategy keeps most of its Sharpe. What does not survive is the
winner's *margin* — the thing that made you pick it.

Calibrate with 29 worthless strategies over the same 131 months: the max Sharpe
by chance has **median 0.60, 95th percentile 0.89**.

Then the splitting taxonomy in four bullets — rolling, odd/even, two-way,
three-way — and the rule that the split is chosen *before* the first backtest.

### §3 · Leakage

EQI's one-line rule, quoted:

> *"Never use data in a backtest on a certain date that we are not able to use
> in production today."*

Four instances, three of them callbacks: `ret` vs `ret_fwd` (L2's P3 — for
STreversal that off-by-one turns t = −0.4 into **+70**); survivorship (L2);
financial statements dated to the quarter rather than the release day; and
**split-adjusted prices**, which is new and the best of the four — a low price
long ago tells you the stock split later, which tells you it went up.

### §4 · Five checks, on your own strategy

The heart of the lecture. Every one runs on a return series, so each group
applies them to their own long-short. **Verified on ours:**

| | Sharpe | SE | t(SR) | boot 5% | frac→half | \|r\|>3σ | maxDD |
|---|---|---|---|---|---|---|---|
| the market | 1.01 | 0.22 | 4.53 | 0.62 | 9.2% | 0.8% | −30% |
| Mom12m | 0.99 | 0.22 | 4.42 | 0.61 | 8.4% | 1.6% | −30% |
| GP | 0.61 | 0.22 | 2.75 | 0.26 | 4.4% | 1.6% | −35% |
| BM | 0.39 | 0.22 | 1.77 | 0.03 | 2.4% | 0.4% | −47% |
| STreversal | 0.08 | 0.22 | 0.35 | **−0.28** | 0.4% | 2.0% | −60% |

Three things this table does that no single number does:

1. **The SE is 0.22 for all five.** It depends on how long you looked, not on
   what you looked at. `SE(SR) ≈ sqrt((1 + SR²/2)/T)`.
2. **The bootstrap 5th percentile separates BM from GP** in a way the Sharpe
   ratio does not: 0.03 against 0.26. BM's is a hair above zero.
3. **Fraction to half is a fragility test, not a performance test.** The market
   needs 9.2% of its best months removed to halve its Sharpe; STreversal needs
   **0.4%**. Whatever STreversal has rests on a handful of dates.

Every check orders the five strategies the same way, which is itself worth
saying out loud — they are not five independent opinions.

### §5 · You tried more than one

**Bonferroni**, as a table rather than a formula:

| signals tried | 1 | 5 | 10 | 20 | 29 | 100 | 300 |
|---|---|---|---|---|---|---|---|
| t you need | 1.96 | 2.58 | 2.81 | 3.02 | **3.13** | 3.48 | 3.76 |

Most of the correction happens in the first few. **29 is our signal menu**, so
the threshold for anything found by searching it is **3.13, not 1.96**.

Then the demonstration — 100 worthless strategies over 24 months:

| threshold | how many of 100 look significant |
|---|---|
| t > 1.64 | **6.1** |
| t > 1.96 | 3.4 |
| t > 3.48 (Bonferroni) | 0.1 |

And the trade-off, which is the best cell in either old notebook. One real
signal (Sharpe 1.0) hidden among 100, 48 months:

| cutoff | hit rate | detection rate |
|---|---|---|
| 1.96 | 15% | 52% |
| 3.00 | 45% | 17% |
| 3.48 | 63% | 8% |

At the conventional threshold, **85% of what you flag is false**. At Bonferroni
you are right most of the time and you find the real signal once in twelve.
There is no cutoff that fixes this — only a choice about which error you prefer.

Then run it again at 120 months: 1.96 gives 26%/90%, 3.48 gives 93%/41%.
**Length of sample is the only thing that buys you both.**

---

## The prompt-it moment

**The train/test split.** *"We want to test this out of sample. Split the data."*

The common AI answer is `train_test_split(..., shuffle=True)` — a random split,
which on a time series trains on 1997 and tests on 1985. The check cell prints
the random-split OOS Sharpe (close to in-sample, because it is not out of sample)
against the chronological split (1.37 → 0.24).

---

## Appendix (new page, not lectured)

- the full `Diagnostics()` function — **ship it working**, so groups can run all
  five checks on their own strategy in one call
- the odd/even interleaved cross-validation split
- the "is 10 years enough?" power calculation
- literature list

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

Discipline: **§4 and §5 are the lecture.** §1 is a paragraph, §3 is four bullets
and a quote. The fine-tuning demo becomes the Hands-On. The `Diagnostics()`
function ships in the appendix so class time goes on reading its output, not
writing it.
