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

Three cases, and only one of them is a strategy:

| | | What you should do |
|---|---|---|
| **You are the average investor** | your circumstances are the market's | hold the market. Any deviation is a bet you have no reason to win |
| **You genuinely differ** | the thing that frightens them does not frighten you | take the other side, and collect for it |
| **You think you differ and do not** | the most common case | you will discover this at the worst possible time |

Then the part that makes it self-limiting, and which is easy to miss:

> **⚠️ As you scale up, you become the investor who bears the risk.**
>
> "Risky for them, not for me" is a statement about a *small* position. Put
> enough capital behind it and the exposure that was other people's problem is
> now yours — you are the one who must hold through the drawdown, meet the
> margin call, and explain it to a client. The premium was never free; it was
> compensation, and at scale you have taken the job of earning it.

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

| | return/yr | vol |
|---|---|---|
| 1980–1997 | **+15.7%** | 16.2% |
| 1998 | +13.1% | 22.5% |
| **1999** | **−81.6%** | 37.6% |
| 2000 | +74.3% | 70.6% |

Worst twelve months: **−98%, ending February 2000.** Maximum drawdown **−75%**.

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

## What this replaces and what it costs

**Dropped from the old L9 sketch:** the file-drawer histogram (nice, not load
bearing), the decay test we cannot run, Harvey–Liu–Zhu, McLean–Pontiff. §1
carries the statistical argument in a third of the space.

**Pulled forward:** the Tier 5e conceptual lecture from `MISSING_CONTENT`, which
was homeless and scheduled vaguely "toward the end." L5 already points forward to
it. Bringing it here means L5's pointer resolves one lecture later instead of ten,
and the equilibrium argument arrives while the anomaly evidence is still warm.

**Cost of that move:** the late-term slot loses its planned content. Options are
to let it go — this lecture covers the argument — or to keep a shorter version
late as a synthesis once students have seen costs, leverage and PCA.

**Still owed by L5 and paid here:** risk vs mispricing. §3 and §4 are what that
dichotomy actually rests on, and §5 gives it a worked case.

---

## The prompt-it moment

Candidate: **"Is the low-vol premium still there?"** — a question with no
well-defined answer until you say over what period, against what benchmark, and
whether you are asking about the raw return or the alpha. Worth building the
check so that four defensible specifications give four different answers.

Needs testing before it goes in.

---

## Length

Target **1,400 lectured words**. §1 and §2 are compressed statistics — 350 words
between them. §3 and §4 are the argument and deserve 500. §5 is mostly a table
and a paragraph. §6 is a list.

The risk with this lecture is the opposite of L8's: it is nearly all prose, so it
will read short and run long. Build in a Hands-On where each group answers §6's
five questions about **their own** signal, and let that absorb the time.
