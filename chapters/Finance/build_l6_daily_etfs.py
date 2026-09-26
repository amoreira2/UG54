"""
Daily returns for L6's "taking the model for a spin" section.

    python chapters/Finance/build_l6_daily_etfs.py

What is in the file -- one row per trading day, returns in decimals, NOT excess:

  BRK, ARKK   Fin418's daily fund file, the same series L6's monthly ARKK and
              Berkshire table is compounded from (see build_funds_monthly.py).
              1988-11-29 to 2021-12-31; ARKK starts 2014-11-03.

  11 ETFs     The momentum ETFs from the old MultiFactorModels notebook. CRSP
              daily returns (crsp.dsf_v2), pulled by PERMNO so a fund keeps its
              history across ticker changes -- XMMO, XSMO and XSVM traded under
              other tickers before Invesco renamed them in 2019. From each fund's
              first day to the end of CRSP's daily file.

  Mkt-RF, SMB, HML, RMW, CMA, UMD, RF
              Ken French's DAILY files, one vintage for the whole file.

Needs a WRDS login (reads ~/.pgpass) and an internet connection.

Output: assets/data/daily_funds_etfs.parquet
"""
from pathlib import Path

import pandas as pd
import pandas_datareader.data as web
import wrds

OUT = Path(__file__).resolve().parents[2] / "assets" / "data" / "daily_funds_etfs.parquet"
FUNDS_DAILY = ("https://raw.githubusercontent.com/amoreira2/Fin418/"
               "main/assets/data/df_WarrenBAndCathieW.pkl")

# ticker -> CRSP permno, from crsp.stocknames (every one is shrcd 73, an ETF).
# PDP is 91876, not 75241: the ticker belonged to Parker & Parsley until 1997.
ETFS = {"MTUM": 13851, "SPMO": 15725, "XMMO": 90621, "IMTM": 15161,
        "XSMO": 90623, "PDP": 91876, "JMOM": 17085, "DWAS": 13512,
        "VFMO": 17622, "XSVM": 90622, "QMOM": 17392}

# ---- factors: Ken French, daily ----------------------------------------------
f5 = web.DataReader("F-F_Research_Data_5_Factors_2x3_daily", "famafrench", start="1988-01-01")[0]
mom = web.DataReader("F-F_Momentum_Factor_daily", "famafrench", start="1988-01-01")[0]
mom.columns = ["UMD"]
factors = f5.join(mom, how="inner") / 100                    # percent -> decimal
factors.index = pd.to_datetime(factors.index)
factors = factors[["Mkt-RF", "SMB", "HML", "RMW", "CMA", "UMD", "RF"]]

# ---- BRK and ARKK: the daily fund file ---------------------------------------
funds = pd.read_pickle(FUNDS_DAILY)
funds.columns = [c.strip() for c in funds.columns]
funds = funds[["BRK", "ARKK"]]

# ---- the momentum ETFs: CRSP daily, by permno --------------------------------
db = wrds.Connection(wrds_username="am16634")
permnos = ",".join(str(p) for p in ETFS.values())
crsp = db.raw_sql(f"""
    select permno, dlycaldt as date, dlyret as ret
    from crsp.dsf_v2
    where permno in ({permnos}) and dlycaldt >= '2005-01-01'
""", date_cols=["date"])
db.close()
ticker = {p: t for t, p in ETFS.items()}
crsp["ticker"] = crsp["permno"].map(ticker)
etfs = crsp.pivot(index="date", columns="ticker", values="ret")[list(ETFS)]

# ---- one table on French's trading days --------------------------------------
start = funds.index.min()
out = factors.loc[start:].join(funds, how="left").join(etfs, how="left")
out.index.name = "date"

# Anything that did not land on a French trading day would be silently dropped.
lost_funds = funds.index.difference(out.index)
lost_etfs = etfs.dropna(how="all").index.difference(out.index)
print(f"fund days not on French's calendar: {len(lost_funds)}   ETF days: {len(lost_etfs)}")

out.astype("float64").to_parquet(OUT)
print(f"\n{OUT.name}: {out.shape[0]:,} days, {out.index.min().date()} to {out.index.max().date()}")
print(f"{'':6s}{'first day':>12s}{'last day':>12s}{'days':>7s}")
for c in ["BRK", "ARKK"] + list(ETFS):
    s = out[c].dropna()
    print(f"{c:6s}{s.index.min().date()!s:>12s}{s.index.max().date()!s:>12s}{len(s):>7,d}")
