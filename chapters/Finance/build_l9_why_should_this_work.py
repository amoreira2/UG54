"""Build L9 · Why Should This Work? — from chapters/Finance/L9_DESIGN.md"""
import json, re

C = []
def md(s): C.append(("markdown", s.strip("\n")))
def co(s): C.append(("code", s.strip("\n")))

# ─────────────────────────────────────────────── 0-3  front matter
md("""
# Why Should This Work?

## 🎯 Learning Objectives

By the end of today you will be able to:

1. **Name the three explanations** for a replication gap, and say why the data cannot separate them
2. **Count how many independent bets** a set of correlated strategies really represents
3. **Say who is on the other side** of a trade, and what makes them willing
4. **Distinguish a risk premium from a bad business** when both show up as a low price
5. **Judge whether a risk is one you can bear** — at the size you intend to trade
6. **Specify an ambiguous performance question** precisely enough to get one answer
""")

md("""
## 📋 Today's Plan

1. [The gap, and three explanations](#gap)
2. [You tested fewer things than you counted](#count)
3. [Risk for whom?](#whom)
4. [A high expected return is a low price](#adverse)
5. [🔄 One anomaly, all the way down](#lowvol)
6. [🎯 Prompt it: what was the worst drawdown?](#prompt)
7. [What to ask before you trade a signal](#checklist)
8. [🛠️ Hands-On: your strategy's counterparty](#ho1)
9. [🎯 Challenge: another family](#challenge) — *homework*
10. [Key takeaways](#takeaways)
""")

md("""
---

## 🛠️ Setup
""")

co("""
#@title Setup — run this first
import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt
from scipy.stats import norm
%matplotlib inline
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = [11, 4]
import warnings; warnings.filterwarnings('ignore')

BASE = "https://raw.githubusercontent.com/amoreira2/UG54/refs/heads/main/assets/data"

# The same 29 long-shorts as last time, plus the published t-statistics.
L    = pd.read_parquet(f"{BASE}/longshort_29.parquet")
menu = pd.read_csv(f"{BASE}/signal_menu.csv").set_index('Acronym')
ff   = pd.read_csv(f"{BASE}/ff_monthly.csv", index_col=0, parse_dates=True)

sharpe = lambda x: x.mean() / x.std() * np.sqrt(12)
tstat  = lambda x: x.mean() / x.std() * np.sqrt(len(x))

print(f"{L.shape[1]} strategies, {len(L)} months, "
      f"{L.index[0]:%Y-%m} to {L.index[-1]:%Y-%m}")
""")

# ─────────────────────────────────────────────── §1
md("""
---

## 1 · The gap, and three explanations <a id="gap"></a>

Last time we audited *your* research process. Today, the published record.

Every one of our 29 strategies was published in a peer-reviewed journal with a
significant t-statistic. Let us re-run them and compare.

> **🤔 Predict first.** Write down a number. Of the 27 that report a
> t-statistic, how many do you expect to clear the Bonferroni bar we derived
> last time on our sample?
""")

co("""
#@title 🔒 What the journals reported, and what we get
rows = [(s, menu.loc[s, 'T-Stat'], tstat(L[s].dropna()))
        for s in L.columns if s in menu.index and pd.notna(menu.loc[s, 'T-Stat'])]
d = pd.DataFrame(rows, columns=['signal', 'published_t', 'our_t']).set_index('signal')

bar = abs(norm.ppf(0.025 / len(d)))          # Bonferroni, from Lecture 8
print(f"{len(d)} strategies with a published t-statistic\\n")
print(f"  mean published t          {d.published_t.mean():6.2f}")
print(f"  mean t in our sample      {d.our_t.mean():6.2f}")
print(f"  clear |t| > 1.96          {(d.our_t > 1.96).sum():3d} of {len(d)}")
print(f"  clear the Bonferroni bar  {(d.our_t > bar).sum():3d} of {len(d)}   (bar = {bar:.2f})")
print(f"  come out the WRONG SIGN   {(d.our_t < 0).sum():3d} of {len(d)}")

r = sm.OLS(d.our_t, sm.add_constant(d.published_t)).fit()
print(f"\\n  our_t = {r.params.iloc[0]:.2f} + {r.params.iloc[1]:.2f} x published_t"
      f"   R-squared {r.rsquared:.2f}")
""")

md("""
Six of twenty-seven survive. Six come out with the **opposite sign** to the
published paper.

And look at the regression. The published t-statistic explains **12%** of the
variation in ours. It is not that published results are uniformly inflated by
some factor you could correct for — it is that knowing a paper reported t = 9
rather than t = 3 tells you almost nothing about what you will get.

So what happened? Three explanations, and they demand opposite actions:

| | Mechanism | So the effect… |
|---|---|---|
| **Selection** | journals print what worked; the failures are in a drawer | never existed |
| **Overfitting** | the authors searched too — last lecture's lesson, applied to them | never existed |
| **Decay** | it was real; publication revealed it; other investors arbitraged it away | existed, and is gone |

> **📌 A replication gap cannot tell you which.**
>
> Two of the three say the effect was never there. One says you are ten years
> late. All three produce exactly the table above.

They are not hypotheses about this sample. They are claims about *how the sample
came to be in front of you*, and no amount of further testing reaches them. The
rest of today is the different question you have to ask instead.
""")

# ─────────────────────────────────────────────── §2
md("""
---

## 2 · You tested fewer things than you counted <a id="count"></a>

Before the different question, one more counting problem.

Last lecture's Bonferroni bar assumed 29 **independent** tests. Look at what
happens when three papers describe the same idea.
""")

co("""
#@title 🔒 Three papers, two journals, three names
fam = ['IdioVol3F', 'RealizedVol', 'MaxRet']
info = menu.loc[fam, ['Authors', 'Year', 'T-Stat']]
info['our_t'] = [tstat(L[s].dropna()) for s in fam]
print(info.to_string(), "\\n")
print("correlation of the three long-short return series:")
print(L[fam].corr().round(2).to_string())
""")

md("""
0.94, 0.96, 0.97.

These are not three strategies. They are one strategy, measured three ways, by
two sets of authors, in two journals, over fifteen years. If you hold all three
you have not diversified — you have tripled one position.

This cuts both ways. **For the literature**, ten papers on ten variations are not
ten confirmations — they are one test run ten times, by people who each knew what
the last one found. **For your portfolio**, last lecture's winner was holding all
29 equally, and that depends on the 29 being different bets. Across all 29 the
average pairwise correlation is 0.20, so mostly they are. Inside a family they
are not, and six volatility signals is one trade with extra steps.

> **📌 Count ideas, not papers.**
>
> Before you apply any multiple-testing correction, ask how many *distinct
> economic mechanisms* you actually tried. That number is smaller than the
> number of regressions you ran, and it is the one the correction wants.
""")

# ─────────────────────────────────────────────── §3
md("""
---

## 3 · Risk for whom? <a id="whom"></a>

Here is the pivot, and everything after it depends on it.

Everything so far has treated risk as a property of an asset. It is not. **It is
a property of an asset for a particular investor.**

Why should any asset earn more than another? Not because it bounces around more.
Because it **pays off badly in bad times, and is hard to hold precisely when
investors are most stressed.** You are paid to own something that hurts you when
you can least afford it.

CAPM is one narrow version of this claim. It declares that "bad times" means
"months when the market falls," and so an asset's risk is its beta. That is a
strong assumption, and it is why CAPM alpha is not a verdict — it is a question.

Because "bad times" is a statement about *people*. Different people have
different ones: a lost job, a consumption drop, a house that falls with the
market, a credit line that disappears.
""")

md("""
Which is why the same asset is not equally risky for everyone. The cleanest case
is **background risk**.

Suppose you work in the automobile industry, with skills specific to it. Your
income already moves with that sector — you are long autos before you own a
single share. The right response is not to avoid stocks. It is to hold the
market **minus** autos. Your portfolio should differ from the average investor's
because *you* differ from the average investor.

That generalises into the only justification there is for not simply holding the
market:

| | | What you should do |
|---|---|---|
| **You are the average investor** | your circumstances are the market's | hold the market. Any deviation is a bet you have no reason to win. |
| **You genuinely differ** | what frightens them does not frighten you | take the other side, and collect for it |
| **You think you differ, and do not** | the most common case | you find out at the worst possible time |

> **💡 This links alpha to who you are, not just to what you believe.**
>
> Two investors can look at the same signal, agree completely about the
> statistics, and correctly reach opposite decisions.

And then the part that is easy to miss, which makes the whole thing
self-limiting:

> **⚠️ As you scale up, you become the investor who bears the risk.**
>
> "Risky for them, not for me" is a statement about a *small* position. Put
> enough capital behind it and the exposure that was somebody else's problem is
> now yours — you are the one who has to hold through the drawdown, meet the
> margin call, and explain it to a client.
>
> And past you: if everyone held it, prices would adjust and the premium would
> shrink. So ask of any hundred-dollar bill on the pavement — **can the world
> support everyone picking it up?** A strategy that needs you to be one of the
> few has a capacity, and you should know roughly what it is.
""")

# ─────────────────────────────────────────────── §4
md("""
---

## 4 · A high expected return is a low price <a id="adverse"></a>

The second half of the pivot, and the more uncomfortable one.

Every anomaly is stated as *"these stocks earn more."* Turn it around, because it
is the same sentence: **these stocks are cheap.** Somebody is selling them to you
at that price and is content to do so. Why?

Two families of answer, and they are not the same thing at all:

| | Why the price is low | What you are buying |
|---|---|---|
| **Cash flows** | the market expects the business to do badly — and is right | a bad business at a fair price. There is no premium here. |
| **Risk** | the payoff is bad in states investors care about | compensation for bearing something real |

Both produce a low price today; only one pays you. And a backtest of high average
returns is equally consistent with a third case — a period in which the bad news
simply did not arrive.

If you cannot say which you are looking at, the honest default is the
uncomfortable one: **the other side may know something you do not.** That is not
cynicism. It is what a price *is* — somebody's willingness to trade at it.

> **📌 The question to ask of any signal**
>
> Not *"does this predict returns?"* — you already know how to check that. Ask
> **"who is selling to me, and what makes them willing?"** If you cannot name
> them, you are the one being selected.
""")

# ─────────────────────────────────────────────── §5
md("""
---

## 🔄 5 · One anomaly, all the way down <a id="lowvol"></a>

Let us run one strategy through all of it. **Low volatility.**

**The claim.** Stocks with low volatility, low beta and low lottery-like payoffs
earn more than their risk justifies. Ang, Hodrick, Xing and Zhang (2006); Bali,
Cakici and Whitelaw (2011). Three of our 29 — and, from §2, one trade.

**Who is on the other side?** Many investors want equity-like returns and cannot
or will not borrow to get them: mandates forbid leverage, regulation penalises
it, margin is expensive. If you cannot lever a safe stock, the only way to reach
for return is to *buy a risky one*. That bids up high-beta and lottery-like
names, and leaves the quiet ones cheap.

Notice what kind of answer that is. It names a counterparty, and their reason is
a **constraint** — not a mistake. Constraints do not get arbitraged away by
someone pointing them out.

**So is it risky for you?** Only if you are unconstrained: if you can borrow, and
if you can hold. That is exactly the §3 test. Here is what holding it required.
""")

co("""
#@title 🔒 What holding low-volatility actually felt like
x = L['IdioVol3F'].dropna()
cagr = lambda s: (1 + s).prod() ** (12 / len(s)) - 1

print(f"{'':14s}{'compounded':>12s}{'vol':>9s}")
for lab, sl in [('1980-1997', x.loc[:'1997-12-31']), ('1998', x.loc['1998']),
                ('1999', x.loc['1999']), ('2000', x.loc['2000'])]:
    ann = cagr(sl) if lab == '1980-1997' else (1 + sl).prod() - 1
    print(f"  {lab:12s}{ann:>11.1%}{sl.std()*np.sqrt(12):>9.1%}")

w = (1 + x).cumprod()
print(f"\\n  $1 in {x.index[0]:%Y-%m}  ->  ${w.max():.2f} at the peak ({w.idxmax():%Y-%m})")
print(f"  {'':13s}      ->  ${w.min():.2f} at the trough ({w.loc[w.idxmax():].idxmin():%Y-%m})")
print(f"  {'':13s}      ->  ${w.iloc[-1]:.2f} at the end ({x.index[-1]:%Y-%m})")

b = sm.OLS(x, sm.add_constant(ff.loc[x.index, 'Mkt-RF'])).fit()
print(f"\\n  market beta {b.params.iloc[1]:+.2f}    "
      f"CAPM alpha {b.params.iloc[0]*12:+.1%}/yr (t = {b.tvalues.iloc[0]:.2f})")
""")

md("""
Eighteen years of 15% a year, and then 1999 takes 60% of it back in twelve
months.

The drawdown is not a footnote — **it is the story.** The strategy is short
lottery stocks, and in a bubble lottery stocks are exactly what runs. So 1999 is
not the strategy breaking. It is the risk the economic story predicted, arriving
in the state of the world where the story says it should.

That is what a risk premium looks like from the inside: not a free lunch with an
occasional off year, but payment for holding something that loses badly at the
worst moment. You do not get paid unless the bad moment is genuinely possible.
""")

# ─────────────────────────────────────────────── prompt moment
md("""
### 🎯 Prompt it — what was the worst drawdown? <a id="prompt"></a>

We need this number to finish the argument. The claim on the table is that
harvesting this premium required leverage, and that leverage is what turns a bad
year into a forced exit. To say that we need to know how bad it got.

> **🤔 The question.** *"What was this strategy's worst drawdown?"*
>
> Write the prompt. Before you do, think about what this portfolio **is** — and
> what you are dividing by.
""")

co("""
# === YOUR TURN ===
MY_PROMPT = \"\"\"
                                    ← write your prompt here
\"\"\"

# ---- paste the AI's code below ----

""")

co("""
#@title 🔒 Check — four defensible answers, and they are 46 points apart
def maxdd(s):
    c = (1 + s).cumprod(); dd = c / c.cummax() - 1
    return dd.min(), dd.idxmin()

cs = x.cumsum()
rows = [("compounded, funded 1-for-1 with equity",) + maxdd(x),
        ("cumulative sum of returns (no capital base)",
         (cs - cs.cummax()).min(), (cs - cs.cummax()).idxmin()),
        ("compounded at 2x leverage",) + maxdd(2 * x),
        ("compounded at 3x leverage",) + maxdd(3 * x)]

print("«What was this strategy's worst drawdown?»\\n")
for lab, v, t in rows:
    print(f"  {lab:46s}{v:8.1%}   trough {t:%Y-%m}")

r12c = (1 + x).rolling(12).apply(np.prod, raw=True) - 1
r12s = x.rolling(12).sum()
print(f"\\n  and 'worst 12 months' is itself two questions:")
print(f"  {'compounded':46s}{r12c.min():8.1%}   ending {r12c.idxmin():%Y-%m}")
print(f"  {'summing the monthly returns':46s}{r12s.min():8.1%}   ending {r12s.idxmin():%Y-%m}")
print(f"\\n  so is '1999':")
print(f"  {'compounded over the calendar year':46s}{(1+x.loc['1999']).prod()-1:8.1%}")
print(f"  {'monthly mean x 12':46s}{x.loc['1999'].mean()*12:8.1%}")
print(f"\\n  the worst 12 months run {r12c.idxmin() - pd.DateOffset(months=11):%Y-%m} "
      f"to {r12c.idxmin():%Y-%m} — straddling the year end")
""")

md("""
### There is no capital, so there is no denominator

A long-short portfolio's weights sum to zero. You are not putting money in — you
are financing the long leg with the short leg. So "drawdown," a loss *relative to
what*, is undefined until you say what capital you posted.

Every line above is correct code. They differ by up to **46 percentage points**,
entirely because of an assumption nobody wrote down. A terse prompt returns
`(1 + r).cumprod()`, which silently assumes 1-for-1 equity funding and never
says so.

The last two rows are the argument we came for:

> **⚠️ At 2× you lose 96%. At 3× you are wiped out — in June 2000, three months
> after the bottom, before any of the recovery.**
>
> Harvesting this premium required leverage. Leverage is what converts a bad year
> into a margin call and a forced sale at the trough. **The risk that was other
> people's became yours the moment you scaled.**

And note the calendar-year trap. Ask about "1999" and you miss the actual
episode, which runs March 1999 to February 2000 and straddles the year end.

> **📌 When a question has more than one right answer, the specification is the
> work.** Say what you are dividing by, whether you compound or sum, and over
> what window. The AI will not ask.
""")

co("""
#@title 🔒 Growth of $1, and the Lecture 8 callback
fig, ax = plt.subplots()
ax.plot(w.index, w.values, lw=1.4, color='#333333')
ax.axvline(pd.Timestamp('1998-09-30'), color='#b03030', lw=0.9, ls='--')
ax.set_yscale('log'); ax.set_ylabel('growth of $1 (log scale)')
ax.set_title('Low-volatility long-short, 1980-2000', loc='left', fontsize=11)
ax.annotate('peak, Sep 1998', xy=(pd.Timestamp('1998-09-30'), w.max()),
            xytext=(-105, -14), textcoords='offset points', fontsize=9, color='#b03030')
plt.tight_layout(); plt.show()

print(f"  Sharpe 1980-1990 (Lecture 8's estimate sample)  {sharpe(x.loc[:'1990-12-31']):.2f}")
print(f"  Sharpe 1991-2000                                {sharpe(x.loc['1991-01-31':]):.2f}")
""")

md("""
This was Lecture 8's in-sample winner — Sharpe 1.37 in the estimate sample, 0.22
in the decade after — and we filed it under overfitting.

Now we can say something last lecture could not. **That collapse is not obviously
selection.** The strategy did what its economic story said it would, in the one
state of the world where the story predicts pain. Same numbers, opposite reading,
and the reading changes what you do: if it is overfitting you drop it; if it is
the premium being paid for, you size it to survive the next 1999.

Nothing in the returns tells you which. Only the story does — and it has to have
been written down *first*.
""")

# ─────────────────────────────────────────────── §6
md("""
---

## 6 · What to ask before you trade a signal <a id="checklist"></a>

Five questions. Take them to the pitch on Wednesday.

1. **Who is on the other side, and what makes them willing?**
2. **Is their reason a constraint, a preference, or an error?**
   Constraints persist. Errors get arbitraged. Preferences depend on who shows up.
3. **Is the risk one *you* can bear** — at the size you actually intend to trade?
4. **What would you have to see to stop believing?** Name it now, in advance,
   while it is still cheap to name.
5. **If the answer to (1) is "I don't know," you are the counterparty.**

None of these are statistical. That is the point of the whole lecture: once the
backtest is honest — and Lecture 8 was about making it honest — everything left
that matters is economics.
""")

# ─────────────────────────────────────────────── Hands-On
md("""
---

## 🛠️ Hands-On: Your Strategy's Counterparty <a id="ho1"></a>

Two things about your group's signal, one measured and one argued.

> **🤔 Predict first.** How correlated do you think your signal is with the
> closest other strategy in the 29? Write the number down before you run it.
""")

co("""
# === EDIT + YOUR TURN ===
MY_SIGNAL = "GP"      # ← your group's signal

# 1. Who are your neighbours? The three most correlated strategies.
nb = L.corr()[MY_SIGNAL].drop(MY_SIGNAL).sort_values(ascending=False).head(3)
print(f"{MY_SIGNAL} — closest neighbours\\n")
for s, c in nb.items():
    print(f"  {s:22s} corr {c:+.2f}   {menu.loc[s,'Cat.Economic'] if s in menu.index else ''}")

# 2. Your worst episode. State the definition — don't let the code choose for you.
mine = L[MY_SIGNAL].dropna()
dd_value, dd_date = ____      # hint: maxdd(mine), compounded and funded 1-for-1
print(f"\\n  worst drawdown {dd_value:.1%}, trough {dd_date:%Y-%m}")
print(f"  market that month: {ff.loc[dd_date,'Mkt-RF']:+.1%}")
""")

md("""
### Compare with the room

- **How close is your nearest neighbour?** Above 0.8 and you should be able to
  say what the shared mechanism is. If you cannot, you do not yet know what your
  signal measures.
- **When was your worst episode?** Compare trough dates across the room. If half
  the class troughs in the same month, the class does not hold ten strategies.
- **Now the hard one.** Who is on the other side of your trade, and what makes
  them willing? A constraint, a preference, or an error? You will be asked this
  on Wednesday, so it is worth having an answer you believe.
""")

# ─────────────────────────────────────────────── Challenge
md("""
---

## 🎯 Challenge: Another Family <a id="challenge"></a>

*Homework — due before the next class.*

§2 took the volatility family apart. Do the same to **valuation**: `BM`
(Stattman 1980), `EP` (Basu 1977) and `EntMult` (Loughran and Wellman 2011).
Three papers, three decades, one economic idea — or so it is usually described.

Throughout, the **composite** means the equal-weighted average of the three
monthly return series.

### Q1 — How many ideas is this?

Report the **mean pairwise correlation** of the three long-short return series —
the average of the three off-diagonal entries of the correlation matrix.

> **📌 Required variable names:**
> ```python
> fam_corr = ____   # mean pairwise correlation of BM, EP, EntMult
> ```
""")

co("""
# Your work here


fam_corr = ____

print(f"mean pairwise correlation: {fam_corr:.2f}")
""")

md("""
### Q2 — The worst episode

Maximum drawdown of the composite, **compounded, funded 1-for-1 with equity** —
the first row of the table in class. Report it as a negative decimal
(−0.30 means −30%).

Then look at *when* the trough falls, and compare it with the low-volatility
trough from class.

> **📌 Required variable names:**
> ```python
> val_dd = ____     # maximum drawdown, negative decimal
> ```
""")

co("""
# Your work here


val_dd = ____

print(f"max drawdown: {val_dd:.1%}")
""")

md("""
### Q3 — Is it a hedge?

Regress the composite on the excess market return and report the **beta**.

Then ask what it means. A negative beta says the strategy makes money when the
market falls. If that is true, the CAPM says it should earn *less* than the
risk-free rate, not more — so a positive average return alongside a negative beta
is a puzzle the model cannot absorb.

> **📌 Required variable names:**
> ```python
> val_beta = ____   # market beta of the composite
> ```
""")

co("""
# Your work here


val_beta = ____

print(f"market beta: {val_beta:+.2f}")
""")

md("""
### Q4 — The memo

> **📝 Your task — maximum eight sentences.**
>
> Your PM read a note claiming the firm holds "three independent value signals"
> and wants to know whether that is true and whether to add a fourth.
>
> Say how many bets those three actually are, and how you know. Say when the
> composite had its worst episode, and what it means that the low-volatility
> strategy — a completely different economic idea — had its worst episode in the
> same month. Then answer the question the whole lecture has been building
> toward: **who is on the other side of the value trade, and is their reason a
> constraint, a preference, or an error?** Say which, and say what you would have
> to observe to change your mind.
""")

co("""
MEMO = \"\"\"
Write your memo here. Don't delete the surrounding triple quotes.
\"\"\"
print(MEMO)
""")

# ─────────────────────────────────────────────── submission
md("""
---

## 📤 Submission <a id="submit"></a>
""")

co("""
# === 📤 SUBMISSION CELL — Run this last ===
import json, base64, hashlib, datetime as dt

required = ["fam_corr", "val_dd", "val_beta", "MEMO"]
missing = [v for v in required if v not in globals()]
if missing:
    raise NameError(f"\\n❌ Missing before submission: {missing}")

payload = {
    "assignment": "L9_WhyShouldThisWork_AI",
    "ts": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
    "answers": {k: float(eval(k)) for k in required if k != "MEMO"},
    "memo": MEMO.strip(),
}
blob = json.dumps(payload, sort_keys=True)
checksum = hashlib.sha256(blob.encode()).hexdigest()[:8]
token = f"UG54::{checksum}::{base64.b64encode(blob.encode()).decode()}"

print("=" * 72)
print("📋  COPY THE LINE BELOW AND PASTE INTO THE SUBMISSION FORM")
print("=" * 72)
print(token)
print("=" * 72)
print("Submission form: https://forms.gle/yazZ8bbatL87jdJi7")
""")

# ─────────────────────────────────────────────── takeaways
md("""
---

## 🧠 Key Takeaways <a id="takeaways"></a>

1. **A replication gap has three explanations** — selection, overfitting, decay —
   and no amount of data separates them. Two say never trade it; one says you are
   late.

2. **Count ideas, not papers.** Three volatility papers correlate 0.94 to 0.97.
   That is one trade with three citations.

3. **Risk is a property of an asset for an investor**, not of the asset. Deviate
   from the market only if you differ from the average investor.

4. **A premium is compensation for paying off badly in bad times** — and whose
   bad times decides who gets paid. CAPM is the special case where bad times means
   the market falling.

5. **As you scale, you become the investor bearing the risk.** "Risky for them,
   not for me" is a claim about a small position.

6. **A high expected return is a low price.** Ask who is selling and why. A
   constraint persists; an error gets arbitraged; if you cannot name them, you are
   the counterparty.

7. **A drawdown is undefined for a long-short until you say what capital you
   posted.** Four defensible answers, 46 points apart, same return series.

8. **The 1999 collapse is the story arriving, not the strategy breaking** — and
   nothing in the returns tells you which. Only a theory written down beforehand
   does.

---

### Next class

You pitch. Five minutes: what your strategy is, what the evidence looks like, and
question 1 from the checklist — who is on the other side.
""")

md("""
---

## 📎 Appendix <a id="appendix"></a>
""")

co("""
# ═══════════════════════════════════════════════════════════════════════
# 📎 APPENDIX — the full replication table
# ═══════════════════════════════════════════════════════════════════════
out = d.copy()
out['ratio']  = out.published_t / out.our_t
out['sharpe'] = [sharpe(L[s].dropna()) for s in out.index]
out['cat']    = [menu.loc[s, 'Cat.Economic'] for s in out.index]
print(out.sort_values('published_t', ascending=False).round(2).to_string())
""")

nb = {"cells": [{"cell_type": t,
                 "metadata": {},
                 "source": s.splitlines(keepends=True),
                 **({"outputs": [], "execution_count": None} if t == "code" else {})}
                for t, s in C],
      "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                   "language_info": {"name": "python", "version": "3.11"}},
      "nbformat": 4, "nbformat_minor": 5}

p = "chapters/Finance/L9_WhyShouldThisWork_AI.ipynb"
json.dump(nb, open(p, "w"), indent=1)
w = sum(len(re.findall(r"[A-Za-z'-]+", s)) for t, s in C if t == "markdown")
print(f"✅ {p}  {len(C)} cells  {w} md words ({w/1417:.2f} sessions)")
