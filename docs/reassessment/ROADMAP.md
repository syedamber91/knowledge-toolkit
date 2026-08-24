# Roadmap — what is built, what is next, in order

One page. Read this before starting anything.

## The two things you want

1. **Point at one company** and see how far it gets, and why it stopped.
2. **Filter Nifty 500** down to a short weekly list worth researching.

These are the **same machine at different sizes**. One company is that machine
with N=1. So we build the per-company part once and both uses share it.

---

## What already works

| Thing | Where | State |
|---|---|---|
| Fetch + freeze prices/ratios | `ladder snapshot` | works |
| Judge 500 companies offline | `ladder judge` | works |
| What changed between two runs | `ladder diff` | **merged** |
| Are the rulebook's citations real | `scripts/audit_rulebook.py` | works — 15/16 sound |
| Turn a REF code into a lecture | `soic_wiki/ref_crosswalk.py` | works |
| 58 lectures, quote-checked | `docs/reassessment/` | done |
| Vault: 39 company notes, 254 lecture links | `Stock Framework` | done |

**A judged record already contains, per company:** the verdict, all four gate
results, six rule outcomes, ten observations. Nothing new needs computing to
explain one company — it needs reading.

## What is half-built

| Thing | Built | Missing |
|---|---|---|
| Weekly loop (D14) | step 4, the diff | rank, cap, brief |
| Rulebook validator (D13) | the script | not wired into CI |

## What does not exist

The **claims graph** (D2–D7, D10, D12). No plan, no code. It is the only way to
catch a rule that lost the condition attached to it in the source.

---

## The chain — build in this order

Each stage is useful on its own. Each reuses the one before it.

### Stage 1 — the lens: explain ONE company

`ladder explain NAVINFLUOR`

Reads an existing judged record and prints the whole journey: every gate, the
actual number, pass or fail, and where it stopped. Then joins the vault: which
lectures name this company, for or against.

- **Reuses:** `judge` output, the vault's company notes, `claims.md`
- **New work:** a reader. No new maths.
- **Why first:** it is the atom. Stage 2 is this, repeated.

### Stage 2 — the funnel: the weekly short list

`ladder weekly`

diff (built) → rank → cap at ~5 → write a brief. Each entry in the brief is a
Stage 1 explanation, trimmed.

- **Reuses:** Stage 1 for every surfaced name; `diff` as-is
- **New work:** rank, cap, brief writer (D14 steps 5, 6, 8)
- **Delivers your stated goal**, with no graph involved

### Stage 3 — the auditor: the claims graph

- Split the 58 lectures into single claims
- Label each: threshold / scope / mechanism / disqualifier / procedure / worked_example
- Link condition → number
- Ask: **does any rule use a number whose condition is not in the code?**

- **Reuses:** the gated briefs, `ref_crosswalk`, the quote-gate machinery
- **New work:** extraction (needs an LLM — the risky part), the graph, the query
- **Adds:** the lost-condition detector, and the "what to do next" checklist for
  Stage 2's brief (D14 step 7)

### Stage 4 — the loop: improve the rules

Graph proposes a fix → you approve → rulebook changes → re-run → diff shows what
moved.

- **Reuses:** everything above
- **Rule:** the graph proposes, a human applies (D9). Never automatic.

---

## Old names, mapped

| Old name | What it really is | Where it went |
|---|---|---|
| **Plan A** | foundation: crosswalk, citation audit, diff | ✅ built and merged |
| **DECISION-REVIEW.md** | a critique of the design decisions | ✅ read, shaped this |
| **D14 spec** | design for the weekly loop | Stage 2 |
| **Plan B** | build instructions for the graph | Stage 3, unwritten |
| **D1–D12** | the graph's design decisions | Stage 3 |
| **D13** | citation validator | built; wire into CI |

## What changed since those were written

We believed three rulebook citations were broken. **Only one is**
(`pe_context-001`, which has no source at all). And `judge.py` already computes
the exit layer we thought was missing — it simply never gates on it.

So Stage 3's value is narrower than first argued: not "audit the citations"
(done), but "catch a rule that dropped its condition" (still nothing does this).

## Shortest path to what you asked for

**Stage 1 → Stage 2.** That gives you both: point at a company and see its
journey, and a weekly Nifty 500 short list. Neither needs the graph.

Stage 3 is worth doing for rule quality, not to get the list.
