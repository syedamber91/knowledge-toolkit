---
title: Re-ranking
kind: cookbook
source: Re-ranking (TypeSafe cookbook)
source_url: https://docs.typesafe.ai/cookbooks/rerank_typesafe
tags: [cookbook, retrieval-rerank, evaluation]
topics: [topic-retrieval-rerank, topic-cost-latency, topic-calibration]
---
# Re-ranking
> Fast search (BM25) builds a 30-passage shortlist; one Noul question per (query, candidate) pair scores each; sort by noul. On 40 CLERC legal queries: top-1 5% -> 18%, top-10 38% -> 62%, 1,200 calls for $0.0645.

## What it is / How it works
Two-step retrieval:
1. **Fast search** compares the query against the whole corpus and returns a ranked shortlist. Methods: keyword (BM25), dense embeddings (meaning), often combined. Here: BM25 only (ranks by shared words), to keep attention on re-ranking. Choice of fast-search method is "a side issue": re-ranking only ever sees the shortlist.
2. **Re-ranking** scores each shortlist candidate individually against the query and sorts by that score.

Why TypeSafe for the scorer: a general LLM can score pairs or rank the whole list, but independent pair scoring needs an invented scoring scale and a prompt forcing the same standard on every candidate; repeated calls can give different scores for the same pair; general generation adds time and cost to a task that needs one number. With TypeSafe the request stays a yes/no question and a [[noul]] returns a 0-1 value = TypeSafe's estimate of how likely the answer is yes. The question's criteria define true/false; no scale to invent; "built to do this repeated scoring faster, cheaper, and more consistently".

Shape of one scoring call (pseudocode in source):
```python
Noul(instructions="Is this candidate the cited case?",
     criteria=NoulCriteria(true="The candidate states the specific rule the query cites.",
                           false="The candidate is only on a similar topic."))
# response.answers["is_cited_source"].noul  # -> 0.87
```
Re-rank = run the same question for every candidate, `sorted(..., key=noul, reverse=True)`. One request per candidate; no request sees another (state = `{query, candidate k}`). See [[score]] and [[speculative-fan-out]].

## When to use / when NOT to use
- Use after any cheap retrieval step when the top-1 is rarely right but the answer is usually somewhere in the shortlist.
- Hard ceiling: re-ranking only reorders the top 30 already selected; it cannot add a passage fast search missed. Here the shortlist contained the gold for 100% of queries, so re-ranking could focus purely on ordering.
- Source note: the walkthrough asks ONE question per pair for clarity; a real application would ask several questions about the same pair in one call (see [[cb-parallel-questions]], [[speculative-fan-out]]).

## Worked example (dataset + design)
Dataset: **CLERC**, legal retrieval (aclanthology.org/2025.findings-naacl.441; HF `jhu-clsp/CLERC`, file `teva_train_dir/train_data.jsonl.gz`). US federal court opinions.
- Row = Query (opinion excerpt with a citation removed) + Gold (passage the removed citation pointed to) + 20 negative passages. Rows kept only if they have a positive passage and exactly 20 negatives; first 1000 qualifying rows streamed; `random.Random(0)` samples.
- `N_ROWS = 170` rows pooled into one shared corpus -> **3,565 passages**. `N_QUERIES = 40` evaluated (sampled from `pool[20:]`; the first 20 pooled rows held out). Other 130 rows only appear as candidates.
- BM25 (`bm25s`, English stopwords) ranks the full 3,565-passage corpus for each query (not just that row's 20 negatives); `TOP_K = 30` candidates go to the re-ranker.
- Corpus id = first 16 chars of SHA-1 of text (dedupes passages shared across queries).

The Noul question (`is_cited_source`):
- instructions: query excerpt comes from a US federal court opinion, written around a citation to a precedent that has been removed; "Could the candidate passage be from that cited precedent — does it establish the specific legal proposition the query excerpt invokes at its citation point?"
- criteria.true: candidate states or establishes the specific rule, standard, holding, or fact pattern the query attributes to its removed citation.
- criteria.false: candidate is merely on a similar topic or doctrine; does not supply the specific proposition relied on.
- state: `{"query_excerpt": query, "candidate_passage": candidate}`; model `jev-1.12`.

Execution: 40 queries x 30 candidates = **1,200 independent calls**, via `ThreadPoolExecutor(max_workers=12)`; question passed as JSON (`model_dump_json(exclude_none=True)`) so the cached string decodes into the call.

## Numbers & limits
| Metric | Fast search (BM25) | + TypeSafe re-rank |
|---|---|---|
| Gold in top-30 shortlist | 100% (40/40) | (same set) |
| Top 1 | 5% | **18%** |
| Top 5 | 15% | **35%** |
| Top 10 | 38% | **62%** |

| Cost item | Value |
|---|---|
| Calls | 1,200 |
| Input tokens | 1,536,002 |
| Output tokens | 25,200 |
| Price (jev-1.12, as of 2026-08) | $0.042 / 1M input, $0.00 / 1M output |
| Total cost | **$0.0645** |

Other constants: corpus 3,565 passages, 170 rows, 40 queries, TOP_K 30, 12 worker threads, client timeout 120.0 s. Average input per call = ~1,280 tokens [inference: 1,536,002 / 1,200].

## Gotchas
- Re-ranking improves ordering, not recall; gold absent from the shortlist stays absent.
- Even after re-ranking, top-1 is only 18%: the task (finding the exact cited precedent among topically similar passages) is hard; the question's false criterion ("merely similar topic") is what pushes similar-but-wrong candidates down.
- Source states one-question-per-pair is for clarity, not the recommended production shape.
- Results depend on cached `json_cache.json`; delete to re-run live.

## Related
[[noul]], [[score]], [[composite-scoring]], [[speculative-fan-out]], [[cb-parallel-questions]], [[cb-line-by-line-search]], [[cb-classifying-rag-passages]], [[topic-retrieval-rerank]], [[topic-cost-latency]], [[cookbooks-overview]]
