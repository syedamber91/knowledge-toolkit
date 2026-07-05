# Nate Herk & Jack Roberts Persona Design

**Date:** 2026-07-05
**Status:** Approved

## Purpose

The user captured 406 YouTube transcripts from two AI/automation creators —
Nate Herk (`@nateherk`, 259 videos) and Jack Roberts (`@Itssssss_Jack`, 147
videos) — into the new "AI & Development" Obsidian vault (see
[`docs/END_TO_END_PLAN.md`](../END_TO_END_PLAN.md) for the capture toolkit).
Both channels cover AI agents, MCP, Claude/LLM tooling, and automation
workflows, mixing durable concepts with fast-moving tool news.

The user wants to **learn from them directly**, as a curious 15-year-old
with no prior AI/dev background. The deliverable is two persona assets —
grounded in the actual captured transcripts, not fabricated — that can be
invoked as mentors in future Claude Code sessions.

This follows the existing persona pattern already used in this repo for
`vutr`, `ben-dicken`, `justin-sung`, `lucsystemdesign`, and `sdcourse`
(`.claude/agents/<name>.md` + `.claude/skills/<name>-persona/SKILL.md`), but
adapts the **role** from "examiner that quizzes and scores" to **"direct
mentor that teaches free-form."**

## Scope decisions (from brainstorming)

1. **Content scope:** durable concepts and frameworks are primary (agent
   design patterns, prompting technique, MCP/tool-use patterns, automation
   workflow philosophy) illustrated with specific videos as examples — not a
   quiz-grade catalog of every tool review. A secondary **dated tool-timeline
   appendix** captures the fast-moving tool opinions, explicitly timestamped
   so staleness is visible.
2. **Persona role:** direct mentor, not examiner. No question-generation or
   answer-scoring mechanism (unlike vutr/ben-dicken). Free-form Q&A in the
   creator's real voice, calibrated to explain concepts to a beginner.

## Extraction pipeline (data flow)

Two personas require grounding in ~13M characters of real transcript across
406 notes — too much to read directly in one pass. Extraction is batched and
parallelized:

1. **Batch the vault notes per channel:**
   - Nate Herk: 259 notes → 6 batches (~40-45 videos each)
   - Jack Roberts: 147 notes → 4 batches (~35-40 videos each)
2. **Fan out one extraction agent per batch** (10 total, run in parallel via
   the `Agent` tool). Each agent reads its assigned vault note files
   (`youtube/nate-herk-ai-automation/*.md` or `youtube/jack-roberts/*.md`)
   and returns a structured summary:
   - Recurring teaching concepts/frameworks observed in this batch, with
     verbatim quotes
   - Named tools/products mentioned, the creator's stated verdict, and the
     video's `published` date (from frontmatter)
   - Notable voice/style traits (catchphrases, delivery patterns, recurring
     structural devices)
3. **Synthesize** all batch outputs into the final persona files (done
   directly in the main conversation, not delegated — batch outputs are
   condensed enough to fit in context together).
4. Cross-check for internal consistency (no contradicting positions
   attributed to the same person, no duplicate/hallucinated quotes) before
   finalizing.

## Deliverables

```
.claude/agents/nate-herk.md              # dense reference persona
.claude/skills/nate-herk-persona/SKILL.md    # /nate-herk trigger
.claude/agents/jack-roberts.md
.claude/skills/jack-roberts-persona/SKILL.md # /jack-roberts trigger
```

### Content structure (each persona)

1. **IDENTITY** — who they are, teaching style/voice, tone, signature
   phrases, production quirks, channel focus (based on actual observed
   patterns across their videos, not assumed).
2. **CORE TEACHING FRAMEWORKS** — durable concepts grouped by theme (e.g.
   agent design principles, MCP/tool-use patterns, prompting technique,
   automation workflow philosophy, career/learning philosophy for
   AI-builders). Each theme includes bullet positions plus verbatim quotes
   pulled from the real transcripts, matching the density of the existing
   `vutr.md` reference sections.
3. **TOOL TIMELINE (dated appendix)** — chronological log: `[date] Tool/
   product name — creator's verdict`, explicitly framed as "opinion at time
   of recording, may be stale by the time you read this."
4. **MENTOR INSTRUCTIONS** — tells Claude to embody this person and explain
   concepts calibrated for a beginner: plain language first, analogies
   before jargon, define terms inline at first use, no assumed prior
   AI/dev context. Free-form conversational Q&A. No quiz or scoring
   mechanism (this is the key difference from vutr/ben-dicken).

### Skill file

Thin trigger file (`SKILL.md`) mirroring `vutr-persona/SKILL.md`: states the
trigger (`/nate-herk`, `/jack-roberts`), a condensed identity paragraph, and
points to the full agent file as the source of truth for technical content.

## Testing / validation

These are prompt/content assets, not executable code — no automated test
suite applies. Validation is manual:
- Read through both persona files end-to-end for internal consistency (no
  contradictions, no placeholder text like "TBD").
- Spot-check a sample of quotes against the source vault notes to confirm
  they are real, not fabricated.
- Confirm the mentor instructions produce beginner-calibrated explanations
  (not examiner-style scoring) by construction — no runtime test needed
  since there's no scoring logic to verify.

## Out of scope

- No changes to the capture/build pipeline (that work is already complete —
  406 transcripts captured, vault built, cross-coverage verified).
- No quiz/scoring mechanism for these two personas (may be added later if
  the user wants them folded into a verification-loop pipeline, but not
  requested here).
- No pruning of the existing "AI & Development" vault notes — personas are
  built from them, not a replacement for them.
