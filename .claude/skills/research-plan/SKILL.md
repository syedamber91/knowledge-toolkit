---
name: research-plan
description: Turn a high-level goal or use case (e.g. "find business opportunities and market gaps in Bhopal, India") into a vetted, token-thrifty capture plan. Reasons out a research approach, autonomously discovers the SPECIFIC Substack channels/blogs, YouTube videos/channels and web pages worth reading, filters out the noise, and presents a prioritized shortlist for approval BEFORE any extraction runs. Use when asked to research a topic/market/question and decide what is worth capturing, or to plan a capture before scraping.
trigger: /research-plan
---

# Research Planning Skill (goal → vetted capture manifest)

Turn a fuzzy goal into a **prioritized, justified shortlist** of sources worth
capturing — and just as importantly, an explicit list of what to **ignore**.
This is the planning front-end that sits *before* the five capture toolkits. It
exists to **save tokens**: discovery and judgment ("which of these 200 YouTube
videos actually matter?") happen here, cheaply, so that expensive transcript /
post / article extraction only ever runs on sources that earned their place.

> **Personal use only.** Discovery uses openly available web-search results.
> No DRM circumvention, no stored passwords, nothing captured is ever committed.
> This skill plans and shortlists — it does **not** capture until you approve.

## Why this exists

Every toolkit in this repo is **URL/handle-driven**: you must already know the
source. `substack-toolkit crawl <handle>`, `youtube-toolkit capture <url>`,
`web-toolkit capture <url…>` each capture a source you hand them — there is no
discovery, ranking, or relevance logic in `src/`. The post-capture topic tagger
(`match_topics()` in `topics.py`) is tech/data-engineering specific and useless
for a general goal like "business in Bhopal." This skill fills that gap: it
decides **what is worth capturing** before a single extraction token is spent.

## The five phases

Run these in order. **Phases 0–4 are cheap (planning + web search). Phase 5
[extraction] only starts after the user approves the manifest.**

### Phase 0 — Intake & clarify (the token gate)

Before searching anything, pin down what "beneficial" means for *this* goal using
`AskUserQuestion`. Ask only what materially changes the search and the filter:

- **Geography / locale** — where does this apply? (e.g. Bhopal, India)
- **Domain(s)** — sectors or angles in scope vs. out of scope.
- **Time horizon / recency** — how fresh must sources be? (kill stale content)
- **What a "good find" looks like** — the signal you actually want (e.g.
  "a concrete US business model that's transplantable to a tier-2 Indian city",
  not generic motivation).
- **Output language** — for the brief and for filtering non-target-language noise.
- **Must-include / must-exclude** — any known sources to seed or to ban.
- **Depth / effort budget** — how many sources to shortlist and how aggressive
  the noise filter should be (this directly bounds token spend downstream).

Do not skip this. A vague goal is the main cause of wasted discovery tokens.

### Phase 1 — Research plan + per-goal relevance rubric

Decompose the goal into **4–8 concrete sub-questions** the research must answer.
Then write a **goal-specific relevance rubric** generated on the fly (do NOT
touch the static `TOPIC_VOCABULARY` — that is for post-capture tech tagging, a
different job). The rubric has three parts:

1. **Weighted criteria** — score axes such as *relevance to the sub-questions*,
   *author authority/credibility*, *recency*, *specificity / actionability*, plus
   **goal-specific axes**. (For Bhopal: *transplantability of a US model to a
   tier-2 Indian city*, *evidence of a real local-market gap*.)
2. **Positive signals** — keywords, entities, channel types that indicate value.
3. **Disqualifiers (noise filter)** — what to reject on sight: generic
   motivational content, SEO listicles, outdated posts, hype with no specifics,
   wrong geography, pure advertising, duplicate aggregators.

Present the plan + rubric to the user before discovering (one short message).

### Phase 2 — Autonomous discovery (cast wide, cap hard)

Run `WebSearch` / `WebFetch` passes per channel type, querying around the
sub-questions. Cover all four capture-able channel types:

- **Substack** publications (newsletters/blogs on Substack).
- **Standalone blogs** / web pages (independent sites, news, reports).
- **YouTube** — both whole **channels** and **specific high-value videos**.
- **Web pages** — individual articles/reports worth reading in full.

**Cap candidates per channel** (e.g. ≤ 8–10 each, tuned to the Phase-0 budget) so
discovery itself stays cheap. For each candidate collect: URL/handle, title +
author, a one-line *why-it-might-matter*, and a freshness signal (date). Prefer
search/preview snippets over fetching full pages — only `WebFetch` a page when
its value is genuinely ambiguous and the decision hinges on it.

### Phase 3 — Score & shortlist (kill the noise, auditably)

Score every candidate against the Phase-1 rubric. Produce **two explicit lists**:

- **Shortlist (ranked)** — each entry: source, channel type, score, and a
  one-line rationale tied to the rubric. These are what you'll capture.
- **Rejected as noise** — each entry: source + a one-line reason it failed the
  filter (so the filtering is transparent and reviewable, not a black box).

Then add a **token/effort estimate** for capturing the shortlist (rough order of
magnitude — e.g. "12 sources ≈ ~8 YouTube transcripts + 3 articles + 1 Substack
crawl"), so the user can trade depth for cost before approving.

### Phase 4 — Emit manifest & STOP for approval

Write a **research brief + capture manifest** to a gitignored artifact at
`output/research/<goal-slug>.md` (the `output/` tree is gitignored — never commit
it). The manifest must include, for each shortlisted source, the **exact capture
command**, using the authoritative syntax from `pyproject.toml [project.scripts]`
(NOT the README, which has known drift):

```bash
substack-toolkit crawl <handle> [--limit N] [--free-only]
youtube-toolkit  capture "<video-or-channel-or-playlist-url>" [--limit N]
web-toolkit      capture "<article-url>" [...]        # or --file urls.txt
```

Present the shortlist, the rejected-as-noise list, and the token estimate, then
**STOP**. Do not capture anything yet. Wait for the user to approve, trim, or
adjust the shortlist.

### Phase 5 — Hand off to capture (only after approval)

Once approved, delegate extraction to the **existing** capture skills/agents —
do not reimplement capture here:

- Substack → `/substack-capture` skill or the `substack-capturer` agent.
- YouTube → `/youtube-capture` skill or the `youtube-capturer` agent.
- YouTube + web together → `/media-capture` skill or the `media-capturer` agent.

Capture with a small `--limit` first to sanity-check, then the full (resumable)
run. Finally build the unified vault (`youtube-toolkit build`) so the captured
posts/videos/articles cross-link by shared topic via the existing
`topics/<slug>.md` machinery. Report concrete numbers; never claim success
without verifying.

## Worked example — "business opportunities & market gaps in Bhopal, India"

- **Phase 0:** Confirm locale = Bhopal (tier-2, India); domains = retail / D2C /
  local services / agritech; horizon = last ~2–3 years; "good find" = a US/metro
  model with evidence it transplants to a tier-2 Indian city; exclude generic
  "top 10 business ideas" listicles; shortlist ~12 sources.
- **Phase 1 sub-questions:** What unmet needs exist in tier-2 Indian cities?
  Which US/metro models have been localized successfully in tier-2 India? What's
  Bhopal's specific demographic/economic profile? Where are competitors thin?
  Rubric goal-axes: *transplantability*, *local-gap evidence*, *recency*.
- **Phase 2:** Search for India-tier-2-market Substacks (e.g. startup/D2C
  newsletters), YouTube channels on Indian small-business/local entrepreneurship
  + specific case-study videos, and web reports on Bhopal's economy.
- **Phase 3:** Shortlist the ones with concrete, recent, transplantable case
  studies; reject motivational "crore in 30 days" videos, undated SEO listicles,
  and metro-only content as noise (with reasons).
- **Phase 4:** Write `output/research/bhopal-business-opportunities.md` with the
  ranked manifest + exact `youtube-toolkit capture …` / `web-toolkit capture …` /
  `substack-toolkit crawl …` commands + token estimate, then stop for approval.
- **Phase 5:** After approval, run the capture skills, build the vault, report
  what was captured (items by kind, transcript/body sizes, topics, broken links).

## Guardrails (non-negotiable)

- **Personal use only**; discovery uses only openly available results.
- **No DRM circumvention, no stored passwords** (capture uses the existing
  session-cookie / interactive auth only).
- **Nothing captured or derived is committed** — briefs live under gitignored
  `output/`; `data/` and the vaults are gitignored too.
- **Stop at the approval gate.** Extraction never runs in Phases 0–4.
