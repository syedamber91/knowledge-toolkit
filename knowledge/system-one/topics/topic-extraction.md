---
title: Extraction
kind: topic
source: generated from note frontmatter
tags: [system-one]
topics: []
---
# Extraction
> Pulling dates, values, structure and fields out of text, verified in code.

## Notes on this topic (8)
- [[primitives-overview]] — The three question types (Choice, Score, Noul), the typed answer each returns, how to pick between them, and how to batch many questions into one request.
- [[cb-autoresearch-feature-discovery]] — Turn free text into numeric features by having an LLM propose System One questions, answering them per row, training CatBoost on the answers, and feeding CatBoost's errors/importances back into the next proposal round. Reached held-out RMSE 1.77 on wine-review scores.
- [[cb-date-extraction]] — Read a date's PARTS off the text with 7 `Choice` questions in one call, then resolve them to a real `date` in code (code does the calendar math, never the model); min-confidence across used parts gates human review.
- [[cb-pre-parsed-value-extraction]] — Regex finds candidate spans (emails, phones, amounts), TypeSafe picks the one the question asks for, code copies it verbatim and normalizes it. Reach for it when you need an exact value out of a document and must never get an invented or digit-transposed one.
- [[cb-sde-cascade]] — Structured-data-extraction cascade: extract with a cheap mini model -> verify per field with TypeSafe Noul questions -> escalate to a reasoning model only if any field's P(wrong) > 0.7. Gets most of the big model's quality at a fraction of the cost.
- [[cb-structure-recovery]] — Rebuild Markdown from plain text that lost its formatting using two System One requests (stitch split sentences with Noul, classify blocks with Choice) while code does all rendering, so no output character is ever model-generated.
- [[cookbooks-overview]] — Index of 19 end-to-end TypeSafe recipes grouped by theme, with each recipe's one-line outcome, headline numbers and difficulty level.
- [[use-case-map]] — Brainstorming catalogue: 5 headline categories, 20 industry/task idea lists, and a 10-row "decision shape" table. Open the closest industry, scan the example decisions, adapt to your own documents and actions.

Back to [[Home]].
