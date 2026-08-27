#!/usr/bin/env python3
"""Build Assignment5_c.ipynb — Solutions to Assignment 5."""
import json, copy

with open('/Users/am16634/Documents/GitHub/UG54/chapters/Assignments/Assignment5.ipynb') as f:
    old = json.load(f)

def src_lines(text):
    lines = text.split('\n')
    result = []
    for i, line in enumerate(lines):
        if i < len(lines) - 1:
            result.append(line + '\n')
        else:
            result.append(line)
    if result and result[-1] == '':
        result.pop()
    return result

def mk_md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": src_lines(text)}

def mk_code(text):
    return {"cell_type": "code", "metadata": {}, "source": src_lines(text),
            "execution_count": None, "outputs": []}

def old_md(i):
    """Return original markdown cell i unchanged."""
    return copy.deepcopy(old['cells'][i])

cells = []

# Title (replace original)
cells.append(mk_md("""# Assignment 5 — Solutions

This notebook provides worked solutions to Assignment 5. The goal is **pedagogical**: we don't just give the answer — we explain *why* each step matters and what to look for in the output.

The unifying theme of this assignment is **estimation uncertainty**. We have only a finite sample of returns, and every statistic we compute (means, variances, optimal weights, Sharpe ratios) is itself a random variable. The exercises walk through how to *quantify* that uncertainty and how it propagates into the portfolio choice problem."""))

# === Q1: Data cleaning ===
cells.append(old_md(2))  # Q1 prompt

cells.append(mk_md("""**Solution.** We follow the same pattern as Assignment 1: load the industry returns sheet, parse the date, set the index, drop rows with missing data, and merge in the risk-free rate so we can subtract it to get excess returns."""))

cells.append(mk_code("""import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pandas.tseries.offsets import MonthEnd

url = 'https://github.com/amoreira2/UG54/blob/main/assets/data/Assignment1.xlsx?raw=true'

# --- 49 industry portfolios ---
df_ind = pd.read_excel(
    url,
    sheet_name='49_Industry_Portfolios',
    skiprows=6,                        # header row (Agric, Food, ...) is row 6
    na_values=['-99.99', '-999'],      # Ken French's missing-value codes
    usecols='A:AX'                     # date + 49 industries
)
df_ind.rename(columns={df_ind.columns[0]: 'date'}, inplace=True)
df_ind['date'] = pd.to_datetime(df_ind['date'], format='%Y%m')
df_ind.set_index('date', inplace=True)

# --- Risk-free rate from the Market_proxy sheet ---
df_rf = pd.read_excel(
    url,
    sheet_name='Market_proxy',
    skiprows=4,
    na_values=['-99.99'],
    header=None
).dropna()
df_rf.columns = ['date', 'Mkt-RF', 'RF']
df_rf['date'] = pd.to_datetime(df_rf['date'].astype(int), format='%Y%m')
df_rf.set_index('date', inplace=True)

# --- Merge industries with risk-free rate, drop missing, build excess returns ---
df_all = df_ind.merge(df_rf[['RF']], left_index=True, right_index=True, how='inner').dropna()
df = df_all.drop(columns='RF').sub(df_all['RF'], axis=0).astype(float)
df.head()"""))

cells.append(mk_md("""**What to notice.** `df` is now a clean panel of 49 industry **excess** returns (in percent per month). Subtracting the risk-free rate is essential before any portfolio analysis — it ensures all comparisons are about *risk premia*, not the level of interest rates."""))

# === Q2: Expected excess return estimation ===
cells.append(old_md(4))

cells.append(mk_md("""**Solution.** The natural estimator of $E[r^e_i]$ is just the sample mean of each column — `df.mean()` does this in one line."""))

cells.append(mk_code("""ERe = df.mean()
ERe.head()"""))

cells.append(mk_md("""**Pedagogical note.** This estimator is *unbiased* — on average across many possible samples, it equals the true mean. But for any *one* sample (like the one we have), it can be substantially off. That's exactly the issue we'll quantify next."""))

# === Q3: Standard error ===
cells.append(old_md(6))

cells.append(mk_md("""**Solution.** Under the (good) approximation that monthly returns are uncorrelated over time, the variance of the sample mean is $\\text{Var}(r_i)/T$. So the standard deviation of our estimator is $\\sigma(r_i)/\\sqrt{T}$ — a basic but central fact in statistics."""))

cells.append(mk_code("""T = df.shape[0]
ERe_se = df.std() / np.sqrt(T)
ERe_se.head()"""))

cells.append(mk_md("""**What to notice.** Compare `ERe` to `ERe_se`. The standard errors are typically the same order of magnitude as the means themselves. That's a warning sign: with this much sampling noise, individual industry premia are barely identified — and downstream calculations that depend on them (like tangency weights) will inherit that noise."""))

# === Q4: Threshold for CI ===
cells.append(old_md(8))

cells.append(mk_md("""**Solution.** For a 95% confidence interval we put 2.5% in each tail. The threshold that leaves 2.5% in the **right** tail is `sn.isf(0.025) ≈ 1.96` — the famous critical value of the standard normal."""))

cells.append(mk_code("""from scipy import stats
sn = stats.norm(0, 1)

prob_value = 0.025      # 2.5% in each tail -> 95% in the middle
threshold = sn.isf(prob_value)
print(threshold)"""))

cells.append(mk_md("""**Why 1.96?** Roughly speaking, "the 95% confidence interval is the point estimate plus or minus 2 standard errors" — and 1.96 is the precise value of that "2"."""))

# === Q5: Build CI ===
cells.append(old_md(10))

cells.append(mk_md("""**Solution.** Standard textbook formula: lower = $\\bar r - z \\cdot \\text{SE}$, upper = $\\bar r + z \\cdot \\text{SE}$."""))

cells.append(mk_code("""ERe_ci = pd.DataFrame(index=ERe.index, columns=['lower', 'upper'], dtype=float)
ERe_ci['lower'] = ERe - threshold * ERe_se
ERe_ci['upper'] = ERe + threshold * ERe_se
ERe_ci.head()"""))

cells.append(mk_md("""**What to notice.** For most industries the CI **contains zero**, meaning we cannot statistically reject that their true expected excess return is zero. This is true even with ~80 years of data. Risk premia are notoriously hard to estimate — the "noise-to-signal" ratio in returns is high."""))

# === Q6: MVE / Tangency weights ===
cells.append(old_md(12))

cells.append(mk_md("""**Solution.** The MVE portfolio uses the formula $W \\propto \\Sigma^{-1} \\mu$, where $\\Sigma$ is the covariance matrix and $\\mu$ is the vector of expected excess returns. We then rescale to hit our 10% annualized volatility target.

Two key steps:
1. Compute the **raw** weights $\\Sigma^{-1} \\mu$.
2. Find the scalar $x$ that produces 10% annualized vol. The portfolio variance is $W' \\Sigma W$, so monthly vol is $\\sqrt{W' \\Sigma W}$ and annualized vol is $\\sqrt{12} \\sqrt{W' \\Sigma W}$. Set $x \\sqrt{12} \\sqrt{W' \\Sigma W} = 10\\%$."""))

cells.append(mk_code("""# Variance-covariance matrix and its inverse
CovRe = df.cov()
invCovRe = np.linalg.inv(CovRe.values)

# Raw MVE direction
raw_weights = invCovRe @ ERe.values

# Scale to 10% annualized volatility
raw_var = raw_weights @ CovRe.values @ raw_weights
raw_vol_annual = np.sqrt(raw_var) * np.sqrt(12)
target_vol = 10.0   # 10% annualized, in the same units as df (which is in %)
x = target_vol / raw_vol_annual
norm_weights = x * raw_weights

Weights = pd.DataFrame({'mve_data': norm_weights}, index=ERe.index)
print(Weights.head())"""))

cells.append(mk_md("""**What to notice.**

- The weights are often **huge** (well above 1 in absolute value) and include many large short positions. This is normal for sample-based MVE portfolios.
- The reason: the optimizer pushes hard on tiny estimated differences in expected returns and exploits sample-specific covariance patterns. With ~50 assets, $\\Sigma^{-1}$ is very sensitive to small estimation errors in $\\Sigma$.
- This is the *first hint* that estimation uncertainty matters a lot for portfolio construction. The next exercises will make this concrete."""))

# === Q7: Sensitivity to perturbing one asset's mean ===
cells.append(old_md(14))

cells.append(mk_md("""**Solution.** We change *only* the mean of `Hshld` (Household products), recompute the entire vector of MVE weights using the same covariance matrix, and compare. We do this twice: once at the lower CI bound for `Hshld`'s mean, once at the upper CI bound."""))

cells.append(mk_code("""def compute_mve_weights(mu, cov, target_vol_annual=10.0):
    \"\"\"Compute MVE weights scaled to a given annualized vol target.\"\"\"
    raw = np.linalg.inv(cov.values) @ mu.values
    raw_vol_ann = np.sqrt(raw @ cov.values @ raw) * np.sqrt(12)
    return (target_vol_annual / raw_vol_ann) * raw

# Make perturbed copies of ERe — change ONLY Hshld's mean
ERe_lower = ERe.copy()
ERe_upper = ERe.copy()
ERe_lower['Hshld'] = ERe_ci.loc['Hshld', 'lower']
ERe_upper['Hshld'] = ERe_ci.loc['Hshld', 'upper']

Weights['mve_Hshld-1.95'] = compute_mve_weights(ERe_lower, CovRe)
Weights['mve_Hshld+1.95'] = compute_mve_weights(ERe_upper, CovRe)

# Bar plot
fig, ax = plt.subplots(figsize=(14, 5))
Weights.plot.bar(ax=ax)
ax.set_title('MVE weights: baseline vs perturbed Hshld mean')
ax.set_ylabel('Weight')
ax.legend(loc='best')
plt.tight_layout()
plt.show()"""))

cells.append(mk_md("""**Discussion.**

1. **How much do the weights change?** The weight on `Hshld` itself moves dramatically — by several units of weight even though the change in its mean is only $\\pm 1.96 \\times \\text{SE}$, which is *within* the 95% CI we cannot reject statistically. So a perfectly-plausible alternative value of $\\mu_{Hshld}$ produces a totally different position.

2. **Which other assets are impacted? Why?** Assets that are highly **correlated** with `Hshld` (e.g., other consumer-staples-like industries) also see their weights move — often in the *opposite* direction. The optimizer uses correlated assets to "hedge" the exposure it's putting on `Hshld`. This is the key insight: a small error in *one* mean spreads across the entire portfolio through the covariance matrix.

This is exactly the kind of brittleness that makes raw sample-based MVE weights dangerous in practice."""))

# === Q8: Sharpe Ratio impact ===
cells.append(old_md(17))

cells.append(mk_md("""**Solution.** For each weight scheme, the in-sample monthly portfolio return is $W'\\mu$ and the monthly variance is $W'\\Sigma W$. Annualized SR = $\\sqrt{12} \\cdot W'\\mu / \\sqrt{W'\\Sigma W}$.

**Important pedagogical point** (the hint emphasizes this): we compute Sharpe ratios using the **actual** sample mean `ERe` and covariance `CovRe`, not the perturbed means we used to compute the weights. The perturbed means represent what we *thought* the means might be — but the *true* in-sample performance is what those weights actually deliver in the data."""))

cells.append(mk_code("""def in_sample_sharpe(w, mu, cov):
    port_mean = w @ mu.values
    port_var = w @ cov.values @ w
    return np.sqrt(12) * port_mean / np.sqrt(port_var)

for col in Weights.columns:
    sr = in_sample_sharpe(Weights[col].values, ERe, CovRe)
    print(f"{col:25s} -> Sharpe = {sr:.3f}")"""))

cells.append(mk_md("""**Discussion.** All three weight schemes deliver almost the same Sharpe ratio on the actual data — even though the weights look very different. Why?

- The MVE portfolio's Sharpe ratio is a *flat* function of the weights near the optimum. Small (or even moderate) deviations from the optimum barely move the SR.
- This is good news in one sense: you don't need to nail the exact weights to capture most of the available SR.
- But it's bad news in another: the data give you almost no information about which *exact* portfolio is best. Many very different-looking portfolios are nearly as good in sample. Out of sample, that distinction can matter a lot."""))

# === Q9: Loop over all assets ===
cells.append(old_md(20))

cells.append(mk_md("""**Solution.** We repeat the perturbation exercise for *every* industry, record the average drop in Sharpe ratio, and plot the result."""))

cells.append(mk_code("""SR_data = in_sample_sharpe(Weights['mve_data'].values, ERe, CovRe)

sr_changes = {}
for asset in ERe.index:
    # Perturb mean to lower CI bound
    ERe_lo = ERe.copy()
    ERe_lo[asset] = ERe_ci.loc[asset, 'lower']
    w_lo = compute_mve_weights(ERe_lo, CovRe)
    SR_lo = in_sample_sharpe(w_lo, ERe, CovRe)

    # Perturb mean to upper CI bound
    ERe_hi = ERe.copy()
    ERe_hi[asset] = ERe_ci.loc[asset, 'upper']
    w_hi = compute_mve_weights(ERe_hi, CovRe)
    SR_hi = in_sample_sharpe(w_hi, ERe, CovRe)

    # Average relative change in SR (formula from the problem)
    sr_diff = 0.5 * ((SR_hi - SR_data) + (SR_lo - SR_data)) / SR_data
    sr_changes[asset] = sr_diff

dSR = pd.DataFrame.from_dict(sr_changes, orient='index', columns=['SR_change'])

fig, ax = plt.subplots(figsize=(14, 5))
dSR['SR_change'].plot.bar(ax=ax)
ax.set_title('Average relative SR change when perturbing one asset\\'s mean to its 95% CI bounds')
ax.set_ylabel('Relative SR change')
ax.axhline(0, color='black', linewidth=0.8)
plt.tight_layout()
plt.show()

print(dSR.head())
print(f"\\nMean change across assets: {dSR['SR_change'].mean():.4f}")
print(f"Max negative change       : {dSR['SR_change'].min():.4f}")"""))

cells.append(mk_md("""**Discussion — key takeaway.** The relative SR changes are **all very small** (typically much less than 1%). Even though we shifted *each* asset's mean by close to two standard errors — a perfectly plausible amount given our sampling uncertainty — the in-sample Sharpe ratio barely moves.

This confirms what we suspected from Q8: the MVE optimization is very flat near the optimum *in sample*. The weights themselves swing wildly with small changes in the inputs, but the **realized in-sample SR is nearly invariant**.

So why do we care? Two reasons:
1. **Out-of-sample**: even if all these weight schemes deliver similar in-sample SRs, they will perform very differently going forward. Picking the right "version" of the MVE portfolio is hard, and small input errors lead to big position differences.
2. **Real-world cost**: huge weights mean huge transaction costs, leverage requirements, and tracking-error risk. Even when SR is "flat," the *implementation* is not."""))

# === Q10-13: Monte Carlo ===
cells.append(old_md(23))

cells.append(mk_md("""**Solution.** `np.random.multivariate_normal(mean, cov, size)` draws from a multivariate normal distribution. With `size=1` (or omitting size), we get one realization."""))

cells.append(mk_code("""one_draw = np.random.multivariate_normal(ERe.values, CovRe.values)
print("Shape:", one_draw.shape)
print("First few values:", one_draw[:5])"""))

cells.append(mk_md("""Each time you run the cell, the values change — that's the random sampling."""))

cells.append(old_md(25))

cells.append(mk_md("""**Solution.** Set `size=T` to draw T monthly realizations of the 49-asset return vector. The output is a $T \\times 49$ matrix — same shape as our actual data."""))

cells.append(mk_code("""sim = np.random.multivariate_normal(ERe.values, CovRe.values, size=T)
print("Shape:", sim.shape)
print(f"(That is T={T} months of {sim.shape[1]}-asset returns)")"""))

cells.append(old_md(27))

cells.append(mk_md("""**Solution.** Each Monte-Carlo run: simulate a fresh sample of returns, apply the **same** MVE weights (`mve_data`) to it, and compute the resulting Sharpe ratio.

This is the question: *if reality is exactly described by `ERe` and `CovRe`, what is the distribution of in-sample Sharpe ratios I would obtain across alternative samples that history could have produced?*"""))

cells.append(mk_code("""simulated_returns = np.random.multivariate_normal(ERe.values, CovRe.values, size=T)
w_mve = Weights['mve_data'].values

simulated_port_returns = simulated_returns @ w_mve
sr_sim = simulated_port_returns.mean() / simulated_port_returns.std() * np.sqrt(12)
print(f"Simulated Sharpe ratio: {sr_sim:.3f}")
print(f"In-sample Sharpe ratio: {SR_data:.3f}")"""))

cells.append(old_md(29))

cells.append(mk_md("""**Solution.** Wrap the previous code in a loop, save all 1000 Sharpe ratios, and plot the distribution."""))

cells.append(mk_code("""mc_sharpes = []
np.random.seed(42)   # for reproducibility while you're studying
for it in range(1000):
    sim = np.random.multivariate_normal(ERe.values, CovRe.values, size=T)
    port = sim @ w_mve
    sr = port.mean() / port.std() * np.sqrt(12)
    mc_sharpes.append(sr)

MC = pd.DataFrame({'sharpe': mc_sharpes})

fig, ax = plt.subplots(figsize=(10, 5))
MC['sharpe'].hist(bins=50, ax=ax, edgecolor='white')
ax.axvline(SR_data, color='red', linestyle='--', linewidth=2, label=f'In-sample SR = {SR_data:.2f}')
ax.axvline(MC['sharpe'].mean(), color='black', linestyle='--', linewidth=2, label=f'MC mean = {MC[\"sharpe\"].mean():.2f}')
ax.set_xlabel('Sharpe ratio')
ax.set_ylabel('Frequency')
ax.set_title(f'Distribution of in-sample Sharpe ratios under MC (1000 sims, T={T})')
ax.legend()
plt.tight_layout()
plt.show()

print(f"MC mean SR: {MC['sharpe'].mean():.3f}")
print(f"MC std SR : {MC['sharpe'].std():.3f}")
print(f"5th pct   : {MC['sharpe'].quantile(0.05):.3f}")
print(f"95th pct  : {MC['sharpe'].quantile(0.95):.3f}")"""))

cells.append(mk_md("""**Discussion.**

- The histogram shows a wide spread of Sharpe ratios. Even though our weights are *fixed* and the *true* moments are fixed (we used `ERe` and `CovRe` as the truth!), small-sample noise alone produces a distribution of SRs spanning a factor of ~2.
- The mean of the MC distribution is *close to* the in-sample SR — that's reassuring: our point estimate isn't biased.
- But the 5th-to-95th percentile range is enormous. With T months of data, we cannot pin down the strategy's true Sharpe ratio precisely. **Sampling noise alone, without any model misspecification, generates a huge range of possible outcomes.**

And remember: this Monte Carlo only captures uncertainty *given the true means and covariances*. We've assumed those are known. In reality, we estimated them too — so the *full* uncertainty is even larger than what this simulation shows."""))

# === Q14: why investor cares ===
cells.append(old_md(32))

cells.append(mk_md("""**Solution / discussion.**

Three reasons every investor should care:

1. **Don't be seduced by in-sample Sharpe ratios.** Q9 and Q13 together showed that the in-sample SR you obtain from optimizing on a single sample is a noisy estimate of *anything*. Two strategies whose true SRs are nearly identical can produce wildly different in-sample numbers; conversely, a strategy that looks great in sample can have substantial probability of being mediocre out of sample. This is the foundation of **overfitting risk**.

2. **Sample-MVE weights are unstable.** Q7 and Q9 showed that small, statistically-indistinguishable changes in the input means produce huge swings in optimal weights. In practice this means: large transaction costs, large leverage requirements, sensitivity to data revisions, and exposure to idiosyncratic risk. Practitioners almost always **shrink** the inputs (toward the global minimum-variance portfolio, toward equal weighting, or toward a Bayesian prior) before optimizing.

3. **The true distribution of Sharpe ratios is wider than people realize.** When a manager presents a backtest with SR = 1.5, the relevant question is not "is 1.5 good?" but "what's the distribution of SRs I would have seen across plausible alternative samples?" The Monte Carlo shows that this distribution can easily span a factor of two even when the strategy is genuinely good.

These ideas tie directly into the Performance Evaluation chapter (the Sharpe-ratio standard error formula, the bootstrap, and the fraction-to-half diagnostic are all attempts to pin down this kind of uncertainty in practice)."""))


# Final structure
nb = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.11.0"
        }
    },
    "cells": cells
}

outpath = '/Users/am16634/Documents/GitHub/UG54/chapters/Assignments/Assignment5_c.ipynb'
with open(outpath, 'w') as f:
    json.dump(nb, f, indent=1)

print(f"Wrote {len(cells)} cells to {outpath}")
