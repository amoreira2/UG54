"""
Figures and numbers for slides/conditional_strategies_1.tex (timing risk) and _2.tex (timing expected returns)

    python slides/conditional_strategies_figures.py

Data:
  assets/data/factors_daily_1926.parquet   daily market and UMD, 1926-2026
  assets/data/ff6_daily_1963.parquet       daily six factors, 1963-2026 (Ken French)
  assets/data/Markettiming_data1.csv       CRSP value-weighted market with dividend yield, 1926-2024
  assets/data/factors_monthly_1926.parquet monthly RF
  assets/data/ff_monthly.csv               monthly six factors, 1980-2026
Realized variance is the sum of squared deviations of daily returns within the month, as in the momentum deck,
so the momentum numbers here match it. Figures go to slides/figures/; every number the slides quote is printed.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "assets" / "data"
OUT = HERE / "figures"
OUT.mkdir(exist_ok=True)

GREY, RED, BLUE, LIGHT = "#6B6B6B", "#B03A2E", "#2E5C8A", "#BDBDBD"
plt.rcParams.update({
    "font.size": 13, "axes.titlesize": 14, "axes.labelsize": 13,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": False, "figure.dpi": 150, "savefig.bbox": "tight",
})
sharpe = lambda x: x.mean() / x.std() * np.sqrt(12)
pct = lambda ax: (ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0%}"))
SIX = ["Mkt-RF", "SMB", "HML", "RMW", "CMA", "UMD"]
NAME = {"Mkt-RF": "Market", "SMB": "SMB", "HML": "HML", "RMW": "RMW", "CMA": "CMA", "UMD": "UMD"}

d26 = pd.read_parquet(DATA / "factors_daily_1926.parquet")
d63 = pd.read_parquet(DATA / "ff6_daily_1963.parquet")


def monthly(daily, col):
    """Monthly return and realized variance (sum of squared deviations) of one daily series, plus last month's."""
    me = daily.index + pd.offsets.MonthEnd(0)
    g = daily[col].groupby(me)
    df = pd.DataFrame({"r": (1 + daily[col]).groupby(me).prod() - 1,
                       "rv": g.apply(lambda x: ((x - x.mean()) ** 2).sum())})
    df["rv_lag"] = df.rv.shift(1)
    return df.dropna()


def manage(df, power=1.0, cap=None):
    """Weights c / RV_{t-1}^power, c chosen so the managed series is as volatile as the original."""
    w = 1 / df.rv_lag ** power
    w = w * df.r.std() / (w * df.r).std()
    if cap is not None:
        w = w.clip(upper=cap)
    return w * df.r, w


def drawdown(x):
    c = (1 + x).cumprod()
    return (c / c.cummax() - 1).min()


# ================================================================== CONDITIONAL STRATEGIES I: TIMING RISK
print("=== CONDITIONAL STRATEGIES I ===")
m = monthly(d26, "Mkt-RF")
vol = np.sqrt(m.rv * 12)
print(f"market {m.index[0]:%Y-%m} to {m.index[-1]:%Y-%m}, {len(m)} months; realized vol: median {vol.median():.1%}, "
      f"max {vol.max():.1%} in {vol.idxmax():%Y-%m}")
for lab, t in [("1929-32", slice("1929", "1932")), ("1987", slice("1987-10", "1987-10")), ("2008", slice("2008-10", "2008-11")),
               ("2020", slice("2020-03", "2020-03"))]:
    print(f"  peak {lab}: {vol.loc[t].max():.0%}")

# volatility comes in waves
fig, ax = plt.subplots(figsize=(10, 3.6))
ax.plot(vol.index, vol, color=GREY, lw=0.8)
ax.axhline(vol.median(), color=RED, lw=1, ls="--")
ax.text(pd.Timestamp("1957"), vol.median() + 0.10, f"median {vol.median():.0%}", color=RED, ha="center")
for lab, dt_ in [("1929-32", "1932-06"), ("1987", "1987-10"), ("2008", "2008-10"), ("2020", "2020-03")]:
    ax.annotate(lab, (pd.Timestamp(dt_), vol.loc[dt_].max()), xytext=(0, 6), textcoords="offset points", ha="center", fontsize=11)
ax.set_ylim(0, 1.05); pct(ax); ax.set_ylabel("realized volatility, a year")
fig.savefig(OUT / "cs_vol_history.pdf"); plt.close(fig)

# volatility forecasts itself, returns do not
lv, lv1 = np.log(np.sqrt(m.rv * 12)), np.log(np.sqrt(m.rv_lag * 12))
c_vol, c_ret = np.corrcoef(lv, lv1)[0, 1], np.corrcoef(m.r, np.sqrt(m.rv_lag * 12))[0, 1]
r2_vol = sm.OLS(lv, sm.add_constant(lv1)).fit().rsquared
r2_ret = sm.OLS(m.r, sm.add_constant(m.rv_lag)).fit().rsquared
print(f"corr(log vol_t, log vol_t-1) {c_vol:.2f} (R2 {r2_vol:.2f}); corr(r_t, vol_t-1) {c_ret:.3f} (R2 {r2_ret:.4f})")
fig, axes = plt.subplots(1, 2, figsize=(10.5, 4))
axes[0].scatter(np.exp(lv1), np.exp(lv), s=6, color=GREY, alpha=0.5)
axes[0].set_xscale("log"); axes[0].set_yscale("log")
for a_ in [axes[0].xaxis, axes[0].yaxis]:
    a_.set_major_formatter(lambda v, _: f"{v:.0%}"); a_.set_minor_formatter(lambda v, _: "")
axes[0].set_xticks([0.05, 0.1, 0.2, 0.5, 1]); axes[0].set_yticks([0.05, 0.1, 0.2, 0.5, 1])
axes[0].set_xlabel("volatility last month"); axes[0].set_ylabel("volatility this month")
axes[0].set_title(f"volatility: correlation {c_vol:.2f}")
axes[1].scatter(np.sqrt(m.rv_lag * 12), m.r, s=6, color=GREY, alpha=0.5)
axes[1].axhline(0, color="k", lw=0.6); axes[1].set_xscale("log")
axes[1].xaxis.set_major_formatter(lambda v, _: f"{v:.0%}"); axes[1].xaxis.set_minor_formatter(lambda v, _: "")
axes[1].set_xticks([0.05, 0.1, 0.2, 0.5, 1]); pct(axes[1])
axes[1].set_xlabel("volatility last month"); axes[1].set_ylabel("market return this month")
axes[1].set_title(f"return: correlation {c_ret:.2f}")
fig.tight_layout(); fig.savefig(OUT / "cs_persist.pdf"); plt.close(fig)


def by_quintile(df):
    q = pd.qcut(df.rv_lag, 5, labels=[1, 2, 3, 4, 5])
    return pd.DataFrame({"vol": df.r.groupby(q, observed=True).std() * np.sqrt(12),
                         "ret": df.r.groupby(q, observed=True).mean() * 12,
                         "sharpe": df.r.groupby(q, observed=True).mean() / df.r.groupby(q, observed=True).std() * np.sqrt(12)})


qm = by_quintile(m)
print("market by last month's volatility, quintiles:\n", qm.round(3).to_string())
fig, axes = plt.subplots(1, 3, figsize=(12, 3.6))
for ax, col, title, colr in zip(axes, ["vol", "ret", "sharpe"], ["volatility next month", "return next month", "Sharpe ratio next month"],
                                [GREY, GREY, RED]):
    ax.bar(range(1, 6), qm[col], color=colr, width=0.6)
    ax.set_xticks(range(1, 6)); ax.set_xticklabels(["1\ncalm", "2", "3", "4", "5\nvolatile"])
    ax.set_title(title); ax.axhline(0, color="k", lw=0.6)
    if col != "sharpe":
        pct(ax)
axes[1].set_ylim(0, 0.2)
axes[1].set_xlabel("last month's volatility, quintile")
fig.tight_layout(); fig.savefig(OUT / "cs_sort_market.pdf"); plt.close(fig)

# the managed market
mm, wm = manage(m)
fit = sm.OLS(mm, sm.add_constant(m.r)).fit()
print(f"market 1926-2026: Sharpe {sharpe(m.r):.2f}, managed {sharpe(mm):.2f}; alpha {fit.params.iloc[0] * 12:.1%}, t {fit.tvalues.iloc[0]:.1f}; "
      f"max drawdown {drawdown(m.r):.0%} vs {drawdown(mm):.0%}")
print(f"  weights: median {wm.median():.2f}, 95th percentile {wm.quantile(0.95):.1f}, max {wm.max():.1f} in {wm.idxmax():%Y-%m}, "
      f"share above 2 {np.mean(wm > 2):.0%}; average change a month {wm.diff().abs().mean():.2f}")
for lab, sl in [("1926-1945", slice("1926", "1945")), ("1946-1979", slice("1946", "1979")), ("1980-2014", slice("1980", "2014")),
                ("2015-2026", slice("2015", "2026")), ("1963-2026", slice("1963", "2026"))]:
    s_ = m.loc[sl]
    mg_, _ = manage(s_)
    f_ = sm.OLS(mg_, sm.add_constant(s_.r)).fit()
    print(f"  {lab}: Sharpe {sharpe(s_.r):.2f}, managed {sharpe(mg_):.2f}; alpha {f_.params.iloc[0] * 12:.1%}, t {f_.tvalues.iloc[0]:.1f}; "
          f"median volatility {np.sqrt(s_.rv * 12).median():.0%}; {len(s_)} months")
for cap in [1, 2, 3]:
    print(f"  capped at {cap}: Sharpe {sharpe(manage(m, cap=cap)[0]):.2f}")
print(f"  scaled by 1/vol instead of 1/variance: Sharpe {sharpe(manage(m, power=0.5)[0]):.2f}")
ep = pd.DataFrame({"market": m.r, "managed": mm, "weight": wm})
print("  episodes:\n", ep.loc["1987-09":"1987-11"].round(3).to_string(), "\n", ep.loc["2008-09":"2008-11"].round(3).to_string(),
      "\n", ep.loc["2020-02":"2020-05"].round(3).to_string())

fig, ax = plt.subplots(figsize=(10, 3.4))
ax.plot(wm.index, wm, color=GREY, lw=0.7)
ax.axhline(1, color=RED, lw=1, ls="--"); ax.text(pd.Timestamp("1931"), 25, "dashed: buy and hold, weight 1", color=RED, fontsize=11)
ax.set_yscale("log"); ax.set_ylim(0.008, 60); ax.set_yticks([0.01, 0.1, 1, 10]); ax.set_yticklabels(["0.01", "0.1", "1", "10"])
ax.set_ylabel("weight on the market")
fig.savefig(OUT / "cs_weights.pdf"); plt.close(fig)

# six factors, 1963-2026
rows = {}
for c in SIX:
    df = monthly(d63, c)
    mg, w_ = manage(df)
    f_ = sm.OLS(mg, sm.add_constant(df.r)).fit()
    rows[c] = dict(sr=sharpe(df.r), managed=sharpe(mg), cap2=sharpe(manage(df, cap=2)[0]), alpha=f_.params.iloc[0] * 12,
                   t=f_.tvalues.iloc[0], corr=np.corrcoef(df.r, df.rv_lag)[0, 1])
SF = pd.DataFrame(rows).T
print("six factors, 1963-2026:\n", SF.round(3).to_string())
fig, ax = plt.subplots(figsize=(9, 3.8))
x_ = np.arange(6)
ax.bar(x_ - 0.18, SF.sr, 0.34, color=LIGHT, label="buy and hold")
ax.bar(x_ + 0.18, SF.managed, 0.34, color=RED, label="volatility managed")
ax.set_xticks(x_); ax.set_xticklabels([NAME[c] for c in SIX]); ax.set_ylabel("Sharpe ratio, 1963-2026")
ax.legend(frameon=False, loc="upper left")
fig.savefig(OUT / "cs_factors.pdf"); plt.close(fig)

# can you beat last month's RV? Other proxies for next month's variance, market 1926-2026 and UMD 1963-2026
def proxies(daily):
    me = daily.index + pd.offsets.MonthEnd(0)
    r_ = (1 + daily).groupby(me).prod() - 1
    rv_ = daily.groupby(me).apply(lambda x: ((x - x.mean()) ** 2).sum())
    ewma = (daily ** 2).ewm(alpha=1 - 0.94).mean().groupby(me).last() * 21     # RiskMetrics, lambda = 0.94, a month ahead
    df = pd.DataFrame({"last month": rv_.shift(1), "last 3 months": rv_.rolling(3).mean().shift(1),
                       "last 12 months": rv_.rolling(12).mean().shift(1), "EWMA of daily returns": ewma.shift(1),
                       "rv": rv_, "r": r_}).dropna()
    out = {}
    for k in ["last month", "last 3 months", "last 12 months", "EWMA of daily returns"]:
        w = 1 / df[k]
        out[k] = (np.corrcoef(np.log(df[k]), np.log(df.rv))[0, 1] ** 2, sharpe(w * df.r * df.r.std() / (w * df.r).std()))
    return out, df.index[0]
for lab, daily in [("market", d26["Mkt-RF"]), ("UMD 1963-2026", d63["UMD"])]:
    out, start = proxies(daily)
    print(f"proxies for next month's variance, {lab} from {start:%Y-%m} (R2 of log variance, managed Sharpe):",
          {k: (round(a, 2), round(b, 2)) for k, (a, b) in out.items()})
print("persistence: autocorrelation of log RV at 1, 3, 6, 12 months:", [round(np.log(m.rv).autocorr(k), 2) for k in [1, 3, 6, 12]])


# how often to rebalance, and on how much history: hold for k trading days, weight 1 / variance of the last `window` days
def every(x, k, window, offset=0):
    v = x.rolling(window).var().shift(1)                       # known at the start of the day
    idx = np.arange(len(x))
    first = np.clip(((idx + offset) // k) * k - offset, 0, None) # the first day of each holding block
    w = 1 / v.values[first]
    ok = ~np.isnan(w)
    s_ = pd.Series(w[ok] * x.values[ok], index=x.index[ok])
    scale = x[ok].std() / s_.std()
    me = s_.index + pd.offsets.MonthEnd(0)
    trades = np.abs(np.diff(w[ok] * scale)).sum() / (ok.sum() / 252)
    return sharpe((1 + s_ * scale).groupby(me).prod() - 1), trades
for lab, x in [("market", d26["Mkt-RF"].loc["1927":]), ("UMD", d26["UMD"].dropna().loc["1927":])]:
    print(f"holding periods, {lab}, 1927-2026 (buy and hold {sharpe((1 + x).groupby(x.index + pd.offsets.MonthEnd(0)).prod() - 1):.2f}):")
    print(f"   every day on the last 5 days: Sharpe {every(x, 1, 5)[0]:.2f}")
    for k, name in [(1, "day"), (5, "week"), (21, "month"), (63, "quarter"), (126, "6 months")]:
        vals = [every(x, k, 21, o)[0] for o in (range(0, k, max(1, k // 6)) if k > 1 else [0])]
        print(f"   every {name:8s} on the last 21 days: Sharpe {np.mean(vals):.2f} (start day {min(vals):.2f} to {max(vals):.2f}), "
              f"trades {every(x, k, 21)[1]:.1f} times the position a year")

# exercise 5: the best mix of the six factors, then volatility-timed
me63 = d63.index + pd.offsets.MonthEnd(0)
R6 = (1 + d63[SIX]).groupby(me63).prod() - 1
w6 = np.linalg.inv(R6.cov().values) @ R6.mean().values
w6 = w6 / np.abs(w6).sum()
combo = monthly(pd.DataFrame({"mix": d63[SIX] @ w6}), "mix")
cm, _ = manage(combo)
fc = sm.OLS(cm, sm.add_constant(combo.r)).fit()
print("best mix weights:", dict(zip(SIX, w6.round(2))), f"Sharpe {sharpe(combo.r):.2f}, managed {sharpe(cm):.2f}; "
      f"alpha {fc.params.iloc[0] * 12:.1%}, t {fc.tvalues.iloc[0]:.1f}")
for a_, b_ in [("1963", "1979"), ("1980", "2014"), ("2015", "2026")]:
    s_ = combo.loc[a_:b_]
    print(f"   {a_}-{b_}: {sharpe(s_.r):.2f} -> {sharpe(manage(s_)[0]):.2f}")
print("   Sharpe by last month's volatility quintile:", by_quintile(combo).sharpe.round(2).tolist())

# why: the price of risk falls with volatility for UMD, not for CMA
qu, qc = by_quintile(monthly(d63, "UMD")), by_quintile(monthly(d63, "CMA"))
print("UMD by quintile:\n", qu.round(2).to_string(), "\nCMA by quintile:\n", qc.round(2).to_string())
fig, axes = plt.subplots(1, 2, figsize=(10, 3.6), sharey=True)
for ax, q_, lab, col in zip(axes, [qu, qc], ["UMD", "CMA"], [RED, GREY]):
    ax.bar(range(1, 6), q_.sharpe, color=col, width=0.6)
    ax.set_xticks(range(1, 6)); ax.set_xticklabels(["1\ncalm", "2", "3", "4", "5\nvolatile"])
    ax.set_title(f"{lab}: Sharpe ratio next month"); ax.axhline(0, color="k", lw=0.6)
    ax.set_xlabel("last month's volatility, quintile")
fig.tight_layout(); fig.savefig(OUT / "cs_sort_umd_cma.pdf"); plt.close(fig)

# UMD over the long sample, for the link to the momentum deck
u = monthly(d26.dropna(subset=["UMD"]), "UMD")              # daily UMD starts in November 1926
um, _ = manage(u)
print(f"UMD {u.index[0]:%Y}-{u.index[-1]:%Y}: Sharpe {sharpe(u.r):.2f}, managed {sharpe(um):.2f}; max drawdown {drawdown(u.r):.0%} vs {drawdown(um):.0%}")
print(f"CHALLENGE I, UMD 1963-2026 capped at 2: Sharpe {SF.loc['UMD', 'cap2']:.4f}")

# ================================================================== CONDITIONAL STRATEGIES II: TIMING EXPECTED RETURNS
print("\n=== CONDITIONAL STRATEGIES II ===")
c = pd.read_csv(DATA / "Markettiming_data1.csv", parse_dates=["date"], index_col="date")
c.index = c.index + pd.offsets.MonthEnd(0)
c = c.join(pd.read_parquet(DATA / "factors_monthly_1926.parquet")[["RF"]], how="inner").dropna()
c["ex"] = c.vwretd - c.RF                                    # market excess return
c["dp"] = c.dp.rolling(12).sum()                             # dividends over the last 12 months, over today's price
lx = np.log1p(c.vwretd) - np.log1p(c.RF)                     # log excess return, so returns add across months
print(f"market {c.index[0]:%Y-%m} to {c.index[-1]:%Y-%m}; D/P from {c.dp.min():.1%} to {c.dp.max():.1%}, last {c.dp.iloc[-1]:.1%}")

fut5 = lx.rolling(60).sum().shift(-60) / 5
fig, ax = plt.subplots(figsize=(10, 3.8))
ax.plot(c.dp, color=BLUE, lw=1.6, label="dividend yield")
ax2 = ax.twinx()
ax2.plot(fut5, color=RED, lw=1.2, label="return over the next five years, a year")
ax2.axhline(0, color="k", lw=0.5)
ax.set_ylabel("dividend yield", color=BLUE); ax2.set_ylabel("next five years, a year", color=RED)
ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0%}"); ax2.yaxis.set_major_formatter(lambda v, _: f"{v:.0%}")
ax2.spines["right"].set_visible(True)
fig.savefig(OUT / "cs_dp.pdf"); plt.close(fig)
print(f"correlation of D/P with the next five years' return: {c.dp.corr(fut5):.2f}")

HZ = {}
for h in [1, 12, 60]:
    y = lx.rolling(h).sum().shift(-h) * 12 / h
    dd = pd.DataFrame({"y": y, "x": c.dp}).loc["1927":].dropna()
    X = sm.add_constant(dd.x)
    naive, hac = sm.OLS(dd.y, X).fit(), sm.OLS(dd.y, X).fit(cov_type="HAC", cov_kwds={"maxlags": max(h, 1)})
    HZ[h] = dict(b=naive.params.x, t_naive=naive.tvalues.x, t_hac=hac.tvalues.x, r2=naive.rsquared, n=len(dd), independent=len(dd) // h)
    print(f"  horizon {h:2d} months: b {naive.params.x:.2f}, naive t {naive.tvalues.x:.2f}, HAC t {hac.tvalues.x:.2f}, "
          f"R2 {naive.rsquared:.3f}, {len(dd)} observations, {len(dd) // h} that do not overlap")
dn = pd.DataFrame({"y": fut5, "x": c.dp}).loc["1927":].dropna().iloc[::60]
fn = sm.OLS(dn.y, sm.add_constant(dn.x)).fit()
print(f"  five-year returns that do not overlap: t {fn.tvalues.x:.2f}, {len(dn)} observations")

for SRa in [0.4, 0.5]:
    for R2 in [HZ[1]["r2"], 0.01, 0.02]:
        s_ = SRa / np.sqrt(12)
        print(f"  Campbell-Thompson: Sharpe {SRa}, monthly R2 {R2:.2%}: timed Sharpe {np.sqrt((s_ ** 2 + R2) / (1 - R2)) * np.sqrt(12):.2f}")


def out_of_sample(start):
    """Each month t from `start`: regress next-month excess return on D/P using only pairs fully known at t,
    forecast month t+1, and keep the historical average as the benchmark."""
    y, x = c.ex.shift(-1), c.dp
    rows_ = []
    for t in c.loc[start:].index[:-1]:
        tr = pd.DataFrame({"y": y, "x": x}).loc["1927":t].iloc[:-1].dropna()
        b, a = np.polyfit(tr.x, tr.y, 1)
        rows_.append((t, y.loc[t], a + b * x.loc[t], tr.y.mean()))
    return pd.DataFrame(rows_, columns=["date", "r", "forecast", "average"]).set_index("date")


r2_oos = lambda P: 1 - ((P.r - P.forecast) ** 2).sum() / ((P.r - P.average) ** 2).sum()
P = out_of_sample("1950")
print(f"out of sample, forecasts from 1950: R2 {r2_oos(P):.2%}")
for a_, b_ in [("1950", "1979"), ("1980", "1999"), ("2000", "2024")]:
    print(f"  {a_}-{b_}: R2 {r2_oos(P.loc[a_:b_]):.2%}")
cum = ((P.r - P.average) ** 2 - (P.r - P.forecast) ** 2).cumsum()
fig, ax = plt.subplots(figsize=(10, 3.6))
ax.plot(cum.index, cum, color=RED, lw=1.5)
ax.axhline(0, color="k", lw=0.6)
ax.set_ylabel("cumulative gain from D/P\nover the historical average")
ax.text(pd.Timestamp("1952"), cum.max() * 0.85, "rising: D/P forecasts better", color=GREY, fontsize=11)
ax.text(pd.Timestamp("2003"), cum.max() * 0.85, "falling: worse", color=GREY, fontsize=11)
fig.savefig(OUT / "cs_gw.pdf"); plt.close(fig)
print(f"  cumulative gain peaks in {cum.idxmax():%Y-%m}")

sig2 = c.ex.loc[:"1949"].var()
w_ = P.forecast / (3 * sig2)
tim = w_ * P.r
print(f"timing strategy from 1950 (gamma 3): Sharpe {sharpe(tim):.2f} vs buy and hold {sharpe(P.r):.2f}; average weight {w_.mean():.2f}, "
      f"share of months short {np.mean(w_ < 0):.0%}")
for a_, b_ in [("1950", "1979"), ("1980", "1999"), ("2000", "2024")]:
    print(f"  {a_}-{b_}: timing {sharpe(tim.loc[a_:b_]):.2f}, buy and hold {sharpe(P.r.loc[a_:b_]):.2f}, average weight {w_.loc[a_:b_].mean():.2f}")
print(f"CHALLENGE II, forecasts from 1980: R2 {r2_oos(out_of_sample('1980')):.4%}")

# timing the factors: 6 factors x 4 signals, first half against second half
ff = pd.read_csv(DATA / "ff_monthly.csv", index_col=0, parse_dates=True)
F = ff[SIX].dropna()
RV = d63[SIX].groupby(d63.index + pd.offsets.MonthEnd(0)).apply(lambda x: ((x - x.mean()) ** 2).sum())
rows = []
for f_ in SIX:
    r_ = F[f_]
    sigs = {"last month": r_, "last 12 months": r_.rolling(12).sum(), "3-5 years ago": r_.shift(12).rolling(48).sum(),
            "own volatility": np.sqrt(RV[f_]).reindex(r_.index)}
    for k, s_ in sigs.items():
        dd = pd.DataFrame({"y": r_.shift(-1), "x": s_}).dropna()
        row = dict(factor=NAME[f_], signal=k)
        for lab, sl in [("first", slice("1980", "2002")), ("second", slice("2003", "2026"))]:
            q_ = dd.loc[sl]
            row[lab] = sm.OLS(q_.y, sm.add_constant(q_.x)).fit().tvalues.iloc[1]
        rows.append(row)
T = pd.DataFrame(rows)
best = T.reindex(T["first"].abs().sort_values(ascending=False).index).head(5)
print(f"24 timing signals: |t| > 2 in the first half {np.sum(T['first'].abs() > 2)}, in the second {np.sum(T['second'].abs() > 2)}; "
      f"correlation of t across halves {T['first'].corr(T['second']):.2f}")
print("  the five best in the first half:\n", best.round(2).to_string())
print("  'last month' signal:\n", T[T.signal == "last month"].round(2).to_string())
fig, ax = plt.subplots(figsize=(6.4, 4.6))
ax.axvspan(-2, 2, color="#F4F4F4", lw=0); ax.axhspan(-2, 2, color="#F4F4F4", lw=0)
ax.axhline(0, color="k", lw=0.5); ax.axvline(0, color="k", lw=0.5)
ax.scatter(T["first"], T["second"], color=GREY, s=26, zorder=3)
ax.scatter(best["first"], best["second"], color=RED, s=40, zorder=4)
OFF = {("RMW", "3-5 years ago"): (6, -10, "left"), ("CMA", "own volatility"): (6, 4, "left"), ("HML", "own volatility"): (6, -10, "left"),
       ("HML", "last month"): (6, 2, "left"), ("HML", "3-5 years ago"): (-6, 8, "right")}
for _, r_ in best.iterrows():
    dx, dy, ha = OFF.get((r_.factor, r_.signal), (6, -4, "left"))
    ax.annotate(f"{r_.factor}, {r_.signal}", (r_["first"], r_["second"]), xytext=(dx, dy), textcoords="offset points", fontsize=9.5, ha=ha)
ax.set_xlabel("t-statistic, 1980-2002"); ax.set_ylabel("t-statistic, 2003-2026")
ax.set_xlim(-4.5, 5.2); ax.set_ylim(-4.5, 4.5)
fig.savefig(OUT / "cs_tstats.pdf"); plt.close(fig)

# factor momentum, the one that survives: hold a factor only if its last 12 months were positive
print("factor momentum, 1981-2026 (hold if the last 12 months were positive, else T-bills):")
for f_ in SIX:
    r_ = F[f_]
    s_ = (r_.rolling(12).sum().shift(1) > 0).astype(float)
    print(f"  {NAME[f_]:7s} buy and hold {sharpe(r_.loc['1981':]):.2f}, timed {sharpe((s_ * r_).loc['1981':]):.2f}, months held {s_.loc['1981':].mean():.0%}")
