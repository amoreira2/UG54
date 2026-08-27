"""
Build sample CRSP and Compustat-derived CSVs for the WRDS Data Tour lecture.

Outputs:
  assets/data/wrds_tour_crsp_xs.csv      → full June 2020 cross-section
  assets/data/wrds_tour_aapl_full.csv    → AAPL monthly history 2002-2024
  assets/data/wrds_tour_chars_xs.csv     → June 2015 characteristics cross-section
"""

import pandas as pd
from pathlib import Path

OUT = Path("/Users/am16634/Documents/GitHub/UG54/assets/data")

# Load full CRSP monthly 2002-2024
crsp = pd.read_pickle(OUT / "crspm2002_2024.pkl")
crsp = crsp.drop_duplicates(subset=["permno", "date"])
print(f"CRSP loaded: {crsp.shape}")

# Slice 1: Full cross-section for one month (lots of stocks at one date)
xs_month = pd.Timestamp("2020-06-30")
xs = crsp[crsp["date"] == xs_month].copy()
xs.to_csv(OUT / "wrds_tour_crsp_xs.csv", index=False)
print(f"Cross-section (June 2020): {xs.shape}  → wrds_tour_crsp_xs.csv")

# Quick sanity: counts of share codes & exchanges
print("\n  shrcd counts (10/11 = common stock; 18 = ETF; 73 = closed-end fund):")
print(xs["shrcd"].value_counts().head(8).to_string())
print("\n  exchcd counts (1=NYSE, 2=AMEX, 3=NASDAQ):")
print(xs["exchcd"].value_counts().head(5).to_string())
print(f"\n  Negative prices (bid-ask midpoints): {(xs['prc'] < 0).sum()} of {len(xs)}")

# Slice 2: AAPL full history
aapl_permno = 14593   # AAPL's CRSP permno
aapl = crsp[crsp["permno"] == aapl_permno].sort_values("date").copy()
if len(aapl) == 0:
    # Try ticker lookup if permno wrong
    aapl = crsp[crsp["ticker"] == "AAPL"].sort_values("date").copy()
aapl.to_csv(OUT / "wrds_tour_aapl_full.csv", index=False)
print(f"\nAAPL monthly history: {aapl.shape}  → wrds_tour_aapl_full.csv")
print(f"  Date range: {aapl['date'].min().date()} to {aapl['date'].max().date()}")

# Slice 3: characteristics cross-section (June 2015)
chars = pd.read_pickle(OUT / "characteristics_raw.pkl")
chars["date"] = pd.to_datetime(chars["date"])
chars_xs_month = pd.Timestamp("2015-06-30")
chars_xs = chars[chars["date"] == chars_xs_month].copy()
# Keep just the columns we'll actually use in class
keep_cols = ["date", "permno", "re", "size", "value", "prof", "growth",
             "ep", "sp", "mom", "mom12", "price", "age"]
chars_xs = chars_xs[keep_cols]
chars_xs.to_csv(OUT / "wrds_tour_chars_xs.csv", index=False)
print(f"\nCharacteristics (June 2015): {chars_xs.shape}  → wrds_tour_chars_xs.csv")
print(f"  columns: size=log market cap, value=B/M, prof=profitability, ep=earnings/price, sp=sales/price")
