"""
Auto-evaluator for UG54 student notebook submissions.

Workflow per submission:
  1. Read .ipynb from local folder (sync from Drive separately, e.g. rclone)
  2. Execute notebook in a sandbox, extract SUBMISSION dict
  3. Compare numeric answers to known-correct values (±tolerance)
  4. Ask Claude to grade the Q5 memo against a rubric
  5. Write a row to Google Sheets, write per-student feedback .md

This is a STARTER. You'll tune the rubric and the SUBMISSION schema per
assignment. The structure is meant to be copied per assignment with the
rubric/keys swapped out.

Setup:
    pip install nbformat nbconvert anthropic gspread google-auth
    export ANTHROPIC_API_KEY=sk-...
    # Service account JSON at ./service_account.json with gspread access
    # to the gradebook sheet.

Usage:
    python auto_evaluator.py \\
        --inbox ./submissions/FactorModels \\
        --feedback ./feedback/FactorModels \\
        --assignment FactorModels_AI \\
        --sheet "UG54 Gradebook"
"""

import argparse
import json
import os
import sys
import hashlib
import traceback
from pathlib import Path
from datetime import datetime

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from anthropic import Anthropic

# ─── Per-assignment configuration ─────────────────────────────────────
# These are the "ground truth" values your evaluator checks against.
# Compute these once from your solution notebook; tolerance is fractional
# (0.05 = within 5% of true value).
ANSWER_KEY = {
    # WRDS tour uses self-consistency, not fixed values. The "_dynamic_"
    # marker tells grade_numeric to dispatch to grade_wrds_tour instead.
    "WRDS_Tour_AI": "_dynamic_",
    "CrossSectional_I_AI": {
        # Single cross-section — these are highly sample-dependent.
        # Very loose tolerances; this is a methodology check, not a precision test.
        "q1_growth_return":  (0.00, 5.00),
        "q5_value_return":   (0.00, 5.00),
        "long_short_return": (0.00, 10.00),
        "mean_bm_growth":    (0.20, 1.50),
        "mean_bm_value":     (1.50, 1.50),
    },
    "CrossSectional_II_AI": {
        # Closed-form: sqrt(3) * 0.4 = 0.693 uncorrelated
        "sharpe_combined":            (0.693, 0.10),
        # With rho=0.5: sqrt(3/(1+2*0.5)) * 0.4 = 0.490
        "sharpe_combined_correlated": (0.490, 0.15),
        # Net sharpe = (0.06 - 0.008) / 0.08 = 0.65
        "sharpe_net":                 (0.65,  0.15),
    },
    "Momentum_AI": {
        "vol_scaled_sharpe":    (0.62,  0.20),   # Barroso-Santa-Clara
        "vol_scaled_worst":    (-0.15,  0.40),
        "raw_crash_ratio":      (0.233, 0.20),   # 0.07/0.30
        "scaled_crash_ratio":   (0.617, 0.30),   # depends on vol_scaled_*
    },
    "PerformanceEval_AI": {
        # mean=18%, vol=22%, rf=4% -> sharpe = (0.18-0.04)/0.22 = 0.636
        "fund_sharpe":             (0.636, 0.10),
        # T=60 months, sharpe=0.636 -> SE = sqrt((1+0.636^2/2)/60) ≈ 0.140
        "fund_sharpe_se":          (0.140, 0.20),
        "alpha_shrinkage":         (0.031, 0.20),   # 4.2 - 1.1 = 3.1pp
        "capm_alpha_significant":  (0.0,   0.50),   # t=1.8 NOT > 2 → False
        "ff3_alpha_significant":   (0.0,   0.50),   # t=0.5 → False
    },
    "CapitalAllocationII_AI": {
        # w_plugin = 0.12 / (3 * 0.10^2) = 4.0
        "w_plugin":     (4.0,  0.10),
        # T=36, SR=1.2 -> SE = sqrt((1+1.44/2)/36) = 0.226
        "sharpe_se":    (0.226, 0.20),
        "w_half_kelly": (2.0,  0.10),
    },
    "MultiFactorModels_AI": {
        # b * p contributions
        "contrib_MKT":           ( 0.088, 0.05),   # 1.10 * 0.08
        "contrib_SMB":           ( 0.006, 0.10),   # 0.30 * 0.02
        "contrib_HML":           (-0.006, 0.10),   # -0.20 * 0.03
        "contrib_RMW":           ( 0.006, 0.10),   # 0.15 * 0.04
        "contrib_CMA":           (-0.002, 0.50),   # -0.10 * 0.02
        "alpha_is_significant":  ( 0.0,   0.50),   # |1.2| not > 2
        "fraction_from_factors": ( 0.767, 0.15),   # 0.092 / 0.12
    },
    "RiskManagement_AI": {
        # sqrt((0.5*0.18)^2 + (0.20*0.08)^2) = sqrt(0.0081 + 0.000256) ≈ 0.0914
        "portfolio_vol":   (0.0914, 0.15),
        # 100M * (0.0914/sqrt(252)) * 1.65 ≈ 950k
        "var_95_dollars":  (950_000, 0.30),
        # vol 9.14% < 12% target → True
        "within_budget":   (1.0, 0.50),
    },
    "Implementation_AI": {
        "trading_cost_drag": (0.0120, 0.10),  # 1.5 * 8 / 10000
        "financing_drag":    (0.060,  0.05),  # 1 * 0.06
        "short_drag":        (0.0030, 0.15),  # 2 * 0.30 * 0.005
        # leveraged_gross = 0.16, drag = 0.075, net_return = 0.085
        "net_return":        (0.085,  0.15),
        # net_sharpe = 0.085 / 0.24 ≈ 0.354
        "net_sharpe":        (0.354,  0.20),
    },
    "ML_I_AI": {
        # Simulated data — exact values depend on random seed
        # Very loose tolerances for a methodology check
        "best_alpha":        (0.05,   3.00),  # alpha can vary widely
        "oos_r2":            (0.10,   3.00),  # any positive value passes
        "n_selected":        (10,     2.00),  # selected nonzero features
    },
    "ML_II_AI": {
        # All values from simulated data; methodology check
        "ols_oos_r2":        (0.05,   3.00),
        "rf_oos_r2":         (0.30,   1.00),
        "gbt_oos_r2":        (0.35,   1.00),
        "best_method_r2":    (0.35,   1.00),
    },
    "LLMs_AI": {
        # Tone scores: snippet 1 is positive (~+0.7), 2 negative (~-0.6), 3 neutral (~0)
        "tone_snippet_1":    ( 0.7,   1.00),
        "tone_snippet_2":    (-0.6,   1.00),
        "tone_snippet_3":    ( 0.0,   2.00),
        "avg_tone":          ( 0.03,  10.0),  # near zero — very loose
        "lookahead_risk":    ( 1.0,   0.50),  # answer is YES
    },
    "WhatIsAlpha_AI": {
        # Single allocation, hold for 1970. Range-check only.
        # truth=0 + abs tolerance: the grader uses |got| <= tol for truth=0.
        # Numbers wider than these tolerances are very unlikely from a real run.
        "port_annual_1970":  (0.0, 2.00),    # plausible 1-year return |x| <= 200%
        "mkt_1970_annual":   (0.0, 0.20),    # 1970 mkt is small; |x| <= 20%
        "eq_annual_1970":    (0.0, 0.30),    # eq-wt 1970 ~2.4%; |x| <= 30%
        "alpha_capm_ann":    (0.0, 5.00),    # |annualized alpha| <= 500%
        "alpha_eqwt_ann":    (0.0, 5.00),
        "alpha_ff3_ann":     (0.0, 5.00),
        "tstat_alpha_capm":  (0.0, 20.0),    # any t-stat
        "tstat_alpha_ff3":   (0.0, 20.0),
        "sr_mkt":            (0.0, 10.0),
        "sr_str":            (0.0, 10.0),
        "sr_best":           (0.0, 10.0),
    },
    "L8_Backtesting_AI": {
        # Estimate ends 1987-12, tune ends 1991-12, test 1992-01 to 2000-12.
        # 29 cached long-shorts; grid N in {1,3,5,10,20,29} x W in {ew,ivol,sharpe}.
        # Tuning picks N=20, ivol. Verified by executing the notebook 2026-08-27.
        "tuned_sharpe": (1.3140, 0.08),
        "naive_sharpe": (0.2427, 0.30),   # small number, loose tolerance
        "all29_sharpe": (1.0519, 0.08),
        "bonf_t":       (3.1340, 0.02),   # norm.isf(0.025/29) -- should be exact
    },
    "L7_Decomposition_AI": {
        # Berkshire 13F, 1996-12-31 snapshot, betas over 1992-01 to 1996-12.
        # Verified by executing the notebook 2026-08-07.
        # Compare with the 1999 lecture numbers: beta 1.08, factor share 73%.
        # The 1996 book is MORE concentrated (86.8% top-3) and more defensive.
        "bu_beta_96":       (0.58,  0.15),
        "top3_share_96":    (0.868, 0.08),
        "factor_share_96":  (0.38,  0.20),
        "top_name_spec_96": (0.79,  0.15),
    },
    "L6_MultiFactor_AI": {
        # Mom12m long-short up the factor ladder, 1980-2000. Verified 2026-08-07.
        # The whole point is that these DIFFER, so tolerances must be tight
        # enough that a student can't submit one number four times.
        "mom_alpha_capm": (0.1817, 0.12),
        "mom_alpha_ff3":  (0.2303, 0.12),
        "mom_alpha_ff5":  (0.2242, 0.12),
        "mom_alpha_ff6":  (0.0346, 0.40),   # small number, looser fractional band
        "mom_umd_beta":   (1.46,   0.12),
        "mom_r2_ff6":     (0.84,   0.10),
    },
    "L5_FactorZoo_AI": {
        # Correlation structure of 29 long-shorts, 251 common months.
        "mean_pairwise_corr": (0.049, 0.45),   # near zero -> loose fractional band
        "frac_high_corr":     (0.086, 0.30),
        "within_cat_corr":    (0.579, 0.15),
        "across_cat_corr":    (0.189, 0.20),
    },
    "L4_PerfEval_AI": {
        # Exxon (11850) and Pfizer (21936) vs the market, 1980-2000.
        # Verified by executing the notebook 2026-08-07.
        # Sharpe ratios are 0.720 and 0.718 -- indistinguishable. The point of
        # the challenge is that the DECOMPOSITION differs sharply even though
        # both the Sharpe and the appraisal ratios come out nearly equal.
        "xom_alpha_ann": (0.0676, 0.15),
        "xom_beta":      (0.59,   0.15),
        "xom_appraisal": (0.470,  0.15),
        "pfe_alpha_ann": (0.1087, 0.15),
        "pfe_beta":      (0.82,   0.15),
        "pfe_appraisal": (0.483,  0.15),
    },
    "L3_Sorts_AI": {
        # Size (small minus big) sorted on raw market cap, 1980-2000, four
        # implementations. Verified by executing the notebook 2026-08-06.
        # The point of the challenge is that these DISAGREE, so the tolerances
        # must be tight enough that a student can't hand in one number 4x.
        "t_ew_all":     ( 3.94, 0.15),
        "t_vw_all":     ( 1.90, 0.20),
        "t_ew_nyse":    (-0.56, 0.45),
        "t_vw_nyse":    (-1.93, 0.20),
        "n_small_all":  ( 597,  0.10),
        "n_small_nyse": (3106,  0.10),
    },
    "L2_Portfolios_AI": {
        # Rebuild the CRSP value-weighted market from the course panel,
        # 1980-2000. Verified by executing the notebook end-to-end 2026-08-06.
        "vw_mean_annual": (0.1574, 0.10),
        "vw_vol_annual":  (0.1553, 0.10),
        # Correlation with Ken French is 1.0000 to four decimals. A student who
        # forgets to shift their series forward one month gets ~0, so this is
        # the check that catches the alignment error.
        "corr_vw_ff":     (1.0000, 0.02),
        "ew_mean_annual": (0.1422, 0.12),
        "ew_vol_annual":  (0.1856, 0.10),
        "top10_share":    (0.2049, 0.15),
    },
    "L1_Returns_AI": {
        # GE (permno 12060) vs the market, 1980-2000, from the course panel.
        # Verified by executing the notebook end-to-end 2026-08-06.
        "ge_total_return": (84.428, 0.10),   # +8443% -> $1,000 becomes $85,428
        "ge_ann_excess":   (0.1713, 0.12),
        "ge_ann_vol":      (0.2216, 0.10),
        "ge_sharpe":       (0.773,  0.12),
        "mkt_sharpe":      (0.601,  0.10),
    },
    "StatisticalFactors_AI": {
        # 49 industry portfolios, LAST 120 MONTHS (pinned in the challenge).
        # N=49, T=120 -> c = 0.4083, MP upper edge = (1+sqrt(c))^2 = 2.686.
        # Verified by running the notebook end-to-end.
        "mp_edge_upper":      (2.686, 0.05),   # deterministic given the window
        "n_factors_mp":       (2.0,   0.50),   # accepts 1-3
        "pc1_share":          (0.556, 0.15),   # 47%-64%
        # Student's own noise draw. Mean 0.051, sd 0.002 across simulations, so
        # this band is very wide relative to sampling noise -- it exists to
        # catch students who report the REAL PC1 share here by mistake (0.556).
        "noise_pc1_share":    (0.054, 0.30),   # 3.8%-7.0%
        "n_factors_parallel": (2.0,   0.50),   # accepts 1-3
    },
    "Timing_AI": {
        # Spans two classes; four timing approaches compared.
        # The "predictor" entry is loose because students pick their own FRED
        # series and OOS split — we just verify it's a plausible Sharpe number.
        "sharpe_buyhold":               (0.58, 0.25),   # post-1991 baseline
        "sharpe_mean_timing_dp":        (0.75, 0.25),   # D/P, post-1991 OOS
        "sharpe_mean_timing_predictor": (0.50, 2.00),   # student's choice — VERY loose (-1 to 2 plausible)
        "sharpe_vol_timing_rv":         (0.50, 0.30),
        "sharpe_vol_timing_vix":        (0.66, 0.25),
    },
    "CapitalAllocationI_AI": {
        # FF6 monthly data (1926+) — computed from live Ken French data.
        # γ=4 per-factor weights: CMA (1.46) > RMW (1.33) > MOM (0.86)
        "best_factor_individual_weight":     (1.46,  0.25),
        "mve_annual_sharpe":                 (1.17,  0.20),
        "target_vol_leverage":               (0.128, 0.25),  # 0.15 / 1.171
        "target_vol_expected_return":        (0.176, 0.25),  # ≈ 17.6%
        "hedged_alpha_sharpe":               (1.08,  0.20),
        "combined_sharpe_market_plus_alpha": (1.17,  0.20),
    },
    "Portfolios_AI": {
        # GlobalFinMonthly.csv (1963-2016) — uses the source notebook's
        # actual dataset (US + International + Emerging + bonds).
        # Q1: 50/30/20 of MKT/WorldxUSA/EM
        "custom_annual_mean":   ( 0.0624, 0.15),
        "custom_annual_vol":    ( 0.1414, 0.15),
        "custom_annual_sharpe": ( 0.441,  0.15),
        # Q2: min-var MKT + WorldxUSA
        "w_intl_min_var":       ( 0.43,   0.20),
        "min_var_annual_vol":   ( 0.1410, 0.10),
        "us_only_annual_vol":   ( 0.1530, 0.10),
        # Q3: best Sharpe of (US, Intl, EM) — grid 0.05
        "best_sharpe_3asset":   ( 0.464,  0.15),
        "w_us_best":            ( 0.60,   0.30),
        "w_intl_best":          ( 0.00,   2.00),   # near-zero — loose
        "w_em_best":            ( 0.40,   0.40),
    },
    "IntrotoReturns_AI": {
        # SPY 2010-2024 — values change slightly with each new Yahoo fetch.
        # Loose tolerances because the sample window is fixed but the data
        # source can be revised retroactively.
        "spy_annual_mean":    (0.13,  0.30),   # ~13%/yr in this window
        "spy_annual_vol":     (0.17,  0.25),
        "spy_annual_sharpe":  (0.75,  0.40),
        "spy_worst_year":    (-0.18,  0.30),   # 2022
        "spy_best_year":      (0.32,  0.30),   # 2013
        "spy_negative_years": (3,     1.00),   # ±1 year tolerance
    },
    "FactorModels_II_AI": {
        # Full-sample alphas: very close to identical (the pedagogical hook).
        "alpha_x_full":  ( 0.044,  0.30),
        "alpha_y_full":  ( 0.042,  0.30),
        "tstat_x_full":  ( 1.38,   0.50),  # generous — small differences ok
        "tstat_y_full":  ( 0.61,   0.80),
        # Half-sample alphas: this is where the truth lives.
        "alpha_x_half1": ( 0.045,  0.30),
        "alpha_x_half2": ( 0.042,  0.30),
        "alpha_y_half1": ( 0.101,  0.20),
        "alpha_y_half2": (-0.013,  1.00),  # near zero → loose tolerance
        # Persistence ratio: the key diagnostic.
        "persistence_x": ( 0.92,   0.30),
        "persistence_y": (-0.13,   1.50),  # near zero/sign-sensitive → very loose
        # Rolling beta std: ancillary.
        "beta_std_x":    ( 0.04,   0.50),
        "beta_std_y":    ( 0.12,   0.40),
    },
    "FactorModels_AI": {
        # Keys MUST match variable names students use in their submission cell.
        # tolerance is fractional (0.30 = within 30% of true value).
        "fund_a_total_return": (1.85, 0.10),   # ~185% over 10 years
        "fund_b_total_return": (0.30, 0.30),
        "alpha_a_annual":      (0.033, 0.50),  # alpha is noisy — generous tol
        "beta_a":              (0.60, 0.15),
        "alpha_b_annual":     (-0.116, 0.30),
        "beta_b":              (1.40, 0.15),
        "appraisal_a":         (0.43, 0.40),
        "appraisal_b":        (-0.78, 0.30),
        # position_a/b depend on student's choice of vol calc — skip from key
    },
}

MEMO_RUBRICS = {
    "L8_Backtesting_AI": """
You are grading a memo on backtesting protocol. Students have just met the
estimate/tune/test split, walk-forward testing, and Bonferroni.

THE QUESTION: having run the process on two different splits, recommend one of
three rules to the PM -- the tuned combination, the single best in-sample
signal, or all 29 equal-weighted. And answer: if the naive rule earned 11.8%/yr
in the walk-forward and the tuned process earned 5.6%, why not recommend it?

GROUND TRUTH:
- The naive rule's 11.8% comes with 15.3% volatility and a 24% drawdown, against
  3.8% and 4% for the tuned process. Sharpe 0.77 vs 1.48. Comparing returns
  without comparing risk is the trap, and it is the whole of the last question.
  A student who does not resolve this cannot score above 3.
- WHAT CHANGED between the two splits: the levels. Class split gave tuned 1.13,
  naive -0.08, all-29 0.85; the homework split gives 1.31, 0.24, 1.05.
- WHAT DID NOT CHANGE: the ordering. Tuned > all-29 > naive, in both, and in the
  three other splits shown in class. **The ordering is the finding; the levels
  are not.** A student who says this has the main point.
- Good answers note that all-29 equal-weighted is close behind the tuned rule
  while requiring no tuning at all, so most of the gain is diversification
  rather than clever parameter choice. Recommending all-29 on robustness grounds
  is a perfectly defensible answer and should score well if argued.
- On what they would need before trusting a single Sharpe: the standard error
  (~0.42 on six years, so these numbers are not distinguishable from each other),
  a bootstrap interval, fraction to half, and how many strategies were searched.

GRADE THE REASONING, NOT THE ARITHMETIC. Quoting the numbers is evidence they
looked; it earns no credit on its own. Never deduct for not quoting figures.

Grade 0-5:
  5 = Picks a rule and defends it; separates what changed (levels) from what did
      not (ordering) and says which is the finding; resolves the return-vs-risk
      question explicitly.
  4 = Two of those three, reasoned well.
  3 = Picks a rule with some justification and handles the return-vs-risk
      question, but treats the two splits as simply confirming each other.
  2 = Recommends the naive rule on the strength of its return, or picks a rule
      with no argument.
  1 = Restates the tables.
  0 = Empty or off-topic.

PENALIZE: treating a Sharpe difference of 0.1-0.2 as meaningful on six years of
data; claiming the test sample proves the strategy will work in future.
DO NOT PENALIZE a well-argued recommendation of all-29 over the tuned rule.

For picked_fund return "neither".
For cited_appraisal_or_alpha return True if the memo makes any risk-adjusted
comparison rather than comparing raw returns, else False.

Output via the `grade_memo` tool.
""",
    "L7_Decomposition_AI": """
Grading a week-7 memo to a risk committee asking: "we already regress the fund's
returns on factors -- why pay for a holdings-based system?"

GROUND TRUTH (Berkshire, from the lecture and the challenge):
- 1999 snapshot: top-down CAPM beta 0.68 (se 0.26); bottom-up 1.08. FF6 top-down
  gave HML +2.08 (se 0.61) and CMA -2.20 (se 1.01) -- four of six loadings not
  two standard errors from zero on 41 months.
- 1996 snapshot: bottom-up beta 0.58, top-3 weight 86.8%, factor share of
  variance 38%, largest name 79% of specific variance.
- So the bottom-up beta moved 0.58 -> 1.08 between 1996 and 1999 as the book
  shifted from Coca-Cola/Gillette/Wells Fargo to Coca-Cola/American Express.
  A single time-series regression over 1992-1999 would report ONE number and
  miss that entirely.
- WHAT BOTTOM-UP GIVES: current exposure rather than a window average; reacts to
  a trade immediately; attributes risk to named positions (Coca-Cola supplied
  67% of specific variance in 1999, 79% in 1996).
- WHAT IT COSTS: you need holdings, and holdings are disclosed quarterly, with a
  lag, and incompletely. You also need a beta per name -- n x m estimates rather
  than m.
- WHERE TOP-DOWN IS THE ONLY OPTION: any fund that doesn't disclose holdings --
  hedge funds, most private vehicles, or any manager you're evaluating from a
  track record alone. Also anything pre-1980 or non-US-listed.
- THE 13F POINT: it covers US-listed equity only. Berkshire's GEICO position is
  visible as a 13F holding in 1993 (15% of the book) and DISAPPEARS after the
  1996 buyout -- not sold, just no longer a marketable security. The operating
  businesses, the insurance float and the leverage never appear at all.

Grade 0-5:
  5 = Names a concrete thing bottom-up reveals that top-down cannot, using the
      numbers (the 0.58 -> 1.08 shift, or the concentration of specific risk);
      states the cost honestly; identifies a case where top-down is the only
      option; and says something specific about 13F limits (GEICO, or that the
      disclosed book is only part of Berkshire).
  4 = Three of those four, with numbers.
  3 = Right direction, argues from the concepts without using the numbers.
  2 = Asserts bottom-up is better with no argument, or ignores the costs.
  1 = Restates the table.
  0 = Empty or off-topic.

PENALIZE: claiming top-down is simply wrong -- it answers a different question
and is the ONLY option for undisclosed portfolios. Also penalize treating the
top-down/bottom-up gap as pure economics without acknowledging that some of it
is estimation noise (the FF6 standard errors).

For picked_fund return "neither".
For cited_appraisal_or_alpha return True if the memo cites a specific number
from either snapshot, else False.

Output via the `grade_memo` tool.
""",
    "L6_MultiFactor_AI": """
Grading a week-6 memo. Students have factor regressions, multi-factor models and
Fama-MacBeth. They have NOT seen multiple testing, out-of-sample testing, or
transaction costs.

THE QUESTION: should the PM pay for a momentum manager? Momentum's alpha is
+18.17%/yr vs CAPM and +3.46%/yr (t=1.75) vs FF6.

GROUND TRUTH:
- The defensible answer is the FF6 number, because UMD is a cheaply investable
  momentum factor. Paying an active fee for exposure you can buy in an ETF is
  paying for beta.
- UMD loading is 1.46 with R2 jumping 0.12 -> 0.84. In plain language: this
  strategy IS the momentum factor, slightly levered. 84% of its month-to-month
  variation is explained by a factor anyone can buy.
- At FF6 the alpha is 3.46% with t = 1.75 -- it does NOT clear the conventional
  |t| > 2 bar. So even the residual is not established.
- The CAPM number would be right only if UMD were NOT investable -- e.g. no
  momentum ETF exists, or the fund accesses momentum in a market where it can't
  be bought cheaply. A student who articulates that condition has understood the
  whole lecture.
- Strong memos may note the model should be fixed BEFORE looking, so choosing
  CAPM after seeing that it gives a bigger number is exactly the error.

Grade 0-5:
  5 = Picks FF6 with the investability argument; explains the UMD loading as
      "this is the momentum factor, levered ~1.5x"; notes t=1.75 fails the usual
      bar; states the condition under which CAPM would be right.
  4 = Picks FF6 with a sound investability argument and reads the loading
      correctly, but misses either the t-stat point or the CAPM condition.
  3 = Picks FF6 but justifies it only as "more factors is more conservative".
  2 = Picks CAPM's 18% without engaging with the UMD loading.
  1 = Reports the numbers with no recommendation.
  0 = Empty or off-topic.

PENALIZE: treating the FF6 R-squared of 0.84 as evidence the strategy is GOOD --
it is evidence the strategy is REPLICABLE, which is the opposite of the case for
paying a fee.

For picked_fund return "neither".
For cited_appraisal_or_alpha return True if the memo uses alpha or the factor
loading in its argument, else False.

Output via the `grade_memo` tool.
""",
    "L5_FactorZoo_AI": """
Grading a week-5 memo to an investment committee that believes "we run a
30-factor model, so we're extremely diversified."

GROUND TRUTH (29 long-shorts, 251 months, 1980-2000):
- Mean pairwise correlation +0.049; only 8.6% of pairs exceed |0.5|. Taken
  alone this SUPPORTS the committee.
- But mean |corr| WITHIN economic category is 0.579 vs 0.189 ACROSS -- a 3.1x
  difference. The average hides block structure.
- Near-duplicates: MaxRet/RealizedVol 0.97, IdioVol3F/RealizedVol 0.96,
  IdioVol3F/MaxRet 0.94, Illiquidity/Size 0.92, DolVol/Illiquidity 0.89.
- Correct recommendation: diversification comes from spanning FAMILIES, not
  from collecting names. Count distinct bets (roughly the number of economic
  categories represented), not signals. Adding a fourth volatility signal adds
  nothing.

Grade 0-5:
  5 = Uses BOTH numbers and explains why they conflict (the average is diluted
      by the many across-category pairs); names a specific near-duplicate pair
      with its correlation; recommends counting families rather than signals.
  4 = Both numbers and the right recommendation, but no specific pair named, or
      the reconciliation of the two numbers is vague.
  3 = Notices the within/across gap but doesn't turn it into a recommendation.
  2 = Reports the average correlation and concludes "diversified" -- the exact
      trap the lecture is built around.
  1 = Restates numbers with no argument.
  0 = Empty or off-topic.

PENALIZE: concluding the model IS well diversified on the strength of the +0.05
average alone. Also penalize claiming high correlation is inherently bad -- the
point is double-counting of evidence and false diversification, not that
correlated signals are useless.

For picked_fund return "neither".
For cited_appraisal_or_alpha return True if the memo cites a specific
correlation number in its argument, else False.

Output via the `grade_memo` tool.
""",
    "L4_PerfEval_AI": """
You are grading a week-4 memo. Students have just met factor regressions, alpha,
beta, and the appraisal ratio. They have NOT seen multi-factor models, multiple
testing, or transaction costs.

THE QUESTION: Exxon and Pfizer have Sharpe ratios of 0.720 and 0.718. After
running the regressions, are the two positions interchangeable for a CIO who
already holds the market?

GROUND TRUTH (1980-2000, monthly, vs Mkt-RF):
  Exxon : alpha  +6.76%/yr (t=2.12), beta 0.59, idio vol 14.4%, appraisal 0.470
  Pfizer: alpha +10.87%/yr (t=2.18), beta 0.82, idio vol 22.5%, appraisal 0.483

- The Sharpe ratios match, AND the appraisal ratios nearly match (0.470 vs
  0.483). So on a per-unit-of-idiosyncratic-risk basis they really are close to
  equivalent. A student who says "the ratios say they're the same" is CORRECT,
  not lazy -- but should notice this is a non-obvious result.
- What DIFFERS is the composition. Pfizer delivers 60% more alpha (10.9% vs
  6.8%) but carries 56% more idiosyncratic risk (22.5% vs 14.4%). The ratio is
  the same because both scale together.
- Beta differs materially: 0.59 vs 0.82. Adding Exxon changes your total market
  exposure much less. For a CIO already at their target market exposure, the
  lower-beta position is easier to size without rebalancing the core.
- Best answers note something the ratios DON'T capture. Any of: position size
  needed to move the needle (Pfizer gives more alpha per dollar deployed);
  capacity/liquidity; that a single stock's alpha is not diversified regardless
  of ratio; that t-stats of ~2.1 over 20 years are marginal for both; that these
  are two firms picked with hindsight.

Grade 0-5:
  5 = Reports both decompositions correctly; recognizes the appraisal ratios are
      close so the ratios call them equivalent; identifies the beta difference
      or the alpha/idio-scale difference as what actually separates them; raises
      at least one consideration the ratios miss.
  4 = Correct decomposition and the equivalence point, plus one of the two
      differentiators, but nothing beyond the ratios.
  3 = Correct numbers, concludes "the same" or "Pfizer" without engaging with
      why the appraisal ratios match.
  2 = Reports the regressions but the argument doesn't follow from them.
  1 = Restates the Sharpe ratios.
  0 = Empty or off-topic.

PENALIZE: claiming Pfizer is clearly better because its alpha is bigger, with no
mention of its higher idiosyncratic risk -- that is the exact error the appraisal
ratio exists to prevent. Also penalize treating a higher R-squared as better.

For picked_fund return "neither" unless the memo clearly picks one, in which
case return "A" for Exxon or "B" for Pfizer.
For cited_appraisal_or_alpha return True if the memo uses alpha or the appraisal
ratio in its argument, else False.

Output via the `grade_memo` tool.
""",
    "L3_Sorts_AI": """
You are grading a week-3 memo to a portfolio manager. Students have seen
returns, Sharpe, portfolio weights, and sorts. They have NOT seen factor
models, alpha, beta, or formal multiple-testing corrections.

THE QUESTION: does the size effect exist over 1980-2000? They computed four
defensible implementations of small-minus-big:
    all-stock deciles, EW   +20.7%/yr   t =  3.94
    all-stock deciles, VW    +9.2%/yr   t =  1.90
    NYSE breakpoints,  EW    -2.1%/yr   t = -0.56
    NYSE breakpoints,  VW    -6.4%/yr   t = -1.93

GROUND TRUTH:
- The defensible answer is "no usable size effect over this period", reported
  on the NYSE-breakpoint value-weighted specification, which is the academic
  and industry standard and the only one implementable at scale.
- MECHANISM: all-stock deciles put ~597 of the very smallest listed firms in
  the bottom bucket; equal-weighting then lets microcaps worth a few million
  dollars drive the average. NYSE breakpoints define "small" relative to NYSE
  and sweep in ~3,106 names, so the extreme tail stops dominating.
- The +20.7% is REAL ARITHMETIC but uninvestable: bid-ask spreads on 600 of the
  tiniest US firms, rebalanced monthly, would consume the spread. A student who
  says this deserves credit even without cost numbers.
- Banz published the size premium in 1981, at the start of this sample. Noting
  that it did not survive its own publication is a strong observation but NOT
  required for a 5.

A memo that reports all four numbers without committing to one has not done the
job -- the PM asked a question. Say so in the feedback.

Grade 0-5:
  5 = Commits to ONE answer; names the specification and justifies it
      (standard / tradability / not microcap-driven); explains the mechanism
      via bucket composition or weighting; says something substantive about why
      the +20.7% is not actionable.
  4 = Commits to one answer with a real justification and the mechanism, but
      the tradability point is thin or missing.
  3 = Commits to an answer but justifies it mainly by "it's the convention",
      with little mechanism.
  2 = Describes the disagreement without committing, or commits arbitrarily.
  1 = Restates the table.
  0 = Empty or off-topic.

ACCEPT a well-argued minority answer. A student who reports the EW all-stock
result AND explicitly says it is not implementable, and explains who it might
be relevant to, can score 4-5. Reward the reasoning, not the conclusion.

PENALIZE: presenting all four numbers as equally valid with no recommendation;
claiming one specification is "wrong" arithmetically (none are).

For picked_fund return "neither" (not applicable).
For cited_appraisal_or_alpha return True if the memo gives a concrete
tradability, liquidity, or transaction-cost reason, else False.

Output via the `grade_memo` tool.
""",
    "L2_Portfolios_AI": """
You are grading a second-week memo from an undergraduate. They have seen returns,
Sharpe ratios, and portfolio weights. They have NOT seen factor models or beta.

THE QUESTION: they built value-weighted and equal-weighted portfolios from the
same ~6,000 stocks. EW earned 14.22%/yr with 18.6% vol; VW earned 15.74%/yr with
15.5% vol. Why do they differ, which is "the market", and why might the EW
return overstate what was achievable?

GROUND TRUTH:
- There are far more small firms than large ones, so equal weighting puts most
  of its money in small stocks. EW is an unintentional small-cap bet; VW is
  dominated by the largest firms (top 10 = 20.5% of total market cap).
- VW deserves to be called "the market" because it is the only weighting ALL
  investors can hold simultaneously -- it is the aggregate portfolio. There are
  not enough shares of small firms for everyone to equal-weight.
- EW overstates achievable returns because the smallest names are illiquid,
  cannot absorb capital, and would cost far more to trade; EW also requires
  constant rebalancing (selling winners, buying losers) which multiplies costs.
- Bonus insight: EW lost to VW here despite holding riskier stocks, which is
  evidence against a size premium over this window.

Grade 0-5:
  5 = Explains the small-cap tilt from the NUMBER of small firms; argues VW is
      the market on aggregation/market-clearing grounds; gives a concrete
      liquidity/tradability or rebalancing-cost reason EW overstates.
  4 = Gets the small-cap tilt and one of the other two clearly.
  3 = Correct intuition about small vs large driving the gap, but the "which is
      the market" argument is asserted rather than reasoned.
  2 = Notices the portfolios differ without explaining the mechanism.
  1 = Restates the numbers.
  0 = Empty or off-topic.

PENALIZE: claiming EW is riskier ONLY because it has more stocks (it has the
same stocks); saying VW is "the market" purely because that is convention.

For picked_fund return "neither" (not applicable).
For cited_appraisal_or_alpha return True if the memo gives a concrete
tradability, liquidity, or transaction-cost reason, else False.

Output via the `grade_memo` tool.
""",
    "L1_Returns_AI": """
You are grading a first-week memo from an undergraduate. This is Lecture 1 --
they have NOT yet seen factor models, beta, or alpha. Grade what they can
reasonably notice, not what a finance PhD would say.

THE QUESTION: GE's annualized Sharpe ratio was 0.773 over 1980-2000 vs the
market's 0.601. Does that prove Jack Welch was an exceptional manager?

GROUND TRUTH:
- GE's volatility was 22.2% vs the market's 15.6% -- about 40% MORE volatile.
- So GE took more risk. Some of the extra return is compensation for that risk,
  not skill. A student who spots this has got the main point.
- The Sharpe ratio already adjusts for TOTAL volatility, so GE's higher Sharpe
  is genuinely something -- it is not nothing. The honest answer is "suggestive,
  not proof."
- What you'd want next: how much of GE's return is explained by simply being a
  levered bet on the market (its beta), and what is left over. That is exactly
  what Lecture 4 does. A student who gestures at this -- even without the words
  "beta" or "alpha" -- deserves full credit.
- Other good observations: 20 years is one sample and GE was SELECTED because it
  was famous (survivorship / hindsight); conglomerates are diversified so this
  may be a portfolio effect; GE Capital made GE partly a financial firm.

GRADE THE REASONING, NOT THE ARITHMETIC. Quoting 22.2% vs 15.6% is evidence a
student looked, but it is not the skill being tested and it earns no credit on
its own. A memo that argues correctly in words scores exactly the same as one
that cites the figures. Never deduct for not quoting numbers.

Grade 0-5:
  5 = Recognizes that a higher Sharpe is suggestive but not decisive, AND names
      something that would settle it -- a risk difference the Sharpe ratio does
      not capture, market exposure, a proper benchmark, or the fact that GE was
      chosen because it was famous.
  4 = Recognizes the comparison is incomplete and reasons correctly about why,
      but stops short of saying what would settle it.
  3 = Gestures at risk but the argument is thin, one-sided, or asserted rather
      than reasoned.
  2 = Answers the question while ignoring risk entirely -- e.g. "yes, higher
      Sharpe means he was better."
  1 = Restates the numbers or the question without an argument.
  0 = Empty or off-topic.

DO NOT penalize a student for not using the words "alpha", "beta", or "CAPM" --
they have not been taught yet. A student who says "riskier in a way volatility
doesn't capture" has made exactly the right move and should be graded as such.
DO reward noticing that the comparison is incomplete.

For picked_fund return "neither" (not applicable).
For cited_appraisal_or_alpha return True if the memo argues that the Sharpe
comparison is incomplete -- whether by pointing at the risk difference, asking
for a benchmark or risk-adjusted comparison, or raising selection bias -- else
False. Do not require that any number be quoted.

Output via the `grade_memo` tool.
""",
    "StatisticalFactors_AI": """
You are grading a junior risk analyst's memo to their boss, who instructed them
to "just use ten principal components, that's what we've always done."

GROUND TRUTH (49 industry portfolios, last 120 months, c = N/T = 0.4083):
- Marchenko-Pastur upper edge = 2.686. Exactly 2 eigenvalues exceed it.
- Parallel analysis, which makes no appeal to MP theory, independently returns 2.
  The two methods agree, and the parallel-analysis cutoff for PC1 (2.68) lands
  essentially on the MP edge.
- PC1 explains 55.6% of variance. Pure noise at the same N and T produces a PC1
  share of about 5%. So PC1 is clearly real -- but the 55.6% figure ALONE proves
  nothing without that null for comparison.
- The Kaiser rule (eigenvalue > 1) returns 7. It is a plausible-looking wrong
  answer that several statistics packages produce by default.
- Keeping 10 components means 8 sit inside the noise bulk. Because the optimizer
  inverts Sigma, small noise eigenvalues become large offsetting positions: in
  the notebook, raw Sigma produces 8.2x gross leverage, a 66% single position,
  and 20.0% out-of-sample volatility, versus 3.0x, 40%, and 13.7% after filtering.
- Correct hedge: factors whose population spike falls below the BBP threshold
  (1 + sqrt(c) = 1.64) are undetectable at this N and T. So "2 factors" means
  "2 that this data can identify", NOT "only 2 exist".

Grade 0-5:
  5 = States 2 (or defensibly 2-3) with evidence; cites BOTH MP and parallel
      analysis agreeing; explains why "% variance explained" is not evidence on
      its own; names a concrete operational cost of over-selecting (leverage,
      turnover, or unstable hedges); acknowledges undetectable factors.
  4 = Right number, solid evidence including the noise-null argument, but misses
      either the operational cost or the undetectability caveat.
  3 = Right number, thin justification -- asserts "the rest is noise" without
      naming a method or a consequence.
  2 = Vague. Gestures at "too many factors" with no number or no evidence.
  1 = Wrong number (accepts 10, or adopts Kaiser's 7 uncritically) but engages
      with the noise idea at all.
  0 = Empty, off-topic, or simply agrees with the boss.

PENALIZE:
- Treating "PC1 explains 55%" as sufficient evidence for anything.
- Claiming the data proves only 2 factors EXIST (overclaiming past detectability).
- Recommending a number with no stated method.

For picked_fund return "neither" (not applicable to this assignment).
For cited_appraisal_or_alpha return True if the memo cites a specific
quantitative criterion (the MP edge, parallel analysis, or a simulated null),
else False.

Output via the `grade_memo` tool.
""",
    "CrossSectional_I_AI": """
Grading a 5-sentence memo on a SINGLE cross-section value-strategy test.

GROUND TRUTH:
- A single cross-section is NOT a valid test of the value premium.
- A real test requires the recipe averaged over many months and decades.
- The biggest pitfall in "discovering a new strategy" is multiple testing
  (trying many characteristics until one looks good).

Grade 0-5:
  5 = Notes single cross-section is insufficient, names the multi-period
      methodology needed, mentions multiple-testing or survivorship.
  4 = Two of the three.
  3 = One concrete point.
  2 = Hand-wavy.
  1 = Treats single-period result as evidence.
  0 = Empty.

picked_fund "A"; cited_appraisal_or_alpha False.
""",
    "CrossSectional_II_AI": """
Grading a memo on whether to deploy a 3-signal cross-sectional strategy.

GROUND TRUTH:
- Combined Sharpe (uncorrelated, 3 signals at 0.4) = 0.69; with rho=0.5 = 0.49.
- Net Sharpe after 0.8% cost on 8% vol portfolio drops by 0.1 per 0.8% cost.
- The biggest risk in practice is signal correlation and crowding.

Grade 0-5:
  5 = Cites Sharpe gain, correlation impact, AND cost impact; recommends defensibly.
  4 = Two of the three.
  3 = One.
  2 = Hand-wavy.
  1 = Recommends based on gross numbers only.
  0 = Empty.
""",
    "Momentum_AI": """
Grading a memo recommending raw vs vol-scaled momentum.

GROUND TRUTH:
- Vol-scaled momentum improves Sharpe ~0.47 → ~0.62 AND cuts worst month roughly in half.
- Vol-scaled is appropriate for risk-averse investors; raw for those who can stomach drawdowns.
- Real-world implementation requires high turnover and leverage management.

Grade 0-5:
  5 = Defensible recommendation citing Sharpe AND crash-risk numbers AND noting investor-fit.
  4 = Two of three.
  3 = One.
  2 = Hand-wavy.
  1 = Ignores crash risk entirely.
  0 = Empty.
""",
    "PerformanceEval_AI": """
Grading a memo evaluating a fund with CAPM α=4.2% (t=1.8), FF3 α=1.1% (t=0.5),
Sharpe=0.64 over 5 years.

GROUND TRUTH:
- Both alphas are statistically indistinguishable from zero (|t| < 2).
- Most of the apparent CAPM alpha disappears when you control for size/value.
- The right benchmark for a tilted fund is multi-factor, not CAPM.
- Sharpe SE is wide on a 5-year sample.

Grade 0-5:
  5 = Notes alpha is not significant, notes FF3 shrinkage, mentions Sharpe uncertainty.
  4 = Two of three.
  3 = One.
  2 = Recommends invest based on Sharpe alone.
  1 = Mistakes CAPM alpha for skill.
  0 = Empty.
""",
    "CapitalAllocationII_AI": """
Grading a memo on sizing a strategy with backtest Sharpe 1.2 over 3 years.

GROUND TRUTH:
- Plug-in weight = 4.0 is too aggressive given parameter uncertainty.
- Half-Kelly (= 2.0) is the standard robust answer.
- Sharpe SE = 0.226 → wide 95% CI; the realized 1.2 is one draw.

Grade 0-5:
  5 = Recommends ≤ half-Kelly sizing, cites Sharpe SE, names estimation error as the reason.
  4 = Two of three.
  3 = One.
  2 = Recommends plug-in size with weak justification.
  1 = Says "just take the optimal weight" with no caveat.
  0 = Empty.
""",
    "MultiFactorModels_AI": """
Grading a memo on a fund with FF5 loadings.

GROUND TRUTH:
- α = 1.5%/yr (t=1.2) is NOT significant.
- Total return decomposition: ~9.2% from factor exposure, rest from alpha + noise.
- ~75% of returns come from factor tilts; the manager isn't earning much "true" alpha.

Grade 0-5:
  5 = Notes alpha is not significant, identifies factor tilts driving returns,
      argues fees should reflect commodity-beta exposure.
  4 = Two of three.
  3 = One.
  2 = Recommends invest without distinguishing alpha from beta.
  1 = Treats raw return as alpha.
  0 = Empty.
""",
    "RiskManagement_AI": """
Grading a memo on a portfolio's risk budget.

GROUND TRUTH:
- Portfolio vol ≈ 9.1% — within 12% target.
- Daily VaR ≈ $950K on $100M NAV.
- VaR assumes normality; actual tails are worse.

Grade 0-5:
  5 = Cites vol vs target, daily VaR, AND notes normal-VaR understates tails.
  4 = Two of three.
  3 = One.
  2 = Recommends "scale up because we're under budget" without caveat.
  1 = Misuses VaR or ignores it.
  0 = Empty.
""",
    "Implementation_AI": """
Grading a memo on deploying a momentum strategy with full implementation cost analysis.

GROUND TRUTH:
- Gross Sharpe = 0.67 (unlevered); net Sharpe after 2x leverage, costs, financing ≈ 0.35.
- Largest cost item is financing (6%/yr × 1x leverage = 6pp drag on net P&L).
- Strategy is marginal at this leverage; better to deploy unleveraged.

Grade 0-5:
  5 = Cites gross vs net Sharpe, identifies financing as the dominant cost,
      gives defensible deploy / don't-deploy recommendation.
  4 = Two of three.
  3 = One.
  2 = Recommends without naming a specific cost.
  1 = Uses gross numbers only.
  0 = Empty.
""",
    "ML_I_AI": """
Grading a memo on tuned Elastic Net for return prediction.

GROUND TRUTH:
- ENet typically beats OLS when features are correlated.
- The model should select a small number of features (true sparsity in sim).
- Real return data has time-series structure; standard CV is invalid.

Grade 0-5:
  5 = Notes ENet OOS beats OLS, comments on feature selection, raises time-series CV concern for real data.
  4 = Two of three.
  3 = One.
  2 = Hand-wavy.
  1 = Misinterprets in-sample R² as evidence.
  0 = Empty.
""",
    "ML_II_AI": """
Grading a memo on tree-based methods vs linear baseline.

GROUND TRUTH:
- Trees beat OLS on non-linear/interaction-heavy data.
- GBT often best when tuned; risk is overfitting in production.
- For real return prediction, gains over Elastic Net are modest.

Grade 0-5:
  5 = Names the winner, explains WHY given data structure, raises production-overfitting risk.
  4 = Two of three.
  3 = One.
  2 = Hand-wavy.
  1 = Picks neural nets without justification.
  0 = Empty.
""",
    "LLMs_AI": """
Grading a memo on LLM-based tone scoring for a hypothetical backtest.

GROUND TRUTH:
- The 3 snippets have clearly different tones (positive, negative, neutral).
- The big risk in using a 2024-trained LLM on 2020 transcripts is lookahead bias.
- Mitigations: use frozen-date models, prompt for time-of-decision awareness.

Grade 0-5:
  5 = Computes avg tone, names lookahead as the critical risk, proposes a mitigation.
  4 = Two of three.
  3 = One.
  2 = Hand-wavy.
  1 = Ignores lookahead bias.
  0 = Empty.
""",
    "WhatIsAlpha_AI": """
You are grading a memo from a student who designed a 5-year industry allocation
strategy (1970-1974) with no access to stock-market data after Dec 1969.
They report cumulative return + alpha vs three benchmarks (CAPM, equal-weight
industries, FF3).

GROUND TRUTH (the patterns to look for in their reasoning):
- The 1970-74 market lost ~21% cumulative; equal-weight 10-industries lost ~18%.
- Most strategies that "beat the market" did so by overweighting Energy
  (oil shock) or Utilities/Health (defensive). That's SECTOR BETA, not alpha.
- Alpha typically shrinks dramatically going CAPM → Equal-Weight → FF3.
- The honest interpretation: most apparent alpha was factor exposure.

KEY POINTS a good memo addresses:
- Cumulative return vs all three benchmarks
- Where alpha "lived" — and how it shrank across benchmarks
- Acknowledges that the strategy's outperformance came largely from sector
  weights, not from skill at picking within sectors
- Acknowledges hindsight bias / drawdown realism
- Has a "would I actually have held this" reflection

Grade 0-5:
  5 = Clear about cumulative numbers, identifies that alpha shrinks across
      benchmarks, names the sector(s) that drove returns, AND honest about
      what would have been hard to actually hold (drawdown / hindsight).
  4 = Three of the four above.
  3 = Two of the four.
  2 = Claims "I had alpha" without distinguishing factor exposure.
  1 = Treats raw cumulative return as evidence of skill.
  0 = Empty / off-topic.

For picked_fund return "A"; for cited_appraisal_or_alpha return False.
""",
    "Timing_AI": """
You are grading a memo comparing four timing strategies on US market exposure.
The student picked their own FRED predictor for Hands-On 1, so the specific
result on "their" predictor will vary.

GROUND TRUTH (the values that stay the same across students):
- Buy-and-hold (post-1991): Sharpe ≈ 0.58
- D/P mean-timing (post-1991 OOS): Sharpe ≈ 0.75 — beats buy-and-hold
- RV vol-timing (full sample): Sharpe ≈ 0.50
- VIX² vol-timing (post-1990): Sharpe ≈ 0.66 — beats RV on the same sample
- Student's chosen predictor: any plausible Sharpe (-0.5 to 1.5).
  - If their predictor beats D/P: the memo should explain why their signal might
    capture something extra (different mechanism, more recent sample, less crowded).
  - If their predictor underperforms: the memo should acknowledge that NOT all
    plausible-sounding predictors work — that's part of the lesson.

KEY POINTS a good memo addresses:
- Vol timing is more robust than mean timing because forecasting σ² is easier
  than forecasting μ.
- VIX > RV because VIX is forward-looking (option-implied) and spikes BEFORE
  stress; RV catches up with a lag. But VIX only available since 1990.
- Different OOS windows complicate direct comparison.
- A defensible recommendation: deploy vol-timing as the lower-risk Sharpe boost;
  treat mean-timing as a supplementary signal with caveats.

Grade 0-5:
  5 = Picks a recommendation (any), cites at least 3 Sharpe numbers, addresses
      mean-vs-vol theoretical reason (μ hard, σ² easier), AND discusses the
      tradeoff between RV (backward-looking) and VIX (forward-looking).
  4 = Three of the above four.
  3 = Two of the four.
  2 = One. Or recommends without citing numbers.
  1 = Mistakes in-sample Sharpe for OOS expected performance.
  0 = Empty.

For picked_fund return "A"; for cited_appraisal_or_alpha return False.
""",
    "CapitalAllocationI_AI": """
You are grading a memo defending a sizing decision for a portfolio that
combines (a) market exposure (SPY) and (b) a hedged alpha strategy.

GROUND TRUTH (computable from the given inputs):
- w_market ≈ 0.82 (slightly underleveraged exposure)
- w_alpha  ≈ 2.08 (heavily leveraged — alpha-book vol is low)
- total Sharpe ≈ 0.66 (vs 0.44 market-only)
- The biggest risk is that the alpha strategy is NOT actually uncorrelated
  with the market in stress periods (correlations spike).

Grade 0-5:
  5 = Quotes the sizing, the Sharpe gain, AND identifies correlation-stability
      as the biggest risk.
  4 = Quotes sizing + Sharpe; weaker on risk.
  3 = One specific number quoted.
  2 = Hand-wavy.
  1 = Says "just take the optimization output" without nuance.
  0 = Empty.

For picked_fund return "A"; for cited_appraisal_or_alpha return False.
""",
    "Portfolios_AI": """
You are grading a memo recommending a weighting scheme (equal-weight,
min-variance, or max-Sharpe) on a 3-stock portfolio (SPY/WMT/JPM).

GROUND TRUTH:
- Max-Sharpe has the highest in-sample Sharpe by construction, but it's the
  most fragile because it depends on $\\mu$ — which is hard to estimate.
- Min-variance and equal-weight are more robust.
- The "right" answer is partly a matter of taste, BUT a good memo should
  acknowledge that the max-Sharpe Sharpe is in-sample and may not persist.

Grade 0-5:
  5 = Picks any scheme, cites the relevant in-sample number, AND notes the
      estimation-error risk (max-Sharpe is sensitive to $\\mu$; min-variance
      ignores expected return; equal-weight ignores both).
  4 = Picks and cites; weaker caveat.
  3 = Picks and cites a number; no caveat.
  2 = Picks but for hand-wavy reason.
  1 = Picks max-Sharpe purely because "highest Sharpe" with no awareness of fragility.
  0 = Empty / off-topic.

For picked_fund return "A". For cited_appraisal_or_alpha return False.

Output via the `grade_memo` tool.
""",
    "IntrotoReturns_AI": """
You are grading a 5-sentence memo to a client who wants to put their entire
retirement in SPY based on a "stocks return 10% per year" rule of thumb.

GROUND TRUTH (2010-2024):
- SPY's realized annual mean is ~13% — close to 10%, so the rule of thumb
  was directionally right in this sample.
- BUT volatility is ~17% per year and the worst year (2022) was about -18%.
- A retiree depending entirely on SPY could lose ~20% in a single year.
- The 2010-2024 sample is unusually favorable — mostly bull market, low
  inflation, post-GFC recovery. Future could differ.

A 5-point memo would:
  - State whether 10%/year is reasonable to plan for (yes, roughly)
  - Quantify the downside (1-in-N years you could lose ~15-20%)
  - Mention the sample-period caveat or sequence-of-returns risk

Grade 0-5:
  5 = States the expected return realistically, quantifies downside, notes a
      good caveat (sample bias, sequence risk, retirement-specific concern).
  4 = Two of the three above.
  3 = One only — either the expected return or the downside.
  2 = Hand-wavy.
  1 = Just says "yes invest in SPY" with no analysis.
  0 = Empty / off-topic.

For picked_fund return "A" (not relevant). For cited_appraisal_or_alpha
return False.

Output via the `grade_memo` tool.
""",
    "WRDS_Tour_AI": """
You are grading a 2-sentence note from a student doing their first WRDS data
exploration. They picked a stock and wrote what they noticed about it.

This is a PARTICIPATION CHECK, not a real memo. Grade leniently.

Grade on a 0-5 scale:
  5 = Two real sentences. Mentions their stock by name. Notes one specific observation.
  4 = Two real sentences, some specific content.
  3 = Some content, maybe vague but not empty.
  2 = One short sentence, very vague.
  1 = "I picked AAPL" or equivalent throwaway.
  0 = Empty / placeholder text not replaced.

For the picked_fund field, just return "A" (we don't use it here).
For cited_appraisal_or_alpha, return false (not relevant).
""",
    "FactorModels_AI": """
You are grading a junior analyst's memo to the CIO. The memo recommends
between Fund A and Fund B for a hedge fund allocation.

GROUND TRUTH:
- Fund A: small but positive alpha (~3-5% annualized), low idiosyncratic
  vol (~8%), appraisal ratio ~0.4. Genuinely skilled, low-beta manager.
- Fund B: NEGATIVE alpha (~-10%), high beta (~1.4), high idio vol (~15%).
  Has only made money by riding the market with leverage. Bad manager.

The CORRECT recommendation is Fund A (or "neither"). Fund B should be
rejected. The KEY METRIC is the appraisal ratio (or equivalently, alpha
after risk-adjustment), NOT raw returns.

Grade the memo on a 0-5 scale:
  5 = Recommends Fund A, cites appraisal ratio / alpha, notes that raw
      returns are misleading, mentions appropriate caveat.
  4 = Recommends Fund A, identifies alpha as key, weaker on caveats.
  3 = Recommends Fund A but for wrong/weak reasons (e.g. "lower vol").
  2 = Picks Fund B because of higher beta or "more upside".
  1 = Picks Fund B and cites raw returns or Sharpe.
  0 = Empty, off-topic, or incoherent.

Output via the `grade_memo` tool.
""",
    "FactorModels_II_AI": """
You are grading a junior analyst's memo to the CIO. The memo recommends
hiring between Manager X and Manager Y.

GROUND TRUTH:
- Both managers have ALMOST IDENTICAL full-sample alpha (~4.4% vs ~4.2%
  per year). Neither full-sample alpha is statistically significant
  (X t-stat = 1.4, Y t-stat = 0.6).
- The persistence test reveals the truth:
  * Manager X: alpha in both halves is similar (~4.5% vs ~4.2%) — skill persists.
  * Manager Y: half-1 alpha = +10%, half-2 alpha = -1% — pure luck mean-reverted.
- Manager X also has much more stable rolling beta (less hidden timing risk).

The CORRECT recommendation is Manager X (or "neither, both are too noisy" —
acceptable given low t-stats). The KEY METRIC is the persistence test
(half-1 vs half-2 alpha), NOT the full-sample alpha or t-stat alone.

Grade the memo on a 0-5 scale:
  5 = Picks X (or "neither"), cites persistence as the deciding factor,
      acknowledges full-sample alphas are similar but misleading, notes
      that even X's alpha has wide CI.
  4 = Picks X, cites persistence, weaker on the noise caveat.
  3 = Picks X but for weaker reasons (e.g. "lower beta std" alone).
  2 = Picks Y because of higher half-1 alpha or larger-looking history.
  1 = Picks based only on full-sample alpha/t-stat (misses the entire lesson).
  0 = Empty, off-topic, or incoherent.

For the picked_fund field, return "A" for Manager X, "B" for Manager Y,
"neither" for declining both.

Output via the `grade_memo` tool.
""",
}

GRADE_MEMO_TOOL = {
    "name": "grade_memo",
    "description": "Submit the memo grade",
    "input_schema": {
        "type": "object",
        "properties": {
            "score": {"type": "integer", "minimum": 0, "maximum": 5},
            "picked_fund": {"type": "string", "enum": ["A", "B", "neither", "unclear"]},
            "cited_appraisal_or_alpha": {"type": "boolean"},
            "feedback": {"type": "string", "description": "2-3 sentences for the student"},
        },
        "required": ["score", "picked_fund", "cited_appraisal_or_alpha", "feedback"],
    },
}


# ─── Helpers ──────────────────────────────────────────────────────────

def anonymize(filename: str) -> str:
    """Hash a filename to a stable anonymous ID."""
    return "stu_" + hashlib.sha256(filename.encode()).hexdigest()[:8]


def execute_notebook(path: Path, timeout: int = 120):
    """Run notebook in a sandbox; return executed nb + any error."""
    nb = nbformat.read(path, as_version=4)
    ep = ExecutePreprocessor(timeout=timeout, kernel_name="python3")
    try:
        ep.preprocess(nb, {"metadata": {"path": str(path.parent)}})
        return nb, None
    except Exception as e:
        return nb, f"{type(e).__name__}: {e}\n{traceback.format_exc()[-500:]}"


def extract_submission_dict(nb) -> dict | None:
    """Find the SUBMISSION dict in any cell output."""
    for cell in nb.cells:
        if cell.cell_type != "code":
            continue
        for out in cell.get("outputs", []):
            text = ""
            if out.get("output_type") == "stream":
                text = out.get("text", "")
            elif "data" in out and "text/plain" in out["data"]:
                text = out["data"]["text/plain"]
            if "SUBMISSION" in text or text.strip().startswith("{"):
                try:
                    # last { ... } block in the text
                    start = text.rfind("{")
                    end = text.rfind("}")
                    if start >= 0 and end > start:
                        return eval(text[start:end + 1])
                except Exception:
                    continue
    return None


def extract_memo(nb) -> str:
    """Find the student's memo paragraph (last markdown cell before takeaways)."""
    for cell in nb.cells:
        if cell.cell_type == "markdown" and "your memo here" in cell.source.lower():
            # Memo is the content of this cell minus the prompt
            lines = cell.source.split("\n")
            memo_lines = [l for l in lines if l.strip() and not l.startswith(">")
                          and "your memo here" not in l.lower()
                          and "double-click" not in l.lower()]
            return "\n".join(memo_lines).strip()
    return ""


def grade_numeric(submission: dict, key) -> dict:
    """Return per-question correctness. `key` is either a dict {var: (truth, tol)}
    or the string "_dynamic_" which dispatches to an assignment-specific grader."""
    if key == "_dynamic_":
        # Caller should use grade_wrds_tour directly; bail out here.
        raise ValueError("Dynamic answer key — use the assignment-specific grader.")
    results = {}
    for q, (truth, tol) in key.items():
        got = submission.get(q)
        if got is None:
            results[q] = {"correct": False, "got": None, "expected": truth,
                          "reason": "missing"}
            continue
        try:
            got = float(got)
            ok = abs(got - truth) <= abs(truth) * tol if truth != 0 else abs(got) <= tol
            results[q] = {"correct": ok, "got": got, "expected": truth,
                          "reason": "ok" if ok else f"off by {(got - truth) / truth * 100:.0f}%"}
        except Exception as e:
            results[q] = {"correct": False, "got": got, "expected": truth, "reason": str(e)}
    return results


def grade_wrds_tour(submission: dict, **kwargs) -> dict:
    """Range-based grading for the WRDS tour challenge.

    Students pull LIVE data from WRDS, so we can't verify against a fixed
    snapshot. Instead we check that values are in plausible ranges and that
    the student's choices are self-consistent (e.g., the ticker is a real
    ticker, the permno is a plausible permno, the cumulative return is in a
    sane range for ANY stock over a 5-year window).

    This is a completion check, not a correctness check. The goal of this
    lecture is infrastructure verification.
    """
    results = {}
    ticker = str(submission.get("my_ticker", "")).strip().upper()

    # Basic ticker sanity: not empty, not placeholder, not AAPL
    if ticker in ("", "____", "AAPL"):
        results["my_ticker"] = {
            "correct": False, "got": ticker, "expected": "non-empty non-AAPL ticker",
            "reason": "missing, placeholder, or AAPL (instructions said any but AAPL)"}
    elif not ticker.isalpha() or len(ticker) > 6:
        results["my_ticker"] = {
            "correct": False, "got": ticker, "expected": "valid stock ticker",
            "reason": "doesn't look like a stock ticker"}
    else:
        results["my_ticker"] = {
            "correct": True, "got": ticker, "expected": "non-empty non-AAPL ticker",
            "reason": "ok"}

    # Permno: integer between 10000 and 99999 (CRSP range)
    try:
        permno = int(submission.get("my_permno", -1))
        if 10000 <= permno <= 99999:
            results["my_permno"] = {"correct": True, "got": permno,
                                    "expected": "5-digit CRSP permno", "reason": "ok"}
        else:
            results["my_permno"] = {"correct": False, "got": permno,
                                    "expected": "5-digit CRSP permno",
                                    "reason": "out of typical permno range"}
    except Exception as e:
        results["my_permno"] = {"correct": False, "got": submission.get("my_permno"),
                                "expected": "int", "reason": str(e)}

    # months_of_data: int between 1 and 80 (5 years ≈ 60 months, allow flex)
    try:
        m = int(submission.get("months_of_data", -1))
        if 1 <= m <= 80:
            results["months_of_data"] = {"correct": True, "got": m,
                                          "expected": "1-80", "reason": "ok"}
        else:
            results["months_of_data"] = {"correct": False, "got": m,
                                          "expected": "1-80 months",
                                          "reason": "implausible row count"}
    except Exception as e:
        results["months_of_data"] = {"correct": False, "got": submission.get("months_of_data"),
                                      "expected": "int", "reason": str(e)}

    # latest_mktcap_M: positive, between $1M and $10T
    try:
        mc = float(submission.get("latest_mktcap_M", -1))
        if 1 <= mc <= 10_000_000:
            results["latest_mktcap_M"] = {"correct": True, "got": mc,
                                           "expected": "1 to 10M ($M)",
                                           "reason": "ok"}
        else:
            results["latest_mktcap_M"] = {"correct": False, "got": mc,
                                           "expected": "1 to 10M ($M)",
                                           "reason": "implausible market cap"}
    except Exception as e:
        results["latest_mktcap_M"] = {"correct": False,
                                       "got": submission.get("latest_mktcap_M"),
                                       "expected": "float", "reason": str(e)}

    # cum_return: between -0.99 and +50 (5 years can be very wild but not infinite)
    try:
        cr = float(submission.get("cum_return", -999))
        if -0.99 <= cr <= 50:
            results["cum_return"] = {"correct": True, "got": cr,
                                      "expected": "-0.99 to +50", "reason": "ok"}
        else:
            results["cum_return"] = {"correct": False, "got": cr,
                                      "expected": "-0.99 to +50",
                                      "reason": "implausible cumulative return"}
    except Exception as e:
        results["cum_return"] = {"correct": False, "got": submission.get("cum_return"),
                                  "expected": "float", "reason": str(e)}

    # avg_monthly_return: between -0.10 and +0.10 typically
    try:
        amr = float(submission.get("avg_monthly_return", -999))
        if -0.20 <= amr <= 0.20:
            results["avg_monthly_return"] = {"correct": True, "got": amr,
                                              "expected": "±20%/month",
                                              "reason": "ok"}
        else:
            results["avg_monthly_return"] = {"correct": False, "got": amr,
                                              "expected": "±20%/month",
                                              "reason": "implausible average monthly return"}
    except Exception as e:
        results["avg_monthly_return"] = {"correct": False,
                                          "got": submission.get("avg_monthly_return"),
                                          "expected": "float", "reason": str(e)}

    return results


def grade_memo(client: Anthropic, memo: str, assignment: str = "FactorModels_AI") -> dict:
    """Call Claude with tool use to score the memo, using the per-assignment rubric."""
    if not memo.strip():
        return {"score": 0, "picked_fund": "unclear",
                "cited_appraisal_or_alpha": False, "feedback": "Memo not submitted."}

    rubric = MEMO_RUBRICS.get(assignment)
    if rubric is None:
        raise KeyError(f"No memo rubric for assignment {assignment!r}")

    resp = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=1024,
        system=rubric,
        tools=[GRADE_MEMO_TOOL],
        tool_choice={"type": "tool", "name": "grade_memo"},
        messages=[{"role": "user", "content": f"Memo to grade:\n\n---\n{memo}\n---"}],
    )
    for block in resp.content:
        if block.type == "tool_use":
            return block.input
    return {"score": 0, "picked_fund": "unclear",
            "cited_appraisal_or_alpha": False, "feedback": "Claude did not return a structured grade."}


def write_feedback(path: Path, anon_id: str, numeric: dict, memo_grade: dict, exec_error: str | None):
    """Write a markdown feedback file."""
    lines = [f"# Feedback for {anon_id}", "", f"_Generated {datetime.now().isoformat(timespec='seconds')}_", ""]

    if exec_error:
        lines += ["## ⚠️ Notebook did not execute cleanly", "```", exec_error, "```", ""]

    lines.append("## Numeric answers")
    lines.append("")
    lines.append("| Question | Your answer | Expected | Status |")
    lines.append("|----------|-------------|----------|--------|")
    for q, r in numeric.items():
        got = f"{r['got']:.4f}" if isinstance(r["got"], (int, float)) else str(r["got"])
        status = "✅" if r["correct"] else f"❌ ({r['reason']})"
        lines.append(f"| {q} | {got} | {r['expected']:.4f} | {status} |")

    lines += ["", "## Memo (Q5)", "",
              f"**Score:** {memo_grade['score']}/5",
              f"**Picked:** Fund {memo_grade['picked_fund']}",
              f"**Cited appraisal/alpha:** {memo_grade['cited_appraisal_or_alpha']}",
              "", f"> {memo_grade['feedback']}", ""]

    path.write_text("\n".join(lines))


# ─── Main ─────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--inbox", required=True, help="Folder of .ipynb submissions")
    p.add_argument("--feedback", required=True, help="Where to write feedback .md")
    p.add_argument("--assignment", required=True, help="Key in ANSWER_KEY")
    p.add_argument("--sheet", default=None, help="(Optional) Google Sheet name for gradebook")
    p.add_argument("--dry-run", action="store_true", help="Skip Sheets write")
    args = p.parse_args()

    if args.assignment not in ANSWER_KEY:
        print(f"No answer key for {args.assignment}", file=sys.stderr)
        sys.exit(1)
    key = ANSWER_KEY[args.assignment]

    inbox = Path(args.inbox)
    feedback = Path(args.feedback)
    feedback.mkdir(parents=True, exist_ok=True)

    client = Anthropic()  # reads ANTHROPIC_API_KEY from env

    rows = []
    for nb_path in sorted(inbox.glob("*.ipynb")):
        anon = anonymize(nb_path.name)
        print(f"→ {nb_path.name}  (as {anon})")

        nb, exec_error = execute_notebook(nb_path)
        submission = extract_submission_dict(nb) or {}
        memo = extract_memo(nb)

        numeric = grade_numeric(submission, key)
        memo_grade = grade_memo(client, memo)

        n_correct = sum(1 for r in numeric.values() if r["correct"])
        n_total = len(numeric)
        pct = n_correct / n_total * 100
        memo_pct = memo_grade["score"] / 5 * 100
        overall = 0.7 * pct + 0.3 * memo_pct  # weight numeric:memo = 70:30

        write_feedback(feedback / f"{anon}.md", anon, numeric, memo_grade, exec_error)

        rows.append({
            "filename": nb_path.name,
            "anon_id": anon,
            "executed": exec_error is None,
            "numeric_score": pct,
            "memo_score": memo_grade["score"],
            "overall": overall,
            "picked_fund": memo_grade["picked_fund"],
            "flag": exec_error is not None or overall < 50 or memo_grade["score"] == 0,
        })

        print(f"  numeric={pct:.0f}%  memo={memo_grade['score']}/5  overall={overall:.0f}")

    # Write a summary CSV regardless of Sheets
    import csv
    summary = feedback / "summary.csv"
    with summary.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader(); w.writerows(rows)
    print(f"\n✅ Wrote summary: {summary}")

    if args.sheet and not args.dry_run:
        try:
            import gspread
            gc = gspread.service_account(filename="service_account.json")
            sh = gc.open(args.sheet).worksheet(args.assignment)
            sh.clear()
            sh.update([list(rows[0].keys())] + [list(r.values()) for r in rows])
            print(f"✅ Updated Sheet: {args.sheet} / {args.assignment}")
        except Exception as e:
            print(f"⚠️ Sheets write failed: {e}", file=sys.stderr)

    flagged = [r for r in rows if r["flag"]]
    if flagged:
        print(f"\n🚩 {len(flagged)} submissions flagged for manual review:")
        for r in flagged:
            print(f"   {r['filename']}  (numeric={r['numeric_score']:.0f}%, memo={r['memo_score']})")


if __name__ == "__main__":
    main()
