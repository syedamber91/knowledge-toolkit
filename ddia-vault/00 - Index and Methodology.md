---
title: Index and Methodology
area: Meta
topic: How This Course Teaches
tags: [ddia, methodology, index, learning]
---

# DDIA Learning Vault — Index & Methodology

This vault teaches **_Designing Data-Intensive Applications_** by Martin Kleppmann
(O'Reilly, 2017) — "the DDIA book" — as a connected course a curious 15-year-old
can follow. The book is the **single source of truth**. Where the book simplifies,
this vault says so; where a topic is deep, this vault climbs more levels. Nothing
here is invented beyond what the book teaches — and where a lesson leans on outside
context, it is flagged as such.

> **Start here:** read this file, then [[01 - Roadmap]], then follow the chapters in
> order from [[Ch01 - Reliable, Scalable, Maintainable Applications]].
> The hub note is [[Home]].

## The Teaching Panel (every lesson passes all five lenses)

1. **The Master Teacher** — sequences ideas from known to new, defines every term in
   plain English, owns pacing and prerequisites.
2. **The Working Engineer** — supplies the concrete, named real-world use case
   ("where does this actually show up?").
3. **The Honest Skeptic / Misconception-Buster** — surfaces the traps beginners fall
   into and names trade-offs and limits. Always fills COMMON MISCONCEPTIONS.
4. **The Curriculum Architect** — maps each topic onto the vault, wires `[[wikilinks]]`
   to prerequisites and related notes, and designs the memory hook.
5. **The 15-Year-Old (Comprehension Gate)** — flags any jargon, undefined term, or
   logical leap a sharp teenager would not get. Nothing ships until this lens passes.

**Editorial board (final pass):** the Prolific Author (rigor, no filler), the
Voracious Reader (narrative flow, memorable framing), and the Rocket-Science
Professor (make the single hardest part click with a diagram).

## The Lesson Template — a Levelled Ladder

Every chapter lesson climbs the same ladder, so you always know where you are:

- **Recap — Where We Just Were** — 1–2 sentences bridging from the previous lesson.
- **Level 1 — The Big Idea** — plain-English definition, an everyday analogy, and the
  simplest possible diagram.
- **Level 2 — How It Actually Works** — the real mechanism, step by step, with a flow
  diagram. Teaches the "why under the why."
- **Level 3 — See It With Real Numbers** — one concrete case with real values plus a
  short `sql` / `bash` / `python` snippet showing input → steps → result.
- **Level 4 — In the Real World & Common Traps** — a named use case (e.g. how a real
  system does it) plus 2–3 misconceptions as "People think X — actually Y."
- **Level 5+ — Expert View** — how the idea relates to and differs from neighbouring
  concepts (a contrast table), trade-offs (when to use it and when not), and edge
  cases. Extra levels only for genuinely hard chapters.
- **Check Yourself** — a one-line memory hook, then exactly 3 self-test Q&A.
- **Connects To** — `[[wikilinks]]` to prerequisite and related concepts.
- **Coming Up Next** — the next chapter's `[[wikilink]]` and why it follows.

## Presentation Contract (non-negotiable)

- **Connected course.** Each lesson recaps the previous chapter and points to the
  next; the vault reads as one path, not isolated notes.
- **Reading level: a 15-year-old.** Short sentences. No undefined jargon. Every new
  term gets a one-line gloss on first use.
- **Diagrams are mandatory.** At least one small `mermaid` diagram in Level 1 and one
  in Level 2, more wherever a picture beats words. Boxes + arrows, ByteByteGo-style.
- **Depth target ~1,200–2,000 words** per chapter — long enough to teach, never padded.
- **Vault-ready Markdown:** YAML frontmatter (`title, area, topic, tags`) + body,
  cross-referenced with `[[wikilinks]]`.
- **Honesty clause:** if the book's treatment of something is subtle, the lesson says
  "I'm simplifying" rather than faking confident detail.

## Toggles ON for this run

- **Granularity:** one laddered lesson per **chapter** (12 chapters). DDIA chapters are
  dense; folding each chapter's core concepts into one connected ladder reads better
  than exploding each into many stubs.
- **Diagrams:** Mermaid, on by default.
- **Cross-linking:** inter-chapter `[[wikilinks]]` + a [[Home]] map + an append-only
  [[Log|Ingestion Log]], matching this repo's *index + log + cross-links* convention.
- **Source fidelity:** grounded in the 2017 first edition's structure and examples.

## Files in this vault

| File | Purpose |
|------|---------|
| [[00 - Index and Methodology]] | this file — how we teach |
| [[01 - Roadmap]] | the 12-chapter syllabus, order, prerequisites, milestones |
| [[Ch01 - Reliable, Scalable, Maintainable Applications]] … [[Ch12 - The Future of Data Systems]] | the lessons |
| [[Home]] | map-of-content hub |
| [[Log\|Ingestion Log]] | append-only history of what was added and when |

Next: [[01 - Roadmap]].
