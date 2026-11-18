# Builds assets/data/value_spreads_monthly_1926.parquet for Conditional Strategies II (timing factors with their value spread)
#   python chapters/Finance/build_value_spread_data.py <folder>
# where <folder> holds the three zip files below, downloaded by hand from Ken French's data library
# (https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html, "6 Portfolios Formed on Size and ..." CSV links).
#
# Source: the three 2x3 sorts behind the Fama-French factors:
#   6_Portfolios_2x3          size x book-to-market   -> HML and SMB, from July 1926
#   6_Portfolios_ME_OP_2x3    size x profitability    -> RMW, from July 1963
#   6_Portfolios_ME_INV_2x3   size x investment       -> CMA, from July 1963
# From each file: the value-weighted monthly returns of the six portfolios, and the value-weighted average book-to-market
# of each portfolio as French publishes it (book equity at the last fiscal year end over market equity in December of
# the prior year, reweighted every month by market equity). No momentum file: French does not publish book-to-market for it.
#
# Each factor is the average of its long portfolios minus the average of its short ones, as French builds it. HML, RMW
# and CMA match French's factors (correlation 1.00). SMB here is the size-by-book-to-market version, the three-factor SMB.
# The book-to-market of a leg is the average over its portfolios, the same way.
#
# After writing the file it prints a check quoted in the slides' appendix: the same forecasting test with book-to-market
# at today's price instead of last December's.
#
# Columns: HML, SMB, RMW, CMA (monthly returns, decimals) and <factor>_bm_long, <factor>_bm_short (book-to-market of the
# long and short legs). RMW and CMA are missing before July 1963.
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

RAW = Path(sys.argv[1])
OUT = Path(__file__).resolve().parents[2] / "assets" / "data" / "value_spreads_monthly_1926.parquet"


def french_blocks(name):
    """Read one French zip and split its CSV into (title, columns, rows) blocks."""
    z = zipfile.ZipFile(RAW / f"{name}_CSV.zip")
    text = z.read(z.namelist()[0]).decode("latin-1")
    blocks, title, cols = [], [], None
    for line in text.splitlines():
        s = line.strip()
        if s.startswith(","):                                  # a column header starts a new block
            cols, rows = ["date"] + [c.strip() for c in s.split(",")[1:]], []
            blocks.append((" ".join(title), cols, rows))
            title = []
        elif s[:1].isdigit() and cols is not None:             # a data row: YYYYMM (monthly) or YYYY (annual)
            rows.append([v.strip() for v in s.split(",")])
        elif s:
            title.append(s)                                    # text: part of the next block's title
    return blocks


def monthly(blocks, key):
    """The monthly block whose title contains `key`, as a DataFrame of floats with month-end dates."""
    _, cols, rows = next(b for b in blocks if key in b[0])
    d = pd.DataFrame(rows, columns=cols)
    d = d[d["date"].str.len() == 6]
    d.index = pd.to_datetime(d.pop("date"), format="%Y%m") + pd.offsets.MonthEnd(0)
    return d.astype(float).replace([-99.99, -999.0], np.nan)


out, legs_r, legs_bmj = {}, {}, {}
for name, legs in [("6_Portfolios_2x3", {"HML": ("HiBM", "LoBM"), "SMB": ("SMALL", "BIG")}),
                   ("6_Portfolios_ME_OP_2x3", {"RMW": ("HiOP", "LoOP")}),
                   ("6_Portfolios_ME_INV_2x3", {"CMA": ("LoINV", "HiINV")})]:
    B = french_blocks(name)
    R = monthly(B, "Average Value Weighted Returns -- Monthly") / 100
    BM = monthly(B, "Value Weight Average of BE/ME")           # BE / ME(Dec t-1); not the BE_FYt-1/ME_June t block
    BMJ = monthly(B, "BE_FYt-1/ME_June t")                     # BE / ME(Jun t): only for the check at the end
    for f, (lo, sh) in legs.items():
        if f == "SMB":                                         # small: SMALL and ME1 columns; big: BIG and ME2
            L = [c for c in R.columns if c.startswith(("SMALL", "ME1"))]
            S = [c for c in R.columns if c.startswith(("BIG", "ME2"))]
        else:
            L = [c for c in R.columns if c.endswith(lo)]
            S = [c for c in R.columns if c.endswith(sh)]
        out[f] = R[L].mean(axis=1) - R[S].mean(axis=1)
        out[f"{f}_bm_long"] = BM[L].mean(axis=1)
        out[f"{f}_bm_short"] = BM[S].mean(axis=1)
        legs_r[f] = (R[L].mean(axis=1), R[S].mean(axis=1))
        legs_bmj[f] = (BMJ[L].mean(axis=1), BMJ[S].mean(axis=1))
        print(f"{f}: long {L}, short {S}")

V = pd.DataFrame(out)[["HML", "SMB", "RMW", "CMA",
                       "HML_bm_long", "HML_bm_short", "SMB_bm_long", "SMB_bm_short",
                       "RMW_bm_long", "RMW_bm_short", "CMA_bm_long", "CMA_bm_short"]]
V.index.name = "date"
V.to_parquet(OUT)
print(f"wrote {OUT.name}: {V.index[0]:%Y-%m} to {V.index[-1]:%Y-%m}, {len(V)} months")
print(V.describe().T.round(3).to_string())

# ---- check for the slides' appendix: book-to-market at today's price
# Start from book over June's price when the portfolios form (read in July), then roll it forward each month with the
# leg's own return: a leg that rose 10% is 10% more expensive. Compare with French's December-price version, used above.
print("\nnext month's factor return on this month's value spread: in-sample HAC t, and out-of-sample R2 with forecasts from 1980")
for f in ["HML", "SMB", "RMW", "CMA"]:
    rl, rs = legs_r[f]
    june = np.log(legs_bmj[f][0]) - np.log(legs_bmj[f][1])
    form = june.where(june.index.month == 7).ffill()
    year_formed = (june.index - pd.offsets.MonthBegin(6)).year               # July t to June t+1 -> t
    now = form - (np.log1p(rl) - np.log1p(rs)).groupby(year_formed).cumsum()
    december = np.log(V[f"{f}_bm_long"]) - np.log(V[f"{f}_bm_short"])
    line = f"  {f}"
    for label, x in [("December prices", december), ("today's prices", now)]:
        d = pd.DataFrame({"y": V[f].shift(-1), "x": x}).dropna()
        t = sm.OLS(d.y, sm.add_constant(d.x)).fit(cov_type="HAC", cov_kwds={"maxlags": 1}).tvalues["x"]
        err_f, err_a = [], []
        for date in d.loc["1980":].index:                                     # fit on pairs complete before this month
            past = d.loc[:date].iloc[:-1]
            b, a = np.polyfit(past.x, past.y, 1)
            err_f.append((d.y[date] - a - b * d.x[date]) ** 2)
            err_a.append((d.y[date] - past.y.mean()) ** 2)
        line += f"   {label}: t {t:.2f}, R2 {1 - sum(err_f) / sum(err_a):.2%}"
    gap = (december - now).dropna()                                           # what the December price adds
    line += f"   gap's correlation with the factor's last 12 months: {gap.corr(V[f].rolling(12).sum()):.2f}"
    print(line)
