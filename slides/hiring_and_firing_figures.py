"""
Figures and numbers for slides/hiring_and_firing.tex

    python slides/hiring_and_firing_figures.py

No data: everything here is arithmetic on one fact from the backtesting slides.
An appraisal ratio measured over T years has a standard error of about
1/sqrt(T), so with a goal a* and a confidence p,

    go in      when the record is above   a* + z_p / sqrt(T)
    walk away  when the record is below   a* - z_p / sqrt(T)

Figures go to slides/figures/; the numbers the slides quote are printed at the end.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm

OUT = Path(__file__).resolve().parent / "figures"
OUT.mkdir(exist_ok=True)

GREY, RED, BLUE = "#6B6B6B", "#B03A2E", "#2E5C8A"
plt.rcParams.update({
    "font.size": 13, "axes.titlesize": 14, "axes.labelsize": 13,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": False, "figure.dpi": 150, "savefig.bbox": "tight",
})

years = np.arange(0.5, 10.01, 0.05)                 # length of the track record
z = {80: norm.ppf(0.80), 95: norm.ppf(0.95), 99: norm.ppf(0.99)}

# ---------------------------------------------------------------- 1. the walk-away line
fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)

ax = axes[0]                                        # one goal, three levels of confidence
goal = 1.0
for conf, colour in [(80, GREY), (95, RED), (99, BLUE)]:
    ax.plot(years, goal - z[conf] / np.sqrt(years), color=colour, linewidth=2, label=f"{conf}% sure")
ax.axhline(goal, color="black", linestyle=":", linewidth=1)
ax.text(10, goal + 0.06, "goal = 1", ha="right", fontsize=11)
ax.set_title("A goal of 1: how sure must you be?")
ax.set_ylabel("walk away if the record is below")

ax = axes[1]                                        # one confidence, three goals
for goal, colour in [(1.5, BLUE), (1.0, RED), (0.5, GREY)]:
    ax.plot(years, goal - z[95] / np.sqrt(years), color=colour, linewidth=2, label=f"goal {goal}")
ax.set_title("95% sure: what is your goal?")

for ax in axes:
    ax.axhline(0, color="black", linewidth=0.6)
    ax.set_xlabel("years of track record"); ax.set_ylim(-1.6, 1.6); ax.set_xlim(0, 10)
    ax.legend(frameon=False, loc="lower right")
fig.tight_layout(); fig.savefig(OUT / "walk_away.pdf"); plt.close(fig)

# ---------------------------------------------------------------- 2. the fire line depends on your process
# Two kinds of manager: good (appraisal ratio a) and unskilled (zero). `share_good` is the
# share of your hires who are good. Fire once the manager is more likely unskilled than good.
a = 1.0
fig, ax = plt.subplots(figsize=(9, 4.2))
for share_good, colour in [(0.2, GREY), (0.5, RED), (0.8, BLUE)]:
    line = a / 2 - np.log(share_good / (1 - share_good)) / (years * a)
    ax.plot(years, line, color=colour, linewidth=2, label=f"{share_good:.0%} of your hires are good")
ax.axhline(0, color="black", linewidth=0.6)
ax.set_xlabel("years since you hired them"); ax.set_ylabel("fire if the record is below")
ax.set_ylim(-1.6, 2.6); ax.set_xlim(0, 10)
ax.legend(frameon=False, loc="upper right")
fig.savefig(OUT / "fire_by_process.pdf"); plt.close(fig)

# ================================================================ the numbers the slides quote
print("WALK-AWAY LINE, goal 1")
for T in (1, 3, 5, 10):
    print(f"  {T:2d} years:  " + "   ".join(f"{c}% sure {1 - z[c] / np.sqrt(T):+.2f}" for c in z))

print("\nTWO FLAT YEARS from a manager hired to deliver 1")
T, record = 2, 0.0
odds_unskilled = np.exp(T * a * (a / 2 - record))            # how much more likely 'unskilled' is than 'good'
for share_good in (0.8, 0.5, 0.2):
    still_good = share_good / (share_good + (1 - share_good) * odds_unskilled)
    line = a / 2 - np.log(share_good / (1 - share_good)) / (T * a)
    confidence = norm.cdf((a - line) * np.sqrt(T))             # how sure you are it is below the goal, at that line
    odds_at_hire = share_good / (1 - share_good)
    print(f"  {share_good:.0%} of hires good:  odds at hire {odds_at_hire:.2f}, after {odds_at_hire / odds_unskilled:.2f};  "
          f"still good {still_good:.0%};  fire line {line:+.2f};  confidence required {confidence:.0%}")
print(f"  the flat record is {odds_unskilled:.1f} times likelier if unskilled (1/{odds_unskilled:.2f} = {1 / odds_unskilled:.2f})")

print("\nWHAT A HIRE COSTS AND PAYS. Your book alone: Sharpe 0.5. The edge lasts 5 years.")
S, lasts = 0.5, 5
for a in (1.0, 0.5):
    good, unskilled = np.sqrt(S**2 + a**2), S**2 / np.sqrt(S**2 + a**2)
    gain, loss = good - S, S - unskilled
    years_to_fire = (z[95] / a) ** 2                           # to be 95% sure an unskilled manager is below the goal
    break_even = loss * years_to_fire / (gain * lasts + loss * years_to_fire)
    print(f"  hired to deliver {a}:  good {good:.2f} (+{gain:.2f})   unskilled {unskilled:.2f} (-{loss:.2f})   "
          f"years to fire {years_to_fire:.1f}   hire if the share good exceeds {break_even:.0%}")

print("\nHIT RATE: standard error with a true 50%:  " + "   ".join(f"{n} hires {np.sqrt(0.25 / n):.0%}" for n in (10, 25, 100)))
from scipy.stats import binom
print(f"TEN HIRES from a 50% process: 3 or fewer good, or 7 or more, {2 * binom.cdf(3, 10, 0.5):.0%} of the time")
print(f"TRACK RECORD: t = ratio x sqrt(T):  1.0 over 3 years {1.0 * np.sqrt(3):.1f};  0.5 over 10 years {0.5 * np.sqrt(10):.1f}")

print("\nHOW PRECISE IS YOUR HIT RATE? Average record 0.6 with a = 1, so pi-hat = 0.6.")
print("  SE(pi-hat) = sqrt(pi (1 - pi) + 1 / (a^2 T)) / sqrt(N)")
pi_hat, a = 0.6, 1.0
print("  hires N   " + "".join(f"{T:>8}" for T in ("0.5y", "1y", "2y", "5y", "forever")))
for N in (5, 10, 20, 50, 100):
    se = [np.sqrt(pi_hat * (1 - pi_hat) + 1 / (a**2 * T)) / np.sqrt(N) for T in (0.5, 1, 2, 5)]
    se.append(np.sqrt(pi_hat * (1 - pi_hat) / N))
    print(f"  {N:>7d}   " + "".join(f"{x:8.2f}" for x in se))
