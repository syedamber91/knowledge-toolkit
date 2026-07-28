# `/learn-topic` — Per-Topic Learning Pipeline (Synthesis → Notebook + PDF)

**Date:** 2026-07-10
**Status:** Approved (design walkthrough in session; Approach A chosen)
**Repos touched:** learning-vault (persona_wiki, wikis, notebook), SOIC_Scraper (PDF generation, verification personas), `~/.claude/skills/` (orchestrator skill)

## 1. Problem & root cause

The user wants every topic to have **both** complementary learning artifacts —
the illustrated learner notebook (HTML) and the verified expert learning pack
(PDF) — produced from **one synthesized source of truth** in the learning
vault, with topic-data synthesis as an explicit prerequisite stage.

A forensic audit of the existing Spark artifacts (2026-07-10, in-session)
found the current wiki is hollow, for three distinct reasons:

1. **Wrong seed, by convenience.** The persona_wiki POC was seeded with
   `learning-vault/data/personas/vutr.md`, which is a byte-identical copy of
   the `vutr` *examiner agent prompt* (`SOIC_Scraper/.claude/agents/vutr.md`)
   — a grading rubric, already ~97.6% compressed from the real newsletter.
   The raw captured posts (`Obsidian Vault/Substack/posts/vutr/`, 229 posts;
   16 Spark posts ≈ 33,592 words) were **never read by any pipeline stage**.
   Funnel: 33,592 → 805 (agent-doc Spark section) → 527 words (wiki notes).
2. **Half-implemented LLM-wiki architecture.** The Decoding AI article the
   POC verifies prescribes `raw/ → wiki/` with derivatives citing raw. The
   POC built only `wiki/`; every note's provenance dead-ends at
   `sources: persona-snapshot`.
3. **Synthesis under-generated.** The spark topic note wikilinks 16 concepts;
   only 5 concept notes exist — 11 dangling links. Alex's learner loop found
   ~372 words and scored 6%; the "deepening loop" that got him to 100%
   bypassed the wiki and taught from the agent doc directly (proven: the
   transcript cites "line 6/8/26", which are literal line numbers of the
   agent doc's Spark bullet list).

Additionally, the hand-authored PDF (`scripts/generate_vutr_spark.py`)
contains figures attributed to Vu Trinh that appear in **no captured source**
(e.g. the "2.6GB Parquet → 3.7GB memory, 1.42×" experiment) — a factual-
grounding defect this design makes structurally impossible.

## 2. Design principle

**Every layer must show its receipt to the layer below it**, all the way down
to the captured posts. One synthesized wiki per persona+topic is the single
source of truth; the notebook and the PDF are two renderings of it (learner
dialogue vs expert exposition) and therefore cannot drift.

## 3. Architecture (Approach A — one orchestrator skill)

```
CAPTURE (knowledge-toolkit)                LEARNING VAULT (hub)
 Obsidian Vault/Substack/posts/<persona>/ ──► [A] INGEST raw/ + SYNTHESIZE wiki
                                                wiki/personas/<persona>/<raw+notes>
                                                        │  (depth gate)
                                     ┌──────────────────┴──────────────────┐
                                     ▼                                     ▼
                          [B] LEARNER LOOP (alex)                [C] PDF chapters generated
                          wiki/personas/alex/<topic>/               closed-book on wiki+raw
                          transcript ─► /learning-notebook          verify loop ≥9.0 + sign-off
                                     │                                     │
                            <topic> notebook HTML                  <topic> pack PDF
                                     └────────► Artifact / gdrive ◄────────┘
```

- `/learn-topic <persona> <topic>` (global skill) drives A → gate → (B ∥ C).
- Stages are idempotent: a stage whose output is current is skipped
  (wiki fresh → skip A; transcript+notebook exist → skip B; verified PDF
  exists → skip C).
- Cross-repo split: synthesis + wikis + notebook in learning-vault;
  PDF generation + examiner personas in SOIC_Scraper; the skill coordinates
  by absolute path.
- Real LLM transport for synthesis/learning/writing: Claude Agent tool, one
  agent per unit of work (never nested `claude -p` — 401s in-session).

## 4. Stage A — Raw layer + grounded synthesis (the precursor)

New layout under the teacher persona:

```
wiki/personas/<persona>/
  raw/<topic>/<post-slug>.md      # immutable copies of captured posts;
                                  # frontmatter: source path/URL, captured date
  concepts/<slug>.md              # re-synthesized FROM raw; frontmatter
                                  # sources: [raw/<topic>/<post>.md, …]
  topics/<topic>.md               # rebuilt; all wikilinks must resolve
  index.yaml · log.md             # existing machinery unchanged
```

**Ingest** (`persona_wiki/ingest.py`): selects posts from
`Obsidian Vault/Substack/posts/<persona>/` by topic keywords **plus a
committed, human-reviewable include-list** (junk like promos/polls excluded).
Copies into `raw/<topic>/`. Idempotent (skips already-copied). `raw/` is
append-only — synthesis can never mutate a source.

**Synthesize** (`persona_wiki/synthesize.py`): per-concept agents read the
relevant raw posts and write mechanism-depth concept notes (target: the
depth of the old agent-doc bullets PLUS mechanisms/numbers/case studies from
the full posts). Rebuilds the topic note (comparisons, open questions,
synthesis paragraph) from the new notes.

**Gates (added to `persona_wiki/qc.py`):**
- **Provenance gate:** a concept note whose `sources:` names no `raw/` file
  fails QC. `persona-snapshot` alone is invalid.
- **Resolution gate:** a topic note containing a wikilink to a nonexistent
  concept note fails QC.
- **Depth gate (entry to B/C):** every concept wikilinked by the topic note
  has a note meeting a mechanism-depth floor — judged by an agent asked to
  reconstruct the how/why from the note alone (the depth-not-coverage lesson
  from Alex's 6%→100%). If raw sources genuinely lack a mechanism, the gap is
  logged in the topic's open-questions as a **source gap** and the gate
  passes with the gap recorded (never blocks forever).

## 5. Stage B — Learner loop → notebook (reuse; one change)

Runs `persona_wiki` `learn` exactly as built (teach → reflect → answer →
verdict per concept; depth-graded mastery; transcript; qa/; open-questions;
mastery.md; 4-shape log). **Change:** `load_topic_concepts` now feeds on the
re-synthesized notes, so the agent-doc side-channel used for Spark's
deepening loop is retired — 0→100 happens in one honest pass against the
wiki. Success requires no source other than the wiki.

Rendering: the existing `/learning-notebook` skill, unchanged (full
unabridged dialogue + per-concept rough.js diagram/table + margin scribbles +
highlights, self-contained HTML; `--transcript` flag). Diagram specs authored
per topic (`diagram_specs/<topic>.json`), same shape as `spark.json`.

## 6. Stage C — PDF generation + verification (the new build)

Replaces hand-authored chapter code with generated chapter data:

1. **Chapter planner** (one agent): reads topic note + concept notes →
   4–6 chapters; every concept mapped to a chapter (coverage by
   construction; unmapped concept = planner failure).
2. **Chapter writers** (one agent per chapter): expert prose, **closed-book
   on the wiki notes + the raw posts they cite**. Every number/claim must
   appear in a cited source; otherwise it is dropped or moved to an explicit
   "beyond the source" box. A grounding check flags unsourced specifics.
3. **Verification loop, reused unchanged** (per
   `docs/LEARNING_PACK_VERIFICATION_WORKFLOW.md`): examiner scores accuracy +
   coverage ≥9.0 per chapter; Justin answers from chapter text; Alex audits
   clarity in parallel; fix rounds apply examiner gaps + Alex improvements;
   tri-agent final sign-off. A chapter stuck <9.0 after 3 fix rounds halts
   with a report naming the failing dimension — never silently ships.
   Chapters are data (JSON/markdown), killing the CHAPTERS-content-sync
   invariant.
4. Render HTML → PDF via headless Chrome `--print-to-pdf`; optional gdrive
   upload (`scripts/gdrive_upload.py`). Render/upload failure leaves the
   verified HTML behind.

New generalized script in SOIC_Scraper:
`scripts/generate_learning_pack_from_wiki.py` (planner/writer prompt
builders + HTML/PDF renderer, wiki-path → pack).

## 7. MVP: Kafka end-to-end

Raw coverage (title-matched, measured): **kafka 18 posts ≈ 42,920 words**
(richer than Spark's 16 ≈ 33,592) — vs iceberg 7/18.8k, parquet 7/16k,
olap 13/34.8k, airflow 3/10.3k, flink 2/4.4k. Kafka also gets two
independent examiners: **vutr** and **sdcourse** (production-Kafka
specialist).

Success criteria:
- Every kafka concept note cites ≥1 `raw/` post; zero dangling wikilinks.
- Alex reaches depth-graded 100% in one pass with no side-channel source.
- Every number in the PDF traceable to a raw post (or boxed "beyond the
  source").
- Notebook published as Artifact; PDF verified ≥9.0 + tri-sign-off;
  both uploaded to gdrive.

## 8. Error handling

- **Ingest:** junk excluded via committed include-list (auditable);
  idempotent re-runs.
- **Synthesis:** per-concept failure (bad JSON, agent error) skips the
  concept this pass, logs, retries next pass; never aborts the topic. A
  gate-failing note is quarantined to `_failed/` for review, not written
  into the wiki.
- **Depth gate:** source gaps logged to open-questions, gate passes with
  record (the honest "wiki's edge" pattern).
- **Stage C:** halt-with-report after 3 failed fix rounds; render/upload
  failures preserve the HTML.
- **Path guard:** all writes confined to `wiki/personas/<persona>/`
  (existing storage guard); `raw/` append-only.

## 9. Testing (offline, stubbed LLM `Callable[[str], str]`)

In `tests/persona_wiki/`, no network/login (established pattern):
- **Ingest:** include/exclude selection on a fixture vault (with iCloud-style
  spaced paths); idempotent re-run; receipt frontmatter written.
- **Gates:** provenance gate rejects `persona-snapshot`-only notes;
  resolution gate rejects dangling wikilinks; both pass valid fixtures.
- **Synthesis:** note written with sources; failed-JSON concept skipped and
  counted; `_failed/` quarantine on gate failure.
- **Stage C:** plan covers all concepts (fail on unmapped); grounding check
  flags unsourced numbers; 4-shape log tests for any new vault writer.
- **Orchestrator:** stage-skip logic on stamped fixtures.
- The live verification loop (real agents, ≥9.0) remains a manually
  triggered run — it is the product, not a unit test.

Known constraints carried forward: venv outside iCloud (`/tmp/pw-venv`);
never reintroduce the `f"{kind}s"` bug — use `index.atomic_dir(kind)`;
Python 3.9+, Pydantic v2, Typer.

## 10. Where things live

| Piece | Repo / location |
|---|---|
| `ingest.py`, `synthesize.py`, gates in `qc.py`, tests | learning-vault `src/persona_wiki/`, `tests/persona_wiki/` |
| Wikis (`raw/` + notes), Alex outputs, notebook HTML | learning-vault `wiki/personas/…` |
| `generate_learning_pack_from_wiki.py`, verification personas | SOIC_Scraper `scripts/`, `.claude/agents/` |
| `/learn-topic` orchestrator skill | `~/.claude/skills/learn-topic/` |
| `/learning-notebook` (reused unchanged) | `~/.claude/skills/learning-notebook/` |

## 11. Out of scope (YAGNI)

- Other capture sources (YouTube/web/Instagram) as synthesis feeders —
  Substack-only for the MVP; the feeder interface should not preclude them.
- Multi-persona blending, whole-vault wikis, vector/graph DBs (the article's
  own scale argument), gap/rescore modes.
- Auto-authoring notebook diagram specs (stays hand-authored per topic).
- Backfilling the Spark wiki — a natural second run of the pipeline, not
  part of the MVP build.
