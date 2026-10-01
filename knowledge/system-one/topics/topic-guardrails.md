---
title: Guardrails & verification
kind: topic
source: generated from note frontmatter
tags: [system-one]
topics: []
---
# Guardrails & verification
> Screening, citation checks, hazard scoring, pass/review/block.

## Notes on this topic (12)
- [[jev-1-13-jaggedness]] — Nine documented failure modes of `jev-1.13` with the prescribed workaround for each. An agent should consult this to decide when NOT to call Jev (or how to reshape the question). Source: "Applies to `jev-1.13`. Last reviewed 2026-09-17." Many are expected to be fixed in later versions.
- [[noul]] — A yes/no question; returns one number 0..1 = probability the answer is yes. Use for checks, guardrails, verification and as a ranking signal.
- [[cb-citation-check]] — Catch wrong or hallucinated LLM citations: an ordinary string match finds fabricated quotes, then ONE `Choice` question reads the quote's section and decides supports / contradicts / says nothing; a 0.8 confidence gate sends weak verdicts to a human.
- [[cb-classifying-rag-passages]] — Between retrieval and generation, score every retrieved passage with ONE `system_one` call of four `Noul` questions, then route it in plain code to evidence / conflict / dropped. Use when similarity search hands noisy, contradicting or prompt-injected passages to an answering LLM.
- [[cb-llm-guardrails]] — Screen every message into and out of an LLM app with ONE request (a battery of `Noul` hazard questions + one `Score` severity question), then threshold in your own code to pass / review / block / support.
- [[cb-sde-cascade]] — Structured-data-extraction cascade: extract with a cheap mini model -> verify per field with TypeSafe Noul questions -> escalate to a reasoning model only if any field's P(wrong) > 0.7. Gets most of the big model's quality at a fraction of the cost.
- [[cookbooks-overview]] — Index of 19 end-to-end TypeSafe recipes grouped by theme, with each recipe's one-line outcome, headline numbers and difficulty level.
- [[use-case-map]] — Brainstorming catalogue: 5 headline categories, 20 industry/task idea lists, and a 10-row "decision shape" table. Open the closest industry, scan the example decisions, adapt to your own documents and actions.
- [[jev-mcp-server]] — Third-party (author J. Kudish, MIT, "early software") MCP server exposing TypeSafe's Jev model as **twelve typed-judgment tools** — verify, screen, noul, find, rerank, classify, decide, compare, extract, audit, review, gate — each ~150–500 ms and a fraction of a cent.
- [[agent-operating-protocol]] — Runbook for an autonomous agent deciding whether and how to use a System One model: availability check -> classify shape -> pick tool -> design question -> fan out once -> route on confidence -> act/escalate -> report. Advisory only in this owner's repo.
- [[anti-patterns]] — Every documented failure mode, trap and pitfall across the vault, grouped, each with the fix and the note that proves it. Section F lists source disagreements and vendor bias.
- [[privacy-and-cost-gates]] — What may go to a hosted System One API (Jev, directly or via a gateway) vs what must stay local; owner rules; cost and latency budgets with sourced numbers; kill-switch conditions.

Back to [[Home]].
