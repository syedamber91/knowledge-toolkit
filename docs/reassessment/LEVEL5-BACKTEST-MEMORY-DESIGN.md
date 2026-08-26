# Level 5 memory, rebuilt around document backtesting — design proposal

Written 2026-08-27. **This is a design proposal. Nothing described below has
been built.** It supersedes the core mechanism of
[`LEVEL5-AGENT-MEMORY-DESIGN.md`](LEVEL5-AGENT-MEMORY-DESIGN.md) (2026-08-26)
while keeping that document's phasing discipline and its statistical traps.

The earlier design proposed a *forward* prediction ledger: log verdicts today,
score them months later. The owner reframed it during the 2026-08-27 session:
the interesting question is not "what will happen" but **"if the framework had
looked at this company in March 2023, what would it have said, and was it any
good?"** That is a backtest, not a prediction. The word "prediction" is
retired.

That reframe removes the multi-year wait the earlier doc treated as
unavoidable — but only if point-in-time inputs can be assembled honestly.
Most of this document is about what that costs.

---

## 1. Corrections to the superseded document

Two attributions in `LEVEL5-AGENT-MEMORY-DESIGN.md` were checked against the
grounded persona corpora this session and do not hold. Both are corrected in
that file by the same commit that adds this one.

**1.1 — The "bet slip" framing and the four traps are not Jack Roberts's.**
The superseded doc presents them under the heading *"The traps (Jack Roberts,
preserved faithfully)"*. A search of `.claude/agents/jack-roberts.md` returns
nothing for "bet slip", survivorship bias, overfitting, correlation-vs-edge,
or hindsight contamination. His corpus covers AI tooling, agency sales, model
routing and design systems; it contains no stated position on statistical
rigour for investing track records. The superseded doc says this material was
*"grounded input gathered this session from the `jack-roberts` persona agent"* —
so the likely history is that an earlier session's persona agent generated it
and it was then recorded as a faithful quote.

**The four traps are retained in this document.** They are sound, standard
statistical discipline and they stand without an authority attached. Only the
attribution is removed.

**1.2 — The Nate Herk "Level 5 / Brain OS auto-ingest" warning is
unconfirmed.** The superseded doc cites it against `youtu.be/DTCyvo6cC54` as
*"verified against the captured transcript"*. The `nate-herk` agent reports no
such quote in its corpus, and flags the framing as one it cannot source. It
may be that the doc's author read a transcript the agent's corpus does not
hold. Until someone re-checks that specific video, the claim is marked
**unverified** rather than deleted.

What *is* grounded from that corpus, and is used below instead:

- *"Do not start with AI. Start with workflows."*
- *"complexity kills and simplicity scales"*
- the AI Systems Pyramid, in which the full-autonomy agent layer is
  *"almost never the right call to start off with"*
- on vector databases: *"if your data is structured and it needs exact
  retrieval… a relational database is going to be much better"*

**1.3 — Hermes Agent was evaluated as an alternative to building, and
rejected.** Considered 2026-08-27 at the owner's request. It is a
general-purpose agentic OS: cross-session memory, background tasks, MCP
connectors, model routing. Grounds for rejection:

- Jack Roberts's own tool timeline records
  `[2026-05-02] Hermes Agent — positive but limitation-flagged ("hooked into
  their roadmap, not yours")`, and he replaced it with a custom Claude-based
  build. His broader anti-lock-in position is consistent and repeated
  (*"the best AI model on the planet can be taken away from you at any time"*).
- Nothing in either corpus connects Hermes to prediction or track-record
  scoring. It is not a tool for this problem; it is a personal assistant.
- **The decisive objection is architectural.** Hermes's memory is designed to
  blend everything it knows about a user into every answer —
  *"Hermes never starts from zero"*. A backtest requires the exact opposite:
  a hard wall around what was knowable at time T. Adopting a
  blend-everything memory as the substrate for a point-in-time study would
  institutionalise trap 4 (§7) rather than defend against it.

Hermes is not ruled out as an *interface* later. It is ruled out as the
memory.

---

## 2. The blocker: `--as-of` does not constrain fundamentals

Before any backtest design, the pipeline was audited for whether it can
honestly reconstruct a past date. **It cannot, and it currently fails
silently.** Findings are from a forensic read of the soic-ladder tree at
`claude/level5-agent-memory-design-02370c`.

### 2.1 Prices are honest

`facts/prices.py` is correct and defended. The fetch window ends at `as_of`
(`prices.py:128-129`), `_resample_to_weekly` independently drops any week whose
Friday is `>= as_of` compared against the **`as_of` string, never wall clock**
(`prices.py:103`, with the reasoning stated at `prices.py:82-96`), and a third
guard drops NaN-OHLC rows before resampling (`prices.py:203`). Three redundant
guards, regression-tested at `tests/test_prices.py:128`, `:148`, `:250`. No
path was found by which a future bar can leak in.

### 2.2 Fundamentals are not, and are stamped as if they were

`_fetch_company_html(symbol)` (`soic_senses/screener_client.py:102`) takes no
date. `_BASE_URL` (`screener_client.py:23`) has no query string. **screener.in
publishes no historical-view endpoint**, so no local work makes this fetch
point-in-time.

The hazard is what happens next. `snapshot.py:486` fetches live HTML;
`snapshot.py:510` writes the derived metrics under the caller-supplied
`as_of`; `store.record_metrics` (`store.py:143-163`) records that date
verbatim; `judge --as-of <past date>` resolves them via
`store.latest_run_id` (`store.py:263-268`) and renders a confident verdict.

`as_of` is never validated against `_today()` — `_today` (`cli.py:45-46`) is
used only as a default (`cli.py:202`), never as a bound.

> Running `ladder snapshot --as-of 2025-01-15` today produces a database that
> **asserts** it is point-in-time 2025-01-15 while containing 2026 fundamentals,
> with no warning anywhere. This is worse than having no backtest capability:
> it is a backtest capability that lies.

**Recommended regardless of whether the rest of this design proceeds:** a
guard that refuses a past `--as-of` on a networked snapshot, or stamps the run
as fundamentals-contaminated. The trap is armed today.

### 2.3 Which metrics could ever be reconstructed

| Class | Metrics | Status |
|---|---|---|
| Price-derived | weekly RSI, ADX, Mansfield RS, V-Stop, EMA break | **Honest today** |
| Group A — backed by a dated table | quarterly sales/PAT growth, D/E, CFO/EBITDA, CFO/PAT, net margin, asset turnover, all four 3y trend deltas | Possible with truncation work |
| Group B — point-in-time-today scalars | **ROCE, ROE**, Stock P/E, Market Cap, Book Value, both 3Y CAGRs, PEG | **Blocked** |

Group B comes from screener's `#top-ratios` and `ranges-table` sections, which
carry single current values with no history behind them. **Two of the seven
verdict-determining gates — `capital_efficiency_gate-001` (ROCE) and
`roe_lender-001` (ROE) — are in Group B.** A partial mitigation exists but is
not wired: `#ratios` does carry an annual ROCE row, and ROE is recomputable
from `#profit-loss` + `#balance-sheet`. Both are *different quantities* from
screener's trailing scalars, so thresholds calibrated on one would not
transfer. The rulebook already flags this tension at
`rulebook/soic-ladder-rules-v1.yaml:231`.

Even a fully built Group A truncation layer has a hard horizon of roughly
**9 quarters (~2.25 years)** — the `#quarters` table holds 13 columns, and the
year-ago comparison quarter falls off the page beyond that.

### 2.4 The archive is 48 hours wide

The freezing machinery is genuinely well built — checksum divergence guard on
`(run_id, company, kind)` (`store.py:164-191`), `.tmp` + `os.replace` so the
guard runs before bytes land (`snapshot.py:499-502`), append-only by design
(`store.py:1-14`). But only **two snapshot dates exist on disk: 2026-08-20 and
2026-08-22.** Four snapshot trees, but they are re-runs of the same two days,
not a time series. `runs/` is gitignored.

Archived screener HTML is architecturally the *right* substrate for
point-in-time fundamentals. There is simply almost none of it yet. At weekly
cadence starting now, the first honest 12-month datapoint arrives in late 2027.

### 2.5 A third bias, in a different file

`universe.fetch_universe` (`universe.py:72-84`) pulls **current** NSE
constituent CSVs with no date parameter. Backtesting 2025 against the 2026
NIFTY500 membership silently excludes every company dropped since — classic
survivorship bias, independent of the screener problem, and previously
uncatalogued.

---

## 3. The reframe that makes a backtest possible now

screener.in's *page* only shows today. But the **documents it links** —
annual reports, concall transcripts, investor presentations — are dated and
immutable. The FY2023 annual report does not change.

So a point-in-time view is assemblable from documents even though it is not
assemblable from the page:

> **A company-year notebook for as-of date D contains the last four quarterly
> concall transcripts and the latest annual report published on or before D.
> Nothing else.**

Worked examples, per the owner's framing: a March 2023 view takes the trailing
four quarters plus the most recent annual report as of March 2023; an October
2024 view takes the trailing four quarters as of October 2024 plus the annual
report available by then. Repeat back five years per company.

This structure disposes of two problems §2 could not solve:

- **Publication lag** is handled by construction — a document is included only
  if it existed by D.
- **Restatement** is handled by construction — the original PDF is what
  investors actually read at the time, not a later revision.

It also enables the comparison the owner specifically asked for: what
management *said* in FY23 versus what the FY24 documents *show*. That is a
documents-against-documents check requiring no market data at all.

---

## 4. The funnel — why this is affordable

Year-notebooks are the expensive stage (five notebooks per company, each with
its own document set and query pass). They must run over the smallest
defensible set. The owner's proposed ordering, which is also cheapest-first:

```
NIFTY500  (500)
  → ladder gates            judge is offline and instant; CANDIDATE only
  → Shariah screen          last measured run: 63 in → 42 Fully Compliant
  → observation columns     re-rank survivors (observations never gate — see §8)
  → YEAR-NOTEBOOKS          only what survives
```

Every stage already exists as tooling. The cross-referencing step is built:
`scripts/ladder_table.py --companies tickers.txt` was written to filter ladder
output against an external roster such as the Shariah screen's Fully Compliant
list. The funnel is largely glue.

**Order matters for cost, not for correctness** — the gates are free relative
to a notebook pass, so they go first. This is the *"start with workflows"*
discipline applied to spend: a deterministic filter should never be replaced
by a language-model pass that costs a thousand times more to answer the same
question.

---

## 5. The yearly query set

Fourteen questions, each grounded in a lesson transcript in the Stock
Framework vault. Per project discipline, thresholds and framework content are
cited to their source file rather than stated from memory. Transcript paths
are relative to `SOIC/crash-course/tvgp-framework-checklist-course/`.

**The course itself prescribes this method.** `281225-part-2` teaches feeding
a concall into an LLM together with the trigger list and asking for a table of
which triggers fit. The pipeline below is that instruction automated and run
backwards through time.

| # | Question | Grounded in |
|---|---|---|
| 1 | Revenue growth — how much volume vs price/realisation vs mix? | `281225-part-1` (Mauboussin decomposition) |
| 2 | Margin bridge — expansion/contraction, drivers named, guided sustainable? | `281225-part-1`, `-part-2` |
| 3 | One-offs and base effect — inventory gains, one-time orders, elevated prior-year base | `281225-part-2` |
| 4 | Which taught triggers fired this year? | `281225-part-2` trigger slide |
| 5 | Capex — greenfield / brownfield / debottlenecking, CWIP, commissioning timeline | `281225-part-2` |
| 6 | Order book — opening vs closing, one-off or concentrated orders | `201225`, `281225-part-2` |
| 7 | Guidance scorecard — guided vs delivered, and what is guided next | `141225-part-1`, `-part-2`, `281225-part-1` |
| 8 | Leverage and cash — interest cost YoY, borrowings, pledges, CFO vs PAT | `281225-part-2`, `201225` Q&A |
| 9 | Working capital — receivable/inventory days, discounting, disclosure gaps | `141225-part-1` (credit-rating template) |
| 10 | Industry demand-supply as management describes it | `281225` both parts |
| 11 | Market share — gained or lost, against whom | `201225`, `281225-part-1` |
| 12 | Corporate actions — M&A, JV, demerger, promoter change, insider buying | `281225-part-2` |
| 13 | Policy exposure cited as tailwind or headwind | `141225-part-1`, `-part-2`, `201225` |
| 14 | Kill-check — margins at multi-year highs, growth rate-of-change turning, order book shrinking, guidance cut, supply flooding | `281225` both parts, `141225-part-1` |

Plus one framing rule that is not a question: state the company's seasonal
quarters first, so YoY-versus-QoQ comparisons are made correctly
(`281225-part-2`).

### 5.1 Reusing existing gems rather than writing new prompts

Reviewed on `origin/main` of the `stock_analyzer` repo, under
`projects/stock-market-analysis/gems/`. Four are directly reusable once
re-anchored to a single year:

- **`gem_timeline_p3.md` §K** — already emits exactly the "why was this year
  good or bad" answer in a strict machine format: one line per financial year,
  sentiment from a fixed enum, a causal sentence, and a mandatory citation.
  Lift the format verbatim; run it once per year-notebook instead of once
  across all years.
- **`gem_47a/b/c`** — per-year metric grid (volumes and utilisation;
  revenue/EBITDA/margins/ROCE/EPS/capex/CFO; input cost, realisation and
  spread per unit; plus one to three key events per year).
- **`gem_34a` §1-3** — sector breadth score, share-gainer ratio, and a
  five-type growth-driver taxonomy that **requires an evidence quote per
  driver**. Filings-only, therefore point-in-time safe.
- **`gem_20`** (Management Credibility Scorecard) — extracts every
  quantitative guidance item, matches it to the outcome, and scores it in
  fixed deviation bands. This is the resolution engine, but it must be split
  (§6).

**`gem_quarterly_review.md` is the only gem of roughly seventy-six carrying a
temporal scoping clause** (*"Cover ONLY the single quarter in the request
line"*). Every other gem assumes the notebook is full current history.

The output envelope should follow the existing precedent at
`gems/sample-payloads/igl_quarterly_review.json` — `schemaVersion`, a period
key, verdict plus rationale, a few numerics, highlights, and a pointer back to
the notebook that produced it — extended with `year`, `as_of_date` and a
manifest of the exact documents included.

---

## 6. Register and resolve — the heart of the memory design

`gem_20` currently extracts guidance *and* checks it in a single hindsight
pass over all transcripts at once. For a backtest that is exactly wrong: the
model sees the answer while forming the question.

The split:

- **REGISTER, in year N's notebook.** Record what management named — guidance
  items with values and horizons, and the growth triggers claimed — with the
  evidence quote. The notebook contains nothing after date D, so this pass is
  forward-blind.
- **RESOLVE, in year N+1's notebook.** Take the registered items as input and
  find what actually happened in the newer documents. Score each one.

This is the append-only discipline the SQLite store already enforces
(`store.py:1-14`), applied to claims: a registration is frozen when written,
and a resolution is a **new record referencing it**, never an edit.

`gem_timeline_p3` §H supplies a ready-made two-year-lag variant — did the
capex deliver, measured by utilisation and revenue two years after
commissioning.

**What has no rubric anywhere: qualitative triggers.** `gem_20` scores only
numeric guidance. "We will enter export markets" has no scoring method in any
existing gem. This must be written, and it is the most likely place for
motivated reasoning to enter. Proposed constraint, not yet settled: a
qualitative trigger must be registered together with the observable that would
demonstrate it, or it is not registered at all.

---

## 7. Sector movement

The owner asked specifically how sector movement is calculated and captured
over time. There are two independent measures and both should be stored, per
sector-year.

### 7.1 From filings — already built, point-in-time safe

The `sector_gem_tm_p1/p2/p3` family measures a sector purely from its
constituent companies' own documents: revenue breadth (how many peers grew),
EBITDA margin landscape, **unit-margin spread and its direction** (narrowing
is treated as a late-cycle warning), capital-cycle consensus, and a count of
capex announcements. Already year-keyed, needs no market data.

This aligns with what the course teaches independently: a real theme shows
several businesses in the sector growing together, and the inverse — a whole
sector's companies posting losses — means the theme is broken (`201225`
conclusion, `141225-part-1`).

### 7.2 From prices — small new build, reuses existing code

TVGP's own sector-rotation tool is built on **relative strength versus Nifty
500 across 13/26/52-week ranges, its rate of change, and 30-week EMA stage
analysis** (`201225`, `281225-part-1`).

soic-ladder already computes Mansfield RS and the 30-week EMA in
`facts/indicators.py`, already fetches a benchmark index under a sentinel
company code (`snapshot.py:125`, `store.py:41`), and already handles
non-`.NS` index tickers via the `is_index` flag (`prices.py:130`). Pointing
that machinery at NSE sector indices yields sector-versus-market strength,
weekly, for any past year — **honestly, because this is price data, the one
class §2.1 proved clean.**

This also fills a gap the gems cannot: `gem_50_sector_intelligence.md` expects
an injected "Sector Rotation Snapshot" giving twelve-month sector return
versus Nifty. Those tables exist only for "now" and cannot be backfilled from
the gem. Computing them from price history can.

### 7.3 Why both

Stored side by side per sector-year, they separate two things that look
identical in a single-company view: whether the company moved on its own
merits, or whether its sector carried it. That is the owner's question about
whether named growth factors "actually moved in the right direction" — a
trigger that delivered in a rising sector is weaker evidence than the same
trigger delivering in a flat one.

---

## 8. The four traps, and what each forces

Retained from the superseded document, attribution removed per §1.1. Each
maps to a concrete constraint here.

1. **Survivorship bias.** Two sources, not one. The known source: score
   WATCH and INSUFFICIENT companies, not only CANDIDATEs. The newly found
   source (§2.5): the universe CSV itself is current-membership.
   *Additionally* — and unavoidably — the funnel in §4 selects companies that
   look good **today**. Results from it describe whether the method is
   *legible*, never whether the framework *works*. That distinction must
   appear in any output this pipeline produces.
2. **Overfitting to a small sample.** The superseded doc's threshold of
   roughly one hundred closed pairs is retained as an order-of-magnitude
   guide, and anything learned beneath it is a hypothesis. Backtesting makes
   volume cheap, which makes this trap *more* dangerous, not less: it is now
   easy to generate thousands of correlated observations across five years of
   the same twenty companies and mistake them for independent evidence.
3. **Correlation versus real edge.** Every outcome is measured against a
   baseline, never in isolation. `^CRSLDX` is already fetched once per run, so
   the market baseline is nearly free; §7.2 adds the sector baseline.
4. **Hindsight and lookback contamination.** The document-notebook structure
   (§3) defends the *inputs*. It does not defend the *judge* — see §9.

---

## 9. The contamination that cannot be fully removed

**The model reading a FY2019 notebook already knows what happened in 2020.**
It was trained on it. Restricting the sources does not restrict the reader.

This cannot be eliminated. It can be reduced, and the reduction must be
designed in rather than assumed:

- Source-scoped queries only, with every answer required to cite the loaded
  documents — the discipline the `soic-shariah-screen` skill already enforces
  and verifies.
- Never state the outcome, the current price, or the current date in a query.
- Strip future references from the prompts themselves. **This is a live
  defect in the existing gems, not a hypothetical:** `gem_timeline_p3` §F.3
  hardcodes COVID (March 2020), Russia-Ukraine (February 2022) and the
  2022-23 Fed hiking cycle as reference events. Pasted into a FY2018
  year-notebook, that prompt hands the model the future in its own
  instructions. `gem_34d`'s list of "hot themes" dates the prompt the same
  way.
- Drop or externally supply the price-dependent questions. `gem_34d` §11
  signal 5 and the whole technical checklist in `gem_34e` §13 require market
  data a filings-only notebook does not contain.

An honest design states the residual: **a document backtest measures whether
the framework's reasoning is legible and internally consistent at a past
date. It does not establish that the framework would have produced those
answers in 2019.** Any stronger claim is unsupported.

---

## 10. What must actually be built

Ordered by dependency. Sizes are relative, not estimates.

| # | Item | Size | Notes |
|---|---|---|---|
| 1 | Guard against a past `--as-of` on a networked snapshot | Small | Independent of everything else; the hazard is live today (§2.2) |
| 2 | As-of document filter | Small | The dates are already extracted by the sibling scraper's `_extract_file_timestamp()`; this is a filter predicate over an existing field, not new parsing |
| 3 | Trailing-four-quarters windowing relative to a date | Small | |
| 4 | Per-company-per-year notebooks | Medium | Existing uploader keys one notebook per company; needs `(company, year)` keying, and FY19 and FY23 source sets must not mix |
| 5 | Time-fence preamble on every prompt | Medium | Sixty-plus gems; mechanical but must be complete to be worth anything |
| 6 | Register/resolve split of `gem_20` | Medium | §6 — the core of the design |
| 7 | Qualitative-trigger scoring rubric | Medium | Does not exist anywhere; highest judgment risk |
| 8 | Sector index RS per year | Small | Reuses `indicators.py`; new fetch targets only |
| 9 | Memory record schema + writer | Medium | Follows the `igl_quarterly_review.json` envelope |
| 10 | Strip future leaks from prompts (§9) | Small | Must precede any pilot, or the pilot is invalid |

**Reusable, verified this session:** `Nau-Tabaq-Stock-Investing/projects/stock-screener/`
already does screener.in authentication, ten-year annual-report fetching,
concall and presentation fetching with real per-document dates, rate limiting
with exponential backoff, resume tracking across runs, and NotebookLM upload
with source deduplication.

**Not reusable:** `Anti-Gravity/Stock Analysis Programer` is an abandoned
prototype whose analysis loop was deleted — it iterates an empty list and
writes empty summaries. Its single recorded run produced two model refusals
and one analysis that read a construction-equipment manufacturer's CSR
section and concluded the company provided emergency medical services. **The
lesson is retained even though the code is not: a small local model plus
aggressive input truncation produces confident, fluent, wrong output.** Use
NotebookLM's retrieval or a long-context model; never a truncated feed.

---

## 11. Pilot

**Two to three companies, five years each — roughly ten to fifteen
notebooks.** Not five hundred companies, and not initially a wide sweep.

Success criteria, all three required before widening:

1. The fourteen questions return answers that cite loaded sources, rather than
   general knowledge about the company.
2. A re-run reproduces the same verdicts. The `soic-shariah-screen` skill
   ships a reproducibility check for exactly this purpose, on the stated
   principle that a screen which is not reproducible is a sample, not a
   screen.
3. At least one registered trigger resolves cleanly in the following year's
   notebook — proving the §6 split works end to end on real documents.

If (1) fails, the time fence is leaking. If (2) fails, nothing downstream can
be trusted. If (3) fails, the register/resolve split needs redesign before any
scale-up.

---

## 12. Status of every claim in this document

**Decided by the owner (2026-08-26 and 2026-08-27):**
- Phase 1 before Phase 2; Phase 2 gated on sample size.
- Defer commodity/gold/silver, broader shareholding pattern, bulk and block
  deals. Proceed with promoter holding only.
- Reframe from forward predictions to document-based backtesting (2026-08-27).
- Funnel ordering: gates → Shariah → observations → year-notebooks.
- Build the memory rather than adopting Hermes Agent.

**Proposed here, needs sign-off before any build:**
- The company-year notebook definition (§3) and the funnel plumbing (§4).
- The fourteen-question yearly set (§5) and the four reused gems (§5.1).
- The register/resolve split (§6).
- Two-measure sector capture (§7).
- The build list and its ordering (§10), and the pilot scope (§11).

**Verified this session, with method:**
- Price handling is point-in-time correct — read of `prices.py` plus its
  regression tests.
- `--as-of` does not constrain fundamentals — traced from `cli.py` through
  `snapshot.py` to `store.py`.
- Only two snapshot dates exist on disk — enumerated across all five
  databases and four snapshot trees.
- Reusable scraper capabilities — read of the sibling repo's source.
- Gem inventory and the future-leak defects in `gem_timeline_p3` and
  `gem_34d` — read from `origin/main`.
- Course positions — read from vault transcripts, cited per claim in §5.

**Open / unverified:**
- Whether Group A truncation (§2.3) is worth building at all, given the
  roughly nine-quarter horizon and that two gates stay blocked regardless.
- Whether "sector moved" is settled as both measures or eventually one.
- The qualitative-trigger rubric (§6) — no design exists yet.
- The Nate Herk Level 5 quote (§1.2) — needs a re-check against the source
  video.
- Storage format and location for memory records, and whether they become
  nodes in the Level 4 knowledge graph or a separate store. Implementation-plan
  territory, deliberately not settled here.
- Whether NotebookLM remains the right engine at pilot scale, given the
  session-lifetime and prompt-size limits the `soic-shariah-screen` skill
  documents.

---

## 13. Standing constraints this design does not relax

- **This is a screen, not investment advice.** No output of this pipeline
  recommends buying, selling or holding. Several source gems contain position
  sizing and exit instructions; those sections are stripped, not adapted.
- **Observations never gate a verdict.** The funnel's observation stage
  (§4) re-ranks and prioritises. It does not reject.
- **Never state a framework threshold from memory.** Every threshold in this
  document is cited to a rulebook line, a gem file, or a lesson transcript.
- **Never echo `provenance.quote`.** Freeze rule ids, slugs and refs into
  memory records; never the licensed quote text.
- **Report failures out loud.** A company-year whose documents cannot be
  assembled is recorded as such, with the missing document named. It is never
  silently dropped, and a missing year is never treated as a neutral year.
