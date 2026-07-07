export const meta = {
  name: 'verify-sdcourse-luc',
  description: 'Dual-examiner verification loop for the sdcourse x lucsystemdesign dual-lens pack',
  phases: [
    { title: 'Questions' },
    { title: 'AnswerAudit' },
    { title: 'Score' },
    { title: 'SignOff' },
  ],
}

// Chapter content mirror — MUST be kept in sync with scripts/generate_sdcourse_luc.py
// CH{n} strings. Phase tasks append entries here; never let this drift from the PDF.
const CHAPTERS = []

// Per-chapter source summaries used to prompt the examiners' question generation.
// Phase tasks append entries keyed by chapter id.
const KNOWLEDGE_BY_CHAPTER = {}

const QUESTION_SCHEMA = {
  type: 'object',
  properties: {
    questions: { type: 'array', items: { type: 'string' }, minItems: 5, maxItems: 5 },
  },
  required: ['questions'],
}

const ANSWER_SCHEMA = {
  type: 'object',
  properties: {
    answers: { type: 'array', items: { type: 'string' } },
  },
  required: ['answers'],
}

const AUDIT_SCHEMA = {
  type: 'object',
  properties: {
    confusionLog: { type: 'array', items: { type: 'string' } },
    improvements: { type: 'array', items: { type: 'string' } },
    blockers: { type: 'array', items: { type: 'string' } },
  },
  required: ['confusionLog', 'improvements', 'blockers'],
}

const SCORE_SCHEMA = {
  type: 'object',
  properties: {
    accuracy: { type: 'number' },
    coverage: { type: 'number' },
    gaps: { type: 'array', items: { type: 'string' } },
  },
  required: ['accuracy', 'coverage', 'gaps'],
}

const SIGNOFF_SCHEMA = {
  type: 'object',
  properties: {
    pass: { type: 'boolean' },
    notes: { type: 'array', items: { type: 'string' } },
  },
  required: ['pass', 'notes'],
}

const chapterIds = args.chapterIds
const chapters = CHAPTERS.filter(c => chapterIds.includes(c.id))

if (chapters.length !== chapterIds.length) {
  throw new Error(`Requested chapterIds ${JSON.stringify(chapterIds)} but CHAPTERS only has ${CHAPTERS.map(c => c.id)}`)
}

phase('Questions')
const results = await pipeline(
  chapters,
  async (chapter) => {
    const know = KNOWLEDGE_BY_CHAPTER[chapter.id]
    const [lucQ, sdQ] = await parallel([
      () => agent(
        `Generate 5 examination questions about your (Luc's) lens in this chapter. Source material: ${know.luc}\n\nRules: at least 2 trade-off questions, at least 1 "when NOT to use" or precise-term question, at least 1 WHY question.`,
        { agentType: 'lucsystemdesign', phase: 'Questions', schema: QUESTION_SCHEMA, label: `luc-q-ch${chapter.id}` }
      ),
      () => agent(
        `Generate 5 examination questions about your (sdcourse's) lens in this chapter. Source material: ${know.sdcourse}\n\nRules: at least 2 trade-off questions, at least 1 precise numeric-benchmark question, at least 1 WHY question.`,
        { agentType: 'sdcourse', phase: 'Questions', schema: QUESTION_SCHEMA, label: `sd-q-ch${chapter.id}` }
      ),
    ])
    return { chapter, lucQ, sdQ }
  },
  async ({ chapter, lucQ, sdQ }) => {
    phase('AnswerAudit')
    const allQuestions = [...lucQ.questions, ...sdQ.questions]
    const [answers, audit] = await parallel([
      () => agent(
        `You are a student who has read ONLY this chapter (no outside knowledge). Chapter content:\n\n${chapter.content}\n\nAnswer each question using only the chapter content. Questions:\n${allQuestions.map((q, i) => `${i + 1}. ${q}`).join('\n')}`,
        { agentType: 'justin-sung', phase: 'AnswerAudit', schema: ANSWER_SCHEMA, label: `answers-ch${chapter.id}` }
      ),
      () => agent(
        `Read this chapter as Alex (a curious 15-year-old with no domain background) and produce a clarity audit — confusion log, additive improvement requests (DEFINE/ANALOGY/BRIDGE/DIAGRAM/EXAMPLE/SEQUENCE), and any remaining blockers. Never ask to remove content. Chapter content:\n\n${chapter.content}`,
        { agentType: 'alex', phase: 'AnswerAudit', schema: AUDIT_SCHEMA, label: `audit-ch${chapter.id}` }
      ),
    ])
    return { chapter, lucQ, sdQ, answers, audit }
  },
  async ({ chapter, lucQ, sdQ, answers, audit }) => {
    phase('Score')
    const answerText = answers.answers.join('\n')
    const [lucScore, sdScore] = await parallel([
      () => agent(
        `Score the student's answers to YOUR questions on accuracy (0-10) and coverage (0-10). Your questions:\n${lucQ.questions.map((q, i) => `${i + 1}. ${q}`).join('\n')}\n\nStudent answers:\n${answerText}\n\nList any gaps.`,
        { agentType: 'lucsystemdesign', phase: 'Score', schema: SCORE_SCHEMA, label: `luc-score-ch${chapter.id}` }
      ),
      () => agent(
        `Score the student's answers to YOUR questions on accuracy (0-10) and coverage (0-10). Your questions:\n${sdQ.questions.map((q, i) => `${i + 1}. ${q}`).join('\n')}\n\nStudent answers:\n${answerText}\n\nList any gaps.`,
        { agentType: 'sdcourse', phase: 'Score', schema: SCORE_SCHEMA, label: `sd-score-ch${chapter.id}` }
      ),
    ])
    const pass = lucScore.accuracy >= 9.0 && lucScore.coverage >= 9.0 && sdScore.accuracy >= 9.0 && sdScore.coverage >= 9.0
    return { chapterId: chapter.id, title: chapter.title, lucScore, sdScore, audit, pass }
  }
)

const allPassed = results.every(r => r.pass)
log(`Phase pass: ${results.filter(r => r.pass).length}/${results.length} chapters at >=9.0 on all four scores`)

let signoff = null
if (allPassed) {
  phase('SignOff')
  const idsLabel = chapterIds.join(',')
  const [luc, sd, justin, alex] = await parallel([
    () => agent(`Final sign-off for chapters ${idsLabel}: confirm decision-framework accuracy and "when NOT to use" coverage are both >=9.0 across these chapters as a whole. Set pass=false if not.`, { agentType: 'lucsystemdesign', phase: 'SignOff', schema: SIGNOFF_SCHEMA }),
    () => agent(`Final sign-off for chapters ${idsLabel}: confirm production accuracy (benchmarks, failure modes, exact numbers) is >=9.0 across these chapters as a whole. Set pass=false if not.`, { agentType: 'sdcourse', phase: 'SignOff', schema: SIGNOFF_SCHEMA }),
    () => agent(`Final sign-off for chapters ${idsLabel}: confirm pedagogical quality (WHY->WHAT->HOW structure, retrieval practice, emotional framing) meets at least 6/7 criteria across these chapters. Set pass=false if not.`, { agentType: 'justin-sung', phase: 'SignOff', schema: SIGNOFF_SCHEMA }),
    () => agent(`Final sign-off for chapters ${idsLabel}: confirm there are no remaining BLOCKERS for a 15-year-old reader. Set pass=false if any blocker remains.`, { agentType: 'alex', phase: 'SignOff', schema: SIGNOFF_SCHEMA }),
  ])
  signoff = { luc, sd, justin, alex, allPassed: [luc, sd, justin, alex].every(Boolean) && [luc, sd, justin, alex].every(s => s.pass) }
}

return { results, allPassed, signoff }
