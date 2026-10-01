---
title: State design
kind: topic
source: generated from note frontmatter
tags: [system-one]
topics: []
---
# State design
> What to put in state; how to word questions, options, levels.

## Notes on this topic (7)
- [[advanced-structure]] — Instructions, Choice option descriptions, Score level descriptions and Noul criteria all accept JSON (object/array) because System One models are trained to understand structure.
- [[how-to-build-with-system-one]] — Design recipe: keep code in control of the workflow, give System One narrow typed questions, run many in one parallel request, combine in code, route on confidence. Includes the 8-step workflow and a full triage example.
- [[state]] — The `state` field = the content (and supporting facts) a System One model evaluates; one state per request, many questions against it. String, JSON object, or array of text.
- [[cb-line-by-line-search]] — Semantic search over one document in a single request: tag each line with an ID, use a Choice over the line IDs to rank lines, and a Noul in the same request to say whether the document answers at all. Returns `exists` probability + one relevance score per line.
- [[cb-parallel-questions]] — Put all N questions about one document into ONE call: answers are identical to N single-question calls (no bias, no added noise), but 12.2x cheaper and 10.0x faster on a 13-question GDPR briefing. Always batch.
- [[typesafe-agent-skill]] — The vendor's drop-in skill (`typesafe-ai`) that tells coding agents how to build with System One/Jev: read live docs first, pick the right primitive, design narrow questions, compose in parallel, verify; plus install steps and troubleshooting.
- [[question-design-checklist]] — Write the state, pick Choice/Score/Noul, word options/levels/criteria, add escape outcomes, set thresholds, add companion Nouls, batch in one call. Every rule carries the example or number that proves it.

Back to [[Home]].
