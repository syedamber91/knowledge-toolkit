---
title: Classification
kind: topic
source: generated from note frontmatter
tags: [system-one]
topics: []
---
# Classification
> Choice-based labelling, hierarchies, 'unsure' outcomes.

## Notes on this topic (14)
- [[advanced-structure]] — Instructions, Choice option descriptions, Score level descriptions and Noul criteria all accept JSON (object/array) because System One models are trained to understand structure.
- [[choice]] — Select one option from a fixed, unordered set; returns the chosen option, a probability per option, and a confidence. Use for routing and classification.
- [[primitives-overview]] — The three question types (Choice, Score, Noul), the typed answer each returns, how to pick between them, and how to batch many questions into one request.
- [[score]] — Rate content against ordered, descriptive levels; returns a fractional position (probability-weighted level number), per-level probabilities, a legend and confidence. Use for spectra (severity, frustration, experience) and as building blocks for weighted composites.
- [[intent-routing]] — Use Jev as a fast, cheap front-door classifier that sends each request to deterministic code, a specialist LLM, or a human — so expensive resources only run when needed.
- [[cb-citation-check]] — Catch wrong or hallucinated LLM citations: an ordinary string match finds fabricated quotes, then ONE `Choice` question reads the quote's section and decides supports / contradicts / says nothing; a 0.8 confidence gate sends weak verdicts to a human.
- [[cb-classification-using-confidence]] — One 75-option `Choice` per document; read its `confidence`; if >= 0.9 report the fine label (industry group), else report the parent label (division). One request per document, no second model, no extra calls.
- [[cb-entity-alignment]] — Decide, for each of 450 candidate duplicate pairs (two beer catalogues), whether to merge, drop, or send to a human curator, using ONE `Score` question (3 levels) plus three companion `Noul` questions in a single request. No fitted threshold anywhere.
- [[cb-hierarchical-classification]] — Classify a document to a leaf of a deep taxonomy (patents, retail, biomedical, code) by asking one `Choice` per node over its direct children, in parallel across K beam paths. Beam K=3 got 4/4 expected leaves; greedy got 2/4.
- [[cb-pre-parsed-value-extraction]] — Regex finds candidate spans (emails, phones, amounts), TypeSafe picks the one the question asks for, code copies it verbatim and normalizes it. Reach for it when you need an exact value out of a document and must never get an invented or digit-transposed one.
- [[cb-structure-recovery]] — Rebuild Markdown from plain text that lost its formatting using two System One requests (stitch split sentences with Noul, classify blocks with Choice) while code does all rendering, so no output character is ever model-generated.
- [[cookbooks-overview]] — Index of 19 end-to-end TypeSafe recipes grouped by theme, with each recipe's one-line outcome, headline numbers and difficulty level.
- [[use-case-map]] — Brainstorming catalogue: 5 headline categories, 20 industry/task idea lists, and a 10-row "decision shape" table. Open the closest industry, scan the example decisions, adapt to your own documents and actions.
- [[question-design-checklist]] — Write the state, pick Choice/Score/Noul, word options/levels/criteria, add escape outcomes, set thresholds, add companion Nouls, batch in one call. Every rule carries the example or number that proves it.

Back to [[Home]].
