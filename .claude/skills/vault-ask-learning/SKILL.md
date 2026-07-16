---
name: vault-ask-learning
description: Answer a question from the SYNTHESIZED learning hubs — learning-vault (data engineering / vutr), Learning Vault AI (AI-automation / nate-herk + jack-roberts), learning-vault-systemdesign (system design / lucsystemdesign + sdcourse), and Learning Vault Invest (stock-market / soic, Phase 1 pilot) — by first checking a compact topic manifest, then routing over each persona's index.yaml + topic notes (all four hubs are local-first now, GitHub fallback only), then having an Opus subagent synthesize a citation-grounded answer written so a curious 12-year-old could follow it (the /explain-simple standard), with inline diagrams and a brief-vs-detailed depth toggle. Use for questions against the grounded persona-wiki concept layer, or when the user invokes /vault-ask-learning.
trigger: /vault-ask-learning
---

# Skill: Vault Ask — Learning Hubs

**Trigger:** `/vault-ask-learning <question>`

The learning-hub sibling of `/vault-ask`. Same philosophy: a knowledge base
isn't valuable because a fancy model built it — it's valuable because cheap
**routing** finds the right note fast. The expensive model only earns its cost
at the very end, turning what routing found into an answer that lands for a
human. **Do not skip straight to a costly model** — that defeats the point.

**How this differs from `/vault-ask`** (and why it's a separate skill):

| | `/vault-ask` (raw-capture vaults) | `/vault-ask-learning` (this skill) |
|---|---|---|
| Index | `Home.md` + `sources/*.md` | per-persona `index.yaml` + topic `Related:` line |
| Content unit | raw transcript / post notes | **synthesized, grounded** `concepts/<slug>.md` |
| Extra layer | — | rendered packs + report/verdict files |
| Source | local vaults only | **local clone first, GitHub fallback** |
| Citation | video/post title | `concept-slug (persona)` (raw one hop away) |

Because these hubs hold already-synthesized, deduped concept notes, answers are
cleaner and citations are by concept slug + persona. The raw provenance is one
hop away via each concept's `sources:` list when you need a primary quote.

Scope is these four hubs **only** — never route into the raw-capture vaults
(AI & Development / Stock Market / Substack); those belong to `/vault-ask`.

## Answer modes & audience (applies to every answer)

**Audience: a curious 12-year-old — the `/explain-simple` standard.** Write so
a smart 12-year-old with no background could follow it: plain words before any
jargon, **every technical term defined on first use with an everyday analogy**,
short sentences, nothing assumed. (Same spirit as this repo's `alex` clarity
persona.) The routed notes are often written for adults — your job is to
*translate*, not transcribe.

**Always include diagrams — inline, in the answer.** For each major mechanism,
draw a simple **ASCII / text box-and-arrow diagram** in a fenced code block, so
it renders anywhere (even a bare terminal). Example shape:

```
[ your write ] --> ( Memtable: sorted list in memory )
                        |  when it gets full
                        v
                   [ SSTable file on disk ]  (frozen, never edited)
```

A `mermaid` fenced block MAY be added as a bonus for complex flows, but never
rely on it alone — the ASCII diagram must carry the idea by itself.

**Two depth modes — detect from the request; default = detailed:**

| Mode | Trigger words in the question | What it produces |
|------|-------------------------------|------------------|
| **brief** | "brief", "quick", "short", "tl;dr", "in a nutshell", "one-liner", "just the gist" | A tight ~150–250 word answer: one core analogy, **one** simple diagram, the 3–5 must-know points, and citations. Skip the open-questions section. |
| **detailed** *(default)* | "detailed", "in depth", "thorough", "full", "deep", "walk me through", or nothing specified | The full walk-through: every mechanism with its own analogy **and** its own diagram, the trade-off/comparison, and the wiki's own open-questions/gaps. |

Citations stay in **both** modes — every non-trivial claim tagged
`concept-slug (persona)` (see Step 4). Simplicity is about *wording and
diagrams*, never about dropping the grounding.

## Step 0 — Fast-path manifest check (do this before Step 1)

Before inferring a hub from prose, grep the committed **topic manifest** for
the question's key nouns — it maps every hub/persona/topic/concept-count in
one small file, so hub + persona + topic selection often resolves in a
single grep instead of walking multiple `index.yaml` files (some 100s of
lines):

- Primary (works in any environment, local or cloud):
  `gh api repos/syedamber91/claude-memory/contents/vault-ask-learning-topic-manifest.md --jq .content | base64 -d`
- Faster local shortcut, if this session already has this project's
  Claude Code memory directory available (check your loaded memory index
  for a `vault-ask-learning-topic-manifest.md` entry — its path is
  session/project-specific, so don't hardcode one): read it directly instead
  of shelling out to `gh`.

The manifest carries a snapshot date. If it doesn't resolve the question, a
matched topic's concept count looks implausible, or the manifest looks old
relative to known recent work on that hub, fall through to Step 1-3's live
`index.yaml` reads — don't trust a stale number when precision matters.

**Never spawn a subagent for Step 0-3** — routing is mechanical grep/read,
cheap enough to do directly in the main loop. Only Step 4 (final answer
synthesis) should cost a subagent call, and only once, on the already-
narrowed file set. This is what keeps routing fast and token-light.

## Step 1 — Pick the hub(s)

| Hub | Local path (exact — naming is inconsistent across hubs, don't guess) | GitHub repo (`syedamber91/…`) | Persona(s) | Domain | Status |
|-----|---------------------------|-------------------------------|-----------|--------|--------|
| **learning-vault** | `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/learning-vault` | `learning-data-engineering-concepts` (public) | `vutr` | Data engineering — Spark, Kafka, Iceberg, dbt, OLAP, storage models, Parquet, LSM-trees, CDC, Flink, Arrow, career, big-tech case studies | **Built**: 33 topics, 292 concepts, 203 entities. No rendered packs. |
| **Learning Vault AI** | `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Learning Vault AI` | `learning-vault-ai` (private) | `nate-herk`, `jack-roberts` — **two independent `index.yaml` trees**, same pattern as systemdesign below | AI/automation — AI agents, memory, orchestration, MCP, prompting, RAG, agency economics | **Partial**: only `ai-agents` built for both personas (42 / 35 concepts) + rendered pack (`output/packs/ai-agents/`: chapters.json, VERIFICATION_SUMMARY.md, PDF). `n8n-automation` / `ai-agency` / `rag-vector-db` not built. |
| **learning-vault-systemdesign** | `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/learning-vault-systemdesign` | `learning-vault-systemdesign` (private, added 2026-07-17) | `lucsystemdesign`, `sdcourse` | System design — `lucsystemdesign`: databases, distributed fundamentals, networking/edge, resilience patterns, architecture styles (DDD/microservices), API architecture, messaging/streaming, infrastructure, auth/security, MCP & AI tooling, case studies. `sdcourse`: log pipelines, Kafka/event streaming, stream processing, leader election/Raft, MapReduce, capacity planning, multi-region replication, FAANG interview prep | **Built**: `lucsystemdesign` — 11 topics, 84 concepts, 18 entities. `sdcourse` — 23 topics, 158 concepts, 46 entities. No rendered packs. |
| **Learning Vault Invest** | `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Learning Vault Invest` (note: spaces, Title Case — **not** `learning-vault-invest`) | `learning-vault-invest` (private) | `soic` | Stock-market / investing — SOIC (Ishmohit Arora) Level-6 sector-analyst method | **Real wiki, Phase 1 pilot** (as of 2026-07-14): `wiki/personas/soic/` has 1 topic (`sector-analysis-framework`), 22 concepts, provenance-gated — no longer a placeholder. `poc/soic/` (`POC_VERDICT.md`, `soic_persona_brief_v2.md`, `PI_Industries_SOIC_analysis.md`, `enrichment_*.md`) remains useful supplementary primary-source material. ~40 individual sector applications not yet built. |

Every hub that has `wiki/personas/alex/` (`learning-vault`, `Learning Vault
AI`) — that directory holds Alex-persona learner-loop notebook outputs, not a
routable persona wiki. Skip it. `learning-vault`'s `wiki/personas/vutr 2/` is
also a stray empty iCloud-sync duplicate — ignore it.

Infer the hub from the question's subject:
- data-engineering terms (Spark, Kafka, Iceberg, dbt, OLAP, warehouse, Parquet,
  LSM, CDC, DuckDB, streaming) → **learning-vault**
- AI-automation terms (agent, n8n, MCP, RAG, subagent, Nate Herk, Jack Roberts,
  Hermes, agency) → **Learning Vault AI**
- system-design terms (load balancer, CAP theorem, microservices, rate
  limiting, circuit breaker, API gateway, consistent hashing, Raft/leader
  election, MapReduce, FAANG interview prep, or Kafka/event-streaming asked
  from an *implementation/systems-design* angle) → **learning-vault-systemdesign**
- investing terms (stock, sector, moat, valuation, SOIC, Ishmohit, a company
  name, sector-analysis method) → **Learning Vault Invest**

Kafka/event-streaming appears in both **learning-vault** (`vutr`, data-engineering
angle) and **learning-vault-systemdesign** (`sdcourse`, distributed-systems
angle) — if the question names a persona, route only that hub; if it doesn't,
route both and let Step 4 attribute each position by persona.

If genuinely ambiguous, route more than one hub — routing is cheap.

## Step 2 — Resolve the hub source (local-first, GitHub fallback)

For each chosen hub:

1. If the **local path exists** → use local files (fast, offline). This is
   now the normal case for **all four hubs**, including Learning Vault
   Invest (it has a local clone with real content as of 2026-07-14 — do not
   assume it's GitHub-only, that's stale).
2. Else → read from **GitHub** via `gh` (fallback only — should rarely fire
   now that every hub has a local clone):
   - List: `gh api repos/syedamber91/<repo>/git/trees/HEAD?recursive=1 --jq '.tree[].path'`
   - Fetch a file: `gh api repos/syedamber91/<repo>/contents/<path> --jq .content | base64 -d`
   - learning-vault-systemdesign now has a GitHub remote (added 2026-07-17,
     `learning-vault-systemdesign`, private) — all four hubs have a working
     fallback.
   - If `gh` is missing/unauthenticated or the repo is unreachable, say so
     plainly and stop — do not guess an answer.

Record, per routed file, whether it came from **local** or **GitHub** (needed
for the sources line in Step 5).

## Step 3 — Route (cheap, mechanical — do it yourself, no subagent, no costly model)

### Built hubs (all four: learning-vault, Learning Vault AI, learning-vault-systemdesign, Learning Vault Invest)

1. Read the relevant persona's `wiki/personas/<persona>/index.yaml` — the
   authoritative `topics:` and `concepts:` maps (slug → file, topic
   membership), or check [[vault-ask-learning-topic-manifest]] first. Two
   hubs have **two independent persona trees**, not one: Learning Vault AI
   (`personas/nate-herk/`, `personas/jack-roberts/`) and
   learning-vault-systemdesign (`personas/lucsystemdesign/`,
   `personas/sdcourse/`) — pick the one matching the question.
2. `grep -il` the question's key nouns against concept slugs (in `index.yaml`
   and `concepts/*.md`) and topic slugs. For a matched topic, open
   `topics/<topic>.md` — its `Related:` line lists concept slugs in
   **curriculum order**; use it to narrow to the concepts the question needs.
3. Assemble the routed set (cap ~6–12 files): matched `concepts/<slug>.md`
   (primary), the owning `topics/<topic>.md` (for its Comparisons /
   Open-questions / Synthesis sections), and `entities/<slug>.md` when relevant
   (**learning-vault** and **learning-vault-systemdesign** have real entities
   content; Learning Vault AI and Learning Vault Invest currently have an
   empty `entities: {}`).
4. **Overview + report boost (Learning Vault AI):** if
   `output/packs/<topic>/` exists (locally, or committed on GitHub) *and* the
   question is broad/overview or asks about coverage/quality/scores, include
   the relevant `chapters.json` chapter `html` and/or `VERIFICATION_SUMMARY.md`.
   (`output/` is gitignored locally but the pack files are committed to the
   `learning-vault-ai` GitHub repo — check both.)
5. **Raw on demand:** only when the question needs primary-source precision (an
   exact quote, "what did X actually say", a number to verify), follow a matched
   concept's `sources:` list to the specific `raw/<topic>/<video>.md` files and
   add those. Otherwise stay in the synthesized layer.
6. **Skip `wiki/personas/alex/`** in `learning-vault` and `Learning Vault
   AI` — learner-loop notebook output, not a routable persona.

### Learning Vault Invest — Phase 1 pilot, not full coverage

`wiki/personas/soic/` now has a real, provenance-gated wiki for topic
`sector-analysis-framework` (22 concepts) — route it exactly like the other
built hubs (index.yaml → topics/<topic>.md → concepts/<slug>.md). This is
**not** a placeholder anymore. But coverage is narrow: only the Level-6
sector-analyst *method* is built; the ~40 individual sector applications
aren't. For primary-source depth or a worked example beyond the method
notes, also pull from `poc/soic/`:
- `soic_persona_brief_v2.md` — the persona + analysis method (prefer v2 over v1)
- `POC_VERDICT.md` — the go/no-go verdict + rationale
- `PI_Industries_SOIC_analysis.md` — a worked company analysis
- `enrichment_*.md` — agrochem / frameworks / value-chain enrichment notes

If the question asks about a specific sector beyond what
`sector-analysis-framework` covers, **state plainly** that hub coverage is
still method-only, not sector-by-sector.

### No match

If nothing matches, or the asked topic isn't built (e.g. `n8n-automation`, or
any specific investing topic beyond the POC), say so plainly and list the topics
that **do** exist for that hub. Never fabricate.

## Step 4 — Present (costly — dispatch a subagent on the most capable model)

Dispatch one `Agent` call with `model: "opus"` (fall back to the session's
top-tier model if opus isn't available). Give it:

- The user's original question, verbatim.
- The **chosen answer mode** (`brief` or `detailed`) from "Answer modes &
  audience" above — tell the agent which one to produce.
- The **absolute local paths** (for local files) or **GitHub locations**
  (`repo` + `path`, for fallback files) of every routed note. For GitHub files
  with no local clone, either fetch their contents in Step 2/3 and pass the
  contents, or instruct the agent to fetch them with the same `gh api` command —
  do not make it guess.
- An explicit instruction set:
  - **Read every routed note end-to-end** — long files in continuation chunks
    (offset/limit) until finished. Skimming is the number-one cause of
    incomplete answers; reading depth matters more than model choice.
  - **Enumerate before drafting**: list every named framework, numbered list,
    and step-sequence found in each note; the answer must cover each relevant
    one (detailed mode) or the 3–5 most important (brief mode), or explicitly
    note it was omitted. Makes skipping visible.
  - Answer **only** from what these notes actually say — never fill gaps from
    general knowledge. (Simplifying the *wording* is required; inventing
    *content* is forbidden.)
  - **Write for a curious 12-year-old — the `/explain-simple` standard.** Plain
    words before jargon; define every technical term on first use with an
    everyday **analogy** (e.g. "a bloom filter is like a bouncer with a
    guest-list who can say 'definitely not on the list' but sometimes waves
    through a maybe"); short sentences; no assumed background. Translate the
    notes, don't transcribe them.
  - **Include inline diagrams.** Draw a simple **ASCII / text box-and-arrow
    diagram** in a fenced code block for each major mechanism (detailed mode) or
    one overall diagram (brief mode). A `mermaid` block may be added as a bonus
    but the ASCII must stand on its own.
  - **Respect the mode.** `detailed` = every mechanism gets its own analogy +
    diagram, plus the trade-off and the wiki's open-questions/gaps. `brief` =
    ~150–250 words, one core analogy, one diagram, the 3–5 must-knows, no
    open-questions section.
  - **Cite `concept-slug (persona)`** for every non-trivial claim, in **both**
    modes; add the video/post title when a raw source was pulled, and the report
    filename (e.g. `VERIFICATION_SUMMARY.md`, `POC_VERDICT.md`) when a
    verdict/summary was used.
  - For **cross-persona** topics (e.g. Nate Herk vs Jack Roberts, or
    lucsystemdesign vs sdcourse on Kafka/event-streaming), attribute every
    position by persona and **never blend** them.
  - If the routed notes don't fully answer, say what's missing — including
    "this topic/wiki isn't built yet" for unbuilt topics, or "this hub only
    covers the sector-analyst method, not this specific sector" for
    Learning Vault Invest questions beyond `sector-analysis-framework`.

For high-stakes or explicitly-thorough requests, add a **completeness-critic
pass**: a second, cheaper agent re-reads the routed notes and diffs them against
the draft, flagging any major framework or claim the presenter missed; feed
flags back for one revision. (Mirrors the learning-pack verification loop at
miniature scale.)

## Step 5 — Return

Relay the subagent's answer, plus a short **sources** line: the routed concept
slugs / topic / persona / hub, and whether each came from **local** or
**GitHub**. If more than one hub contributed, say which part of the answer came
from which hub.

## Why split this way

- Step 3 (routing) is pattern-matching over `index.yaml` + a topic's `Related:`
  line — a cheap/no-model operation, and doing it first keeps Step 4's input
  small and relevant instead of dumping a whole hub into a costly model.
- Step 4 (presentation) is where explanation quality matters most, so it's the
  one step worth paying for a stronger model.
- These hubs are the *synthesized* layer (the output of the `/learn-topic`
  pipeline), distinct from the raw-capture vaults `/vault-ask` reads — so this
  skill routes the concept/topic/report layer and resolves local-first with a
  GitHub fallback across four named hubs. All four now have a GitHub remote
  (learning-vault-systemdesign was the last to get one, 2026-07-17), so a
  cloud/remote session with `gh` access can read any hub without the local
  Mac being reachable — local-first is purely a latency optimization now, not
  a hard requirement.

## Example questions (ready to use)

The prompt is just a plain-English question — the skill supplies all routing and
grounding rules. Naming the persona, using the hub's own topic words, and
stating the shape you want ("compare", "step-by-step", "where do they disagree")
all sharpen the answer. Add a **mode word** to pick depth — `brief` / `quick` /
`tl;dr` for a short answer, or nothing (default) / `detailed` / `in depth` for
the full walk-through. Every answer is written for a 12-year-old and comes with
diagrams either way.

Mode examples:
```
/vault-ask-learning brief: explain LSM-tree storage engines per vutr.
/vault-ask-learning Explain LSM-tree storage engines the way the vutr wiki does, in depth.
```

learning-vault (data engineering · `vutr`):
```
/vault-ask-learning Explain LSM-tree storage engines the way the vutr wiki does.
/vault-ask-learning How does the learning-vault describe Kafka's zero-copy + page-cache path?
/vault-ask-learning Compare Spark vs single-node engines (DuckDB/Polars) per vutr.
/vault-ask-learning What's the vutr take on storage models — NSM vs DSM vs PAX?
```

Learning Vault AI (AI/automation · `nate-herk` + `jack-roberts`):
```
/vault-ask-learning Where do Nate Herk and Jack Roberts disagree on agent memory architecture?
/vault-ask-learning Give me the ai-agents pack's take on workflows vs agents.
/vault-ask-learning What does the ai-agents VERIFICATION_SUMMARY say about coverage gaps?
```

learning-vault-systemdesign (system design · `lucsystemdesign` + `sdcourse`):
```
/vault-ask-learning How does lucsystemdesign explain the CAP theorem and consistent hashing?
/vault-ask-learning Walk me through rate limiting — token bucket vs leaky bucket vs sliding window, per lucsystemdesign.
/vault-ask-learning How does sdcourse's course build a Kafka-based log pipeline end to end?
/vault-ask-learning Where do lucsystemdesign and sdcourse differ on Kafka / event-streaming internals?
/vault-ask-learning brief: circuit breakers per lucsystemdesign.
```

Learning Vault Invest (investing · `soic`, Phase 1 pilot):
```
/vault-ask-learning How does SOIC's sector-analysis-framework wiki explain value-chain mapping?
/vault-ask-learning How does the SOIC persona analyze a company like PI Industries?
/vault-ask-learning What did the invest POC conclude — is the SOIC wiki worth building?
```
