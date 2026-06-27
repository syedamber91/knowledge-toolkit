# Full Workflow Guide — Prompts, Verification, and GitHub

This guide covers the complete cycle for any learning pack: from giving Claude the initial prompt, through the multi-agent verification loop, to pushing a branch and merging to main.

---

## 1. Overview

```
Capture vault content
        ↓
Give Claude the E2E prompt
        ↓
Claude generates scripts/generate_AUTHOR_TOPIC.py + PDF
        ↓
Claude runs verification workflow (Examiner → Justin → Scores)
        ↓
Any chapter < 9.0? → Claude fixes generator, regenerates, reruns
        ↓
allPassed = true → git commit + push branch → open PR → merge main
```

---

## 2. Prerequisites

### Vault content must exist

Substack posts must already be captured in the Obsidian vault before you ask for a learning pack:

```
~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian Vault/Substack/posts/
  vutr/        (225 posts)
  luc/         (47 posts)
  sdc/         (68 posts)
```

To capture a new author use the substack-capturer agent:
```
Capture all posts from vutr.substack.com into the Obsidian vault.
```

### Repo is cloned and on the working branch

```bash
git clone https://github.com/syedamber91/knowledge-toolkit.git
cd knowledge-toolkit
git checkout claude/eager-gates-UqFZF   # or current working branch
pip install -e ".[dev]"
```

---

## 3. Step 1 — Give Claude the E2E Prompt

Paste the template below into Claude Code, filling in the CAPS placeholders.

### Template

```
Create a 5-chapter learning pack PDF on TOPIC from AUTHOR's Obsidian vault posts at:
~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian Vault/Substack/posts/AUTHOR_FOLDER/

Chapter topics:
1. CHAPTER_1_TITLE
2. CHAPTER_2_TITLE
3. CHAPTER_3_TITLE
4. CHAPTER_4_TITLE
5. CHAPTER_5_TITLE

Structure it with the Justin Sung pedagogical framework (same as scripts/generate_learning_pack.py):
- WHY→WHAT→HOW structure per section
- Recall section per chapter (4-5 hard retrieval questions)
- Emotional hooks and concrete failure scenarios
- Cross-chapter connection callouts
- Callout boxes: .box.why, .box.s, .box.n, .box.f, .box.r, .box.teach, .box.gap

Save the generator script as scripts/generate_AUTHOR_TOPIC.py and output to output/AUTHOR_TOPIC.pdf.

Then run the multi-agent verification workflow with AGENT_NAME (.claude/agents/AGENT_NAME.md) as examiner:
- EXAMINER generates exactly 5 questions per chapter (≥2 trade-off, ≥1 WHY, ≥1 term precision)
- Justin Sung (student mode) answers only from the chapter content string — no outside knowledge
- EXAMINER scores accuracy (0-10) and coverage (0-10) per question, identifies gaps

For any chapter below 9.0 on either dimension: fix the generator script, regenerate the PDF,
update the CHAPTERS[n].content strings in the workflow to match, then rerun.

Iterate until all 5 chapters achieve ≥9.0 accuracy and ≥9.0 coverage. Report final scores.
```

### Ready-to-use examples

**vutr — Apache Spark Internals**
```
Create a 5-chapter learning pack PDF on Apache Spark internals from vutr's Obsidian vault posts at:
~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian Vault/Substack/posts/vutr/

Chapter topics:
1. RDDs, DAGs, and the Catalyst Optimizer
2. Spark Memory Model and OOM Mechanics
3. Shuffle, Joins (SMJ / SHJ / Broadcast), and Skew
4. PySpark, Tungsten, and Photon
5. Spark Structured Streaming and AQE

Structure it with the Justin Sung pedagogical framework (same as scripts/generate_learning_pack.py).
Save as scripts/generate_vutr_spark.py → output/vutr_spark.pdf.

Examiner: vutr (.claude/agents/vutr.md)
Run the verification workflow. Iterate until all chapters ≥ 9.0 accuracy and ≥ 9.0 coverage.
```

**lucsystemdesign — System Design Decision Frameworks**
```
Create a 5-chapter learning pack PDF on system design decision frameworks from lucsystemdesign's vault posts at:
~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian Vault/Substack/posts/luc/

Chapter topics:
1. CAP Theorem and Consistency Models (correcting the slogan)
2. Database Selection — Matching the Database to the Question
3. Load Balancing Algorithms and Trade-offs
4. Authentication and Security (OAuth 2.0, JWT, SSO, TLS)
5. Microservices, Event-Driven Architecture, and When NOT to Decompose

Save as scripts/generate_luc_sysdesign.py → output/luc_sysdesign.pdf.
Examiner: lucsystemdesign (.claude/agents/lucsystemdesign.md)
Run verification. Iterate until all chapters ≥ 9.0 / 9.0.
```

**sdcourse — Distributed Log Processing System**
```
Create a 5-chapter learning pack PDF on building a distributed log processing system from sdcourse's vault posts at:
~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian Vault/Substack/posts/sdc/

Chapter topics:
1. Leader Election and Raft Consensus
2. Bloom Filters for Log Deduplication
3. Dead Letter Queues and Poison Message Handling
4. Kafka for High-Throughput Log Ingestion
5. Multi-Region Replication and TLS

Save as scripts/generate_sdc_logprocessing.py → output/sdc_logprocessing.pdf.
Examiner: sdcourse (.claude/agents/sdcourse.md)
Run verification. Iterate until all chapters ≥ 9.0 / 9.0.
```

---

## 4. Step 2 — What Claude Does (The E2E Run)

You don't need to do anything during this phase. Claude will:

1. **Read vault posts** — selects 15-25 most substantive posts per chapter topic
2. **Generate `scripts/generate_AUTHOR_TOPIC.py`** — 5 chapter HTML strings (CH1–CH5) using the same CSS/callout system as `scripts/generate_learning_pack.py`
3. **Run the generator and produce the PDF**:
   ```bash
   python3 scripts/generate_AUTHOR_TOPIC.py
   "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
       --headless --print-to-pdf=output/AUTHOR_TOPIC.pdf \
       --print-to-pdf-no-header output/AUTHOR_TOPIC.html
   ```
4. **Launch the verification Workflow** — a 3-stage pipeline over all 5 chapters:
   - Stage 1: Examiner generates 5 questions per chapter
   - Stage 2: Justin Sung (student) answers from chapter content only
   - Stage 3: Examiner scores accuracy + coverage, lists gaps
5. **Iterate** — for each chapter below 9.0, Claude fixes the generator script, regenerates, updates `CHAPTERS[n].content` in the workflow, and reruns (cached chapters skip instantly)
6. **Reports final scores** when `allPassed = true`

### Critical invariant during iteration

`CHAPTERS[n].content` in the workflow script ≠ the PDF. They are separate strings.  
After every generator script edit, the chapter text must also be updated in the workflow's `CHAPTERS[n].content`. If this is missed, the student reads old content and scores don't improve (this caused passes 4–7 to stall on the Ben Dicken pack).

---

## 5. Step 3 — Interpreting Verification Output

After each pass Claude reports per-chapter scores. Use these to judge readiness:

| Score | Meaning |
|-------|---------|
| Accuracy ≥ 9.0 | Chapter content is technically correct and uses precise terminology |
| Accuracy < 9.0 | PDF contains wrong explanations — fix those specific claims |
| Coverage ≥ 9.0 | PDF teaches what the examiner considers important |
| Coverage < 9.0 | PDF is missing concepts the examiner emphasises — add them |

**Pass threshold**: all 5 chapters must hit ≥ 9.0 on BOTH dimensions.

**Typical pass count**: 3–8 passes. Earlier passes usually fix coverage; later passes fix accuracy precision.

---

## 6. Step 4 — Commit the Results

Once `allPassed = true`, commit the generator script and persona files (output/ is gitignored):

```bash
git add scripts/generate_AUTHOR_TOPIC.py
git add .claude/agents/AGENT_NAME.md          # if persona was updated
git add .claude/skills/AGENT_NAME-persona/SKILL.md  # if persona was updated
git add docs/AUTHOR_TOPIC_VERIFICATION_WORKFLOW.md   # if created

git commit -m "feat(AUTHOR): TOPIC learning pack — Xchapters, all ≥9.0/9.0 (passN)"
```

Commit message convention:
```
feat(vutr): Spark internals learning pack — 5 chapters, all ≥9.0/9.0 (pass 4)
feat(luc): system design learning pack — 5 chapters, all ≥9.0/9.0 (pass 3)
feat(sdc): distributed log processing learning pack — 5 chapters, all ≥9.0/9.0 (pass 5)
```

---

## 7. Step 5 — Push to GitHub Branch

```bash
# Push the current working branch (claude/eager-gates-UqFZF or whatever you're on)
git push origin HEAD

# If the branch doesn't exist on remote yet:
git push -u origin HEAD
```

Verify it landed:
```bash
git log origin/claude/eager-gates-UqFZF --oneline -5
```

---

## 8. Step 6 — Open a Pull Request

Use the `gh` CLI:

```bash
gh pr create \
  --title "feat: AUTHOR TOPIC learning pack (all chapters ≥9.0/9.0)" \
  --body "$(cat <<'EOF'
## Summary
- 5-chapter learning pack PDF for AUTHOR on TOPIC
- Verified by multi-agent loop: EXAMINER examiner + Justin Sung student
- All 5 chapters: accuracy ≥ 9.0, coverage ≥ 9.0 (achieved at pass N)

## What's included
- `scripts/generate_AUTHOR_TOPIC.py` — content generator (source of truth)
- `.claude/agents/AGENT_NAME.md` — persona agent (if updated)
- `.claude/skills/AGENT_NAME-persona/SKILL.md` — persona skill (if updated)

## What's gitignored (not in this PR)
- `output/AUTHOR_TOPIC.pdf` — regenerate locally with `python3 scripts/generate_AUTHOR_TOPIC.py`
- `output/AUTHOR_TOPIC.html` — intermediate HTML

## Verification scores (pass N)
| Chapter | Accuracy | Coverage |
|---------|----------|----------|
| Ch1     | X.X      | X.X      |
| Ch2     | X.X      | X.X      |
| Ch3     | X.X      | X.X      |
| Ch4     | X.X      | X.X      |
| Ch5     | X.X      | X.X      |

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)" \
  --base main
```

Or ask Claude to open the PR:
```
Open a PR from claude/eager-gates-UqFZF to main titled "feat: vutr Spark learning pack (all chapters ≥9.0/9.0)"
with a body that lists the 5 chapters and their final verification scores.
```

---

## 9. Step 7 — Merge to Main

After PR review (or self-approval):

**Via GitHub UI**: click "Merge pull request" → "Confirm merge"

**Via gh CLI**:
```bash
gh pr merge --merge    # regular merge commit
# or
gh pr merge --squash   # squash all commits into one clean commit on main
```

After merging:
```bash
git checkout main
git pull origin main
```

---

## 10. What Gets Committed vs Gitignored

| Path | Status | Notes |
|------|--------|-------|
| `scripts/generate_*.py` | ✅ committed | Source of truth for chapter content |
| `.claude/agents/*.md` | ✅ committed | Persona definitions |
| `.claude/skills/*/SKILL.md` | ✅ committed | Skill triggers |
| `docs/*.md` | ✅ committed | This guide, verification history |
| `output/*.pdf` | ❌ gitignored | Regenerate from script |
| `output/*.html` | ❌ gitignored | Intermediate |
| `.auth/` | ❌ gitignored | Session cookies — never commit |
| `data/` | ❌ gitignored | Raw crawl cache |

---

## 11. Re-running on a Fresh Machine

Anyone who clones the repo can regenerate the PDF from the committed script:

```bash
git clone https://github.com/syedamber91/knowledge-toolkit.git
cd knowledge-toolkit
pip install -e ".[dev]"
python3 scripts/generate_vutr_spark.py
# Opens output/vutr_spark.html → convert via headless Chrome
```

No Obsidian vault or credentials needed to regenerate — all chapter content is embedded in the generator script.

---

## 12. Quick Reference — Prompt Patterns

| What you want | Prompt to give Claude |
|--------------|----------------------|
| New learning pack from scratch | Use the template in Section 3 |
| Rerun verification only (PDF already exists) | `Rerun the verification workflow for scripts/generate_AUTHOR_TOPIC.py using AGENT_NAME as examiner. Iterate until all chapters ≥9.0/9.0.` |
| Fix one chapter | `Chapter N scored X.X on coverage. The gaps were: [paste gaps]. Fix generate_AUTHOR_TOPIC.py for that chapter, regenerate, update CHAPTERS[N].content, and rerun verification.` |
| Push and open PR | `Push the current branch to origin and open a PR to main titled "feat: DESCRIPTION"` |
| Check PR status | `What's the status of the open PR on this repo?` |
| Merge the PR | `Merge the open PR to main using a squash merge.` |
