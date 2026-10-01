---
title: Line-by-Line Search
kind: cookbook
source: Line-by-line search (TypeSafe cookbook, semantic_find)
source_url: https://docs.typesafe.ai/cookbooks/semantic_find
tags: [cookbook, retrieval-rerank, primitives]
topics: [topic-retrieval-rerank, topic-calibration, topic-state-design]
---
# Line-by-Line Search
> Semantic search over one document in a single request: tag each line with an ID, use a Choice over the line IDs to rank lines, and a Noul in the same request to say whether the document answers at all. Returns `exists` probability + one relevance score per line.

## What it is / How it works
Goal: given GitHub's Terms of Service and a plain-language question, return the lines that answer it and detect when the document has no answer. Result: `find()` returns `{exists, relevance[]}`.

Three parts:
1. **Tag each line with an ID** so TypeSafe can point to it.
2. **[[choice]] question** ranks the line IDs by how well they answer the query. Choice probabilities always sum to 1, so some line ranks first even when none answer.
3. **[[noul]] question in the same request** checks whether the document contains an answer at all. Unlike Choice, a Noul probability does not depend on other options, so it can fall near zero when there is no answer.

Both go in one `client.system_one(state=DOCUMENT, questions={"where": ..., "exists": ...}, model="jev-1.12")` call. State is sent once, so the existence check costs only a small amount of extra output. The state stays unchanged between searches; the query goes in `instructions`. See [[state]].

Setup: `pip install 'cooksafe>=0.2.0,<0.3.0'`, `export TYPESAFE_API_KEY=...`. `JsonCache` replays included responses (no key/spend); delete `json_cache.json` to run live. Client timeout 120.0.

### Step 1: tagging
Test document: GitHub ToS from a gist (eugene-shvarts), split with `splitlines()` into **218** clauses (43,980 characters). IDs `L000`...`L217` via `f"L{i:03d}"`; document lines are `"{id}| {line}"` joined by newlines, e.g. `L052| You own Your Content...`.

### Step 2: where question
```python
Choice(instructions=f'Which line of the document contains the answer to: "{query}"?',
       criteria={line_id(i): None for i in range(len(LINES))})
```
Option descriptions are `None` because the document already holds each ID's text.

### Step 3: exists question
```python
Noul(instructions=f'Does any line of the document address or answer: "{query}"?',
     criteria=NoulCriteria(true="At least one line of the document states or directly implies the answer",
                           false="No line of the document addresses this"))
```

### Step 4-5: result and verdict
`relevance = [probabilities.get(line_id(i), 0.0) for i in range(len(LINES))]` (one score per line, document order); `exists = answers["exists"].noul`. Verdict thresholds in local code:
```python
FOUND, ABSENT = 0.7, 0.35  # present answers typically read >=0.9, absent <=0.05
exists >= 0.7 -> "answered in this document"; < 0.35 -> "not in this document"; else "partially addressed"
```
Source: thresholds separate the examples but "tune them against your own documents before using them in production." `show()` renders relevance as a text bar chart (`#` x round(relevance*12), min 1) with a 58-char line preview.

## When to use / when NOT to use
- Use for: finding quotable lines in one document, plus an honest "not answered here" signal. Swap the URL in `fetch_document()` for your own text; everything else works off `LINES`.
- Limit: a Choice question accepts **up to 255 options**, so this recipe handles documents of up to 255 lines in one request. Past that, search in two passes: one Choice picks a window of lines, a second ranks lines inside it.
- The ranking alone cannot distinguish a real answer from the closest irrelevant line; always pair with `exists`.

## Worked examples (218 lines, 43,980 chars)
| Query | exists | Verdict | Top lines (relevance) |
|---|---|---|---|
| who owns the code I upload? | 0.98 | answered | L052 0.95 ("You own Your Content..."), L046 0.02, L051 0.02, L217 0.01 |
| can GitHub kick me off the platform without warning? | 0.97 | answered | L168 0.97 ("GitHub has the right to suspend or terminate your access..."), L167 0.03, L000 0.00, L001 0.00 |
| do I have to take disputes to arbitration? | 0.14 | not in this document | L205 0.86 (closest line), L168 0.02 |
| can minors use GitHub with parental permission? | 0.46 | partially addressed | L029 0.90 ("You must be age 13 or older..."), L012 0.07 |

Interpretation (source "What the scores mean"):
- First two: direct answers + source lines to verify.
- Arbitration: ranking gives the closest line 0.86 but `exists` only 0.14, so the answer is not in the document.
- Parental permission: age rule ranks first but does not say whether parental permission changes the rule -> partially addressed.
- "The ranking tells you where to look; the `exists` score tells you whether the result answers the question." The included queries rank direct-answer lines first.

## Numbers & limits
| Item | Value |
|---|---|
| Lines / chars in test doc | 218 / 43,980 |
| Max Choice options | 255 |
| FOUND / ABSENT thresholds | 0.7 / 0.35 |
| Typical `exists` when answer present | >= 0.9 |
| Typical `exists` when absent | <= 0.05 |
| Observed partial | 0.46 |
| Observed absent-but-closest-line | exists 0.14 vs relevance 0.86 |
| Model | jev-1.12 |
| Latency/cost | not stated |

## Gotchas
- Choice sums to 1 -> always a "winner", even for unanswerable queries (arbitration case: 0.86 on a non-answer).
- The arbitration example sits at exists 0.14, above the "absent <= 0.05" typical range but below ABSENT 0.35; thresholds are tuned to these examples only.
- IDs make results quotable: every hit points to one line.

## Related
[[choice]], [[noul]], [[state]], [[cb-reranking]], [[cb-citation-check]], [[cb-structure-recovery]], [[confidence]], [[topic-retrieval-rerank]], [[cookbooks-overview]]
