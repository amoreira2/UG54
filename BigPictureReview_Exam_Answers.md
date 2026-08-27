# UG54 — Big Picture Review Exam — Answer Key

## Chapters 4–13 | Data-Driven Investing with Python

---

### Question 1: Returns & the Sharpe Ratio (Ch 4)

**(a)**
- Total return 2023: $(1 + 2.40) = 3.40$
- Total return 2024: $(1 + 1.70) = 2.70$
- Cumulative: $3.40 \times 2.70 = 9.18$ (i.e., +818% over two years)
- Annualized total return: $9.18^{1/2} - 1 = 2.03$, or **203% per year**
- Risk-free rate ≈ 5% per year
- **Annualized excess return ≈ 198% per year**

Why excess returns: the risk-free rate is the opportunity cost of capital — it's what you earn for doing nothing. Only the return *above* the risk-free rate compensates for bearing risk. This is why every key concept in the course (Sharpe ratio, alpha, factor premia, optimal weights) is defined in terms of excess returns.

**(b)**
- $SR = 198\% / 55\% \approx \mathbf{3.6}$

Two reasons the comparison with Vol-Managed Momentum (SR = 1.48) is misleading:

1. **Estimation error**: NVIDIA's SR is estimated from just 2 years of data. The standard error of an estimated Sharpe ratio is $\approx 1/\sqrt{T} = 1/\sqrt{2} = 0.71$. The 95% confidence interval is roughly (2.2, 5.0) — far too wide to draw conclusions.

2. **In-sample vs. realized**: The managed momentum SR of 1.48 is computed using a normalization constant $c$ calibrated on the *full sample* (1963–2024) — it benefits from look-ahead in the scaling. Comparing an in-sample optimized strategy SR to a single stock's realized return is apples to oranges.

**(c)**
- The colleague multiplied by 12 instead of $\sqrt{12}$.
- The correct rule: expected returns scale proportionally with time ($\mu_A = 12 \mu_M$), but volatility scales with the square root of time ($\sigma_A = \sqrt{12} \, \sigma_M$). Therefore the Sharpe ratio scales with $\sqrt{T}$:

$$SR_A = SR_M \times \sqrt{12} = 0.40 \times 3.46 = \mathbf{1.39}$$

---

### Question 2: Estimation Uncertainty & the Big Picture (Ch 8, 9, 11)

**(a)**
- $SR = 4.68\% / 19.95\% = \mathbf{0.235}$
- $SE(SR) \approx 1/\sqrt{20} = 0.224$
- 95% confidence interval: $0.235 \pm 1.96 \times 0.224 = \mathbf{(-0.20, \; 0.67)}$
- **The interval includes zero.** We cannot reject that the true Sharpe ratio is zero — even 20 years of monthly data is insufficient to confirm a strategy with SR ≈ 0.24. This illustrates the central problem of the course: expected returns are extremely hard to estimate. The standard error $1/\sqrt{T}$ shrinks painfully slowly.

**(b)**

This is the **bias-variance tradeoff**. With 51 characteristics, each estimated with noise from historical data, the model has enormous flexibility — but that flexibility allows it to fit noise in-sample. Key points:

- The signal-to-noise ratio in stock returns is very low (monthly cross-sectional R² ≈ 1%). In this environment, the variance of estimates dominates any gain from modeling complexity.
- A 1-parameter model (interest coverage) has high bias (it ignores 50 potentially relevant characteristics) but very low variance in its estimates. The net prediction quality is better because there's so little noise in the estimate.
- This is exactly why **shrinkage**, **regularization** (Lasso), and **factor models** work — they all deliberately trade bias for variance reduction. In finance's low-SNR world, this trade is almost always worthwhile.

**(c)**

Three responses to estimation uncertainty, with student project examples:

1. **Shrink expected returns** toward zero or a prior — reduces estimation error in $\hat{\mu}$. DJR's LightGBM uses tree regularization (implicit shrinkage). Foundation Capital caps weights at $|w| \leq 0.25$, which implicitly shrinks extreme $\hat{\mu}$ estimates.

2. **Factor model for the covariance matrix** — reduces parameters from $N(N+1)/2$ to $NK + N$. The Interest Coverage team uses inverse-volatility weighting (implicitly a diagonal $\Sigma$ model). The Inertia team builds on the FF5 factor structure.

3. **Bet-sizing heuristics / weight constraints** (1/N, risk parity, caps) — prevent extreme positions driven by noisy estimates. Foundation Capital's $|w| \leq 0.25$ cap. Vol-Managed Momentum's 2× cap. The Macro Risk-Managed team bounds allocation to [0, 1.5].

---

### Question 3: Factor Models — Two Uses (Ch 6, 9)

**(a)**
- **Momentum** ($\beta_{Mom} = 0.71$) is most responsible for the alpha drop.
- The expected return decomposition (factor model as E[R] model):

$$E[r^e] = \alpha + \beta_{MKT} \lambda_{MKT} + \beta_{SMB} \lambda_{SMB} + \beta_{HML} \lambda_{HML} + \beta_{Mom} \lambda_{Mom}$$

- If the momentum premium is approximately 5% per year, then the momentum loading explains $0.71 \times 5\% \approx 3.6\%$ — accounting for nearly all of the 3.7% drop from 8.28% to 4.57%.
- **Economic intuition**: A CEO whose stock has been rising (high momentum) naturally sounds more optimistic and confident in earnings calls. The LLM detects this confidence as "positive sentiment" — but it's really just picking up the effect of past price appreciation on managerial tone, not independent information about future returns.

**(b)**

Not fully justified. Three considerations:

1. **Small sample**: 24 quarterly observations is very short. The t-stat of 0.99 may reflect insufficient statistical power, not zero true alpha. With a longer sample, the t-stat could be significant.

2. **Correlation ≠ causation**: Sentiment might *cause* future momentum (information in the earnings call → prices adjust → measured as momentum), rather than merely reflecting past momentum. If so, the factor loading is endogenous and the alpha is real.

3. **What you'd need**: A *conditional analysis* — compute the strategy's returns in months where momentum does poorly (negative UMD returns). If the strategy still earns positive returns when momentum fails, it contains genuinely independent information.

**(c)**

Factor model as a **risk model** — R² for portfolios vs. individual stocks:

- **Individual stocks**: R² would increase substantially (from ~2.5% to maybe 20–30%) because individual stock returns are driven by multiple systematic factors. Adding SMB, HML, RMW, CMA captures more of each stock's comovement with the broader market.

- **The L/S portfolio**: R² would increase only *marginally*. A sector-neutral long-short portfolio is constructed to diversify away factor exposures — that's the whole point. The remaining risk is predominantly idiosyncratic regardless of how many factors you use.

- **The key difference**: Diversification eliminates systematic risk in portfolios (idiosyncratic risks cancel across many stocks). Factor models matter most for individual stocks (they capture the covariance structure), but well-diversified L/S portfolios have mostly idiosyncratic risk by construction.

---

### Question 4: Factor Models — Risk Decomposition (Ch 6)

**(a)**
- Systematic variance: $\beta^2 \sigma^2_{MKT} = (0.28)^2 \times (15\%)^2 = 0.0784 \times 225 = 17.64\; (\%^2)$ → $\sigma_{sys} = 4.2\%$ per year
- Idiosyncratic variance: $\sigma^2_\varepsilon = (26\%)^2 = 676\; (\%^2)$
- Total variance: $17.64 + 676 = 693.64\; (\%^2)$
- **Fraction idiosyncratic**: $676 / 693.64 = \mathbf{97.5\%}$

Interpretation: Almost all of the strategy's risk is stock-specific (idiosyncratic). This is a pure alpha/stock-picking bet, not a market directional bet. The near-zero market exposure means the strategy's returns are almost entirely driven by the quality of individual stock selection within each sector.

**(b)**
- $AR = \alpha / \sigma(\varepsilon) = 24\% / 26\% = \mathbf{0.92}$

AR alone is **not sufficient**. The maximum drawdown of −35% reveals:

1. **Tail risk**: AR assumes returns are normally distributed. Real returns have fat tails — extreme losses are more frequent than the normal distribution predicts.
2. **Path dependency**: An investor can be forced out (margin calls, redemptions, career risk) long before the AR "materializes" over the expected holding period.
3. **Capacity**: Large drawdowns may exceed risk limits, triggering forced liquidation at the worst possible time.

The AR tells you the *expected* Sharpe ratio of the alpha stream; the drawdown tells you the *worst path* you might actually experience.

**(c)**

$$SR^2_{combined} = SR^2_{mkt} + AR^2 = 0.46^2 + 0.92^2 = 0.2116 + 0.8464 = 1.058$$

$$SR_{combined} = \sqrt{1.058} = \mathbf{1.03}$$

The combined SR exceeds either component because the hedged alpha ($r_{hedge} = \alpha + \varepsilon$) is **uncorrelated** with the market by construction. Combining uncorrelated return streams always increases the Sharpe ratio — this is diversification applied not to assets but to *sources of return*. This is the **Pythagorean theorem of active management**: $SR^2 = SR^2_{mkt} + AR^2$.

---

### Question 5: Portfolio Mathematics — Diversification (Ch 7)

**(a)**

Despite Factor X having higher volatility (22% vs 15%), adding a small allocation *reduces* portfolio volatility because the correlation $\rho = 0.20$ is low.

**Intuition**: When MKT goes down, Factor X usually does *not* follow (they move mostly independently). The portfolio variance formula includes a cross-term $2w_1 w_2 \rho \sigma_1 \sigma_2$ — when $\rho$ is small, this cross-term is small, and the variance reduction from "averaging" dominates the additional variance from X's higher volatility.

Compared to US/International ($\rho \approx 0.65$): those two assets move together much more, so the cross-term is large, and diversification is limited. **Low correlation is the engine of diversification.**

**(b)**

The MVE portfolio puts **less** than 30% in Factor X.

**Tension**: The minimum-variance portfolio maximizes diversification (puts ~30% in X) but completely ignores expected returns. The MVE investor must also consider that MKT has a much higher expected return (8% vs 5%). She tilts *toward* MKT, accepting somewhat higher risk to capture the return premium. The MVE portfolio optimally trades off the diversification benefit of X against its lower expected return — the allocation reflects both risk AND return considerations.

**(c)**

Take the derivative of portfolio variance with respect to weight $w$ on Factor X, evaluated at $w = 0$:

$$\frac{d\text{Var}}{dw}\bigg|_{w=0} = -2\sigma^2_{MKT} + 2\rho \sigma_{MKT} \sigma_X = 2\sigma_{MKT}(\rho \sigma_X - \sigma_{MKT})$$

This is negative (adding X reduces variance) when:

$$\rho \sigma_X < \sigma_{MKT} \quad \Longrightarrow \quad \rho < \frac{\sigma_{MKT}}{\sigma_X} = \frac{15}{22} = \mathbf{0.68}$$

At $\rho = 0.80$: since $0.80 > 0.68$, adding Factor X would **increase** portfolio volatility. Diversification fails.

**General principle**: Adding a more volatile asset reduces portfolio risk *only if* the correlation is below $\sigma_1 / \sigma_2$. When the new asset is more volatile, the threshold is below 1 and the condition is genuinely restrictive.

---

### Question 6: Hedging & Portable Alpha (Ch 6, 8, 9)

**(a)**

$$r^e_{Tech} = \alpha + \beta f + \varepsilon = 0.26\% + (-0.34)f + \varepsilon$$

Expected excess return:

$$E[r^e_{Tech}] = \alpha + \beta \cdot E[f] = 0.26\% + (-0.34)(0.65\%) = 0.26\% - 0.22\% = \mathbf{0.04\%\text{/month}}$$

**Decomposition**: 0.26% comes from alpha (stock-picking skill), while −0.22% comes from the negative market beta (the negative loading *costs* expected return because the market has a positive risk premium). Almost all expected return is alpha; the market exposure actually *hurts*.

**(b)**

Since $\beta = -0.34$, the hedge is to go **long** \$0.34 in the market index per \$1 of L/S position (you need to *add* market exposure to offset the negative beta).

$$r_{hedged} = r_{LS} - \beta \cdot f = (\alpha + \beta f + \varepsilon) - \beta f = \mathbf{\alpha + \varepsilon}$$

The hedge removes all market exposure. The volatility of the hedged position is:

$$\sigma(hedged) = \sigma(\varepsilon) = \mathbf{12\% \text{ per month}}$$

**(c)**

$$AR = \frac{\alpha}{\sigma(\varepsilon)} = \frac{0.26\%}{12\%} = 0.0217 \text{/month} \quad \Rightarrow \quad AR_{ann} = 0.0217 \times \sqrt{12} = \mathbf{0.075}$$

Optimal position size:

$$w^* = \frac{1}{\gamma} \frac{\alpha}{\sigma^2(\varepsilon)} = \frac{1}{2} \frac{0.0026}{0.0144} = \mathbf{0.09}$$

(9 cents per dollar of capital — a tiny position.)

**Lesson**: Alpha alone does not determine how much to bet — the ratio $\alpha / \sigma^2(\varepsilon)$ does. The Tech sleeve has positive alpha (0.26%/month) but enormous idiosyncratic volatility (12%/month). The Appraisal Ratio of 0.075 is extremely low, and the optimal weight formula correctly prescribes a near-zero bet. The −97% max drawdown confirms this: even with positive alpha, a strategy with terrible signal-to-noise deserves almost no capital. **The optimal weight formula w* ∝ α/σ²(ε) is the formalization of this idea — it says: bet proportionally to the AR, not to alpha alone.**

---

### Question 7: Capital Allocation & Bet Sizing (Ch 8, 11)

**(a)**

Starting from the mean-variance objective:

$$\max_w \quad w \cdot \hat{\mu} - \frac{\gamma}{2} w^2 \cdot RV$$

First-order condition (take derivative w.r.t. $w$, set to zero):

$$\hat{\mu} - \gamma \cdot w \cdot RV = 0$$

Solve:

$$\boxed{w^* = \frac{\hat{\mu}}{\gamma \cdot RV}}$$

This is the **golden thread** of the course — every capital allocation decision is a version of this formula.

**(b)**

**Problem with uncapped $w^*$**: If $\hat{\mu}$ is noisy (high estimation error) and $RV$ happens to be temporarily low, $w^*$ explodes. A noisy numerator and small denominator → absurdly large bets driven by noise, not signal. This is estimation risk in action.

**The cap $|w| \leq 0.25$ is analogous to shrinkage**: It truncates extreme weights, effectively saying "even if the formula says bet 3× your capital, never exceed 0.25." This is a hard constraint version of shrinkage — it pulls extreme estimates toward zero.

**Alternative bet-sizing approach**: **Risk parity** ($w_i \propto 1/\sigma_i$) — allocates inversely proportional to volatility, ignoring expected returns entirely. It addresses estimation risk by refusing to estimate $\hat{\mu}$ at all, betting only on diversification. This is appropriate when expected return estimates are very unreliable (which they usually are) but risk estimates are stable (which they usually are — volatility is much easier to estimate than means).

**(c)**

With fees consuming fraction $\phi$ of gross expected return, the net expected return is $\hat{\mu}(1 - \phi)$:

$$w^*_{net} = \frac{\hat{\mu}(1 - \phi)}{\gamma \cdot RV} = (1 - \phi) \cdot \frac{\hat{\mu}}{\gamma \cdot RV}$$

Fees proportionally shrink both the optimal weight and the net Sharpe ratio: $SR_{net} = (1-\phi) \cdot SR_{gross}$.

**Foundation Capital's case**: Fees consumed roughly 42% of gross expected return ($\phi \approx 0.42$), and spread costs pushed total friction even higher. The strategy's gross SR of 1.43 was destroyed because $(1 - \phi) \times 1.43 < 0$ when total costs exceed gross return.

**General principle**: There is a **minimum implementable Sharpe ratio** — below which no strategy survives after costs. The higher the transaction costs (frequency, spreads, fees), the higher the gross SR must be to remain profitable. This is why high-frequency strategies require much stronger raw signals than low-frequency ones.

---

### Question 8: Volatility Timing & Momentum (Ch 5, 10)

**(a)**

- February 2009 RV = 10% annualized → $\sigma^2_{Feb} = (0.10)^2 = 0.01$
- $w_{March} = \min\left(\frac{0.015}{0.01}, 2\right) = \min(1.5, 2) = \mathbf{1.5}$ (heavily loaded)

- March 2009 RV = 80% annualized → $\sigma^2_{March} = (0.80)^2 = 0.64$
- $w_{April} = \min\left(\frac{0.015}{0.64}, 2\right) = \min(0.023, 2) = \mathbf{0.023}$ (nearly zero)

The weight drops from 1.5 to 0.023 — a **98.5% reduction** in a single month.

**(b)**

The strategy *was* heavily loaded (w = 1.5) going into March 2009 and took a hit in that month. But **momentum crashes are prolonged** — the raw −53% for 2009 accumulated over many months, not just March.

The critical mechanism: after the initial crash, RV spiked → weight dropped to near zero → the managed strategy sat out the subsequent months of continued losses. Raw momentum kept *full exposure* (w = 1) throughout, absorbing every subsequent loss.

**Vol timing doesn't predict the first hit, but it prevents the slow bleed that follows.** Because volatility *clusters* (high vol is followed by high vol), cutting exposure after a spike correctly anticipates continued danger.

**(c)**

When volatility is persistently low, $RV \approx c$ (the long-run variance) → $w \approx c/c = 1$. Or it hits the 2× cap if RV dips below the long-run average. Either way, the weight becomes **nearly constant** — there's no timing, just fixed leverage.

**Connection to Chapter 5**: Volatility timing works because volatility is *forecastable* — lagged realized volatility predicts future realized volatility with R² ≈ 50% at the monthly horizon. This is in stark contrast to expected returns, which are essentially *unforecastable* (out-of-sample R² ≈ 0% for dividend yield and other predictors).

But forecastability only helps when there's **variation to exploit**. In a stable low-vol regime (2013–2024), volatility barely moved — there was nothing to forecast. The strategy degenerates into fixed leverage because the input (RV) is constant. Volatility timing earns its keep during *regime transitions* — calm → crisis → calm — not during prolonged stability.

---

### Question 9: Performance Evaluation & Overfitting (Ch 12)

**(a)**

The single most important number is the **t-statistic on FF4 alpha = 0.99**.

**Reasoning**: This directly answers "does this strategy have alpha after controlling for factor exposures you could obtain cheaply from factor ETFs?" The threshold is t > 2.0 (for 95% confidence — and arguably higher given potential multiple testing).

At t = 0.99, we **cannot reject** that true alpha is zero. The raw return (6.51%) and CAPM alpha (t = 1.76) are misleading because they don't account for factor exposures — particularly momentum — that provide "free" expected return. The strategy could simply be repackaging known factor premia.

The FF4 alpha t-stat is the definitive metric because it isolates the question: *does this strategy have skill beyond what you can get from passive factor exposure?*

**(b)**

**Standard look-ahead bias**: Using price data from time $t+1$ to form a signal at time $t$. Mechanical, obvious, and detectable by code review.

**LLM look-ahead bias**: Claude was trained on text from 2019–2024 — financial news, analyst reports, earnings discussions, company narratives. When scoring a Q1 2020 earnings call, Claude may "know" from its training data that the company subsequently thrived or collapsed. This knowledge is embedded in the model's weights — the signal at time $t$ is contaminated by information from $t+1, \ldots, T$ that exists in the training corpus.

**More concerning** than standard look-ahead because:

1. **Cannot be fixed**: You can't un-train the model or remove specific future knowledge from its parameters.
2. **Invisible**: No timestamp violation in the code — the data pipeline looks clean.
3. **Potentially large**: LLMs may have internalized company-specific narratives ("Tesla's 2020 stock surge," "Peloton's post-COVID decline") that directly predict returns.
4. **Unquantifiable**: There's no way to measure how much "future knowledge" the model uses in each scoring decision.

**(c)**

**Argument FOR real alpha:**
- CAPM alpha is 8.28% with t = 1.76 — close to significant, and the short sample (24 quarters) limits statistical power
- Hit rate of 67% (16/24 quarters positive) shows consistency
- Even FF4 alpha is positive (4.57%) — it's just statistically underpowered, not estimated to be zero
- Fraction-to-half of 12.5% (only need to remove 3 best quarters to halve returns) is reasonable — not fragile

**Argument AGAINST (just repackaged momentum):**
- Momentum $\beta = 0.71$ with $t = 1.93$ — large and nearly significant
- FF4 alpha $t = 0.99$ — cannot reject zero once momentum is controlled for
- Economic logic directly supports overlap: stocks with recent price appreciation → confident management → positive LLM sentiment score. The signal chain is: momentum → tone → LLM score.

**Most informative additional analysis**: **Conditional performance** — compute the strategy's returns in months where momentum returns are *negative*. If the strategy earns positive returns when momentum *fails*, it contains genuinely independent information about future returns. If it only makes money when momentum also makes money, it's redundant with a momentum ETF.

---

### Question 10: Multiple Choice

**(1) Answer: (B) 8.8%**

$E[r_i] = r_f + \beta_i (E[r_m] - r_f) = 4\% + 0.8 \times (10\% - 4\%) = 4\% + 4.8\% = 8.8\%$

Core concept: The CAPM expected return equation — beta scales the *equity premium*, not the total market return.

**(2) Answer: (B)**

In Technology, financially distressed firms (low interest coverage) are often high-growth companies investing aggressively — think Amazon, Tesla, or early-stage biotech. These firms have low or negative interest coverage because they're borrowing to fund growth, not because they're failing. During bull markets, these "distressed" tech firms outperform, reversing the signal's logic. The signal works in sectors where low coverage genuinely indicates financial distress (Energy, Finance, Pharma) but fails where it proxies for growth investment.

Core concept: Factor premia depend on the *economic mechanism* behind the signal, not just the statistical relationship. The same characteristic can have opposite implications in different economic contexts.

**(3) Answer: (B)**

- Factor model: $5 \times 1{,}000$ betas + $5(6)/2 = 15$ factor covariances + $1{,}000$ idiosyncratic variances = **6,015 parameters**
- Full covariance matrix: $1{,}000 \times 1{,}001 / 2 = 500{,}500$ parameters
- Ratio: approximately **100× reduction**

Core concept: The factor model achieves massive dimension reduction — this is its primary value as a *risk model*.

**(4) Answer: (B) $\sqrt{0.46^2 + 0.60^2} \approx 0.76$**

$SR_{combined} = \sqrt{SR^2_{mkt} + AR^2}$

Core concept: The **Pythagorean theorem of active management** — because the hedged alpha ($\alpha + \varepsilon$) is uncorrelated with the market factor, their squared Sharpe ratios add.

**(5) Answer: (B)**

The Sharpe ratio improvement is 0.03 (from 0.45 to 0.48) over 35 years. The standard error of a Sharpe ratio estimate over 35 years is $\approx 1/\sqrt{35} \approx 0.17$. The improvement (0.03) is **far smaller than the estimation error** (0.17), so it is almost certainly not statistically significant. We cannot distinguish the "improved" strategy from the benchmark.

Core concept: Estimation uncertainty applies not just to building strategies but to *evaluating* them — a small improvement in Sharpe could easily be noise.
