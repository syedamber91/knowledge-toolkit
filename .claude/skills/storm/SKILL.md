---
name: storm
description: Run a STORM multi-perspective business-research pass on an idea — cast expert lenses that deliberately disagree, map their contradictions, adversarially fact-check, and produce a graded vault note + HTML briefing. Use for evaluating a business idea/opportunity, or when the user invokes /storm.
trigger: /storm
---

# Skill: STORM Business Research

**Trigger:** `/storm [business idea]`

Multi-lens business research modeled on Stanford's STORM method. It borrows
expertise you don't have — a council of lenses that contradict each other — then
verifies and grades the result. See
`docs/superpowers/specs/2026-07-06-storm-business-research-design.md`.

## Modes

Only **`idea`** (evaluate one business idea) is live in the MVP. If the user asks
for `gap` / `rescore` / `research`, say those modes are designed but not yet
built, and offer to run `idea` instead.

## Steps

1. **Get the idea.** If the user didn't name a business idea after `/storm`, ask
   for one.
2. **Ask the voice count.** "How many named expert voices should I cast? (default
   3 — Mufti is always added on top as the halal gate.)" Use 3 if they don't say.
3. **Make a scratch dir** under the session scratchpad, e.g.
   `<scratch>/storm-<slug>/`.
4. **Write the run config.** The workflow's `args` global arrives EMPTY in this
   environment (known gotcha), so parameters are passed via a fixed file the
   workflow reads in Phase 0. Write the run config to
   `<repo>/output/storm/_run.json` (create the dir first):
   ```bash
   mkdir -p output/storm && cat > output/storm/_run.json <<JSON
   {"mode":"idea","topic":"<idea>","voices":<n>,"scratch":"<abs scratch dir>"}
   JSON
   ```
5. **Invoke the engine.** Call the `Workflow` tool:
   `Workflow({ name: "storm-business-research" })` (no `args` — the workflow reads
   `output/storm/_run.json`). It casts lenses (auto best-fit + Mufti), runs them
   on vault+web, maps contradictions, adversarially verifies, and renders outputs.
6. **Relay results.** Report the verdict (KEEP/WATCHLIST/CUT) and the two written
   paths: the graded vault note in the Opportunity-Catalog `STORM-Reports/` folder
   and the HTML briefing under `output/storm/`. Note that the vault note is not in
   git (personal vault) — that's expected.

## Guardrails

- Mufti's halal judgement is a hard gate — a FAIL forces a CUT verdict.
- Never fabricate evidence; an unverifiable claim is demoted, not dressed up.
- Nothing captured is committed — reports live in the iCloud vault / gitignored
  `output/`.
