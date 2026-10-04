# Operating protocol and Sonnet/Opus tiering

Condensed from vault notes `agent-operating-protocol`, `model-tiering-sonnet-opus`,
`privacy-and-cost-gates`, plus this repo's `docs/JEV-MCP-SETUP.md` and the
`jev-checkpoint` skill. Citations are vault note names.

## Runbook
0. **Availability.** `ToolSearch "jev"` once, unconditionally (Jev tools are usually
   deferred). None -> one line, fall back (Laya local / code / LLM tier). Never fake
   a result. Usual causes: multi-repo cloud session (clones' `.mcp.json` unread),
   network policy blocking `api.typesafe.ai`, untrusted workspace, MCP client
   filtering env so `TYPESAFE_API_KEY` is dropped (jev-mcp-server).
1. **Classify the shape** — see `decision-matrix.md`.
2. **Pick the tool.** MCP moments per the repo skill `jev-checkpoint`: close choice
   -> `jev_decide`; claim into report/PR/commit -> `jev_verify`; before "done" ->
   `jev_review`/`jev_gate`; external content -> `jev_screen`. Any other bounded judgment:
   Jev is the default unless a Jev-first exception in SKILL.md applies (`jev-mcp-tools.md`). Without MCP: SDK/HTTP
   (`POST https://api.typesafe.ai/v1/systemone`) or Laya `laya-serve`.
3. **Design** — `question-design.md`.
4. **Fan out once.** All independent questions over one state in one request;
   13 questions gave identical answers, 12.2x cheaper, 10.0x faster
   (cb-parallel-questions; Primitives page says 11.5x/9.6x). Second request only
   if it needs the first answer to fetch data, build state, or pick options.
5. **Route on confidence** (illustrative): floor 0.5-0.6 -> human; high-stakes act
   > 0.85-0.9 else confirm; top prob < 0.60 -> uncertain; Noul 0.30-0.70 -> review;
   multi-part = min; verifier = max > 0.7; `invalid_response`/truncated never auto.
   Low Score confidence = fix the question (overlapping levels, two dimensions, thin state).
6. **Act / escalate.** High: act (code owns side effects). Medium: confirm/flag.
   Low: human, clarification, or a bigger model; in this repo, read the primary
   source yourself.
7. **Report.** Tool, verdict, confidence, action, cost if relevant. Errors reported,
   not retried. Log `response.model` (aliases move).

## Hard rules
- **Advisory only.** Never replaces repo gates (G2 cited-quote verification in
  `soic_wiki/sector_gate.py` at 80%; `verify_briefs.py`). Never edit a quote or REF
  code because Jev disagreed.
- **No retry loops**; one `jev_decide` per unchanged decision.
- **Privacy:** never send `.env`, keys, licensed/private/do-not-quote content.
- **Typed output guarantees the interface, not truth** (typesafe-agent-skill).

## Tiering (owner rule)
| Tier | Owns | Never owns |
|---|---|---|
| Sonnet | bulk reading, condensation, extraction, summarising, mechanical steps | final answers, contradiction resolution, choosing sources |
| Opus | synthesis, retrieval/routing (which notes, what order, how deep), contradiction resolution, final answers | bulk reading it can delegate |
| System One | narrow typed judgments inside either tier | prose, synthesis, reasoning |
| Code | anything exact | — |
- **A subagent cannot spawn subagents.** The main session fans out Sonnet readers in
  ONE message (parallel), then calls the Opus advisor (agent `system-one-advisor`),
  or synthesizes inline if it is already Opus.
- Why: errors compound at routing/synthesis ("the second pass can only reject what
  the wide ranking hands it" — cb-skill-suggestion); spend reasoning only where a
  cheap signal says so (cb-sde-cascade) [inference for the general rule].

### Cost/latency anchors (no Sonnet/Opus list prices in the vault)
| Model | Number | Source |
|---|---|---|
| Jev | $0.042/M input, output free; 111-114 ms; $0.000043-46 per 8-14-question call | models-and-versions, cb-consistency-* |
| Haiku 4.5 | 0.99-3.9 s; $0.0015-0.0035 per rubric call | cb-consistency-* |
| Sonnet 5 | 293x Jev cost, 195x latency per case (TypeSafe self-run) | community-guide-devto |
| Opus 4.8 reasoning | 10.4-13.9 s; $0.028-0.034 per rubric call (617-805x Jev) | cb-consistency-* |
| Opus 5 | $0.032 vs Jev $0.0002 per computer-use decision; 5.2 s vs 0.13-0.38 s | community-guide-devto |

### Hand-off format (Sonnet -> Opus)
1. Frontmatter: `title`, `kind`, `source`, `source_url`, `tags` (fixed vocab), `topics`.
2. Gist; mechanism with every number; worked examples (inputs -> outputs); numbers
   table; gotchas; related links.
3. Flag, don't resolve: contradictions quoted with location; `[inference]` on
   anything not in the source; "not stated in source" for gaps.
4. Reply to orchestrator in <200 words: files written, word counts, unplaceable or
   contradictory facts with locations.
Opus reads notes, not raw sources; spot-checks raw only for disputed numbers.

## Setup facts (repo `docs/JEV-MCP-SETUP.md`, measured 2026-09-30)
- Server `@jkudish/jev-mcp`, pinned `0.11.0` in `.mcp.json`, stdio, needs
  `TYPESAFE_API_KEY`; Node 22+ (jev-mcp-server).
- **Cloud (claude.ai/code):** (1) environment network access -> Custom -> add
  `api.typesafe.ai`, keep the default list; (2) set `TYPESAFE_API_KEY` in the
  environment's settings, never in chat (anyone using the environment can read it);
  (3) start a ONE-repo session (multi-repo sessions don't read clones' `.mcp.json`
  or hooks); (4) verify: `ToolSearch "jev"` lists `mcp__jev__*`, call `jev_decide`
  on a trivial choice, proxy status shows no `api.typesafe.ai` rejection.
- **Proxy gotcha:** Node `fetch` ignores `HTTPS_PROXY` unless
  `NODE_USE_ENV_PROXY=1` (Node >= 22.21). Symptom: "Jev provider typesafe: request
  failed" while curl works. `.mcp.json` sets it for the `jev` server.
- **Local CLI:** export the key in the shell that launches `claude`; approve the
  server once (trust prompt, or `{"enabledMcpjsonServers": ["jev"]}` in uncommitted
  `.claude/settings.local.json`); avoid `enableAllProjectMcpServers` when another
  server must stay gated; verify with `claude mcp list`, `/mcp`, one real call.
- **Hook, narrowly:** `.claude/hooks/jev_hook.py` (PostToolUse on `Bash|WebFetch`, added 2026-10-03)
  reviews a just-made commit and screens a fetched page; advisory, always exits 0, never a gate.
  No Stop/PreToolUse hook: that would send diffs to a third party every turn.
- HTTP mode of jev-mcp requires `JEV_MCP_AUTH_TOKEN` unless bound to loopback.

## Privacy and cost gates (privacy-and-cost-gates)
- Hosted routes: TypeSafe direct (not trained on customer data; ZDR enterprise
  only), OpenRouter (alpha Decisions API, extra hop), Vercel (calls in Vercel logs),
  Cloudflare. Local: Laya, Kev, code, local MiniLM.
- SDK debug logs bodies unredacted; keys never in browser JS or chat.
- Rate limits 100K tok/s + 40 req/s (docs; may change without notice); 8 workers
  already hits a shared-key limit (cb-autoresearch-feature-discovery).
- **Kill switches:** tools/key/network absent; payload has secrets; repeated
  429/529 after SDK retries; `invalid_response`/truncation; `response.model` differs
  from the version thresholds were tuned on; jaggedness-category task;
  unvalidated non-English input; operator budget exceeded.
