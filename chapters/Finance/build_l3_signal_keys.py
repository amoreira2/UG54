"""Answer key for the sorts lecture's challenge, one entry per signal.

The challenge is done on each student's own signal, so the right numbers depend
on which one they picked. This runs the lecture's reference construction on all
30 menu signals and writes keys_L3_by_signal.json, which auto_evaluator.py reads.

    python chapters/Finance/build_l3_signal_keys.py

Construction (the lecture's 🔒 Reference cell, applied to each signal):
merge the signal onto the panel keeping every panel month, lag the signal and
market cap one month within each stock, drop rows missing ret / me_l1 / signal,
ten equal-count buckets within each month (pd.qcut, duplicates='drop'), D10 - D1.

Signals that cannot be cut into ten buckets get no key: DivSeason and OScore
take two values, and ShareIss1Y has a tenth bucket in only 84 of 251 months.
"""
import os, json
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "..", "assets", "data")

panel = pd.read_parquet(os.path.join(DATA, "panel_backbone_1980_2000.parquet"))
menu  = pd.read_csv(os.path.join(DATA, "signal_menu.csv"))
panel['me_l1'] = panel.groupby('permno')['me'].shift(1)

keys = {}
for s in menu.Acronym:
    sig = pd.read_parquet(os.path.join(DATA, "signals", f"{s}.parquet"))
    x = panel.merge(sig, on=['permno', 'date'], how='left').sort_values(['permno', 'date'])
    x['sig_l1'] = x.groupby('permno')[s].shift(1)
    x = x.dropna(subset=['sig_l1', 'ret', 'me_l1'])
    x['decile'] = x.groupby('date')['sig_l1'].transform(
        lambda v: pd.qcut(v, 10, labels=False, duplicates='drop'))

    ew = x.groupby(['date', 'decile'])['ret'].mean().unstack()
    if 9 not in ew.columns or ew[9].notna().sum() < 0.9 * len(ew):
        print(f"{s:22s} no key: cannot be cut into ten buckets")
        continue
    vw = x.groupby(['date', 'decile']).apply(
        lambda g: np.average(g['ret'], weights=g['me_l1'])).unstack()
    avg_sig = x.groupby(['date', 'decile'])['sig_l1'].mean().unstack().mean()
    sd = float(x.groupby('date')['sig_l1'].std().mean())      # typical cross-sectional spread

    le = (ew[9] - ew[0]).dropna()
    lv = (vw[9] - vw[0]).dropna()
    t = lambda r: float(r.mean() / r.std() * np.sqrt(len(r)))

    # (truth, fractional tolerance, absolute floor). The floor keeps answers near
    # zero from needing impossible precision.
    keys[s] = {
        "ls_ew_ann": [round(float(le.mean() * 12), 5), 0.15, 0.01],
        "t_ew":      [round(t(le), 3),                 0.15, 0.30],
        "ls_vw_ann": [round(float(lv.mean() * 12), 5), 0.15, 0.01],
        "t_vw":      [round(t(lv), 3),                 0.15, 0.30],
        "sig_d1":    [float(f"{avg_sig[0]:.6g}"),      0.10, float(f"{0.05 * sd:.3g}")],
        "sig_d10":   [float(f"{avg_sig[9]:.6g}"),      0.10, float(f"{0.05 * sd:.3g}")],
    }
    k = keys[s]
    print(f"{s:22s} EW {k['ls_ew_ann'][0]:+.3f} t {k['t_ew'][0]:+6.2f}   "
          f"VW {k['ls_vw_ann'][0]:+.3f} t {k['t_vw'][0]:+6.2f}")

out = os.path.join(HERE, "keys_L3_by_signal.json")
json.dump(keys, open(out, "w"), indent=1)
print(f"\n{len(keys)} signals -> {out}")
