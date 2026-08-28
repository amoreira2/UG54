"""Build L13 · Capital Allocation I — content lives in l13_content.txt beside this file."""
import json, re, os
HERE=os.path.dirname(os.path.abspath(__file__))
block=open(os.path.join(HERE,"l13_content.txt"),encoding='utf8').read()
parts=block.split("@@CELL@@"); cells=[("markdown",parts[0])]
for ch in parts[1:]:
    k,r=ch.split("@@",1); cells.append((k.strip(),r))
nb={"cells":[{"cell_type":k,"metadata":{},"source":t.strip("\n").splitlines(keepends=True),
              **({"outputs":[],"execution_count":None} if k=="code" else {})} for k,t in cells],
    "metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},
                "language_info":{"name":"python","version":"3.11"}},
    "nbformat":4,"nbformat_minor":5}
p=os.path.join(HERE,"L13_CapitalAllocationI_AI.ipynb")
json.dump(nb,open(p,"w"),indent=1)
w=sum(len(re.findall(r"[A-Za-z'-]+",t)) for k,t in cells if k=="markdown")
cut=next(i for i,(k,t) in enumerate(cells) if '## 🎯 Challenge' in t)
lec=sum(len(re.findall(r"[A-Za-z'-]+",t)) for k,t in cells[:cut] if k=="markdown")
print(f"✅ {os.path.basename(p)}  {len(cells)} cells  {w} md words total")
print(f"   lectured {lec} = {lec/1417:.2f} sessions")
