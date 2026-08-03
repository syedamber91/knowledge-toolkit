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

// NOTE: the Workflow `args` global arrives EMPTY in this environment (a known
// gotcha — a passed object silently becomes {}). So the run parameters are NOT
// read from `args`; the /storm skill writes them to this fixed run-config file,
// and Phase 0 reads it. Everything downstream flows from Phase 0's return value.
const REPO = '/Users/syedamberiqbal/Documents/workspace/Claude_Code/SOIC_Scraper/.claude/worktrees/bold-sammet-8c78b3'
const RUN_CFG = `${REPO}/output/storm/_run.json`
const PY = `cd '${REPO}' && PYTHONPATH=src '/Users/syedamberiqbal/Documents/workspace/Claude_Code/SOIC_Scraper/.venv/bin/python' -m storm_core`

const ROLE_LENSES = ['Operator', 'Investor', 'Customer', 'Skeptic', 'Local-Market']

// The StormReport JSON schema, mirroring src/storm_core/models.py exactly so the
// agent output validates cleanly at the `storm_core build` step.
const EVIDENCE_SCHEMA = {
  type: 'object',
  properties: {
    claim: { type: 'string' },
    source: { type: 'string' },
    date: { type: 'string' },
    grade: { type: 'string', enum: ['A', 'B', 'C'] },
    status: { type: 'string', enum: ['confirmed', 'corrected', 'demoted'] },
  },
  required: ['claim', 'source', 'grade'],
}
const FINDING_SCHEMA = {
  type: 'object',
  properties: {
    title: { type: 'string' },
    detail: { type: 'string' },
    reliability: { type: 'integer', minimum: 1, maximum: 10 },
    supported_by: { type: 'array', items: { type: 'string' } },
    challenged_by: { type: 'array', items: { type: 'string' } },
    evidence: { type: 'array', items: EVIDENCE_SCHEMA },
  },
  required: ['title', 'detail', 'reliability'],
}
const CONTRADICTION_SCHEMA = {
  type: 'object',
  properties: {
    topic: { type: 'string' },
    positions: { type: 'object', additionalProperties: { type: 'string' } },
    resolution: { type: 'string' },
  },
  required: ['topic'],
}
const REPORT_SCHEMA = {
  type: 'object',
  properties: {
    topic: { type: 'string' }, mode: { type: 'string' }, summary: { type: 'string' },
    verdict: { type: 'string', enum: ['KEEP', 'WATCHLIST', 'CUT'] },
    lenses: { type: 'array', items: { type: 'string' } },
    findings: { type: 'array', items: FINDING_SCHEMA },
    contradictions: { type: 'array', items: CONTRADICTION_SCHEMA },
    halal_note: { type: 'string' }, generated: { type: 'string' },
  },
  required: ['topic', 'mode', 'summary', 'verdict', 'findings', 'generated'],
}

// Phase 0 — Read the run config, then scope + cast (roster via CLI, best-fit + Mufti)
phase('Scope & Cast')
const run = await agent(
  `You are the setup step of a STORM business-research run.\n` +
  `1. Read the run config JSON at: ${RUN_CFG}\n   It has keys: mode, topic, voices (an integer), scratch (an absolute dir).\n` +
  `2. Run this exact command (copy verbatim): ${PY} roster\n   It prints a JSON array of available named personas.\n` +
  `3. Pick the \`voices\` best-fit named voices for THIS topic from that roster (by description). ALWAYS add the Mufti persona on top as a halal gate (do NOT count it against \`voices\`).\n` +
  `4. Tighten the topic into a one-line research scope.\n` +
  `5. Run this exact command (copy verbatim): ${PY} reach-probe\n` +
  `   It prints the optional Agent Reach retrieval layer's status. Return \`reach_channels\` = ` +
  `the names of channels where "available" is true, ONLY if the top-level "enabled" is also true; ` +
  `otherwise return an empty array. This layer is optional — an empty array is a perfectly normal ` +
  `result and is NOT an error, so never stop or retry because of it.\n` +
  `Return JSON with the config values you read (mode, topic, voices, scratch) plus scope, named_voices and reach_channels.`,
  { phase: 'Scope & Cast', schema: {
      type: 'object',
      properties: {
        mode: { type: 'string' },
        topic: { type: 'string' },
        voices: { type: 'integer' },
        scratch: { type: 'string' },
        scope: { type: 'string' },
        named_voices: { type: 'array', items: { type: 'string' } },
        reach_channels: { type: 'array', items: { type: 'string' } },
      },
      required: ['mode', 'topic', 'scratch', 'scope', 'named_voices'],
  } })

const { mode, topic, scratch, scope, named_voices } = run
const lenses = [...ROLE_LENSES, ...named_voices, 'Mufti']

// Optional Agent Reach breadth (Exa / X / Reddit / RSS). Absent-safe by design:
// with no channels live this string is empty and the lens prompt is byte-for-byte
// what it was before the layer existed. See
// docs/superpowers/specs/2026-08-03-agent-reach-evaluation.md
const reachChannels = Array.isArray(run.reach_channels) ? run.reach_channels : []
const REACH_HINT = reachChannels.length
  ? `You ALSO have a structured retrieval layer over these channels: ${reachChannels.join(', ')}. ` +
    `Use it for evidence a plain web search misses — practitioner chatter, dated posts, niche feeds — ` +
    `by running: ${PY} reach --query "<your search>" --channels ${reachChannels.join(',')} --limit 5\n` +
    `It returns JSON with results[] (channel/title/url/snippet/published/author) and channels_skipped. ` +
    `A skipped channel is normal, not a failure — carry on with what came back. Treat every returned ` +
    `item as a LEAD to weigh, never as a verified fact: social posts are opinion, so cite the url and ` +
    `date and let the Verify phase judge it.\n`
  : ''

// Phase 1 — Lenses in parallel; each writes its OWN file (output-cap guardrail)
phase('Lenses')
await parallel(lenses.map((lens, i) => () =>
  agent(
    `You are the "${lens}" lens in a STORM business-research council.\n` +
    `Business topic: "${topic}"\nScope: ${scope}\n` +
    `Research this from YOUR perspective using BOTH the local Obsidian vaults (grep the ` +
    `Business Personas and AI & Development vaults first) AND live web search for current, ` +
    `dated evidence. If you are the Mufti lens, judge halal permissibility and give a clear ` +
    `PASS/FAIL with reasoning.\n` +
    REACH_HINT +
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

// Phase 3 — Synthesis into a StormReport JSON (schema mirrors the Pydantic model)
phase('Synthesis')
const report = await agent(
  `Read ${scratch}/lens-*.md and ${scratch}/contradictions.md . Synthesize a single ` +
  `StormReport for the business "${topic}" (mode "${mode}").\n` +
  `Each finding MUST have: title (short), detail (prose), reliability (integer 1-10), ` +
  `supported_by (lens names), challenged_by (lens names), and evidence (a LIST of objects, ` +
  `each with claim, source, optional date, grade A/B/C, and status confirmed|corrected|demoted).\n` +
  `Give a verdict of exactly KEEP, WATCHLIST, or CUT (a Mufti FAIL forces CUT). ` +
  `Put the halal judgement in halal_note. Set lenses to the full list of lens names used. ` +
  `Set generated to today's date as YYYY-MM-DD.`,
  { phase: 'Synthesis', schema: REPORT_SCHEMA })

// Phase 4 — Adversarial verify (top-tier); writes the corrected StormReport to disk
phase('Verify')
const reportPath = `${scratch}/report.json`
await agent(
  `Here is a draft StormReport JSON:\n${JSON.stringify(report)}\n\n` +
  `Adversarially fact-check its TOP findings against the local vault AND live web. For each ` +
  `evidence object set status to confirmed, corrected, or demoted, fixing claims/sources as ` +
  `needed. If verification weakens the case, lower the verdict. Preserve the EXACT StormReport ` +
  `shape (findings with title/detail/reliability/supported_by/challenged_by/evidence-list). ` +
  `Write the final corrected StormReport JSON to ${reportPath} and return only that path.`,
  { phase: 'Verify', model: 'opus' }
)

// Phase 5 — Render note + HTML via the CLI
phase('Render')
const rendered = await agent(
  `Run this exact command (copy verbatim): ${PY} build --report ${reportPath}\n` +
  `It prints two file paths (the vault note and the HTML briefing). Report both.`,
  { phase: 'Render' }
)

return { report: reportPath, rendered }
