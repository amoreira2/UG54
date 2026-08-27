# UG54 — AI-Centric Redesign Plan

**Term:** Fall 2026 (NYU Stern Undergrad, M/W, two 75-min sessions per week)
**Status:** Living document — single source of truth.
**Last updated:** 2026-05-26

---

## 0. Quick state

We're rebuilding UG54 around AI-assisted learning. Half the lectures are built
to a high standard (rebuilt from scratch with care); half were drafted in a
fast batch and need a rebuild pass. The grading infrastructure (paste-token
submission + Google Form + Claude-graded memos) is fully designed and the
grader runs. The macro schedule fits Fall 2026's 28 M/W lecture slots.

**What's done well (ready to teach):**
Course Intro · Asset Returns · WRDS Data Tour · Factor Models I · Factor
Models II · Portfolios · Capital Allocation I · Timing (2 sessions) · What Is
Alpha? (NEW — 1970 challenge)

**What's drafted but needs proper rebuild:**
Cross-Sectional Strategies I & II · Momentum · Performance Evaluation ·
Capital Allocation II · Multi-Factor Models · Risk Management · Implementation
(NEW) · Machine Learning I & II · LLMs in Finance

**What still needs to be created from scratch:**
Run sheets for Lectures 6-23 (instructor cheat sheets) · Midterm + Final
materials · Guest-lecture coordination · Project assignment specification

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

Every lecture, every assignment, every challenge follows:

> **Specify → Implement → Validate**

- **Specify** — student writes a precise English description (frequency, units, edge cases)
- **Implement** — AI generates the code; student runs it
- **Validate** — student uses a domain-specific pitfall checklist to audit the output

### Pitfall checklists

Each lecture includes a 5-8-item table of silent bugs AI will produce on that
topic. Students use these as a checklist on assignments. Pitfalls are the
syllabus expressed as falsifiable claims.

### Scenario-based challenges

Each lecture ends with a single scenario challenge that forces students to
apply the lecture's concepts to a small dataset and write a one-paragraph
memo. The challenge is the assessment.

### Tone — drop the hype

The course voice is **instructor-talking-to-students**, not marketer-pitching.
Salesy phrases are out. State the fact, drop the puffery.

| ❌ Don't write | ✅ Write instead |
|---------------|------------------|
| "This is a $1M-a-year analyst skill" | "This is a standard equity-analysis task" |
| "Killer feature" / "This is gold" | "Useful feature" |
| "The entire business model of X" | "The logic behind X" |
| "Tape this to your monitor" | "Keep this handy" |
| "They are the syllabus" | (just delete — overstated) |
| "This is where you earn your salary" | "This is where the bugs hide" |
| "The single most valuable thing you'll leave this course with" | "The habit we'll practice all semester" |
| "Internalize this" | (just delete) |
| "Pod shops obsess about Sharpe" | "High-Sharpe strategies are prized because..." |
| "Gave birth to a $2T industry" | "Underlies a large industry — Fama-French factor funds" |

**Rule of thumb:** if a sentence sounds like a finance-bro LinkedIn post, rewrite it.

Grep check before finalizing any notebook or run sheet:

```bash
grep -nE 'a-year analyst|is gold|killer feature|tape (it|this|these)|earn your salary|memorable number|gave birth|pod shops obsess|the spine of|the entire (industry|course|business)' chapters/Finance/build_*.py chapters/Finance/*runsheet.md
```

Output should be empty.

### 🆕 Belt-and-Suspenders Data Loading (NEW — apply to every notebook)

**Principle:** every notebook that fetches data from the web should have an
appendix cell that documents three things:

1. **The AI prompt** that generated the fetch code (as a comment)
2. **The live-fetch + save code** that pulls from the source and writes a CSV
3. **The GitHub raw-URL load code** that reads the CSV back

This is a fallback path. The main body of the notebook can use whichever it
prefers (typically the live fetch), but the appendix guarantees there's always
a working path if the live source breaks. The appendix lives at the very end
of the notebook so it doesn't interfere with the lecture flow.

**Template** (insert at the bottom of any notebook with web data):

````python
# ═══════════════════════════════════════════════════════════════════════
# 📎 APPENDIX — Belt-and-Suspenders Data Loading
# ═══════════════════════════════════════════════════════════════════════
# The main body of this notebook fetches data live from <SOURCE>.
# This appendix documents the alternate path: pull once, save to the repo,
# load from a GitHub raw URL. Use as a fallback if the live source breaks.

# ─── 1. AI prompt that generated the data-pull code ────────────────────
# Prompt: "Using pandas-datareader, fetch the FRED series T10Y3M (10Y - 3M
#  Treasury spread) starting 1982. Resample to month-end. Convert from
#  percent to decimal. Save to assets/data/term_spread_monthly.csv."

# ─── 2. Live fetch + save (run once, then commit the CSV) ──────────────
def fetch_and_save_term_spread():
    from pandas_datareader.data import DataReader
    ts = DataReader('T10Y3M', 'fred', start='1982-01-01')
    ts_monthly = ts.resample('ME').last() / 100
    ts_monthly.columns = ['term_spread']
    ts_monthly.to_csv('assets/data/term_spread_monthly.csv')
    return ts_monthly

# Uncomment to re-fetch live (overwrites local CSV; then commit to repo):
# fetch_and_save_term_spread()

# ─── 3. Load from GitHub raw URL (reliable backup path) ────────────────
url_backup = ('https://raw.githubusercontent.com/amoreira2/UG54/'
              'refs/heads/main/assets/data/term_spread_monthly.csv')
ts_backup = pd.read_csv(url_backup, parse_dates=['DATE'], index_col='DATE')
print(f"Backup loaded: {len(ts_backup)} rows, "
      f"{ts_backup.index.min().date()} to {ts_backup.index.max().date()}")
````

**TODO**: retrofit this appendix into all already-built notebooks that pull
data from the web. See §11 for the full retrofit list.

---

## 2. Macro Plan — Fall 2026 (28 lectures)

### Calendar context (NYU Stern Undergrad, M/W)

- **First class:** Wed Sep 2
- **No-class days:** Mon Sep 7 (Labor Day) · Mon Oct 12 (Indigenous Peoples Day) · Thu Nov 26 + Fri Nov 27 (Thanksgiving)
- **Wed Oct 14:** classes meet on a Monday schedule (Fall Legislative Day) — for an M/W course this is a regular class day
- **Last class:** Mon Dec 14
- **Final exam window:** Tue Dec 15 – Tue Dec 22
- **Total lecture slots:** 28

| Wk | Lec | Date | Day | Topic | Status |
|----|-----|------|-----|-------|--------|
| 1 | 1 | Sep 2 | W | Course Intro + AI Workflow | ✅ Built |
| 2 | 2 | Sep 9 | W | Asset Returns | ✅ Built |
| 3 | 3 | Sep 14 | M | WRDS Data Tour (live queries) | ✅ Built |
| 3 | 4 | Sep 16 | W | Factor Models I — Concepts | ✅ Built |
| 4 | 5 | Sep 21 | M | Factor Models II — Estimation | ✅ Built |
| 4 | 6 | Sep 23 | W | Portfolios | ✅ Built |
| 5 | 7 | Sep 28 | M | Capital Allocation I | ✅ Built |
| 5 | 8 | Sep 30 | W | Timing — Part I (Market Timing) | ✅ Built |
| 6 | 9 | Oct 5 | M | Timing — Part II (Vol Timing) + Final Challenge | ✅ Built |
| 6 | 10 | Oct 7 | W | **What Is Alpha? — 1970 Challenge** (NEW) | ✅ Built |
| 7 | 11 | Oct 14 | W* | **Midterm** | ⏳ Needs problems + key |
| 8 | 12 | Oct 19 | M | **Guest Lecture 1** | ⏳ Coord |
| 8 | 13 | Oct 21 | W | Cross-Sectional Strategies I | ⚠️ Draft — needs rebuild |
| 9 | 14 | Oct 26 | M | Cross-Sectional Strategies II | ⚠️ Draft |
| 9 | 15 | Oct 28 | W | Momentum | ⚠️ Draft |
| 10 | 16 | Nov 2 | M | Performance Evaluation | ⚠️ Draft |
| 10 | 17 | Nov 4 | W | Capital Allocation II | ⚠️ Draft |
| 11 | 18 | Nov 9 | M | Multi-Factor Models | ⚠️ Draft |
| 11 | 19 | Nov 11 | W | Risk Management (incl. variance forecasting) | ⚠️ Draft |
| 12 | 20 | Nov 16 | M | **Implementation** (trading costs, leverage, shorting) — NEW | ⚠️ Draft |
| 12 | 21 | Nov 18 | W | Machine Learning I — Penalized Regression | ⚠️ Draft |
| 13 | 22 | Nov 23 | M | Machine Learning II — Trees & Boosting | ⚠️ Draft |
| 13 | 23 | Nov 25 | W | LLMs in Finance (heads up: day before Thanksgiving) | ⚠️ Draft |
| 14 | 24 | Nov 30 | M | **Guest Lecture 2** | ⏳ Coord |
| 14 | 25 | Dec 2 | W | Project work session | ⏳ Design |
| 15 | 26 | Dec 7 | M | **Presentations 1** | ⏳ Logistics |
| 15 | 27 | Dec 9 | W | **Presentations 2** | ⏳ Logistics |
| 16 | 28 | Dec 14 | M | **Final Review** (cumulative) | ⏳ Design |

`W*` = Wed Oct 14 meets on a Monday schedule (Fall Legislative Day).

**Calendar notes:**
- No spring break in Fall — post-midterm runs Oct 21 → Dec 14 continuously.
- **Heads up: Wed Nov 25** is the day before Thanksgiving (UG calendar treats it as a class day — only Thu/Fri off). LLMs lands there. Students may travel early. Consider swapping with Guest Lecture 2 on Nov 30 if attendance is a concern.

---

## 3. Lecture micro-structure (the standard 75-min arc)

| Phase | Time | What happens |
|-------|------|--------------|
| **Cold open** | 3 min | Memorable hook — real scenario, anecdote, or provocative question |
| **Motivate** | 10-15 min | Real-world context, key concept, the "why" — mostly talking |
| **Pitfall checklist** | 5 min | Project the lecture-specific checklist of silent AI bugs |
| **Live AI Moment 1** | 10-12 min | Project a Specify cell; paste the prompt into Gemini live; class audits the output |
| **Concept** | 5-10 min | Conceptual content with minimal code |
| **Live AI Moment 2** | 10-12 min | Second prompt-and-audit cycle for a different concept |
| **More concepts** | 5-10 min | Wrap up theoretical content |
| **Challenge** | 15-20 min | Scenario-based; students work in pairs; cold-call wrap |
| **Wrap** | 3-5 min | Key takeaways (pick 2-3), preview next class, assignment reminder |

Total: ~73-78 min. Tight but doable in a 75-min slot.

---

## 4. Notebook anatomy (standard cell order)

```
1.  Title + 🎯 Learning Objectives (5-6 bullets, including the AI-audit objective)
2.  📋 Table of Contents
3.  🛠️ Setup section (collapsible #@title cells)
4.  Helper functions (if needed)
5.  Section 1 (Motivate) — markdown intro + data load + key insight callout
6.  🛡️ Pitfall checklist (6-8 item table specific to this lecture's topic)
7.  Specify → Implement → Validate live demo #1
8.  Conceptual sections (equations, tables, key insights, cautions)
9.  Live Demo #2
10. More concepts
11. 🎯 Challenge with variable stubs (var = ____) + MEMO
12. 📤 Submission cell (paste-token pattern)
13. 🧠 Key Takeaways (6-9 numbered items)
14. 📎 APPENDIX — belt-and-suspenders data loading (NEW)
```

### Variable stub pattern (challenge cells)

```python
# Your work here (scratch space)


# Required outputs — fill these in:
fund_a_total_return = ____
fund_b_total_return = ____

print(f"Fund A: {fund_a_total_return:.1%}")
print(f"Fund B: {fund_b_total_return:.1%}")
```

- `____` raises `NameError` if left unfilled (immediate feedback)
- Print statement on next line for visual sanity check
- Variable names MUST match what the submission cell expects

### Callout vocabulary

| Type | Format | When to use |
|------|--------|-------------|
| Key insight | `> **💡 Key Insight:**` | Critical concept to remember |
| Caution / pitfall | `> **⚠️ Caution:**` | Common mistakes |
| Remember | `> **📌 Remember:**` | Must-know facts |
| Think & code | `> **🤔 Think and Code:**` | Conceptual question + small task |
| Exercise | `> **🔧 Exercise:**` | Hands-on task |
| Python insight | `> **🐍 Python Insight:** \`function()\`` | New pandas/numpy function (first time used) |
| AI-era insight | `> **🤖 AI-Era Insight**` | How AI changes this particular task |
| Specification | `> **📝 Spec**` | A precise English description |
| AI prompt | `> **🤖 AI prompt:** *"..."*` | What to paste into Gemini |

---

## 5. Submission system

### Paste-token flow

Students never upload files. Every submission goes through:

1. Notebook has a final cell that bundles answers into a base64-encoded JSON token (~500-1400 chars)
2. Student pastes the token into a Google Form (NYU SSO captures email)
3. Form auto-appends to a Google Sheet
4. Instructor runs `chapters/Finance/auto_evaluator_form.py`:
   - Reads new rows from the Sheet
   - Decodes each token (checksum validates)
   - Grades numeric values (direct comparison, self-consistency, or range-based)
   - Sends memo to Claude with assignment-specific rubric
   - Writes a grades tab in the same Sheet

### Submission cell template

```python
# === 📤 SUBMISSION CELL ===
import json, base64, hashlib, datetime as dt

required = [
    "var1", "var2", "var3",  # ← your numeric outputs
    "MEMO",
]
missing = [v for v in required if v not in dir()]
if missing:
    raise NameError(f"❌ Missing: {missing}")

payload = {
    "assignment": "AssignmentName_AI",  # ← MUST match ANSWER_KEY key in auto_evaluator.py
    "ts": dt.datetime.utcnow().isoformat(timespec="seconds") + "Z",
    "answers": {k: float(eval(k)) for k in required if k != "MEMO"},
    "memo": MEMO.strip(),
}
blob = json.dumps(payload, sort_keys=True)
checksum = hashlib.sha256(blob.encode()).hexdigest()[:8]
token = f"UG54::{checksum}::{base64.b64encode(blob.encode()).decode()}"

print("=" * 72)
print("📋  COPY THE LINE BELOW AND PASTE INTO THE SUBMISSION FORM")
print("=" * 72)
print(token)
print("=" * 72)
print(f"\nLength: {len(token)} chars")
print("Submission form: https://forms.gle/YOUR_FORM_LINK_HERE")
```

### Three grading patterns (all in `chapters/Finance/auto_evaluator.py`)

**Pattern A — Fixed numeric (most common):**
```python
ANSWER_KEY["AssignmentName_AI"] = {
    "var1": (expected_value, tolerance_fraction),  # e.g., (0.044, 0.30)
}
```
- Tolerance is fractional (0.30 = within 30%)
- For near-zero values, use `truth=0` and `tolerance` = absolute bound

**Pattern B — Self-consistency (open-ended choice, like WRDS Tour):**
```python
ANSWER_KEY["AssignmentName_AI"] = "_dynamic_"
```
- Add a `grade_<assignment>()` function that loads source data and verifies

**Pattern C — Memo only:** skip the numeric dict, weight rests on memo grade.

### Memo rubric template

In `MEMO_RUBRICS` dict:

```python
"AssignmentName_AI": """
You are grading a junior analyst's memo recommending [decision].

GROUND TRUTH: ...

Grade 0-5:
  5 = [best response criteria]
  ...
  0 = Empty / off-topic.

For picked_fund return "A" or "B". For cited_X return True/False.

Output via the `grade_memo` tool.
""",
```

---

## 6. File conventions

| Type | Pattern | Example |
|------|---------|---------|
| Lecture notebook | `<TopicName>_AI.ipynb` | `FactorModels_c_AI.ipynb` |
| Build script | `build_<topic>_ai_notebook.py` | `build_factor_models_ai_notebook.py` |
| Run sheet | `<TopicName>_AI_runsheet.md` | `FactorModels_c_AI_runsheet.md` |
| Challenge data builder | `build_<topic>_challenge_data.py` | `build_factor_challenge_data.py` |
| Challenge data CSV | `<topic>_AI_challenge.csv` (in `assets/data/`) | `FactorModels_AI_challenge.csv` |

### Where things live

```
UG54/
├── PLAN.md                                  ← this file (canonical plan)
├── chapters/Finance/
│   ├── build_<topic>_ai_notebook.py         (build script per lecture)
│   ├── build_<topic>_challenge_data.py      (data prep, if needed)
│   ├── <TopicName>_AI.ipynb                 (the lecture notebook)
│   ├── <TopicName>_AI_runsheet.md           (the run sheet)
│   ├── auto_evaluator.py                    (shared grader)
│   ├── auto_evaluator_form.py               (Form-based grader runner)
│   ├── AUTO_EVAL_DESIGN.md                  (design doc for grading)
│   └── COURSE_REDESIGN_PLAN.md              (legacy — superseded by this PLAN.md)
└── assets/data/
    ├── <topic>_AI_challenge.csv             (challenge data per lecture)
    └── ... (existing finance CSVs reused as-is)
```

### Build script pattern

Each notebook is generated by a Python script that defines `cells = []`,
appends markdown and code cells via helper functions, and writes the JSON.
This makes notebooks reproducible and editable as code.

```python
def md(text): return {"cell_type": "markdown", "metadata": {}, "source": text.splitlines(keepends=True)}
def code(text): return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": text.splitlines(keepends=True)}

cells = []
cells.append(md("# Title\n## Learning Objectives\n..."))
cells.append(code("import numpy as np\n..."))
# ... build out all cells ...
notebook = {"cells": cells, "metadata": {...}, "nbformat": 4, "nbformat_minor": 5}
OUT.write_text(json.dumps(notebook, indent=1))
```

Why this pattern: lets you edit programmatically, keeps source in
version-controllable Python, avoids notebook-merge conflicts.

---

## 7. Smoke-test pattern (run after every build)

```python
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from pathlib import Path

nb = nbformat.read("path/to/<Lecture>_AI.ipynb", as_version=4)

# Patch GitHub URLs to local paths so it works pre-push (optional)
url_map = {"https://raw.githubusercontent.com/.../foo.csv":
           str(Path("assets/data/foo.csv").resolve())}
for cell in nb.cells:
    if cell.cell_type == "code":
        src = "".join(cell.source) if isinstance(cell.source, list) else cell.source
        for orig, local in url_map.items():
            src = src.replace(orig, local)
        cell.source = src

# Skip student cells (anything with ____ or MEMO = "" or SUBMISSION CELL)
for i, cell in enumerate(nb.cells):
    if cell.cell_type == "code":
        src = "".join(cell.source) if isinstance(cell.source, list) else cell.source
        if "____" in src or "MEMO = " in src or "SUBMISSION CELL" in src:
            nb.cells[i].source = "pass  # student cell — skipped"

ep = ExecutePreprocessor(timeout=300, kernel_name="python3")
ep.preprocess(nb, {"metadata": {"path": "chapters/Finance"}})
print(f"✅ Executes cleanly ({len(nb.cells)} cells)")
```

End every build session with this. If it doesn't pass, fix before moving on.

---

## 8. Workflow for adding a new lecture

When picking up a new lecture, follow in order:

1. **Audit the original notebook(s)** — read what's there; list topics, equations, key takeaways. Identify CORE vs ASIDE.
2. **Identify the lecture's core narrative** — what's the ONE thing students should remember?
3. **Identify the challenge** — what's a scenario that forces application of the core?
4. **Design the dataset** if the challenge needs synthetic or pre-pulled data.
5. **Write the build script** following the standard notebook anatomy (§4).
6. **Write the answer key + memo rubric** in `auto_evaluator.py`.
7. **Round-trip test** — simulate a good student and a bad student through the grader.
8. **Build the run sheet** with timing and AI prompts.
9. **End-to-end smoke test** (§7).
10. **Re-audit against the original** — what's missing? Is it CORE (add) or ASIDE (skip)? Document the choice.
11. **Add the belt-and-suspenders APPENDIX** (§1) if the notebook fetches web data.
12. **Update this plan** — flip the lecture's row from ⏳/⚠️ to ✅.

---

## 9. Key decisions made (audit trail)

- **Specify → Implement → Validate** as the unifying workflow.
- **Pitfall checklists per lecture** instead of generic "be careful."
- **Single scenario-based challenge** at end of each lecture (not multiple exercises).
- **Paste-token submission** (not file upload) — see §5.
- **Variable-stub pattern** (`var = ____`) for student-fillable cells.
- **Build scripts** generate notebooks (reproducibility + git-friendly).
- **Estimation compressed** from 3 lectures to 1; variance estimation moved to Risk Management.
- **What Is Alpha lecture inserted** (Oct 7) — replaces dedicated review session; serves as hands-on review by integrating portfolios + tangent + Sharpe + benchmarking.
- **Timing notebook spans 2 sessions** with student-chosen FRED predictor for Hands-On 1 (open-ended), VIX² for Hands-On 2.
- **Belt-and-suspenders data loading** (this update) — every web fetch gets an appendix.
- **No spring break in Fall** — post-midterm runs continuously.

---

## 10. What's done (lecture-by-lecture status)

| Lec | Topic | Notebook | Build script | Run sheet | Answer key | Memo rubric | Smoke test | Appendix |
|-----|-------|----------|--------------|-----------|------------|-------------|------------|----------|
| L1 | Course Intro | ✅ | ✅ | ✅ | n/a | n/a | ✅ | n/a |
| L2 | Asset Returns | ✅ (extended) | ⚠️ patch script | ✅ | ✅ | ✅ | — | ⏳ |
| L3 | WRDS Data Tour | ✅ | ✅ | ✅ | ✅ (range) | ✅ | ⚠️ needs WRDS | ⏳ |
| L4 | Factor Models I | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | n/a |
| L5 | Factor Models II | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | n/a |
| L6 | Portfolios | ✅ | ✅ | ⏳ | ✅ | ✅ | ✅ | n/a |
| L7 | Capital Allocation I | ✅ | ✅ | ⏳ | ✅ | ✅ | ✅ | ⏳ (FF data) |
| L8 | Timing Part I | ✅ | ✅ | ⏳ | ✅ | ✅ | ✅ | ⏳ (FRED) |
| L9 | Timing Part II | (same nb) | (same) | ⏳ | (same) | (same) | (same) | ⏳ (FRED VIX) |
| L10 | **What Is Alpha?** | ✅ | ✅ | ⏳ | ✅ | ✅ | ✅ | ⏳ (FF) |
| L11 | Midterm | ⏳ | ⏳ | ⏳ | n/a | n/a | n/a | n/a |
| L12 | Guest Lecture 1 | ⏳ Coord | — | — | — | — | — | — |
| L13 | Cross-Sectional I | ⚠️ Draft | ⚠️ tight | ⏳ | ⚠️ | ⚠️ | — | ⏳ |
| L14 | Cross-Sectional II | ⚠️ Draft | ⚠️ tight | ⏳ | ⚠️ | ⚠️ | — | n/a |
| L15 | Momentum | ⚠️ Draft | ⚠️ tight | ⏳ | ⚠️ | ⚠️ | — | n/a |
| L16 | Performance Evaluation | ⚠️ Draft | ⚠️ tight | ⏳ | ⚠️ | ⚠️ | — | ⏳ |
| L17 | Capital Allocation II | ⚠️ Draft | ⚠️ tight | ⏳ | ⚠️ | ⚠️ | — | n/a |
| L18 | Multi-Factor Models | ⚠️ Draft | ⚠️ tight | ⏳ | ⚠️ | ⚠️ | — | ⏳ |
| L19 | Risk Management | ⚠️ Draft | ⚠️ tight | ⏳ | ⚠️ | ⚠️ | — | ⏳ |
| L20 | **Implementation** (NEW) | ⚠️ Draft | ⚠️ tight | ⏳ | ⚠️ | ⚠️ | — | n/a |
| L21 | ML I | ⚠️ Draft | ⚠️ tight | ⏳ | ⚠️ | ⚠️ | — | ⏳ |
| L22 | ML II | ⚠️ Draft | ⚠️ tight | ⏳ | ⚠️ | ⚠️ | — | ⏳ |
| L23 | LLMs | ⚠️ Draft | ⚠️ tight | ⏳ | ⚠️ | ⚠️ | — | ⏳ (text data) |
| L24-28 | Guest, project, presentations, review | ⏳ Logistics | — | — | — | — | — | — |

**Legend:**
- ✅ Built to standard, ready to teach
- ⚠️ Draft (built in a fast batch, needs rebuild following the §8 workflow)
- ⏳ Not started or needs work
- n/a — doesn't apply (no challenge, no web data, etc.)

### Infrastructure status

- ✅ `auto_evaluator.py` — 19 assignments wired up; three grading patterns supported
- ✅ `auto_evaluator_form.py` — Google-Form-based grader runner
- ✅ `AUTO_EVAL_DESIGN.md` — full design doc with setup steps
- ⏳ **Service-account auth + Google Form** — not yet set up; documented in AUTO_EVAL_DESIGN.md
- ⏳ **Form-link placeholder** still says `https://forms.gle/YOUR_FORM_LINK_HERE` in every submission cell — needs to be replaced once the form exists

---

## 11. What's left to do (in priority order)

### Block A — Belt-and-suspenders retrofit (1-2 hours)

Add the §1 APPENDIX template to these already-built notebooks that fetch from
the web. For each, identify the data sources and write the corresponding fetch
+ save + load cells.

- [ ] `WRDS_Data_Tour_AI.ipynb` — WRDS queries (separate appendix per query type)
- [ ] `CapitalAllocationI_AI.ipynb` — FF6 monthly from Ken French
- [ ] `Timing_AI.ipynb` — CRSP CSV + FF daily + FRED (term spread, VIX)
- [ ] `WhatIsAlpha_AI.ipynb` — 10-industry portfolios + FF3 from Ken French
- [ ] `Asset Returns` (`IntrotoReturns_c_AI`) — Yahoo via yfinance + FF daily
- [ ] `Factor Models I` and `II` — FF6 + UNH/MSFT CSVs

### Block B — Rebuild draft lectures (the big remaining work)

Each lecture in the ⚠️ Draft bucket needs the §8 workflow applied properly:
read source carefully, preserve content, real-data challenge, audit step,
smoke test. Pace: ~1-2 hours per lecture done well.

Priority order (paired by topic):

- [ ] **L13 + L14 Cross-Sectional Strategies I & II** — use WRDS panel data; classic value/size sorts; long-short construction
- [ ] **L15 Momentum** — uses the same cross-sectional panel; build the (12,1) momentum signal; the crash discussion
- [ ] **L16 Performance Evaluation** — already partially mined for the What-Is-Alpha lecture; the remainder is: overfitting, multiple-testing, bootstrap, publication bias
- [ ] **L17 Capital Allocation II** — under uncertainty; shrinkage; half-Kelly
- [ ] **L18 Multi-Factor Models** — FF3 → FF5 → FF6 → factor zoo; choosing the right benchmark
- [ ] **L19 Risk Management** — variance estimation (the deferred content from L5); VaR / ES; factor risk limits
- [ ] **L20 Implementation (NEW)** — trading costs, leverage, shorting, implementation shortfall
- [ ] **L21 ML I** — penalized regression, Lasso/Ridge/Elastic Net, time-series CV
- [ ] **L22 ML II** — trees, gradient boosting, the Gu-Kelly-Xiu story
- [ ] **L23 LLMs** — earnings tone, FOMC parsing, the lookahead-bias trap

### Block C — Run sheets (after rebuilds)

For each rebuilt lecture, write a ~100-line run sheet with the standard
structure (cold-open / sections / timing / key transitions / fall-behind /
pre-class checklist).

### Block D — Infrastructure rollout

- [ ] Set up service account for Google Sheets (15 min — see AUTO_EVAL_DESIGN.md)
- [ ] Create the Google Form (5 min)
- [ ] Replace `https://forms.gle/YOUR_FORM_LINK_HERE` placeholders across all notebooks (sed replacement)
- [ ] Run the grader against 3-5 test submissions to verify end-to-end

### Block E — Midterm + final + project

- [ ] Design midterm questions (covers L1-L10)
- [ ] Design final exam (cumulative)
- [ ] Design project specification + presentation format
- [ ] Coordinate guest lectures (L12 + L24)

---

## 12. Open questions / pending decisions

- **Group sizes for the final project.** Cap at 3? 4? Affects presentation logistics.
- **Number of presentation sessions** (L26 + L27 currently). Depends on enrollment.
- **Grading turnaround SLA** — what's the promise to students? 24h? 48h?
- **WRDS access timing** — students need it by L3 (Sep 14). Start sign-up in L1?
- **Wed Nov 25** — keep LLMs there, or swap with Guest Lecture 2 (Nov 30)?
- **AI-policy enforcement** — is "explain what your code does" enough? Or do we add an oral-defense moment for one assignment?

---

## 13. Quick-start for next session

If you (or anyone) is picking this up cold, here's the minimum to get back into flow:

1. **Read this PLAN.md** — that's the source of truth.
2. **Read the most recently built lecture** (`WhatIsAlpha_AI.ipynb`) to see the pattern in its mature form.
3. **Pick the next ⚠️ lecture** from §11 Block B.
4. **Follow the §8 workflow** to rebuild it properly.
5. **End with the §7 smoke test.**
6. **Flip its status** in §10 from ⚠️ to ✅.
7. **Add the §1 appendix** if it fetches web data.

**Key files to have open while building:**
- This file (PLAN.md)
- `chapters/Finance/FactorModels_c_AI.ipynb` (cleanest mature example)
- `chapters/Finance/build_what_is_alpha_ai_notebook.py` (most recent build script)
- `chapters/Finance/auto_evaluator.py` (to add ANSWER_KEY + MEMO_RUBRICS entries)

---

## 14. Conventions cheat sheet (one-glance reference)

| Thing | Convention |
|-------|-----------|
| Notebook title | `# Topic — Subtopic` followed by `## 🎯 Learning Objectives` |
| Section anchor IDs | lowercase kebab-case: `<a id="risk-budget"></a>` |
| Equation style | LaTeX, double-backslash in Python string for math symbols |
| Required variable naming | `snake_case`, descriptive (`alpha_a_annual` not `aa`) |
| Tolerance default for numeric grading | 0.10–0.30 (looser for noisier quantities; near-zero needs absolute tolerance via `truth=0`) |
| Memo length | "max 5-6 sentences" — tight |
| Pitfall checklist length | 5-8 items per lecture |
| "Live AI moments" per lecture | 2 (one warmup, one for the key new concept) |
| Number of takeaways | 6-9 numbered items at end of notebook |
| Run sheet timing format | `## N️⃣ Section (X min) — H:MM` |
| Web-data appendix | Every notebook that pulls web data — see §1 template |

---

**End of plan. Update this file every time you finish a lecture or change a convention.**
