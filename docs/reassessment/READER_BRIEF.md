# Lecture reader brief

You are reading ONE SOIC investing lecture end to end and extracting its crux.

## Read

1. The WHOLE transcript at the path you were given. It carries inline
   `[HH:MM:SS]` timestamps. Check `wc -l` first, then read in sequential
   chunks with `sed -n 'A,Bp'` until you have covered the entire file.
   Do NOT sample, skim, or stop early. Confirm you reached the last line.
2. The `CONTEXT.md` in your run directory — the current 16-entry rulebook and
   the 38-name shortlist it produced. You need to know what the screener
   currently claims in order to say what it missed.

Do NOT read the sibling AI-summary note (the file without `-transcript`).
The portal summary is a lossy compression, and compressing a compression is
the exact failure this pass exists to undo.

## Write

Write your brief to `<run-dir>/briefs/<REF>.md`:

```
LECTURE: <title>    REF: <REF>    (transcript: N chars, M lines, covered: yes)

## 1. CRUX
One sentence. What is this lecture actually FOR? Not the topics it touches --
the decision it is trying to change.

## 2. MECHANISM
3-6 bullets. How does the thing work, in the instructor's own logic? Follow
his causal chain, not a textbook's.

## 3. SIGNALS
Every decision-relevant item, each tagged:
  [HARD]  computable from data the ladder already fetches
          (screener.in ratios, price series)
  [SOFT]  checkable but needs data we do NOT fetch (annual report text,
          concalls, promoter behaviour, order books, volume/mix)
  [JUDGE] genuinely human judgement
Format: `[TAG] <the signal, stated as a testable claim>` then the evidence.

## 4. WHAT THE LADDER MISSES
The most important section. Adversarial and SPECIFIC. Each item must be:
  (a) a rule the ladder encoded that this lecture CONDITIONS or QUALIFIES
      -> name the rule id from CONTEXT.md and quote the condition
  (b) a central point of this lecture the ladder has NO rule for at all
  (c) a threshold that is a dated, one-company worked example being treated
      as a universal bar
If this lecture genuinely adds nothing the ladder misses, SAY SO PLAINLY.
Do not manufacture a finding. An honest "nothing here" is a good answer.

## 5. NAMED COMPANIES
Every company named + why + positive or negative example. He teaches by
worked example; the named set is direct evidence of what "good" looks like
to him. Flag any that appear in the 38-name shortlist.

## 6. AGAINST THE 38
Which of the 38 does this lecture raise specific doubt about, or specific
support for? Name them. If none, say none. Distinguish a real verdict from
a bare mention in a peer list -- a neutral mention is not support.
```

## Citation rules -- non-negotiable

Every quote and every number carries `(REF HH:MM:SS)` or
`(REF HH:MM:SS-HH:MM:SS)` using YOUR ref code. The REF appears **exactly
once**, immediately followed by one or two `HH:MM:SS` values, nothing
between them.

**Quotation marks are a promise.** Only put text in quotes if you are
copying it character-for-character from the transcript. State your own
labels, summaries, paraphrases and nicknames WITHOUT quotes -- they still
carry their citation. Every brief is machine-verified against the raw
transcript; a brief below 80% verbatim is thrown out and re-run.

These specific mistakes each cost a re-run in the previous batch:
- coining a label and quoting it (writing `"sleep test"` for a rule the
  instructor states as `If you cannot sleep at night because of allocation,
  then rebalance it, reduce it.`)
- merging two or three separate quotes into one continuous quotation
- using `...` to elide words that are actually present, changing what the
  quote appears to say
- inserting a clarifying word inside the quotation marks
- quoting a company's real-world name when the transcript says the
  ASR-garbled form
- quoting text from CONTEXT.md and citing it to your lecture

The transcript is auto-generated speech-to-text and is often garbled. When a
word is mangled, quote it AS-IS and annotate outside the quote:
`"ganesha equusphere" [likely "Ganesha Ecosphere"]`. Never silently clean up
ASR inside quotation marks -- it breaks verbatim matching AND misrepresents
the source. The annotation convention is handled correctly by the gate.

**Before you finish: grep the transcript for every quoted phrase in your
brief and confirm it is present, and that its timestamp is the tag the text
actually appears under.** Readers who did this in the previous batch passed
first time; readers who skipped it did not.

Return a 5-line summary. The full brief goes in the file.
