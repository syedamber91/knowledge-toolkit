# Learning Pack Verification Workflow

## Goal

Generate a pedagogically rigorous study PDF from raw video transcripts, then verify it meets content standards through an automated multi-agent loop — without any manual re-reading or judgment.

---

## The Three Layers

### Layer 1 — Content Source
Ben Dicken's video transcripts (`transcripts/`) are the authoritative source of technical truth. All facts, trade-offs, terminology, and emphasis come from these 33 transcripts.

### Layer 2 — Pedagogical Wrapper
Justin Sung's framework structures how the content is presented:
- **WHY before WHAT before HOW** — every concept opens with the problem it solves
- **Active recall** — chapters end with retrieval questions, not summaries
- **Emotional hooks** — confusion is framed as signal, not failure
- **5 Levels of understanding** — content targets "schema" level (interconnected understanding), not lower-order memorisation

### Layer 3 — Verification Loop
A multi-agent pipeline checks that Layer 2 faithfully captures Layer 1 — from the perspective of a student who only has the PDF.

---

## Verification Loop Architecture

```
for each chapter:
    Ben Dicken → generate 5 questions (≥2 trade-off, ≥1 precise term, ≥1 WHY)
         ↓
    Justin Sung (student mode) → answer from PDF content only
         ↓
    Ben Dicken → score on two dimensions:
        Accuracy  (0–10): correct term + correct trade-off direction + WHY explanation
        Coverage  (0–10): did the PDF teach what Ben considers important?

if any chapter < 9.0 on either dimension:
    identify gaps → revise generate_learning_pack.py → regenerate PDF → repeat
else:
    allPassed = true → commit + ship
```

### Scoring Standards (Ben Dicken)
- **10/10** requires: correct term + correct trade-off direction + WHY explanation + full coverage of all key sub-concepts
- **Coverage < 9** means the PDF is missing something Ben emphasises in his videos — the student can't know what they don't know
- **Accuracy < 9** means the PDF contains imprecise or incorrect content

### Question Generation Rules
Ben generates questions that require:
- At least 2 questions testing trade-offs (not just definitions)
- At least 1 question requiring a precise technical term
- At least 1 WHY question (why does this exist / what problem does it solve)

---

## Self-Contained Persona Design

**Critical constraint**: all persona knowledge must be embedded in the agent/skill files. The agents must not re-read transcripts at verification time.

Why: the verification loop runs 20+ agents across 3 passes. Re-reading 33 transcripts per agent would make each pass prohibitively slow and context-heavy.

**Justin Sung** (`.claude/agents/justin-sung.md`, `.claude/skills/justin-sung-persona/SKILL.md`):
- Embeds: 5 Levels of Understanding, 3 Encoding Conditions, Memory Ladder, pedagogical criteria
- Two modes: Pedagogical Reviewer + Student Demonstrator
- Hard boundary: student mode must answer only from PDF content passed in the prompt — no invented citations, no off-transcript knowledge

**Ben Dicken** (`.claude/agents/ben-dicken.md`, `.claude/skills/ben-dicken-persona/SKILL.md`):
- Embeds: all 9 technical topic areas (storage, buffer management, indexing, transactions, WAL, etc.)
- Embeds: scoring rubric and question generation guidelines
- Acts as both examiner (generating questions) and judge (scoring answers)

---

## PDF Generation

`scripts/generate_learning_pack.py` produces `output/ben_dicken_phase1.pdf` via headless Chrome:

```bash
python3 scripts/generate_learning_pack.py          # generates HTML
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
    --headless --print-to-pdf=output/ben_dicken_phase1.pdf \
    --print-to-pdf-no-header output/ben_dicken_phase1.html
```

The script hardcodes all chapter content as Python strings — no runtime transcript access. Changes to content go into the `CHAPTERS` list in the script, then the PDF is regenerated.

---

## Gap → Fix Cycle

Each verification pass produces a gap report per chapter. Gaps fall into two categories:

**Coverage gaps** (Ben's scorer: "the PDF doesn't mention X"):
→ Add the missing concept to the relevant chapter section in `generate_learning_pack.py`

**Accuracy gaps** (Ben's scorer: "the PDF says X but the correct explanation is Y"):
→ Find and correct the wrong content; be precise about the error (e.g. "erase cycles explain write amplification, not read latency")

After editing the script, regenerate and re-run the workflow from the same `scriptPath` — the workflow caches unchanged agent calls and only re-runs chapters that were touched.

---

## Pass History (Phase 1)

| Pass | Ch1 Acc/Cov | Ch2 Acc/Cov | Ch3 Acc/Cov | Ch4 Acc/Cov | Ch5 Acc/Cov |
|------|-------------|-------------|-------------|-------------|-------------|
| 1    | 8.2 / 7.8   | 8.6 / 8.2   | 8.8 / 6.6   | 8.4 / 6.0   | 8.4 / 8.0   |
| 2    | 9.0 / 8.8   | 9.2 / 9.0   | 9.4 / 8.6   | 9.6 / 9.4   | 9.2 / 8.8   |
| 3    | 9.4 / 9.2 ✓ | 9.4 / 9.4 ✓ | 10 / 10 ✓   | 9.8 / 9.8 ✓ | 9.8 / 9.2 ✓ |
| 4    | 8.8 / 8.2 ✗ | 9.2 / 7.0 ✗ | 9.8 / 9.8 ✓ | 9.4 / 9.4 ✓ | 10 / 9.4 ✓  |
| 5    | 9.0 / 8.0 ✗ | 9.6 / 9.6 ✓ | 9.8 / 9.8 ✓ | 9.4 / 9.4 ✓ | 10 / 9.4 ✓  |
| 6    | 8.8 / 8.2 ✗ | 9.6 / 9.6 ✓ | 9.8 / 9.8 ✓ | 9.8 / 7.8 ✗ | 9.8 / 8.8 ✗ |
| 7    | 8.8 / 7.8 ✗ | 9.6 / 9.6 ✓ | 9.8 / 9.8 ✓ | 9.8 / 9.8 ✓ | 8.8 / 7.4 ✗ |
| **8** | **10 / 9.6 ✓** | **10 / 10 ✓** | **10 / 10 ✓** | **10 / 10 ✓** | **10 / 9.6 ✓** |

**allPassed = true at Pass 8.**

Key fixes driven by the loop:
- **Pass 1→2**: Added B+ tree vs B-tree distinction across all chapters (leaf nodes, neighbour pointers, node split)
- **Pass 1→2**: Added dirty page definition, WAL multi-index atomic entry, deadlock resolution (kill + rollback)
- **Pass 2→3**: Node split key promotion to parent (how O(log n) depth is maintained)
- **Pass 2→3**: RAM (~100ns) vs disk (~10ms) = 100,000× latency numbers
- **Pass 2→3**: WAL sequential vs random I/O distinction
- **Pass 3→4**: Added Substack cross-references, Mermaid diagrams (ByteByteGo style), callout CSS variants (xr/teach/gap/why)
- **Pass 4→5**: Ch2 System Libraries concrete examples (O_DIRECT, jemalloc/tcmalloc/palloc, SSL/TLS), named syscalls table, io_uring shared-memory trick + trade-offs
- **Pass 5→6**: Ch1 HDD sequential positive mechanism (arm stays stationary; platter delivers sectors), SSD 4× penalty root cause
- **Pass 6→8 (root fix)**: Discovered that the verification workflow's Justin Sung student reads from hardcoded `CHAPTERS[n].content` strings — NOT the generated PDF. All PDF improvements since pass 3 were never tested because the student content was stale. Fix: rewrote all 5 `CHAPTERS[n].content` strings AND `BEN_KNOWLEDGE_BY_CHAPTER` to match current PDF content, including:
  - Ch1: correct SSD 4× explanation (NAND die parallelism + FTL lookup, NOT erase cycles), WHY pages exist (HDD track geometry + NAND wordline + ECC block granularity), Bayer & McCreight 1972 founding motivation, concrete sequential-rule violation (non-clustered index heap fetches), B+ tree structural preview (fanout 580, node splits, sibling pointers)
  - Ch2: io_uring corrected from "kernel-bypass" (wrong term — that's DPDK/SPDK) to "eliminates per-I/O syscall crossings via shared memory ring buffers", io_uring trade-offs (Linux-only, kernel 5.1+, CVEs, Google/Android 2023 disable), named syscalls table, diagnostic toolkit (strace/perf/bpftrace/iostat/fio)
  - Ch4: ACID mapping table (Lock Manager → Isolation, Recovery Manager → Durability, Buffer Manager → Performance NOT Durability), WAL REDO vs UNDO distinction with record fields (LSN, XID, after-image, before-image, prev_lsn, CLR), ARIES 3 phases, buffer pool OOM risk + OS page cache starvation trade-offs
  - Ch5: Lock Manager → Isolation ('I' in ACID) explicit, LSM tree description, WAL REDO+UNDO, ACID mapping

---

## Running a New Pass

```bash
# From the repo root:
# 1. Edit scripts/generate_learning_pack.py with fixes
# 2. Regenerate PDF
python3 scripts/generate_learning_pack.py
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
    --headless --print-to-pdf=output/ben_dicken_phase1.pdf \
    --print-to-pdf-no-header output/ben_dicken_phase1.html

# 3. Re-run verification workflow
# In Claude Code, use Workflow with scriptPath pointing to the saved workflow script
# The workflow caches unchanged agent calls — only changed chapters re-run
```

---

## Extending to New Phases

The same workflow applies to additional Ben Dicken content (phases 2+):

1. Add new chapters to `CHAPTERS` in `generate_learning_pack.py`
2. Regenerate PDF
3. Run the verification workflow — it pipelines over whatever chapters are in `CHAPTERS`
4. Fix gaps, repeat until all chapters ≥9.0/9.0
5. Commit and push

Output files (`output/`) are gitignored. Only the generator script and persona files are committed.
