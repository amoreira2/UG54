"""
Cache the 29 standard long-short return series.

Every lecture from L5 onward rebuilds these from the 30 signal files, which
means downloading ~94 MB and waiting ~90 seconds. Forty students doing that at
once is 3.7 GB off GitHub raw. This writes them once.

Convention is the course standard: NYSE breakpoints, value-weighted,
top decile minus bottom decile, on ret_fwd, indexed by the month EARNED.

Output: assets/data/longshort_29.parquet   (one column per signal, ~60 KB)
"""
import numpy as np, pandas as pd, warnings
from pathlib import Path
warnings.filterwarnings('ignore')

D = Path(__file__).resolve().parents[2] / "assets" / "data"
panel = pd.read_parquet(D / "panel_backbone_1980_2000.parquet")
menu  = pd.read_csv(D / "signal_menu.csv")

def long_short(sig):
    s = pd.read_parquet(D / "signals" / f"{sig}.parquet")
    d = panel.merge(s, on=['permno','date'], how='inner').dropna(subset=[sig,'ret_fwd','me'])
    q = (d[d.exchcd == 1].groupby('date')[sig].quantile([.1,.9]).unstack()
           .rename(columns={0.1:'lo', 0.9:'hi'}))
    d = d.merge(q, on='date')
    d['g'] = np.where(d[sig] <= d.lo, 0, np.where(d[sig] >= d.hi, 9, np.nan))
    p = (d.dropna(subset=['g']).groupby(['date','g'])
           .apply(lambda g: np.average(g['ret_fwd'], weights=g['me'])).unstack())
    r = (p[9] - p[0]).dropna()
    r.index = r.index + pd.offsets.MonthEnd(1)     # date the return was EARNED
    return r

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
