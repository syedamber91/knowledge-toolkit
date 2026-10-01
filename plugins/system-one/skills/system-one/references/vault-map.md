# Vault map and lookup chain

## Lookup chain
1. **Repo vault:** `knowledge/system-one/` in the knowledge-toolkit (SOIC_Scraper) repo. Start at `08-playbook/`.
2. **iCloud Obsidian:** `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/System One`.
3. **Neither on disk** (cloud session, another repo): these `references/*.md`. Say you are working from the condensed copy; the full vault has every worked example and number.
Check with `ls` before assuming; never claim a vault note says something you have not read.

## What the vault holds (72 notes; ~83k words of source notes + playbook)
Built 2026-10-01/02: 10 Sonnet readers condensed TypeSafe's Jev / System One docs and
third-party sources into 64 notes; one Opus pass wrote the 8 playbook notes.

| Folder | Notes | Use for |
|---|---|---|
| 00-orientation | jev-introduction, system-one-model-category, ai-primer-calibrated-decisions, jev-with-coding-agents, quickstart, models-and-versions, jev-1-13-jaggedness | what Jev is; price/limits/versions; failure modes |
| 01-concepts | state, primitives-overview, choice, score, noul, advanced-structure, confidence, how-to-build-with-system-one | semantics of questions and answers; design recipe |
| 02-patterns | patterns-overview, speculative-fan-out, confidence-gated-routing, composite-scoring, intent-routing | architecture patterns |
| 03-cookbooks | cookbooks-overview + 18 recipes: consistency (nouls, choices), parallel-questions, reranking, line-by-line-search, structure-recovery, function-calling, skill-suggestion, entity-alignment, classifying-rag-passages, citation-check, llm-guardrails, sde-cascade, date-extraction, pre-parsed-value-extraction, hierarchical-classification, autoresearch-feature-discovery, classification-using-confidence (slugs prefixed `cb-`) | datasets, exact question designs, thresholds, results |
| 04-use-cases | use-case-map, demo-smart-home | brainstorming; fan-out + LLM fallback demo |
| 05-api-sdk | http-api-reference, sdk-overview, sdk-python, sdk-python-usage, sdk-python-clients, sdk-python-types, sdk-python-retries-and-exceptions, sdk-javascript, sdk-javascript-api, sdk-changelogs | call shapes, errors, retries, gateways |
| 06-agent-tooling | typesafe-agent-skill, jev-mcp-server, awesome-typesafe-jev, openrouter-jev-guide, community-guide-devto, community-guide-marktechpost | agent integration; third-party evidence |
| 07-alternatives | system-one-alternatives-overview, laya, kev, openjev-and-nanojev, minilm-embeddings, benchmarks-and-comparisons, jev-vs-laya | model choice, self-hosting, benchmark trust ladder |
| 08-playbook | when-to-use-which-model, model-tiering-sonnet-opus, agent-operating-protocol, retrieval-protocol-opus, question-design-checklist, anti-patterns, privacy-and-cost-gates, cheat-sheet | first stop for "what should I do" |
Also `Home.md`, `Log.md`, `topics/topic-*.md` hubs (calibration, routing,
classification, extraction, guardrails, retrieval-rerank, cost-latency,
state-design, agent-integration, model-selection).

## Note format (every source note)
Frontmatter `title`, `kind` (concept/pattern/cookbook/reference/tool/comparison/playbook),
`source`, `source_url`, `tags` (fixed 18-word vocab), `topics`. Body: gist, mechanism
with every number, when/when-not, worked examples, numbers table, gotchas, related.
`[inference]` marks non-source claims; contradictions are quoted with location.

## Retrieval procedure (Opus)
1. "Which/how/should" questions: open `08-playbook/` first.
2. Named things: `grep -ril "<term>" knowledge/system-one/`.
3. Themes: `grep -l "topics:.*topic-<x>" -r knowledge/system-one/` (or `tags:.*<tag>`).
4. Too many hits: `Home.md` -> `topics/topic-*.md` -> note.
5. Read whole notes (already condensed); read Gotchas/Contradictions before quoting numbers.
6. Contested number: read every note stating it; report the range with sources.
7. Cite `[[slug]]` (Obsidian) or the file path; label first-party vs third-party vs independent.

## Question -> notes
| Question | Notes |
|---|---|
| limits, price, versions | models-and-versions, http-api-reference (+ community-guide-devto, openrouter-jev-guide for conflicts) |
| can it do X / failures | jev-1-13-jaggedness, anti-patterns |
| question wording | primitives-overview, choice, score, noul, advanced-structure, question-design-checklist |
| confidence/thresholds | confidence, confidence-gated-routing, cb-consistency-choices, cb-consistency-nouls, community-guide-marktechpost |
| retrieval / RAG | cb-reranking, cb-classifying-rag-passages, cb-line-by-line-search, minilm-embeddings |
| extraction | cb-pre-parsed-value-extraction, cb-date-extraction, cb-sde-cascade, cb-structure-recovery |
| classification | cb-classification-using-confidence, cb-hierarchical-classification, cb-entity-alignment |
| guardrails / verification | cb-llm-guardrails, cb-citation-check, jev-mcp-server |
| agents / MCP | agent-operating-protocol, jev-mcp-server, typesafe-agent-skill, cb-skill-suggestion, cb-function-calling |
| Jev vs alternatives | jev-vs-laya, benchmarks-and-comparisons, system-one-alternatives-overview |

## Known gaps (say "not covered")
Sonnet/Opus list prices; Python `RetryPolicy` defaults; Kev latency; which MiniLM
checkpoint; Jev parameter count/training data; entity-alignment accuracy vs gold;
latency/cost for several cookbooks (citation check, line search, classification).
