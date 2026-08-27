# Course Intro — In-Class Run Sheet

**Notebook:** `CourseIntro_AI.ipynb`
**Duration:** 75 min
**Audience:** First class of the semester. They've never seen the syllabus before today.
**Energy:** Set the tone for the whole semester. Don't read off slides — talk.

---

## 🎬 Cold open (2 min) — 0:00

Walk in. Say something like:

> "Welcome to UG54. This is the **most different version** of this class I've ever taught — and I'm guessing some of you signed up because you heard about it.
>
> You're going to leave here knowing how to do quantitative finance with AI doing 60% of the typing for you. **What you'll be doing is much harder than typing.** You'll be the one telling the AI what to do, then catching it when it makes a mistake.
>
> By 5pm you will have used AI to answer a real finance question and audited the answer. Let's go."

---

## 1️⃣ Mechanics (5 min) — 0:02

**Notebook cells:** Section 1.

**Things to actually say (not just project):**
- "Assignments are completion-based. If it runs and looks like you tried, full credit. Drop your worst — only 6/7 count."
- "AI policy: **use it freely.** This whole course is built around it. But you have to be able to explain what you submitted."
- "**No phones, no recording.** FERPA + I want you focused."
- "Office hours posted — don't email me Sunday night about an assignment due Monday."

**Don't dwell.** The syllabus is on Brightspace. They'll read it later.

---

## 2️⃣ Why this course, why now (10 min) — 0:07

**Notebook cells:** Section 2. The "old skill / new skill" table is the centerpiece.

**Land the punchline:**
> "60% of what a first-year quant analyst used to do is now a 5-second AI call. That's not a threat — it's an opportunity. **The 40% that's left is what we're teaching.**"

**Optional anecdote** (use if you have one):
> "Last summer I talked to a friend at [hedge fund]. He said they're already changing the interview. They don't ask candidates to write merge syntax on a whiteboard anymore. They show them a buggy AI-generated analysis and ask: 'What's wrong with this?'"

**Pivot to the workflow:**
> "So how do you actually do that? Three steps."

---

## 3️⃣ The workflow (8 min) — 0:17

**Notebook cells:** Section 3.

**Walk through the table slowly:**
- "**Specify** — you say exactly what you want, in English. Frequency, units, edge cases."
- "**Implement** — AI generates the code. Or you do, if it's faster."
- "**Validate** — you check the output against a domain-specific list of pitfalls."

**Drive the spec quality point:**
- Project the "vague / better / precise" example
- Read out the vague one in a deadpan voice
- "What happens? You get a number. It might even look right. But you have no idea what it actually computed."
- Read out the precise version
- "Same task. Different reliability. **The whole semester is teaching you to write the precise version.**"

**Mention the pitfall checklists:**
- "Every topic comes with one. Print them. They are the syllabus."

---

## 4️⃣ Setup (15 min) — 0:25

**Notebook cells:** Section 4.

**This is the highest-risk segment.** Some students will have setup problems. Plan for it.

**Walk them through live:**
1. Open colab.research.google.com — sign in with NYU Google
2. Open this notebook (link in Brightspace)
3. File → Save a Copy in Drive (so their edits persist)
4. Click the Gemini sparkle icon, accept terms
5. Run the "Setup works ✓" cell (cell 9)
6. Type the test prompt into Gemini, see if it can read the notebook

**Common problems:**
- NYU SSO timing out → retry after 30s
- Gemini panel not appearing → it's in Tools → Gemini if the sparkle isn't visible
- Gemini saying "I can't see your notebook" → ensure the panel is active and they ran at least one cell

**If a student is stuck:** ask their neighbor to help. Most setup problems get solved by a peer faster than by you. This is intentional — it builds the group dynamic.

**Don't move on until at least 80% of the room has "Setup works ✓"** on screen.

---

## 5️⃣ Hands-on exercise (25 min) — 0:40

**The exercise:** "How much would $1000 of [stock] be worth today if your parents had bought it the day you were born?"

**Why this works as a first exercise:**
- Personal — they care about the number
- Simple enough that nobody is intimidated
- Has REAL pitfalls (Adj Close vs Close, IPO date issues, dividend handling)
- Each student walks out with a concrete number tied to their own birthday — easier to remember than an abstract example

**Steps:**
1. **(5 min)** Read out section 5. Show the spec format. Have everyone fill in their stock + birthday.
2. **(10 min)** They paste the suggested prompt into Gemini, run the output. Walk the room — help anyone stuck.
3. **(5 min)** **AUDIT TIME.** Project the validation checklist (cell 13). Have students answer each question for THEIR code:
   - Did the AI use Adj Close or just Close? (Pull up someone's screen if possible)
   - Is the start date what they expected?
   - Is the final number plausible?
4. **(5 min)** **Cold-call discussion:**
   - "Who got the biggest number? What stock?" (Hands up)
   - "What's the annualized return? Tell me without using a calculator." (Push back if they hedge — make them compute it on paper)
   - "Did that beat the market over the same period? How would you know?"

**The teaching moment:**
> "Notice what just happened. None of you wrote a line of code from scratch. You wrote a spec, AI wrote the code, you ran it, you sanity-checked it. That's the loop we'll repeat all semester."

---

## 6️⃣ What's next + Assignment 1 (8 min) — 1:05

**Notebook cells:** Section 6.

- "Wednesday: we do this properly. The full story on returns — total vs excess, the risk-free rate, the Sharpe ratio."
- "Assignment 1 is up on Brightspace. **Due next Monday before class.**"
- "It extends today's exercise to 3 stocks. The submission cell at the bottom of the notebook will bundle your answers into one line. Paste that into the Google Form. We'll cover the submission flow on Wednesday."
- "Office hours start Friday. Sign up on Brightspace if you want to chat about the course or anything else."

**Final question to leave them with:**
> "Before next class: try to think of one finance question you actually want answered. Could be 'should I buy index funds or stock-pick?' Could be 'why are some hedge funds worth their fees?' Bring it. **We'll spend the semester teaching you how to answer questions like that with data.**"

---

## 🎯 Wrap (2 min) — 1:13

**Project the 5 key takeaways** (cell 14).

Pick #2: *"Every analysis follows the same loop: Specify → Implement → Validate. Internalize this."*

> "If you remember nothing else from today, remember those three words. We'll come back to them every single class."

**Dismiss with energy.** First impressions matter.

---

## 📋 Pre-class checklist (10 min before)

- [ ] Notebook open in Colab, Gemini panel visible
- [ ] Test the "Setup works ✓" cell once before class so you know it runs
- [ ] This run sheet on second screen
- [ ] Have an example student stock+birthday ready in case nobody volunteers (e.g. "I was born in 1980, would have bought AAPL if I were brave")
- [ ] Brightspace tab open in case you need to point at the syllabus
- [ ] Name cards distributed if you're using them
- [ ] A backup non-AI version of the AAPL exercise pre-rendered, in case Gemini is down

---

## 🆘 Backup plans

**If Gemini is down for the whole class:**
- Pivot to using ChatGPT / Claude on phones
- Or: project YOUR Gemini session and have students follow along, then they retry at home

**If Colab is down:**
- Most students should still be able to follow projection
- Have them install Jupyter locally as a fallback (this is in the assigned reading)
- Acknowledge it's a bad first day, push the hands-on to Wednesday

**If half the class doesn't have NYU Google login working:**
- They can use personal Google for today
- Switch back to NYU before submitting Assignment 1
- Brightspace has the right SSO troubleshooting links
