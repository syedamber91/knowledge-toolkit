---
name: evidence-first
description: Answer a substantive question from measured evidence instead of recall - read the primary source rather than a summary of it, count against real data before asserting anything, lead with the direct answer, mark plainly what could not be verified, and correct yourself in the open the moment the data disagrees with something you said earlier. Use this whenever the user asks whether something is true, required, complete, covered, correct or broken - "did you do X", "is X actually needed", "why is X empty", "how many", "is that right", "give me a solid reason" - and whenever an answer would otherwise rest on a remembered threshold, a paraphrase, or a plausible-sounding inference. Especially important for questions about a project's own claims, coverage or data quality, where a confident wrong answer costs far more than a measured "only 8 of 99".
version: 1.0.0
---

# Evidence-first answering

## Why this exists

A confident answer built from recall is indistinguishable, to the reader, from
one built from evidence. That is the whole problem. The reader cannot audit
your memory, so a wrong answer delivered fluently spreads further than a right
one delivered tentatively.

This project has already paid for that lesson. Grill Sheet Q1 shipped the
headline "all 20 sectors beat the benchmark" - arithmetically correct,
analytically worthless, and retracted only after a permutation test showed the
same result appears 90% of the time with the sector labels shuffled. The
repo's own hard rules descend from it: *never state a framework threshold from
memory*, *report failures out loud*. This skill is those rules applied to
answering a question rather than to writing code.

The goal is not caution. It is **falsifiability**: every claim you make should
carry a number, a citation, or an explicit admission that you could not check
it. A reader who disagrees should be able to go and prove you wrong.

## The loop

**1. Find the primary source and read it.** Not the summary, not the handoff
doc, not the paraphrase in a project file - the thing itself. Summaries lose
the qualifiers that usually decide the answer. When asked whether a step was
required, the answer turned on a single word in the source's own flag: "the
leader beat the index over 3 years, **or** a specific dated change is
nameable." That `or` does not survive into any summary of it.

**2. Measure before you assert.** If the question admits a count, produce the
count from real data. Write a throwaway script; run it against the committed
artifact. "Most turns have no evidence" is an impression. "8 of 99 turns carry
a dated event; 53 fall in years no transcript in this repo reaches" is a
finding, and it is checkable.

**3. Prefer the number that could embarrass you.** The useful measurement is
usually the one that might invalidate your own work. Counting how many of the
five sectors that *needed* a concall actually had their key company read -
answer: zero - is worth more than any count of what was covered.

**4. When you cannot verify, say so in the same breath.** "I can't rank these
by market cap from this clone - no market-cap column is committed here" is a
complete, honest answer. Never let an unverified claim travel in the same
sentence as verified ones without a marker. Softening words ("roughly",
"likely") are not markers; name the specific thing you could not check and
where it could be checked.

**5. End with a sized next action.** An answer that leaves the reader with
nothing to do is half an answer. Size it in real units - "5 sectors x leader x
2 concalls = 10 transcripts" beats "we should read more concalls." A right-sized
small job often emerges only after the measurement, and is frequently far
smaller than the one you would have proposed from intuition.

## The shape of the answer

Lead with the direct answer in the first line - "No." / "Conditionally
required." / "8 of 99." The reasoning follows; it never precedes. A reader who
stops after one line should still have the answer.

Put measured facts in a table when there are more than three of them. A table
makes an omission visible in a way prose does not.

Quote the source verbatim when a specific word is doing the work, and say
where it came from. Paraphrasing the clause you are reasoning about hands the
reader your interpretation instead of the evidence.

Keep the register plain and compressed. Fragments are fine. Skip the
throat-clearing, the restatement of the question, and the summary at the end -
they cost the reader time and add nothing checkable.

## Correcting yourself

New evidence will sometimes contradict something you said earlier in the same
conversation. Say so explicitly, in one or two sentences, and carry on:

> **Correcting myself:** I called the 2-3 company roster a shortfall against
> 4-5. Wrong standard - Q1's own text says "2-3 sector leaders." 4-5 is Q2's
> number.

State what was wrong, what is right, and stop. No apology paragraph, no
re-litigating how the error happened, no tallying of past mistakes. The
correction is a fact the reader needs; the self-criticism is not.

Correct an earlier statement only when the error changes what the reader would
conclude or do. A slip that changes nothing needs no announcement.

The same applies when your first framing was incomplete rather than wrong -
"I pinned the coverage gap entirely on the transcript window; there is a
second, independent cause" is a correction worth making, because the reader
would otherwise fix the wrong thing.

## What never to do

**Never fill a gap with something plausible.** An empty slot that says *why*
it is empty - "the transcripts this repo holds for this sector begin
2025-10-17; this turn is 2021-01-08" - is information. The same slot filled
with a reasonable-sounding sentence nobody checked is the exact failure mode
this discipline exists to prevent, and it is invisible to the reader.

**Never let proximity pass as causation.** A dated event near a turn is
something to read, not a cause. Where you surface one, say which it is and
show the distance, so a seven-day gap cannot read like an eighty-nine-day one.

**Never quote a rate without its denominator and its comparator.** "53.5% of
strong prints were shrugged off" reverses its own sense once you learn the
figure for ordinary prints is 57.0%.

**Never answer a scope question from the summary that is closest to hand.**
Project files drift from the sources they describe. Check which one is
authoritative for the specific claim, then read that.

## Worked example

**Question:** "Is the transcript read required or not for the Q1 output? Give
me a solid reason."

**What the loop produced:**

- Read `docs/GRILL-SHEET.md` Q1 verbatim rather than the CLAUDE.md summary -
  which surfaced that its green flag is a disjunction, so the answer is
  *conditional*, not yes or no.
- Counted the condition against the committed CSV: the acknowledged leader
  lagged in **5 of 20** sectors; those five are the ones that require it.
- Found the number that hurt: in **0 of those 5** had the existing concall run
  read the sector's acknowledged leader.
- Marked the unverifiable: market-cap rank could not be checked from this
  clone, and named where it could be.
- Corrected an earlier claim of mine about roster size, in two sentences.
- Sized the fix: **10 transcripts**, not the much larger job proposed before
  the measurement.

The answer's load-bearing sentence was not any of the counts. It was the
structural point they supported: without the transcript, Q1's arithmetic
passes every sector and the question degrades into a test that cannot fail.
Measurement earns you the right to make that kind of claim.
