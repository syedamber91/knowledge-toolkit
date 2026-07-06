export const meta = {
  name: 'storm-business-research',
  description: 'STORM multi-lens business research: cast lenses, map contradictions, verify, render a graded note + HTML',
  phases: [
    { title: 'Scope & Cast' },
    { title: 'Lenses' },
    { title: 'Contradiction Map' },
    { title: 'Synthesis' },
    { title: 'Verify' },
    { title: 'Render' },
  ],
}

const { mode, topic, voices = 3, scratch } = args
const ROLE_LENSES = ['Operator', 'Investor', 'Customer', 'Skeptic', 'Local-Market']

// Phase 0 — Scope & cast (reads live roster via the CLI, picks best-fit voices + Mufti)
phase('Scope & Cast')
const cast = await agent(
  `You are the casting + scoping step of a STORM business-research run.\n` +
  `Business topic: "${topic}".\n` +
  `1. Run: python -m storm_core roster   (cwd is the repo root; prefix with PYTHONPATH=src and use .venv/bin/python). It prints JSON of the available named personas.\n` +
  `2. Pick the ${voices} best-fit named voices for THIS topic from that roster (by their description). ALWAYS add the Mufti persona on top as a halal gate (do not count it against the ${voices}).\n` +
  `3. Tighten the topic into a one-line research scope.\n` +
  `Return JSON only.`,
  { phase: 'Scope & Cast', schema: {
      type: 'object',
      properties: {
        scope: { type: 'string' },
        named_voices: { type: 'array', items: { type: 'string' } },
        mufti_slug: { type: 'string' },
      },
      required: ['scope', 'named_voices', 'mufti_slug'],
  } })

const lenses = [...ROLE_LENSES, ...cast.named_voices, 'Mufti']

// Phase 1 — Lenses in parallel; each writes its OWN file (output-cap guardrail)
phase('Lenses')
await parallel(lenses.map((lens, i) => () =>
  agent(
    `You are the "${lens}" lens in a STORM business-research council.\n` +
    `Scope: ${cast.scope}\n` +
    `Research this from YOUR perspective using BOTH the local Obsidian vaults (grep the ` +
    `Business Personas and AI & Development vaults first) AND live web search for current, ` +
    `dated evidence. If you are the Mufti lens, judge halal permissibility and give a clear ` +
    `PASS/FAIL with reasoning.\n` +
    `Write your findings (claims + dated sources + your stance) to the file ` +
    `${scratch}/lens-${i}-${lens.replace(/[^a-z0-9]/gi, '_')}.md . Return only the file path.`,
    { phase: 'Lenses', label: `lens:${lens}` }
  )
))

// Phase 2 — Contradiction map (reads all lens files)
phase('Contradiction Map')
await agent(
  `Read every file matching ${scratch}/lens-*.md . Produce a contradiction map: for each ` +
  `point of disagreement, name the topic, each lens's stance, and who has stronger evidence. ` +
  `Write it to ${scratch}/contradictions.md . Return only the file path.`,
  { phase: 'Contradiction Map' }
)

// Phase 3 — Synthesis into a StormReport JSON (schema-validated)
phase('Synthesis')
const report = await agent(
  `Read ${scratch}/lens-*.md and ${scratch}/contradictions.md . Synthesize a single ` +
  `StormReport for the business "${topic}" (mode "${mode}"). Rank findings by reliability ` +
  `(1-10). Give a verdict of exactly KEEP, WATCHLIST, or CUT (a Mufti FAIL forces CUT). ` +
  `Grade each piece of evidence A/B/C. Include the halal judgement in halal_note. ` +
  `Set generated to today's date in YYYY-MM-DD.`,
  { phase: 'Synthesis', schema: {
      type: 'object',
      properties: {
        topic: { type: 'string' }, mode: { type: 'string' }, summary: { type: 'string' },
        verdict: { type: 'string', enum: ['KEEP', 'WATCHLIST', 'CUT'] },
        lenses: { type: 'array', items: { type: 'string' } },
        findings: { type: 'array', items: { type: 'object' } },
        contradictions: { type: 'array', items: { type: 'object' } },
        halal_note: { type: 'string' }, generated: { type: 'string' },
      },
      required: ['topic', 'mode', 'summary', 'verdict', 'generated'],
  } })

// Phase 4 — Adversarial verify (top-tier model); rewrites the report file if it corrects anything
phase('Verify')
const reportPath = `${scratch}/report.json`
const verified = await agent(
  `Here is a draft StormReport JSON:\n${JSON.stringify(report)}\n\n` +
  `Adversarially fact-check its TOP findings against the local vault AND live web. For each ` +
  `piece of evidence set status to confirmed, corrected, or demoted, fixing claims/sources as ` +
  `needed. If verification weakens the case, lower the verdict. Write the final corrected ` +
  `StormReport JSON to ${reportPath} and return only that path.`,
  { phase: 'Verify', model: 'opus' }
)

// Phase 5 — Render note + HTML via the CLI
phase('Render')
const rendered = await agent(
  `Run, from the repo root with PYTHONPATH=src and .venv/bin/python:\n` +
  `python -m storm_core build --report ${reportPath}\n` +
  `Then report the two written file paths (the vault note and the HTML briefing).`,
  { phase: 'Render' }
)

return { report: reportPath, rendered }
