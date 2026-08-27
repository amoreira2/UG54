"""
Build the Factor Models AI challenge dataset.

Generates two synthetic fund return series (Fund_A, Fund_B) on top of real
historical market data, with deliberately contrasting properties:

  Fund A: low beta (~0.5), positive alpha (~8%/yr), low idio vol (~12%/yr)
  Fund B: high beta (~2.0), negative alpha (~-3%/yr), high idio vol (~25%/yr)

Both end up with similar total cumulative returns, so a naive "who made
more money" comparison is ambiguous. Students have to run the regression
and look at alpha / appraisal ratio to figure out who is actually skilled.

Output CSV columns: date, MKT (market excess), RF, Fund_A, Fund_B
  (Fund_A and Fund_B are TOTAL returns -- students must subtract RF.)
"""

import numpy as np
import pandas as pd
from pandas_datareader.data import DataReader

# Reproducible
rng = np.random.default_rng(20260524)

# Real market data: Fama-French daily factors
ff = DataReader("F-F_Research_Data_Factors_daily", "famafrench",
                start="2015-01-01", end="2024-12-31")[0] / 100
ff.index = pd.to_datetime(ff.index)
mkt = ff["Mkt-RF"]
rf = ff["RF"]
T = len(mkt)
print(f"Using {T} trading days, {mkt.index.min().date()} to {mkt.index.max().date()}")

# Target ANNUAL parameters.
# Fund B has HIGHER expected raw return (because of high beta in a bull
# market) but NEGATIVE alpha, so it looks better naively but is actually
# riding the market with no skill. Fund A has low beta + positive alpha.
alpha_A, beta_A, idio_A = 0.06, 0.6, 0.08
alpha_B, beta_B, idio_B = -0.04, 1.4, 0.15

# Convert to daily
def daily(annual_mean, annual_vol):
    return annual_mean / 252, annual_vol / np.sqrt(252)

mu_A, sig_A = daily(alpha_A, idio_A)
mu_B, sig_B = daily(alpha_B, idio_B)

# Generate excess returns: r_e = alpha + beta * mkt + epsilon
eps_A = rng.normal(0, sig_A, T)
eps_B = rng.normal(0, sig_B, T)

re_A = mu_A + beta_A * mkt.values + eps_A
re_B = mu_B + beta_B * mkt.values + eps_B

# Convert to total returns by adding RF back
ret_A = re_A + rf.values
ret_B = re_B + rf.values

out = pd.DataFrame({
    "MKT": mkt.values,    # already excess
    "RF":  rf.values,
    "Fund_A": ret_A,
    "Fund_B": ret_B,
}, index=mkt.index)
out.index.name = "date"

# Sanity check
print("\nRealized properties (annualized):")
for name, r in [("Fund_A", ret_A), ("Fund_B", ret_B)]:
    re = r - rf.values
    mean_ann = re.mean() * 252
    vol_ann = re.std() * np.sqrt(252)
    cov_mkt = np.cov(re, mkt.values)[0, 1]
    beta = cov_mkt / mkt.var()
    alpha = mean_ann - beta * (mkt.mean() * 252)
    idio = (re - beta * mkt.values).std() * np.sqrt(252)
    cum = (1 + r).prod() - 1
    print(f"  {name}: mean={mean_ann:.2%}, vol={vol_ann:.2%}, "
          f"beta={beta:.2f}, alpha={alpha:.2%}, idio={idio:.2%}, "
          f"cum={cum:.1%}")

out.to_csv("/Users/am16634/Documents/GitHub/UG54/assets/data/FactorModels_AI_challenge.csv")
print("\nWrote: assets/data/FactorModels_AI_challenge.csv")
