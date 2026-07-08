# sdcourse × lucsystemdesign — Dual-Lens System Design Learning Pack

**Date:** 2026-07-07
**Status:** Design approved; ready for implementation plan
**Author:** Claude (brainstormed with repo owner)

## 1. Goal

Produce a single, comprehensive **distributed-systems / system-design learning
pack PDF** that teaches every topic covered by the two system-design examiner
personas in this repo — **lucsystemdesign** (Luc) and **sdcourse** — presented
through *both* voices at once, then verify it to the same ≥9.0/9.0 bar the
existing learning packs meet.

This reuses the established learning-pack machinery (generator script →
headless-Chrome PDF → multi-agent verification loop). It does **not** invent a
new pattern; it extends the pattern to a **dual-examiner, dual-lens** pack.

### Why dual-lens

The two personas teach overlapping distributed-systems material from opposite
angles:

- **Luc (lucsystemdesign)** — *decision frameworks*. "It is not X. It is Y."
  Reframes the misconception, gives a decision rule, and always includes
  "when NOT to use it." Chooses consciously.
- **sdcourse** — *production build*. Benchmarks, FAANG-scale failure modes,
  anti-patterns, exact numbers. Builds the thing and shows how it breaks.

Presenting both per topic — and explicitly mapping where they **converge or
diverge** — is more valuable than either voice alone, and mirrors the repo's
existing "where do they disagree" strengths (vault-ask, STORM contradiction
mapping).

## 2. Content source (authoritative truth)

The persona files are the **self-contained source of truth**. No external
capture (no Substack vault, no transcripts) exists for these two authors, and
none is needed — the same self-contained model the Ben Dicken and Vu Trinh
packs use at verification time.

- `.claude/skills/lucsystemdesign-persona/SKILL.md` (467 lines, ~45 positions)
- `.claude/agents/lucsystemdesign.md` (663 lines — richer, with verbatim quotes)
- `.claude/skills/sdcourse-persona/SKILL.md` (283 lines, ~28 positions)
- `.claude/agents/sdcourse.md` (619 lines — richer, with verbatim quotes + benchmarks)

These files are **read-only** for this project. They are the ground truth for
both content generation and examiner scoring. We do not edit them.

## 3. Architecture & files

Mirrors the Spark / Ben Dicken packs exactly.

| File | Role | Committed? |
|------|------|-----------|
| `scripts/generate_sdcourse_luc.py` | Generator: hardcoded CSS (copied from `generate_vutr_spark.py`, **minus** the Mermaid `<script>` tag) + `COVER` + `CH1..CH23` HTML strings → `output/sdcourse_luc.html` → headless-Chrome `--print-to-pdf` → `output/sdcourse_luc.pdf`. Content lives in the script strings. | ✅ script only |
| `.claude/workflows/verify-sdcourse-luc.js` | Verification `Workflow` script. Pipelines over the current phase's chapters through both examiners + Justin + Alex. Carries in-file `CHAPTERS[n].content` + `KNOWLEDGE_BY_CHAPTER`, kept in sync with the PDF. | ✅ committed (like `storm.js`) |
| `docs/superpowers/specs/2026-07-07-sdcourse-luc-dual-lens-pack-design.md` | This design | ✅ |
| `output/sdcourse_luc.{html,pdf}` | Rendered pack | ❌ gitignored (`output/`) |

**Doc updates on completion:** add a row to
`docs/LEARNING_PACK_VERIFICATION_WORKFLOW.md` and to the learning-pack table in
`CLAUDE.md` so the pack is discoverable.

**Google Drive:** after Phase 4 sign-off, optionally upload via the existing
`scripts/gdrive_upload.py output/sdcourse_luc.pdf` to the Learning Packs folder
(ID `1G0h8cBj9ZXDlXXv97LAj9P0esFwyk5KH`).

## 4. Chapter structure — 23 chapters, 5 parts, 4 phases

Every chapter is **[D] dual** — both authors carry genuine, substantive
content in every chapter, not a primary voice with a token sidebar. A handful
of Luc/sdcourse topics legitimately anchor **two** chapters from a **different
angle** each time (e.g. Rate Limiting is its own algorithm topic in Ch14 but
"what gateways enforce at the edge" in Ch8) — marked with `*`. This mirrors
reuse already present elsewhere in the design (Dead Letter Queues appears in
both Ch11 and Ch15; Multi-Region Replication in both Ch2 and Ch16). Every
chapter closes with a **"Where they converge / diverge"** callout.

### Phase 1 · Part I — Design Foundations
| # | Chapter | Luc | sdcourse |
|---|---------|-----|----------|
| 1 | Quality Attributes, Trade-offs & the Production Reality Gap | Quality Attributes | Course Structure/Curriculum ("map vs shovel" gap) |
| 2 | Consistency Models: CAP, ACID vs BASE, Strong/Eventual & Multi-Region | CAP Theorem, ACID vs BASE, Strong vs Eventual Consistency | Multi-Region Replication and Distributed Consistency* |

### Phase 1 · Part II — Data, Storage & Caching
| # | Chapter | Luc | sdcourse |
|---|---------|-----|----------|
| 3 | Database Selection & Distributed Query Patterns | Database Selection, SQL vs NoSQL | Distributed Query Engine and Caching Patterns* |
| 4 | Indexing, CDC & Structured Log Data | Database Indexing, Change Data Capture (CDC) | Log Format Normalization and Serialization, Faceted Search and Multi-Dimensional Filtering* |
| 5 | Tiered Storage & Caching Economics | Database Caching Strategies, Connection Pooling | Distributed Log Storage and Tiered Architecture |
| 6 | Fast Access: Redis, Consistent Hashing & Bloom Filters | Redis, Consistent Hashing, Bloom Filters | Bloom Filters in Log Processing, Distributed Query Engine and Caching Patterns* |

### Phase 2 · Part III — Communication, APIs & Messaging
| # | Chapter | Luc | sdcourse |
|---|---------|-----|----------|
| 7 | API Architecture: REST, GraphQL, gRPC & Idempotency | REST vs GraphQL vs gRPC, REST APIs, gRPC, Idempotency in API Design | Webhook Notifications and Event Routing* |
| 8 | Gateways, Proxies & CDNs | API Gateway vs LB vs Reverse Proxy, Forward/Reverse Proxy, CDNs | Rate Limiting and Sliding Window Algorithms* (edge-enforcement angle) |
| 9 | Networking & Protocol Layers + Batching Economics | Network Protocols and Layered Debugging | Network Batching and Throughput Optimization |
| 10 | Real-Time & Async: WebSockets, Sync/Async, Webhooks | WebSockets, Synchronous vs Asynchronous Communication, Health Checks vs Heartbeats | Webhook Notifications and Event Routing* (delivery-mechanism angle), Task Scheduling and Observability* |
| 11 | Messaging & Event Streaming: EDA, Pub/Sub, Kafka | Event-Driven Architecture (EDA), Pub/Sub, Message Queues | Event-Driven Architecture and Apache Kafka, Distributed Log Parsing with Kafka, Dead Letter Queues* |
| 12 | Stream Processing & Batch: Kafka Streams, Sliding Windows, MapReduce | Synchronous vs Asynchronous Communication* (streaming-as-continuous-async angle) | Stream Processing: Kafka Streams and Sliding Windows, MapReduce for Batch Log Processing |

### Phase 3 · Part IV — Scale, Reliability & Operations
| # | Chapter | Luc | sdcourse |
|---|---------|-----|----------|
| 13 | Load Balancing, Auto-Scaling & Capacity Planning | Load Balancing Algorithms | Automated Scaling and Self-Healing Infrastructure*, Capacity Planning and Infrastructure Forecasting, Predictive Analytics and Forecasting for Logs |
| 14 | Rate Limiting & Backpressure | Rate Limiting | Rate Limiting and Sliding Window Algorithms* (algorithm angle) |
| 15 | Resilience: Circuit Breakers, DLQs, Health Checks, Backup/Recovery | Circuit Breakers, Health Checks vs Heartbeats* | Circuit Breakers and Resilience Patterns, Dead Letter Queues* (resilience angle), Backup and Recovery for Distributed Systems |
| 16 | Coordination: Leader Election, Service Discovery, Multi-Region | Service Discovery in Distributed Systems | Distributed Cluster Coordination and Leader Election*, Multi-Region Replication and Distributed Consistency* (coordination angle) |
| 17 | Observability, Incident Management & BI | Observability | Task Scheduling and Observability* (ops angle), Incident Management and Automated Incident Response*, BI Integration and Business Intelligence from Logs |

### Phase 4 · Part V — Security, Architecture & Delivery
| # | Chapter | Luc | sdcourse |
|---|---------|-----|----------|
| 18 | Authentication: JWT, OAuth, SSO | JWT Authentication, OAuth, Single Sign-On (SSO) | Incident Management and Automated Incident Response* (breach-response angle) |
| 19 | Encryption, Secrets & TLS | HTTPS and TLS | TLS Encryption and Security, Field-Level Encryption and PII Protection |
| 20 | Compliance & Data Governance | Hashing vs Encryption vs Tokenization, Password Storage Security | Automated Compliance Reporting |
| 21 | Architecture Styles: Microservices & DDD | Microservices, Domain-Driven Design (DDD) | Distributed Cluster Coordination and Leader Election* (many-instances angle) |
| 22 | Delivery & Infra: Docker/K8s, IaC, CI/CD, MCP | Docker vs Kubernetes, Infrastructure as Code (IaC), CI/CD Pipelines, Model Context Protocol (MCP) | Automated Scaling and Self-Healing Infrastructure* (infra-executes-this angle) |
| 23 | **FAANG Capstone: Decision Frameworks Under Interview Pressure** *(split out from Ch22)* | Synthesis — the reframe-then-decide method applied as a review lens across the pack's key decision points (DB selection, load balancing, consistency, API styles) | FAANG System Design Interview Preparation |

This covers the full topic inventory of both personas, with every chapter
genuinely dual.

### Per-chapter shape (same as the Spark pack)

- Chapter head (eyebrow + title + source line + italic summary)
- Topic sections (`h2`/`h3`) with body prose
- Callout boxes using existing CSS variants: `.box.s` (success/decision rule),
  `.box.n` (note), `.box.d` (definition), `.box.f` (failure/anti-pattern),
  `.box.r` (production reality / benchmark), `.box.l` (Luc lens)
- At least one comparison **table** per chapter
- At least one **inline-SVG diagram** with `Caveat`-font scribble annotations
- A **`.quote`** block carrying one verbatim line from *each* author
- A **"Where they converge / diverge"** callout
- A closing **`.recall`** active-recall question block

## 5. Verification loop (per phase)

Runs as `.claude/workflows/verify-sdcourse-luc.js` via the `Workflow` tool,
pipelining over the current phase's chapters. Two technical examiners because
every chapter is dual-voice.

### Per pass (pipeline over the phase's chapters)

```
Stage 1 — Question generation (parallel, per chapter):
   • lucsystemdesign examiner → 5 questions on the Luc-lens content
   • sdcourse examiner        → 5 questions on the sdcourse-lens content
   Each obeys its own rules: ≥2 trade-off, ≥1 "when NOT to use" / precise term,
   ≥1 WHY.

Stage 2 — Answer + audit (parallel):
   • Justin Sung (student mode) → answers ALL questions from CHAPTERS[n].content
     ONLY (no off-source knowledge, no invented citations)
   • Alex → clarity audit (confusion log + additive DEFINE/ANALOGY/BRIDGE/
     DIAGRAM/EXAMPLE/SEQUENCE requests; never asks to remove content)

Stage 3 — Scoring:
   • lucsystemdesign → accuracy + coverage on ITS questions
   • sdcourse        → accuracy + coverage on ITS questions
   • Alex audit attached to the chapter result
```

### Gate

A chapter passes only when **all four scores** are **≥9.0**:
Luc-accuracy, Luc-coverage, sdcourse-accuracy, sdcourse-coverage.

### Fix round (any chapter < 9.0)

A fix agent applies **both** examiners' gaps **and** Alex's high/medium
improvements → edits the generator's chapter HTML string → **rewrites the
matching `CHAPTERS[n].content` + `KNOWLEDGE_BY_CHAPTER`** (the sync invariant)
→ regenerate PDF → re-run from the same `scriptPath` (cached agents skip; only
touched chapters re-run).

### Final sign-off for the phase (after allPassed)

Quad-agent gate, mirroring the existing tri-agent gate:

- **lucsystemdesign** — decision-framework accuracy + "when NOT to use"
  coverage ≥9.0
- **sdcourse** — production accuracy (benchmarks, failure modes, exact
  numbers) ≥9.0
- **Justin** — pedagogy: WHY→WHAT→HOW, retrieval practice, emotional framing
  (≥6/7 criteria)
- **Alex** — no remaining BLOCKERS for a 15-year-old reader

Any reject → one sign-off fix round → phase PDF locked → commit → next phase.

### Self-contained constraint

Examiners score from their embedded persona knowledge + the chapter content
passed in-prompt. They do **not** re-read source files at verification time
(the loop runs many agents per pass; re-reading would be prohibitively slow).
The dual-lens twist: each examiner scores only the questions in its own voice;
the convergence/divergence callout is checked by both.

## 6. Build phases

Each phase is a full cycle: **write chapters → generate PDF → run verification
loop to ≥9.0 → quad-agent sign-off → commit** — before starting the next
phase. This avoids running a large verification pass against unfinished content
and keeps each pass tractable.

| Phase | Chapters | Parts |
|-------|----------|-------|
| 1 | Ch 1–6 | I + II |
| 2 | Ch 7–12 | III |
| 3 | Ch 13–17 | IV |
| 4 | Ch 18–23 | V |

The single `output/sdcourse_luc.pdf` grows each phase; the generator and
workflow accumulate chapters.

## 7. Guardrails (hard-won knowledge baked in)

1. **No Mermaid CDN.** It does not render in headless-Chrome print (confirmed
   in repo memory: "Mermaid CDN dead in headless print"). Although
   `generate_vutr_spark.py` still carries the `<script src=…mermaid…>` tag, the
   new generator omits it. All diagrams are **inline SVG** with `Caveat`-font
   scribble annotations (the Spark Ch3 GRINDE PoC approach).
2. **Sync invariant.** Every generator content edit must rewrite the matching
   `CHAPTERS[n].content` in the workflow, or scores stall silently even though
   the PDF changed (the pass-6→8 lesson from the Ben Dicken loop). Keep
   `KNOWLEDGE_BY_CHAPTER` current too.
3. **Persona files are read-only.** They are the source of truth for both
   content and scoring; we never edit them to make a chapter pass.
4. **Render before verify.** Each phase's PDF must render without Chrome errors
   ("bytes written" / "written to file") before the verification loop runs.
5. **Gitignored outputs.** `output/` is never committed; only the generator,
   workflow, spec, and doc updates are.

## 8. Success criteria

- All 23 chapters score ≥9.0 on accuracy **and** coverage from **both**
  examiners.
- Quad-agent sign-off (Luc + sdcourse + Justin + Alex) passes for every phase.
- The single `output/sdcourse_luc.pdf` renders cleanly end-to-end.
- Generator, workflow, spec, and doc/table updates committed; persona files
  untouched.

## 9. Out of scope (YAGNI)

- No new pytest module (these are content-generation scripts, consistent with
  how `generate_vutr_spark.py` / `generate_learning_pack.py` are treated).
- No new persona files or agents — all four required agents (lucsystemdesign,
  sdcourse, justin-sung, alex) already exist.
- No changes to the source persona files.
- No automated Drive upload in the workflow — it stays a manual final step.
