# L10 · Momentum — design note

**Slot:** Meeting 13, Wed Oct 21 (first meeting after the midterm). **Feeds:** A5.
**Status:** built 2026-08-28.

---

## The one idea

> **The signal is one line of code. Everything that decides whether it makes
> money is the twenty decisions around it — and nobody writes those down.**

L10 is the "zero to one hundred" lecture: raw CRSP monthly returns in, a
long-short track record out, with every choice on the table made explicitly and
its cost measured.

Momentum is the vehicle because it needs **one dataset — prices** — so the entire
lecture can be about the choices instead of about data plumbing.

---

## §0 · Where signals come from (the survey)

Students have used shipped signals for nine lectures. Before building one they
should see the landscape, briefly: for each family, what data, from where, and
what you would have to decide.

| Family | Signal | Data | Where | The choices that bite |
|---|---|---|---|---|
| **Value** | book/market, E/P, EV/EBITDA | annual accounting + price | Compustat + CRSP | which fundamental; when the filing was *knowable*; annual or monthly rebalance |
| **Profitability** | gross profit / assets | income statement | Compustat | which line (gross, operating, net); which denominator |
| **Investment** | asset growth | balance sheet | Compustat | horizon; scale by what |
| **Issuance** | share count change | shares outstanding | CRSP or Compustat | split adjustment — the L8 leakage trap |
| **Return-based** | momentum, reversal, vol | prices only | CRSP | **today** |

Two lines to keep from the old notebooks: **"signal construction is ART, not
science"**, and the value framing `W ∝ F/P` — buy cheap, sell expensive, where
the whole game is which `F` you believe.

The point of the table is that return-based signals are the one family where the
data is free and clean, so the *only* thing left is the construction. That is why
they are the right teaching vehicle, and it is also why there are hundreds of
them.

---

## §1 · The claim

Jegadeesh–Titman (1993). Carry the old notebook's wording: momentum is that
stocks that have performed **relatively** well continue to perform **relatively**
well. And the contrast with value, which is good: value uses the *entire* history
of returns, because that is what a price is; momentum uses only the last twelve
months. **They are the same kind of bet on different windows** — and they point
opposite ways.

Daniel–Moskowitz's construction, quoted verbatim, because the lecture is about
taking it apart: rank on cumulative returns from t−12 to t−2, skipping one month
"to avoid the short-term reversals documented by Jegadeesh (1990)."

---

## §3 · Build it from the paper — revised 2026-08-28 after AM

**The skip month was priced but never explained, and the explanation given was
wrong.** The code comment said the shift exists "so the month before formation is
not in the signal", which reads as a tradability rule — but `ret_fwd` already
handles tradability, so that was not the reason. Daniel and Moskowitz state the
real one: *to avoid the short-term reversals*.

**New shape, per AM.** The construction is no longer handed over as code. Students
get the Daniel–Moskowitz paragraph and nothing else, with the recipe in words
inside a collapsed `<details>` block as a fallback. They build it by prompting.
Then the reveal, and then the skip.

The skip is the clause everyone drops — one subordinate phrase in the middle of a
long sentence — and it is worth **0.32 of Sharpe ratio**, 1.03 down to 0.70.

**The mechanism, demonstrated rather than asserted.** Trade the discarded month on
its own — sort on last month's return, buy the losers:

| | reversal (D1−D10) | momentum, skip | no skip | cost |
|---|---|---|---|---|
| value / NYSE | **0.08** | 1.03 | 0.70 | −0.32 |
| value / all | 0.11 | 1.13 | 0.83 | −0.30 |
| equal / NYSE | **1.54** | 0.93 | 0.53 | −0.40 |
| equal / all | **1.56** | 0.70 | 0.12 | −0.58 |

Reversal is a *small-stock* effect — 1.54 equal-weighted, 0.08 value-weighted,
because much of it is the bid-ask spread bouncing. And **the cost of not skipping
tracks the strength of reversal across all four constructions.** A momentum signal
that includes last month is a momentum bet plus a reversal bet pointing the other
way. `STreversal`, one of our 29, is exactly that month traded on purpose.

**What this replaced.** The old §3 centrepiece was the correlation-0.11 alignment
trap. It is demoted — the reference implementation now does the shift itself and
reports 0.999 — because the skip is the better teaching moment and the alignment
point was, as AM noted, resting on a wrong explanation of the skip.

**Consolidation.** The skip had been taught three times (the five-readings check,
§4's own skip sweep, and now §3). §4's skip section is gone and points back; the
second build-momentum prompt moment is folded into a short warning that keeps the
`shift(-1)` → 6.58 finding. L10 now has exactly two prompt moments, which is the
`PLAN.md` budget: build-from-the-paper (§3) and industry-neutral (§5b).

## §2 · Build it, and check it

From the raw panel: log returns → rolling 11-month sum → shift 1 → NYSE
breakpoints → value-weighted deciles → D10 − D1. **+20.0%/yr, Sharpe 1.03.**

The shipped `Mom12m` is +19.9%/yr, Sharpe 0.99. Same numbers.

**But the correlation is 0.113.** Not because the strategy differs — because one
series is dated by the month the signal was *formed* and the other by the month
the return was *earned*. Shift by one month and the correlation is **0.999**.

That is L2's `ret_fwd` lesson returning, and it is worth the cell: two series can
agree on every summary statistic and still be misaligned, and a correlation of
0.11 would have you concluding you had built something new.

---

## §3 · The decision tree — measured

**Lookback (skip = 1 throughout).** The hump, reproduced:

| J | 1 | 3 | 6 | 9 | **11** | 17 | 23 | 35 | 47 | 59 |
|---|---|---|---|---|---|---|---|---|---|---|
| Sharpe | 0.40 | 0.56 | 0.71 | 0.81 | **1.03** | 0.51 | 0.54 | 0.37 | 0.47 | 0.48 |

The peak sits exactly where the literature says. **But the long end does not
reverse** — +0.37, +0.47, +0.48 at 35, 47 and 59 months, all still positive.
The textbook wave (reversal → continuation → reversal) is not in this sample, and
the notebook says so rather than asserting the picture. The challenge makes
students settle it: t−60 to t−13, D1 − D10, comes out at Sharpe **−0.08**
(alpha vs momentum +0.9%/yr, t = 0.21). A null, and the memo has to take a
position on whether that is decay, construction, or never-there — L9's three
explanations, on a chart they built.

**The skip month.**

| skip | 0 | **1** | 2 | 3 | 6 |
|---|---|---|---|---|---|
| Sharpe | 0.64 | **1.03** | 0.98 | 0.87 | 0.45 |

**Not skipping costs 38% of the Sharpe ratio.** One line of code, and it is the
line an AI will not write unless you ask.

**Weighting, breakpoints, bucket count.**

| | Sharpe | vol |
|---|---|---|
| VW, NYSE breakpoints, deciles — *the standard* | 1.03 | 19.5% |
| EW, NYSE breakpoints, deciles | 0.93 | 16.7% |
| VW, all-stock breakpoints, deciles | **1.13** | 25.1% |
| EW, all-stock breakpoints, deciles | 0.70 | 22.0% |
| VW, NYSE, terciles | 0.45 | 13.2% |
| VW, NYSE, quintiles | 0.56 | 16.1% |
| VW, NYSE, 20 groups | 1.09 | 23.5% |

> **Same signal. Same data. Sharpe from 0.45 to 1.13.**

All-stock breakpoints look best and are mostly microcaps — the L3 lesson, priced.
Terciles to twentiles is the diversification-against-signal-strength trade from
the value notebook, and it is worth 0.64 of Sharpe ratio.

And the L8 callback: **that range is the researcher's degrees of freedom.** Seven
defensible constructions is seven tests, and the Bonferroni bar moves.

---

## §5 · The many momenta — added 2026-08-28

AM: *"a discussion of the many versions of momentum, with links... referencing the
many papers and variations people have done is illustrative of how much details
matter."* Placed **before** industries so that industry momentum reads as one
instance of a family rather than a one-off.

Fifteen published variations in a linked table — Jegadeesh–Titman, Carhart,
Chan–Jegadeesh–Lakonishok, Moskowitz–Grinblatt, Hong–Lim–Stein,
Lee–Swaminathan, Grundy–Martin, George–Hwang, Blitz–Huij–Martens, Novy-Marx,
Moskowitz–Ooi–Pedersen, Asness–Moskowitz–Pedersen, Da–Gurun–Warachka,
Barroso–Santa-Clara, Daniel–Moskowitz. Links are Google Scholar searches rather
than DOIs: they always resolve, they are not paywalled, and they land students on
a page with the PDF.

**Two of them we can settle live**, because `momentum()` already takes the dial as
an argument.

**Novy-Marx (2012), the echo — and it replicates.**

| | Sharpe |
|---|---|
| standard, months 2–12 | 1.03 |
| recent, months 2–6 | 0.62 |
| **echo, months 7–12** | **0.85** |

Correlation between recent and echo is only **0.38**. The ladder: echo on recent
**+10.7%/yr, t = 2.88**; recent on echo +6.3%/yr, t = 1.56. The older window
survives the recent one and not the reverse — the part of momentum that works is
the part you would have assumed was stale.

**This is a deliberate contrast with §6.** Moskowitz–Grinblatt does *not*
replicate here; Novy-Marx does. Set against L9's six-of-27, the lesson is that
replication is variable rather than hopeless, and the only way to know which case
you are in is to run it.

**Four variants we already hold.** Mom12m, Mom6m, ResidualMomentum,
AnnouncementReturn — correlations 0.24 to 0.79. Mom12m/Mom6m at 0.79 are one
trade; residual momentum at 0.53 and earnings momentum at 0.24 are not, and
earnings momentum has the highest Sharpe of the four (1.17). The takeaway for the
project: a signal correlating 0.8 with momentum is not new whatever it is called,
and one correlating 0.2 is — and now owes an explanation.

## §6 · Stocks or industries?

The question AM asked for. Industry momentum (Moskowitz–Grinblatt 1999) built
from the 49 Fama–French industry portfolios, same t−12 to t−2 rule, long the top
5 industries and short the bottom 5.

| | Sharpe | mean |
|---|---|---|
| stock momentum | **1.03** | +20.0%/yr |
| industry momentum | 0.60 | +11.5%/yr |
| correlation | **0.73** | |

Both work, and they are largely the same trade. The ladder from L4 settles which
is which:

| regression | alpha | t | verdict |
|---|---|---|---|
| stock on industry | **+11.5%/yr** | **3.76** | **survives** |
| industry on stock | −2.7%/yr | −0.88 | does not survive |
| stock on industry + FF3 | +14.4%/yr | 4.47 | survives |

**Momentum is a stock effect that shows up at the industry level, not an industry
effect that shows up in stocks.**

**And we get the opposite of the published paper.** Moskowitz–Grinblatt concluded
industry momentum subsumes individual momentum; our sample says the reverse. Do
not hide this — it is L9 arriving on schedule. Different sample (1980–2000 vs
their 1963–1995), 49 industries rather than 20, and they industry-adjust at the
stock level while we compare two portfolios. Any of those could do it. The honest
statement is that we cannot tell which, which is exactly L9 §1.

### §6b · Within industries — solved 2026-08-28

The first pass called within-industry momentum impossible for want of SIC codes.
**It is recoverable.** The KNS-style characteristics files carry `indmom`, the
stock's *industry* momentum, which is identical for every stock in the same
industry on the same date. Used purely as a group label it yields **48 industries
covering ~950 stocks a month, 1980–2000** — shipped as `industry_labels.parquet`,
built by `build_industry_labels.py`.

(Union-find over the whole sample collapses to two components, because stocks
change industry across 20 years. The per-date label is what is wanted anyway.)

**First, the price of the smaller universe.** Same dates, same construction:
Sharpe **0.99** on all 5,427 stocks against **0.42** on the largest 950.
*Momentum is largely a small- and mid-cap phenomenon*, which is a finding in its
own right and the reason every number below is modest. It also sets up L11: the
place momentum works best is the place it costs most to trade.

**Four constructions on the 950-stock universe:**

| | VW mean | VW Sharpe | EW mean | EW Sharpe |
|---|---|---|---|---|
| plain | +8.8% | 0.42 | +11.7% | 0.60 |
| **industry-neutral** (demean the signal by industry) | +5.6% | 0.41 | +9.1% | **0.83** |
| pure within-industry (T3 − T1, averaged) | +3.8% | 0.44 | +4.5% | 0.53 |
| across-industry (top 8 − bottom 8) | +5.0% | 0.32 | +8.4% | 0.53 |

**Equal-weighted, neutralising the industry bet makes momentum better: 0.83
against 0.60.** Value-weighted the gain vanishes: 0.41 against 0.42. Both weightings
are standard, and the answer to "within or across?" flips between them — which is
this lecture's own theme landing at the worst possible moment, and should be said
rather than smoothed over.

**The ladder, equal-weighted:**

| | alpha | t |
|---|---|---|
| within-neutral on across | **+6.1%/yr** | **2.77** |
| across on within-neutral | +1.5%/yr | 0.48 |
| **plain on within-neutral** | **−1.2%/yr** | −0.41 |

Same asymmetry as §5a, now at the stock level — and one step further: **plain
momentum has no alpha against the industry-neutral version.** Once you own
within-industry momentum, ordinary momentum adds nothing. The practical
conclusion is that momentum should probably be run industry-neutral.

**Caveats to state:** 950 large stocks only, where momentum is weak to begin
with; and the conclusion is weighting-dependent. We cannot verify it on the full
universe because we cannot label the full universe.

---

## §5 · Crashes

The panel stops in 2000, but `ff_monthly.csv` runs to 2026, so UMD reaches the
one that matters.

- **2009: −52.9%**, while the market returned **+28.3%**
- worst month **April 2009, −34.4%**; max drawdown **−57.8%**
- 2023: −20.4% with the market +20.8% — the same shape, recently

The mechanism, measured. Split months by whether the trailing 24-month market
return was negative:

| | β on the market | Sharpe |
|---|---|---|
| after a 24-month **bear** market | **−0.75** | 0.18 |
| after a 24-month **bull** market | +0.06 | 0.55 |

After a crash the short leg is beaten-down high-beta stocks. When the market
turns, they scream, and a market-neutral-on-average strategy turns out to have
been short the market at the worst possible moment. **Momentum's beta is a
function of the state you are in** — which is L9 §3 in return space, and the
setup for conditional strategies at meeting 19.

Vol-scaling — divide by trailing 6-month volatility — takes UMD from Sharpe 0.43
to **0.73** and the drawdown from −57.8% to **−36.7%**. Show it; do not derive it.
It is the one-line version of what L15 does properly.

---

## The prompt-it moment

**"Compute 12-month momentum for each stock."**

Load-bearing, and the whole lecture rests on it. Five readings, all valid code:

| | mean | Sharpe |
|---|---|---|
| t−12 to t−2, 11 months, skip 1 — *the standard* | +20.0% | **1.03** |
| t−12 to t−1, 12 months, no skip | +19.5% | 1.02 |
| t−11 to t−0, includes the current month | +14.4% | 0.70 |
| sums simple returns instead of compounding | +19.6% | 0.92 |
| **off-by-one the other way — includes next month** | **+143.7%** | **6.58** |

The last row is the one to sit on. It is a one-character error — `shift(-1)`
instead of `shift(1)` — and it does not raise, warn, or look wrong. It produces a
Sharpe ratio of 6.58, and **a Sharpe of 6.58 is not a discovery, it is a bug.**
The only defence is knowing what the number should roughly be before you compute
it.

---

## Challenge answer key

`ltr_sharpe` **−0.0807** · `ltr_alpha` **+0.0092** (t = 0.21) · `ltr_noskip`
**−0.4937**. The no-skip version is *strongly* negative because a t−48 to t−1
window still contains the twelve-month momentum signal — so removing the skip
does not add noise here, it adds momentum. Skip effect −0.41 at four years
against −0.39 at one year.

## Length budget

Target **1,700 lectured words**. §3 and §4 are the lecture; §0 is a table and two
sentences, §5 is short and mostly a plot.

## Code shape — revised 2026-08-28 after AM

The first build computed momentum as
`np.expm1(groupby.transform(lambda s: s.rolling(11).sum().shift(1)))` on log
returns, and read §4's grid from a cached parquet. **Both were wrong choices**,
and the old `Momentum.ipynb` had it right:

- **Rolling product of `(1+r)`, not a sum of logs.** The product *is* the formula
  in the markdown. The log detour is a numerical trick students must decode
  first, and it forces a `.clip(lower=-0.9999)` guard that exists only because
  `log(0)` blows up on the 15 delisting months. A product handles them correctly
  with no guard.
- **Named intermediate columns**, one idea per line — `cumret`, then `signal` —
  instead of four operations nested in one expression.
- **The skip as its own visible step**: `groupby('permno')['cumret'].shift(skip)`.
- **Two functions, and the signature is the decision tree.**
  `sort_portfolios(df, signal, ngroups, weights, breakpoints)` is Lecture 3's
  recipe and works on any signal — including the student's own in the Hands-On.
  `momentum(df, lookback, skip, **kwargs)` builds the signal and calls it.

§4 is now **live**, not cached: every number comes from calling `momentum()` in a
loop. 1.7 s per call, so the lookback sweep is ~16 s, the skip sweep ~8 s, and the
variant table ~12 s. Worth the wait, because changing an argument *is* the
experiment. `momentum_grid.parquet` and its build script are deleted.

Parameter semantics, documented in the docstring: `lookback=11, skip=1` spans
t−12 to t−2 counting from the month whose return you earn. Verified to correlate
**1.000000** with the previous log-based construction.

## Data

`assets/data/industry_labels.parquet` (48 industries × ~950 stocks/month) and
`assets/data/momentum_industry.parquet` (the four §5b treatments, both
weightings, built with the same rolling-product construction the notebook
teaches). Built by `build_industry_labels.py` and `build_momentum_industry.py`.
