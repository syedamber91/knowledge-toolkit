export const meta = {
  name: 'verify-lvai',
  description: 'Dual-lens verification loop for a Learning Vault AI pack (nate-herk-examiner x jack-roberts-examiner), grounded on the generated chapters.json',
  phases: [
    { title: 'Setup' },
    { title: 'Questions' },
    { title: 'AnswerAudit' },
    { title: 'Score' },
    { title: 'SignOff' },
  ],
}

// Unlike verify-sdcourse-luc.js, this workflow keeps NO chapter-content mirror in
// the script. Learning Vault AI packs are wiki-generated: output/packs/<topic>/
// chapters.json is the SINGLE source for both the rendered PDF and these exam
// prompts, so there is nothing to drift out of sync. The Setup agent reads that
// file and hands the chapters to the pipeline inline (closed-book: the student
// only ever sees one chapter's html at a time).

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

const CHAPTERS_SCHEMA = {
  type: 'object',
  properties: {
    topic: { type: 'string' },
    chapters: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          id: { type: 'integer' },
          title: { type: 'string' },
          concepts: { type: 'array', items: { type: 'string' } },
          content: { type: 'string' },
        },
        required: ['id', 'title', 'content'],
      },
    },
  },
  required: ['topic', 'chapters'],
}

// The Workflow `args` global arrives EMPTY here (a known gotcha shared with the
// STORM engine and verify-sdcourse-luc). So the controller writes the run config
// to <repo-root>/output/lvai/_run.json — `{ "topic": "ai-agents", "chapterIds":
// [1,2,3] }` (chapterIds optional; omit or [] to verify every chapter) — before
// invoking this workflow. The repo root is resolved at RUN TIME from the current
// git checkout, never hardcoded to one worktree. The Setup agent then reads both
// _run.json and the generated output/packs/<topic>/chapters.json and returns the
// chapters inline (html as `content`), so the pipeline needs no filesystem access.
phase('Setup')
const setup = await agent(
  `Find the repository root of the current git checkout (\`git rev-parse --show-toplevel\`). Read the JSON at "<repo-root>/output/lvai/_run.json" to get { topic, chapterIds? }. Then read "<repo-root>/output/packs/<topic>/chapters.json" (shape: { "title", "chapters": [ { "title", "concepts", "html" } ] }).\n\nReturn an object { topic, chapters } where chapters is an array of { id (1-based index into the file's chapters array), title, concepts, content } — set content to the chapter's exact "html" string, verbatim, no summarizing. If _run.json has a non-empty chapterIds array, include ONLY chapters whose 1-based id is in that list; otherwise include every chapter in file order.`,
  { schema: CHAPTERS_SCHEMA, label: 'read-pack' }
)
const topic = setup.topic
const chapters = setup.chapters
if (!chapters || chapters.length === 0) {
  throw new Error(`No chapters resolved for topic "${topic}" — check output/lvai/_run.json and output/packs/${topic}/chapters.json`)
}
log(`Verifying ${chapters.length} chapter(s) of "${topic}" with nate-herk-examiner x jack-roberts-examiner`)

phase('Questions')
const results = await pipeline(
  chapters,
  // Stage 1 — both examiners generate 5 questions each, from their own persona,
  // grounded on the chapter content.
  async (chapter) => {
    const qPrompt = (who) =>
      `You are the ${who} examiner. Read this Learning Vault AI chapter and generate exactly 5 examination questions about the AI/automation concepts it teaches, from your own persona's lens and grounded ONLY in your real positions. Rules: at least 2 trade-off questions, at least 1 question requiring a precise term or mechanism, at least 1 WHY question; no surface recall.\n\nChapter: "${chapter.title}"\n\n${chapter.content}`
    const [nateQ, jackQ] = await parallel([
      () => agent(qPrompt('Nate Herk (nate-herk-examiner)'),
        { agentType: 'nate-herk-examiner', phase: 'Questions', schema: QUESTION_SCHEMA, label: `nate-q-ch${chapter.id}` }),
      () => agent(qPrompt('Jack Roberts (jack-roberts-examiner)'),
        { agentType: 'jack-roberts-examiner', phase: 'Questions', schema: QUESTION_SCHEMA, label: `jack-q-ch${chapter.id}` }),
    ])
    return { chapter, nateQ, jackQ }
  },
  // Stage 2 — student answers each examiner's set in SEPARATE calls (prevents
  // cross-attribution / invention), and Alex clarity-audits in parallel.
  async ({ chapter, nateQ, jackQ }) => {
    phase('AnswerAudit')
    const other = { 'Nate Herk': 'Jack Roberts', 'Jack Roberts': 'Nate Herk' }
    const sourcingRules = (voice) =>
      `Rules:\n- Answer using only the chapter text above, from memory of reading it just now — no tools, no outside knowledge, no invented quotes (copy exact wording if you quote).\n- These 5 questions are all from the ${voice} examiner — answer from what the chapter actually teaches, not from anything only the ${other[voice]} examiner would emphasize.\n- If the chapter doesn't fully cover something, say so plainly rather than inventing detail.\n- Always answer every question with your best attempt — never leave an answer blank or refuse.`
    const [nateAnswersRes, jackAnswersRes, audit] = await parallel([
      () => agent(
        `You are a student who has read ONLY this chapter (no outside knowledge). Chapter content:\n\n${chapter.content}\n\nAnswer EXACTLY these ${nateQ.questions.length} questions from the Nate Herk examiner, in order, one answer per question.\n\n${sourcingRules('Nate Herk')}\n\nQuestions:\n${nateQ.questions.map((q, i) => `${i + 1}. ${q}`).join('\n')}`,
        { agentType: 'justin-sung', phase: 'AnswerAudit', schema: ANSWER_SCHEMA, label: `nate-answers-ch${chapter.id}` }
      ),
      () => agent(
        `You are a student who has read ONLY this chapter (no outside knowledge). Chapter content:\n\n${chapter.content}\n\nAnswer EXACTLY these ${jackQ.questions.length} questions from the Jack Roberts examiner, in order, one answer per question.\n\n${sourcingRules('Jack Roberts')}\n\nQuestions:\n${jackQ.questions.map((q, i) => `${i + 1}. ${q}`).join('\n')}`,
        { agentType: 'justin-sung', phase: 'AnswerAudit', schema: ANSWER_SCHEMA, label: `jack-answers-ch${chapter.id}` }
      ),
      () => agent(
        `Read this chapter as Alex (a curious 15-year-old with no AI/dev background) and produce a clarity audit — confusion log, additive improvement requests (DEFINE/ANALOGY/BRIDGE/DIAGRAM/EXAMPLE/SEQUENCE), and any remaining blockers. Never ask to remove content. Chapter content:\n\n${chapter.content}`,
        { agentType: 'alex', phase: 'AnswerAudit', schema: AUDIT_SCHEMA, label: `audit-ch${chapter.id}` }
      ),
    ])
    return { chapter, nateQ, jackQ, nateAnswersRes, jackAnswersRes, audit }
  },
  // Stage 3 — each examiner scores its OWN Q/A on accuracy + coverage.
  async ({ chapter, nateQ, jackQ, nateAnswersRes, jackAnswersRes, audit }) => {
    phase('Score')
    const formatQA = (questions, answers) =>
      questions.map((q, i) => `Q${i + 1}: ${q}\nA${i + 1}: ${answers[i] ?? '(no answer provided)'}`).join('\n\n')
    const scorePrompt = (qaText) =>
      `Score the student's answers to YOUR questions on accuracy (0-10) and coverage (0-10). These are ONLY your questions and the student's matching answers — no other examiner's material is included. Judge accuracy against your real positions (dock for invented specifics or positions you never took) and coverage against what you consider important. List any gaps.\n\n${qaText}`
    const [nateScore, jackScore] = await parallel([
      () => agent(scorePrompt(formatQA(nateQ.questions, nateAnswersRes.answers)),
        { agentType: 'nate-herk-examiner', phase: 'Score', schema: SCORE_SCHEMA, label: `nate-score-ch${chapter.id}` }),
      () => agent(scorePrompt(formatQA(jackQ.questions, jackAnswersRes.answers)),
        { agentType: 'jack-roberts-examiner', phase: 'Score', schema: SCORE_SCHEMA, label: `jack-score-ch${chapter.id}` }),
    ])
    const pass = nateScore.accuracy >= 9.0 && nateScore.coverage >= 9.0 && jackScore.accuracy >= 9.0 && jackScore.coverage >= 9.0
    return { chapterId: chapter.id, title: chapter.title, nateScore, jackScore, audit, pass }
  }
)

const allPassed = results.every(r => r.pass)
log(`Phase pass: ${results.filter(r => r.pass).length}/${results.length} chapters at >=9.0 on all four scores`)

let signoff = null
if (allPassed) {
  phase('SignOff')
  const idsLabel = results.map(r => r.chapterId).join(',')
  const [nate, jack, justin, alexSignoff] = await parallel([
    () => agent(`Final sign-off for "${topic}" chapters ${idsLabel}: confirm technical accuracy of the AI/automation concepts, and coverage of the trade-offs and "when NOT to use" guidance you (Nate Herk) consider essential, are both >=9.0 across these chapters as a whole. Set pass=false if not.`, { agentType: 'nate-herk-examiner', phase: 'SignOff', schema: SIGNOFF_SCHEMA }),
    () => agent(`Final sign-off for "${topic}" chapters ${idsLabel}: confirm technical accuracy and coverage of the systems-thinking, simplicity, and business framing you (Jack Roberts) consider essential are both >=9.0 across these chapters as a whole. Set pass=false if not.`, { agentType: 'jack-roberts-examiner', phase: 'SignOff', schema: SIGNOFF_SCHEMA }),
    () => agent(`Final sign-off for "${topic}" chapters ${idsLabel}: confirm pedagogical quality (WHY->WHAT->HOW structure, retrieval practice, emotional framing) meets at least 6/7 criteria across these chapters. Set pass=false if not.`, { agentType: 'justin-sung', phase: 'SignOff', schema: SIGNOFF_SCHEMA }),
    () => agent(`Final sign-off for "${topic}" chapters ${idsLabel}: confirm there are no remaining BLOCKERS for a 15-year-old reader. Set pass=false if any blocker remains.`, { agentType: 'alex', phase: 'SignOff', schema: SIGNOFF_SCHEMA }),
  ])
  signoff = { nate, jack, justin, alex: alexSignoff, allPassed: [nate, jack, justin, alexSignoff].every(Boolean) && [nate, jack, justin, alexSignoff].every(s => s.pass) }
}

return { topic, results, allPassed, signoff }
