# SOIC Method Spec — Design

**Date:** 2026-07-20
**Status:** Approved, ready for planning
**Stage:** 0 of 5 in the SOIC Investment Desk program
**Repos:** built in `SOIC_Scraper`; published into `stock_analyzer`

---

## Context — why this exists

The goal is a SOIC-persona-driven **investment desk**: sector-first, running the
full funnel from sector call → screen → shortlist → deep dive → tracked
watchlist. That is far too large for one spec, so it decomposes into five
stages. This document specifies **stage 0 only**.

### The five stages, and what already exists

| Stage | Status in `stock_analyzer` |
|---|---|
| **0. The method itself** — what SOIC actually teaches | **Nothing.** 563 captured lessons unmined. `gem_33-36` are a second-hand approximation. |
| **1. Sector map + sector call** (SOIC L6) | Rich plumbing (cycle, peer-comparison, competitive-intel, time-machine, sector gems), **no verdict layer**. |
| **2. Screen → shortlist** (L5) | **Zero.** No screening surface exists anywhere. |
| **3. Deep dive → verdict** (L2/L3) | Most mature: `tvgp_flow`, DCF engine, `overview_kpi` reconcile. Fidelity is the open question, not existence. |
| **4. Hold/buy/sell monitoring** (L4) | Inputs exist (quarterly board, daily `price_recompute`, company intel). No watchlist object, no thesis-break triggers. |

Stage 0 gates every other stage. Skipping it repeats the failure documented in
`stock_analyzer`'s `docs/reviews/POLYCAB-GEM-OUTPUTS-SOIC-REVIEW.md`: a
vibes-level version of SOIC encoded into prompts, discovered only downstream
when the pillars contradict each other (`gem_35` printed five different current
P/E values, three verdicts, and two mutually exclusive peak-earnings calls in a
single document).

### Source corpus

`SOIC_Scraper/data/content.json` — 563 lessons, 14 courses, **~25M chars of
transcript (~6.2M tokens)** in `body_text`, plus a **~2.9M char `ai_summary`
layer** (one per lesson).

| Course | Lessons w/ body | Body chars |
|---|---|---|
| Level 6 — Become a Sectoral Expert | 116 | 7,326,899 |
| SOIC Market Signals + StockScans | 53 | 3,281,921 |
| Conversation with India's Super Investors | 25 | 2,957,210 |
| Crash Course | 25 | 2,565,960 |
| Level 2 — Intensive (Investing from Scratch) | 51 | 2,079,330 |
| L4 — When to Hold, Buy & Sell using Technicals | 19 | 1,436,642 |
| Ask SOIC on Saturdays | 27 | 1,425,580 |
| Level 1 — Financial Literacy (Hindi) | 51 | 1,274,038 |
| Level 3 — How to Value a Company | 9 | 855,064 |
| Rising Stars | 45 | 750,851 |
| Masterclass on Investing Using AI | 7 | 464,171 |
| Level 5 — How to Screen & Filter Epic Stocks | 4 | 278,314 |
| SOIC Labs: AI-Powered Investor | 5 | 229,601 |

**Critical corpus property:** transcripts are raw ASR with interleaved
`[HH:MM:SS]` markers and **no speaker labels**. In a guest-interview lesson
there is no mechanical way to attribute a sentence to Ishmohit rather than the
guest. This drives a hard exclusion rule (see Gate 1.4).

---

## Decisions taken

| Decision | Choice | Rationale |
|---|---|---|
| Artifact shape | **Both, cleanly separated** — executable `rules.yaml` + judgement `rubrics/*.md` | Code executes thresholds; an LLM applies rubrics. One format cannot serve both. |
| Coverage | **Pilot Level 5, then routed two-pass over the full corpus** | Validates format and gates on 278k chars before spending on 25M. |
| Home repo | **Mine in `SOIC_Scraper`, publish into `stock_analyzer`** | Corpus and persona tooling already live in the former; the screener that executes rules lives in the latter. |
| Conflict policy | **Context-scope first, surface true conflicts for human review** | Prevents "scoped variant" and "genuine contradiction" collapsing into each other. |
| Approach | **Router → extractor → deterministic verifier → refuter** | The verifier is a non-LLM gate that makes fabricated citations structurally impossible. |

### Approach rejected, and why

**Reusing the `/learn-topic` persona-wiki pipeline and deriving rules from the
wiki.** A persona wiki is a prose synthesis of transcripts. Extracting
`ROCE > 18%` from a concept note that already paraphrased a lesson is two lossy
hops from source, and exact figures are the first casualty of prose
abstraction. Figures are the entire point of `rules.yaml`. The wiki approach is
correct for teaching a human and wrong for machine-executable thresholds.

---

## Architecture

New toolkit `src/soic_method/` in `SOIC_Scraper`, alongside the existing five.
Follows repo conventions: Typer CLI (`soic-method`), Pydantic models,
`media_core` where applicable.

```
data/content.json  (563 lessons, 25M chars)
        |
        v
[1] router.py          deterministic. no LLM.
        |              scans ai_summary + body_text for rule signals:
        |              numerals w/ units (%, x, cr), comparatives (above/below/
        |              at least), imperatives (never/always/avoid/only if).
        |              applies format-eligibility exclusions.
        v
   candidates.jsonl    lesson_id + why-flagged + char spans
        |
        v
[2] extract.py         LLM. reads ONLY candidate spans' full body_text.
        |              emits Rule objects, each REQUIRING a verbatim quote
        |              copied exactly from body_text.
        v
   raw_rules.jsonl
        |
        v
[3] verify.py          deterministic. no LLM.   <-- load-bearing gate
        |              quote must be a literal substring of that lesson's
        |              normalized body_text. no match -> REJECT.
        |              resolves [HH:MM:SS] -> citation URL + timestamp.
        v
   verified.jsonl  +  rejected.jsonl (retained, calibration signal)
        |
        v
[4] refute.py          LLM, adversarial. "argue this quote does NOT support
        |              this rule." defaults to refuted under uncertainty.
        |              tiered: knockouts/thresholds = 3 refuters, majority kill.
        |              soft/rubric material = 1 refuter.
        v
   survived.jsonl
        |
        v
[5] reconcile.py       deterministic grouping + conflict detection.
        |              LLM used ONLY for scope inference.
        |              applies hand-maintained resolutions.yaml.
        v
   spec bundle  +  conflicts.open.yaml
        |
        v
[6] publish.py  --> versioned bundle committed into stock_analyzer
                    at configs/soic-method/
```

### Two load-bearing properties

**Stages 1, 3 and 5 contain no LLM.** Routing, quote verification and conflict
detection are pure code. The LLM does only the two things it is good at —
reading prose to propose a rule, and arguing against one. Every claim it makes
passes through a deterministic check it cannot talk past.

**`rejected.jsonl` is retained.** If the extractor begins fabricating quotes,
the rejection rate is the signal, measurable per-run — rather than something
discovered downstream in a POLYCAB-style audit months later.

### Publish target

`configs/soic-method/` in `stock_analyzer`. Per that repo's `CLAUDE.md`,
`configs/` is **bind-mounted** into the orchestrator, so a spec update lands on
the next cron tick with no image rebuild. Anything baked into the image would
make every threshold change a ~6-minute Rebuild Orchestrator cycle.

---

## Output artifacts

### `rules.yaml` — executable

```yaml
- rule_key: screen.roce.floor
  stage: screen                    # screen | sector | valuation | exit
  kind: threshold                  # threshold | boolean | ranking | knockout
  operator: gte
  value: 18
  unit: percent
  scope:                           # null = universal
    business_type: capital_light
  binding:
    source: postgres
    table: quarterly_financials
    expr: "roce_ttm"
    status: bound                  # bound | unbound | derived
  citations:
    - lesson_url: "https://learn.soic.in/.../lesson/123456"
      timestamp: "00:41:12"
      quote: "we don't even look at a business doing less than 18% ROCE"
  status: active                   # active | conflicted | unbound | draft
  spec_version: "0.1.0"
```

#### `rule_key` convention

`rule_key` is the join key for conflict detection, so an unconstrained format
breaks Gate 3 silently — two extractions emitting `screen.roce.floor` and
`roce_minimum` for the same rule would never be compared, and a genuine
contradiction would ship as two happy independent rules.

Format is `<stage>.<metric>.<qualifier>`, lowercase, dot-separated, drawn from
a **checked-in controlled vocabulary** (`rule_keys.yaml`). The extractor
selects from that vocabulary; it does not invent keys. A rule that fits no
existing key is emitted with `rule_key: null` and `status: draft`, and lands in
a `new_keys.md` queue for a human to name and add to the vocabulary.

This deliberately trades extractor autonomy for join integrity — vocabulary
drift is the mechanism by which conflict detection quietly stops working.

**`binding` is the field doing the real work.** A rule is executable only if it
resolves to a column that exists in the stack. Extraction therefore has a third
outcome beyond accept/reject: **`unbound`** — SOIC states the rule, the quote
verifies, but no data field exists to run it against.

This yields an unplanned but valuable deliverable: **a ranked data-gap list**
(`gaps.md`). "To execute SOIC's screen faithfully, the platform is missing
these N inputs" — derived from the method rather than guessed. Given
`market_cap_updater` is already blocked on NSE and shares-outstanding is a
known open problem, knowing which gaps bind a *real* rule is decision-useful.

### `rubrics/*.md` — judgement

One per stage: `l6-sector.md`, `l5-screen.md`, `l3-valuation.md`,
`l4-exit.md`. Each holds the question set an analyst walks, **worked examples
lifted from actual lessons** (the L6 sector webinars earn their keep here — a
real sector reasoned end to end beats any abstract checklist), and its citation
trail. Capped at ~8–10KB each so they compose without blowing context.

### Bundle layout

```
soic-method/
  VERSION                 semver; bump on any rule change
  rules.yaml              executable
  rubrics/*.md            judgement
  evidence.jsonl          every surviving quote, full provenance
  rejected.jsonl          failed the verifier — calibration signal
  conflicts.open.yaml     review queue
  gaps.md                 unbound rules = the data-gap list
```

Versioned so a stage-2 screener can pin a spec version and diffs between runs
are legible.

---

## Gates

### Gate 1 — Provenance (deterministic, no LLM). All four must pass.

1. **Literal substring match.** Timestamp markers are interleaved mid-sentence,
   so quote and `body_text` are normalized identically — strip `[HH:MM:SS]`,
   collapse whitespace — while retaining an offset map. No match, no rule.
2. **Minimum quote length (~40 chars).** Without this a fragment like `"18%"`
   trivially matches somewhere in a 300KB transcript and the gate becomes
   decorative.
3. **Timestamp resolution.** Offset maps back to the nearest *preceding*
   marker → citation URL + timestamp that can be clicked and heard.
4. **Format eligibility.** Because transcripts carry no speaker labels,
   **interview-format lessons cannot source a rule.**

Gate 1.4 is the one that would otherwise quietly poison the spec: a guest's
macro call encoded as SOIC method, carrying a perfectly valid-looking citation.

#### Where exclusion is enforced

**Both places, deliberately.** `router.py` skips ineligible lessons so they are
never sent to the extractor (cost), and `verify.py` independently rejects any
rule whose source lesson is ineligible (safety). The router is an optimization;
the verifier is the guarantee. A router bug must not be able to leak a guest
quote into `rules.yaml`.

#### Course eligibility classification

Eligibility is a per-course property recorded in a checked-in
`course_eligibility.yaml`, not inferred at runtime:

| Course | Eligible for `rules.yaml` | Reason |
|---|---|---|
| Levels 1–6, Crash Course | yes | Ishmohit teaching solo |
| Ask SOIC on Saturdays | yes | Ishmohit answering |
| SOIC Market Signals + StockScans | yes | solo format |
| Masterclass on Investing Using AI, SOIC Labs | yes | solo format |
| Conversation with India's Super Investors | **no** | guest interviews, unattributable |
| Rising Stars | **unclassified — defaults to no** | format unverified |
| Important Membership Updates | **no** | no transcripts, admin content |

**Unclassified defaults to ineligible.** A course is promoted to eligible only
after its format is confirmed by inspection. This makes the failure mode "we
under-collected from a solo course" rather than "we attributed a guest's rule
to SOIC" — the first is recoverable by reclassifying, the second corrupts the
spec silently.

### Gate 2 — Adversarial refute (LLM), tiered by stakes

Knockouts and screen thresholds get **3 independent refuters, killed on
majority**. Soft/rubric material gets 1. Every refuter defaults to *refuted*
under uncertainty, so ambiguity fails closed.

### Gate 3 — Conflict and scope

Grouping and conflict detection are deterministic (group by `rule_key`, compare
value + scope tuple). **Only scope inference uses an LLM**, since it requires
reading surrounding context.

- same key + different value + **same** scope → **conflict** → review queue
- same key + different value + **different** scope → **variants**, no conflict

### The review queue

Conflicts render to `conflicts.md` with both quotes side by side, lesson links,
and a recommended resolution. The human settles them by editing
**`resolutions.yaml`**.

**`resolutions.yaml` is hand-maintained, versioned, and never written by the
pipeline.** Re-running extraction re-derives everything else from scratch but
applies existing resolutions on top. If resolutions lived in generated output,
every re-run would silently discard accumulated judgement and re-runs would
stop being trustworthy.

---

## Testing

Unit tests, no network and no LLM — matching the repo's existing convention
that extraction/parsing/vault tests run offline.

`verify.py` carries the most test weight:

| Case | Expected |
|---|---|
| Exact quote present | accept |
| Quote spanning interleaved `[HH:MM:SS]` markers | normalizes, accepts |
| Fabricated quote | **reject** |
| Quote below min length | reject |
| Quote real but from a *different* lesson | **reject** (cross-lesson leakage) |
| Timestamp resolution | picks nearest *preceding* marker |

Also:

- `router.py` — signal detection on a fixture; interview-format exclusion
  actually applied.
- `reconcile.py` — conflict vs. variant classification; and specifically that
  **`resolutions.yaml` survives a full re-run** (the most likely regression to
  sneak in later).

---

## Pilot success criteria (Level 5)

Deliberately **not** a rule count — a target number pressures the extractor
toward quantity.

1. **Sample verifiable by ear.** Pick 5 rules at random, click the citation,
   hear Ishmohit say it. Any failure means the gate is broken and nothing
   downstream is trustworthy.
2. **`l5-screen.md` is recognizable.** The human reads it and recognizes the
   method they actually learned. This is the real acceptance test; no automated
   metric substitutes.
3. **Rejection rate reported**, establishing a baseline to watch as coverage
   scales to the full corpus.
4. **Zero rules sourced from interview-format lessons** — mechanically
   checkable.
5. **Bound/unbound split reported**, producing a first data-gap list.

### A pilot outcome that looks like failure but isn't

Level 5 is only 4 lessons. If it yields very few executable rules, the most
likely explanation is that **the real thresholds are not taught in the
screening course — they are stated in passing during Ask SOIC and StockScans.**
That is a finding about where the method actually lives, and it raises the
value of the routing pass rather than undermining it. It will be reported as a
result, not retried until the number looks better.

---

## Out of scope for stage 0

- Any screening UI or API surface (stage 2)
- Sector verdict logic (stage 1)
- Changes to `tvgp_flow`, `dcf_engine`, or `overview_kpi` (stage 3)
- Watchlist objects or thesis-break triggers (stage 4)
- Full-corpus extraction — gated on pilot outcome
- Parallel multi-agent fan-out — requires separate explicit authorization

## Open items carried forward

- The Phase-1 SOIC persona wiki (`wiki/personas/soic/`, 1 topic + 22 concepts)
  lives in an iCloud Obsidian vault unreadable from the sandbox. Its current
  state needs confirming; it may supply rubric material but is not a rules
  source (see rejected approach).
- Binding targets in `stock_analyzer` are assumed from `CLAUDE.md`
  documentation; the concrete column inventory needs verifying during
  implementation, and will determine the real bound/unbound ratio.
