"""
Cache Berkshire Hathaway's disclosed 13F equity holdings, 1990-2000.

Source: WRDS `tr_13f.s34type3` (Thomson Reuters institutional holdings),
mgrno 8350 = BERKSHIRE HATHAWAY INC. Joined to CRSP via ncusip to get permno
and to CRSP monthly prices to value each position.

Coverage note worth carrying into the lecture: Thomson has 13F from 1980-03-31,
and Berkshire appears in every quarter since. But the NUMBER of positions
Berkshire reports swings a lot -- 11-13 in 1993-95, down to 5 in 1997-98, up to
29 by end-2000. That is confidential-treatment requests and Thomson coverage,
NOT portfolio turnover. Known large holdings (Wells Fargo, Freddie Mac) are
missing from some filings entirely.

Output: assets/data/brk_13f_holdings.csv
    fdate, permno, comnam, shares, prc, value, weight
"""

import wrds
import pandas as pd
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "assets" / "data" / "brk_13f_holdings.csv"
MGRNO = 8350
START, END = "1990-01-01", "2000-12-31"

db = wrds.Connection(wrds_username="am16634")

h = db.raw_sql("""select fdate, cusip, shares from tr_13f.s34type3
                  where mgrno = %(m)s and fdate between %(s)s and %(e)s""",
               params={"m": MGRNO, "s": START, "e": END})
h["fdate"] = pd.to_datetime(h["fdate"])
print(f"{len(h)} raw position-dates over {h.fdate.nunique()} filings", flush=True)

# cusip -> permno.  msenames is name-history, so restrict to the row valid at fdate.
nm = db.raw_sql("""select ncusip, comnam, permno, namedt, nameendt from crsp.msenames
                   where ncusip in %(c)s""",
                params={"c": tuple(str(x) for x in h.cusip.unique())})
for c in ("namedt", "nameendt"):
    nm[c] = pd.to_datetime(nm[c])

j = h.merge(nm, left_on="cusip", right_on="ncusip", how="left")
j = j[(j.namedt <= j.fdate) & (j.fdate <= j.nameendt)]      # the name valid on that date
j["permno"] = j.permno.astype(int)

# price each position from CRSP monthly
px = db.raw_sql("""select permno, date, prc from crsp.msf
                   where date between %(s)s and %(e)s and permno in %(p)s""",
                params={"s": START, "e": END,
                        "p": tuple(int(x) for x in j.permno.unique())})
px["date"] = pd.to_datetime(px["date"]) + pd.offsets.MonthEnd(0)
db.close()

j["fdate"] = j.fdate + pd.offsets.MonthEnd(0)
j = j.merge(px, left_on=["permno", "fdate"], right_on=["permno", "date"], how="left")

# Thomson reports shares in ACTUAL units (not thousands) -- verified against the
# known ~$37B Berkshire equity book at end-1999. prc is negative when CRSP is
# reporting a bid/ask midpoint, so take the absolute value.
j["value"] = j.shares * j.prc.abs()
j = j.dropna(subset=["value"])
j["weight"] = j.value / j.groupby("fdate")["value"].transform("sum")

out = (j[["fdate", "permno", "comnam", "shares", "prc", "value", "weight"]]
         .sort_values(["fdate", "value"], ascending=[True, False]))
out.to_csv(OUT, index=False)

print(f"\n✅ {OUT.name}: {len(out)} rows, {out.fdate.nunique()} filing dates")
n = out.groupby("fdate").size()
print(f"   positions per filing: min {n.min()}, median {int(n.median())}, max {n.max()}")
tot = out.groupby("fdate")["value"].sum() / 1e9
print(f"   disclosed value: ${tot.min():.1f}B to ${tot.max():.1f}B")
print(f"\n1999-12-31 snapshot:")
s = out[out.fdate == "1999-12-31"].head(10)
for _, r in s.iterrows():
    print(f"   {r.comnam[:30]:32s} {r.weight:6.1%}")
