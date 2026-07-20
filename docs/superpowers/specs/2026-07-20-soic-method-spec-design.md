# SOIC Method Spec — Design

**Date:** 2026-07-20
**Revision:** 3 (post-Fable adversarial review; empirical claims re-verified against corpus)
**Status:** Approved in shape, pending final read
**Stage:** 0 of 5 in the SOIC Investment Desk program
**Repos:** built in `SOIC_Scraper`; published into `stock_analyzer`

---

## Context — why this exists

The goal is a SOIC-persona-driven **investment desk**: sector-first, running the
full funnel from sector call → screen → shortlist → deep dive → tracked
watchlist. Too large for one spec; it decomposes into five stages. This
document specifies **stage 0 only**.

| Stage | Status in `stock_analyzer` |
|---|---|
| **0. The method itself** | **Nothing.** 563 captured lessons unmined. `gem_33-36` are a second-hand approximation. |
| **1. Sector map + sector call** (L6) | Rich plumbing, **no verdict layer**. |
| **2. Screen → shortlist** (L5) | **Zero.** No screening surface exists. |
| **3. Deep dive → verdict** (L2/L3) | Most mature: `tvgp_flow`, DCF engine, `overview_kpi` reconcile. |
| **4. Hold/buy/sell monitoring** (L4) | Inputs exist; no watchlist object, no thesis-break triggers. |

Stage 0 gates every other stage. Skipping it repeats the failure documented in
`stock_analyzer`'s `docs/reviews/POLYCAB-GEM-OUTPUTS-SOIC-REVIEW.md`.

**Note what kind of failure POLYCAB was:** "a vibes-level version of SOIC
encoded into prompts" — a **rubric**-class failure, not a threshold-class one.
Revision 3 corrects a serious imbalance in revisions 1–2, which gated the
artifact that hadn't failed and left ungated the one that had. See
*Rubric gates*.

### Why this program is worth doing at all

`poc/soic/POC_VERDICT.md` (verdict **GO**) lists among its honest limits:
*"No valuation/market data — the notebook holds company filings, not price"*
and *"No scuttlebutt / peer-node comparison."* `stock_analyzer` has exactly
those: live prices in `stock_prices`, screener.in fundamentals in
`quarterly_financials`, and a sector peer-comparison API surface.

**The POC has the method and is blind to price; the platform has the price and
is weak on method.** That complementarity is the case for the program, and it
is why `binding` (below) matters more than it looks.

`learning-vault-invest`'s CLAUDE.md already declares a Phase 2 "tracked in the
`stock_analyzer` repo" (2a: upgrade `gems/*.md`; 2b: a `/soic` analyst agent).
The five-stage desk *is* that Phase 2. Reconcile the naming during planning so
two roadmaps do not diverge.

---

## Source corpus — and its defects

`SOIC_Scraper/data/content.json` — 563 lessons, 14 courses, **~25M chars of
transcript (~6.2M tokens)** in `body_text`, plus a **~2.9M char `ai_summary`
layer**.

### Measured corpus defects (verified 2026-07-20 — these drive the design)

These are not hypothetical risks. Each was counted directly:

| Defect | Measurement | Consequence |
|---|---|---|
| ASR drops trailing consonants on the flagship metric | `ROCE` **54×** vs `ROC` **961×** | A router keyed on "ROCE" misses ~95% of the material |
| ASR mangles metric names | `pad growth` **363×** vs `PAT growth` **74×** | Same — and quotes will contain the mangled form |
| ASR corrupts digits | `"it is still 499% pad growth"` (HBL context) | **Unrecoverable from text.** 49%? 4.99%? |
| **ASR corrupts proper nouns** | One 30-second stretch: `Sinjenta` (Syngenta), `Sumitoma` then `Sumitobho` (same company, two spellings), `Pessisites India` / `pesticides India` / `India pesticides` (three) | Router lexicon cannot match company/sector names naively; entity-level claims are unreliable |
| **ASR corrupts sentence structure** | `"the bears and BASF just in my opinion are three is Satya"` — unparseable | A verbatim-quotable span can be **semantically empty**. Gate 1 would pass it |
| **Level 1 is translated, not transcribed** | Labeled Hindi; `body_text` is fluent English | A *correctly* extracted L1 quote **cannot** be heard in the audio as written |

The last three compound: degradation is not confined to digits, so `corroboration ≥ 2` is doing more work than it first appears — it is the main defence against *any* single-stream ASR artifact, numeric or not. It also raises the refuter's bar: one of its checklist items must be "is this span coherent enough to support any rule at all?"

The last one invalidated an earlier pilot criterion ("click the citation, hear
Ishmohit say it") for 51 lessons. Courses must carry a `transcript_fidelity`
flag (`verbatim` | `translated`), and ear-verification only applies to
`verbatim` courses.

**Structural property:** transcripts carry interleaved `[HH:MM:SS]` markers and
**no speaker labels**.

---

## Decisions taken

| Decision | Choice |
|---|---|
| Artifact shape | **Two-tier executable rules** (knockouts vs graded) + judgement `rubrics/*.md` |
| Coverage | Pilot L5 **+ the L6 module where screening actually lives**, then routed two-pass |
| Home repo | Mine in `SOIC_Scraper`; publish into `stock_analyzer` |
| Conflict policy | Context-scope **only when the scope distinction is itself evidence-backed**; otherwise conflict |
| Approach | Router → extractor → deterministic verifier → refuter → reconciler |

### Approach rejected, and why (revised after reading the actual wiki)

**Deriving rules from the `/learn-topic` persona wiki.** Rejected as a *rules*
source — but the original rationale was wrong and is corrected here.

**The original claim that prose synthesis destroys exact figures is
empirically false.** `learning-vault-invest`'s
`concepts/screening-filters-for-stock-selection.md` preserves P/E `< 50 or 40x`,
`>15%` sales / `20%` PAT growth, Accelya's `100 → 3600 cr`, and named cases.
Figures survived.

The real disqualifiers are narrower:

1. **Provenance stops at a file, not a timestamp** — cannot be heard.
2. **That `raw/` layer is summaries, not transcripts** — per the hub's own
   CLAUDE.md, depth gate logged gaps on **20 of 22 concepts**.
3. **Near-total absence of verbatim quotes** — Gate 1 cannot run on paraphrase.
4. **It preserves ambiguity a rule must resolve** — "P/E less than 50 **or** 40
   times."

**Consequence:** the wiki is promoted to first-class input for `rubrics/*.md`,
while `rules` still require transcript-level extraction.

> **Recorded disagreement.** The Fable review called it inconsistent to use the
> wiki as evidence for re-aiming the pilot while rejecting it as a rules
> source. This spec disagrees and keeps the redirect: the evidence used was the
> `sources:` frontmatter — a **machine-written file path emitted by the ingest
> pipeline** — not the note's prose. Trusting provenance metadata while
> distrusting paraphrase is coherent. Every other review finding was accepted.

---

## Architecture

New toolkit `src/soic_method/` in `SOIC_Scraper`. Typer CLI (`soic-method`),
Pydantic models.

```
data/content.json  (563 lessons, 25M chars)
        |
        v
[1] router.py          deterministic. no LLM.
        |              signal lexicon MUST include ASR variants:
        |              ROC/ROCE, pad/PAT, "p e"/PE, etc.
        |              applies course eligibility + transcript_fidelity tags.
        v
   candidates.jsonl    lesson_id + flagged char spans
        |
        v
[2] extract.py         LLM. reads flagged span +/- context window.
        |              returns (start, end) CHAR OFFSETS, never copied text.
        v
   raw_rules.jsonl
        |
        v
[3] verify.py          deterministic. no LLM.  THREE checks, not one:
        |                3a. offsets in range; slice is >= 40 chars
        |                3b. rule.value appears within the slice
        |                3c. slice contains a comparative token whose
        |                    direction matches rule.operator
        v
   verified.jsonl  +  rejected.jsonl (retained, calibration)
        |
        v
[4] refute.py          LLM, adversarial. ONE refuter, well-fed:
        |              gets slice + ~1500 chars either side + full rule
        |              + named failure-mode checklist.
        v
   survived.jsonl
        |
        v
[5] reconcile.py       corroboration -> scope attestation -> conflict.
        |              scope from controlled scopes.yaml ONLY.
        v
   spec bundle + conflicts.open.yaml
        |
        v
[6] publish.py  --> bundle committed into stock_analyzer configs/soic-method/
```

### Offsets, not copied quotes

**The extractor returns `(start, end)` character offsets; the verifier slices
`body_text` itself.** This is strictly better than asking for copied text:

- Fabrication becomes impossible **by construction**, not by check.
- It eliminates a rejection class revision 1 did not anticipate: extractors
  instinctively *repair* ASR while copying (`ROC`→`ROCE`, `pad`→`PAT`), which
  would fail a substring match and pollute `rejected.jsonl` — the very signal
  the spec relies on as its fabrication alarm.

### What Gate 1 does and does not do

Revisions 1–2 claimed the substring check made fabricated citations
"structurally impossible." **That was overstated and the framing was
dangerous** — it invited reviewers to under-scrutinize the refuter, where the
real risk lives.

Corrected claim: **Gate 1 prevents fabricated *strings*. It does not prevent
misattributed *meaning*.** Quote-mining survives it — negation ("people say
never buy above 40x, but that breaks when…"), reported speech ("many people
show the same to other income"), hypotheticals ("suppose ROCE is above 18%…"),
and company-specific asides quoted as universal rules.

Checks 3b and 3c exist because they convert the two most damaging silent errors
— **wrong value** and **inverted operator** — from LLM-judgement problems into
deterministic rejections. Everything else is the refuter's job, which is why
the refuter's input contract is now specified rather than left implicit.

### Stage-2 read granularity and budget

The extractor reads **flagged spans plus a bounded context window**, not whole
lessons. Whole-lesson reading would approach ~6.2M input tokens; span-plus-
window keeps the pilot in the low tens of dollars. State actual spend in the
pilot report.

---

## Output artifacts

### Two tiers of rule — because the method has two kinds

SOIC's thresholds are pedagogical anchors inside a **discretionary** method,
uttered across ~5 years of market regimes. Encoding "P/E below 50" as a hard
gate asserts precision the method never claimed. So rules split:

**Tier 1 — `knockouts.yaml`.** Things SOIC states absolutely (governance red
flags, promoter pledge, accounting fraud markers). Full rigor, execute as hard
exclusions.

```yaml
- rule_key: knockout.promoter.pledge
  tier: knockout
  kind: boolean
  assertion: "promoter pledge present"
  conviction: absolute          # absolute | strong | preference
  binding: {source: postgres, table: TBD_verify, expr: TBD_verify, status: unbound}
  citations: [...]
  corroboration: 3              # independent lessons attesting
  status: active
```

**Tier 2 — `graded.yaml`.** Everything else: ranges, not scalars; ranks and
flags, never excludes.

```yaml
- rule_key: screen.pe.ceiling
  tier: graded
  kind: range
  value: {min: 40, max: 50}     # the source genuinely teaches both
  unit: multiple
  conviction: preference
  as_of: "2021-06"              # recording period — regime matters
  scope: {business_type: capital_light}   # from scopes.yaml ONLY
  scope_attestation:
    span: [148230, 148295]
    text_hash: "sha256:..."
  binding:
    source: postgres
    table: quarterly_financials
    expr: "TBD — see gaps.md"
    status: unbound             # quarterly_financials has Sales/OP/NP/EPS/OPM%,
                                # no ROCE or P/E column. Do not assume bound.
  citations:
    - lesson_url: "https://learn.soic.in/.../lesson/123456"
      timestamp: "00:41:12"
      span: [148100, 148180]
      transcript_fidelity: verbatim
  corroboration: 2
  status: active
```

**`as_of` and `conviction` are load-bearing.** Without them, a 2021 bull-market
anchor and a 2024 one look like a contradiction when they are the same
judgement under different regimes.

**`corroboration` gates `active`.** A threshold attested in only one lesson
stays `draft` — the cheapest possible defence against a single ASR digit error
shipping as truth.

### `binding` — and the data-gap list

A rule is executable only if it resolves to a column that exists. A third
outcome beyond accept/reject: **`unbound`** — the rule is real, the quote
verifies, no data field exists.

This yields `gaps.md`: *"to execute SOIC's screen faithfully, the platform is
missing these N inputs"* — derived from the method, not guessed.

**Every `binding` in this spec is `unbound`/`TBD` on purpose.** Revision 2
carried an example binding `screen.roce.floor → quarterly_financials.roce_ttm`
marked `bound`; that column does not exist (the table holds Sales / Operating
Profit / Net Profit / EPS / OPM%). Examples are what implementers copy, so no
binding is asserted until the column inventory is verified.

### `rubrics/*.md` — judgement

`l6-sector.md`, `l5-screen.md`, `l3-valuation.md`, `l4-exit.md`. Question sets,
worked examples from real lessons, citation trails. ~8–10KB each.

#### Rubric inputs — reuse before re-deriving

| Source | What it gives | Caveat |
|---|---|---|
| `wiki/personas/soic/concepts/*.md` (22) | Mechanism-depth prose, `qc: passed` | Summary layer; depth gaps 20/22 |
| `poc/soic/soic_persona_brief_v2.md` | Voice, method, **15-point analysis-standards checklist**, from **19 full transcripts** | Hand-distilled, not gate-run |
| `poc/soic/PI_Industries_SOIC_analysis.md` | Worked end-to-end application, receipts-tagged | Single company |

The 15-point checklist is the closest thing to a ready-made rubric skeleton in
existence — start there, refine against transcript evidence.

#### Rubric gates (added revision 3)

POLYCAB was a rubric-class failure, so rubrics cannot be the ungated artifact:

- **Every checklist item and worked-example claim carries a citation line**
  (lesson + timestamp + span).
- **A 20% random sample is span-verified** exactly as rules are.
- Rubric *prose* may paraphrase freely; rubric *claims* must pin.

This makes "the human recognizes the method" an acceptance test rather than the
only line of defence.

### Bundle layout

```
soic-method/
  knockouts.yaml          tier 1 — hard
  graded.yaml             tier 2 — ranges + conviction
  rubrics/*.md            judgement, citation-gated
  scopes.yaml             controlled scope vocabulary
  rule_keys.yaml          controlled key vocabulary
  evidence.jsonl          spans, citations, corpus hashes
  rejected.jsonl          calibration signal
  conflicts.open.yaml     review queue
  gaps.md                 unbound rules
  SNAPSHOT                sha256 per lesson body_text at build time
```

Versioned by git SHA. **No semver at stage 0** — there is one consumer and it
does not exist yet.

---

## Gates

### Gate 1 — Provenance (deterministic, no LLM)

1. **Offsets valid**, slice ≥ 40 chars.
2. **`value` appears within the slice** (digits or spelled form).
3. **Comparative direction matches `operator`** — small lexicon
   (less/below/under/at most → `lte` family; above/over/at least → `gte`).
   Mismatch → reject.
4. **Timestamp resolution** — nearest *preceding* marker to `start`. On
   duplicate occurrences, first-occurrence wins, recorded explicitly.
5. **Course eligibility** (below).
6. **Corpus hash match** — the lesson's `body_text` sha256 must equal the
   `SNAPSHOT` entry. Re-captured corpus with drifted ASR **hard-fails** rather
   than silently re-pointing citations at moved audio.

### Gate 1b — Numeric corroboration (deterministic)

Any digit-bearing rule must have its value independently attested **either** in
that lesson's `ai_summary` (a second rendering of the same audio) **or** in a
second lesson. Single-stream-only values get `status: needs_audio_check` and
enter a human ear-verification queue. Thresholds are few; this is cheap.

### Course eligibility — coarse filter only

| Course | Rules-eligible | Reason |
|---|---|---|
| Levels 2–6, Crash Course | yes | solo instruction |
| Level 1 | yes, `translated` | ear-check N/A |
| Ask SOIC on Saturdays | yes | instructor answering |
| StockScans, AI masterclasses, SOIC Labs | yes | solo |
| Conversation with India's Super Investors | **no** | guest interviews |
| **Rising Stars** | **no** | confirmed guest/member presentations |
| Important Membership Updates | no | admin, no transcripts |

Recorded in `course_eligibility.yaml`. **Unclassified defaults to ineligible.**

### Module-level eligibility — course level is not enough

Verified 2026-07-20: **Level 6 contains guest-led modules despite the course
being eligible.** Of its 40 modules, at least two are guest-taught:

- `a-primer-to-saas-by-siddharth-bhandari`
- `masterclass-on-banks-nbfcs-by-digant-haria`

Bhandari also appears in the *excluded* Super Investors course. Course-level
eligibility would have admitted his rules through the Level 6 door.

Eligibility is therefore recorded at **module** granularity. A cheap first pass
exists: the capture's module slugs encode authorship as `-by-<person>`, so
candidates are mechanically greppable. **That is a routing heuristic, not a
guarantee** — a guest module named without the pattern would slip through, so
the 40 L6 module names get a one-time human classification pass, recorded in
`course_eligibility.yaml` alongside courses. It is 40 lines of judgement, once.

**None of this solves in-lesson attribution.** Eligible modules still contain
quoted third parties ("Buffett says…"), read-aloud member questions, and
consensus views described in order to disagree. That is the refuter's job — see
the checklist. Enforced at both router (cost) and verifier (guarantee).

### Gate 2 — Refute (LLM). One well-fed refuter, not three.

Three same-model refuters are **correlated, not independent** — the majority
vote largely measures sampling temperature. Budget goes to context instead.

**Refuter input contract:** the slice, **±1500 chars of surrounding
`body_text`**, the full rule object, and a checklist of named failure modes to
argue:

- negation / retraction
- reported speech or another person's view
- hypothetical or arithmetic illustration
- company-specific aside quoted as a universal rule
- read-aloud member question
- value or direction not actually supported by surrounding context

Defaults to *refuted* under uncertainty.

### Gate 3 — Scope and conflict

**Scope comes from a controlled `scopes.yaml`, never free text.** Revisions 1–2
diagnosed exactly this failure for `rule_key` — *"vocabulary drift is the
mechanism by which conflict detection quietly stops working"* — and then
committed the same error one field over. Free-text scopes never compare equal,
so every disagreement would classify as a "variant" and **zero conflicts would
ever reach the review queue.**

**Conflict is the default.** Same key + different value = conflict, *unless*
the scope distinction is itself evidence-backed: the scope inference must
return its own attesting span that passes Gate 1. Unattested scope → conflict.

This inverts the incentive. Previously "variant" was the no-friction outcome
and "conflict" cost a human, so the LLM would always find a distinguishing
context and launder a real contradiction into two happy active rules.

Third outcome: **`scope: contested`** — scope in this material is often a
continuum (business quality, cycle stage), and forcing a binary manufactures
false confidence.

**Pilot-only:** route *every* variant classification to human review once, to
measure the laundering rate. Trivial at pilot scale; the only way to know.

### Vocabulary bootstrap — an explicit phase

On a first run `rule_keys.yaml` is near-empty, so nearly everything lands
`rule_key: null, status: draft` — meaning **conflict detection would run over
an empty set and the pilot could "pass" without Gate 3 ever executing.**

Bootstrap is therefore a named phase:

1. Run extraction key-free.
2. Cluster drafts by metric vocabulary.
3. Human names clusters → commit `rule_keys.yaml`.
4. **Re-run** against the vocabulary.

Once the vocabulary is non-trivial the opposite bias appears — LLMs shoehorn
into the nearest existing key rather than emitting null. **Tripwire:** within a
key group, rules whose spans share no metric vocabulary are flagged as possible
shoehorns.

### Reconcile mechanics

- **Join key for `resolutions.yaml`: `(rule_key, sorted value set)`** —
  content-stable and quote-independent. Keying on quotes or generated ids would
  break the join on any re-run that shifts a span, silently dropping your
  accumulated judgement — the exact failure this file exists to prevent.
- **Agreement-merge:** the same threshold in 10 lessons is **one** rule with 10
  citations and `corroboration: 10`, not 10 rows.
- `resolutions.yaml` is **hand-maintained and never written by the pipeline.**

---

## Testing

Offline, no network, no LLM.

`verify.py` carries the most weight:

| Case | Expected |
|---|---|
| Valid offsets, value present, direction matches | accept |
| Offsets out of range / slice < 40 chars | reject |
| `value: 15` but slice says `18%` | **reject** (3b) |
| Slice says "less than" but `operator: gte` | **reject** (3c) |
| Corpus hash mismatch | **hard fail** |
| Duplicate occurrence | first-occurrence, recorded |

Also: router ASR-variant lexicon actually matches `ROC`/`pad growth`;
ineligible-course exclusion applied; `resolutions.yaml` survives a full re-run
**with spans shifted** (the join-key regression); agreement-merge produces one
row not ten.

---

## Pilot — scope and falsifiable criteria

### Slice

L5's 4 lessons **plus the L6 lessons backing `part-2-scalable-businesses`**.

`screening-filters-for-stock-selection.md` — the one existing wiki concept
about screening — cites a **Level 6** module, and the thresholds it surfaces
(P/E `<50 or 40x`, `>15%`/`20%` growth) trace there, not to L5.
**Course-title-driven scoping is abandoned as a heuristic** — it is precisely
the assumption this falsified.

### Criteria — each with a threshold, or it isn't a criterion

| # | Criterion | Pass condition |
|---|---|---|
| 1 | Ear-verification | **n=10, oversampling digit-bearing rules**, drawn only from `verbatim` courses. **Zero** failures tolerated. |
| 2 | Rejection rate | Reported **and** within 5–40%. Near-0% means the gates aren't binding; >40% means extraction is broken. |
| 3 | Gate 3 exercised | **≥1 seeded synthetic conflict** flows end-to-end into `conflicts.open.yaml`. Otherwise the conflict machinery ships untested. |
| 4 | Attribution | **Zero** rules sourced from ineligible courses. Mechanical. |
| 5 | Bindings | Bound/unbound split reported; `gaps.md` non-empty. |
| 6 | Acceptance (not a criterion) | Human reads `l5-screen.md` and recognizes the method. Subjective by design — the final gate, not the only one. |

Note #1's revision: an n=5 random sample has weak power (at a 20% bad-rule
rate, all five pass ~33% of the time) and would have been impossible on
translated lessons.

### An outcome that looks like failure but isn't

If the revised slice still yields few executable rules, the likely explanation
is that thresholds are **stated in passing during Ask SOIC and StockScans**
rather than taught in any course module. That is a finding about where the
method lives, and it raises the value of the routing pass. Report it as a
result; do not retry until the number looks better.

---

## Access — sources and how to read them

### iCloud: now readable locally, but not a dependency

Originally blocked: `~/Library/Mobile Documents/...` returned **EPERM** (not
EACCES) via Bash, Bash-with-sandbox-disabled, and the Read tool — ruling out
POSIX permissions and the Claude Code sandbox, and confirming **macOS TCC**.
Full Disk Access was granted to `/Applications/Claude.app` on 2026-07-20 and
the iCloud vaults are now readable.

**This does not change the data plan, and the pipeline must not depend on it.**
A local FDA grant is meaningless in sandboxed, remote, headless and cloud
sessions — which is where this pipeline will often run.

### Canonical source: `data/content.json` (unchanged)

Verified 2026-07-20: the `Stock Market Vault` transcripts are a **derived view
of `content.json`, byte-identical** (26,618 vs 26,619 chars on the compared
lesson — a trailing newline). The vault is built *from* the capture by
`soic_toolkit build_vault`.

So the vault offers **no fidelity gain** and is not an alternative source. It
remains useful for two narrow purposes:

- **Human browsing** of the corpus in Obsidian.
- **Module-name inspection** — its per-module directory slugs are what surfaced
  the guest-module problem above.

### Wiki: read via `gh`

```bash
gh api "repos/syedamber91/learning-vault-invest/git/trees/HEAD?recursive=1" \
  --jq '.tree[] | select(.type=="blob") | .path'
gh api "repos/syedamber91/learning-vault-invest/contents/<path>" \
  --jq '.content' | base64 -d
```

Portable across every execution environment; prefer it over the local clone.

---

## Out of scope for stage 0

- Screening UI/API (stage 2), sector verdict logic (stage 1), changes to
  `tvgp_flow`/`dcf_engine`/`overview_kpi` (stage 3), watchlist objects (stage 4)
- Full-corpus extraction — gated on pilot outcome
- Parallel multi-agent fan-out — requires separate explicit authorization

## Open items

- **Column inventory in `stock_analyzer` is unverified.** Every `binding` is
  `unbound`/`TBD` until it is. This determines the real bound/unbound ratio and
  the whole content of `gaps.md`.
- The wiki's 22 concepts carry logged depth gaps on 20. If rubric drafting hits
  them, the fix is per-concept re-synthesis against transcript excerpts —
  available, not scheduled.
- `transcript_fidelity` is confirmed for L1 (`translated`) and L6 (`verbatim`,
  though heavily ASR-degraded) by inspection. The other 12 courses are
  **assumed** `verbatim` and should be spot-checked before the ear-verification
  criterion is trusted.
- The 40 Level-6 module names need their one-time human eligibility pass. Two
  guest modules are already identified; the pass is to catch any named without
  the `-by-<person>` pattern.
