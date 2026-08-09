# Concept ledger — every point made in L1–L7, and where it is made

**Purpose.** One place to see what each lecture claims, so a point can be
delivered **once, in its best place**, instead of being front-loaded wherever it
first becomes tempting.

**How to use it.** Before adding an idea to a lecture, find it here. If it
already has a home, say one sentence and point forward. If it doesn't, add a row.

**Last updated:** 2026-08-08 · covers the state after the prompt-it commit
(`5a3b8691`).

Legend for the **Status** column:

- **◆ home** — this is the canonical statement. Full explanation lives here.
- **↪ callback** — deliberate, one or two sentences, reuses a point already made.
- **⤴ forward** — a deliberate teaser for a later lecture.
- **✖ repeat** — the same claim restated at the same depth. Candidate for cutting.

---

## Part A — The beat sheet

### L1 · The Workflow, and What a Return Is  · 3,010 w · 2.12 lectures

| § | w | The point | Status |
|---|---|---|---|
| 1 | 291 | Course mechanics: grading, groups, two kinds of work, AI policy | ◆ |
| 2 | 215 | AI writes the code; the value moved to spec / audit / interpret | ◆ |
| 2 | — | **AI code usually runs — that is the problem** | ◆ home |
| 3 | 221 | Specify → Implement → Validate; a vague prompt returns a plausible wrong number | ◆ |
| 4 | 103 | Colab + Gemini setup | ◆ |
| 5 | 222 | Returns not prices; total vs price return; dividends ≈ ⅓ of long-run return | ◆ |
| 5 | — | Compounding: chain multiplicatively, −50% then +50% is −25% | ◆ |
| PC | 202 | Six return pitfalls | ◆ |
| PC | — | *"Every one of these produces a number. None throws an error."* | ✖ repeats §2 |
| Demo | 426 | **P1** — growth of $1,000; `auto_adjust` on/off | ◆ |
| 6 | 453 | Excess return = compensation for risk (10% vs 8% bills) | ◆ |
| 6 | — | The units trap: percent vs decimal, print the mean first | ◆ |
| 6 | — | Should a *risk-free* rate change the variance at all? | ◆ ⤴ |
| 6 | — | **An excess return is a self-financed long-short**; the mortgage analogy | ◆ **home** |
| 7 | 155 | Sharpe = return per unit of vol; annualization; benchmark magnitudes | ◆ |
| 7 | — | High Sharpe ≠ skill | ◆ ⤴ L4 |
| KT | 204 | 7 takeaways | ✖ by construction |

### L2 · The Panel and Portfolio Mathematics · 3,280 w · 2.31 lectures

| § | w | The point | Status |
|---|---|---|---|
| 1 | 336 | CRSP: what it is, survivorship bias, delisting returns; Compustat | ◆ |
| 2 | 639 | Long vs wide: breaks on variables, breaks on assets | ◆ |
| 2 | — | `groupby('date')` is the workhorse | ◆ |
| 2 | — | The columns, incl. `prc` can be negative | ◆ ⤴ L3 |
| 2 | — | **Two return columns: form weights at *t*, earn `ret_fwd`** | ◆ **home** |
| 2 | — | **P2** — build `ret_fwd`; `shift` without `groupby` is wrong on 19,156 rows | ◆ |
| 3 | 280 | Returns are not normal: fat tails, skew, kurtosis; −100% returns are real | ◆ |
| 3 | — | Sharpe can't see any of this | ◆ ⤴ |
| PC | 218 | Six portfolio pitfalls | partly ✖ |
| PC | — | Pitfall 1 = look-ahead; AI-Era box restates it | ✖ ×2, §2 already |
| 4 | 408 | `w` is a weight vector; three cases (EW / VW / long-short) | ◆ |
| 4 | — | Long-short weights sum to zero, costs nothing, returns a spread | ✖ **re-derives L1** |
| 4 | — | **Value-weighting is the only portfolio everyone can hold — it IS the market** | ◆ home |
| 4 | — | VW rebalances itself → zero turnover → why index funds work | ◆ ⤴ L16 |
| 4 | — | VW never builds a big position in a tiny stock; EW alphas are "mostly a mirage" | ◆ home |
| Demo | 355 | **P3** — `w′r`; using `ret` says the market returned 25.5%/yr | ◆ |
| Demo | — | "The general form of this bug" | ✖ third statement |
| 5 | 74 | EW is an unintended small-cap bet | ✖ overlaps §4 |
| HO | 254 | EW lost to VW by 1.5%/yr with more vol; Banz died on publication | ◆ ⤴ L3 |
| HO | — | EW is not tradeable at scale | ✖ overlaps §4 |
| KT | 262 | 8 takeaways | ✖ by construction |

### L3 · Sorts, Breakpoints, Long-Short · 3,681 w · 2.60 lectures

| § | w | The point | Status |
|---|---|---|---|
| 1 | 727 | A signal can be anything; three requirements | ◆ |
| 1 | — | The five-step recipe; rank within month = curving by cohort | ◆ home |
| 1 | — | Sorting vs regression: non-parametric, shows shape, output is a portfolio | ◆ |
| 1 | — | Step 5 is self-financed | ✖ **third derivation** (L1, L2) |
| 1 | — | Book size: why weights must sum to one | ◆ home |
| 1 | — | **From names to characteristics** — what quant investing *is* | ◆ home |
| 1 | — | MSFT migration: portfolios churn, so you bet on the property | ◆ ⤴ L7 |
| 1 | — | The negative control: sort on the ticker's first letter and get nothing | ◆ home |
| PC | 206 | Six sort pitfalls | ◆ |
| Demo | 277 | BM decile sort, deliberately naive; read monotonicity before the t-stat | ◆ |
| 2 | 1,006 | Equal-count deciles put 600 microcaps in the bottom bucket | ◆ home |
| 2 | — | **P4** — NYSE breakpoints; the wrong reading gives 150 not 3,106 | ◆ |
| 2 | — | **Implementation choices flip the sign**: +20.7% (t 3.94) to −6.4% (t −1.93) | ◆ home |
| 2 | — | +20.7% is real in the data and uninvestable in the world | ◆ ⤴ L16 |
| 2 | — | Negative prices: 25% of the panel, 32%/33% in the extreme deciles | ◆ home |
| 2 | — | Value under the standard convention: +5.3%, t 1.78 | ◆ home |
| 3 | 272 | **Diversification vs signal strength** — σ/√T; t peaks at 20 buckets | ◆ home |
| 4 | 322 | Infinities: two implementations, two failures, zero errors | ◆ home |
| 4 | — | Describe your signal before you sort on it | ◆ |
| 4 | — | Fixing a data bug doesn't always rescue a result | ◆ |
| HO | 268 | Replication: your t vs the published t; sample windows differ | ◆ ⤴ L9 |
| KT | 229 | 7 takeaways | ✖ by construction |

### L4 · Performance Evaluation + Factor Models · 4,095 w · 2.89 lectures

| § | w | The point | Status |
|---|---|---|---|
| 1 | 103 | Three questions, three ratios | ◆ |
| 2 | 582 | Sharpe for long-short vs long-only | ◆ |
| 2 | — | IR = active return / tracking error; the benchmark is a contract | ◆ home |
| 2 | — | **Sharpe is the IR against cash** | ◆ ⤴ §4 |
| 2 | — | Benchmark choice manufactures performance | ◆ home |
| 2 | — | Endogenous benchmark = the fitted value | ◆ ⤴ §4 |
| 2 | — | **Alpha scarce / beta plentiful — pay different prices** | ◆ home |
| PC | 202 | Six factor-regression pitfalls | ◆ |
| Demo | 945 | **Co-movement**: defensive / cyclical / levered — why a factor exists | ◆ home |
| Demo | — | `r = α + βf + ε`; the decomposition is always valid, it's just statistics | ◆ home |
| Demo | — | `E[r] = r_f + α + βE[f]`; α ≠ 0 means skill **or** a missing factor | ◆ home |
| Demo | — | Risk model vs expected-return model — two jobs, one equation | ◆ home |
| Demo | — | **P5** — total instead of excess returns doubles α | ◆ |
| Demo | — | GE: β = 1.07, so not a levered market bet | ◆ |
| 3 | 535 | σ² = β²σ²ₘ + σ²ε; variances add, volatilities don't | ◆ home |
| 3 | — | R² is not a quality measure | ◆ home |
| 3 | — | The hedged portfolio; risk budget → 50% more position | ◆ home |
| 3 | — | Hedging doesn't always improve the Sharpe ratio | ◆ home |
| 3 | — | "Beta is plentiful and cheap, alpha is scarce and dear" | ✖ repeats §2 |
| 4 | 544 | Appraisal ratio = α / σ_ε | ◆ home |
| 4 | — | **They were never three ratios** — one formula, three benchmarks | ◆ closes §2 |
| 4 | — | "Picking a performance measure IS picking a benchmark" | ✖ restates the table |
| 4 | — | Sharpe and appraisal can reverse the ranking | ◆ home |
| 5 | 406 | ARKK vs Berkshire; read the loadings before the alpha | ◆ home |
| KT | 327 | **12 takeaways** — the longest list in the block | ✖ by construction |

### L5 · Where Factors Come From, and the Zoo · 2,043 w · 1.44 lectures

| § | w | The point | Status |
|---|---|---|---|
| 1 | 226 | Three kinds of factor model: time-series / characteristic / statistical | ◆ home |
| 1 | — | A sort makes a factor; a regression consumes one | ◆ home |
| 2 | 484 | The seven families and their canonical signals | ◆ home |
| 2 | — | Risk vs mispricing — and they predict different futures | ◆ home ⤴ L9 |
| 2 | — | Deviate from the market only if you differ from the average investor | ◆ ⤴ conceptual lecture |
| PC | 180 | Five comparison pitfalls | ◆ |
| Demo | 301 | **P6** — correlate strategies, not characteristics: 0.07 vs 0.92 | ◆ home |
| 3 | 257 | Within family \|ρ\| 0.58, across 0.19 — count bets, not papers | ◆ home |
| 3 | — | 300 papers is not 300 pieces of evidence | ◆ ⤴ L9 |
| KT | 197 | 8 takeaways | ✖ by construction |

### L6 · Multi-Factor Models · 2,436 w · 1.72 lectures

| § | w | The point | Status |
|---|---|---|---|
| 1 | 209 | The ladder: CAPM → FF3 → FF5 → FF6; each factor is a long-short | ◆ home |
| 1 | — | *"Change the model, change the α"* | ✖ **pre-empts §2's reveal** |
| PC | 217 | Six multi-factor pitfalls | ◆ |
| Demo | 215 | BM's α goes 7.15% → −1.16%: we rediscovered HML and asked it to beat HML | ◆ home |
| 2 | 339 | Four signals, four stories; α can *grow* (GP loads −0.43 on HML) | ◆ home |
| 2 | — | **α is a property of (strategy, model)** — the punchline | ◆ home |
| 2 | — | Fix the model before you look | ◆ home |
| 3 | 315 | Time-series vs cross-sectional: what you supply, what you estimate | ◆ home |
| 3 | — | The slope **is** a portfolio return, from `(X′X)⁻¹X′r` | ◆ home |
| 4 | 508 | Fama-MacBeth, two steps | ◆ home |
| 4 | — | **P7** — pooling inflates t-stats 3–6× | ◆ home |
| 4 | — | The intercept is not alpha | ◆ |
| 4 | — | Characteristic-adjusted returns | ⤴ L7 |
| KT | 233 | 8 takeaways | ✖ by construction |

### L7 · Decomposing a Portfolio · 3,140 w · 2.22 lectures

| § | w | The point | Status |
|---|---|---|---|
| 1 | 307 | One regression is right only if positions *and* betas were stable | ◆ home |
| 1 | — | 13F position counts are a data artifact, not turnover | ◆ home |
| 2 | 143 | `r = α + Bf + ε` in matrix form; **`b = B′w`** | ◆ home |
| PC | 202 | Six decomposition pitfalls | ◆ |
| 3 | 264 | Top-down; print the standard errors; more factors = precision about less | ◆ home |
| 4 | 309 | Bottom-up tells you about *today*; the one-sentence rule | ◆ home |
| 4 | — | How long a window: 1–2y daily, ~5y monthly | ◆ home |
| 5 | 201 | `Ω = BΩ_fB′ + Ω_ε`; 73% factor risk; Coca-Cola is 67% of specific | ◆ home |
| 6 | 723 | Approach C: characteristic scores × premia | ◆ home |
| 6 | — | **P8** — renormalize after the merge: −16.4% vs −10.7% | ◆ home |
| 6 | — | A characteristic says what you own, not what you paid | ◆ ↪ L3 MSFT |
| 6 | — | The critique: ignores covariances; overloads microcaps; complements | ◆ home |
| 7 | 402 | Three routes, three questions; why A and B disagree | ◆ home |
| KT | 300 | 9 takeaways | ✖ by construction |

---

## Part B — The repetition audit

Cross-notebook count of markdown cells that state each concept:

| Concept | L1 | L2 | L3 | L4 | L5 | L6 | L7 | Verdict |
|---|---|---|---|---|---|---|---|---|
| self-financed / weights sum to zero | **2** | 2 | 3 | 1 | · | · | 1 | **fully derived 3×** |
| look-ahead: weights at *t*, earn *t+1* | 1 | **5** | 1 | · | · | · | · | **stated 4× inside L2** |
| EW is a small-cap bet / untradeable | · | **6** | 6 | · | · | · | 1 | overlapping in L2 |
| size premium died after Banz | · | 2 | 2 | · | 1 | · | · | ✅ proper spiral |
| alpha scarce / beta cheap | · | · | · | **5** | · | 1 | · | **3× inside L4** |
| Sharpe = IR vs cash → one formula | · | · | · | 4 | · | · | · | ✅ arc, but trim the coda |
| α depends on the model | · | · | · | 1 | · | **4** | · | **L6 §1 spoils L6 §2** |
| R² is not a quality measure | · | · | · | 4 | · | · | · | pitfall row duplicates it |
| published t vs replication | · | · | 2 | 3 | · | · | · | ✅ different jobs |
| print the SE / \|t\| > 2 | · | · | 1 | 2 | · | 3 | 1 | ✅ habit, keep |
| "code runs but is wrong" | **4** | 1 | · | · | · | · | 1 | **4× inside L1** |
| diversification vs signal strength | · | · | 1 | 1 | · | · | · | ✅ |
| value-weighting IS the market | · | 1 | · | · | · | · | · | ✅ |

### The five that are actually costing you time

**1. Self-financing is derived from scratch three times.** L1 §6 introduces it
with the mortgage analogy (the best version). L2 §4 re-derives it in the weights
table — *"they sum to zero, it costs nothing to enter, so what it returns is a
spread."* L3 §1 re-derives it again as "Step 5 is a self-financed position."
Same depth, three times. **L1 keeps the derivation; L2 and L3 get one clause
each.** ≈ 120 w.

**2. L2 states the look-ahead rule four times** — §2's "most important thing in
today's class," the Remember box, pitfall 1, the AI-Era box, and now P3's
debrief, which *proves* it with 25.5% vs 15.7%. The proof makes the assertions
redundant. **Keep §2's statement and P3; cut the pitfall-row prose and the
AI-Era box to pointers.** ≈ 150 w.

**3. L4 says "you can buy the market for five basis points" three times**
(§2, §3 twice, §4). Say it once in §2. ≈ 80 w.

**4. L6 §1 pre-announces L6 §2's punchline.** §1's Remember box says *"Change
the model, change the α. It is not a fixed property of your strategy"* — which
is exactly the reveal §2 builds to over four signals and an alpha ladder. This
is the front-loading you described: the reader is told the answer before the
evidence, so the evidence lands as confirmation instead of discovery.
**Cut the §1 box entirely.** ≈ 50 w, and the section gets *better*.

**5. L1 says "AI code runs, that's the problem" four times** — §2's Key Insight,
§5's Caution, the pitfall table's AI-Era box, takeaway 2. §2 is the home. ≈ 60 w.

### The one that is systematic

**Key Takeaways total 1,752 words across the seven** — 1.24 lectures, every word
a restatement by construction. They earn their place as a study aid, and the
calibration was fitted on notebooks that had them, so I can't argue them away on
the metric. But **L4's twelve** is an outlier (next longest is nine), and items
1+2, 4+8, and 10 duplicate each other. Capping every list at seven recovers
≈ 250 w and costs nothing.

### What is *not* repetition, and should stay

- **Banz across L2 → L3 → L5.** L2 flags it and points forward, L3 delivers the
  four-way table, L5 uses it as evidence for risk-vs-mispricing. Three different
  jobs. This is the spiral working.
- **`|t| > 2` in four lectures.** A habit, reinforced in new contexts each time.
- **MSFT migration (L3) → "what you own, not what you paid" (L7).** The second is
  the first seen from the other side, four lectures later. Exactly the kind of
  callback that pays.
- **Sharpe → IR → appraisal across L4 §2 and §4.** §2 plants the seed with a
  number the students can't yet explain; §4 closes it once a factor model
  exists. Deliberate and worth the words.

---

## Part C — Proposed trims

| # | Where | What | ≈ w |
|---|---|---|---|
| T1 | L2 §4, L3 §1 | Self-financing → one clause each, keep L1's derivation | 120 |
| T2 | L2 PC + Demo | Look-ahead: cut the pitfall prose and "general form of this bug" | 150 |
| T3 | L2 §5 + HO | Merge "EW is a small-cap bet" and "not tradeable at scale" into §4 | 100 |
| T4 | L4 §3, §4 | Drop two of the three "five basis points" restatements | 80 |
| T5 | L6 §1 | Delete the Remember box that spoils §2 | 50 |
| T6 | L1 PC | AI-Era box → pointer to §2 | 60 |
| T7 | L4 §4 | Cut the "picking a measure IS picking a benchmark" coda | 70 |
| T8 | all | Cap every takeaway list at 7 items | 250 |
| T9 | L4 KT | Merge takeaways 1+2, 4+8; drop 10 | (in T8) |
| | | **total** | **≈ 880** |

That is **0.62 of a lecture** — real, but it does not solve the capacity problem
on its own. The block is at 15.3 lectures in 7 slots; trimming repetition gets it
to ≈ 14.7. **Repetition is not why L1–L7 is long.** It is long because L3 §2 is
1,006 words, L4's demo is 945, and L7 §6 is 723 — three sections that are each
most of a lecture on their own. Cutting scope, not prose, is the lever, and that
is a curriculum decision rather than an editing one.
