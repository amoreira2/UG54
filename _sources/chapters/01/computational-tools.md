Computational Tools
====================

This course uses **Python 3** and an **AI coding assistant**, together, all term.
That pairing is deliberate. Python is the language the analysis is written in;
AI writes most of it. Neither half is optional, and the interesting part is why
they work well together.

A programming language is, loosely, a structured subset of natural language
(words) and special characters (e.g. `,` or `{`) that lets you describe
operations you would like a computer to perform on your behalf. What has changed
recently is who does the describing. You now specify the analysis in English,
and something else translates it into Python.

### Why Python

- Easy to learn and read, relative to almost anything else.
- Excellent tools for handling data efficiently and succinctly — `pandas`,
  `numpy`, `statsmodels` and `matplotlib` are what the industry actually runs on.
- The standard for data analysis in finance. CRSP, Compustat and WRDS all have
  Python interfaces; so does every broker and data vendor you are likely to meet.
- General purpose. You will learn it for data analysis, but it also does web
  scraping, databases, dashboards and modelling, and it is the world's best
  language for [gluing](https://en.wikipedia.org/wiki/Glue_code) those pieces
  together.

It is sometimes said that Python is "the best language for nothing but the
second best language for everything." A versatile second-best language is a good
one to learn first.

### Why AI, and why with Python in particular

Three reasons the combination works better than either half alone.

**Models write Python better than they write anything else.** Two decades of
public Python — GitHub repositories, Stack Overflow answers, library
documentation, millions of notebooks — is what these models learned from. Ask
for a merge or a rolling regression in Python and you will usually get working
code on the first try. Ask for the same thing in a proprietary language with a
fraction of the public corpus and the error rate climbs.

**The correction loop is seconds long.** Generate a cell, run it, look at the
output, fix it. There is no compile step and no licence server between you and
the answer. That loop is what makes it practical to accept code you did not
write, because you can check it immediately and cheaply.

**You can read what it did.** Python is close enough to English that you can
look at generated code and disagree with a specific line — this used total
returns where it should have used excess, this dropped rows before ranking
instead of after. That readability is what makes auditing possible at all. Code
you cannot read is code you have to trust.

### What each of you is for

The division of labour is **Specify → Implement → Validate**, and Lecture 1 sets
it up in detail:

| Step | Who |
|------|-----|
| Say precisely what you want | **You** |
| Write the code | **AI** |
| Check whether the output is right | **You** |

The failure mode worth knowing before you start: **AI-generated code usually
runs.** Code that crashes tells you it is wrong. Code that returns a plausible
number does not. A Sharpe ratio of 0.61 computed on total returns instead of
excess returns looks exactly like a Sharpe ratio of 0.61 computed correctly, and
it is wrong by about 40%. Most of this course is built around catching the
second kind of error.

This is also why you still have to learn Python rather than only prompting. You
cannot validate what you cannot read.

### Why open source

Software development is now largely a process of stitching together
high-quality libraries and current research code. Proprietary languages sit
outside that.

- Open languages are easier for anyone in the world to write and share packages
  in, because the code is accessible and available.
- Academics, businesses and hobbyists all have an incentive to contribute.
- Public hosting (e.g. GitHub) makes it easier to build a community and
  collaborate.
- Package management — finding, downloading, installing and upgrading packages —
  can be open and simple, with no proprietary licences to negotiate.

There is now a further reason. A language whose source, documentation and twenty
years of question-and-answer archives are all public is a language AI models
have learned properly. Openness used to be about cost and collaboration; it is
also, now, about how well your assistant can help you.

### What you will use

**Google Colab**, which runs Python in the browser with nothing to install and
has Gemini built in. Bring a charged laptop. **ChatGPT and Claude** are equally
welcome — use whichever you like, and use it actively.
