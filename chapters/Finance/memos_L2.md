# Memos to grade — L2_Portfolios_AI

Score each 0–5 against the rubric, then paste the scores into the 'Grades_L2' tab.

## Rubric

```
You are grading a second-week memo from an undergraduate. They have seen returns,
Sharpe ratios, and portfolio weights. They have NOT seen factor models or beta.

THE QUESTION: they built value-weighted and equal-weighted portfolios from the
same ~6,000 stocks. EW earned 14.20%/yr with 18.6% vol; VW earned 15.73%/yr with
15.5% vol. Why do they differ, which is "the market", and why might the EW
return overstate what was achievable?

GROUND TRUTH:
- There are far more small firms than large ones, so equal weighting puts most
  of its money in small stocks. EW is an unintentional small-cap bet; VW is
  dominated by the largest firms (top 10 = 20.5% of total market cap).
- VW deserves to be called "the market" because it is the only weighting ALL
  investors can hold simultaneously -- it is the aggregate portfolio. There are
  not enough shares of small firms for everyone to equal-weight.
- EW overstates achievable returns because the smallest names are illiquid,
  cannot absorb capital, and would cost far more to trade; EW also requires
  constant rebalancing (selling winners, buying losers) which multiplies costs.
- Bonus insight: EW lost to VW here despite holding riskier stocks, which is
  evidence against a size premium over this window.

Grade 0-5:
  5 = Explains the small-cap tilt from the NUMBER of small firms; argues VW is
      the market on aggregation/market-clearing grounds; gives a concrete
      liquidity/tradability or rebalancing-cost reason EW overstates.
  4 = Gets the small-cap tilt and one of the other two clearly.
  3 = Correct intuition about small vs large driving the gap, but the "which is
      the market" argument is asserted rather than reasoned.
  2 = Notices the portfolios differ without explaining the mechanism.
  1 = Restates the numbers.
  0 = Empty or off-topic.

PENALIZE: claiming EW is riskier ONLY because it has more stocks (it has the
same stocks); saying VW is "the market" purely because that is convention.

For picked_fund return "neither" (not applicable).
For cited_appraisal_or_alpha return True if the memo gives a concrete
tradability, liquidity, or transaction-cost reason, else False.

Output via the `grade_memo` tool.
```

---

## [0] ci2106  <ci2106@nyu.edu>

The equal-weighted and value-weighted portfolios differ because equal weighting gives small companies much more importance than value weighting does. 
Small companies tend to have larger price swings, which helps explain why the equal-weighted portfolio was more volatile and, during this period, earned a lower return.
The value-weighted portfolio deserves to be called “the market” because companies are weighted according to their actual market value, so it better represents how investors’ money is distributed across the market.
The equal-weighted return may also be unrealistic because keeping thousands of stocks equally weighted requires frequent buying and selling.
Those trades, especially in small stocks, can have significant transaction costs that reduce the return an investor actually earns.

**Score:** 4/5
**Feedback:** Clear on the small-cap tilt and on rebalancing costs. 'Weighted by actual market value' describes the value-weighted portfolio rather than arguing for it: the case is that it is the one portfolio all investors can hold at the same time.

---

## [1] Carina Ilie  <ci2106@nyu.edu>

The equal-weighted and value-weighted portfolios differ because equal weighting gives small companies much more importance than value weighting does. 
Small companies tend to have larger price swings, which helps explain why the equal-weighted portfolio was more volatile and, during this period, earned a lower return.
The value-weighted portfolio deserves to be called “the market” because companies are weighted according to their actual market value, so it better represents how investors’ money is distributed across the market.
The equal-weighted return may also be unrealistic because keeping thousands of stocks equally weighted requires frequent buying and selling.
Those trades, especially in small stocks, can have significant transaction costs that reduce the return an investor actually earns.

**Score:** 4/5
**Feedback:** Clear on the small-cap tilt and on rebalancing costs. 'Weighted by actual market value' describes the value-weighted portfolio rather than arguing for it: the case is that it is the one portfolio all investors can hold at the same time.

---

## [2] Aayush Srinivas  <as19258@stern.nyu.edu>

The equal-weighted (EW) portfolio's overweighting of small stocks resulted in higher volatility and lower returns compared to the value-weighted (VW) portfolio. The VW portfolio, based on market capitalization, is better described as 'the market' because it's the only weighting scheme all investors can hold and is naturally rebalancing. The EW return might overstate what investors can actually earn due to the illiquidity and high transaction costs associated with trading many small-cap stocks at scale. Despite expectations of a small-cap premium, our analysis showed EW underperforming VW. This suggests the small-cap premium does not always exist or easily captured by simple equal-weighting.

**Score:** 5/5
**Feedback:** All three parts: the small-stock tilt, the only weighting all investors can hold, and illiquidity costs, plus a sharp point about the size premium.

---

## [3] Red Xiao  <hx2494@stern.nyu.edu>

The two portfolios differ so much because equal weighting gives much more relative weight to small companies, while value weighting allocates capital according to each company's market capitalization. 
In our sample, this higher weighting toward small-cap stocks resulted in a lower return and higher volatility for the equal-weighted portfolio. 
I think the value-weighted portfolio better represents the market because it can reflect the actual market value of all companies and is a portfolio that all investors could collectively hold. 
The equal-weighted return may also overstate what an investor could actually earn since frequently trading small and illiquid stocks can create substantial transaction costs.

**Score:** 5/5
**Feedback:** All three parts, cleanly: the small-cap tilt, a portfolio all investors can hold together, and trading costs in illiquid stocks.

---

## [4] Jai Paradkar  <jp7956@stern.nyu.edu>

The Value-Weighted (VW) portfolio represents 'the market' because it reflects the aggregate wealth of all investors and requires no rebalancing as prices move. Equal-Weighting (EW) is an implicit bet on small-cap stocks, which proved detrimental during the 1980-2000 period where EW underperformed VW while carrying significantly higher volatility. The EW portfolio is difficult to trade at scale because it requires building massive positions in illiquid, small companies, which would lead to high transaction costs not captured in these returns. Thus, VW is the more accurate benchmark for market performance.

**Score:** 5/5
**Feedback:** Complete: aggregate wealth and no rebalancing for value weights, the implicit small-cap bet, and the cost of building positions in illiquid names.

---

## [5] Katherine Graci  <ksg7758@nyu.edu>

One reason the two differ so much is because equal weighting requires investors to sell winners and buy losers every month, while value-weighting is "free" to maintain. Equal weighted also holds more volatility because it doesn't hold more of the "good" stocks proportionally speaking. I think that value weighting deserves to be called the market because it proportionally matches the companies' market caps, which make up the market's overall market cap. Also, equal weighting returns might be overstated because investors have to pay fees when selling and buying stocks, which can add up when equal weighting investors do that often

**Score:** 3/5
**Feedback:** The trading-cost point is right, but the main reason the two differ is missing: most stocks are small, so equal weights are mostly a small-cap bet. 'Matches market caps' describes value weights; the argument is that they are what all investors hold together.

---

## [6] Dennis Petushkov  <dap9805@stern.nyu.edu>

The equal weighted portfolio underperformed the value weighted one with more
volatility because equal weighting puts the same dollars into thousands of
small, more volatile companies that barely register in the real market, while
value weighting mirrors how capital is genuinely distributed across firms.
Value weighting has the better claim to being called the market, since it is
the only portfolio every investor could hold at once, if one investor buys
more of a small stock someone else must hold less, and value weights already
reflect that balance. Equal weighting is really an unintentional small stock
tilt rather than broad diversification, which is also why its extra volatility
does not come with extra reward here. One reason the equal weighted return
likely overstates what a real investor could earn is that holding every stock
at the same dollar weight for 252 months requires constant rebalancing, and
small stocks trade thinly enough that the price impact and costs of that
rebalancing would eat into the return in practice.

**Score:** 5/5
**Feedback:** Complete: the unintended small-stock tilt, why value weights are the only portfolio everyone can hold at once, and thin trading making rebalancing costly.

---

## [7] Mitch Cahill  <mcc9930@nyu.edu>

The equal-weighted portfolio puts the same amount of money into every stock, giving much more weight to small stocks, while the value-weighted portfolio gives the largest companies much more influence. Small stocks tend to be more volatile, which helps explain why the equal-weighted portfolio had higher volatility and a different return. The value-weighted portfolio deserves to be called "the market" because it represents the aggregate portfolio of all investors, with each company weighted according to its actual market capitalization. The equal-weighted portfolio is instead a particular investment strategy that requires regularly buying and selling to maintain equal weights. Its return may overstate what an investor could actually earn because frequent rebalancing creates transaction costs, especially when trading many small and illiquid stocks.

**Score:** 5/5
**Feedback:** Complete: small-stock weight, the aggregate portfolio of all investors, and rebalancing costs in illiquid stocks.

---

## [8] Julia Huang  <jh9608@stern.nyu.edu>

The equal-weighted (EW) portfolio's higher volatility and lower returns compared to the value-weighted (VW) portfolio stem from its inherent bias towards smaller, riskier stocks. The VW portfolio, being proportional to company size, more accurately represents "the market" as it reflects the aggregate investment choices of all participants and rebalances naturally. EW returns can overstate real-world earnings because holding equal dollar amounts in tiny, illiquid stocks is practically unfeasible for large-scale investors, leading to high transaction costs and difficulty in execution.

**Score:** 5/5
**Feedback:** Complete and concise: the small-stock bias, aggregate holdings that rebalance themselves, and trading at scale in tiny illiquid stocks.

---

## [9] Alex Kong  <ak11478@stern.nyu.edu>

Self answer: To answer the puzzle of ew earning less with more volatility. The higher volatility can be attributed to more money 
being pooled into smaller-cap stocks. Historically, these stocks have been riskier and more volatile. To compensate, they are supposed 
to yield higher returns, but it's possible that this compensation did not hold up over the years in which the market portfolio was 
constructed on. On the other hand, the vw stocks have less money pooled into majority small-caps, and is most likely more spread out
 among large-caps. This is why the volatility is lower, since larger stocks tend to be less volatile. Although they are less risky than 
 small-caps, it seems like they have provided better returns than the riskier small-caps. For why large-caps have been doing better than
  small-caps, one reason I can come up with is the extreme inflow of investor money in stocks related to AI. Due to the AI wave, 
  investors are pooling massive amounts of money into AI. The companies which invest the heaviest in AI are the large-cap stocks 
  like Nvidia, Apple, etc, that have the capital to take on such large scale infrastructure projects. As a result, investors are 
  pooling more and more money into the large-cap stocks, rather than smaller stocks, since the smaller stocks do not have the 
  capital to compete with these larger stocks. I believe that "vw" is more "the market" than "ew." A large portion of the market is comprised
  of the magnificent 7 stocks, which are all either tech / chip / AI stocks. EW naturally owns a higher % of smaller-cap stocks rather
  than the larger stocks, since equal amounts of money are allocated across all stocks, which VW puts an equal percentage into each stock. 
  The qual-weighted return might overstate the actual return investors could've earned. For why ew overstates returns is because of many reasons.
  First, for very small stocks, investing a large amount of money at once may not be possible. Investing in small increments could cause prices 
  to move against the investor, resulting in them buying higher than they desired. Furthermore, there are liquidity issues with these smaller
  stocks that makes the constant buying and selling required for an ew method to work extremely costly.

**Score:** 3/5
**Feedback:** The small-cap tilt and the price-impact point are good. But the sample is 1980-2000, so AI stocks and the Magnificent 7 cannot explain it, and value weighting does not put an equal percentage in each stock. Also well over the five-sentence limit.

---

## [10] Aiden Li  <al8793@stern.nyu.edu>

The two differ so much because of massively market equity is skewed. The top 10 companies hold 19% of the total weighted market cap, whilt here are over 6000 companies we are looking at. 
The difference comes from if we put equal weighting in an extremely small cap company, they are more likely to volatile which can skew results more and its essentially taking a gamble, overstating what an investor could actually have earned.
Therefore, i think the weighted portfolio deserves to be called the market because it is where most of the money lies anyways (in market cap) anyways.

**Score:** 3/5
**Feedback:** Good use of the concentration number. But higher volatility is not why equal weights overstate what you could earn -- that is trading costs in small, illiquid stocks -- and 'where most of the money lies' needs the aggregation argument behind it.

---

## [11] Diane Soulan  <das9789@nyu.edu>

Although both portfolios hold the same stocks, their weights create very different exposures: equal-weighting gives much more influence to small firms, while value-weighting concentrates capital in the largest companies, with the top 10 stocks representing 20.5% of total market capitalization in the final month. In our sample, the equal-weighted portfolio earned 14.22% per year with 18.56% volatility, compared with 15.74% and 15.53% for the value-weighted portfolio. The value-weighted portfolio deserves to be called the market because it reflects how aggregate investor wealth is actually distributed across stocks, including the market's real concentration in real firms. Equal-weighted returns may overstate what an investor could actually earn because maintaining equal weights requires frequent rebalancing, especially in small and less liquid stocks, creating transaction costs and market impact that the backtest ignores.

**Score:** 5/5
**Feedback:** Complete: the small-firm tilt with the concentration number, how aggregate investor wealth is distributed, and rebalancing and market-impact costs.

---

## [12] Philip Matchev  <pkm5810@stern.nyu.edu>

The two portfolios differ because value-weighting lets a handful of giant
firms like GE dominate the return, while equal-weighting gives a company
worth a few million dollars the same vote as one worth billions — and
because there are far more small firms than large ones, equal-weighting is
effectively a concentrated bet on small stocks. Value-weighting deserves the
name "the market" because it is the only portfolio every investor could hold
at once without anyone's trade needing a counterparty; equal-weighting is
not something the market as a whole can be in. The equal-weighted return
also overstates what an investor could actually have earned, because
matching the same dollar weight in the smallest, most illiquid stocks as
in GE requires trading thinly-traded shares at a scale the market can't
actually absorb without moving the price against you.

**Score:** 5/5
**Feedback:** Complete, and says outright that the tilt comes from there being far more small firms than large ones.

---

## [13] Haoyu Huangfu  <hh3170@nyu.edu>

Equal weighting gives small stocks more weight than value weighting does.
In this sample, that small-stock exposure produced lower returns and higher volatility.
The value-weighted portfolio better represents the market because each stock is weighted by its share of total market value.
Equal weighting requires regular rebalancing, often in small and illiquid stocks.
Transaction costs and market impact would reduce the returns an investor could actually earn.

**Score:** 4/5
**Feedback:** Tilt and trading costs are right. 'Weighted by its share of total market value' describes value weights; the argument for them is that they are the one portfolio all investors can hold at once.

---

## [14] Jai Paradkar  <jp7956@stern.nyu.edu>

The two portfolios differ because equal-weighting gives every stock the same weight, which puts much more exposure on small, volatile companies, while value-weighting puts more weight on large firms. Value-weighting deserves to be called the market because the weights reflect each company's actual share of total market capitalization and can be held by investors in aggregate. In this sample, equal-weighting earned less while taking more risk. Its return can also overstate what an investor could actually earn because many of the smallest stocks are illiquid and costly to trade in the amounts needed for constant rebalancing.

**Score:** 5/5
**Feedback:** Complete: small-cap exposure, a portfolio investors can hold in aggregate, and costly rebalancing in illiquid stocks.

---

## [15] Krittrin Olarnrak  <ko2324@nyu.edu>

The two portfolios differ because value-weighting puts more capital in large firms, while equal-weighting gives the same weight to every stock and therefore creates a strong small-cap tilt. Over this sample, that small-cap tilt produced lower average returns and higher volatility than the value-weighted portfolio. The value-weighted portfolio deserves to be called the market because its weights match each firm's share of total market capitalization and, unlike equal-weighting, it is a portfolio all investors can collectively hold. Equal-weighted returns can overstate what an investor could actually earn because maintaining equal weights requires frequent rebalancing and large relative trades in small, illiquid stocks, creating transaction costs and market-impact problems.

**Score:** 5/5
**Feedback:** Complete: the small-cap tilt, a portfolio all investors can collectively hold, and rebalancing and market-impact costs.

---

