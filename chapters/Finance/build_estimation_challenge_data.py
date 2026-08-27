"""
Build the Factor Models II (Estimation) challenge dataset.

Generates two manager return series with the SAME full-sample alpha (~2%/yr)
but very different underlying truth:

  Manager X: real alpha = 3%/yr, persists in both halves, low idio vol
  Manager Y: TRUE alpha = 0, but high idio vol => realized alpha noisy.
             We pick a seed where realized alpha is big and positive in
             half 1 (~+8%) and negative in half 2 (~-4%). Full sample
             still looks vaguely positive.

The pedagogical point: full-sample alpha is misleading without checking
persistence. Manager X has the smaller full-sample alpha but is the
actual hire.
"""

import numpy as np
import pandas as pd
from pandas_datareader.data import DataReader

# Reproducible. Seed chosen to give the "lucky first half, unlucky second"
# pattern for Manager Y.
rng = np.random.default_rng(11)

ff = DataReader("F-F_Research_Data_Factors_daily", "famafrench",
                start="2015-01-01", end="2024-12-31")[0] / 100
ff.index = pd.to_datetime(ff.index)
mkt = ff["Mkt-RF"]
rf = ff["RF"]
T = len(mkt)
mid = T // 2
print(f"Sample: {T} days, midpoint = {mkt.index[mid].date()}")


def daily(annual_mean, annual_vol):
    return annual_mean / 252, annual_vol / np.sqrt(252)


# Manager X — small but real alpha, low idio vol
mu_x, sig_x = daily(0.03, 0.10)
beta_x = 1.0
eps_x = rng.normal(0, sig_x, T)
re_x = mu_x + beta_x * mkt.values + eps_x

# Manager Y — ZERO true alpha, high idio vol.
# We boost half-1 epsilon by a constant to engineer "lucky first half."
mu_y, sig_y = daily(0.00, 0.22)
beta_y = 1.3
eps_y = rng.normal(0, sig_y, T)
# Add a constant drift in half 1 and a negative drift in half 2.
# (Daily 6%/252 ≈ 0.024%/day boost in first half.)
eps_y[:mid] += 0.04 / 252
eps_y[mid:] -= 0.03 / 252
re_y = mu_y + beta_y * mkt.values + eps_y

# Convert to total returns
ret_x = re_x + rf.values
ret_y = re_y + rf.values

out = pd.DataFrame({
    "MKT": mkt.values,
    "RF":  rf.values,
    "Mgr_X": ret_x,
    "Mgr_Y": ret_y,
}, index=mkt.index)
out.index.name = "date"

# Diagnostic: full-sample and half-sample alphas
def fit(re, mkt):
    X = np.column_stack([np.ones_like(mkt), mkt])
    b, *_ = np.linalg.lstsq(X, re, rcond=None)
    return b[0] * 252, b[1]  # annualized alpha, beta

for name, re in [("Mgr_X", re_x), ("Mgr_Y", re_y)]:
    a_full, b_full = fit(re, mkt.values)
    a_h1, b_h1 = fit(re[:mid], mkt.values[:mid])
    a_h2, b_h2 = fit(re[mid:], mkt.values[mid:])
    print(f"\n{name}:")
    print(f"  Full sample: α = {a_full:>+7.2%}/yr,  β = {b_full:.2f}")
    print(f"  Half 1:      α = {a_h1:>+7.2%}/yr,  β = {b_h1:.2f}")
    print(f"  Half 2:      α = {a_h2:>+7.2%}/yr,  β = {b_h2:.2f}")
    print(f"  Persistence: α2/α1 = {a_h2/a_h1:+.2f}" if a_h1 != 0 else "")

out.to_csv("/Users/am16634/Documents/GitHub/UG54/assets/data/Estimation_AI_challenge.csv")
print("\nWrote: assets/data/Estimation_AI_challenge.csv")
