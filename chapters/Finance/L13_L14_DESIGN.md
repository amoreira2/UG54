# L13 + L14 · Capital Allocation — joint design note

**Slots:** Meetings 16 and 17 (Mon Nov 2, Wed Nov 4). **Feeds:** A6.
**Status:** **L13 built 2026-08-28** — `L13_CapitalAllocationI_AI.ipynb`, 39 cells,
2,084 lectured words = 1.47 sessions, 9 lecture cells clean in 1 s. Built but not
published (see `PLAN.md` §6b). **L14 built 2026-08-28** —
`L14_CapitalAllocationII_AI.ipynb`, 45 cells, 1,956 lectured words = 1.38
sessions, 12 lecture cells clean in 3 s. Also built but not published.

Written as one design because the split only makes sense jointly.

---

## The spine, across both meetings

> **How much do you bet, and on what? There is exactly one formula. It is
> beautiful, it is three lines of linear algebra, and it stops working the
> moment you have to estimate its inputs.**

**L13 builds the formula and shows what it buys you.** **L14 breaks it and
rebuilds something you would actually run.** Neither half works alone: L13 on its
own is a maths lecture students will never use, and L14 on its own is a list of
heuristics with no reason behind them.

The unifying result, which appears three times in three costumes:

| where | form |
|---|---|
| L13 §5, two uncorrelated bets | $SR = \sqrt{SR_A^2 + SR_B^2}$ |
| L13 §6, pod shops | $SR_{\text{pool}} = \sqrt{N}\,SR_{\text{pod}}$ |
| EQI §8.5, the Fundamental Law | $IR = IC\sqrt{nT}$ |

All three say: **skill times breadth.** Getting students to see that these are one
theorem is the intellectual job of L13.

---

## A note on meeting 15 — nothing decided

L12 (leverage and shorting) is **skipped for now**, not cut: AM is thinking about
moving it later and may or may not kill it. **The calendar is unchanged and this
plan assumes nothing about it.** L13 and L14 are designed for meetings 16 and 17
exactly as scheduled.

Recorded only so it is not forgotten: *if* L12 eventually moves or goes, meeting
15 opens up, and the strongest claim on it is momentum part 2 — L10 is 2.80
lectured sessions and already built, so a split would cost nothing but the slot.
That is a decision for later, not an input to this design.

---

## The sources, honestly assessed

### `CapitalAllocationI.ipynb` — 2,858 words, strong

The best of the four CA-I variants. Take almost all of it:

- **The two-decision framing** — how much risk, then how to spread it — and the
  fact that they separate. This is the organising idea of the whole block.
- **Principal vs delegate.** *"Who is choosing the portfolio, and what do they
  care about?"* Preferences, horizon, goals, **background risk**. This is L9 §3
  returning with a portfolio attached, and it is the right way in.
- The single-asset derivation, which needs no matrices:
  $x^\star = \frac{1}{\gamma}\frac{\mu}{\sigma^2}$, and therefore
  **optimal volatility $= \frac{1}{\gamma}\times$ Sharpe ratio.**
- $W^\star = \frac{1}{\gamma}\Sigma^{-1}\mu$ and **two-fund separation** —
  *"a risk-averse investor does not hold safer assets, it holds a safer
  portfolio."*
- **Alpha bets vs factor bets**, and the diagonal case where no inversion is
  needed at all: $w_i \propto \alpha_i/\sigma^2_{\epsilon,i}$, so that
  $w_i\sigma_{\epsilon,i} = \alpha_i/\sigma_{\epsilon,i}$ — **the volatility you
  allocate to a strategy is its appraisal ratio.** That single line is the payoff
  of L4 and L7 and it belongs at the centre of L13.
- $SR = \sqrt{SR_A^2+SR_B^2}$, and *"the appraisal ratio is the Sharpe ratio
  cousin that actually matters."*

**Skip:** the `get_factors` plumbing, and the frontier plot (pretty, and it needs
a no-risk-free-asset detour we do not want).

### `CapitalAllocationII.ipynb` — 2,099 words, strong

- Estimation risk framed exactly right: **in-sample MVO delivers the highest
  in-sample Sharpe by construction — it is just algebra**, so the number tells
  you nothing.
- Perturb μ within its standard error and watch the weights move.
- **The bet-sizing menu**: mean-variance, 1/N, proportional, risk parity,
  minimum-variance, shrinkage — each with the assumption that justifies it. Risk
  parity is *"assume all appraisal ratios are equal"*, which is the honest way to
  present it.
- **The pod-shop calculation.** $SR_{\text{pool}} = \sqrt{N}SR_{\text{pod}}$,
  and *"finding a new uncorrelated idea is super valuable."* This is the best
  single passage in either notebook and it is the natural climax of L13, not L14.

**Skip:** Black–Litterman (needs a Bayesian detour we cannot afford).

### EQI chapters 8 and 9

Chapter 8 is *Portfolio Management: The Basics*, chapter 9 *Beyond Simple
Mean-Variance*. Unlike chapter 10, **most of this is usable**, and four things are
genuinely additive:

- **§8.5, the Fundamental Law of Active Management: $IR = IC\sqrt{nT}$.** The
  missing conceptual glue — performance is *skill* (the information coefficient,
  a cross-sectional correlation between your alphas and realised returns) times
  *breadth*. Insight 8.3 makes IC concrete: $IC^2$ is the $R^2$ of the
  cross-sectional predictive regression, so students can compute their own.
- **§8.4, "alpha orthogonal is the golden currency in investing"**, and the recipe
  is orthogonalise then inverse-variance weight — the same two steps as CA I's
  alpha bets, said better.
- **§9.1, naive MVO shorts a positive-Sharpe asset** whenever
  $s_2/s_1 < \rho$. Deeply counterintuitive, easy to demonstrate in two lines,
  and it is *why* the optimizer misbehaves rather than just *that* it does.
  **Insight 9.2 is quotable: forecast error routinely costs 10–50% of the Sharpe
  ratio.**
- **§9.2.2, constraints worsen performance if your inputs are right and can
  improve it if they are estimated.** This is the theoretical licence for
  everything in L14 §4 — 1/N and long-only stop being embarrassing hacks and
  become regularisation.

**Skip:** all of §8.7 (convex duality, local analysis) and §9.5 (operator-norm
theorems, Lemmas 9.1, 9.3, 9.4). Graduate material with no undergraduate path.
**Defer:** §9.4, trading Sharpe for capacity — L11 already did the capacity work
and re-opening it here would blur both.

---

## L13 · Capital Allocation I — the formula

### §1 · Who decides how much risk?

Principal versus delegate, from CA I. Preferences, horizon, goals, background
risk. Explicitly a callback: L9 said risk is a property of an asset *for an
investor*; this is that statement turned into a number.

### §2 · One asset, no matrices

$\max_x\ x\mu - \frac{\gamma}{2}x^2\sigma^2 \Rightarrow x^\star = \frac{\mu}{\gamma\sigma^2}$,
hence $x^\star\sigma = \frac{1}{\gamma}\times SR$.

**How much volatility you run is your Sharpe ratio divided by your risk
aversion.** Everything else in the lecture is this line with more indices.

### §3 · Many assets

$W^\star = \frac{1}{\gamma}\Sigma^{-1}\mu$, derived the same way. Two-fund
separation, and the point that $\gamma$ only sets leverage — the *composition* is
the same for everyone.

### §4 · Alpha bets — where the inverse disappears

Their strategies are already market-hedged (L4, L7). If the residuals are
uncorrelated, $\Sigma_\epsilon$ is diagonal and the formula collapses to
$w_i \propto \alpha_i/\sigma^2_{\epsilon,i}$, i.e.

$$\underbrace{w_i\sigma_{\epsilon,i}}_{\text{vol you allocate}} \;=\; \underbrace{\frac{\alpha_i}{\sigma_{\epsilon,i}}}_{\text{appraisal ratio}}$$

**No matrix inversion, and the answer is a quantity they already know.** State the
diagonality assumption as an assumption — L14 attacks it.

### §5 · Combining bets

$SR = \sqrt{SR_A^2+SR_B^2}$ for orthogonal strategies, then the general
$\sqrt{\sum_i AR_i^2}$, then the Fundamental Law as the same statement:
**skill × √breadth**.

### §6 · Pod shops

Why Citadel and Millennium are organised the way they are. $\sqrt{N}$, and then
the reality check on our own data:

| | |
|---|---|
| mean individual Sharpe of our 29 long-shorts | **0.40** |
| best single | 1.36 |
| equal-volatility pool of all 29 | **1.38** |
| $\sqrt{29}\times 0.40$ if truly uncorrelated | 2.13 |
| mean pairwise correlation | **0.05** |

Pooling turns 0.40 into 1.38 — a 3.4× gain from breadth alone. It does not reach
2.13, and **the gap is entirely the correlation.** That single table earns §5 and
sets up L14.

---

## L14 as built — the plan was wrong and the data said so

A 13-agent adversarial verification workflow ran every empirical claim the
planned L14 rested on, and **two of the three headline results did not survive**.
Every number below was then re-run independently before use; where the agents and
I disagreed, my numbers are the ones in the notebook.

**What died.** The plan's emotional centre was *"1/N beats mean-variance out of
sample, 0.92 to 0.83"*. It is real on the full sample but it is **a twentieth-
century result**: the gap is **+0.282 before 2000 and +0.014 after**, and the
full-sample gap of 0.089 has a bootstrap CI containing zero. Presenting it as
*the* finding would have been exactly the error L8 and L9 warn about. Two agent
figures were also discarded outright — a claimed 86% long-window win rate (I get
54%) and a claimed post-2000 sign reversal (I get the gap merely vanishing).

**What replaced it, and it is better.** Run a control on L13's own alpha book:
throw the alphas away and weight by $1/\sigma^2_\epsilon$ alone.

| | in sample | out of sample |
|---|---|---|
| alpha book $\alpha/\sigma^2_\epsilon$ | 2.2585 | 1.8470 |
| **no alpha, $1/\sigma^2_\epsilon$** | **2.2924** | **2.0735** |
| risk parity $1/\sigma_\epsilon$ | 2.0958 | 1.8784 |
| equal | 2.0011 | 1.7762 |

**The zero-information rule beats the optimal one in the sample the optimal one
was fitted on.** It should be impossible, and the reason it is not is that the
diagonal shortcut is not $\Sigma_\epsilon^{-1}\alpha$ when the residuals are
correlated — which they are (mean |corr| 0.198, `MaxRet`/`RealizedVol` at 0.952).
Read as a decomposition: risk information is worth about **+0.3**, return
information about **−0.2**.

**The placebo, which is the prompt moment.** The obvious way to measure
estimation error — fit on one window, score on the next against that window's own
optimum — says the cost is **46%**. Score a *clairvoyant* portfolio built from the
entire sample by the same metric and it "loses" **19%**. The benchmark is an
in-sample maximum, so everything loses to it, including something that cannot be
wrong. The honest cost, from a Monte Carlo where the truth is known: you keep
**76% / 85% / 92% / 96%** of the achievable Sharpe with 5 / 10 / 20 / 40 years.
**More data genuinely helps** — the fashionable nihilism is wrong.

**Shrinkage, with the shape argument.** Covariance toward the scaled identity:
0.828 → **0.908**, interior optimum at a ≈ 0.6. Means toward their common average:
0.828 → 0.810 → **0.768**, monotonically destructive. The prior has to have the
right shape; "all expected returns are equal" throws away the only signal there
was.

**Challenge answer key.** `alpha_cost` **+0.2265**, `best_a` **0.6**,
`live_shrinkage_sr` **0.7882** — and that last number is the best thing in the
lecture: choosing the shrinkage intensity honestly from trailing performance
lands *below plain mean-variance at 0.828*, giving back **150%** of the gain. The
hindsight-optimal `a` is itself an estimated parameter and estimating it costs
more than it buys. L8's lesson, one level up.

### Added 2026-08-28 after AM: the bet-sizing menu and differential exposure

AM: *"are we showing the sensitivity to estimation uncertainty of the different
pieces? not simply the out-of-sample things but the standard error construction
or bootstrap simulation to show clearly how different bet-sizing approaches
expose themselves to different estimation uncertainty. Also important to
highlight the different bet-sizing approaches and their motivation."*

Both were genuinely missing — L14 had four rules appearing inside code cells with
no menu and no motivation, and its only uncertainty evidence was one sign-flip
perturbation plus an out-of-sample race. Two new sections, +0.47 sessions.

**§3, the menu.** Five rules, each presented as *an assumption about what you
know* rather than a level of sophistication, with an explicit column for **which
inputs it estimates**. Minimum-variance is "you cannot forecast returns"; risk
parity is "you cannot distinguish appraisal ratios" — which is L13 §4 with the
appraisal ratios set equal, not a rejection of alpha.

**§4, exposure — bootstrap then simulation.** Resample the months 1,000 times and
refit:

| rule | inputs estimated | avg weight sd | worst sign flip |
|---|---|---|---|
| mean-variance | μ **and** Σ | **0.061** | **41%** |
| minimum-variance | Σ | 0.020 | 22% |
| risk parity | diag(Σ) | 0.007 | 0% |
| equal 1/N | none | 0.000 | 0% |

**The ordering is exactly the input list**, and the min-variance → mean-variance
step isolates the price of μ: same covariance matrix, one extra input, and the
weight uncertainty triples. This *measures* the "means are harder than variances"
claim that the first draft asserted, so the old §3 half-section is deleted and
§5 now opens by pointing at the bootstrap.

Then the known-world simulation, scored against the truth:

| rule | 5y | 10y | 20y | 40y |
|---|---|---|---|---|
| mean-variance | 74% | 86% | 92% | **96%** |
| minimum-variance | 85% | 86% | 87% | 87% |
| risk parity | 80% | 80% | 80% | 80% |
| equal 1/N | **88%** | 88% | 88% | 88% |

**A crossover, not a winner.** 1/N never learns and never errs — flat at 88%
forever. Mean-variance is beaten badly at five years and wins at twenty. The
crossover sits at ten to twenty years of monthly data, which is what everyone
has, **which is why this argument never ends.** That reframes the whole lecture:
choosing a bet-sizing rule is a bet on how much data you have, not on which
formula is cleverer.

One honest wrinkle kept in the notebook: in this simulation the true covariance
*is* the sample covariance, so shrinkage can only add bias — which is why §7 finds
it helping on real data anyway. The contrast is the point.

§6's separate Monte Carlo was deleted as a duplicate; it now reads the
mean-variance row of §4's table.

### Consequence for L13, applied

L13 §4 derived $w_i\sigma_{\epsilon,i} = AR_i$ under a stated diagonality
assumption but never tested it, and §6's "mean pairwise correlation 0.049"
actively invited students to believe it. **Patched**: §4 now ends with a
diagonality test showing mean signed correlation +0.03 against mean *absolute*
correlation 0.20 and a worst pair of 0.95, and a box saying the formula is the
right answer to a question about a world we are not in. L13 goes from 1.47 to
1.60 lectured sessions.

## L14 · Capital Allocation II — as originally planned

### §1 · The in-sample illusion

On the six Fama–French factors, 1980–2026:

| | Sharpe |
|---|---|
| in-sample MVE | **1.17** |
| equal-weighted | 1.03 |
| best single factor (market) | 0.57 |

MVE wins **by construction** — it is the algebraic maximum. And it beats naive
equal weighting by only 0.14. Ask what that 0.14 is worth before believing it.

### §2 · Why it breaks

First the mechanism, from EQI §9.1: with two assets, the optimizer **shorts a
positive-Sharpe asset** whenever $s_2/s_1 < \rho$. Not a bug — it is using the
asset as a hedge — but it means the weights depend on differences between
similar, badly estimated numbers.

Then the demonstration. Perturb each expected return by **one standard error**
and ask how often the sign of the weight flips:

| | Mkt | SMB | HML | RMW | CMA | UMD |
|---|---|---|---|---|---|---|
| P(sign flips) | 0% | 20% | **46%** | 0% | 5% | 0% |

**HML flips essentially at random.** The optimizer is not telling you to go long
value; it is telling you that it cannot tell.

Then EQI's Insight 9.2 for the scale of the damage: 10–50% of the Sharpe ratio,
routinely.

### §3 · The bet-sizing menu

Mean-variance, 1/N, proportional, risk parity, minimum-variance, shrinkage — each
presented as **an assumption, not a hack**:

- 1/N: "I know the sign and nothing else"
- risk parity: "all appraisal ratios are equal"
- minimum-variance: "all alphas are equal"
- shrinkage: "the truth is between my estimate and a simple prior"

### §4 · The horse race

Expanding-window, 120-month burn-in, out of sample:

| rule | OOS Sharpe |
|---|---|
| **1/N** | **0.92** |
| mean-variance | 0.83 |
| minimum-variance | 0.77 |
| risk parity | 0.76 |

**Equal weighting beats the optimizer.** This is DeMiguel, Garlappi and Uppal
(2009) reproduced on our data, and it is the emotional centre of the lecture: the
formula they spent all of L13 deriving loses to dividing by six.

### §5 · Why constraints help

EQI §9.2.2, and it rescues the lecture from nihilism. Constraints *must* reduce
performance if your inputs are correct. They can *improve* it when your inputs
are estimated, because they are regularisation — a constraint is a penalty
(§9.2.3), and a penalty is a prior. **1/N is not giving up; it is an extreme
prior, and on this data it is a better prior than the sample mean.**

### §6 · What you should actually do

Estimate → Tune → Test from L8, applied to the choice of rule itself. Choose the
bet-sizing rule on the tune sample; report on the test sample once. Close on the
honest position: use the optimizer on inputs you trust (covariances, which are
estimable) and shrink hard toward simple priors on inputs you do not (means,
which are not).

---

## L13 as built — verified numbers

| | |
|---|---|
| market 1980–2000 | 9.2%/yr, 15.6% vol, Sharpe 0.59 |
| γ = 1 / 2 / 5 / 10 → portfolio vol | 58.7% / 29.3% / 11.7% / 5.9% |
| `vol_alloc == appraisal ratio` | exact to 2.2e-16 |
| best appraisal ratio | 1.36 (DivSeason, on a 4.0% residual vol) |
| alpha-bet combo | Sharpe 1.65, alpha +9.0%/yr, beta −0.15 |
| market ⊕ hedged combo | 0.59 and 2.26 → **2.33**, and √(0.59²+2.26²) = 2.33 |
| pooling N = 1/4/9/16/29 | 0.34 / 1.00 / 1.26 / **1.16** / 1.38 |
| √N × mean, same N | 0.34 / 1.20 / 1.34 / 1.55 / 2.13 |
| mean pairwise correlation | 0.049 |

Two things the data gave that the plan did not anticipate, both kept:

**The optimizer's favourite is its most fragile.** `DivSeason` takes 21% of gross
weight, not because its alpha is large (5.4%/yr, mid-pack) but because its
residual volatility is 4% and the formula divides by the square. The notebook says
so and hands the consequence to L14.

**Pooling is not monotonic** — 9 strategies pool to 1.26 and 16 pool to 1.16.
Adding bets 10–16 made it worse. Shown rather than smoothed, because it is the
honest version of "breadth helps".

**Challenge answer key:** `book_sharpe` **2.26**, `diversification_shortfall`
**0.588** (the book captures 59% of the √Σ AR² ideal of 3.84),
`book_without_divseason` **2.01**. The memo's anchor: an uncorrelated strategy
with Sharpe 0.35 adds √(2.26²+0.35²) − 2.26 = **+0.03** — almost nothing — but the
59% shortfall is exactly why a *genuinely* orthogonal idea is worth more at the
margin than the formula suggests.

**The Fundamental Law is one box in §5**, stated and connected to the two results
students just derived, with no IC computed anywhere — as agreed.

## The prompt-it moments — one per meeting

**L13: "Find me the optimal portfolio weights."** Load-bearing, and
underspecified in three ways that change the answer: maximum-Sharpe (scale-free)
or a volatility target; full $\Sigma^{-1}$ or the diagonal idiosyncratic version;
and with or without the risk-free asset. A terse prompt returns
`np.linalg.inv(cov) @ mu` with no scaling and no statement of which problem it
solved.

**L14: "Is this out of sample?"** The horse race is only meaningful if every
rule is estimated on data strictly before the return it earns. The trap is the
expanding window: it is easy to write a loop that refits on `F.iloc[:t+1]` and
then earns `F.iloc[t]`. One index, and 1/N stops beating mean-variance.

---

## Length budget

**1,500 lectured words each.** L13 is derivation-heavy and will *feel* longer
than it reads, so the word count understates it — budget accordingly and move the
frontier plot to the appendix if it runs.

## Data

`ff_monthly.csv` (six factors, 1980–2026) for the optimizer work and the horse
race; `longshort_29.parquet` for the pod-shop table and the alpha-bets version.
Both already shipped. A small cache of the horse-race series is probably worth
building so the expanding-window loop does not run in class.

## Open questions for AM

### 1 · How much of the Fundamental Law to teach

The law says **IR = IC × √(breadth)**: your risk-adjusted performance is your
*skill per bet* multiplied by the square root of *how many bets you make*.

- **IC**, the information coefficient, is the cross-sectional correlation between
  the alphas you predicted and the returns that happened. It is a skill score, and
  real values are tiny — a good equity manager runs 0.02 to 0.05.
- **Breadth** is the number of genuinely independent bets per year: roughly the
  number of names times the number of times a year you re-forecast.

So a manager with IC = 0.03 across 1,000 independent bets a year has
IR ≈ 0.03 × √1000 ≈ 0.95. Skill can be nearly undetectable per bet and still make
a business, provided there are enough bets.

**The question is how far into L13 it goes**, because it is a third formula in
the most formula-dense meeting of the term, and computing an IC properly needs a
cross-sectional regression setup students do not have.

**My recommendation — state it, never compute it.** One box in §5 saying the two
results they *just derived themselves* (√(SR_A²+SR_B²), and √N for the pods) are
special cases of it. No IC estimation, no exercise, nothing in the assignment.
It costs about eighty words and it names the pattern they have already seen twice.

The alternative is to drop it entirely and let the two derived results stand
alone. That is defensible; it just leaves the pattern unnamed.

### 2 · A6 is currently specified for the wrong half of the block

The working spec for Assignment 6 is *"scale your strategy by volatility, combine
it with the market, and find the weight that maximises the Sharpe ratio."*

**All of that is L13.** But A6 is due **Thu Nov 5**, which is the day after L14 —
so students would sit through a lecture whose entire point is *the optimizer does
not survive out of sample*, and then go home and run the optimizer. The
assignment would contradict the meeting they just left.

**Suggested rewrite: "size your own strategy three ways and defend one."** They
apply mean-variance, 1/N and risk parity to their own signal combined with the
market, compare the three, and argue for one in the memo. That uses L13's formula
*and* L14's scepticism, and it is the actual decision a portfolio manager makes.

Not urgent — A6 does not exist yet — but it should be settled before L13 is built,
because it changes what the Hands-On has to set up.
