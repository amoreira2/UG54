# UG54 — to do

Running list. Newest ideas at the top of their section; done items get struck
through and dated rather than deleted, so the reasoning survives.

**Term starts Wed 2 Sep 2026.**

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

### ▸ A2 — pinned from the old Assignment 3

Old `chapters/Assignments/Assignment3.ipynb` exercises 11–15 need L4 and were
deliberately held out of A1. They are the best material in the old assignments
and should go into **A2** (due Thu Sep 24, after L4–L6):

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

Also for A2: old `Assignment4_c.ipynb` is the FF5 mean-variance lab
(`w ∝ Σ⁻¹μ`) — that belongs in **A5**, not A2.

**Turnover:** PLAN's one-line A1 spec said "report turnover", but turnover is
never defined in L1–L3 and appears in **none** of the old assignments. It is
properly a Lecture 16 topic (`TradingCosts_revamped_curated.ipynb` computes it).
Dropped from A1; put it in A6, which is the transaction-cost assignment.

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
- [ ] Build the conceptual/theory lecture (Tier 5e) seeded by
      `InterpretingFactorModels.ipynb`. L5 now points forward to it.

---

## Infrastructure

- [ ] **Decide about the build scripts.** `build_l1_welcome_returns.py` …
      `build_l7_portfolio_decomposition.py` still generate the *old* notebooks —
      they contain none of the last six commits. Running one silently reverts
      everything. Either backport the changes into them, or add a
      "DO NOT RUN — superseded" header.
- [ ] L5's demo downloads all 30 signal files (~94 MB) to build the correlation
      matrix — 87 s on one machine, and 40 students at once is ~3.7 GB from
      GitHub raw, which rate-limits. Cache the 29 long-short return series as one
      small parquet.
- [ ] Optional, October: schedule grading. `grade_latest.py` works out which
      challenge is due, so a cron entry is one line. Grade the *morning of* each
      class, not after it — the challenge is due before the next lecture, so
      nothing is in yet at 5pm.
- [ ] `MISSING_CONTENT.md` Tier 5c/5d.1 are stale — L7 now teaches `b = B′w`,
      `Ω = BΩ_fB′ + Ω_ε` and bottom-up/top-down. L13 should *use* them, not
      re-introduce them. (Noted in the file, not yet reflected in the L13 plan.)

---

## Lectures not yet built

L8 onward. L8 backtesting protocol, L9 anomalies, L10 momentum, L11–L12
conditional, L13–L14 capital allocation, L15 BARRA, L16 costs, L17 leverage,
L18 PCA, L19 ML. Calendar in `PLAN.md` §3.

---

## Done

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
