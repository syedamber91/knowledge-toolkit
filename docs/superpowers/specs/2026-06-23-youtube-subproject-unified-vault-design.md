# YouTube sub-project + unified knowledge vault — design

Date: 2026-06-23
Status: Approved (brainstorming)

## Goal

1. Make **YouTube** its own sub-project (separate package + CLI), peer to web —
   not nested inside the combined `media_toolkit`.
2. Land YouTube + web + Substack content in the **existing "Obsidian Vault"**
   with **unified topic notes** so a video, an article, and a Substack post about
   the same topic all hang off ONE topic note (true cross-linking).
3. **Move SOIC** out to a new standalone **"Stock Market Vault"** (it is
   stock-market/investing content, a different domain and a different tagging
   system).
4. Capture `https://www.youtube.com/@JustinSung/shorts` as the first real run.

Non-goal: pulling SOIC into the unified topic notes (different keyword-tag
system; would require re-tagging every lesson against the canonical vocabulary).

## Vaults (both inside the iCloud Obsidian container)

```
…/iCloud~md~obsidian/Documents/
  Obsidian Vault/            # tech & learning — UNIFIED
    topics/<topic>.md        # SHARED across Substack + YouTube + web
    Substack/posts/…         # Substack content notes (stay under Substack/)
    Substack/channels/…      # Substack channel MOCs (stay)
    youtube/<channel>/<video>.md
    web/<domain>/<article>.md
    sources/<kind>-<source>.md
    Home.md                  # root index across all sources
  Stock Market Vault/        # NEW standalone vault — SOIC content moves here
```

The old `Obsidian Vault/Substack/topics/` and `Obsidian Vault/Substack/Home.md`
are removed during the first unified build (otherwise duplicate same-named topic
notes appear). `Obsidian Vault/SOIC/` is moved entirely to `Stock Market Vault/`.

## Package structure (Approach A: shared core + source peers)

```
src/
  media_core/
    config.py        # paths: shared data/media.json, Obsidian Vault root, etc.
    models.py        # MediaItem, MediaCatalog
    store.py         # load/save the shared media catalog
    topics.py        # canonical vocabulary (reuses substack base) + extensions
    unified_vault.py # cross-source builder (reads substack + media catalogs)
  youtube_toolkit/
    capture.py       # yt-dlp enumerate (video/channel/playlist/shorts) + transcripts
    cli.py           # `youtube-toolkit` entry point
  web_toolkit/
    capture.py       # trafilatura readable extraction
    cli.py           # `web-toolkit` entry point
```

`media_toolkit` is refactored away into the above. Existing media tests are
repointed to the new module paths. `youtube_toolkit` and `web_toolkit` are true
peers — neither imports the other; both depend only on `media_core`.

## The unified vault builder (`media_core/unified_vault.py`)

The single seam that produces cross-source links. It is the builder for the whole
"Obsidian Vault".

Inputs: the Substack catalog (`data/substack.json`) and the media catalog
(`data/media.json`). Substack is optional — build still works with only media.

A neutral internal type decouples the builder from each source:

```
VaultEntry:
  title: str
  note_path: str        # vault-root-relative, no extension
                        #   e.g. "Substack/posts/vutr/<slug>", "youtube/<chan>/<vid>"
  source_label: str     # topic-note section header, e.g. "Substack · vutr",
                        #   "YouTube · JustinSung", "Web · martinfowler.com"
  topics: list[str]
  published_at: datetime | None
```

Steps:
1. **Content notes.** Write Substack post/channel notes under `Substack/`
   (reuse substack render functions, adjusted so topic links are bare
   `[[<topic-slug>|Topic]]` and resolve to the root `topics/`). Write media
   notes under `youtube/` and `web/` (reuse the media renderers).
2. **Collect** a `VaultEntry` per content note from both catalogs.
3. **Shared topics/** — one note per topic at the vault root, grouping its
   entries by `source_label` (sorted), each line `- [[<note_path>|<title>]]`.
4. **sources/** MOCs and root **Home.md** indexing all sources + topics.
5. **Migration** — delete stale `Substack/topics/` and `Substack/Home.md`.

Every content note links its topics with bare `[[<topic-slug>|Topic]]`; because
there is exactly one `topics/<slug>.md` at the root, those links resolve
uniquely. Link integrity = every wikilink target resolves (code-fence aware).

CLI: a `build` command (e.g. `youtube-toolkit build` / `web-toolkit build`, or a
small shared entry) that calls `unified_vault.build_from_disk()`. Both source
CLIs expose the same build so either can refresh the whole vault.

## YouTube capture (`youtube_toolkit/capture.py`)

Carried over from the current `media_toolkit/youtube.py`, unchanged in behavior:

- `yt-dlp` with `extract_flat="in_playlist"` enumerates entries; the nested-tab
  walker handles channel tabs INCLUDING `/shorts`. A `@handle/shorts` URL yields
  the shorts entries.
- Per item: full metadata via `yt-dlp`, transcript via
  `youtube-transcript-api` (supports legacy `get_transcript` and new `.fetch`).
- Shorts/videos without captions → `body_accessible=false`, warning callout in
  the note. No transcript is ever fabricated.
- Resumable (skip URLs already in the catalog), incremental save, polite delay.
- Network seams (`fetch_info`, `enumerate_entries`, `fetch_transcript`) are
  injectable for tests.

## SOIC move (`soic_toolkit`)

- Create `…/Documents/Stock Market Vault/`.
- Move `…/Obsidian Vault/SOIC/` → `…/Stock Market Vault/` (atomic, same volume).
- Update `SOIC_VAULT_DIR` in `.env` → `…/Stock Market Vault`.
- Open once in Obsidian to initialize it as a standalone vault.

## Testing (TDD)

- Carry over media tests, repointed to `youtube_toolkit` / `web_toolkit` /
  `media_core`.
- New: shorts enumeration (nested `/shorts` tab → entries).
- New: unified builder produces one `topics/<t>.md` with multiple
  `## <source_label>` sections drawn from both a Substack catalog and a media
  catalog.
- New: link-integrity across the merged vault (0 broken wikilinks, code-fence
  aware).
- Full suite stays green.

## Build/run order

1. Move SOIC → Stock Market Vault; update `.env`.
2. Refactor into `media_core` + `youtube_toolkit` + `web_toolkit` (tests green).
3. Implement `unified_vault.py` (+ tests).
4. Capture `@JustinSung/shorts`.
5. Unified build → "Obsidian Vault" with shared topics; verify link integrity.
6. Create the media-capture skill + agent (queued request).

## Risks / notes

- yt-dlp / transcript availability varies; shorts often have auto-captions but
  not always — handled via `body_accessible=false`.
- First unified build mutates the live iCloud vault (removes old Substack topic
  notes, moves SOIC). Verify counts and link integrity before/after; iCloud
  re-syncs afterward.
- `data/media.json` and `data/substack.json` are gitignored; vaults live outside
  the repo.
