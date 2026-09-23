"""
Rebuild df_WarrenBAndCathieW_monthly.pkl.

Why this exists
---------------
The circulating monthly file
    Fin418/assets/data/df_WarrenBAndCathieW_monthly.pkl
spans 1988-11 to 2021-12 (398 months) but contains only 279 of them. About 30%
of months are simply absent from the index, scattered roughly uniformly -- 3-4
per year, 9-14 per calendar month-of-year -- so this is dropped rows, not a
different series or a deliberate filter. L7's appendix already flags it.

Nothing else is wrong with it. Its factor columns match Ken French's MONTHLY
files to 1-8bp (ordinary vintage revision) and its BRK/ARKK columns match the
compounded daily file essentially exactly.

The cost of the gaps falls mostly on ARKK, which had 59 of its 86 months.

How this rebuild works
----------------------
FUNDS  compounded from the daily file
           https://.../Fin418/.../df_WarrenBAndCathieW.pkl
       which is intact: 8,338 of the 8,339 French trading days in the window
       (only 1994-03-25 is missing).

FACTORS taken from Ken French's MONTHLY files, NOT compounded from the daily
       factors. French builds the monthly factors from monthly returns, and
       the two do not agree: compounding the daily factors moves Mom by 72bp
       in the average month (max 758bp) and HML/RMW/CMA by ~14bp. The original
       file used the monthly files and so does this.

The whole file is therefore one French vintage, where the original mixed
whatever vintage it was built from. Existing months move by the 1-8bp of
revision; see the printed comparison at the end.

Column names, dtypes and the month-end DatetimeIndex match the original,
including the trailing spaces in 'Mom   ', so this is a drop-in replacement.

Output: assets/data/df_WarrenBAndCathieW_monthly.pkl
"""

import pandas as pd
import pandas_datareader.data as web
from pathlib import Path

DAILY = ('https://raw.githubusercontent.com/amoreira2/Fin418/'
         'main/assets/data/df_WarrenBAndCathieW.pkl')
OLD   = ('https://raw.githubusercontent.com/amoreira2/Fin418/'
         'main/assets/data/df_WarrenBAndCathieW_monthly.pkl')
OUT   = Path(__file__).resolve().parents[2] / 'assets' / 'data' / 'df_WarrenBAndCathieW_monthly.pkl'
FUNDS = ['BRK', 'ARKK']

# ---- funds: compound the daily file ------------------------------------
daily = pd.read_pickle(DAILY)
daily.columns = [c.strip() for c in daily.columns]

# Drop partial calendar months at the ends. The file starts 1988-11-29, so
# 1988-11 holds 2 trading days; compounding it would put a 2-day "month" in the
# sample. 2021-12 is complete (through 12-31), so only the first month goes.
month = daily.index.to_period('M')
daily = daily[month != month[0]]

funds = pd.DataFrame(index=(1 + daily[FUNDS[0]]).resample('ME').prod().index)
for f in FUNDS:
    # Each fund is compounded over ITS OWN non-missing days. Resampling the
    # whole frame would turn ARKK's pre-2014 NaNs into 0.0 returns and silently
    # add 300 fake months of a fund that did not exist yet.
    s = daily[f].dropna()
    funds[f] = ((1 + s).resample('ME').prod() - 1).reindex(funds.index)

# ---- factors: Ken French's monthly files -------------------------------
ff5 = web.DataReader('F-F_Research_Data_5_Factors_2x3', 'famafrench', start='1988-01-01')[0] / 100
mom = web.DataReader('F-F_Momentum_Factor', 'famafrench', start='1988-01-01')[0] / 100
mom.columns = ['Mom   ']                                  # keep the original's name
ff = ff5.join(mom, how='inner')
ff.index = pd.to_datetime(ff.index.to_timestamp()) + pd.offsets.MonthEnd(0)

monthly = ff.join(funds, how='inner')
monthly = monthly[['Mkt-RF', 'SMB', 'HML', 'RMW', 'CMA', 'RF', 'Mom   ', 'BRK', 'ARKK']]

print(f"{len(monthly)} months, {monthly.index[0]:%Y-%m} to {monthly.index[-1]:%Y-%m}")
for f in FUNDS:
    s = monthly[f].dropna()
    print(f"  {f:5s} {len(s):3d} months, {s.index[0]:%Y-%m} to {s.index[-1]:%Y-%m}")

# ---- agreement with the file being replaced ----------------------------
old = pd.read_pickle(OLD)
old.columns = [c.strip() for c in old.columns]
chk = monthly.copy()
chk.columns = [c.strip() for c in chk.columns]
i = old.index.intersection(chk.index)
print(f"\nvs the old file, on its {len(i)} shared months (bp):")
for c in chk.columns:
    d = (old.loc[i, c] - chk.loc[i, c]).abs() * 1e4
    print(f"  {c:7s} mean {d.mean():6.2f}  max {d.max():7.2f}   (n={d.notna().sum()})")
print(f"months restored: {len(chk.index.difference(old.index))}")

OUT.parent.mkdir(parents=True, exist_ok=True)
monthly.to_pickle(OUT)
print(f"\nwrote {OUT}")
