"""
Cache the 29 standard long-short return series.

Every lecture from L5 onward rebuilds these from the 30 signal files, which
means downloading ~94 MB and waiting ~90 seconds. Forty students doing that at
once is 3.7 GB off GitHub raw. This writes them once.

Convention is the course standard: NYSE breakpoints, value-weighted,
top decile minus bottom decile, signal and weights lagged one month, indexed
by the month the return was EARNED.

NOTE: re-running this regenerates longshort_29.parquet, which L12's pod-shop
table and the intro chapter's header figure both read. The lagged convention
moves those numbers slightly, so re-run deliberately, not by accident.

Output: assets/data/longshort_29.parquet   (one column per signal, ~60 KB)
"""
import numpy as np, pandas as pd, warnings
from pathlib import Path
warnings.filterwarnings('ignore')

D = Path(__file__).resolve().parents[2] / "assets" / "data"
panel = pd.read_parquet(D / "panel_backbone_1980_2000.parquet")
menu  = pd.read_csv(D / "signal_menu.csv")
panel["me_l1"] = panel.groupby("permno")["me"].shift(1)

def long_short(sig):
    s = pd.read_parquet(D / "signals" / f"{sig}.parquet")
    d = panel.merge(s, on=['permno','date'], how='left').sort_values(['permno','date'])
    d['sig_l1'] = d.groupby('permno')[sig].shift(1)
    d = d.dropna(subset=['sig_l1','ret','me_l1'])
    q = (d[d.exchcd == 1].groupby('date')['sig_l1'].quantile([.1,.9]).unstack()
           .rename(columns={0.1:'lo', 0.9:'hi'}))
    d = d.merge(q, on='date')
    d['g'] = np.where(d.sig_l1 <= d.lo, 0, np.where(d.sig_l1 >= d.hi, 9, np.nan))
    p = (d.dropna(subset=['g']).groupby(['date','g'])
           .apply(lambda g: np.average(g['ret'], weights=g['me_l1'])).unstack())
    return (p[9] - p[0]).dropna()     # already dated by the month EARNED

out = {}
for s in sorted(menu.Acronym):
    try:
        r = long_short(s)
        if len(r) > 200:
            out[s] = r
            print(f"  {s:24s} {len(r):3d} months  Sharpe {r.mean()/r.std()*np.sqrt(12):+.2f}")
    except Exception as e:
        print(f"  {s:24s} skipped ({type(e).__name__})")

L = pd.DataFrame(out).dropna(how='all')
L.to_parquet(D / "longshort_29.parquet")
print(f"\n✅ {L.shape[1]} strategies x {len(L)} months -> longshort_29.parquet "
      f"({(D/'longshort_29.parquet').stat().st_size/1024:.0f} KB)")
print(f"   {L.index[0]:%Y-%m} to {L.index[-1]:%Y-%m}")
