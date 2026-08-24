---
name: grill-me
description: Interview the user relentlessly about a plan, design, or topic, checkpointing every answer to a brainstorm file so nothing is lost. Use when the user wants to stress-test a plan, get grilled on a design, run a brainstorm or discovery session, extract what's in their head into a doc, or says "grill me".
---

# Grill Me

> **Provenance (vendored 2026-08-24).** Supplied by the repo owner, who took it
> from Nate Herk's "5 levels of a Claude Code second brain" video
> (`youtu.be/DTCyvo6cC54`), where he credits **Matt Pocock** as the original
> author and notes he customised it. The method text below is reproduced as the
> owner supplied it, with only character-encoding repairs; the *Where captures
> live* and *Why this exists* sections are this repo's own additions. Pinned
> in-repo rather than plugin-installed, per the same reasoning as
> `karpathy-guidelines`: a skill steers future sessions, so its text must not
> change under us. Reviewed before install — pure prose, no scripts, hooks,
> network calls, or postinstall steps.
>
> **Relationship to `brainstorming`.** These overlap and do not replace each
> other. `superpowers:brainstorming` is a *design* process — it ends by writing
> a spec and handing off to `writing-plans`, and it gates on user approval.
> `grill-me` is an *extraction* process — it has no deliverable but the capture
> file, and it does not stop to design. Use `brainstorming` when you are going
> to build the thing. Use `grill-me` when the knowledge is in the user's head
> and the goal is to get it onto disk. When both apply, brainstorming wins on
> anything that will become code.

Relentlessly interview the user about every aspect of the topic until you reach
shared understanding. Walk down each branch of the decision tree, resolving
dependencies one by one. The real goal is to **extract what's in their head into
a durable, organized markdown file** so nothing is lost as context fills up.

## The capture file is the whole point

Long interviews fill up context. If you hold answers only in your head, you will
eventually misremember, conflate, or drop something. So you **checkpoint to disk
after every single answer**. The file, not your context, is the source of truth.
Never make the user ask you to save progress.

## Setup (do this BEFORE the first question)

1. **Create the capture file** at `brainstorms/{YYYY-MM-DD}-{topic-slug}.md`
   (create the `brainstorms/` folder if it doesn't exist). Every brainstorm
   capture lives here. One predictable home, regardless of topic. Do NOT scatter
   captures into project folders. If a session later produces a polished
   deliverable (a plan, a map, a spec), that artifact can move into the relevant
   project folder, but the raw capture always stays in `brainstorms/`.
   - Get today's date with `date +%F` (Bash) if you don't already know it.
2. **Create the file immediately** with a header: title, date, the goal of the
   session, and an empty "Open flags" section.
3. **Tell the user where you're saving**, in one line. Then ask Q1.

## The checkpoint rule (non-negotiable)

After EVERY user answer, BEFORE you ask the next question:

- Append a structured entry to the capture file: the question topic, the key
  facts and decisions from their answer (in their words where the wording
  matters), and any flags (things they couldn't answer plus who should).
- Update or correct earlier entries if a later answer changes them.
- Only then ask the next question.

Never batch multiple answers into one write. Checkpoint one answer at a time.
The point is that if context is lost at any moment, the file already holds
everything said so far.

## Interview method

- Ask **one question at a time**. For each, provide your **recommended answer**
  (your best inference from context) so the user can simply confirm, correct, or
  redirect.
- Resolve dependencies in order: settle the upstream decision before the ones
  that depend on it.
- If a question can be answered by **exploring the codebase or reading a
  file/doc**, do that instead of asking. If the user hands you a doc (e.g. a
  Google Doc), read it and only surface what's net-new.
- When the user **can't answer** something, capture it as a flag with the right
  owner and move on. Don't stall.
- Keep going until the user says you're done, or you've covered every branch.
  Offer a completeness backstop near the end ("anything we haven't touched?").

## Capture file structure

```
# {Topic}: Brainstorm / Discovery Notes
Date: {date} · Goal: {one line}

## Summary / key decisions
(running synthesis, updated as you go)

## Q&A log
### Q1 — {topic}
- Asked: {question}
- Captured: {facts, decisions, in their words where it matters}
- Flags: {open item -> owner}
...

## Open flags (pending input)
- {item} -> {who can answer}
```

## At the end

- Do a final read of the capture file for contradictions or gaps and reconcile
  them.
- Give the user a short recap: what's captured, what's still flagged, and the
  suggested next step.

---

## Where captures live in this repo

`brainstorms/` at the repo root. It is **gitignored by default** — captures are
the owner's own unfiltered thinking and may contain client, business or personal
detail, which is the same instinct behind this repo's rule that nothing captured
is ever committed. Gitignoring does not hide the folder from local tooling:
`graphify` still reads it, so captures reach the knowledge graph without
reaching the remote. To commit a specific capture deliberately, `git add -f` it,
or drop the `brainstorms/` line from `.gitignore` if the owner decides the whole
folder should be tracked.

## Why this exists (the knowledge-graph half)

The video this came from makes the point that matters here: people assume the
hard part of a second brain is **retrieval**, when the harder part is usually
**getting what you know out of your head and into the system at all**. A graph
can only relate what has been written down.

This repo already has strong retrieval — a committed `graphify` graph
(`graphify-out/`), the `vault-ask` router, per-source vaults, and a
`docs/reassessment/` corpus where every claim traces to a quote-gated source.
What it has no mechanism for is **capture of the owner's own undocumented
reasoning**: why a threshold was chosen, what a rule was meant to encode, which
alternatives were rejected and why.

That gap has already cost this repo real work. The `soic-ladder` rulebook's
`pe_context-001` carries `ref: null` and `growth_trap_flag-001` cites a
timestamp that does not exist in the lecture it names — both because the
reasoning behind them was never written down at the time. A `grill-me` session
run while authoring those rules would have produced exactly the record that is
now missing.

So the intended loop is:

1. `grill-me` extracts reasoning into `brainstorms/`.
2. `/graphify .` re-extracts code **and** docs, so captures become nodes and
   edges alongside the source they explain.
3. Later sessions read the graph first (see `CLAUDE.md` § START HERE) and
   inherit the *why*, not just the *what*.

Run `/graphify .` after a substantial capture, the same as after any docs
change — the post-commit hook only flags the graph stale, it never rebuilds.
