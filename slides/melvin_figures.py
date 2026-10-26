"""
Figures for the Melvin Capital opening of slides/hiring_and_firing.tex.

    python slides/melvin_figures.py

Melvin's returns are not public month by month. Everything below is a number reported in
the press (sources in the comments and on the deck's sources slide). Between reported
dates the path is unknown, so the 2021-22 lines are drawn dashed between the dots.

GameStop prices come from Yahoo Finance (yfinance) and are multiplied by 4 to undo the
4-for-1 split of July 2022, so they read as the prices traded in January 2021
(close of $18.84 on 31 Dec 2020 and $347.51 on 27 Jan 2021). Saved to slides/gme_daily.csv.
"""
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / "figures"
OUT.mkdir(exist_ok=True)

GREY, RED, BLUE, LIGHT = "#6B6B6B", "#B03A2E", "#2E5C8A", "#C9C9C9"
plt.rcParams.update({
    "font.size": 13, "axes.titlesize": 14, "axes.labelsize": 13,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": False, "figure.dpi": 150, "savefig.bbox": "tight",
})

# ---------------------------------------------------------------- the reported numbers
# Annual returns, net of fees, as reported (Wikipedia's compilation of Bloomberg / WSJ / II reports).
# 2016 and 2018 full-year figures were not reported. Melvin averaged about 30% a year 2014-2020.
annual = {2015: 47, 2016: None, 2017: 41, 2018: None, 2019: 44, 2020: 52}

# Value of $100 invested at the end of 2020, at each date for which a return was reported.
nav = pd.Series({
    "2020-12-31": 100.0,
    "2021-01-22": 70.0,         # down about 30% so far this year (WSJ, 24 Jan 2021)
    "2021-01-29": 47.0,         # down 53% in January (Reuters / WSJ)
    "2021-02-26": 47.0 * 1.22,  # up 22% in February
    "2021-03-31": 51.0,         # down 49% for the year at end of March
    "2021-06-30": 54.0,         # down 46% at end of June
    "2021-11-30": 58.0,         # down 42% in November
    "2021-12-31": 61.0,         # down 39% for 2021
    "2022-01-21": 61.0 * 0.83,  # down 17% in the first three weeks of January 2022 (Reuters)
    "2022-03-31": 61.0 * 0.79,  # down 21% in Q1 2022 (CNBC)
    "2022-04-29": 61.0 * 0.77,  # down 23% in the first four months of 2022 (Reuters)
})
nav.index = pd.to_datetime(nav.index)
INJECTION, CLOSURE = pd.Timestamp("2021-01-25"), pd.Timestamp("2022-05-18")

# ---------------------------------------------------------------- GameStop, as traded in January 2021
import yfinance as yf
raw = yf.download("GME", start="2020-11-30", end="2021-03-01", auto_adjust=False, progress=False)
raw.columns = [c[0] if isinstance(c, tuple) else c for c in raw.columns]
gme = (raw["Close"] * 4).rename("close")                       # undo the July 2022 4-for-1 split
gme.to_frame().to_csv(HERE / "gme_daily.csv")

# ---------------------------------------------------------------- 1. the record (anonymous), against the S&P 500
# S&P 500 total return (dividends reinvested), from the ^SP500TR index on Yahoo Finance, year-end to year-end.
spx = yf.download("^SP500TR", start="2014-12-01", end="2021-01-10", auto_adjust=False, progress=False)
spx.columns = [c[0] if isinstance(c, tuple) else c for c in spx.columns]
year_end = spx["Close"].groupby(spx.index.year).last()
sp500 = (100 * (year_end / year_end.shift(1) - 1)).loc[2015:2020]

fig, ax = plt.subplots(figsize=(8.5, 3.9))
years = list(annual)
w = 0.38
for i, y in enumerate(years):
    v = annual[y]
    if v is None:
        ax.bar(i - w / 2, 2, color="white", edgecolor=LIGHT, hatch="///", width=w)
        ax.text(i - w / 2, 4, "not\nreported", ha="center", va="bottom", fontsize=9, color=GREY)
    else:
        ax.bar(i - w / 2, v, color=BLUE, width=w)
        ax.text(i - w / 2, v + 1.5, f"+{v}%", ha="center", va="bottom", fontsize=12, fontweight="bold")
    m = sp500.loc[y]
    ax.bar(i + w / 2, m, color=LIGHT, width=w)
    ax.text(i + w / 2, m + 1.5 if m >= 0 else m - 1.5, f"{m:+.0f}%".replace("-", "\u2212"), ha="center", va="bottom" if m >= 0 else "top",
            fontsize=10.5, color=GREY)
ax.axhline(0, color=GREY, linewidth=0.8)
ax.set_xticks(range(len(years)), years)
ax.set_yticks([])
ax.spines["left"].set_visible(False)
ax.spines["bottom"].set_visible(False)
ax.tick_params(axis="x", length=0)
ax.set_ylim(-10, 62)
ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=BLUE), plt.Rectangle((0, 0), 1, 1, color=LIGHT)],
          labels=["Fund M, net of fees", "S&P 500, with dividends"], frameon=False, ncol=2,
          loc="lower left", bbox_to_anchor=(0, 1.0), fontsize=11)
ax.set_title("Return each year: Fund M against the S&P 500", pad=30)
fig.savefig(OUT / "melvin_record.pdf"); plt.close(fig)

# ---------------------------------------------------------------- 2. January 2021 (anonymous)
jan = nav[:"2021-01-29"]
fig, ax = plt.subplots(figsize=(8.5, 3.9))
ax.plot(jan.index, jan.values, color=RED, linewidth=2.2, linestyle="--", marker="o", markersize=8)   # dashed: path between reports unknown
for d, v in jan.items():
    ax.text(d, v + 5, f"{v:.0f}", ha="center", fontsize=12)
ax.axhline(100, color=LIGHT, linewidth=1, linestyle=":")
ax.set_ylim(30, 115)
ax.set_ylabel("value of $100 put in\non 31 Dec 2020")
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
ax.set_xticks(jan.index)
ax.set_title("Fund M in January 2021")
fig.savefig(OUT / "melvin_january.pdf"); plt.close(fig)

# ---------------------------------------------------------------- 3. what GameStop did
fig, ax = plt.subplots(figsize=(8.5, 3.9))
ax.plot(gme.index, gme.values, color=GREY, linewidth=2)
peak = gme.idxmax()
ax.annotate(f"${gme.max():.2f} close, {peak:%b %d}", xy=(peak, gme.max()), xytext=(peak + pd.Timedelta(days=9), gme.max() - 20),
            fontsize=12, arrowprops=dict(arrowstyle="-", color=GREY))
ax.annotate(f"${gme.loc['2020-12-31']:.2f} on Dec 31", xy=(pd.Timestamp("2020-12-31"), gme.loc["2020-12-31"]),
            xytext=(pd.Timestamp("2020-12-03"), 90), fontsize=12, arrowprops=dict(arrowstyle="-", color=GREY))
ax.axvline(INJECTION, color=RED, linewidth=1.2, linestyle="--")
ax.text(INJECTION - pd.Timedelta(days=1), 300, "Jan 25:\n$2.75bn\ninto Fund M", color=RED, ha="right", fontsize=11)
ax.set_ylabel("GameStop share price ($)")
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
ax.set_title("GameStop, December 2020 to February 2021")
fig.savefig(OUT / "gme_squeeze.pdf"); plt.close(fig)

# ---------------------------------------------------------------- 4. what happened next
fig, ax = plt.subplots(figsize=(9.5, 4.1))
ax.plot(nav.index, nav.values, color=RED, linewidth=1.8, linestyle="--", marker="o", markersize=6)
ax.axhline(100, color=LIGHT, linewidth=1, linestyle=":")
ax.axvline(INJECTION, color=BLUE, linewidth=1.2)
ax.text(INJECTION + pd.Timedelta(days=8), 104, "Jan 25, 2021: $2.75bn injection", color=BLUE, fontsize=11)
ax.axvline(CLOSURE, color=GREY, linewidth=1.2)
ax.text(CLOSURE - pd.Timedelta(days=8), 104, "May 18, 2022:\nfund to close", color=GREY, fontsize=11, ha="right", va="top")
ax.annotate("end of 2021: 61", xy=(pd.Timestamp("2021-12-31"), 61), xytext=(pd.Timestamp("2021-09-01"), 75),
            fontsize=11, arrowprops=dict(arrowstyle="-", color=GREY))
ax.annotate("end of Jan 2021: 47", xy=(pd.Timestamp("2021-01-29"), 47), xytext=(pd.Timestamp("2021-03-20"), 36),
            fontsize=11, arrowprops=dict(arrowstyle="-", color=GREY))
ax.set_ylim(30, 110)
ax.set_ylabel("value of $100 put in\non 31 Dec 2020")
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 4, 7, 10]))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
ax.set_title("Melvin Capital after January 2021 (dots are reported returns)")
fig.savefig(OUT / "melvin_after.pdf"); plt.close(fig)

# ================================================================ numbers the slides quote
print(f"GME close: Dec 31 2020 ${gme.loc['2020-12-31']:.2f}; peak close ${gme.max():.2f} on {peak:%Y-%m-%d}; "
      f"Jan 25 ${gme.loc['2021-01-25']:.2f}; Jan 28 ${gme.loc['2021-01-28']:.2f}; rise to peak x{gme.max() / gme.loc['2020-12-31']:.0f}")
print(f"Money in at end of Jan 2021 (47) -> end of 2021 (61): {61 / 47 - 1:+.0%};  -> end of Apr 2022 ({nav.iloc[-1]:.0f}): {nav.iloc[-1] / 47 - 1:+.0%}")
print(f"Money in since end of 2020: end of 2021 {61 / 100 - 1:+.0%}; end of Apr 2022 {nav.iloc[-1] / 100 - 1:+.0%}")
print("S&P 500 total return by year:", sp500.round(1).to_dict(), "| average 2015-2020:", round(100 * ((1 + sp500 / 100).prod() ** (1 / len(sp500)) - 1), 1), "%")
print("Bayes example: odds 9:1 x 1/3 = 3:1 (75%); odds 1:1 x 1/3 = 1:3 (25%)")
