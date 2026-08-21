# Udemy Toolkit — Design

Date: 2026-08-22
Status: approved (design), not yet implemented

## Purpose

Capture lecture **transcripts** from courses the user has purchased on Udemy,
using the user's own interactive browser session, and build a standalone
Obsidian vault ("Udemy Vault") from them. One course at a time.

## Non-goals / guardrails (non-negotiable)

- **No video or audio is ever downloaded or decrypted.** Udemy media is DRM
  protected. This toolkit fetches caption/transcript text only.
- **No stored passwords.** Login is interactive via Playwright; only the
  resulting session state is persisted, under `.auth/udemy_state.json`.
- Personal use only, from the user's own paid account. `data/` and the vault
  directory stay gitignored — captured content is never committed.
- Never fabricate a transcript. A lecture without captions is skipped and
  recorded as skipped.

## Scope decisions (settled during brainstorming)

| Question | Decision |
|---|---|
| Selection granularity | One course at a time, by course URL. "All my courses" is a later loop over this, not built now. |
| Transcript source | Fetch the caption asset (`.vtt`) with the authenticated session. Fall back to reading the in-page transcript panel when no caption asset exists. |
| Vault location | New standalone iCloud vault at `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Udemy Vault`, overridable via `UDEMY_VAULT_DIR`. |
| Note granularity | One note per lecture, with section MOC notes rolling them up. |
| Model tiering | The mechanical crawl/fetch loop is dispatched to a **Sonnet** subagent. Opus tier is reserved for design and review. |

## Package layout

`src/udemy_toolkit/`, mirroring `src/soic_toolkit/`:

- `config.py` — env + paths. `UDEMY_VAULT_DIR`, `UDEMY_BASE_URL`
  (default `https://www.udemy.com`), `UDEMY_CRAWL_MIN_DELAY` (1.5),
  `UDEMY_CRAWL_MAX_DELAY` (3.5), `UDEMY_CRAWL_HEADED`.
  Paths: `.auth/udemy_state.json`, `data/udemy.json`.
- `auth.py` — `login()` launches headed Chromium, waits for the user to sign in
  (detected by a logged-in URL fragment / DOM marker), saves storage state.
  `load_state()` raises a clear "run `udemy-toolkit login`" error when missing
  or expired.
- `models.py` — Pydantic:
  - `UdemyLecture`: `id`, `title`, `url`, `duration_seconds`, `section_title`,
    `transcript` (str), `has_transcript` (bool), `captured_at`.
  - `UdemySection`: `title`, `order`, `lectures: list[UdemyLecture]`.
  - `UdemyCourse`: `id`, `title`, `url`, `instructor`, `sections`.
  - `UdemyCatalog`: `courses: list[UdemyCourse]`, plus `seen_lecture_ids` so
    resume skips both captured and known-caption-less lectures.
- `crawler.py` — `crawl_course(url, limit=None)`:
  1. resolve the course from its URL, read the curriculum (sections + lectures);
  2. for each not-yet-seen lecture, locate its caption asset and fetch it with
     the authenticated session;
  3. on no caption asset, fall back to the in-page transcript panel;
  4. on neither, mark `has_transcript=False`, add to `seen_lecture_ids`, move on;
  5. save the catalog **after every lecture** (incremental, resumable);
  6. sleep a random `min..max` delay between requests.
- `extract.py` — caption text → cleaned, timestamped plain text: strip cue
  numbering/markup, merge cues into readable paragraphs, keep `HH:MM:SS` offsets
  at paragraph starts. Pure function over a string; fully unit-testable offline.
- `vault.py` — catalog → Obsidian notes. Implements all three required
  components:
  1. **Index** — `Home.md` plus one MOC per course and per section.
  2. **Log** — append-only `Log.md`, copying the `_last_logged_total()` /
     `_log_ingest()` contract from `media_core/unified_vault.py`: parse the last
     entry's `(N total`; word the first-ever entry as a backfill; append only
     when the total actually changed; link `[[Log|Ingestion Log]]` from Home.md.
  3. **Cross-links** — shared `topics/<topic>.md` notes using the existing
     centralized topic vocabulary (`media_core/topics.py`), plus inline
     `[[wikilinks]]`. No ad-hoc tagging is added anywhere else.
- `cli.py` — Typer app, registered in `pyproject.toml` as `udemy-toolkit`:
  - `login`
  - `crawl <course-url> [--limit N]`
  - `build-vault`

## Note shape

One file per lecture, `<section-order>-<lecture-slug>.md`, YAML frontmatter
(`title`, `course`, `section`, `url`, `duration`, `captured_at`, `topics`,
`topic_links`) then the transcript body. Section MOC links its lectures; course
MOC links its sections; `Home.md` links the courses.

## Error handling

| Situation | Behaviour |
|---|---|
| No/expired session | Clear message: re-run `udemy-toolkit login`. Non-zero exit. |
| Lecture has no captions | Skip, mark seen, continue. Counted in the run summary. |
| Rate limited / blocked | Stop politely with a message; the saved catalog means a re-run resumes. |
| Course URL not resolvable | Fail fast before any crawling begins. |

## Testing

All offline — no login, no network.

- `extract.py`: caption fixture → expected cleaned text, including malformed and
  empty-cue cases.
- Curriculum parsing: saved fixture → expected `UdemyCourse` tree.
- Crawler resume: injected fetch seam returns canned payloads; assert already
  seen lectures are not re-fetched and that caption-less lectures are marked
  seen.
- Vault: the standard 4 log tests — backfill wording on first build, append on
  growth, no duplicate entry on unchanged rebuild, removed-item wording — plus
  index/cross-link assertions.

Fixtures live in `tests/fixtures/udemy/`.

## Out of scope for this spec

- Capturing every enrolled course in one command.
- Quizzes, coding exercises, attached resources, Q&A.
- Any media download.

## Addendum (2026-08-22) — machine-routable vault layer

Added at the user's request after the design was approved: the vault must be
readable by an agent that will generate a wiki and learning materials from it,
not only by a human in Obsidian. Beyond the index + log + cross-links contract
above, `build_vault` also emits:

- **`index.yaml`** — a cheap routing manifest read *before* any grep: every
  lecture's note path, URL, section, tags, topics, `has_transcript`, and word
  count, plus vault-level counts and the tag vocabulary.
- **`tags/<tag>.md`** — notes over a **closed** 12-tag vocabulary
  (`classify_tags` may never return a tag outside it), giving a second routing
  axis alongside `topics/`.
- **`verify_vault()`** — one pass over the entire built vault reporting dangling
  wikilinks, orphan notes, untagged lectures, and out-of-vocabulary tags.
  `build-vault` exits non-zero when it finds any. Per the lesson recorded in
  CLAUDE.md's cross-linking pass, verification is a single whole-set read, never
  a trust of per-file self-reports.

This is additive: no existing field is rewritten, matching the "add a new field
for a new capability" rule.
