---
title: Routing
kind: topic
source: generated from note frontmatter
tags: [system-one]
topics: []
---
# Routing
> Send each input to code, a small model, an LLM or a human based on answer + confidence.

## Notes on this topic (23)
- [[choice]] — Select one option from a fixed, unordered set; returns the chosen option, a probability per option, and a confidence. Use for routing and classification.
- [[confidence]] — A 0-1 summary of how peaked an answer's probability distribution is, returned on every Choice and Score answer; use it to decide act / confirm / escalate.
- [[how-to-build-with-system-one]] — Design recipe: keep code in control of the workflow, give System One narrow typed questions, run many in one parallel request, combine in code, route on confidence. Includes the 8-step workflow and a full triage example.
- [[composite-scoring]] — Break a complex judgment into independent atomic Score dimensions, normalize, then combine with weights you own in code.
- [[confidence-gated-routing]] — The answer says WHAT; confidence says WHETHER to act. Set per-action thresholds by risk, escalate to a human or ask for confirmation in the middle band.
- [[intent-routing]] — Use Jev as a fast, cheap front-door classifier that sends each request to deterministic code, a specialist LLM, or a human — so expensive resources only run when needed.
- [[patterns-overview]] — Index of the four architectural patterns for building with TypeSafe; each is one atomic-decision composition idea.
- [[speculative-fan-out]] — Put every question your system might need into ONE request (including ones that may turn out irrelevant), then let code pick which answers matter.
- [[cb-classification-using-confidence]] — One 75-option `Choice` per document; read its `confidence`; if >= 0.9 report the fine label (industry group), else report the parent label (division). One request per document, no second model, no extra calls.
- [[cb-consistency-choices]] — Re-run one borderline moderation post through an 8-`Choice` rubric 15 times per condition (TypeSafe vs LLMs) and measure label stability; adding an `uncertain` outcome below top-probability 0.60 lifts TypeSafe agreement from 90.8% to 99.2% while still acting automatically on 74.2% of answers.
- [[cb-consistency-nouls]] — Re-run one auto-insurance claim through a 14-`Noul` rubric 15 times per condition (TypeSafe vs LLMs); TypeSafe's probabilities barely move (mean std 0.0102) but can still straddle 0.5, so map P(true) into yes / uncertain (0.30-0.70 inclusive) / no and send the middle to a human.
- [[cb-entity-alignment]] — Decide, for each of 450 candidate duplicate pairs (two beer catalogues), whether to merge, drop, or send to a human curator, using ONE `Score` question (3 levels) plus three companion `Noul` questions in a single request. No fitted threshold anywhere.
- [[cb-function-calling]] — Turn a natural-language sentence into a call to an ordinary typed Python function (name + arguments), where every argument is an evaluated enum with a probability, via a `Dispatcher` built from a plain-words spec. Reach for it when function arguments come from fixed lists and you want per-argument confidence.
- [[cb-hierarchical-classification]] — Classify a document to a leaf of a deep taxonomy (patents, retail, biomedical, code) by asking one `Choice` per node over its direct children, in parallel across K beam paths. Beam K=3 got 4/4 expected leaves; greedy got 2/4.
- [[cb-skill-suggestion]] — Pick at most one skill for an agent turn out of the 182 in Nous Research's Hermes catalog using two TypeSafe requests (rank all, then re-check top 3). Cuts wrong skill loads 16.8% -> 7.3% and needless loads 9.8% -> 4.0%.
- [[demo-smart-home]] — Demo app that evaluates smart-home requests with one up-front batch of "speculative" questions, uses an LLM only to split compound requests and to chat; reach for it as the reference for [[speculative-fan-out]] plus LLM fallback.
- [[use-case-map]] — Brainstorming catalogue: 5 headline categories, 20 industry/task idea lists, and a 10-row "decision shape" table. Open the closest industry, scan the example decisions, adapt to your own documents and actions.
- [[community-guide-devto]] — THIRD-PARTY blog guide: setup, three primitives, five patterns, launch-week projects, failure modes, an "honest scorecard". Quotes TypeSafe's own numbers as self-run and unreproduced. Read for the cascade economics and the skeptic's checklist.
- [[community-guide-marktechpost]] — THIRD-PARTY runnable notebook (Python, typesafe-sdk 0.7.0) covering all three primitives, state shapes, the confidence formula, fan-out vs separate calls, gated routing, composite scoring, function calling, counting, and the async/typed production shape. Contains code and prose but **no measured outputs** — it prints results at runtime; the article quotes none.
- [[agent-operating-protocol]] — Runbook for an autonomous agent deciding whether and how to use a System One model: availability check -> classify shape -> pick tool -> design question -> fan out once -> route on confidence -> act/escalate -> report. Advisory only in this owner's repo.
- [[question-design-checklist]] — Write the state, pick Choice/Score/Noul, word options/levels/criteria, add escape outcomes, set thresholds, add companion Nouls, batch in one call. Every rule carries the example or number that proves it.
- [[retrieval-protocol-opus]] — How the Opus agent answers from THIS vault: grep-first routing via `Home.md` -> topic hub -> note, which notes to open per question type, depth rules, citation format, and how to say "the vault doesn't cover it". Plus how System One tools and embeddings shortlist big corpora.
- [[when-to-use-which-model]] — Executable decision matrix: deterministic code vs MiniLM-style embeddings vs a System One model (Jev hosted / Laya local / Kev / openjev) vs Sonnet vs Opus. Ladder, escalation triggers, never-use list. Every number cites the note it came from; trust labels matter.

Back to [[Home]].
