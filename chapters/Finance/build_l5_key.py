"""Answer key for the factor-zoo lecture's challenge: ten portfolios on two given
signals, their market betas and average excess returns, and the 10 - 1
long-short with the t-statistic of its alpha.

    python chapters/Finance/build_l5_key.py

Construction — the lecture's own `portfolio_formation()`: signal lagged one month
within each stock; rows missing ret / me_l1 / signal dropped; ten equal-count
groups each month (pd.qcut over every stock, no NYSE breakpoints); value-weighted
by me_l1 inside each group. Portfolio returns minus RF, regressed on Mkt-RF. The
long-short is portfolio 10 minus portfolio 1 (RF cancels). Writes keys_L5.json,
which auto_evaluator.py reads.
"""
import os, json
import numpy as np
import pandas as pd
import statsmodels.api as sm

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "..", "assets", "data")

panel = pd.read_parquet(os.path.join(DATA, "panel_backbone_1980_2000.parquet"))
ff    = pd.read_csv(os.path.join(DATA, "ff_monthly.csv"), index_col=0, parse_dates=True)
panel['me_l1'] = panel.groupby('permno')['me'].shift(1)


def portfolio_formation(df, signal, ngroups=10):
    """The lecture's function, copied so the key is built the way students sort."""
    df['signal_group'] = df.groupby(['date'])[signal].transform(
        lambda x: pd.qcut(x, ngroups, labels=False, duplicates='drop'))
    ret = df.groupby(['date', 'signal_group']).apply(
        lambda x: (x['ret'] * x['me_l1']).sum() / x['me_l1'].sum())
    return ret.unstack(level=-1)


key = {}
for sig, tag in [("BookLeverage", "bl"), ("IdioVol3F", "iv")]:
    s = pd.read_parquet(os.path.join(DATA, "signals", f"{sig}.parquet"))
    d = panel.merge(s, on=['permno', 'date'], how='left').sort_values(['permno', 'date'])
    d['sig_l1'] = d.groupby('permno')[sig].shift(1)
    d = d.dropna(subset=['sig_l1', 'ret', 'me_l1'])
    ex = portfolio_formation(d, 'sig_l1').sub(ff['RF'], axis=0).dropna(how='all')
    ls = (ex[9] - ex[0]).dropna()

    betas, avgs = [], []
    for p in range(10):
        j = pd.concat([ex[p].rename('y'), ff['Mkt-RF']], axis=1).dropna()
        betas.append(sm.OLS(j.y, sm.add_constant(j['Mkt-RF'])).fit().params['Mkt-RF'])
        avgs.append(j.y.mean() * 12)
    j = pd.concat([ls.rename('y'), ff['Mkt-RF']], axis=1).dropna()
    m = sm.OLS(j.y, sm.add_constant(j['Mkt-RF'])).fit()
    alpha, resid_vol = m.params['const'] * 12, m.resid.std() * np.sqrt(12)
    mkt = j['Mkt-RF']
    sr_m = mkt.mean() / mkt.std() * np.sqrt(12)

    # lists: every element within an absolute band; scalars: (truth, tol, floor)
    key[f"betas_{tag}"] = {"each": [round(float(x), 4) for x in betas], "abs_tol": 0.05}
    key[f"avg_{tag}"]   = {"each": [round(float(x), 5) for x in avgs],  "abs_tol": 0.01}
    key[f"ls_beta_{tag}"] = [round(float(m.params['Mkt-RF']), 4), 0.10, 0.05]
    key[f"ls_avg_{tag}"]  = [round(float(ls.mean() * 12), 5), 0.10, 0.01]
    key[f"ls_t_{tag}"]    = [round(float(m.tvalues['const']), 3), 0.15, 0.30]
    key["mkt_avg"] = [round(float(mkt.mean() * 12), 5), 0.05, 0.005]

    print(f"{sig}  ({len(j)} months)")
    print("  beta   " + " ".join(f"{x:6.2f}" for x in betas))
    print("  avg    " + " ".join(f"{x:6.1%}" for x in avgs))
    print("  alpha  " + " ".join(f"{a - b * mkt.mean() * 12:+6.1%}" for a, b in zip(avgs, betas)))
    print(f"  10 - 1: beta {m.params['Mkt-RF']:+.2f}  avg {ls.mean()*12:+.2%}/yr  "
          f"alpha {alpha:+.2%}/yr (t = {m.tvalues['const']:+.2f})  appraisal {alpha/resid_vol:+.2f}  "
          f"SR_max with market {np.sqrt(sr_m**2 + (alpha/resid_vol)**2):.2f} vs market {sr_m:.2f}")

print(f"\nmarket: {key['mkt_avg'][0]:.2%}/yr over the same months")
out = os.path.join(HERE, "keys_L5.json")
json.dump(key, open(out, "w"), indent=1)
print(f"-> {out}")
