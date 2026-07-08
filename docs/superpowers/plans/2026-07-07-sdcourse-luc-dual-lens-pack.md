# sdcourse × lucsystemdesign Dual-Lens Learning Pack Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a single 23-chapter system-design learning-pack PDF (`output/sdcourse_luc.pdf`) that presents every topic from the `lucsystemdesign` and `sdcourse` examiner personas through both voices in every chapter, verified to ≥9.0/9.0 accuracy+coverage by both examiners plus a Justin/Alex pedagogy-and-clarity sign-off, built in 4 phases.

**Architecture:** A single hardcoded-content generator script (`scripts/generate_sdcourse_luc.py`) renders HTML → PDF via headless Chrome, exactly like `scripts/generate_vutr_spark.py`. A companion `Workflow` script (`.claude/workflows/verify-sdcourse-luc.js`) pipelines chapters through `lucsystemdesign` + `sdcourse` (question generation + scoring), `justin-sung` (student answers), and `alex` (clarity audit), gated at ≥9.0 on all four scores, with a quad-agent sign-off per phase.

**Tech Stack:** Python 3 (generator, stdlib only + `subprocess` for headless Chrome), JavaScript (Workflow script — plain JS, no TypeScript, no `Date.now()`/`Math.random()`), existing Claude Code agents (`lucsystemdesign`, `sdcourse`, `justin-sung`, `alex`).

## Global Constraints

- Persona files (`.claude/skills/{sdcourse,lucsystemdesign}-persona/SKILL.md`, `.claude/agents/{sdcourse,lucsystemdesign}.md`) are **read-only** — never edited to make a chapter pass.
- No Mermaid CDN `<script>` tag in the generator (does not render in headless-Chrome print). All diagrams are inline `<svg>` with `Caveat`-font scribble annotations.
- Every chapter must contain genuine, substantive content from **both** authors (not a token sidebar) — enforced by the `data-author="luc"` / `data-author="sdcourse"` quote-block convention (Section: Per-chapter acceptance check).
- Every generator content edit must be mirrored into the workflow's `CHAPTERS[n].content` + `KNOWLEDGE_BY_CHAPTER[n]` in the same task (the sync invariant — stale `CHAPTERS[].content` silently stalls verification scores).
- `output/` is gitignored — never commit rendered HTML/PDF, only the generator script, workflow script, and docs.
- A chapter passes only when **all four** scores (Luc-accuracy, Luc-coverage, sdcourse-accuracy, sdcourse-coverage) are **≥9.0**.
- No new pytest module — these are content-generation scripts, consistent with `generate_vutr_spark.py` / `generate_learning_pack.py`.

---

## File Structure

| File | Responsibility |
|------|-----------------|
| `scripts/generate_sdcourse_luc.py` | CSS + `COVER` + `CH1`..`CH23` HTML strings + assembly + headless-Chrome PDF export. Grows once per phase (chapters added, assembly line extended). |
| `.claude/workflows/verify-sdcourse-luc.js` | Verification `Workflow` script. `CHAPTERS[]` (id/title/content) + `KNOWLEDGE_BY_CHAPTER{}` (luc/sdcourse source summaries) grow once per phase. Pipeline logic is written once and does not change per phase — only the two data structures and the `args.chapterIds` passed at invocation time change. |
| `docs/LEARNING_PACK_VERIFICATION_WORKFLOW.md` | Append a new section documenting this pack (mirrors the existing Ben Dicken section). |
| `CLAUDE.md` | Append a row to the learning-packs table. |
| `output/sdcourse_luc.{html,pdf}` | Rendered pack (gitignored, not committed). |

---

## Shared reference: per-chapter HTML skeleton

Every chapter (`CH1` .. `CH23`) follows this exact skeleton. Task 3 (Chapter 1) works through it in full; Chapters 2–23 reuse the identical mechanical structure with different source citations, titles, and box content — each chapter's task gives its own exact source line ranges and title, and is independently gate-checked with the grep commands in "Per-chapter acceptance check" below.

```html
<div class="chapter">
<div class="ch-head">
  <div class="ch-eye">Chapter {N} of 23</div>
  <h1>{TITLE}</h1>
  <div class="ch-src">Sources: lucsystemdesign — {luc topic name(s)} · sdcourse — {sdcourse topic name(s)}</div>
  <p class="ch-sum">{1-2 sentence summary of the chapter's central tension/synthesis}</p>
</div>

<div class="topic">
<h2>Luc's Lens: {luc angle}</h2>
<!-- SOURCE: .claude/agents/lucsystemdesign.md:{start}-{end} — synthesize into 2-4 paragraphs.
     Preserve at least one **Verbatim** quote from the source verbatim. -->
<p>...</p>
<div class="box s"><div class="box-lbl">Decision Rule</div>
<p>...</p>
</div>
<div class="quote" data-author="luc">"{exact verbatim Luc quote from the cited source lines}"<cite>— Luc, lucsystemdesign</cite></div>
</div>

<div class="topic">
<h2>sdcourse's Lens: {sdcourse angle}</h2>
<!-- SOURCE: .claude/agents/sdcourse.md:{start}-{end} — synthesize into 2-4 paragraphs.
     Preserve at least one **Verbatim** quote from the source verbatim. Include at least
     one numeric benchmark table. -->
<p>...</p>
<table>
<thead><tr><th>...</th><th>...</th></tr></thead>
<tbody><tr><td>...</td><td>...</td></tr></tbody>
</table>
<div class="box r"><div class="box-lbl">Production Reality</div>
<p>...</p>
</div>
<div class="quote" data-author="sdcourse">"{exact verbatim sdcourse quote from the cited source lines}"<cite>— sdcourse</cite></div>
</div>

<div class="sketch">
<svg viewBox="0 0 700 260" xmlns="http://www.w3.org/2000/svg" font-family="Caveat, cursive">
  <g filter="url(#squig1)" fill="none" stroke="#1c1c2e" stroke-width="2.6" stroke-linecap="round">
    <rect x="40" y="40" width="260" height="90" rx="12" fill="#eff6ff"/>
    <rect x="400" y="40" width="260" height="90" rx="12" fill="#fff7ed"/>
  </g>
  <text x="170" y="30" text-anchor="middle" font-size="15" font-weight="700" fill="#1e3a8a">LUC: {short decision-rule label}</text>
  <text x="170" y="90" text-anchor="middle" font-size="13" fill="#1e3a8a">{one-line paraphrase}</text>
  <text x="530" y="30" text-anchor="middle" font-size="15" font-weight="700" fill="#7c2d12">SDCOURSE: {short production label}</text>
  <text x="530" y="90" text-anchor="middle" font-size="13" fill="#7c2d12">{one-line paraphrase}</text>
</svg>
</div>
<div class="sketch-cap">{one-sentence caption for the diagram}</div>

<div class="box xr"><div class="box-lbl">Where They Converge / Diverge</div>
<p><strong>Converge:</strong> {one sentence}</p>
<p><strong>Diverge:</strong> {one sentence}</p>
</div>

<div class="recall">
<div class="recall-head">Active Recall</div>
<div class="q"><span class="q-n">Q1.</span> {question testing the Luc decision rule}</div>
<div class="q"><span class="q-n">Q2.</span> {question testing the sdcourse benchmark/failure mode}</div>
<div class="q"><span class="q-n">Q3.</span> {question testing the convergence/divergence synthesis}</div>
</div>
</div>
```

Use the existing `.box.xr` CSS class (already defined in the CSS block, purple `#7c3aed`) for the **"Where They Converge / Diverge"** callout — no new CSS class needed.

### Per-chapter acceptance check

After writing `CH{n}` in `scripts/generate_sdcourse_luc.py`, run:

```bash
python3 -c "
import ast
tree = ast.parse(open('scripts/generate_sdcourse_luc.py').read())
print('syntax OK')
"
python3 - <<'EOF'
import re
src = open('scripts/generate_sdcourse_luc.py').read()
m = re.search(r'CH{n} = """(.*?)"""', src, re.S)
assert m, 'CH{n} not found'
block = m.group(1)
assert block.count('data-author="luc"') >= 1, 'missing Luc quote'
assert block.count('data-author="sdcourse"') >= 1, 'missing sdcourse quote'
assert '<table>' in block, 'missing comparison table'
assert '<svg' in block, 'missing inline SVG diagram'
assert 'box xr' in block, 'missing convergence/divergence callout'
assert 'class="recall"' in block, 'missing recall block'
print('CH{n} structural check: PASS')
EOF
```

(Replace `{n}` with the literal chapter number in both the regex and the printed messages when running for each chapter.)

Expected: `syntax OK` then `CH{n} structural check: PASS`.

**Additionally, whenever a chapter reuses a source citation range another chapter
already used** (the plan marks these with `*` in the chapter tables — 14 pairs
across Chapters 6–23, e.g. Ch8/Ch14 both citing Rate Limiting, Ch16/Ch21 both
citing Leader Election), run:

```bash
python3 scripts/check_chapter_overlap.py
```

Expected: `No verbatim sentence overlap found across N chapters.` A reported
sentence shared between the two chapters citing the same range means the newer
chapter copy-pasted rather than re-synthesized — reword it before moving on.
This is the exact bug class that hit Chapter 6 (reusing Chapter 3's exact
sentences for the same `sdcourse.md:236-250` citation, fixed in commit
`25510a4`); this script catches it offline instead of waiting for the live
verification loop to flag it a fix-and-reverify cycle later.

---

## Task 1: Generator scaffold (CSS + cover + empty assembly + PDF smoke test)

**Files:**
- Create: `scripts/generate_sdcourse_luc.py`

**Interfaces:**
- Produces: module-level Python string constants `CSS`, `COVER`, and the assembly variable `HTML_CONTENT` (an f-string referencing `COVER` and, once defined, `CH1..CH23`). Later tasks add `CH{n} = """..."""` constants and extend the `{COVER}\n{CH1}\n...` interpolation inside `HTML_CONTENT`.

- [ ] **Step 1: Write the generator scaffold**

```python
#!/usr/bin/env python3
"""
System Design, Two Lenses: Decide Consciously, Build for Production
Dual-lens reference pairing lucsystemdesign (decision frameworks) with
sdcourse (production build) across 23 chapters.
Run: python3 scripts/generate_sdcourse_luc.py
"""
import os

# ─────────────────────────────────────────────────────────────────────────────
# CSS — copied from generate_vutr_spark.py, Mermaid <script> tag NOT included
# (Mermaid does not render in headless-Chrome print — see repo CLAUDE.md /
# spark-pack-scribble-layer memory). All diagrams are inline SVG instead.
# ─────────────────────────────────────────────────────────────────────────────
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,300;0,8..60,400;0,8..60,600;0,8..60,700;1,8..60,400&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&family=Caveat:wght@400;600;700&display=swap');
:root {
  --ink:#1c1c2e; --body:#2d2d3e; --muted:#666680; --border:#d8d8e8; --bg:#fff; --alt:#f8f8fc;
  --s-bg:#f0fdf4; --s-bd:#22c55e; --s-tx:#14532d;
  --n-bg:#eff6ff; --n-bd:#3b82f6; --n-tx:#1e3a8a;
  --d-bg:#faf5ff; --d-bd:#a855f7; --d-tx:#581c87;
  --f-bg:#fff1f2; --f-bd:#f43f5e; --f-tx:#881337;
  --r-bg:#fff7ed; --r-bd:#f97316; --r-tx:#7c2d12;
  --l-bg:#f0f9ff; --l-bd:#0ea5e9; --l-tx:#0c4a6e;
}
*{box-sizing:border-box;margin:0;padding:0}
@page{size:A4;margin:18mm 16mm 18mm 16mm}
body{font-family:'Source Serif 4',Georgia,serif;font-size:9.5pt;line-height:1.72;color:var(--ink);background:#fff}

/* Cover */
.cover{page-break-after:always;display:flex;flex-direction:column;justify-content:center;min-height:250mm;padding:0 8mm}
.eyebrow{font-family:'Inter',sans-serif;font-size:7.5pt;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:#3b82f6;margin-bottom:5mm}
.cover-title{font-family:'Inter',sans-serif;font-size:26pt;font-weight:700;line-height:1.15;color:var(--ink);margin-bottom:4mm}
.cover-sub{font-size:12pt;color:var(--muted);font-style:italic;margin-bottom:9mm}
.rule{width:14mm;height:3px;background:#3b82f6;margin-bottom:7mm}
.cover-desc{font-family:'Inter',sans-serif;font-size:9pt;color:var(--body);line-height:1.6;max-width:130mm;margin-bottom:10mm}
.cover-toc{margin-top:4mm}
.toc-item{display:flex;align-items:baseline;padding:2mm 0;border-bottom:1px solid var(--border);font-family:'Inter',sans-serif;font-size:8.5pt}
.toc-n{font-weight:700;color:#3b82f6;width:16mm;flex-shrink:0}

/* Chapter */
.chapter{page-break-before:always}
.ch-head{margin-bottom:7mm;padding-bottom:4mm;border-bottom:2px solid var(--border)}
.ch-eye{font-family:'Inter',sans-serif;font-size:7.5pt;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#3b82f6;margin-bottom:2mm}
.chapter h1{font-family:'Inter',sans-serif;font-size:18pt;font-weight:700;line-height:1.2;color:var(--ink);margin-bottom:2mm}
.ch-src{font-family:'Inter',sans-serif;font-size:8pt;color:var(--muted);margin-bottom:3mm}
.ch-sum{font-size:10pt;font-style:italic;color:var(--body);line-height:1.6}

/* Topics */
.topic{margin-bottom:8mm}
.topic h2{font-family:'Inter',sans-serif;font-size:12pt;font-weight:700;color:var(--ink);margin:6mm 0 2mm;padding-bottom:1.5mm;border-bottom:1px solid var(--border)}
.topic h3{font-family:'Inter',sans-serif;font-size:10.5pt;font-weight:600;color:var(--body);margin:4mm 0 1.5mm}
.topic p{margin-bottom:2.5mm}
.topic ul,.topic ol{padding-left:5mm;margin-bottom:2.5mm}
.topic li{margin-bottom:1.2mm}
.topic strong{font-weight:700;color:var(--ink)}
code{font-family:'JetBrains Mono',monospace;font-size:8pt;background:var(--alt);padding:1px 3px;border-radius:3px;color:#c2410c}
pre{font-family:'JetBrains Mono',monospace;font-size:8pt;background:#1e1e2e;color:#cdd6f4;padding:3.5mm;border-radius:4px;margin:2.5mm 0;page-break-inside:avoid;line-height:1.5}

/* Callouts */
.box{margin:3mm 0;border-left:4px solid;padding:3.5mm 4.5mm;border-radius:0 4px 4px 0;page-break-inside:avoid}
.box-lbl{font-family:'Inter',sans-serif;font-size:7pt;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:1.5mm}
.box.s{background:var(--s-bg);border-color:var(--s-bd)}.box.s .box-lbl{color:var(--s-bd)}
.box.n{background:var(--n-bg);border-color:var(--n-bd)}.box.n .box-lbl{color:var(--n-bd)}
.box.d{background:var(--d-bg);border-color:var(--d-bd)}.box.d .box-lbl{color:var(--d-bd)}
.box.f{background:var(--f-bg);border-color:var(--f-bd)}.box.f .box-lbl{color:var(--f-bd)}
.box.r{background:var(--r-bg);border-color:var(--r-bd)}.box.r .box-lbl{color:var(--r-bd)}
.box.l{background:var(--l-bg);border-color:var(--l-bd)}.box.l .box-lbl{color:var(--l-bd)}
.box.xr{background:#f5f3ff;border-color:#7c3aed}.box.xr .box-lbl{color:#7c3aed}
.box p{margin-bottom:1.5mm}.box p:last-child{margin-bottom:0}
.box ul{padding-left:4.5mm}.box li{margin-bottom:1mm}

/* Tables */
table{width:100%;border-collapse:collapse;margin:2.5mm 0;font-size:8.5pt;font-family:'Inter',sans-serif;page-break-inside:avoid}
thead{background:var(--alt)}
th{text-align:left;font-weight:700;padding:2mm 2.5mm;border-bottom:2px solid var(--border);color:var(--ink);font-size:8pt;text-transform:uppercase;letter-spacing:.3px}
td{padding:1.8mm 2.5mm;border-bottom:1px solid var(--border);vertical-align:top;line-height:1.5}
tr:last-child td{border-bottom:none}
.g{color:#15803d;font-weight:600}.y{color:#d97706}.rd{color:#dc2626;font-weight:600}
.hr{background:#fefce8}

/* Recall section */
.recall{margin-top:6mm;padding:4mm;background:var(--alt);border:1px solid var(--border);border-radius:4px;page-break-inside:avoid}
.recall-head{font-family:'Inter',sans-serif;font-size:7.5pt;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:var(--muted);margin-bottom:3mm}
.q{margin-bottom:2.5mm;padding-left:4mm;border-left:2px solid var(--border)}
.q-n{font-family:'Inter',sans-serif;font-size:7.5pt;font-weight:700;color:#3b82f6}

/* Quote */
.quote{font-style:italic;color:var(--muted);border-left:3px solid var(--border);padding:2mm 0 2mm 4mm;margin:4mm 0;font-size:9pt}
.quote cite{display:block;font-style:normal;font-size:8pt;margin-top:1mm}

/* Scribble layer — hand-drawn diagrams (GRINDE: Non-verbal + Emphasized) */
.sketch{margin:4mm 0 1mm;text-align:center;page-break-inside:avoid}
.sketch svg{max-width:100%;height:auto}
.sketch-cap{font-family:'Caveat',cursive;font-size:12pt;color:#44446a;text-align:center;margin:0 0 4mm;line-height:1.25}
"""

# ─────────────────────────────────────────────────────────────────────────────
# COVER
# ─────────────────────────────────────────────────────────────────────────────
COVER = """
<div class="cover">
  <div class="eyebrow">System Design · Two Lenses</div>
  <div class="cover-title">Decide Consciously, Build for Production</div>
  <div class="cover-sub">Pairing lucsystemdesign's decision frameworks with sdcourse's production benchmarks across 23 chapters of distributed-systems fundamentals.</div>
  <div class="rule"></div>
  <div class="cover-desc">Every chapter carries both voices: Luc reframes the misconception and gives a decision rule ("when NOT to use it"); sdcourse grounds the same domain in production failure modes and exact benchmarks. Each chapter closes with an explicit convergence/divergence synthesis.</div>
  <div class="cover-toc">
    <!-- TOC items appended here, one per phase, as chapters land -->
  </div>
</div>
"""

# ─────────────────────────────────────────────────────────────────────────────
# CHAPTERS — appended below, one CH{n} block per chapter, across 4 phases
# ─────────────────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────────────────
# ASSEMBLY + GENERATION
# ─────────────────────────────────────────────────────────────────────────────
HTML_CONTENT = f"""<!DOCTYPE html>
<html lang='en'>
<head>
<meta charset='UTF-8'>
<meta name='viewport' content='width=device-width, initial-scale=1.0'>
<title>System Design, Two Lenses — lucsystemdesign x sdcourse</title>
<style>{CSS}</style>
</head>
<body>
{COVER}
</body>
</html>"""

os.makedirs('output', exist_ok=True)
with open('output/sdcourse_luc.html', 'w') as f:
    f.write(HTML_CONTENT)
print('Written: output/sdcourse_luc.html')

try:
    import subprocess
    chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    pdf_path = "output/sdcourse_luc.pdf"
    html_path = "output/sdcourse_luc.html"
    result = subprocess.run(
        [chrome, "--headless", "--disable-gpu",
         f"--print-to-pdf={pdf_path}",
         "--print-to-pdf-no-header", html_path],
        capture_output=True, text=True
    )
    if "bytes written" in result.stderr or "written to file" in result.stderr:
        size = os.path.getsize(pdf_path)
        print(f"PDF written: {pdf_path} ({size:,} bytes)")
    else:
        print("Chrome output:", result.stderr[-200:])
        print(f"HTML is ready at {html_path} — open in browser and Print → Save as PDF")
except Exception as e:
    print(f"PDF generation error: {e}")
    print(f"HTML is ready at output/sdcourse_luc.html")
```

- [ ] **Step 2: Run the scaffold and verify it renders**

```bash
python3 scripts/generate_sdcourse_luc.py
```

Expected: `Written: output/sdcourse_luc.html` then a line starting with `PDF written: output/sdcourse_luc.pdf (` followed by a byte count.

- [ ] **Step 3: Commit**

```bash
git add scripts/generate_sdcourse_luc.py
git commit -m "feat(sdcourse-luc): scaffold dual-lens pack generator (CSS + cover + PDF export)"
```

---

## Task 2: Verification workflow scaffold

**Files:**
- Create: `.claude/workflows/verify-sdcourse-luc.js`

**Interfaces:**
- Consumes: `args.chapterIds` (array of integers, e.g. `[1,2,3,4,5,6]`) passed at `Workflow` invocation time.
- Produces: `CHAPTERS` (array of `{id, title, content}`, empty until phase tasks append entries), `KNOWLEDGE_BY_CHAPTER` (object keyed by chapter id: `{luc: string, sdcourse: string}`, empty until phase tasks append entries). Later phase-verification tasks invoke this script via the `Workflow` tool with different `args.chapterIds` slices and read the returned `{results, allPassed, signoff}`.

- [ ] **Step 1: Write the workflow script**

```javascript
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
```

- [ ] **Step 2: Verify the script is syntactically valid JS**

```bash
node --check .claude/workflows/verify-sdcourse-luc.js 2>&1 || node -e "
const fs = require('fs');
const src = fs.readFileSync('.claude/workflows/verify-sdcourse-luc.js', 'utf8');
new Function(src.replace(/^export const meta.*?^}/ms, ''));
console.log('parses OK (ignoring top-level await/workflow globals)');
"
```

Expected: no syntax errors reported (the script uses top-level `await` and workflow globals like `args`/`agent`/`pipeline`/`parallel`/`phase`/`log`, which only resolve inside the `Workflow` tool's runtime — this step only checks for JS syntax errors, not execution).

- [ ] **Step 3: Commit**

```bash
git add .claude/workflows/verify-sdcourse-luc.js
git commit -m "feat(sdcourse-luc): scaffold dual-examiner verification workflow"
```

---

## Phase 1 — Part I (Foundations) + Part II (Data, Storage & Caching): Chapters 1–6

### Task 3: Chapter 1 — Quality Attributes, Trade-offs & the Production Reality Gap

**Files:**
- Modify: `scripts/generate_sdcourse_luc.py` (add `CH1` constant after the `# CHAPTERS` comment block)

**Sources:**
- Luc — Quality Attributes: `.claude/agents/lucsystemdesign.md:74-84`
- sdcourse — Course Structure and Curriculum Design: `.claude/agents/sdcourse.md:33-50`

- [ ] **Step 1: Write `CH1` following the shared skeleton** (see "Shared reference: per-chapter HTML skeleton" above). Title: "Quality Attributes, Trade-offs & the Production Reality Gap". Luc's lens section must synthesize the cited quality-attributes lines (attributes vs pillars vs tactics; "you cannot maximize everything"). sdcourse's lens section must synthesize the cited course-structure lines (the "map vs shovel" gap between knowing and building). Insert as:

```python
# ─────────────────────────────────────────────────────────────────────────────
# CHAPTER 1 — Quality Attributes, Trade-offs & the Production Reality Gap
# ─────────────────────────────────────────────────────────────────────────────
CH1 = """
<div class="chapter">
...
</div>
"""
```

- [ ] **Step 2: Run the per-chapter acceptance check** (substitute `{n}` = `1` in the "Per-chapter acceptance check" commands above).

Expected: `syntax OK` then `CH1 structural check: PASS`.

- [ ] **Step 3: Commit**

```bash
git add scripts/generate_sdcourse_luc.py
git commit -m "feat(sdcourse-luc): write Chapter 1 — Quality Attributes & Production Reality Gap"
```

### Task 4: Chapter 2 — Consistency Models: CAP, ACID vs BASE, Strong/Eventual & Multi-Region

**Files:** Modify: `scripts/generate_sdcourse_luc.py`

**Sources:**
- Luc — CAP Theorem: `.claude/agents/lucsystemdesign.md:317-329`; ACID vs BASE: `:422-431`; Strong vs Eventual Consistency: `:290-299`
- sdcourse — Multi-Region Replication and Distributed Consistency: `.claude/agents/sdcourse.md:217-235`

- [ ] **Step 1:** Write `CH2` per the shared skeleton (title as above). Luc's lens covers all three cited sections; sdcourse's lens covers multi-region replication.
- [ ] **Step 2:** Run the per-chapter acceptance check for `n=2`. Expected: `CH2 structural check: PASS`.
- [ ] **Step 3:** `git add scripts/generate_sdcourse_luc.py && git commit -m "feat(sdcourse-luc): write Chapter 2 — Consistency Models"`

### Task 5: Chapter 3 — Database Selection & Distributed Query Patterns

**Sources:**
- Luc — Database Selection: `.claude/agents/lucsystemdesign.md:30-45`; SQL vs NoSQL: `:359-367`
- sdcourse — Distributed Query Engine and Caching Patterns: `.claude/agents/sdcourse.md:236-250`

- [ ] **Step 1:** Write `CH3` per the shared skeleton. Convergence/divergence angle: Luc frames choosing a store by "the hardest question you ask"; sdcourse shows the production reality of answering sub-second queries on historical data.
- [ ] **Step 2:** Run the per-chapter acceptance check for `n=3`. Expected: `CH3 structural check: PASS`.
- [ ] **Step 3:** `git add scripts/generate_sdcourse_luc.py && git commit -m "feat(sdcourse-luc): write Chapter 3 — Database Selection & Query Patterns"`

### Task 6: Chapter 4 — Indexing, CDC & Structured Log Data

**Sources:**
- Luc — Database Indexing: `.claude/agents/lucsystemdesign.md:488-497`; Change Data Capture (CDC): `:178-188`
- sdcourse — Log Format Normalization and Serialization: `.claude/agents/sdcourse.md:333-347`; Faceted Search and Multi-Dimensional Filtering: `:317-332`

- [ ] **Step 1:** Write `CH4` per the shared skeleton. Convergence/divergence angle: indexing/CDC structure data for fast retrieval on the OLTP side; log normalization/faceted search do the same for the log-pipeline side.
- [ ] **Step 2:** Run the per-chapter acceptance check for `n=4`. Expected: `CH4 structural check: PASS`.
- [ ] **Step 3:** `git add scripts/generate_sdcourse_luc.py && git commit -m "feat(sdcourse-luc): write Chapter 4 — Indexing, CDC & Structured Log Data"`

### Task 7: Chapter 5 — Tiered Storage & Caching Economics

**Sources:**
- Luc — Database Caching Strategies: `.claude/agents/lucsystemdesign.md:244-255`; Connection Pooling: `:169-177`
- sdcourse — Distributed Log Storage and Tiered Architecture: `.claude/agents/sdcourse.md:143-157`

- [ ] **Step 1:** Write `CH5` per the shared skeleton. Convergence/divergence angle: Luc's caching-strategy decision framework vs sdcourse's hot/warm/cold tiering as the production execution of "which tier does this data belong in."
- [ ] **Step 2:** Run the per-chapter acceptance check for `n=5`. Expected: `CH5 structural check: PASS`.
- [ ] **Step 3:** `git add scripts/generate_sdcourse_luc.py && git commit -m "feat(sdcourse-luc): write Chapter 5 — Tiered Storage & Caching Economics"`

### Task 8: Chapter 6 — Fast Access: Redis, Consistent Hashing & Bloom Filters

**Sources:**
- Luc — Redis: `.claude/agents/lucsystemdesign.md:310-316`; Consistent Hashing: `:200-210`; Bloom Filters: `:211-220`
- sdcourse — Bloom Filters in Log Processing: `.claude/agents/sdcourse.md:301-316`; Distributed Query Engine and Caching Patterns: `:236-250` (reused from Chapter 3 — this occurrence takes the fast-access/in-memory-hashing angle, distinct from Chapter 3's "which store answers which question" angle)

- [ ] **Step 1:** Write `CH6` per the shared skeleton. Bloom Filters is a natural 1:1 dual topic (both authors have a dedicated section) — lead with that.
- [ ] **Step 2:** Run the per-chapter acceptance check for `n=6`. Expected: `CH6 structural check: PASS`.
- [ ] **Step 3:** `git add scripts/generate_sdcourse_luc.py && git commit -m "feat(sdcourse-luc): write Chapter 6 — Fast Access: Redis, Consistent Hashing & Bloom Filters"`

### Task 9: Assemble & render Phase 1 PDF

**Files:** Modify: `scripts/generate_sdcourse_luc.py` (the `HTML_CONTENT` assembly and `COVER`'s TOC)

- [ ] **Step 1: Extend the cover TOC** — in `COVER`, replace the `<!-- TOC items appended here... -->` comment with:

```html
    <div class="toc-item"><span class="toc-n">Ch 1</span><span>Quality Attributes, Trade-offs & the Production Reality Gap</span></div>
    <div class="toc-item"><span class="toc-n">Ch 2</span><span>Consistency Models: CAP, ACID vs BASE, Strong/Eventual & Multi-Region</span></div>
    <div class="toc-item"><span class="toc-n">Ch 3</span><span>Database Selection & Distributed Query Patterns</span></div>
    <div class="toc-item"><span class="toc-n">Ch 4</span><span>Indexing, CDC & Structured Log Data</span></div>
    <div class="toc-item"><span class="toc-n">Ch 5</span><span>Tiered Storage & Caching Economics</span></div>
    <div class="toc-item"><span class="toc-n">Ch 6</span><span>Fast Access: Redis, Consistent Hashing & Bloom Filters</span></div>
```

- [ ] **Step 2: Extend the `HTML_CONTENT` assembly**, changing:

```python
HTML_CONTENT = f"""<!DOCTYPE html>
...
<body>
{COVER}
</body>
</html>"""
```

to:

```python
HTML_CONTENT = f"""<!DOCTYPE html>
...
<body>
{COVER}
{CH1}
{CH2}
{CH3}
{CH4}
{CH5}
{CH6}
</body>
</html>"""
```

- [ ] **Step 3: Regenerate and verify**

```bash
python3 scripts/generate_sdcourse_luc.py
```

Expected: `Written: output/sdcourse_luc.html` then `PDF written: output/sdcourse_luc.pdf (` with a byte count larger than Task 1's cover-only render.

- [ ] **Step 4: Commit**

```bash
git add scripts/generate_sdcourse_luc.py
git commit -m "feat(sdcourse-luc): assemble Phase 1 (Chapters 1-6) into PDF"
```

### Task 10: Extend workflow with Phase 1 chapters

**Files:** Modify: `.claude/workflows/verify-sdcourse-luc.js`

- [ ] **Step 1: Populate `CHAPTERS`** — replace `const CHAPTERS = []` with an array of 6 entries, each `{id, title, content}` where `content` is a **plain-text mirror** of the corresponding `CH{n}` HTML (strip tags, keep all prose/quotes/table data — this is what Justin/Alex read as "the chapter"). Example shape for one entry (repeat for ids 2–6 using each chapter's own title/content):

```javascript
const CHAPTERS = [
  {
    id: 1,
    title: 'Quality Attributes, Trade-offs & the Production Reality Gap',
    content: `[plain-text transcription of CH1's prose, quotes, table rows, and callouts from scripts/generate_sdcourse_luc.py]`,
  },
  // ids 2-6 follow the same {id, title, content} shape
]
```

- [ ] **Step 2: Populate `KNOWLEDGE_BY_CHAPTER`** — replace `const KNOWLEDGE_BY_CHAPTER = {}` with entries for ids 1–6, each `{luc: string, sdcourse: string}` summarizing the source material examiners should draw questions from, e.g.:

```javascript
const KNOWLEDGE_BY_CHAPTER = {
  1: {
    luc: 'System Design Quality Attributes (lucsystemdesign.md:74-84): attributes vs pillars vs tactics; you cannot maximize everything; vague targets do not guide design.',
    sdcourse: 'Course Structure and Curriculum Design (sdcourse.md:33-50): the gap between knowing system design and building a production system; map vs shovel.',
  },
  // ids 2-6 follow the same {luc, sdcourse} shape, citing that chapter's Task N source lines
}
```

- [ ] **Step 2: Verify JS syntax**

```bash
node --check .claude/workflows/verify-sdcourse-luc.js 2>&1 || node -e "
const fs = require('fs');
const src = fs.readFileSync('.claude/workflows/verify-sdcourse-luc.js', 'utf8');
new Function(src.replace(/^export const meta.*?^}/ms, ''));
console.log('parses OK');
"
```

Expected: `parses OK` (or no output from `node --check`).

- [ ] **Step 3: Commit**

```bash
git add .claude/workflows/verify-sdcourse-luc.js
git commit -m "feat(sdcourse-luc): sync Phase 1 chapter content into verification workflow"
```

### Task 11: Run Phase 1 verification loop to allPassed + sign-off

**Files:** None (this task drives the `Workflow` tool interactively; any fixes it produces land back in `scripts/generate_sdcourse_luc.py` and `.claude/workflows/verify-sdcourse-luc.js`).

- [ ] **Step 1: Invoke the workflow** for Phase 1 via the `Workflow` tool with `scriptPath: ".claude/workflows/verify-sdcourse-luc.js"` and `args: { chapterIds: [1,2,3,4,5,6] }`.

- [ ] **Step 2: Read the returned `results` array.** For any chapter with `pass: false`, read its `lucScore.gaps`, `sdScore.gaps`, and `audit.improvements`/`audit.blockers`.

- [ ] **Step 3: For each failing chapter, apply a fix round:**
  1. Edit that chapter's `CH{n}` block in `scripts/generate_sdcourse_luc.py` to address every cited gap (accuracy gaps = correct the wrong/imprecise content; coverage gaps = add the missing concept) and every Alex high/medium improvement request.
  2. Mirror the same edit into `CHAPTERS[n].content` in `.claude/workflows/verify-sdcourse-luc.js` (the sync invariant — do not skip this).
  3. Regenerate: `python3 scripts/generate_sdcourse_luc.py` and confirm `PDF written:` appears.

- [ ] **Step 4: Re-run the workflow** via `Workflow` with the same `scriptPath` and `args`, passing `resumeFromRunId` from Step 1's result — unchanged chapters return cached results instantly; only edited chapters re-run.

- [ ] **Step 5: Repeat Steps 2–4 until `allPassed: true`.**

- [ ] **Step 6: Confirm the sign-off** — the returned `signoff.allPassed` must be `true` (all of `luc.pass`, `sd.pass`, `justin.pass`, `alex.pass`). If any sign-off agent returns `pass: false`, apply one more fix round addressing its `notes`, regenerate, and re-run once more.

### Task 12: Commit Phase 1

- [ ] **Step 1: Commit the final Phase 1 state** (only if Task 11's fix rounds produced uncommitted edits beyond Tasks 3–10; if Task 11 made no further edits, skip this task).

```bash
git add scripts/generate_sdcourse_luc.py .claude/workflows/verify-sdcourse-luc.js
git commit -m "fix(sdcourse-luc): Phase 1 verification fixes — Chapters 1-6 all >=9.0, signed off"
```

---

## Phase 2 — Part III (Communication, APIs & Messaging): Chapters 7–12

### Task 13: Chapter 7 — API Architecture: REST, GraphQL, gRPC & Idempotency

**Sources:**
- Luc — REST vs GraphQL vs gRPC: `.claude/agents/lucsystemdesign.md:85-97`; REST APIs: `:350-358`; gRPC: `:432-445`; Idempotency in API Design: `:478-487`
- sdcourse — Webhook Notifications and Event Routing: `.claude/agents/sdcourse.md:422-435`

- [ ] **Step 1:** Write `CH7` per the shared skeleton. Convergence/divergence angle: Luc's API-style contract choice vs sdcourse's production event-driven API integration pattern (webhooks).
- [ ] **Step 2:** Run the per-chapter acceptance check for `n=7`. Expected: `CH7 structural check: PASS`.
- [ ] **Step 3:** `git add scripts/generate_sdcourse_luc.py && git commit -m "feat(sdcourse-luc): write Chapter 7 — API Architecture"`

### Task 14: Chapter 8 — Gateways, Proxies & CDNs

**Sources:**
- Luc — API Gateway vs Load Balancer vs Reverse Proxy: `.claude/agents/lucsystemdesign.md:221-231`; Forward Proxy vs Reverse Proxy: `:507-518`; Content Delivery Networks (CDNs): `:123-134`
- sdcourse — Rate Limiting and Sliding Window Algorithms: `.claude/agents/sdcourse.md:348-360` (reused in Chapter 14 with the algorithm-mechanics angle; here the angle is edge-layer enforcement)

- [ ] **Step 1:** Write `CH8` per the shared skeleton. Convergence/divergence angle: Luc's gateway/proxy/CDN taxonomy vs sdcourse's production rate-limiting as what actually runs at that edge layer.
- [ ] **Step 2:** Run the per-chapter acceptance check for `n=8`. Expected: `CH8 structural check: PASS`.
- [ ] **Step 3:** `git add scripts/generate_sdcourse_luc.py && git commit -m "feat(sdcourse-luc): write Chapter 8 — Gateways, Proxies & CDNs"`

### Task 15: Chapter 9 — Networking & Protocol Layers + Batching Economics

**Sources:**
- Luc — Network Protocols and Layered Debugging: `.claude/agents/lucsystemdesign.md:60-73`
- sdcourse — Network Batching and Throughput Optimization: `.claude/agents/sdcourse.md:51-69`

- [ ] **Step 1:** Write `CH9` per the shared skeleton.
- [ ] **Step 2:** Run the per-chapter acceptance check for `n=9`. Expected: `CH9 structural check: PASS`.
- [ ] **Step 3:** `git add scripts/generate_sdcourse_luc.py && git commit -m "feat(sdcourse-luc): write Chapter 9 — Networking & Protocol Layers"`

### Task 16: Chapter 10 — Real-Time & Async: WebSockets, Sync/Async, Webhooks

**Sources:**
- Luc — WebSockets: `.claude/agents/lucsystemdesign.md:458-468`; Synchronous vs Asynchronous Communication: `:300-309`; Health Checks vs Heartbeats: `:446-457`
- sdcourse — Webhook Notifications and Event Routing: `.claude/agents/sdcourse.md:422-435` (reused from Chapter 7 with a delivery-mechanism angle here vs an API-contract angle there); Task Scheduling and Observability: `:408-421` (reused in Chapter 17 with a liveness/heartbeat angle here)

- [ ] **Step 1:** Write `CH10` per the shared skeleton.
- [ ] **Step 2:** Run the per-chapter acceptance check for `n=10`. Expected: `CH10 structural check: PASS`.
- [ ] **Step 3:** `git add scripts/generate_sdcourse_luc.py && git commit -m "feat(sdcourse-luc): write Chapter 10 — Real-Time & Async Communication"`

### Task 17: Chapter 11 — Messaging & Event Streaming: EDA, Pub/Sub, Kafka

**Sources:**
- Luc — Event-Driven Architecture (EDA): `.claude/agents/lucsystemdesign.md:388-397`; Pub/Sub: `:256-266`; Message Queues: `:469-477`
- sdcourse — Event-Driven Architecture and Apache Kafka: `.claude/agents/sdcourse.md:158-174`; Distributed Log Parsing with Kafka: `:361-373`; Dead Letter Queues: `:193-216` (reused in Chapter 15 with a general-resilience angle here vs the messaging-pipeline angle here)

- [ ] **Step 1:** Write `CH11` per the shared skeleton. This is the largest chapter of Phase 2 — both authors have 3 cited sections; keep each Topic subsection focused (one `<h2>` per major sub-theme rather than one giant block).
- [ ] **Step 2:** Run the per-chapter acceptance check for `n=11`. Expected: `CH11 structural check: PASS`.
- [ ] **Step 3:** `git add scripts/generate_sdcourse_luc.py && git commit -m "feat(sdcourse-luc): write Chapter 11 — Messaging & Event Streaming"`

### Task 18: Chapter 12 — Stream Processing & Batch: Kafka Streams, Sliding Windows, MapReduce

**Sources:**
- Luc — Synchronous vs Asynchronous Communication: `.claude/agents/lucsystemdesign.md:300-309` (reused from Chapter 10; here the angle is "stream processing is continuous async communication at scale")
- sdcourse — Stream Processing: Kafka Streams and Sliding Windows: `.claude/agents/sdcourse.md:269-286`; MapReduce for Batch Log Processing: `:287-300`

- [ ] **Step 1:** Write `CH12` per the shared skeleton.
- [ ] **Step 2:** Run the per-chapter acceptance check for `n=12`. Expected: `CH12 structural check: PASS`.
- [ ] **Step 3:** `git add scripts/generate_sdcourse_luc.py && git commit -m "feat(sdcourse-luc): write Chapter 12 — Stream Processing & Batch"`

### Task 19: Assemble & render Phase 2 PDF

**Files:** Modify: `scripts/generate_sdcourse_luc.py`

- [ ] **Step 1: Extend the cover TOC** with Ch 7–12 entries (same `<div class="toc-item">` pattern as Task 9 Step 1, using each chapter's title from Tasks 13–18).
- [ ] **Step 2: Extend `HTML_CONTENT`** to add `{CH7}` through `{CH12}` after `{CH6}`.
- [ ] **Step 3: Regenerate and verify**

```bash
python3 scripts/generate_sdcourse_luc.py
```

Expected: `Written: output/sdcourse_luc.html` then `PDF written: output/sdcourse_luc.pdf (` with a larger byte count than Task 9.

- [ ] **Step 4: Commit**

```bash
git add scripts/generate_sdcourse_luc.py
git commit -m "feat(sdcourse-luc): assemble Phase 2 (Chapters 7-12) into PDF"
```

### Task 20: Extend workflow with Phase 2 chapters

**Files:** Modify: `.claude/workflows/verify-sdcourse-luc.js`

- [ ] **Step 1:** Append 6 entries (ids 7–12) to `CHAPTERS`, same `{id, title, content}` shape as Task 10.
- [ ] **Step 2:** Append 6 entries (ids 7–12) to `KNOWLEDGE_BY_CHAPTER`, same `{luc, sdcourse}` shape as Task 10, citing each chapter's Task 13–18 source lines.
- [ ] **Step 3:** Verify JS syntax (same command as Task 10 Step 2). Expected: `parses OK`.
- [ ] **Step 4:** Commit:

```bash
git add .claude/workflows/verify-sdcourse-luc.js
git commit -m "feat(sdcourse-luc): sync Phase 2 chapter content into verification workflow"
```

### Task 21: Run Phase 2 verification loop to allPassed + sign-off

Same procedure as Task 11, with `args: { chapterIds: [7,8,9,10,11,12] }`.

- [ ] **Step 1:** Invoke the workflow with `args: { chapterIds: [7,8,9,10,11,12] }`.
- [ ] **Step 2:** Read `results`; for any `pass: false` chapter, read `lucScore.gaps` / `sdScore.gaps` / `audit.improvements` / `audit.blockers`.
- [ ] **Step 3:** Apply fix rounds (edit `CH{n}` in the generator + mirror into `CHAPTERS[n].content` in the workflow + regenerate) for every failing chapter.
- [ ] **Step 4:** Re-run via `resumeFromRunId` from Step 1.
- [ ] **Step 5:** Repeat until `allPassed: true`.
- [ ] **Step 6:** Confirm `signoff.allPassed: true`; if not, one more fix round on the cited `notes`, regenerate, re-run.

### Task 22: Commit Phase 2

- [ ] **Step 1:** If Task 21 produced fix-round edits, commit them:

```bash
git add scripts/generate_sdcourse_luc.py .claude/workflows/verify-sdcourse-luc.js
git commit -m "fix(sdcourse-luc): Phase 2 verification fixes — Chapters 7-12 all >=9.0, signed off"
```

---

## Phase 3 — Part IV (Scale, Reliability & Operations): Chapters 13–17

### Task 23: Chapter 13 — Load Balancing, Auto-Scaling & Capacity Planning

**Sources:**
- Luc — Load Balancing Algorithms: `.claude/agents/lucsystemdesign.md:46-59`
- sdcourse — Automated Scaling and Self-Healing Infrastructure: `.claude/agents/sdcourse.md:115-127` (reused in Chapter 22 with an infra-as-code execution angle here vs an algorithms/capacity-math angle here); Capacity Planning and Infrastructure Forecasting: `:128-142`; Predictive Analytics and Forecasting for Logs: `:374-387`

- [ ] **Step 1:** Write `CH13` per the shared skeleton.
- [ ] **Step 2:** Run the per-chapter acceptance check for `n=13`. Expected: `CH13 structural check: PASS`.
- [ ] **Step 3:** `git add scripts/generate_sdcourse_luc.py && git commit -m "feat(sdcourse-luc): write Chapter 13 — Load Balancing, Auto-Scaling & Capacity Planning"`

### Task 24: Chapter 14 — Rate Limiting & Backpressure

**Sources:**
- Luc — Rate Limiting: `.claude/agents/lucsystemdesign.md:189-199`
- sdcourse — Rate Limiting and Sliding Window Algorithms: `.claude/agents/sdcourse.md:348-360` (reused from Chapter 8; here the angle is the algorithm itself vs Chapter 8's edge-enforcement angle)

- [ ] **Step 1:** Write `CH14` per the shared skeleton. Rate Limiting is a 1:1 dual topic (both authors have a dedicated section) — lead with that.
- [ ] **Step 2:** Run the per-chapter acceptance check for `n=14`. Expected: `CH14 structural check: PASS`.
- [ ] **Step 3:** `git add scripts/generate_sdcourse_luc.py && git commit -m "feat(sdcourse-luc): write Chapter 14 — Rate Limiting & Backpressure"`

### Task 25: Chapter 15 — Resilience: Circuit Breakers, DLQs, Health Checks, Backup/Recovery

**Sources:**
- Luc — Circuit Breakers: `.claude/agents/lucsystemdesign.md:398-409`; Health Checks vs Heartbeats: `:446-457` (reused from Chapter 10 with a resilience-pattern angle here vs a real-time-liveness angle there)
- sdcourse — Circuit Breakers and Resilience Patterns: `.claude/agents/sdcourse.md:175-192`; Dead Letter Queues: `:193-216` (reused from Chapter 11 with a general-resilience angle here); Backup and Recovery for Distributed Systems: `:464-478`

- [ ] **Step 1:** Write `CH15` per the shared skeleton. Circuit Breakers is a 1:1 dual topic — lead with that.
- [ ] **Step 2:** Run the per-chapter acceptance check for `n=15`. Expected: `CH15 structural check: PASS`.
- [ ] **Step 3:** `git add scripts/generate_sdcourse_luc.py && git commit -m "feat(sdcourse-luc): write Chapter 15 — Resilience"`

### Task 26: Chapter 16 — Coordination: Leader Election, Service Discovery, Multi-Region

**Sources:**
- Luc — Service Discovery in Distributed Systems: `.claude/agents/lucsystemdesign.md:279-289`
- sdcourse — Distributed Cluster Coordination and Leader Election: `.claude/agents/sdcourse.md:251-268` (reused in Chapter 21 with a microservices-instance angle here vs a general-coordination angle here); Multi-Region Replication and Distributed Consistency: `:217-235` (reused from Chapter 2 with a coordination angle here vs a consistency-model angle there)

- [ ] **Step 1:** Write `CH16` per the shared skeleton.
- [ ] **Step 2:** Run the per-chapter acceptance check for `n=16`. Expected: `CH16 structural check: PASS`.
- [ ] **Step 3:** `git add scripts/generate_sdcourse_luc.py && git commit -m "feat(sdcourse-luc): write Chapter 16 — Coordination"`

### Task 27: Chapter 17 — Observability, Incident Management & BI

**Sources:**
- Luc — Observability: `.claude/agents/lucsystemdesign.md:232-243`
- sdcourse — Task Scheduling and Observability: `.claude/agents/sdcourse.md:408-421` (reused from Chapter 10 with an ops angle here); Incident Management and Automated Incident Response: `:449-463` (reused in Chapter 18 with a breach-response angle there vs a general-ops angle here); BI Integration and Business Intelligence from Logs: `:436-448`

- [ ] **Step 1:** Write `CH17` per the shared skeleton.
- [ ] **Step 2:** Run the per-chapter acceptance check for `n=17`. Expected: `CH17 structural check: PASS`.
- [ ] **Step 3:** `git add scripts/generate_sdcourse_luc.py && git commit -m "feat(sdcourse-luc): write Chapter 17 — Observability, Incident Management & BI"`

### Task 28: Assemble & render Phase 3 PDF

**Files:** Modify: `scripts/generate_sdcourse_luc.py`

- [ ] **Step 1:** Extend the cover TOC with Ch 13–17 entries.
- [ ] **Step 2:** Extend `HTML_CONTENT` to add `{CH13}` through `{CH17}` after `{CH12}`.
- [ ] **Step 3: Regenerate and verify**

```bash
python3 scripts/generate_sdcourse_luc.py
```

Expected: `Written: output/sdcourse_luc.html` then `PDF written: output/sdcourse_luc.pdf (` with a larger byte count than Task 19.

- [ ] **Step 4: Commit**

```bash
git add scripts/generate_sdcourse_luc.py
git commit -m "feat(sdcourse-luc): assemble Phase 3 (Chapters 13-17) into PDF"
```

### Task 29: Extend workflow with Phase 3 chapters

**Files:** Modify: `.claude/workflows/verify-sdcourse-luc.js`

- [ ] **Step 1:** Append 5 entries (ids 13–17) to `CHAPTERS`.
- [ ] **Step 2:** Append 5 entries (ids 13–17) to `KNOWLEDGE_BY_CHAPTER`, citing Tasks 23–27 source lines.
- [ ] **Step 3:** Verify JS syntax (same command as Task 10 Step 2). Expected: `parses OK`.
- [ ] **Step 4:** Commit:

```bash
git add .claude/workflows/verify-sdcourse-luc.js
git commit -m "feat(sdcourse-luc): sync Phase 3 chapter content into verification workflow"
```

### Task 30: Run Phase 3 verification loop to allPassed + sign-off

Same procedure as Task 11, with `args: { chapterIds: [13,14,15,16,17] }`.

- [ ] **Step 1:** Invoke the workflow with `args: { chapterIds: [13,14,15,16,17] }`.
- [ ] **Step 2:** Read `results`; for any `pass: false` chapter, read gaps/audit.
- [ ] **Step 3:** Apply fix rounds for every failing chapter (generator + workflow sync + regenerate).
- [ ] **Step 4:** Re-run via `resumeFromRunId`.
- [ ] **Step 5:** Repeat until `allPassed: true`.
- [ ] **Step 6:** Confirm `signoff.allPassed: true`; else one more fix round, regenerate, re-run.

### Task 31: Commit Phase 3

- [ ] **Step 1:** If Task 30 produced fix-round edits, commit:

```bash
git add scripts/generate_sdcourse_luc.py .claude/workflows/verify-sdcourse-luc.js
git commit -m "fix(sdcourse-luc): Phase 3 verification fixes — Chapters 13-17 all >=9.0, signed off"
```

---

## Phase 4 — Part V (Security, Architecture & Delivery): Chapters 18–23

### Task 32: Chapter 18 — Authentication: JWT, OAuth, SSO

**Sources:**
- Luc — JWT Authentication: `.claude/agents/lucsystemdesign.md:98-108`; OAuth: `:368-378`; Single Sign-On (SSO): `:342-349`
- sdcourse — Incident Management and Automated Incident Response: `.claude/agents/sdcourse.md:449-463` (reused from Chapter 17; here the angle is what happens when credentials are compromised)

- [ ] **Step 1:** Write `CH18` per the shared skeleton.
- [ ] **Step 2:** Run the per-chapter acceptance check for `n=18`. Expected: `CH18 structural check: PASS`.
- [ ] **Step 3:** `git add scripts/generate_sdcourse_luc.py && git commit -m "feat(sdcourse-luc): write Chapter 18 — Authentication"`

### Task 33: Chapter 19 — Encryption, Secrets & TLS

**Sources:**
- Luc — HTTPS and TLS: `.claude/agents/lucsystemdesign.md:498-506`
- sdcourse — TLS Encryption and Security: `.claude/agents/sdcourse.md:70-87`; Field-Level Encryption and PII Protection: `:88-101`

- [ ] **Step 1:** Write `CH19` per the shared skeleton.
- [ ] **Step 2:** Run the per-chapter acceptance check for `n=19`. Expected: `CH19 structural check: PASS`.
- [ ] **Step 3:** `git add scripts/generate_sdcourse_luc.py && git commit -m "feat(sdcourse-luc): write Chapter 19 — Encryption, Secrets & TLS"`

### Task 34: Chapter 20 — Compliance & Data Governance

**Sources:**
- Luc — Hashing vs Encryption vs Tokenization: `.claude/agents/lucsystemdesign.md:147-158`; Password Storage Security: `:267-278`
- sdcourse — Automated Compliance Reporting: `.claude/agents/sdcourse.md:102-114`

- [ ] **Step 1:** Write `CH20` per the shared skeleton. Convergence/divergence angle: compliance frameworks (GDPR/HIPAA/PCI-DSS retention windows) directly dictate how Luc's hashing/tokenization/password-storage rules must be applied.
- [ ] **Step 2:** Run the per-chapter acceptance check for `n=20`. Expected: `CH20 structural check: PASS`.
- [ ] **Step 3:** `git add scripts/generate_sdcourse_luc.py && git commit -m "feat(sdcourse-luc): write Chapter 20 — Compliance & Data Governance"`

### Task 35: Chapter 21 — Architecture Styles: Microservices & DDD

**Sources:**
- Luc — Microservices: `.claude/agents/lucsystemdesign.md:410-421`; Domain-Driven Design (DDD): `:109-122`
- sdcourse — Distributed Cluster Coordination and Leader Election: `.claude/agents/sdcourse.md:251-268` (reused from Chapter 16; here the angle is coordinating many microservice instances specifically)

- [ ] **Step 1:** Write `CH21` per the shared skeleton.
- [ ] **Step 2:** Run the per-chapter acceptance check for `n=21`. Expected: `CH21 structural check: PASS`.
- [ ] **Step 3:** `git add scripts/generate_sdcourse_luc.py && git commit -m "feat(sdcourse-luc): write Chapter 21 — Architecture Styles"`

### Task 36: Chapter 22 — Delivery & Infra: Docker/K8s, IaC, CI/CD, MCP

**Sources:**
- Luc — Docker vs Kubernetes: `.claude/agents/lucsystemdesign.md:330-341`; Infrastructure as Code (IaC): `:135-146`; CI/CD Pipelines: `:379-387`; Model Context Protocol (MCP): `:159-168`
- sdcourse — Automated Scaling and Self-Healing Infrastructure: `.claude/agents/sdcourse.md:115-127` (reused from Chapter 13; here the angle is that Docker/K8s/IaC is exactly the infrastructure that executes auto-scaling/self-healing)

- [ ] **Step 1:** Write `CH22` per the shared skeleton.
- [ ] **Step 2:** Run the per-chapter acceptance check for `n=22`. Expected: `CH22 structural check: PASS`.
- [ ] **Step 3:** `git add scripts/generate_sdcourse_luc.py && git commit -m "feat(sdcourse-luc): write Chapter 22 — Delivery & Infra"`

### Task 37: Chapter 23 — FAANG Capstone: Decision Frameworks Under Interview Pressure

**Sources:**
- Luc — synthesis: no single new source section; this chapter reviews the reframe-then-decide method ("It is not X. It is Y." + explicit decision rules + "when NOT to use it") across the pack's key decision points (Database Selection `lucsystemdesign.md:30-45`, Load Balancing `:46-59`, CAP Theorem `:317-329`, API Architecture `:85-97`) as an interview-review lens.
- sdcourse — FAANG System Design Interview Preparation: `.claude/agents/sdcourse.md:388-407`

- [ ] **Step 1:** Write `CH23` per the shared skeleton. This chapter is the pack's synthesis capstone — its recall block should ask the reader to apply the reframe-then-decide method to a fresh scenario, not just recall a fact.
- [ ] **Step 2:** Run the per-chapter acceptance check for `n=23`. Expected: `CH23 structural check: PASS`.
- [ ] **Step 3:** `git add scripts/generate_sdcourse_luc.py && git commit -m "feat(sdcourse-luc): write Chapter 23 — FAANG Capstone"`

### Task 38: Assemble & render Phase 4 PDF (final assembly)

**Files:** Modify: `scripts/generate_sdcourse_luc.py`

- [ ] **Step 1:** Extend the cover TOC with Ch 18–23 entries.
- [ ] **Step 2:** Extend `HTML_CONTENT` to add `{CH18}` through `{CH23}` after `{CH17}` — the assembly now includes all 23 chapters.
- [ ] **Step 3: Regenerate and verify**

```bash
python3 scripts/generate_sdcourse_luc.py
```

Expected: `Written: output/sdcourse_luc.html` then `PDF written: output/sdcourse_luc.pdf (` with the largest byte count yet (all 23 chapters).

- [ ] **Step 4: Commit**

```bash
git add scripts/generate_sdcourse_luc.py
git commit -m "feat(sdcourse-luc): assemble Phase 4 (Chapters 18-23) — full 23-chapter PDF complete"
```

### Task 39: Extend workflow with Phase 4 chapters

**Files:** Modify: `.claude/workflows/verify-sdcourse-luc.js`

- [ ] **Step 1:** Append 6 entries (ids 18–23) to `CHAPTERS`.
- [ ] **Step 2:** Append 6 entries (ids 18–23) to `KNOWLEDGE_BY_CHAPTER`, citing Tasks 32–37 source lines.
- [ ] **Step 3:** Verify JS syntax (same command as Task 10 Step 2). Expected: `parses OK`.
- [ ] **Step 4:** Commit:

```bash
git add .claude/workflows/verify-sdcourse-luc.js
git commit -m "feat(sdcourse-luc): sync Phase 4 chapter content into verification workflow"
```

### Task 40: Run Phase 4 verification loop to allPassed + sign-off

Same procedure as Task 11, with `args: { chapterIds: [18,19,20,21,22,23] }`.

- [ ] **Step 1:** Invoke the workflow with `args: { chapterIds: [18,19,20,21,22,23] }`.
- [ ] **Step 2:** Read `results`; for any `pass: false` chapter, read gaps/audit.
- [ ] **Step 3:** Apply fix rounds for every failing chapter (generator + workflow sync + regenerate).
- [ ] **Step 4:** Re-run via `resumeFromRunId`.
- [ ] **Step 5:** Repeat until `allPassed: true`.
- [ ] **Step 6:** Confirm `signoff.allPassed: true`; else one more fix round, regenerate, re-run.

### Task 41: Commit Phase 4

- [ ] **Step 1:** If Task 40 produced fix-round edits, commit:

```bash
git add scripts/generate_sdcourse_luc.py .claude/workflows/verify-sdcourse-luc.js
git commit -m "fix(sdcourse-luc): Phase 4 verification fixes — Chapters 18-23 all >=9.0, signed off"
```

---

## Task 42: Documentation updates & completion

**Files:**
- Modify: `docs/LEARNING_PACK_VERIFICATION_WORKFLOW.md`
- Modify: `CLAUDE.md`

- [ ] **Step 1: Append a new section to `docs/LEARNING_PACK_VERIFICATION_WORKFLOW.md`**, after the existing "Extending to New Phases" section:

```markdown
---

## sdcourse × lucsystemdesign Dual-Lens Pack

A second application of this same verification pattern, extended to **two**
technical examiners per chapter instead of one. See
`docs/superpowers/specs/2026-07-07-sdcourse-luc-dual-lens-pack-design.md` for
the full design.

- **Generator:** `scripts/generate_sdcourse_luc.py` → `output/sdcourse_luc.pdf`
- **Workflow:** `.claude/workflows/verify-sdcourse-luc.js`
- **Content source:** the `lucsystemdesign` and `sdcourse` persona files
  directly (`.claude/agents/{lucsystemdesign,sdcourse}.md`) — no transcripts
  or external capture involved.
- **Gate:** a chapter passes only when Luc-accuracy, Luc-coverage,
  sdcourse-accuracy, and sdcourse-coverage are all ≥9.0.
- **Sign-off:** quad-agent (lucsystemdesign + sdcourse + justin-sung + alex),
  once per phase.
- **Built in 4 phases:** Ch 1–6, Ch 7–12, Ch 13–17, Ch 18–23 — each phase is
  generate → verify to allPassed → sign-off → commit before the next phase
  starts.
```

- [ ] **Step 2: Add a row to the learning-packs table in `CLAUDE.md`** — locate the table under "## Learning packs, verification loop & Google Drive" and add a row:

```markdown
| `scripts/generate_sdcourse_luc.py` | Dual-lens (lucsystemdesign + sdcourse) system-design reference, 23 chapters | `output/sdcourse_luc.pdf` |
```

- [ ] **Step 3: Verify the full pack renders cleanly end-to-end** (final smoke test):

```bash
python3 scripts/generate_sdcourse_luc.py
ls -la output/sdcourse_luc.pdf
```

Expected: `PDF written: output/sdcourse_luc.pdf (` with a byte count, and `ls -la` confirms the file exists.

- [ ] **Step 4: Commit the doc updates**

```bash
git add docs/LEARNING_PACK_VERIFICATION_WORKFLOW.md CLAUDE.md
git commit -m "docs: document the sdcourse x lucsystemdesign dual-lens pack"
```

- [ ] **Step 5 (optional, manual — not automated in this plan): Upload to Google Drive**

```bash
python3 scripts/gdrive_upload.py output/sdcourse_luc.pdf
```

Expected: upload confirmation to the Learning Packs Drive folder (ID `1G0h8cBj9ZXDlXXv97LAj9P0esFwyk5KH`).

---

## Plan Self-Review Notes

- **Spec coverage:** Every spec section maps to a task — Section 3 (Architecture & files) → Tasks 1–2; Section 4 (23 chapters) → Tasks 3–8, 13–18, 23–27, 32–37 (one task per chapter) plus Tasks 9, 19, 28, 38 (assembly); Section 5 (verification loop) → Tasks 2, 11, 21, 30, 40; Section 6 (build phases) → the Phase 1–4 groupings; Section 7 (guardrails) → the Global Constraints section above (no Mermaid, sync invariant, read-only personas, gitignored outputs) and Task 1's CSS omitting the Mermaid script tag; Section 8 (success criteria) → Task 42 Step 3; the "every chapter genuinely dual" revision → the `data-author` grep check in every chapter task.
- **Placeholder scan:** No task says "add appropriate content" without a mechanism — every chapter task cites exact source file:line ranges and the exact structural grep check; the only "fill in your own words" spots are marked `<!-- SOURCE: ... -->` HTML comments in the shared skeleton, which is the correct level of specificity for a content-authoring task (the alternative — pre-writing all 23 chapters' full prose inline in this plan — would duplicate persona-file content at the plan-authoring stage instead of the implementation stage).
- **Type/interface consistency:** `CHAPTERS[].{id,title,content}` and `KNOWLEDGE_BY_CHAPTER[id].{luc,sdcourse}` shapes are defined once in Task 2 and referenced identically in every "extend workflow" task (10, 20, 29, 39). The `agentType` values (`lucsystemdesign`, `sdcourse`, `justin-sung`, `alex`) match the existing agent registry exactly. `args.chapterIds` is the single input contract between every phase-verification task and the workflow script.
