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

## §4 · Stocks or industries?

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

**Limitation to state out loud.** True industry-*neutral* momentum — ranking
stocks against their own industry peers — needs a stock-level industry code, and
the panel has none. Shipping SIC codes would unlock it; a note goes in TODO.

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

## Data

`assets/data/momentum_grid.parquet` — 22 series, 25 KB: the ten lookbacks, the
five skips, the seven construction variants, and industry momentum. Built by
`build_momentum_grid.py`. The notebook rebuilds momentum once from the raw panel
so students see it happen, then uses the cache for the grid.
