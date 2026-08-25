# The Stock Framework knowledge graph (Level 4)

Built 2026-08-25 against the "Stock Framework" Obsidian vault (145 files —
lectures, rules, companies, findings, errata) via `/graphify`. Outputs live
inside that vault at `graphify-out/`: `graph.html` (standalone interactive
viewer), `graph.json` (raw node/edge data), `obsidian/` (vault export), and
`GRAPH_REPORT.md` (community summary, god nodes, surprising/ambiguous edges).

"Level 4" refers to Nate Herk's "5 levels of a Claude second brain"
taxonomy (`youtu.be/DTCyvo6cC54`, captured transcript in the media vault at
`AI & Development/youtube/nate-herk-ai-automation/`). His five levels run
roughly: L1 flat notes → L2 wiki with backlinks → L3 routing/retrieval → L4
**entity-relationship knowledge graph** ("Jordan is a person, Acme is a
company, Jordan works at Acme — you can trace a relationship chain from X
back to A") → L5 (agents acting on top of the graph). Confirmed against the
transcript, not assumed: what graphify produces — typed entities as nodes,
typed relationships as edges, traceable chains — matches his L4 description
directly, not just by analogy.

## How it was generated

The graphify pipeline (`.claude/skills/graphify/SKILL.md`) has two extraction
tiers, run for this vault as follows:

1. **Detect** — walked the vault, found 145 files / ~208K words, all
   Markdown (no code files, so AST extraction contributed 0 nodes).
2. **Semantic extraction, parallelized** — split the 145 files into 7 chunks
   of ~24 files each, dispatched 7 subagents *in a single batched call* (true
   parallelism, not sequential), each reading its chunk and returning a JSON
   fragment of nodes + typed edges. Every edge is tagged `EXTRACTED` (stated
   directly in the source text), `INFERRED` (a reasonable but unstated
   connection), or `AMBIGUOUS` (uncertain — kept, not discarded, and flagged
   for review). This is the audit-trail discipline that makes the graph
   honest rather than a black box: **96% of the final 1,686 edges are
   EXTRACTED, 2% INFERRED, 2% AMBIGUOUS** — you can ask *why* any edge exists.
3. **Merge + cache** — the 7 fragments (488 nodes total after dedup) were
   combined, each file's extraction cached so a future incremental re-run
   (`--update`) only re-reads changed files.
4. **Build + cluster** — assembled into a networkx graph, then Louvain
   community detection found 15 topic clusters (e.g. "Chemical & Pharma
   Candidates," "Valuation Traps & Findings," "Errata & Exit-Layer
   Corrections") — labeled by hand from each cluster's actual member list,
   not auto-named.
5. **Export** — `graph.html` (self-contained, vis-network force-directed
   layout, click-to-inspect, community-filter checkboxes, search), the
   Obsidian vault mirror, and `GRAPH_REPORT.md` (god nodes by edge count,
   flagged surprising/ambiguous connections, isolated-node gaps).

**Known imperfection, worth stating plainly:** because extraction ran as 7
*independent* subagents rather than one pass, the same real-world rule
sometimes got minted under 2-3 slightly different node IDs (e.g.
`capital_efficiency_gate-001` vs `capital_efficiency_gate_001` vs a
longer auto-generated variant) when different chunks both touched a file
that referenced it. This didn't corrupt anything — every edge is still
individually correct — but it means a full trace on a rule sometimes has to
walk 2-3 near-duplicate nodes rather than one canonical one, as shown below.
A follow-up `dedup` pass (graphify ships one) would collapse these safely.

## How to trace with it

Two ways in, both demonstrated live this session:

- **From `graph.html`**: type a name in search, click the node, read its
  info panel (source file + every neighbor), click a neighbor to walk
  outward one hop at a time. Good for a human exploring interactively.
- **Programmatically, from `graph.json`**: it's a plain networkx
  node-link JSON (`nodes: [...]`, `links: [...]`, each link carrying
  `relation`, `confidence`, `source_file`). A script (or an agent) can load
  it and answer "what connects to X" or "is there a path from X to Y" with a
  few lines of Python — no LLM call needed for the traversal itself, only
  for interpreting what comes back. This is exactly what happened when
  tracing `capital_efficiency_gate-001` above: a `python -c` one-liner over
  `graph.json` returned every lecture that qualifies/mentions the rule, the
  company it's cited against (CARTRADE), and the reassessment finding
  (`F03`) that flags a known gap between the rule as coded and the rule as
  taught — all pulled from real edges, not re-derived from scratch.

## How this could help an autonomous stock-picking agent

The graph's real value to an agent isn't "tell me a stock is good" — nothing
here computes a verdict, and it shouldn't be asked to. Its value is as a
**grounding and retrieval layer** underneath an agent that already has to do
that work some other way (e.g. `soic_ladder`'s `judge` command, which reads
live financials and applies the rulebook's gates/observations). Four
concrete uses, each tied to something this graph already contains:

1. **Citation verification before trusting a rule.** Before an agent applies
   `capital_efficiency_gate-001` to a company, it can walk the graph to see
   *which lectures actually support this rule* and *whether any finding
   flags a problem with it* (here: F03, "dropped 'or trending toward it'").
   That's a cheap, deterministic check an agent can run before leaning on a
   rule — closing the exact gap this whole reassessment thread exists to
   close (a threshold with no memory of the sentence that qualified it).
2. **"What do we actually know about this company" in one query.** Every
   company node's edges show every lecture that cites it, every rule it's
   been checked against, and (via `claims.md`'s typed edges — `support`,
   `doubt`, `neutral`) which lectures view it favorably vs skeptically. An
   agent building a thesis on a candidate can pull this instead of
   re-reading 58 lecture transcripts cold.
3. **Sector/topic context from community membership**, not a lookup table.
   A company's cluster membership (e.g. "Chemical & Pharma Candidates")
   tells an agent what peer group and which sector-specific rules
   (`ev_to_ebitda_context-001`'s sector scoping, etc.) are actually relevant,
   without needing a separate sector-classification step.
4. **A stale/contested-rule tripwire.** The `Errata & Exit-Layer Corrections`
   cluster and the `F01`-`F12` findings are *first-class graph nodes*, wired
   directly to the rules they correct. An agent that checks "does this rule
   have an open correction attached to it?" before using it gets the same
   discipline this reassessment enforced by hand (Sonnet drafts, Fable
   adversarially re-checks) as a cheap structural query instead of a full
   review pass.

What the graph explicitly does **not** do: it doesn't fetch live
financials, doesn't run the gates, doesn't produce a CANDIDATE/WATCH/REJECT
verdict, and doesn't resolve which of two contested numbers (e.g. entry RSI
45 vs 50, both real per `entry_rsi_context-001`) is correct — those stay
human/`soic_ladder` decisions. It's the map an agent consults before or
alongside that work, not a replacement for it.
