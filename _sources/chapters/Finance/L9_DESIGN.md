# L9 · Anomalies — design note

**Slot:** Meeting 9, Mon 5 Oct. **Feeds:** A4, due Thu 8 Oct.
**Status:** planned, not built.

---

## The one idea

> **L8 audited your research process. L9 audits everyone else's.**
> Thirty published anomalies, every one of them significant when it was printed.
> Sixteen survive in our data. Six clear a corrected bar. Six have the wrong sign.

---

## What L9 already owes

Three debts written into earlier notebooks, all payable with data we have:

| From | Promise | Paid by |
|---|---|---|
| **L3** c29 | *"your t-statistic next to the published one — which should you believe?"* | §1 |
| **L5** §2 | risk vs mispricing — *"we test this properly in Lecture 9"* | §4, **and an honest failure** |
| **L5** §3 | *"300 papers is not 300 pieces of evidence"* | §3 |

L8 also hands over Bonferroni, so L9 does not have to teach it — it applies it.

## What does *not* exist

**There is no pre-AI notebook for this lecture.** `Factors.ipynb` (2,509 words)
looks like a candidate and is not: it is a descriptive tour of the families —
value, momentum, defensive, quality, with the economic story for each. That is
**L5's** content and L5 already covers it. Do not mine it here; L9 would turn
into a second zoo tour.

So L9 is built from scratch, unlike L8. The upside is that nothing needs
un-picking.

---

## MUST HAVE

### 1 · The replication gap — the spine

Every one of our 29 signals came from a published paper with a significant
t-statistic. Run them on 1980–2000 and:

| | |
|---|---|
| mean **published** t | **5.82** |
| mean **our** t | **1.87** |
| clear \\|t\\| > 1.96 in our data | **16 of 27** |
| clear the corrected bar (t > 3.13) | **6 of 27** |
| **wrong sign** in our data | **6** — BookLeverage, CompositeDebtIssuance, DolVol, Illiquidity, ReturnSkew, Size |

### 2 · The shrinkage line — the number to carry out of the room

Regress our t on the published t across the 29:

```
ours  =  0.57  +  0.22 × published        R² = 0.12
```

A published t of **6** predicts one of **1.91** in fresh data. The slope is 0.22.

> **The rule of thumb: divide a published t-statistic by about four.**

That single line is the most portable thing in the lecture. The low R² matters
too and should be said: the published t barely predicts which anomalies work.

### 3 · Three explanations, and you cannot tell them apart

The gap has at least three causes, and **they imply different actions**:

| | Mechanism | If this is it, then… |
|---|---|---|
| **Selection** | journals print what worked; the failures are in a drawer | the effect was never there — do not trade it |
| **Overfitting** | the original authors searched too — L8's lesson, applied to them | the effect was never there |
| **Decay** | it was real, publication revealed it, arbitrage removed it | it was real, and it is gone now |

The first two say the anomaly never existed. The third says it did. **A
replication gap on its own cannot distinguish them** — and most published
commentary talks as though it can.

### 4 · The file drawer, visible as an absence

Distribution of the **published** t-statistics of our 29:

```
 t 0.0–2.0     0
   2.0–2.5     2  ██
   2.5–3.0     4  ████
   3.0–4.0     5  █████
   4.0–5.0     3  ███
   5.0–7.0     4  ████
   7.0–20      9  █████████
```

**Not one published t-statistic below 2.0.** Hundreds of researchers tested
thousands of characteristics and, apparently, never once found something
insignificant worth reporting. The empty bin is the evidence.

### 5 · The decay test we cannot run — and saying so

L5 promised the risk-vs-mispricing test: does the premium shrink *after
publication*? Mispricing says yes, risk says no. Split each signal at its own
publication year and compare.

**On our panel this does not work, and the lecture should show why rather than
fake it.** Only **4** of the 29 have five years on both sides of publication
inside 1980–2000:

| | pre-pub | post-pub |
|---|---|---|
| Mom12m (1993) | 1.00 | 0.99 |
| Mom6m (1993) | 0.59 | 0.65 |
| STreversal (1990) | 0.32 | −0.12 |
| BookLeverage (1992) | −0.18 | −0.17 |

Mean decline 0.09 on **n = 4**. That is not a finding.

The obvious workaround — compare signals published before 1995 (Sharpe 0.22)
with those published after 2000 (0.46) — points the right way and is
**confounded**: the late-published ones were *discovered using* data overlapping
our sample, so of course they look good in it. Distinguishing decay from
selection needs the original sample end-dates, which the menu does not carry.

This is a genuinely good half-hour of the course: the test you want, the data you
have, and the discipline to report that the second does not support the first.

### 6 · 300 papers is not 300 pieces of evidence

Pay L5's other debt. Combine two facts they already own: within an economic
family the long-shorts correlate about **0.58**, and the published bar is a
t-statistic on a *single* test. Ten papers on ten variations of the same idea
are one test run ten times.

---

## NICE TO HAVE

Ordered by how much I would fight for each.

1. **Harvey–Liu–Zhu's "t > 3" as the new bar.** Free — we already compute it, and
   it happens to land on our Bonferroni-29 threshold of 3.13. One sentence.
2. **Chen–Zimmermann's counter-argument.** The signals *are* from their
   replication project, and their headline finding is that most anomalies **do**
   replicate — the pessimism is overstated. Presenting the critique without the
   rebuttal would be exactly the selection problem the lecture is about.
3. **Limits to arbitrage** — why a real anomaly might survive publication:
   shorting costs, capacity, career risk. Points forward to **L17**.
4. **McLean–Pontiff's decomposition** as a citation — post-publication decay of
   roughly 58%, of which about 26% is attributed to statistical bias. Gives the
   §3 table real numbers from a study that *could* run the test we cannot.
5. **What a good anomaly paper looks like now** — pre-registration, out-of-sample
   periods, an economic mechanism. Connects to A2's Q7, where they already had to
   commit to a story before computing.

## Explicitly NOT in L9

- The factor families and their economic stories — **that is L5.**
- Sample splitting, walk-forward, the diagnostics — **that is L8.**
- The equilibrium argument for why premia exist — that is the late-term
  conceptual lecture (`MISSING_CONTENT` Tier 5e).

---

## The prompt-it moment

**Comparing our results to the published ones.** *"Merge the published
t-statistics onto our results and see how they compare."*

Two traps, both live in our own files:

1. **Sign.** Published t-statistics are all positive — an author reports the
   profitable direction. Our signals are pre-signed, and **18 of 30 were
   flipped** on write. Merge naively and the six wrong-signed replications look
   like a bug rather than a result.
2. **Comparability.** A published t from 1963–1990 on NYSE-only large caps is
   not the same object as our t from 1980–2000 on everything. The number can be
   merged; the comparison needs an argument.

The check prints the merge both ways and the six sign flips.

---

## Length

Target **1,400 lectured words**. §1 and §2 are the lecture and should get half of
it. §5 is the one that will want to sprawl — cap it at the four-row table and one
paragraph.

L8 came in at 2,657 (1.88 sessions). L9 has less machinery and more argument, so
it should be easier to hold — but the argument is the part that grows.
