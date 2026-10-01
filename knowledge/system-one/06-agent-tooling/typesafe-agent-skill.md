---
title: TypeSafe Agent Skill
kind: playbook
source: Agent skill (docs page); typesafe-ai/skills SKILL.md (upstream vendor skill)
source_url: https://docs.typesafe.ai/agent-skill, https://github.com/typesafe-ai/skills/blob/main/skills/typesafe-ai/SKILL.md
tags: [agent-tooling, patterns]
topics: [topic-agent-integration, topic-state-design, topic-calibration]
---
# TypeSafe Agent Skill
> The vendor's drop-in skill (`typesafe-ai`) that tells coding agents how to build with System One/Jev: read live docs first, pick the right primitive, design narrow questions, compose in parallel, verify; plus install steps and troubleshooting.

## Part A — Installing and using the skill (docs page "Agent skill")
Skill gives an agent full context on the TypeSafe API: the three question types ([[primitives-overview]]), architectural patterns ([[patterns-overview]]) and best practices for structuring evaluations.

### Install (choose ONE method to avoid duplicate copies)
| Agent | Commands |
|---|---|
| Claude Code | `claude plugin marketplace add typesafe-ai/skills` then `claude plugin install typesafe@typesafe-ai` |
| Other agents | `npx skills add typesafe-ai/skills --skill typesafe-ai`; choose agent when prompted; project-local by default, add `-g` for global |
| Copy-prompt | Paste a prompt telling the agent to install via the right method (Claude Code: the two commands; otherwise npx) "Use one installation method", then read the skill at github.com/typesafe-ai/skills/blob/main/skills/typesafe-ai/SKILL.md (raw: raw.githubusercontent.com/typesafe-ai/skills/main/skills/typesafe-ai/SKILL.md) and use it on the project |
| Manual | copy the whole `skills/typesafe-ai` directory **including reference files** into the agent's skills dir |

Invoke: with the Claude Code plugin use `/typesafe:typesafe-ai`; in any agent say "use the TypeSafe skill".

### Updates
- Claude Code: `claude plugin marketplace update typesafe-ai` then `claude plugin update typesafe@typesafe-ai`; restart or `/reload-plugins`. Auto-update: `/plugin` -> Marketplaces -> typesafe-ai -> Enable auto-update.
- skills.sh installs: `npx skills update`. Manual copies: replace the entire directory with latest from GitHub.

### Example prompts (all name the skill)
1. Brainstorm: "Using the TypeSafe skill, explore the project and find opportunities for using intelligent judgement to stand in for complex parsing or other fragile code."
2. Experiment: give a key exported as `TYPESAFE_API_KEY` (create at console.typesafe.ai/keys) and let the agent run cheap test queries, "Propose changes based on the most promising results."
3. Cookbook match: point at a specific cookbook (e.g. `/cookbooks/consistency_noul_cookbook`) or the cookbooks index and ask for applicable refactors to be "less fragile or complex" ([[cookbooks-overview]]).

### Good vibe-coding principles (vendor list)
1. Talk it out with your agent.
2. Review the plan before implementing.
3. **Put constants (questions and thresholds) in a single place** for easy review. "Agents aren't great at writing questions, so expect to edit collaboratively."
4. Don't take assertions at face value; have the agent validate assumptions.

### Common issues
| Symptom | Fix |
|---|---|
| Agent isn't using the skill | Claude Code: invoke `/typesafe:typesafe-ai`. Others: "use the TypeSafe skill". Confirm installer targeted your agent; restart |
| Routing isn't working | Check questions and thresholds: too high -> false negatives, too low -> false positives; make questions more specific ([[confidence-gated-routing]]) |
| Confidence thresholds everywhere | If you only need the best option, take the **highest-confidence option** rather than a threshold; if you have a specific statistical algorithm, use **probabilities** not confidence ([[confidence]]) |
| Hard to review TypeSafe code | Humans should review the questions and threshold constants — define them in one code file |
| Agent invents request/response fields | A **stale skill** can cause it: update via your install method and retry |

## Part B — Upstream SKILL.md (vendor's rules to coding agents), in full substance
Frontmatter: `name: typesafe-ai`, `license: MIT`. Description: build AI-powered software with TypeSafe: small units of AI intelligence used like programming primitives; System One models (including Jev) turn natural language and application state into typed judgments and probabilities; use when a feature needs programmable common sense, when brainstorming what AI could enable, or when an LLM prompt-and-parse step could become a structured decision. Applications: routing, ranking, extraction, verification, interactive experiences — "starting points, not the limits". Read live docs and cookbooks to discover patterns.

### Core framing
- TypeSafe turns AI into **programming primitives**: small judgments composed into larger capabilities. System One models return fast, focused judgments software can consume directly. **Jev** = flagship and first System One model; it returns **typed answers and probabilities rather than generating text or reasoning explanations**. **Code owns the workflow; the model supplies programmable common sense** where ordinary code needs semantic understanding ([[system-one-model-category]], [[jev-introduction]]).

### Rule 1 — Read the live docs (they are the source of truth)
- The skill gives direction; docs carry current concepts, prompting guidance, API contracts, SDK usage, models, limits, worked examples.
- Start with the documentation index docs.typesafe.ai/llms.txt; use **targeted reads** rather than loading the whole site.
- Mintlify serves Markdown by appending **`.md`** to a page path (e.g. `/concepts/how-to-build-with-system-one.md`); convert extensionless links to `.md`; resolve relative links against `https://docs.typesafe.ai`.
- Before writing an integration read the current API or chosen SDK page and relevant question guidance. For a new workflow also inspect the **closest cookbook** — it "often shows a better decomposition than a generic classifier".
- Fallbacks: if the index is unavailable use direct links/site nav; if Markdown fetching fails try the normal page; if live access is unavailable use local docs or installed SDK types, **state that limitation, and avoid inventing version-dependent details**.

| Task | Start here (docs paths) |
|---|---|
| Understand the programming model | /concepts/system-one.md, /concepts/how-to-build-with-system-one.md ([[how-to-build-with-system-one]]) |
| Explore what to build | /concepts/use-case-map.md, then relevant cookbooks ([[use-case-map]]) |
| Prepare inputs and questions | /concepts/state.md, /primitives.md, then the primitive's page ([[state]], [[primitives-overview]]) |
| Decide how to handle uncertainty | /confidence.md ([[confidence]]) |
| Write API code | /api.md, /sdk/python.md, /sdk/javascript.md ([[http-api-reference]], [[sdk-python]], [[sdk-javascript]]) |
| Update an older integration | /migrating-to-v1.md and the installed SDK's current reference |

### Rule 2 — Find the useful shape
- Start from the behaviour the user wants (show, select, change, hand off); work backward to the judgments needed. **Keep known rules, calculations, exact lookups and execution in code.** Preserve the user's stack and scope; add TypeSafe where semantic understanding helps.
- Consider more than classification. Six starting-point patterns (combine freely):
  1. **Route and fill known arguments** — a request selects a handler and its typed parameters; ask branch-specific questions up front, consume only the relevant answers. Explore function calling (`/cookbooks/function_calling.md`, [[cb-function-calling]]) and speculative fan-out (`/patterns/fan-out.md`, [[speculative-fan-out]]).
  2. **Select instead of generate** — find candidate values or source spans in code, use a judgment to select, then copy/normalize. Code can also assemble source text into a formatted document or reading guide. Explore value extraction (`pre_parsed_value_extraction_cookbook`, [[cb-pre-parsed-value-extraction]]) and structure recovery (`autoformat`, [[cb-structure-recovery]]).
  3. **Find and judge evidence** — retrieve candidates, compare relevance to a query, select context. Explore reranking (`rerank_typesafe`, [[cb-reranking]]) and hierarchical classification ([[cb-hierarchical-classification]]).
  4. **Turn judgments into reusable data** — score dimensions once, let code or user controls change weights/thresholds/rankings/views; with labeled outcomes these signals can become classical ML features. Explore composite scoring ([[composite-scoring]]) and feature discovery (`autoresearch_feature_discovery`, [[cb-autoresearch-feature-discovery]]).
  5. **Verify and escalate** — check specific claims/fields against their evidence; send uncertain or failing cases to a person or reasoning model. Explore citation checks ([[cb-citation-check]]) and extraction cascades (`sde_cascade`, [[cb-sde-cascade]]).
  6. **Respond to changing state** — code retains goals and observations while fresh judgments guide the next bounded step. **Keep inferred state distinct from observed facts, and check freshness before applying a result to a changed situation.**
- Open-ended requests: offer the few directions that best serve the goal and recommend a starting point. Concrete requests: choose the relevant pattern and build; "a brainstorm is not a mandatory detour."

### Rule 3 — Design the judgments (choose by what the answer means)
| Need | Primitive | Important distinction |
|---|---|---|
| One of a defined set | [[choice]] | picks one option; its distribution compares competing options |
| Whether a condition holds | [[noul]] | probability of yes; **no separate confidence**; use **one per label when several may apply** |
| Degree along a described dimension | [[score]] | probability-weighted position on ordered levels; use comparable per-item Scores for graded ranking |

Question-writing rules:
- Give each question enough relevant **state**: source text, identities, relationships, policies, current facts. Prefer **named JSON fields** when context has several parts.
- Put the judgment in **instructions**; define possible answers in **criteria**.
- **Question IDs are for code and are NOT sent to the model** — include the complete meaning in the question itself.
- Reference nested state with backticked paths such as `ticket.messages[0].text`.
- Ask **one narrow, coherent judgment per question**. Split independently useful dimensions without destroying the relationship being judged. A bounded action selection or contextual interpretation is valid; "atomic does not mean literal fact extraction or a one-sentence limit."
- Strings suffice for simple questions; use structured objects/arrays when definitions, contrasts, exclusions or examples clarify instructions or criteria. **Score levels must describe concrete situations and stand on their own.**
- Keep needed answers available: include a **no-match outcome** when nothing may fit; use a separate presence judgment when independently useful. For **source-value selection, check candidate coverage — the model cannot choose an omitted value.**

### Rule 4 — Compose and verify
- **Ask independent questions over the same state together**, including useful speculative questions: they run in parallel and **cannot see one another's answers**. State each speculative premise explicitly; code consumes the applicable answers. A second request is warranted only when an earlier answer is needed to fetch evidence, construct new state, or determine next options. Extra questions still use tokens — **measure actual request budgets, cost and end-to-end latency** ([[topic-cost-latency]]).
- Use probabilities and confidence to guide behaviour; evaluate thresholds on the user's data and consequences. **Choice/Score confidence summarizes distribution concentration, not overall workflow correctness or permission to act.** A Noul near 0.5 means similar yes/no probability, **not medium intensity**. Several acceptable alternatives can also spread probability; low confidence need not invalidate a harmless preference choice. Ignore uncertainty on unused branches.
- Keep policy explicit and raw judgments reusable. **Weighted scores suit compensating preferences; an "any serious violation" rule needs separate conditions.** Changing a weight or display filter need not rerun inference when evidence and question meanings are unchanged ([[composite-scoring]]).
- **Typed output guarantees the interface, not truth.** System One models are trained for calibrated decisions; **validate performance in the target domain**.
- Test representative cases and the resulting application behaviour. For failures inspect exact state, questions, candidates, answers, composition, observed outcome; **separate missing evidence, model errors, code errors, service failures**. Treat cookbook thresholds and demo results as **examples to evaluate, not universal rules or permanent model limitations**.
- **Keep API credentials server-side in web apps.**

## When to use / when NOT to use
- Install when a coding agent will write or review code that calls System One; invoke when brainstorming where judgment replaces fragile parsing.
- Not a substitute for the live docs; stale copies cause invented fields.
- For tools the agent can call directly (no code), see [[jev-mcp-server]].

## Numbers & limits
None numeric in the skill itself; thresholds are deliberately delegated to the user's data. No specific token/latency figures.

## Gotchas
- Stale skill => hallucinated request/response fields; update.
- Install **one** method only.
- Thresholds everywhere is an anti-pattern: argmax needs no threshold.
- Agents are weak at writing questions; humans review the question+threshold file.

## Related
[[jev-with-coding-agents]], [[jev-mcp-server]], [[how-to-build-with-system-one]], [[confidence]], [[primitives-overview]], [[patterns-overview]], [[cookbooks-overview]], [[sdk-overview]], [[http-api-reference]]
