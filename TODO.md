# UG54 — to do

Running list. Newest ideas at the top of their section; done items get struck
through and dated rather than deleted, so the reasoning survives.

**Term starts Wed 2 Sep 2026.**

---

## Open decisions

- [ ] **A8 (Thu Dec 3).** Its Thursday is Thanksgiving so it slips to the day
      before the final report. Keep it and let students drop it, or cut it and
      run seven? *Postponed — nothing dropped for now.*
- [x] ~~Ship stock-level industry codes~~ — **done 2026-08-28.**
      `industry_labels.parquet`, 48 industries × ~950 stocks/month, 1980–2000,
      recovered from `indmom` in the characteristics files (see
      `build_industry_labels.py`). No WRDS pull needed.
- [ ] **Widen the industry labels if a group needs them.** Coverage is the ~950
      largest stocks a month, not the full 5,400-stock panel, so L10 §5b's
      conclusion cannot be checked on small caps — where momentum is strongest
      (Sharpe 1.09 vs 0.47). A WRDS `crsp.msenames.siccd` pull mapped to FF49
      would cover everything.
- [ ] **L10 is 1.98 lectured sessions** — genuinely two lectures now that §5b
      exists. Either trim, or move §6 (crashes, vol-scaling) into L15 volatility
      timing, where it is the natural motivating example and would cost L10 only
      ~220 words.
- [ ] **Assignments 4–8 do not exist yet.** A1, A2 and A3 are built and tested.
      **A4 can now be written** — L8 and L9 both exist. A5–A8 wait on their
      lectures, and A5's due date needs the fix noted below.

---

## Before the first class

- [ ] **Submit one test response yourself.** Open L1 in Colab, run it, paste the
      token into the form, then `python3 chapters/Finance/grade_latest.py
      L1_Returns_AI`. Every link in the chain has been checked separately but
      never with a real submission passing through it.
- [ ] **Decide what the in-lecture challenges are worth.** L1 tells students they
      are auto-graded; the syllabus grade table has no line for them (it has
      *Assignments 20%, completion-only* and *Attendance + participation 15%*).
      Someone will ask on day one. Five-word fix once you decide.
- [ ] **Cut L1 to fit 75 minutes.** It currently holds ~2 sessions of material and
      day one always loses time to setup.

---

## Data

### ▸ ~~Remove `ret_fwd` from the course panel~~ — **decided against, 2026-08-26**

Considered making students build the forward return themselves, so the
`groupby`/`shift` trap is something they fall into rather than read about.
**Keeping the shipped column.** Three reasons, in order of weight:

1. **It would break L2's best demo.** The P2 prompt moment asks students to
   build `ret_fwd` and then scores the attempt *against the shipped column* —
   `shift(-1)` alone is wrong on 19,156 rows, `groupby` first on 1,357. Delete
   the column and there is nothing to score against. The lesson is already
   taught, and taught better, *because* the answer exists to check against.
2. **Every answer key assumes the stricter rule.** The shipped column only fills
   when the next observation is the very next *calendar* month, so it never
   splices across a gap in a stock's history — that is the whole 1,357-row
   difference. A plain groupby-shift does not do this, so removing the column
   means re-verifying every key in `auto_evaluator.py`.
3. **68 uses across seven notebooks** plus `build_course_panel.py`.

Revisit only if the project work shows students are still hitting the trap on
their own signals — which is the thing this was meant to prevent.

---

### ▸ Submission cell: `globals()` not `dir()`

`dir()` with no argument returns the *current scope*, which IPython/Colab does
not always populate the way a plain script does, so a variable the student
really has defined can be reported missing. `globals()` is reliable.

```python
missing = [v for v in required if v not in globals()]   # ✅
missing = [v for v in required if v not in dir()]       # ❌ flaky in Colab
```

Checked 2026-08-26 — **L1 already uses `globals()`; L2–L7 all still use `dir()`.**
One line each, six files. Not day-one urgent (L1 is correct and L2 is not until
Sep 9), but it should go in before the second class, because the failure mode is
a student being told their answer is missing when it isn't.

---

### ▸ ~~A3 — pinned from the old Assignment 3~~ — **built 2026-08-26**

All five exercises are in `A3_Beta_and_Alpha_AI.ipynb` as Part 1 (Q1–Q5), on the
49-industry file so students reuse their A1 cleaning code. Verified: betas run
0.52 (Util) to 1.63 (Softw), median 1.10; Smoke has the top alpha at +8.85%/yr,
t = +3.14; **only 5 of 49 clear |t| > 2**, which seeds multiple testing for A4.
The beta-0.5 mandate is solvable several ways — Util alone is already 0.52 — and
a hedged portfolio comes out at corr 0.000 with the market, 12.0% vol against
14.4% unhedged, which makes the "risk-free in what sense?" question land.

Old text preserved below for reference.

### ▸ Original note — old Assignment 3

Old `chapters/Assignments/Assignment3.ipynb` exercises 11–15 need L4 and were
deliberately held out of A1. They are the best material in the old assignments
and should go into **A3** (due Thu Sep 24, after L4–L6):

- **Ex 11** — plot ten stocks against the market and guess which has the highest
  beta *by eye*, then: *"why is it important to measure beta correctly? Explain
  how you can use beta to improve a trade you have in one of these companies."*
- **Ex 12** — regress every stock on the market. Then: *"you are a fund manager
  with a mandate to keep your beta at 0.5. Provide portfolio weights."* Sharper
  than anything currently in L4.
- **Ex 13** — beta-hedged returns for those mandate portfolios. *"Do they
  co-move? Can you call them risk-free? In what sense are they free of risk and
  in what sense not?"*
- **Ex 14** — largest-alpha and lowest-alpha stock. *"If you were picking one
  trade, would picking the largest alpha be right?"*
- **Ex 15** — *"Is that the best we can do? How could you improve the portfolio?"*

Also: old `Assignment4_c.ipynb` is the FF5 mean-variance lab (`w ∝ Σ⁻¹μ`) —
that belongs in **A6**, not A3.

**Turnover:** PLAN's one-line spec said "report turnover", but turnover is
never defined in L1–L3 and appears in **none** of the old assignments. It is
properly a Lecture 16 topic (`TradingCosts_revamped_curated.ipynb` computes it).
Dropped from A2; it belongs in A7, the transaction-cost assignment.

---

### ▸ Strip the "this is important" framing — 7 hits

New style rule in `PLAN.md` §1: don't tell students how important a passage is.
Not urgent, do it in the next editing pass rather than piecemeal.

| file | cell | phrase |
|---|---|---|
| `L3_Sorts_AI` | c30 | "🤖 AI-Era Insight: **this is the whole course in one cell**" |
| `L2_Panel_Portfolios_AI` | c7 | "This is **the most important thing in today's class**" |
| `L2_Panel_Portfolios_AI` | c22 | "Which return column — and this is **the whole ballgame**" |
| `L1_Welcome_Returns_AI` | c33 | "That's **the whole shape of this course**" |
| `L1_Welcome_Returns_AI` | c33 | "**the single most common** way a Sharpe ratio ends up 100× wrong" |
| `L1_Welcome_Returns_AI` | c8 | "**the single most common** silent bug in AI-generated code" |
| `A1_Python_and_Pandas_AI` | c7 | "**the single most common** way a Jupyter result turns out wrong" |

The L3 one is the worst — it sits on genuinely the best cell in the block, and
labelling it that way is what stops it working. The rest are mine; the grep in
`PLAN.md` §1 catches them all.

---

## Content and length

- [ ] **The block is 15.3 lectures of material in 7 slots.** The nine trims in
      `chapters/Finance/CONCEPT_LEDGER.md` §C recover ~880 words (0.6 of a
      lecture). The rest is scope, concentrated in three sections: L3 §2 (1,006
      w), L4's Live Demo (945 w), L7 §6 (723 w).
- [ ] Execute the nine trims from the ledger.
- [ ] **Pilot the eight prompt-it moments against Gemini-in-Colab.** The wrong
      answers are measured and real; whether Gemini actually falls into them is
      not. If it writes `groupby` and `ret_fwd` unprompted, P2 and P3 have no
      payoff.
- [ ] Content gaps M8–M11 from `L1_L7_AUDIT.md` §1c — log vs simple returns,
      empirical VaR, the S&P-500 construction assignment. All Appendix or
      assignment material, none urgent.
- [x] ~~Build the conceptual/theory lecture (Tier 5e)~~ — **split 2026-08-27.**
      Foundations move to L9; the scaling half (crowding, equilibrium net of
      costs, multifactor) stays late and needs L16/L17/L18. See `L9_DESIGN.md`
      and `MISSING_CONTENT.md` Tier 5e.

---

## Infrastructure

- [ ] **Decide about the build scripts.** `build_l1_welcome_returns.py` …
      `build_l7_portfolio_decomposition.py` still generate the *old* notebooks —
      they contain none of the last six commits. Running one silently reverts
      everything. Either backport the changes into them, or add a
      "DO NOT RUN — superseded" header.
- [x] ~~L5's demo downloads all 30 signal files (~94 MB)~~ — **done 2026-08-27.**
      `build_longshort_panel.py` writes `longshort_29.parquet`, 55 KB, and L8
      uses it (3 s instead of 90 s). **L5 itself still rebuilds from scratch** —
      point its `long_short()` demo at the cache too.
- [ ] Optional, October: schedule grading. `grade_latest.py` works out which
      challenge is due, so a cron entry is one line. Grade the *morning of* each
      class, not after it — the challenge is due before the next lecture, so
      nothing is in yet at 5pm.
- [ ] `MISSING_CONTENT.md` Tier 5c/5d.1 are stale — L7 now teaches `b = B′w`,
      `Ω = BΩ_fB′ + Ω_ε` and bottom-up/top-down. L13 should *use* them, not
      re-introduce them. (Noted in the file, not yet reflected in the L13 plan.)

---

## Lectures not yet built

**Reordered 2026-08-28** — see `chapters/Finance/BACK_HALF_PLAN.md`.


**L11 transaction costs (14)** · **L12 leverage and shorting (15)** · L13–L14
capital allocation (16–17) · **L15–L16 conditional strategies (19–20)** ·
**L17 BARRA (22)** · L18 PCA (23) · L19 ML (24).

Three things the reorder surfaced:

- [ ] **BARRA has no source notebook.** `PLAN.md` §11 claims 780KB for the
      untaught block; that holds for costs and leverage but "BARRA" appears only
      *inside* other notebooks and a one-page stub. It is the only from-scratch
      build left. Decide whether it is a lecture or an appendix.
- [ ] **PCA is 3.15 sessions and ML is 2.33.** `StatisticalFactors_AI` is
      described as built and smoke-tested; it is built, and it is three lectures.
      Both need the cut L1–L7 needed.
- [ ] **Buy a buffer.** Ten lectures in ten slots. Merging the two timing
      lectures (1.83 sessions combined) frees meeting 20 for a project clinic.
      Read `MarketTiming_c` and `Volatilitytiming_c` before committing.
- [ ] **A5 is due the day after the lecture it depends on** (Thu Oct 22, mtg 13
      is Wed Oct 21). Make A5 the backtest-protocol assignment on L8/L9 material
      and move the momentum comparison into A6.
- [ ] `PLAN.md` §11 Blocks C–E still use pre-L7 numbering — that is how the
      missing BARRA source went unnoticed. Needs a pass.

---

## Done

- ✅ **2026-08-28** — **L10 built** (`L10_Momentum_AI.ipynb`, 48 cells, 2,201
      lectured words = 1.55 sessions). Zero-to-one-hundred strategy construction:
      the signal survey, momentum rebuilt from the raw panel, the construction
      grid priced, stocks-vs-industries, and crashes.

- ✅ **2026-08-28** — **L9 built** (`L9_WhyShouldThisWork_AI.ipynb`, 39 cells,
      2,339 lectured words = 1.65 sessions). Back-half reorder applied to the
      syllabus, `_toc.yml`, the eleven stubs and L2's two forward references.

- ✅ **2026-08-26** — Shipped the course data (nothing ran before: every notebook
      404'd); fixed L5's `glob`-on-a-URL; renumbered 13 stale lecture references;
      fixed the L3-vs-L4/5/6 book-to-market convention mismatch; moved L7 off a
      fund file missing 19 of 60 months.
- ✅ **2026-08-26** — Language pass borrowing back from the pre-AI notebooks.
- ✅ **2026-08-26** — Eight prompt-it moments.
- ✅ **2026-08-26** — Concept ledger built (`CONCEPT_LEDGER.md`).
- ✅ **2026-08-26** — Submission form wired into all seven notebooks; grader made
      to work with one shared form; service account set up and verified against
      the live sheet; Anthropic API key made optional.
- ✅ **2026-08-26** — Removed the 27 per-item minute counts from Today's Plan.
