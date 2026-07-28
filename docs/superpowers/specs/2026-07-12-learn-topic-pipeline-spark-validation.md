# /learn-topic pipeline — Spark PDF size validation

**Date:** 2026-07-12
**Status:** Validated (Approach B, stratified sample — see below)
**Trigger:** the new `spark_pack.pdf` (13,131 words) is roughly half the size of the
old hand-authored `vutr_spark.pdf` (23,761 words). This doc records the investigation
into why, and whether that size drop represents lost learning value.

## The question

Does the grounded `/learn-topic` pipeline (see
`docs/superpowers/specs/2026-07-10-learn-topic-pipeline-design.md`) produce a *shorter*
pack because it's dropping real details, subtopics, or the source writer's (Vu Trinh's)
own narrative voice — or because the old pack was padded with unsourced elaboration the
new pipeline correctly refuses to invent?

## Method: word-count flow, then a stratified fact/voice audit

**Step 1 — word-count flow through each pipeline** (cheap, first signal):

| | Old pipeline | New pipeline |
|---|---|---|
| Raw posts available | 32,155 words | 32,155 words |
| Raw posts actually **read** | 0 (seeded from an 805-word examiner-agent cheat sheet) | 32,155 (ingested into `raw/spark/`) |
| Wiki / outline | 805 words | 12,760 words (19 concept notes) |
| PDF | 23,761 words | 13,131 words |
| Outline → PDF ratio | **29.5× expansion** | **1.03×** (PDF stays tight to its grounding) |

A 29.5× expansion from an 805-word bullet outline cannot be legitimate recall — it's the
model elaborating from general knowledge. This is corroborated by an earlier finding in
this session: the old PDF's illustrative skew-OOM arithmetic ("8GB executor → 3.6GB OOM;
double to 16GB → still OOMs at 7.5GB") does not appear anywhere in the 15 raw Spark posts.

**Step 2 — stratified fact/subtopic/voice audit (Approach B).** Word-count alone doesn't
prove nothing real was lost in the new pipeline's 32,155 → 12,760 word compression. Three
concepts were audited end-to-end (raw → wiki note → notebook transcript → PDF chapter),
chosen to cover the profiles most likely to expose a real gap:

| Concept | Profile | Result |
|---|---|---|
| `photon-vectorized-engine` | Dense, 1 dedicated post (5,483w) | All 6 benchmark/timing numbers kept; old PDF's only invented content was a fake "SIGMOD 2022" citation and an unsourced "50–200×" figure |
| `data-skew-and-oom` | Dense, scattered across 4 posts — the exact concept the old PDF fabricated on | Every case-study number kept (84→168 tasks, 35s→12s, 65.7%, 832MB→~1GB spill); correctly **omits** the old PDF's invented executor-doubling arithmetic; Vu Trinh's direct quotes and project-specific config choices preserved |
| `data-locality-and-speculative-execution` | Thin — 1 post, a subsection within a broader piece | All 5 locality levels, delay scheduling, and the parallel-copy/kill-loser mechanic kept, including a detail ("both copies run in parallel, winner kept") that required re-reading past the initial grep window to confirm — it was a faithful paraphrase, not invented |

**Step 3 — downstream propagation check.** `data-skew-and-oom`'s case-study numbers
(84→168, 65.7%, 832MB) were traced through the wiki note into both the notebook
transcript and the PDF chapter — identical in both, confirming the wiki note is the
single source of truth both downstream artifacts draw from correctly, with no further
loss or drift after synthesis.

## Conclusion

The size difference is explained by:
1. **Mostly (≈2/3):** the old PDF was inflated with unsourced elaboration from an
   805-word outline — including invented arithmetic. The new pipeline's closed-book
   writer, gated by `grounding_check()`, structurally cannot do this.
2. **Partly (≈1/3), and legitimately:** compressing narrative-heavy newsletter prose
   (repeated framing, transitions, cross-post redundancy) into reference-style
   concept notes shortens word count without dropping mechanism-level facts.

All three audited concepts — spanning single-dense-source, multi-source-scattered, and
thin-single-mention profiles — retained every checked detail, subtopic, and instance of
the source writer's own voice, and correctly declined to fabricate what the old pipeline
had fabricated. **No evidence of real learning-value loss was found in this sample.**

**Standing item:** a full 39-concept audit (every Spark + Kafka concept, not just this
3-concept stratified sample) would give total certainty but wasn't run here — see this
doc if that level of confidence is ever needed. Nothing in the sample suggests it would
change the verdict.

Related: `docs/superpowers/specs/2026-07-10-learn-topic-pipeline-design.md`,
learning-vault `wiki/personas/vutr/concepts/{photon-vectorized-engine,data-skew-and-oom,
data-locality-and-speculative-execution}.md`.
