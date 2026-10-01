---
title: Community Guide (DEV.to, Valyu)
kind: playbook
source: "How to Use Jev: A practical guide to TypeSafe's System One model" (DEV Community, Valyu AI org feed; author not named in the captured text; comments dated Sep 21 and Sep 23 2026)
source_url: https://dev.to/valyuai/how-to-use-jev-a-practical-guide-to-typesafes-system-one-model-g5e
tags: [use-case, patterns, model-limits]
topics: [topic-routing, topic-cost-latency, topic-model-selection]
---
# Community Guide (DEV.to, Valyu)
> THIRD-PARTY blog guide: setup, three primitives, five patterns, launch-week projects, failure modes, an "honest scorecard". Quotes TypeSafe's own numbers as self-run and unreproduced. Read for the cascade economics and the skeptic's checklist.

Provenance flags: author-reported summary of TypeSafe materials and third-party projects; all benchmark figures are TypeSafe's (self-run) or the project authors'. The article itself says "launch-week artefacts, not production case studies". Includes a Valyu retrieval example (the publishing org is a search vendor — [inference] commercial interest in the "retrieve then judge" framing).

## Headline claims (as stated)
- Jev returns typed probabilistic decisions, answers all questions in one parallel pass in **70-500 ms**, **$0.042 per million input tokens**, output free. Launched **September 15, 2026** with **$40M led by DCVC**; built by **Diogo Almeida** (described as co-inventor of RLHF and InstructGPT at OpenAI). "System One" named after Kahneman's fast thinking.

| | Jev | Frontier LLMs |
|---|---|---|
| End-to-end latency | 70-500 ms | 3 s to 329 s |
| Input price | $0.042/MTok | $0.20-$10/MTok |
| Output price | free | ~5x input |
| Structured-output errors | 0% (by construction) | 0.58%-45.5% |
Caveat given up front: TypeSafe's own numbers, self-run, unreproduced.

## Setup
- Key: console.typesafe.ai/settings/keys (early access **waitlisted**) or Vercel AI gateway; `export TYPESAFE_API_KEY=...`.
- Python 3.10+: `pip install typesafe-sdk` or `uv add`. JS/TS (Node 20+): `npm install @typesafe-ai/sdk`. Both read `TYPESAFE_API_KEY`, default model `jev-latest`. Single endpoint `POST https://api.typesafe.ai/v1/systemone`.
- Agent skill: `claude plugin marketplace add typesafe-ai/skills`; `claude plugin install typesafe@typesafe-ai`; or `npx skills add typesafe-ai/skills --skill typesafe-ai`. See [[typesafe-agent-skill]].

## The three primitives (as described)
- **Choice**: one option from a set. Returns `.choice`, `.probabilities` (per option), `.confidence`. **Up to 255 options**, each costing a few tokens — pass the full list, add an explicit `other` so the model can say nothing fits.
- **Score**: position on a spectrum; **2 to 10 ordered levels** described in words; array order gives the index (level 0 = first). Returns `.score` (can land between levels, e.g. 1.035), `.probabilities`, `.confidence`.
- **Noul**: yes/no as probability 0-1 in `.noul`; no confidence field (the number is the belief).
- **State**: string, JSON object, or array of text (object when several contexts; array for a conversation). **Text only** — no images/audio/video.
- **Context limits (as stated here):** **64k tokens** for state and all questions together; **32k tokens** for state plus the single longest question. (Conflicts with OpenRouter's 32,000 total — see Flags.)
Worked call: ticket "Duplicate charge" with order A-104 (two $49 captured charges) and refund policy; questions: department Choice (billing/technical/sales), frustration Score (3 levels), refund_requested Noul, policy_supports Noul. TS example: `choice(...)`, `noul(...)`, types inferred. See [[primitives-overview]], [[state]].

## Five patterns
1. **Speculative fan-out.** Questions evaluate in parallel so a 10th question costs tokens, little time. Ask everything up front (even branch-only questions) and let code pick relevant ones. Example ticket: category Choice (bug_report/billing/feature_request/account), bug_severity Score (3), has_repro Noul, refund_wanted Noul, frustration Score; code: bug_report and severity > 1.5 and has_repro > 0.6 -> escalate; billing and refund_wanted > 0.7 -> refund flow. TypeSafe cookbook cited: **13-question regulatory briefing over a long Wikipedia article: batching = 12.2x cheaper, 10.0x faster, identical answers** vs one-at-a-time. See [[speculative-fan-out]].
2. **Confidence-gated routing.** Jev trained with **RLCD (Reinforcement Learning for Calibrated Decisions)**, optimising probabilities against outcomes not preference, so confidence is meaningful in aggregate. One threshold per action by cost of being wrong. Example: confidence < 0.5 -> human; check_balance (read-only, low bar); approve_transfer needs > 0.85 else ask user to confirm; else human. Raw `.probabilities` available; a **flat distribution usually signals bad criteria**, not a confused model. See [[confidence-gated-routing]], [[confidence]].
3. **Composite scoring.** Break a fuzzy judgment into independent Score dimensions, combine with code weights. Resume example: python_depth (5 levels) 0.40, team_leadership (5) 0.25, system_design (5) 0.35; `composite = sum(w * score/4)`. Re-weighting = code change, A/B-able. See [[composite-scoring]].
4. **The Cascade.** Jev "is the thing that decides which requests deserve" a frontier model. Intent Choice (order_status, product_question, return_exchange, complaint) + complexity Score (3 levels); confidence < 0.5 -> human; order_status = pure code, no LLM; product/returns load specialists; complaint with complexity > 1 or confidence < 0.5 -> human. **Economics (TypeSafe per-case figures):** 1M tickets ~**$6,480 instead of $30,400**, with ~**800,000 answered in under half a second instead of ten** (as written; "ten" unit unspecified). Commenter: biggest saving is requests that skip the model entirely (order lookup).
5. **Retrieve, then judge.** Jev knows nothing beyond the state; jaggedness page: "retrieve and filter in code first, and send only the fields the question needs". Whatever builds the state decides what Jev may know; pad it and lose accuracy; ground it in weak sources and get calibrated judgments of bad material. Example with Valyu search (PubMed + arXiv, from 2024-01-01, 20 results, relevance_threshold 0.5), then per paper: is_rct Noul, reports_mace Noul, evidence_strength Score (4 levels); keep if is_rct > 0.7 and strength > 1.5. Cost ~**$0.0004 each**; 20 papers x 4 dimensions "well under a cent". Same shape as TypeSafe's RAG passage classification and citation-check cookbooks ([[cb-classifying-rag-passages]], [[cb-citation-check]]).

## What people shipped in the first 48 hours (all self-reported)
| Project | Claim |
|---|---|
| 1kpapers.com (Hassan El Mghari) | 1,018 papers: summaries via DeepSeek V4 Flash **$3.99**; Jev classification (title+summary+24 candidate topics, one Choice) **$0.08**; median **256 ms** per paper; author running evals before replacing existing classifications |
| browser-use/jev-ultrafast (641 stars) | indexed element table; one Jev request picks operation (CLICK, TYPE_TEXT, SELECT, SCROLL, WAIT, DONE, BLOCKED) + target; small LLM only for TYPE_TEXT; Zurich->London on real Google Flights **7.1 s, $0.0039**; fan-out applied to actions (two decisions, one call) |
| awlevin/typesafe-computer-use | OCR reads screen, Jev picks action, writer model only for free text; Jev vs Opus 5 (bare screenshot): cost/decision **$0.0002 vs $0.032**; 12-step task **$0.003 vs $0.40-$0.90**; model latency **0.13-0.38 s vs 5.2 s**; end-to-end step **~1.5 s vs ~5.5 s**. Author caveat: frontier model read event dates off pixels; classifier needed explicit date parsing — "every piece of reasoning the frontier model does for free has to be rebuilt ... as deterministic state" |
| jarrodwatts/jev-trader | one decision per Monad block (~300 ms); Kuru MON-USDC order book -> buy/sell; post-only limit one tick inside the touch; reported model latency **~81 ms**; two RPC round trips; dry-run mode with real book data (see Flags re mock) |
| RomanSlack/jev-drone | layers: 500 Hz geometric controller (code); 50 Hz guidance/safety reflex (code, always owns safety); 15 Hz camera->symbolic scene (classical CV); ~2.5 Hz tactical judgment (Jev, advisory only); one call = Choice over manoeuvres + Score risk + Noul target lost-vs-occluded. README: Jev "cannot be the perception layer, and it cannot run at control rate" |
| fhshaik/typesafe-mario (73 stars) | Super Mario Bros from emulator RAM as object-centric JSON, no screenshots |
| devagrawal09/jev-review (48 stars) | staged reviewer: Noul risk matrix -> Choice/Score file profiles -> evidence selection -> severity -> conditional routing |
| TheoLeeCJ/openjev (166 stars) | typed option probabilities from a 4B open model's logits in one forward pass; explicitly reproduces the interface, not Jev's model/training |
| phyous/tsai-sc | Jev completes first StarCraft shareware mission over 421 decisions with verification report |
| AbdelStark/awesome-typesafe | ecosystem index ([[awesome-typesafe-jev]]) |
Pattern across all: keep loop, safety and arithmetic in code; Jev for the narrow judgment code finds hard to phrase.

## Failure modes ("jaggedness" page of jev-1.13, as relayed)
- **Reads literally**: negations, scoping words, implied conditions at face value. Tell: you catch yourself explaining what you really meant — that is the missing half of the instruction.
- **Not a calculator / cannot count reliably**; error grows with count size. Iterate in code, one Noul per item (e.g. `items[i]` is a fruit; `count = sum(noul > 0.5)`).
- **Dates are text**, not ordered quantities (order, gap, window unreliable). Extraction = Choice over enumerated months/days with an explicit "not stated" option; assembly/ordering in code.
- **Context rot**: accuracy falls as state fills with irrelevant material; retrieve/filter first.
- **State not treated as hostile**: text engineered to argue for its own classification can move the answer; user-controlled content in state is your threat model; test it.
- **Contradictory instructions/criteria confuse it**: e.g. a Noul where true maps to "no" underperforms; criteria are an extension of the instruction.
- **Does not generate** text/code/summaries; for extraction get candidates with regex/generative model and let Jev pick.
- Meta-rule: "Avoid asking the model something code can compute exactly. Avoid hiding several judgments inside one question." See [[jev-1-13-jaggedness]], [[anti-patterns]].

## Operational notes
- Rate limits jev-1.13: **250,000 tokens/second** and **1,200 requests/minute**; exceeding either = HTTP 429; SDKs retry with exponential backoff, honour `retry-after`; TypeSafe warns limits "moving without notice" as GPU capacity lands.
- **Pin the version** if tuning thresholds: `jev-latest` currently resolves to `jev-1.13.0` and will move; `model` field in response reports versioned ID — log it. `TypeSafeClient(model="jev-1.13.0")`.
- Billing is input-only, so fan-out and extra Choice options cost almost nothing.

## Honest scorecard (as stated)
- TypeSafe four-workflow evaluation: Jev **67.8%**, level with GPT-5.6 Terra (**67.9%**), behind Sol (**74.1%**) and Opus 5 (**73.1%**), at roughly **1/200th cost and 1/50th latency**. Claude Sonnet 5 also **67.8%** at **293x** cost per case and **195x** latency.
- Four cautions: (1) not accuracy — no ground truth; consensus labels = average of GPT-6 Astra and Claude Fable 5.1 at high thinking, scored against those (TypeSafe says this biases toward OpenAI and Anthropic); (2) self-run, no independent reproduction; (3) "cannot hallucinate" = cannot return an invalid value, can return the wrong valid one; the 0% structured-error figure is asserted not measured ("Schema matching is guaranteed, thus we can confidently add 0% into the plots"); the 45.5% comparison is a single outlier (Haiku 4.5), most models 0.58%-13.2%; (4) price may move — TypeSafe cannot prove it is not subsidised, expects it to fall.

## When to use / not (author's view)
- Yes: routing/triage, moderation, relevance filtering before an expensive context window, scoring/guardrailing LLM output, tagging at previously uneconomic volumes, sub-second decisions in a request handler.
- No: generation, arithmetic/counting/date math, decisions needing a written rationale for an auditor, one-off complex reasoning, genuinely open answer spaces.
- FAQ: should I replace my LLM? No; cascade (Jev classifies/routes, code handles what it can, frontier model takes the hard minority). Cost per case ~$0.0004 on TypeSafe's benchmark.

## Reader comments (third-party)
- Pushpendra Agrawal (commenter, founder): the cascade is the real story; requests that skip the model entirely (e.g. order-status lookup straight to code) are the bigger saving than a cheaper model.
- Kiell Tampubolon (security engineer): instrument the cascade harder — log model version, probabilities and confidence per decision; a silent model bump can move every decision; treat pinning like thresholds; user-supplied state is adversarial input.

## Flags / disagreements
- **Context limit:** dev.to 64k (state+questions) / 32k (state + longest question) vs OpenRouter 32,000 total ([[openrouter-jev-guide]]).
- **Access:** waitlisted early access (dev.to) vs "no waitlist" via OpenRouter.
- **jev-trader 81 ms:** the awesome directory says the stated latency was measured with the mock model, not Jev ([[awesome-typesafe-jev]]).
- "ten" in "800,000 answered under half a second instead of ten" is unitless in the source.
- Typesafe-computer-use is not in the awesome directory list.

## Related
[[community-guide-marktechpost]] · [[awesome-typesafe-jev]] · [[openrouter-jev-guide]] · [[benchmarks-and-comparisons]] · [[speculative-fan-out]] · [[confidence-gated-routing]] · [[composite-scoring]] · [[intent-routing]] · [[jev-1-13-jaggedness]] · [[models-and-versions]] · topics: [[topic-routing]] [[topic-cost-latency]] [[topic-model-selection]]
