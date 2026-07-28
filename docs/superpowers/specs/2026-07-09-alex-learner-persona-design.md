# Alex the Learner — persona-wiki learning loop (Apache Spark)

**Status:** Design (approved in brainstorming, pending spec review)
**Date:** 2026-07-09
**Scope:** Proof-of-concept. One learner (`alex`), one source persona (`vutr`), one
topic (`spark`). Autonomous learning loop; grounded, closed-book; captures Alex's
learning into his own growing wiki.

---

## Motivation

The Decoding AI "LLM wiki / agent memory" article claims an LLM wiki is something
agents **query, maintain, and grow**. We have the *query* half (`persona-wiki
query` over the `vutr` wiki). This feature demonstrates the other half with a
concrete second agent: **Alex**, a 15-year-old learner, learns Apache Spark
*by querying* the `vutr` wiki and *grows his own* wiki of captured learning. The
result is a verifiable, inspectable artifact of the article's claim.

Alex is the existing `alex` persona (a 15-year-old clarity auditor —
`.claude/agents/alex.md`), here in a **learner** role: curious, thinks out loud
("wait, so… okay but then why…"), no prior data-engineering knowledge, honest
about confusion.

## Goals

- Alex goes **0 → 100** on Apache Spark, mastering vutr's 16 Spark concepts.
- Every answer Alex learns from is **grounded, closed-book** in vutr's Spark wiki
  notes — his knowledge is provably sourced from the vault.
- The learning interaction (Q&A, Alex's own understanding, confusions, mastery
  progression) is **captured into `wiki/personas/alex/spark/`** — a living wiki
  that grows as Alex learns.
- A full **human-readable end-to-end transcript** of the entire learning process
  is produced (`transcript.md`) so a person can read Alex's whole journey as a
  dialogue and learn from it alongside him.
- **Diagrammatic learning:** Alex's concept notes include a simple Mermaid diagram
  where the concept has genuine visual structure (flow, hierarchy, decision) — a
  token-cheap, Obsidian-native visual aid for a 15-year-old.

## Non-goals

- Other topics/streams (career, kafka, …) — Spark only for now; the design
  generalizes via `--topic`.
- Interactive "you are Alex" mode — deferred; the autonomous loop is built first.
- Teaching-pack PDFs or the examiner/verification loop — separate machinery.
- Modifying the `vutr` wiki — it is read-only source of truth here.

---

## The 16 Spark concepts (vutr wiki atomic notes)

Learned in a **pedagogical order** (foundational → advanced), not the file order:

1. `spark-origin` → 2. `rdd` → 3. `lazy-evaluation` → 4. `catalyst-optimizer` →
5. `adaptive-query-execution` → 6. `executor-memory-model` →
7. `shuffle-writes-to-disk` → 8. `data-skew-oom` → 9. `sort-merge-join` →
10. `shuffle-hash-join` → 11. `data-locality` → 12. `jvm-object-overhead` →
13. `pyspark` → 14. `spark-structured-streaming` → 15. `photon` →
16. `remote-shuffle-service`.

The order is a static list in the module (curated once); anything vutr adds later
that isn't in the list is appended at the end.

## The learning loop (per concept)

```
for concept in ORDER (repeating unmastered ones, up to a retry cap):
  1. TEACH   — vutr agent reads ONLY that concept's vutr note + returns a
               15-year-old-level explanation (closed-book: no outside facts).
  2. REFLECT — alex agent restates it in his own words, flags confusions,
               asks 1–2 grounded follow-up questions.
  3. ANSWER  — vutr agent answers the follow-ups from the wiki; a question the
               wiki cannot answer is returned as an explicit gap (not faked).
  4. SCORE   — vutr agent judges whether Alex's restatement covers the concept
               note's key points → level: learning | familiar | mastered.
  5. CAPTURE — write Alex's concept note (+ optional Mermaid), the Q&A note,
               update open-questions + mastery.md, append to log.md.
```

Mastery: overall % = `mastered / 16`. A concept re-enters the queue if it scored
below `mastered`, up to a retry cap (e.g. 2) after which it is recorded at its best
level with its gaps noted (honest 0→100: "94% — 15 mastered, 1 familiar (gap: …)").

## Alex's wiki structure (`wiki/personas/alex/spark/`)

Reuses persona_wiki plumbing (YAML-frontmatter notes, `index.yaml`, append-only
`log.md`, `[[wikilinks]]`, `storage.write_note` path guard).

```
wiki/personas/alex/
  spark/
    concepts/<slug>.md      # Alex's OWN understanding, 15-yo voice; links [[vutr source]];
                            #   optional ```mermaid diagram where the concept has structure
    qa/<nnn>-<slug>.md       # one exchange: question, vutr's grounded answer, "what I got",
                            #   follow-ups + their answers/gaps
    open-questions.md        # Alex's lingering confusions + genuine wiki gaps
    mastery.md               # 0→100 tracker: table (concept | level | source) + overall %
    transcript.md            # full human-readable dialogue of the WHOLE learning run
    index.yaml               # catalog of Alex's notes
    log.md                   # append-only learning log (when Alex learned what)
```

### The transcript (`transcript.md`)

The full learning process, written as a readable dialogue in concept order, so a
person can review and learn from it. Append-only across the run; each concept adds
a section:

```
## 2. RDD  (mastered)

**vutr teaches:** <the 15-yo explanation>

**Alex:** <restatement in his voice> "wait, so… okay but then why…"  <follow-ups>

**vutr answers:** <grounded answers, or an explicit "the wiki doesn't cover that">

**Verdict:** mastered — Alex's restatement covered lazy DAG building + the 5 RDD
properties.  ·  Diagram added: yes.
```

It is the linear narrative counterpart to the structured `qa/` notes: `qa/` is
atomic and queryable, `transcript.md` is the story end to end. A short header links
`[[mastery]]` and lists the concept order so it doubles as a table of contents.

Alex's concept-note frontmatter records provenance: `learner: alex`, `topic: spark`,
`source_note: <vutr slug>`, `mastery: mastered|familiar|learning`, `last_updated`.

### Diagram policy (token-cheap)

- Format: native ```mermaid``` blocks only (text; renders in Obsidian desktop +
  mobile). No image generation.
- Include **at most one** small diagram per concept note, and **only** where the
  concept has real visual structure — e.g. `rdd` (transformations→DAG→action),
  `shuffle-writes-to-disk` (map→disk→reduce), joins (a `BROADCAST > MERGE >
  SHUFFLE_HASH` decision tree), `executor-memory-model` (reserved/unified split).
  Concepts that are purely definitional get no diagram. The teach/capture prompt
  instructs "add a simple mermaid diagram ONLY if it genuinely clarifies flow or
  structure; otherwise omit."

## Architecture

- New module `src/persona_wiki/learn.py` — the loop orchestrator + capture. Pure
  logic behind the injectable LLM seam (`Callable[[str], str]`); no direct I/O to
  the network in tests.
- New prompt builders in `learn.py` (or `llm.py`): `build_teach_prompt`,
  `build_reflect_prompt`, `build_answer_prompt`, `build_score_prompt` — each takes
  the relevant vutr note text (closed-book context) and the running state.
- Reads the source concept notes via the existing vutr wiki files (a
  `load_topic_concepts(vutr_root, topic)` helper reading `index.yaml` + notes).
- New CLI command `persona-wiki learn --learner alex --from vutr --topic spark
  [--vault-dir …] [--max-retries N] [--dry-run]`. `--dry-run` prints the concept
  order + prompts, calls no LLM.
- Real run: the LLM seam is fulfilled by Claude **agents** (teacher + learner),
  same transport used to build the vutr wiki (nested `claude -p` 401s in-session).

## Data flow (one concept, end to end)

```
concept "rdd"
  → load vutr note wiki/personas/vutr/entities/rdd.md (closed-book context)
  → TEACH(rdd note) → 15-yo explanation
  → REFLECT(explanation) → Alex restatement + confusions + follow-ups
  → ANSWER(follow-ups, rdd note) → grounded answers / explicit gaps
  → SCORE(restatement, rdd note) → "mastered"
  → CAPTURE:
      concepts/rdd.md         (Alex's words + mermaid DAG)
      qa/001-rdd.md           (the exchange)
      open-questions.md       (any gap appended)
      mastery.md              (rdd → mastered; overall % updated)
      transcript.md           (this exchange appended as a readable dialogue section)
      index.yaml, log.md      (registered + logged)
```

## Error handling

- **Closed-book violation guard:** the score step also flags if the teach/answer
  introduced a claim not in the source note; flagged content is captured under
  `open-questions.md` as "unverified (not in vutr wiki)" rather than as fact.
- **LLM/JSON failure on a step:** that concept is skipped this pass (no partial
  note), counted, and retried next pass; the run never aborts mid-topic.
- **Retry cap reached:** concept recorded at best level with gaps; loop continues.
- **Path guard:** all writes go through `storage.write_note`, confined to
  `wiki/personas/alex/`.
- **Idempotent re-run:** a concept already `mastered` in Alex's index is skipped
  (no repeat LLM call), mirroring `update`'s source-dedup.

## Testing (offline, stubbed LLM)

- **Loop:** concept ordering; unmastered concept re-enters queue; retry cap;
  idempotent skip of already-mastered.
- **Mastery math:** % = mastered/total; honest partial (familiar/learning counted).
- **Capture/structure:** concept + qa + mastery + open-questions + transcript
  written; index and 4-shape log updated; frontmatter provenance present.
- **Transcript:** each processed concept appends one readable dialogue section (in
  concept order) with teach/Alex/answer/verdict; re-running an already-mastered
  concept does not duplicate its section.
- **Diagram gating:** a stubbed teach output with a mermaid block is preserved in
  the concept note; without one, the note still writes cleanly (no empty fence).
- **Grounding guard:** a stubbed "unverified" score routes the claim to
  open-questions, not the concept body.
- **Path guard:** a write outside `wiki/personas/alex/` is rejected.

## Verification of the article claim

After a real run, the artifact proves the loop worked:
- `mastery.md` shows Spark at (near) 100% with a per-concept trail.
- Every `concepts/<slug>.md` links `[[<vutr source>]]` — knowledge sourced from the
  vault (query half).
- `log.md` shows the wiki grew concept-by-concept (grow half).
- `qa/` + `open-questions.md` capture the actual interaction for future reuse.
- `transcript.md` is the full readable dialogue of the run — the reviewable
  end-to-end record of how Alex went 0→100.

## Resolved decisions (from brainstorming)

1. **Learning mode:** autonomous Alex↔vutr loop (0→100), inspected after.
2. **Grounding:** closed-book — vutr answers only from its Spark wiki.
3. **Mastery:** mastered/16; a concept is `mastered` when Alex's restatement covers
   the source note's key points (vutr scores); honest partials allowed.
4. **Structure:** new `learn.py` + `persona-wiki learn` command reusing persona_wiki
   plumbing; not bolted onto `update`.
5. **Diagrammatic learning:** one optional native Mermaid block per concept note,
   only where it clarifies flow/structure — token-cheap, Obsidian-native.
