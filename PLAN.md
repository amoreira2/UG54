# UG54 — AI-Centric Redesign Plan

**Term:** Fall 2026 (NYU Stern Undergrad, M/W 3:30–4:45, 28 meetings)
**Status:** Living document — single source of truth.
**Last updated:** 2026-08-08

Previous version preserved at `PLAN_v1_backup.md`.

---

## 0. Quick state

The course is being restructured around a **cumulative group project** and a
**chapter spine borrowed from Columbia's B8420** (Daniel/Paleologo, *Quantitative
Investing*): expected returns (μ) → risk (Σ) → optimization → implementation.

Two things changed from the v1 plan:

1. **The 19 per-lecture challenges are no longer the whole assessment.** They
   remain, auto-graded, as *formative* practice. On top of them sit seven
   submission-only milestones (A1–A7) in which each group applies that block's
   technique to **their own trading strategy**, plus two in-class pitch days.
2. **The lecture order changed** so students hold a long-short portfolio by
   week 3 instead of week 9.

**Priority: get L1–L6 into excellent shape first.** The opening flow sets the
tone for the whole term and every downstream milestone depends on students
having a working panel and a working sort by meeting 4.

---

## 1. Design philosophy

### The AI-workflow shift

The job of a junior quant analyst used to be **60% writing code**. AI now
writes that code in seconds. What's left — the 40% that's actually hard — is:

| Old skill | New skill |
|-----------|-----------|
| Remember the API | **Specify** what you want precisely |
| Write the regression | **Audit** the regression for silent bugs |
| Format the output | **Interpret** the output and decide |
| Type fast | Be sharp at **judgment** |

### The three-step workflow

Every lecture, every milestone, every challenge follows:

> **Specify → Implement → Validate**

- **Specify** — student writes a precise English description (frequency, units, edge cases)
- **Implement** — AI generates the code; student runs it
- **Validate** — student uses a domain-specific pitfall checklist to audit the output

### Pitfall checklists

Each lecture includes a 5–8-item table of silent bugs AI will produce on that
topic. Students use these as a checklist on milestones.

### Two tiers of student work

| Tier | What | Graded how | Cadence |
|------|------|-----------|---------|
| **In-lecture challenge** | Scenario on the *same data for everyone*, `____` stubs + memo, paste-token | **Auto-graded** — fixed answer keys in `auto_evaluator.py` | Every lecture |
| **Milestone A1–A7** | The same technique applied to **your group's own strategy** | **Submission only** (completion) | Every ~2 weeks |

The split is what makes both tractable: the in-lecture challenge has one right
answer because everyone uses the same data, so it can be auto-graded. The
milestone has no right answer because every group's strategy differs, so it is
completion-credit and the feedback happens in the pitch days and in class.

### Tone — drop the hype

The course voice is **instructor-talking-to-students**, not marketer-pitching.

| ❌ Don't write | ✅ Write instead |
|---------------|------------------|
| "This is a $1M-a-year analyst skill" | "This is a standard equity-analysis task" |
| "Killer feature" / "This is gold" | "Useful feature" |
| "The entire business model of X" | "The logic behind X" |
| "Tape this to your monitor" | "Keep this handy" |
| "This is where you earn your salary" | "This is where the bugs hide" |
| "Internalize this" | (just delete) |

**Rule of thumb:** if a sentence sounds like a finance-bro LinkedIn post, rewrite it.

```bash
grep -nE 'a-year analyst|is gold|killer feature|tape (it|this|these)|earn your salary|gave birth|pod shops obsess|the spine of' chapters/Finance/build_*.py chapters/Finance/*runsheet.md
```

Output should be empty.

### Belt-and-suspenders data loading

Every notebook that fetches from the web gets an appendix documenting three
things: the AI prompt that generated the fetch, the live-fetch-and-save code,
and the GitHub raw-URL load. Template in §7. See
`build_statistical_factors_ai_notebook.py` for a worked example.

---

## 2. Chapter structure

Chapters group meetings into blocks with one idea each. Students should always
know which half of `Σ⁻¹μ` they are working on.

| Ch | Name | The one idea | Meetings |
|----|------|--------------|----------|
| 0–1 | **Portfolio Construction Basics** | Turn a signal into a portfolio and measure it | L1–L3 |
| 2 | **Expected Returns I — Factor Models** (μ) | Is this return skill or exposure? | L4–L6 |
| 2b | **Portfolio Decomposition** | What is this portfolio actually exposed to? | L7 |
| 3 | **Expected Returns II — Evidence** (μ) | What has worked, and how would you know? | L8–L9 |
| 4 | **Expected Returns III — Momentum & Conditional** (μ) | Signals that change over time | L10–L12 |
| 5 | **Optimization** | Sizing, and what estimation error does to it | L13–L14 |
| 6 | **Risk Models** (Σ) | You cannot measure risk as well as you think | L15, L18 |
| 7 | **Implementation** | What the backtest didn't tell you | L16–L17 |
| 8 | **Machine Learning** (μ) | Many signals at once | L19 |

Columbia session numbers are noted in the calendar as `(2A)`, `(4B)` etc. for
traceability — they are the source for the ordering, not a target to match.

---

## 3. Macro plan — Fall 2026 calendar

### Calendar facts (verified against the NYU undergraduate business bulletin)

- **First class:** Wed Sep 2 · **Last class:** Mon Dec 14
- **No class:** Mon Sep 7 (Labor Day) · **Mon Oct 12 (Fall Break)** · Nov 26–27 (Thanksgiving)
- **Wed Oct 14:** Legislative Day — classes meet on a **Monday** schedule
- **Final exam period:** Dec 16–22
- **Total meetings: 28**

Note Wed **Nov 25 is a class day** for undergrads (the Stern MBA calendar
differs — it has Nov 25–29 off. The UG bulletin governs).

### The schedule

| # | Date | Session | Due |
|---|------|---------|-----|
| 1 | Wed Sep 2 | **L1** Course intro + AI workflow + asset returns | |
| 2 | Wed Sep 9 | **L2** The panel + portfolio mathematics | *groups formed* |
| 3 | Mon Sep 14 | **L3** Sorts, breakpoints, long-short; **WRDS at the end** | *strategy chosen* |
| 4 | Wed Sep 16 | **L4** Intro to Performance Evaluation + Factor Models I `(2B)` | *A1 due Thu Sep 17* |
| 5 | Mon Sep 21 | **L5** Factor models II — types, the zoo `(3A)` | |
| 6 | Wed Sep 23 | **L6** Factor models III — multi-factor, Fama-MacBeth `(3B)` | |
| 7 | Mon Sep 28 | **L7** Portfolio decomposition — top-down / bottom-up / characteristic | *A2 was due Thu Sep 24* |
| 8 | Wed Sep 30 | **L8** Backtesting protocol `(4A)` | |
| 9 | Mon Oct 5 | **L9** Anomalies `(4B)` | *A3 due Thu Oct 8* |
| 10 | Wed Oct 7 | **Project pitches I** — 5 min × 10 groups | pitch deck |
| — | Mon Oct 12 | *Fall Break — no class* | |
| 11 | Wed Oct 14 | **Review** *(Legislative Day)* | |
| 12 | Mon Oct 19 | **MIDTERM** | |
| 13 | Wed Oct 21 | **L10** Momentum and trend following `(5A)` | |
| 14 | Mon Oct 26 | **L11** Conditional strategies I `(5B)` | *A4 was due Thu Oct 22* |
| 15 | Wed Oct 28 | **L12** Conditional strategies II — factor timing | |
| 16 | Mon Nov 2 | **L13** Capital allocation I | *A5 due Thu Nov 5* |
| 17 | Wed Nov 4 | **L14** Capital allocation II — fragility | |
| 18 | Mon Nov 9 | **Guest 1** | |
| 19 | Wed Nov 11 | **L15** BARRA / fundamental risk models `(7A)` | |
| 20 | Mon Nov 16 | **L16** Transaction costs `(7B)` | *A6 due Thu Nov 19* |
| 21 | Wed Nov 18 | **Project pitches II** — 5 min × 10 | |
| 22 | Mon Nov 23 | **L17** Leverage and shorting | |
| 23 | Wed Nov 25 | **L18** PCA / statistical factors `(6)` | |
| 24 | Mon Nov 30 | **Guest 2** | *A7 due Thu Dec 3* |
| 25 | Wed Dec 2 | **L19** Machine learning | |
| 26 | Mon Dec 7 | **Presentations I** | report + code **Fri Dec 4** |
| 27 | Wed Dec 9 | **Presentations II** | slides AM of your slot |
| 28 | Mon Dec 14 | **Review** (cumulative) | |

**19 lectures · 1 midterm · 2 reviews · 2 guests · 2 pitch days · 2 presentation days = 28.**

### Calendar reasoning

- **Midterm Mon Oct 19, review Wed Oct 14.** Fall Break creates a 6-day gap
  (Oct 8–13) — the only light week of the term — used as the study runway.
  The *review* goes on the Legislative Day, not the exam: students get confused
  about whether class meets on a Monday-schedule Wednesday, and that must not
  happen on an exam day.
- **Wed Nov 25 (day before Thanksgiving)** gets L17, the most self-contained
  session in the back half and the cheapest to miss.
- **A1–A3 land pre-midterm.** A4 ("is your signal just momentum?") now follows
  L10 and is due Mtg 14. December stays clear for the project.

### What inserting L7 cost (2026-08-08)

L7 (portfolio decomposition) was added after L6, so every lecture from the old
L7 onward shifted by one and the term needs 29 slots for 28 meetings. Two
consequences, both resolved above:

1. **Presentations go from three days to two.** 10 groups × 15 min = 150 min =
   exactly two slots. This was the cheapest slot in the term to reclaim; the
   report deadline moves from Tue Dec 1 to Fri Dec 4.
2. **Momentum moved past the midterm**, so **A4 moved from Mtg 11 to Mtg 14** —
   it cannot be due before the lecture it depends on. Guest 2 moved to Nov 30 so
   that A7 (the shorting constraint) still follows L17.
   **Wed Nov 25 keeps the most self-contained session** — now L18, PCA — for the
   same reason as before: it is the day before Thanksgiving and the cheapest
   to miss.

All cross-lecture references inside L1–L7 were renumbered to match on
2026-08-08. If this ordering changes again, they must be renumbered again — see
`chapters/Finance/L1_L7_AUDIT.md` §2a for the list.

### The course panel — what students actually run on

Built once by `chapters/Finance/build_course_panel.py`; students never touch
WRDS or Open Source Asset Pricing to do their work.

| File | Contents |
|------|----------|
| `panel_backbone_1980_2000.parquet` | 1.52M rows, 17,800 stocks, 252 months, ~6,021/month. permno, date, ret, **ret_fwd**, me, prc, exchcd, shrcd. Delisting returns merged. 15 MB. |
| `signals/<Name>.parquet` × 30 | one file per signal, **pre-signed** so high = predicted high return. 0.1–7 MB each. |
| `signal_menu.csv` | author, year, journal, description, **published t-stat** for each of the 30 |

Backbone + one signal ≈ 16 MB — comfortable in Colab, and choosing the file is
choosing the strategy.

**Why 1980–2000:** it is the discovery era for most of these anomalies, so the
machinery demos actually work — Mom12m is +19.9%/yr, t = 4.51 (published 3.74).
15 of 29 signals are correctly positive at |t| > 2, so ten groups can find
something real while half still fail. Banz's size effect is *negative* over this
window: it died the year he published it.

**Two conventions baked in, both of which are teaching material:**
- OSAP ships raw characteristics plus a `Sign` column, not pre-signed. 18 of 30
  are Sign = −1. We pre-sign on write; the original direction is in the menu.
- `ret_fwd` is the return you earn by sorting at *t*. Using `ret` instead is
  look-ahead — for STreversal that off-by-one turns t = −0.4 into **t = +70**.
  Both columns ship so L3 can show the disaster.

### WRDS

Students do not need WRDS for any graded work. It appears **at the end of L3**
as a ~15-minute segment: what CRSP and Compustat are, delisting returns, and the
actual query that produced the panel they have been using. The hands-on
querying from `WRDS_Data_Tour_AI` moves into an assignment rather than
consuming a lecture slot. Account signup starts in L1 so access exists by the
time the assignment lands.

### Cut from the plan

**LLMs / text signals.** No slot survives. `LLMs.ipynb` and `LLMs_AI.ipynb`
remain in the repo, unused. Reinstating it costs one presentation slot.

---

## 4. The project and milestones

### Structure

Each group (of ~3; 10 groups) picks **any trading strategy** and develops it all
term. Groups may change strategy during the course — each milestone is a
self-contained exercise on *whatever strategy you currently have*, not a rigid
chain. Pitch day I is the natural point to commit.

### A1–A7 — same skill, their strategy

The lecture block fixes the **skill**; the group's own strategy supplies the
**data**.

| | Due (Thu, midnight) | Last lecture it needs | The task |
|---|-----|-------|----------|
| **A1** | **Thu Sep 17** | L3 (Mon Sep 14) | Decile-sort your signal. Long-short spread, turnover, Sharpe. |
| **A2** | **Thu Sep 24** | L6 (Wed Sep 23) | Regress your long-short return on FF6. Alpha, betas, t-stat, R². Skill or exposure? |
| **A3** | **Thu Oct 8** | L9 (Mon Oct 5) | Split your sample. IS vs OOS Sharpe, how many variants you tried, a multiple-testing haircut. |
| **A4** | **Thu Oct 22** | L10 (Wed Oct 21) | Build the (12,1) benchmark. Your signal's correlation with it, and its alpha controlling for momentum. **Is your signal just momentum?** |
| **A5** | **Thu Nov 5** | L13 (Mon Nov 2) | Vol-scale your strategy; MVE combination with the market; optimal weight. |
| **A6** | **Thu Nov 19** | L16 (Mon Nov 16) | Bootstrap your Sharpe SE; apply a cost model; net-of-cost Sharpe. |
| **A7** | **Thu Dec 3** | L17 (Mon Nov 23) | Long-only vs long-short. What does the shorting constraint cost you? |

**Every assignment is due Thursday at midnight.** One weekday, all term, so
nobody has to look it up. Gaps run 1–3 days after the last lecture the
assignment needs; a Wednesday lecture means it is due the next night, which is
fine because the assignment applies a technique the lecture has just shown.

**A7 is the exception and it is worth watching.** Its Thursday is Nov 26 —
Thanksgiving — so it slips a week to **Dec 3, the day before the final report**.
Ten days after L17 rather than three, and it lands in the project crunch. Since
students drop one of seven, **A7 is the natural drop** for anyone squeezed;
that should be said out loud rather than discovered. The alternative is to cut
A7 and run six.

### Pitch days

- **Pitches I (Mtg 10, Wed Oct 7)** — 5 min × 10 groups. What's the signal, why
  might it work, what does the first sort show.
- **Pitches II (Mtg 21, Wed Nov 18)** — 5 min × 10. What survived, what broke,
  what's left to do.

These are the feedback mechanism for the project, since A1–A7 are not graded on
content. Adopt the Columbia device: cold-call one member per group to explain a
decision — *why this approach, what alternatives did you consider, why did you
reject them.*

### Final deliverables

- Report + code: **Fri Dec 4** (before Presentations I)
- Slides: morning of your presentation slot
- Presentations: Dec 7, 9 — ~15 min per group, 5 groups per day

---

## 4b. Lecture length — calibrated, not guessed

Estimated from the **realized Spring 2026 allocations** on seven comparable
topics (Timing 2, Factor Models 2, Capital Allocation 2, Estimation 3,
Cross-Sectional 2, Momentum 1, Multifactor 1 — ML and LLMs excluded as
atypical), counting **markdown words in lectured sections only**; exercises,
challenges, submission cells and appendices are homework and don't count.

> **≈ 1,400 lectured words = one 75-minute session.**
> Observed range 685–2,208; CV 0.34. Low end = foundational material you go
> slowly on; high end = survey material.

Things that do **not** predict lecture time in the historical data: code lines
(zero explanatory power — Momentum ran a lecture on 69 lines, Multifactor on
238), cells, equations. A composite search over `words + a·code + b·eqs`
returns a ≈ 0. Word count alone is the metric.

**Adjust down for the AI format.** Hands-On blocks are student working time, not
instructor content, so a 75-minute slot with one Hands-On carries roughly
**1,200–1,300 lectured words**. Flag anything above 1,600.

⚠️ n = 7, and the original allocations were set topically rather than from word
counts. This is a tripwire, not a measurement. Recalibrate after teaching L1.

---

## 5. Lecture micro-structure (the standard 75-min arc)

| Phase | Time | What happens |
|-------|------|--------------|
| **Cold open** | 3 min | Memorable hook — real scenario, anecdote, provocative question |
| **Motivate** | 10–15 min | Real-world context, the key concept, the "why" |
| **Pitfall checklist** | 5 min | Project the lecture-specific checklist of silent AI bugs |
| **Live AI Moment 1** | 10–12 min | Project a Specify cell; paste into Gemini live; class audits |
| **Concept** | 5–10 min | Conceptual content with minimal code |
| **Hands-On / Live AI 2** | 10–12 min | Students discover a result themselves, or a second audit cycle |
| **More concepts** | 5–10 min | Wrap up theory |
| **Challenge** | 15–20 min | Scenario-based; pairs; cold-call wrap |
| **Wrap** | 3–5 min | 2–3 takeaways, preview, milestone reminder |

**Hands-On blocks** are the interactive core: students find the result *before*
it is explained. `StatisticalFactors_AI.ipynb` has three worked examples of the
pattern (§7).

---

## 6. Notebook anatomy (standard cell order)

```
1.  Title + 🎯 Learning Objectives (5-6 bullets, including the AI-audit objective)
2.  📋 Table of Contents
3.  🛠️ Setup section (collapsible #@title cells)
4.  Section 1 (Motivate) — markdown intro + data load + key insight callout
5.  🛡️ Pitfall checklist (5-8 item table specific to this lecture)
6.  🔄 Live Demo: Specify → Implement → Validate
7.  🛠️ Hands-On block — student discovers a result
8.  Conceptual sections (equations, tables, key insights, cautions)
9.  Second Live Demo or Hands-On
10. 🎯 Challenge with variable stubs (var = ____) + MEMO
11. 📤 Submission cell (paste-token pattern)
12. 🧠 Key Takeaways (6-9 numbered items)
13. 📎 APPENDIX — belt-and-suspenders data loading
```

### Variable stub pattern

```python
# Your work here (scratch space)


# Required outputs — fill these in:
fund_a_total_return = ____

print(f"Fund A: {fund_a_total_return:.1%}")
```

`____` raises `NameError` if left unfilled. Variable names MUST match the
submission cell.

### Hands-On pattern

```
## 🛠️ Hands-On N: <imperative title> <a id="hoN"></a>
### Your task            — what to build, in one paragraph
> **🤔 Predict first.**  — commit to a guess before running
# === YOUR TURN ===      — code cell with 1-2 ____ stubs
### What did you find?   — the reveal, then the theory that explains it
```

### Callout vocabulary

| Type | Format |
|------|--------|
| Key insight | `> **💡 Key Insight**` |
| Caution / pitfall | `> **⚠️ Caution:**` |
| Remember | `> **📌 Remember**` |
| Predict / think | `> **🤔 ...**` |
| Python insight | `> **🐍 Python Insight:** \`function()\`` |
| AI-era insight | `> **🤖 AI-Era Insight**` |
| Specification | `> **📝 Spec**` |
| AI prompt | `> **🤖 AI prompt:** *"..."*` |

---

## 7. File conventions

| Type | Pattern | Example |
|------|---------|---------|
| Lecture notebook | `<TopicName>_AI.ipynb` | `StatisticalFactors_AI.ipynb` |
| Build script | `build_<topic>_ai_notebook.py` | `build_statistical_factors_ai_notebook.py` |
| Run sheet | `<TopicName>_AI_runsheet.md` | `FactorModels_c_AI_runsheet.md` |
| Challenge data | `assets/data/<topic>_AI_challenge.csv` | |

Each notebook is generated by a Python script defining `cells = []` with `md()`
and `code()` helpers. Keeps source in version-controllable Python and avoids
notebook merge conflicts.

### Belt-and-suspenders appendix template

````python
# ═══════════════════════════════════════════════════════════════════════
# 📎 APPENDIX — Belt-and-Suspenders Data Loading
# ═══════════════════════════════════════════════════════════════════════
# ─── 1. AI prompt that generated the data-pull code ────────────────────
# Prompt: "..."

# ─── 2. Live fetch + save (run once, then commit the CSV) ──────────────
def fetch_and_save_x():
    ...
    df.to_csv('assets/data/x.csv')
    return df
# Uncomment to re-fetch live:
# fetch_and_save_x()

# ─── 3. Load from GitHub raw URL (reliable backup path) ────────────────
url_backup = ('https://raw.githubusercontent.com/amoreira2/UG54/'
              'refs/heads/main/assets/data/x.csv')
x_backup = pd.read_csv(url_backup, index_col=0, parse_dates=True)
````

---

## 8. Smoke test (run after every build)

See `scratchpad/smoke_statfactors.py` for a full worked example. The pattern:

1. Read the notebook with `nbformat`.
2. **Fill in Hands-On stubs with the intended solutions** — downstream cells
   depend on them, so skipping breaks execution. This also verifies the intended
   solution actually works.
3. Fill or skip the Challenge stubs and the submission cell.
4. Patch GitHub raw URLs to local paths so the appendix runs pre-push.
5. Execute with `ExecutePreprocessor(timeout=900)`.
6. Print key outputs and eyeball them for pedagogical sense — *numbers that run
   are not the same as numbers that teach.*

⚠️ Watch for substring collisions when replacing stubs (`noise = ____` is a
substring of `C_noise = ____`).

---

## 9. Workflow for adding/rebuilding a lecture

1. **Audit the source notebook(s)** — list topics, equations, takeaways. Mark CORE vs ASIDE.
2. **Identify the core narrative** — the ONE thing students should remember.
3. **Identify the challenge** — a scenario forcing application of the core, on data everyone shares.
4. **Identify 1–3 Hands-On discoveries** — results students can find before being told.
5. **Write the build script** following §6.
6. **Write the answer key + memo rubric** in `auto_evaluator.py` (in-lecture challenge only).
7. **Round-trip test** — simulate a good student and a wrong-in-a-specific-way student through the grader.
8. **Smoke test** (§8), and read the outputs for teaching quality.
9. **Re-audit against the original** — what's missing? CORE (add) or ASIDE (skip)? Document the choice.
10. **Write the run sheet** with timing and AI prompts.
11. **Update this plan** — flip the status row.

---

## 10. Status by lecture

**Legend:** ✅ built to standard · 🟡 strong source material, needs rebuild ·
🔴 thin or missing · ⬛ non-teaching slot

| L | Topic | Source assets | Status |
|---|-------|---------------|--------|
| L1 | Intro + AI workflow + returns | `CourseIntro_AI` ✅ · `IntrotoReturns_c_AI` ✅ | 🟡 merge two builts |
| L2 | WRDS panel + portfolio math | `WRDS_Data_Tour_AI` ✅ · `PortfolioMath_c` | 🟡 merge + condense |
| L3 | Sorts, breakpoints, ratios | `crosssectional` · `FactorModels_c_AI` ✅ | 🟡 **needs NYSE breakpoints (new)** |
| L4 | **Intro to Performance Eval** + Factor models I | `FactorModels_c_AI` ✅ + Sharpe/IR moved from L3 | 🟡 merge |
| L5 | Factor models II — types, zoo | `Factors.ipynb` · `MultiFactorModels_c` | 🟡 |
| L6 | Factor models III — estimation | `FactorModels_II_AI` ✅ · `FactorModelEstimation_c` | 🟡 **needs Fama-MacBeth (new)** |
| L7 | Backtesting protocol | `Performance_evaluation_c` | 🔴 **messy; overfitting demo built on MVE, must repackage** |
| L8 | Anomalies | `Factors.ipynb` | 🔴 **design unresolved — tour or depth?** |
| L9 | Momentum and trend | `Momentum.ipynb` | 🟡 strong bones |
| L10 | Conditional strategies I | `MarketTiming_c` · `Timing_AI` ✅ | 🟡 strong bones |
| L11 | Conditional strategies II | `Volatilitytiming_c` · `Timing_AI` ✅ | 🟡 **generalize to factor timing** |
| L12 | Capital allocation I | `CapitalAllocationI_AI` ✅ | 🟡 **make the math intuitive** |
| L13 | Capital allocation II — fragility | `CapitalAllocationII` · `L16_L17_AlphaCapture_joint_design.md` | 🟡 **the core; design doc awaiting sign-off** |
| L14 | BARRA / fundamental risk models | `RiskManagement` (covariance half) | 🔴 **never taught; needs anatomy, winsorization, specific risk, bias tests** |
| L15 | Transaction costs | `TradingCosts` | 🔴 **never taught** |
| L16 | Leverage and shorting | `LeverageandShorting` | 🔴 **never taught** |
| L17 | PCA / statistical factors | **`StatisticalFactors_AI`** ✅ | ✅ **built + smoke-tested 2026-08-06** |
| L18 | Machine learning | `MachineLearning_cc` | 🟡 |
| ⬛ | Midterm, reviews ×2, guests ×2, pitches ×2, presentations ×3 | | 🔴 all to design |

### Superseded

The fast-batch AI drafts (`CrossSectional_I/II_AI`, `Momentum_AI`,
`PerformanceEval_AI`, `CapitalAllocationII_AI`, `MultiFactorModels_AI`,
`RiskManagement_AI`, `Implementation_AI`, `ML_I/II_AI`, `LLMs_AI`) are 9–11KB
skeletons whose challenges grade arithmetic on numbers the notebook hands the
student. **Rebuild from the old rich notebooks, not from these.** Their
`auto_evaluator.py` entries will need replacing along with them.

### Infrastructure

- ✅ `auto_evaluator.py` — 20 assignments wired (19 + StatisticalFactors_AI)
- ✅ `auto_evaluator_form.py` — Form-based grader runner
- ⏳ **Service account + Google Form — not set up.** See §12.
- ⏳ `https://forms.gle/YOUR_FORM_LINK_HERE` placeholder in 7 notebooks;
  `WhatIsAlpha_AI` has a submission cell with **no** form link at all
- ⚠️ `AUTO_EVAL_DESIGN.md` documents a **superseded** architecture (Drive upload
  + notebook execution). The live system is paste-token + Form. Do not follow it.

---

## 11. What's left, in priority order

### Block A — L1–L6, the opening flow (highest priority)

Getting the first six meetings excellent sets the tone and gates every
milestone. Five of six run on already-built notebooks; the work is merging,
condensing, and two genuinely new pieces.

- [ ] **L1** — merge `CourseIntro_AI` + `IntrotoReturns_c_AI`; fix the syllabus cells (they still describe the v1 assessment)
- [ ] **L2** — condense `WRDS_Data_Tour_AI` to what the project needs; add portfolio math from `PortfolioMath_c`
- [ ] **L3** — sorts on **size** as the vehicle; **write the NYSE-breakpoint function** (current code is `pd.qcut` over all stocks → microcap-dominated extreme deciles); add z-scoring and the information ratio
- [ ] **L4** — light edit of `FactorModels_c_AI`
- [ ] **L5** — factor types + the zoo from `Factors.ipynb`
- [ ] **L6** — `FactorModels_II_AI` + **new Fama-MacBeth section**
- [ ] **A1 spec** — due meeting 4, gates everything downstream

### Block B — L7–L8, the evidence block

- [ ] **L7** rebuild. `Performance_evaluation_c` is 2.5MB and messy. The
      overfitting demo is built on MVE (25 references) which is now *post*-midterm
      — repackage it around signal selection instead. Same lesson, and it runs on
      the object students already hold.
- [ ] **L8 design decision** — the existing anomaly material is a tour and it's
      boring. Options: (a) a deeper dive on 2–3 anomalies with the original
      papers, (b) a replication exercise against Open Source Asset Pricing,
      (c) organize around *why* they might work rather than a catalogue.
      **Decide before building.**

### Block C — L10–L13, the core

- [ ] **L10–L11** — `MarketTiming_c` + `Volatilitytiming_c`. Generalize from
      market timing to **factor timing**. Include the *single-asset*
      `w* = μ/(γσ²)` here as motivation (one line, no matrices) since capital
      allocation is now downstream.
- [ ] **L12–L13** — sign off `L16_L17_AlphaCapture_joint_design.md`, then build.
      L13 (estimation-error fragility) is the intellectual core of the back half.
      Students complain about the math — the fix is that it now arrives at
      meeting 15–16, after they've built something to apply it to.
      ⚠️ The design doc names answer keys `PerfEval_AI` / `CapAllocII_AI`; the
      grader uses `PerformanceEval_AI` / `CapitalAllocationII_AI`.

### Block D — L14–L16, the untaught block

~780KB of source material, none of it ever taught. Highest build risk.

- [ ] **L14 BARRA** — `XFX' + Δ`; exposures observed / factor returns estimated;
      industries are most of the model and exist for variance not premium;
      winsorization and standardization; specific risk as its own pooled
      cross-sectional model; bias tests; the risk report as a deliverable
- [ ] **L15** — transaction costs, market impact, half-lives
- [ ] **L16** — leverage, shorting, constraints

### Block E — L17–L18

- [x] **L17** — `StatisticalFactors_AI` built and smoke-tested
- [ ] **L18** — condense `MachineLearning_cc` to one session

### Block F — Assessment and infrastructure

- [ ] Midterm (covers L1–L9) + cumulative final
- [ ] Run sheets for every rebuilt lecture
- [ ] Service account + Google Form; replace the placeholder URL; add a form
      link to `WhatIsAlpha_AI`
- [ ] Fix `auto_evaluator_form.py`: header built from `rows[0].keys()` silently
      drops per-question columns for everyone if the first submission fails to
      decode; `grades_ws.clear()` re-grades and re-bills every row on every run;
      `GRADE_MEMO_TOOL` requires `picked_fund` on every assignment
- [ ] Guest lecture coordination (Mtg 17, Mtg 22)
- [ ] **Commit everything.** Last commit is 2026-04-20; the entire redesign is untracked.

---

## 12. Open questions

- **L8 anomalies** — tour, deep dive, or replication exercise? (Blocks Block B.)
- **Group formation logistics** — groups by meeting 2, strategy by meeting 3.
  How are groups formed, and how do you avoid ten momentum strategies?
- **Strategy changes** — groups may switch. Should a switch after Pitches I be
  declared, or is it free all term?
- **Midterm scope** — L1–L9 is μ-only (no Σ, no optimization). Confirm that's
  the intended scope.
- **WRDS access timing** — students need it by meeting 2 (Sep 9). Start signup
  in meeting 1?
- **Presentation length** — 3 slots / 10 groups ≈ 22 min each. Right?

---

## 13. Quick-start for the next session

1. Read this file.
2. Read `chapters/Finance/StatisticalFactors_AI.ipynb` — the most recent build,
   and the best example of the Hands-On discovery pattern.
3. Read `build_statistical_factors_ai_notebook.py` for the build-script idiom.
4. Pick the next item from §11 Block A.
5. Follow §9, end with §8.

**Key files to have open:** this file · `build_statistical_factors_ai_notebook.py`
· `auto_evaluator.py` · `QI_Syllabus_FA2026.v2.pdf` (the Columbia syllabus, for
ordering reference)

---

**End of plan. Update every time a lecture is finished or a convention changes.**
