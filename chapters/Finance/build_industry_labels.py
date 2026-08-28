"""Recover FF49 industry membership per (permno, month) from the KNS-style
characteristics files, where `indmom` is the stock's industry momentum and is
therefore identical for every stock in the same industry on the same date.
We use it only as a GROUP LABEL, never as a value.  Writes industry_labels.parquet."""
import pandas as pd, numpy as np
a=pd.read_pickle('assets/data/characteristics19721991.pkl')
b=pd.read_pickle('assets/data/characteristics19922001.pkl')
ch=pd.concat([a,b])[['indmom']].reset_index().dropna()
ch=ch[(ch.date>='1979-01-01')&(ch.date<='2001-01-01')]
# dense integer label per date, so the file carries no accidental information
ch['ind']=ch.groupby('date')['indmom'].transform(lambda s:s.rank(method='dense').astype(int)-1)
out=ch[['permno','date','ind']].copy()
out['date']=out.date.dt.to_period('M').dt.to_timestamp('M')   # month-end, to match the panel
out=out.astype({'permno':'int32','ind':'int8'})
out.to_parquet('assets/data/industry_labels.parquet',index=False)
print(f"industry_labels.parquet  {len(out):,} rows  "
      f"{out.date.min():%Y-%m}..{out.date.max():%Y-%m}  "
      f"{out.groupby('date').ind.nunique().median():.0f} industries/month  "
      f"{out.groupby('date').permno.nunique().median():.0f} stocks/month")
