---
title: Cookbooks Overview
kind: reference
source: Cookbooks (TypeSafe docs)
source_url: https://docs.typesafe.ai/cookbooks
tags: [cookbook, system-one, patterns]
topics: [topic-classification, topic-extraction, topic-guardrails, topic-retrieval-rerank]
---
# Cookbooks Overview
> Index of 19 end-to-end TypeSafe recipes grouped by theme, with each recipe's one-line outcome, headline numbers and difficulty level.

## What it is
Each cookbook is a worked example: real dataset, the TypeSafe questions that decide something about it, and the code that turns those decisions into a working system. Read one to see how [[primitives-overview]] and [[patterns-overview]] combine on a concrete problem, or copy one as a starting point. Prerequisites: know the primitives and [[confidence]].

## Catalogue (all 19)
### Self-consistency — repeat a decision, use agreement across runs as a signal
| Cookbook | What it does | Level |
|---|---|---|
| [[cb-consistency-nouls]] | Route uncertain probabilities to human review while keeping underlying noul values visible | Beginner |
| [[cb-consistency-choices]] | Add an "uncertain" outcome to moderation decisions; compare label agreement with share of automatic actions | Beginner |

### Batching — pack many questions into one request
| [[cb-parallel-questions]] | 13-question regulatory briefing over the GDPR Wikipedia article; batching every question into one call is **12.2x cheaper** and **10.0x faster** with no change in answers | Beginner |

### How-to — search, formatting, tool selection, guardrails
| Cookbook | What it does | Level |
|---|---|---|
| [[cb-reranking]] | 30-passage BM25 shortlists for 40 CLERC legal queries; one question per query-candidate pair raises top-1 accuracy **5% -> 18%** and top-10 **38% -> 62%** | Beginner |
| [[cb-line-by-line-search]] | Semantic search over GitHub's Terms of Service: one request scores **218 line ids** against a plain-language query with a Choice question; a Noul checks whether the document contains an answer | Beginner |
| [[cb-structure-recovery]] | Reconstruct Markdown from plain text in **two requests**: one stitches hard-wrapped lines, one classifies every block (heading, list, code, callout) | Beginner |
| [[cb-function-calling]] | Natural-language trading requests -> calls to ordinary typed functions, mapping function names and closed-set arguments to confidence-aware questions | Intermediate |
| [[cb-skill-suggestion]] | Pick at most one skill per agent turn from the **182** in Nous Research's Hermes catalog, using **two** requests (rank, then re-check top candidates) | Intermediate |
| [[cb-entity-alignment]] | Which of **450** candidate pairs from two beer catalogues are the same product: one Score question + three companion Nouls surfacing which fields disagree | Beginner |
| [[cb-classifying-rag-passages]] | Score each retrieved passage with one request; decide in code which reach the answering model | Intermediate |
| [[cb-citation-check]] | Catch wrong/hallucinated citations against the source doc; one Choice decides whether the quote's context supports the claim | Beginner |
| [[cb-llm-guardrails]] | Screen every message into/out of an LLM app with one request; threshold hazard probabilities + severity to pass/review/block/route | Intermediate |

### Extraction — typed values out of messy text
| [[cb-sde-cascade]] | 2-stage structured-data-extraction cascade (mini -> verify -> reasoning): most of a big reasoning model's quality at a fraction of cost | Intermediate |
| [[cb-date-extraction]] | Absolute + relative dates: ask for the parts named in the doc, resolve and validate in code, confidence-based review | Beginner |
| [[cb-pre-parsed-value-extraction]] | Regexes find candidate emails/phones/amounts; TypeSafe selects the requested span so code can normalize a verbatim value | Beginner |

### Classification — inputs to categories at any depth
| [[cb-hierarchical-classification]] | Deep patent, retail product, biomedical, source-code hierarchies via parallel beam search over Choice probabilities | Intermediate |
| [[cb-autoresearch-feature-discovery]] | Autoresearch loop proposes TypeSafe questions, turns free text into numeric features, uses model errors to improve a supervised CatBoost regressor | Advanced |
| [[cb-classification-using-confidence]] | SEC annual reports -> **75** industry groups with one Choice each; read the answer's own confidence to decide between that group and the broader division above | Beginner |

## Level distribution
Beginner: consistency x2, parallel questions, reranking, line-by-line search, structure recovery, entity alignment, citation check, date extraction, pre-parsed extraction, classification using confidence (11). Intermediate: function calling, skill suggestion, classifying RAG passages, LLM guardrails, SDE cascade, hierarchical classification (6). Advanced: autoresearch feature discovery (1). Total 18 recipes (2 + 1 + 9 + 3 + 3 by group); counts derived from the table by this note. [inference] The vault's 19 cookbook slugs = 18 recipes + this overview.

## When to use / when NOT to use
- Starting point choice: need a recipe for guardrails -> [[cb-llm-guardrails]]; for RAG filtering -> [[cb-classifying-rag-passages]]; for hallucination checking -> [[cb-citation-check]]; for dates -> [[cb-date-extraction]]; for taxonomy depth -> [[cb-hierarchical-classification]].
- The page includes a note inviting users to submit their own cookbook-worthy use cases.

## Gotchas
- Cookbook pages say numbers were produced with a specific model version (e.g. `jev-1.12`) and ship a `json_cache.json` so reruns replay published numbers without API calls (see [[cb-citation-check]], [[cb-llm-guardrails]]). [[models-and-versions]]

## Related
[[use-case-map]] · [[demo-smart-home]] · [[patterns-overview]] · [[primitives-overview]] · [[confidence]]
