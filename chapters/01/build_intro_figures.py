"""Figures for chapters/01/what-is-data-driven-investing.md.

Run from anywhere:  python chapters/01/build_intro_figures.py
Writes five PNGs into assets/plots/ (ddi_*.png).

Palette matches the existing PowerPoint figures on that page (intro1/3/4/5):
grey boxes, a single orange accent, dark grey type, no gridlines.
"""
import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrow

HERE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(HERE, "..", "..", "assets", "plots")

GREY, EDGE, DARK = "#EFEFEF", "#BFBFBF", "#3A3A3A"
ORANGE, OEDGE    = "#F2C066", "#D9A036"
MUTE             = "#8C8C8C"

plt.rcParams.update({"font.family": "DejaVu Sans", "text.color": DARK,
                     "axes.edgecolor": EDGE, "axes.labelcolor": DARK,
                     "xtick.color": DARK, "ytick.color": DARK})


def box(ax, x, y, w, h, text, fill=GREY, edge=EDGE, size=9, weight="normal"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.008,rounding_size=0.012",
                                fc=fill, ec=edge, lw=1.0))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=size, fontweight=weight, color=DARK, linespacing=1.45)


def save(fig, name):
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, name)
    fig.savefig(p, dpi=170, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote", os.path.normpath(p))


# ══════════════════════════════════════════════ A · the five gates
fig, ax = plt.subplots(figsize=(11, 2.9))
ax.set_xlim(0, 11); ax.set_ylim(0.15, 2.85); ax.axis("off")

box(ax, 0.05, 1.30, 1.45, 0.95, "You have a\nprediction", fill=ORANGE, edge=OEDGE,
    size=10, weight="bold")

gates = [("Risk", "the forecast is\nright on average\nand you can still\nbe wrong"),
         ("Liquidity", "you cannot buy\nor borrow it in\nthe size you\nneed"),
         ("Funding", "it is cheapest\nexactly when you\nhave no capital\nleft"),
         ("Flows", "someone must\ntrade on a known\ndate whether or\nnot they want to"),
         ("Information", "you know\nsomething your\ncompetitors\ndo not")]

x = 1.75
for i, (title, sub) in enumerate(gates):
    box(ax, x, 0.95, 1.62, 1.65, "", fill="white", edge=EDGE)
    ax.text(x + 0.81, 2.33, title, ha="center", va="center", fontsize=10,
            fontweight="bold", color=DARK)
    ax.plot([x + 0.20, x + 1.42], [2.13, 2.13], color=EDGE, lw=0.9)
    ax.text(x + 0.81, 1.55, sub, ha="center", va="center", fontsize=8.1,
            color=MUTE, linespacing=1.5)
    if i < len(gates) - 1:
        ax.add_patch(FancyArrow(x + 1.66, 1.78, 0.14, 0, width=0.012,
                                head_width=0.10, head_length=0.07,
                                fc=MUTE, ec=MUTE, length_includes_head=True))
    x += 1.80

ax.add_patch(FancyArrow(1.52, 1.78, 0.16, 0, width=0.012, head_width=0.10,
                        head_length=0.07, fc=MUTE, ec=MUTE, length_includes_head=True))
ax.text(5.5, 0.42,
        "Four of these can stop a correct forecast from becoming a profitable trade.\n"
        "Only the last one is what most people mean by “having an edge.”",
        ha="center", va="center", fontsize=9.3, color=DARK, linespacing=1.6)
save(fig, "ddi_five_gates.png")


# ══════════════════════════════════════════════ B · the pipeline
fig, ax = plt.subplots(figsize=(11.5, 4.6))
ax.set_xlim(0, 11.5); ax.set_ylim(0, 4.6); ax.axis("off")

stages = [
    ("Data",             ["prices and volumes", "characteristics", "time series",
                          "unstructured text"],
     "the panel · sorts and signals"),
    ("Before the trade", ["risk", "expected returns", "transaction costs"],
     "factor models · backtesting\nmomentum · trading costs"),
    ("During the trade", ["risk constraints", "signal aggregation", "hedging"],
     "capital allocation\nleverage and shorting"),
    ("After the trade",  ["performance attribution", "volatility allocation",
                          "leverage"],
     "performance evaluation\nportfolio decomposition\nconditional strategies"),
]

w, gap = 2.55, 0.30
x = 0.10
for i, (title, items, course) in enumerate(stages):
    ax.text(x + w / 2, 4.28, title, ha="center", va="center", fontsize=10.5,
            fontweight="bold", color=DARK)
    h = 0.28 + 0.46 * len(items)
    box(ax, x, 4.02 - h, w, h, "", fill="white", edge=EDGE)
    for j, it in enumerate(items):
        box(ax, x + 0.16, 3.58 - j * 0.46, w - 0.32, 0.36, it, fill=GREY, size=8.8)
    box(ax, x, 0.62, w, 1.10, course, fill=ORANGE, edge=OEDGE, size=8.6)
    if i < 3:
        ax.add_patch(FancyArrow(x + w + 0.04, 3.05, gap - 0.10, 0, width=0.02,
                                head_width=0.14, head_length=0.10,
                                fc=MUTE, ec=MUTE, length_includes_head=True))
    x += w + gap

ax.text(5.85, 0.20,
        "The orange row is where this course does each stage.\n"
        "After the trade feeds back into Data — the loop is the job.",
        ha="center", va="center", fontsize=9.2, color=DARK, linespacing=1.6)
save(fig, "ddi_pipeline.png")


# ══════════════════════════════════════════════ C · 3Com / Palm
fig, ax = plt.subplots(figsize=(7.6, 4.3))
labels = ["Palm\nmarket value", "3Com's 95%\nstake in Palm",
          "3Com\nmarket value", "Implied value of\n3Com's other assets"]
vals   = [54, 51, 28, -23]
cols   = [GREY, GREY, GREY, ORANGE]
edges  = [EDGE, EDGE, EDGE, OEDGE]

bars = ax.bar(labels, vals, color=cols, edgecolor=edges, width=0.62, lw=1.1)
ax.axhline(0, color=DARK, lw=1.0)
for b, v in zip(bars, vals):
    ax.text(b.get_x() + b.get_width() / 2, v + (2.2 if v > 0 else -3.4),
            f"${v}B" if v > 0 else f"−${abs(v)}B",
            ha="center", va="bottom" if v > 0 else "top",
            fontsize=10.5, fontweight="bold", color=DARK)
ax.set_ylabel("$ billions", fontsize=9.5)
ax.set_ylim(-33, 63)
ax.set_title("3Com and Palm, March 2000", fontsize=11.5, fontweight="bold",
             color=DARK, pad=12)
for s in ("top", "right"): ax.spines[s].set_visible(False)
ax.spines["left"].set_color(EDGE); ax.spines["bottom"].set_visible(False)
ax.tick_params(axis="x", length=0, labelsize=8.8)
ax.tick_params(axis="y", labelsize=8.8)
fig.text(0.5, -0.12,
         "3Com had no debt, $1B of cash and positive cash flow. The arbitrage was arithmetic.\n"
         "You could not borrow Palm shares to short at any workable rate.",
         ha="center", fontsize=8.8, color=MUTE, linespacing=1.6)
save(fig, "ddi_3com_palm.png")


# ══════════════════════════════════════════════ D · who owns, who trades
fig, axes = plt.subplots(1, 2, figsize=(11, 3.4))

a = axes[0]
a.barh([0], [37], color=ORANGE, edgecolor=OEDGE, height=0.40, lw=1.1)
a.barh([0], [63], left=[37], color=GREY, edgecolor=EDGE, height=0.40, lw=1.1)
a.text(18.5, 0, "37%", ha="center", va="center", fontsize=12,
       fontweight="bold", color=DARK)
a.text(68.5, 0, "everyone else", ha="center", va="center", fontsize=9.5, color=DARK)
a.text(18.5, -0.34, "index funds\nand ETFs", ha="center", va="top",
       fontsize=8.6, color=MUTE, linespacing=1.4)
a.set_xlim(0, 100); a.set_ylim(-0.95, 0.45); a.axis("off")
a.set_title("Who owns the US stock market\nshare of market capitalisation, 2020",
            fontsize=10.2, fontweight="bold", color=DARK, pad=8)

b = axes[1]
b.bar(["2011", "2020"], [10, 20], color=[GREY, ORANGE],
      edgecolor=[EDGE, OEDGE], width=0.45, lw=1.1)
for x_, v in zip([0, 1], [10, 20]):
    b.text(x_, v + 0.8, f"{v}%", ha="center", fontsize=11, fontweight="bold", color=DARK)
b.set_ylim(0, 26); b.set_ylabel("share of volume", fontsize=9)
b.set_title("Who trades\nretail share of US trading volume",
            fontsize=10.2, fontweight="bold", color=DARK, pad=8)
for s in ("top", "right"): b.spines[s].set_visible(False)
b.spines["left"].set_color(EDGE); b.spines["bottom"].set_color(EDGE)
b.tick_params(labelsize=9, length=0)

fig.text(0.5, -0.13,
         "Left: Chinco & Sammon (2023). Right: share of trading volume — a different denominator, "
         "so the two panels\nare not slices of the same pie. Other estimates of the passive share "
         "are much lower on a different basis; see the text.",
         ha="center", fontsize=8.4, color=MUTE, linespacing=1.6)
save(fig, "ddi_who_owns_who_trades.png")


# ══════════════════════════════════════════════ E · what Bogle proved
fig, ax = plt.subplots(figsize=(8.6, 1.45))
ax.barh([0], [91], color=ORANGE, edgecolor=OEDGE, height=0.40, lw=1.1)
ax.barh([0], [9], left=[91], color=GREY, edgecolor=EDGE, height=0.40, lw=1.1)
ax.text(45.5, 0, "91%  trailed the index", ha="center", va="center",
        fontsize=11.5, fontweight="bold", color=DARK)
ax.text(95.5, 0, "9%", ha="center", va="center", fontsize=10, color=DARK)
ax.set_xlim(0, 100); ax.set_ylim(-0.5, 0.5); ax.axis("off")
ax.set_title("US large-cap active funds vs the S&P 500, fifteen years to January 2024",
             fontsize=10.5, fontweight="bold", color=DARK, pad=10)
fig.text(0.5, -0.16, "Source: S&P SPIVA scorecard.", ha="center",
         fontsize=8.6, color=MUTE)
save(fig, "ddi_active_vs_index.png")

print("\nall five figures written to assets/plots/")
