# Learning Vault AI — Nate Herk & Jack Roberts personas (design)

**Status:** Approved · **Date:** 2026-07-13 · **Branch:** `claude/learning-vault-ai-personas-3f8639`

## Problem

We already have, for the **data-engineering** domain, a complete grounded
learning pipeline: the `vutr` persona living inside the `learning-vault` hub —
raw captured Substack posts → provenance-gated persona wiki → Alex illustrated
notebook → closed-book PDF learning pack verified ≥9.0 by an examiner loop.

We want the **exact same thing for the AI / automation domain**, grounded in the
captured YouTube transcripts of two creators — **Nate Herk** (`@nateherk`) and
**Jack Roberts** (`@Itssssss_Jack`) — without disturbing what already exists.

Two constraints:
1. The existing `nate-herk` / `jack-roberts` agents are **teaching mentors**
   (free-form, no scoring) and must stay exactly as they are.
2. The pipeline that produces verified packs needs an **examiner** (question-gen +
   accuracy/coverage scoring), which mentors are not.

## Two findings that make this cheap (verified against code)

1. **Ingest is source-agnostic.** `persona_wiki/ingest.py` (`propose_include` +
   `ingest`) copies `.md` files from any `--posts-dir` into `raw/<topic>/`,
   matching filename+body keywords. The captured YouTube notes are already
   markdown, so the *only* change from the Substack hub is the `--posts-dir`.
   Confirmed: a `--propose` scan against
   `AI & Development/youtube/nate-herk-ai-automation/` returned 276/286 matches
   with no code change.
2. **The hub is data, not code.** `persona_root = <vault-dir>/wiki/personas/<persona>`.
   Passing `--vault-dir "<Learning Vault AI>"` makes a brand-new hub work with
   the **existing** `persona-wiki` package (installed from the `learning-vault`
   repo). Confirmed: `persona-wiki status … --vault-dir "<hub>"` reports
   `missing` for a fresh persona/topic — no duplication of pipeline code.

## Decisions

- **New content hub** `~/…/Documents/Learning Vault AI/` (own git repo; Obsidian
  vault). Data only — wikis, learner outputs, diagram specs, packs. It reuses the
  `persona-wiki` package via `--vault-dir`; nothing is `pip install`-able from it.
- **Examiners are separate agents.** New
  `.claude/agents/{nate-herk,jack-roberts}-examiner.md` +
  `.claude/skills/{…}-examiner-persona/SKILL.md`. Mentors untouched. Each examiner
  **derives its grounded content from the mentor agent** (IDENTITY + CORE TEACHING
  FRAMEWORKS + TOOL TIMELINE, real quotes only) and **adds** the four vutr-style
  examiner sections: `ROLE IN VERIFICATION LOOP`, `SCORING STANDARDS`,
  `QUESTION GENERATION GUIDELINES`, `INVOCATION (A/B/C)`. No transcript re-reading —
  the mentors already distilled 286 + 155 transcripts.
- **Dual-lens verification.** Packs are verified by BOTH examiners at once (one
  pack per topic, two lenses), modeled on `verify-sdcourse-luc.js`. New workflow
  `.claude/workflows/verify-lvai.js` reads the wiki-generated
  `output/packs/<topic>/chapters.json` directly — **no CHAPTERS mirror**, so the
  "CHAPTERS content ≠ PDF" invariant that bites hand-authored packs cannot apply.
  Phases: Setup → Questions (both examiners) → AnswerAudit (justin-sung student in
  two separate calls + alex clarity audit) → Score (`pass = all four ≥9.0`) →
  SignOff (nate-ex, jack-ex, justin, alex). Halt after 3 failed fix rounds.
- **Topics:** `ai-agents` (pilot) · `n8n-automation` · `ai-agency` ·
  `rag-vector-db`. Per persona → per topic wiki; packs are dual-lens per topic.

## Pipeline (unchanged shape, second source)

`/learn-topic <persona> <topic>` with `--vault-dir "<Learning Vault AI>"`:
- **A** ingest from the YouTube dir (human-reviewed include-list committed to
  `data/ingest/<persona>-<topic>.txt`) → synthesize concept notes via Claude
  agent transport → provenance/resolution/depth gates.
- **B** `persona-wiki learn --learner alex` → `/learning-notebook` render.
- **C** `scripts/learning_pack_wiki.py` (plan → write → verify via
  `verify-lvai.js` → render PDF).

## Known risk

Spoken transcripts are less numerically precise than Vu's written posts, so the
**depth gate** will log more `**source gap**` lines and packs on the most
technical topics (RAG internals) may need more fix rounds. That is the wiki
honestly showing its edge — not a failure to paper over with invented specifics
(the exact defect the provenance floor exists to prevent).

## Verification

1. Ingest agnosticism — `raw/<topic>/_manifest.yaml` cites YouTube source paths;
   `concepts/*.md` `sources:` cite `raw/<topic>/*`; provenance gate green.
2. Examiner fidelity — dry-run each examiner via the Agent tool; 5 rule-compliant
   questions + two-dimension score; positions trace to mentor quotes.
3. Pipeline gate — `verify-lvai.js` reaches `allPassed` or halts with a report.
4. Mentors untouched — `git diff` shows no change to the mentor agents.

## Files

| New | Where |
|---|---|
| Hub | `~/…/Documents/Learning Vault AI/` (git repo, `CLAUDE.md`, `README.md`) |
| Examiner agents | `.claude/agents/{nate-herk,jack-roberts}-examiner.md` |
| Examiner skills | `.claude/skills/{nate-herk,jack-roberts}-examiner-persona/SKILL.md` |
| Verify workflow | `.claude/workflows/verify-lvai.js` |
| This spec | `docs/superpowers/specs/2026-07-13-learning-vault-ai-personas-design.md` |

| Reused (unchanged) | Where |
|---|---|
| `persona-wiki` package | `learning-vault` repo `src/persona_wiki/` |
| Pack generator | `SOIC_Scraper/scripts/learning_pack_wiki.py` |
| Student / clarity | `.claude/agents/justin-sung.md`, `.claude/agents/alex.md` |
| Mentors | `.claude/agents/{nate-herk,jack-roberts}.md` |
