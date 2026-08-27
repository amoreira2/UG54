"""Smoke test for StatisticalFactors_AI.ipynb.

Fills in the intended solutions for every ____ stub (Hands-On AND Challenge)
and executes the whole notebook. This verifies both that the notebook runs and
that the challenge answers match the answer key.
"""
import nbformat, re, sys
from nbconvert.preprocessors import ExecutePreprocessor
from pathlib import Path

NB = Path("/Users/am16634/Documents/GitHub/UG54/chapters/Finance/StatisticalFactors_AI.ipynb")
nb = nbformat.read(NB, as_version=4)

# stub → intended solution
SOLUTIONS = [
    # NB: C_noise must come first — "noise = ____" is a substring of it.
    ("C_noise = ____",      "C_noise = np.corrcoef(noise.T)"),
    ("\nnoise = ____",      "\nnoise = np.random.randn(T, N)"),
    ("    X = ____",        "    X = np.outer(f, beta) + eps"),
    ("    return ____",     "    return V[:, comp]"),
    # Challenge
    ("mp_edge_upper = ____",
     "mp_edge_upper = (1 + np.sqrt(R.shape[1]/120))**2"),
    ("n_factors_mp  = ____",
     "n_factors_mp = int((np.linalg.eigvalsh(np.corrcoef(R.iloc[-120:].values.T)) > mp_edge_upper).sum())"),
    ("pc1_share       = ____",
     "pc1_share = np.sort(np.linalg.eigvalsh(np.corrcoef(R.iloc[-120:].values.T)))[::-1][0] / R.shape[1]"),
    ("noise_pc1_share = ____",
     "noise_pc1_share = np.sort(np.linalg.eigvalsh(np.corrcoef(np.random.randn(120, R.shape[1]).T)))[::-1][0] / R.shape[1]"),
    ("n_factors_parallel = ____",
     "n_factors_parallel = parallel_analysis(R.iloc[-120:].values)[0]"),
]

MEMO_FILL = '''MEMO = """
Two factors, not ten. Both the Marchenko-Pastur edge and parallel analysis put
the cutoff at two eigenvalues, and they agree despite being derived completely
differently. PC1 explaining 55% of variance is not itself an argument, since
pure noise at this N and T produces a PC1 share of about 5% and a smoothly
decaying scree plot that looks like structure. Keeping ten components means
eight of them are directions the data cannot distinguish from noise, and because
the optimizer inverts the covariance matrix, those small noise eigenvalues get
amplified into large offsetting positions that cost turnover without reducing
risk. What I cannot rule out is that real factors exist below the detection
threshold, so the honest statement is that this data supports two factors, not
that only two exist.
"""'''

# Patch the GitHub raw URL to the local file so the appendix works pre-push (§7)
URL_MAP = {
    "https://raw.githubusercontent.com/amoreira2/UG54/refs/heads/main/assets/data/industry49_monthly.csv":
        str(Path("/Users/am16634/Documents/GitHub/UG54/assets/data/industry49_monthly.csv")),
}

filled = 0
for i, cell in enumerate(nb.cells):
    if cell.cell_type != "code":
        continue
    src = cell.source
    # the URL is split across two source lines in the notebook; rejoin then map
    src = src.replace("('https://raw.githubusercontent.com/amoreira2/UG54/'\n"
                      "              'refs/heads/main/assets/data/industry49_monthly.csv')",
                      repr(URL_MAP[list(URL_MAP)[0]]))
    if "SUBMISSION CELL" in src:
        nb.cells[i].source = "print('submission cell — skipped in smoke test')"
        continue
    if src.strip().startswith("MEMO = "):
        nb.cells[i].source = MEMO_FILL + "\nprint(MEMO)"
        filled += 1
        continue
    for stub, sol in SOLUTIONS:
        if stub in src:
            src = src.replace(stub, sol)
            filled += 1
    nb.cells[i].source = src

remaining = [i for i, c in enumerate(nb.cells)
             if c.cell_type == "code" and "____" in c.source]
print(f"Filled {filled} stubs. Cells still containing ____: {remaining}")
if remaining:
    for i in remaining:
        print("  ---", nb.cells[i].source[:200])

ep = ExecutePreprocessor(timeout=900, kernel_name="python3")
try:
    ep.preprocess(nb, {"metadata": {"path": "/Users/am16634/Documents/GitHub/UG54"}})
except Exception as e:
    print(f"\n❌ EXECUTION FAILED:\n{type(e).__name__}: {str(e)[-3000:]}")
    sys.exit(1)

print(f"\n✅ Executes cleanly ({len(nb.cells)} cells)\n")
print("=" * 70)
print("KEY OUTPUTS")
print("=" * 70)
for c in nb.cells:
    if c.cell_type != "code":
        continue
    for o in c.get("outputs", []):
        if o.get("output_type") == "stream":
            t = o.get("text", "")
            if any(k in t for k in ("MP upper edge", "Parallel analysis", "Real PC1",
                                    "You first detect", "Eigenvalues above the MP",
                                    "Condition number", "OOS annualized vol",
                                    "similarity between", "Sign flips",
                                    "Correlation of the PC1")):
                print(t.rstrip())
                print("-" * 50)
