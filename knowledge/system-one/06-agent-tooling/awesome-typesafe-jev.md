---
title: Awesome TypeSafe Jev (Community Directory)
kind: reference
source: Awesome Jev / TypeSafe (AbdelStark/awesome-typesafe-jev README, last updated 2026-09-23)
source_url: https://github.com/AbdelStark/awesome-typesafe-jev ; https://abdelstark.github.io/awesome-typesafe-jev/
tags: [agent-tooling, alternatives, evaluation]
topics: [topic-agent-integration, topic-calibration, topic-model-selection]
---
# Awesome TypeSafe Jev (Community Directory)
> THIRD-PARTY, independent, not affiliated with TypeSafe. A curated catalogue of ~246 community SDKs, agent tools, apps, games, evaluations and open alternatives around Jev, plus five "before you trust a decision" independent findings. Reach for it to find an existing client/tool or to see what independent tests measured. All numbers below are author-reported by the listed projects, as the directory relays them; many are single-run, small-sample, or private-data.

**Provenance / trust label.** Everything here is third-party. The directory itself says: inclusion is not a TypeSafe endorsement; entries are labelled by section; links and descriptions change; "Last updated: 2026-09-23" (header). It states results "belong to the cited task, dataset, and model run" and are "not a leaderboard or a guarantee". Counts per section (my tally): client libraries/integrations 42, agent+developer tooling 78, browser agents 12, applications 30, games/robotics 17, evaluations/independent research 53, showcases 14. Also ships a JSON directory (`resources.json`), a skill for coding agents (`skills/awesome-jev/SKILL.md`), a live site with a policy-threshold toy and a listing builder (runs in-browser, no model call).

## 1. What the directory itself says about using Jev (design rules, third-party)
**Code vs Jev vs text LLM** (README "Choose the right tool"; described as a practical design rule from the TypeSafe introduction, not a performance claim):

| Step needs | Use | Example |
|---|---|---|
| Explicit rule on known fields | Code | account flag, routing threshold |
| Judge messy context, bounded answer | Jev | choose billing/technical/other with probabilities |
| Prose / open-ended | Text LLM | draft reply after routing |

Code validates the answer and owns the action. "Measure Jev's error and abstention rates on your own cases before automating a consequential step."

**Question shapes:** Noul = yes/no -> number 0..1 (probability of yes). Choice = named options -> selected option + probability per option + confidence. Score = ordered rubric -> position on rubric + probabilities over levels + confidence. One state can answer several focused questions in the same request; ask independent questions together; set thresholds, fallbacks, side effects in application code.
**Question-shaping tips:** keep state short; describe options so they do not overlap; include a no-match option when the task allows; choose thresholds/actions only after measuring labelled cases. Example designer input: state `The PDF upload fails with a 500 error. I need it before today's deadline.`; Choice `technical / support / other`; Noul "explicitly mention a deadline?"; Score levels `Cosmetic; Workaround available; Blocks the task`.

**Documented example (saved `jev-1.13.0` response from TypeSafe quickstart, not a live call):** state = Stripe-connection support message ("trying to connect my Stripe account for 3 days ... losing sales. Please help ASAP."). Choice -> `technical` at 0.85 selected probability; Score -> `1` on a 0-2 frustration rubric (label "Frustrated but civil"); Noul urgency -> `1.0`.

**Threshold toy:** selected team `technical`, probability 0.85. At threshold 0.90 -> goes to review; at 0.80 -> routes to technical. Model answer unchanged; only policy changed. Directory says these thresholds are teaching examples, not measured operating points or safety guarantees. First-decision examples use a `0.9` rule, explicitly "illustrative ... not a measured or recommended operating point".

**First-decision snippet (JS, Node 20+, `npm install @typesafe-ai/sdk`; Python 3.10+, `uv add typesafe-sdk`; env `TYPESAFE_API_KEY`):** state `{ticket: "I was charged twice. Please refund the extra payment."}`; questions `team` = Choice("Which team should handle this ticket?", billing "Payments and refunds" / technical "Bugs and integrations" / other "None of the above") and `refund` = Noul("Does the customer explicitly request a refund?"). Code: `team = answers.team.choice; p = answers.team.probabilities[team]; action = route if team != other and p >= 0.9 else review`. Python shape: `client.system_one(state=..., questions={...})`, read `result.choices["team"].choice`, `result.nouls["refund"].noul`.

## 2. Ways to call Jev (README "Choose where to call Jev")
| Route | Way in | Check before use |
|---|---|---|
| TypeSafe direct | official JS/Python SDK + TypeSafe key | sends state to TypeSafe; documented `systemOne` contract |
| Cloudflare Workers AI | model `typesafe/jev`, Workers AI binding or Cloudflare API | Cloudflare request shape/credentials; page labels Jev third-party model |
| Netlify AI Gateway | official TypeSafe JS SDK from Netlify Function/Edge Function; gateway supplies env config | Netlify plan + key-override rules; server-side only, not browser key |
| Vercel AI Gateway | AI SDK experimental `evaluate`, model `typesafe-ai/jev` | Boolean question maps to Noul; interface differs from `systemOne` |
| OpenRouter | decisions API, `typesafe/jev-1.13` or latest-model route | OpenRouter key + decisions request shape; "do not send these questions to a chat-completions API" |
Directory: these are documented access paths, not equivalent SDKs, no claims on price/latency/reliability. (See [[openrouter-jev-guide]].)

## 3. "Before you trust a decision" — five independent findings (README table)
| Decision | What was measured (third-party, task/dataset/run specific) | Test before shipping |
|---|---|---|
| Answer or abstain? | KoBBQ audit (jev-calibration-audit): Jev chose "unknown" for **95% of 300 ambiguous items** when that option existed. With the gold answer removed from options, accuracy on those items necessarily 0%; **79%** of answers picked the dataset's stereotype | explicit no-match/review option; measure wrong forced answers and needless abstentions on own ambiguous cases |
| Route to fallback? | Janus: 500 items each from Banking77 and Web of Science. Tuned Jev->DeepSeek cascade beat either model alone on Banking77; on Web of Science matched Jev alone (**47%**) at **higher cost** | label representative cases, price both legs, pick threshold on held-out split, confirm fallback fixes errors where Jev is uncertain |
| Certify a routing threshold? | jev-certify, CLINC150: 5% bound on silently misrouted incoming queries held on 400 in-scope examples: **84.75% auto-routed, 2.25% loss per incoming query**. Separate scope gate **missed 5% target by 3.6x** when out-of-scope prevalence rose | calibrate on deployment-like traffic; monitor mix; distinguish loss per incoming query from error among routed; bound does not cover shifted population |
| Sort by probability? | jev-orderby-bench: passed 6 ranking gates on 360 topic-membership rows, failed 4 of 6 on 306 human-graded shopping pairs. 53 rows tied at 0.99; batching 40 rows turned a passing gate into a failure | measure pairwise order, ties at cutoff, exact request shape; good classifier is not automatically a good sort key |
| Approve an agent action? | 111-case action-gate study (jev-enterprise-decision-fabric): Jev matched **100** case labels, Claude **102**; each had **one unsafe allow**. Contract/policy mapping was the largest single source of wrong decisions for both | test answer-to-action mapping too; escalate consequential tool families with deterministic policy even when answer looks confident |

**JevBench method (README):** publishes scoring code, frozen tasks, adapters, result artifacts. Composite = accuracy + calibration + speed + cost; some latency/hosting costs are estimates; a held-out set is still sent to evaluated services. Read per-task outcomes before treating a rank as evidence. Results file `RESULTS-v1.2.md`. Also points to TypeSafe's own evals at evals.typesafe.ai.

## 4. Official resources listed (first-party links the directory points to)
Product site typesafe.ai; docs.typesafe.ai; HTTP API ref; interactive demos (incl. smart-home); workflow evals (evals.typesafe.ai); **JS SDK** `typesafe-ai/typesafe-sdk-js` (inferred answer types); **Python SDK** `typesafe-ai/typesafe-sdk-python` (sync+async); **System One Adapter** `typesafe-ai/system-one-adapter-python` (same typed interface over OpenAI, Anthropic, OpenAI-compatible LLM APIs); **TypeSafe Agent Skills** `typesafe-ai/skills` (Claude Code, Codex, other skill-compatible agents); console.typesafe.ai (keys + live request inspection); concept pages (primitives, confidence, patterns, use-case-map, cookbooks, agent-skill); blog posts (Introducing System One Models & Jev; Manifesto; The Bitterest Lesson; "AI: too good to be true, too bad to be useful"); Discord (discord.gg/typesafe, with Show and Tell), X @typesafeai, LinkedIn. See [[typesafe-agent-skill]], [[sdk-overview]], [[http-api-reference]].

## 5. Community catalogue
Each line: name — what it does — stated numbers/caveats. Entries marked (unaffiliated) say so. Data path: unless noted, text sent to TypeSafe (or configured gateway).

### 5a. Client libraries and integrations (42)
- **Advocaat** — small TypeScript client, tagged helpers for typed chances/choices/scores.
- **AnyDecisionModel** — Swift 6.2 package; typed sessions, enum choices, ordered scores; backend = TypeSafe Jev API or local MLX LLM on Apple silicon (local reads answer-token probabilities, no text generation); calibration caller-configured, not established per task.
- **Ax TypeSafe integration** — Ax TS provider: required Boolean/class signatures + native Jev client for Noul/Choice/Score with probabilities+criteria; free-text and numeric signature fields are not native Jev outputs; use explicit native interface for scoring, not a bounded number as a Score rubric.
- **DuckDB Jev** — native DuckDB extension: predicates, Choice, Score, streaming batched judgments over SQL rows; per-query budgets, caching, request telemetry. Published live throughput uses a repeated synthetic ticket corpus, does not measure accuracy; binaries must match DuckDB version+platform.
- **Hunch** (Ruby gem) — `if Hunch.likely?("fraudulent", given: order)` branches on a typed answer; `pick` (Choice), `rate` (Score), graded predicates `possibly?` to `almost_certainly?`; TS port `hunch-ts`; unaffiliated.
- **Hunch for Python** — `pip install hunch-jev`; maps Choice/Score/Noul to functions over strings, lists, DataFrames; deduplicates per-row requests; thresholds in caller code; optional LLM escalation sends uncertain rows to that provider; TS port `hunch-js`.
- **Jev for Apple Foundation Models** — Swift 6 bridge translating `@Generable` Boolean/enum/bounded score fields into one Jev question set; mock-transport tests + 2 demos; needs iOS/macOS/visionOS 27; key must stay on backend/trusted machine.
- **jev-acp** — standalone ACP agent for Choice/Score/Noul with guided input, templates, probability displays; needs TypeSafe key.
- **Jev-Switch** — Rust gateway + React console + Windows Tauri app; serves Jev-shaped `/v1/systemone`, routes via editable graph of upstreams with failover; v0.1.0 adapters only Vercel AI Gateway and Laya (not TypeSafe API); README in Chinese.
- **jev.zig** — Zig client, compile-time typed answers, retries with per-attempt timeouts, diagnostics; questions fixed at compile time.
- **Jevelry** — early TS CLI/library/skill for reusable question templates mapping answers to act/mark/fallback; local decision/outcome log (state hash by default, opt-in full state); configured `run` commands may execute locally without per-action confirmation when confidence high.
- **jevframe** — early Python; async Noul/Choice/Score/multi-question for pandas and eager Polars; full probability distributions; bounded row concurrency; opt-in memory cache; each uncached row sent to TypeSafe; LazyFrame out of scope in v0.
- **jevql** — psql-shaped CLI + Go/TS/Python SDKs: `WHERE jev(alias,'condition')`, `jev_prob`, `jev_choice`, `jev_score` on vanilla Postgres (no extension): runs plain SQL server-side, judges surviving rows with Jev in batches (cached in local SQLite), filter/sort/group applied client-side; every surviving row is sent and judged — put cheap predicates in SQL first.
- **jevsearch** — shadcn/ui registry block for Cmd-K search: local keyword pass first, top 20 to Jev in one request (Noul per page, Choice for best answer, Noul for "any page answers"); code reorders/drops; only reranks keyword hits (no embeddings/vector DB); keyword order stands if TypeSafe slow/down.
- **json-render** (Vercel Labs) — generative-UI framework; experimental Jev composer picks components/layout from app-supplied candidates via Vercel AI Gateway; Jev API unreleased, needs source build.
- **Laya for Node.js** — MIT TS client running the independent Jev-compatible Laya model locally via ONNX Runtime; batches a question set; first use downloads about **1.7 GB** weights; reference-output test runs only with bundle present.
- **LlamaIndex Jev** — unofficial reranker + query-engine selector on official Python SDK; score mode is a 0-3 rubric, not cosine similarity.
- **Milvus Model** — Python reranker adapter: query + candidates sent as batched Noul questions, scores sorted, original indices preserved; prompt currently claim/evidence-specific; in source but not yet in a verified package release.
- **mysql-ailike** — native MySQL plugin: `AILIKE` predicate for NL row filters; 3-arg `ailike(left,right,prompt)` for semantic JOIN; preview; each uncached evaluation is an API request.
- **NeuroLink** (Juspay) — TS SDK exposing `decide` as third inference type next to `generate`/`stream`; backend TypeSafe Jev or open-weights Laya, declared via `inferenceKinds`; used internally for model routing, context compaction, MCP tool selection, RAG planning; fail-open wrapper returns `null` on any failure, so no key = old behaviour; unaffiliated.
- **OCaml SDK** (verdict) — unofficial eio client.
- **pg-jev** — PostgreSQL extension: Jev WHERE predicates, probabilities, Choice, Score; batches rows, per-session cache, optional spend caps; every judged row goes to TypeSafe; needs `plpython3u` + superuser (many managed hosts lack it).
- **pi-typesafe** — Pi extension giving one consented key-managed TypeSafe client with batched `typesafe_evaluate` tool; billable, opt-in per user.
- **RubyLLM TypeSafe** — provider for RubyLLM 2, offline model metadata, typed responses.
- **s1-rs** — Rust derive layer: Choice/Score/Noul, typed question sets, confidence gates, network-free testing.
- **scala-jev-sdk** — Scala 3 client; answers retrieved with the question value itself; works on any sttp backend (Future/blocking/cats-effect/ZIO); retries honour `Retry-After`; local validation rejects malformed question sets pre-request; returns `Either`; non-Future/Identity effects must supply a one-line sleeper; Scala 2.13 unsupported; unaffiliated.
- **SemanticPolicy** — alpha .NET 10 (Apache-2.0): rules as Boolean/Choice/Score Jev answers; thresholds measured on labelled examples via evals CLI run from a clone; checks before model call, before tool run, after tool returns in Microsoft Agent Framework; text goes to Jev via OpenRouter or TypeSafe endpoint, not logged; "a rule is a signal, not a security boundary".
- **Swift SDK** (marandaneto) — unofficial experimental, async/await, SwiftPM.
- **TypeSafe AI for Rust** (Twister915) — async+blocking transports, typed responses, observable retries, inspectable errors.
- **TypeSafe AI Swift SDK** (alterhq) — dependency-free Swift 6, strict concurrency, configurable retries, network-free tests; production Apple apps should proxy via backend.
- **TypeSafe SDK for Go** (SergeAx) — Go 1.23; options-over-env config; retries honour `Retry-After`; `errors.Is` error tree; `log/slog` redacts credential headers but logs request bodies at debug; unmodelled answer types dropped with warning; no tagged release (pseudo-version).
- **TypeSafe SDK for Java** (Premo-Cloud) — Java 17, lambda builders for nested criteria, retries matching official SDKs, status-specific exceptions, Spring Boot starter; depends only on Jackson.
- **TypeSafe SDK for Kotlin** (ufec) — port of official JS SDK; retry policy matching upstream; HTTP/SOCKS5 proxy; runtime check that each answer matches its question; Android+JVM only; JitPack not Maven Central.
- **TypeSafe SDK for PHP** (Fox-Islam) — PHP 8.3; one-call switch between TypeSafe and OpenRouter decisions endpoint; retries, per-call overrides, any PSR-18 transport, Laravel provider; synchronous; model listing only on TypeSafe.
- **typesafe-ai-rails** — Rails integration on typesafe-sdk; persisted usage/cost telemetry; opt-in confidence policies for Choice/Score.
- **typesafe-rs** (AbdelStark) — latency-focused Rust transport, behavioural parity with official clients.
- **typesafe-sdk** (joshmn) — Ruby 3.1+, retries, model listing, thread-safe pooled HTTP; no async.
- **typesafe_sdk** (nshkrdotcom) — Elixir; typed structs, configurable retries, upstream parity.
- **TypeSafeAI.Net** — .NET; question sets, HttpClientFactory/DI, Microsoft.Extensions.AI guardrail/routing/tool/evaluator adapters.
- **Vercel AI Gateway** (vercel.com/ai-gateway/models/jev) — third-party hosted gateway entry for Jev via AI SDK.
- **Vercel AI SDK for Python** — public-beta; experimental `evaluate` with typed Choice/Score/Boolean through AI Gateway using `typesafe-ai/jev`; still experimental.
- **vgi-typesafe** (Query-farm) — DuckDB integration via community VGI extension: Choice/Noul/Score as SQL table functions for `LATERAL` joins; typed columns with confidence, probabilities, per-row token usage; `is_true()` scalar for WHERE; several questions share one request per row; repeated values asked once per batch; every other non-null row = billable request sending content to TypeSafe.

### 5b. Agent and developer tooling (78)
- **Augustus** — `augustus`/`augustus-train` agent skills: placing and building app-specific decision models (primitive, base-model, method selection, data, fitting, export/reload, bounded improvement, offline eval); TypeSafe Jev is default hosted exemplar; rules-only/no-training outcomes valid.
- **Beacon** (Asymptote Labs) — agent memory; explicit `beacon memory evaluations run`: Jev judges bounded redacted trace projections for reusable lessons; human reviews before adding to memory/skill; hooks and dry runs do not call Jev; capture can retain sensitive text locally.
- **Bicameral** — Pi coding harness: LLM writes, Jev supplies typed reflexes (policy, loop detection, review); not a sandbox.
- **Building with TypeSafe Jev** (aaddrick) — unofficial agent skill (Claude Code, Codex, Antigravity CLI) holding API shapes, cookbook thresholds, community failure modes, 150+ community projects with code sketches; Markdown only; **snapshot dated 2026-09-25** (see Contradictions); says live docs win on conflict.
- **Canny** — Claude Code/Codex hooks: append-only ledger of edits/checks, flags "done" claim without passing check after last edit; optional Noul for advisory rule checks; default gate allows repeated stop after warning; author has not measured project-wide quality gains; Jev gets clipped diffs, rules, final messages.
- **Codex Jev Router** (suenot) — Codex subagent router: Jev Choice/Noul on short task summary, code thresholds, falls back to "Sol" on failure; installer edits local Codex config with backup; not enforced at tool boundary.
- **DGP** — experimental decision-based agent protocol: Jev adapter, immutable evidence frames, typed assessments, application-guarded commits; reference app simulates effects; live mode opt-in.
- **Distill** — coding-agent harness using Jev to pick model+effort, route utility tasks, judge context to retain; code constrains choices; Jev does not decide tool permissions; may send request + recent steps.
- **Every** — semantic code-search CLI: yes/no question for every function, ranks probabilities.
- **evoke** — Rust CLI + TS SDK: Jev selects installed reflex + bounded args, code gates as run/confirm/ask/abstain; reflexes fetched from Git run as your user, no sandbox.
- **fast-jev-compaction** — Claude Code function-hook plugin/npm lib: Jev decides which older tool calls/results to keep/truncate/remove; user/assistant messages untouched; relevance probabilities do not guarantee safe deletion.
- **Foreman** — experimental Codex/OpenCode supervisor sending bounded job/output/diff to Jev for progress checks; workers run locally unisolated; accuracy unproven.
- **fx** (Vercel Labs) — experimental Zig coding agent; optional Jev permission reviewer: `review_model` = `typesafeai/jev` sends policy+context+pending action, Jev's Choice mapped to permission decision; probabilities/confidence not threshold gates. (Model id spelled `typesafeai/jev` here vs `typesafe-ai/jev` elsewhere — see Contradictions.)
- **Hermes Jev Skills** — Python toolkit + 9 agent skills (Hermes, Claude Code, Codex): route models, filter retrieved passages, select skills, choose bounded computer/browser actions; installer dry run; routing shadow mode; redacted prompts sent when enabled.
- **Hermes JIT Context OS** — context runtime with optional Jev Noul ranker over candidate facts via OpenRouter; caches scores; labels token-overlap fallback; ten-task live-call record on small SWE-bench-style inline fixtures, not a SWE-bench score.
- **Hippo Memory** — local agent memory; opt-in Jev reranker batches Noul over **top 40** recalled memories, falls back to local cross-encoder on errors; author's study: better ranking on two corpora but **no demonstrated answer-quality gain** over the cross-encoder.
- **hush** — GitHub Action issue triage: label, spam, needs-more-info, possible-duplicate in one call; each applied only above maintainer threshold; nothing below.
- **is-malicious** — CLI scanning source/config/build/CI files with Jev; reports suspicious behaviour with file+line; file contents sent.
- **jeff** (saembit) — Go CLI: noul/choice/score/eval commands mapping threshold to exit code; `rank` sends one Score per item per weighted YAML dimension in one request, composite computed in code (weighted sum is the tool's arithmetic, not Jev feature).
- **Jev Clean** — experimental CSV cleaning: repair candidates computed locally, Jev gates changes; audit+rollback records; limit **10,000 rows, 30 columns**.
- **Jev Codex Router** (0xNatoshi) — asks Jev for model tier + thinking depth on each model call incl. tool continuations, relays native Responses request; needs local routing stack; savings backtest simulates an older policy, not current quota saved.
- **Jev Cookbook** (nexibeo) — **15** runnable OpenRouter recipes (support triage, data cleanup, search, browser actions, Gmail labelling), small labelled samples, saved live results; thresholds in code; does not establish production accuracy.
- **Jev MCP** (blakestone-x) — Python MCP server: classify, score, check, match, screen.
- **Jev MCP by jkudish** — Node MCP server, **ten** bounded tools (check claims vs evidence, screen content, choose candidates, rerank, extraction, patch review); TypeSafe or configured gateways; does not run tests or establish factual truth. See [[jev-mcp-server]].
- **Jev Review** (devagrawal09) — staged code-review workflow + local dashboard following structured signals through focused Jev calls (dev.to: Noul risk matrix, then Choice/Score file profiles, evidence selection, severity, conditional routing; 48 stars).
- **jev-align (Sutro)** — experimental active-learning CLI over CSV/Parquet/JSONL: Jev evaluates, humans label uncertain + randomly audited examples, GEPA proposes improved definitions; labels and acceptance under human control.
- **Jev-assisted compaction** (ljedrz/nachalnik, kamchatka agent) — simple example of content-aware compaction.
- **Jev-assisted shell** (kamchatka) — built with `--assisted-shell`, run with `--advise`: classifies shell commands, colour-coded safety rating per command.
- **jev-axi** — agent-ergonomic CLI (AXI conventions): blocks risky tool calls, screens fetched content for prompt injection, triages build logs, flags risky diffs, filters/ranks items; own benchmark: agents read fewer files but **cost the same** — for judgments, not a substitute for reading code.
- **jev-belay** — Claude Code Stop hook: checks transcript for evidence before trusting "done"; one **four-question** Jev call only when files changed with no passing check since; fails open on every error.
- **jev-cli** (`npm install -g jevctl`) — pipeable exit-code-gated: `verify`, `screen`, `classify`, `extract`, `match`, `route`, `find`, `rerank` (up to **250** candidates), `compact` (drops stale tool calls verbatim), `batch` over JSONL with concurrency pool; `--fail-on` policy in code; works over TypeSafe, OpenRouter, Cloudflare Workers AI; Claude Code plugin with compaction hook.
- **jev-commit** — pre-commit hook: one Jev call judges whether message matches staged diff, flags debug leftovers/unmentioned work; **blocks only on detected credential**.
- **jev-engineering** — decision layer for coding agents: deterministic rules first, then one Jev request; Claude Code PreToolUse hook, MCP server, loopback service, team policy (personal overrides may tighten, never loosen). Published adversarial results over **300 calls**: blunt injections moved **0 of 30** dangerous commands but caused **10% false denials** on safe ones; authority framing moved **3 of 30**.
- **jev-graphify** — Python CLI naming/classifying graphify code-graph communities via Jev picking from candidate names; routes developer question to community+symbol; sends symbol names, paths, short comments (not source bodies); tested on one codebase.
- **jev-lint** (MIT) — fuzzy linter flagging team-rule violations as Claude Code/Codex edit; local thresholds; API errors fail open.
- **jev-logtriage** — Noul/Score/Choice over collapsed Loki log batches -> suppress/watch/review/notify/page in code; remediations stay candidates.
- **jev-mobile** — experimental Android agent: bounded per-step choices over prevalidated UI actions; confidence gates, pagination, escalation, optional LLM planning; PoC mainly on Android Settings.
- **jev-pref** — CLI + GitHub Action: project semantic preferences -> Noul/Choice over code changes -> advisory/blocking in code; tuning on labelled diffs.
- **jev-pruner** — Claude Code plugin/opt-in Codex wrapper trimming long Bash output; preserves diagnostics, archives full output locally; retention rules heuristic.
- **jev-router** (gargpratyush) — Claude Code/Codex wrappers choosing model tier per fresh user turn; documented compatibility testing on Windows with specific CLI versions.
- **jev-semgrep** (`@uehaj/semgrep`) — batches Noul per line for multilingual meaning-grep; AND/OR/NOT in code; every searched line sent; repeated searches pay again; command name `semgrep` collides with static-analysis tool.
- **jev-skill-router** — Claude Code UserPromptSubmit hook porting the skill-suggestion cookbook; starts in log-only shadow mode; shipped thresholds not yet calibrated on its own data. See [[cb-skill-suggestion]].
- **jev-use** — Claude Code/Codex/pi plugin: `jev_judge` batches typed noul/choice/score about one state in one call; `jev_gate` opt-in PreToolUse gate that can only deny or ask; typed escalation contract (writing, open_ended, oversized, unsure, unreachable) returns other steps to the LLM; unreachable backend escalates (never waves through); TypeSafe/OpenRouter/Vercel backends; publishes live benchmarks including runs where Jev did worse.
- **jev.nvim** — Neovim: Treesitter splits buffer into functions, Jev scores each vs plain-language question, quickfix ranking by probability.
- **jevcal** — CLI fitting a per-question confidence threshold to a target accuracy on your labelled data, verifies on held-out split, estimates fallback traffic, re-checks locked thresholds in CI; publishes no Jev results; **thresholds fitted on fewer than about 100 labelled rows should not be trusted**.
- **JevDroid** — experimental Python Android framework: Jev picks actions from accessibility trees, executes via ADB/UIAutomator2; explicit action permissions and per-run budgets.
- **jevgrep (allebee)** — streaming grep-by-meaning (`jevgrep-cli`, works with `tail -f`): one Noul per line, prints above code-set threshold; hand-labelled **195-line** synthetic-log benchmark vs Claude; `--explain` sends lines to Anthropic via OpenRouter.
- **Jeview** — experimental unofficial loopback proxy/live map of Jev calls; stores requests, responses and API key (plaintext) in local SQLite; keep off public addresses.
- **JevLoop (Python)** — experimental agent runtime: Jev selects typed actions/targets, low-confidence -> LLM arbitration; guarded kernel executes file/shell ops in Docker sandboxes.
- **Jevonian** — experimental local proxy for coding agents (OpenAI/Anthropic/Responses APIs); `jevonian/auto` route asks Jev for model+thinking level after deterministic compatibility/quota filters; explicit routes skip Jev; ledger records serving model, route reason, tokens, estimated cost; optional `fullPrompt` sends whole conversation; low confidence flagged not rerouted; costs/cache savings estimates.
- **jevr** — Rust semantic code/doc search: local BM25 recalls files, Noul judges bounded windows, Choice reranks survivors into `path:line`; up to **24 KB** source per request.
- **JevRouter** (BillionsBobby) — routes models/skills/MCP tools/CLIs/plugins via typed choices; code enforces availability, permissions, risk, confirmation; offline demo mode; append-only decision receipts.
- **jgrep** — semantic grep (`npm install -g jevgrep`): splits files/git diff hunks into **5-60 line** chunks, packs several per request with Noul per chunk, prints `file:line` above threshold with grep-style exit codes; lint a diff in CI with English rules; chunks judged in isolation so cross-file questions do not match.
- **langchain-skill-router** — per-turn skill routing for LangChain deepagents; judge ranks/verifies candidates before middleware loads one skill or shortlist; evaluation = one generated testbed + one agent model.
- **Mobile Jev** (droidrun) — local Android agent+studio on Mobilerun: Jev selects operations/targets, code rejects stale actions; needs device + Mobilerun and TypeSafe keys; CI does not control a live phone.
- **Oko** — local MCP code search for Codex/Claude Code/OpenCode: reranks keyword shortlist with Noul, returns whole-function excerpts; sends question + up to **90 code chunks** per search; keyword-only mode needs no key.
- **oxlint-plugin-jev** — experimental Oxlint plugin: Noul on functions/calls/JSX/files, reports above cutoff; API failures skip checks by default so set `ci: "fail"` in CI; keep out of editor linting (edits trigger paid calls).
- **patdown** — CLI/GitHub Action/agent hooks judging files/changes vs Markdown rules; provider-swappable backend; no request budget or cache yet; needs human review for consequential gates.
- **perch** — code scanner: parses methods + call graph, asks Jev typed questions per method, ranks defects/security findings; `--since` scopes CI; reads every method in scope.
- **pi-heed** — Pi extension: turns constraints stated in conversation (English, Chinese) into scoped replayable policy (deny/allow/exceptions/once-per-run/ask-first/tests-before-push), checks side-effecting tool calls before run; Jev only classifies how each message changes policy; ships replayable benchmark + experiment log on Jev calibration/question design; shadow mode default, fails open, benchmark scripted not real sessions.
- **pi-jev** (y0usaf) — Pi extension: shadow-mode tool-call gate, output judge, general `jev_ask` tool.
- **pi-jev-compaction** — hides older tool results after context pressure, keeps originals, `jev_read` tool recovers an output; protects recent results; unchanged on API failure; tests do not establish live relevance quality or savings.
- **pi-jev-context** — shortens long tool output before it enters context (no cached prefix invalidated): Jev gives each block a probability the request needs it; only confidently-unneeded blocks hidden; code guarantees failure lines, request terms, top-ranked blocks survive; `context_recall` returns original; ships experiment reports + findings log with pre-registered synthetic sets and weakly labelled replays; includes a **negative result**: Jev-judged pruning of old context dropped information needed later, so that part stays shadow-only; real-session replays from one user.
- **pi-verdict** — Pi permission gate: deterministic rules first (danger floor, user allow/deny, protected-path prompts), then gray-zone to fail-closed enforcing classifier (`classifierModel` may point at Jev: allow/ask/deny); Jev backend experimental, via OpenRouter or TypeSafe; ignores protected-path hints; **can be swayed by adversarial transcript content**.
- **pi-warden** — Pi guardrails on pi-typesafe: verdict returned as held tool result/short steer; checks writes vs project rules file; grades own holds against user's next message; action guard calibrated on one user's **17k calls**, other guards on synthetic cases only.
- **pytest-jev** — `jev.expect` batches Noul claims about one text; default fails uncertain claims (holds needs >= **0.8**, lacks <= **0.2**); Choice checks selected option, Score checks probability mass across ordered levels; caches in `.pytest_cache`; skips without key.
- **Second Thought** — Python SDK/CLI/dashboard capturing typed decisions from Laya/Jev/custom classifier, measures calibration, routes uncertain to human review; dataset export excludes Jev decisions in code; reported Laya result from a **24-ticket** example run.
- **Skillbox** — self-hosted skill library; opt-in Jev recommendations over task text + authorized skill descriptions; failed/oversized/rate-limited -> deterministic search fallback.
- **SkillRanker** — Rust CLI: Jev Choice/Noul shortlist+rerank of skills, real "none" option, local replay; license has OpenAI/Anthropic rider (not plain MIT).
- **slop-grader** — grades markdown/text vs rulesets (AI slop, grammar, docs quality) via Jev scores/flags; guides agent to auto-fix.
- **Sniff Test** — prose linter, local rules + opt-in Noul on paragraphs; CLI/pre-commit/GitHub Action; author comparison uses small seeded corpus, some rules tuned on same seeds.
- **Supercov** — Jev scores each source file so the coding agent knows what to fix first.
- **Switchboard** — local Claude Code/Codex wrapper: Jev assesses new conversation's task, local confidence policy picks model+effort, **pins route through follow-ups/tool calls/resume to avoid prompt-cache disruption**; raw history stored only if enabled.
- **toolgate** — MIT TS tool-call firewall (Claude Code PreToolUse hook + MCP stdio proxy): static rules, then **seven Noul risk questions** per action -> allow/ask/deny by thresholds; action ledger, key-aware redaction, JSONL audit log. One author's **1,369-decision window on 0.9.1**: blind second labelling of **150 sampled allows** found **no permissive misses**; **21%** of decisions required an ask, mostly one axis; v0.11.0 addresses that axis, not re-measured. Heuristic redaction + model judgments are defense in depth, not a sandbox.
- **TypeSafe MCP** (itsmostafa) — Go CLI + single-binary MCP server; setup for Claude Desktop/Code/Codex.
- **Vercel Eve** — agent framework; `auto` model router defaults to Jev via Vercel AI Gateway; `evaluate` helper asks Choice/Score/Boolean inside tools; spec experimental.
- **VexJoy Agent** — cross-harness toolkit; `/d` path uses up to **two** Jev evaluations to select agents/skills/pipeline then checks intent before dispatch; deterministic force-route rules bypass Jev; installer changes local config/hooks.
- **wakegate** — experimental gate for long-running agents (Workers/Durable Objects/Node): before resuming a sleeping agent's LLM, one Choice (wake / not yet / unrelated) vs sleep note; skip only when wake probability **below 0.2**; always wakes on user messages, bare timers, skip limit, errors, timeouts; eval = **21** hand-written scenarios, not a benchmark.

### 5c. Browser agents (12)
- **Cline Jev Browser** — Cline plugin delegating bounded Playwright steps to Jev via Vercel AI Gateway using structured DOM observations; separate text model fills form values; review instruction is guidance, not enforced boundary.
- **fastbrowse** — pre-alpha: Jev picks actions from observed controls, LLM plans/reads, code requires page quotes for answer claims; classifier stops before consequential actions unless `--authorize` (not a guarantee); default browser = Browser Use Cloud; author's comparisons not independent.
- **Jev Browser** (jkudish) — MIT Playwright navigator (MCP/CLI/library): Jev chooses DOM actions, judges goal/stuck from page excerpts; TypeSafe/OpenRouter/Cloudflare/Vercel; code bounds loop, returns trace+final page+screenshot; no per-action approval; iframe, shadow-DOM, file-input unsupported.
- **Jev Browser Use** — Codex Computer Use skill: accessibility snapshot to Jev to choose among host-allowed clicks/scrolls; Codex types and verifies; validated only in Codex; author's speedup not independent.
- **Jev for Chrome** — unofficial MV3 port of Jev Ultrafast; separate text model writes typed values; Step/Stop manual oversight, Run executes without per-action approval; **17-task** headless-Chromium suite with traces.
- **Jev Social** — local Instagram/TikTok/LinkedIn research app: confidence-gated choices over bounded socai CLI operations; capture read-only except optional TikTok media download; no per-step approval.
- **Jev Ultrafast** (browser-use) — dynamic indexed action space, batched operation+target decisions, traces, measured Google Flights demo (dev.to: Zurich->London in **7.1 s, $0.0039**, 641 stars; see community-guide-devto).
- **jev-agent-browser** — delegated browser execution: Jev picks bounded typed actions, agent-browser performs, ambiguous/blocked flows escalate to parent agent.
- **jev-skip** — browser extension: reads YouTube caption track, paints per-segment sponsor probability on seek bar before intro ends, no crowd DB; reports catching **77%** of SponsorBlock sponsor seconds across **23 videos** at **$0.0008 per video**.
- **PlotVeil** — Chrome MV3: covers a YouTube comment while one Noul decides whether it reveals plot/ending; app code owns **0.5 / 0.7 / 0.85** threshold; failed/quota-rejected check leaves comment covered; requests via author's Cloudflare Worker; committed eval = **10-sample** hand-written regression set (EN/ZH/JA + prompt injection), not production accuracy.
- **unclutter** — Chrome/Firefox extension classifying bounded page-element snippets, stores reusable local hiding rules per page template; paid analysis manual by default; API key in unencrypted local extension storage.
- **voice-browser** — local voice-controlled Playwright browser: Jev picks typed intent+target from speech and page snapshot; code applies confidence gates, asks confirmation before classified-destructive actions; Web Speech API sends audio to Google; author's **34-case** result on captured fixtures.

### 5d. Applications and workflows (30)
- **BTK audit studies** — production SEO studies, Jev striking-distance triage: **1,204 pages** judged per run, **4,816 typed judgments in under 3 minutes**, **$0.0048 per 12-query batch** (jev-1.13.0).
- **discoprint** — CLI: artist discography + lyrics, five typed questions per song (theme, mood, complexity, explicit, perspective), terminal dashboard; full lyrics sent.
- **DocJev** (jerryjliu) — Python lib/CLI/app: LiteParse text + Jev to classify PDF/DOCX/PPTX or split mixed packets; optional LlamaParse OCR; published **40-document, eight-packet** comparison, raw results, no human label review.
- **Formanator** — Forma benefit claims CLI+MCP: optional Jev Choice over valid benefit/category pairs, LLM fallback on no match/low confidence; merchant+description only (no receipts); CLI asks confirmation by default, `--yolo` and MCP `create_claim` can submit without.
- **GeekLink Jev Subtitle Translator** — SRT translator/QC: each source-translation pair as Noul, flags suspected omissions/meaning changes for human review, no auto-rewrite.
- **HA-Jev** — Home Assistant: typed questions about entity state -> sensors/automations; entities report daily calls, tokens, estimated cost; token budget halts evaluation; answers carry no explanation, not for safety decisions.
- **Jev Chat Assistant** — Android overlay reading WeChat/QQ/X via accessibility; Jev typed intent/action, text model drafts **3 replies**, can fill without sending; author-reported device tests; Lark capture partial.
- **Jev Search** — web-search demo: Choice/Noul select sources, time ranges, query candidates, rank Search1API results; scores are model judgments.
- **Jev Trade** — live Hyperliquid desk, **five** isolated wallets: each tick packages book/tape/position, Jev Choice for long/short, open/close/hold, leverage; code places/pulls quote (hold = no order); dry-run documented; configured live key sends real testnet/mainnet orders.
- **Jev Trader** (jarrodwatts) — Monad/Kuru MON-USDC bot: order-book+trade data -> opt-in Jev buy/sell Choice; code places post-only quotes; default model and public demo use a **mock** dry-run; private key can place real orders and consume gas; stated block-time latency measured with the mock model, **not Jev** (conflicts with dev.to; see Contradictions).
- **Jev Wrapped** — Telegram public-channel X-ray: reads up to **1,500 posts**/12 months (sampled evenly across months if more) from public web preview; Choice over **ten** post kinds + **three** Noul (paid ad, clickbait, emotional pressure); fixed thresholds; shareable card; shares are model judgments, can misread partner promotions as ads; MIT.
- **jev-fit** — hosted fit checker/public API: one Jev call over fixed typed rubric returns plain code / Jev / reasoning LLM with probabilities; app code adds image veto + low-confidence "not sure"; closed source.
- **jev-research-pipeline** — daily research monitor: deterministic Python loop, Jev screens each source vs each open question (Noul gates then Score dimensions, via Pydantic AI `typesafe:` model), Qwen writes Obsidian note only for kept items; thresholds still cookbook starting values; pilot **5 of 7** goal conditions met; MIT.
- **jevmeter** — local video editor: transcribes, Jev preset Noul per sentence, renders shareable debate/earnings/podcast/sales meter; **200-sentence** authored eval does not establish accuracy.
- **JevNoiseGate** — Android: Jev judges whether each notification/SMS is noise, suppresses only explicit flags; local pre-filter for verification codes never reaches API; fail-open; single-device; credentials unencrypted in app-private storage.
- **Jevometry** — alpha Python toolkit: offline analysis of Jev-like output distributions, parameter sensitivity, Fisher geometry; first live smoke test captured responses but gave **no stable Fisher estimates**.
- **JevPDF** — browser PDF viewer: pdf.js extracts lines locally, one Noul per line "does it answer the query" (page text as shared state), lines above code threshold lit up; only extracted text sent, key behind server-side proxy.
- **JevSpan** — zero-shot NER (Chinese+English): code enumerates candidate windows with exact offsets; Jev Choice nominates/verifies/fixes boundaries; reports **73.7 average strict F1** on **200-sentence** samples of **12** public NER benchmarks with jev-1.13.0; entity not covered by any candidate window cannot be found.
- **Jevtown** — 10,000 computed personas react to a post/listing/product/headline: one opening request scores text vs ~**60** audience attributes (**83** for listing/product) + **seven** moderation questions, plans first wave of **600** readers; batched Choice returns reactions; text reaches next wave only while glad > sorry; also audience by interest/job/age/city/budget, first buyer question, demand curve over price ladder; personas computed from id, reactions sampled with fixed seed -> a simulation, not a forecast; MIT.
- **Lossless Rewrite** — choose ideas that must stay, model rewrites, Jev checks lost meaning and guides repairs; local editor+CLI; MIT.
- **Paper Radar** — GitHub Action: arXiv/bioRxiv/RSS titles/abstracts/categories to Jev for interest/contribution-type, code thresholds publish page+RSS; committed **50-paper** run: **5 seconds, $0.001957** (jev-1.13.0); does not inspect full papers.
- **Paper Trellis Citation Verifier** — human-reviewed: code verifies retrieved passages, Claude proposes evidence, Jev scores whether cited passage supports claim; no labelled biomedical validation set yet. See [[cb-citation-check]].
- **QuantDinger** — self-hosted quant platform: optional Jev PASS/REJECT gate for strategy and Quick Trade entry orders, LLM fallback, deterministic bypass for exits/protective orders.
- **Refix** — Slack-native product assistant; per author, scores product signals with Jev, waits for human review; integration not independently inspectable, data sent unspecified.
- **Ring Zero Security** — Apache-2.0 userspace + GPL-2.0 kernel runtime security for coding agents: deterministic Linux BPF LSM enforces protected-file boundaries; optional Jev checks can only raise a finding; off by default; repo does not measure whether model scoring improves detection.
- **Slop Filter for LinkedIn** — Chrome extension: stamps engagement bait/corporate marketing with probability; two Noul + a Choice per post; local keyword rules first; cached per post; thresholds **is_slop 0.60, is_corporate 0.70** fitted to a bundled **14-post** set (too small); EN/text only; DOM selector will need updating.
- **sortwell** — MCP server/Claude Code plugin filing notes/links/meeting lines: one request = Choice for kind/project/next action + Noul for duplicates; thresholds **0.45** to route to a project, **0.70** plus a specific matching item to call a duplicate; appends verbatim to local JSONL; author's `claude plugin eval` found agents did not call `capture` unprompted; MIT.
- **Tax Document Classifier** — Apache, text-only, **261** federal tax forms; author reports no wrong labels on two test corpora but **38 low-confidence pages**; no page-level results committed.
- **TypeSafe Conversation** (the-sof) — experimental Home Assistant Assist agent: each command sends utterance + every exposed entity to Jev in one call of ~**twenty** typed questions; acts only when chosen answer confident and clear of runner-up; asks before unlock/disarm when Jev's separate risk score crosses a threshold (not a deterministic safety gate); optional Ollama/OpenAI-compatible LLM for multi-part requests; thresholds fitted to a small recorded set; MIT.
- **TypeSafe Typewriter** — Val Town live demo updating **16** typed judgments as text changes.

### 5e. Games and robotics (17)
- **1 Million Emojis** — shared 1000x1000 emoji canvas; after each stroke Jev picks adjacent square + emoji as one Choice over named (square, emoji) pairs, sampled from probabilities.
- **Chess with Jev** — browser chess/Chess960; code computes each legal move's facts (exchanges, mates, threats), Jev picks one per turn as one Choice; candidates drawn as arrows.
- **EmbodiedJev** — MuJoCo Franka Panda workbench comparing Jev candidate decisions vs rule baselines and other models on pick/place/obstacle tasks; simulated completion != physical reliability.
- **HEIST//ONE** — browser stealth game; Jev gives batched typed judgments for **six** guards; deterministic code owns simulation and validates proposals; Decision Lens, scripted offline mode, traces; one documented live sandbox extraction.
- **Jev Chess** (jevchess.com) — shared chessboard; one Choice covers every legal move, probabilities shade the board; confidence panel uses a narrow one-ply material check; source closed.
- **Jev Driver** — browser driving demo: Florence-2 captions dropped images locally; Cloudflare Worker sends caption + lane/sidewalk to Jev, **three** Choice questions (action, category, speed limit); no rule table overriding; fixed per-zone fallback only if captioning/request fails; ~**357 MB** first-visit model download, WebGPU recommended; live at drive.mrza.ch.
- **Jev Drone** — MuJoCo quadrotor: control and safety in code, Jev for slower tactical judgments (dev.to table: 500 Hz flight controller code; 50 Hz guidance/safety reflex code; 15 Hz camera->symbolic scene classical CV; ~2.5 Hz tactical judgment Jev advisory only).
- **Jev Minecraft Agent** — Astra plans, Jev selects bounded actions from structured state via Mineflayer; author reports **8 min 43 s** dragon kill + exit, Survival/Peaceful, preselected seed with naturally active End portal; recording and per-run log local, not independently replayable.
- **Jev Plays Pokemon** (anxkhn) — emulate GBA games, Jev makes battle decisions from stats/state/moves.
- **Jev plays Snake** — code computes legal moves, food distance, reachable space; Jev chooses one move per tick via server-side SDK call; late answer = snake goes straight; no license.
- **Jev Plays StarCraft** (phyous/tsai-sc) — structured-state harness, verified run, probability trace, evidence bundle for original StarCraft shareware campaign (dev.to: first mission, **421 decisions**).
- **jev-physical-ai** — warehouse-fleet triage demo, **300 Jev calls**, raw results, local-model cost comparison; incidents simulated from templates, no robot hardware.
- **jev-plays-pokemon-red** — PyBoy; code owns route/arithmetic, Jev picks only at branches; every battle turn's faint prediction scored by Brier vs emulator RAM.
- **Magic Jev Ball** — 3D Magic 8 Ball; Convex backend sends question to Jev via Convex AI Gateway as Choice over the **20** classic answers; shows full distribution; question/result stored in Convex DB; users supply no key.
- **PlayJev** — open **0.8B** model playing **ten** browser games from the frame alone, one forward pass per move; public weights.
- **quackd** — robot orchestration CLI with optional Jev stepper choosing among permitted discrete calls; LLM still writes poses/prose; executor enforces safety; one arm ran on hardware under the LLM pilot, Jev stepper **not measured on a physical robot**.
- **TypeSafe Mario** — NES controller experiment: emulator telemetry -> structured state -> Jev chooses legal actions (dev.to: 73 stars).

### 5f. Evaluations and independent research (53)
**Independent studies of hosted Jev (numbers as stated):**
- **Awesome Jev Robustness** — index of independent tests grouped by calibration, consistency, perturbation, injection, abstention, failure modes, language; numbers reported as author findings.
- **Confident Where People Disagree** (GautamTalksDev/jevbench) — preregistered bias-corrected test, jev-1.13.0 vs ChaosNLI (100 annotators): **750 low- + 750 high-disagreement items**; Choice close to calibrated on agreed items, overconfident on contested ones (**bias-corrected ECE gap 0.264**); Noul gap inconclusive; paper + preregistration on Zenodo.
- **Convex Decision Evals** — leaderboard, Jev vs structured-output LLMs on **108** four-option questions about the Convex platform; tests platform API knowledge, not code-writing.
- **DecisionBench** (Hanno-Labs) — open benchmark runtime for document-grounded decision models; pinned tasks; OpenRouter adapter.
- **Janus** — Banking77 + Web of Science calibration; Jev-to-frontier cascade priced per row from measured tokens; `pip install janus-decide` measures a threshold on your data, ships none by default; protocol frozen before results; **no routing parameter transferred between datasets** (optimal threshold, sign of accuracy gap, whether routing paid for itself all changed); WoS labels from publication metadata so part of the error is label ambiguity.
- **Jev Capability Atlas** — bilingual EN/ZH map of use cases and failure modes; separates author's small raw-response suites from cited third-party results and TypeSafe claims.
- **Jev Enterprise Decision Fabric** — .NET architecture, **111-case** Jev-vs-Claude agent-action eval, public labels/raw JSONL; one annotator revised labels after reviewing a Jev pilot.
- **Jev IDS** — MIT intrusion detection: one Noul + one five-way Choice per network flow vs GPT-5.6 Luna and Random Forest on NSL-KDD; **300-flow pilot**; gateway masks exact Jev version.
- **Jev in Search: Three Practical Evaluations** — search stopping, coding-memory reranking, multi-hop relationship selection in DeepSearcher, MemSearch, Vector Graph RAG; some datasets private, different sample counts, animated speed illustration simulated.
- **Jev in the Wild** (arXiv 2609.30216) — survey of **2,170** public GitHub Jev projects (growth, domains, decision patterns); measures repo activity, not production use.
- **Jev Judge vs Dimension Scores** (agentjournal.dev) — three classification tasks: one direct Jev question per row vs 12-14 Jev-scored dimensions with locally fitted weights; **5,477 test rows, 34.1M input tokens, $1.43**; decomposition **0.9076 vs 0.8373** on Japanese NLI but flagged ~**25x** more hard benign rows as attacks; four repair attempts failed; author-written dimensions.
- **Jev Rerank Bench** — reranking comparison with raw responses, scoring code, dataset-level results, uncertainty intervals.
- **Jev Spam Eval** — exploratory zero-shot spam vs trained TF-IDF baselines; post-hoc tuning caveats.
- **jev-calibration-audit** — jev-1.13.0 audit: abstention options, matched Korean/English items, question-shape interference, option order; strong abstention finding is KoBBQ-specific.
- **jev-certify** — conformal routing thresholds + prediction-powered audits over Jev 1.13 via OpenRouter on CLINC150; **2,412 journalled answers**; fallback accuracy unmeasured.
- **jev-does-not-play-dice** — calibration where truth is fixed by construction (hidden fair dice, coins, four-way spinners, synthetic forecasts): Choice put **82.9%** on face 1 across all **400 rolls** at **19.0%** accuracy and turned a stated 30% risk into **5.3%**; Noul stayed near truth for 2-4 options and reported **15-17%** for 8-20 options; no model comparison; launch week, jev-1.13.0.
- **jev-fanout-bench** — billing study, batched vs one-question-per-call via OpenRouter's TypeSafe-compatible endpoint; synthetic unlabelled tickets; stability via repeated requests; separate-call latency measured serially.
- **jev-measured** — OpenRouter measurements of response shapes, cost, latency across **eight** use cases + head-to-head on **27** author-written tickets; raw data and corrections to earlier errors.
- **jev-ood-calibration** — raw Gateway responses on **three** public benchmarks + **900** rule-generated support tickets; near-calibrated on public sets, overconfident on an unseen priority rule; Boolean question showed a different error direction; Gateway did not expose fixed model version.
- **jev-orderby-bench** — see section 3; one seed, **30** ESCI queries; two-decimal output leaves **53 of 360** rows tied at the top so `LIMIT k` cuts inside a tie; regenerated locally for about a cent.
- **jev-sec-bench** — blind jev-1.13.0 security eval: **662** public prompt-injection messages + **200** matched vulnerable-code pairs; fixed 0.5 threshold; Go runner, TUI.
- **Jevals.com** — independent benchmark of hosted Jev + **six** LLMs on PubMedQA, Banking77, HelpSteer2; human labels, proper scores, calibration, cost, latency; suite files/logs public, harness not; LLM probabilities from a prompt adapter.
- **JevBench** (fstandhartinger) — **534 frozen cases** per complete entrant; four-axis score (accuracy, calibration, latency, cost).
- **LLM Memory Audit: Jev earnings test** — pre-registered; `jev-1.13-20260917`; **12,533** US earnings announcements, each company only vs itself: **no detectable memory** (within-company AUC **0.506** on beats vs **0.587** pooled for Claude Sonnet 5 as positive control); licensed FMP data withheld; provisional until **757** prospective announcements scored in **January 2027**.
- **TypeSafe AI Benchmark** (iammrduncan) — side-by-side Jev vs Qwen-on-Cerebras with raw exports and cost accounting.
- **When a Judgment Layer's Self-Reported Fields Lie** (Zenodo) — three judgment layers on identical items (Laya local; Jev and a frontier model remote), ledger cost accounting, Murphy/Brier/ECE; Jev findings: verdict vocabulary reaching **three** values where **six** are documented; a `sufficient` field that does not separate thin from contradictory evidence; the contradiction claim rests on **seven** live readings with no JSON artifact, stated in the errata.
- **LeJudge** — MIT PushT study: LeWorldModel imagined latents -> closed-vocabulary facts, Jev typed questions about NL constraints added to a CEM planner cost; one world model, **twelve** constraints; near-miss false positives and rollout drift are limitations.
- **Love-Language Arena** — local reproduction of the pattern on Ollama logprobs; does **not** call Jev; labels are Claude-generated; shows the pipeline runs, not that judges are valid.

**Open / local Jev-style alternatives (not hosted Jev; see [[laya]], [[kev]], [[openjev-and-nanojev]], [[benchmarks-and-comparisons]], [[system-one-alternatives-overview]]):**
- **blink** (thegovind) — Apache-2.0 code, TypeSafe-compatible API; weights non-commercial research/eval only; no hosted endpoint.
- **Bosun v3.1** (Hanno-Labs) — Apache-2.0 Qwen3-based, **0.6B and 1.7B** weights; choice/score/noul.
- **jeff** (logan-markewich) — GLiFormer **400M** self-hosted server, Jev-compatible API; weaker than Jev on reasoning-heavy items in its JevBench comparison; hosted cost figures estimates.
- **jevmlx** — MIT Apple Silicon: Boolean/enum/multi-select fields scored from MLX logits in one prefill, schema-valid JSON, System One-compatible endpoint; needs calibration.
- **jevos** — MIT **1B** yes/no model, q4_k_m GGUF on CPU via llama.cpp, `/v1/systemone`; Noul only (Choice and Score return **422**); reports **0.815 vs 0.927** hosted Jev on **2,000** questions from unseen policies; training code + eval set unpublished.
- **Kev** — Apache locally runnable Choice/Score/Noul at **0.8B, 4B, 9B**; weights, training code, System One-compatible server, frozen suites, playground; author: Kev-9B **0.822** new-source dev accuracy vs **0.857** hosted Jev; Jev training data unknown so not a controlled comparison.
- **Laya** (NandhaKishorM) — open local models + router, English/multilingual; Jev comparisons use different prompts/sample sizes; raw calibration and some languages weak.
- **LLM2Jev** — Apache toolkit reading causal-model logits via Transformers/SGLang; System One-shaped endpoint; web+Snake demos; shared-prefix cache benchmark on one model/GPU, not decision quality.
- **Luce** — open recipe: task description -> LLM teacher writes data -> LoRA + decision head on Qwen3-4B-Base, 12 GB GPU; README reports accuracy+ECE vs Jev on identical items including where training does not help.
- **NanoJev** — **0.6B** for Maze, Snake, ViZDoom; not a general API replacement.
- **OneJev** (OmniJev) — Apache-2.0 multimodal, **four sizes (0.8B to 27B, plus 27B FP8)**, images/video/text, `/v1/systemone`-compatible.
- **Open Alternative to Jev** — Apache library reading option-token probabilities via Transformers/vLLM; packed vs separate question modes; temperature scaling; packed answers can change with question order; not an API server.
- **Open Medical Jev** — MIT reproduction: two frozen open-weight readers, fit-free confidence gate, split-conformal sets; four-reading config within **2 points** of hosted Jev 1.13.0 on three **600-item** medical licensing papers, one 24 GB GPU; only the China paper is a real exam; trails hosted Jev at highest precision tiers.
- **OpenJev (DiffusionGemma)** (razorback16) — Apache; DiffusionGemma **26B** probabilities via System One-shaped API; NVIDIA path pins unmerged vLLM branch.
- **poorjev** — local reproduction on zero-shot NLI models with temperature scaling and conformal abstention; ECE **0.170 -> 0.071** on its own small labelled set; offline.
- **Rizzo Flow** — local server reading answer-token probabilities, Jev-compatible + own numeric primitive; explicitly no quality-parity claim.
- **RSI-Jev** — **2B** model trained by a recursively self-improving research system; **0.791** typed-decisions (after training on that benchmark's train split), **0.774** on **873** held-out scienthoon tickets; MMLU-Pro **0.383** on a 1,000-question subset.
- **ruling** — MIT System One-compatible server, Apple Silicon, stock model logits, no training; re-scores **256** public judgments carrying Jev's own answers (**231 vs 238**, no significant difference); no CUDA path.
- **SemIf (formerly OpenJev)** (TheoLeeCJ) — research baseline; reproduces interface pattern, not Jev's model/training.
- **Simple Jev** (featherless-ai) — Apache local server on open-model logits; tokenizer support and calibration vary.
- **stuntd** — experimental local Jev-compatible proxy on Laya; records decisions in SQLite, trains a head per decision site, forwards uncertain requests upstream; demos use rule-based teachers.
- **TetraJev** — MIT local layer: two frozen readers, four readings fused fit-free, routed by agreement into auto-release vs human review; eight decision suites + RAG reranking incl. DecisionBench's **35** task categories; does not call TypeSafe.
- **Verdict** (Manavarya09) — Apache-2.0 **118M** multilingual bi-encoder, ONNX CPU/browser, temperature scaling + optional conformal abstention; scores lower than Laya on the published typed-decision suite.
- **Von** — open local model; README **91.23%** headline without matching artifact vs its 49-task table **71.5%** macro accuracy (internal inconsistency, author-reported).
- **WebJev** (lexmount) — Apache-2.0 Qwen3.5-35B-A3B fine-tune for browser agents; **47/122** gradable successes vs **20/120** for Jev 1.13 in the same agent; **83.72% vs 84.70%** mean accuracy on eight single-step benchmarks; runs on different days, different gradable subsets; weights need one **80 GB** GPU.
- **laya.tools** — directory of Laya projects (see 5g).

### 5g. Showcases and field notes (14)
- **Browser Use + Jev** (Gregor Zunic, X) — real-time flight-search demo, dynamic DOM action space.
- **Free JEV API Guide** (jevapi.io) — first-request walkthrough; examples go through BeatAPI.
- **Internal classifier field note** (X, identityTorn) — early matched-precision comparison vs a private fine-tuned Qwen classifier; anecdotal.
- **Jev by Example** — ten MIT JS exercises with policies, fixtures, baselines; offline needs no key; live outcomes not yet verified.
- **Jev Typewriter launch post** (Steve Krouse, X) — playable 16-judgment demo.
- **Jev Web Analyzer** — Next.js demo: public page Markdown -> Vercel Gateway; needs both credentials.
- **jev-agent-skill** (yuyang2230) — Claude Code/ZCode skill offloading small judgments to Jev on OpenCode Zen's **free** `/v1/systemone` endpoint; zero-dependency `jev.py` with retries for transient 500s, WAF-safe User-Agent, GBK-pipe-safe stdin; adapted from official typesafe-ai/skills SKILL.md (MIT); e-commerce comment-triage case study.
- **jevbooks** — bilingual gallery of open-source Jev projects, Jev gates/tags each listing, **sixteen** design patterns from **ten** codebases; site source not public.
- **laya.tools** — independent Laya-ecosystem directory, daily imports; not Jev itself.
- **Learn Jev end to end** — MIT **12** Python notebooks, Jev inside hand-rolled agent loop (router, tool-call guard, done gate, judge), **13** use cases vs labelled fixtures, compared with two LLMs via system-one-adapter; one committed run including cases where LLMs did better.
- **Milvus Search with Jev** — **nine** notebooks: Gemini embeddings + Milvus + Jev for reranking, filtering, search stopping, routing, cache reuse, curation, guardrails, evaluation; synthetic data, not benchmarks.
- **Qwen on Cerebras comparison** (Shannon, X) — video + source-backed comparison of structured-output LLM vs Jev.
- **Typed Decisions, Not Chat** (warmersun.com) — walkthrough separating TypeSafe claims from public evidence.
- **typesafeai.app** — directory of public Jev capabilities with evidence level (author-reported to editor-reproduced) and Official/Community label.

## 6. Cross-cutting patterns the catalogue shows (my synthesis from the entries)
- [inference] Dominant shapes: (1) gate/permission layers on agent tool calls (toolgate, jev-use, pi-verdict, fx, jev-engineering, jev-axi); (2) model/skill routers (Switchboard, jev-router, Jevonian, Codex routers, skill routers); (3) context/compaction pruners; (4) rerank/search over rows or lines; (5) SQL-embedded judgments (pg-jev, DuckDB, jevql, mysql-ailike); (6) bounded-action browser/mobile/game agents. Common design: code owns loop/safety/arithmetic, Jev answers the narrow judgment.
- Recurring cautions in entries: fail-open vs fail-closed varies by tool; many send content to TypeSafe or a gateway; several store keys in plaintext; "shadow mode" is a common default; thresholds in several tools are uncalibrated or fitted to tiny sets (14, 21, 10, 24 items).
- Failure modes independent studies surfaced: overconfidence on contested/OOD items; over-abstention or forced wrong answers depending on whether a no-match option exists; ties from two-decimal output; batching changes rankings; adversarial text swaying classifiers; thresholds not transferring across datasets.

## Numbers & limits (collected)
| Item | Value | Source entry |
|---|---|---|
| Documented example | technical @0.85; score 1 on 0-2; noul urgency 1.0 | README quick-start |
| KoBBQ abstention | 95% of 300; 79% stereotype when option removed | jev-calibration-audit |
| Banking77/WoS cascade | WoS parity at 47% higher cost | Janus |
| CLINC150 | 84.75% auto-routed, 2.25% loss; scope gate missed by 3.6x | jev-certify |
| Ordering | 6/6 gates on 360 rows; fails 4/6 on 306 pairs; 53 ties at 0.99 | jev-orderby-bench |
| Action gate | 111 cases; Jev 100 vs Claude 102; 1 unsafe allow each | decision-fabric |
| Dice test | 82.9% on face 1 of 400 rolls, 19.0% acc | jev-does-not-play-dice |
| Cost studies | $0.0048/12-query batch; $0.0008/video; $0.001957/50 papers; $1.43 for 5,477 rows | BTK; jev-skip; Paper Radar; Judge vs Dimension |
| Open models | Kev-9B 0.822 vs hosted 0.857; jevos 0.815 vs 0.927; ruling 231 vs 238 | author-reported |

## Contradictions and flags
- **Date:** README header "Last updated: 2026-09-23" and "Recently curated ... 22 September 2026", yet the Building-with-TypeSafe-Jev entry says it is a "2026-09-25 snapshot" — a date after the stated update.
- **Model id spelling:** Vercel route uses `typesafe-ai/jev`; the fx entry says `typesafeai/jev`; OpenRouter uses `typesafe/jev-1.13`; Cloudflare uses `typesafe/jev`. Treat each as route-specific.
- **jev-trader latency:** the directory says the stated block-time latency is measured with the **mock** model, not Jev; the dev.to guide ([[community-guide-devto]]) reports "around 81ms" model latency. Do not rely on 81 ms as a measured Jev figure.
- **OpenJev name collision:** "OpenJev (DiffusionGemma)" (razorback16, 26B) vs "SemIf (formerly OpenJev)" (TheoLeeCJ); dev.to's "TheoLeeCJ/openjev ... 4B open model" corresponds to the latter.
- **Von:** 91.23% headline vs 71.5% macro in its own table.
- Directory says every number is task-specific; none are TypeSafe-verified.

## Other facts
- `jev-fit` and several tools add vetoes/"not sure" states in code rather than trusting Jev's raw output.
- The directory's contribution rules: one README entry per PR; include license, off-device data, and a limitation.

## Related
[[jev-mcp-server]] · [[typesafe-agent-skill]] · [[openrouter-jev-guide]] · [[community-guide-devto]] · [[community-guide-marktechpost]] · [[benchmarks-and-comparisons]] · [[laya]] · [[kev]] · [[openjev-and-nanojev]] · [[system-one-alternatives-overview]] · [[sdk-overview]] · [[confidence]] · [[confidence-gated-routing]] · [[cb-llm-guardrails]] · [[cb-reranking]] · topics: [[topic-agent-integration]] [[topic-calibration]] [[topic-model-selection]]
