---
title: Hierarchical Classification With Beam Search
kind: cookbook
source: Hierarchical classification (TypeSafe cookbook)
source_url: https://docs.typesafe.ai/cookbooks/hierarchical_classification
tags: [cookbook, classification, patterns]
topics: [topic-classification, topic-routing, topic-cost-latency]
---
# Hierarchical Classification With Beam Search
> Classify a document to a leaf of a deep taxonomy (patents, retail, biomedical, code) by asking one `Choice` per node over its direct children, in parallel across K beam paths. Beam K=3 got 4/4 expected leaves; greedy got 2/4.

## What it is / How it works
Data often lives in hierarchies (taxonomies, filesystems, website structures, codebases, org charts, ontologies, LLM skills, moderation policies). Goal: traverse to the correct **leaf**. This fits [[choice]]: classify the document at each node starting at the root, then proceed to the next most-probable node until a leaf.

**Two methods**
- **Greedy search:** pick the highest-probability child, discard all alternatives. One early mistake is unrecoverable.
- **Beam search:** keep `K` plausible paths; classify every frontier in parallel; deeper evidence can repair an ambiguous early decision. Final answer = leaf of the path with the highest geometric-mean probability. Because each path runs as parallel questions (see [[speculative-fan-out]]), extra exploration adds little wall-clock latency.

**Every node is a `Choice` question** whose full probability distribution *is* its edges. Sibling set = one Choice. Implementation: option keys are `c0, c1, ...` mapped reversibly to labels; instructions: "Which direct child category best matches this document?" Single-child nodes skip the call (`{label: 1.0}`) and are not counted as decisions.

**Formulas**
- `path_score = product(edge_probabilities) ** (1 / decisions)` (geometric mean; used for pruning and comparing paths). Length-normalised so shallow and deep leaves compare fairly.
- `separation = top_path_score / second_path_score` (useful but **not** used for pruning). Near 1x = ambiguous; large ratio = clear separation.
- Metric notes from source: a different metric such as `min(top_prob/second_top_prob)` would favour paths that are very clear at every node. For very deep hierarchies (e.g. >10 layers) use `exp(mean(log(probs)))` instead of `product ** (1/decisions)` to avoid precision errors (code comment: "Use log space for very deep trees").

**Constants in the code:** `MODEL="jev-1.12"`, `BEAM_WIDTH=3`, `MAX_DEPTH=12`, `EPSILON=1e-9` (probabilities floored at 1e-9 in the product). Client: `TypeSafeClient(api_key=..., retry=RetryPolicy(max_retries=5, backoff_initial=1.0, backoff_max=20.0))`; results cached via `JsonCache("json_cache.json")`.

**Loop (beam_search):** start with an empty path (score 1.0). Each round: split beam into expandable (has children) and finished (leaf); if nothing expandable, stop. For each expandable candidate, run `choose(document, children)` in parallel (`ThreadPoolExecutor(max_workers=BEAM_WIDTH)`); extend each candidate by every child using that distribution; sort finished+expanded by score and keep top `BEAM_WIDTH`. Finished leaves stay in the beam and compete on score. `greedy_search` follows `max(probabilities)` each step, up to `MAX_DEPTH`. Both strategies on all four hierarchies were run concurrently (`max_workers=len(HIERARCHIES)`).

**Benefits of decomposing into a hierarchy (source):** *Observability:* identify which nodes misclassifications concentrate in; count traversals of each node and edge. *Testability:* unit test and measure the impact of hierarchy updates on classification performance.

## When to use / when NOT to use
- Use: large taxonomies where one flat Choice over all leaves is impractical; need to localise errors per node; ambiguous early decisions that deeper evidence can fix (use beam).
- Greedy is cheaper but cannot recover from an early wrong branch (it failed 2 of 4 here).
- Not stated: how K should be chosen (only K=3 used), cost numbers, or accuracy on many documents (one document per hierarchy). [inference] 4 test documents is a demonstration, not a benchmark.

## Worked example(s)
Four hierarchies, one labelled document each; each result is the leaf reached.

| Hierarchy (version) | Structure notes | Document (gist) | Expected leaf | Greedy leaf | Beam K=3 leaf |
|---|---|---|---|---|---|
| CPC patents (2026.05) | broad technology sections -> narrow inventions | abstract: freestanding structural wooden perch for poultry/pet birds, crossbars sized for bird feet, mounts inside an aviary | A01K31/12 Perches for poultry or birds, e.g. roosts | **E99Z99/00 Subject matter not otherwise provided for in this section (wrong)** | A01K31/12 (correct) |
| Shopify products (2026-02) | store departments -> specific product types; paths split on " > " | furniture listing: wall-mounted padded window shelf bed with suction cups and washable cushion, sunny perch for one cat | Cat Window Beds & Perches | **Pet Chairs (wrong)** | Cat Window Beds & Perches (correct) |
| MeSH biomedical (2026) | a DAG; one descriptor can appear under multiple parents; demo expands official tree-number paths; top level = 16 categories A..N, V, Z (Anatomy, Organisms, Diseases, Chemicals and Drugs, Analytical/Diagnostic/Therapeutic Techniques and Equipment, Psychiatry and Psychology, Phenomena and Processes, Disciplines and Occupations, Anthropology/Education/Sociology/Social Phenomena, Technology/Industry/Agriculture, Humanities, Information Science, Named Groups, Health Care, Publication Characteristics, Geographicals) | clinical abstract: Crohn disease (transmural ileocolonic inflammation, skip lesions, abdominal pain, chronic diarrhea; colonoscopy cobblestoning; biopsy noncaseating granulomas; infliximab remission) | C06.405.469.432.500 Crohn Disease | same (correct) | same (correct) |
| CookSafe files (snapshot 2026-08-06) | TypeSafe's cookbook repo, folders -> source files; frozen listing `codebase_files.txt`, root "CookSafe" | developer search: experimental Python module under x/eugene implementing BM25, dense and fused retrievers for legal RAG | retrievers.py | same (correct) | same (correct) |

**Result: beam K=3 matched 4 of 4; greedy 2 of 4.** Keeping three paths recovered CPC patents and Shopify products. The source produces static SVGs per hierarchy (orange = greedy route, green = winning beam route, purple = other retained paths, dashed = pruned) showing edge probabilities (top 5 children per node plus retained/best/greedy ones); the per-run `mean p` and `top/second` values are computed but not printed in the extract.

Taxonomy data sources (pinned): CPC `CPCSchemeXML202605.zip` (cooperativepatentclassification.org), Shopify product-taxonomy `v2026-02/dist/en/categories.txt`, MeSH `desc2026.zip` (nlmpubs.nlm.nih.gov). MeSH position count = tree-number names + top-level tree entries.

## Numbers & limits
| Item | Value |
|---|---|
| Beam width K | 3 |
| Max depth | 12 |
| Probability floor | 1e-9 |
| Retry policy | max_retries 5, backoff 1.0 -> 20.0 s |
| Hierarchies / docs | 4 / 1 each |
| Beam accuracy | 4/4 |
| Greedy accuracy | 2/4 |
| Model | jev-1.12 |
| Depth where log-space needed | >10 layers (suggested) |

## Gotchas
- **Sibling order is part of the question.** In the codebase hierarchy, sibling options are asked in the order they appear in the snapshot file ("Line order is significant ... part of the question, not presentation"). A live repo walk would make the taxonomy and all numbers depend on the reader's checkout (even untracked scratch files); hence the frozen snapshot.
- Greedy's CPC failure went to a catch-all "Subject matter not otherwise provided for" leaf; catch-all nodes can attract probability.
- Use length-normalised (geometric mean) scores; raw products would unfairly punish deep leaves.
- Floating-point precision on very deep trees: use log-space mean.
- MeSH is a DAG: expand tree-number paths into a tree before searching; the same descriptor appears multiple times.
- Obscure: `separation` is reported but not used for pruning. [inference] it could serve as a confidence-gating signal (see [[confidence-gated-routing]]); the source only calls it a useful metric.

## Related
[[choice]] · [[confidence]] · [[speculative-fan-out]] · [[cb-classification-using-confidence]] · [[cb-classifying-rag-passages]] · [[cb-skill-suggestion]] · [[topic-classification]] · [[cookbooks-overview]]
