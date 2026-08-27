# Auto-Evaluation System Design

## Is this feasible? **Yes, very.**

For a class of 50 students × 7 assignments = ~350 evaluations per semester:
- **Cost:** ~$15-25 total in Claude API calls (with prompt caching)
- **Your time:** ~2 hours setup, then ~10 min/assignment to review flagged outliers
- **Student turnaround:** 24-48 hour feedback loop

The main pieces already exist (Drive API, Anthropic SDK, gspread). The hard part is the **rubric design**, not the plumbing.

---

## Architecture (simplest viable version)

```
┌─────────────────┐    upload .ipynb     ┌─────────────────┐
│    Students     │ ───────────────────> │ Google Drive    │
│                 │                      │ shared folder   │
└─────────────────┘                      └────────┬────────┘
                                                  │ download new files
                                                  ▼
                                         ┌─────────────────┐
                                         │ Your laptop     │
                                         │ evaluator.py    │
                                         │  • parse .ipynb │
                                         │  • call Claude  │
                                         │  • write grades │
                                         └────────┬────────┘
                                                  │
                              ┌───────────────────┼───────────────────┐
                              ▼                   ▼                   ▼
                       ┌────────────┐     ┌────────────┐      ┌────────────┐
                       │  Google    │     │  feedback/ │      │  flagged/  │
                       │  Sheets    │     │  per-student│     │  (review   │
                       │  (grades)  │     │  .md files │     │   manually)│
                       └────────────┘     └────────────┘      └────────────┘
```

You run `python evaluator.py` after the deadline. It pulls new files, evaluates them, writes a row to Google Sheets per student, and saves a feedback markdown per student. Anything Claude flags as ambiguous (low confidence, weird output, didn't run) lands in `flagged/` for you to review by hand.

**Why this and not full automation?** Two reasons:
1. **You stay in the loop.** First semester running this, you want to spot-check 5-10% of grades. Triggers on a button press, not on a Drive event.
2. **No cloud setup.** No GCP, no Cloud Functions, no webhooks. Just a Python script and a cron line (or a manual run).

---

## Tech stack

| Component | Tool | Why |
|-----------|------|-----|
| File transport | Google Drive folder + `rclone` or Drive API | Students already have Google accounts |
| Notebook parsing | `nbformat` | Standard library for ipynb |
| LLM eval | `anthropic` SDK + Claude Sonnet 4.6 | Best price/capability; supports prompt caching |
| Output structure | Tool use (JSON schema) | Forces consistent grading |
| Gradebook | `gspread` → Google Sheets | You can see it in a browser |
| Per-student feedback | Markdown files in a Drive folder | Email or share-link to students |

---

## Rubric design (the hard part)

For each notebook, Claude returns a structured grade:

```python
{
    "student_id": "extracted from filename",
    "assignment": "FactorModels_AI",
    "completion_score": 0-100,  # did they fill in all required cells?
    "q1_correct": bool, "q1_feedback": str,
    "q2_correct": bool, "q2_feedback": str,
    "q3_correct": bool, "q3_feedback": str,
    "q4_correct": bool, "q4_feedback": str,
    "q5_memo_score": 0-5, "q5_feedback": str,
    "overall_grade": "A" | "B" | "C" | "D" | "F",
    "flag_for_review": bool,
    "summary": "1-2 sentence overall feedback for the student",
}
```

Tool use guarantees the structure. You write the rubric once per assignment.

**Trick for numerical answers:** instead of asking Claude to verify the value (it can't reliably run code), you embed a **validation block** at the bottom of the student notebook that they're told *not* to touch. Something like:

```python
# === DO NOT EDIT BELOW THIS LINE ===
# Submission checker. The auto-grader uses these values.
SUBMISSION = {
    "Q1_fund_a_total_return": fund_a_total_return,
    "Q1_fund_b_total_return": fund_b_total_return,
    "Q2_alpha_a_annual": alpha_a * 252,
    "Q2_beta_a": beta_a,
    "Q2_alpha_b_annual": alpha_b * 252,
    "Q2_beta_b": beta_b,
    "Q3_sharpe_a": sharpe_a,
    "Q3_appraisal_a": appraisal_a,
    "Q3_sharpe_b": sharpe_b,
    "Q3_appraisal_b": appraisal_b,
    "Q4_position_a": position_a,
    "Q4_position_b": position_b,
}
print(SUBMISSION)
```

The evaluator script **actually runs the notebook** in a sandbox and reads `SUBMISSION`. It compares to known-correct values with a tolerance. Then Claude only judges the *memo* (Q5) — the hard part where you actually need an LLM.

This is a 10x more reliable than asking Claude to look at code and guess if it's right.

---

## FERPA / privacy

Anthropic's API doesn't train on customer prompts (per their TOS) but the safest setup is:

1. **Anonymize before sending.** Map `NetID → hash` locally. Send `Student_a3f9b1` to Claude, never `Smith_John`.
2. **Keep the mapping table on your laptop only.** It's just a CSV with NetID ↔ hash.
3. **Don't put student names in the notebook submission.** Have them rename their file to `<hash>.ipynb` (or your script does it on download).

This makes a breach inert — even if logs leak, the only thing exposed is an anonymous hash and a memo about factor regressions.

---

## Cost / effort estimate

**Setup (one-time):**
- Google Drive shared folder: 5 min
- gspread + Drive API auth: 30 min
- Adapt the starter script for your rubric: 1 hour
- Test on 3 dummy submissions: 30 min

**Per assignment:**
- Run script: ~1 min
- Review flagged submissions: 10-20 min
- Push feedback files back to Drive: 1 min (script does it)

**API cost:**
- ~30K input tokens per notebook (notebook + rubric + system)
- ~500 output tokens (the grade JSON + feedback)
- With prompt caching on the rubric: ~$0.04 per notebook
- **Per assignment (50 students): ~$2**
- **Per semester: ~$15**

---

## Failure modes and how to handle them

| Failure | Detection | Action |
|---------|-----------|--------|
| Notebook won't execute | Script catches exception | Mark `flag_for_review=true`, save error, you grade manually |
| Student renamed `SUBMISSION` dict | KeyError when reading | Flag for review |
| Numerical answer ±50% off | Comparison with tolerance | Mark wrong, Claude explains why |
| Memo is empty | Length check | Score = 0, feedback = "memo not submitted" |
| Claude gives inconsistent grade across runs | Run twice on a sample, compare | If <90% agreement, tighten rubric |
| Student LLM-generates the memo | You inspect a sample | This is a policy question, not a tech one |

---

## What about cheating?

For completion-graded assignments (as in your syllabus), cheating doesn't really matter — submission = credit. For the final project, you want a human reading the memo anyway.

If you want a cheating signal, Claude can compare two submissions and rate similarity. That's a separate $0.01/comparison call. With 50 students that's $25 to compare every pair — not free but doable.

A simpler approach: require students to record a 90-second voice memo explaining their answer to Q5. They can use AI to write code, but they have to defend the conclusion in their own voice.

---

## Starter script

See `auto_evaluator.py` in this folder — runnable starter code with sample rubric.
