---
title: Retrieval Protocol Opus
kind: playbook
source: Synthesis of vault structure and notes (Opus synthesis pass, 2026-10-02)
source_url: vault-internal
tags: [retrieval-rerank, agent-tooling, routing]
topics: [topic-retrieval-rerank, topic-agent-integration, topic-routing]
---
# Retrieval Protocol (Opus)
> How the Opus agent answers from THIS vault: grep-first routing via `Home.md` -> topic hub -> note, which notes to open per question type, depth rules, citation format, and how to say "the vault doesn't cover it". Plus how System One tools and embeddings shortlist big corpora.

## Lookup chain (where the vault lives)
1. Repo: `knowledge/system-one/` (this vault).
2. iCloud Obsidian: `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/System One`.
3. Neither on disk (cloud session, other repo): the plugin's condensed `references/*.md` (`plugins/system-one/skills/system-one/references/`). Say you are on the condensed copy.

## Vault layout (64 source notes + 8 playbook)
| Folder | Holds | Open for |
|---|---|---|
| 00-orientation | what Jev is, models/prices/limits, jaggedness | "what is", limits, never-use |
| 01-concepts | state, primitives, Choice/Score/Noul, confidence, how-to-build | question design, semantics of outputs |
| 02-patterns | fan-out, confidence gating, composite scoring, intent routing | architecture |
| 03-cookbooks | 18 worked recipes with datasets + numbers | "show me numbers", "has this been done" |
| 04-use-cases | use-case map, smart-home demo | brainstorming |
| 05-api-sdk | HTTP API, Python/JS SDKs, changelogs | exact call shapes, errors, retries |
| 06-agent-tooling | jev-mcp, TypeSafe skill, OpenRouter, community guides, awesome directory | agent integration, third-party evidence |
| 07-alternatives | Laya, Kev, openjev/NanoJev, MiniLM, benchmarks, Jev vs Laya | model choice, self-hosting |
| 08-playbook | this synthesis layer | first stop for "what should I do" |

## Routing procedure
1. **Start in 08-playbook** if the question is "which/how/should" — it already links the evidence.
2. **Grep-first** for named things: `grep -ril "<term>" knowledge/system-one/` (tool names, numbers, model ids). Cheapest route, exact.
3. **Filter by frontmatter** for themes: `grep -l "topics:.*topic-retrieval-rerank" -r knowledge/system-one/`; tags likewise (`tags:.*guardrails`).
4. **Then hubs:** `Home.md` -> `topics/<topic-*>.md` -> note (written by the vault lead; use when grep returns too much).
5. **Open the minimum set**, read whole notes (they are condensed already); always read a note's Gotchas / Contradictions / Flags section before quoting a number.
6. **Spot-check raw source only for a disputed number** (raw pages are outside the vault; cite note first).

## Question type -> notes to open
| Question | Open (in order) |
|---|---|
| What is Jev / System One? | [[jev-introduction]], [[system-one-model-category]], [[ai-primer-calibrated-decisions]] |
| Price, limits, versions, languages | [[models-and-versions]], [[http-api-reference]]; check [[community-guide-devto]] / [[openrouter-jev-guide]] for conflicting numbers |
| Can Jev do X? / failure modes | [[jev-1-13-jaggedness]], [[anti-patterns]] |
| Which primitive / how to word it | [[primitives-overview]], [[choice]] / [[score]] / [[noul]], [[advanced-structure]], [[question-design-checklist]] |
| What does confidence mean / thresholds | [[confidence]], [[confidence-gated-routing]], [[cb-consistency-choices]], [[cb-consistency-nouls]], [[community-guide-marktechpost]] (formula) |
| Retrieval / RAG / reranking | [[cb-reranking]], [[cb-classifying-rag-passages]], [[cb-line-by-line-search]], [[minilm-embeddings]] |
| Extraction | [[cb-pre-parsed-value-extraction]], [[cb-date-extraction]], [[cb-sde-cascade]], [[cb-structure-recovery]] |
| Classification / taxonomy | [[cb-classification-using-confidence]], [[cb-hierarchical-classification]], [[cb-entity-alignment]] |
| Guardrails / verification | [[cb-llm-guardrails]], [[cb-citation-check]], [[cb-classifying-rag-passages]], `jev_screen`/`jev_verify` in [[jev-mcp-server]] |
| Agent integration / MCP / skills | [[agent-operating-protocol]], [[jev-mcp-server]], [[typesafe-agent-skill]], [[cb-skill-suggestion]], [[cb-function-calling]] |
| Code calls (Python/JS/HTTP) | [[quickstart]], [[sdk-python-usage]], [[sdk-python-clients]], [[sdk-python-retries-and-exceptions]], [[sdk-javascript-api]] |
| Jev vs Laya vs others | [[jev-vs-laya]], [[benchmarks-and-comparisons]] (trust ladder first), [[system-one-alternatives-overview]], [[laya]], [[kev]], [[openjev-and-nanojev]] |
| Independent evidence on Jev | [[awesome-typesafe-jev]] §3 and §5f, [[benchmarks-and-comparisons]] |
| Cost / latency budgets | [[privacy-and-cost-gates]], [[cb-parallel-questions]], [[cb-consistency-nouls]], [[cb-reranking]] |

## Depth rules
- **Factual lookup (one number/name):** 1-2 notes; quote with citation; check that note's Gotchas.
- **How-to:** playbook note + the closest cookbook ("often shows a better decomposition than a generic classifier", [[typesafe-agent-skill]]).
- **Comparison / recommendation:** all notes on both sides + trust ladder ([[benchmarks-and-comparisons]]); label vendor vs third-party vs independent.
- **Contested number:** read every note that states it; report the range with sources; prefer first-party for API facts, independent measurement for quality claims.

## Citing
- Inline double-bracket slug links (Obsidian) or `knowledge/system-one/<folder>/<slug>.md` (outside Obsidian), plus section name when long.
- Label provenance: TypeSafe docs (first-party) / author-reported (third-party) / independent measurement (SOTAAZ, jev-certify, etc.).
- Synthesis claims not stated in any note: `[inference]`.

## Saying "not covered"
Say it in one line, name the closest note, and stop. Known gaps (verified absent from the vault): Sonnet/Opus list prices; Python `RetryPolicy` defaults ([[sdk-python-retries-and-exceptions]]); Kev latency ([[kev]]); which MiniLM checkpoint ([[minilm-embeddings]]); Jev size/training data; accuracy of entity alignment vs `known_same_as` ([[cb-entity-alignment]]); latency/cost for several cookbooks (citation check, line search, classification).

## Retrieval over BIG corpora with System One + embeddings
| Corpus shape | Recipe | Source |
|---|---|---|
| Thousands of passages | fast search (BM25 and/or embeddings) to top-30 -> one Noul per (query, candidate) -> sort | [[cb-reranking]] (top-1 5%->18%, 1,200 calls $0.0645) |
| RAG top-k, noisy/untrusted | cosine top-12 -> 4 Nouls per passage (relevant, evidence, contradicts premise, injection) -> route in code | [[cb-classifying-rag-passages]] |
| One document <=255 lines | prefix each line with an id (`L000`...), one Choice over ids + an `exists` Noul | [[cb-line-by-line-search]]; >255 lines: two passes |
| Up to 250 candidate notes | `jev_find` (best + exists) or `jev_rerank` (full order); chunk docs to ~2,000 chars, merge by best chunk | [[jev-mcp-server]] |
| Many classes, labels available | MiniLM + logistic regression (90%+ on TREC/BANKING77) | [[minilm-embeddings]] |
| Many options, small decision model | embedding shortlist to ~20 first (Laya 37.0% -> 59.1%) | [[minilm-embeddings]], [[laya]] |
| Large roster (skills/tools) | wide Choice over all + gate Nouls, then rerank top-3 with full text | [[cb-skill-suggestion]] |
| Deep taxonomy | one Choice per level, beam K=3 | [[cb-hierarchical-classification]] |
Cautions: an embedding or zero-shot-Laya page-finder in front of a reader LOWERED accuracy on long financial PDFs (owner spike 2026-10-02; recall@4 0.40-0.55) - see [[anti-patterns]] section G; reranking cannot add what the shortlist missed ([[cb-reranking]]); Choice always returns a winner — pair with `exists` ([[cb-line-by-line-search]]); similarity ranked the injection passage FIRST ([[cb-classifying-rag-passages]]); probability ties at two decimals break `LIMIT k` (jev-orderby-bench, [[awesome-typesafe-jev]]); this vault (72 notes) is small enough to grep — use Jev tools only where grep cannot express meaning [inference].

## Related
[[model-tiering-sonnet-opus]] · [[when-to-use-which-model]] · [[cheat-sheet]] · [[topic-retrieval-rerank]] · [[topic-agent-integration]]
