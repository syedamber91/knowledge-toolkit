---
title: Model Tiering Sonnet Opus
kind: playbook
source: Owner rule for this build + synthesis of vault notes (Opus synthesis pass, 2026-10-02)
source_url: vault-internal
tags: [agent-tooling, cost-latency, routing]
topics: [topic-model-selection, topic-agent-integration, topic-cost-latency]
---
# Model Tiering: Sonnet Reads, Opus Synthesizes and Routes
> Owner rule: Sonnet for READING and CONDENSATION; Opus for SYNTHESIS and for INFORMATION RETRIEVAL/ROUTING. System One models sit below both as the cheap judgment layer. The orchestrating main session dispatches both tiers because a subagent cannot spawn subagents.

## The rule (owner, stated for this build)
| Tier | Owns | Never owns |
|---|---|---|
| **Sonnet** | bulk reading of source docs; condensation into notes; extraction/summarising; mechanical orchestration (file moves, format checks) | final answers; resolving contradictions between sources; deciding which sources matter |
| **Opus** | synthesis across notes; retrieval/routing (which notes/sources to open, in what order, how deep); contradiction resolution; final answers and recommendations | bulk reading it can delegate (cost) |
| **System One (Jev / Laya)** | narrow typed judgments inside either tier's workflow: rerank, find, classify, screen, verify | prose, synthesis, reasoning ([[when-to-use-which-model]]) |
| **Code** | anything exact | — |

Why this split matches the vault's evidence:
- Reading is bulk and parallel; condensation is the step where a cheaper LLM is adequate when its output is checked downstream [inference]. The vault itself was built this way: 10 Sonnet readers -> 64 notes -> one Opus synthesis (this note).
- Routing/synthesis is where errors compound: a wrong routing choice hides the right evidence, and "the second pass can only reject what the wide ranking hands it" ([[cb-skill-suggestion]]). Spend the expensive model there [inference].
- Expensive reasoning should run only where a cheaper signal says it is needed: SDE cascade spends `gpt-5.5` reasoning dollars only when the Jev verifier fires ([[cb-sde-cascade]]); intent routing sends only some intents to an LLM ([[intent-routing]]).

## Cost / latency anchors (vault numbers; no Sonnet/Opus list prices are in the vault)
| Model | Number | Source |
|---|---|---|
| Jev | $0.042/M input, output free; 111-114 ms per 8-14-question call; $0.000043-46 per call | [[models-and-versions]], [[cb-consistency-nouls]], [[cb-consistency-choices]] |
| Claude Haiku 4.5 | 0.99-3.9 s, $0.0015-0.0035 per rubric call (33-76x Jev cost) | same cookbooks |
| Claude Sonnet 5 | 67.8% on TypeSafe's 4-workflow eval at 293x Jev cost/case and 195x latency (TypeSafe self-run) | [[community-guide-devto]] |
| Claude Opus 4.8 (reasoning) | 10.4-13.9 s, $0.028-0.034 per rubric call (617-805x Jev) | [[cb-consistency-choices]], [[cb-consistency-nouls]] |
| Opus 5 | 73.1% on the 4-workflow eval; $0.032 vs Jev $0.0002 per computer-use decision; 5.2 s vs 0.13-0.38 s | [[community-guide-devto]] |
Implication: one Opus call costs roughly as much as several hundred Jev calls on these workloads [inference from the ratios]. Use Jev/code to narrow, Opus to decide.

## Who does what in a retrieval/synthesis job
```
main session (orchestrator; holds the Agent tool)
 ├─ dispatch N Sonnet readers in ONE message (parallel)  -> each writes condensed notes / returns findings
 ├─ optional: Jev/MiniLM/BM25 narrowing over a big corpus  (jev_find / jev_rerank, [[jev-mcp-server]])
 └─ dispatch ONE Opus advisor (or run Opus itself)        -> routes over notes, resolves conflicts, answers
```
- **Honest limitation:** a subagent cannot spawn subagents. So the *main session* must fan out Sonnet readers and then call the Opus advisor; an Opus subagent cannot itself dispatch readers. If the main session is already Opus it can do the synthesis inline.
- Fan out in one message (parallel), mirroring Jev's own "ask everything in one request" rule ([[speculative-fan-out]]) [inference: analogy, not a measured claim].

## Hand-off format (Sonnet -> Opus)
Use the vault's own note contract (it is what made this synthesis possible):
1. Frontmatter: `title`, `kind`, `source`, `source_url`, `tags` (fixed vocab), `topics`.
2. One-line gist, then mechanism with **every number**, worked examples (inputs -> outputs), numbers table, gotchas, related links.
3. **Flag, don't resolve:** contradictions quoted with location ("dev.to says X; OpenRouter says Y"); `[inference]` on anything not in the source; "not stated in source" for gaps.
4. Reply to orchestrator: files written, word counts, unplaceable or contradictory facts with locations (<200 words).
Opus then: reads the notes (not the raw source), opens raw only to spot-check a disputed number ([[retrieval-protocol-opus]]).

## Opus responsibilities checklist
- Decide which notes matter for the question (route by `topics:`/`tags:` then grep) — [[retrieval-protocol-opus]].
- Surface every disagreement with both citations; never average conflicting numbers.
- Mark synthesis-only claims `[inference]`; state "vault doesn't cover it" plainly.
- Choose the cheapest adequate tool per sub-task via [[when-to-use-which-model]].

## Gotchas
- Sonnet-written notes can still carry reader errors: e.g. one reader asserted confidence formula is unknown ([[confidence]]) while another captured the published formula ([[community-guide-marktechpost]]). Opus must cross-check, not trust either note alone.
- Don't let Opus re-read raw sources wholesale — that defeats the tiering. Spot-check only disputed numbers.
- Don't use Jev as the synthesizer: it does not generate text ([[jev-1-13-jaggedness]] #9).

## Related
[[when-to-use-which-model]] · [[retrieval-protocol-opus]] · [[agent-operating-protocol]] · [[privacy-and-cost-gates]] · [[topic-model-selection]] · [[topic-agent-integration]]
