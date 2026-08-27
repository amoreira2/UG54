import json, pathlib
def md(s): return {"cell_type":"markdown","metadata":{},"source":s.splitlines(keepends=True)}
def code(s): return {"cell_type":"code","execution_count":None,"metadata":{},"outputs":[],
                     "source":s.splitlines(keepends=True)}
C=[]
C.append(md("""# Assignment 0 — Python, pandas, and Data That Fights Back

**Due Thursday 10 September, midnight, on Brightspace.**
Graded on completion. You may work with others; each of you submits your own copy.

---

**Your name / NYU email:**

**Worked with:**

---

This is the warm-up. It exists because the rest of the term assumes you can get
data into Python and trust what comes out.

**Use AI for all of it.** Every line of code here is something Gemini or ChatGPT
will write for you in seconds, and you should let it. What the AI will *not* do
is notice when the answer is wrong — and this assignment is mostly a tour of
ways a notebook returns a confident, plausible, incorrect number.

Where a question asks you to **predict before running**, do that honestly. The
prediction is the point; getting it wrong costs you nothing."""))

C.append(md("""---

# Part 1 — Two ways a notebook will lie to you"""))

C.append(md("""### Q1 — Cells run in the order *you* run them, not the order they appear

Run the next two cells in order. You should get 2,552.56."""))
C.append(code("""deposit = 2000
rate    = 0.05
years   = 6"""))
C.append(code("""deposit * (1 + rate) ** years"""))
C.append(md("""Now, in the cell below, change the rate to **10%** — and do *not* re-run
anything above."""))
C.append(code("""rate = 0.10"""))
C.append(md("""Go back and re-run **only** the `deposit * (1 + rate) ** years` cell.

> **(a)** What number do you get now, and why is it not the 5% answer?
>
> **(b)** Now scroll up and re-run the *first* cell, then the calculation cell
> again. What happens, and why?
>
> **(c)** A notebook has an execution *order* and a visual *order*, and they are
> not the same thing. Describe, in one or two sentences, how this could produce a
> number in your final report that you cannot reproduce the next morning.

This is the single most common way a Jupyter result turns out to be wrong, and
AI makes it worse rather than better — pasting a fix halfway up the notebook and
re-running one cell is exactly the move that causes it."""))
C.append(md("""**(a)**

**(b)**

**(c)**"""))

C.append(md("""### Q2 — Code that runs, returns a plausible number, and is wrong

You put \\$100 into a stock. It returns **+15%** in year one and **−14%** in
year two. The cell below claims to compute what you end up with.

**Do not fix it yet.** First: look at it, and write down what you think it will
print."""))
C.append(code("""r1 = 0.15
r2 = -0.14

100 * 1 + r1 * 1 + r2      # <- what will this print?"""))
C.append(md("""> **(a)** Your prediction, before running:
>
> **(b)** Run it. What did it actually print? Is that number plausible as
> "\\$100 after two years"? Would you have caught it if it had appeared in the
> middle of a table?
>
> **(c)** Fix it in the cell below, and state the correct final value."""))
C.append(code("""# Your corrected calculation
"""))
C.append(md("""**(a)** prediction:

**(b)**

**(c)** correct value:"""))

C.append(md("""---

# Part 2 — Python worth knowing when the AI writes the code"""))

C.append(md("""### Q3 — Predict, then run

Below are six statements. `x = 2`, `y = 2`, `z = 4`.

```python
x > z                              # 1
x == y                             # 2
(x < y) and (x > y)                # 3
(x < y) or  (x > y)                # 4
(x <= y) and (x >= y)              # 5
True and ((x < z) or (x < y))      # 6
```

**Write down your six answers first**, as a list like `[True, False, ...]`.
Then run them and compare. Note any you got wrong — `and`/`or` precedence is a
real source of silently wrong filters later in the course."""))
C.append(md("""**My predictions:** `[ , , , , , ]`"""))
C.append(code("""x, y, z = 2, 2, 4
# check your six predictions here
"""))

C.append(md("""### Q4 — Data does not arrive as numbers

You are handed a price as `"$6.50"`. Python sees a string, and `"$6.50" * 2`
gives you `"$6.50$6.50"` rather than 13.

Turn it into the float `6.5`. Then say in one sentence what would happen if a
column of a thousand prices had this problem and you took its mean."""))
C.append(code("""price = "$6.50"
# your code here
"""))
C.append(md("""**What happens to the mean of a column like this:**"""))

C.append(md("""### Q5 — Why logs show up everywhere in finance

There is a trick worth knowing: for numbers close to 1, the percent change
$(x-y)/y$ is well approximated by the difference in logs, $\\log x - \\log y$.

Verify it with the numbers below — compute both and compare. Then try it again
with `x = 2.0, y = 1.0` and report how well the approximation holds.

One sentence: when is it safe to use, and when is it not?"""))
C.append(code("""x, y = 1.05, 1.02
# your code here
"""))
C.append(md("""**When it holds, and when it breaks:**"""))

C.append(md("""---

# Part 3 — Real data, which does not want to help you

Everything from here uses one Excel file: 49 US industry portfolios from Ken
French, monthly, going back to 1926, plus a sheet with the market return and the
risk-free rate.

```
https://raw.githubusercontent.com/amoreira2/UG54/refs/heads/main/assets/data/Assignment1.xlsx
```

**Download it and open it in Excel before you write any code.** Ten seconds of
looking will save you an hour. This is a habit, not a suggestion."""))
C.append(code("""import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
%matplotlib inline
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = [10, 4]

URL = ("https://raw.githubusercontent.com/amoreira2/UG54/"
       "refs/heads/main/assets/data/Assignment1.xlsx")
pd.ExcelFile(URL).sheet_names"""))

C.append(md("""### Q6 — Load it, and count the columns

Read the `49_Industry_Portfolios` sheet. The real column names are **not** in
the first row — there are several lines of description above them, so you will
need `skiprows`.

Then answer this before going further: **how many columns did you get?**

> **(a)** How many columns are there, and how many industries were you promised?
>
> **(b)** Print the column names. Some of them end in `.1` and `.2`. What has
> happened, and what would you have computed if you had just averaged everything?
>
> **(c)** Keep only the block you actually want — the value-weighted returns —
> and say how you know it is the right one."""))
C.append(code("""# your code here

raw = ____
print(raw.shape)
print(list(raw.columns))"""))
C.append(md("""**(a)**

**(b)**

**(c)**"""))
C.append(code("""ind = ____        # date column + the 49 value-weighted industries only
print(ind.shape)"""))

C.append(md("""### Q7 — Missing values that are not missing

The header text says: *"All missing values are indicated by -99.99 or -999."*

Find them and replace them with proper `NaN`. Then report what fraction of the
table was missing.

> **⚠️** If you skip this, `-99.99` is a perfectly valid number and every mean,
> standard deviation and correlation you compute will quietly include it as a
> **−99.99% monthly return**. Nothing will error."""))
C.append(code("""# your code here
"""))

C.append(md("""### Q8 — Dates and units

Two more things stand between you and usable data.

**Dates.** The first column is an integer like `192607`. Convert it to a proper
month-end date and make it the index. Month-*end* matters: these are monthly
returns, and later in the course you will merge them against other series that
are stamped at month end. A one-day mismatch silently drops every row.

**Units.** Print the mean of one industry. Is it a monthly return of 0.9%, or
90%? Convert so that a 1% return is stored as `0.01`."""))
C.append(code("""# your code here

print(ind.index[:3])
print(f"mean monthly return, Agric: {ind['Agric'].mean():.5f}")"""))

C.append(md("""### Q9 — Excess returns

Load the `Market_proxy` sheet the same way — it has `Mkt-RF` and `RF`. Watch the
units here too.

Then build excess returns two ways:

1. For **one** industry, `Agric`, subtract `RF` month by month. Print its mean.
2. For **all 49 at once**, in a single line, producing a DataFrame called `inde`.

> **🤖 Worth asking the AI:** *"subtract a Series from every column of a
> DataFrame, aligning on the index"* — and then check that the row count did not
> change. Getting the axis wrong here produces a table full of NaN, or worse, a
> table that looks fine and is transposed."""))
C.append(code("""# your code here
"""))

C.append(md("""### Q10 — Dropping rows has a price

Not every industry exists in 1926. To get a rectangular table where every
industry covers the same months, drop the incomplete rows.

Report: how many months you had before, how many after, and **what date the
sample now starts**.

> **(a)** How many months did that cost you?
>
> **(b)** You have just thrown away 40 years of data to keep 49 columns. Name
> one thing you might have done instead, and say what it would have cost."""))
C.append(code("""# your code here
"""))
C.append(md("""**(a)**

**(b)**"""))

C.append(md("""### Q11 — The two objects everything else is built from

Compute and display:

1. `ERe` — the vector of **annualized** mean excess returns, one per industry
2. `CovRe` — the **annualized** covariance matrix of excess returns

Report the highest and lowest average-return industries. Then print the
correlation between three pairs of your choosing — pick one pair you expect to
move together and one you expect not to, and say whether the data agreed.

Remember: means annualize by ×12, variances by ×12, volatilities by ×√12."""))
C.append(code("""# your code here
"""))
C.append(md("""**Pairs I picked, what I expected, what I found:**"""))

C.append(md("""### Q12 — Look at it

Pick **two** industries that you think behaved very differently in some
identifiable episode — a crisis, a boom, a technological shift.

1. Plot their monthly excess returns over that period.
2. Plot the **cumulative** return of \\$1 invested in each over that period.
3. In three or four sentences, say what happened, using the actual magnitudes
   from your plot. What would \\$1 have become in each?

> **📌** Cumulative returns compound: `(1 + r).cumprod()`, not `r.cumsum()`.
> Adding returns is Lecture 1's pitfall 4 and the error grows with horizon."""))
C.append(code("""# your code here
"""))
C.append(md("""**What happened:**"""))

C.append(md("""---

## 📤 Submission

1. **Run your notebook from a clean start** — Runtime → Restart and run all.
   If it does not survive that, Q1 is still ahead of you.
2. File → Download → `.ipynb`
3. Upload to Brightspace under Assignment 0.

---

## What this was for

Next week you meet a dataset with 1.5 million rows where you cannot open the
file and look. Every trap in Part 3 is one you will hit again there, invisibly:
columns that are not what they claim, sentinel values masquerading as data,
dates that do not line up, and percent where you assumed decimal.

You will also notice that this file is **wide** — one column per industry. The
course panel is **long** — one row per stock-month. Lecture 2 explains why, and
having built something in the wide shape first is the point."""))

nb={"cells":C,"metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},
    "language_info":{"name":"python","version":"3.11"}},"nbformat":4,"nbformat_minor":5}
out=pathlib.Path("chapters/Assignments/A0_Python_and_Pandas_AI.ipynb")
json.dump(nb, open(out,'w'), indent=1, ensure_ascii=False); open(out,'a').write("\n")
print(f"✅ {out}  —  {len(C)} cells, 12 questions")
