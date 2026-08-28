# L11 · Transaction Costs — design note

**Slot:** Meeting 14, Mon Oct 26 (the meeting after momentum). **Feeds:** A6.
**Status:** **built 2026-08-28** — `L11_TransactionCosts_AI.ipynb`, 41 cells,
2,197 lectured words = 1.55 sessions, 10 lecture cells clean in 2 s.

---

## The one idea

> **Every backtest in this course bought at the closing price. Nobody can do
> that. Whether a strategy survives is not a property of the strategy — it is a
> property of the strategy *and how much money you run*.**

The reorder put costs here for a reason: L10 just showed momentum earning 20% a
year, and momentum's turnover is **820% annualised**. The standard objection to
momentum is that trading eats it. That objection is now a computation.

**The number the lecture is built around, verified:**

| gross AUM (long side) | annual cost |
|---|---|
| $10m | 4.2% |
| $100m | 13.2% |
| $1bn | 41.6% |
| $10bn | 132% |

Momentum's ~20%/yr gross is gone at about **$230 million**. Same signal, same
data, same alpha — and it is a good business at $50m and a bad one at $500m.
That is Lecture 9's *"as you scale up you become the investor who bears the
risk"*, made arithmetic.

---

## The two sources, honestly assessed

### `TradingCosts_revamped_curated.ipynb` — 1,057 words, never taught

Better than its history suggests. Four things are load-bearing and go straight in:

- **The four sources of illiquidity** — exogenous costs, demand pressure,
  inventory risk, private information. One paragraph, and the last one is L9's
  adverse selection wearing a market-microstructure hat.
- **Implementation shortfall** = wish − actual, split into **execution cost**
  (trading toward the target) and **opportunity cost** (not getting there). The
  trade-off between them is the whole subject.
- **Absorption capacity** — `UsedVolume = trade / volume`, and the **max across
  stocks is the weakest link**. The right diagnostic, and it is one line.
- **The wish vs implementation portfolio regression.** This is the notebook's
  original contribution and nothing in EQI matches it: regress the implementable
  portfolio's return on the wish portfolio's, and read three numbers —
  **β ≠ 1 is free to fix** (lever up), **σ(ε) is noise you can only reduce by
  tracking more closely**, and **α is the actual cost of deviating.** The
  industry's single tracking-error number conflates all three and hides α.

Also worth keeping: the drift formula. You do not trade the whole target weight,
only the difference between it and what returns already left you holding.

**Skip:** the published-factor comparison at the end. L10 §5 now does that job
better, with correlations across four variants.

### EQI Chapter 10, "Market-Impact-Aware Portfolio Management" (pp. 365–386)

**Most of this chapter is unusable here, and it is worth saying why.** From
§10.3 on it is Baldacci–Benveniste–Ritter: adjoint operators, first-order
conditions on functionals, a matrix ODE, Kronecker products. That is a PhD
treatment and there is no undergraduate path through it.

Three things are gold:

- **The decomposition.** Cost = spread + temporary impact + permanent impact,
  and temporary impact dominates. Quotable in three lines.
- **The square-root law**, `c ≈ κ σ √(Q/V)`, *with its dimensional-analysis
  derivation.* This is the gem of the chapter and it is completely accessible:
  cost is dimensionless; you have dollars traded, dollars of market volume, and
  a volatility carrying units of 1/√time; there is only one way to combine them.
  **A physical-units argument that pins the exponent at ½ without any finance.**
  Students should see this — it is the best example in the course of a result
  you can get before you have any data.
- **Optimal liquidation as exponential decay.** With no alpha, the optimal policy
  is `x(t) = e^{−Γt} x(0)`: bleed the position out, faster when risk aversion or
  volatility is high, slower when costs are high. The single-asset version is
  scalar and needs no matrices.

**Deliberately deferred:** the no-impact limit recovering mean-variance is a
lovely result and it needs L13. Note it forward; do not teach it.

---

## Structure

### §1 · Turnover — the primitive nobody defined

`TODO.md` has flagged this since August: **turnover is never defined in L1–L10
and appears in none of the old assignments.** It gets defined here.

Turnover is not "how much you hold", it is **how much you replace**, and the
subtlety is that returns move your weights for free. You only trade the gap
between the new target and where drift left you:

$$w^{\text{drift}}_{i,t+1} = \frac{w^*_{i,t}(1+r_{i,t+1})}{1+r^p_{t+1}}
\qquad
\text{turnover}_t = \tfrac{1}{2}\sum_i \left| w^*_{i,t+1} - w^{\text{drift}}_{i,t+1}\right|$$

Verified for momentum, VW NYSE deciles: **66% one-way per month, 820% a year.**
Compare with value, which rebalances annually. The contrast is the section.

### §2 · What one trade costs

The decomposition, then the square-root law, then the derivation.

$$c \;\approx\; \kappa\,\sigma\sqrt{Q/V}$$

Do the dimensional analysis on the board. It takes four lines and it produces the
exponent ½ out of nothing but units. Then calibrate κ and show what the formula
says: **cost is convex in size**, so doubling your fund does not double your
costs, it multiplies them by √2 — per dollar. Total cost rises with the 3/2
power.

### §3 · Absorption capacity — how big can you get?

`UsedVolume = trade / volume`, per stock per month. The max is the weakest link;
the 95th percentile tells you whether dropping the worst 5% of names would fix
it.

Then the headline table above, and the break-even. **This is the centre of the
lecture.** It is also the answer to a question every group will face in the
project: *how much money could this actually run?*

### §4 · What's left — the net-of-cost backtest

Re-run L10's momentum net of costs at several fund sizes and plot the Sharpe
ratio against AUM. The gross number is a horizontal line; the net number crosses
zero. Everything students have built so far lives on that horizontal line.

### §5 · Making it cheaper

The wish vs implementation portfolio. Volume-weight instead of value-weight, or
drop the illiquid tail, then run the regression and read β, σ(ε), α.

The lesson is that **you buy cost reduction with tracking error**, and the
question is the exchange rate. α is what you actually paid.

### §6 · Trade slower — and how slow

EQI's optimal-liquidation intuition, single asset, no matrices. You never
rebalance all the way to the target; you move part of the way, and the fraction
depends on three things: how fast the signal decays, how expensive trading is,
and how much tracking error you will tolerate.

This is where momentum's problem becomes visible from a second angle: a signal
that decays in months *cannot* be traded slowly. **Value can be implemented
patiently; momentum cannot.** That is why they have different capacities even
though the cost formula is the same.

Close with the practical rule from the notebook: set a tracking-error band, do
nothing inside it, trade back to the edge when you leave it.

---

## The prompt-it moments — two, per `PLAN.md`

**P1 · "How much does this strategy trade?"** Load-bearing, since every cost
number is turnover times a rate. Underspecified in at least four ways: one-way or
two-way; as a fraction of what; does drift count as trading; and what about the
short leg. A terse prompt returns `weights.diff().abs().sum()`, which ignores
drift entirely and overstates momentum's turnover by a wide margin. The check
prints the drift-aware and drift-naive numbers side by side.

**P2 · "Apply a cost model and tell me what's left."** The question the whole
lecture points at, and it cannot be answered without stating the fund size — a
parameter the request does not contain and the model will silently invent.

---

## Length budget

**Target 1,500 lectured words.** L10 came in at 2.80 and is being split; L11 must
not repeat that. Discipline: §3 and §4 are the lecture. §1 is a formula and one
table. §6 is prose and one picture, no derivation.

If it runs long, §5 is the section to move to the appendix — it is the most
self-contained and the least load-bearing for A6.

## Data

Everything needed exists. Dollar volume is recoverable from
`signals/DolVol.parquet`, which stores **−log(dollar volume in $m)** — the signal
files are sign-flipped so that high means long, and `Size` correlating −1.000
with log market cap is the proof. Verified: monthly volume/market-cap runs 4–6%
across size buckets, and GE in December 2000 shows $475bn of market cap against
$23.5bn of monthly volume.

A cached `momentum_costs.parquet` will probably be wanted for §4, since the
net-of-cost backtest at five fund sizes is a slow loop.

## Built — what changed from this plan

**§5's premise was wrong and the data said so.** The notebook proposed
volume-weighting as the implementation portfolio. It does fix the tail — the worst
position drops from 1,406% of monthly volume to 100% — but **turnover jumps from
68% to 82%** because volume is noisier than market cap, and total cost goes *up*,
20.1% to 26.2% at $250m. The lecture now shows that failure and then uses the
blunter fix: drop the least liquid 40% before sorting. That gives the α/β/σ(ε)
framework a proper workout — β 1.04, σ(ε) 3.6%/yr, **α −2.1%/yr with t = −2.46**,
R² 0.97 — and a genuine size-dependent answer: the screen loses at $1bn and wins
from about $5bn up.

**Verified numbers as shipped** — all post-recalibration; see the section below
for what changed and why. Turnover 68.2%/mo for momentum against 12.2% for value,
and the drift correction is worth 4% on momentum but 36% on value, which is a
better prompt-moment payoff than expected. Used volume at $10bn: median 16.2%,
p95 846%, **23.1% of trades need more than the stock's entire monthly volume**
(4.3% at $1bn). Cost 3.4% at $100m rising to 50.0% at $100bn; **break-even
$13.4bn**; net Sharpe 1.00 gross → 0.82 at $100m → 0.65 at $1bn → 0.12 at $10bn →
−1.41 at $100bn. Decay: momentum 1.12 → 0.26 at six months and −0.38 at twelve;
value 0.44 → 0.45 → 0.22.

**Challenge answer key.** `value_capacity` **$53.8bn** — four times momentum's, on
a third of the gross return, purely because value trades 5.6× less.
`patient_net` **+10.1%** at $10bn against +2.4% impatient: rebalancing every
second month buys 8 points by giving up 2.9 points of gross return.
`screen_wins_at` **$10,000m** on the net-Sharpe criterion the question specifies
(the net-*return* crossover is earlier, around $5bn — worth being precise about
which one you ask for).

**Data shipped:** `l11_costs.parquet` (240×29), `l11_usedvolume.parquet` (424k
stock-months), `l11_decay.parquet`. Built by `build_l11_cost_cache.py`. Notebook
content lives in `l11_content.txt` and is assembled by
`build_l11_transaction_costs.py` — the split avoids the quote-escaping problems
that bit the L10 build.

## Recalibrated 2026-08-28 after AM

AM: *"I don't like this theory mumbo jumbo for the square root law... motivate
instead that it is natural that the participation rate matters... and that
volatility will matter due for example to adverse selection, and then discuss how
this empirically kind of fits the data — which is the most important thing. Cite
the Moskowitz et al. paper."*

**The dimensional-analysis derivation is out.** §2 now motivates the two
arguments directly — participation because liquidity is a finite resource that
refills, volatility because the counterparty bears inventory risk *and* cannot
tell whether you are informed, which is L9's adverse selection in its original
habitat — and then asks whether the shape fits.

It does. `assets/plots/marketimpact.jpg` was already in the repo: it is
**Frazzini, Israel and Moskowitz, "Trading Costs of Asset Pricing Anomalies"**,
realised impact on ~$1.7tn of live AQR trades. Fitting the 2004–07 curve gives
**9bp + 144bp·√(participation)**, tracking the data across the whole range, with
costs falling by 2010–13 and roughly doubling in 2008–09.
`marketimpact2.jpg` — the anatomy of one order, 11bp average impact split 2.5bp
temporary and 8.5bp permanent — opens the section.

### Checking against FIM caught a real error

Calibrating to that figure exposed a **units bug in the cost model**. Almgren's σ
is the volatility over the *execution horizon*; spreading a month's trade across
the month makes that **daily** volatility, and the first build used monthly. That
overcharged by √21 ≈ 4.6, and κ = 1 against FIM's implied 0.55 added the rest:
**costs were 8.4× too high, capacity 70× too low.**

Corrected model, now in `build_l11_cost_cache.py`:

$$c_i = \tfrac12\text{spread} + \kappa\,\sigma_i^{\text{daily}}\sqrt{Q_i/V_i},
\qquad \kappa = 0.55,\ \text{spread}/2 = 20\text{bp}$$

### What the numbers became

| | before | after |
|---|---|---|
| break-even | $236m | **$13.4bn** |
| cost at $1bn | 40.1% | 6.7% |
| net Sharpe at $1bn | −0.98 | **+0.65** |
| screen starts winning | $100m | ~$5bn (net return), $10bn (Sharpe) |
| value capacity | $859m | **$53.8bn** |
| `screen_wins_at` (Sharpe) | $100m | **$10bn** |
| `patient_net` | −1.4% at $1bn | **+10.1% at $10bn** |

The lesson survives intact and is now *more* honest: momentum is a real business
at $1bn (12.8%/yr net, Sharpe 0.65) and dead by $25bn. It also agrees with FIM's
own headline — proxy-based academic estimates overstated costs by roughly an
order of magnitude, and anomaly capacity is far larger than the pessimistic
literature claimed.

Two caveats are now in the notebook rather than in this file: κ comes from
post-2004 large-cap institutional flow while our sample is 1980–2000 when spreads
were quoted in eighths, so **every cost is an underestimate for the period**; and
the units trap is written up as a warning box, because the formula does not carry
its units with it.

**Lectured length rose to 1.84 sessions** from 1.55 — §2 is longer as prose than
it was as a derivation.

## Open question for AM — resolved

Both, in the end. κ is **calibrated to FIM's figure** (0.55) rather than
asserted, and it is still a dial the Hands-On makes students turn. The earlier
worry that "a few hundred million" was the robust answer turned out to be wrong
in the other direction — it was an artefact of the units bug.
