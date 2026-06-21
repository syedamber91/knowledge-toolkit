# Substack Toolkit — Design

**Date:** 2026-06-21
**Status:** Approved (design phase)
**Repo:** `knowledge-toolkit` (sibling to `soic_toolkit`)

## Purpose

Add a second content source to the `knowledge-toolkit` repo: a `substack_toolkit`
package that captures posts from a Substack publication the user subscribes to,
and writes them into a dedicated Obsidian vault. The first channel is
**vutr** (Vu Trinh's Data Engineering newsletter, `vutr.substack.com`).

The defining requirement is **cross-channel topic linking**: a post about *dbt*
captured from vutr and a post about *dbt* captured from a future channel must
connect in the Obsidian graph. This is achieved with a shared, canonical topic
vocabulary that every channel matches against, so identical topics resolve to the
same topic note regardless of source.

This is **simple text extraction** — no AI-generated summaries. Topic detection is
purely lexical (vocabulary matching + keyword frequency).

## Scope

**In scope**
- Capture free *and* paywalled posts from a Substack publication using the user's
  own logged-in session.
- One Obsidian note per post, with frontmatter, body as Markdown, `[[topic]]`
  wikilinks, auto keyword tags, and a link back to the source post.
- Shared topic notes that aggregate posts across channels.
- A channel Map-of-Content (MOC) note and a Home note.
- Resumable crawl with a JSON cache, polite rate limiting.

**Out of scope (for now)**
- AI summaries or any generated/derived prose.
- Downloading or rehosting images/media. (Body text and code blocks only; image
  references may be kept as Markdown links but files are not downloaded.)
- Merging the Substack vault with the SOIC vault (kept separate per user choice).
- A shared `knowledge_core` refactor unifying SOIC + Substack (future work; the
  topic engine is designed to make this easy later).

## Architecture

New sibling package in the existing repo, mirroring `soic_toolkit`'s pipeline
shape (`auth → crawler → extract → topics → vault → cli`):

```
src/substack_toolkit/
  __init__.py
  config.py     # SUBSTACK_* env + paths
  models.py     # Channel, Post, SubstackCatalog
  auth.py       # Playwright interactive login -> save session cookie
  crawler.py    # HTTP API crawl (archive list -> per-post), resumable, polite
  extract.py    # API JSON -> Post; HTML body -> Markdown
  topics.py     # canonical topic vocabulary + matcher (the cross-channel seam)
  vault.py      # post notes + channel MOC + shared topic notes + Home
  cli.py        # typer app: login | crawl <handle> | build-vault | list-topics
```

New console script `substack-toolkit` registered in `pyproject.toml`.
New dependency: `markdownify` (HTML body -> Markdown). `requests` is added for the
HTTP API crawl (or `urllib` to avoid a new dependency — see Open Decisions).

### Data flow

1. **login** — `auth.py` opens a headed browser to `https://<handle>.substack.com`,
   the user logs in interactively, and the storage state (session cookie) is saved
   to `.auth/substack_state.json`. The password is never read or stored.
2. **crawl** — `crawler.py` loads the saved cookie and calls the Substack JSON API:
   - List: `GET /api/v1/archive?sort=new&limit=<N>&offset=<O>` — paginate to
     enumerate all posts (metadata + slug).
   - Detail: `GET /api/v1/posts/<slug>` — returns post JSON including `body_html`.
     With the auth cookie, paid posts return their body too.
   Already-captured post URLs are skipped (resumable). Results are merged into
   `data/substack.json`. Polite randomized delay between requests.
3. **extract** — `extract.py` converts each post's API JSON into a `Post`:
   metadata + `body_html` -> `body_markdown` via `markdownify`. Marks `is_paid`
   and whether the body was actually accessible.
4. **topics** — `topics.py` scans each post's title + body against the canonical
   vocabulary; matched canonical topics are attached to the post. Keyword
   frequency yields secondary `#tags`.
5. **build-vault** — `vault.py` renders the Obsidian vault from
   `data/substack.json` into `SUBSTACK_VAULT_DIR`.

### Fallback

If the JSON API withholds a paid post's `body_html` despite a valid session, the
crawler falls back to Playwright: open the post URL with the saved session and
read the rendered article text. The API path is primary because it is faster and
less brittle.

## Components

### `config.py`
- `SUBSTACK_VAULT_DIR` (default `~/Documents/Obsidian Vault/Substack`)
- `.auth/substack_state.json`, `data/substack.json`
- Crawl delays: `SUBSTACK_CRAWL_MIN_DELAY` (default 1.5s),
  `SUBSTACK_CRAWL_MAX_DELAY` (default 3.5s); `SUBSTACK_CRAWL_HEADED`.
- `ensure_dirs()` to create working directories.

### `models.py` (Pydantic)
```
Post:
  title: str
  subtitle: str = ""
  slug: str
  url: str
  author: str = ""
  published_at: datetime | None
  is_paid: bool = False          # post is marked paid/subscriber-only
  body_accessible: bool = True   # body text was actually captured
  body_markdown: str = ""
  topics: list[str] = []         # canonical topics matched
  keywords: list[str] = []       # secondary auto tags
  captured_at: datetime | None

Channel:
  handle: str                    # e.g. "vutr"
  name: str = ""                 # display name
  url: str                       # https://vutr.substack.com
  posts: list[Post] = []

SubstackCatalog:
  generated_at: datetime
  channels: list[Channel] = []
  def post_urls(self) -> set[str]   # for resumable crawl
```

### `topics.py` — the cross-channel seam
- `TOPIC_VOCABULARY`: an ordered mapping of **canonical topic -> alias patterns**.
  Seeded with data-engineering terms, e.g.:
  - `dbt` <- {"dbt", "data build tool"}
  - `Apache Airflow` <- {"airflow"}
  - `Apache Kafka` <- {"kafka"}
  - `Apache Spark` <- {"spark", "pyspark"}
  - `Apache Iceberg` <- {"iceberg"}
  - `Snowflake`, `Delta Lake`, `Data Modeling`, `Data Warehouse`, `Lakehouse`,
    `Orchestration`, `Streaming`, `Batch Processing`, `Data Quality`,
    `Data Governance`, `Change Data Capture`, `Data Engineering`, ...
- `match_topics(text) -> list[str]`: case-insensitive, whole-word matching;
  returns canonical names (deduplicated, order-stable).
- The vocabulary is the single source of truth that guarantees cross-channel
  topics collapse to one note. It is easy to extend; adding an entry makes future
  and re-built notes link on that topic.
- Keyword extraction (secondary tags) reuses the stopword approach already proven
  in `soic_toolkit/vault.py`.

### `vault.py`
Renders the Substack vault:

```
<SUBSTACK_VAULT_DIR>/
  Home.md                       # lists channels + most-used topics
  channels/
    vutr.md                     # channel MOC: all vutr posts (date-ordered)
  posts/
    vutr/
      <post-slug>.md            # one note per post
  topics/
    dbt.md                      # shared topic note (cross-channel)
    apache-airflow.md
    ...
```

**Post note** — frontmatter (`title, channel, author, published, url, paid,
topics, tags`), the Markdown body, a "Topics" section of `[[topic]]` wikilinks, a
`> Source: [Open post](url)` line, and a backlink to the channel MOC.

**Topic note** — heading + an explicit, build-time list of all posts that match
the topic, **grouped by channel**:
```
# dbt
## vutr
- [[a-deep-dive-into-dbt|A deep dive into dbt]]
```
Regenerated on every build, so adding a channel simply adds a new `##` group.
This works without the Dataview plugin and, combined with Obsidian's native
backlinks/graph, makes cross-channel grouping visible directly.

**Channel MOC** — lists the channel's posts in reverse-chronological order.

**Home** — links to each channel MOC and the top topic notes.

### `cli.py` (typer)
- `substack-toolkit login --handle vutr` — interactive session capture.
- `substack-toolkit crawl vutr [--limit N]` — crawl/refresh posts into the cache.
- `substack-toolkit build-vault` — render the Obsidian vault.
- `substack-toolkit list-topics` — print the topic vocabulary and per-topic post
  counts from the cache.

## Error handling
- **Auth missing/expired** — crawl detects a 401/redirect-to-login or empty bodies
  on known-paid posts and instructs the user to run `login` again.
- **Rate limiting (429)** — exponential backoff with a capped number of retries;
  honor `Retry-After` if present.
- **Network/transient errors** — bounded retries; on persistent failure the post
  is skipped and recorded so the resumable crawl retries next run.
- **Paid post without access** — recorded as `is_paid=True, body_accessible=False`
  with an empty body; the note is still created with a clear "not accessible"
  marker rather than failing the build.
- **Partial crawl** — the cache is written incrementally so interruption never
  loses captured posts.

## Testing
Mirror the existing `tests/` layout:
- `test_substack_extract.py` — API JSON fixture -> `Post` (incl. HTML->Markdown,
  paid/free flags).
- `test_substack_topics.py` — vocabulary matching (aliases, whole-word, dedupe).
- `test_substack_vault.py` — note rendering; **cross-channel topic aggregation**
  (two channels referencing the same topic produce one topic note with both
  groups) — this is the core requirement and gets an explicit test.
- `test_substack_crawl.py` — resumability (already-captured URLs skipped) using a
  mocked API; no live network in tests.
- Fixtures under `tests/fixtures/` (sample post API JSON).

## Guardrails
- Personal use of the user's **own** subscription. Crawl politely (rate-limited).
- Capture only text the authenticated session renders. Do not download, decrypt,
  or rehost media.
- Never store the password. Login is interactive; only the session cookie is kept,
  under `.auth/` (gitignored).
- `.auth/`, `data/`, `output/`, and vault output stay gitignored.
- Personal knowledge management, not redistribution of paid content.
- Ask before adding a new channel beyond vutr (scope control), consistent with the
  SOIC workflow.

## Open decisions (defaults chosen; easy to change)
- **HTTP client:** `requests` (clean) vs `urllib` (no new dep). Default: add
  `requests` for readability and cookie handling; revisit if minimizing deps.
- **Topic vocabulary seed size:** start with ~20 high-value data-engineering terms;
  grow as real vutr posts reveal gaps.
- **Image handling:** keep image references as Markdown links pointing at Substack
  URLs; do not download files.

## Future work (designed for, not built now)
- Additional channels (just crawl; topic notes auto-aggregate).
- Optional hierarchy: topic notes linking to a parent category (e.g.
  `[[dbt]]` -> `[[Data Engineering]]`).
- Refactor a shared `knowledge_core` so SOIC and Substack share one vault/topic
  engine. The canonical topic vocabulary is the seam that makes this low-risk.
