# The back half — order and content

**Written 2026-08-28.** L1–L8 are fixed. This is about meetings 13–24, and it is
written under one assumption AM stated: **whatever sits at the end will not
happen.** So the question is not "what is the logical order" but "what do we
most regret losing, and is it early enough to survive."

---

## The structural problem

Ten lecture slots after the midterm. Ten lectures planned.

| | |
|---|---|
| meetings 13–17 | 5 lectures |
| meeting 18 | guest |
| meetings 19–20 | 2 lectures |
| meeting 21 | pitches II |
| meetings 22–24 | 3 lectures |
| **total** | **10 slots, 10 lectures** |

**Zero buffer**, in a term that contains a guest speaker to schedule, three
presentation days including a non-standard **Friday** that needs a room, and
Thanksgiving. Add the ordinary slippage of any term and two lectures do not
happen.

The planning move is to decide *now* which two, rather than discovering it on
November 20. Right now the axe would fall on **meetings 23–24: PCA and machine
learning** — and machine learning is a line in the course description.

### Supply, measured

At the calibrated 1,417 lectured words per session:

| lecture | source | sessions of material |
|---|---|---|
| Momentum | `Momentum.ipynb` | 1.25 |
| Conditional strategies | `MarketTiming_c` + `Volatilitytiming_c` | 1.03 + 0.80 = **1.83** |
| Capital allocation | `CapitalAllocationI_AI` + `CapitalAllocationII` | 1.85 + 1.48 = **3.33** |
| **BARRA** | **none — see below** | **0.00** |
| Transaction costs | `TradingCosts_revamped_curated` | 0.75 |
| Leverage and shorting | `LeverageandShorting.ipynb` | 1.27 |
| PCA | `StatisticalFactors_AI` | **3.15** |
| Machine learning | `MachineLearning_cc` | **2.33** |

≈14 sessions of existing material for 10 slots, **plus one lecture that does not
exist at all**. The same over-supply that produced 15.3 lectures in L1–L7's seven
slots is sitting in the back half, unaddressed.

### BARRA has no source notebook

`PLAN.md` §11 Block D says the untaught block has "~780KB of source material."
For costs and leverage that is true. **For BARRA it is not** — the word appears
only *inside* other notebooks (L5, `FactorModels_II_AI`, `StatisticalFactors_AI`,
`TradingCosts_revamped_curated`) and in a one-page stub. It is the only lecture
in the course that would be written from nothing.

It is currently **meeting 19**, in the middle of the block, where failing to
finish it displaces everything after it.

---

## The ordering finding

> **The two most project-essential lectures in the back half are the eighth and
> ninth of ten.**

**Transaction costs — meeting 20.** Every backtest a student has ever run in this
course is gross of costs. Nothing else in the term does more to separate a
1.5 Sharpe from a business.

**Leverage and shorting — meeting 22.** Every group's strategy is *long-short*.
They have been told since L3 that the weights sum to zero, and they have been
reporting Sharpe ratios on that object for eight weeks. What capital sits behind
it is not answered until meeting 22 — after six assignments have been written
assuming an answer.

That gap is not hypothetical. Building the L9 drawdown demo, "what was this
strategy's worst drawdown?" turned out to have **five defensible answers** —
−75%, −121%, −96%, −100%, −98% — and the only thing separating them is what you
assume the capital base is. That is L17 material, and students need it to
interpret numbers they started producing in September.

**The report is due Sunday Dec 6.** Under the current order, leverage lands
Nov 23 — two weeks before. Lose two meetings anywhere in November and it lands
the week the reports are written, or not at all.

---

## Recommended order

Move the implementation block forward; push timing and BARRA back.

| # | Date | Session | change |
|---|---|---|---|
| 13 | Wed Oct 21 | **L10 · Momentum and trend following** | — |
| 14 | Mon Oct 26 | **L11 · Transaction costs** | ↑ from 20 |
| 15 | Wed Oct 28 | **L12 · Leverage, shorting, and the capital base** | ↑ from 22 |
| 16 | Mon Nov 2 | **L13 · Capital allocation I** | — |
| 17 | Wed Nov 4 | **L14 · Capital allocation II — estimation error** | — |
| 18 | Mon Nov 9 | Guest | — |
| 19 | Wed Nov 11 | **L15 · Conditional strategies I — volatility timing** | ↓ from 14 |
| 20 | Mon Nov 16 | **L16 · Conditional strategies II — factor timing** | ↓ from 15 |
| 21 | Wed Nov 18 | Pitches II | — |
| 22 | Mon Nov 23 | **L17 · Fundamental risk models (BARRA)** | ↓ from 19 |
| 23 | Wed Nov 25 | **L18 · PCA and statistical factors** | — |
| 24 | Mon Nov 30 | **L19 · Machine learning** | — |

### Why this and not the current order

**Momentum → costs is the best transition available.** The standard critique of
momentum is that its turnover eats the premium. Asking "so what does it cost?"
the meeting after momentum is the natural next question; asking it six meetings
later is a topic change.

**Costs → leverage is one coherent block: what it takes to actually run this.**
Two lectures, both cheap to build (0.75 and 1.27 sessions of existing material,
the two best-sized sources in the back half), both directly a section of the
December report. They also close L9: *"can the world support everyone picking it
up?"* is qualitative in L9 and quantitative in the costs lecture.

**Nothing downstream breaks.** Costs needs portfolio weights (L2) and turnover
(definable from them). Leverage needs long-short weights (L3) and drawdowns (L8).
Neither needs `Σ⁻¹μ`. The dependency graph permits the swap — the only hard chain
in the back half is momentum before the momentum assignment.

**Capital allocation is better with costs already taught.** The optimizer that
ignores trading costs is the toy version; students meet the real problem if they
already know what a trade costs.

**Volatility timing pairs with leverage, not against it.** "Scale the position by
1/σ" *is* a leverage decision. Having taught leverage at 15, timing at 19 is
better motivated than it is at 14.

**BARRA moves into the zone where failure is free.** It is the only from-scratch
build left. At meeting 22 it can slip or be cut without displacing anything; at
meeting 19 it cannot. And L7 already taught `b = B′w` and `Ω = BΩ_fB′ + Ω_ε`, so
BARRA is now a *worked instance* of machinery students have, not new machinery —
which is an argument for it being a smaller lecture than planned.

**Nov 25 keeps PCA.** Day before Thanksgiving, most self-contained session,
cheapest to miss. Same reasoning as before, unchanged.

### What this costs

Timing moves from meetings 14–15 to 19–20, so if the term slips it is **timing
that is at risk instead of costs**. That is the trade, stated plainly. I take it
because a student writing a December report needs to know what their strategy
costs to run more than they need to know whether it works better in some states.

---

## The second decision: buy a buffer

The reorder fixes *which* lectures are exposed. It does not fix the fact that ten
lectures are booked into ten slots.

**Recommendation: merge conditional strategies into one lecture** — the two
sources are 1.83 sessions combined, and volatility timing plus factor timing is
one idea (*condition the position on something you can observe today*) with two
applications. That frees meeting 20 as a **project clinic** before Pitches II.

That is the cheapest slot to buy, and I would want to read both notebooks before
committing to it. The alternative — merging capital allocation I and II — I would
not do: the estimation-error half is the intellectual core of the back half and
it is the payoff of L8's `Estimate → Tune → Test` frame.

**And cut A8.** It is due Thu Dec 3, three days before the report, on material
from meetings 22–24. It competes with the thing it is supposed to support. The
syllabus already says six of eight earns full credit, so cutting it costs nothing
and returns a week to ten groups at exactly the moment they need it.

---

## Does L9 belong at meeting 9?

**Yes, and the reason is narrower than the design doc claims.**

Not the intellectual arc. **Project pitches are meeting 10, two days later.** L9
§6 is the pitch rubric: what frictions does this exploit, why has nobody
arbitraged it, who is on the other side. If students have not been asked those
questions before they pitch, the pitches are ten backtests and the pitch day is
wasted.

Everything else about the placement is secondary — the midterm covers 1–9 and L9
makes good essay material, and it closes L8's loop. But those would not be enough
on their own.

### The alternative I considered and reject

**Momentum at meeting 9, L9 late.** It has real appeal: momentum is the canonical
worked anomaly, it is a content lecture moved pre-midterm, and it frees a back-half
slot — which is exactly what the back half needs.

I reject it because it spends the pitch day. It also puts the term's most
interpretive lecture after students have already committed publicly to a
strategy, which is backwards: the point of L9 is to change what they pitch.

If the back half needs a slot more than the pitch day needs a rubric, this is the
trade to make. I do not think it is.

---

## Defects found in the current syllabus

Independent of any reordering, four things in
`UG54_syllabus_fall2026.docx` need fixing:

1. **The report due date contradicts itself.** The by-topic table says
   *"report + code, Fri Dec 4"*; the key-dates table says *"Sunday, Dec 6."*
   (Both are real dates — Dec 4 2026 is a Friday, Dec 6 a Sunday.) Pick one.
2. **Seven or eight assignments?** The grade table says *"Assignments (eight,
   completion only)"*, the prose says *"The seven assignments are different"*,
   and the next paragraph says *"There will be eight assignments."*
3. **Meeting 9 is still titled "L9 · Anomalies."** It is *Why Should This Work?*
4. **The by-topic table is off by one at the end** — it puts machine learning at
   meeting 25 and the project at 26–28; the by-meeting table has ML at 24 and the
   project at 25–28.

And one scheduling defect: **A5 is due Thu Oct 22, the day after meeting 13.**
A one-day turnaround on brand-new material. If A5 is the momentum assignment it
cannot stay there. Fix: make A5 the backtest-protocol assignment on L8/L9
material — which students have had since Oct 5 — and move the momentum
comparison into A6.

### Assignment mapping under the recommended order

| | due | covers | content taught by |
|---|---|---|---|
| A5 | Thu Oct 22 | run Estimate → Tune → Test on your own strategy | mtg 9 |
| A6 | Thu Nov 5 | what does your strategy cost, and is it just momentum? | mtgs 13–15 |
| A7 | Thu Nov 19 | sizing it, and does it work better in some states? | mtgs 16–17, 19 |
| A8 | — | **cut** | |

Every assignment now follows its lecture by at least a week.

---

## Open, and worth deciding before the term starts

- **PCA is 3.15 sessions of material** in `StatisticalFactors_AI`, described in
  `PLAN.md` as "built and smoke-tested." It is built, and it is three lectures.
  Machine learning is 2.33. Both need the same cut L1–L7 needed.
- **Does BARRA survive at all?** It is a from-scratch build, at meeting 22, after
  L7 already delivered its machinery. The honest question is whether it is a
  lecture or an appendix. Deciding *now* frees the build effort.
- `PLAN.md` §11 Blocks C–E still use pre-L7 numbering (it calls BARRA "L14"),
  which is why the missing source went unnoticed. §11 needs a pass.
