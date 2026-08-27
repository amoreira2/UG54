# UG54 — Big Picture Review Exam

## Chapters 4–13 | Data-Driven Investing with Python

---

### Question 1: Returns & the Sharpe Ratio (Ch 4)

NVIDIA returned approximately 240% in 2023 (the AI boom year) and 170% in 2024. Meanwhile, 1-month T-bills yielded about 5% per year in both years, and the S&P 500 returned about 26% in 2023 and 25% in 2024.

**(a)** Compute NVIDIA's annualized excess return over the two-year period 2023–2024. (Hint: compound the total returns first, then annualize, then subtract the risk-free rate.) Why do we work with excess returns rather than raw returns throughout this course?

**(b)** Suppose NVIDIA's annualized volatility over this period was 55%. Compute its Sharpe ratio. The Volatility-Managed Momentum team reported an in-sample Sharpe ratio of 1.48 for their strategy over 1963–2024. A classmate says: "NVIDIA's Sharpe is lower than the momentum strategy, so momentum is the better investment." Give two distinct reasons why this comparison is misleading.

**(c)** A colleague argues: "NVIDIA's monthly Sharpe ratio was about 0.40, so its annual Sharpe ratio is 0.40 × 12 = 4.8." What mistake did they make? What is the correct annualization, and what annual Sharpe does it imply?

---

### Question 2: Estimation Uncertainty & the Big Picture (Ch 8, 9, 11)

The DJR Investments team used LightGBM (a machine learning model) with 51 firm characteristics to predict monthly stock returns. After a careful walk-forward backtest over 20 years (2000–2019), their long-short strategy earned an annualized excess return of 4.68% with a volatility of 19.95% and a t-statistic on alpha of approximately 1.09.

**(a)** Compute DJR's annualized Sharpe ratio. Using the rule of thumb that the standard error of an estimated Sharpe ratio is approximately $1/\sqrt{T}$ where $T$ is in years, construct a 95% confidence interval around DJR's Sharpe ratio. Does the interval include zero? What does this tell you?

**(b)** DJR used 51 characteristics — far more inputs than a simple factor model. Despite this, their t-stat is only 1.09, while the Interest Coverage team's simpler strategy (one signal: EBIT / Interest Expense) achieved a t-stat of 3.67 over a similar horizon. More complexity does not always mean better performance. Using concepts from the course, explain why estimation uncertainty can make a simpler model outperform a more complex one out of sample.

**(c)** Name three distinct responses to estimation uncertainty that we studied in this course, and for each, identify which student project (if any) used that approach. (Hint: think about what you do to expected returns, what you do to the covariance matrix, and what you do to portfolio weights.)

---

### Question 3: Factor Models — Two Uses (Ch 6, 9)

The Athena (Earnings Sentiment) strategy used Claude to score the sentiment of earnings call transcripts and formed long-short quintile portfolios. The regression results were:

| Model | Alpha (ann.) | Market β | SMB β | HML β | Mom β | t(α) |
|-------|-------------|----------|-------|-------|-------|------|
| CAPM | 8.28% | 0.01 | — | — | — | 1.76 |
| FF4 | 4.57% | −0.04 | 0.29 | −0.17 | 0.71 | 0.99 |

**(a)** The CAPM alpha is 8.28% but the four-factor alpha drops to 4.57%. Which factor is most responsible for this drop? Using the factor model as an expected return model, write the equation that shows how the strategy's expected return decomposes into factor premia and alpha. Explain the economic intuition for why an earnings sentiment strategy loads on this factor.

**(b)** The t-statistic on alpha goes from 1.76 (CAPM) to 0.99 (FF4). A classmate concludes: "The strategy has no skill — it's just momentum in disguise." Is this conclusion fully justified? What would you need to check before dismissing the strategy entirely?

**(c)** Now consider the factor model as a *risk model*. The Interest Coverage team estimated their strategy's market β = −0.29 and found R² ≈ 2.5% (almost all risk is idiosyncratic). If they had used a richer model with 5 factors instead of 1, would you expect R² to increase substantially for their *portfolio*? What about for *individual stocks* in their portfolio? Explain the difference.

---

### Question 4: Factor Models — Risk Decomposition (Ch 6)

The Interest Coverage team reported the following statistics for their equal-weight sector-neutral long-short strategy:

- Market β = −0.28
- α = 24% per year (approximately, after adjusting for small negative β × market premium)
- σ(ε) = 26% per year (idiosyncratic volatility)
- Market annual volatility: σ_MKT = 15%

**(a)** Compute the systematic (market-related) variance and the idiosyncratic variance of the strategy (annualized). What fraction of total variance is idiosyncratic? What does this tell you about the nature of the strategy's risk?

**(b)** Compute the Appraisal Ratio. The team also reported a maximum drawdown of −35%. Is the Appraisal Ratio alone sufficient to evaluate this strategy? What additional risk measure matters and why?

**(c)** If the market's annual Sharpe ratio is 0.46, what is the combined Sharpe ratio of a portfolio that optimally combines the market with this fund's hedged alpha? Show the formula and the calculation. Why is the combined SR higher than either component alone?

---

### Question 5: Portfolio Mathematics — Diversification (Ch 7)

The Inertia team (Wu & Yang) combined five Fama-French factors into a single portfolio. Consider combining MKT with a hypothetical high-volatility factor:

| Factor | E[Rᵉ] (annual) | σ (annual) |
|--------|----------------|------------|
| MKT | 8.0% | 15.0% |
| Factor X | 5.0% | 22.0% |

The correlation between MKT and Factor X is ρ = 0.20. You compute portfolio volatility for several allocations:

| Weight on X | Portfolio Volatility |
|-------------|---------------------|
| 0% | 15.00% |
| 10% | 14.11% |
| 20% | 13.58% |
| 30% | 13.47% |
| 40% | 13.79% |
| 50% | 14.50% |

**(a)** Factor X is more volatile than MKT (22% vs 15%), yet adding a 10% allocation to X *reduces* portfolio volatility below 15%. Explain intuitively why this is possible. What property of the two assets makes this work?

**(b)** The minimum-volatility portfolio is near 30% Factor X. But a mean-variance investor cares about both risk *and* return. Would the MVE portfolio put more or less than 30% in Factor X? Explain the tension between diversification and expected return without doing any calculation.

**(c)** Now suppose the correlation were ρ = 0.80 instead of 0.20. For a *small* addition of Factor X to a 100% MKT portfolio, derive the condition on ρ under which adding Factor X reduces portfolio volatility. (Hint: take the derivative of portfolio variance with respect to the weight on X, evaluate at w = 0, and find when it is negative.) Does Factor X still help at ρ = 0.80?

---

### Question 6: Hedging & Portable Alpha (Ch 6, 8, 9)

The Interest Coverage team runs a sector-neutral long-short strategy. Within the Technology sector, their long-short portfolio had:

- α = 0.26% per month (annualized ~3.13%)
- β = −0.34
- σ(ε) = 12% per month (very high — tech is volatile)

The market's expected excess return is 0.65% per month and its volatility is 4.5% per month.

**(a)** Write out the return equation for the Tech sleeve: $r^e_{Tech} = \alpha + \beta f + \varepsilon$. Plug in the numbers to compute the expected excess return of the *unhedged* position. How much of this expected return comes from alpha versus from the market factor loading?

**(b)** Suppose a pod shop wanted to fully hedge the Tech sleeve. For every $1 in the Tech long-short position, describe the hedge trade. Write out the return on the hedged position. What is the volatility of the hedged position?

**(c)** Compute the Appraisal Ratio (annualized). Using the optimal bet-sizing formula $w^* = \frac{1}{\gamma} \frac{\alpha}{\sigma^2(\varepsilon)}$, compute the optimal position size for an investor with γ = 2. Despite having positive alpha, the Tech sleeve had a maximum drawdown of −97%. What does this illustrate about the relationship between alpha, the Appraisal Ratio, and position sizing?

---

### Question 7: Capital Allocation & Bet Sizing (Ch 8, 11)

The Foundation Capital team traded prediction markets on Kalshi. Their bet-sizing rule was:

$$w = \frac{\hat{\mu}}{\gamma \cdot RV}$$

where $\hat{\mu}$ is the estimated expected return from a regression, $\gamma = 2$ is risk aversion, and $RV$ is the trailing 30-day realized variance. They capped $|w| \leq 0.25$.

**(a)** This formula is the mean-variance optimal weight from Chapter 8. Derive it starting from the investor's objective: $\max_w \; w \cdot \hat{\mu} - \frac{\gamma}{2} w^2 \cdot RV$. Take the first-order condition and solve for $w^*$.

**(b)** The team caps |w| ≤ 0.25. In the language of Chapter 11, this is a bet-sizing heuristic that addresses estimation risk. Explain: if the estimated $\hat{\mu}$ is very noisy, what could go wrong with the uncapped optimal weight? Why is this cap analogous to shrinkage? Name one other bet-sizing approach from the course and explain how it handles the same problem differently.

**(c)** Foundation Capital's strategy had a *pre-fee* Sharpe of 1.43 but a *post-fee* Sharpe of −1.03. Using the optimal weight formula from part (a), explain how transaction costs change the effective $\hat{\mu}$ in the formula. If fees consume a fraction $\phi$ of gross expected return, rewrite the optimal weight formula incorporating costs. What does this imply about the relationship between signal strength and the minimum required Sharpe for profitability?

---

### Question 8: Volatility Timing & Momentum (Ch 5, 10)

The Volatility-Managed Momentum team applied the Moreira & Muir (2017) approach to the UMD (momentum) factor. Their managed strategy sets:

$$w_t = \min\left(\frac{c}{\hat{\sigma}^2_{t-1}},\; 2\right) $$

where $\hat{\sigma}^2_{t-1}$ is the trailing 21-day realized variance of UMD returns, and the weight is capped at 2×.

**(a)** In February 2009 (just before the momentum crash), momentum's trailing realized volatility was low — suppose annualized RV was about 10%. In March 2009, momentum crashed and RV spiked to 80%. If $c$ is calibrated so that average weight equals 1 (i.e., $c \approx$ long-run variance ≈ 0.015), compute the weight the strategy assigns in March 2009 (using February's RV) and in April 2009 (using March's RV).

**(b)** The strategy was heavily loaded going into the 2009 crash. Yet over the full year of 2009, the managed strategy lost only −4.4% vs raw momentum's −53%. How is this possible if the weight was high at the start of the crash? (Hint: think about what happens in the months *after* the initial crash.)

**(c)** The team reported that their strategy's Sharpe ratio improvement over raw momentum was much smaller in the 2013–2024 period (a prolonged low-volatility environment). Explain why volatility timing adds less value when volatility is persistently low. Connect this to the key insight from Chapter 5: what is it about volatility (compared to expected returns) that makes it forecastable, and under what conditions does that forecastability stop helping?

---

### Question 9: Performance Evaluation & Overfitting (Ch 12)

The Athena (Earnings Sentiment) strategy reported the following out-of-sample results over 24 quarterly observations (2019–2024):

| Metric | Value |
|--------|-------|
| Annualized L/S Return | 6.51% |
| Annualized L/S Volatility | 11.2% |
| CAPM Alpha (ann.) | 8.28%, t = 1.76 |
| FF4 Alpha (ann.) | 4.57%, t = 0.99 |
| Momentum β | 0.71, t = 1.93 |
| Fraction-to-half | 12.5% (3 of 24 quarters) |

**(a)** Looking at this table, what is the single most important number for deciding whether to allocate capital to this strategy? Explain your reasoning and the threshold you would use.

**(b)** The strategy uses Claude (an LLM) to score earnings transcripts. Claude was trained on data that includes the 2019–2024 period — the same period used for backtesting. Explain precisely why this is a form of look-ahead bias. How is this different from the standard "using future data" look-ahead bias we discussed in class? Is it more or less concerning?

**(c)** Suppose you wanted to determine whether this strategy has real alpha or is just repackaged momentum. Using the data in the table, construct an argument for each side. What single additional analysis would be most informative in settling the question?

---

### Question 10: Conceptual Multiple Choice (All Chapters)

*Choose the best answer for each.*

**(1)** A stock has β = 0.8 with respect to the market. According to the CAPM (where α = 0 for all stocks), an investor who believes the market will return 10% this year (risk-free rate = 4%) should expect this stock to return:

- (A) 10.0%
- (B) 8.8%
- (C) 4.8%
- (D) 8.0%
- (E) 12.8%

**(2)** The Interest Coverage team found that their strategy worked well in Energy, Finance, and Pharma but had a −97% max drawdown in Technology. The most likely explanation is:

- (A) The Technology sector is too efficient for factor strategies to work
- (B) In Technology, financially distressed (low interest coverage) firms are often high-growth companies that outperform during bull markets — the signal's economic logic reverses in growth-dominated sectors
- (C) The team's data for Technology stocks had errors
- (D) Interest coverage is only valid for capital-intensive industries
- (E) The short leg was too concentrated in a few names

**(3)** A factor model estimates Σ = BΣ_FB' + Σ_ε for 1,000 stocks using 5 factors. Approximately how many parameters does this require, compared to the full sample covariance matrix?

- (A) About the same (both ≈ 500,000)
- (B) The factor model uses about 6,000 vs. 500,000 for full Σ — roughly a 100× reduction
- (C) The factor model uses about 50,000 — a 10× reduction
- (D) The factor model uses more because it also needs factor covariances
- (E) Both require exactly N² parameters

**(4)** You hold a hedged portfolio with AR = 0.6. The market Sharpe ratio is 0.46. If you optimally combine your hedged alpha with the market, what is the combined Sharpe ratio?

- (A) 0.46 + 0.60 = 1.06
- (B) √(0.46² + 0.60²) ≈ 0.76
- (C) max(0.46, 0.60) = 0.60
- (D) (0.46 + 0.60) / 2 = 0.53
- (E) 0.46 × 0.60 = 0.28

**(5)** The Macro Risk-Managed team's volatility-targeting strategy improved the S&P 500's Sharpe ratio from 0.45 to 0.48 over 35 years. This result most likely means:

- (A) Volatility timing does not work for equity markets
- (B) The improvement is economically small and probably not statistically significant over this sample — you would need to test whether 0.03 exceeds the estimation error in the Sharpe ratio
- (C) The strategy would work better with daily rebalancing
- (D) Volatility targeting only works for factor portfolios, not the aggregate market
- (E) The strategy failed because it generated no CAPM alpha

