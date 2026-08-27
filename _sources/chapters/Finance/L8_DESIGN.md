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

## Proposed structure — v3, built around the process

**Revised 2026-08-27 after AM.** The focus is the **process**, not the measures.
The measures get *shown* — they are what the process outputs — but the lecture is
about **Estimate → Tune → Test** and the techniques that keep the test honest.

This also solves the MVE problem. The old notebook needed `Σ⁻¹μ` to have something
to tune. We do not: **"take the top *N* signals and combine them with weights
*W*"** is a rule with two knobs and no optimizer. *N* and *W* are the tuning
parameters. No mean-variance required, so it fits at meeting 8.

### §1 · You have one history and you tried several things on it

Open on A3. *How many signals did your group look at before choosing one?*

### §2 · Estimate → Tune → Test

Three disjoint samples, three different jobs. Nothing else in the lecture matters
as much as this.

| sample | dates | months | its job |
|---|---|---|---|
| **Estimate** | 1980–89 | 119 | rank the 29 signals |
| **Tune** | 1990–94 | 60 | choose *N* and *W* |
| **Test** | 1995–2000 | 72 | report, **once** |

Top of the estimate ranking: ShareIss5Y 1.17, IdioVol3F 1.17, AnnouncementReturn
1.13, DivSeason 1.11.

Show the **tune grid** first — this is all you are allowed to look at:

| N | ew | ivol | sharpe |
|---|---|---|---|
| 1 | 0.99 | 0.99 | 0.99 |
| 3 | 1.56 | 1.84 | 1.54 |
| 5 | 1.27 | 1.82 | 1.29 |
| 10 | 1.31 | 1.62 | 1.29 |
| 20 | 1.61 | **1.90** | 1.46 |
| 29 | 1.67 | 1.66 | 1.50 |

Tuning picks **N = 20, inverse-vol**. *Then* reveal the test grid:

| | TEST Sharpe |
|---|---|
| the tuned choice, N=20 ivol | **1.13** |
| naive — the single best signal from the estimate sample | **−0.08** |
| no tuning at all — all 29, equal-weighted | 0.85 |
| average over the whole grid | 0.59 |

**The naive rule is the disaster.** ShareIss5Y had a 1.17 Sharpe in the estimate
sample and delivers **−0.08** in the test. Meanwhile the crudest possible rule —
hold everything, weight equally, tune nothing — delivers 0.85.

**Robustness, checked across five split dates.** The ordering never flips:

| estimate ends | tuned pick | TEST tuned | best-1 | all-29 |
|---|---|---|---|---|
| 1987-12 | N=20, ivol | 1.33 | 0.26 | 1.02 |
| 1988-12 | N=5, ivol | 1.28 | 0.02 | 0.91 |
| 1989-12 | N=20, ivol | 1.14 | −0.04 | 0.85 |
| 1990-12 | N=29, ew | 0.85 | 0.26 | 0.85 |
| 1991-12 | N=3, ivol | 1.26 | 0.80 | 0.83 |

Tuning beats no-tuning every time and beats best-1 every time. Worth saying that
in four of five it also lands on the best cell in the grid — which is partly
luck, and should be said rather than implied.

### §3 · Walk-forward, and a trap I fell into

Re-rank, re-tune and re-invest every year on an expanding window, then stitch the
monthly returns. 1990–2000, 132 months:

| | return/yr | vol/yr | **Sharpe** | maxDD |
|---|---|---|---|---|
| re-tuned every year | 5.7% | 4.0% | **1.42** | **−4%** |
| always the single best | 11.8% | 15.3% | 0.77 | −24% |
| always all 29, equal-weighted | 4.8% | 4.8% | 0.99 | −12% |

**On raw return the naive rule "wins" — 11.8% against 5.7%.** It loses on every
risk-adjusted measure and carries a −24% drawdown against −4%.

I made exactly this mistake building the demo: my first walk-forward compared
mean returns and concluded the naive rule was best. **Put that in the notebook.**
It is L1's lesson — return alone is not quality — arriving unannounced five
lectures later, and it is a live example of the thing the course is about.

### §4 · What you report at the end

The measures, shown as the *output* of the test stage rather than as a topic.
Run on the test sample only, for the tuned strategy and for the market:

Sharpe · **SE(Sharpe)** and its t · **bootstrap 5th percentile** · **alpha, its
SE, and the appraisal ratio** · **fraction to half** · tails beyond ±3σ · max
drawdown.

Verified on the full sample as a reference:

| | vol/yr | Sharpe | SE(SR) | boot 5% | alpha | SE(α) | t(α) | appraisal | frac→half | maxDD |
|---|---|---|---|---|---|---|---|---|---|---|
| Mom12m | 20.1% | 0.99 | 0.22 | 0.61 | 18.2% | 4.4% | 4.10 | 0.91 | 8.4% | −30% |
| GP | 11.0% | 0.61 | 0.22 | 0.26 | 6.3% | 2.4% | 2.59 | 0.58 | 4.4% | −35% |
| BM | 13.5% | 0.39 | 0.22 | 0.03 | 7.2% | 2.9% | 2.45 | 0.54 | 2.4% | −47% |
| STreversal | 18.4% | 0.08 | 0.22 | −0.28 | −1.2% | 4.0% | −0.29 | −0.06 | 0.4% | −60% |

**On SE(Sharpe) being ~0.22 for all of them.** This is right, and it is
counterintuitive enough to be worth a box. Volatility cancels: SR = mean/sd, and
both the numerator and the denominator of the *estimate* scale with σ, so only
*T* and *SR* survive — `SE(SR) ≈ sqrt((1 + SR²/2)/T)`. Simulated at a true Sharpe
of 0.5 over 250 months, the sampling sd of the estimate is 0.220 at 5% annual
volatility and 0.220 at 80%.

The intuition that it *should* depend on volatility is correct for everything in
return units, and the table shows it: **SE(mean)** runs 2.4% to 4.4% and
**SE(α)** runs 2.4% to 4.4%, both tracking vol exactly. Put the two side by side
— the contrast is the lesson.

### §5 · Leakage

EQI's rule, quoted:

> *"Never use data in a backtest on a certain date that we are not able to use in
> production today."*

Four instances, three of them callbacks: `ret` vs `ret_fwd` (L2's P3 — STreversal
goes t = −0.4 to **+70**); survivorship (L2); financial statements dated to the
quarter rather than the release day; and **split-adjusted prices**, new and the
best of the four.

### §6 · You tried more than one — short

Bonferroni as a table, not a formula:

| signals tried | 1 | 10 | 20 | **29** | 100 | 300 |
|---|---|---|---|---|---|---|
| t you need | 1.96 | 2.81 | 3.02 | **3.13** | 3.48 | 3.76 |

100 worthless strategies over 24 months flag **6.1** at t > 1.64, 3.4 at 1.96,
0.1 at Bonferroni. Then the trade-off — one real signal of Sharpe 1.0 among 100,
48 months:

| cutoff | hit rate | detection |
|---|---|---|
| 1.96 | 15% | 52% |
| 3.00 | 45% | 17% |
| 3.48 | 63% | 8% |

At 120 months: 1.96 → 26%/90%, 3.48 → 93%/41%. **Only a longer sample buys both.**

---

## The prompt-it moment

**The train/test split.** *"We want to test this out of sample. Split the data."*
The common AI answer is `train_test_split(..., shuffle=True)` — random, which on
a time series trains on 1997 and tests on 1985. The check prints the random split
against the chronological one.

---

## Appendix (not lectured)

- the full `Diagnostics()` function — **shipped working**, so groups run every
  check on their own strategy in one call
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
