"""
Figures and numbers for slides/momentum.tex

    python slides/momentum_figures.py

Data: Ken French's factors and 49 industries (assets/data/*_1926.parquet, monthly and daily,
1926-2026), our CRSP panel (1980-2000) and the 29 published long-shorts (1980-2000).
The industry-momentum rule is the one in chapters/Finance/L10_Momentum_v2_AI.ipynb.
Figures go to slides/figures/; every number the slides quote is printed at the end.
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

GREY, RED, BLUE = "#6B6B6B", "#B03A2E", "#2E5C8A"
plt.rcParams.update({
    "font.size": 13, "axes.titlesize": 14, "axes.labelsize": 13,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": False, "figure.dpi": 150, "savefig.bbox": "tight",
})

fac   = pd.read_parquet(DATA / "factors_monthly_1926.parquet")
fac_d = pd.read_parquet(DATA / "factors_daily_1926.parquet")
ind   = pd.read_parquet(DATA / "ind49_monthly_1926.parquet")
panel = pd.read_parquet(DATA / "panel_backbone_1980_2000.parquet")
L     = pd.read_parquet(DATA / "longshort_29.parquet")

sharpe   = lambda x: x.mean() / x.std() * np.sqrt(12)
drawdown = lambda x: ((1 + x).cumprod() / (1 + x).cumprod().cummax() - 1)

def reg(y, cols):
    return sm.OLS(y, sm.add_constant(fac.loc[y.index, cols]), missing="drop").fit()

umd, mkt = fac["UMD"].dropna(), fac["Mkt-RF"]

# ---------------------------------------------------------------- 1. UMD against the market, 1927-2026
both = pd.concat([umd.rename("UMD"), mkt.rename("market")], axis=1).dropna()
fig, ax = plt.subplots(figsize=(9, 4.4))
for col, colour in [("UMD", RED), ("market", GREY)]:
    ax.plot(both.index, (1 + both[col]).cumprod(), color=colour, linewidth=1.6)
ax.set_yscale("log")
ax.legend(["UMD: winners minus losers", "the market, over the T-bill"], frameon=False, loc="upper left")
ax.set_ylabel("growth of \\$1, excess returns (log scale)")
fig.savefig(OUT / "mom_umd_vs_market.pdf"); plt.close(fig)

# ---------------------------------------------------------------- 2. deciles from our panel, 1981-2000
p = panel[panel.shrcd.isin([10, 11]) & panel.exchcd.isin([1, 2, 3])].sort_values(["permno", "date"]).copy()
p["1+ret"] = 1 + p["ret"]
p["cum11"] = (p.groupby("permno")["1+ret"].rolling(11).apply(np.prod, raw=True).reset_index(level=0, drop=True) - 1)
p["signal"] = p.groupby("permno")["cum11"].shift(2)
p["me_lag"] = p.groupby("permno")["me"].shift(1)
d = p.dropna(subset=["signal", "ret", "me_lag"]).copy()
def decile(x):
    edges = np.unique(np.quantile(x.loc[x.exchcd == 1, "signal"], np.linspace(0, 1, 11)))
    edges[0], edges[-1] = -np.inf, np.inf
    return pd.cut(x["signal"], edges, labels=False, duplicates="drop")
d["decile"] = d.groupby("date", group_keys=False).apply(decile)
dec = d.groupby(["date", "decile"]).apply(lambda x: np.average(x["ret"], weights=x["me_lag"])).unstack()
wml = dec[9] - dec[0]

fig, ax = plt.subplots(figsize=(9, 4.2))
means = dec.mean() * 12
ax.bar(range(1, 11), means * 100, color=[RED if k in (0, 9) else GREY for k in dec.columns])
ax.set_xticks(range(1, 11)); ax.set_xticklabels(["1\nlosers"] + [str(k) for k in range(2, 10)] + ["10\nwinners"])
ax.set_ylabel("average return, % per year")
for k, v in zip(range(1, 11), means * 100):
    ax.text(k, v + 0.3, f"{v:.1f}", ha="center", fontsize=11)
fig.savefig(OUT / "mom_deciles.pdf"); plt.close(fig)

# ---------------------------------------------------------------- 3. horizons: buy past winners at three lookbacks
h = pd.concat([-fac["ST_Rev"], fac["UMD"], -fac["LT_Rev"]], axis=1, keys=["st", "mom", "lt"]).dropna()
labels = ["last month\n($t-1$)", "the past year\n($t-12$ to $t-2$)", "the past five years\n($t-60$ to $t-13$)"]
srs = [sharpe(h[c]) for c in h.columns]
fig, ax = plt.subplots(figsize=(9, 4.2))
ax.bar(range(3), srs, color=[BLUE if s < 0 else RED for s in srs], width=0.55)
ax.axhline(0, color="black", linewidth=0.8)
ax.set_xticks(range(3)); ax.set_xticklabels(labels)
ax.set_ylabel("Sharpe ratio of buying the winners")
for k, s in enumerate(srs):
    ax.text(k, s + (0.03 if s > 0 else -0.09), f"{s:+.2f}", ha="center", fontsize=12)
ax.set_ylim(-0.9, 0.55)
fig.savefig(OUT / "mom_horizons.pdf"); plt.close(fig)

# ---------------------------------------------------------------- 4. industry momentum (the notebook's rule) and crashes
signal = ((1 + ind).rolling(11).apply(np.prod, raw=True) - 1).shift(2)
top, bottom = signal.rank(axis=1, ascending=False) <= 5, signal.rank(axis=1, ascending=True) <= 5
IM = (ind.where(top).mean(axis=1) - ind.where(bottom).mean(axis=1)).dropna()

fig, ax = plt.subplots(figsize=(9, 4.2))
ax.fill_between(umd.index, drawdown(umd) * 100, 0, color=RED, alpha=0.35, linewidth=0, label="UMD")
ax.plot(IM.index, drawdown(IM) * 100, color="black", linewidth=1.0, label="industry momentum")
ax.set_ylabel("drawdown from the last peak, %")
ax.legend(frameon=False, loc="lower right")
fig.savefig(OUT / "mom_crashes.pdf"); plt.close(fig)

# ---------------------------------------------------------------- 5. after a volatile month: more risk, no more return
ud = fac_d["UMD"].dropna()
RV = ud.resample("ME").apply(lambda x: ((x - x.mean()) ** 2).sum())
lag = RV.shift(1).reindex(umd.index)
q = pd.qcut(lag, 5, labels=False)
by_q = pd.DataFrame({"mean": umd.groupby(q).mean() * 12 * 100, "vol": umd.groupby(q).std() * np.sqrt(12) * 100})
fig, axes = plt.subplots(1, 2, figsize=(10, 4.0))
for ax, col, title, colour in [(axes[0], "mean", "average return next month, % per year", GREY),
                               (axes[1], "vol", "volatility next month, % per year", RED)]:
    ax.bar(range(1, 6), by_q[col], color=colour)
    ax.set_xticks(range(1, 6)); ax.set_xticklabels(["1\ncalm", "2", "3", "4", "5\nvolatile"])
    ax.set_title(title, fontsize=13); ax.set_xlabel("last month's volatility, quintile")
    for k, v in zip(range(1, 6), by_q[col]):
        ax.text(k, max(v, 0) + 0.5, f"{v:.1f}" if col == "mean" else f"{v:.0f}", ha="center", fontsize=11)
    ax.set_ylim(min(by_q[col].min(), 0) * 1.3, by_q[col].max() * 1.18)
axes[0].axhline(0, color="black", linewidth=0.8)
fig.tight_layout()
fig.savefig(OUT / "mom_vol_quintiles.pdf"); plt.close(fig)

# ---------------------------------------------------------------- 6. volatility-managed UMD
w = 1 / RV.shift(1)
Uv = (w.reindex(umd.index) * umd).dropna()
c = umd.loc[Uv.index].std() / Uv.std()
Uv = c * Uv
weight = (c * w).reindex(Uv.index)

fig, ax = plt.subplots(figsize=(9, 4.4))
ax.plot(Uv.index, (1 + umd.loc[Uv.index]).cumprod(), color=GREY, linewidth=1.5)
ax.plot(Uv.index, (1 + Uv).cumprod(), color=RED, linewidth=1.5)
ax.set_yscale("log")
ax.text(Uv.index[-1], (1 + Uv).prod() * 1.5, "scaled by last month's variance", color=RED, ha="right", fontsize=12)
ax.text(Uv.index[-1], (1 + umd.loc[Uv.index]).prod() / 4, "UMD", color=GREY, ha="right", fontsize=12)
ax.set_ylabel("growth of \\$1 (log scale)")
fig.savefig(OUT / "mom_vol_managed.pdf"); plt.close(fig)

# ================================================================ the numbers the slides quote
r = reg(umd, ["Mkt-RF"])
print(f"UMD {umd.index[0]:%Y-%m} to {umd.index[-1]:%Y-%m}: mean {umd.mean()*12:.1%}/yr, vol {umd.std()*np.sqrt(12):.1%}, "
      f"Sharpe {sharpe(umd):.2f}, maxDD {drawdown(umd).min():.1%};  market Sharpe {sharpe(mkt.loc[umd.index]):.2f}")
print(f"  $1 grows to: UMD ${(1+both['UMD']).prod():,.0f}, market ${(1+both['market']).prod():,.0f}")
print(f"  CAPM: alpha {r.params['const']*12:.1%}/yr (t {r.tvalues['const']:.2f}), beta {r.params['Mkt-RF']:.2f}")
print(f"DECILES 1981-2000: losers {means[0]:.1%}, winners {means[9]:.1%}, middle (5,6) {means[[4,5]].mean():.1%};  "
      f"WML mean {wml.mean()*12:.1%}, Sharpe {sharpe(wml):.2f}")
for cols in (["Mkt-RF"], ["Mkt-RF", "UMD"]):
    r = reg(wml, cols); print(f"  WML on {cols}: alpha {r.params['const']*12:.1%} (t {r.tvalues['const']:.2f}) "
                              f"{r.params.drop('const').round(2).to_dict()}  R2 {r.rsquared:.2f}")
print(f"HORIZONS {h.index[0]:%Y-%m} to {h.index[-1]:%Y-%m}: Sharpe last month {srs[0]:+.2f}, past year {srs[1]:+.2f}, "
      f"past five years {srs[2]:+.2f}")
terc = pd.qcut(mkt.loc[umd.index], 3, labels=["worst", "middle", "best"])
print("UMD by market tercile, %/month:", (umd.groupby(terc).mean() * 100).round(2).to_dict(),
      " market:", (mkt.loc[umd.index].groupby(terc).mean() * 100).round(2).to_dict())
for a, b in [("1927", "1964"), ("1965", "1989"), ("1990", "2026")]:
    x = umd.loc[a:b]; r = reg(x, ["Mkt-RF"])
    print(f"PERIOD {a}-{b}: mean {x.mean()*12:.1%}, Sharpe {sharpe(x):.2f}, CAPM alpha {r.params['const']*12:.1%} (t {r.tvalues['const']:.2f})")
fam = ["Mom12m", "Mom6m", "ResidualMomentum", "AnnouncementReturn"]
print("VARIANTS 1980-2000 correlations:"); print(L[fam].corr().round(2).to_string())
for s in fam:
    x = L[s].dropna(); x.index = x.index + pd.offsets.MonthEnd(0); r = reg(x, ["Mkt-RF", "UMD"])
    print(f"  {s:20s} Sharpe {sharpe(x):.2f}  alpha on Mkt+UMD {r.params['const']*12:+.1%} (t {r.tvalues['const']:+.2f})  UMD beta {r.params['UMD']:.2f}")
print(f"INDUSTRY MOMENTUM {IM.index[0]:%Y-%m} to {IM.index[-1]:%Y-%m}: mean {IM.mean()*12:.1%}, Sharpe {sharpe(IM):.2f}, "
      f"corr with UMD {pd.concat([IM, umd], axis=1).dropna().corr().iloc[0,1]:.2f}")
for cols in (["Mkt-RF"], ["Mkt-RF", "UMD"]):
    r = reg(IM, cols); print(f"  IM on {cols}: alpha {r.params['const']*12:.1%} (t {r.tvalues['const']:.2f}) "
                             f"{r.params.drop('const').round(2).to_dict()}  R2 {r.rsquared:.2f}")
for y in ["1932", "2009"]:
    print(f"CRASH {y}: UMD {(1+umd.loc[y]).prod()-1:+.1%}, industry momentum {(1+IM.loc[y]).prod()-1:+.1%}, "
          f"market {(1+mkt.loc[y]+fac['RF'].loc[y]).prod()-1:+.1%}")
print(f"  worst UMD month {umd.min():.1%} in {umd.idxmin():%Y-%m}; UMD maxDD {drawdown(umd).min():.1%} (trough {drawdown(umd).idxmin():%Y-%m}); "
      f"IM maxDD {drawdown(IM).min():.1%}")
bear = (((1 + mkt + fac["RF"]).rolling(24).apply(np.prod, raw=True) - 1) < 0).shift(1).reindex(umd.index).fillna(False).astype(bool)
for lab, mask in [("after a 2-year bear market", bear), ("after a 2-year bull market", ~bear)]:
    r = sm.OLS(umd[mask], sm.add_constant(mkt.loc[umd.index][mask])).fit()
    up = mask & (mkt.loc[umd.index] > 0)
    print(f"BEAR/BULL {lab}: {mask.sum()} months, beta {r.params.iloc[1]:+.2f}, UMD mean {umd[mask].mean()*12:+.1%}/yr, "
          f"UMD in the months the market rose {umd[up].mean()*100:+.1f}%/month")
print("VOL QUINTILES (lagged RV of daily UMD):"); print(by_q.round(1).to_string())
print(f"  persistence: corr(RV_t, RV_t-1) = {np.corrcoef(np.log(RV.iloc[1:]), np.log(RV.shift(1).iloc[1:]))[0,1]:.2f} (logs)")
r1, r2 = reg(Uv, ["Mkt-RF"]), reg(Uv, ["Mkt-RF", "UMD"])
print(f"VOL-MANAGED UMD {Uv.index[0]:%Y-%m}: Sharpe {sharpe(Uv):.2f} vs {sharpe(umd.loc[Uv.index]):.2f}; maxDD {drawdown(Uv).min():.1%} vs {drawdown(umd.loc[Uv.index]).min():.1%}")
print(f"  CAPM alpha {r1.params['const']*12:.1%} (t {r1.tvalues['const']:.2f});  Mkt+UMD alpha {r2.params['const']*12:.1%} (t {r2.tvalues['const']:.2f}), UMD beta {r2.params['UMD']:.2f}")
print(f"  weight on UMD: median {weight.median():.2f}, 90th pct {weight.quantile(.9):.2f}, 99th {weight.quantile(.99):.2f}, max {weight.max():.1f}; "
      f"share of months above 2x {(weight > 2).mean():.0%};  1932 {(1+Uv.loc['1932']).prod()-1:+.1%}, 2009 {(1+Uv.loc['2009']).prod()-1:+.1%}")
print(f"  average monthly change in the weight {weight.diff().abs().mean():.2f}")
capped = (weight.clip(upper=2) * umd.loc[Uv.index])
print(f"  capped at 2x: Sharpe {sharpe(capped):.2f}, maxDD {drawdown(capped).min():.1%}, vol {capped.std()*np.sqrt(12):.1%} vs UMD {umd.std()*np.sqrt(12):.1%}, "
      f"Mkt+UMD alpha {reg(capped, ['Mkt-RF', 'UMD']).params['const']*12:.1%} (t {reg(capped, ['Mkt-RF', 'UMD']).tvalues['const']:.2f})")
