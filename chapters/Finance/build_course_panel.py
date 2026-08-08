"""
Build the UG54 course panel.

Two tiers, mirroring the assessment structure:

  WORKHORSE (in repo, used in class)   1980-2000, full CRSP universe,
                                       ~10 famous signals. Everyone same data,
                                       so in-lecture challenges stay auto-gradable.

  PROJECT   (students pull themselves) full history, any of 331 OSAP signals
                                       via openassetpricing.dl_signal().

Outputs (assets/data/):
  panel_backbone_1980_2000.parquet   permno, date, ret, me, exchcd, shrcd, prc
  panel_signals_1980_2000.parquet    permno, date + workhorse signals (float32)
  signal_doc.csv                     331 signals w/ authors, year, published t-stat

Why a separate backbone file: L2 (build the market portfolio) and L3 (NYSE
breakpoints) need the FULL universe including microcaps but only 5-6 columns.
Keeping it separate means those lectures load ~15MB instead of ~300MB, and
students merge on only the one signal they actually use.

Delisting returns ARE merged in. CRSP msf.ret is missing in the delisting
month; ignoring dlret biases returns upward. This is exactly the kind of
silent bug the course is about, so the panel gets it right and the L2 notebook
shows the adjustment.

Run:  python build_course_panel.py
"""

import numpy as np
import pandas as pd
from pathlib import Path
import time

OUT = Path(__file__).resolve().parents[2] / "assets" / "data"
OUT.mkdir(parents=True, exist_ok=True)

START, END = "1980-01-01", "2000-12-31"

# 30 signals across 18 economic categories. Every one is "1_clear" predictability
# with "1_good"/"2_fair" replication quality in OSAP, has history before 1985,
# and has a named paper a group can actually read.
#
# Stored ONE PARQUET PER SIGNAL (~3-4 MB each) rather than one wide file:
#   - a student loads backbone + their one signal = ~16 MB, fast in Colab
#   - no file approaches GitHub's size limit
#   - choosing the file IS choosing the strategy, which is the pedagogical point
WORKHORSE = [
    # valuation
    "BM", "EP", "EntMult",
    # size / momentum / reversal
    "Size", "Mom12m", "Mom6m", "ResidualMomentum", "STreversal",
    # investment & asset composition
    "AssetGrowth", "InvestPPEInv", "NOA",
    # accruals & profitability
    "Accruals", "GP", "CBOperProf", "roaq",
    # external financing
    "ShareIss1Y", "ShareIss5Y", "CompositeDebtIssuance",
    # volatility & risk
    "IdioVol3F", "RealizedVol", "MaxRet", "ReturnSkew",
    # liquidity & volume
    "Illiquidity", "DolVol",
    # other
    "BookLeverage", "OScore", "AnnouncementReturn", "IntanBM",
    "DivSeason", "OrgCap",
]


def pull_crsp():
    import wrds
    print("connecting to WRDS ...", flush=True)
    db = wrds.Connection(wrds_username="am16634")
    print("  connected", flush=True)

    t0 = time.time()
    crsp = db.raw_sql(f"""
        select a.permno, a.date, a.ret, a.prc, a.shrout,
               b.exchcd, b.shrcd
        from crsp.msf a
        left join crsp.msenames b
          on a.permno = b.permno
         and b.namedt <= a.date
         and a.date <= b.nameendt
        where a.date between '{START}' and '{END}'
          and b.shrcd in (10, 11)
          and b.exchcd in (1, 2, 3)
    """, date_cols=["date"])
    print(f"  msf: {len(crsp):,} rows in {time.time()-t0:.0f}s", flush=True)

    # Delisting returns — msf.ret is missing in the delist month.
    dl = db.raw_sql(f"""
        select permno, dlstdt as date, dlret
        from crsp.msedelist
        where dlstdt between '{START}' and '{END}'
    """, date_cols=["date"])
    print(f"  msedelist: {len(dl):,} rows", flush=True)
    db.close()

    # align to month end so the merge keys match
    for df in (crsp, dl):
        df["date"] = pd.to_datetime(df["date"]) + pd.offsets.MonthEnd(0)

    m = crsp.merge(dl, on=["permno", "date"], how="left")
    n_dl = m["dlret"].notna().sum()

    # compound ret with dlret where both present; use whichever exists otherwise
    r, d = m["ret"], m["dlret"]
    m["ret_adj"] = np.where(r.notna() & d.notna(), (1 + r) * (1 + d) - 1,
                     np.where(r.isna() & d.notna(), d, r))
    print(f"  delisting returns applied to {n_dl:,} obs", flush=True)

    m["me"] = m["prc"].abs() * m["shrout"]        # $thousands
    m = m.dropna(subset=["ret_adj"])
    out = (m[["permno", "date", "ret_adj", "me", "prc", "exchcd", "shrcd"]]
             .rename(columns={"ret_adj": "ret"})
             .astype({"permno": "int32", "exchcd": "int8", "shrcd": "int8",
                      "ret": "float32", "me": "float32", "prc": "float32"}))
    out = out.sort_values(["permno", "date"]).reset_index(drop=True)

    # ret_fwd: the return you EARN by sorting on a signal observed at date t.
    # Only defined when the next observation is the very next calendar month —
    # otherwise a gap in the series would silently splice returns across time.
    # Sorting on a signal at t and measuring ret at t is look-ahead: for
    # STreversal that single error turns t = -0.4 into t = +70.
    mo = out["date"].dt.year * 12 + out["date"].dt.month
    nxt = out.groupby("permno")["date"].shift(-1)
    nxt = nxt.dt.year * 12 + nxt.dt.month
    out["ret_fwd"] = (out.groupby("permno")["ret"].shift(-1)
                         .where((nxt - mo) == 1).astype("float32"))
    return out


def pull_signals():
    import openassetpricing as oap
    o = oap.OpenAP()

    print("downloading signal documentation ...", flush=True)
    doc = o.dl_signal_doc("pandas")
    doc.to_csv(OUT / "signal_doc.csv", index=False)
    print(f"  signal_doc.csv: {len(doc)} signals", flush=True)

    print(f"downloading {len(WORKHORSE)} workhorse signals (slow, ~2 min) ...", flush=True)
    t0 = time.time()
    sig = o.dl_signal("pandas", WORKHORSE)
    print(f"  {len(sig):,} rows in {time.time()-t0:.0f}s", flush=True)

    sig["yyyymm"] = sig["yyyymm"].astype(int)
    sig["date"] = (pd.to_datetime(sig["yyyymm"].astype(str), format="%Y%m")
                   + pd.offsets.MonthEnd(0))
    sig = sig[(sig["date"] >= START) & (sig["date"] <= END)]

    cols = {"permno": "int32"}
    cols.update({c: "float32" for c in WORKHORSE if c in sig.columns})
    return sig[["permno", "date"] + [c for c in WORKHORSE if c in sig.columns]].astype(cols)


if __name__ == "__main__":
    p1 = OUT / "panel_backbone_1980_2000.parquet"
    if p1.exists():
        bb = pd.read_parquet(p1)
        print(f"reusing {p1.name}: {len(bb):,} rows", flush=True)
    else:
        bb = pull_crsp()
        bb.to_parquet(p1, compression="zstd", index=False)
        print(f"\n✅ {p1.name}: {len(bb):,} rows, {p1.stat().st_size/1e6:.1f} MB", flush=True)
        print(f"   {bb.permno.nunique():,} permnos, {bb.date.nunique()} months, "
              f"{len(bb)/bb.date.nunique():.0f} stocks/month", flush=True)

    sg = pull_signals()
    keys = bb[["permno", "date"]]

    # OSAP ships the RAW characteristic plus a Sign column; it is NOT pre-signed.
    # 18 of our 30 have Sign = -1. We pre-sign on write so every stored signal
    # means "higher = predicted higher return", the long-short is always D10-D1,
    # and our t-stats are directly comparable to the published ones in
    # signal_menu.csv. The original direction is preserved in that file.
    doc_sign = (pd.read_csv(OUT / "signal_doc.csv")
                  .set_index("Acronym")["Sign"].to_dict())

    sigdir = OUT / "signals"
    sigdir.mkdir(exist_ok=True)
    rows = []
    for c in WORKHORSE:
        if c not in sg.columns:
            print(f"   ⚠️  {c} not returned by OSAP — skipped", flush=True)
            continue
        one = keys.merge(sg[["permno", "date", c]], on=["permno", "date"], how="inner")
        # OSAP characteristics are often log ratios, so a zero or negative
        # denominator yields +/-inf rather than NaN. Five of our thirty are
        # affected; CompositeDebtIssuance is 8.6% infinite. pd.qcut sorts inf
        # silently into the extreme bucket, so an unfiltered top decile can be
        # nothing but infinities -- corrupting the result, not just the mean.
        one[c] = one[c].replace([np.inf, -np.inf], np.nan)
        one = one.dropna(subset=[c])
        if doc_sign.get(c) == -1:
            one[c] = (-one[c]).astype("float32")
        f = sigdir / f"{c}.parquet"
        one.to_parquet(f, compression="zstd", index=False)
        rows.append((c, len(one), len(one) / len(bb), f.stat().st_size / 1e6))

    print(f"\n{'signal':24s}{'rows':>11s}{'coverage':>10s}{'MB':>7s}")
    for c, n, cov, mb in rows:
        print(f"{c:24s}{n:>11,}{cov:>10.1%}{mb:>7.1f}", flush=True)
    print(f"\n✅ {len(rows)} signal files, total "
          f"{sum(r[3] for r in rows):.1f} MB, largest {max(r[3] for r in rows):.1f} MB")

    # student-facing data dictionary for exactly these signals
    doc = pd.read_csv(OUT / "signal_doc.csv")
    keep = ["Acronym", "Authors", "Year", "Journal", "Cat.Economic",
            "LongDescription", "Sign", "T-Stat", "Signal Rep Quality"]
    d = doc[doc.Acronym.isin([r[0] for r in rows])][keep].sort_values("Cat.Economic")
    d.to_csv(OUT / "signal_menu.csv", index=False)
    print(f"✅ signal_menu.csv: {len(d)} signals with paper + published t-stat")
