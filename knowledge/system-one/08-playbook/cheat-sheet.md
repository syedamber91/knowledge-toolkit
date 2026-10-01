---
title: Cheat Sheet
kind: playbook
source: Synthesis of vault notes (Opus synthesis pass, 2026-10-02)
source_url: vault-internal
tags: [system-one, primitives, api-sdk]
topics: [topic-model-selection, topic-calibration, topic-cost-latency, topic-agent-integration]
---
# System One Cheat Sheet
> One page: primitives, thresholds, latency/cost, minimal calls, model landscape, the 12 jev-mcp tools. Follow links for caveats.

## Primitives ([[primitives-overview]])
| Type | Ask | Request | Returns | Limits |
|---|---|---|---|---|
| Choice | which of these? | `criteria: {option: desc-or-null}` | `choice`, `probabilities` (sum 1), `confidence` | max 255 options (~240 reliable) |
| Score | which level? | `criteria: [level0, level1, ...]` | `score` (prob-weighted, fractional), `legend`, `probabilities`, `confidence` | 2-10 levels; 11 = error |
| Noul | is this true? | optional `criteria: {true, false}` | `noul` 0-1 (no confidence) | — |
Confidence = `(n x peak - 1)/(n - 1)` ([[community-guide-marktechpost]]; fits all pairs in [[confidence]]). Question IDs never reach the model. Backtick state paths. Score normalize: `score/(levels-1)`.

## Default thresholds seen in sources (illustrative; tune) — [[question-design-checklist]] §H
| Decision | Threshold |
|---|---|
| route to human (Choice confidence) | < 0.5 / 0.6 |
| act on high-stakes action | > 0.85 / 0.9, else confirm |
| Choice uncertain | top prob < 0.60 |
| Noul uncertain band | 0.30-0.70 |
| verifier escalate | any P(wrong) > 0.7 (max) |
| citation auto-accept | conf >= 0.8 |
| fine vs coarse label | conf >= 0.9 |
| exists found / absent | >= 0.7 / < 0.35 |
| skill gate / fits | 0.30 / 0.30 |
| jev-mcp defaults | verify 0.8; screen block 0.75 / review 0.25; noul 0.85; classify 0.85 + margin 0.5; audit wrong 0.7; review .8/.5/.7 |

## Latency / cost ([[privacy-and-cost-gates]])
| Item | Value |
|---|---|
| Jev price | $0.042 / M input tokens; output free |
| Jev per call | ~100 ms vendor; 111-114 ms measured; 150-500 ms via MCP; 230-317 ms third-party |
| Jev per 8-14-question call | $0.000043-0.000046 |
| Batching 13 questions | 12.2x cheaper, 10.0x faster (Primitives page: 11.5x / 9.6x) |
| Rate limits | 100K tok/s, 40 req/s (docs) — dev.to says 250K tok/s, 1,200 req/min |
| Context | 64k/request; 32k state + longest question (OpenRouter: 32,000 total) |
| Laya local | 23-43 ms, $0 licence, ~1 GB RAM |
| MiniLM + LR (CPU) | 5.7-6.8 ms |
| Haiku 4.5 | 0.99-3.9 s, 33-76x Jev cost |
| Opus 4.8 reasoning | 10.4-13.9 s, 617-805x Jev cost |

## Minimal calls ([[quickstart]], [[sdk-python-usage]], [[sdk-javascript]])
```python
from typesafe_sdk import TypeSafeClient, Choice, Noul, Score   # pip install typesafe-sdk ; Python >= 3.10
client = TypeSafeClient(model="jev-1.13.0")                     # reads TYPESAFE_API_KEY; pin when thresholds tuned
r = client.system_one(state={"msg": text}, questions={
    "team": Choice(instructions="Which team should handle `msg`?", criteria={"billing": "...", "technical": "...", "other": None}),
    "urgent": Noul(instructions="Does `msg` convey urgency?"),
    "sev": Score(instructions="How severe is the issue in `msg`?", criteria=["Cosmetic", "Broken, workaround exists", "Blocking"])})
r.choices["team"].confidence; r.nouls["urgent"].noul; r.scores["sev"].score; r.model  # log r.model
```
```http
POST https://api.typesafe.ai/v1/systemone   Authorization: Bearer $TYPESAFE_API_KEY
{"state": "...", "model": "jev-latest", "questions": {"q": {"type": "noul", "instructions": "..."}}}
```
JS: `npm install @typesafe-ai/sdk` (Node 20+); `client.systemOne({state, questions})` with `choice()/noul()/score()`. Gateways (Python `base_url`): OpenRouter `https://openrouter.ai/api` + `~typesafe/jev-latest`; Vercel `https://ai-gateway.vercel.sh/typesafe` + `typesafe-ai/jev`; Pydantic `https://gateway-us.pydantic.dev/proxy/typesafe` + `jev-latest`. Errors: 401, 422, 429, 529 ([[http-api-reference]]).

## Model landscape ([[system-one-alternatives-overview]], [[jev-vs-laya]], [[benchmarks-and-comparisons]])
| Model | What | Size / host | Key number (who measured) |
|---|---|---|---|
| Jev 1.13 (`jev-1.13.0`) | TypeSafe hosted System One | undisclosed; cloud | rerank top-1 5->18% (TypeSafe); BANKING77 76.3% on 77 labels (nibzard) |
| Laya | Convai encoder, Apache 2.0 | 421M EN / 322M multilingual; CPU ok | TREC 86.6%, BANKING77 37.0% default (SOTAAZ); 0.766 fine-tuned (own) |
| Kev | Jared Palmer, Qwen-based, Apache | 0.8/4/9(/27)B | Kev-9B 0.822 vs Jev 0.857 (author) |
| openjev (razorback16) | DiffusionGemma 26B server | 26B GPU | BANKING77 66.9%, 81 ms (SOTAAZ) |
| NanoJev | game decisions only | 0.6B | TREC 18.4% (SOTAAZ) — not for text |
| MiniLM + LR | trained embedding classifier | CPU | TREC 90.4%, BANKING77 90.3% (SOTAAZ) |
"OpenJev" names four different projects ([[openjev-and-nanojev]]).

## The 12 jev-mcp tools ([[jev-mcp-server]], `npx -y @jkudish/jev-mcp`, Node 22+)
| Tool | One line |
|---|---|
| `jev_verify` | claims vs evidence -> verified/contradicted/unsupported |
| `jev_screen` | injection/substance/relevance before content enters context |
| `jev_noul` | calibrated probability of propositions (<=64) |
| `jev_find` | best of <=250 candidates + `exists` |
| `jev_rerank` | score and sort <=250 candidates |
| `jev_classify` | label <=64 items vs <=250 classes |
| `jev_decide` | choose among 2-6 options with evidence, priorities, escape hatches |
| `jev_compare` | relation of two passages (same_fact/contradicts/different_facts) |
| `jev_extract` | regex candidates -> verbatim pick |
| `jev_audit` | extracted values vs source, max-gated p_wrong |
| `jev_review` | diff rubric -> auto/review/escalate |
| `jev_gate` | review + completion claims vs evidence |
Repo defaults (jev-checkpoint): decide / verify / review-gate / screen. Advisory only.

## Never use System One for
math, counting, dates, generation, explanations, multi-hop reasoning, huge irrelevant state, safety boundaries — [[when-to-use-which-model]] §5, [[jev-1-13-jaggedness]].

## Related
[[when-to-use-which-model]] · [[agent-operating-protocol]] · [[question-design-checklist]] · [[anti-patterns]] · [[privacy-and-cost-gates]] · [[retrieval-protocol-opus]] · [[model-tiering-sonnet-opus]]
