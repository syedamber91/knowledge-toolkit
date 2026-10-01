---
title: Agent Operating Protocol
kind: playbook
source: Synthesis of vault notes + repo docs/JEV-MCP-SETUP.md + .claude/skills/jev-checkpoint/SKILL.md (Opus synthesis pass, 2026-10-02)
source_url: vault-internal
tags: [agent-tooling, routing, confidence]
topics: [topic-agent-integration, topic-routing, topic-calibration, topic-guardrails]
---
# Agent Operating Protocol
> Runbook for an autonomous agent deciding whether and how to use a System One model: availability check -> classify shape -> pick tool -> design question -> fan out once -> route on confidence -> act/escalate -> report. Advisory only in this owner's repo.

## Hard rules (bind every step)
1. **Advisory only.** Jev gates nothing and never replaces the repo's own gates: G2 cited-quote verification (`soic_wiki/sector_gate.py`, 80%) and `verify_briefs.py`. Never edit a quote or REF code because Jev disagreed. (repo `jev-checkpoint` skill; CLAUDE.md)
2. **Never fake a result.** No `mcp__jev__*` tools -> say so in one line, fall back. Never invent a probability.
3. **No retry loops.** One call per moment; on error report it. `jev_decide`: "One call per unchanged decision; repeat only with materially new evidence" ([[jev-mcp-server]]).
4. **Privacy.** Nothing from `.env`, keys, licensed/private/do-not-quote material goes to a hosted tool ([[privacy-and-cost-gates]]).
5. **Typed output guarantees the interface, not truth** ([[typesafe-agent-skill]] Rule 4; [[jev-mcp-server]]).

## Step 0 — availability
- Run `ToolSearch "jev"` once, unconditionally (tools are usually deferred; "are they loaded?" is the wrong test — repo CLAUDE.md).
- None listed -> one line ("Jev tools unavailable; using <fallback>") and choose: Laya/local model if installed ([[laya]]), deterministic code, or an LLM tier ([[when-to-use-which-model]]).
- Common causes (repo setup doc): multi-repo cloud session (clones' `.mcp.json` not read); network policy blocking `api.typesafe.ai`; workspace not trusted; MCP client filtering env drops `TYPESAFE_API_KEY` ([[jev-mcp-server]]).

## Step 1 — classify the task shape
Rule/math/date/count -> code. Bounded pick -> Choice. Yes/no -> Noul. Degree -> Score. Rank many -> shortlist + Noul per pair. Prose/reasoning -> LLM. Full table: [[when-to-use-which-model]] §1.

## Step 2 — pick the tool
### The 12 `jev-mcp` tools (`@jkudish/jev-mcp`; repo pins 0.11.0) — from [[jev-mcp-server]]
| Tool | Call when | Key defaults / limits | Output to read |
|---|---|---|---|
| `jev_verify` | claims vs evidence you hold (before a claim enters a report/PR/commit) | `auto_accept` 0.8; match quotes in code first | verdict verified/contradicted/unsupported, confidence, action auto/review |
| `jev_screen` | fetched/pasted content before it enters context | `block_at` 0.75, `review_at` 0.25 on injection prob | injection/substance/relevance, action pass/review/block/skip (advisory; you enforce) |
| `jev_noul` | bare probability of a proposition | <=64 props, 2,000 chars each, 150k total; `auto_accept` >0.5, default 0.85 | probability, label likely/unlikely/uncertain (context is not proof) |
| `jev_find` | single best of <=250 candidates + does any answer exist | 2,000 chars/candidate | `exists`, `exists_verdict` answered/partial/absent, top[] |
| `jev_rerank` | ordering is the deliverable | <=250 candidates, 100k chars aggregate | ranked[] relevance; any malformed answer invalidates all |
| `jev_classify` | label many items vs a catalog | <=250 classes, 64 items, 8,000 item-class budget; `auto_accept` 0.85, `minimum_margin` 0.5 | per item class, margin, confidence, decision |
| `jev_decide` | close choice among 2-6 bounded options with evidence + priorities | escape hatches `ask_user`/`investigate`/`none` on by default | selected, escaped, confidence, contradicted_requirements |
| `jev_compare` | relation of two passages (drift, reconciliation) | 20,000 chars each; optional aspects | same_fact/contradicts/different_facts (same_fact != true) |
| `jev_extract` | regex-findable fields, verbatim | 32 fields, 20 matches/field, doc 50k, regex 1 s | value, status auto/review/not_found/... |
| `jev_audit` | extracted values before trusting them | 32 records, `wrong_at` 0.7, max-gated | p_wrong per record; any >= 0.7 escalates |
| `jev_review` | a diff before "done" | 16 files; weights .4/.3/.15/.15; `auto_accept` .8, `review_at` .5, `composite_floor` .7 | action auto/review/escalate, reason_codes |
| `jev_gate` | diff + completion claims vs evidence | <=16 claims, 16 evidence items, 200k aggregate | action; a contradicted claim escalates |
Repo default moments (jev-checkpoint): close choice -> `jev_decide`; claim into report -> `jev_verify`; before "done" -> `jev_review`/`jev_gate`; external content -> `jev_screen`. Others only when the task is exactly that shape.
Without MCP: same primitives via SDK/HTTP ([[quickstart]], [[http-api-reference]]); local Laya via `laya-serve` on `POST /v1/systemone` ([[laya]]).

## Step 3 — design state + question
Checklist: [[question-design-checklist]]. Minimum: only needed fields in state; one judgment per question; full option list + `other`/`none`; levels as situations; high Noul = yes.

## Step 4 — fan out in ONE call
All independent questions over the same state go in one request, including speculative ones; code ignores irrelevant answers ([[speculative-fan-out]]). Batching 13 questions: identical answers, 12.2x cheaper, 10.0x faster ([[cb-parallel-questions]]; the Primitives page quotes 11.5x/9.6x for the same cookbook — [[primitives-overview]]). Second request only when it needs the first answer to fetch data, build state, or pick options ([[primitives-overview]]).

## Step 5 — read confidence, route by thresholds
| Signal | Rule (illustrative; tune on your data) | Source |
|---|---|---|
| Choice/Score `confidence` | floor 0.5-0.6 -> human; high-stakes act > 0.85-0.9 else confirm | [[confidence]], [[confidence-gated-routing]] |
| Choice top probability | < 0.60 -> `uncertain` | [[cb-consistency-choices]] |
| Noul | < 0.30 no, > 0.70 yes, between -> review | [[cb-consistency-nouls]] |
| Verifier batteries | max over checks; > 0.7 -> escalate | [[cb-sde-cascade]] |
| Multi-part calls | call confidence = min over parts | [[cb-function-calling]], [[cb-date-extraction]] |
| `invalid_response` / truncation | never `auto`; treat as review/escalate | [[jev-mcp-server]] |
Low confidence on Score = levels overlap, multi-dimensional, or thin state: fix the question, not just the threshold ([[confidence]]). Low confidence on an unused branch: ignore ([[typesafe-agent-skill]]).

## Step 6 — act or escalate
- High: act (code owns the side effect). Medium: confirm/flag. Low: human, clarification, or bigger model ([[confidence]] three paths).
- Low-confidence Jev result in this repo = **read the primary source yourself** (jev-checkpoint rule 2).
- Escalation target per [[model-tiering-sonnet-opus]]: generation -> Sonnet; synthesis/conflict -> Opus.

## Step 7 — report
One line per call: tool, verdict, confidence/probability, action taken, cost/usage if relevant. Errors reported, not retried. Log `response.model` — aliases move ([[models-and-versions]]).

## Setup facts (repo `docs/JEV-MCP-SETUP.md`, measured 2026-09-30)
| Where | Steps |
|---|---|
| Cloud (claude.ai/code) | (1) env network access -> Custom, add `api.typesafe.ai`, keep default list; (2) `TYPESAFE_API_KEY` in the environment's settings, **never in chat** (anyone using the env can read it); (3) start a **one-repo** session (multi-repo sessions don't read clones' `.mcp.json`); (4) verify: `ToolSearch "jev"`, trivial `jev_decide`, proxy status shows no `api.typesafe.ai` rejection |
| Proxy gotcha | Node `fetch` ignores `HTTPS_PROXY` unless `NODE_USE_ENV_PROXY=1` (Node >= 22.21); without it: "Jev provider typesafe: request failed" while curl works. `.mcp.json` sets it |
| Local CLI | export `TYPESAFE_API_KEY` in the launching shell; approve server (trust prompt, or `{"enabledMcpjsonServers": ["jev"]}` in uncommitted `.claude/settings.local.json`); don't use `enableAllProjectMcpServers` when another server must stay gated; verify `claude mcp list`, `/mcp`, one real call |
| Not done on purpose | no hooks: a Stop/PreToolUse hook would send diffs to a third party every turn and an exit-2 hook turns advisory into a gate |
jev-mcp needs Node 22+; HTTP mode requires `JEV_MCP_AUTH_TOKEN` unless loopback ([[jev-mcp-server]]).

## Related
[[when-to-use-which-model]] · [[question-design-checklist]] · [[privacy-and-cost-gates]] · [[anti-patterns]] · [[jev-mcp-server]] · [[typesafe-agent-skill]] · [[topic-agent-integration]]
