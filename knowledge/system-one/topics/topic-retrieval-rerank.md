---
title: Retrieval & rerank
kind: topic
source: generated from note frontmatter
tags: [system-one]
topics: []
---
# Retrieval & rerank
> Shortlist cheaply, then score candidates with typed questions.

## Notes on this topic (7)
- [[cb-classifying-rag-passages]] — Between retrieval and generation, score every retrieved passage with ONE `system_one` call of four `Noul` questions, then route it in plain code to evidence / conflict / dropped. Use when similarity search hands noisy, contradicting or prompt-injected passages to an answering LLM.
- [[cb-line-by-line-search]] — Semantic search over one document in a single request: tag each line with an ID, use a Choice over the line IDs to rank lines, and a Noul in the same request to say whether the document answers at all. Returns `exists` probability + one relevance score per line.
- [[cb-reranking]] — Fast search (BM25) builds a 30-passage shortlist; one Noul question per (query, candidate) pair scores each; sort by noul. On 40 CLERC legal queries: top-1 5% -> 18%, top-10 38% -> 62%, 1,200 calls for $0.0645.
- [[cb-skill-suggestion]] — Pick at most one skill for an agent turn out of the 182 in Nous Research's Hermes catalog using two TypeSafe requests (rank all, then re-check top 3). Cuts wrong skill loads 16.8% -> 7.3% and needless loads 9.8% -> 4.0%.
- [[cookbooks-overview]] — Index of 19 end-to-end TypeSafe recipes grouped by theme, with each recipe's one-line outcome, headline numbers and difficulty level.
- [[minilm-embeddings]] — A small sentence-embedding model used in the SOTAAZ benchmarks as (a) a trained-classifier baseline, (b) a nearest-label-name zero-shot baseline, and (c) a candidate shortlister in front of Laya. It is NOT a typed, calibrated System One decision model — it embeds text; it does not natively answer choice/score/noul questions with calibrated probabilities.
- [[retrieval-protocol-opus]] — How the Opus agent answers from THIS vault: grep-first routing via `Home.md` -> topic hub -> note, which notes to open per question type, depth rules, citation format, and how to say "the vault doesn't cover it". Plus how System One tools and embeddings shortlist big corpora.

Back to [[Home]].
