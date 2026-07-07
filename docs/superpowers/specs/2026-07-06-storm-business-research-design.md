# STORM Business Research Engine — Design Spec

**Date:** 2026-07-06
**Status:** Approved design (pending user spec review → implementation plan)

## Goal

A reusable, on-demand **multi-perspective business research engine** for the
Opportunity-Catalog founder, modeled on Stanford's STORM method (as taught in
Nate Herk's "Stanford's Method Turns Claude Into a PhD Level Research Team").
Given a business idea, market, catalog entry, or freeform question, it runs the
topic through several deliberately-disagreeing expert lenses, maps their
contradictions, adversarially fact-checks the strongest claims, and produces a
graded report — both as a durable Obsidian note and a shareable HTML briefing.

It generalizes the one-off v2 catalog scoring pipeline (built 2026-06-30) into a
repeatable tool.

## Origin & grounding

- **STORM pattern** (per the Nate Herk video, AI & Development vault): multiple
  expert *perspectives* → *contradiction map* → *synthesis* → *adversarial peer
  review* → verified output graded by reliability. Nate's insight: if you lack
  subject-matter expertise, borrow it — a council of lenses that contradict each
  other kills your blind spots.
- **Existing repo patterns reused:** the v2 catalog pipeline (parallel scoring
  agents + 10-persona panel + Mufti halal gate); the `/vault-ask` route-cheap /
  present-costly split and its completeness-critic verification pass; the
  learning-pack verification loop (examiner + Alex).

## Architecture

Execution model **Option C — thin skill triggers a deterministic workflow**:

```
/storm  (skill: pick mode, gather input, confirm)
   │
   ▼
storm workflow  (deterministic multi-agent orchestration)
   Phase 0 Scope → 1 Lenses → 2 Contradiction-map → 3 Synthesis
                 → 4 Adversarial-verify → 5 Render
   ▼
Outputs:  vault note (durable, graded)  +  self-contained HTML briefing
```

- Code lives in **this repo** (`knowledge-toolkit`): `.claude/skills/storm/SKILL.md`
  (front door) + a saved workflow script (the engine) + a small `src/` module of
  **pure, unit-tested helpers** (slugify, note-merge-between-markers, HTML render).
- It **writes into the Business Personas iCloud vault**
  (`~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Business Personas/Opportunity-Catalog/`),
  the same way the SOIC/media toolkits write to their iCloud vaults. That vault
  is not in git; **no captured output is ever committed**.

## The engine — six phases (shared by every mode)

- **Phase 0 — Scope & cast.** Normalize the input; if it's vague, ask
  clarifying questions (Nate's "phase zero"). Do **cheap vault retrieval first**
  (grep the Business Personas + AI & Development vaults for existing context) so
  lenses start from what's already known. Then **cast** the named voices (see
  "Casting" below).
- **Phase 1 — Lenses (parallel).** Each configured lens researches its angle
  from **vault + live web** (hybrid evidence). Each agent **writes its own
  scratchpad result file** — never echoes all results through one return value
  (v2 lesson: that blows the 64k output-token cap). The **Mufti halal gate**
  runs here for business modes and can veto.
- **Phase 2 — Contradiction map.** One agent reads all lens files and maps where
  they agree/disagree, ranking each claim by evidence strength. This is the
  stage Nate credits for STORM beating one-shot research.
- **Phase 3 — Synthesis.** Merge into findings ranked by reliability, plus a
  verdict on the existing scale (**KEEP / WATCHLIST / CUT**) and **A/B/C evidence
  grades**, consistent with the v2 catalog vocabulary.
- **Phase 4 — Adversarial verify.** Independent verifiers fact-check the top
  claims against web + vault and mark each source **confirmed / corrected /
  demoted** (the `/vault-ask` completeness-critic pattern, scaled up). Verify
  runs on the top model tier.
- **Phase 5 — Render.** Write the durable vault note **and** the standalone HTML
  briefing.

## Lenses (shared roster, configurable per mode)

- **Role lenses (stable, pinned per mode):** Operator · Investor/Economist ·
  Customer · Skeptic/Risk · Local-Market.
- **Named voices (DYNAMIC — never hardcoded).** Discovered at runtime by globbing
  the persona roster (`.claude/agents/*.md` persona files + persona notes in the
  Business Personas vault). Adding a new persona makes it castable with **zero
  engine changes**.
- **Mufti** — a **named, always-on, special-cased halal gate** with veto power;
  never subject to casting.

### Casting (how dynamic voices are chosen per run)

**Auto-cast best-fit, always add Mufti.** The `/storm` skill **asks for the
number of named voices each run (default 3)**. A cheap casting step in Phase 0
then reads the live roster and each persona's description and selects that many
best-fit voices for this specific topic (e.g. a food-import idea casts Falguni
Nayar + Biyani; a SaaS idea casts Levels + Kahl). **Mufti is always appended on
top of the chosen count** (i.e. N best-fit voices + Mufti gate) regardless of the
number entered. The count is per-run input, not hardcoded; the roster is
discovered dynamically so casting adapts automatically as personas are added.

## Modes (MVP-first)

| Mode | Input | Output destination |
|------|-------|--------------------|
| **idea** (MVP — build & prove first) | one business idea/name | new report note in `STORM-Reports/` + HTML |
| **gap** | a city + sector | Macro-style gap note in `STORM-Reports/` + HTML |
| **rescore** | catalog note path(s) | updates the business note's evidence section **in place** (between `<!-- storm-start -->` / `<!-- storm-end -->` markers) + HTML |
| **research** | any business question | report note in `STORM-Reports/` + HTML |

**Sequencing:** build the **engine + `idea` mode** first, prove it end-to-end on
one known business (e.g. the top-5 "Zakat & Islamic-Finance Advisory"), eyeball
the note + HTML, then layer `gap`, `rescore`, `research` onto the same engine.

## Outputs

- **Vault note:** graded findings, the contradiction map, the verdict
  (KEEP/WATCHLIST/CUT), and dated evidence with A/B/C grades. For `rescore`, it
  updates the existing business note between `<!-- storm-start/end -->` markers
  (matching the v2 `<!-- v2-scoring-start/end -->` convention) rather than
  creating a new file.
- **HTML briefing:** a self-contained file (inlined CSS, no external deps) with a
  ~60-second summary, findings ranked by reliability, and the contradiction map —
  written under a gitignored `output/storm/<slug>.html`.

## Models & cost control

- **Scope/cast/render:** cheap tier. **Lenses:** standard tier (Opus optional per
  run for depth). **Adversarial verify:** top tier. Tunable per stage.
- Lens/verify fan-out is bounded; the skill reports the planned agent count
  before a large run (e.g. `rescore` over many notes) so cost is visible.

## Testing

- **Pure helpers get real unit tests** (TDD): `slugify`, note-merge between
  markers (idempotent — re-running replaces the marked block, never duplicates),
  and HTML render (valid self-contained doc, expected sections present).
- **Orchestration** is validated by a **dry-run of `idea` mode on one known
  business**, then eyeballing the vault note + HTML for grounding, citations, and
  a coherent contradiction map.

## Guardrails (carried over from v2 + repo conventions)

- Each parallel agent writes its **own** result file (output-cap gotcha).
- **No large objects through workflow `args`** — hardcode stable maps as script
  literals; agents read shared data from on-disk files (v2 gotcha: a ~9KB args
  object silently arrived empty).
- **Mufti veto is hard** — a halal rejection cannot be overridden by other lenses.
- **Nothing captured is committed** — reports live in the (non-git) iCloud vault
  and gitignored `output/`.
- Honest evidence grading — a claim with weak/absent sourcing is demoted, not
  dressed up (consistent with A/B/C grades and the "keep it honest" principle).

## Out of scope (YAGNI)

- No new persona *authoring* — STORM consumes whatever personas exist; creating
  personas stays a separate task.
- No live web-scraping infrastructure beyond the agents' existing web tools.
- No automatic re-run scheduling; runs are user-triggered.
- `gap`/`rescore`/`research` modes are designed here but implemented **after** the
  `idea`-mode MVP proves the engine.
