---
title: Use Case Map
kind: reference
source: Example use cases (TypeSafe docs, concepts/use-case-map)
source_url: https://docs.typesafe.ai/concepts/use-case-map
tags: [use-case, system-one, patterns]
topics: [topic-routing, topic-guardrails, topic-extraction, topic-classification]
---
# Use Case Map
> Brainstorming catalogue: 5 headline categories, 20 industry/task idea lists, and a 10-row "decision shape" table. Open the closest industry, scan the example decisions, adapt to your own documents and actions.

## What it is / How it works
The docs page is a brainstorm aid, not a spec. It has three parts: (1) five headline "use case categories", (2) an accordion of 20 "automation use cases" (each a bullet list of semantic decisions), (3) a table mapping a *decision shape* to when to reach for it. Every item below is a decision a Jev/System One query can make (typed answer + probability, see [[primitives-overview]], [[confidence]]); code owns control flow. The source states no numbers beyond the ones recorded in the table at the end.

## 1. Headline categories (5)
| Category | Idea in the source |
|---|---|
| AI Automation Software | Interleave AI with reliable software so it can run "a million times in the background" with no human co-pilot. Code owns control flow (not markdown files); TypeSafe handles the semantic decisions and language understanding. |
| Real-time applications | Frontier intelligence at real-time speed (**150ms**) means AI can decide faster than human perception. Fast/smart enough to be programmed to play games or embedded in a UI. |
| AI Map Reduce over Big Data | "100x cheaper" so you can process giant datasets: search giant corpora for relevant info, classify giant agent traces, extract features to make predictions. |
| Universal Verification | Verify the input prompt, extractions, reasoning traces, tool calls, or inputs of any other AI. Detect jailbreaks, citation errors, hallucinations, mistakes and other error modes of other AIs/LLMs at a fraction of the cost of the actual LLM call. |
| Harness Engineering | Use Jev queries to make an agent harness smarter: model routing, semantic context retrieval, LLM error detection and guardrails, reasoning-trace classification "at lightspeed and a fraction of the cost". |

## 2. Industry / task use-case lists (all 20, every bullet)

**Search and retrieval**
- Replace or supplement embeddings in RAG pipelines with semantic search, scoring, ranking.
- Score query-to-candidate relevance.
- Rerank results with pairwise comparisons.
- Cross-encode queries and candidates for higher precision.
- Select useful context for downstream AI workflows.

**Scientific discovery**
- Screen papers against inclusion/exclusion criteria for systematic reviews.
- Label passages in interview transcripts, open-ended survey responses, field notes using predefined themes/categories.
- Check whether cited passages support claims in manuscripts and generated summaries.
- Flag missing methodological details (controls, dataset descriptions, experimental settings).
- Identify entities and relationships across papers to build research knowledge graphs, linking findings to supporting passages.

**Model routing**
- Build a custom router that chooses which LLM receives each prompt.
- Set routing rules and thresholds for your workflow.
- Classify intent and domain.
- Estimate difficulty and risk.
- Escalate requests that need a more expensive model.

**LLM guardrails**
- Place semantic checks on every LLM input, output, and tool call at a fraction of the cost of the LLM call.
- Detect jailbreaks and prompt injection.
- Identify policy violations and sensitive-data exposure.
- Detect tool-call errors and response-quality failures in real time.
- Log structured check results and probabilities so AI-system/harness failures are easier to trace.

**Semantic code linting**
- Add automated semantic lints to code and writing.
- Define checks for the team's coding conventions and writing guidelines.
- Run them in CI and flag violations for review.

**Feature extraction for predictive modeling**
- Extract probabilistic features from natural-language data.
- Combine them with structured data to train models for tasks with ground-truth outcomes.
- Use autoresearch workflows to propose feature definitions and evaluate predictive value against held-out ground truth (see [[cb-autoresearch-feature-discovery]]).

**Recruiting**
- Evaluate resumes, applications, interview feedback against explicit, job-related criteria.
- Identify relevant experience; score evidence for required competencies.
- Match candidates to roles; route to hiring managers or recruiters.
- Escalate uncertain cases for human review.

**Lead generation**
- Match company profiles, executive bios, inbound messages to an ideal customer profile.
- Score industry fit and company maturity.
- Detect buyer relevance, pain points, purchase intent.
- Prioritize and route leads.

**Customer support**
- Classify incoming tickets by issue, product area, customer intent.
- Process call transcripts to extract customer issues, commitments, follow-up actions.
- Detect urgency, frustration, churn risk, refund requests.
- Route cases to the right team, queue, or automated workflow.
- Verify support responses against policies and the customer's request.

**Insurance claims**
- Classify first-notice-of-loss reports, adjuster notes, supporting documents.
- Detect claim complexity, missing information, potential fraud indicators.
- Prioritize claims for straight-through processing or specialist review.
- Escalate uncertain or high-risk cases to a human adjuster.

**Financial crime**
- Evaluate transaction narratives, KYC documents, alert histories for suspicious characteristics.
- Match entities across inconsistent names, profiles, records (cf. [[cb-entity-alignment]]).
- Prioritize alerts by risk, relevance, evidence quality.
- Route ambiguous cases to investigators.

**Legal and compliance**
- Classify contracts, policies, regulatory filings, marketing claims.
- Detect missing clauses, prohibited claims, policy violations.
- Verify documents against explicit legal/compliance requirements.
- Escalate high-risk or uncertain findings to counsel or compliance teams.

**E-commerce marketplaces**
- Classify and normalize product listings across inconsistent seller catalogs.
- Extract product attributes from titles and descriptions.
- Detect prohibited listings, counterfeit signals, review abuse, policy violations.
- Rank products; route uncertain listings for human review.

**Moderation and trust and safety**
- Apply company-specific, nuanced criteria to decide which posts meet moderation standards.
- Moderate user content and automated conversations across communities, customer support, and SDR workflows.
- Detect toxicity, harassment, spam, fraud, unsafe advice, personal-data exposure, opt-out requests, policy-violating claims.
- Combine severity and confidence to allow, warn, review, or block content.

**Advertising**
- Evaluate creative assets, campaign copy, landing pages, placement context.
- Classify brand safety and audience suitability.
- Check regulatory compliance and prohibited claims.
- Evaluate creative quality and ad-to-landing-page alignment.

**Gaming**
- Evaluate player reports, in-game chat, reviews, support conversations.
- Moderate chat; detect abuse, toxicity, suspicious behavior.
- Annotate content; score frustration or engagement.
- Detect churn signals; route player-support requests.

**Risk assessment**
- Convert incident reports, claims notes, transaction descriptions, vendor assessments into probabilistic risk indicators.
- Use them in insurance and underwriting workflows.
- Classify risk types; detect suspicious characteristics.
- Score severity; prioritize review.
- Extract features for broader risk models.

**Demand forecasting**
- Enrich forecasting models with semantic signals from customer inquiries, sales notes, product reviews, support tickets, market reports.
- Extract purchase intent, urgency, product interest.
- Detect supply concerns, competitive pressure, emerging demand themes.
- Feed those features into a forecasting model alongside historical time-series data.

**Graphs and knowledge graphs**
- Annotate and verify knowledge graphs with typed semantic decisions.
- Classify relationships and entity types.
- Detect contradictions between records or claims.
- Support probabilistic traversal and hierarchical classification (see [[cb-hierarchical-classification]]).

## 3. Decision-shape table (task categories)
| Decision shape | Reach for it when | Examples |
|---|---|---|
| Classification | One known category should win | intent, topic, department, risk type, entity type |
| Detection | You need a probability that one property is present | spam, fraud, urgency, jailbreaks, sensitive data |
| Scoring | The answer belongs on an ordered rubric | severity, relevance, quality, frustration, suitability |
| Routing | A category selects the next code path | tool use, escalation, model routing, support queues |
| Search | Find items matching a natural-language query | semantic search, document discovery, candidate generation |
| Retrieval | A workflow needs the most relevant context/records | RAG context, evidence retrieval, knowledge lookup |
| Ranking | Items ordered by semantic relevance/quality | search results, recommendations, candidate prioritization |
| Verification | An artifact must be checked for specific failure modes | citation support, policy violations, tool-call errors, response quality |
| ML Feature Extraction | A downstream classical ML model needs semantic signals | purchase intent, product interest, competitive pressure, churn signals |
| Structured Data Extraction | Known fields must be recovered from unstructured input | candidate attributes, order fields, document labels |

Mapping to primitives is not stated on the page. [inference] "Detection" ~ Noul ([[noul]]), "Classification"/"Routing" ~ Choice ([[choice]]), "Scoring"/"Ranking" ~ Score ([[score]]).

## When to use / when NOT to use
- Use as brainstorm input; pick the closest industry then adapt to your documents and actions.
- Recurring theme across industries: *escalate uncertain cases to a human* (recruiting, insurance, financial crime, legal, moderation) — i.e. [[confidence-gated-routing]].
- Recurring theme: "combine severity and confidence" (moderation) — i.e. [[composite-scoring]].
- The page says nothing about when NOT to use; no benchmarks or accuracy claims are made here.

## Numbers & limits
| Claim | Value (as stated) |
|---|---|
| Latency for "real-time" | 150ms |
| Cost vs. LLM | "100x cheaper" (headline-category claim; no baseline given on this page) |
| Counts | 5 headline categories; 20 automation use-case lists; 10 decision shapes |

## Gotchas
- Page is aspirational/brainstorm; each bullet is an idea, not a verified result. Verified worked examples live in the cookbooks ([[cookbooks-overview]]).

## Related
[[cookbooks-overview]] · [[demo-smart-home]] · [[patterns-overview]] · [[primitives-overview]] · [[cb-llm-guardrails]] · [[cb-citation-check]] · [[cb-reranking]] · [[intent-routing]] · [[system-one-model-category]]
