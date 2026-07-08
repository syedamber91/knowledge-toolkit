# Persona Wiki POC — incremental research-memory derivatives for the `vutr` persona

**Status:** Design (approved in brainstorming, pending spec review)
**Date:** 2026-07-08
**Author:** brainstormed with Claude
**Scope:** Proof-of-concept. One persona (`vutr`), one flavor (research memory), all 7
pipeline steps, kept deliberately lightweight.

---

## Motivation

This repo's personas (`.claude/agents/vutr.md`, `nate-herk.md`, etc.) are **one-time,
hand-authored knowledge snapshots**. `vutr.md` is a single ~700-line file with Vu Trinh's
technical positions baked into the agent prompt as prose. There is **no mechanism** to
update a persona when new source content is captured: if `substack-capturer` pulls in five
new Vu Trinh posts, nothing downstream ever touches `vutr.md`. The new material sits
captured, catalogued, and invisible to the `/vutr` persona until a human manually rewrites
the file.

The "LLM wiki" pattern (from *Decoding AI*,
<https://www.decodingai.com/p/llm-wiki-agent-memory>) solves exactly this: instead of
re-deriving knowledge from raw documents on every query (the RAG pattern), an LLM
**incrementally builds and maintains a persistent, interlinked wiki** of derivatives over
raw sources. This POC applies that pattern, scoped per-persona, to close the "persona
knowledge cannot grow without manual rewriting" gap.

Persona scope is a natural fit for the article's PARA-style boundary: one persona = one
author's corpus, already a clean, self-contained unit.

## Goals

- A persona's knowledge on a topic can be **incrementally revised** as new sources are
  captured, rather than regenerated from scratch or hand-authored.
- Derivatives are **research memory for an agent** (entities, concepts, comparisons, open
  questions, synthesis) — optimized for machine retrieval and reuse, not human study.
- The system carries a **CDC (change-data-capture) record**: every note declares which
  sources fed it and when it last changed; an append-only log records the history.
- **Atomic, referenced storage** (article-faithful): entities and concepts are their own
  notes, deduplicated across topics, cross-linked via `[[wikilinks]]` so Obsidian's graph
  renders real concept-to-concept edges.

## Non-goals (explicitly out of scope for the POC)

- **Teaching derivatives** (flashcards, decision trees, "when to use which"). These are a
  different flavor aimed at a human learner and are already served by the existing
  Spark-pack generation + verification workflow (`scripts/generate_vutr_spark.py` and the
  persona verification loop). Not rebuilt here.
- **Automatic triggering.** The POC runs manually. Wiring into `substack-capturer` /
  `youtube-capturer` completion hooks is a later step.
- **Other personas.** Only `vutr` is piloted.
- **Rewiring the live `/vutr` agent.** The existing static `vutr.md` persona is left
  untouched. Querying the new wiki is a separate, additive entrypoint.
- **A deep-research web loop** (multi-round query generation, source ranking, scraping).
  The POC derives from sources already captured in this repo's catalogs, not from fresh
  web research.

---

## Placement

`learning-vault` is its own git repo (the `de-toolkit` project, at the iCloud Obsidian
path). This repo (`knowledge-toolkit` / SOIC_Scraper) is where the personas live. The two
are kept in their established roles:

| Concern | Location | Rationale |
|---|---|---|
| POC **code** | `src/persona_wiki/` in **this** repo | Mirrors `media_core`: code lives here, writes Obsidian notes into an external configurable vault dir. |
| Derivative **output** | `learning-vault/wiki/personas/vutr/` | Reuses the learning-vault's existing empty `wiki/` synthesized-layer namespace, honoring its read-only contract (never touches the authored course, `data/`, or `src/de_toolkit/`). |
| Vault dir config | env var (e.g. `PERSONA_WIKI_DIR`) | Same override pattern as `MEDIA_VAULT_DIR`. |

Nothing is deleted. The authored dbt course and the existing `wiki/` scaffolding
(`index.md`, `log.md`, `hot.md`) stay intact; `wiki/personas/` is a net-new subtree.

**Why the learning-vault:** its `CLAUDE.md` / `WIKI.md` already enforce the article's
read-only-source + synthesized-derivative split, already carry an index + append-only log,
and the `wiki/` derivative namespace was scaffolded but left essentially empty. This POC
populates a layer that repo already designed a home for.

---

## Architecture — the 7-step pipeline

Running example throughout: persona `vutr`, topic `kafka`, a newly captured post
"Kafka Tiered Storage."

### Step 1 — Raw capture (reuse existing)
Sources are already captured by `substack-capturer` / `youtube-capturer` into their
catalogs (`data/substack.json`, `data/media.json`) and raw notes. The POC **reads** from
these; it captures nothing new. This is the article's immutable `raw/` layer.

### Step 2 — Derivative writer (new)
An LLM reads the raw source(s) for a topic plus the current derivative notes (if any) and
writes/revises research-memory derivatives in Vu Trinh's grounded positions. Produces the
article's five kinds, stored per the **atomic storage model** below. No teaching
scaffolding. The LLM call sits behind an injectable seam (see Testing).

### Step 3 — Change detection / CDC (new)
`match_topics()` (reused from `media_core`/`substack_toolkit` — deterministic keyword
match) maps each new source to topics and entity candidates. The index is consulted to
decide, per topic **and** per entity/concept: **REVISE** an existing note (feed the LLM the
old note + new source, ask for an in-place revision) or **CREATE** a new one. This is the
mechanism that makes the wiki incremental rather than regenerated-from-scratch.

### Step 4 — Index (new)
`index.yaml` is the catalog an agent reads **first**, before opening any note. It maps
every topic and atomic note to its file, source list, and last-updated date — enabling
progressive disclosure.

### Step 5 — Query entrypoint (new, lightweight)
An additive `/vutr-wiki <question>` path: read `index.yaml` → open the relevant topic note
→ follow `[[wikilinks]]` to entity/concept notes only as needed → answer from that content.
The existing static `/vutr` persona is **not** rewired in the POC.

### Step 6 — PARA scoping (fully isolated)
`wiki/personas/vutr/` reads **only** Vu Trinh's own captured sources. It never reads or
writes the global `topics/*.md` cross-link notes, and never mutates the learning-vault's
authored course. Persona corpora do not bleed into each other.

### Step 7 — QC pass (new, single check)
After step 2 writes/revises a note, one LLM pass verifies that each claim traces to a cited
source and flags overreach (e.g. a conditional source claim rewritten as an absolute one).
On failure, the note is flagged (frontmatter `qc: failed` + a reason) and not blessed into
the index until resolved. This is a single guardrail, **not** the full multi-agent
verification loop used for the teaching packs — that loop is reserved for human-facing
material.

---

## Storage model (atomic notes + references — "Option 2")

```
learning-vault/wiki/personas/vutr/
  topics/
    kafka.md            # synthesis + comparisons + open questions; links out to entities/concepts
    spark.md
  entities/
    lsm-tree.md         # written ONCE; referenced by kafka.md AND spark.md via [[lsm-tree]]
    franz-kafka.md
  concepts/
    log-compaction.md
  index.yaml            # the catalog read first
  log.md                # append-only CDC history
```

The five article-kinds map onto this layout as:
- **entities** → `entities/<slug>.md` (atomic, deduplicated, shared across topics)
- **concepts** → `concepts/<slug>.md` (atomic, deduplicated)
- **comparisons**, **open questions**, **synthesis** → sections inside the relevant
  `topics/<topic>.md`, referencing the atomic entity/concept notes via `[[wikilinks]]`

This gives the article's three payoffs: **dedup** (a shared entity is written once),
**progressive disclosure** (agent opens only the atomic notes it needs), and a **real
Obsidian graph** of concept-to-concept edges rather than per-topic blobs.

### Topic note shape
```yaml
---
persona: vutr
topic: kafka
kind: topic
sources: [substack/vutr/kafka-internals, substack/vutr/kafka-tiered-storage]
last_updated: 2026-07-08
qc: passed
---
## Comparisons
Sort Merge Join vs Shuffle Hash Join … (references [[lsm-tree]], [[log-compaction]])

## Open questions
- …

## Synthesis
Vu Trinh's grounded position on Kafka's design philosophy …
```

### Entity/concept note shape
```yaml
---
persona: vutr
kind: entity            # or: concept
slug: lsm-tree
sources: [substack/vutr/kafka-internals]
topics: [kafka, spark]  # back-references — which topic notes cite this
last_updated: 2026-07-08
qc: passed
---
Vu Trinh's positions on the LSM-tree, grounded in his corpus …
```

### Index shape (`index.yaml`)
```yaml
topics:
  kafka: {file: topics/kafka.md, sources: 2, last_updated: 2026-07-08}
entities:
  lsm-tree: {file: entities/lsm-tree.md, topics: [kafka, spark], last_updated: 2026-07-08}
concepts:
  log-compaction: {file: concepts/log-compaction.md, last_updated: 2026-07-08}
```

### Log shape (`log.md`) — CDC history
Append-only, following this repo's standardized `_log_ingest` contract (parse last entry's
`(N total)` for prior count; first-ever entry worded as a backfill; append only on actual
change; never spam on unchanged rebuild):
```
# Persona Wiki Log — vutr

- 2026-07-08 — backfill: 3 topic notes, 7 entities, 4 concepts already synthesized (log started here) (14 total)
- 2026-07-09 — kafka revised (+1 source: kafka-tiered-storage); +1 entity (tiered-storage) (15 total)
```

---

## Data flow (one new source, end to end)

```
new captured source (kafka-tiered-storage)
  → step 1: read from data/substack.json (already there)
  → step 3: match_topics → ["kafka"]; index says kafka.md EXISTS → REVISE
            entity scan → "tiered-storage" NOT in index → CREATE entity
  → step 2: LLM reads kafka.md + new source → revised comparisons/synthesis
            LLM writes entities/tiered-storage.md
  → step 7: QC checks revised kafka.md + new entity against cited sources
  → step 4: index.yaml updated (kafka sources 1→2; new entity registered)
  → log.md: append "kafka revised (+1 source); +1 entity"
```

## Error handling

- **LLM QC failure** → note written with `qc: failed` + reason in frontmatter; excluded
  from the "blessed" index view; logged. Never silently accepted.
- **LLM call failure / timeout** → the in-progress note is left unchanged (no partial
  overwrite); the run reports the failure and exits non-zero. Re-runnable (idempotent on
  unchanged sources — no duplicate log entry).
- **Source referenced but missing** → skipped with a warning; does not abort the batch.
- **Never mutate the learning-vault's authored course** — enforced by writing only under
  `wiki/personas/`; a path guard rejects writes outside it.

## Testing

Following this repo's offline-first convention (no login/network in unit tests):

- The **derivative-writer LLM call is injected behind a seam** (à la Instagram's
  `post_fetch`), so CDC logic, index updates, storage layout, and the log all run against
  fixtures with a stub LLM returning canned derivatives.
- **CDC tests:** new-topic → CREATE; existing-topic → REVISE; shared-entity → reused not
  duplicated; missing-source → skipped.
- **Log tests (the standard 4-shape):** backfill wording on first-ever; append-on-growth;
  skip-on-no-change; revision wording.
- **Storage tests:** entity written once is referenced by two topic notes; wikilinks
  resolve; index matches on-disk files.
- **QC tests:** a canned overreaching claim is flagged `qc: failed`; a grounded one passes.
- **Path-guard test:** a write targeting outside `wiki/personas/` is rejected.

## Open questions for spec review

1. **Placement confirmation** — code in this repo, output in learning-vault (as above). If
   you want the POC code itself inside the learning-vault repo instead, that changes the
   module home.
2. **Persona source of truth for the *bootstrap*** — seed `wiki/personas/vutr/` by having
   the LLM split the existing `vutr.md` sections into atomic notes (preserves current
   knowledge), vs. start empty and only grow from newly captured sources. Recommendation:
   bootstrap-split, so existing knowledge isn't stranded.
3. **Which LLM entrypoint** — reuse the local `claude` CLI shell-out pattern (as
   `de-toolkit`'s `teach.py` does, no API key), vs. a direct API call. Recommendation:
   `claude` CLI shell-out, consistent with the sibling repo.
