# `sj` (Shrayansh Jain) — Udemy-sourced persona for the `learning-vault-systemdesign` hub

**Date:** 2026-08-23
**Status:** Draft for confirmation (design substance pre-approved in an earlier session;
this document is the reality-checked version)
**Repos touched:**
- `learning-vault` (iCloud path) — **all code + tests** (`src/persona_wiki/`, `tests/persona_wiki/`)
- `learning-vault-systemdesign` (iCloud path) — **output only** (`wiki/personas/sj/`)
- `knowledge-toolkit` / SOIC_Scraper (this repo) — **this spec + the implementation plan only**

---

## 0. Three corrections to the incoming brief

The brief was written against assumptions that don't match the repos. All three were
verified against real files before writing this.

### 0.1 "This repo (`learning-vault`)" — it isn't

The brief was delivered in a SOIC_Scraper worktree. The pipeline it describes lives in a
**different repo**:

| Thing | Real location |
|---|---|
| `persona_wiki` package (ingest/synthesize/gates/log/index) | `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/learning-vault/src/persona_wiki/` |
| Its tests | `.../learning-vault/tests/persona_wiki/` |
| The hub the new persona joins | `.../learning-vault-systemdesign/wiki/personas/` (vault files **only** — no code, no CLI) |
| Design specs | **this repo**, `docs/superpowers/specs/` |

That last row is not a guess: `learning-vault/CLAUDE.md` says *"Design + plan live in the
sibling `knowledge-toolkit` repo under `docs/superpowers/`"*, and `learning-vault/docs/`
contains exactly one unrelated file. So the split is: **spec here, code there, output in
the hub.**

Also relevant: `learning-vault-systemdesign/wiki/personas/README.md` states the hub was
built by *"a one-off multi-agent ingestion pass"*, not by the `persona-wiki` CLI. This
work is the first time the CLI is pointed at that hub. `persona_wiki.config` supports it
already — `resolve_vault_dir()` honours `--vault-dir` / `PERSONA_WIKI_DIR`, and
`persona_root()` appends `wiki/personas/<persona>`. No config change needed.

### 0.2 `[[../lucsystemdesign/topics/<slug>|lucsystemdesign]]` will not resolve

`learning-vault-systemdesign/.obsidian` exists — the hub **is** its own Obsidian vault,
rooted at the repo root. Obsidian wikilinks are not relative filesystem paths; `../` is
not a thing it resolves. The link would render dead.

Compounding it: the hub already has **two unresolved slug collisions** across its two
personas — `bloom-filters` (`lucsystemdesign/concepts/` vs `sdcourse/topics/`) and `redis`
(both `entities/`). Bare `[[slug]]` links are therefore already ambiguous in this vault.

**Corrected link format — vault-root-relative, fully path-qualified:**

```
**Also covered by:** [[wiki/personas/lucsystemdesign/topics/databases|lucsystemdesign]]
```

One such line per matching persona, appended in a deterministic order
(`lucsystemdesign` then `sdcourse`).

### 0.3 `lld` + `hld` as the only two topics — breaks synthesis *and* backlinks

Measured, not estimated:

| Section | Lectures | Raw chars | ≈ tokens |
|---|---|---|---|
| `LLD (Low Level Design)` | 38 | 744,588 | ~186k |
| `HLD(High Level Design)` | 37 | 956,451 | ~239k |

`synthesize()` (`src/persona_wiki/synthesize.py:103`) inlines **every** raw post of a topic
into a single `CONCEPT-LIST` prompt via `build_concept_list_prompt`. A 239k-token prompt
does not fit. Two topics is a hard blocker, not a quality concern.

Second, independent failure: **neither existing persona has a topic named `lld`, `hld`,
`high-level-design`, or `system-design`.** Real filenames:

- `lucsystemdesign/topics/` (11): `api-architecture`, `architecture-styles`,
  `authentication-and-security`, `case-studies`, `databases`, `distributed-fundamentals`,
  `infrastructure`, `mcp-and-ai-tooling`, `messaging-and-streaming`, `networking-and-edge`,
  `resilience-patterns`
- `sdcourse/topics/` (23): `bi-integration`, `bloom-filters`,
  `capacity-planning-and-forecasting`, `circuit-breakers-and-resilience`,
  `course-administrative`, `dead-letter-queues`, `faang-interview-prep`,
  `faceted-search-and-query`, `field-level-encryption-and-compliance`,
  `foundational-log-pipeline-setup`, `incident-management-and-backup-recovery`,
  `kafka-and-event-streaming`, `leader-election-and-raft`, `log-analytics-and-dashboards`,
  `log-collection-agents-and-client-libraries`, `log-parsing-and-normalization`,
  `mapreduce-and-batch-processing`, `multi-region-replication-and-consensus`,
  `storage-tiering-and-caching`, `stream-processing-and-windows`, `task-scheduling`,
  `tls-and-security`, `webhooks-and-event-routing`

No normalization rule maps `hld` onto any of those. Task 3 would ship as provably dead
code.

**Resolution (user-confirmed 2026-08-23): fine-grained topic groups.** See §2.

---

## 1. Architecture

```
Udemy Vault (separate toolkit, read-only to us)
  lectures/system-design-lld-hld-from-basics-to-advanced/*.md   (75 files)
              │
              │  [Task 1]  persona_wiki.udemy.ingest_udemy()
              │            + data/sj_lecture_groups.yaml  (lecture_id -> group)
              ▼
learning-vault-systemdesign/wiki/personas/sj/
  raw/<group>/<lecture-slug>.md          14 groups, immutable, + _manifest.yaml
              │
              │  [Task 2]  persona_wiki.synthesize.synthesize()   UNCHANGED
              │            provenance gate / depth gate / resolution gate as-is
              ▼
  concepts/<slug>.md   (cites raw/<group>/<file>.md)
  topics/<group>.md    (Related: · Comparisons · Open questions · Synthesis)
  index.yaml, log.md
              │
              │  [Task 3]  persona_wiki.crosslink.apply_backlinks()   NEW
              ▼
  topics/<group>.md  += "**Also covered by:** [[wiki/personas/…|persona]]"
```

Nothing in Task 2 changes. That is the point: the same gates that judge every other
persona judge this one.

---

## 2. Topic grouping (Task 1's routing table)

75 lectures → **14 groups**. Grouping is driven by lecture content; where the content
matches a taxonomy `lucsystemdesign` already curated by hand, **that exact slug is
reused**. That reuse is a deliberate design choice — a shared vocabulary is what makes
cross-persona discovery possible at all — and it is why the match rate in §4 is high. It
is a decision, not a discovery, and this spec says so plainly rather than presenting 8
matches as an emergent finding.

### LLD → 5 groups (38 lectures) — no cross-persona matches expected

| Group slug | n | Lectures |
|---|---|---|
| `lld-foundations` | 4 | What is LLD & Pattern Categories; SOLID Principles; Liskov Substitution; MVC |
| `creational-patterns` | 3 | Builder; Factory & Abstract Factory; Object Pool |
| `structural-patterns` | 7 | Adapter; Bridge; Composite; Decorator; Facade; Flyweight; Proxy |
| `behavioral-patterns` | 12 | Chain of Responsibility; Command; Interpreter; Iterator; Mediator; Memento; Null Object; Observer; State (Vending Machine); Strategy; Template Method; Visitor |
| `lld-case-studies` | 12 | Parking Lot; Tic-Tac-Toe; Apply Coupons; ATM; BookMyShow; Car Rental; Cricbuzz; Elevator; Inventory Mgmt; Payment Gateway; Snake n Ladder; Splitwise |

### HLD → 9 groups (37 lectures)

| Group slug | n | Lectures | Matches |
|---|---|---|---|
| `databases` | 5 | SQL vs NoSQL; Database Indexing (B+ tree); Key-Value Store/DynamoDB; Two Phase Locking; Concurrency Control | luc |
| `distributed-fundamentals` | 4 | CAP Theorem; Consistent Hashing; 2PC/3PC/SAGA; Dual Write Problem | luc |
| `resilience-patterns` | 5 | Circuit Breaker; Bulkhead; Retry Pattern; Thundering Herd; High Availability (Active-Passive/Active-Active) | luc |
| `networking-and-edge` | 5 | Load Balancer; Proxy vs Reverse Proxy; DNS; Network Protocols; API Gateway | luc |
| `authentication-and-security` | 4 | JWT; OAuth 2.0; Symmetric/Asymmetric Encryption; CSRF/XSS/CORS/SQLi | luc |
| `architecture-styles` | 5 | Intro Microservices; SAGA/Strangler Patterns; How Many Microservices; Service Mesh; Service Discovery | luc |
| `messaging-and-streaming` | 1 | Distributed Messaging Queue (Kafka/RabbitMQ) | luc |
| `case-studies` | 4 | WhatsApp; TinyURL; Scale Zero→Million; Back-of-the-Envelope Estimation | luc |
| `caching-and-rate-limiting` | 4 | Distributed Cache & Strategies; Design Rate Limiter; Rate Limiter Algorithms; Idempotent POST API | — |

**Largest group ≈ 12 lectures ≈ 235k chars ≈ 59k tokens** — comfortably inside a single
synthesis prompt. Blocker 0.3(a) is resolved.

### The mapping file

`learning-vault/data/sj_lecture_groups.yaml`, keyed on **Udemy `lecture_id`** (the trailing
numeric in the source filename and the last URL path segment) — the only field that cannot
drift when a title is edited upstream.

```yaml
# sj (Shrayansh Jain) — System Design (LLD + HLD) from Basics to Advanced
# lecture_id -> raw/<group>/ . Titles are comments only; the id is the key.
course_dir: "system-design-lld-hld-from-basics-to-advanced"
groups:
  lld-foundations:
    - 53198193   # What is LLD and Pattern Categories?
    - 51802699   # SOLID Principles
    - 41932786   # Liskov Substitution Principle (LSP) Solution
    - 46258341   # MVC Design Pattern
  creational-patterns:
    - 41932808   # Builder Design Pattern
    # ... (full file written during implementation; all 75 ids accounted for)
```

**Already verified by hand before this spec was written:** the 14 id-lists in §2 cover 75
unique lecture ids with zero duplicates and zero gaps against the real course directory.
**Invariant, asserted by a test:** the union of all group id-lists is exactly the set of
lecture ids present in the course directory — no missing lecture, no unknown id. A
mismatch raises rather than silently dropping a lecture.

---

## 3. Task 1 — the Udemy feeder

### Why a new module, not an extension of `ingest.py`

`ingest.py` has **no pluggable source interface** — no Protocol, ABC, or registry. Its core
is `shutil.copyfile(src, dst)` (`ingest.py:59`): a byte-for-byte copy of files that some
upstream capture skill already shaped. The Udemy feeder must *transform* (parse
frontmatter, slice out `## Transcript`, drop vault-local link lines, re-emit frontmatter),
so `copyfile` cannot be reused.

Decision: **new module `src/persona_wiki/udemy.py`**, reusing `IngestResult` and the
`MANIFEST = "_manifest.yaml"` constant from `ingest.py` and mirroring its manifest shape
exactly. `ingest.py` is not modified. Cost: ~10 duplicated lines of manifest bookkeeping.
Benefit: zero risk to the feeder every other persona depends on.

### Source shape — verified against a real file

Confirmed against
`.../Udemy Vault/lectures/system-design-lld-hld-from-basics-to-advanced/1-adapter-pattern-structural-design-pattern-41932990.md`.
The brief's description is accurate, with two notes:

- `section` is `"LLD (Low Level Design)"` (space before paren) but `"HLD(High Level
  Design)"` (**no** space). Verified across all 75: 38 LLD / 37 HLD. Any parser keying on
  that string must tolerate both; this design keys on `lecture_id` instead, so it doesn't
  matter — `section` is carried through as provenance metadata only.
- `topics:`/`topic_links:`/`tags:` in the source are junk from the Udemy vault's own
  auto-tagger (`topics: [Career, Education]`). **Dropped**, not propagated.

### What gets written

`wiki/personas/sj/raw/<group>/<slugify(title)>.md`:

```markdown
---
title: "Adapter Pattern (Structural Design Pattern)"
instructor: "Shrayansh Jain"
course: "System Design (LLD + HLD) from Basics to Advanced"
section: "LLD (Low Level Design)"
lecture_id: "41932990"
url: "https://www.udemy.com/course/draft/5776816/learn/lecture/41932990"
duration: "00:16:44"
captured_at: 2026-08-22T06:02:45.870634+00:00
---

# Adapter Pattern (Structural Design Pattern)

[00:00:00] Hey guys. Welcome to Concept and Coding. ...
```

Body = everything after the `## Transcript` heading, verbatim, timestamps preserved.
Dropped: the `Part of [[courses/...]]` line and the `[Open on Udemy]` line (both link into
a *different* Obsidian vault and would be dangling here; the `url` frontmatter field keeps
the same information).

Filename = `slugify(title)` via `persona_wiki.storage.slugify` (re-exported from
`de_toolkit.vault`) — the repo's existing slug function, reused, not reinvented.

### Signature

```python
@dataclass
class UdemyIngestResult(IngestResult):        # copied / skipped / manifest
    unmapped: List[str] = field(default_factory=list)   # lecture_ids absent from the yaml

def load_group_map(path: Path) -> Dict[str, str]:
    """lecture_id -> group slug, from data/sj_lecture_groups.yaml."""

def parse_lecture(text: str) -> Tuple[dict, str]:
    """(frontmatter dict, transcript body). Raises ValueError if '## Transcript' absent."""

def ingest_udemy(course_dir: Path, root: Path, group_map: Dict[str, str],
                 stamp: str) -> UdemyIngestResult:
    """Transform every lecture in course_dir into root/raw/<group>/, idempotently."""
```

### Idempotency

Stronger than `ingest.py`'s, and deliberately so, because the destination filename is
*derived* (`slugify(title)`) rather than carried over — a retitled lecture upstream would
otherwise be copied twice under two names.

Skip a lecture if **either**:
1. its `lecture_id` already appears in `raw/<group>/_manifest.yaml`, **or**
2. the destination file already exists.

Manifest entry, mirroring `ingest.py`'s shape plus the id:

```yaml
adapter-pattern-structural-design-pattern.md:
  copied: '2026-08-23'
  lecture_id: '41932990'
  source: /Users/.../Udemy Vault/lectures/.../1-adapter-pattern-...-41932990.md
```

Written with `yaml.safe_dump(manifest, sort_keys=True, allow_unicode=True)` — same call as
`ingest.py:63-64`. Never overwrites an existing raw file; the raw layer stays immutable.

A lecture whose id is not in the mapping goes to `result.unmapped` and is **not** copied —
reported, never guessed at, never aborting the run.

### CLI

New Typer subcommand in `src/persona_wiki/cli.py`, alongside the existing `ingest`:

```bash
persona-wiki ingest-udemy \
  --persona sj \
  --vault-dir "$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/learning-vault-systemdesign" \
  --course-dir "$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/Udemy Vault/lectures/system-design-lld-hld-from-basics-to-advanced" \
  --group-map data/sj_lecture_groups.yaml
```

---

## 4. Task 3 — cross-persona backlinks

New module `src/persona_wiki/crosslink.py`. Deterministic, no LLM, no shared vocabulary
file.

### Normalization

```python
_STOP = {"and", "or", "the", "of", "in", "a", "an", "for"}
_EXPAND = {"hld": ("high", "level", "design"), "lld": ("low", "level", "design"),
           "db": ("database",), "oo": ("object", "oriented"), "auth": ("authentication",)}

def normalize(slug: str) -> FrozenSet[str]:
    """topics/High-Level-Design.md -> frozenset({'high','level','design'})"""
    # strip .md, lowercase, split on '-'/'_', expand abbreviations,
    # drop stopwords, strip a single trailing 's' from each token
```

### Match rule — exact normalized-set equality only

`normalize(sj_slug) == normalize(their_slug)` → match. Nothing looser.

A "shared token" or "subset" rule was considered and **rejected**: `structural-patterns`
and `resilience-patterns` both normalize to a set containing `pattern`, and
`caching-and-rate-limiting` vs `storage-tiering-and-caching` share `caching`. Any looser
rule fabricates links between unrelated topics. Exact equality is the smallest mechanism
that works, per the brief's rule 4.

The abbreviation table earns its place as drift insurance and as the reusable rule for the
*next* persona — with the §2 slugs, most matches would also hold under plain string
equality. Stated honestly rather than oversold.

### Existence guard

A line is written only if the resolved target file **actually exists on disk**. The matcher
enumerates real `topics/*.md` filenames under each sibling persona at run time — it never
constructs a path from a guess. Rule 5 holds: no match → no line, not an error.

### Expected result (8 of 14 sj topics get a line)

`databases`, `distributed-fundamentals`, `resilience-patterns`, `networking-and-edge`,
`authentication-and-security`, `architecture-styles`, `messaging-and-streaming`,
`case-studies` → all match `lucsystemdesign`. No `sdcourse` matches under exact equality.
The 5 LLD groups and `caching-and-rate-limiting` get nothing — correct, they have no
counterpart.

### Placement & idempotency

The line is appended to the end of the topic note body, after `## Synthesis`. Re-running is
a no-op: the module reads the note first and skips if an identical `**Also covered by:**`
line is already present. It does **not** call `log_ingest` — no note count changes, and
`log_ingest` would no-op anyway (`log.py:31`).

### Interaction with `resolution_gate` — checked

`resolution_gate` (`qc.py:56`) resolves a wikilink slug only against
`<root>/{concepts,entities,topics}/<slug>.md`, i.e. within a single persona. A
path-qualified cross-persona link would look "dangling" to it. This does not fire, because
the gate runs *inside* `synthesize()` before the topic note is written, and the crosslink
pass appends afterwards. Sequencing (all synthesis → then crosslink) is therefore
load-bearing and is called out in the plan. No gate is modified or weakened.

---

## 5. Known risk: slug collisions in a flat Obsidian namespace

Obsidian resolves `[[slug]]` across the whole vault. `sj/topics/databases.md` will collide
with `lucsystemdesign/topics/databases.md`; concept notes will collide more (sj will almost
certainly generate `cap-theorem`, `consistent-hashing`, `circuit-breaker` — all already in
`lucsystemdesign/concepts/`). The hub already ships two such collisions
(`bloom-filters`, `redis`) unresolved.

`resolution_gate` is single-persona-scoped and will not catch this.

**Mitigation (deliberately minimal):**
1. Every link this work *writes* is path-qualified (§0.2) — new links are never ambiguous.
2. A **collision report** step: a small script enumerating sj slugs that collide with
   either sibling persona, printed and pasted into the plan's verification section. A
   report, not a rename — renaming sj's slugs to dodge collisions would break the §4
   matcher and diverge from the hub's existing convention.

Renaming or namespacing existing notes is explicitly **out of scope**.

---

## 6. Testing

`learning-vault/tests/persona_wiki/`, matching the existing convention exactly: offline, no
network, no login; LLM stubbed as a plain `Callable[[str], str]` closure keyed on prompt
substrings; fixture vaults built inline with `tmp_path` (**there is no `conftest.py` and no
`fixtures/` dir in this repo** — do not introduce one); `test_<function>_<behavior>` naming;
plain `assert`; written files re-read through the real `storage.parse_note`.

### `tests/persona_wiki/test_udemy.py`
1. `test_parse_lecture_extracts_frontmatter_and_transcript` — fixture Udemy-shaped note in, `(dict, body)` out; body starts at the first timestamp; `Part of [[courses/...]]` and `[Open on Udemy]` lines excluded.
2. `test_parse_lecture_rejects_missing_transcript` — `ValueError`.
3. `test_ingest_udemy_routes_to_group_dir` — two fixture lectures, two groups → correct `raw/<group>/<slug>.md` paths, correct frontmatter, `_manifest.yaml` written with `lecture_id`.
4. `test_ingest_udemy_is_idempotent` — second run copies 0, skips 2, manifest unchanged; **and** mutating the source after the first run leaves the destination untouched (mirrors `test_ingest.py::test_ingest_is_append_only`).
5. `test_ingest_udemy_reports_unmapped_lecture` — id absent from the map → `result.unmapped`, nothing written, no raise.
6. `test_group_map_covers_every_lecture` — the union-equals-directory invariant of §2, run against the real `data/sj_lecture_groups.yaml` and the real course dir; **skipped** (`pytest.mark.skipif`) when the Udemy Vault path is absent, keeping the suite offline-clean on other machines.

### `tests/persona_wiki/test_crosslink.py`
7. `test_normalize_expands_and_strips` — `High-Level-Design` / `hld` → same frozenset; trailing-s and stopwords handled.
8. `test_backlink_added_on_normalized_match` — fixture hub with `sj/topics/databases.md` + `lucsystemdesign/topics/databases.md` → exact path-qualified line appended after `## Synthesis`.
9. `test_no_backlink_when_no_match` — `sj/topics/structural-patterns.md` against a sibling with only `resilience-patterns.md` → file byte-identical afterwards. **This is the anti-fabrication test.**
10. `test_no_backlink_when_target_file_missing` — a slug that normalizes to a match but whose `.md` doesn't exist → nothing written.
11. `test_backlink_is_idempotent` — second run appends nothing.
12. `test_backlink_lists_both_personas_deterministically` — when both siblings match, two lines, `lucsystemdesign` first.

### The "4-shape vault-writer test" question — answered

The brief asked whether this repo requires it for every new writer. **It exists here and
already passes; neither new module triggers it.**

`src/persona_wiki/log.py` implements the contract and `tests/persona_wiki/test_log.py`
covers its 4 shapes: `backfill` / `append-on-growth` / `skip-on-no-change` /
`revision-wording-on-change`. Note this repo's shapes differ from SOIC_Scraper's — there is
**no removed-item shape** (`log_ingest` has no `total < prior` branch) and the phrase
`"already in vault"` appears nowhere in `persona_wiki` (its one occurrence
repo-wide is a stray legacy `wiki/books/ddia/Log.md.bak`). Do not port SOIC_Scraper's wording.

Neither new module writes index-counted notes: the feeder writes only into `raw/`, and the
crosslink pass only appends a line to an existing note. Neither calls `log_ingest`. The
log entries for `sj` are produced by the **unchanged** `synthesize()`
(`synthesize.py:166`), already covered by `test_log.py` + `test_synthesize.py`. No new log
tests are warranted, and adding them would test `log.py` a second time rather than the new
code.

### Error handling

Unchanged from the rest of the pipeline. A provenance-gate failure quarantines that one
concept to `_failed/<slug>.md` with `qc: failed` + `qc_reason`
(`synthesize.py:116-121`) and continues; an unparseable concept body lands in
`result.skipped` for the next pass; the depth gate fails open and logs gaps into the topic
note's "Open questions". Nothing aborts a run. The feeder adds one non-fatal case of its
own: an unmapped `lecture_id` is reported, not copied, not raised.

---

## 7. Out of scope

- Any change to `ingest.py`, `synthesize.py`, `qc.py`, `log.py`, `index.py`, `storage.py`.
- A shared/global topic vocabulary file across personas.
- Renaming or namespacing existing `lucsystemdesign` / `sdcourse` notes.
- Backlinks *from* the two existing personas back to `sj` (this pass is one-directional;
  the same module could be run in reverse later, deliberately, as its own change).
- Stages B/C of `/learn-topic` (Alex learner notebook, verified PDF pack) for `sj`.
