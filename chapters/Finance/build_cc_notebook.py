#!/usr/bin/env python3
"""
Build MachineLearning_cc.ipynb from MachineLearning_c.ipynb.

Key change: the controlled experiment (synthetic returns with known signal)
is constructed early and used as the target throughout every ML method.
"""

import json
import uuid

# ── Load source notebook ─────────────────────────────────────
with open('MachineLearning_c.ipynb') as f:
    nb_c = json.load(f)

old = nb_c['cells']


def uid():
    return uuid.uuid4().hex[:8]


def md_cell(source):
    """Create a markdown cell."""
    if isinstance(source, str):
        source = source.split('\n')
        source = [line + '\n' for line in source[:-1]] + [source[-1]]
    return {
        'cell_type': 'markdown',
        'id': uid(),
        'metadata': {},
        'source': source,
    }


def code_cell(source):
    """Create a code cell."""
    if isinstance(source, str):
        source = source.split('\n')
        source = [line + '\n' for line in source[:-1]] + [source[-1]]
    return {
        'cell_type': 'code',
        'execution_count': None,
        'id': uid(),
        'metadata': {},
        'outputs': [],
        'source': source,
    }


def copy_cell(idx):
    """Copy a cell from the old notebook, resetting outputs."""
    c = dict(old[idx])
    c['id'] = uid()
    c['outputs'] = []
    if 'execution_count' in c:
        c['execution_count'] = None
    return c


cells = []

# ═══════════════════════════════════════════════════════════════
# Section 1: Title + Objectives + Libraries (cells 0-2)
# ═══════════════════════════════════════════════════════════════
cells.append(copy_cell(0))   # markdown title + objectives
cells.append(copy_cell(1))   # markdown "Libraries"

# Cell 2: imports — add Ridge
old_imports = ''.join(old[2]['source'])
new_imports = old_imports.replace(
    'from sklearn.linear_model import Lasso, ElasticNet',
    'from sklearn.linear_model import Lasso, ElasticNet, Ridge'
)
cells.append(code_cell(new_imports))

# ═══════════════════════════════════════════════════════════════
# Section 2: The Problem (cells 3-4)
# ═══════════════════════════════════════════════════════════════
cells.append(copy_cell(3))   # markdown problem statement
cells.append(copy_cell(4))   # markdown roadmap

# ═══════════════════════════════════════════════════════════════
# Section 3: Data + Controlled Experiment Setup
# ═══════════════════════════════════════════════════════════════
cells.append(copy_cell(5))   # markdown "## Data"
cells.append(copy_cell(6))   # code — data loading

# NEW: Laboratory markdown
cells.append(md_cell(r"""## A Laboratory for Machine Learning

With real returns, we never know the true expected return function — so we can't tell whether a model fails because of estimation error or because the signal doesn't exist.

To build intuition, we construct **synthetic returns** with a known signal embedded in real noise:

$$\tilde{R}_{i,t} = \alpha \cdot \lambda' X_{i,t} + \varepsilon_{i,t}$$

- $X_{i,t}$: actual standardized characteristics
- $\varepsilon_{i,t}$: demeaned actual returns (preserves real factor structure and cross-sectional dependence)
- $\lambda$: known weight vector — we choose which characteristics predict returns
- $\alpha$: signal strength — controls the signal-to-noise ratio

This lets us evaluate each model against the truth: Do the estimated coefficients recover $\lambda$? Does the model's trading strategy approach the oracle Sharpe ratio?"""))

# Parameters + synthetic return construction
cells.append(code_cell(r"""# ── Parameters ────────────────────────────────────────────────
chars = list(X_train.columns)

# Lambda: weight vector on characteristics (sums to 1)
lam = np.zeros(len(chars))
lam[chars.index('value')] = 1.0       # try 'mom', 'size', or spread across multiple

alpha = 0.01                           # signal strength
T_train = 20                           # years of training data

# ── Date-based train/test split ─────────────────────────────
all_dates = sorted(set(Y_train.index.get_level_values(0).unique()) |
                   set(Y_tuning.index.get_level_values(0).unique()))
n_train_months = T_train * 12
train_dates = all_dates[:n_train_months]
test_dates = all_dates[n_train_months:]

# Combine all data
X_all = pd.concat([X_train, X_tuning])
Y_all = pd.concat([Y_train, Y_tuning])

mask_tr = Y_all.index.get_level_values(0).isin(train_dates)
mask_te = Y_all.index.get_level_values(0).isin(test_dates)
X_ctrl_tr = X_all[mask_tr];  Y_ctrl_tr = Y_all[mask_tr]
X_ctrl_te = X_all[mask_te];  Y_ctrl_te = Y_all[mask_te]

# ── Standardize characteristics ─────────────────────────────
mu_x = X_ctrl_tr.mean()
sd_x = X_ctrl_tr.std(); sd_x[sd_x == 0] = 1
X_tr_std = ((X_ctrl_tr - mu_x) / sd_x).values
X_te_std = ((X_ctrl_te - mu_x) / sd_x).values

# ── Construct synthetic returns ──────────────────────────────
noise_tr = (Y_ctrl_tr - Y_ctrl_tr.mean()).values
noise_te = (Y_ctrl_te - Y_ctrl_te.mean()).values

er_tr = alpha * (X_tr_std @ lam)
er_te = alpha * (X_te_std @ lam)
Y_synth_tr = er_tr + noise_tr
Y_synth_te = er_te + noise_te

# ── What does alpha imply? ───────────────────────────────────
cs_std = np.std(er_tr)
noise_std = np.std(noise_tr)

# Approximate oracle Sharpe ratio
z90 = 1.2816
phi_z90 = np.exp(-0.5 * z90**2) / np.sqrt(2 * np.pi)
expected_ls_monthly = 2 * cs_std * phi_z90 / 0.1

# L-S noise vol from factor structure
df_noise_vol = pd.DataFrame({'er': er_te, 'noise': noise_te}, index=Y_ctrl_te.index)
def _ls_noise(g):
    n = len(g); d = n // 10
    s = g.sort_values('er')
    return s['noise'].iloc[-d:].mean() - s['noise'].iloc[:d].mean()
ls_noise_vol = df_noise_vol.groupby('date').apply(_ls_noise).dropna().std()
oracle_sr = (expected_ls_monthly / ls_noise_vol) * np.sqrt(12)

print(f"Training: {len(train_dates)} months ({T_train} years), {len(Y_ctrl_tr):,} stock-months")
print(f"Test:     {len(test_dates)} months, {len(Y_ctrl_te):,} stock-months")
print(f"\nCross-sectional std of E[R]:  {cs_std*100:.2f}% monthly  /  {cs_std*np.sqrt(12)*100:.1f}% annual")
print(f"Noise std:                    {noise_std*100:.2f}% monthly")
print(f"SNR:                          {cs_std/noise_std:.3f}")
print(f"Lambda: all weight on '{chars[np.argmax(lam)]}'")
print(f"\n── Oracle long-short approximation ──")
print(f"E[L-S monthly]:     {expected_ls_monthly*100:.3f}%")
print(f"Vol(L-S monthly):   {ls_noise_vol*100:.3f}%  (from noise factor structure)")
print(f"Oracle SR (annual):  {oracle_sr:.2f}")"""))

# Helper functions + oracle performance
_helpers_src = (
    '# ── Helper functions (used throughout the notebook) ──────────\n'
    '\n'
    "def long_short_decile(group, signal_col='er'):\n"
    '    """Each month: long top decile, short bottom decile."""\n'
    '    n = len(group)\n'
    '    if n < 20:\n'
    '        return np.nan\n'
    '    decile = n // 10\n'
    '    sorted_g = group.sort_values(signal_col)\n'
    "    return sorted_g['ret'].iloc[-decile:].mean() - sorted_g['ret'].iloc[:decile].mean()\n"
    '\n'
    '# Running scoreboard — each model adds a row\n'
    'all_results = []\n'
    '\n'
    'def evaluate_model(er_hat, name, show_plot=False):\n'
    '    """Compute L-S strategy from predicted E[R], add to running scoreboard."""\n'
    "    df = pd.DataFrame({'er_hat': er_hat, 'ret': Y_synth_te}, index=Y_ctrl_te.index)\n"
    "    ls = df.groupby('date').apply(long_short_decile, signal_col='er_hat').dropna()\n"
    '    ls.index = pd.to_datetime(ls.index)\n'
    '\n'
    '    ann_ret = ls.mean() * 12\n'
    '    ann_vol = ls.std() * np.sqrt(12)\n'
    '    sr = ann_ret / ann_vol if ann_vol > 0 else 0\n'
    '\n'
    "    all_results.append({'Model': name, 'Ann. Return': ann_ret,\n"
    "                        'Ann. Vol': ann_vol, 'Sharpe': sr})\n"
    '\n'
    '    print(f"{name}:  SR = {sr:.2f}  |  Ann. Return = {ann_ret*100:.1f}%  |  Ann. Vol = {ann_vol*100:.1f}%")\n'
    '\n'
    '    if show_plot:\n'
    '        fig, ax = plt.subplots(figsize=(10, 4))\n'
    '        ax.plot((1 + ls).cumprod(), linewidth=1.5)\n'
    "        ax.set_ylabel('Cumulative return ($1)')\n"
    "        ax.set_title(f'{name} — long-short decile strategy')\n"
    "        ax.set_yscale('log')\n"
    '        plt.tight_layout()\n'
    '        plt.show()\n'
    '\n'
    '    return ls\n'
    '\n'
    "def plot_coefficients(coef_est, title='Estimated vs. true coefficients'):\n"
    '    """Bar chart comparing estimated coefficients to true lambda."""\n'
    '    fig, ax = plt.subplots(figsize=(10, 4))\n'
    '    x = np.arange(len(chars))\n'
    '    width = 0.35\n'
    "    ax.bar(x - width/2, lam, width, label='True \\u03bb', alpha=0.7)\n"
    '    ax.bar(x + width/2, coef_est / (alpha if alpha != 0 else 1), width,\n'
    "           label='Estimated (scaled)', alpha=0.7)\n"
    '    ax.set_xticks(x)\n'
    '    ax.set_xticklabels(chars, rotation=90, fontsize=7)\n'
    '    ax.legend()\n'
    '    ax.set_title(title)\n'
    "    ax.axhline(0, color='gray', lw=0.5)\n"
    '    plt.tight_layout()\n'
    '    plt.show()\n'
    '\n'
    'def show_scoreboard():\n'
    '    """Display the running comparison table."""\n'
    '    df = pd.DataFrame(all_results)\n'
    '    return (df.style\n'
    "        .format({'Ann. Return': '{:.1%}', 'Ann. Vol': '{:.1%}', 'Sharpe': '{:.2f}'})\n"
    "        .set_properties(subset=['Model'], **{'text-align': 'left', 'font-weight': 'bold', 'width': '250px'})\n"
    "        .set_properties(subset=['Ann. Return', 'Ann. Vol', 'Sharpe'], **{'text-align': 'right'})\n"
    "        .hide(axis='index')\n"
    '        .set_table_styles([\n'
    "            {'selector': 'th', 'props': [('text-align', 'left'), ('padding', '6px 12px')]},\n"
    "            {'selector': 'td', 'props': [('padding', '4px 12px')]},\n"
    '        ])\n'
    '    )\n'
    '\n'
    '# ── Oracle performance ───────────────────────────────────────\n'
    "ls_oracle = evaluate_model(er_te, 'Oracle (true E[R])', show_plot=True)\n"
    'print(f"\\nApproximate oracle SR: {oracle_sr:.2f}")'
)
cells.append(code_cell(_helpers_src))

# ═══════════════════════════════════════════════════════════════
# Section 4: Linear Models with Regularization
# ═══════════════════════════════════════════════════════════════
cells.append(copy_cell(7))   # markdown: Linear Models with Regularization
cells.append(copy_cell(8))   # markdown: Lasso Regression

# Lasso path — modified for synthetic data
cells.append(code_cell(r"""# Lasso regularization path
# Training on synthetic returns — the signal is alpha * lambda' X
alphas_lasso = np.logspace(-5, -2, 50)
coef_paths = []
mses = []

for a in alphas_lasso:
    model = Lasso(alpha=a, max_iter=10000)
    model.fit(X_tr_std, Y_synth_tr)
    coef_paths.append(model.coef_)
    mses.append(mean_squared_error(Y_synth_te, model.predict(X_te_std)))

coef_paths = np.array(coef_paths)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
ax = axes[0]
for i in range(coef_paths.shape[1]):
    ax.plot(alphas_lasso, coef_paths[:, i])
ax.set_xscale('log')
ax.set_xlabel('Alpha (regularization strength)')
ax.set_ylabel('Coefficient value')
ax.set_title('Lasso coefficient paths')
ax.axhline(0, color='gray', linewidth=0.5)

ax = axes[1]
ax.plot(alphas_lasso, mses, 'o-', markersize=3)
ax.set_xscale('log')
ax.set_xlabel('Alpha (regularization strength)')
ax.set_ylabel('MSE (test sample)')
ax.set_title('Out-of-sample MSE vs. regularization')
plt.tight_layout()
plt.show()

best_alpha = alphas_lasso[np.argmin(mses)]
print(f"Best alpha: {best_alpha:.6f}")
print(f"Best test MSE: {min(mses):.6f}")"""))

# Lasso best — modified
cells.append(code_cell(r"""# Fit at best alpha and compare to truth
lasso_best = Lasso(alpha=best_alpha, max_iter=10000)
lasso_best.fit(X_tr_std, Y_synth_tr)

surviving = pd.Series(lasso_best.coef_, index=chars)
surviving = surviving[surviving != 0].sort_values()
print(f"Surviving features: {len(surviving)} out of {len(chars)}")
print(f"Test R²: {r2_score(Y_synth_te, lasso_best.predict(X_te_std)):.4f}")
print(f"\nNon-zero coefficients:")
print(surviving.to_string())

# How close are estimated coefficients to truth?
plot_coefficients(lasso_best.coef_, 'Lasso — estimated vs. true coefficients')

# Long-short performance
er_hat_lasso = lasso_best.predict(X_te_std)
ls_lasso = evaluate_model(er_hat_lasso, 'Lasso (linear)')
show_scoreboard()"""))

# Cell 11 markdown — modified first sentence
old_cell11_src = ''.join(old[11]['source'])
new_cell11_src = old_cell11_src.replace(
    'Note that the tuning-sample $R^2$ is very small — this is entirely expected for monthly return prediction. Recall that even $R^2$ values below 1% are economically meaningful in the cross-section.\n\nThe surviving features tell us which characteristics the Lasso believes carry genuine predictive power for future returns, after accounting for redundancy across the full set.',
    'The Lasso recovers some of the true signal direction, but with noise in the coefficient estimates.\n\nThe surviving features tell us which characteristics the Lasso selects, and we can compare them directly to the true $\\lambda$ vector.'
)
cells.append(md_cell(new_cell11_src))

cells.append(copy_cell(12))  # markdown: Adding Interactions

# Interactions — modified
cells.append(code_cell(r"""# Add pairwise interaction features
poly = PolynomialFeatures(degree=2, interaction_only=True, include_bias=False)
X_train_int = poly.fit_transform(X_tr_std)
X_test_int = poly.transform(X_te_std)

print(f"Features: {X_tr_std.shape[1]} → {X_train_int.shape[1]} (with interactions)")

# Lasso with interactions
alphas_int = [0.0005, 0.00075, 0.001, 0.0015, 0.002, 0.00225]
mses_int = []
for a in alphas_int:
    model = Lasso(alpha=a, max_iter=10000)
    model.fit(X_train_int, Y_synth_tr)
    mses_int.append(mean_squared_error(Y_synth_te, model.predict(X_test_int)))

best_int = Lasso(alpha=alphas_int[np.argmin(mses_int)], max_iter=10000)
best_int.fit(X_train_int, Y_synth_tr)

er_hat_int = best_int.predict(X_test_int)
ls_int = evaluate_model(er_hat_int, 'Lasso (interactions)')

print(f"\nBest interaction MSE: {min(mses_int):.6f}")
print(f"Best linear-only MSE: {min(mses):.6f}")
show_scoreboard()"""))

cells.append(copy_cell(14))  # markdown: interactions discussion
cells.append(copy_cell(15))  # markdown: Elastic Net

# Elastic Net — modified
cells.append(code_cell(r"""enet = ElasticNet(alpha=0.001, l1_ratio=0.5, max_iter=10000)
enet.fit(X_tr_std, Y_synth_tr)

mse_enet = mean_squared_error(Y_synth_te, enet.predict(X_te_std))
print(f"Elastic Net — Test MSE: {mse_enet:.6f}")
print(f"Non-zero coefficients: {np.sum(enet.coef_ != 0)} / {len(chars)}")

plot_coefficients(enet.coef_, 'Elastic Net — estimated vs. true coefficients')

er_hat_enet = enet.predict(X_te_std)
ls_enet = evaluate_model(er_hat_enet, 'Elastic Net')
show_scoreboard()"""))

cells.append(copy_cell(17))  # markdown: Percentile Dummies

# Percentile dummies — modified for controlled experiment data
cells.append(code_cell(r"""# Convert characteristics to percentile dummies
num_percentiles = 5
new_cols_train = []
new_cols_test = []

for col in X_ctrl_tr.columns:
    bins_tr = X_ctrl_tr[col].groupby('date').transform(
        lambda x: pd.qcut(x, q=num_percentiles, labels=False, duplicates='drop'))
    for p in range(num_percentiles):
        new_cols_train.append((bins_tr == p).astype(int).rename(f"{col}_p{p+1}"))

    bins_te = X_ctrl_te[col].groupby('date').transform(
        lambda x: pd.qcut(x, q=num_percentiles, labels=False, duplicates='drop'))
    for p in range(num_percentiles):
        new_cols_test.append((bins_te == p).astype(int).rename(f"{col}_p{p+1}"))

X_train_pct = pd.concat(new_cols_train, axis=1)
X_test_pct = pd.concat(new_cols_test, axis=1)
print(f"Percentile features: {X_train_pct.shape[1]}")

alphas_pct = [0.0005, 0.001, 0.0015, 0.002]
mses_pct = []
for a in alphas_pct:
    model = Lasso(alpha=a, max_iter=10000)
    model.fit(X_train_pct, Y_synth_tr)
    mses_pct.append(mean_squared_error(Y_synth_te, model.predict(X_test_pct)))

best_pct = Lasso(alpha=alphas_pct[np.argmin(mses_pct)], max_iter=10000)
best_pct.fit(X_train_pct, Y_synth_tr)

er_hat_pct = best_pct.predict(X_test_pct)
ls_pct = evaluate_model(er_hat_pct, 'Lasso (percentile)')
show_scoreboard()"""))

# ═══════════════════════════════════════════════════════════════
# Section 5: Tree-Based Methods
# ═══════════════════════════════════════════════════════════════
cells.append(copy_cell(19))  # markdown: Tree-Based Methods
cells.append(copy_cell(20))  # markdown: Random Forest

# RF — modified
cells.append(code_cell(r"""rf = RandomForestRegressor(n_estimators=50, max_depth=3, random_state=42, n_jobs=-1)
rf.fit(X_tr_std, Y_synth_tr)

mse_rf = mean_squared_error(Y_synth_te, rf.predict(X_te_std))
print(f"Random Forest — Test MSE: {mse_rf:.6f}")

# Feature importance vs truth
importance = pd.Series(rf.feature_importances_, index=chars).sort_values(ascending=True)
fig, ax = plt.subplots(figsize=(8, 6))
importance.plot(kind='barh', ax=ax)
ax.set_xlabel('Feature importance')
ax.set_title('Random Forest — feature importance (compare: true signal is on value)')
plt.tight_layout()
plt.show()

er_hat_rf = rf.predict(X_te_std)
ls_rf = evaluate_model(er_hat_rf, 'Random Forest')
show_scoreboard()"""))

cells.append(copy_cell(22))  # markdown: GBRT

# GBRT — modified
cells.append(code_cell(r"""gbrt = GradientBoostingRegressor(n_estimators=50, learning_rate=0.2, max_depth=3, random_state=42)
gbrt.fit(X_tr_std, Y_synth_tr)

mse_gbrt = mean_squared_error(Y_synth_te, gbrt.predict(X_te_std))
print(f"GBRT — Test MSE: {mse_gbrt:.6f}")

# Feature importance vs truth
importance_gb = pd.Series(gbrt.feature_importances_, index=chars).sort_values(ascending=True)
fig, ax = plt.subplots(figsize=(8, 6))
importance_gb.plot(kind='barh', ax=ax)
ax.set_xlabel('Feature importance')
ax.set_title('GBRT — feature importance (compare: true signal is on value)')
plt.tight_layout()
plt.show()

er_hat_gbrt = gbrt.predict(X_te_std)
ls_gbrt = evaluate_model(er_hat_gbrt, 'GBRT')
show_scoreboard()"""))

# ═══════════════════════════════════════════════════════════════
# Section 6: Neural Networks
# ═══════════════════════════════════════════════════════════════
cells.append(copy_cell(24))  # markdown: Neural Networks
cells.append(copy_cell(25))  # code: PyTorch imports
# Cell 26 from _c contains the class + train_nn + predict_nn + basic NN training
# We only want the class/functions, not the training code at the bottom
cell26_src = ''.join(old[26]['source'])
split_marker = '# Basic NN'
class_only = cell26_src[:cell26_src.index(split_marker)].rstrip() + '\n'
cells.append(code_cell(class_only))  # code: ReturnPredictor class + train_nn/predict_nn only

# DataFrame wrappers for NN
cells.append(code_cell(r"""# Create DataFrame versions for PyTorch (train_nn expects .values attribute)
X_tr_df = pd.DataFrame(X_tr_std, columns=chars, index=Y_ctrl_tr.index)
X_te_df = pd.DataFrame(X_te_std, columns=chars, index=Y_ctrl_te.index)
Y_tr_series = pd.Series(Y_synth_tr, index=Y_ctrl_tr.index)
Y_te_series = pd.Series(Y_synth_te, index=Y_ctrl_te.index)"""))

# Basic NN — modified to use synthetic data
cells.append(code_cell(r"""# Basic NN -- no regularization, trained on synthetic returns
print("Training basic NN (no regularization)...")
nn_basic = ReturnPredictor(len(chars), neurons=64, num_layers=3)
nn_basic = train_nn(nn_basic, X_tr_df, Y_tr_series, X_te_df, Y_te_series,
                    epochs=20, batch_size=256)

mse_nn_basic = mean_squared_error(Y_synth_te, predict_nn(nn_basic, X_te_df))
print(f"\nBasic NN -- Test MSE: {mse_nn_basic:.6f}")

er_hat_nn_basic = predict_nn(nn_basic, X_te_df)
ls_nn_basic = evaluate_model(er_hat_nn_basic, 'Neural Net (basic)')
show_scoreboard()"""))

cells.append(copy_cell(27))  # markdown: Regularizing NNs

# Regularized NN — modified
cells.append(code_cell(r"""# Regularized NN -- weight decay, dropout, early stopping
print("Training regularized NN...")
nn_reg = ReturnPredictor(len(chars), neurons=64, num_layers=3, dropout=0.1)
nn_reg = train_nn(nn_reg, X_tr_df, Y_tr_series, X_te_df, Y_te_series,
                  epochs=50, batch_size=256, weight_decay=1e-5, patience=10)

mse_nn_reg = mean_squared_error(Y_synth_te, predict_nn(nn_reg, X_te_df))
print(f"\nRegularized NN -- Test MSE: {mse_nn_reg:.6f}")
print(f"Basic NN -- Test MSE:       {mse_nn_basic:.6f}")

er_hat_nn_reg = predict_nn(nn_reg, X_te_df)
ls_nn_reg = evaluate_model(er_hat_nn_reg, 'Neural Net (regularized)')
show_scoreboard()"""))

# Scatter plot — modified to use synthetic data
cells.append(md_cell("Let's visualize what the neural network has learned by comparing its predicted returns to the true expected returns:"))

cells.append(code_cell(r"""# Compare NN predictions to true expected returns (we know the truth!)
last_date = X_te_df.index.get_level_values(0).unique().max()
X_last = X_te_df.loc[last_date]

pred_basic = pd.Series(predict_nn(nn_basic, X_last), index=X_last.index, name='Basic NN')
pred_reg = pd.Series(predict_nn(nn_reg, X_last), index=X_last.index, name='Regularized NN')
true_er = pd.Series(alpha * (((X_last - mu_x) / sd_x).values @ lam),
                     index=X_last.index, name='True E[R]')
combined = pd.concat([pred_basic, pred_reg, true_er], axis=1).dropna()

fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharex=True, sharey=True)

for ax, col, title in zip(axes, ['Basic NN', 'Regularized NN'],
                           ['Basic NN (no regularization)', 'Regularized NN (dropout + weight decay)']):
    ax.scatter(combined['True E[R]'] * 12, combined[col] * 12, alpha=0.3, s=10)
    ax.set_xlabel('True expected return (annualized)')
    ax.set_ylabel('NN predicted return (annualized)')
    ax.set_title(title)
    ax.axhline(0, color='gray', linewidth=0.5)
    ax.axvline(0, color='gray', linewidth=0.5)
    # 45-degree line
    lims = ax.get_xlim()
    ax.plot(lims, lims, 'r--', linewidth=0.5, alpha=0.5)

plt.tight_layout()
plt.show()"""))

# ═══════════════════════════════════════════════════════════════
# Section 7: Model Comparison
# ═══════════════════════════════════════════════════════════════
cells.append(copy_cell(31))  # markdown: Model Comparison

cells.append(code_cell(r"""# Final scoreboard
print(f"Oracle SR (analytical approximation): {oracle_sr:.2f}\n")
show_scoreboard()"""))

cells.append(copy_cell(33))  # markdown: Discussion

# ═══════════════════════════════════════════════════════════════
# Section 8: More Data, Smaller Signals
# ═══════════════════════════════════════════════════════════════
cells.append(copy_cell(46))  # markdown: More data, smaller signals
cells.append(copy_cell(47))  # code: Sharpe ratio vs training sample size

# ═══════════════════════════════════════════════════════════════
# Section 9: Double Descent
# ═══════════════════════════════════════════════════════════════
cells.append(copy_cell(34))  # markdown: DD intro
cells.append(copy_cell(35))  # code: DD on real data
cells.append(copy_cell(36))  # markdown: DD discussion

# DD with controlled experiment
cells.append(copy_cell(44))  # code: DD with date-based subsampling
cells.append(copy_cell(45))  # code: DD plot

cells.append(copy_cell(48))  # markdown: signal-to-noise threshold

# ═══════════════════════════════════════════════════════════════
# Section 10: Key Takeaways
# ═══════════════════════════════════════════════════════════════
cells.append(copy_cell(49))  # markdown: Key Takeaways

# ═══════════════════════════════════════════════════════════════
# Assemble notebook
# ═══════════════════════════════════════════════════════════════
nb_cc = {
    'cells': cells,
    'metadata': nb_c['metadata'],
    'nbformat': nb_c['nbformat'],
    'nbformat_minor': nb_c['nbformat_minor'],
}

out_path = 'MachineLearning_cc.ipynb'
with open(out_path, 'w') as f:
    json.dump(nb_cc, f, indent=1)

print(f"Wrote {out_path} with {len(cells)} cells")
for i, c in enumerate(cells):
    src = ''.join(c['source'])[:70].replace('\n', ' | ')
    print(f"  {i:2d} [{c['cell_type']:8s}]: {src}")
