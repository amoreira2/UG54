"""
Build StatisticalFactors_AI.ipynb — Statistical Factor Models.

Covers the content Columbia B8420 puts in Session 6A:
  PCA and best low-rank approximation; the spiked covariance model;
  noise filtering; choosing the number of factors.
The maximum-likelihood / factor-analysis half is deliberately dropped —
it needs linear algebra our students don't have and adds little they can use.

Design: interactive class. Three HANDS-ON discovery blocks where the student
finds the result before we explain it:

  Hands-On 1  "Run it on nothing"      → noise produces a scree plot that
                                          looks like structure
  Hands-On 2  "Find the threshold"      → sweep a planted factor's strength,
                                          discover the BBP phase transition
  Hands-On 3  "Watch the factors move"  → rolling PCA, discover eigenvector
                                          sign flips and reordering

Data: Ken French 49 Industry Portfolios (monthly, free, no WRDS).
Verified numbers on the last 120 months (N=49, T=120, c=0.4083):
    MP upper edge      = 2.686
    eigenvalues above  = 2
    PC1 variance share = 0.556
    parallel analysis  = 2 factors  (p95 for PC1 = 2.661 — matches MP edge)
    pure-noise PC1 share ≈ 0.051
"""

import json
from pathlib import Path

OUT = Path(__file__).parent / "StatisticalFactors_AI.ipynb"


def md(t): return {"cell_type": "markdown", "metadata": {}, "source": t.splitlines(keepends=True)}
def code(t): return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": t.splitlines(keepends=True)}


cells = []

# ─── Title + Learning Objectives ──────────────────────────────────────
cells.append(md("""# Statistical Factor Models — Finding Factors You Never Specified
## 🎯 Learning Objectives

By the end of this notebook, you will be able to:

1. **Explain why the sample covariance matrix is unusable** for a large cross-section — and show that it cannot even be inverted
2. **Extract statistical factors with PCA** and read an eigenvector as a portfolio and an eigenvalue as that portfolio's variance
3. **Recognize that noise produces apparent structure** — and use the Marchenko–Pastur distribution to say how much structure noise alone should produce
4. **Decide how many factors are real** using the MP edge and parallel analysis, and know why "% variance explained" is not evidence
5. **Filter a correlation matrix** and connect noise filtering to the shrinkage you already know
6. **Audit AI-generated PCA code** — every model will hand you components with no noise check whatsoever"""))

cells.append(md("""## 📋 Table of Contents

1. [Setup](#setup)
2. [The Problem: You Cannot Estimate a Covariance Matrix](#problem)
3. [Three Kinds of Factor Model](#three)
4. [Pitfall Checklist](#pitfalls)
5. [Live Demo 1: Specify → Implement → Validate](#demo1)
6. [🛠️ Hands-On 1: Run It On Nothing](#ho1)
7. [The Spiked Covariance Model](#spiked)
8. [🛠️ Hands-On 2: Find the Detection Threshold](#ho2)
9. [Noise Filtering](#filter)
10. [Live Demo 2: Does Filtering Fix the Optimizer?](#demo2)
11. [How Many Factors?](#howmany)
12. [🛠️ Hands-On 3: Watch the Factors Move](#ho3)
13. [Why Practitioners Still Use Fundamental Factors](#why)
14. [🎯 Challenge: How Many Factors Are Real?](#challenge)
15. [Submission](#submit)
16. [Key Takeaways](#takeaways)
17. [📎 Appendix — Data Loading](#appendix)"""))

# ─── Setup ────────────────────────────────────────────────────────────
cells.append(md("---\n\n## 🛠️ Setup <a id=\"setup\"></a>"))

cells.append(code("""#@title Setup
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
%matplotlib inline
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = [11, 4.5]
plt.rcParams['font.size'] = 11
import warnings; warnings.filterwarnings('ignore')

from pandas_datareader.data import DataReader
np.random.seed(42)
print("✅ Libraries loaded")"""))

cells.append(code("""#@title Load 49 Industry Portfolios (Ken French, monthly)
ind = DataReader('49_Industry_Portfolios', 'famafrench', start='1970-01-01')[0] / 100
ind.index = pd.to_datetime(ind.index.to_timestamp()) + pd.offsets.MonthEnd(0)
ind.columns = [c.strip() for c in ind.columns]

# Ken French codes missing data as -99.99 (i.e. -0.9999 after /100). Drop those.
ind = ind.mask(ind < -0.99)
R = ind.dropna(axis=1).dropna()

print(f"Industries : {R.shape[1]}")
print(f"Months     : {R.shape[0]}   ({R.index.min().date()} to {R.index.max().date()})")
print(f"\\nFirst few  : {list(R.columns[:8])} ...")"""))

# ─── Section 1: the problem ───────────────────────────────────────────
cells.append(md(r"""---

## The Problem: You Cannot Estimate a Covariance Matrix <a id="problem"></a>

In Capital Allocation you learned the mean-variance weights:

$$W \propto \Sigma^{-1}\mu$$

That formula needs $\Sigma^{-1}$. So before you can optimize anything, you have
to estimate $\Sigma$ — and for a real cross-section that is much harder than it
looks.

With $N$ assets, $\Sigma$ has $N(N+1)/2$ distinct entries. Every one of them is
a parameter you must estimate from data. Let's count."""))

cells.append(code("""for N, T in [(49, 120), (100, 60), (500, 60), (3000, 120)]:
    n_params = N * (N + 1) // 2
    n_data   = N * T
    rank     = min(T - 1, N)
    invertible = "yes" if rank >= N else "NO — singular"
    print(f"N={N:5d}  T={T:4d} months | parameters {n_params:>9,} | "
          f"data points {n_data:>8,} | rank(Σ̂)={rank:4d} → invertible? {invertible}")"""))

cells.append(md(r"""> **⚠️ Caution: the optimizer simply does not run**
>
> $\text{rank}(\hat\Sigma) \le \min(T-1,\ N)$. With 500 stocks and 60 months of
> history, the sample covariance matrix has rank 59. It is **singular** —
> $\hat\Sigma^{-1}$ does not exist. This is not a precision problem you can fix
> with better data hygiene. The object you need mathematically does not exist.

Even when $T > N$ and the inverse technically exists, the estimate is badly
behaved: the largest sample eigenvalues are biased **up**, the smallest biased
**down**, and it is the smallest ones that dominate $\hat\Sigma^{-1}$.

**Everything in this notebook exists to solve that problem.** The idea: if
returns are driven by a small number of common factors, then $\Sigma$ has a lot
of structure, and we can estimate that structure instead of $N(N+1)/2$ free
numbers."""))

# ─── Section 2: three kinds ───────────────────────────────────────────
cells.append(md(r"""---

## Three Kinds of Factor Model <a id="three"></a>

You have already built two of these. Here is the third, and what separates them:

| Model type | You **specify** | You **estimate** | Example |
|---|---|---|---|
| **Time-series** | the factor *returns* | the betas, by time-series regression | Fama-French: you know HML and SMB, regress to get $\beta$ |
| **Characteristic / fundamental** | the *betas* (firm attributes) | the factor returns, by cross-sectional regression each period | Fama-MacBeth, BARRA: book-to-market *is* the loading |
| **Statistical** | **nothing** | both, from the covariance matrix | PCA — today |

> **💡 Key Insight**
>
> The first two require you to already know what risk *is*. Statistical factor
> models ask a different question: **what if we don't know?** Let the
> covariance matrix tell us what moves together, and see whether we recognize
> what comes out.

### The decomposition

We approximate the covariance matrix as a low-rank piece plus a diagonal:

$$\Sigma \approx \underbrace{B B'}_{\text{common, rank } K} + \underbrace{D}_{\text{diagonal, idiosyncratic}}$$

Instead of $N(N+1)/2$ parameters we now estimate $NK + N$. For $N=49$, $K=3$:
1,225 parameters becomes 196.

### Why PCA is the right way to do it

Take the eigendecomposition $\hat\Sigma = V\Lambda V'$ with eigenvalues sorted
$\lambda_1 \ge \lambda_2 \ge \dots \ge \lambda_N$, and keep the top $K$.

By the **Eckart–Young theorem**, the truncated eigendecomposition is *provably*
the closest rank-$K$ matrix to $\hat\Sigma$ in Frobenius norm. PCA is not a
heuristic — it is the optimal low-rank approximation. That is what "best
low-rank approximation" means.

> **📌 Remember: an eigenvector is a portfolio.**
>
> The $k$-th eigenvector $v_k$ is a vector of portfolio weights. The resulting
> return series $f_{k,t} = v_k'r_t$ is the $k$-th statistical factor, and
> $\lambda_k$ is that portfolio's variance. PCA hands you factor-mimicking
> portfolios for free."""))

# ─── Pitfall checklist ────────────────────────────────────────────────
cells.append(md("""---

## 🛡️ Pitfall Checklist for Statistical Factors <a id="pitfalls"></a>

| | Pitfall | What goes wrong | 🔍 How to detect |
|---|---|---|---|
| 1 | **PCA on the covariance matrix instead of the correlation matrix** | The highest-volatility asset hijacks PC1 — you've found a stock, not a factor | Check whether PC1 weights are concentrated on one or two names |
| 2 | **Forgetting to demean** | PC1 becomes the mean vector, not a source of co-movement | PC1 weights are all the same sign *and* explain an implausible share |
| 3 | **Reading "% variance explained" as evidence of a factor** | Pure noise also produces a decaying scree plot | Simulate noise at your $N$ and $T$ and compare — Hands-On 1 |
| 4 | **Keeping more factors than the data can support** | You are fitting noise and calling it risk | Count eigenvalues above the Marchenko–Pastur edge |
| 5 | **Assuming eigenvectors are stable** | Signs flip and components swap order between windows; your hedges churn | Re-estimate on a rolling window and track — Hands-On 3 |
| 6 | **Treating eigenvector portfolios as tradeable** | Extreme long-short weights, brutal turnover, no capacity | Look at max |weight| and the implied turnover |
| 7 | **Estimating components on the full sample, then "backtesting"** | Textbook look-ahead — your factors were built with tomorrow's data | Did the PCA window end before the backtest window started? |

> **🤖 AI-Era Insight**
>
> Ask any model to "extract factors from these returns using PCA" and you will
> get `PCA(n_components=10).fit(returns)` — ten components, no correlation
> matrix, no noise check, no discussion of whether ten is defensible. The code
> runs. The output is a table of numbers. **Nothing in it tells you that seven
> of those components are indistinguishable from random noise.** That is the
> gap this notebook is about."""))

# ─── Live Demo 1 ──────────────────────────────────────────────────────
cells.append(md("""---

## 🔄 Live Demo 1: Specify → Implement → Validate <a id="demo1"></a>

### Step 1 — The Specification

> **📝 Spec**
>
> Using the DataFrame `R` (49 industry portfolio monthly returns), take the
> **last 120 months**. Compute the **correlation** matrix (not covariance).
> Return its eigenvalues sorted descending and the corresponding eigenvectors.
> Report the share of total variance explained by each of the first five
> components, where "share" means eigenvalue divided by N.

Is that specification complete?
- ✅ Which data, which window — specified
- ✅ Correlation, not covariance — specified (pitfall 1)
- ✅ Sort order — specified
- ✅ What "share" means — specified
- ⚠️ Demeaning — implicit in using the correlation matrix, but worth stating"""))

cells.append(md("""### Step 2 — Implementation

> **🤖 AI prompt** *(paste into Gemini):*
>
> *"Given a DataFrame R of monthly returns, take the last 120 rows. Compute the
> correlation matrix with numpy, get eigenvalues and eigenvectors with
> np.linalg.eigh, sort descending, and print the variance share (eigenvalue / N)
> of the first five components."*"""))

cells.append(code("""# What competent AI-generated code looks like:
WINDOW = 120
Y = R.iloc[-WINDOW:]
N, T = Y.shape[1], Y.shape[0]

C = np.corrcoef(Y.values.T)              # correlation, not covariance
evals, evecs = np.linalg.eigh(C)         # eigh: symmetric matrices, ascending
order = np.argsort(evals)[::-1]          # sort descending
evals, evecs = evals[order], evecs[:, order]

print(f"N = {N} industries,  T = {T} months")
print(f"Sum of eigenvalues = {evals.sum():.1f}  (must equal N = {N})\\n")
for k in range(5):
    print(f"  PC{k+1}:  eigenvalue = {evals[k]:6.3f}   variance share = {evals[k]/N:6.2%}")"""))

cells.append(md("""### Step 3 — Validate

Two checks before we believe anything.

**Check 1 — do the eigenvalues sum to N?** For a correlation matrix the trace is
N (ones on the diagonal), and the trace equals the sum of eigenvalues. If that
doesn't hold, something is wrong upstream.

**Check 2 — what does PC1 actually look like?** If the decomposition is finding
real co-movement, PC1 should be recognizable. Let's look at the weights."""))

cells.append(code("""fig, axes = plt.subplots(1, 2, figsize=(13, 4.2))

# Scree
axes[0].bar(range(1, 16), evals[:15], color='steelblue')
axes[0].set_xlabel('Component'); axes[0].set_ylabel('Eigenvalue')
axes[0].set_title('Scree plot — 49 industries, 120 months', fontweight='bold')

# PC1 weights across industries
axes[1].bar(range(N), evecs[:, 0], color='darkorange')
axes[1].axhline(0, color='black', linewidth=0.8)
axes[1].set_xlabel('Industry'); axes[1].set_ylabel('PC1 weight')
axes[1].set_title('PC1 eigenvector — the weights on each industry', fontweight='bold')

plt.tight_layout(); plt.show()

pc1 = evecs[:, 0]
print(f"PC1 weights: all same sign? {np.all(pc1 > 0) or np.all(pc1 < 0)}")
print(f"             min {pc1.min():.3f}   max {pc1.max():.3f}   "
      f"ratio max/min {abs(pc1).max()/abs(pc1).min():.1f}x")
print(f"\\nCorrelation of the PC1 portfolio with an equal-weight portfolio: "
      f"{np.corrcoef(Y.values @ pc1, Y.values.mean(axis=1))[0,1]:.4f}")"""))

cells.append(md("""> **💡 Key Insight: you just rediscovered the market**
>
> PC1 has the same sign on every industry, roughly comparable magnitudes, and
> correlates ~0.99 with an equal-weighted portfolio of all 49 industries. It
> explains over half the variance.
>
> **Nobody told the algorithm that a market portfolio exists.** We handed it a
> correlation matrix and it returned the market. That is the appeal of
> statistical factors: they find structure without being told what to look for.

PC2 and PC3 typically read as sector or style tilts — long some industries,
short others. They are harder to name, and that is the beginning of the problem
we'll get to in Section [Why Practitioners Still Use Fundamental Factors](#why)."""))

# ─── HANDS-ON 1 ───────────────────────────────────────────────────────
cells.append(md("""---

## 🛠️ Hands-On 1: Run It On Nothing <a id="ho1"></a>

That demo felt like a success. PC1 is the market, PC2 and PC3 look like
something, the scree plot decays smoothly. It is tempting to conclude that we
have found five or six real factors.

**Before you conclude anything: run the identical analysis on data you know has
no factors in it.**

### Your task

Generate a matrix of **pure independent random noise** with the *same shape* as
`Y` — 49 columns, 120 rows, all independent standard normals. There is no
common factor anywhere in it, by construction. Then run exactly the same PCA
and compare the two scree plots.

> **🤔 Predict before you run.** Write down your guess now: what share of
> variance will PC1 explain in the noise matrix? Most people say something
> close to 1/49 ≈ 2%. Commit to a number before executing the next cell."""))

cells.append(code("""# === YOUR TURN ===
# Build a noise matrix with the same shape as Y and run the same PCA.
# Fill in the two lines marked with ____ .

noise = ____          # hint: np.random.randn(T, N) — same T and N as the real data
C_noise = ____        # hint: same correlation-matrix step you used above

evals_noise = np.sort(np.linalg.eigvalsh(C_noise))[::-1]

print(f"Noise matrix shape: {noise.shape}  (should be ({T}, {N}))")
print(f"Eigenvalues sum to {evals_noise.sum():.1f}  (should be {N})\\n")
for k in range(5):
    print(f"  PC{k+1}:  eigenvalue = {evals_noise[k]:6.3f}   "
          f"variance share = {evals_noise[k]/N:6.2%}")"""))

cells.append(md("""### Now compare them side by side"""))

cells.append(code("""fig, ax = plt.subplots(figsize=(11, 4.2))
w = 0.4
ax.bar(np.arange(1, 16) - w/2, evals[:15],       w, label='Real industries', color='steelblue')
ax.bar(np.arange(1, 16) + w/2, evals_noise[:15], w, label='Pure noise',      color='indianred')
ax.set_xlabel('Component'); ax.set_ylabel('Eigenvalue')
ax.set_title('Real data vs pure noise — same N, same T', fontweight='bold')
ax.legend()
plt.tight_layout(); plt.show()

print(f"Largest noise eigenvalue      : {evals_noise[0]:.3f}  "
      f"({evals_noise[0]/N:.1%} of variance)")
print(f"Smallest noise eigenvalue     : {evals_noise[-1]:.3f}")
print(f"Ratio largest/smallest (noise): {evals_noise[0]/evals_noise[-1]:.1f}x")
print(f"\\nReal PC4 eigenvalue           : {evals[3]:.3f}")
print(f"Noise PC1 eigenvalue          : {evals_noise[0]:.3f}")"""))

cells.append(md("""### What did you find?

> **🤔 Answer these before reading on**
>
> 1. Did the noise eigenvalues all come out near 1.0? Why not?
> 2. Is the real data's PC4 bigger or smaller than the *largest* noise eigenvalue?
> 3. If someone showed you only the noise scree plot and called it "returns data,"
>    how many factors would you have said there were?

Here is the uncomfortable result. Pure noise — no factors, none, by
construction — produces a spread of eigenvalues running roughly from 0.15 to
2.7, a ratio of nearly 20×. It produces a scree plot that decays smoothly and
looks exactly like the kind of picture people point at when they say "you can
see there are about four factors here."

> **⚠️ Caution: "PC1 explains 30% of variance" is not evidence of a factor**
>
> It is only evidence if 30% is more than noise alone would have produced at
> your $N$ and $T$. Nobody who reports a scree plot without this comparison has
> told you anything.

And notice the specific damage: in the real data, **PC4 and beyond sit inside
the range that pure noise generates.** Whatever those components are, we cannot
distinguish them from randomness. The next section explains exactly where that
boundary sits and why."""))

# ─── Spiked covariance model ──────────────────────────────────────────
cells.append(md(r"""---

## The Spiked Covariance Model <a id="spiked"></a>

Hands-On 1 showed *that* noise makes structure. The **spiked covariance model**
(Johnstone, 2001) tells us *how much*, precisely.

The model: the true population covariance has a few large eigenvalues — the
"spikes" — sitting on a flat sea of equal small ones.

$$\lambda_1 > \lambda_2 > \dots > \lambda_K \;>\; \underbrace{\sigma^2 = \sigma^2 = \dots = \sigma^2}_{N-K \text{ of them}}$$

The spikes are real factors. The flat part is idiosyncratic noise. The question
is what happens when you estimate this from $T$ observations.

### Marchenko–Pastur: what noise alone produces

If there are **no** spikes at all — pure noise — the sample eigenvalues do not
converge to $\sigma^2$. They spread out over an interval:

$$\lambda \in \left[\sigma^2(1-\sqrt{c})^2,\;\; \sigma^2(1+\sqrt{c})^2\right],
\qquad c = \frac{N}{T}$$

The width is governed entirely by $c = N/T$ — how many assets relative to how
much history. More assets or less history means a wider spread of pure-noise
eigenvalues, and more apparent structure that isn't there.

For a correlation matrix, $\sigma^2 = 1$, so the **upper edge is
$(1+\sqrt{c})^2$**. Let's check that against what you just simulated."""))

cells.append(code("""c = N / T
mp_lower = (1 - np.sqrt(c))**2
mp_upper = (1 + np.sqrt(c))**2

def mp_density(x, c):
    \"\"\"Marchenko-Pastur density for a correlation matrix (sigma^2 = 1).\"\"\"
    lo, hi = (1-np.sqrt(c))**2, (1+np.sqrt(c))**2
    out = np.zeros_like(x)
    m = (x > lo) & (x < hi)
    out[m] = np.sqrt((hi - x[m]) * (x[m] - lo)) / (2 * np.pi * c * x[m])
    return out

print(f"c = N/T = {N}/{T} = {c:.4f}")
print(f"MP support: [{mp_lower:.3f}, {mp_upper:.3f}]")
print(f"Your simulated noise eigenvalues ran: "
      f"[{evals_noise[-1]:.3f}, {evals_noise[0]:.3f}]")

fig, ax = plt.subplots(figsize=(11, 4.2))
ax.hist(evals_noise, bins=25, density=True, alpha=0.55,
        color='indianred', label='Simulated noise eigenvalues')
xs = np.linspace(0.01, mp_upper * 1.2, 500)
ax.plot(xs, mp_density(xs, c), 'k-', linewidth=2.2, label='Marchenko–Pastur density')
ax.axvline(mp_upper, color='darkgreen', linestyle='--', linewidth=2,
           label=f'Upper edge = {mp_upper:.2f}')
ax.set_xlabel('Eigenvalue'); ax.set_ylabel('Density')
ax.set_title('Theory predicts the noise spectrum exactly', fontweight='bold')
ax.legend()
plt.tight_layout(); plt.show()"""))

cells.append(md(r"""> **💡 Key Insight**
>
> The black curve is not fitted to anything — it is the theoretical prediction
> from $c=N/T$ alone. It matches your simulation because the spread of
> eigenvalues in a noise matrix is a *mathematical fact*, not a property of
> your data.

### Now put the real eigenvalues on the same picture

Anything above the green line is a candidate factor. Anything below it is
indistinguishable from noise."""))

cells.append(code("""fig, ax = plt.subplots(figsize=(11, 4.2))
xs = np.linspace(0.01, 6, 500)
ax.plot(xs, mp_density(xs, c), 'k-', linewidth=2, label='MP noise density')
ax.axvline(mp_upper, color='darkgreen', linestyle='--', linewidth=2,
           label=f'MP upper edge = {mp_upper:.2f}')
inside  = evals[evals <= mp_upper]
outside = evals[evals >  mp_upper]
ax.scatter(inside,  np.full_like(inside, 0.05),  marker='|', s=380,
           color='grey',      label=f'Inside the bulk — noise ({len(inside)})')
ax.scatter(outside, np.full_like(outside, 0.05), marker='|', s=380,
           color='crimson',   label=f'Above the edge — signal ({len(outside)})')
ax.set_xlim(0, 6); ax.set_xlabel('Eigenvalue'); ax.set_ylabel('Density')
ax.set_title('49 industries: which eigenvalues survive the noise test?',
             fontweight='bold')
ax.legend(loc='upper right')
plt.tight_layout(); plt.show()

print(f"Eigenvalues above the MP edge: {len(outside)}  →  {np.round(outside,2)}")
print(f"PC1 = {evals[0]:.1f} is far off this chart (it's the market).")
print(f"\\nOf {N} industries, only {len(outside)} directions are distinguishable from noise.")"""))

cells.append(md(r"""### The phase transition: factors you cannot find

There is a sharper result. **Baik–Ben Arous–Péché** showed that a true spike
only separates from the noise bulk if it exceeds a threshold:

$$\lambda_{\text{true}} > \sigma^2\left(1 + \sqrt{c}\right)$$

Below that, the sample eigenvalue is swallowed by the bulk and the factor is
**undetectable** — not weakly estimated, but invisible. No amount of cleverness
recovers it at that $N/T$.

Two more consequences, both worth knowing:

| Effect | What it means for you |
|---|---|
| Detected eigenvalues are biased **upward** | Your "factor" explains less variance than the sample says |
| Eigenvectors are **inconsistent** | The estimated factor sits at an angle to the true one that does *not* vanish as $T$ grows |

You are about to find the threshold yourself."""))

# ─── HANDS-ON 2 ───────────────────────────────────────────────────────
cells.append(md(r"""---

## 🛠️ Hands-On 2: Find the Detection Threshold <a id="ho2"></a>

### Your task

Build a synthetic panel that has **exactly one** factor in it, whose strength
you control:

$$r_{i,t} = \beta f_t + \varepsilon_{i,t}, \qquad
f_t \sim N(0,1), \quad \varepsilon_{i,t} \sim N(0,1), \quad
\beta = \sqrt{\tfrac{\rho}{1-\rho}}$$

That loading makes every pair of assets have correlation $\rho$. The population
correlation matrix then has one large eigenvalue and a flat bulk:

$$\lambda_{\text{pop}} = 1 + (N-1)\rho$$

**$\lambda_{\text{pop}}$ is the spike.** That — not $\rho$, and not $\beta$ — is
the quantity BBP makes a statement about: the spike is detectable only if

$$\lambda_{\text{pop}} > 1 + \sqrt{c}$$

Sweep $\rho$ upward, record the **largest sample eigenvalue**, and plot it
against $\lambda_{\text{pop}}$. Find where it breaks out of the bulk.

> **🤔 Predict first.** Do you expect the largest sample eigenvalue to rise
> smoothly out of the bulk as the spike grows, or to stay pinned inside the bulk
> and then suddenly take off? Commit before running."""))

cells.append(code("""# === YOUR TURN ===
# Complete the simulation below.

def top_eigenvalue(rho, N, T, seed=None):
    \"\"\"One-factor panel with pairwise correlation rho. Returns the largest
    eigenvalue of the sample correlation matrix.\"\"\"
    rng  = np.random.default_rng(seed)
    f    = rng.standard_normal(T)                        # the common factor
    beta = np.sqrt(rho / (1 - rho)) * np.ones(N)         # equal loadings
    eps  = rng.standard_normal((T, N))                   # idiosyncratic noise

    X = ____                                   # hint: np.outer(f, beta) + eps
    return np.linalg.eigvalsh(np.corrcoef(X.T))[-1]

rho_grid = np.linspace(0.0005, 0.06, 25)
lam_pop  = 1 + (N - 1) * rho_grid              # the population spike
top = np.array([np.mean([top_eigenvalue(r, N, T, seed=j) for j in range(20)])
                for r in rho_grid])

print(f"Spike ranges from {lam_pop[0]:.2f} to {lam_pop[-1]:.2f}")
print(f"Largest sample eigenvalue ranges from {top[0]:.2f} to {top[-1]:.2f}")"""))

cells.append(code("""bbp_threshold = 1 + np.sqrt(c)          # BBP: population spike must exceed this

# What theory predicts the SAMPLE eigenvalue will be:
theory = np.where(lam_pop <= bbp_threshold,
                  mp_upper,                                     # buried in the bulk
                  lam_pop * (1 + c / np.maximum(lam_pop - 1, 1e-9)))

fig, ax = plt.subplots(figsize=(11, 4.5))
ax.plot(lam_pop, top, 'o-', color='steelblue', markersize=4,
        label='Largest sample eigenvalue (simulated)')
ax.plot(lam_pop, theory, '-', color='black', linewidth=1.8, alpha=0.75,
        label='Spiked-model prediction')
ax.axhline(mp_upper, color='darkgreen', linestyle='--', linewidth=2,
           label=f'MP upper edge = {mp_upper:.2f}')
ax.axvline(bbp_threshold, color='crimson', linestyle=':', linewidth=2.2,
           label=f'BBP threshold  1+√c = {bbp_threshold:.2f}')
ax.set_xlabel('Population spike  $\\\\lambda_{pop}$'); ax.set_ylabel('Largest sample eigenvalue')
ax.set_title('A factor is invisible until the spike crosses the threshold',
             fontweight='bold')
ax.legend()
plt.tight_layout(); plt.show()

detected = lam_pop[top > mp_upper]
print(f"You first detect the factor at a spike of ≈ {detected[0]:.2f}")
print(f"BBP theory says the threshold is 1+√c = {bbp_threshold:.2f}")"""))

cells.append(md(r"""### What did you find?

The curve is **flat and then it isn't.** Below the threshold the largest sample
eigenvalue just sits at the noise edge and barely moves as the spike grows — the
factor is genuinely present in the data-generating process and completely
invisible. Past $1+\sqrt{c}$ it lifts off and tracks the theoretical curve
$\lambda(1 + \frac{c}{\lambda-1})$.

> **🤔 Two details worth noticing**
>
> 1. Your empirical detection point sits a little *above* $1+\sqrt{c}$. That's
>    expected: the threshold is an asymptotic result, and in a finite sample the
>    spike has to clear the bulk by enough to be visible above sampling noise.
> 2. Above the threshold, the sample eigenvalue sits **above** the population
>    spike — that's the upward bias mentioned earlier. Your factor always looks
>    more important than it is.

That is the phase transition. It is not a statistical power issue that more data
would fix at fixed $N/T$ — it is a hard boundary set by the ratio.

> **📌 Remember**
>
> There exist real risk factors in your market that you cannot detect with the
> data you have. The correct response is not to lower your threshold until you
> find them. It is to say: *at this N and T, I can identify k factors, and there
> may be more that I cannot see.*

> **🤔 Think about the implication**
>
> $c = N/T$. To detect weaker factors you need $c$ smaller — fewer assets, or
> more history. But more history means older data, and factor structure changes
> over time. **This is a genuine, unavoidable tradeoff**, and it is why risk
> model vendors argue about window length."""))

# ─── Noise filtering ──────────────────────────────────────────────────
cells.append(md(r"""---

## Noise Filtering <a id="filter"></a>

We now know which eigenvalues are signal and which are noise. The filtering
recipe follows immediately:

1. Compute the eigenvalues of the sample **correlation** matrix
2. Anything **above** the MP edge → keep as is (signal)
3. Anything **inside** the bulk → replace with their common average (noise)
4. Rescale so the trace still equals $N$, and reconstruct

This is **random matrix theory filtering** — Laloux, Cizeau, Bouchaud & Potters
(1999), *Noise Dressing of Financial Correlation Matrices*. Applying it to the
S&P 500, they found roughly **94% of eigenvalues indistinguishable from noise**.

> **💡 Key Insight: this is shrinkage in different clothing**
>
> You already met Ledoit–Wolf shrinkage in Risk Management: pull $\hat\Sigma$
> toward a simple target because the sample estimate is too extreme. RMT
> filtering does the same job by a different route — it identifies *which*
> eigenvalues are pure noise and flattens exactly those.
>
> Both are answers to the same fact: **sample eigenvalues are too spread out.**
> The top ones are too big, the bottom ones too small, and it is the bottom ones
> that blow up $\hat\Sigma^{-1}$."""))

cells.append(code("""def rmt_filter(corr, c):
    \"\"\"Replace sub-MP-edge eigenvalues with their average; preserve the trace.\"\"\"
    n = corr.shape[0]
    ev, V = np.linalg.eigh(corr)
    ev, V = ev[::-1], V[:, ::-1]
    edge = (1 + np.sqrt(c))**2

    keep = ev > edge
    ev_f = ev.copy()
    if (~keep).any():
        ev_f[~keep] = ev[~keep].mean()          # flatten the noise bulk
    ev_f *= n / ev_f.sum()                      # restore trace = n

    Cf = V @ np.diag(ev_f) @ V.T
    d = np.sqrt(np.diag(Cf))                    # renormalize to a correlation matrix
    return Cf / np.outer(d, d), keep.sum()

C_filtered, n_kept = rmt_filter(C, c)

print(f"Factors kept          : {n_kept}  of {N}")
print(f"Eigenvalues flattened : {N - n_kept}\\n")
print(f"Condition number, raw      : {np.linalg.cond(C):>12,.0f}")
print(f"Condition number, filtered : {np.linalg.cond(C_filtered):>12,.0f}")"""))

# ─── Live Demo 2 ──────────────────────────────────────────────────────
cells.append(md("""---

## 🔄 Live Demo 2: Does Filtering Fix the Optimizer? <a id="demo2"></a>

Condition numbers are abstract. The question you actually care about: **do the
portfolio weights get better?**

> **📝 Spec**
>
> Estimate on the **first 120 months** only — a realistic risk-model window, and
> the same $c$ we have been working with. Compute minimum-variance weights
> $w \\propto \\Sigma^{-1}\\mathbf{1}$ two ways: once from the raw correlation
> matrix, once from the RMT-filtered one. Apply both weight vectors to
> **everything after** (which neither saw) and compare realized volatility,
> gross leverage, and the largest single position.

> **⚠️ Why the window length matters here.** Run this with 30 years of training
> data and the two methods look almost identical — with $c$ small, the raw
> estimate is already decent. The filtering only earns its keep when $c$ is
> large, which is exactly the regime real risk models operate in."""))

cells.append(code("""TRAIN = 120
train, test = R.iloc[:TRAIN], R.iloc[TRAIN:]
Ntr, Ttr = train.shape[1], train.shape[0]
c_tr = Ntr / Ttr

sd_tr = train.std().values
C_tr  = np.corrcoef(train.values.T)
C_tr_f, kept_tr = rmt_filter(C_tr, c_tr)

def min_var_weights(corr, sd):
    cov = corr * np.outer(sd, sd)
    inv = np.linalg.pinv(cov)
    w = inv @ np.ones(len(sd))
    return w / w.sum()

w_raw = min_var_weights(C_tr,   sd_tr)
w_flt = min_var_weights(C_tr_f, sd_tr)

vol_raw = (test.values @ w_raw).std() * np.sqrt(12)
vol_flt = (test.values @ w_flt).std() * np.sqrt(12)

print(f"Training: {train.index.min().date()} to {train.index.max().date()}  "
      f"(c = {c_tr:.3f}, {kept_tr} factors kept)")
print(f"Test    : {test.index.min().date()} to {test.index.max().date()}\\n")
print(f"{'':22s} {'raw Σ':>12s} {'filtered Σ':>12s}")
print(f"{'max |weight|':22s} {np.abs(w_raw).max():>12.2%} {np.abs(w_flt).max():>12.2%}")
print(f"{'sum |weight| (gross)':22s} {np.abs(w_raw).sum():>12.2f} {np.abs(w_flt).sum():>12.2f}")
print(f"{'# short positions':22s} {int((w_raw<0).sum()):>12d} {int((w_flt<0).sum()):>12d}")
print(f"{'OOS annualized vol':22s} {vol_raw:>12.2%} {vol_flt:>12.2%}")"""))

cells.append(md("""> **🤔 Read the table before moving on**
>
> The raw-covariance optimizer takes a single position of roughly 66% and runs
> over 8× gross leverage, to deliver *higher* out-of-sample volatility than the
> filtered version. It looks superb in-sample precisely because it is exploiting
> the noise eigenvalues — the tiny ones that $\\Sigma^{-1}$ blows up into huge
> offsetting positions. Out of sample those directions were never real, so all
> that leverage buys nothing.
>
> The filtered version reaches lower realized risk with roughly a third of the
> gross exposure. Hold on to the leverage number — at the turnover implied by
> 8× gross, transaction costs (next lecture) would eat the difference several
> times over even if the volatilities *had* matched.
>
> This is the same estimation-error story as Capital Allocation II, seen through
> the covariance matrix instead of the mean vector."""))

# ─── How many factors ─────────────────────────────────────────────────
cells.append(md(r"""---

## How Many Factors? <a id="howmany"></a>

Everything above depends on choosing $K$. Here is the menu, worst to best:

| Method | How it works | Verdict |
|---|---|---|
| **Scree elbow** | Look for the bend | Everyone does it; unprincipled and irreproducible |
| **Cumulative variance** | Keep enough for 80% | Arbitrary threshold, no statistical content |
| **Kaiser rule** | Keep eigenvalues > 1 | Known to badly over-select. Avoid. |
| **Marchenko–Pastur edge** | Keep eigenvalues above $(1+\sqrt{c})^2$ | Principled; falls out of the spiked model |
| **Parallel analysis** | Shuffle your own data to destroy cross-correlation, re-run PCA, keep components beating the simulated 95th percentile | Cheap, intuitive, works |
| **Bai–Ng (2002)** | Information criteria penalizing $K$ by a function of $N,T$ | The empirical asset pricing standard |
| **Onatski (2010)** | Test based on the edge distribution | More powerful near the threshold |

**Parallel analysis** is the one to internalize, because it is just Hands-On 1
turned into a tool: rather than reasoning about what noise *would* do, you
generate the null from your own data and look."""))

cells.append(code("""def parallel_analysis(Ymat, n_sim=200, pct=95, seed=0):
    \"\"\"Shuffle each column independently to kill cross-correlation while
    preserving each series' own distribution. Keep components above the
    simulated percentile.\"\"\"
    rng = np.random.default_rng(seed)
    Tn, Nn = Ymat.shape
    sims = np.empty((n_sim, Nn))
    for i in range(n_sim):
        Z = np.column_stack([rng.permutation(Ymat[:, j]) for j in range(Nn)])
        sims[i] = np.sort(np.linalg.eigvalsh(np.corrcoef(Z.T)))[::-1]
    cutoff = np.percentile(sims, pct, axis=0)
    real = np.sort(np.linalg.eigvalsh(np.corrcoef(Ymat.T)))[::-1]
    return int((real > cutoff).sum()), real, cutoff

k_par, real_ev, cutoff = parallel_analysis(Y.values)

print(f"Parallel analysis  : {k_par} factors")
print(f"Marchenko–Pastur   : {int((evals > mp_upper).sum())} factors")
print(f"Kaiser (>1)        : {int((evals > 1).sum())} factors   ← note the over-selection\\n")
for k in range(6):
    verdict = "KEEP" if real_ev[k] > cutoff[k] else "noise"
    print(f"  PC{k+1}: eigenvalue {real_ev[k]:6.2f}   "
          f"95th pct of shuffled {cutoff[k]:5.2f}   → {verdict}")"""))

cells.append(md("""> **💡 Key Insight: two independent methods agree**
>
> Parallel analysis makes no appeal to Marchenko–Pastur — it simulates the null
> from your own data by shuffling. MP is pure theory from $c = N/T$. They land
> on the same answer, and the parallel-analysis cutoff for PC1 comes out
> essentially *on* the MP edge.
>
> When a theoretical bound and a brute-force simulation agree, you can trust the
> number. When they disagree, your data violates an assumption — usually fat
> tails or time-varying volatility — and that is worth knowing too.

Meanwhile the Kaiser rule keeps many more components. It is still the default in
several statistics packages. This is a good example of an AI-generated analysis
producing a defensible-*looking* number that is simply the wrong tool."""))

# ─── HANDS-ON 3 ───────────────────────────────────────────────────────
cells.append(md("""---

## 🛠️ Hands-On 3: Watch the Factors Move <a id="ho3"></a>

Suppose you have settled on $K$ factors and built a risk model. You re-estimate
it next month, as any real risk system does.

**Do you get the same factors back?**

### Your task

Estimate PCA on rolling 120-month windows, stepping forward 12 months at a time.
For each window, record PC2's weights. Then check two things: whether the
*sign* stayed the same, and whether PC2 in one window still looks like PC2 in
the next.

> **🤔 Predict.** PC1 is the market and is huge — you'd expect it to be stable.
> What about PC2, whose eigenvalue in our sample is around 3, and PC3, around 2?"""))

cells.append(code("""# === YOUR TURN ===
# Fill in the line that extracts the eigenvector for component `comp`.

def pcs_for_window(Ymat, comp):
    ev, V = np.linalg.eigh(np.corrcoef(Ymat.T))
    order = np.argsort(ev)[::-1]
    V = V[:, order]
    return ____              # hint: V[:, comp] — the comp-th eigenvector

STEP, W = 12, 120
starts = range(0, len(R) - W, STEP)
dates, pc2s, pc1s = [], [], []
for s0 in starts:
    win = R.iloc[s0:s0+W].values
    pc1s.append(pcs_for_window(win, 0))
    pc2s.append(pcs_for_window(win, 1))
    dates.append(R.index[s0+W-1].date())

pc1s, pc2s = np.array(pc1s), np.array(pc2s)

# Similarity between consecutive windows = |cos angle| between eigenvectors
sim1 = [abs(np.dot(pc1s[i], pc1s[i+1])) for i in range(len(pc1s)-1)]
sim2 = [abs(np.dot(pc2s[i], pc2s[i+1])) for i in range(len(pc2s)-1)]

print(f"Windows: {len(pc1s)}   (each 120 months, stepping 12)\\n")
print(f"PC1 similarity between consecutive windows: "
      f"mean {np.mean(sim1):.3f}, min {np.min(sim1):.3f}")
print(f"PC2 similarity between consecutive windows: "
      f"mean {np.mean(sim2):.3f}, min {np.min(sim2):.3f}")

raw_signs = [np.dot(pc2s[i], pc2s[i+1]) for i in range(len(pc2s)-1)]
print(f"\\nSign flips in PC2 across windows: "
      f"{sum(1 for x in raw_signs if x < 0)} of {len(raw_signs)}")"""))

cells.append(code("""fig, ax = plt.subplots(figsize=(11, 4.2))
ax.plot(dates[1:], sim1, 'o-', color='steelblue', label='PC1 (the market)')
ax.plot(dates[1:], sim2, 's-', color='indianred',  label='PC2')
ax.axhline(1.0, color='black', linewidth=0.8, linestyle=':')
ax.set_ylabel('|cos angle| with previous window'); ax.set_ylim(0, 1.05)
ax.set_title('How much does each factor change when you re-estimate?',
             fontweight='bold')
ax.legend(); plt.xticks(rotation=45)
plt.tight_layout(); plt.show()"""))

cells.append(md("""### What did you find?

PC1 is rock stable — it is the market, its eigenvalue is enormous, and it is
nowhere near any other eigenvalue. PC2 is a different story: it moves
substantially between windows, and its **sign flips arbitrarily**.

The sign flip is pure mathematics: if $v$ is an eigenvector, so is $-v$, with
the same eigenvalue. `np.linalg.eigh` picks one and there is no rule about
which. Nothing economic happened.

But the *rotation* is a real problem, and its cause is worth naming:

> **⚠️ Caution: near-degenerate eigenvalues**
>
> When $\\lambda_k \\approx \\lambda_{k+1}$, the two-dimensional **subspace** they
> span is estimated well, but the individual eigenvectors within it are not
> identified. Small sampling noise rotates them freely inside that plane. In our
> sample PC4 and PC5 have eigenvalues around 1.78 and 1.76 — for practical
> purposes indistinguishable, so those two "factors" are meaningless
> individually.

**Why this costs money.** A risk model whose factors rotate every month
generates hedge ratios that change for no economic reason. You trade to
rebalance against a factor that only moved because of estimation noise, and you
pay real transaction costs (next lecture) for it.

Standard fixes, in order of sophistication:

| Fix | What it does |
|---|---|
| Sign alignment | Force $\\text{sign}(v_k'v_k^{\\text{prev}}) > 0$ each period. Removes the artifact, not the rotation. |
| Overlapping windows | Step forward slowly so consecutive estimates share most of their data |
| Procrustes rotation | Rotate the new factor basis to be as close as possible to the previous one |
| Just use fundamental factors | Book-to-market does not flip sign — see the next section |"""))

# ─── Why practitioners ────────────────────────────────────────────────
cells.append(md("""---

## Why Practitioners Still Use Fundamental Factors <a id="why"></a>

Statistical factors fit variance better than any specified model — by
construction, via Eckart–Young. Yet BARRA, Axioma, and every major risk vendor
sell **fundamental** factor models. Why?

| | Statistical (PCA) | Fundamental (BARRA-style) |
|---|---|---|
| In-sample variance fit | Best possible for its rank | Worse |
| Interpretation | PC1 is the market. What is PC7? | "Momentum", "Size", "Semiconductors" |
| Stability | Rotates, flips, reorders | Book-to-market is book-to-market |
| Attribution | "You lost money on PC4" | "You lost money on your value tilt" |
| Needs data on | Returns only | Returns *and* firm fundamentals |

The decisive issue is the third row and the fourth. A risk model is not a
variance-minimization contest — it is a **communication device**. Its job is to
tell a portfolio manager which bets they are taking so they can decide whether
they meant to take them. "Your P&L was driven by PC4" is not actionable. "You
are long low-quality semiconductors" is.

> **📌 Remember**
>
> Statistical factors answer *how much* common variation there is. Fundamental
> factors answer *what it is*. Most production risk models are fundamental, with
> a few statistical factors bolted on to catch structure the specified factors
> miss.

And the honest summary of today: even where PCA is not the model you ship, the
**noise analysis is indispensable**. Marchenko–Pastur tells you how many
directions your data can support, whatever you decide to call them."""))

# ─── Challenge ────────────────────────────────────────────────────────
cells.append(md("""---

## 🎯 Challenge: How Many Factors Are Real? <a id="challenge"></a>

You are building a risk model for a 49-industry universe. Your boss says
"just use ten principal components, that's what we've always done."

Your job is to determine how many factors the data can actually support, and to
write the memo that either supports or refutes that instruction.

**Use the last 120 months of `R`** so everyone's numbers are comparable."""))

cells.append(md("""### Q1 — The noise boundary

Compute $c = N/T$ and the Marchenko–Pastur upper edge for this window, then
count how many eigenvalues of the correlation matrix exceed it.

> **📌 Required variable names:**
> ```python
> mp_edge_upper = ____   # the MP upper edge, e.g. 2.69
> n_factors_mp  = ____   # how many eigenvalues exceed it (an integer count)
> ```"""))

cells.append(code("""# Your work here


# Required outputs — fill these in:
mp_edge_upper = ____
n_factors_mp  = ____

print(f"MP upper edge         : {mp_edge_upper:.3f}")
print(f"Eigenvalues above it  : {n_factors_mp}")"""))

cells.append(md("""### Q2 — How much does PC1 explain, and is that impressive?

Report PC1's variance share on the real data, then run the same PCA on a pure
noise matrix of identical shape and report *its* PC1 share.

> **🤔 The point of this question:** a number is only meaningful next to its null.
>
> **📌 Required variable names:**
> ```python
> pc1_share       = ____   # PC1 eigenvalue / N on the real data
> noise_pc1_share = ____   # PC1 eigenvalue / N on pure noise, same N and T
> ```"""))

cells.append(code("""# Your work here


# Required outputs — fill these in:
pc1_share       = ____
noise_pc1_share = ____

print(f"Real PC1 share  : {pc1_share:.1%}")
print(f"Noise PC1 share : {noise_pc1_share:.1%}")
print(f"Ratio           : {pc1_share/noise_pc1_share:.1f}x")"""))

cells.append(md("""### Q3 — A second opinion

Run parallel analysis on the same window and report how many factors it keeps.
You may reuse the `parallel_analysis` function from above.

> **📌 Required variable name:**
> ```python
> n_factors_parallel = ____   # integer count from parallel analysis
> ```"""))

cells.append(code("""# Your work here


# Required output — fill this in:
n_factors_parallel = ____

print(f"Parallel analysis : {n_factors_parallel} factors")
print(f"MP edge           : {n_factors_mp} factors")
print(f"Agreement?        : {n_factors_parallel == n_factors_mp}")"""))

cells.append(md("""### Q4 — The memo

> **📝 Your task**
>
> Write a memo to your boss, **maximum 6 sentences**, answering: how many
> factors should the risk model use, and why is ten wrong?
>
> A strong memo will:
> - Give a specific number and the evidence for it (cite MP and parallel analysis agreeing)
> - Explain why "PC1 explains 55% of variance" is not by itself an argument
> - Say what goes wrong operationally if you keep ten — not just "it's noise", but what it *costs*
> - Acknowledge what you cannot rule out (factors below the detection threshold)"""))

cells.append(code('''MEMO = """
Write your memo here. Don't delete the surrounding triple quotes.
"""
print(MEMO)
print(f"\\nWord count: {len(MEMO.split())}")'''))

# ─── Submission ───────────────────────────────────────────────────────
cells.append(md("""---

## 📤 Submission <a id="submit"></a>

Run the cell below. It bundles your answers into one line — copy it and paste
into the submission form."""))

cells.append(code('''# === 📤 SUBMISSION CELL — Run this last ===
import json, base64, hashlib, datetime as dt

required = [
    "mp_edge_upper", "n_factors_mp",
    "pc1_share", "noise_pc1_share",
    "n_factors_parallel",
    "MEMO",
]
missing = [v for v in required if v not in dir()]
if missing:
    raise NameError(
        f"\\n❌ Missing variables before submission: {missing}\\n"
        "Every question above defines the variable names it expects."
    )

payload = {
    "assignment": "StatisticalFactors_AI",
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
print(f"\\nLength: {len(token)} chars")
print("Submission form: https://forms.gle/YOUR_FORM_LINK_HERE")'''))

# ─── Takeaways ────────────────────────────────────────────────────────
cells.append(md(r"""---

## 🧠 Key Takeaways <a id="takeaways"></a>

1. **The sample covariance matrix is unusable for a large cross-section.** With
   $T < N$ it is singular and $\hat\Sigma^{-1}$ does not exist. Factor structure
   is how you get around this, not an optional refinement.

2. **PCA is the optimal low-rank approximation**, by Eckart–Young — not a
   heuristic. An eigenvector is a portfolio; its eigenvalue is that portfolio's
   variance.

3. **PC1 of a broad equity cross-section is the market**, and it typically
   explains half the variance. You get that for free without specifying anything.

4. **Noise produces apparent structure.** Pure random data yields a smoothly
   decaying scree plot spanning a 20× range of eigenvalues. "% variance
   explained" means nothing without its null.

5. **Marchenko–Pastur says exactly how much structure noise produces**: the bulk
   spans $[(1-\sqrt{c})^2, (1+\sqrt{c})^2]$ with $c = N/T$. Only eigenvalues
   above the upper edge are candidate factors.

6. **Some real factors are undetectable.** Below the BBP threshold a true factor
   never separates from the bulk. The right response is to state what you can
   and cannot identify, not to lower the bar.

7. **Filtering and shrinkage solve the same problem** — sample eigenvalues are
   too spread out. RMT flattens the noise bulk; Ledoit–Wolf pulls toward a
   target. Both make $\hat\Sigma^{-1}$ usable.

8. **Statistical factors fit best and communicate worst.** "You lost money on
   PC4" is not actionable, and PC4 may be a different portfolio next month.
   Production risk models are fundamental for that reason.

9. **49 industries, 2–3 factors.** The number of things you can measure is far
   smaller than the number of assets you hold — and it is set by $N/T$, not by
   how sophisticated your estimator is."""))

# ─── Appendix ─────────────────────────────────────────────────────────
cells.append(md("""---

## 📎 Appendix — Belt-and-Suspenders Data Loading <a id="appendix"></a>

The body of this notebook fetches the 49 Industry Portfolios live from Ken
French's data library. This appendix documents the fallback path: pull once,
save to the repo, load from a GitHub raw URL."""))

cells.append(code('''# ═══════════════════════════════════════════════════════════════════════
# 📎 APPENDIX — Belt-and-Suspenders Data Loading
# ═══════════════════════════════════════════════════════════════════════

# ─── 1. AI prompt that generated the data-pull code ────────────────────
# Prompt: "Using pandas-datareader, fetch '49_Industry_Portfolios' monthly from
#  the famafrench source starting 1970. Divide by 100 to get decimals. Convert
#  the PeriodIndex to month-end timestamps. Ken French codes missing values as
#  -99.99; mask anything below -0.99 after scaling. Drop industries with any
#  missing data. Save to assets/data/industry49_monthly.csv."

# ─── 2. Live fetch + save (run once, then commit the CSV) ──────────────
def fetch_and_save_industries():
    ind = DataReader('49_Industry_Portfolios', 'famafrench', start='1970-01-01')[0] / 100
    ind.index = pd.to_datetime(ind.index.to_timestamp()) + pd.offsets.MonthEnd(0)
    ind.columns = [c.strip() for c in ind.columns]
    ind = ind.mask(ind < -0.99).dropna(axis=1).dropna()
    ind.to_csv('assets/data/industry49_monthly.csv')
    return ind

# Uncomment to re-fetch live (overwrites the local CSV; then commit it):
# fetch_and_save_industries()

# ─── 3. Load from GitHub raw URL (reliable backup path) ────────────────
url_backup = ('https://raw.githubusercontent.com/amoreira2/UG54/'
              'refs/heads/main/assets/data/industry49_monthly.csv')
R_backup = pd.read_csv(url_backup, index_col=0, parse_dates=True)
print(f"Backup loaded: {R_backup.shape[0]} months x {R_backup.shape[1]} industries, "
      f"{R_backup.index.min().date()} to {R_backup.index.max().date()}")'''))

# ─── Write ────────────────────────────────────────────────────────────
notebook = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.11"},
        "colab": {"provenance": []},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

OUT.write_text(json.dumps(notebook, indent=1))
print(f"✅ Wrote {OUT}  ({len(cells)} cells)")
