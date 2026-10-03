---
name: checking-scope
description: Use when the user asks whether the conversation is still on track, what the original purpose was, or whether work has drifted from it — especially after a long multi-topic session or a handoff/compaction from a prior conversation.
disable-model-invocation: true
---

# Checking Scope

> **Provenance (authored 2026-10-03).** Written this session, by request,
> after checking `github.com/mattpocock/skills` first — nothing there
> covers this. The closest neighbours are `wait-what` (re-pitch the LAST
> message, not a whole-session audit), `retro` (post-hoc review of the
> coding *environment*, not of whether the session stayed on purpose), and
> `wayfinder` (plans large multi-session work via an issue tracker; this
> skill instead retrospectively audits a session already in progress).
> None overlap enough to extend. The procedure below was drafted, then
> adversarially reviewed by a Fable-tier pass before being written here —
> that review is what added the `(b*) open pivot` tag, the initiator field
> on deviations, and the trivial-case escape in step 4; see git history
> for the pre-review draft if it's ever worth comparing.

## Overview

Audits a conversation against its own stated purpose: what was asked at
the start (or at a handoff boundary, if this session continues one), what
has happened since, and whether any of it quietly became a different
investigation. User-invoked only (`disable-model-invocation: true`) —
running this on every turn would be noise, and silently reporting "on
track" by default is exactly the failure this skill exists to catch.

## Procedure

1. **Root purpose — quote it, don't paraphrase it.** Find the earliest
   boundary in this session: a system-reminder compaction summary, a
   referenced handoff doc or plan file, or (if neither exists) the first
   user message. Quote the purpose verbatim with its location. If it
   comes from a summary rather than primary text, say so explicitly — a
   summary can flatter or compress what was actually asked. If no purpose
   can be quoted, say that and ask, rather than inventing one. Never widen
   it mid-audit ("the purpose was *really* to...") — that is how real
   drift gets laundered into "on track."

2. **Timeline — one line per major move, tagged with evidence, not vibes.**
   - **(a) direct service** — names which part of the root purpose it
     advances.
   - **(b) pivot** — earns this tag only with three things cited: the
     blocker that forced it, the sentence connecting it back to the root
     purpose, and whether it ever returned. No return yet → tag it
     **(b\*) open pivot**, not (b). A pivot that never closes the loop is
     a deviation wearing a justification.
   - **(c) deviation** — a different question, even if topically related.
     Note who started it — user- or agent-initiated. An agent-initiated
     deviation the user never asked for or approved is the finding that
     matters most, since the agent has the strongest incentive to not
     surface it.
   If the evidence (a) or (b) requires can't be cited, it's (c). Default
   to the less flattering tag.

3. **Verdict: MET / NOT MET / PARTIAL.** PARTIAL must name the specific
   unmet deliverable from step 1 and the last turn any work happened on
   it. "Partially met" with nothing named is a dodge, not a verdict.

4. **Per (c) and (b\*) — resolve, don't just narrate.**
   - Nothing in flight and no tool calls were spent on it → report
     "closed tangent, no action" and move on; that's a finding, not a
     decision point.
   - Otherwise offer exactly two options and pick neither:
     **BRANCH** (name precisely what carries over — a plan file, a diff,
     a result — so branching is never just a polite way to drop it), or
     **STOP** (name precisely what gets abandoned). The user decides.

5. **The audit itself is not progress.** Running this skill doesn't
   advance the root purpose — don't count it as a step toward MET.

## Common mistakes

| Mistake | Fix |
|---|---|
| Inferring the root purpose from your own earlier summary of a handoff, not the handoff's own text | Quote the primary source with its location; mark it "reconstructed from summary" if that's all that exists |
| Calling any pivot-with-a-reason "(b) justified" | (b) requires a cited return path; no return means (b\*) — a deviation in disguise |
| "Partially met" with no named gap | Always name the specific unmet deliverable and when work on it stopped |
| Reading the session from memory instead of re-reading it, especially across a compaction boundary | Re-read; a flattered recollection of the pre-compaction half is the most common way drift gets missed |
| Deciding BRANCH or STOP for the user | Present both, name what each one carries or drops, then stop — the user picks |

## Output shape

```
Root purpose: "<verbatim quote>" (<location>)

Timeline:
- <move> — (a)/(b)/(b*)/(c) <evidence or initiator>
...

Verdict: MET / NOT MET / PARTIAL — <unmet deliverable, if any>

Deviations found:
- <deviation> — BRANCH (carries: <...>) or STOP (abandons: <...>)?
```
