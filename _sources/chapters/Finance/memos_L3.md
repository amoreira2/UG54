# Memos to grade — L3_Sorts_AI

Score each 0–5 against the rubric, then paste the scores into the 'Grades_L3' tab.

## Rubric

```
You are grading a week-3 memo to a portfolio manager. Students have seen
returns, Sharpe, portfolio weights, and sorts. They have NOT seen factor
models, alpha, beta, NYSE breakpoints, or multiple-testing corrections.

THE TASK: each student picked ONE signal from a menu of 30 published
predictors and sorted on it the lecture's way (signal lagged one month, ten
equal-count deciles within each month, D10 - D1, 1980-2000). They built the
long-short twice, equal-weighted and value-weighted by last month's market cap,
and computed the average lagged signal in each decile. The memo is at most six
sentences to a PM about their signal. Their numbers are in the token; you may
not see them, so grade the reasoning, not the values.

WHAT A GOOD MEMO DOES:
- Says whether the signal works and UNDER WHICH WEIGHTING. Many signals are much
  stronger equal-weighted than value-weighted (accruals, asset growth, debt
  issuance, short-term reversal, illiquidity); some are the reverse (momentum,
  volatility). Either is fine; not saying is not.
- EXPLAINS the EW/VW gap by what the weighting does: equal weights let the many
  small stocks dominate, value weights put the money in the large ones. A signal
  that works only equal-weighted mostly lives in small, costly-to-trade stocks.
- READS THE SIGNAL CHART: the extreme deciles hold the tails of the signal, so
  D1 and D10 usually sit far from their neighbours while the middle deciles are
  bunched together. A student who notices this and connects it to where the
  return spread comes from deserves credit.
- COMPARES THE SHAPES: the signal rises across deciles by construction; does the
  return? A monotone return staircase is stronger evidence than a gap between
  two extremes with a flat middle.

Grade 0-5:
  5 = Commits to an answer and names the weighting; explains the EW/VW gap by
      which stocks drive each; says something specific about the signal chart
      and compares it with the return chart.
  4 = All of that but one element is thin (usually the signal chart).
  3 = Commits and explains EW vs VW, but ignores the signal chart or the shape.
  2 = Reports both numbers without committing, or commits with no reason.
  1 = Restates numbers.
  0 = Empty or off-topic.

A negative or null result reported honestly can score 5. Do not reward claims
of "alpha" or "abnormal returns": they have not been taught what those require.

For picked_fund return "neither" (not applicable).
For cited_appraisal_or_alpha return True if the memo explains the EW/VW gap by
firm size or by which stocks drive each weighting, else False.
```

---

## [0] Onat Safak  <os2325@nyu.edu>

Gross profitability works over 1980-2000: the equal-weighted D10-D1 earns
+11.7%/yr with a t of 3.3, and it survives value-weighting at +8.5%/yr with a
t of 2.3, so the result is not purely a microcap artifact. The two weightings
differ because the equal-weighted version leans on the short leg's small,
unprofitable firms -- D1 holds the smallest stocks in the sort (median cap
about $28m, under 3% of total market value) at +9.9%/yr, and value-weighting
hands that leg to its few large names instead, lifting it to +12.6%/yr and
shrinking the spread. The signal chart is badly uneven: deciles 2 through 9
drift from 0.11 to 0.66, while D1 sits at -0.11 and D10 jumps to 0.98, so the
two extreme buckets are far further from their neighbours than the interior
buckets are from each other. The return chart is the opposite shape -- an
almost perfectly monotone staircase from 9.9% to 21.6%, with every decile
beating the one below it. That mismatch is the encouraging part: returns climb
steadily through the middle of the sort where the signal itself barely moves,
which looks like a broad relationship rather than something driven only by the
tails. I would trade this at modest size and check it against market and size
exposure before calling any of it alpha.

**Score:** 5/5
**Feedback:** Model answer. The contrast you draw -- returns climb steadily through the middle where the signal barely moves -- is exactly the right read, and the leg-level numbers earn it.
---

## [1] Fang Chen  <fc2274@nyu.edu>

The AssetGrowth signal works well for the 1980 to 2000 data sample with 
equal-weighting (+22.43%/yr, t=6.66). Meanwhile, value-weighting (+6.94%/yr, 
t=2.27) is significantly weaker. This is because asset growth is a stronger
indicator for smaller firms, but value emphasizes large firms. The signal chart 
shows a non-linear distribution, with the bottom decile (D1) having a much more 
negative lagged signal (-1.566) compared to other buckets. The return chart 
corroborates the signal chart, showing a sharp increase in performance between 
D1 and D2.

**Score:** 4/5
**Feedback:** Right on all four counts, but the last step is one clause: you say the return chart 'corroborates' the signal chart without saying what the shared shape is. Name it and this is a 5.
---

## [2] Carina-Ana-Maria Ilie  <ci2106@nyu.edu>

For the 'Size' signal (MY_SIGNAL='Size'), the D10-D1 long-short strategy yields a strong equal-weighted annualized return of +20.77% (t=3.96). However, the value-weighted counterpart achieves a lower +9.28% (t=1.92), suggesting the largest firms do not drive as much of the spread on a value-weighted basis. The average lagged signal chart confirms effective decile sorting, showing a monotonic increase in size from D1 (smallest) to D10 (largest). In contrast, the mean returns across deciles are not perfectly monotonic, with D10 significantly outperforming all other deciles. This indicates that while the signal successfully differentiates firms by size, its return predictability is most pronounced in the largest decile, and the performance is less robust when considering market capitalization weighting.

**Score:** 3/5
**Feedback:** You commit and you read both charts, but the EW/VW gap is only restated, not explained. Say what equal weighting actually does -- thousands of small firms get the same say as the giants -- and why that matters for a size sort in particular.
---

## [3] Julia Huang  <jh9608@stern.nyu.edu>

Our analysis of the `Mom6m` signal from 1980-2000 confirms its efficacy, particularly under value-weighting. The equal-weighted D10-D1 long-short portfolio generated an annualized mean return of +10.92% (t=2.41), replicating the published t-statistic of 2.44 very closely. However, the value-weighted portfolio significantly outperformed, yielding +24.85% (t=4.56). This difference suggests that the momentum effect is stronger among larger, more liquid stocks.

The signal chart shows a strong, almost monotonically increasing, spread of the lagged Mom6m signal across deciles, with D1 averaging -0.4508 and D10 averaging 0.8634. This indicates that our sorting mechanism effectively separates stocks based on the signal.

Comparing the return and signal charts reveals a general positive relationship: higher deciles (with higher average Mom6m) tend to have higher annualized mean returns. The largest return spread occurs between the extremes, reinforcing the effectiveness of the D10-D1 long-short strategy.

**Score:** 4/5
**Feedback:** Good, specific read of the signal chart. The EW/VW sentence states where the effect lives rather than why the weighting changes the answer; the mechanism is which stocks each scheme puts the money in.
---

## [4] Red Xiao  <hx2494@stern.nyu.edu>

The Mom12m signal works strongly under both weighting methods, with an equal-weighted D10-D1 return of 16.48% per year and a value-weighted return of 28.62% per year. 
The stronger value-weighted result suggests that larger firms contribute substantially to the momentum effect rather than the result being driven mainly by small stocks. 
The signal profile rises steadily from D1 to D10, showing clear separation across the deciles. 
The return profile also rises almost monotonically across the deciles, which is consistent with higher past momentum predicting higher future returns. 
Overall, the similarity between the signal and return profiles provides stronger evidence that Mom12m has a systematic relationship with future returns rather than being driven only by the extreme portfolios.

**Score:** 4/5
**Feedback:** Clear commitment, and the closing point about the signal and return profiles agreeing is the right one. The signal chart itself is only 'rises steadily' -- give the D1 and D10 values and say whether the extremes sit apart from the middle.
---

## [5] Benedict Marco Kosasih  <bmk7327@nyu.edu>

The signal somewhat works under equal-weighting, 
although the annualized returns are somehwhat flat (low differences between some deciles).
The results between weightings differ because, I assume, momentum is stronger for smaller-cap stocks because
there is less liquidity.

The 10th decile shows a strong difference between the next decile, 
while the 1st decile has an extreme return only in value-weighting.
The signal also breaks around decile 6-8 for both weightings although the difference, 
in momentum is somewhat consistent in the signal value, which means maybe the signal does not work
when momentum turns positive.

**Score:** 2/5
**Feedback:** Your own numbers say the opposite of your explanation: value-weighted (+24.8%/yr) beat equal-weighted (+10.9%/yr), so this effect is stronger in large stocks, not small illiquid ones. Check the direction before reasoning from it, and keep the signal chart and the return chart separate -- several sentences mix them.
---

## [6] Mitch  <mcc9930@nyu.edu>

The GP signal works well because returns increase steadily from D1 to D10. The equal- and value-weighted results differ because equal weighting gives small stocks more influence, while value weighting gives large stocks more influence. The signal chart shows a clear spread across the ten deciles, with D1 at -0.115 and D10 at 0.976. The return chart has a similar upward shape to the signal chart. Overall, higher GP is associated with higher returns.

**Score:** 3/5
**Feedback:** The mechanism sentence is right, but you never say which weighting won for GP or by how much. The PM needs the verdict, not only the reason the two can differ.
---

## [7] Jin Bu  <jb8412@nyu.edu>

GP works under both weighting schemes, with an equal-weighted D10−D1 return of 11.73% per year (t = 3.30) and a value-weighted return of 8.50% (t = 2.27). The stronger equal-weighted result suggests that smaller stocks are contributing more to the effect, since equal weighting gives them more influence than value weighting does. The signal sort clearly separates firms, with average lagged GP rising from −0.1146 in D1 to 0.9752 in D10, and the extreme deciles appear more separated than the middle portfolios. The return pattern is less smooth than the signal pattern, so returns do not increase perfectly with GP in every decile. Overall, GP has a positive return spread that is strongest when stocks are equally weighted.

**Score:** 5/5
**Feedback:** All four boxes, cleanly: verdict, mechanism, a specific signal chart, and the honest observation that returns are less smooth than the signal.
---

## [8] Samir Ahuja  <sa8725@stern.nyu.edu>

NOA replicates cleanly on 1980-2000: equal-weighted D10-D1 earns +19.96%/yr
(t = 7.61) against the authors' published 8.45, and the effect survives
value-weighting at +10.35%/yr (t = 3.48). The spread halves under
value-weighting because it is driven by the short leg among small firms: the
bottom decile earns only 1.78% equal-weighted but 9.12% value-weighted, so
small high-NOA firms underperform far more than large ones, and equal-weighting
loads on exactly the names that are hardest and most expensive to borrow. The
signal chart is a hockey stick rather than a staircase: deciles 2 through 10
sit in a tight band from -0.88 to +0.07, stepping about 0.10 apart, while
decile 1 falls to -1.54, roughly eight normal steps below decile 2. The return
chart has the opposite shape, a near-perfect monotone climb from 1.8% to 21.8%
with only D8 and D9 out of order. So returns track the rank of NOA rather than
its level, which is reassuring for the signal but means decile 1 is a tail of
extreme accrual firms rather than a tenth of the distribution. I would trade
this value-weighted and size the short leg conservatively.

**Score:** 5/5
**Feedback:** 'Hockey stick rather than a staircase', plus the conclusion that returns track the rank of NOA rather than its level -- that is the whole exercise in one sentence.
---

## [9] Alex Kong  <ak11478@stern.nyu.edu>

To the PM:

The 'Mom6m' signal effectively predicts returns, performing strongly, especially under value-weighting. The equal-weighted portfolio yielded +10.92%/yr (t=+2.41), while the value-weighted delivered a significantly higher +24.85%/yr (t=+4.56). This difference indicates that larger-cap stocks with high momentum contribute substantially to the premium, driving the stronger value-weighted performance. The signal chart demonstrates excellent sorting, with extreme deciles (D1 at -0.4508 and D10 at 0.8634) being far apart and a clear, non-even spread, showing pronounced jumps in the higher deciles. Both equal- and value-weighted return charts exhibit a similar monotonic upward trend, mirroring the signal's distribution, with the value-weighted chart showing an even more pronounced return increase in the top deciles.

**Score:** 4/5
**Feedback:** The memo is sound and the numbers you quote inside it are the right Mom6m ones. The four values in your submission cell are not: they are from a GP run. See the note on your numeric score.
---

## [10] Diane Soulan  <das9789@nyu.edu>

ResidualMomentum works under both weighting schemes, but it is stronger equal-weighted: D10 - D1 earns 14.09% per year with a t-stat of 5.66, versus 10.07% and a t-stat of 3.28 value-weighted. The weaker value-weighted result suggests that smaller firms, which receive relatively more weight in the equal-weighted portfolio, contribute more strongly to the signal, although the effect remains present among larger firms. The sort clearly separates firms on ResidualMomentum, with the average lagged signal rising from -0.6543 in D1 to 0.5037 in D10. The signal increases monotonically across the deciles, but the extreme portfolios, especially D1 and D10, are noticeably farther from their neighboring deciles than the middle portfolios are from one another. Mean returns also rise nearly monotonically from D1 to D10, showing that higher ResidualMomentum is associated with higher subsequent returns across most of the distribution rather than only at the endpoints. The return profile is smoother and more nearly linear than the signal profile, indicating that the extreme signal values translate into higher returns without the return spread being driven solely by the extreme deciles.

**Score:** 5/5
**Feedback:** Strong throughout, and the closing contrast -- the return profile smoother and more linear than the signal profile -- is exactly what this question is after.
---

## [11] Aayush Srinivas  <as19258@stern.nyu.edu>

Momentum works. Buying the biggest past winners and shorting the biggest
past losers made +16.5%/yr equal-weighted and +28.6%/yr value-weighted from
1980-2000, both solid t-stats (3.4 and 5.1). Value-weighted did better
mainly because the losers we shorted did much worse when we weighted by
size (-6.0%/yr) than when we weighted every stock the same (+7.9%/yr), so
it's a couple big losers dragging things down, not a pile of tiny illiquid
ones. Looking at the signal itself, most deciles are close together and
only the very top decile (the biggest winners) stands far apart from the
rest. Returns don't show that same jump at the top, instead they climb pretty
steadily across all ten deciles - which is a good sign the result isn't
just one weird bucket skewing everything. Overall I'd trade this
value-weighted, since that's both the bigger spread and the one built from
stocks we could actually trade.

**Score:** 5/5
**Feedback:** Best diagnosis in the class. You traced the value-weighted edge to the short leg and then checked whether it was a few big losers or a pile of microcaps, which is the question that decides whether it is tradable.
---

## [12] Philip Matchev  <pkm5810@stern.nyu.edu>

GP (gross profitability) shows a positive spread in both weighting schemes,
but it is far stronger and more statistically reliable equal-weighted
(t ~ 3.3) than value-weighted (t ~ 2.3). This gap says small stocks are
doing most of the work: once the biggest names dominate the value-weighted
average, the effect fades. The signal chart shows GP is fairly evenly
spread across the middle deciles, with the two extreme deciles pulling
further away from the pack, so most of the identifying variation really
does sit at the tails. That matches the shape of the return chart, which
also rises mostly steadily with a bigger jump into the top decile,
consistent with the signal doing real work at the top rather than the
spread being driven by one noisy bucket. Overall I'd size this bet modestly
and monitor the value-weighted leg specifically, since that's where the
edge is weakest.

**Score:** 5/5
**Feedback:** Commits, explains, reads both charts, and ends with what you would actually do about it. Well judged.
---

## [13] Dennis Petushkov  <dap9805@stern.nyu.edu>

RealizedVol works, but only value weighted: the equal weighted D10 minus D1
spread is a weak, insignificant 6.25% per year (t = 0.98), while the value
weighted spread is a strong 27.82% per year (t = 4.13). The gap comes down to
which stocks dominate each portfolio, equal weighting gives the same say to
thousands of tiny, illiquid high volatility names whose noisy returns wash out
the pattern, while value weighting concentrates the portfolio in the largest,
most liquid names in each decile, where the volatility to return relationship
comes through cleanly. The signal chart shows the opposite of an even spread,
decile 1 sits far below the rest around negative 0.10 while deciles 2 through
10 are all bunched close together near zero, so almost all the separation
comes from one extreme low decile rather than a smooth gradient. That lopsided
signal shape matches the return chart too, which is not monotonic, equal
weighted returns climb from decile 0 to a peak around decile 6 then fall back
through deciles 8 and 9, so decile 10 isn't even the worst performing decile.
If this signal is ever traded, the value weighted version is the one worth
using, since that's where the real, statistically significant effect actually
lives.

**Score:** 5/5
**Feedback:** Good: you commit to value-weighted only, and the reason equal weighting washes out a volatility sort is right. Watch the decile labels -- you switch between 'decile 0' and 'decile 10' mid-sentence.
---

## [14] haoyu Huangfu  <hh3170@nyu.edu>

The momentum strategy earns an annualized average return of 16.48% with equal weights (t = 3.44).
With value weights, the return is higher at 28.62% (t = 5.14).
Value weighting gives larger stocks more weight, and the higher spread mainly comes from the low-momentum group performing worse.
Average past returns range from −58.39% in D1 to 150.73% in D10, with D10 far above the other groups.
Future returns generally increase with momentum, but they do not rise steadily across every group.
These results support momentum in this sample, but they do not account for trading costs or differences in risk.

**Score:** 5/5
**Feedback:** Terse and entirely substantive. The low-momentum leg doing worse under value weighting is the right explanation for the gap, and the caveat about costs and risk is well placed.
---

## [15] Aiden Li  <al8793@stern.nyu.edu>

1. The GP signal produces an annualized EW long-short return of 11.73% (t=3.30) and a VW return of 8.50% (t=2.27).
2. The difference between EW and VW results suggests that the signal's predictive power is stronger in smaller-cap stocks than in larger firms.
3. Decile 1 has an average lagged signal of -0.1146, while Decile 10 reaches 0.9752.
4. The signal spread demonstrates how extreme values are distributed across the sorted buckets.
5. Evaluating both weighting schemes provides a complete picture of the signal's real-world tradeability.

**Score:** 3/5
**Feedback:** Points 1-3 are fine, but 4 and 5 say nothing -- 'demonstrates how extreme values are distributed' is not a finding. You never compare the return chart with the signal chart, which is half of what was asked.
---

## [16] Kyle Chan   <hc4427@stern.nyu.edu>

Gross profitability (GP, Novy-Marx 2013) works in our 1980-2000 sample under both weightings: the D10 - D1 spread is +11.7%/yr (t = 3.30) equal-weighted and +8.5%/yr (t = 2.27) value-weighted, both above the published t of 2.49 and with both legs contributing (the long leg earns about 21%/yr under either weighting, the short leg 10-13%).
The equal-weighted spread is larger mainly because the short leg is worse: equal-weighting lets the many small, low-profitability firms in D1 dominate that leg (9.9%/yr), whereas value-weighting is driven by the large firms, whose unprofitable decile still earns 12.6%/yr, so the value-weighted result is the more tradable and the one to trust.
The signal chart is not evenly spaced: deciles 2 through 9 rise in small steps (0.11 to 0.66), but the two extremes sit far from the rest, with D1 the only decile with negative gross profits (-0.11) and D10 roughly 50% above D9 (0.98).
The return chart has the same shape, a near-monotone staircase with the biggest jump at D10, so the extreme deciles carry a disproportionate share of both the signal and the return, which is exactly where the sort concentrates its bet.

**Score:** 5/5
**Feedback:** Excellent. The leg-level numbers do real work, and noticing that D1 is the only decile with negative gross profits is the kind of detail that makes a sort interpretable.
---

## [17] Krittrin Olarnrak  <ko2324@nyu.edu>

Our GP signal works robustly under both weightings, delivering a strong annualized equal-weighted spread of +11.73% (t = +3.30) and a solid value-weighted spread of +8.50% (t = +2.27). The stronger performance under equal-weighting indicates that smaller firms, which dominate that scheme, are driving a larger portion of the anomaly's returns compared to large-cap stocks. The signal chart reveals a highly linear and symmetric distribution across the middle deciles, but displays noticeably wider gaps at the extreme tails (D1 and D10). While the underlying characteristic shows this symmetric dispersion, the equal-weighted return chart exhibits a more pronounced, monotonic upward trajectory, confirming that our sorting framework successfully captures a consistent return premium as profitability increases.

**Score:** 4/5
**Feedback:** All four elements are present, but the language outruns the evidence: 'highly linear and symmetric' is not what a GP decile chart with wide tails looks like. Fewer adjectives, more numbers.
---

## [18] Jai Paradkar  <jp7956@stern.nyu.edu>

GP works under both equal and value weighting: equal-weighted D10-D1 is +11.7%/yr (t=3.30) and value-weighted is +8.5%/yr (t=2.27).
The stronger equal-weighted spread indicates that smaller stocks, which get much more influence under equal weighting, are doing more of the work.
The signal rises across deciles, with the extreme portfolios noticeably farther apart than the typical middle-decile step.
Returns are broadly monotone with the signal, so the D10-D1 spread reflects a general cross-sectional pattern rather than only two unusual endpoints.
The original paper used July 1963 to December 2010, while this notebook tests 1980-2000, so this is a partial-sample replication rather than the same experiment.

**Score:** 5/5
**Feedback:** Concise and correct, and flagging that the paper ran 1963-2010 while you ran 1980-2000 is a good instinct -- that makes this a partial-sample replication, which is worth saying out loud.
---

