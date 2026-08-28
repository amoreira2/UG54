# L9 · Why Should This Work? — design sketch

**Slot:** Meeting 9, Mon 5 Oct. **Feeds:** A4, due Thu 8 Oct.
**Status:** sketch. Supersedes the earlier "Anomalies (option b)" note.

**What changed.** The tour/depth/replication question was the wrong question. This
is **B plus the two parts of C that survive** — the three explanations, and
300-is-not-300 — unified by a single subject: **how to interpret evidence.**

---

## The one idea

> **A backtest tells you what happened. It does not tell you whether you should
> expect it to happen again. For that you need an answer to: who is on the other
> side of this trade, and why are they happy to be there?**

L8 asked whether the number is real. L9 asks what would have to be true about
*other investors* for it to keep being real — and whether you are the investor
who gets to collect.

---

## Two constraints on the build

**No mean-variance.** Students have not seen `Σ⁻¹μ`, the tangency portfolio, or
the efficient frontier — that is L13. `InterpretingFactorModels` leans on the
tangency portfolio in places and **those passages must be rewritten**, not
lifted. What students *do* have is **CAPM logic**, from L4 and L6, and that is
enough: "hold the market unless you differ from the average investor" is a CAPM
statement. They also have the **appraisal ratio** from L4, which the source
notebook uses.

**Use the source notebook's wording.** `InterpretingFactorModels.ipynb` already
says most of this well. Phrases to carry over intact:

- *"Assets earn higher expected returns not because they're riskier in general,
  but because they perform poorly in bad times and are hard to hold when
  investors are most stressed."*
- *"Even if your data says 'this works', equilibrium forces might say 'this
  can't scale.'"* — and the test: **"Can the world support everyone picking it
  up?"**
- *"This links alpha to **who you are**, not just what you believe."*
- The **background risk** example, verbatim: you work in the automobile industry
  with specialized human capital, your income already moves with that sector, so
  hold the market *minus* autos. It is the cleanest statement of "risk for whom"
  in the repo.
- *"If you find alpha, at least one of these must be false: the model is
  correct, or markets are efficient."* — L4 already plants this; L9 says the
  choice between them is **economic, not statistical**.
- The practitioner's five questions, which become §6.

---

## Structure

### §1 · The gap, and three explanations you cannot tell apart

Our 29 signals were all published significant. On 1980–2000:

| mean **published** t | **5.82** |
|---|---|
| mean **our** t | **1.87** |
| survive a corrected bar | **6 of 27** |
| **wrong sign** | 6 |

Regressing ours on theirs: `ours = 0.57 + 0.22 × published`, R² 0.12.
**Divide a published t-statistic by about four.**

Three explanations, and they imply opposite actions:

| | Mechanism | So the effect… |
|---|---|---|
| **Selection** | journals print what worked; failures are in a drawer | never existed |
| **Overfitting** | the authors searched too — L8's lesson, applied to them | never existed |
| **Decay** | it was real; publication revealed it; arbitrage removed it | existed, and is gone |

**A replication gap cannot distinguish them.** Two of the three say do not trade
it; one says you are too late. All three are consistent with the same table.

That is the problem the rest of the lecture solves — not statistically, because
statistics cannot solve it, but by asking a different kind of question.

### §2 · And you tested fewer things than you counted

L5's debt. Within an economic family the long-shorts correlate about **0.58**;
the published bar is a t-statistic on a *single* test. Ten papers on ten
variations are one test run ten times.

Concretely, and this is the bridge into §5:

| | Authors | Year | published t | our t |
|---|---|---|---|---|
| IdioVol3F | Ang et al. | 2006 | 3.10 | 2.61 |
| RealizedVol | Ang et al. | 2006 | 2.86 | 2.16 |
| MaxRet | Bali, Cakici, Whitelaw | 2011 | 2.83 | 1.72 |

Pairwise correlation of the three long-shorts: **0.94, 0.96, 0.97.**
Three papers, two journals, three names. **One trade.**

### §3 · Risk for whom?

The pivot. Everything so far has treated "risk" as a property of an asset. It is
not. **It is a property of an asset for a particular investor.**

> **Deviate from the market only if you are different from the average
> investor.**

Why should any asset earn more? Not because it is volatile — because it
**performs poorly in bad times, and is hard to hold when investors are most
stressed**. CAPM is one narrow version of that: it declares "bad times" to be
months when the market falls. But "bad times" is a statement about people, and
different people have different ones — a consumption drop, a lost job, a housing
crash, a credit freeze.

Which is why the same asset is not equally risky for everyone. The clearest case
is **background risk**: you work in the automobile industry with specialised
human capital, so your income already moves with that sector. The right response
is not to avoid equities — it is to hold the market *minus* autos. Your
portfolio is different from the average investor's because **you** are.

Three cases, and only one of them is a strategy:

| | | What you should do |
|---|---|---|
| **You are the average investor** | your circumstances are the market's | hold the market. Any deviation is a bet you have no reason to win |
| **You genuinely differ** | the thing that frightens them does not frighten you | take the other side, and collect for it |
| **You think you differ and do not** | the most common case | you will discover this at the worst possible time |

> **💡 This links alpha to who you are, not just what you believe.**

Then the part that makes it self-limiting, and which is easy to miss:

> **⚠️ As you scale up, you become the investor who bears the risk.**
>
> "Risky for them, not for me" is a statement about a *small* position. Put
> enough capital behind it and the exposure that was other people's problem is
> now yours — you are the one who must hold through the drawdown, meet the
> margin call, and explain it to a client. The premium was never free; it was
> compensation, and at scale you have taken the job of earning it.
>
> The same logic scales past you. If *everyone* tried to hold it, prices would
> adjust, expected returns would fall, and the premium would shrink. So even
> when you have found what looks like a hundred-dollar bill on the pavement,
> ask: **can the world support everyone picking it up?** A strategy that
> requires you to be one of the few is a strategy with a capacity, and you
> should know roughly what it is.

### §4 · Adverse selection: a high expected return is a low price

The second half of the pivot, and the more uncomfortable one.

Every anomaly is stated as "these stocks earn more." **Turn it around: these
stocks are cheap.** Somebody is selling them to you at that price and is content
to do so. Why?

Two families of answer, and they are not the same:

| | Why the price is low | What you are buying |
|---|---|---|
| **Cash flows** | the market expects the business to do badly, and is right | a bad business at a fair price. There is no premium. |
| **Risk** | the payoff is bad in states investors care about | compensation for bearing something real |

If you cannot say which, the default assumption is the honest one: **the other
side knows something you do not.** That is not cynicism, it is what a price *is*
— someone's willingness to trade at it.

> **📌 The question to ask of any signal**
>
> Not *"does this predict returns?"* — you already know how to check that. Ask
> **"who is selling to me, and what makes them willing?"** If you cannot name
> them, you are the one being selected.

### §5 · One anomaly, all the way down

Low-volatility investing. It carries every point above, on our own data.

**The claim.** Low-volatility, low-beta, low-lottery stocks earn more than their
risk justifies. Ang et al. (2006); Bali, Cakici and Whitelaw (2011).

**Who is on the other side, and why.** Many investors want equity-like returns
and cannot or will not use leverage — mandates, regulation, margin rules. To
reach for return they buy *high-beta* stocks instead of levering a safe one. That
bids up high-beta and lottery-like names, and leaves low-vol stocks cheap. The
mechanism is a constraint, not a mistake, and it names the counterparty exactly.

**Is it risky for you?** Only if you are unconstrained — if you can lever, and
hold. Which is the §3 test, applied.

**And here is what holding it actually felt like:**

**Corrected 2026-08-28.** The first pass annualised a single calendar year by
multiplying its monthly mean by 12, which is not what you would have lost.
Everything below is compounded, consistently.

| | compounded return | vol |
|---|---|---|
| 1980–1997 | **+15.4%/yr** (+1,200% total) | 16.2% |
| 1998 | +11.5% | 22.5% |
| **1999** | **−60.4%** | 37.6% |
| 2000 | +63.0% | 70.6% |

$1 in Feb 1980 becomes **\$16.68 by September 1998**, falls to **\$4.19 by
February 2000**, and ends the sample at \$9.35 — **it never recovers the peak.**
Maximum drawdown **−74.9%**, market beta **−0.70**, alpha **+20.1%/yr** (t = 4.21).

Read that against §3. The strategy is short lottery stocks. In a bubble, lottery
stocks are exactly what runs. So the drawdown is not the strategy failing — **it
is the risk the story predicted, arriving.** And harvesting the premium required
leverage, which is precisely what turns a −75% drawdown into a margin call and a
forced exit at the bottom. **The risk that was other people's became yours the
moment you scaled.**

**And the L8 callback.** IdioVol3F was the in-sample winner in Lecture 8 —
Sharpe 1.37 over 1980–90, then **0.22** over 1991–2000. Now we can say something
Lecture 8 could not: that collapse is not obviously selection or overfitting.
The strategy did what its economic story said it would do, in the state of the
world where that story predicts pain.

### §6 · What to ask before you trade a signal

Short closing checklist, and the thing to take to the project:

1. Who is on the other side, and what makes them willing?
2. Is their reason a constraint, a preference, or an error? *(Constraints persist.
   Errors get arbitraged. Preferences depend on who shows up.)*
3. Is the risk one **you** can bear — at the size you intend to trade?
4. What would you have to see to stop believing? Name it now.
5. If the answer to (1) is "I don't know," you are the counterparty.

---

## What L9 takes from the late conceptual lecture — and what is left

L9 pulls the Tier 5e material forward. Here is the honest accounting of what is
then covered here rather than there, and whether the late slot still has a job.

### Covered in L9 — gone from the late lecture

| From `InterpretingFactorModels` | Why it belongs at meeting 9 |
|---|---|
| Risk in bad times as the reason a premium exists | It is the answer to the question §1 leaves open. Waiting ten lectures means the anomaly evidence has gone cold. |
| Deviate only if you differ from the average investor | Needs only CAPM, which they have. |
| Background risk — the auto-worker example | Same. |
| Alpha means the model is wrong **or** markets are — and the choice is economic | L4 already plants half of it; leaving the resolution to December is too long a gap. |
| "Can the world support everyone picking it up?" | The natural close to §3's scaling argument. |
| The practitioner's five questions | They become §6, and the project needs them **now** — groups are choosing what to defend at Pitches I two days later. |
| CAPM as a special case of a general principle | Free: they know CAPM and nothing else is required. |

### Left for a late lecture — and it is not nothing

| Still uncovered | Why it cannot come forward |
|---|---|
| **Crowding** — *"how will I know if this trade is getting crowded?"* | Needs capacity and price impact, which is **L16**. Asking it at meeting 9 gets a shrug. |
| **Equilibrium with trading costs** — a premium that exists gross and not net | Needs L16 too, and it is the sharpest version of "can everyone do this?" |
| **Multifactor equilibrium** — what a second priced factor even means | Needs L15's risk models to be more than a list. |
| **Adding the anomaly as a factor** — the Case (1) response | Needs L15 and L18: you cannot sensibly add a factor to a model you cannot estimate. |
| **What the eigenvalue structure says about how many risks there are** | L18. |
| **Synthesis** — the whole argument re-run once costs, leverage and PCA are known | Only possible at the end, by construction. |

### Verdict

**The late slot survives, with a different job.** L9 takes the *foundations* —
why a premium can exist and who is entitled to collect it. What is left is the
*scaling* half: what happens to that argument once you know what trading costs,
how much capacity a strategy has, and how many distinct risks the data supports.

That is a better late lecture than the one currently planned, because it can use
everything the back half teaches instead of being a philosophy session grafted
onto the end. It should probably be retitled — something like *"What survives
contact with costs"* — and `MISSING_CONTENT` Tier 5e updated to say so.

**If you would rather not run it at all,** the loss is real but bounded: crowding
and net-of-cost equilibrium would need a home in L16, and the multifactor
material would go unsaid. That is a defensible trade if the slot is needed
elsewhere.

---

## What this replaces from the old sketch

**Dropped:** the file-drawer histogram (nice, not load-bearing), the decay test
we cannot run, Harvey–Liu–Zhu, McLean–Pontiff. §1 carries the statistical
argument in a third of the space the old note gave it.

**Still owed by L5 and paid here:** risk vs mispricing. §3 and §4 are what that
dichotomy actually rests on, and §5 gives it a worked case.

---

## The prompt-it moment

**"What was this strategy's worst drawdown?"**

Load-bearing: §5's argument is that harvesting the premium needed leverage and
the drawdown is what turns that into a forced exit. You cannot make that argument
without the number.

And the number is not one number. A long-short portfolio's weights sum to zero —
**there is no capital**, which is the thing Lecture 1 established and nobody
remembers by October. So "drawdown" is undefined until you say what you are
dividing by. Five defensible answers, all verified:

| definition | answer | trough |
|---|---|---|
| compounded, funded 1-for-1 with equity | **−74.9%** | 2000-02 |
| cumulative sum of returns, no capital base assumed | **−120.9%** | 2000-02 |
| compounded at 2× leverage | **−96.4%** | 2000-02 |
| compounded at 3× leverage | **−100.0%** — wiped out | 2000-06 |
| worst rolling 12 months, compounded | **−67.6%** | 2000-02 |

**And the trap nests.** "Worst rolling 12 months" is itself ambiguous: −67.6%
compounded, **−97.6%** if you sum the monthly returns instead. So is "1999" —
−60.4% compounded, **−81.6%** if you annualise the year's monthly mean by
multiplying by 12, which is a thing people do and it is wrong. A terse prompt
picks one of these silently and never says which. It also returns the *calendar*
year and misses that the worst twelve months run **March 1999 to February 2000**,
straddling the year end.

*(My own first pass through this made both mistakes — it reported −81.6% for 1999
and −97.6% for the worst twelve months without saying they were an annualised
mean and a sum. That is exactly the failure the moment is for.)*

Two things make this the right moment rather than a puzzle:

1. The failure is **conceptual, not syntactic**. Every one of those five lines is
   correct code. Choosing between them requires knowing that a self-financed
   position has no denominator until you supply one.
2. The last two rows **are the lecture**. At 2× you lose almost everything; at 3×
   you are gone before the recovery. The leverage that was required to harvest
   the premium is what stops you being there to collect it.

---

## Length

Target **1,400 lectured words**. §1 and §2 are compressed statistics — 350 words
between them. §3 and §4 are the argument and deserve 500. §5 is mostly a table
and a paragraph. §6 is a list.

The risk with this lecture is the opposite of L8's: it is nearly all prose, so it
will read short and run long. Build in a Hands-On where each group answers §6's
five questions about **their own** signal, and let that absorb the time.
