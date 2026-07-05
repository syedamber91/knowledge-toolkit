# Graph Report - .  (2026-07-05)

## Corpus Check
- 192 files · ~230,614 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1119 nodes · 1893 edges · 84 communities (58 shown, 26 thin omitted)
- Extraction: 92% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 141 edges (avg confidence: 0.67)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Brainstorm WS Client|Brainstorm WS Client]]
- [[_COMMUNITY_Brainstorm Start-Server|Brainstorm Start-Server]]
- [[_COMMUNITY_Brainstorm Stop-Server|Brainstorm Stop-Server]]
- [[_COMMUNITY_Goal Skill Engine|Goal Skill Engine]]
- [[_COMMUNITY_Test Polluter Finder|Test Polluter Finder]]
- [[_COMMUNITY_SDD Scripts & Graph Render|SDD Scripts & Graph Render]]
- [[_COMMUNITY_Project Toolkits Overview|Project Toolkits Overview]]
- [[_COMMUNITY_Learning Pack Scripts & Drive|Learning Pack Scripts & Drive]]
- [[_COMMUNITY_Instagram CLI|Instagram CLI]]
- [[_COMMUNITY_Instagram Chrome-Cookie Auth|Instagram Chrome-Cookie Auth]]
- [[_COMMUNITY_Instagram Config|Instagram Config]]
- [[_COMMUNITY_Instagram Instaloader Crawler|Instagram Instaloader Crawler]]
- [[_COMMUNITY_Instagram Block Handling|Instagram Block Handling]]
- [[_COMMUNITY_Substack Crawler (JSON API)|Substack Crawler (JSON API)]]
- [[_COMMUNITY_Instagram Crawl Entry|Instagram Crawl Entry]]
- [[_COMMUNITY_Instagram Auth & Crawl|Instagram Auth & Crawl]]
- [[_COMMUNITY_media_core Package Init|media_core Package Init]]
- [[_COMMUNITY_Media Core (configmodels)|Media Core (config/models)]]
- [[_COMMUNITY_Webapp Backend Routers & Models|Webapp Backend Routers & Models]]
- [[_COMMUNITY_SOIC CLI|SOIC CLI]]
- [[_COMMUNITY_SOIC Playwright Auth|SOIC Playwright Auth]]
- [[_COMMUNITY_SOIC Bodhi Crawler|SOIC Bodhi Crawler]]
- [[_COMMUNITY_SOIC Extract  Parse|SOIC Extract / Parse]]
- [[_COMMUNITY_SOIC Mindmap (Markmap)|SOIC Mindmap (Markmap)]]
- [[_COMMUNITY_SOIC Models & Vault Tests|SOIC Models & Vault Tests]]
- [[_COMMUNITY_SOIC Vault Builder|SOIC Vault Builder]]
- [[_COMMUNITY_Substack CLI & Commands|Substack CLI & Commands]]
- [[_COMMUNITY_Substack Chrome Auth|Substack Chrome Auth]]
- [[_COMMUNITY_Substack Config|Substack Config]]
- [[_COMMUNITY_Substack Extract & Topics|Substack Extract & Topics]]
- [[_COMMUNITY_Substack Extract Tests|Substack Extract Tests]]
- [[_COMMUNITY_web_toolkit Package Init|web_toolkit Package Init]]
- [[_COMMUNITY_Web Toolkit CLI|Web Toolkit CLI]]
- [[_COMMUNITY_youtube_toolkit Package Init|youtube_toolkit Package Init]]
- [[_COMMUNITY_YouTube Transcript Capture|YouTube Transcript Capture]]
- [[_COMMUNITY_SOIC Toolkit Suite|SOIC Toolkit Suite]]
- [[_COMMUNITY_Media Topics Tests|Media Topics Tests]]
- [[_COMMUNITY_YouTube Capture Tests|YouTube Capture Tests]]
- [[_COMMUNITY_Substack Toolkit Suite|Substack Toolkit Suite]]
- [[_COMMUNITY_ESLint Config|ESLint Config]]
- [[_COMMUNITY_Root Layout & Topbar|Root Layout & Topbar]]
- [[_COMMUNITY_Run Detail Page|Run Detail Page]]
- [[_COMMUNITY_New Run  Pack Builder Page|New Run / Pack Builder Page]]
- [[_COMMUNITY_Runs List Page|Runs List Page]]
- [[_COMMUNITY_Chapter Fields UI|Chapter Fields UI]]
- [[_COMMUNITY_Examiner Grid UI|Examiner Grid UI]]
- [[_COMMUNITY_Live Log UI|Live Log UI]]
- [[_COMMUNITY_Run Detail Sidebar|Run Detail Sidebar]]
- [[_COMMUNITY_Run List Table UI|Run List Table UI]]
- [[_COMMUNITY_Sign-Off Checklist UI|Sign-Off Checklist UI]]
- [[_COMMUNITY_Frontend Colors|Frontend Colors]]
- [[_COMMUNITY_Next Config|Next Config]]
- [[_COMMUNITY_Frontend Package Deps|Frontend Package Deps]]
- [[_COMMUNITY_PostCSS Config|PostCSS Config]]
- [[_COMMUNITY_Webapp Backend & TS Config|Webapp Backend & TS Config]]
- [[_COMMUNITY_Webapp Start Script|Webapp Start Script]]
- [[_COMMUNITY_Instagram CLI Entry|Instagram CLI Entry]]
- [[_COMMUNITY_Instagram Auth Node|Instagram Auth Node]]
- [[_COMMUNITY_Instagram Config Node|Instagram Config Node]]
- [[_COMMUNITY_Instagram Package|Instagram Package]]
- [[_COMMUNITY_Goal Script Clone|Goal Script Clone]]
- [[_COMMUNITY_Brainstorm Server Scripts|Brainstorm Server Scripts]]
- [[_COMMUNITY_Substack match_topics|Substack match_topics]]
- [[_COMMUNITY_Substack topics.keywords|Substack topics.keywords]]
- [[_COMMUNITY_Substack Topics Tests|Substack Topics Tests]]
- [[_COMMUNITY_Substack Vault Tests|Substack Vault Tests]]
- [[_COMMUNITY_Unified Vault Tests|Unified Vault Tests]]
- [[_COMMUNITY_Vault Tests|Vault Tests]]
- [[_COMMUNITY_Frontend App Routes|Frontend App Routes]]
- [[_COMMUNITY_Frontend Feature Areas|Frontend Feature Areas]]
- [[_COMMUNITY_Frontend Build Config|Frontend Build Config]]
- [[_COMMUNITY_Verification Persona Agents|Verification Persona Agents]]
- [[_COMMUNITY_Capture Agents & Guardrails|Capture Agents & Guardrails]]
- [[_COMMUNITY_Brainstorming & Process Skills|Brainstorming & Process Skills]]
- [[_COMMUNITY_Goal Skill|Goal Skill]]
- [[_COMMUNITY_Goal Research Notes|Goal Research Notes]]
- [[_COMMUNITY_Graphify & Capture Skills|Graphify & Capture Skills]]
- [[_COMMUNITY_Justin Sung Learning Framework|Justin Sung Learning Framework]]
- [[_COMMUNITY_System Design Concepts (Luc)|System Design Concepts (Luc)]]
- [[_COMMUNITY_Superpowers Skill Docs|Superpowers Skill Docs]]

## God Nodes (most connected - your core abstractions)
1. `media_core Unified Vault Builder` - 39 edges
2. `MediaCatalog` - 22 edges
3. `SubstackCatalog` - 22 edges
4. `Catalog` - 20 edges
5. `build_unified()` - 19 edges
6. `post_from_api()` - 19 edges
7. `MediaItem` - 18 edges
8. `Instagram Toolkit Test` - 18 edges
9. `Run ORM model` - 18 edges
10. `media_core Catalog Store` - 17 edges

## Surprising Connections (you probably didn't know these)
- `keywords()` --calls--> `test_keywords_reused()`  [INFERRED]
  src/substack_toolkit/topics.py → tests/test_media_topics.py
- `Run ORM model` --conceptually_related_to--> `Substack models tests`  [AMBIGUOUS]
  webapp/backend/models.py → tests/test_substack_models.py
- `soic-toolkit` --conceptually_related_to--> `media_core (shared infra package)`  [INFERRED]
  pyproject.toml → CLAUDE.md
- `item_from_post()` --calls--> `test_item_from_post_matches_topics_from_caption()`  [INFERRED]
  src/instagram_toolkit/extract.py → tests/test_instagram_extract.py
- `MediaItem` --calls--> `_media()`  [INFERRED]
  src/media_core/models.py → tests/test_unified_vault.py

## Import Cycles
- None detected.

## Communities (84 total, 26 thin omitted)

### Community 38 - "Brainstorm WS Client"
Cohesion: 0.42
Nodes (7): nextReconnectDelay(), sessionKey(), websocketUrl(), reloadAfterRecovery(), setStatus(), showTombstone(), connect()

### Community 40 - "Brainstorm Stop-Server"
Cohesion: 0.43
Nodes (4): stop-server.sh script, mark_stopped(), command_has_server_id(), is_brainstorm_server()

### Community 4 - "Goal Skill Engine"
Cohesion: 0.13
Nodes (43): now(), _term_session_id(), session_id(), cwd_session_id(), sqlite_connect(), Path, Connection, init_db() (+35 more)

### Community 34 - "SDD Scripts & Graph Render"
Cohesion: 0.25
Nodes (11): render-graphs.js (SKILL.md dot -> SVG), fs, { execSync }, extractDotBlocks(), extractGraphBody(), combineGraphs(), renderToSvg(), main() (+3 more)

### Community 35 - "Project Toolkits Overview"
Cohesion: 0.35
Nodes (11): soic-toolkit, YouTube Capture Skill, Three-Stage Transcript Fallback Chain, CLAUDE.md (knowledge-toolkit project guidance), media_core (shared infra package), substack_toolkit, youtube_toolkit, web_toolkit (+3 more)

### Community 33 - "Learning Pack Scripts & Drive"
Cohesion: 0.31
Nodes (11): gdrive_upload script, gdrive_upload.authenticate (OAuth), get_credentials(), gdrive_upload.upload_file, main(), Google Drive uploader — one-time OAuth setup, then silent uploads.  Usage:   Fir, generate_learning_pack script (Ben Dicken pack), generate_vutr_spark script (Spark pack) (+3 more)

### Community 32 - "Instagram CLI"
Cohesion: 0.17
Nodes (10): Capture public Instagram captions + metadata into the shared media catalog., login(), crawl(), crawl_hashtag(), build(), Command-line interface for the Instagram toolkit: `instagram-toolkit`.  Subcomma, Save an Instagram session cookie — via browser login or by importing Chrome's., Capture a public profile's posts + reels (captions + metadata) — resumable. (+2 more)

### Community 23 - "Instagram Chrome-Cookie Auth"
Cohesion: 0.15
Nodes (15): session_has_auth(), _saved_cookies(), login(), _chrome_key(), _decrypt_cookie(), import_from_chrome(), load_session_into(), Capture the user's Instagram session for the crawler.  Two ways to obtain a sess (+7 more)

### Community 43 - "Instagram Config"
Cohesion: 0.29
Nodes (4): Settings, post_url(), Configuration and paths for the Instagram toolkit.  Instagram capture writes int, Canonical permalink for a shortcode, e.g. 'ABC' -> .../reel/ABC/ or /p/ABC/.

### Community 39 - "Instagram Instaloader Crawler"
Cohesion: 0.39
Nodes (7): _make_loader(), _normalize(), _profile_posts(), _hashtag_posts(), Instaloader-backed Instagram capture into the shared media catalog.  Captures CA, An Instaloader configured to fetch NO media and NO comments., Instaloader Post -> normalized dict (no extra network requests).

### Community 57 - "Instagram Block Handling"
Cohesion: 0.67
Nodes (3): _reraise_as_block(), Exception, Convert a genuine Instagram rate-limit/block error into a friendly message.

### Community 25 - "Substack Crawler (JSON API)"
Cohesion: 0.22
Nodes (15): _run(), channel_url(), Base URL for a publication handle, e.g. 'vutr' -> https://vutr.substack.com., _load_cookie_header(), _default_fetcher(), Fetcher, _load_catalog(), _save_catalog() (+7 more)

### Community 49 - "Instagram Crawl Entry"
Cohesion: 0.40
Nodes (5): crawl(), PostFetch, crawl_hashtag(), Capture a public profile's posts + reels (captions + metadata). Resumable., Discover posts by hashtag (captions + metadata). Resumable.

### Community 5 - "Instagram Auth & Crawl"
Cohesion: 0.06
Nodes (44): _as_dt(), datetime, _title_from_caption(), item_from_post(), Instagram post -> media_core.MediaItem.  The extractor works on a NORMALIZED pos, Coerce a datetime / ISO string / None into a tz-aware datetime., First line of the caption (trimmed), else '@owner · date'., Build a MediaItem (kind=instagram) from a normalized post dict. (+36 more)

### Community 0 - "Media Core (config/models)"
Cohesion: 0.05
Nodes (74): media_core Config, Settings, Configuration and filesystem paths for the media (YouTube + web) toolkit.  Value, MediaItem / MediaCatalog Models, MediaItem, MediaCatalog, Pydantic models for captured media (YouTube videos and web articles).  Intention, Top-level container persisted to data/media.json. (+66 more)

### Community 2 - "Webapp Backend Routers & Models"
Cohesion: 0.11
Nodes (42): BaseModel, Backend database (engine/session), Base, DeclarativeBase, get_db dependency, Run ORM model, Chapter ORM model, PassRecord ORM model (+34 more)

### Community 28 - "SOIC CLI"
Cohesion: 0.14
Nodes (12): soic_toolkit — personal study toolkit for your own SOIC/Learnyst membership.  Lo, login(), status(), crawl(), build_vault(), build_map(), Command-line interface for the SOIC study toolkit.  Subcommands:     login, Open a browser, log in manually, and save the session. (+4 more)

### Community 22 - "SOIC Playwright Auth"
Cohesion: 0.15
Nodes (13): login(), has_saved_session(), session_is_valid(), authenticated_context(), BrowserContext, Interactive authentication and session persistence.  Login is deliberately *manu, Open a browser, let the user log in manually, then save the session., Best-effort check that the saved session still resolves to a logged-in page. (+5 more)

### Community 14 - "SOIC Bodhi Crawler"
Cohesion: 0.15
Nodes (21): load_catalog(), save_catalog(), _polite_sleep(), _bundle_url(), _read_syllabus(), Page, _read_summary(), _course_cards() (+13 more)

### Community 6 - "SOIC Extract / Parse"
Cohesion: 0.08
Nodes (31): _clean_text(), _first_match_text(), BeautifulSoup, extract_title(), extract_body(), extract_captions_url(), extract_resource_links(), derive_key_points() (+23 more)

### Community 36 - "SOIC Mindmap (Markmap)"
Cohesion: 0.27
Nodes (10): _escape(), build_markdown(), write_markdown(), Path, render_html(), build_map(), Turn the captured catalog into a Markmap mind map.  The Markdown produced here i, Render the catalog as nested Markmap Markdown.      Heading levels: course (#) → (+2 more)

### Community 29 - "SOIC Models & Vault Tests"
Cohesion: 0.24
Nodes (10): Lesson, Pydantic models describing the captured course structure.  The shape mirrors a t, SOIC Mindmap Test, _catalog(), test_markdown_hierarchy_and_links(), test_frontmatter_present(), _catalog(), test_build_vault_writes_notes_and_mocs() (+2 more)

### Community 15 - "SOIC Vault Builder"
Cohesion: 0.19
Nodes (22): slugify(), _keywords(), Note, _unique(), _plan_notes(), _compute_related(), _yaml_list(), _transcript_basename() (+14 more)

### Community 1 - "Substack CLI & Commands"
Cohesion: 0.07
Nodes (48): Personal Substack archiver: capture subscribed posts into an Obsidian vault., login(), crawl(), build_vault(), list_topics(), Command-line interface for the Substack toolkit.  Subcommands:     login, Save a Substack session cookie — via browser login or by importing Chrome's., Capture accessible post text into data/substack.json (resumable). (+40 more)

### Community 30 - "Substack Chrome Auth"
Cohesion: 0.19
Nodes (11): session_has_auth(), login(), _chrome_key(), _decrypt_cookie(), import_from_chrome(), Capture the user's Substack session for the crawler.  Two ways to obtain a sessi, True when the saved session actually contains the real auth cookie., Open a browser to the publication, wait for manual login, save cookies. (+3 more)

### Community 44 - "Substack Config"
Cohesion: 0.29
Nodes (4): Settings, ensure_dirs(), Configuration and filesystem paths for the Substack toolkit.  Values come from t, Create the local working directories if they don't already exist.

### Community 18 - "Substack Extract & Topics"
Cohesion: 0.14
Nodes (11): _parse_date(), datetime, enrich(), Convert Substack API JSON into Post models and enrich with topics.  Body HTML is, Attach canonical topics and secondary keyword tags (mutates and returns post)., match_topics(), keywords(), Canonical topic vocabulary and lexical matchers.  This module is the cross-chann (+3 more)

### Community 26 - "Substack Extract Tests"
Cohesion: 0.21
Nodes (16): _is_truncated_preview(), Any, _author(), post_from_api(), True when the API returned only the paywalled preview, not the full body.      S, Build a Post from one Substack ``/api/v1/posts/<slug>`` JSON object., Substack Extract Test, test_post_from_api_maps_fields_and_converts_markdown() (+8 more)

### Community 45 - "Web Toolkit CLI"
Cohesion: 0.29
Nodes (6): capture(), Path, build(), CLI for web article capture: `web-toolkit`., Capture readable article text from one or more web pages (resumable)., Build the unified Obsidian vault (Substack + YouTube + web).

### Community 9 - "YouTube Transcript Capture"
Cohesion: 0.08
Nodes (31): _ydl(), fetch_info(), _flatten_entries(), enumerate_entries(), _vtt_to_text(), fetch_transcript_from_info(), fetch_transcript_via_pytubefix(), fetch_transcript() (+23 more)

### Community 11 - "SOIC Toolkit Suite"
Cohesion: 0.10
Nodes (14): SOIC Crawl Integration Test, _Locator, _FakePage, _FakeContext, test_crawl_persists_resumable_catalog(), End-to-end integration test of the crawl ORCHESTRATION.  The live portal needs P, Replays the captured portal DOM through the Playwright Page surface used by craw, SOIC Auth (Playwright session) (+6 more)

### Community 19 - "YouTube Capture Tests"
Cohesion: 0.14
Nodes (15): Media YouTube Capture Test, _info(), test_capture_single_video(), test_capture_channel_respects_limit_and_resumes(), test_short_video_skipped(), test_missing_transcript_skipped(), Videos ≤60s (Shorts) are skipped regardless of transcript availability., Videos with no transcript are silently skipped (not stored). (+7 more)

### Community 10 - "Substack Toolkit Suite"
Cohesion: 0.10
Nodes (28): Substack Auth Test, _make_chrome_db(), _wire(), test_import_from_chrome_writes_session(), test_import_from_chrome_requires_session_cookie(), Tests for session import from Chrome — crypto/Keychain mocked out.  The AES decr, Build a minimal Chrome-shaped Cookies SQLite at ``path``., Substack Crawl Test (+20 more)

### Community 24 - "Run Detail Page"
Cohesion: 0.17
Nodes (8): AGENT_META, Props, TAG_COLORS, Props, GapsList(), Props, Chapter, Run

### Community 20 - "New Run / Pack Builder Page"
Cohesion: 0.15
Nodes (13): DEFAULT_CHAPTERS, Props, AttentionDigest(), AUTHORS, Props, AuthorChips(), Props, STEPS (+5 more)

### Community 21 - "Runs List Page"
Cohesion: 0.15
Nodes (14): Filter, FilterPills, FILTERS, Filter, Props, FilterPills(), StatsRow, Props (+6 more)

### Community 51 - "Live Log UI"
Cohesion: 0.40
Nodes (3): LogLine, AGENT_COLORS, Props

### Community 48 - "Run Detail Sidebar"
Cohesion: 0.47
Nodes (5): STAGES, STAGE_ORDER, stageSub(), Props, Sidebar()

### Community 46 - "Run List Table UI"
Cohesion: 0.33
Nodes (3): RunListTable, Props, HEADERS

### Community 31 - "Sign-Off Checklist UI"
Cohesion: 0.21
Nodes (8): Props, AGENT_META, Props, Gap, PassRecord, SignOff, DeliveryStep, RunsListResponse

### Community 16 - "Frontend Package Deps"
Cohesion: 0.09
Nodes (22): name, version, private, scripts, dev, build, start, lint (+14 more)

### Community 12 - "Webapp Backend & TS Config"
Cohesion: 0.08
Nodes (24): Frontend Tailwind Config, config, Frontend TypeScript Config, compilerOptions, lib, allowJs, skipLibCheck, strict (+16 more)

### Community 54 - "Brainstorm Server Scripts"
Cohesion: 0.67
Nodes (3): brainstorming helper.js (WS reconnect), brainstorming start-server.sh, brainstorming stop-server.sh

### Community 41 - "Frontend App Routes"
Cohesion: 0.29
Nodes (7): Root layout, Home page (redirect), Run detail page, New run page, Runs list page, Topbar component, Frontend api client (@/lib/api)

### Community 17 - "Frontend Feature Areas"
Cohesion: 0.17
Nodes (19): API Client (api), Frontend Type Models, Color Token Map (C), Pack Builder Feature Area, AttentionDigest, AuthorChips, ChapterFields, ExaminerGrid (+11 more)

### Community 56 - "Frontend Build Config"
Cohesion: 0.67
Nodes (3): Next.js Config, Frontend package.json, PostCSS Config

### Community 7 - "Verification Persona Agents"
Cohesion: 0.08
Nodes (41): Alex Agent (Clarity Auditor), Ben Dicken Agent (DB Examiner), Justin Sung Agent (Learning Coach), Luc Agent (System Design Examiner), sdcourse Agent (Distributed Systems Examiner), Vu Trinh Agent (Data Engineering Examiner), Alex Persona Skill, Ben Dicken Persona Skill (+33 more)

### Community 8 - "Capture Agents & Guardrails"
Cohesion: 0.10
Nodes (36): Media Capturer Agent, Substack Capturer Agent, YouTube Capturer Agent, Unified Obsidian Vault, media_core / topics cross-linking, Substack substack.sid Auth + Paywall Detection, Three-Stage Transcript Fallback Chain, README — SOIC Knowledge Toolkit (+28 more)

### Community 37 - "Brainstorming & Process Skills"
Cohesion: 0.22
Nodes (10): Brainstorming Skill, Brainstorming Frame Template, Spec Document Reviewer Prompt, Brainstorming Visual Companion Guide, Dispatching Parallel Agents Skill, Executing Plans Skill, Finishing a Development Branch Skill, Writing Plans Skill (referenced) (+2 more)

### Community 52 - "Goal Research Notes"
Cohesion: 0.50
Nodes (4): Codex /goal Research Notes, thread_goals SQLite persistence, Soft Token Budget, Completion-Audit Prompt

### Community 13 - "Graphify & Capture Skills"
Cohesion: 0.11
Nodes (23): graphify Skill, Community Detection / Clustering, Honest Audit Trail (EXTRACTED/INFERRED/AMBIGUOUS), AST Structural Extraction, Parallel Semantic Extraction Subagents, Obsidian Vault + HTML Export, Neo4j / GraphML / SVG Export, graphify MCP Server (+15 more)

### Community 42 - "Justin Sung Learning Framework"
Cohesion: 0.33
Nodes (7): Justin Sung Persona Skill, 5 Levels of Learners, Three Encoding Conditions, The Memory Ladder, Retrieval Practice vs Passive Re-reading, 7 Review Criteria for Learning Materials, WHY-WHAT-HOW Structure

### Community 27 - "System Design Concepts (Luc)"
Cohesion: 0.15
Nodes (15): Luc (lucsystemdesign) Persona Skill, CAP Theorem (partition-only framing), Database Selection is a Question Problem, OAuth is Permission not Login, Complexity Relocates, Not Eliminates, Decision Frameworks over Definitions, When NOT to Use X, sdcourse Persona Skill (+7 more)

### Community 3 - "Superpowers Skill Docs"
Cohesion: 0.05
Nodes (47): receiving-code-review Skill, Verify Before Implementing, No Performative Agreement, YAGNI Check, requesting-code-review Skill, Code Reviewer Prompt Template, Severity Categorization (Critical/Important/Minor), subagent-driven-development Skill (+39 more)

## Ambiguous Edges - Review These
- `render-graphs.js (SKILL.md dot -> SVG)` → `sdd task-brief script`  [AMBIGUOUS]
  .claude/skills/writing-skills/render-graphs.js · relation: conceptually_related_to
- `Run ORM model` → `Substack models tests`  [AMBIGUOUS]
  tests/test_substack_models.py · relation: conceptually_related_to
- `CAP Theorem (partition-only framing)` → `Field-Level Encryption / TLS`  [AMBIGUOUS]
  .claude/skills/lucsystemdesign-persona/SKILL.md · relation: conceptually_related_to
- `Learnyst Bodhi Portal (Shadow DOM PWA)` → `Chrome Keychain Cookie Decryption`  [AMBIGUOUS]
  .claude/skills/substack-capture/SKILL.md · relation: conceptually_related_to

## Knowledge Gaps
- **192 isolated node(s):** `find-polluter.sh script`, `fs`, `{ execSync }`, `Settings`, `Settings` (+187 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **26 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `render-graphs.js (SKILL.md dot -> SVG)` and `sdd task-brief script`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Run ORM model` and `Substack models tests`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `CAP Theorem (partition-only framing)` and `Field-Level Encryption / TLS`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Learnyst Bodhi Portal (Shadow DOM PWA)` and `Chrome Keychain Cookie Decryption`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `MediaCatalog` connect `Media Core (config/models)` to `Substack CLI & Commands`, `Webapp Backend Routers & Models`, `Instagram Auth & Crawl`, `YouTube Transcript Capture`, `Instagram Crawl Entry`, `Substack Crawler (JSON API)`?**
  _High betweenness centrality (0.070) - this node is a cross-community bridge._
- **Why does `MediaItem / MediaCatalog Models` connect `Media Core (config/models)` to `Substack CLI & Commands`, `Webapp Backend Routers & Models`, `Instagram Auth & Crawl`, `Instagram Instaloader Crawler`, `YouTube Transcript Capture`?**
  _High betweenness centrality (0.054) - this node is a cross-community bridge._
- **Why does `media_core Unified Vault Builder` connect `Media Core (config/models)` to `YouTube Capture Tests`, `Substack Toolkit Suite`, `SOIC Toolkit Suite`, `Instagram Auth & Crawl`?**
  _High betweenness centrality (0.053) - this node is a cross-community bridge._