"""
One market-model regression per stock per calendar year, for the stock-level
slides in backtesting_intuition.tex.

    python slides/pull_stock_years.py            # all years
    python slides/pull_stock_years.py 1995 1996  # a test: just these years

The 50-stock file in assets/data is monthly and holds only survivors, so it
cannot do this. Instead:

  Universe   each year, the 500 largest US common stocks by market cap at the
             END OF THE PREVIOUS YEAR (CRSP monthly, December). Chosen before
             the year starts, so nothing about the year decides who is in.
  Regression daily excess return on the market's, within the calendar year.
             The WRDS server runs it (regr_slope and friends), so only the
             summary comes back -- no daily returns are downloaded.
  Returns    crsp.dsf_v2 `dlyret`, which includes delisting returns.

A stock chosen for year t is also followed through year t+3, whether or not it
is still in the top 500, so "hold it next year" and "hold it the year after"
have no survivorship filter.

Needs a WRDS login (reads ~/.pgpass). Output: slides/stock_years.parquet
"""
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import wrds

OUT = Path(__file__).resolve().parent / "stock_years.parquet"
COMMON = ("sharetype = 'NS' and securitytype = 'EQTY' and securitysubtype = 'COM' "
          "and usincflg = 'Y' and issuertype in ('ACOR', 'CORP') and primaryexch in ('N', 'A', 'Q')")
N_STOCKS = 500
FOLLOW   = 3          # years to keep following a stock after the year it was picked for

db = wrds.Connection(wrds_username="am16634")

# ---- the universe: top 500 by market cap each December -----------------------
caps = db.raw_sql(f"""
    select permno, extract(year from mthcaldt)::int as year, mthcap
    from crsp.msf_v2
    where extract(month from mthcaldt) = 12 and mthcap is not null and {COMMON}
""")
caps["rank"] = caps.groupby("year")["mthcap"].rank(ascending=False, method="first")
top = caps[caps["rank"] <= N_STOCKS]
universe = {int(y) + 1: sorted(g["permno"].astype(int)) for y, g in top.groupby("year")}   # used the FOLLOWING year
print(f"universe built for {min(universe)} to {max(universe)}", flush=True)

years = [int(a) for a in sys.argv[1:]] or [y for y in sorted(universe) if y >= 1927]

# ---- one regression per stock per year, run on the server --------------------
parts = []
for y in years:
    t0 = time.time()
    permnos = sorted(set().union(*[universe.get(y - k, []) for k in range(FOLLOW + 1)]))   # this year's picks and the last three years'
    if not permnos:
        continue
    q = f"""
        select d.permno, {y} as year,
               regr_count(d.dlyret - f.rf, f.mktrf)     as n,
               regr_slope(d.dlyret - f.rf, f.mktrf)     as beta,
               regr_intercept(d.dlyret - f.rf, f.mktrf) as alpha,
               regr_syy(d.dlyret - f.rf, f.mktrf)       as syy,
               regr_sxx(d.dlyret - f.rf, f.mktrf)       as sxx,
               regr_sxy(d.dlyret - f.rf, f.mktrf)       as sxy,
               avg(d.dlyret - f.rf)                     as ybar,
               avg(f.mktrf)                             as xbar
        from crsp.dsf_v2 d join ff.factors_daily f on d.dlycaldt = f.date
        where d.dlycaldt between '{y}-01-01' and '{y}-12-31'
          and d.permno in ({','.join(str(p) for p in permnos)})
        group by d.permno
    """
    x = db.raw_sql(q)
    x["in_universe"] = x["permno"].isin(universe.get(y, []))        # picked for THIS year
    parts.append(x)
    print(f"{y}: {len(x):4d} stocks, {time.time() - t0:4.1f}s", flush=True)
db.close()

s = pd.concat(parts, ignore_index=True)
num = ["n", "beta", "alpha", "syy", "sxx", "sxy", "ybar", "xbar"]
s[num] = s[num].astype(float)                       # the server hands some of these back as objects

# ---- turn the server's sums into the usual regression output -----------------
resid_var = (s["syy"] - s["sxy"] ** 2 / s["sxx"]) / (s["n"] - 2)             # variance of the residual
s["ivol"]     = np.sqrt(resid_var * 252)                                     # annualized
s["se_beta"]  = np.sqrt(resid_var / s["sxx"])
s["se_alpha"] = np.sqrt(resid_var * (1 / s["n"] + s["xbar"] ** 2 / s["sxx"])) * 252
s["alpha"]    = s["alpha"] * 252                                             # per year
s["mean_excess"] = s["ybar"] * 252
s["mean_mkt"]    = s["xbar"] * 252
s = s[["permno", "year", "in_universe", "n", "alpha", "se_alpha", "beta", "se_beta", "ivol", "mean_excess", "mean_mkt"]]

if len(sys.argv) > 1:
    print(s.groupby("year")[["n", "beta", "alpha", "ivol"]].median().round(3))
else:
    s.to_parquet(OUT, index=False)
    print(f"\n{OUT.name}: {len(s):,} stock-years, {s.year.min()} to {s.year.max()}")
