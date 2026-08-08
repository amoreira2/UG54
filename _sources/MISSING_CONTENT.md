# Content from the pre-AI notebooks — placement tracker

**Purpose:** the pre-AI notebooks contain analysis and intuition that did not
survive the rebuild into L1–L3. This file tracks every item, where it should
land, and whether it's back in. Update the Status column as things get included.

**Last updated:** 2026-08-08

**Status:** ☐ not yet · ◐ in progress · ☑ included

The pattern behind most of these: the rebuild preserved **mechanics** and cut
**motivation**. L2 knew how to compute `w′r` but never said why portfolios
exist; L3 knew the sort recipe but not why sorting works.

---

## Tier 1 — conceptual losses, placed

| # | Item | Source | Goes to | Status |
|---|------|--------|---------|--------|
| 1.1 | **Markowitz: risk is what an asset adds to your mix, not its standalone vol.** Sugar analogy; "1% position going to zero costs you 1%"; *"how risky is an asset depends on the portfolio of whoever is asking."* | `PortfolioMath_c` c3–5 | **L12 Capital Allocation I — opening** | ☐ |
| 1.2 | ☑ **The MSFT migration narrative.** Small in the 80s → giant in the 90s → low BM in the tech boom → high BM after the crash → low again with AI. Why sorting works: portfolios churn as firms change, so you bet on characteristics, not names. | `crosssectional` c27, c37 | **L3** — in the sort recipe | ☑ |
| 1.3 | ☑ **Diversification vs signal strength.** Why 10 deciles and not 100, or not just the single highest-signal stock. *"Individual stocks have σ = 40–80%, so σ/√T makes E(R) nearly unmeasurable."* Justifies the entire decile methodology. | `crosssectional` c41 | **L3** §"Why Ten Buckets?" | ☑ |
| 1.4 | ☑ **"From names to characteristics."** *"Instead of betting on Apple because it's exposed to tariffs, build a tariff-exposure characteristic."* Defines what quant investing is, in one sentence. | `crosssectional` c27 | **L3** — with 1.2 | ☑ |
| 1.5 | ☑ **The market-cap portfolio needs no rebalancing** — weights drift with prices automatically. This is *why* index funds work. | `crosssectional` c7 | **L2** §"And it costs nothing to maintain" | ☑ |

---

## Tier 2 — homeless, looking for a home

Real content, no obvious slot yet. Several would work well as assignment
material rather than lecture time.

| # | Item | Source | Candidate home |
|---|------|--------|----------------|
| 2.1 | **Log returns vs simple returns** — absent from L1–L3 entirely | `IntrotoReturns_c_AI` | Appendix ch. (§ below) or L1 if room |
| 2.2 | **Annualization caveat** — mean scaling is exact only for log returns; variance scaling needs log *and* iid | `IntrotoReturns_c` c19 | Appendix ch. (with 4.1) |
| 2.3 | **"Subtracting a constant barely moves volatility — but the risk-free rate is *risk-free*, should it change variance at all?"** Socratic, good | `IntrotoReturns_c` c29 | L1, cheap to add |
| 2.4 | **First return is always NaN** — you lose one observation | `IntrotoReturns_c` c12 | L1 or appendix |
| 2.5 | **Empirical VaR** — 5th percentile, worst day, dollar loss | `IntrotoReturns_c` Ex. 3 | L2 (next to distributions), or **L19 Risk Mgmt** |
| 2.6 | **Rolling analysis** — rolling Sharpe and volatility | `IntrotoReturns_c` Ex. 4 | Assignment, or L10 (conditional strategies) |

---

## Tier 2b — needed for Capital Allocation

All from `PortfolioMath_c`. The first three are **required** before L12 can do
mean-variance properly.

| # | Item | Goes to | Status |
|---|------|---------|--------|
| 2b.1 | **Long-only / short / leveraged taxonomy**, with the risk-free weight separated: `Σwⱼ + w_rf = 1`, so risky weights can exceed 1 | **L12** | ☐ |
| 2b.2 | **`R_p = W′Rᵉ + r_f`** — the excess-return representation, and why risky weights need not sum to one | **L12** | ☐ |
| 2b.3 | **`E[R_p] = W′E[R]`** — linearity of expectations | **L12** | ☐ |
| 2b.4 | The `@` operator for matrix multiplication (currently 1 mention in L2) | Appendix ch. | ☐ |

---

## Tier 3 — data traps students will actually hit

| # | Item | Goes to | Status |
|---|------|---------|--------|
| 3.1 | **The `groupby` + `shift` trap.** *"Shift the first month of security n and you get the last month of security n−1."* Our `ret_fwd` column sidesteps this — which means students never learn it, then hit it the first time they build their own signal. | **L2** — alongside `ret_fwd` | ☑ |
| 3.2 | **Negative prices.** **Verified: 25.4% of our panel** (384,715 rows, 12,105 stocks, 94% NASDAQ). CRSP flags a bid/ask midpoint when the stock didn't trade on the last day of the month — so the "price" isn't transactable. Median mktcap $10.8M vs $102.5M. **They cluster in the extremes: 31.9% of BM D1 and 33.2% of D10, vs ~16% mid-deciles.** A third of both legs of a long-short never traded. | **L3** §"the extremes didn't trade" | ☑ |
| 3.3 | **Build an S&P-500-like index** (value-weight the top 500 by market cap each month). | **Assignment** — construct it as the benchmark for the group's own information ratio | ☐ |

---

## Tier 4 — the Appendix chapter (new)

A chapter of short reference notebooks students can consult, not lectured. Home
for material that is genuinely useful but doesn't earn a lecture slot.

| Notebook | Content | Source |
|---|---|---|
| ☑ **`SignalHygiene_AI.ipynb`** | Winsorize, z-score within month, and **combining two signals**. Built 2026-08-07, executes clean. Referenced from L3 and A1. | moved out of L3 |
| ☐ **Choice of frequency** | Exact vs approximate annualization; groupby aggregation to annual/quarterly; when the approximation breaks; best/worst-year analysis | `TheChoiceofFrequency_c.ipynb` — **entire notebook, orphaned, no AI version exists** |
| ☐ **Matrix algebra for portfolios** | The `@` operator, `W′R`, `W′ΣW`, why matrix form beats loops | `PortfolioMath_c` c14, c20 |
| ☐ **Log vs simple returns** | Definitions, when each is right, the annualization consequences | 2.1, 2.2 above |

---

## Deliberate deferrals — not losses

- Portfolio **variance, covariance, diversification, the frontier** → L12. See the
  ordering note below.
- **Correlation across different long-shorts** → L25 (crowding), where it's the
  whole point rather than an aside.
- **Appraisal ratio** → L4, once a factor model provides alpha.

---

## Resolved question: where does portfolio variance go?

**The algebra must be at L12, not L14.**

`W′ΣW`, diversification, and the frontier are **prerequisites** for
mean-variance optimization — you cannot derive `W = Σ⁻¹μ` without them. L12 is
Capital Allocation I; L14 is BARRA. L12 comes first, so the algebra cannot wait
for BARRA.

The clean division:

| Lecture | What it covers |
|---|---|
| **L12** | The **algebra** — `W′ΣW`, diversification, the frontier, then MVE and tangency |
| **L14** | How you actually **estimate** Σ — `XFX′ + Δ`, winsorization, specific risk, shrinkage |
| **L17** | What Σ's **structure** looks like — PCA, the noise floor |

**The cost:** L12 has to open with ~20 minutes of variance algebra before it
gets to allocation, on top of items 1.1 and 2b.1–2b.3 above. That is a heavy
lecture and it needs watching when we build it.

**One option worth considering:** put the *two-asset* variance case in L2 —
`Var = w₁²σ₁² + 2w₁w₂σ₁₂ + w₂²σ₂²` — and leave the N-asset matrix form for L12.
L2 already shows EW volatility at 18.6% vs VW at 15.5% without explaining why,
which is a diversification fact begging for the formula. Costs L2 about 6
minutes, which it currently doesn't have.


---

> **⚠️ 2026-08-08: Tier 5c and 5d.1 below are STALE.** L7 (portfolio
> decomposition) now teaches `r = α + Bf + ε` in matrix form, `b = B′w`,
> `Ω = BΩ_f B′ + Ω_ε`, the factor/specific variance split, **and** bottom-up vs
> top-down. L13 (Capital Allocation I, formerly L12) therefore *uses* that
> algebra rather than introducing it — which buys L13 back the ~20 minutes the
> note at the bottom of this file was worried about. See `L1_L7_AUDIT.md` §1b.

## Tier 5 — L4–L6 audit (2026-08-07)

Cross-checked against **EQI Ch. 3** (the reading Columbia assigns for these
sessions) and against `FactorModels_c`, `MultiFactorModels_c`,
`InterpretingFactorModels`.

### 5a. Decided: SKIP

| # | Item | Why |
|---|------|-----|
| 5a.1 | **Alpha spanned vs alpha orthogonal** (EQI §3.3) | The identification story only bites when factors are *not* traded, and Paleologo's own factors are tradable by construction (Ch. 6 factor returns are FMPs; Ch. 7 are eigenportfolios). The decomposition's real work is mechanical — he needs `B'α⊥ = 0` so the factor term drops out of `w'r` and the √n Sharpe bound goes through. Stripped of that, it restates APT with a projection. **Skipped.** |

### 5b. Single-asset + multi-factor — DO NOW

These need no multi-asset machinery; they work with one return series and
several factors.

| # | Item | Source | Goes to | Status |
|---|------|--------|---------|--------|
| 5b.1 | ☑ **Risk model vs expected-return model** — the two things a factor model is for | `FactorModels_c` | **L4** | ☐ |
| 5b.2 | ☑ **Alpha/beta as how the industry is organized** — alpha is scarce and dear, beta is plentiful and cheap | `FactorModels_c` | **L4** | ☐ |
| 5b.3 | ☑ **Hedged portfolio + risk budget / position sizing under a vol budget** — the practical payoff: hedging lets you hold more | `FactorModels_c` | **L4** | ☐ |
| 5b.4 | ☑ **ARKK / Cathie Wood vs Buffett** — the fake-alpha / real-alpha pair, on real funds | `MultiFactorModels_c` c14+ | **L4** (also claimed by the L16/L17 design doc — decide) | ☐ |
| 5b.5 | ☑ **"Endogenous" benchmarking** — benchmark = Σβⱼfⱼ, the fitted value. **Closes a loop: IR against the endogenous benchmark IS the appraisal ratio**, so Sharpe / IR / appraisal become one formula with three benchmarks (cash / mandate / fitted). | `MultiFactorModels_c` c8 | **L4** | ☐ |
| 5b.6 | ☑ **Characteristic-adjusted returns — the CONCEPT.** "Hedging, but with characteristics instead of time-series betas." Completes L6's time-series/cross-sectional symmetry. | `MultiFactorModels_c` c48 | **L6**, short closer after Fama-MacBeth | ☐ |

### 5c. Multi-asset — DELAY to Capital Allocation

Deliberately postponed. All of it needs the portfolio/matrix view.

| # | Item | Goes to |
|---|------|---------|
| 5c.1 | `r = α + Bf + ε` in matrix form across many assets | **L12** |
| 5c.2 | **`Ω = BΩ_f B′ + Ω_ε`** — the covariance decomposition | **L12** (note: EQI puts it in Ch. 3, i.e. at the foundations) |
| 5c.3 | **Portfolio factor exposures `b = B′w`** | **L12** |
| 5c.4 | `PnL = Factor PnL + Residual PnL`; % idio variance as a monitored statistic | **L12** |
| 5c.5 | Marginal contribution to risk; Sharpe-ratio sensitivity | L14 or skip |

### 5d. Needs a home, later

| # | Item | Note |
|---|------|------|
| 5d.1 | ☑ **Bottom-up vs top-down decomposition** | **Done — L7 §3–4 (2026-08-08).** |
| 5d.2 | **Characteristic-adjusted returns — the CRITIQUE**: ignores covariances (characteristic-neutral ≠ factor-neutral); OLS overloads small stocks; fix by WLS on market cap or restrict to the largest 20% | **L14** — this is BARRA construction practice |

### 5e. A conceptual / theory lecture, late in the term

**Decided: build one, toward the end.** `InterpretingFactorModels.ipynb` is the
skeleton and it is entirely absent from L4–L6 today:

- The academic view vs the practitioner view
- **"Deviate from the market only if you are different from the average investor"**
- Risk in bad times as the economic story for why a premium exists
- CAPM as a special case of equilibrium reasoning
- What to do *after* you find alpha, or after you reject the model
- Equilibrium thinking as a guard against overfitting

This is the half of the argument Paleologo does not supply — he gives machinery,
not a reason to expect a premium to exist. Without it the factor zoo in L5 is a
list of things that happened to work. L5's "risk vs mispricing" section is
currently posed as a dichotomy with no equilibrium argument behind the risk side;
that section should point forward to this lecture.

### Deliberate skips from EQI Ch. 3

Rotations / projections / push-outs (§3.4), Frisch-Waugh-Lovell (§3.7.3),
marginal contribution to risk. All need linear algebra our students don't have;
Columbia can assume Strang.

---

## Build log

**2026-08-07 — Tier 1.2–1.5 and Tier 3.1–3.2 included.** All verified by
executing the notebooks.

- **L3 "Why Ten Buckets?"** turned out sharper than the original claim. Spread
  rises monotonically with bucket count (16.3% at quintiles → 28.7% at 50), but
  the **t-stat peaks at 20 buckets (7.2) and then falls to 6.7**. Deciles sit
  essentially at the top of the curve. The trade-off is visible in four lines of
  output rather than asserted.
- **L3 negative prices**: 25.3% of the panel, median market cap $10.9M vs
  $102.8M, and U-shaped across deciles — 31.9% of D1 and 33.2% of D10 vs ~16%
  mid. Printed as a bar chart.
- **L2 shift trap**: demonstrated live on the seam between permno 10000 and
  10001, showing `naive` reaching across into the next company's first return
  while `grouped` correctly returns NaN.
- Cleaning the infinities from `BM` also lengthened the L3 value demo from 228
  to 251 usable months (spread 20.8%/yr, t = 7.05).

**2026-08-07 (later) — signal hygiene moved to the Appendix.**
`chapters/Appendix/SignalHygiene_AI.ipynb`, 14 cells, executes clean. It gained
the section it never had room for in L3: **combining two signals**. Value alone
Sharpe 0.34, profitability alone 0.58, **the two averaged as z-scores 0.78** —
and the two long-shorts are **negatively correlated (−0.26)**, so the
combination has lower volatility than either input while earning more than both.
That also answers a question the pre-AI cross-sectional notebook posed and left
hanging: *"How do you buy profitable firms at a good value, like Warren likes?"*

**Time cost after the move:** L2 ~87 min, L3 ~83 min, against 75-minute slots.

---

## Open: L2 and L3 are over capacity

| | budgeted | now |
|---|---|---|
| L1 | 75 | 75 ✅ |
| L2 | 75 | **~87** |
| L3 | 75 | **~83** (was 99) |

The L1–L3 block has 225 minutes and now wants ~261. Options, roughly in order of
how much I'd recommend them:

1. ☑ ~~Move L3 §"Signal hygiene" (8 min) to the Appendix chapter~~ — **done**.
2. ☑ ~~Move L3 §5 (Sharpe / information ratio) to L4~~ — **done**. L4 is now
   *Introduction to Performance Evaluation + Factor Models I*. The moved section
   is parked at `/tmp/l3_measurement_section.py`; fold it into the L4 build.
3. **Trim the L2 "where this data comes from" section** — it is pure lecture
   with no code and could lose 3–4 minutes.
4. **Accept that this block is 4 lectures, not 3**, and push factor models back
   one slot. This is the honest reading of the content, but it cascades through
   the whole calendar.


---

## Lecture length — the calibration that replaced my guesses

Fitted to the **realized** Spring 2026 allocations (Timing 2, Factor Models 2,
Capital Allocation 2, Estimation 3, Cross-Sectional 2, Momentum 1, Multifactor
1; ML and LLMs dropped as atypical), counting lectured markdown only —
exercises, challenges and appendices excluded on both sides.

**≈ 1,400 lectured words = one 75-minute lecture.** CV 0.34, range 685–2,208.

Code lines have **zero** predictive power (Momentum: 69 lines, one lecture;
Multifactor: 238, one lecture). Neither do cells or equations. A search over
`words + a·code + b·eqs` returns a = 0.

Current state of the built notebooks, at ~1,400 words/lecture:

| | lectured words | implied lectures |
|---|---|---|
| L1 | 2,689 | 1.90 |
| L2 | 2,965 | 2.09 |
| L3 (after moving Sharpe/IR out) | 3,198 | 2.26 |

**The three lectures carry ~6.3 lectures of prose.** The structure, demos and
findings are right; the exposition is roughly 2× too long. The fix is
compression, not cutting sections — my words-per-code-line ratio is 2–4× the
historical notebooks'.


---

## Build log — 2026-08-08 (L1–L7 audit and correctness pass)

Full findings in `chapters/Finance/L1_L7_AUDIT.md`. Applied today:

**Blockers**
- **`ff_monthly.csv` built** — FF5 + Mom + RF, monthly, 1980–2025, decimals, 558
  rows. Three appendices cited it as the belt-and-suspenders fallback and it did
  not exist.
- **L5's `glob.glob()` on an HTTPS URL** returned `[]`, so `SIGS` was empty and
  the correlation matrix, heatmap, within/across split, Hands-On and the entire
  Challenge silently produced nothing. Now `SIGS = sorted(menu.Acronym)` — the
  menu *is* the directory listing. Verified: 29 strategies, 251 common months,
  within |ρ| 0.579 vs across 0.189, exactly as the lecture text claims.
- **The data layer is still untracked.** Every notebook loads from
  `raw.githubusercontent.com/…` and every one of those URLs 404s.

**Correctness**
- **Renumbered 13 cross-lecture references.** Inserting L7 shifted everything
  after it by one; none of the notebooks had been updated. L3's
  backtesting/anomalies pointer is now written topic-first so it survives the
  next reshuffle.
- **The BM convention mismatch.** L3's Live Demo showed +20.76%/yr (t = 7.05)
  from `qcut` + equal weights, while L4, L5 and L6 all assumed the standard
  +5.27%/yr (t = 1.78). L6 explicitly attributed 5.27% to "Lecture 3," which
  Lecture 3 never displayed. **L3 §2 now closes the loop** — three cells that
  re-run value under NYSE breakpoints and value weights and state that 5.3% is
  the number the rest of the course uses. L4 names the convention at the point
  it switches.
- **L7 no longer uses the Fin418 fund pickle for Berkshire.**
  `df_WarrenBAndCathieW_monthly.pkl` spans 398 months and contains **279**,
  dropping scattered single months; over 1995–1999 that left **41 of 60** and
  quietly inflated every standard error in §3 — in the section whose whole point
  is that the standard errors are large. Berkshire is **permno 17778** in the
  course panel, complete, 252 months. Swapped, and §3, §7, the pitfall table and
  takeaway 4 were rewritten on the new numbers.

**What changed in L7's results**

| | old (41 mo, pickle) | new (60 mo, panel) |
|---|---|---|
| CAPM β | 0.68 (se 0.26) | **0.78 (se 0.22)** |
| FF6 Mkt-RF | 0.62 (se 0.35) | **1.09 (se 0.29)** |
| FF6 HML | +2.08 (se 0.61) | **+0.83 (se 0.52)** |
| FF6 CMA | −2.20 (se 1.01) | **+0.07 (se 0.70)** |
| loadings inside 2 SE | 4 of 6 | 5 of 6 |

The dramatic HML/CMA collinearity artifact was **partly a symptom of the missing
months**. The teaching point survives and is arguably better: the market loading
moves from 0.78 to 1.09 purely from adding five regressors, and the top-down
CAPM beta (0.78, se 0.22) sits only ~1.4 SE from the bottom-up 1.08 — so the two
routes are economically different and statistically indistinguishable, which is
a more honest thing to say than "they disagree." Bottom-up, the risk split
(73% factor) and Approach C are unchanged; the Challenge answer key is
unaffected because it runs off the panel.

**Verified:** all seven notebooks execute end to end against local data —
L1 6 cells, L2 11, L3 14, L4 10, L5 6, L6 6, L7 8 (blanks, submission and
appendix cells skipped).

**Still open:** language borrowings (§3 of the audit), content gaps M1–M11, and
the eight prompt-it moments (§4).
