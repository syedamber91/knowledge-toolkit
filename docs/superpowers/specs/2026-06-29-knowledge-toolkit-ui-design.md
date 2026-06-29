# Knowledge Toolkit UI — Design Spec
**Date:** 2026-06-29  
**Status:** Approved for implementation planning

---

## 1. Goal

Replace the current manual workflow (copy-pasting prompts into the Claude Agentic Chat window) with a web-based UI that automates the full end-to-end learning pack pipeline — from vault content ingestion through multi-agent verification to Google Drive delivery and GitHub PR.

---

## 2. Scope

All five pipeline stages are in scope as connected screens:

1. Content ingestion (Substack / YouTube / Web / SOIC → Obsidian vault)
2. Learning pack generation (author + topic + chapters → PDF via headless Chrome)
3. Verification loop (multi-pass multi-agent Q&A until all chapters ≥ 9.0)
4. Tri-agent final sign-off gate (examiner(s) + Justin + Alex)
5. Delivery (Google Drive upload → git commit → push → PR)

---

## 3. Platform

- **Web app**, runs locally first, deployable to VPS later
- Multi-tenant architecture from the start (accounts/subscriptions for future monetization)
- No native desktop shell — runs in the browser

---

## 4. Visual Design Language

- **AI-native + developer-tool aesthetic, light mode**
- Dense information display; progress logs always visible
- Flat surfaces, no gradients or shadows
- Monospace font for log streams and CLI command previews
- Color system: blue (#185FA5) for primary actions and vutr/examiner accent, green (#3B6D11) for pass/done states, amber (#854F0B / #EF9F27) for warnings and Alex, red (#A32D2D) for failures

---

## 5. Navigation Model

**Pipeline / timeline view** — one persistent left sidebar showing all 5 stages as a vertical list; the main area shows details for the active stage. No full-page navigation transitions; the sidebar always visible.

---

## 6. Screens

### 6.1 Run List (Dashboard / Entry Point)

The home screen. Shows all past and active runs.

**Top bar:** App name ("Knowledge Toolkit"), "New run" primary button (opens Pack Builder).

**Stats row (4 cards):** Total runs, Passed this week, Avg passes to ship, Tokens this month (with estimated cost).

**Run list table columns:**
- Status dot (animated pulse = running, green = done, red = stalled)
- Pack name (author + topic)
- Stage pill (Verification / Sign-off / Generating / Done / Stalled)
- Score bars (acc / cov / alex as 3 thin horizontal bars, green = pass, red = fail)
- Pass count
- Started timestamp

Clicking any row opens the Run Detail screen.

**Filter pills:** All / Running / Done / Failed.

---

### 6.2 Pack Builder (New Run Form)

Two-column layout. Opens from "New run" button.

**Left column — Source + Topic + Chapters:**

**Authors (multi-select chips):** Each author chip shows handle and post count. Multiple authors can be selected simultaneously; selecting more than one activates "joint mode" for both examiners and vault merging.

**Topic browser (replaces plain text input):**

A scrollable list of topics derived from vault post density. Topics exist in three states:

| State | Visual | Behaviour |
|---|---|---|
| **Suggested** | Plain card, muted "Suggested" badge, post count shown | Selectable — click to pick |
| **Shipped** | Green border/background, "Shipped ✓" badge | Shows PDF name, pass count, ship date, "vault unchanged since" confirmation. Clicking opens the existing run. |
| **New content** | Amber border/background, "New content" badge with refresh icon | Shows how many new posts per author landed in vault since the pack shipped. Inline warning: "re-extraction recommended". Right panel surfaces a digest of all flagged topics. |

A search input filters the list. Filter pills: All / Suggested / Completed / Needs update.

When a topic is selected, a chapter field panel appears below the topic list showing 5 editable chapter title inputs.

**Examiners (multi-select cards):** vutr / lucsystemdesign / sdcourse / ben-dicken. Selecting more than one shows a "Joint mode — 5 questions each per chapter, asked in parallel" pill. Justin Sung (pedagogy) and Alex Chen (clarity) are always included automatically and not selectable.

**Right column — Run Preview + Controls:**

- Vault status indicator (posts found, matched to topic)
- Preview card: authors, topic, post count matched, chapters, examiners, questions per chapter, scoring model, pass threshold, output PDF path, Drive folder, git commit trigger
- Pipeline steps checklist (5 steps, all pre-confirmed with check icons)
- "Start pipeline" primary button
- "Save as draft" secondary button
- "Topics needing attention" digest (amber warning cards for any flagged re-extraction topics, shown regardless of which topic is selected)

---

### 6.3 Run Detail (Pipeline Console)

Split-screen layout. This is the core working view.

**Left sidebar (210px, always visible):**

- Run header: title (author — topic), start time + pass number, author tag pills (e.g. `vutr` `luc` in their brand colours), running badge with animated dot
- Stage list (5 items with connectors between):
  - Done stages: green filled circle with checkmark icon
  - Active stage: animated spinning progress ring (SVG arc) around an inner circle with the stage icon; the left edge of the row has a 2px blue accent line
  - Pending stages: grey outlined circle with the stage icon

Stages: Content ingestion → Pack generation → Verification loop → Sign-off gate → Delivery.

Each stage shows a name and a one-line sub-label (e.g. "Pass 3 · Ch 1–5 scoring").

**Main area (remainder):**

**Top bar:** Stage label + pass number on the left; "Joint · N agents active" badge on the right (only shown in joint examiner mode).

**Agent strip (horizontal scroll):** One card per active agent. Cards have a coloured left border (blue = vutr, teal = luc/justin, amber = alex, grey = queued). Each card shows: agent name, current task description, status badge (running / queued), token count. In joint examiner mode, the two examiners share a single card with dual colour dots and a combined token count.

**Score grid (5 cells, one per chapter):**

Each cell contains:
- Chapter label (Ch 1 … Ch 5)
- Dual colour dots (one per examiner) — in single-examiner mode, one dot
- Joint acc / cov score as the primary number (e.g. "9.2 / 9.3")
- "acc / cov" sub-label
- Horizontal divider
- Alex clarity score with amber "alex" tag
- Pass/fail threshold result ("all ✓" in green or "acc below ✗" in red)
- "scoring…" or "queued" placeholder while awaiting results

**Gaps section (always visible, below score grid):**

List of gaps identified so far in the current pass. Each gap item shows:
- Source tag (e.g. "Ch 2 · joint" in blue-green gradient, or "Ch 3 · alex" in amber)
- Gap description (one line)

**Live log (always visible, below gaps):**

Monospace stream. Each line: timestamp · agent name (colour-coded) · message. Log messages include: pass start, question generation events (per examiner), Justin answering, Alex auditing, joint score emission, gap flagging, fix round triggers.

---

### 6.4 Sign-off Gate + Delivery

Two-column layout. Reached automatically when all chapters pass ≥ 9.0.

**Left column:**

- "All chapters passed ≥ 9.0" green banner with pass number
- Final score grid (same 5-cell layout as run detail, all values filled in)
- Sign-off cards (one per required approver — 3 in single-examiner mode, N+2 in joint mode):
  - In single-examiner runs: 3 cards (examiner + Justin + Alex)
  - In joint-examiner runs: N+2 cards (all examiners + Justin + Alex)
  - Each card: agent avatar initials, name, role description, approval status badge (Approved green / Rejected red / Running amber)
  - Approved cards show a checklist of criteria met
  - Rejected cards show what failed (triggers one fix round automatically)
  - Pending card shows "Auditing final PDF…" placeholder

**Right column:**

- Delivery checklist (5 steps, each with status):
  1. PDF generated (always done by this point)
  2. Google Drive upload (waiting / uploading / done)
  3. Git commit (shows commit message preview in monospace)
  4. Push branch (shows `git push origin HEAD`)
  5. Open pull request (shows `gh pr create` preview)
- Explanatory note: "Delivery runs automatically once all agents approve. If any reject, one fix round runs before delivery."
- "Ship" primary button — disabled (greyed) until all approvals in; becomes active and triggers delivery automatically
- "View [agent] audit in progress" secondary button

---

## 7. Multi-Author / Joint Examiner Mode

When more than one author is selected in the Pack Builder:

- Vault posts from all selected authors are merged and deduplicated before chapter generation
- Output PDF filename uses all author handles (e.g. `vutr_luc_kafka.pdf`)
- The "Examiners" section allows selecting multiple examiners

When more than one examiner is selected:

- Each examiner generates their own set of questions (5 each) per chapter — in parallel
- Justin Sung answers all questions from the combined pool in a single pass
- Both examiners score their respective questions simultaneously
- A single joint score is emitted per chapter (consensus, not average)
- The score grid shows dual colour dots + one acc/cov value
- The agent strip shows a single "joint" card with dual dots and combined token count
- Gap tags are labelled "joint" when the gap came from combined examiner judgment
- The sign-off gate includes all selected examiners as separate approvers

---

## 8. Topic Re-extraction Logic

The UI tracks, per topic:
- The date the pack was shipped
- The post count in the vault at ship time (per author)
- The current post count in the vault (checked on dashboard load and pack builder open)

If current count > ship-time count for any author on a shipped topic:
- The topic card shows the amber "New content" badge
- The delta (new posts per author) is shown inline on the card
- The right panel of the pack builder surfaces a "Topics needing attention" digest
- Starting a new run on a flagged topic is a fresh full run (all posts, not just new ones)
- Future enhancement: offer a "update existing pack" path that re-runs verification on chapters affected by new posts only (out of scope for v1)

---

## 9. Data Model (UI layer)

```
Run {
  id, title (author + topic), authors[], examiners[],
  status (running | done | stalled),
  currentStage, currentPass,
  pdf { path, size, generatedAt },
  chapters[5] {
    title,
    passes[n] { accScore, covScore, alexScore, jointScore, gaps[] }
  },
  signOff { examiner(s)[], justin, alex — each: status, criteria[], verdict },
  delivery { drive, gitCommit, push, pr — each: status, detail }
}

Topic {
  name, authors[], postCount { byAuthor, total },
  status (suggested | shipped | needsUpdate),
  pack? { runId, pdfPath, shippedAt, postCountAtShip }
}
```

---

## 10. Out of Scope (v1)

- Partial re-extraction (only chapters affected by new vault posts)
- User accounts / auth (single-user local first)
- Mobile layout
- Dark mode
- Content ingestion UI (Substack / YouTube / SOIC capture is still CLI-driven for v1; the UI monitors the vault but does not trigger captures)

---

## 11. Open Questions

None — all design decisions resolved in brainstorming session.
