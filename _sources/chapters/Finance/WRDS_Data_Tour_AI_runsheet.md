# WRDS — Live Data Tour — In-Class Run Sheet

**Notebook:** `WRDS_Data_Tour_AI.ipynb`
**Duration:** 75 min
**Style:** Live demo + hands-on. **Students directly use WRDS today** — the whole point is to force the first login + first queries.
**Pre-class state:** Students completed L1 (Course Intro) and L2 (Asset Returns). They've registered for WRDS in Week 1 and should have their credentials by now.

---

## 🎬 Cold open (3 min) — 0:00

> "Last class we computed Apple's return on data I handed you. Today: **YOU
> pull the data.** From WRDS. With your own account.
>
> By 5pm you will have written SQL against CRSP, pulled a stock's full
> history, joined it to Compustat fundamentals, and submitted a token from
> a query *you* ran. **If WRDS doesn't work for you at 4pm, you have one
> hour to fix it.**
>
> The big skill today: **writing precise prompts for AI to generate SQL.**
> Loose prompts produce subtly wrong queries. Precise prompts produce SQL
> that works the first time. We'll see three pairs."

---

## 1️⃣ Why WRDS + first connection (10 min) — 0:03

**Notebook cells:** Sections "Why WRDS" + "First WRDS Connection" (cells 4-9).

**Talk through the source table** (FRED, Yahoo, WRDS). Survivorship-bias is the killer reason for WRDS.

**The connection cell is the highest-risk moment of the day.** Plan for it:
- Students need to replace `'your-netid-here'` with their actual WRDS username
- The cell will prompt for password the first time
- It WILL fail for 10-30% of students on first try

**Common failures:**
- "Authentication failed" → wrong username (most often NetID without `@nyu.edu`)
- "Connection refused" → corporate VPN blocking port 9737 (have them disable VPN)
- "Module not found: wrds" → uncomment the `!pip install wrds` line in setup

**Strategy:** "If your connection works, **help your neighbor.** If you're stuck, raise your hand. We do not move past this section until at least 80% of the room has `✅ Connected to WRDS`."

**Run cell 9 to enumerate tables.** Show them the schema map (key tables to know).

---

## 2️⃣ Query workflow (5 min) — 0:13

**Notebook cells:** "Querying WRDS" section (cell 11).

**Drive home the loose-vs-precise framing:**

> "When you ask AI to write SQL for WRDS, **AI does not actually know the
> WRDS schema well**. It's seen lots of SQL online — but the *quirks* of
> CRSP and Compustat (column names, multi-row-per-firm-year, ticker
> instability) — it has to be TOLD. **The precise prompt does the telling.**"

**Tease:** "We'll see this pattern three times today. Watch for what the loose prompt gets wrong."

---

## 3️⃣ Demo 1 — Single stock (AAPL) (15 min) — 0:18

**Notebook cells:** Demo 1 section (cells 13-15) + retx tricks + share issuance (cells 17-20).

### The loose-vs-precise reveal

**Project cell 13 (the markdown).** Read out the LOOSE prompt:
> *"Get Apple's stock returns from WRDS"*

**Read the AI's likely output (the bug list):**
- SELECT * (slow)
- ticker filter (unstable)
- no date range (40 years of data)
- no order
- date as string

**Then the precise prompt.** Read it slowly — pause on each named element:
- table name (`crsp.msf`)
- permno (14593, not ticker)
- date range
- exact columns
- ordering
- date_cols arg

**Run cell 14.** Students should see ~180 rows.

### The retx trick (5 min)

**Run cell 17.** The dividend yield extraction.

> "Three lines of code. We just extracted Apple's entire dividend history
> from two CRSP columns. **No data source other than CRSP gives you this
> split cleanly.**"

**Run cell 19.** The buyback story.

> "Apple's market cap grew faster than its share count fell — and you can
> see exactly how much of the cap growth came from repurchases. Decomposing
> business growth vs. buybacks is a standard piece of equity analysis, and
> it lives in two CRSP columns."

---

## 4️⃣ Demo 2 — Cross-section (10 min) — 0:33

**Notebook cells:** Demo 2 section (cells 22-23) + "What's IN the cross-section" (cells 25-29).

### The loose-vs-precise reveal #2

**Project cell 22.** Read the LOOSE prompt:
> *"Get all stocks from CRSP for June 2020"*

**The bug to highlight: `BETWEEN '2020-06-01' AND '2020-06-30'`** — but CRSP
monthly dates are always month-end. Depending on what your filter looks like,
you might get zero rows back. **And the SHRCD filter is missing** — you'd get
ETFs mixed in.

**Then the precise prompt.** `date = '2020-06-30'` (exact). `shrcd IN (10, 11)`.

**Run cell 23.** ~3,500 stocks.

### Quick tour: shrcd, exchange, negative prices (8 min)

**Run cells 26-29** in succession. Don't dwell:
- Share codes: 10/11 are the academic universe; 18 = ETFs.
- Exchange breakdown: NASDAQ dominates by count, NYSE by value.
- Negative prices on AMEX (low-liquidity flag).

> "These quirks are the kind of thing you only learn by playing with the
> data. Not in textbooks. Not in courses. You either know it or your
> regression silently breaks."

---

## 5️⃣ Demo 3 — Compustat fundamentals (12 min) — 0:43

**Notebook cells:** Demo 3 section (cells 31-32) + Value premium (cells 34-35).

### The loose-vs-precise reveal #3 — THE HARDEST

**Project cell 31.** Read the LOOSE prompt:
> *"Get Apple's revenue and assets from Compustat"*

**The bugs are subtler:**
- `tic = 'AAPL'` — works for AAPL today, breaks for any firm whose ticker changed
- `comp.funda` returns MULTIPLE rows per firm-year unless you filter on indfmt/datafmt/popsrc/consol
- 700 columns in the schema → SELECT * is brutal

**The 4-filter pattern is the headline of today.** Pause on it:

> "If you remember ONE thing from today: **the four filters.** indfmt='INDL',
> datafmt='STD', popsrc='D', consol='C'. Forget them and your Compustat data
> is silently 4x too many rows per firm-year. Your subsequent analysis will
> be wrong in subtle ways. Tape these to your monitor."

**Run cell 32.** Show AAPL's fiscal-year history.

### Quick book-to-market computation (3 min)

**Run cell 35.** Apple's B/M is tiny (deep growth stock).

> "We'll spend Weeks 8-9 unpacking the value premium — high B/M earns more
> on average. Today you just learned how to compute it for any firm in
> WRDS. **That's a research-grade tool.**"

---

## 6️⃣ Final Challenge (15 min) — 0:55

**Notebook cells:** "Final Challenge" section (cells 37-43).

**Set it up (1 min):**
> "Pick a stock — NOT AAPL. Use `crsp.stocknames` to find its permno.
> Pull 5 years of monthly data. Fill in 6 variables. Run the submission
> cell. Paste the token into the form. **The whole point is to verify
> you can do this end-to-end with WRDS.** You have 12 minutes."

**During (12 min):** Walk the room.

**Common issues:**
- Stocknames lookup returns multiple permnos → "Pick the one whose name and date range match"
- Forgot to convert prc to abs() before computing market cap → negative values
- cum_return computed as sum instead of `(1+ret).prod()-1`

**Cold-call wrap (2 min):**
- "Three people: shout your ticker, your permno, your market cap"
- This confirms they got real data and submitted

---

## 🎯 Wrap (2 min) — 1:10

**Takeaways to emphasize (cell 45):**
1. **Loose prompts → wrong SQL. Precise prompts → working SQL.**
2. **The 4 Compustat filters are non-negotiable.**
3. **permno, not ticker. abs(prc), not prc.**

**Next class:** "Factor models. We move from data plumbing to actual analysis. **Today was setting up the plumbing.** Next class we use it."

---

## 🆘 If you fall behind

Cut in this order:
1. ✂️ Demo 3 (Compustat join) — the hardest, can defer to a later lecture if absolutely needed
2. ✂️ The share-issuance detour (cells 19-20) — keep the conceptual point
3. ✂️ Cross-section exchange breakdown (cell 27) — verbalize instead

**Do NOT cut:**
- The first connection moment (every student MUST get WRDS working)
- Demo 1 (the loose-vs-precise pattern needs to be seen at least once before the challenge)
- The challenge (whole point of the lecture is the infrastructure check)

---

## 🆘 If WRDS is broken across the network

This is the nuclear scenario: WRDS itself is down, or NYU's gateway is
broken, and *nobody* can connect. Backup plan:

1. Acknowledge it openly: "WRDS is down. We pivot."
2. Have students run the **FALLBACK_LOAD_CSVS** cell at the bottom of the
   notebook (loads pre-pulled equivalents of the demo data)
3. Walk through demos 1 and 2 against the CSVs — show them the SQL they
   *would* have written
4. Push the Challenge to a 30-minute homework, due before next class

This pivot eats your last 20 min. Accept it. Move on.

---

## 📋 Pre-class checklist

- [ ] **Verify your own WRDS connection works** in the same Colab environment
  before class. If yours fails, students' will too.
- [ ] Have your WRDS username already typed (so the demo runs in 5 seconds)
- [ ] This run sheet on second screen
- [ ] AAPL permno (14593), MSFT permno (10107), AAPL gvkey (001690) ready to
  reference
- [ ] Brightspace link to WRDS account signup ready (in case anyone hasn't done it)
- [ ] Estimated split: ~30% of students will have a connection issue on first try; plan for 10 min of debugging
