# L1–L7 audit — content, language, sequence, and prompt-it moments

**Date:** 2026-08-08
**Scope:** `L1_Welcome_Returns_AI` … `L7_Portfolio_Decomposition_AI`
**Companion docs:** `PLAN.md` (calendar, philosophy), `MISSING_CONTENT.md` (placement tracker)

---

## 0. Blockers — nothing in L1–L7 runs today

| # | Problem | Evidence | Fix |
|---|---------|----------|-----|
| **B1** | **The entire data layer is untracked and 404s.** Every notebook loads from `raw.githubusercontent.com/amoreira2/UG54/refs/heads/main/assets/data/…` | `git ls-files` → UNTRACKED for `panel_backbone_1980_2000.parquet`, `signal_menu.csv`, `brk_13f_holdings.csv`, `signals/*.parquet`, `signals_raw/*.parquet`. `curl` on the panel URL → **404** | `git add assets/data/…` + push. Panel is 12.3 MB, signals ≤7 MB each — under GitHub's 100 MB file limit but worth a repo-size check |
| **B2** | **L5 cell 8 calls `glob.glob()` on an HTTPS URL.** Returns `[]`, so `SIGS` is empty, `L` is an empty frame, and the correlation matrix, heatmap, within/across split, Hands-On and the entire Challenge all collapse. This is the whole lecture. | verified: `glob.glob('https://…/signals/*.parquet') == []` | Read the acronym list from `signal_menu.csv`, which is already loaded: `SIGS = sorted(menu.Acronym)` |
| **B3** | **`ff_monthly.csv` does not exist.** Cited as the belt-and-suspenders fallback in the L1, L2 and L4 appendices. | `ls assets/data/ff_monthly.csv` → no such file | Either write the file or delete the fallback comment. A documented backup path that 404s is worse than none |

**B1 is the one that matters.** Everything below is secondary until the data is pushed.

---

## 1. Content check

### 1a. What was promised and delivered

Tier 5b (`MISSING_CONTENT.md`) said six items go into L4/L6. All six are in:

| | Item | Where it landed |
|---|---|---|
| 5b.1 | risk model vs expected-return model | L4 §"The same equation does two different jobs" |
| 5b.2 | alpha scarce / beta plentiful | L4 c7 and c17 |
| 5b.3 | hedged portfolio + risk budget | L4 §3, `BUDGET = 5_000_000` |
| 5b.4 | ARKK vs Berkshire | L4 §5 |
| 5b.5 | endogenous benchmark ⇒ IR = appraisal | L4 §2 and §4, and it closes properly |
| 5b.6 | characteristic-adjusted, the concept | L6 c16 as a forward pointer; delivered in full in L7 §6 |

### 1b. `MISSING_CONTENT.md` is now stale in two places

**Tier 5c said `r = α + Bf + ε`, `Ω = BΩ_fB′ + Ω_ε` and `b = B′w` were delayed to L12.** L7 now teaches all three, plus the `Σwᵢ²σ²_ε,i` specific-risk split. L12's job changes from *introduce* to *use* — and if that isn't recorded, L12 will re-teach 20 minutes it doesn't have.

**Tier 5d.1 "bottom-up vs top-down — no obvious slot yet"** is now L7 §3–4. Close it.

### 1c. What is genuinely missing — ranked

These are all in the pre-AI notebooks and all absent from L1–L7.

| # | Item | Source | Why it matters | Home |
|---|------|--------|----------------|------|
| **M1** | **Co-movement as the motivation for a factor model.** Stocks don't move independently; the *degree* varies. Defensive (utilities, groceries) vs cyclical (luxury, banks) vs levered. | `FactorModels_c` c8, c16 | L4 opens by *running* a regression and never says why a common factor should exist, or what a β means about a business. This is the best-written passage in the old notebooks. | **L4**, before the GE demo |
| **M2** | **Beta estimation windows.** *"Daily data: 1–2 year windows. Monthly: ~5 years. Long samples give precision if betas are constant; short samples capture time-variation."* | `MultiFactorModels_c` c40 | L7 hard-codes `w0='1995-01-31', min_months=48` with zero justification, in the exact lecture whose thesis is that exposures move. | **L7** §4 |
| **M3** | **`E[r] = r_f + α + β·E[f]`**, and: a significant α means **either** skill/mispricing **or** a missing factor. | `FactorModels_c` c25–26 | L4 has only the realized-return decomposition. Without the expectation version, "α = 0 if the model is right" is not a statement about anything. The two-sided reading is the seed of the Tier 5e conceptual lecture. | **L4** §1 or §4 |
| **M4** | **Hedging does not always improve your Sharpe ratio** — if the factor premium is high and your α is small, keep the exposure. *"But exposure to factors is fundamentally different from exposure to ε. Why?"* | `FactorModels_c` c51 | L4 §3 sells hedging hard (+50% position) with no counterweight. The Socratic follow-up is the best question in that notebook. | **L4** §3, ~40 words |
| **M5** | **The negative control.** *"If you use the first letter of the stock ticker to construct 26 portfolios you are unlikely to get spread in average returns — each portfolio will resemble the market but with much more volatility."* | `crosssectional` c27 | L3 has the MSFT migration (why sorting works) but nothing on why it can fail. One sentence, and it inoculates against "the recipe is magic." | **L3** §1, ~35 words |
| **M6** | **The characteristic-model critique, in full**: ignores covariances (characteristic-neutral ≠ factor-neutral — a stock classified "retail" can co-move with tech); OLS overloads tiny stocks; fix with WLS on market cap or restrict to the top 20%. And: characteristics and factors are **complements, not substitutes**. | `MultiFactorModels_c` c56 | L7 compresses this to one table cell reading "ignores covariances." Approach C is a third of the lecture and gets a third of a sentence of critique. (`MISSING_CONTENT` 5d.2 parks it in L14 — that was written before L7 existed.) | **L7** §6, promote from L14 |
| **M7** | **"Deviate from the market only if you are different from the average investor."** Equilibrium reasoning as a guard against overfitting. | `InterpretingFactorModels` | L5's risk-vs-mispricing section is posed as a bare dichotomy with no argument behind the risk side. It should *point forward* to the 5e lecture explicitly, which it currently doesn't. | pointer in **L5** §2; lecture stays late-term |
| **M8** | Log vs simple returns; the annualization caveat (mean scaling exact only for logs; variance scaling needs logs **and** iid). | `IntrotoReturns_c` c19 | Tier 2.1/2.2, still ☐. L1 annualizes by ×12 and ×√12 with no caveat at all. | Appendix ch. |
| **M9** | Empirical VaR — 5th percentile, worst day, dollar loss on $1M. | `IntrotoReturns_c` Ex. 3 | Tier 2.5. L2 §3 builds the full distribution machinery and then doesn't use it for the one thing a risk manager would. | **L2** §3 or L19 |
| **M10** | *"Subtracting a constant barely moves volatility — but the risk-free rate is* risk-free*, should it change the variance at all?"* | `IntrotoReturns_c` c29 | Tier 2.3. Free — one sentence next to L1's units-trap cell. | **L1** §6 |
| **M11** | Build an S&P-500-like index (VW top 500 by market cap each month). | `crosssectional` c25 | Tier 3.3. Also the natural benchmark for each group's own information ratio. | **Assignment** |

---

## 2. Sequence check

### 2a. Nine stale forward references — L7's insertion shifted everything after it

Inserting L7 pushed backtesting → L8, anomalies → L9, momentum → L10, capital allocation → L13, costs → L16, PCA → L18. None of the notebooks were updated.

| Notebook | Cell | Says | Should say |
|---|---|---|---|
| L2 | c17 | "Hold this thought for **Lecture 15**, when we put a price on turnover" | L16 |
| L2 | c22 | "once portfolios have covariance matrices in them (**Lecture 12**)" | L13 |
| L2 | c27 | "That's **Lecture 15**" | L16 |
| L3 | c12 | "We quantify this in **Lecture 15**" | L16 |
| L3 | c29 | "It is **Lecture 7 and Lecture 8**" | L8 and L9 |
| L4 | c23 | "both are **Lectures 7 and 8**" | L8 and L9 |
| L4 | c26 | "how to reason about that gap is **Lecture 7**" | L8 |
| L5 | c4 | "The statistical route gets its own lecture (**L17**)" | L18 |
| L5 | c5 | "We test this properly in **Lecture 8**" | L9 |
| L5 | c14 | "apart in **Lecture 8**, and **Lecture 17** asks…" | L9, L18 |
| L5 | c26 | "the subject of **Lecture 8**" | L9 |
| L6 | c19 | "**Lectures 7 and 8**" | L8 and L9 |

L6 c16's *"it needs the multi-asset machinery, so it's Lecture 7"* is the one that is now **correct**. Everything else after L7 is off by one.

### 2b. L3's headline number contradicts L4/L5/L6

Verified on the panel:

| Construction | BM long-short | t | Where it appears |
|---|---|---|---|
| `pd.qcut(10)`, equal-weighted, all stocks | **+20.76 %/yr** | 7.05 | **L3's Live Demo** — the number students actually see |
| NYSE breakpoints, value-weighted | **+5.27 %/yr** | 1.78 | L3 Hands-On convention; L4 §4; L5; L6 |

Two consequences:

- **L6 c16 says** *"In Lecture 3, the BM decile sort gave +5.27%/yr."* Lecture 3 displayed 20.76%. The claim is wrong as written.
- **L4 c20 says** *"Here is the value long-short from Lecture 3"* and then silently switches to the other construction — a 4× smaller return — without a word.

The demo's use of the naive construction is *deliberate* and good (§2 then demolishes it). But value is never re-run under the standard convention, so students leave L3 holding the wrong number, and L4/L6 quietly assume they hold the right one. **Fix:** one line at the end of L3 §2 re-running BM under NYSE/VW, and say the number out loud.

### 2c. The fund pickle has 119 missing months

`df_WarrenBAndCathieW_monthly.pkl` (loaded in L4 §5 and L7 setup, from the **Fin418** repo) spans 1988-11 → 2021-12 = 398 months and contains **279**. The gaps are scattered single months, not a contiguous block: 1995-04, 1995-09, 1995-12, 1996-03, 1996-06, 1996-08, 1996-11, …

Consequences:

- **L4 §5** reports "BRK: 279 months" as if it were a clean 23-year series. It is 279 of 398 with 30% dropped at irregular intervals. Every number in that table — Sharpe 0.64, α, all six loadings — is computed on it. If the drops are non-random the estimates are biased; if random, the label is still misleading.
- **L7 §3** claims a **1995–1999** window and silently gets **41 of 60 months**. L7 then builds its central argument on the standard errors being large — *"41 months, six factors"* — and attributes the small *n* to the window, not to a data defect.

**Fix:** Berkshire is **permno 17778** in the course panel — a complete 252-month series, 1980-01 → 2000-12. Use it for the L7 top-down regression: full 60 months, same source as everything else in the course, no external repo. (ARKK genuinely needs the pickle; keep it there and print the gap count.)

### 2d. Smaller ordering notes

- L4 §5 introduces a **second, undocumented data source** (a pickle on the `Fin418` repo) mid-lecture, with no appendix entry. Every other dataset in L1–L7 is documented in the belt-and-suspenders appendix. This one isn't.
- L4's ARKK/BRK sample is modern; the rest of L4 is 1980–2000. The caution box mentions sample *lengths* but not that the samples don't overlap the course panel at all.
- L3's Challenge says *"Use `size_spread()` from Section 2"* — fine, but it silently depends on the student having run c11.

---

## 3. Language — what to borrow from the pre-AI notebooks

Ranked by how much better the old wording is. All of these are *replacements*, not additions.

### L1

**Excess return, the intuition.** L1 opens with "You could always have earned the risk-free rate." `IntrotoReturns_c` c21 is sharper because it's concrete:

> A **10% return** sounds great, but what if risk-free bonds paid **8%**? The stock only gave you **2% extra** for taking on stock-market risk.

**Self-financed, the analogy.** L1 c17 asserts that a zero-weight portfolio costs nothing. `IntrotoReturns_c` c31 earns it:

> This means you don't need any cash to invest in it — you borrow all you need. Of course you bear risk. Banks will lend to you if they expect to get paid, so in practice you will have limits on how many dollars you can put on the strategy. You will be required to post collateral. It is no different from buying a house with a mortgage.

The mortgage line is the whole idea of a self-financed position in one sentence, and it defuses the "how can it cost nothing?" objection that always comes up.

### L2

**Why stacked, not wide.** L2 c7 gives two sentences. `crosssectional` c14 gives the actual argument and is worth taking nearly verbatim:

> With a rectangular data set we need two coordinates, row and column, to identify one asset's return on one date. It was easier to manipulate, but we would need one dataframe for each firm variable — one for return, one for market equity. As we work with many signals this becomes intractable. As we work with many assets it becomes intractable again, because we'd need dataframes with many columns and most locations empty. Now we need two coordinates in columns — date and permno — and a third, the column name, to identify the variable.

**The shift trap.** L2 c11's caution box is fine but abstract. `crosssectional` c16 states the mechanism in one line and it lands harder:

> Because the data set is stacked, when you shift the first month of security *n* it will return the last month of security *n−1*.

**Value weights need no rebalancing.** L2 c17 has this. `crosssectional` c7 adds the second reason, which L2 omits and which is the one that matters for the rest of the course:

> By buying proportionally to market cap you never have to build a huge position in a tiny stock — so this is much easier to trade. Equal-weighted portfolios tend to be very hard to trade and the alphas you get there are mostly a mirage, unless you focus on large caps.

"Mostly a mirage" is the phrase L2 §5 and L3 §2 are both circling and never say.

### L3

**The recipe.** `crosssectional` c26 is better than L3's five-step box on exactly one point — what a characteristic can be:

> It can be based on accounting data, return data, textual data from earnings calls, Twitter activity, ownership, shorting activity, satellite images — **anything**. What matters is that for each stock on each date you have a value, that it varies across firms, and that you have a theory of how it relates to expected returns.

That list is what makes a room of undergraduates believe the course is about the present.

**The curved-grades analogy for within-month ranking.** `crosssectional` c31, absent from L3, and it kills pitfall 4 dead:

> We apply this date by date. That makes the strategy cross-sectional, because you use the distribution of the signal on a given date to do the grouping — very much like curving grades by cohort.

**Book size.** `crosssectional` c33 explains *why* weights must sum to one in a way L3 doesn't:

> We do this so that when we do the long-short we have a clear notion of "book size." If you go 100 times the long-short, you know this means buying 100 dollars of the long and selling 100 dollars of the short.

**The negative control** — M5 above.

### L4

**Co-movement** — M1. `FactorModels_c` c8, essentially verbatim:

> To understand how much to invest in different stocks, the first step is to understand to what extent stocks are alike and to what extent they are different. It makes no sense to say you are buying a bunch of different assets to be diversified if they all behave like each other.

**What β means about a business.** `FactorModels_c` c16 — three lines, and L4 currently reports β = 1.07 without ever telling students how to read one.

**The decomposition is always valid.** `FactorModels_c` c12 makes a point L4 never makes and should:

> This decomposition is always valid — it's just statistics. The power comes from *interpreting* each piece.

That is the honest framing, and it sets up M3 (α ≠ 0 means skill **or** a missing factor).

**Caution: hedging and the Sharpe ratio** — M4.

⚠️ **Do not borrow** `FactorModels_c` c24 ("Big bonuses only come from perceived α", the pod-shop links) — it trips the PLAN §1 tone rule. L4 c17's rewrite ("beta is plentiful and cheap, alpha is scarce and dear") is the right register and should stay.

### L6

**The cross-sectional recipe, four steps.** `MultiFactorModels_c` c41 states it more cleanly than L6 §3, and the OLS line makes the "slope is a portfolio" claim concrete rather than asserted:

> From OLS: β = (X′X)⁻¹X′R. The β coefficients **are excess returns themselves** — returns on "pure play" portfolios designed to have a loading of 1 on one characteristic and zero on all others. The weights (X′X)⁻¹X′ **are** the portfolio weights.

L6 says "the slope IS a portfolio return" and asks the reader to take it. One extra line shows it.

### L7

**Why bottom-up, in one sentence.** `MultiFactorModels_c` c24:

> For high-turnover portfolios the bottom-up approach tracks exposures much better because it refreshes at the holding level. For stable portfolios, top-down regressions are simpler and avoid the noise of estimating individual-stock betas.

L7's trade-off table has this spread across four rows. The sentence is better.

**Estimation windows** — M2, `MultiFactorModels_c` c40.
**The critique of characteristics** — M6, `MultiFactorModels_c` c56.

---

## 4. Prompt-it moments

### 4a. The problem with what's there now

L1–L4 have a `Specify → Implement → Validate` scaffold. Only **L1 c13** is a genuine blank paste cell. L2 c19, L3 c7 and L4 c10 show the prompt and then hand over working code labelled *"what competent AI-generated code looks like."* That demonstrates the workflow; it doesn't practise it. L5, L6 and L7 have no scaffold at all.

### 4b. Selection criteria

A moment earns a slot only if all five hold:

1. It sits at a **transition** — the lecture has just established a need and the next move is "so how do we do that?"
2. The **specification decision is the lesson**. If the only hard part is syntax, AI is right and there's nothing to discuss.
3. The likely-wrong answer **runs and returns a plausible number**. No exceptions, no crashes.
4. There is a **known right answer** so the room converges instead of arguing.
5. The code is **≤ 12 lines**, auditable on a projector in 60 seconds.

### 4c. The eight

> **Checked 2026-08-08:** `b = B′w` was my first pick for L7 and it does **not**
> work — both snapshots have full beta coverage (16/16 at 1999, 9/9 at 1996), so
> the renormalization never bites. Approach C is where it does: 8 of 16 holdings
> have characteristics, carrying 0.6515 of the book.

Two in L2 (it has two genuinely distinct traps); one everywhere else. **These replace exposition — they are not additions.** Every lecture is already over its 1,417-word budget, L4 worst at 2.45.

| | Lecture | Moment | The transition line | What AI gets wrong | Right answer |
|---|---|---|---|---|---|
| **P1** | L1 | Growth of $1,000 in your stock *(already exists, c13)* | "If your parents had put $1,000 in one stock the day you were born…" | price vs total return; start-date alignment | add a hidden check that recomputes for permno 12060 off the panel — students compare yfinance vs CRSP and find the gap themselves |
| **P2** | L2 | **`w′r` — the market return** *(replaces c19)* | "We want each month's market return. How do we ask for it?" | `weights=g['me']` against **`ret`**, not `ret_fwd` — pitfall 1, verbatim | VW mean 17.6%/yr vs the look-ahead version, visibly higher; corr with Ken French **1.0000** only for the right one |
| **P3** | L2 | **Build `ret_fwd` yourself** *(replaces c10)* | "We handed you this column. Build it." | `df['ret'].shift(-1)` without `groupby('permno')` | count the mismatches against the shipped column — **~17,800**, one per stock boundary. Mechanically provable |
| **P4** | L3 | **NYSE breakpoints** *(replaces part of c11)* | "Cutoffs from NYSE stocks only, applied to everybody. How do you say that?" | applies the cutoffs only to NYSE stocks, or recomputes them per-subgroup | avg stocks in the small bucket = **3,106**. The wrong spec gives ~150 and it's obvious |
| **P5** | L4 | **The factor regression** *(replaces c10)* | "We have a return and a factor. How much of one is the other?" | no `add_constant` (pitfall 2) and/or total instead of excess returns (pitfall 1) — both silent | β = **1.07**, α = **+7.1%/yr**, R² = 0.56. Missing the constant moves β visibly |
| **P6** | L5 | **Correlate strategies, not signals** *(replaces c8–9, which are broken anyway — B2)* | "Are these 30 signals 30 bets? What exactly do we correlate?" | correlates the **characteristics** — the natural one-liner — instead of the long-short returns. Pitfall 2, and the answers differ a lot | within-category mean \|ρ\| **0.579** vs across **0.189** |
| **P7** | L6 | **Fama-MacBeth** *(replaces c14)* | "The return to being cheap, holding size and profitability fixed. Not a sort — a regression per month." | pools all months into one big regression, or takes the t-stat from pooled OLS standard errors instead of the time series of slopes | BM **+5.55%/yr, t = 4.99**. The pooled t is an order of magnitude larger — that contrast *is* step 2 |
| **P8** | L7 | **Approach C — the characteristic score** *(replaces c21)* | "We have the premia. What's this portfolio's characteristic score?" | merges holdings onto characteristics and weights without renormalizing over the names that actually matched. Pitfall 5 | only **8 of 16** holdings have characteristics and they carry **0.6515** of the book — skip the renormalization and every z-score, and the implied return, is scaled by 0.65 |

**Deliberately not chosen**, and why: L1's units trap (better as a 30-second demonstration — the trap *is* the point); L3's infinities (a *validation* moment, not a generation moment — leave it); L4's ARKK/BRK (the interest is in reading the loadings, not producing them); L7's risk split (`Ω = BΩ_fB′ + Ω_ε` is algebra to derive, not code to specify).

### 4d. The cell pattern

Four cells, fixed, so students learn the rhythm:

```
1. MD    ── the transition and the question. No spec yet.
           "We want X. Before you write anything: what does whoever
            writes this code need to be told?"          [60–90 s, cold-call]

2. CODE  ── empty. MY_PROMPT = """…"""  then paste below.

3. CODE  ── 🔒 hidden. The check. Always runs, never breaks the notebook.
           Prints the one number that must match, plus a diagnostic that
           separates the known failure modes from each other.

4. MD    ── what the room got, and why the answers differ.
```

A fifth hidden cell holds the reference implementation, but **only** where downstream cells depend on the result (P2, P4, P6, P8). Where nothing downstream needs it (P3, P5, P7), leave it out — a visible answer key is an invitation to skip step 1.

### 4e. Hiding mechanics

Two channels, set both:

- **Colab** — first line `#@title 🔒 Reference implementation — open after you've tried yours`. Renders collapsed in form mode. Already used by the setup cells.
- **JupyterBook** — cell metadata `{"tags": ["hide-input"]}`.

One pass over all seven notebooks can set both.

### 4f. Two things to test before relying on any of this

1. **Pilot every prompt against Gemini-in-Colab specifically**, since that's what students will use. If the model gets it right, the moment has no payoff and needs a weaker prompt or a different target. The failure modes in 4c are the ones the notebooks already assert as pitfalls — they are informed expectations, not measurements.
2. **Time it.** 8–10 minutes each including discussion. Two moments is ~20 minutes of a 75-minute slot. Against lectures already running 1.2–2.5×, that has to come out of exposition somewhere, and the prose the moments replace is roughly 250–400 words each — which is about the right trade.

---

## 5. Suggested order of work

1. **Push the data** (B1). Nothing else is testable until then.
2. **Fix L5's glob** (B2) — one line.
3. **Renumber the twelve forward references** (2a) — mechanical, and it will only get worse as more lectures land.
4. **Fix the BM number** (2b) and **swap L7 to permno 17778** (2c). Both are correctness, not polish.
5. **Language pass** (§3) — replacements, so roughly word-count-neutral, and several *shorten* the current text.
6. **Prompt-it moments** (§4), one lecture at a time, starting with **P5 (L4)** — L4 is the longest lecture and the regression is the cleanest audit exercise in the course, so it buys the most.
7. Content gaps M1–M7 as room allows; M8–M11 to the Appendix chapter and assignments.


---

## 5. Build log — prompt-it moments shipped 2026-08-08

All eight are in and all seven notebooks execute. Structure per moment:

```
MD     transition + the question, no spec         [60–90 s, cold-call]
CODE   MY_PROMPT = """…"""  then paste below      [visible, empty]
CODE   🔒 the check — always runs                  [hidden]
CODE   🔒 reference implementation                 [hidden, only where downstream needs it]
MD     what the room got, and why answers differ
```

Hidden cells carry `#@title` (Colab collapses them in form mode) **and**
`metadata.tags = ["hide-input"]` (JupyterBook). Reference cells are present in
L2 (P3), L3, L4, L5, L6 and L7 because later cells depend on their variables;
P1, P2 and P8 need none.

### What the checks actually print — measured, not predicted

| | Lecture | The trap | Wrong | Right |
|---|---|---|---|---|
| P1 | L1 | `auto_adjust` — dividends or not | price return | total return (their own stock, both printed) |
| P2 | L2 | `shift(-1)` without `groupby` | **19,156** rows wrong | 1,357 (the calendar-gap rule) |
| P3 | L2 | `ret` instead of `ret_fwd` | market = **25.49%/yr** | **15.74%/yr** |
| P4 | L3 | NYSE cutoffs applied only to NYSE | **150** in the small bucket | **3,106** |
| P5 | L4 | total instead of excess returns | α = **+13.83%/yr** | α = **+7.12%/yr** |
| P6 | L5 | correlating characteristics, not strategies | Illiquidity vs Size = **0.07** | **0.92** |
| P7 | L6 | one pooled regression instead of 251 | size t = **−11.69** | t = **−1.81** |
| P8 | L7 | no renormalization after the merge | implied **−10.67%/yr** | **−16.38%/yr** |

### Two predictions from §4c that the data corrected

- **P5 was supposed to be about `add_constant`.** It isn't. Dropping the
  intercept moves GE's β from 1.07 to 1.09 — worth a sentence, not a demo.
  *Excess vs total returns* is the one that bites: α nearly doubles, because the
  risk-free rate averaged 6.64%/yr over the sample and α absorbs it whole. The
  cell prints all three specifications and leads with that.
- **P8 was supposed to be `b = B′w`.** Both snapshots have full beta coverage
  (16/16 and 9/9), so the renormalization never bites there. Approach C is where
  it does: 8 of 16 holdings match, carrying 0.6515 of the book.

**P6 turned out to be the best of the eight.** Illiquidity and Size correlate
**0.07 as characteristics and 0.92 as strategies** — the raw numbers say two
unrelated ideas, the portfolios say one trade. That single row is the lecture.

### Cost

| | start | after language | after prompts | lectures |
|---|---|---|---|---|
| L1 | 2,689 | 2,883 | 3,010 | 1.90 → 2.12 |
| L2 | 2,965 | 3,224 | 3,280 | 2.09 → 2.31 |
| L3 | 3,198 | 3,536 | 3,681 | 2.26 → 2.60 |
| L4 | 3,468 | 3,985 | 4,095 | 2.45 → **2.89** |
| L5 | 1,719 | 1,886 | 2,043 | 1.21 → 1.44 |
| L6 | 2,198 | 2,276 | 2,436 | 1.55 → 1.72 |
| L7 | 2,460 | 2,973 | 3,140 | 1.74 → **2.22** |
| **total** | **18,697** | **20,763** | **21,685** | **13.19 → 15.30** |

The prompt moments cost **+922 words** — about half what the language pass cost,
because each one replaced a "here's what competent AI code looks like" block. But
the block now holds **15.3 lectures of material in 7 slots**, up from 13.2. The
word metric also cannot see that a prompt moment consumes *clock* well beyond its
word count: 8–10 minutes each of writing, running and arguing. On that basis
L1–L7 is closer to **17 lectures of wall-clock**, and a trim is no longer
optional.

### Before this is used in class

**Pilot every prompt against Gemini-in-Colab.** The traps above are measured on
*our* data — the wrong answers are real and the numbers are exact. What is not
measured is whether the model actually falls into them. If Gemini writes
`ret_fwd` and `groupby` unprompted, P2 and P3 have no payoff and need weaker
prompts or different targets.
