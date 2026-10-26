"""
Figures and numbers for slides/backtesting_intuition.tex

    python slides/backtesting_intuition_figures.py

Data: Ken French's 49 industry portfolios (daily) and the market factor, the
same data as chapters/Not used/Evaluatinghedgeportfolios.ipynb. Downloaded each
run, so it needs an internet connection.

THE MAIN EXPERIMENT. At the end of each year, regress every industry on the
market using the last THREE calendar years of daily returns:
    excess return = alpha + beta * market + residual
Then ask what that alpha, beta and residual volatility say about the NEXT year.

THE APPENDIX repeats it with a ONE-year look-back, for industries and for the
500 largest stocks, and asks why less data gives a better result. The stock numbers come from
slides/stock_years.parquet, written by pull_stock_years.py (needs WRDS).

Figures go to slides/figures/ as PDF; the numbers the slides quote are printed
at the end.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pandas_datareader.data as web
import statsmodels.api as sm

HERE = Path(__file__).resolve().parent
OUT = HERE / "figures"
OUT.mkdir(exist_ok=True)

GREY, RED, BLUE = "#6B6B6B", "#B03A2E", "#2E5C8A"
plt.rcParams.update({
    "font.size": 13, "axes.titlesize": 14, "axes.labelsize": 13,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": False, "figure.dpi": 150, "savefig.bbox": "tight",
})
LOOKBACK = 3            # calendar years in the estimation window

# ---------------------------------------------------------------- data
ind = web.DataReader("49_Industry_Portfolios_daily", "famafrench", start="1926-01-01")[0]
ind = ind.replace([-99.99, -999], np.nan) / 100                      # French's missing codes
ffd = web.DataReader("F-F_Research_Data_Factors_daily", "famafrench", start="1926-01-01")[0] / 100
ffm = web.DataReader("F-F_Research_Data_Factors", "famafrench", start="1926-01-01")[0] / 100

daily = ind.join(ffd[["Mkt-RF", "RF"]], how="inner")
industries = list(ind.columns)
year_of = daily.index.year
all_years = sorted(set(year_of))

# ---------------------------------------------------------------- regressions
# One regression per industry on a window of `span` calendar years ending in `year`.
rows = {1: [], LOOKBACK: []}
for span in rows:
    for year in all_years:
        g = daily[(year_of > year - span) & (year_of <= year)]
        days = g.groupby(g.index.year).size()
        if len(days) < span or days.min() < 200:                      # need every year of the window, in full
            continue
        X = sm.add_constant(g["Mkt-RF"])
        for name in industries:
            excess = (g[name] - g["RF"]).dropna()
            if len(excess) < 200 * span:
                continue
            reg = sm.OLS(excess, X.loc[excess.index]).fit()
            rows[span].append({"year": year, "industry": name,
                               "alpha": reg.params["const"] * 252, "se_alpha": reg.bse["const"] * 252,
                               "beta": reg.params["Mkt-RF"],       "se_beta": reg.bse["Mkt-RF"],
                               "ivol": reg.resid.std() * np.sqrt(252)})
one_year   = pd.DataFrame(rows[1])            # what actually happened in each single year
estimates  = pd.DataFrame(rows[LOOKBACK])     # what three years of data told you at the end of `year`

# Is a beta different from the AVERAGE beta that December? (Different from zero is no test at all.)
estimates["beta_avg"] = estimates.groupby("year")["beta"].transform("mean")
estimates["t_beta_vs_avg"] = (estimates["beta"] - estimates["beta_avg"]) / estimates["se_beta"]
estimates["t_alpha"] = estimates["alpha"] / estimates["se_alpha"]
estimates["appraisal"] = estimates["alpha"] / estimates["ivol"]              # alpha per unit of its own risk, annual

# The same three-year windows again, but sampled MONTHLY: 36 observations instead of about 756.
month_of = daily.index.to_period("M")
monthly = (1 + daily[industries]).groupby(month_of).prod() - 1                 # compound the days in each month
monthly[daily[industries].isna().groupby(month_of).any()] = np.nan             # a month with a missing day is missing
monthly["RF"] = (1 + daily["RF"]).groupby(month_of).prod() - 1
monthly["Mkt-RF"] = (1 + daily["Mkt-RF"] + daily["RF"]).groupby(month_of).prod() - 1 - monthly["RF"]

rows_monthly = []
for year, name in zip(estimates["year"], estimates["industry"]):               # exactly the windows used above
    g = monthly[(monthly.index.year > year - LOOKBACK) & (monthly.index.year <= year)]
    excess = (g[name] - g["RF"]).dropna()
    if len(excess) < 12 * LOOKBACK:
        continue
    reg = sm.OLS(excess, sm.add_constant(g.loc[excess.index, "Mkt-RF"])).fit()
    rows_monthly.append({"year": year, "industry": name,
                         "se_alpha": reg.bse["const"] * 12, "se_beta": reg.bse["Mkt-RF"]})
estimates_monthly = pd.DataFrame(rows_monthly)

# the three-year estimate next to what the NEXT year delivered, for the same industry
nxt = one_year.assign(year=one_year["year"] - 1)[["year", "industry", "alpha", "beta", "ivol"]]
pairs = estimates.merge(nxt, on=["year", "industry"], suffixes=("", "_next"))

persistence = {}
for k in ["alpha", "beta", "ivol"]:
    reg = sm.OLS(pairs[k + "_next"], sm.add_constant(pairs[k])).fit()
    persistence[k] = (reg.params["const"], reg.params[k], reg.rsquared)

# ---------------------------------------------------------------- the hedge and the trade
A = estimates.pivot(index="year", columns="industry", values="alpha")
B = estimates.pivot(index="year", columns="industry", values="beta")

hedged_parts, trade_parts, promised = [], [], []            # the main trade: top fifth minus bottom fifth
thirds_parts, thirds_promised = [], []                      # top third minus bottom third, for the appendix table
for year, g in daily.groupby(year_of):
    if (year - 1) not in B.index:
        continue
    beta_est  = B.loc[year - 1].reindex(industries)                      # estimated through LAST December
    alpha_est = A.loc[year - 1].dropna()
    excess = g[industries].sub(g["RF"], axis=0)
    hedged = excess - np.outer(g["Mkt-RF"].values, beta_est.values)      # hedge chosen BEFORE the year starts
    hedged_parts.append(hedged.assign(mkt=g["Mkt-RF"]))

    if len(alpha_est) < 30:
        continue
    # MAIN: buy the best fifth by estimated alpha, short the worst fifth, equal weights (about 10 industries a side)
    top    = alpha_est[alpha_est >= alpha_est.quantile(0.8)].index
    bottom = alpha_est[alpha_est <= alpha_est.quantile(0.2)].index
    promised.append(alpha_est[top].mean() - alpha_est[bottom].mean())    # what the estimation window showed
    trade_parts.append(pd.DataFrame({"trade": hedged[top].mean(axis=1) - hedged[bottom].mean(axis=1)}))

    # APPENDIX: the same with thirds
    top    = alpha_est[alpha_est >= alpha_est.quantile(2 / 3)].index
    bottom = alpha_est[alpha_est <= alpha_est.quantile(1 / 3)].index
    thirds_promised.append(alpha_est[top].mean() - alpha_est[bottom].mean())
    thirds_parts.append(pd.DataFrame({"trade": hedged[top].mean(axis=1) - hedged[bottom].mean(axis=1)}))

hedged_all = pd.concat(hedged_parts)
trade = pd.concat(trade_parts)["trade"].dropna()
trade_by_year = trade.groupby(trade.index.year).mean() * 252             # one return per holding year
trade_ar = trade_by_year.mean() / trade_by_year.std()                    # hedged, so mean = alpha and vol = residual risk
mkt_by_year = daily["Mkt-RF"].groupby(year_of).mean().reindex(trade_by_year.index) * 252
trade_reg = sm.OLS(trade_by_year, sm.add_constant(mkt_by_year)).fit()    # check: is the trade really market-neutral?
thirds = pd.concat(thirds_parts)["trade"].dropna()
thirds_by_year = thirds.groupby(thirds.index.year).mean() * 252

raw_beta, hedged_beta = {}, {}
for name in industries:
    h = hedged_all[name].dropna()
    m = hedged_all.loc[h.index, "mkt"]
    e = daily.loc[h.index, name] - daily.loc[h.index, "RF"]
    raw_beta[name]    = sm.OLS(e, sm.add_constant(m)).fit().params["mkt"]
    hedged_beta[name] = sm.OLS(h, sm.add_constant(m)).fit().params["mkt"]
betas = pd.DataFrame({"raw": raw_beta, "hedged": hedged_beta}).sort_values("raw")

tstat = lambda x: x.mean() / x.std() * np.sqrt(len(x))

# ---------------------------------------------------------------- the market, monthly, 100 years
mkt = ffm["Mkt-RF"]
mkt_mean, mkt_vol = mkt.mean() * 12, mkt.std() * np.sqrt(12)
mkt_sr = mkt_mean / mkt_vol
decades = {f"{d}s": mkt[str(d):str(d + 9)].mean() * 12 for d in range(1930, 2020, 10)}

# ================================================================ APPENDIX: one-year look-back
# Rank on a single year's alpha and hold k years later.
A1 = one_year.pivot(index="year", columns="industry", values="alpha")
B1 = one_year.pivot(index="year", columns="industry", values="beta")
ind_mean = daily[industries].sub(daily["RF"], axis=0).groupby(year_of).mean() * 252      # mean excess return, per year
mkt_year = daily["Mkt-RF"].groupby(year_of).mean() * 252
ind_trade, ind_promised = {}, []
for k in [1, 2, 3]:
    gaps = []
    for year in A1.index:
        alpha_then = A1.loc[year].dropna()
        if (year + k) not in ind_mean.index or len(alpha_then) < 30:
            continue
        top    = alpha_then[alpha_then >= alpha_then.quantile(2 / 3)].index
        bottom = alpha_then[alpha_then <= alpha_then.quantile(1 / 3)].index
        earned = ind_mean.loc[year + k] - B1.loc[year] * mkt_year.loc[year + k]
        gaps.append(earned[top].mean() - earned[bottom].mean())
        if k == 1:
            ind_promised.append(alpha_then[top].mean() - alpha_then[bottom].mean())
    ind_trade[k] = pd.Series(gaps)

# the same on the 500 largest stocks
stocks = pd.read_parquet(HERE / "stock_years.parquet")
stocks = stocks.astype({"permno": int, "year": int, "in_universe": bool})
picked = stocks[stocks["in_universe"] & (stocks["n"] >= 200)]            # the 500 largest, with a full year of data

stock_persistence, stock_trade, stock_promised = {}, {}, {}
for k in [1, 2, 3]:
    later = stocks.assign(year=stocks["year"] - k)[["permno", "year", "n", "alpha", "beta", "ivol", "mean_excess", "mean_mkt"]]
    both  = picked.merge(later, on=["permno", "year"], suffixes=("", "_later"), how="left")
    full  = both[both["n_later"] >= 200]
    for v in ["alpha", "beta", "ivol"]:
        reg = sm.OLS(full[v + "_later"], sm.add_constant(full[v])).fit()
        stock_persistence[(v, k)] = (reg.params["const"], reg.params[v], reg.rsquared)
    if k == 1:
        stock_pairs = full
    gaps, promises = [], []
    for year, g in both.groupby("year"):
        top    = g[g["alpha"] >= g["alpha"].quantile(2 / 3)]
        bottom = g[g["alpha"] <= g["alpha"].quantile(1 / 3)]
        # hedged with the RANKING year's beta, earned k years later; a stock with any data that year counts
        earned = lambda x: (x["mean_excess_later"] - x["beta"] * x["mean_mkt_later"]).dropna().mean()
        gaps.append(earned(top) - earned(bottom)); promises.append(top["alpha"].mean() - bottom["alpha"].mean())
    stock_trade[k] = pd.Series(gaps).dropna(); stock_promised[k] = np.mean(promises)

# ================================================================ figures
pct = lambda v, _: f"{v:.0%}"

# 1. promised vs delivered
fig, ax = plt.subplots(figsize=(8.5, 3.0))
vals = [np.mean(promised), trade.mean() * 252]
ax.barh(["the same trade,\nheld the next year", "alpha gap,\nin the three years you ranked on"], vals[::-1],
        color=[RED, GREY], height=0.55)
for y, v in enumerate(vals[::-1]):
    ax.text(v + 0.004, y, f"{v:.0%} a year", va="center", fontsize=15, fontweight="bold")
ax.set_xlim(0, 0.36); ax.set_xticks([]); ax.spines["bottom"].set_visible(False)
fig.savefig(OUT / "promised_vs_delivered.pdf"); plt.close(fig)

# 2. beta carries over, alpha does not
fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.3))
for ax, k, lim, title, is_pct in [(axes[0], "beta", (0, 2.2), "Beta", False),
                                  (axes[1], "alpha", (-0.6, 0.6), "Alpha, per year", True)]:
    a, b, r2 = persistence[k]
    ax.scatter(pairs[k], pairs[k + "_next"], s=5, color=GREY, alpha=0.25, linewidths=0)
    ax.plot(lim, lim, color="black", linestyle=":", linewidth=1)
    ax.plot(lim, [a + b * lim[0], a + b * lim[1]], color=RED, linewidth=2)
    ax.set_xlim(lim); ax.set_ylim(lim); ax.set_aspect("equal")
    ax.set_xlabel("estimated on the last three years"); ax.set_ylabel("the next year"); ax.set_title(title)
    ax.text(0.05, 0.92, f"slope {b:.2f}   $R^2$ {r2:.2f}", transform=ax.transAxes, color=RED, fontsize=13)
    if is_pct:
        ax.xaxis.set_major_formatter(pct); ax.yaxis.set_major_formatter(pct)
fig.tight_layout(); fig.savefig(OUT / "beta_alpha_persistence.pdf"); plt.close(fig)

# 3. the hedge works out of sample
fig, ax = plt.subplots(figsize=(9.5, 3.9))
x = np.arange(len(betas))
ax.axhline(0, color="black", linewidth=0.8)
ax.scatter(x, betas["raw"], color=GREY, s=34, label="unhedged")
ax.scatter(x, betas["hedged"], color=RED, s=34, label="hedged with the beta estimated beforehand")
ax.set_xticks([]); ax.set_xlabel("49 industries, sorted by beta"); ax.set_ylabel("market beta")
ax.legend(frameon=False, loc="upper left")
fig.savefig(OUT / "hedge_works.pdf"); plt.close(fig)

# 4. the market, decade by decade
fig, ax = plt.subplots(figsize=(9.5, 3.7))
ax.bar(list(decades), list(decades.values()), color=GREY, width=0.65)
ax.plot([-0.5, len(decades) - 0.5], [mkt_mean, mkt_mean], color=RED, linewidth=2)
ax.text(len(decades) - 0.4, mkt_mean, f"100-year\naverage\n{mkt_mean:.1%}", color=RED, ha="left", va="center")
ax.set_xlim(-0.6, len(decades) + 0.9)
ax.axhline(0, color="black", linewidth=0.8)
ax.yaxis.set_major_formatter(pct); ax.set_ylabel("average excess return, per year")
fig.savefig(OUT / "market_decades.pdf"); plt.close(fig)

# 5. volatility carries over like beta
fig, ax = plt.subplots(figsize=(4.9, 4.5))
a, b, r2 = persistence["ivol"]; lim = (0, 0.6)
ax.scatter(pairs["ivol"], pairs["ivol_next"], s=5, color=GREY, alpha=0.25, linewidths=0)
ax.plot(lim, lim, color="black", linestyle=":", linewidth=1)
ax.plot(lim, [a + b * lim[0], a + b * lim[1]], color=RED, linewidth=2)
ax.set_xlim(lim); ax.set_ylim(lim); ax.set_aspect("equal")
ax.xaxis.set_major_formatter(pct); ax.yaxis.set_major_formatter(pct)
ax.set_xlabel("estimated on the last three years"); ax.set_ylabel("the next year"); ax.set_title("Residual volatility")
ax.text(0.05, 0.92, f"slope {b:.2f}   $R^2$ {r2:.2f}", transform=ax.transAxes, color=RED, fontsize=13)
fig.savefig(OUT / "vol_persistence.pdf"); plt.close(fig)

# A. appendix: what a one-year ranking earns, by holding year
fig, ax = plt.subplots(figsize=(8.8, 3.7))
x = np.arange(3); w = 0.36
for offset, by_k, colour, label in [(-w / 2, ind_trade, GREY, "49 industries"), (w / 2, stock_trade, BLUE, "500 largest stocks")]:
    vals = [by_k[k].mean() for k in [1, 2, 3]]
    ax.bar(x + offset, vals, width=w, color=colour, label=label)
    for xi, v in zip(x + offset, vals):
        ax.text(xi, v + (0.002 if v >= 0 else -0.002), f"{v:+.1%}", ha="center", va="bottom" if v >= 0 else "top")
ax.axhline(0, color="black", linewidth=0.8)
ax.set_xticks(x); ax.set_xticklabels(["held the next year", "the year after", "three years on"])
ax.set_ylim(-0.022, 0.068); ax.set_yticks([]); ax.spines["left"].set_visible(False)
ax.legend(frameon=False, loc="upper right")
fig.savefig(OUT / "alpha_by_holding_year.pdf"); plt.close(fig)

# B. appendix: stocks, one-year look-back
fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.3))
for ax, k, lim, title, is_pct in [(axes[0], "beta", (0, 2.5), "Beta", False),
                                  (axes[1], "alpha", (-1.2, 1.2), "Alpha, per year", True)]:
    a, b, r2 = stock_persistence[(k, 1)]
    ax.scatter(stock_pairs[k], stock_pairs[k + "_later"], s=3, color=GREY, alpha=0.12, linewidths=0, rasterized=True)
    ax.plot(lim, lim, color="black", linestyle=":", linewidth=1)
    ax.plot(lim, [a + b * lim[0], a + b * lim[1]], color=RED, linewidth=2)
    ax.set_xlim(lim); ax.set_ylim(lim); ax.set_aspect("equal")
    ax.set_xlabel("this year"); ax.set_ylabel("next year"); ax.set_title(title)
    ax.text(0.05, 0.92, f"slope {b:.2f}   $R^2$ {r2:.2f}", transform=ax.transAxes, color=RED, fontsize=13)
    if is_pct:
        ax.xaxis.set_major_formatter(pct); ax.yaxis.set_major_formatter(pct)
fig.tight_layout(); fig.savefig(OUT / "stock_beta_alpha_persistence.pdf", dpi=200); plt.close(fig)

# ================================================================ the numbers the slides quote
print(f"MAIN: {LOOKBACK}-year look-back, {len(industries)} industries, estimates at the end of {estimates.year.min()}-{estimates.year.max()}, "
      f"{len(pairs):,} pairs, holding years {trade.index[0].year}-{trade.index[-1].year}")
print(f"  trade, top fifth minus bottom fifth   promised {np.mean(promised):.2%}/yr   delivered {trade.mean()*252:.2%}/yr   "
      f"t on yearly returns {tstat(trade_by_year):.2f}   daily Sharpe {trade.mean()/trade.std()*np.sqrt(252):.2f}   "
      f"delivered/promised {trade.mean()*252/np.mean(promised):.0%}")
print(f"  trade, yearly returns: {len(trade_by_year)} years   mean {trade_by_year.mean():.2%}   vol {trade_by_year.std():.2%}   "
      f"appraisal ratio {trade_ar:.3f}   x sqrt(years) = {trade_ar * np.sqrt(len(trade_by_year)):.2f}   "
      f"t / sqrt(years) = {tstat(trade_by_year) / np.sqrt(len(trade_by_year)):.3f}")
print(f"  trade on the market, yearly: beta {trade_reg.params['Mkt-RF']:+.3f}   alpha {trade_reg.params['const']:.2%}   "
      f"residual vol {np.sqrt(trade_reg.mse_resid):.2%}   alpha / residual vol {trade_reg.params['const'] / np.sqrt(trade_reg.mse_resid):.3f}   "
      f"t(alpha) {trade_reg.tvalues['const']:.2f}")
trade_reg_daily = sm.OLS(trade, sm.add_constant(daily.loc[trade.index, "Mkt-RF"])).fit()
print(f"  trade on the market, yearly: beta SE {trade_reg.bse['Mkt-RF']:.3f};   daily: beta {trade_reg_daily.params['Mkt-RF']:+.3f} (SE {trade_reg_daily.bse['Mkt-RF']:.3f})   "
      f"alpha {trade_reg_daily.params['const']*252:.2%}   alpha / residual vol {trade_reg_daily.params['const']*252 / (np.sqrt(trade_reg_daily.mse_resid)*np.sqrt(252)):.3f}   "
      f"t(alpha) {trade_reg_daily.tvalues['const']:.2f}")
print(f"  appraisal ratio standard error, typical: {(estimates.se_alpha / estimates.ivol).median():.3f};   mean beta {estimates.beta.mean():.3f}   mean alpha {estimates.alpha.mean():.3%}   "
      f"mean appraisal {estimates.appraisal.mean():.3f}   trade yearly mean {trade_by_year.mean():.3%}")
print(f"  trade, top third minus bottom third (appendix table)   promised {np.mean(thirds_promised):.1%}/yr   "
      f"delivered {thirds.mean()*252:.1%}/yr   t on yearly returns {tstat(thirds_by_year):.1f}")
for k in ["beta", "alpha", "ivol"]:
    print(f"  {k:5s}   slope {persistence[k][1]:.2f}  R2 {persistence[k][2]:.3f}")
print(f"  hedge   raw betas {betas.raw.min():.2f} to {betas.raw.max():.2f};  hedged: mean |beta| {betas.hedged.abs().mean():.2f}, "
      f"range {betas.hedged.min():+.2f} to {betas.hedged.max():+.2f}")
print(f"  typical estimate   beta {estimates.beta.median():.2f} +/- {estimates.se_beta.median():.2f};  "
      f"alpha {estimates.alpha.median():+.1%} +/- {estimates.se_alpha.median():.1%};  "
      f"|t|>2: betas {(estimates.beta.abs() > 2*estimates.se_beta).mean():.0%}, alphas {(estimates.alpha.abs() > 2*estimates.se_alpha).mean():.0%}")
both = estimates.merge(estimates_monthly, on=["year", "industry"], suffixes=("", "_monthly"))
print(f"  beta against the average beta that year ({estimates.beta_avg.mean():.2f} on average):  |t|>2 {(estimates.t_beta_vs_avg.abs() > 2).mean():.0%};   "
      f"against 1:  |t|>2 {(((estimates.beta - 1) / estimates.se_beta).abs() > 2).mean():.0%};   "
      f"typical |beta - average| {(estimates.beta - estimates.beta_avg).abs().median():.2f}")
print(f"  appraisal ratio of each three-year estimate:  mean {estimates.appraisal.mean():+.2f}   median {estimates.appraisal.median():+.2f}   "
      f"mean |.| {estimates.appraisal.abs().mean():.2f}   median |.| {estimates.appraisal.abs().median():.2f};   "
      f"mean alpha {estimates.alpha.mean():+.1%}, mean ivol {estimates.ivol.mean():.1%}, median ivol {estimates.ivol.median():.1%};   "
      f"1/sqrt(3) = {1/np.sqrt(3):.2f};   mean t(alpha) {estimates.t_alpha.mean():+.2f}, median {estimates.t_alpha.median():+.2f}")
print(f"  same windows, daily vs monthly ({len(both):,} of {len(estimates):,}):   "
      f"beta SE {both.se_beta.median():.3f} vs {both.se_beta_monthly.median():.3f};   "
      f"alpha SE {both.se_alpha.median():.1%} vs {both.se_alpha_monthly.median():.1%};   "
      f"formula says beta SE x sqrt(21) = {both.se_beta.median() * np.sqrt(21):.3f}, alpha SE unchanged")
print(f"MARKET {mkt.index[0]} to {mkt.index[-1]}: mean {mkt_mean:.1%}  vol {mkt_vol:.1%}  Sharpe {mkt_sr:.2f}  "
      f"SE after 10 yrs {mkt_vol/np.sqrt(10):.1%}   decades {min(decades.values()):+.1%} to {max(decades.values()):+.1%}   "
      f"years to be 95% sure it is above zero (z = 1.64): {(1.645/mkt_sr)**2:.0f}")
print(f"APPENDIX, one-year look-back.  industries: promised {np.mean(ind_promised):.1%}/yr, "
      f"typical alpha {one_year.alpha.median():+.1%} +/- {one_year.se_alpha.median():.1%};  "
      f"stocks: {len(picked):,} estimates, {picked.year.min()}-{picked.year.max()}")
for k in [1, 2, 3]:
    print(f"  year {k}: industries earned {ind_trade[k].mean():+.1%} (t {tstat(ind_trade[k]):+.1f});  "
          f"stocks promised {stock_promised[k]:.0%}, earned {stock_trade[k].mean():+.1%} (t {tstat(stock_trade[k]):+.1f});  "
          f"stock beta slope {stock_persistence[('beta', k)][1]:.2f} R2 {stock_persistence[('beta', k)][2]:.2f},  "
          f"alpha slope {stock_persistence[('alpha', k)][1]:+.2f} R2 {stock_persistence[('alpha', k)][2]:.3f}")
