# Level 5 agent memory — design proposal

Written 2026-08-26. **This is a design proposal, not an implementation** —
nothing described below has been built. It follows on from
[`LEVEL4-KNOWLEDGE-GRAPH.md`](LEVEL4-KNOWLEDGE-GRAPH.md) (the graphify
knowledge graph over the "Stock Framework" vault: 488 nodes, 1,686
typed/confidence-tagged edges spanning the lecture transcripts, the
soic-ladder rulebook, and the tracked companies with their
CANDIDATE/WATCH/REJECT verdicts). Level 4 gave an agent a map to consult;
this doc designs the memory that would let an agent *learn from its own
track record* while consulting it.

## What "Level 5" means here — and Nate Herk's own warning about it

In the same taxonomy Level 4 came from ("Every Level of a Claude Second
Brain Explained", `youtu.be/DTCyvo6cC54`, verified against the captured
transcript), Level 5 is making the second brain "super autonomous" — an
always-on "Brain OS", constantly syncing and refreshing memories. Two
things he says about it matter more than the definition:

- **He explicitly does not call it the best level, and doesn't run it
  himself.** His stated goal is finding the *lowest* level that solves your
  actual pain, not maximizing levels.
- **His stated reason:** auto-ingesting too much context can do more harm
  than good — the same failure mode as an overlong context window degrading
  a model.

So this design is deliberately not "make everything autonomous." It targets
the two specific things the current system (Level 4 graph + `soic_ladder`
gates) genuinely cannot do:

1. **Historical backtracking.** The system produces verdicts but remembers
   nothing about whether they were *right*. There is no record joining a
   past CANDIDATE call to what the stock actually did afterward, so nothing
   can ever be learned from the track record.
2. **Forward-looking models.** The gates are static filters over current
   financials. Nothing projects which companies are *likely future* growth
   stocks — pass/fail today is all there is.

## The three layers of agent memory, as a lens over the phases

A useful framing (paraphrased from a short instructional video by Romi
Patel) splits agent memory into three layers: **episodic** memory is a log
of specific things that happened; **semantic** memory is facts distilled
across many episodes into a standing model of how something works; and
**procedural** memory saves the exact steps of a solved messy case as a
reusable playbook, so the agent doesn't reason from scratch the next time
the same shape of problem appears.

Mapped onto this project:

| Layer | What it is here | Status in this design |
|---|---|---|
| Episodic | The Phase 1 prediction ledger — each verdict logged with its evidence | Proposed, buildable now |
| Semantic | The quarterly pattern review — which gates/observations correlated with good outcomes | Proposed, buildable now (human-reviewed) |
| Procedural | Saved analysis playbooks per sector/situation | **New proposal in this doc ("Phase 1.5") — not previously discussed, not decided** |

## Phase 1 (buildable now): ledger, one cron, one human-reviewed diff

This phase is deliberately unglamorous, matching both Nate Herk's caution
against overbuilding and the grounded input gathered this session from the
`jack-roberts` persona agent. Jack's framing: the minimal honest unit of
memory is a **prediction record — a "bet slip", not a diary entry**:

```
prediction:  { company, verdict, timestamp,
               exact gates/observations that produced it }
outcome:     { outcome, outcome_timestamp,
               measured_against_baseline }   # joined later
```

Three components, and only three:

1. **An append-only prediction ledger.** Every verdict `soic_ladder`'s
   judge emits gets a row at emission time — including REJECTs and WATCHes,
   not just CANDIDATEs (see the survivorship-bias trap below). Each row
   cites the specific Level-4 graph nodes (rules, observations, lecture
   citations) that produced the verdict, so the ledger *extends the
   knowledge graph* rather than growing up beside it as a disconnected
   system. A closed prediction/outcome pair becomes a traceable chain:
   lecture → rule → verdict → outcome.
2. **A monthly outcome-scoring cron.** Checks any prediction past its
   holding window and appends the real outcome. Monthly, not more often —
   per Jack, checking more frequently adds noise, not signal.
3. **A quarterly, human-reviewed rule-diff proposal.** Reads closed
   pairs, asks which gates/observations correlated with good outcomes, and
   proposes a rulebook diff for human approval — reusing this project's
   existing `evolve-frameworks` pattern (propose-only, preview file, never
   auto-applied). **The agent must never grade and rewrite its own rulebook
   unsupervised.** This is the same discipline the framework-evolution
   pipeline already enforces, applied to a new evidence source.

What Phase 1 explicitly is **not**: a self-updating rulebook, daily
re-scoring, or any autonomous rule-rewriting. Those are the overbuilt
versions this design rejects.

## Phase 1.5 (proposed here, not previously agreed): procedural playbooks

The episodic and semantic layers fall out of Phase 1 naturally. The
procedural layer does not — it is a genuinely new third piece, named here
for the first time, and it should be treated as **a proposal for the owner
to accept or reject, not something already decided**.

The idea: when the quarterly review (or ordinary use) finds a repeatable,
effective analysis recipe for a specific sector or situation — e.g. a
sequence of checks that reliably separates good from bad calls in one
sector — that recipe gets saved as its own reusable playbook note rather
than being re-derived from scratch each time. The vault already has a
natural home for such notes (the same index + log + cross-links pattern
every vault builder implements), but the trigger, format, and admission
bar for a playbook are all open design questions. Deliberately unspecified
here; specifying them before Phase 1 produces any evidence would be
designing on air.

## Phase 2 (gated — does not exist until the data does)

Once the ledger holds **~100+ closed prediction/outcome pairs**, train a
forward-looking model on the ledger's labeled outcomes plus the graph's
structured features, to score current CANDIDATEs by likely forward
performance rather than binary gate pass/fail. Constraints already agreed:

- A **simple statistical model, not a black box** — the whole system's
  discipline is that every claim traces to evidence, and an unexplainable
  scorer would break that.
- **Before the ~100-pair threshold is crossed, this phase does not honestly
  exist yet.** Do not describe it as buildable today; at monthly outcome
  scoring, accumulating 100 closed pairs will take real calendar time, and
  that is the point — the gate is data volume, not engineering effort.

## The traps (Jack Roberts, preserved faithfully)

Four failure modes a stock-picking learning loop walks into by default.
Each one shaped a concrete design choice above:

1. **Survivorship bias.** Log REJECTs and WATCHes, not just winners —
   otherwise you never learn what a bad call looks like. (Hence: every
   verdict gets a ledger row, not just CANDIDATEs.)
2. **Overfitting to a small sample.** Don't trust anything learned from
   under ~100 closed outcomes — and even past that threshold, treat it as
   a hypothesis, not a fact. (Hence: the Phase 2 gate, and the quarterly
   review producing *proposals*, never automatic edits.)
3. **Correlation vs. real edge.** Markets are regime-dependent; always
   compare against a dumb index-return baseline before crediting the
   rulebook for anything. (Hence: `measured_against_baseline` is a
   required field of the outcome record, not an optional analysis step.)
4. **Hindsight/lookback contamination.** Outcome data must never leak back
   into the gates that produced the original prediction — timestamp and
   gate everything hard. (Hence: the ledger is append-only, predictions
   are frozen at emission time with the exact rule versions that produced
   them, and outcomes are joined as separate rows, never edits.)

## Dependency check: what signals the gates can even see

A prediction ledger is only as good as the features frozen into each row,
so the current metric coverage was checked this session against the
signals SOIC actually teaches. Findings, and the owner's decision on them
(already made — recorded here as final, not up for re-litigation):

- **`soic-ladder/rulebook/vendor/metric-registry.yaml` tracks zero of:**
  commodity/gold/silver signals, delivery %, volume, shareholding pattern,
  bulk deals, block deals, promoter holding.
- **One gap is real and in-scope: promoter holding** (and its
  quarter-over-quarter change). It is a stated SOIC screening criterion in
  the FESTF crash-course lecture
  (`crash-course/mastering-fundamental-analysis/151224-class-4-how-to-filter-epic-stocks-transcript.md`,
  timestamp 01:28:37–01:29:56) — a lecture the rulebook *already cites*
  for its CANSLIM and capital-efficiency rules. The transcript frames it
  as an idea-sourcing/conviction signal (promoters/FIIs/DIIs increasing
  their stake), with an explicit caution that the *cause* matters: an
  increase via preferential allotment/warrant issuance is not the same
  bullish signal as one via open-market buying. It should land as an
  **OBSERVATION, not a hard gate** — the same shape as the existing
  `capital_efficiency-001` and `cash_conversion-001` observations.
- **The fetch-side gap is small.** `src/soic_senses/screener_client.py`
  (this repo, installed editably into soic-ladder's venv) has no
  shareholding-pattern parsing yet, but it already has a generic
  `parse_statement_section(html, section_id)` used for the
  profit-loss/balance-sheet/cash-flow/ratios/quarters sections.
  screener.in's shareholding-pattern table is *very likely* parseable by
  that same function once wired in — a cheap-reuse case like the earlier
  `price_to_book` addition, not a new-data-source case like
  `ev_to_ebitda`. **This has not been verified against real screener.in
  HTML.** Confirming that the shareholding table has a section id the
  existing parser handles is the next concrete step, and it is unverified
  until someone runs it.
- **The other signals are real but out of corpus.** A scan of the broader
  ~1,115-file "Stock Market Vault" (SOIC's full teaching library, far
  larger than the 58-lecture corpus Level 4 and the rulebook are built
  from) found extensive discussion — commodity (166 files), gold (189),
  crude oil (41), silver (46), shareholding pattern broadly (22), block
  deals (11), bulk deals (10) — but almost entirely *outside* the current
  58-lecture scope: Level 6 sector deep-dives, market-signals/stockscans
  shows, live Q&A.
- **Owner's decision (final):** defer commodity/gold/silver, the broader
  shareholding-pattern signal, and bulk/block deals — each needs a
  corpus-expansion decision (pulling in that much larger content set) that
  is out of scope for this design. **Proceed with promoter-holding only**,
  since the underlying data source (screener.in) already has it on the
  page — the gap is purely that this project's own fetch code hasn't
  scraped it yet.

## A candidate accelerator for promoter holding: Chartink (checked, not adopted)

Chartink was investigated live this session as a possible faster path to the
promoter-holding gap above. Findings, kept separate from the dependency
check because nothing here changes its conclusion:

- **Confirmed real, filterable fields on chartink.com**: a "Shareholding
  pattern" category (promoter holding, foreign-promoter %, encumbered-holding
  %) and delivery percentage/volume, the latter with several ready-made
  community scan templates already built.
- **No official Chartink API.** Checked directly on their site — no
  "API"/"Developer" link anywhere in the nav or footer.
- **An unofficial third-party tool exists**: `shahparthiv/chartink-mcp`
  (verified real on GitHub, MIT licensed). It wraps Chartink's own internal
  `/screener/process` and `/backtest/process` endpoints — the same ones
  their web frontend calls, not a supported API. Authentication is a
  manually-copied browser session cookie (`XSRF-TOKEN`, `ci_session`), not
  an API key. It is a small, single-maintainer project (2 stars, 4 commits)
  with no stability guarantee if Chartink changes its internal endpoints.
  **Chartink's Terms of Usage did not load during this check** — whether
  this kind of automated access is even permitted remains unconfirmed.
- **The cookie-expiry problem this creates is not new to this project.**
  `src/soic_senses/notebook_preflight.py` already solves the identical
  shape of problem for NotebookLM. Its own header states the governing
  principle: minting a session needs a human-supplied cookie, and
  "pretending otherwise would just relocate the same mid-run failure into a
  background thread." It is deliberately **not an auto-refresher** — it is
  a fail-fast preflight that checks cached-token age *and* makes one cheap
  live functional call before a long job starts (age alone was found to
  lie: a token that looks fresh by age can already be dead server-side),
  and refuses to start with an error that names the exact refresh steps,
  rather than dying silently mid-run. If Chartink is ever adopted, the same
  shape applies directly — a `chartink_preflight.py`-style check before the
  monthly cron runs, refusing a dead cookie loudly and early, never
  auto-logging in.
- **Status: informational only.** This addendum adopts nothing. The
  screener.in / `parse_statement_section` path in the dependency check above
  remains the primary route scoped for promoter holding. Chartink is
  recorded here as a possible accelerator only if that path proves harder
  than expected, and any use of it is gated on the unresolved ToS question
  and the single-maintainer risk of `chartink-mcp` above.

## What's proposed here vs. what's still open

Following this project's standing discipline — a design doc must never
quietly imply something is decided when it isn't:

**Already decided (by the owner, this session — final):**
- The phased sequencing: Phase 1 first; Phase 2 gated on ~100 closed pairs.
- Defer commodity/gold/silver, broader shareholding pattern, bulk/block
  deals; proceed with promoter-holding only.

**Proposed in this doc (needs owner sign-off before any build):**
- The Phase 1 component design: ledger row schema citing Level-4 graph
  nodes; monthly cron; quarterly human-reviewed diff via the
  `evolve-frameworks` pattern.
- Promoter holding as an observation (not a gate), in the shape of
  `capital_efficiency-001` / `cash_conversion-001`.
- **Phase 1.5 procedural playbooks — entirely new here**, with trigger,
  format, and admission bar all deliberately unspecified until Phase 1
  produces evidence to design against.

**Open / unverified:**
- Whether screener.in's shareholding table actually parses via the
  existing `parse_statement_section` (next concrete step; unverified).
- The holding window per verdict type, the ledger's storage format, and
  how ledger rows are represented as graph nodes/edges — all Phase 1
  implementation-plan territory, not settled by this doc.
- Everything about Phase 2 beyond its gate and its
  simple-model/no-black-box constraint. It does not exist until the
  ledger's data does.
