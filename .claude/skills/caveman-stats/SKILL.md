---
name: caveman-stats
description: >
  Show recorded output and cache-read token usage and mode attribution for
  the current Claude Code session, or locate the host's native usage report.
  Trigger: /caveman-stats.
---

> **Provenance (vendored 2026-09-27).** Copied verbatim from
> `github.com/JuliusBrussee/caveman` @ `2fd153c6`, `skills/caveman-stats/SKILL.md`,
> MIT. One of the six-skill `caveman` set vendored here — see the
> provenance block in the sibling `caveman/SKILL.md` for the full source,
> licensing-split and hooks-not-vendored notes; not repeated per file.
> **The hook this skill depends on (`src/hooks/caveman-mode-tracker.js`
> resolving `src/hooks/caveman-stats.js`) is NOT vendored here** — no
> lifecycle hooks were carried over (see `caveman/SKILL.md`'s provenance
> block), so `/caveman-stats` in these repos has nothing to read and
> cannot report usage or mode-attribution history. Say so plainly rather
> than fabricating a report if invoked.

In Claude Code, `src/hooks/caveman-mode-tracker.js` resolves `src/hooks/caveman-stats.js` next to itself and runs it on `/caveman-stats`. The hook does not block the prompt: it supplies the report through `hookSpecificOutput.additionalContext` with an instruction to print it verbatim inside a fenced code block. Do exactly that, and do not calculate, recompute or re-round the numbers yourself.

In Gemini CLI, direct the user to `/stats model` for current session token usage or `/stats session` for session statistics. Gemini custom commands are prompts; they cannot invoke the built-in command or read its live session metrics. Never read Claude Code transcripts as Gemini usage. In other hosts, use a native usage report if one is available; otherwise say that current session usage is unavailable. The Claude reader and its lifetime history apply only to Claude Code. Savings remain unknown in every host without a measured comparison.

The report shows recorded output and cache-read tokens, response counts, and mode attribution where available. Savings are unknown: the transcript has no measured comparison without Caveman. Do not infer saved tokens, percentages, dollars, rule overhead, or a net result from output counts or the current mode.

`--all` and `--since 7d` aggregate the latest recorded output count per session. `--share` reports observed usage with savings unknown. Historical `est_saved_*` fields are ignored; their original history rows remain on disk. The statusline shows the active mode without the retired savings badge.

Original/current memory-file pairs are reported by their measured byte sizes. Those file-size differences do not establish provider token or billing savings. (Upstream's own methodology write-up is `docs/HONEST-NUMBERS.md` in `github.com/JuliusBrussee/caveman` — not vendored into this repo.)
