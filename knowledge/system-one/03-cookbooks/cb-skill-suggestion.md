---
title: Skill Suggestion
kind: cookbook
source: Skill suggestion (TypeSafe cookbook)
source_url: https://docs.typesafe.ai/cookbooks/skill_suggestion
tags: [cookbook, retrieval-rerank, agent-tooling]
topics: [topic-agent-integration, topic-retrieval-rerank, topic-routing, topic-cost-latency]
---
# Skill Suggestion
> Pick at most one skill for an agent turn out of the 182 in Nous Research's Hermes catalog using two TypeSafe requests (rank all, then re-check top 3). Cuts wrong skill loads 16.8% -> 7.3% and needless loads 9.8% -> 4.0%.

## What it is / How it works
Problem: agents choose skills from an index of one line per skill with descriptions truncated (Hermes cuts to 60 characters by default). At that width the skill that *edits* `.pptx` reads nearly the same as the one that *authors* them; and when no skill fits, a list of names invites a guess ("err on the side of loading"). Loading all skills into the system message raises cost, degrades selection, and induces context rot.

Fix = progressive disclosure, descriptions untouched: read all 182 cheaply, then read three in detail. Two TypeSafe requests precede the load decision:
1. **Wide request (call 1)** - ranks every skill vs the user's turn AND answers whether the turn needs a skill at all.
2. **Rerank request (call 2)** - re-reads only the top 3 with full description + opening of SKILL.md; free to reject all.

Winner goes into one extra system-prompt block for that turn, placed AFTER the roster so the roster text is identical every turn and prefix caching holds:
```
<skill_relevance>
Relevant to the current request: pptx-author. Ignore this if it does not fit what the user
actually asked for.
</skill_relevance>
```
The agent keeps its full index and own judgement; the line only says which entry to look at first. With nothing to suggest, the block still says "No skill in the roster appears relevant to this request." (sending nothing would leave the roster's own "err on the side of loading" instruction unopposed).

Deliverables: `suggest()` returns at most one skill name (or `()`), `suggestion_block()` wraps it, plus the measurement harness. To use your own roster, replace `hermes_roster.json` - every question reads `name`, `description`, `description_full`, `body` and nothing else knows Hermes.

### Call 1: rank the whole roster (`rank_wide`)
Questions in ONE `system_one` request (`state = {"request": request, "recent_context": ""}`):
- `which`: [[choice]] over all 182 skill names; criteria = each skill's index description (same text the agent sees); instructions "Which of these skills, if any, is the right one to load to help with the user's latest request?". Probabilities = ranking (top 12 kept in cache).
- Three gate [[noul]] questions (`gate::<key>`), no custom criteria, each asking whether an ACTION is wanted rather than an explanation:
  - `acts_on_user_system`: asked to act on user's files, accounts, devices, online services, rather than only explain/advise?
  - `would_follow_documented_procedure`: would a careful expert consult a specific documented procedure/commands rather than answer from general understanding?
  - `prose_suffices` (INVERTED): could a knowledgeable generalist fully satisfy this in prose with no tools/docs/file access? A yes points AWAY from a skill, so its value becomes `1 - v`.
- `gate` = mean of the three oriented nouls; **gate < 0.30 (`GATE_THRESHOLD`) -> suggest nothing**.
- Write gate questions to ask whether an action is wanted; a subject-matter question would not separate "explain what a monad is" from a skill-needing request, since both are software.
- One Choice holds this roster size comfortably; a few times larger -> split into chunks, rank each, run the same shortlist step over the winners.

### Call 2: rerank the top three (`rerank`)
- `SHORTLIST = 3`; `EXCERPT_CHARS = 700` of SKILL.md body per candidate (roster file stores 1600; asserted <= 1600).
- `which`: Choice over the 3, criteria = `description_full — body[:700]`; instructions "Exactly one of these skills is the right one to load... Read what each actually does, not just its name."
- `fits::{name}`: one [[noul]] per candidate: "Does the skill 'X' do the specific thing the user's request asks for? It is described as: <description_full>". Answered independently, so all can come back low.
- If max fits noul < **0.30 (`FITS_THRESHOLD`)** the shortlist is dropped (nothing suggested). Else the Choice winner is suggested.
- Choice and nouls decide different things: Choice settles WHICH skill; nouls settle WHETHER to say anything.

```python
def suggest(request):
    wide = rank_wide(request)
    if wide["gate"] < GATE_THRESHOLD: return ()
    shortlist = tuple(n for n,_ in wide["ranked"][:SHORTLIST])
    result = rerank(request, shortlist, EXCERPT_CHARS)
    if max(result["fits"].values()) < FITS_THRESHOLD: return ()
    return (result["winner"],)
```

## When to use / when NOT to use
- Use when an agent carries a large roster (skills, tools) and descriptions must be truncated. Shape: cheap ranking over everything, then a close look at two or three; either step may come back empty-handed.
- Limits: the second pass can only reject what the wide ranking hands it; near-miss shortlists can survive both checks (Mastodon example).
- A confident wrong suggestion is more persuasive than none (7 regressions below).

## Dataset and measurement design
- Roster: `hermes_roster.json` = **182 skills in 33 categories** of NousResearch/hermes-agent (MIT) at one pinned commit. Roster prompt 16,089 characters; index descriptions average 54 characters, max 60. Prompt text (PREAMBLE, IDENTITY, FOOTER) copied verbatim from Hermes `agent/prompt_builder.py:build_skills_system_prompt`; `skill_view` tool schema from `tools/skills_tool.py:SKILL_VIEW_SCHEMA`.
- Requests: `requests.json` = **488 single-turn requests**: **315 covered** by exactly one skill (171 distinct skills; written by Claude Sonnet 5 from each skill's own SKILL.md, so labels are trustworthy and requests easier than real user ones) and **173 uncovered**, all written to punish guessing: **85** everyday requests, **42** technical questions no skill serves (e.g. "explain what a monad is"), **46** asking for something specific the roster lacks (e.g. "post this to Mastodon" when the roster covers X only).
- Agent under test: `claude-haiku-4-5-20251001` (pinned), `max_tokens=1024`, tools `skill_view(name)`, `terminal`, `read_file`, `web_search`; roster in system block with `cache_control: ephemeral`, suggestion block after the breakpoint. `skill_view` takes a free-text name that must match exactly. Scoring reads the agent's FIRST response only.
- Metrics (both error rates, lower is better): **wrong load** = covered requests where the first `skill_view` was not the covering skill (loading nothing counts as a miss); **needless load** = uncovered requests where the agent called `skill_view` at all.
- Three arms, each request run once per arm: agent alone (nothing); with suggestion (`suggest()` output); agent given the answer ("oracle": covering skill name, or "nothing applies") - a ceiling, not achievable.
- Run params: `WORKERS = 8`; published run `jev-1.12` + `claude-haiku-4-5-20251001`, rendered 2026-07-31; up to 488 x 2 TypeSafe requests.

## Results
| Arm | Wrong load (315 covered) | Needless load (173 uncovered) |
|---|---|---|
| agent alone (roster only) | 16.8% | 9.8% |
| **agent + TypeSafe suggestion** | **7.3%** | **4.0%** |
| oracle (handed the right answer) | 2.5% | 1.2% |

- baseline -> TypeSafe: **2.3x fewer** wrong loads, **2.4x fewer** needless ones. Source summary: cuts incorrect skill loads "by more than half"; most of the gap between guessing from a truncated index and being handed the answer.
- Floor is not zero: an agent handed the right skill still does not always load it; no method gets past that.
- Of 315 covered requests: the suggestion **fixed 37, broke 7**.
- Baseline wrong picks: of **36** wrong first picks, **10** came from the right skill's own category -> the hard part is telling lookalikes apart; the agent is already looking in roughly the right place.
- Suggestion wording does two jobs: it says it can be ignored (pushing harder wins compliance on wrong suggestions too, and a wrong one is worse than none), and the no-suggestion turn still sends a sentence saying so. The block string is a measured input: part of every graded turn's cache key; editing a word invalidates shipped cached results.

## Worked examples (demo requests)
| Request | Call-1 gate | Call-1 top 3 (prob) | Call-2 fits | Outcome |
|---|---|---|---|---|
| Save recipe as note in 'Recipes' folder in Notes.app (syncs to phone) | 0.75 suggest (0.31s) | apple-notes 0.990, computer-use 0.010, concept-diagrams 0.000 | apple-notes 0.60, computer-use 0.54, concept-diagrams 0.01 (0.12s) | apple-notes |
| Pitch deck skeleton (.pptx; firm-template.pptx branding; footnote valuation numbers to model cells) | 0.76 suggest (0.16s) | powerpoint 0.700, pptx-author 0.300, chroma 0.000 | powerpoint 0.73, pptx-author 0.38, chroma 0.02 (0.09s) | was powerpoint -> **pptx-author** |
| Post this announcement to my Mastodon account | 0.78 suggest (0.16s) | xurl 0.550, computer-use 0.140, openhands 0.080 | xurl 0.56, computer-use 0.38, openhands 0.05 (0.09s) | xurl (wrong: no Mastodon skill) |

Lessons:
- Deck case: on 60-char descriptions the wide Choice puts the editing skill (powerpoint: "Create, read, edit .pptx decks...") ahead of the authoring one (pptx-author: "Build PowerPoint decks headless with python-pptx") for an authoring request; the two separate once each brings its own full text, and the Choice flips to authoring. Here the nouls scored the editing skill higher (0.73 vs 0.38) while the Choice picked the authoring one: they decide different things.
- Mastodon case: all three gate questions say a skill is wanted (posting is an action) and the closest skill wins anyway; best `fits` noul 0.56 > 0.30 so it survives both checks. "Most requests like it are caught" but not all; no ranking can save it.

## Numbers & limits
| Item | Value |
|---|---|
| Roster | 182 skills, 33 categories, 16,089-char prompt |
| Index description | avg 54 chars, max 60 (Hermes default cut 60) |
| SHORTLIST | 3 |
| EXCERPT_CHARS | 700 (file stores 1600) |
| GATE_THRESHOLD | 0.30 (mean of 3 nouls) |
| FITS_THRESHOLD | 0.30 (best fits noul) |
| Call-1 latency (demo) | 0.31s, 0.16s, 0.16s |
| Call-2 latency (demo) | 0.12s, 0.09s, 0.09s |
| Test set | 488 requests (315 covered / 173 uncovered) |
| Thread workers | 8 |

## Gotchas
- Gate is a mean, not a max; `prose_suffices` must be inverted before averaging.
- Suggestion can break previously-correct turns (7 of 315).
- Keep the suggestion block AFTER the roster to preserve prefix caching.
- Covered-request labels were generated from the skills' own SKILL.md, so real accuracy on user phrasing is likely lower [inference; source says requests are "easier than the ones users send"].
- Thresholds (0.30/0.30) are chosen per the Confidence page; see [[confidence]].

## Related
[[choice]], [[noul]], [[intent-routing]], [[speculative-fan-out]], [[confidence-gated-routing]], [[confidence]], [[cb-reranking]], [[typesafe-agent-skill]], [[jev-with-coding-agents]], [[topic-agent-integration]], [[cookbooks-overview]]
