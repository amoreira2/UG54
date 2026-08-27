# L16 + L17 Joint Redesign — Performance Evaluation × Capital Allocation

**Status:** Design doc for review (not yet built). Once approved, build per PLAN.md §8.
**Scope:** Rebuild L16 (Performance Evaluation) and L17 (Capital Allocation II)
as a single integrated 2-lecture unit. Capital Allocation I (L7) stays where it
is — these two lectures call back to it.
**Spine:** Ken Griffin / Citadel multimanager "pod shop" + the buyside
alpha-capture program. One running example that makes the nesting concrete.
**Last updated:** 2026-06-03

---

## 1. The one idea

A pod shop's entire business is two steps run in a loop:

> **(1) grade PMs → (2) size bets on them → (3) re-grade, re-size, fire Dave.**

Step 1 is **performance evaluation**. Step 2 is **capital allocation**. They are
*nested*: you cannot size what you cannot evaluate, and the only reason to
evaluate is to size. The alpha-capture program is the same loop applied to
*rented* signals instead of in-house PMs — which is why it makes Citadel money:
it buys **breadth** without buying headcount.

This is the thread that ties the whole unit together, and it converts two
abstract estimation lectures into one concrete business problem the students
can hold in their heads.

Levine's two sentences map exactly onto the two lectures:

| Levine | Lecture | Concept |
|--------|---------|---------|
| "edge ∝ skill × number of independent decisions" | **L17** | Fundamental Law: IR = IC·√BR |
| "they know how confident they are; you know how confident they *should* be" | **L16** | shrinking a self-reported track record toward zero by its t-stat |

The handoff between the lectures is a single object: **L16 produces a shrunk,
honestly-graded alpha for each PM; L17 consumes those as the `μ` it sizes on.**

---

## 2. How it fits PLAN.md

- **Schedule:** no change to slots. L16 (Mon Nov 2) = Lecture A; L17 (Wed Nov 4)
  = Lecture B. Both are currently ⚠️ Draft in §10 — this is their rebuild pass.
- **Callbacks to Capital Allocation I (L7, ✅ built), reused, not re-taught:**
  - single-asset weight `w* = μ/(γσ²)` and vol allocation `w*σ = SR/γ`
  - MVE weights `W = Σ⁻¹μ`
  - **Sharpe-Pythagoras** `SR² = SR₁² + SR₂²` for uncorrelated bets — this is
    the seed of the Fundamental Law, so L17 is literally "Cap Alloc I, but with
    N PMs and estimation error."
  L17's cold open should explicitly say "remember Sharpe-Pythagoras from L7?"
- **No redundancy:** L7 derives the optimizer assuming you *know* μ and Σ.
  This unit is about where those numbers come from (L16) and what breaks when
  they're estimated (L17). Clean division of labor.
- **Conventions honored:** standard 75-min arc (§3), notebook anatomy (§4),
  paste-token submission (§5), 6–8-item pitfall checklist, 2 live AI moments,
  single scenario challenge, drop-the-hype tone (§1).

---

## 3. Lecture A — "Evaluating the Talent" (L16, Performance Evaluation)

**Core narrative (the one thing to remember):** a track record is a noisy
estimate of skill. Grading it means (a) stripping out factor beta that isn't
skill, and (b) discounting what's left by how uncertain it is. *That discount
is the edge a good allocator has over the PM pitching to them.*

### 75-min arc (§3 micro-structure)

| Phase | Content |
|-------|---------|
| Cold open (3) | The Bloomberg alpha-capture story. "Citadel will pay outside managers for their trade signals. Why would a $60B fund buy other people's ideas? Because their edge isn't ideas — it's *grading* ideas." |
| Motivate (12) | The pod-shop loop. Today = step 1: how do you grade a PM? Set up the alpha-attribution regression (CAPM→FF3→FF6). |
| Pitfall checklist (5) | 6 items (below). |
| Live AI #1 (12) | **Specify → Implement → Validate**: regress a real fund (ARKK) on FF6, audit the output. Is the "alpha" real or just small-cap/growth beta? |
| Concept (8) | "Is it real?" — Sharpe standard error (Lo 2002) and the alpha t-stat. Short track records → wide CIs. |
| Live AI #2 (12) | Regress Berkshire (BRK) on FF6 → genuine residual alpha (quality/low-beta tilt the 6 factors miss). Contrast with ARKK. |
| Concept (8) | **Statistical shrinkage** — the handoff. Pull α̂ toward zero by its t-stat (rule below). Distinguish from benchmark re-attribution. |
| Challenge (18) | Grade a pitched PM (synthetic). See §5. |
| Wrap (4) | Two takeaways: "alpha shrinks twice — once for beta, once for noise"; "the shrunk alpha is what tomorrow's lecture sizes." Preview L17. |

### Content KEPT (from the draft + What-Is-Alpha that already mined L16)
- Multifactor alpha attribution (CAPM/FF3/FF6); "alpha shrinks as you add factors."
- ARKK (fake alpha = factor beta) and Buffett (real alpha) cases — these are the
  vivid hands-on hooks; keep both.
- Sharpe standard error and the alpha t-stat as the "is this real?" test.
- The honesty pitfalls: survivorship, multiple testing, sample cherry-picking.

### Content CUT or COMPRESSED (to make room for the spine)
- Drop the standalone "overfitting / in-sample vs OOS" mini-section as its own
  beat — fold it into the multiple-testing pitfall (one line: "in-sample Sharpe
  is the ultimate multiple-test winner").
- Bonferroni mechanics → mention as a one-liner, don't derive.
- Keep the regression itself entirely in the AI-demo cells (don't teach OLS
  again; L4/L5 did that).

### Pitfall checklist (6 items)
1. **Single-factor benchmark** — "alpha" that's just size/value/momentum loading. Detect: always run FF6, watch α collapse.
2. **Sample-period cherry-picking** — report sub-period alphas, not one number.
3. **Survivorship in the PM universe** — grading only survivors inflates average skill 1–2%/yr. Detect: is the dead PM in your sample?
4. **Multiple testing** — 500 PMs → ~25 fake stars at p<0.05. The pitched track record is *self-selected* to look good.
5. **Sharpe SE units** — compute SE in the *return frequency* used, then annualize SE by √12. Mixing frequencies is the classic silent bug.
6. **t-stat ≠ economic size** — a t=3 on 0.1%/yr alpha is real but worthless; a t=1 on 8%/yr is huge but unproven.

### The shrinkage rule we teach (classroom version)
Two different things both get called "shrinkage" — separate them explicitly:

- **(a) Benchmark re-attribution:** α falls as you add factors (CAPM 8% → FF6
  2%). This is *not* shrinkage — it's correctly reclassifying beta as not-alpha.
- **(b) Statistical shrinkage (the handoff):** even the FF6 α̂ is noisy. Best
  estimate of *true* skill pulls it toward zero:

$$\tilde\alpha = \hat\alpha \cdot \max\!\left(0,\; 1 - \tfrac{1}{t^2}\right), \qquad t = \hat\alpha / \text{SE}(\hat\alpha)$$

This is a James–Stein–flavored heuristic, defensible and *teachable*: a t≈2
alpha is cut ~25%; a t≈1 alpha collapses to ~0. It ties the discount directly
to the t-stat, which *is* "knowing how confident they should be." (Flag in the
notes that this is one convenient rule, not the unique Bayesian answer — the
fuller normal-normal posterior is an aside.)

---

## 4. Lecture B — "Sizing the Bets" (L17, Capital Allocation under Uncertainty)

**Core narrative:** given a roster of graded PMs, how many dollars on each? Two
forces fight: **breadth** (more independent bets → higher Sharpe) pushes you to
add PMs; **estimation error and crowding** push you to bet less than the
formula says. The optimizer `W = Σ⁻¹μ` handles both — if you feed it shrunk
inputs and an honest Σ.

### 75-min arc

| Phase | Content |
|-------|---------|
| Cold open (3) | Back to Citadel: "You graded Alice, Bob, Claire, Dave yesterday. Now — how many dollars on each, and why does adding a *mediocre* fifth PM still make Griffin richer?" |
| Motivate (12) | **More independent bets → higher Sharpe.** Straight implication of Sharpe-Pythagoras (L7): N independent equal-skill PMs → `SR_combined = √N · SR_individual`. So doubling your roster of *uncorrelated* PMs multiplies Sharpe by √2 — why pod shops scale and why alpha capture exists: buy independent bets cheaply. *(Note: people sometimes call this the "Fundamental Law of Active Management," written `IR = IC·√BR` where BR = number of independent bets.)* |
| Pitfall checklist (5) | 6 items (below). |
| Live AI #1 (12) | Specify→Implement→Validate: equal-weight-combine the PM panel, compute combined Sharpe, compare to √N prediction. Audit: does it match? If not, why (correlation)? |
| Concept (10) | **Correlation cancels the √N gain.** If PMs are correlated (ρ), the combined Sharpe stops growing: it behaves like only `N/(1+(N−1)ρ)` independent PMs, which →1/ρ as N→∞. The crowded pair counts as ~one PM. This is exactly what Σ in `W = Σ⁻¹μ` already encodes. *(Note: that count is sometimes called "effective breadth.")* |
| Live AI #2 (12) | Plug-in `W = Σ̂⁻¹μ̂` on the panel → absurd leverage. Then feed *shrunk* μ (from L16's rule) + shrunk Σ → sane weights. Audit the difference. |
| Concept (8) | **Bet less than the formula says.** Because μ̂ is noisy, shrink it toward zero (mean shrinkage, already taught), so the weight `w = μ̃/(γσ²)` comes down — equivalently, a noisier estimate means a higher effective γ. Biasing toward zero is cheap; over-betting is not. *(Note: taking a fixed fraction of the raw plug-in weight is sometimes called "fractional / half-Kelly.")* |
| Challenge (18) | Size the roster + fire decision (synthetic). See §5. |
| Wrap (4) | Close the loop: "evaluation set the μ, allocation set the W, next quarter you re-grade and fire Dave." The pod-shop loop, complete. |

### Content KEPT
- Estimation-error fragility of `W = Σ⁻¹μ` (plug-in over-betting).
- Shrinkage of μ (James–Stein / toward grand mean) and Σ (Ledoit–Wolf, stated as a closed form, not derived).
- Robust sizing via mean shrinkage of μ̂ (equivalently, a larger γ in `w = μ̃/(γσ²)`); backtest Sharpe overstates OOS, so discount it.

### Content ADDED (the spine; this is the new center of gravity)
- The √N result — combined Sharpe grows with the number of *independent* bets
  (taught as a direct implication of L7's Sharpe-Pythagoras, with the
  "Fundamental Law / IR = IC·√BR" name relegated to a side note).
- How correlation cancels that gain — the rigor payoff; "independent" is the
  load-bearing word (the "effective breadth" name kept as a side note only).

### Content CUT or COMPRESSED
- **Black–Litterman** (draft LO #3): cut to a single sentence ("mixing a prior
  with views is the same shrinkage idea, formalized") — don't teach the
  machinery. It's an aside, not core, and the t-stat shrinkage rule already
  delivers the intuition.
- Transaction-cost penalty in the optimizer → one pitfall-table line; the full
  treatment lives in L20 Implementation.
- Condition-number / singular-Σ mechanics → keep as a pitfall line, not a section.

### Pitfall checklist (6 items)
1. **Plug-in optimization** — using μ̂ as if it were μ → wild leverage. Detect: |w| > 2.
2. **Correlation ignored ("counting crowded bets as independent")** — √N only holds at ρ=0; check the off-diagonals before claiming breadth.
3. **Near-singular Σ** — N assets need T ≫ N²; condition number > 100 → unstable inverse → shrink Σ.
4. **No shrinkage on μ** — un-shrunk alpha sizes the lucky fake star largest. Feed L16's shrunk α.
5. **Backtest-Sharpe optimism** — the in-sample optimal weights look great in-sample by construction. Discount.
6. **Ignoring costs/turnover** — optimal weights demand 100% turnover (→ L20).

---

## 5. Shared dataset — one synthetic pod shop, used by both lectures

A single seeded generator produces a panel of monthly PM returns plus the
factor returns they were built from. **L16 grades the PMs; L17 sizes the
survivors.** Reusing one dataset across both lectures is what makes the
nesting tangible.

**`build_podshop_challenge_data.py` → `assets/data/podshop_AI_challenge.csv`**
(+ `podshop_factors_AI.csv` for the attribution regressions). Seeded, no web
fetch, so the belt-and-suspenders appendix is N/A (document the seed instead).

Roster designed so each pitfall has a poster child:

| PM | True α | Truth | Teaching role |
|----|--------|-------|---------------|
| Alice | +4%/yr, t≈2.5 | real skill | the keeper; survives shrinkage |
| Bob | +2%/yr, t≈1.8 | marginal | shrinks a lot; "fund small" |
| Claire | 0, but high in-sample SR over short history | **lucky fake star** | multiple-testing / shrinkage hard to ~0 |
| Dave | slightly negative | the **fire** | the re-allocation decision |
| Erin & Frank | each +3%/yr but ρ(Erin,Frank) ≈ 0.9 | **crowded pair** | effective-breadth collapse |
| Grace | +3%/yr but only 18 months of data | short history | wide Sharpe SE |
| (Heidi) | blew up / removed mid-sample | **survivorship** | only appears in the "full" file, not the "surviving" file |

Construction: simulate FF-style factor returns, give each PM a beta vector +
true α + idiosyncratic noise so an FF6 regression recovers (β, α̂, t) cleanly.
Calibrate noise so Claire's *realized* in-sample Sharpe is tempting but her
t-stat is weak — that's the whole lesson.

### Challenge A (L16) — "Grade the roster"
Required outputs (variable-stub pattern, §4):
```python
arkk_ff6_alpha   = ____   # annualized, from the demo fund
claire_t_stat    = ____   # the lucky star's alpha t-stat
claire_alpha_shrunk = ____   # apply the (1 - 1/t²) rule → ~0
n_real_skill     = ____   # how many PMs survive shrinkage (alpha_shrunk > 0)
MEMO             = "..."  # which PMs are real, which are noise, and why
```
Memo rubric (Pattern C, §5): rewards naming Claire as a multiple-testing
artifact, citing the t-stat (not the raw Sharpe), and flagging survivorship.

### Challenge B (L17) — "Size the roster + fire decision"
Builds directly on A's shrunk alphas.
```python
sr_equal_weight  = ____   # combined Sharpe, equal-weight across survivors
sr_sqrt_n_pred   = ____   # √N · avg individual Sharpe (the naive prediction)
breadth_effective = ____  # N/(1+(N-1)ρ) using the Erin/Frank crowding
w_plugin_max     = ____   # max |weight| from plug-in Σ⁻¹μ̂ (shows over-betting)
w_robust_alice   = ____   # Alice's weight using shrunk μ̃ (smaller, sane)
fire_dave        = ____   # 1.0 / 0.0
MEMO             = "..."  # the allocation + who to fund/fire and why
```
Memo rubric: rewards explaining why equal-weight Sharpe falls short of √N
(crowding), why plug-in over-bets, and sizing on *shrunk* not raw alpha.

---

## 6. Build deliverables (after approval, per PLAN §8)

| File | Purpose |
|------|---------|
| `build_perf_eval_ai_notebook.py` → `PerformanceEval_AI.ipynb` | rebuild Lecture A |
| `build_cap_alloc_ii_ai_notebook.py` → `CapitalAllocationII_AI.ipynb` | rebuild Lecture B |
| `build_podshop_challenge_data.py` → `assets/data/podshop_AI_challenge.csv` (+ factors) | shared dataset |
| `PerformanceEval_AI_runsheet.md`, `CapitalAllocationII_AI_runsheet.md` | run sheets (§3 timing) |
| `auto_evaluator.py` entries: `PerfEval_AI`, `CapAllocII_AI` | answer keys + memo rubrics |

Keep existing filenames (`PerformanceEval_AI.ipynb`, `CapitalAllocationII_AI.ipynb`)
to avoid churn; the rebuild overwrites the drafts. ARKK/BRK + FF6 in the demo
cells get the belt-and-suspenders appendix (§1); the synthetic challenge data
does not need it.

---

## 7. Open questions before building

1. **ARKK/BRK real data vs fully synthetic cases.** Real names are more vivid
   but add a yfinance/Ken-French fetch (mitigated by the appendix). I lean
   real for the *demo* cases, synthetic for the *graded* challenge. OK?
2. **γ (risk aversion) convention** across L7/L16/L17 — keep γ=3 annual as in
   the Cap Alloc I draft, for continuity?
3. **Scrub "Kelly" from the existing L17 draft.** Robust sizing is taught only
   via mean shrinkage of μ̂ + the `w = μ̃/(γσ²)` formula already in Cap Alloc I.
   The draft's "Fractional Kelly" section gets removed. (Confirmed direction —
   noting it here so the build does it.)
4. **Survivorship PM (Heidi):** include the two-file (full vs surviving) device,
   or is that one pitfall too many for a 75-min slot? I lean keep — it's the
   most underappreciated bias and the dataset makes it free.
