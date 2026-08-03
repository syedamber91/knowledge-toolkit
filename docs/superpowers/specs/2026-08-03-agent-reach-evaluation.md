# Agent Reach — evaluation & selective-adoption decision

**Date:** 2026-08-03
**Status:** Evaluation complete → **research lane BUILT** (2026-08-03, owner-approved
scope: Exa + X + Reddit + RSS). Capture lane not built — see "What is built" below.
**Subject:** [`Panniantong/Agent-Reach`](https://github.com/Panniantong/Agent-Reach) (MIT, Python 3.10+, ~30k+ stars)
**Author:** researched from the upstream README/`docs/install.md`/`docs/README_en.md`;
written as an anti-sycophantic review at the owner's standing request

## What it actually is

A **capability layer**, not a library: an installer + health-checker + router that
selects among third-party CLIs per platform and fails over between them. Its own
README is explicit — *"负责选型、安装、体检、路由，不负责底层读取本身"* (it handles
selection, install, health-check and routing; it does not do the reading itself).
After install the agent calls the upstream tools **directly** (`yt-dlp`, `twitter`,
`bili`, `rdt`, `gh`, `opencli`, `mcporter`), so Agent Reach is not in the runtime
path — it is a bootstrapper and a routing table.

Install is: `pipx install https://github.com/Panniantong/agent-reach/archive/main.zip`
then `agent-reach install --env=auto`. Credentials live in `~/.agent-reach/config.yaml`
(mode 600), user-exported via Cookie-Editor; nothing is transmitted externally. It
writes only under `~/.agent-reach/` and `/tmp`, and its install doc explicitly forbids
the agent from running `sudo`, touching system files, or installing unlisted packages.

## Channel-by-channel audit against what this repo already has

This is the part that decides the answer. Of the 15 channels:

| Agent Reach channel | Backend | Verdict for **this** repo |
|---|---|---|
| YouTube | yt-dlp | **Already have, and ours is better.** `youtube_toolkit` has a documented 3-stage fallback (yt-dlp VTT → pytubefix → youtube-transcript-api). Agent Reach is single-backend yt-dlp. Adopting = regression. |
| Web | Jina Reader | **Already have, and ours is more private.** `web_toolkit` uses local `trafilatura`; Jina Reader routes page fetches through a third-party service. |
| Instagram | OpenCLI (desktop browser session) | **Already have, and ours is better-suited.** `instagram_toolkit` uses Instaloader + `sessionid`; Agent Reach's path needs a logged-in desktop Chrome, which is worse for scripted/resumable capture. |
| **Twitter/X** | twitter-cli + `TWITTER_AUTH_TOKEN`/`TWITTER_CT0` | **The real prize.** Genuinely hard to DIY, no existing coverage here. |
| **Exa web search** | via mcporter, no API key | **Genuinely useful**, and to a *different* consumer — see "two lanes" below. |
| Reddit | OpenCLI ▶ rdt-cli | Useful, but **login required either way** — upstream states anonymous endpoints are blocked. The OpenCLI path wants desktop Chrome; this repo already owns that pattern via Playwright (SOIC/Substack). Buildable natively. |
| RSS | feedparser | Useful and **trivially native** — one small dep, no new supply chain. |
| GitHub | gh CLI | Marginal for a knowledge vault. |
| LinkedIn | linkedin-scraper-mcp ▶ Jina Reader | Public pages only without the MCP; low value, high ToS risk. |
| V2EX · Bilibili · XiaoHongShu · Xueqiu · Xiaoyuzhou | various | **Chinese-language platforms.** Near-zero relevance to this vault (Indian equities via SOIC, English AI/dev content). Xueqiu is a Chinese retail-stock forum, not a substitute for anything here. |

**Net tally: 2 genuinely valuable net-new (X/Twitter, Exa), 2 cheap-to-DIY net-new
(RSS, Reddit), 3 duplicate-and-would-regress, 6 effectively irrelevant.**

Installing an 8-tool bootstrapper to obtain what is realistically **one platform plus
one search backend** is a poor trade at face value. The recommendation below is what
makes it a good trade instead.

## The reframe that makes it worth adopting: two lanes, not one

The instinct "add it to the capture toolkits" is the wrong seam, because Agent Reach
and the capture toolkits solve different halves:

- **Capture lane** (`*_toolkit` → `media_core` catalog → Obsidian vault). Needs a
  *stable schema contract*: Pydantic `MediaItem`s, resumable crawls, dedup on seen
  URLs, and the mandatory **index + log + cross-links** vault pattern. Agent Reach
  emits **unstructured text to stdout with no schema guarantee**, and its whole design
  premise is that the backend behind a channel *changes over time* (it retired yt-dlp
  for Bilibili in June 2026 after a 412 block). A pipeline that must produce
  byte-stable catalogs should not sit on a deliberately-shifting substrate.
- **Research lane** (`/storm`, `/vault-ask`). Ephemeral, breadth-first, one-shot,
  no catalog, no vault write, tolerant of a backend swapping underneath it. **This is
  exactly what Agent Reach is built for**, and `storm_core` currently has no live
  retrieval breadth at all beyond what the model already knows.

**So: adopt Agent Reach for the research lane, not the capture lane.** That is where
"better reach and broader analysis" actually lands, and it needs no catalog/vault work.

## Risks — stated plainly

1. **Unpinned supply chain, and you have been burned by this exact failure class.**
   The install pulls `archive/main.zip` — i.e. **whatever `main` is at that moment** —
   plus Node, mcporter, gh, yt-dlp, twitter-cli, bili-cli, rdt-cli and OpenCLI, each
   independently unpinned. This is structurally identical to `stock_analyzer`'s
   `notebooklm_mcp` (a third-party fork, `uv tool install`ed from `main`), which broke
   on an upstream fingerprint change and now requires a build-time monkey-patch to stay
   alive. **Pin to a commit SHA, or accept the same class of outage.**
2. **Account-ban exposure across four platforms at once.** X, Reddit, Instagram and
   LinkedIn cookie-scraping all risk suspension. This repo's existing guardrail
   ("use a burner account", `instagram_toolkit`) must extend to every channel enabled —
   not the owner's primary X account.
3. **ToS.** Same standing posture as the rest of the repo: personal use, only text the
   platform openly renders, nothing captured is committed. Enabling LinkedIn in
   particular buys the most ToS risk for the least content value.
4. **Install-by-agent.** The documented install is "point your agent at a remote
   markdown file and let it execute the steps." The doc is well-behaved (no sudo, no
   remote script execution, user-dir only) — but the pattern means the instruction set
   can change upstream between reads. Read the pinned copy, then run the commands.
5. **No schema contract** — restated because it is the load-bearing reason for the
   two-lane split above, not a nitpick.

## Recommendation

**Adopt selectively; do not wholesale-install into the capture pipeline.**

1. **Research lane (primary win).** Wire Agent Reach's `web_search` (Exa) + X + Reddit
   channels into `storm_core` as an optional retrieval breadth layer, pinned to a
   commit, feature-flagged off by default, and **absent-safe** (STORM must still run
   exactly as today when Agent Reach is not installed — same discipline as
   `tvgp_reconcile`'s absent-safe rule in the sibling repo).
2. **Capture lane (one platform only, if wanted).** X/Twitter is the only channel worth
   a real `x_toolkit`, and even then the honest build is *twitter-cli behind our own
   `capture.py`*, producing `media_core.MediaItem`s, with the full index + log +
   cross-links vault contract and the 4-test log shape. RSS is cheaper to build
   natively than to route through Agent Reach.
3. **Do not** replace `youtube_toolkit`, `web_toolkit` or `instagram_toolkit`. All three
   would regress.
4. **Do not** enable the Chinese-platform channels or LinkedIn.

## What is built (2026-08-03)

Owner picked the **research lane** with **all four** channels (Exa, X, Reddit, RSS).

| File | Role |
|---|---|
| `configs/reach_channels.yaml` | Channel registry: name, auth requirement, enabled flag, **argv template**. The argv lives in config so a renamed upstream command is a YAML edit, not a code change — the direct mitigation for the unpinned-install risk. |
| `src/storm_core/reach.py` | `load_channels` / `pinned_ref` / `probe` / `search` / `normalize`. Pydantic models (`ReachChannel`, `ChannelStatus`, `ReachResult`, `ReachSearch`), `run`/`which` seams injected for offline tests. |
| `src/storm_core/config.py` | `REACH_CONFIG`, `REACH_TIMEOUT_SEC` (60s), `reach_enabled()` — reads `STORM_REACH_ENABLED`, **off unless truthy**. |
| `src/storm_core/__main__.py` | `python -m storm_core reach-probe` and `… reach --query … [--channels …] [--limit N]`, both printing JSON like `roster` does. |
| `.claude/workflows/storm.js` | Phase 0 runs `reach-probe` once and returns `reach_channels`; the Phase-1 lens prompt gains a hint **only when a channel is live**. Empty list ⇒ the prompt is byte-for-byte what it was before. |
| `tests/test_storm_reach.py` | 23 offline tests — no Agent Reach install, no credentials, no network. |

**The absent-safe contract, which the tests pin:** layer disabled, registry missing,
registry malformed, command not on PATH, non-zero exit, subprocess raising, timeout,
empty stdout — **every one is a skip carrying a human-readable reason**, never an
exception, and `reach --query …` exits 0 regardless so it can never fail a STORM run.

**Output normalization is best-effort by design.** The channels front independent CLIs
with no shared output contract, so `normalize()` tries JSON (list, `{results:[…]}`,
or a single object, with key aliasing), then URL-bearing lines, then keeps the raw
text as one result. Returning unparsed text is deliberate: a format change should
surface as odd-looking evidence a lens can still read, not as a silently empty result.

**One real bug found while building:** YAML 1.1 parses a bare `off`/`on`/`no`/`yes`
as a boolean, so a channel named that way arrived as `False` and was silently dropped
from the registry. `load_channels` now coerces the name instead of dropping it. Quote
such names in the registry.

**Verification:** `python -m pytest` → 523 passed (500 before), the same **9 pre-existing
failures** in `test_storm_cli.py` / `test_soic_wiki_*` both before and after — those
hardcode the author's macOS venv path and cannot run outside that machine. `node --check`
passes on the workflow. Nothing new was broken.

## Still not done, deliberately

- **No capture-lane toolkit.** No `x_toolkit`; nothing writes to a catalog or a vault.
  The research lane is read-only and ephemeral by design.
- **No installation performed, and no argv confirmed against a live install.** Agent
  Reach installs to `~/.agent-reach` on the owner's own machine with live browser
  cookies a human must export. The registry's `reach_*` command names are what upstream
  documents — `python -m storm_core reach-probe` is the one-command way to confirm them,
  and a wrong name is a one-line YAML fix.

## First-run checklist for the owner

1. Install Agent Reach on the Mac, then **record the commit SHA in
   `configs/reach_channels.yaml`'s `pinned_ref`** — it installs from `archive/main.zip`
   (unpinned), so this is the only place drift becomes visible in git.
2. `agent-reach doctor`, then `python -m storm_core reach-probe`. Fix any channel whose
   `argv[0]` doesn't resolve, in the YAML.
3. Configure X and Reddit **on burner accounts** — not the primary ones.
4. `export STORM_REACH_ENABLED=1`, then run `/storm` as usual. With the flag unset,
   STORM behaves exactly as it did before this layer existed.
