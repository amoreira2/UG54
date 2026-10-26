"""
Figures and numbers for slides/why_should_this_work.tex

    python slides/why_should_this_work_figures.py

Same data and the same calculations as chapters/Finance/L9_WhyShouldThisWork_AI.ipynb,
so the slides and the notebook show the same numbers. Figures go to slides/figures/;
every number the slides quote is printed at the end.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import norm

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

L = pd.read_parquet(DATA / "longshort_29.parquet")
menu = pd.read_csv(DATA / "signal_menu.csv").set_index("Acronym")
sharpe = lambda s: s.mean() / s.std() * np.sqrt(12)
tstat = lambda s: s.mean() / s.std() * np.sqrt(len(s))

# ---------------------------------------------------------------- 1. published t against ours
rows = [(s, menu.loc[s, "T-Stat"], tstat(L[s].dropna()))
        for s in L.columns if s in menu.index and pd.notna(menu.loc[s, "T-Stat"])]
d = pd.DataFrame(rows, columns=["signal", "published_t", "our_t"]).set_index("signal")
bar = abs(norm.ppf(0.025 / len(d)))                     # Bonferroni, as in the backtesting lecture
fit = sm.OLS(d.our_t, sm.add_constant(d.published_t)).fit()

fig, ax = plt.subplots(figsize=(9, 4.6))
survive = d.our_t > bar
ax.scatter(d.published_t[~survive], d.our_t[~survive], s=46, color=GREY, label="does not clear the bar")
ax.scatter(d.published_t[survive], d.our_t[survive], s=46, color=RED, label="clears the bar")
ax.axhline(bar, color=RED, linestyle="--", linewidth=1)
ax.text(d.published_t.min(), bar + 0.25, f"Bonferroni bar, t = {bar:.2f}", ha="left", color=RED, fontsize=11)
ax.axhline(0, color="black", linewidth=0.7)
xs = np.linspace(d.published_t.min(), d.published_t.max(), 50)
ax.plot(xs, fit.params["const"] + fit.params["published_t"] * xs, color=BLUE, linewidth=1.6)
ax.text(xs[-1], fit.params["const"] + fit.params["published_t"] * xs[-1] - 2.4,
        f"fitted line, $R^2$ = {fit.rsquared:.2f}", ha="right", color=BLUE, fontsize=11)
ax.set_xlabel("t-statistic in the published paper")
ax.set_ylabel("t-statistic in our sample")
ax.legend(frameon=False, loc="lower right")
fig.savefig(OUT / "wstw_replication.pdf"); plt.close(fig)

# ---------------------------------------------------------------- 2. low volatility: growth of $1
x = L["IdioVol3F"].dropna()
w = (1 + x).cumprod()
peak_date = w.idxmax()
trough_date = w.loc[peak_date:].idxmin()

fig, ax = plt.subplots(figsize=(9, 4.0))
ax.plot(w.index, w.values, color="#333333", linewidth=1.5)
ax.set_yscale("log")
ax.scatter([peak_date, trough_date], [w.max(), w.loc[trough_date]], color=RED, s=30, zorder=3)
ax.annotate(f"peak, {peak_date:%b %Y}: ${w.max():.2f}", xy=(peak_date, w.max()), xytext=(-150, 2),
            textcoords="offset points", color=RED, fontsize=11)
ax.annotate(f"trough, {trough_date:%b %Y}: ${w.loc[trough_date]:.2f}", xy=(trough_date, w.loc[trough_date]),
            xytext=(-190, -4), textcoords="offset points", color=RED, fontsize=11)
ax.set_ylabel("growth of \\$1 (log scale)")
fig.savefig(OUT / "wstw_lowvol_growth.pdf"); plt.close(fig)

# ---------------------------------------------------------------- 3. the same returns at 1x, 2x, 3x
start = "1997-01-01"
fig, ax = plt.subplots(figsize=(9, 4.0))
for k, colour in [(1, "#333333"), (2, BLUE), (3, RED)]:
    path = (1 + k * x.loc[start:]).cumprod()
    if (k * x.loc[start:] <= -1).any() or (path <= 0).any():
        cut = path.index[(path <= 0) | (k * x.loc[start:] <= -1)][0]
        path = path.loc[:cut].clip(lower=0)
    ax.plot(path.index, path.values, color=colour, linewidth=1.6, label=f"{k}x leverage")
ax.axhline(0, color="black", linewidth=0.7)
ax.set_ylabel("growth of \\$1 invested in Jan 1997")
import matplotlib.dates as mdates
ax.xaxis.set_major_locator(mdates.YearLocator()); ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax.legend(frameon=False, loc="upper left")
fig.savefig(OUT / "wstw_leverage.pdf"); plt.close(fig)

# ================================================================ the numbers the slides quote
def maxdd(s):
    c = (1 + s).cumprod(); dd = c / c.cummax() - 1
    return dd.min(), dd.idxmin()

print(f"REPLICATION: {len(d)} strategies with a published t;  bar {bar:.2f};  clear the bar {int(survive.sum())};  "
      f"|t|>1.96 {(d.our_t > 1.96).sum()};  wrong sign {(d.our_t < 0).sum()};  R2 {fit.rsquared:.2f};  "
      f"mean published t {d.published_t.mean():.2f}, ours {d.our_t.mean():.2f}")
fam = ["IdioVol3F", "RealizedVol", "MaxRet"]
c = L[fam].corr()
print(f"VOLATILITY FAMILY corr: {c.loc['IdioVol3F','RealizedVol']:.2f}, {c.loc['IdioVol3F','MaxRet']:.2f}, "
      f"{c.loc['RealizedVol','MaxRet']:.2f};  average pairwise corr across all 29: "
      f"{L.corr().values[np.triu_indices(L.shape[1], 1)].mean():.2f}")
cagr = (1 + x.loc[:"1997-12-31"]).prod() ** (12 / len(x.loc[:"1997-12-31"])) - 1
print(f"LOW VOL: 1980-97 {cagr:.1%}/yr;  1999 {(1 + x.loc['1999']).prod() - 1:.1%};  peak {peak_date:%Y-%m} ${w.max():.2f};  "
      f"trough {trough_date:%Y-%m} ${w.loc[trough_date]:.2f}")
for k in (1, 2, 3):
    v, t = maxdd(k * x)
    print(f"  drawdown at {k}x: {v:.1%}, trough {t:%Y-%m}")
cs = x.cumsum()
print(f"  summing returns: {(cs - cs.cummax()).min():.1%}")
print(f"SHARPE 1980-90 {sharpe(x.loc[:'1990-12-31']):.2f};  1991-2000 {sharpe(x.loc['1991-01-01':]):.2f}")

path = np.array([0.10, -0.20, -0.20, 0.05])
for k in (1, 2):
    g = np.cumprod(1 + k * path)
    print(f"WORKED PROBLEM at {k}x: values {np.round(g, 4)};  drawdown {(g.min() / g[:np.argmin(g)].max() - 1):.1%}")
s = np.cumsum(path)
g3 = np.cumprod(1 + 3 * path)
print(f"WORKED PROBLEM at 3x: values {np.round(g3, 4)};  drawdown {(g3.min() / g3[:np.argmin(g3)].max() - 1):.1%}")
print(f"WORKED PROBLEM summing: running sums {np.round(s * 100, 1)} -> drawdown {(s.min() - s[:np.argmin(s)].max()) * 100:.0f} points")
