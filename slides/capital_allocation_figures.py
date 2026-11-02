"""
Figures and numbers for slides/capital_allocation_1.tex, _2.tex and _3.tex

    python slides/capital_allocation_figures.py

Data: the six Fama-French factors, 1980-2026 (assets/data/ff_monthly.csv), and the 29 published
long-shorts, 1980-2000 (assets/data/longshort_29.parquet). Deck III adds five asset classes, 1963-2016 (assets/data/GlobalFinMonthly.csv).
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

GREY, RED, BLUE, LIGHT = "#6B6B6B", "#B03A2E", "#2E5C8A", "#BDBDBD"
plt.rcParams.update({
    "font.size": 13, "axes.titlesize": 14, "axes.labelsize": 13,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": False, "figure.dpi": 150, "savefig.bbox": "tight",
})

ff = pd.read_csv(DATA / "ff_monthly.csv", index_col=0, parse_dates=True)
L  = pd.read_parquet(DATA / "longshort_29.parquet")
SIX = ["Mkt-RF", "SMB", "HML", "RMW", "CMA", "UMD"]
F  = ff[SIX].dropna()
m  = F["Mkt-RF"]
sharpe = lambda x: x.mean() / x.std() * np.sqrt(12)
nz = lambda w: w / np.abs(w).sum()
print(f"six factors {F.index[0]:%Y-%m} to {F.index[-1]:%Y-%m}, {len(F)} months; "
      f"29 long-shorts {L.index[0]:%Y-%m} to {L.index[-1]:%Y-%m}, {len(L)} months\n")

# ================================================================== CAPITAL ALLOCATION I
print("=== CAPITAL ALLOCATION I ===")
print(f"market: mean {m.mean()*12:.1%}, vol {m.std()*np.sqrt(12):.1%}, Sharpe {sharpe(m):.2f}")
for g in [1, 2, 5, 10]:
    x = m.mean() * 12 / (g * m.var() * 12)
    print(f"  gamma {g:2d}: weight {x:.2f}, volatility {x * m.std() * np.sqrt(12):.1%}")

mu, S = F.mean() * 12, F.cov() * 12
W = pd.Series(np.linalg.solve(S, mu), index=SIX)
print("\nSigma^-1 mu, six factors:", W.round(2).to_dict(), f"Sharpe {sharpe(F @ W):.2f}")

# alpha bets on the five non-market factors
rows, H5 = {}, {}
for c in SIX[1:]:
    r = sm.OLS(F[c], sm.add_constant(m)).fit()
    H5[c] = F[c] - r.params["Mkt-RF"] * m
    rows[c] = {"alpha": r.params["const"] * 12, "sd": r.resid.std() * np.sqrt(12)}
A5 = pd.DataFrame(rows).T; A5["AR"] = A5.alpha / A5.sd; A5["w"] = A5.alpha / A5.sd ** 2; H5 = pd.DataFrame(H5)
book5 = (H5 * A5.w).sum(axis=1)
print("\nhedged factors:\n", A5.round(3).to_string())
print(f"book Sharpe {sharpe(book5):.2f}, independence ideal {np.sqrt((A5.AR ** 2).sum()):.2f}, "
      f"market + book {np.sqrt(sharpe(m) ** 2 + sharpe(book5) ** 2):.2f}, HML-CMA residual correlation {H5.corr().loc['HML', 'CMA']:.2f}")

# pooling the 29
s = L.apply(sharpe); iu = np.triu_indices(29, 1); rho = L.corr().values[iu].mean()
Z = L / L.std()
rng = np.random.default_rng(0)
Ns = np.arange(1, 30)
pooled = [np.mean([sharpe(Z[rng.choice(L.columns, n, replace=False)].mean(axis=1)) for _ in range(300)]) for n in Ns]
print(f"\n29 long-shorts: mean Sharpe {s.mean():.2f}, best {s.max():.2f}, mean correlation {rho:.3f}")
print(f"  pool of 29 {sharpe(Z.mean(axis=1)):.3f}; sqrt(N)*mean {np.sqrt(29) * s.mean():.2f}; "
      f"with correlation {s.mean() * np.sqrt(29 / (1 + 28 * rho)):.3f}; limit as N grows {s.mean() / np.sqrt(rho):.2f}")
fig, ax = plt.subplots(figsize=(7, 3.9))
ax.plot(Ns, np.sqrt(Ns) * s.mean(), color=LIGHT, lw=2)
ax.plot(Ns, s.mean() * np.sqrt(Ns / (1 + (Ns - 1) * rho)), color=BLUE, lw=2)
ax.plot(Ns, pooled, "o", color=RED, ms=4)
ax.text(29.4, np.sqrt(29) * s.mean(), "if uncorrelated", color=GREY, va="center")
ax.text(29.4, 1.46, "with $\\bar\\rho=0.05$", color=BLUE, va="center")
ax.text(29.4, 1.28, "our 29", color=RED, va="center")
ax.set_xlim(0, 38); ax.set_ylim(0, 2.3); ax.set_xticks([1, 5, 10, 15, 20, 25, 29])
ax.set_xlabel("number of strategies pooled, equal volatility"); ax.set_ylabel("Sharpe ratio")
fig.savefig(OUT / "ca_pool.pdf"); plt.close(fig)

# the residuals are not uncorrelated
mk = ff.loc[L.index, "Mkt-RF"]
Hd = pd.DataFrame({c: sm.OLS(L[c], sm.add_constant(mk)).fit().resid for c in L})
off = Hd.corr().values[iu]
pair = np.argmax(np.abs(off))
print(f"\nresidual correlations: mean {off.mean():.2f}, mean absolute {np.abs(off).mean():.2f}, "
      f"worst {Hd.columns[iu[0][pair]]}/{Hd.columns[iu[1][pair]]} {off[pair]:.2f}")
fig, ax = plt.subplots(figsize=(7, 3.5))
ax.hist(off, bins=40, color=GREY)
ax.axvline(0, color="k", lw=0.8)
ax.annotate("MaxRet and RealizedVol\n0.95", xy=(0.95, 3), xytext=(0.72, 20), color=RED, ha="center",
            arrowprops=dict(arrowstyle="-", color=RED))
ax.set_xticks([-0.6, -0.2, 0.2, 0.6, 1.0])
ax.set_xlabel("correlation between two hedged strategies (406 pairs)"); ax.set_ylabel("number of pairs")
fig.savefig(OUT / "ca_resid_corr.pdf"); plt.close(fig)

# ================================================================== CAPITAL ALLOCATION I: THE FRONTIER AND ITS TILTS
# Eight sectors built from Ken French's 49 industries, equal-weighted within each sector, 1980-2026, over T-bills.
from scipy.optimize import brentq, minimize
from scipy.stats import norm
print("\n=== THE FRONTIER ===")
ind = pd.read_parquet(DATA / "ind49_monthly_1926.parquet")
fac = pd.read_parquet(DATA / "factors_monthly_1926.parquet")
SECTORS = {"Tech": ["Hardw", "Softw", "Chips", "LabEq"], "Health": ["Hlth", "MedEq", "Drugs"],
           "Finance": ["Banks", "Insur", "RlEst", "Fin"], "Energy": ["Oil", "Coal"], "Sin": ["Smoke", "Guns", "Beer"],
           "Consumer": ["Food", "Soda", "Hshld", "Clths", "Toys", "Fun", "Books", "Rtail", "Whlsl", "Meals", "PerSv"],
           "Industrial": ["Chems", "Rubbr", "Txtls", "BldMt", "Cnstr", "Steel", "FabPr", "Mach", "ElcEq", "Autos", "Aero",
                          "Ships", "Paper", "Boxes", "Trans", "BusSv", "Agric", "Mines", "Gold"],
           "Utilities": ["Util", "Telcm"]}
ex = ind.sub(fac["RF"], axis=0).loc["1980-01":"2026-06"]
R  = pd.DataFrame({k: ex[v].mean(axis=1) for k, v in SECTORS.items()})
M, C = R.mean() * 12, R.cov() * 12
Ci = np.linalg.inv(C)
one = np.ones(8)
sdv = np.sqrt(np.diag(C))
mkt_s = fac["Mkt-RF"].loc[R.index]
beta_s = R.apply(lambda c: np.cov(c, mkt_s)[0, 1] / mkt_s.var())
print(pd.DataFrame({"mean": M, "vol": sdv, "Sharpe": M / sdv, "beta": beta_s}).round(2).to_string())
SR_T = np.sqrt(M @ Ci @ M)
raw  = pd.Series(Ci @ M, index=R.columns)
wT   = raw / raw.sum()
print(f"tangency: Sharpe {SR_T:.3f}, vol {np.sqrt(wT @ C @ wT):.1%}, mean {wT @ M:.1%}, weights {wT.round(2).to_dict()}")
SR_m = sharpe(mkt_s)
print(f"market Sharpe {SR_m:.2f}")

pt = lambda w: (np.sqrt(w @ C @ w), w @ M)                # (volatility, mean) of weights w
A_, B_, C_ = one @ Ci @ one, one @ Ci @ M, M @ Ci @ M     # the risky-only frontier, weights adding to one
def hyperbola(mus):
    return np.sqrt((A_ * mus ** 2 - 2 * B_ * mus + C_) / (A_ * C_ - B_ ** 2))
mus = np.linspace(0.02, 0.26, 200)
XMAX, YMAX = 0.30, 0.26

def base(ax, dots=True, line=True, curve=True):
    if curve:
        ax.plot(hyperbola(mus), mus, color=LIGHT, lw=1.5)
    if line:
        ax.plot([0, XMAX], [0, SR_T * XMAX], color=RED, lw=2)
    if dots:
        ax.plot(sdv, M, "o", color=GREY, ms=4)
    ax.plot(0, 0, "s", color="k", ms=5)
    ax.set_xlim(0, XMAX); ax.set_ylim(0, YMAX)
    ax.set_xticks([0, .1, .2, .3]); ax.set_xticklabels(["0%", "10%", "20%", "30%"])
    ax.set_yticks([0, .05, .1, .15, .2, .25]); ax.set_yticklabels(["0%", "5%", "10%", "15%", "20%", "25%"])
    ax.set_xlabel("volatility"); ax.set_ylabel("expected return over T-bills")

# everyone wants the line
fig, ax = plt.subplots(figsize=(7.2, 4.2))
base(ax)
for s, dx, dy in [("Tech", .004, .002), ("Sin", .004, -.008), ("Energy", .004, -.004), ("Utilities", -.033, -.008)]:
    ax.text(sdv[R.columns.get_loc(s)] + dx, M[s] + dy, s, color=GREY, fontsize=11)
ax.plot(*pt(wT), "*", color=RED, ms=15, zorder=5); ax.text(pt(wT)[0] - .004, pt(wT)[1] + .009, "tangency", color=RED, ha="right")
ax.plot(mkt_s.std() * np.sqrt(12), mkt_s.mean() * 12, "D", color=BLUE, ms=6); ax.text(mkt_s.std() * np.sqrt(12) - .002, mkt_s.mean() * 12 - .018, "market", color=BLUE, ha="center")
ax.text(.003, .006, "T-bills", fontsize=11)
ax.text(.205, SR_T * .205 + .026, f"slope = Sharpe {SR_T:.2f}", color=RED, ha="center")
fig.savefig(OUT / "ca_frontier.pdf"); plt.close(fig)

# three people on one line
fig, ax = plt.subplots(figsize=(7.2, 4.2))
base(ax, dots=False)
for g in [12, 5.5, 3]:
    x = raw.sum() / g; s_, m_ = SR_T / g, SR_T ** 2 / g
    ax.plot(s_, m_, "o", color=BLUE, ms=9, zorder=5)
    print(f"  gamma {g}: {x:.0%} in the tangency portfolio, volatility {s_:.1%}, mean {m_:.1%}")
    ax.text(s_ + .006, m_ - .014, {12: f"cautious\n$\\gamma=12$, {x:.0%} in tangency", 5.5: f"$\\gamma=5.5$, {x:.0%}", 3: f"aggressive\n$\\gamma=3$, {x:.0%}: borrows"}[g], color=BLUE, fontsize=12, va="top")
ax.plot(*pt(wT), "*", color=RED, ms=15, zorder=6)
fig.savefig(OUT / "ca_frontier_people.pdf"); plt.close(fig)

# the principal: the worst loss you can stand
w_mkt = (1 + mkt_s + fac["RF"].loc[R.index]).cumprod()
dd = (w_mkt / w_mkt.cummax() - 1).min()
print(f"\nmarket worst drawdown 1980-2026, monthly: {dd:.0%}")
mm, vm = fac["Mkt-RF"].loc["1980-01":"2026-06"].mean() * 12, fac["Mkt-RF"].loc["1980-01":"2026-06"].std() * np.sqrt(12)
for loss in [.1, .2, .3, .5]:
    x = loss / abs(dd)
    print(f"  worst loss {loss:.0%}: in the market {x:.0%}, gamma {mm / (x * vm ** 2):.1f}, volatility {x * vm:.1%}")

# the delegate: a stop-loss. Chance of hitting a loss D at some point in a year, continuous monitoring, from the start
def p_stop(D, sr, s, T=1.0):
    mu_ = sr * s
    return norm.cdf((-D - mu_ * T) / (s * np.sqrt(T))) + np.exp(-2 * mu_ * D / s ** 2) * norm.cdf((-D + mu_ * T) / (s * np.sqrt(T)))
fig, ax = plt.subplots(figsize=(7, 3.9))
vols = np.linspace(.01, .30, 200)
for sr, col, lab, y in [(.5, LIGHT, "Sharpe 0.5", 0), (1, RED, "Sharpe 1", 0), (2, BLUE, "Sharpe 2", 0)]:
    pr = [p_stop(.10, sr, s) for s in vols]
    ax.plot(vols, np.array(pr) * 100, color=col if col != LIGHT else GREY, lw=2)
    ax.text(.303, pr[-1] * 100, lab, color=col if col != LIGHT else GREY, va="center")
ax.axhline(10, color="k", lw=.7, ls=":")
ax.plot(brentq(lambda s: p_stop(.10, 1, s) - .10, .01, 1), 10, "o", color=RED, ms=8)
ax.set_xlim(0, .36); ax.set_ylim(0, 70); ax.set_xticks([0, .1, .2, .3]); ax.set_xticklabels(["0%", "10%", "20%", "30%"])
ax.set_xlabel("volatility you run"); ax.set_ylabel("chance of hitting a 10% stop (%)")
fig.savefig(OUT / "ca_stop.pdf"); plt.close(fig)
for sr in [.5, 1, 2]:
    print(f"  stop table, SR {sr}:", {f"{d:.1%}": (round(brentq(lambda s: p_stop(d, sr, s) - .10, .002, 3), 3), round(sr / brentq(lambda s: p_stop(d, sr, s) - .10, .002, 3), 1)) for d in [.05, .075, .10, .20]})
print("  P(stop 10%), SR 1:", {f"{s:.0%}": round(p_stop(.10, 1, s), 3) for s in [.05, .10, .15, .20, .30]})

# human capital. W = financial wealth, H = human capital, h = H / W
# financial portfolio = (1 + h) x_star - h b, where b is the portfolio that mimics your job
GAMMA, h_ = 10, 1.0
xstar = raw / GAMMA
print(f"\nhuman capital: gamma {GAMMA}, h {h_}: x* volatility {np.sqrt(xstar @ C @ xstar):.1%}, in risky assets {xstar.sum():.0%}, Tech {xstar['Tech']:.0%}")
def person(job):
    b = pd.Series(0.0, index=R.columns)
    for k, v in job.items():
        b[k] = v
    w = (1 + h_) * xstar - h_ * b
    return w
PEOPLE = {"Professor (nothing)": {}, "Software engineer (+0.5 Tech)": {"Tech": .5}, "Legal translator (-0.5 Tech)": {"Tech": -.5},
          "Banker (+0.5 Finance)": {"Finance": .5}, "Oil engineer (+0.5 Energy)": {"Energy": .5}}
for name, job in PEOPLE.items():
    w = person(job); s_, m_ = pt(w)
    print(f"  {name:30s} vol {s_:.1%} mean {m_:.1%} Sharpe {m_ / s_:.2f}; Tech {w['Tech']:+.2f}, Finance {w['Finance']:+.2f}, Energy {w['Energy']:+.2f}")

# a safe job: same mix, more risk
ss, sm_ = pt(xstar); ps, pm = pt(person({}))
fig, ax = plt.subplots(figsize=(7.2, 4.2))
base(ax, dots=False)
ax.plot(ss, sm_, "*", color="k", ms=14, zorder=6); ax.text(ss - .004, sm_ + .012, "total portfolio,\nfinancial + job", ha="right", fontsize=10.5)
ax.annotate("", xy=(ps, pm), xytext=(ss, sm_), arrowprops=dict(arrowstyle="->", color=BLUE, lw=1.5))
ax.plot(ps, pm, "o", color=BLUE, ms=9, zorder=5); ax.text(ps + .008, pm - .013, "the professor's\nfinancial account", color=BLUE, fontsize=10.5, va="top")
fig.savefig(OUT / "ca_hc_safe.pdf"); plt.close(fig)

# AI: two accounts, one total portfolio
fig, ax = plt.subplots(figsize=(7.2, 4.2))
base(ax, dots=False)
ax.plot(ss, sm_, "*", color="k", ms=14, zorder=6); ax.text(ss - .006, sm_ + .012, "same total\nportfolio", fontsize=10.5, ha="right")
for name, col, tx, ty, ha in [("Software engineer (+0.5 Tech)", BLUE, .007, -.012, "left"), ("Legal translator (-0.5 Tech)", RED, 0, -.02, "center")]:
    s_, m_ = pt(person(PEOPLE[name]))
    ax.annotate("", xy=(ss, sm_), xytext=(s_, m_), arrowprops=dict(arrowstyle="->", color=col, lw=1, ls="--"))
    ax.plot(s_, m_, "o", color=col, ms=9, zorder=5)
    ax.text(s_ + tx, m_ + ty, {"S": "software engineer's account", "L": "translator's account"}[name[0]], color=col, fontsize=10.5, ha=ha)
fig.savefig(OUT / "ca_hc_ai.pdf"); plt.close(fig)

# everybody on one map
fig, ax = plt.subplots(figsize=(7.4, 4.3))
base(ax, dots=False)
ax.plot(ss, sm_, "*", color="k", ms=13, zorder=6)
for name, lab, dx, dy, ha in [("Professor (nothing)", "professor", .005, -.004, "left"), ("Software engineer (+0.5 Tech)", "software engineer", 0.002, -.017, "center"),
                              ("Legal translator (-0.5 Tech)", "translator", .006, .002, "left"), ("Banker (+0.5 Finance)", "banker", .006, -.003, "left"),
                              ("Oil engineer (+0.5 Energy)", "oil engineer", .006, -.003, "left")]:
    s_, m_ = pt(person(PEOPLE[name]))
    ax.plot(s_, m_, "o", color=BLUE, ms=7, zorder=5); ax.text(s_ + dx, m_ + dy, lab, color=BLUE, fontsize=10.5, ha=ha)
fig.savefig(OUT / "ca_hc_map.pdf"); plt.close(fig)

# ---------- mandates
def max_sr(mu, S, bounds=None):
    n = len(mu)
    r = minimize(lambda w: -(w @ mu) / np.sqrt(w @ S @ w), np.ones(n) / n, bounds=bounds,
                 constraints=[{"type": "eq", "fun": lambda w: w.sum() - 1}], method="SLSQP", options={"maxiter": 2000, "ftol": 1e-12})
    return r.x
# long-only, no leverage
wL = max_sr(M.values, C.values, bounds=[(0, None)] * 8)
SR_L = (wL @ M.values) / np.sqrt(wL @ C.values @ wL)
print(f"\nlong-only tangency: Sharpe {SR_L:.2f}, {dict(zip(R.columns, wL.round(2)))}")
targets = np.linspace(M.min(), M.max(), 60)
lo_s, lo_m = [], []
for t in targets:
    r = minimize(lambda w: w @ C.values @ w, np.ones(8) / 8, bounds=[(0, None)] * 8, method="SLSQP", options={"maxiter": 2000, "ftol": 1e-12},
                 constraints=[{"type": "eq", "fun": lambda w: w.sum() - 1}, {"type": "eq", "fun": lambda w, t=t: w @ M.values - t}])
    lo_s.append(np.sqrt(r.x @ C.values @ r.x)); lo_m.append(t)
lo_s, lo_m = np.array(lo_s), np.array(lo_m)
sL, mL = pt(wL)
fig, ax = plt.subplots(figsize=(7.2, 4.2))
base(ax, dots=False, curve=False)
keep_ = lo_m >= mL
ax.plot([0, sL], [0, mL], color=BLUE, lw=2.5, zorder=4)
ax.plot(lo_s[keep_], lo_m[keep_], color=BLUE, lw=2.5, zorder=4)
ax.plot(sL, mL, "o", color=BLUE, ms=8, zorder=5)
ax.text(.15, .07, "long-only, no borrowing:\nmore risk, no more return", color=BLUE, fontsize=11)
top = lo_s[keep_][-1], lo_m[keep_][-1]
print(f"  long-only frontier ends at volatility {top[0]:.1%}, mean {top[1]:.1%}; the line at that volatility earns {SR_T * top[0]:.1%}")
ax.text(.255, SR_T * .255 - .03, "the line", color=RED)
ax.plot(top[0], top[1], "o", color=BLUE, ms=7, zorder=5); ax.text(top[0] + .005, top[1] - .002, "all Tech", color=BLUE, fontsize=11, va="center")
i20 = np.argmin(np.abs(lo_s[keep_] - .20)) if lo_s[keep_].max() >= .2 else None
fig.savefig(OUT / "ca_mandate_longonly.pdf"); plt.close(fig)
for vol_ in [.156, .18]:
    r = minimize(lambda w: -(w @ M.values), wL, bounds=[(0, None)] * 8, method="SLSQP", options={"maxiter": 2000, "ftol": 1e-12},
                 constraints=[{"type": "eq", "fun": lambda w: w.sum() - 1}, {"type": "eq", "fun": lambda w, s=vol_: w @ C.values @ w - s ** 2}])
    print(f"  no borrowing at {vol_:.1%} volatility: mean {r.x @ M.values:.1%} vs line {SR_T * vol_:.1%}; {dict(zip(R.columns, r.x.round(2)))}")

# exclusions
drop = lambda cols: np.sqrt(M.drop(cols) @ np.linalg.inv(C.drop(cols).drop(columns=cols)) @ M.drop(cols))
SR_noS, SR_noE, SR_noB = drop(["Sin"]), drop(["Energy"]), drop(["Sin", "Energy"])
print(f"\nexclude Energy {SR_noE:.2f}; exclude Sin {SR_noS:.2f}; both {SR_noB:.2f}; Smoke alone in Sin: 'Smoke' Sharpe {sharpe(ex['Smoke']):.2f}")
fig, ax = plt.subplots(figsize=(7.2, 4.2))
base(ax, dots=False, curve=False)
ax.plot([0, XMAX], [0, SR_noB * XMAX], color=GREY, lw=2)
ax.text(.19, SR_T * .19 + .026, f"everything: {SR_T:.2f}\nno energy: {SR_noE:.2f}", color=RED, ha="center")
ax.text(.245, SR_noB * .245 - .03, f"no energy, no tobacco,\nguns, alcohol: {SR_noB:.2f}", color=GREY, ha="center", va="top", fontsize=11)
fig.savefig(OUT / "ca_mandate_esg.pdf"); plt.close(fig)

# factor limit: zero market beta
bv = beta_s.values; Mv = M.values
lam = (bv @ Ci @ Mv) / (bv @ Ci @ bv)
wZ = Ci @ (Mv - lam * bv)
SR_Z = (wZ @ Mv) / np.sqrt(wZ @ C.values @ wZ)
print(f"\nzero-beta frontier: Sharpe {SR_Z:.2f}, against sqrt(T^2 - m^2) = {np.sqrt(SR_T ** 2 - SR_m ** 2):.2f}")
fig, ax = plt.subplots(figsize=(7.2, 4.2))
base(ax, dots=False, curve=False)
ax.plot([0, XMAX], [0, SR_Z * XMAX], color=BLUE, lw=2)
ax.text(.215, SR_T * .215 + .022, f"no limit: {SR_T:.2f}", color=RED, ha="center")
ax.text(.262, SR_Z * .262 - .03, f"zero beta: {SR_Z:.2f}", color=BLUE, ha="center")
fig.savefig(OUT / "ca_mandate_beta.pdf"); plt.close(fig)

# tracking error, weights adding to one (Roll 1992). The benchmark: the sector mix that best tracks the market
bm = np.linalg.lstsq(np.c_[np.ones(len(R)), R.values], mkt_s.values, rcond=None)[0][1:]
wB = bm / bm.sum()
print(f"\nbenchmark {dict(zip(R.columns, wB.round(2)))}: Sharpe {(wB @ Mv) / np.sqrt(wB @ C.values @ wB):.2f}, correlation with the market {np.corrcoef(R @ wB, mkt_s)[0, 1]:.3f}")
Aq = Ci - np.outer(Ci @ one, one @ Ci) / (one @ Ci @ one)              # active portfolios add to zero
fB = C.values @ wB
Gq = np.array([[Mv @ Aq @ Mv, Mv @ Aq @ fB], [Mv @ Aq @ fB, fB @ Aq @ fB]])
Lq = np.linalg.cholesky(Gq)
sB, mB = pt(wB)
def ellipse(te):
    th = np.linspace(0, 2 * np.pi, 400)
    y = te * Lq @ np.vstack([np.cos(th), np.sin(th)])
    return np.sqrt(sB ** 2 + 2 * y[1] + te ** 2), mB + y[0]
def best_te(te):
    a = Aq @ Mv; a = a * te / np.sqrt(a @ C.values @ a)
    return wB + a
fig, ax = plt.subplots(figsize=(7.2, 4.2))
base(ax, dots=False)
for te, col in [(.05, BLUE), (.02, GREY)]:
    ax.plot(*ellipse(te), color=col, lw=1.6)
    w_ = best_te(te); s_, m_ = pt(w_)
    ax.plot(s_, m_, "o", color=col, ms=7, zorder=5)
    print(f"  tracking error {te:.0%}: volatility {s_:.1%}, mean {m_:.1%}, Sharpe {m_ / s_:.2f}, active share of weights {np.abs(w_ - wB).sum() / 2:.0%}, beta {w_ @ bv:.2f}")
ax.plot(sB, mB, "D", color="k", ms=6, zorder=6); ax.text(.108, mB - .012, "benchmark", ha="right", fontsize=11)
wline = xs = raw / raw.sum() * (sB / np.sqrt(wT @ C @ wT))
print(f"  on the line at the benchmark's volatility: mean {SR_T * sB:.1%}; distance from the benchmark in tracking error (with T-bills) {np.sqrt((wline - wB) @ C.values @ (wline - wB)):.1%}")
print(f"  tangency tracking error from the benchmark {np.sqrt((wT.values - wB) @ C.values @ (wT.values - wB)):.1%}")
ax.text(.226, .118, "5% tracking error", color=BLUE, fontsize=11)
ax.text(.226, .100, "2% tracking error", color=GREY, fontsize=11)
fig.savefig(OUT / "ca_mandate_te.pdf"); plt.close(fig)

# the price of each mandate
price = pd.Series({"no limits": SR_T, "no energy": SR_noE, "tracking error 5%": pt(best_te(.05))[1] / pt(best_te(.05))[0], "long-only": SR_L,
                   "no tobacco, guns, alcohol": SR_noS, "zero market beta": SR_Z, "tracking error 2%": pt(best_te(.02))[1] / pt(best_te(.02))[0], "the market": SR_m}).sort_values()
print("\nprice:", price.round(2).to_dict())
fig, ax = plt.subplots(figsize=(7.2, 3.9))
ax.barh(price.index, price.values, color=[RED if k == "no limits" else GREY if k != "the market" else BLUE for k in price.index], height=.65)
for i, v in enumerate(price.values):
    ax.text(v + .012, i, f"{v:.2f}", va="center")
ax.set_xlim(0, 1); ax.set_xlabel("Sharpe ratio of the best line you can reach")
fig.savefig(OUT / "ca_mandate_price.pdf"); plt.close(fig)

# ---------- the six factors: two portfolios draw the curve, one portfolio takes any size, and what a new factor adds
print("\n=== THE SIX FACTORS ===")
FACN = {"Mkt-RF": "Market", "SMB": "SMB", "HML": "HML", "RMW": "RMW", "CMA": "CMA", "UMD": "UMD"}
mF, SF = F.mean().values * 12, F.cov().values * 12
WF = np.linalg.solve(SF, mF); TF = WF / WF.sum()
MF = np.linalg.solve(SF, np.ones(6)); MF = MF / MF.sum()
mean_T, vol_T, mean_M, vol_M = TF @ mF, np.sqrt(TF @ SF @ TF), MF @ mF, np.sqrt(MF @ SF @ MF)
SR_F = mean_T / vol_T
print("tangency:", dict(zip(SIX, TF.round(2))), f"mean {mean_T:.1%}, vol {vol_T:.1%}, Sharpe {SR_F:.3f}")
print("minimum variance:", dict(zip(SIX, MF.round(2))), f"mean {mean_M:.1%}, vol {vol_M:.1%}, Sharpe {mean_M / vol_M:.3f}")
aa = np.linspace(-12, 30, 600)
curve = np.array([(np.sqrt(w @ SF @ w), w @ mF) for w in [a_ * TF + (1 - a_) * MF for a_ in aa]])
def dots(ax):
    ax.scatter(np.sqrt(np.diag(SF)), mF, s=26, color=GREY, zorder=3)
    for c_, v_, m_ in zip(SIX, np.sqrt(np.diag(SF)), mF):
        ax.annotate(FACN[c_], (v_, m_), xytext=(5, 4), textcoords="offset points", fontsize=11, color=GREY)

fig, ax = plt.subplots(figsize=(7, 4.2))
ax.plot(curve[:, 0], curve[:, 1], color=LIGHT, lw=2)
dots(ax)
ax.plot(vol_T, mean_T, "*", color=RED, ms=16, zorder=5); ax.plot(vol_M, mean_M, "o", color=BLUE, ms=8, zorder=5)
ax.annotate("tangency", (vol_T, mean_T), xytext=(-10, 14), textcoords="offset points", color=RED, ha="right")
ax.annotate("minimum variance", (vol_M, mean_M), xytext=(-8, -24), textcoords="offset points", color=BLUE, ha="center")
ax.set_xlim(0, .18); ax.set_ylim(0, .12)
ax.xaxis.set_major_formatter(lambda v, _: f"{v:.0%}"); ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0%}")
ax.set_xlabel("volatility"); ax.set_ylabel("expected return over T-bills")
fig.savefig(OUT / "ca_fac_curve.pdf"); plt.close(fig)

GOALS = {"$\\gamma=5$": WF.sum() / 5, "10% volatility": .10 / vol_T, "8% return": .08 / mean_T}
print(f"gamma 1: multiple of the tangency portfolio {WF.sum():.1f}, mean {SR_F ** 2:.0%}, volatility {SR_F:.0%}")
for k_, x_ in GOALS.items():
    print(f"  {k_:16s} multiple {x_:.2f}, mean {x_ * mean_T:.1%}, volatility {x_ * vol_T:.1%}, Sharpe {SR_F:.2f}")
fig, ax = plt.subplots(figsize=(7, 4.2))
ax.plot(curve[:, 0], curve[:, 1], color=LIGHT, lw=2)
ax.plot([0, .26], [0, .26 * SR_F], color=RED, lw=2)
dots(ax)
ax.plot(vol_T, mean_T, "*", color=RED, ms=14, zorder=5); ax.plot(vol_M, mean_M, "o", color=BLUE, ms=7, zorder=5)
for k_, x_ in GOALS.items():
    ax.plot(x_ * vol_T, x_ * mean_T, "o", color=RED, ms=8, zorder=5)
    ax.annotate(k_, (x_ * vol_T, x_ * mean_T), xytext=(-8, 6), textcoords="offset points", ha="right")
ax.annotate("tangency", (vol_T, mean_T), xytext=(10, 13), textcoords="offset points", color=RED, ha="right")
ax.set_xlim(0, .26); ax.set_ylim(0, .30)
ax.xaxis.set_major_formatter(lambda v, _: f"{v:.0%}"); ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0%}")
ax.set_xlabel("volatility"); ax.set_ylabel("expected return over T-bills")
fig.savefig(OUT / "ca_fac_goals.pdf"); plt.close(fig)

# does a new factor move the frontier? regress it on the tangency portfolio of the other five, and on all five
print("what each factor adds to the other five:")
SPAN = {}
for c_ in SIX:
    oth = [o for o in SIX if o != c_]
    w5 = np.linalg.solve(F[oth].cov(), F[oth].mean()); t5 = (F[oth] @ (w5 / w5.sum())).rename("tangency")
    r_t = sm.OLS(F[c_], sm.add_constant(t5)).fit(); r_a = sm.OLS(F[c_], sm.add_constant(F[oth])).fit()
    ar_ = r_a.params["const"] / r_a.resid.std() * np.sqrt(12)
    SPAN[c_] = dict(sr=sharpe(F[c_]), alpha=r_a.params["const"] * 12, se=r_a.bse["const"] * 12, t=r_a.tvalues["const"], a_t=r_t.params["const"] * 12, ar=ar_, without=sharpe(t5), check=np.sqrt(sharpe(t5) ** 2 + ar_ ** 2))
    print(f"  {FACN[c_]:7s} Sharpe {SPAN[c_]['sr']:.2f}; alpha on all five {SPAN[c_]['alpha']:6.2%} +/- {SPAN[c_]['se']:.2%}, t {SPAN[c_]['t']:5.2f}; alpha on their tangency {SPAN[c_]['a_t']:6.2%}; "
          f"appraisal ratio {ar_:.2f}; best Sharpe without {SPAN[c_]['without']:.2f}, with {SR_F:.2f}, sqrt(without^2 + AR^2) {SPAN[c_]['check']:.3f}")
fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.0), sharex=True, sharey=True)
for ax, c_ in zip(axes, ["HML", "UMD"]):
    oth = [o for o in SIX if o != c_]
    m5, S5 = F[oth].mean().values * 12, F[oth].cov().values * 12
    w5 = np.linalg.solve(S5, m5); t5_ = w5 / w5.sum(); g5 = np.linalg.solve(S5, np.ones(5)); g5 = g5 / g5.sum()
    cv5 = np.array([(np.sqrt(w @ S5 @ w), w @ m5) for w in [a_ * t5_ + (1 - a_) * g5 for a_ in aa]])
    s5 = (t5_ @ m5) / np.sqrt(t5_ @ S5 @ t5_)
    ax.plot(cv5[:, 0], cv5[:, 1], color=LIGHT, lw=4); ax.plot([0, .16], [0, .16 * s5], color=LIGHT, lw=4, label="without it")
    ax.plot(curve[:, 0], curve[:, 1], color=RED, lw=1.4); ax.plot([0, .16], [0, .16 * SR_F], color=RED, lw=1.4, label="with it")
    i_ = SIX.index(c_)
    ax.plot(np.sqrt(SF[i_, i_]), mF[i_], "o", color="k", ms=7, zorder=5)
    ax.annotate(FACN[c_], (np.sqrt(SF[i_, i_]), mF[i_]), xytext=(-6, 7), textcoords="offset points", ha="right")
    ax.set_title(f"{FACN[c_]}: alpha {SPAN[c_]['alpha']:.1%}, best Sharpe {s5:.2f} $\\to$ {SR_F:.2f}")
    ax.set_xlim(0, .16); ax.set_ylim(0, .14); ax.set_xlabel("volatility")
    ax.xaxis.set_major_formatter(lambda v, _: f"{v:.0%}"); ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0%}")
axes[0].set_ylabel("expected return over T-bills"); axes[0].legend(frameon=False, loc="upper left")
fig.tight_layout()
fig.savefig(OUT / "ca_fac_span.pdf"); plt.close(fig)

# ================================================================== CAPITAL ALLOCATION II: FACTORS AND ALPHAS
print("\n=== FACTORS AND ALPHAS ===")
# what persists: the market premium over long windows, and industries window on window
X = ind.sub(fac["RF"], axis=0)
mk_all = fac["Mkt-RF"]
windows = [("1927-46", "1927", "1946"), ("1947-66", "1947", "1966"), ("1967-86", "1967", "1986"), ("1987-06", "1987", "2006"), ("2007-26", "2007", "2026")]
pm = [mk_all.loc[a:b].mean() * 12 for _, a, b in windows]
pu = [fac["UMD"].loc[a:b].mean() * 12 for _, a, b in windows]
print("market by window:", np.round(pm, 3), " UMD by window:", np.round(pu, 3))
dec_ = mk_all.groupby((mk_all.index.year // 10) * 10).mean()
print(f"market premium positive in {(dec_ > 0).sum()} of {len(dec_)} decades")
def fit_window(Y, n):
    out = {}
    for c in Y:
        y = Y[c].dropna()
        if len(y) >= n:
            r = sm.OLS(y, sm.add_constant(mk_all.loc[y.index])).fit()
            out[c] = (r.params.iloc[0] * 12, r.params.iloc[1], r.resid.std() * np.sqrt(12))
    return pd.DataFrame(out, index=["alpha", "beta", "sd"]).T
for yrs in [3, 5, 10]:
    rows_ = []
    for y0 in range(1927, 2026 - 2 * yrs + 2, yrs):
        a = fit_window(X.loc[str(y0):str(y0 + yrs - 1)], yrs * 10); b = fit_window(X.loc[str(y0 + yrs):str(y0 + 2 * yrs - 1)], yrs * 10)
        j_ = a.join(b, lsuffix="1", rsuffix="2").dropna()
        rows_.append((j_.alpha1.corr(j_.alpha2), j_.beta1.corr(j_.beta2), j_.sd1.corr(j_.sd2)))
    print(f"  49 industries, {yrs}-year window on the next: correlation of alpha {np.mean(rows_, axis=0)[0]:+.2f}, beta {np.mean(rows_, axis=0)[1]:+.2f}, residual vol {np.mean(rows_, axis=0)[2]:+.2f}")
mid = len(L) // 2
a1 = pd.Series({c: sm.OLS(L[c].iloc[:mid], sm.add_constant(mk.iloc[:mid])).fit().params.iloc[0] for c in L})
a2 = pd.Series({c: sm.OLS(L[c].iloc[mid:], sm.add_constant(mk.iloc[mid:])).fit().params.iloc[0] for c in L})
print(f"  the 29 published strategies, first half on second half: correlation of alpha {a1.corr(a2):.2f}")
fig, ax = plt.subplots(figsize=(6.4, 3.6))
xp = np.arange(5)
ax.bar(xp - .19, np.array(pm) * 100, .38, color=GREY, label="market")
ax.bar(xp + .19, np.array(pu) * 100, .38, color=RED, label="UMD")
ax.set_xticks(xp); ax.set_xticklabels([w[0] for w in windows]); ax.set_ylabel("average return, % a year"); ax.set_ylim(0, 14); ax.legend(frameon=False, ncol=2, loc="upper left")
fig.savefig(OUT / "ca_persist.pdf"); plt.close(fig)

# correlation is an angle: the best combination is a vector, and each Sharpe ratio is its shadow on that strategy's direction
def angle_panel(ax, s1, s2, theta_deg, title, lim=None):
    th = np.radians(theta_deg)
    e1, e2 = np.array([np.cos(th / 2), np.sin(th / 2)]), np.array([np.cos(th / 2), -np.sin(th / 2)])
    if s1 != s2:                                        # the right-angle case with unequal Sharpes: axes
        e1, e2 = np.array([1.0, 0.0]), np.array([0.0, 1.0])
    A_m = np.array([e1, e2]); P = np.linalg.solve(A_m, np.array([s1, s2]))
    f1, f2 = s1 * e1, s2 * e2
    for f, e, lab in [(f1, e1, "A"), (f2, e2, "B")]:
        ax.plot([0, e[0] * 1.45 * max(s1, s2)], [0, e[1] * 1.45 * max(s1, s2)], color=LIGHT, lw=1)
    ax.plot([0, f1[0]], [0, f1[1]], color=BLUE, lw=3); ax.plot([0, f2[0]], [0, f2[1]], color=BLUE, lw=3)
    ax.plot([f1[0], P[0]], [f1[1], P[1]], color=GREY, lw=1, ls="--"); ax.plot([f2[0], P[0]], [f2[1], P[1]], color=GREY, lw=1, ls="--")
    ax.annotate("", xy=P, xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=RED, lw=2.2))
    ax.plot(0, 0, "o", color="k", ms=4)
    ax.set_aspect("equal"); ax.axis("off")
    if lim:
        ax.set_xlim(*lim[0]); ax.set_ylim(*lim[1])
    ax.set_title(title, fontsize=13)
    return P, f1, f2, e1, e2
fig, axes = plt.subplots(1, 3, figsize=(11, 3.9))
for ax, th, rho in zip(axes, [60, 90, 120], [.5, 0, -.5]):
    P, f1, f2, e1, e2 = angle_panel(ax, 1, 1, th, f"$\\rho={rho:+.1f}$, angle {th}$^\\circ$", lim=((-.25, 2.75), (-1.5, 1.5)))
    srv = np.linalg.norm(P)
    print(f"  angle {th}: combined {srv:.3f}, formula {np.sqrt(2 / (1 + rho)):.3f}")
    ax.text(P[0] + .07, 0, f"{srv:.2f}", color=RED, ha="left", va="center", fontsize=15, fontweight="bold")
    ax.text(f1[0] - .12, f1[1] + .03, "A: 1.0", color=BLUE, ha="right", fontsize=11.5); ax.text(f2[0] - .12, f2[1] - .07, "B: 1.0", color=BLUE, ha="right", va="top", fontsize=11.5)
fig.savefig(OUT / "ca_angle_three.pdf"); plt.close(fig)
fig, ax = plt.subplots(figsize=(4.7, 3.6))
P, f1, f2, e1, e2 = angle_panel(ax, 1.0, 0.5, 90, "", lim=((-.1, 1.5), (-.08, .78)))
ax.text(.5, -.07, "$SR_A = 1.0$", color=BLUE, ha="center"); ax.text(-.02, .25, "$SR_B = 0.5$", color=BLUE, ha="right", va="center")
ax.text(.42, .36, "1.12", color=RED, fontsize=15, fontweight="bold", ha="right")
fig.savefig(OUT / "ca_angle_right.pdf"); plt.close(fig)

# a taste of Black-Litterman: prior alpha zero, one view on HML, three levels of confidence
Hf_ = pd.DataFrame({c: F[c] - sm.OLS(F[c], sm.add_constant(m)).fit().params.iloc[1] * m for c in SIX[1:]})
Sf_ = Hf_.cov().values * 12
TAU = 0.05
Pv = np.array([[0, 1, 0, 0, 0.0]]); Qv = np.array([0.05])
fig, ax = plt.subplots(figsize=(7, 3.8))
for k, (om, col, lab) in enumerate([(.01, RED, "very sure, $\\omega=1\\%$"), (.03, BLUE, "$\\omega=3\\%$"), (.08, LIGHT, "unsure, $\\omega=8\\%$")]):
    post = TAU * Sf_ @ Pv.T @ np.linalg.inv(Pv @ (TAU * Sf_) @ Pv.T + np.array([[om ** 2]])) @ Qv
    print(f"  BL, HML view 5%, omega {om:.0%}: posterior {dict(zip(Hf_.columns, post.round(4)))}; shrink factor {post[1] / .05:.2f}")
    ax.bar(np.arange(5) + (k - 1) * .27, post * 100, .27, color=col, label=lab)
ax.axhline(0, color="k", lw=.7); ax.axhline(5, color=GREY, lw=.8, ls=":"); ax.text(4.45, 5.08, "the view: 5%", color=GREY, ha="right", fontsize=11)
ax.set_xticks(np.arange(5)); ax.set_xticklabels(Hf_.columns); ax.set_ylabel("alpha you act on, % a year"); ax.legend(frameon=False, loc="upper right", bbox_to_anchor=(1.0, .88))
fig.savefig(OUT / "ca_bl.pdf"); plt.close(fig)
print("  prior sd of HML's alpha:", round(np.sqrt(TAU * Sf_[1, 1]), 4))

# the Apple arithmetic
sig_a, hz = .25, 30 / 252
for p_ in [.6, .55]:
    a_ = (2 * p_ - 1) * .04; sd_h = sig_a * np.sqrt(hz); ar = a_ / sd_h / np.sqrt(hz)
    print(f"  Apple, right {p_:.0%}: alpha {a_:.2%} over 6 weeks, sd {sd_h:.1%}, IC at score 1 {a_ / sd_h:.3f}, AR {ar:.2f}, volatility given in a Sharpe-1, 10% book {ar * .10:.1%}, weight {ar * .10 / sig_a:.1%}")

# ================================================================== CAPITAL ALLOCATION III
# Sensitivity of the optimizer, which input drives it, and the race between real differences and estimation error.
print("\n=== CAPITAL ALLOCATION III ===")
print(f"in sample: mean-variance {sharpe(F @ W):.2f}, 1/N {sharpe(F.mean(axis=1)):.2f}, best single {F.apply(sharpe).max():.2f}")
for c in SIX:
    sd, se_m, se_v = F[c].std() * np.sqrt(12), F[c].std() * np.sqrt(12) / np.sqrt(len(F) / 12), F[c].std() * np.sqrt(12) / np.sqrt(2 * len(F))
    print(f"  {c:7s} mean {F[c].mean()*12:6.1%} +/- {se_m:.1%}   vol {sd:6.1%} +/- {se_v:.1%}")
rho_ = F.corr().loc["Mkt-RF", "HML"]
print(f"  correlation Mkt-RF/HML {rho_:.2f} +/- {(1 - rho_ ** 2) / np.sqrt(len(F)):.2f}")

# ---------- the amplifier: two assets, same volatility, weights add to one
AVG = .08
print("amplifier (1+rho)/(1-rho), weight on asset 1 at a 1pp gap, average mean 8%:")
for r_ in [0, .5, .8, .9, .95]:
    print(f"  rho {r_:.2f}: amplifier {(1 + r_) / (1 - r_):5.1f}, weight {.5 + .01 / (4 * AVG) * (1 + r_) / (1 - r_):.0%}")
gaps = np.linspace(-.02, .02, 101)
SEQ = {0: "#BDBDBD", .5: "#D9A79F", .8: "#C4685B", .9: "#8E2A20"}
fig, ax = plt.subplots(figsize=(7.2, 4.0))
ax.axhspan(0, 100, color="#F4F4F4", lw=0)
for r_, col in SEQ.items():
    ax.plot(gaps * 100, (.5 + gaps / (4 * AVG) * (1 + r_) / (1 - r_)) * 100, color=col, lw=2.2)
for r_ in SEQ:
    ax.text(2.07, (.5 + .02 / (4 * AVG) * (1 + r_) / (1 - r_)) * 100 + {0: -9, .5: 6}.get(r_, 0), f"$\\rho={r_}$", color="k", va="center")
ax.axhline(50, color=GREY, lw=.6, ls=":")
ax.text(-1.95, 88, "shaded: long both assets", color=GREY, fontsize=11)
ax.set_xlim(-2, 2.6); ax.set_ylim(-100, 200); ax.set_xticks([-2, -1, 0, 1, 2]); ax.set_yticks([-100, -50, 0, 50, 100, 150, 200])
ax.set_xlabel("gap in expected returns, asset 1 minus asset 2 (pp)"); ax.set_ylabel("weight on asset 1 (%)")
fig.savefig(OUT / "ca_amplifier.pdf"); plt.close(fig)

# ---------- a real pair
HC = ex[["Hardw", "Chips"]]
yrs = len(HC) / 12
mH, mC, sH, sC, rHC = HC.Hardw.mean() * 12, HC.Chips.mean() * 12, HC.Hardw.std() * np.sqrt(12), HC.Chips.std() * np.sqrt(12), HC.corr().iloc[0, 1]
vol_lev, vol_spr = (HC.Hardw + HC.Chips).std() * np.sqrt(12), (HC.Chips - HC.Hardw).std() * np.sqrt(12)
gap, se_gap = mC - mH, vol_spr / np.sqrt(yrs)
wC = lambda g: (lambda w: w[1] / w.sum())(np.linalg.solve(HC.cov().values * 12, np.array([(mH + mC) / 2 - g / 2, (mH + mC) / 2 + g / 2])))
print(f"Hardware {mH:.1%} +/- {sH / np.sqrt(yrs):.1%}, vol {sH:.1%}, Sharpe {mH / sH:.2f}; Chips {mC:.1%} +/- {sC / np.sqrt(yrs):.1%}, vol {sC:.1%}, Sharpe {mC / sC:.2f}; correlation {rHC:.2f}")
print(f"  Sharpe ratio {(mH / sH) / (mC / sC):.2f} of Chips against correlation {rHC:.2f}")
print(f"  vol of Hardw+Chips {vol_lev:.1%}, vol of Chips-Hardw {vol_spr:.1%}, variance ratio {(vol_lev / vol_spr) ** 2:.1f}, amplifier {(1 + rHC) / (1 - rHC):.1f}")
print(f"  gap {gap:.1%} +/- {se_gap:.1%}, t {gap / se_gap:.2f}; weight on Chips at gap-1se {wC(gap - se_gap):.0%}, at gap {wC(gap):.0%}, at gap+1se {wC(gap + se_gap):.0%}; equal means {wC(0):.0%}")

fig, ax = plt.subplots(figsize=(5.2, 4.6))
ax.scatter(HC.Hardw * 100, HC.Chips * 100, s=9, color=LIGHT, lw=0)
c0 = HC.mean().values * 100
def arrow(dx, dy, col):
    ax.annotate("", xy=(c0[0] + dx, c0[1] + dy), xytext=(c0[0] - dx, c0[1] - dy), arrowprops=dict(arrowstyle="<->", color=col, lw=2.2))
L_ = 2 * (HC.Hardw + HC.Chips).std() * 100 / np.sqrt(2) / np.sqrt(2)
S_ = 2 * (HC.Chips - HC.Hardw).std() * 100 / np.sqrt(2) / np.sqrt(2)
arrow(L_, L_, BLUE); arrow(S_, -S_, RED)
ax.text(-38, 36, f"level: buy both\nvolatility {vol_lev:.0%} a year", color=BLUE, ha="left", va="top")
ax.text(38, -38, f"spread: Chips minus Hardware\nvolatility {vol_spr:.0%} a year", color=RED, ha="right", va="bottom")
ax.set_xlim(-40, 40); ax.set_ylim(-40, 40); ax.set_aspect("equal")
ax.set_xlabel("Hardware, monthly excess return (%)"); ax.set_ylabel("Chips, monthly excess return (%)")
fig.savefig(OUT / "ca_pair_scatter.pdf"); plt.close(fig)

gg = np.linspace(-.03, .08, 111)
fig, ax = plt.subplots(figsize=(7, 3.9))
ax.axvspan((gap - se_gap) * 100, (gap + se_gap) * 100, color="#F1E3E1", lw=0)
ax.plot(gg * 100, [wC(g) * 100 for g in gg], color=GREY, lw=2)
for g, lab in [(gap - se_gap, "one standard error below"), (gap, "the estimate"), (gap + se_gap, "one standard error above")]:
    ax.plot(g * 100, wC(g) * 100, "o", color=RED, ms=8, zorder=5)
    low = g < gap
    ax.text(g * 100 + (.3 if low else -.2), wC(g) * 100 + (-16 if low else 15), f"{lab}: {wC(g):.0%}", color="k", ha="left" if low else "right", va="center", fontsize=12)
ax.axhline(100, color=GREY, lw=.6, ls=":"); ax.text(8, 88, "above 100%: short Hardware", color=GREY, fontsize=11, ha="right")
ax.set_xlim(-3, 8); ax.set_ylim(-50, 250)
ax.set_xlabel("gap in expected returns, Chips minus Hardware (pp)"); ax.set_ylabel("weight on Chips (%)")
fig.savefig(OUT / "ca_pair_weights.pdf"); plt.close(fig)

# ---------- same truth, 46 years of data, three correlations. The truth is 50/50 in all three.
sig_, Tm = .16 / np.sqrt(12), len(F)
rng = np.random.default_rng(0)
fig, axes = plt.subplots(1, 3, figsize=(12, 3.3), sharey=True, sharex=True)
for ax, r_ in zip(axes, [0, .5, .9]):
    Sg = sig_ ** 2 * np.array([[1, r_], [r_, 1]]); Lc = np.linalg.cholesky(Sg); w1 = []
    for _ in range(4000):
        X = rng.standard_normal((Tm, 2)) @ Lc.T + AVG / 12
        w = np.linalg.solve(np.cov(X.T), X.mean(0)); w1.append(w[0] / w.sum())
    w1 = np.array(w1)
    theory = (1 + r_) / (4 * (AVG / .16)) * np.sqrt(2 / ((Tm / 12) * (1 - r_)))
    print(f"same truth, rho {r_}: weight sd by formula {theory:.0%}, 5-95 band {np.percentile(w1, 5):.0%} to {np.percentile(w1, 95):.0%}, share of histories with a short position {np.mean((w1 < 0) | (w1 > 1)):.0%}")
    ax.hist(np.clip(w1 * 100, -150, 250), bins=np.arange(-150, 255, 10), color=LIGHT)
    ax.axvline(50, color=RED, lw=2)
    ax.axvspan(-150, 0, color="#F4F4F4", lw=0, zorder=0); ax.axvspan(100, 250, color="#F4F4F4", lw=0, zorder=0)
    ax.set_title(f"$\\rho={r_}$"); ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_xticks([-100, 0, 50, 100, 200]); ax.set_xlabel("weight on asset 1 (%)")
fig.savefig(OUT / "ca_same_truth.pdf"); plt.close(fig)

# ---------- move one input by one standard error, on the six factors
split = lambda m_, S_: (m_, np.sqrt(np.diag(S_)), S_ / np.outer(np.sqrt(np.diag(S_)), np.sqrt(np.diag(S_))))
glue = lambda D_, C_: np.outer(D_, D_) * C_
m0, D0, C0 = split(F.mean().values, F.cov().values)
base = nz(np.linalg.solve(glue(D0, C0), m0))
moved = lambda w: np.abs(w - base).sum() / 2
NAMES = ["Market", "SMB", "HML", "RMW", "CMA", "UMD"]
bm, bv, bc = {}, {}, {}
for i, c in enumerate(NAMES):
    m1 = m0.copy(); m1[i] += D0[i] / np.sqrt(Tm); bm[c] = moved(nz(np.linalg.solve(glue(D0, C0), m1)))
    d1 = D0.copy(); d1[i] += D0[i] / np.sqrt(2 * Tm); bv[c] = moved(nz(np.linalg.solve(glue(d1, C0), m0)))
    for j in range(i + 1, 6):
        c1 = C0.copy(); c1[i, j] = c1[j, i] = C0[i, j] + (1 - C0[i, j] ** 2) / np.sqrt(Tm)
        bc[f"{c}/{NAMES[j]}"] = moved(nz(np.linalg.solve(glue(D0, c1), m0)))
bm, bv, bc = [pd.Series(b).sort_values() for b in (bm, bv, bc)]
print("base weights:", dict(zip(NAMES, base.round(2))))
print(f"one standard error, share of the book moved: means {bm.mean():.1%} (max {bm.max():.1%} {bm.idxmax()}), vols {bv.mean():.1%} (max {bv.max():.1%} {bv.idxmax()}), correlations {bc.mean():.1%} (max {bc.max():.1%} {bc.idxmax()})")
INPUT_COL = {"means": RED, "volatilities": LIGHT, "correlations": BLUE}
fig, axes = plt.subplots(1, 3, figsize=(12, 4.4), sharex=True)
for ax, b, lab in zip(axes, [bm, bv, bc], INPUT_COL):
    ax.barh(b.index, b.values * 100, color=INPUT_COL[lab], height=.72)
    ax.set_title(f"one {'volatility' if lab == 'volatilities' else lab[:-1]}"); ax.tick_params(axis="y", labelsize=10 if len(b) > 6 else 12)
    ax.set_xlabel("% of the book moved")
axes[0].set_xlim(0, 14)
fig.tight_layout()
fig.savefig(OUT / "ca_one_se.pdf"); plt.close(fig)

# ---------- the bootstrap, one input at a time
RULES = {"mean-variance":   lambda mu, C: np.linalg.solve(C, mu),
         "no correlations": lambda mu, C: mu / np.diag(C),
         "same Sharpe":     lambda mu, C: np.linalg.solve(C, np.sqrt(np.diag(C))),
         "same mean":       lambda mu, C: np.linalg.solve(C, np.ones(len(mu))),
         "risk parity":     lambda mu, C: 1 / np.sqrt(np.diag(C)),
         "1/N":             lambda mu, C: np.ones(len(mu))}
SETS = {"six factors": F, "eight sectors": R, "asset classes": None, "29 long-shorts": L.astype(float)}
G = pd.read_csv(DATA / "GlobalFinMonthly.csv", parse_dates=["Date"]).set_index("Date").replace(-99, np.nan)
SETS["asset classes"] = G[["MKT", "USA30yearGovBond", "EmergingMarkets", "WorldxUSA", "WorldxUSAGovBond"]].sub(G.RF, axis=0).dropna()
INPUTS = ["means", "volatilities", "correlations", "all"]

def bootstrap(X, T=None, B=1000):
    Y = X.values; n = len(Y); T = T or n
    m_, D_, C_ = split(Y.mean(0), np.cov(Y.T)); S_ = glue(D_, C_); best = np.sqrt(m_ @ np.linalg.solve(S_, m_))
    rng = np.random.default_rng(0)
    W_ = {r: {k: [] for k in INPUTS} for r in RULES}
    for _ in range(B):
        Z = Y[rng.integers(0, n, T)]; m1, D1, C1 = split(Z.mean(0), np.cov(Z.T))
        for k, (a, b, c) in {"means": (m1, D_, C_), "volatilities": (m_, D1, C_), "correlations": (m_, D_, C1), "all": (m1, D1, C1)}.items():
            for r, f in RULES.items():
                W_[r][k].append(nz(f(a, glue(b, c))))
    out = {}
    for r, f in RULES.items():
        w0 = nz(f(m_, S_)); sr0 = (w0 @ m_) / np.sqrt(w0 @ S_ @ w0)
        for k in INPUTS:
            A_ = np.array(W_[r][k]); sr = (A_ @ m_) / np.sqrt(np.einsum("ij,jk,ik->i", A_, S_, A_))
            out[(r, k)] = {"var": A_.var(0).mean(), "lost": (sr0 - sr.mean()) / best}
    return pd.DataFrame(out).T, np.array(W_["mean-variance"]["means"]), W_["mean-variance"], best

print("\nbootstrap, mean-variance only: share of the weight variance, and Sharpe ratio lost (share of the best)")
ALLB = {}
for name, X in SETS.items():
    for T_, lab in [(None, "all the data"), (120, "ten years")]:
        out, _, _, best = bootstrap(X, T_)
        ALLB[(name, T_)] = out
        v = out.loc["mean-variance", "var"]; l = out.loc["mean-variance", "lost"]; tot = v[INPUTS[:3]].sum()
        print(f"  {name:15s} {lab:13s} variance shares: means {v['means']/tot:.0%}, vols {v['volatilities']/tot:.0%}, corrs {v['correlations']/tot:.0%}; sd of a weight {np.sqrt(v['all']):.3f}; "
              f"Sharpe lost: means {l['means']:.1%}, vols {l['volatilities']:.1%}, corrs {l['correlations']:.1%}, all {l['all']:.1%}; best in sample {best * np.sqrt(12):.2f}")

_, _, wf, _ = bootstrap(F)
fig, axes = plt.subplots(1, 4, figsize=(12, 3.3), sharey=True)
for ax, k in zip(axes, INPUTS):
    ax.boxplot(np.array(wf[k]), widths=.6, showfliers=False, patch_artist=True, boxprops=dict(facecolor=LIGHT, color=GREY),
               medianprops=dict(color=RED), whiskerprops=dict(color=GREY), capprops=dict(color=GREY))
    ax.axhline(0, color="k", lw=.6)
    ax.set_xticklabels(["Mkt", "SMB", "HML", "RMW", "CMA", "UMD"], fontsize=10, rotation=90)
    ax.set_title("all three" if k == "all" else f"only {k}")
axes[0].set_ylabel("weight, 1,000 resamples")
fig.savefig(OUT / "ca_boot_inputs.pdf"); plt.close(fig)

# exposure by rule, ten years of data
print("\nexposure by rule, six factors:")
for T_, lab in [(None, "all the data"), (120, "ten years")]:
    o = ALLB[("six factors", T_)]
    print(" ", lab, {r: (round(float(np.sqrt(o.loc[(r, 'all'), 'var'])), 3), f"{o.loc[(r, 'all'), 'lost']:.1%}") for r in RULES})
o = ALLB[("six factors", 120)]
fig, axes = plt.subplots(1, 2, figsize=(12, 3.8))
for ax, col, ylab, sc in zip(axes, ["var", "lost"], ["average variance of a weight ($\\times 10^{4}$)", "Sharpe ratio lost to estimation (%)"], [1e4, 100]):
    bot = np.zeros(len(RULES))
    for k in INPUTS[:3]:
        h = np.array([max(o.loc[(r, k), col], 0) * sc for r in RULES])
        ax.bar([r.replace(" ", "\n") for r in RULES], h, bottom=bot, color=INPUT_COL[k], width=.62, edgecolor="white", lw=1.5, label=k); bot += h
    ax.set_ylabel(ylab); ax.tick_params(axis="x", labelsize=10.5)
axes[0].legend(frameon=False, loc="upper right")
fig.tight_layout()
fig.savefig(OUT / "ca_boot_rules.pdf"); plt.close(fig)

# ---------- the race, on real data
def run(D, fn, burn=120):
    return pd.Series([D.iloc[t].values @ nz(fn(D.iloc[:t].mean().values, D.iloc[:t].cov().values)) for t in range(burn, len(D))], index=D.index[burn:])
print("\nthe race, expanding window, ten-year burn-in, before costs:")
RACE = {}
for name, X in SETS.items():
    res = {r: run(X, f) for r, f in RULES.items()}
    a, b = res["1/N"].values, res["mean-variance"].values
    rng = np.random.default_rng(0); dd = []
    for _ in range(2000):
        i = rng.integers(0, len(a), len(a)); dd.append(sharpe(a[i]) - sharpe(b[i]))
    RACE[name] = {r: sharpe(v) for r, v in res.items()}
    print(f"  {name:15s} {X.index[0]:%Y}-{X.index[-1]:%Y}", {r: round(v, 2) for r, v in RACE[name].items()}, f"1/N minus mean-variance {RACE[name]['1/N'] - RACE[name]['mean-variance']:+.2f}, se {np.std(dd):.2f}")
leak = pd.Series([F.iloc[t].values @ nz(np.linalg.solve(F.iloc[:t + 1].cov().values, F.iloc[:t + 1].mean().values)) for t in range(120, len(F))])
print(f"  six factors with the month it earns inside the estimate: {sharpe(leak):.2f}")
for lab, sl in [("1980-1999", slice("1980", "1999")), ("2000-2026", slice("2000", "2026"))]:
    a, b = sharpe(run(F.loc[sl], RULES["mean-variance"], 60)), sharpe(run(F.loc[sl], RULES["1/N"], 60))
    print(f"  {lab}: mean-variance {a:.2f}, 1/N {b:.2f}, gap {b - a:+.2f}")

# how to measure the cost, and how not to
Lw, naive, placebo = 120, [], []
w_full = nz(np.linalg.solve(F.cov().values, F.mean().values))
for t in range(Lw, len(F) - Lw, 12):
    est, ev = F.iloc[t - Lw:t], F.iloc[t:t + Lw]
    best_ = sharpe(ev @ nz(np.linalg.solve(ev.cov().values, ev.mean().values)))
    naive.append(1 - sharpe(ev @ nz(np.linalg.solve(est.cov().values, est.mean().values))) / best_)
    placebo.append(1 - sharpe(ev @ w_full) / best_)
print(f"placebo: estimated weights lose {np.median(naive):.0%}, clairvoyant weights lose {np.median(placebo):.0%}")

# ---------- the race, in one formula. In annual units, with T in years:
#   in-sample Sharpe^2 = truth + N/T, and kept = 1 / sqrt(1 + N / (T * truth))
# The truth keeps the 1/N direction and removes the (N-1)/T of noise from the rest.
print("\nthe race by asset set:")
TRUTH = {}
for name, X in SETS.items():
    N = X.shape[1]; Ty = len(X) / 12; m_, S_ = X.mean().values * 12, X.cov().values * 12
    th2 = m_ @ np.linalg.solve(S_, m_); one_ = np.ones(N); a2 = (one_ @ m_) ** 2 / (one_ @ S_ @ one_)
    r2 = th2 - a2; noise = (N - 1) / Ty; r2t = max(r2 - noise, 0); t2 = a2 + r2t; q2 = a2 / t2
    Tstar = np.inf if q2 >= 1 else (N / t2) * q2 / (1 - q2)
    D_ = np.sqrt(np.diag(S_)); s_ = m_ / D_
    M_ = np.eye(N) - one_[:, None] @ one_[None, :] / N; C_ = S_ / np.outer(D_, D_)
    sh_noise = np.trace(M_ @ C_) / (N - 1) / Ty; sh_obs = s_.var(ddof=1)
    TRUTH[name] = dict(N=N, Ty=Ty, th2=th2, a2=a2, r2=r2, noise=noise, t2=t2, q=np.sqrt(q2), Tstar=Tstar, dstar=min(sh_noise / sh_obs, 1), m_=m_, S_=S_, r2t=r2t)
    print(f"  {name:15s} N {N:2d}, {Ty:.0f} years: in-sample best {np.sqrt(th2):.2f}, 1/N {np.sqrt(a2):.2f}; extra Sharpe^2 {r2:.2f}, noise {noise:.2f}, noise share {noise / r2:.0%}; "
          f"true best {np.sqrt(t2):.2f}; 1/N keeps {np.sqrt(q2):.0%}; years to beat 1/N {Tstar:.1f}; kept at {Ty:.0f} years {1 / np.sqrt(1 + N / (Ty * t2)):.0%}")
    print(f"     means from {m_.min():.1%} to {m_.max():.1%}, Sharpes from {s_.min():.2f} to {s_.max():.2f}; Sharpe dispersion {np.sqrt(sh_obs):.2f}, noise {np.sqrt(sh_noise):.2f}, share {sh_noise / sh_obs:.0%}")

YRS = [3, 5, 10, 20, 30, 40, 60]
TGRID = np.linspace(2, 60, 120)
fig, axes = plt.subplots(1, 4, figsize=(12.5, 3.4), sharey=True, sharex=True)
for ax, name in zip(axes, ["29 long-shorts", "six factors", "eight sectors", "asset classes"]):
    t_ = TRUTH[name]; N, m_, S_ = t_["N"], t_["m_"], t_["S_"]
    Lc = np.linalg.cholesky(S_); z = np.linalg.solve(Lc, m_); e = Lc.T @ np.ones(N); e /= np.linalg.norm(e)
    a = e @ z; rest = z - a * e
    zt = a * e + rest * np.sqrt(t_["r2t"] / t_["r2"]); mt = Lc @ zt          # the truth: the extra Sharpe^2 net of noise
    th = np.sqrt(mt @ np.linalg.solve(S_, mt)); C12 = np.linalg.cholesky(S_ / 12)
    rng = np.random.default_rng(0); dots = []
    for y in YRS:
        v = []
        for _ in range(300):
            X = rng.standard_normal((y * 12, N)) @ C12.T + mt / 12
            w = np.linalg.solve(np.cov(X.T), X.mean(0)); v.append((w @ mt) / np.sqrt(w @ S_ @ w) / th)
        dots.append(np.mean(v))
    print(f"  {name}: simulated share kept, estimating everything", dict(zip(YRS, np.round(dots, 2))), "formula", dict(zip(YRS, np.round(1 / np.sqrt(1 + N / (np.array(YRS) * t_['t2'])), 2))))
    ax.plot(TGRID, 100 / np.sqrt(1 + N / (TGRID * t_["t2"])), color=RED, lw=2.2)
    ax.plot(YRS, np.array(dots) * 100, "o", color=RED, ms=5, mfc="white")
    ax.axhline(t_["q"] * 100, color=BLUE, lw=2.2)
    ax.axvline(t_["Ty"], color=GREY, lw=.8, ls=":")
    ax.set_title(name); ax.set_xlabel("years of data"); ax.set_ylim(0, 105); ax.set_xticks([0, 20, 40, 60])
axes[0].set_ylabel("% of the true best Sharpe kept")
axes[0].text(58, 10, "1/N", color=BLUE, ha="right", fontsize=12); axes[0].text(58, 79, "optimizer", color=RED, ha="right", fontsize=12)
fig.tight_layout()
fig.savefig(OUT / "ca_race.pdf"); plt.close(fig)

print(f"average window in the race: {np.arange(120, 558).mean() / 12:.0f} years")
wa = lambda f: dict(zip(SETS["asset classes"].columns, np.round((lambda w: w / w.sum())(f(SETS["asset classes"].mean().values, SETS["asset classes"].cov().values)), 2)))
print("asset classes, full-sample weights, same mean:", wa(RULES["same mean"]), "same Sharpe:", wa(RULES["same Sharpe"]))

# ---------- shrinkage: the rules are the corners of two dials
def dial(d, c):
    def fn(mu, C):
        D_ = np.sqrt(np.diag(C)); R_ = C / np.outer(D_, D_); s_ = mu / D_
        return np.linalg.solve(glue(D_, (1 - c) * R_ + c * np.eye(len(mu))), ((1 - d) * s_ + d * s_.mean()) * D_)
    return fn
GRID = [0, .25, .5, .75, 1]
print("\nthe Sharpe dial, out of sample, at c = 0:")
PATH = {}
for name, X in SETS.items():
    PATH[name] = [sharpe(run(X, dial(d, 0))) for d in GRID]
    print(f"  {name:15s}", np.round(PATH[name], 2), f"formula for d: {TRUTH[name]['dstar']:.2f}")
fig, ax = plt.subplots(figsize=(7.2, 3.9))
for name, col in [("eight sectors", BLUE), ("six factors", GREY), ("asset classes", LIGHT), ("29 long-shorts", RED)]:
    y = np.array(PATH[name]) / PATH[name][0] * 100 - 100
    ax.plot(GRID, y, color=col, lw=2.2, ls="--" if col == GREY else "-")
    ax.plot(TRUTH[name]["dstar"], np.interp(TRUTH[name]["dstar"], GRID, y), "o", color=col, ms=9, mec="white", zorder=5)
    ax.text(1.03, y[-1] + (5 if col == GREY else 0), name, color="k", va="center", fontsize=12)
ax.axhline(0, color="k", lw=.6); ax.set_xlim(0, 1.42); ax.set_xticks(GRID)
ax.set_xlabel("$d$: how far toward the same Sharpe ratio"); ax.set_ylabel("Sharpe ratio, change from $d=0$ (%)")
fig.savefig(OUT / "ca_dial_path.pdf"); plt.close(fig)

fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
for ax, name, cmap in zip(axes, ["eight sectors", "29 long-shorts"], ["Blues", "Reds"]):
    Gd = np.array([[sharpe(run(SETS[name], dial(d, c))) for d in GRID] for c in GRID])
    print(f"grid, {name} (rows c = 0 to 1, columns d = 0 to 1):\n", np.round(Gd, 2))
    ax.imshow(Gd, origin="lower", cmap=cmap, vmin=Gd.min() - .3 * (Gd.max() - Gd.min()), vmax=Gd.max() + .3 * (Gd.max() - Gd.min()), aspect="auto")
    for i in range(5):
        for j in range(5):
            ax.text(j, i, f"{Gd[i, j]:.2f}", ha="center", va="center", fontsize=12, fontweight="bold" if Gd[i, j] == Gd.max() else "normal")
    ax.set_xticks(range(5)); ax.set_xticklabels(GRID); ax.set_yticks(range(5)); ax.set_yticklabels(GRID)
    ax.set_xlabel("$d$: toward the same Sharpe ratio"); ax.set_ylabel("$c$: toward no correlation"); ax.set_title(name)
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
fig.tight_layout()
fig.savefig(OUT / "ca_dial_grid.pdf"); plt.close(fig)
