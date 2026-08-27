"""
Fix the previous patch which inserted into the TOC instead of before the
actual Key Takeaways header. Strategy:
  1. Find the 8 challenge/submission cells (identified by unique markers)
  2. Remove them
  3. Re-insert just before the markdown cell that BEGINS with "## 🧠 Key Takeaways"
"""

import json
from pathlib import Path

NB = Path(__file__).parent / "IntrotoReturns_c_AI.ipynb"
nb = json.loads(NB.read_text())

# Identify the 8 inserted cells by content markers
markers = [
    "Final Challenge: How Stable",  # 1st new cell
    "spy = yf.download",             # 2nd
    "spy_annual_mean      = ____",   # 3rd
    "spy_annual_mean    = ____",     # 4th (code stub)
    "Write a **single paragraph** (max 5",  # 5th
    "MEMO = ",                       # 6th
    "## 📤 Submission <a id=\"submit",  # 7th
    "SUBMISSION CELL — Run this last",  # 8th
]

# Find cells matching any marker
to_remove_indices = []
for i, c in enumerate(nb["cells"]):
    src = "".join(c["source"]) if isinstance(c["source"], list) else c["source"]
    for m in markers:
        if m in src:
            to_remove_indices.append(i)
            break

print(f"Found {len(to_remove_indices)} inserted cells at positions {to_remove_indices}")

# Extract them in order
extracted = [nb["cells"][i] for i in to_remove_indices]

# Remove from original (reverse order to preserve indices)
for i in sorted(to_remove_indices, reverse=True):
    del nb["cells"][i]

# Find the REAL Key Takeaways header: a markdown cell whose source STARTS with "## 🧠 Key Takeaways"
insert_at = None
for i, c in enumerate(nb["cells"]):
    if c["cell_type"] != "markdown":
        continue
    src = "".join(c["source"]) if isinstance(c["source"], list) else c["source"]
    # Strip leading whitespace and check for the actual header
    stripped = src.lstrip()
    if stripped.startswith("## 🧠 Key Takeaways") or stripped.startswith("---\n\n## 🧠 Key Takeaways"):
        insert_at = i
        break

if insert_at is None:
    # Fallback: append at end
    insert_at = len(nb["cells"])
    print("⚠️ Could not find Key Takeaways header — appending at end")
else:
    print(f"Inserting before cell {insert_at} (Key Takeaways header)")

# Re-insert
nb["cells"] = nb["cells"][:insert_at] + extracted + nb["cells"][insert_at:]

NB.write_text(json.dumps(nb, indent=1))
print(f"✅ Now {len(nb['cells'])} cells total")

# Sanity print: show 3 cells before and after the insertion point
print("\nContext around insertion:")
for i in range(max(0, insert_at - 2), min(len(nb["cells"]), insert_at + len(extracted) + 2)):
    c = nb["cells"][i]
    src = "".join(c["source"]) if isinstance(c["source"], list) else c["source"]
    print(f"  [{i:3d}] {c['cell_type']}: {src[:70].replace(chr(10),' ⏎ ')}")
