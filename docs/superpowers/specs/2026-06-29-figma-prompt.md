# Figma AI Design Prompt — Knowledge Toolkit UI

Paste the block below directly into Figma AI (Make Designs). It is self-contained.

---

## PROMPT

Design a web application called **Knowledge Toolkit** — an AI-native learning pack pipeline dashboard. The app automates a multi-agent workflow that captures content from Obsidian vaults, generates PDF study guides, and runs automated quality verification loops using AI examiner agents.

---

### Visual Language

**Style:** AI-native + developer-tool, light mode. Clean, flat, information-dense. Feels like a cross between Vercel's dashboard and a CI/CD run console.

**Colors:**
- Primary action / blue accent: `#185FA5`
- Light blue surface: `#E6F1FB`
- Blue border: `#B5D4F4`
- Pass / success green: `#3B6D11`
- Light green surface: `#EAF3DE`
- Green border: `#C0DD97`
- Warning / Alex amber: `#EF9F27` (dark text: `#854F0B`)
- Light amber surface: `#FAEEDA`
- Amber border: `#FAC775`
- Failure red: `#A32D2D`
- Light red surface: `#FCEBEB`
- Luc / teal accent: `#0F6E56`
- Light teal surface: `#E1F5EE`
- Page background: `#FFFFFF`
- Secondary surface: `#F5F5F3`
- Border default: `rgba(0,0,0,0.15)`
- Text primary: `#1A1A18`
- Text secondary: `#5F5E5A`
- Text tertiary: `#888780`

**Typography:**
- Font: Inter (or system sans-serif)
- App headings: 13px / 500
- Section labels: 10px / 500 / uppercase / letter-spacing 0.05em
- Body / labels: 12px / 400
- Hints: 11px / 400 / tertiary color
- Log stream: 11px / monospace (JetBrains Mono or Fira Code)

**Components:**
- Borders: 0.5px solid
- Corner radius: 8px (cards), 12px (large cards), 20px (pills/chips)
- No drop shadows, no gradients
- Animated states (show as separate frames): spinning ring for active stage, pulsing dot for running status, blinking cursor in log stream

---

### Screen 1 — Run List (Home / Dashboard)

**Layout:** Full-width browser window. Top bar + stats row + filter bar + table.

**Top bar (48px tall, light secondary background):**
- Left: app name "Knowledge Toolkit" (13px/500) + sub-label "Learning pack pipeline" (11px/tertiary)
- Right: "＋ New run" button (primary blue fill, white text, 12px/500, 8px radius, 7px 14px padding)

**Stats row (4 metric cards in a horizontal grid, 14px padding around, 12px gap):**
Each card: secondary background, 8px radius, 10px 14px padding. Muted 10px uppercase label above, 22px/500 number below, 10px tertiary sub-note.
- Card 1: "Total runs" / 14 / "since Jun 1"
- Card 2: "Passed this week" / 3 / "all ≥ 9.0 / 9.0"
- Card 3: "Avg passes to ship" / 4.2 / "across all packs"
- Card 4: "Tokens this month" / 2.1M / "est. $6.30"

**Filter bar:** Row of pills — "All" (active, blue fill), "Running", "Done", "Failed". 20px radius, 11px text.

**Table (column headers row + 5 data rows):**
Column headers: 10px uppercase tertiary. 6 columns: [status dot] [Pack] [Stage] [Scores] [Passes] [Started]

Row 1 — Running:
- Animated pulse dot (blue)
- "vutr — Spark Internals" / "5 chapters · examiner: vutr · 3 agents active" (11px tertiary)
- Stage pill: blue background "↻ Verification"
- 3 score bars (acc/cov/alex) — thin 4px height, green fill at 70% / 85% / 60%
- "Pass 3"
- "09:14"

Row 2 — Done:
- Solid green dot
- "vutr — Spark Internals" / "5 chapters · all ≥ 9.0 · shipped to Drive"
- Stage pill: green "✓ Done"
- All 3 bars green at ~95%
- "Pass 5" / "Jun 27"

Row 3 — Sign-off:
- Animated pulse dot (amber)
- "luc — System Design" / "all ≥ 9.0 · awaiting tri-agent sign-off"
- Stage pill: amber "⌛ Sign-off"
- All 3 bars green at ~95%
- "Pass 4" / "Jun 28"

Row 4 — Generating:
- Animated pulse dot (blue)
- "sdc — Distributed Log Processing" / "generating PDF"
- Stage pill: grey "⊡ Generating"
- All 3 bars empty (grey)
- "—" / "Today"

Row 5 — Stalled:
- Solid red dot
- "ben-dicken — Database Internals" / "Ch 3 acc 7.1 · stalled after 8 passes"
- Stage pill: red "✕ Stalled"
- acc bar red at 71%, cov bar green at 90%, alex bar green at 88%
- "Pass 8" / "Jun 25"

---

### Screen 2 — Pack Builder (New Run Form)

**Layout:** Full-width, two-column (50/50), vertical divider between columns.

**Top bar (same height as screen 1):** "← Runs" back link (secondary text, 12px) · separator · "New learning pack" title (13px/500)

**Left column — Source + Topic + Chapters:**

Section label "Source" above:

**Authors row:** Horizontal chips, multi-select. Two selected (blue chip: "● vutr · 225 posts", teal chip: "● luc · 47 posts"), two unselected ("＋ sdc", "＋ ben-dicken"). Selected chips have colored border + light fill matching their accent color.

Section label "Topic" above:

**Search input** (full width, 12px, placeholder "Search topics from vault…")

**Filter pills:** All (active/blue) / Suggested / Completed / Needs update

**Topic list (scrollable, 5 visible cards with 6px gap):**

Card A — Amber "New content" (amber border, very light amber background):
- Header row: "Apache Kafka" (12px/500) | right-aligned amber badge "↻ New content"
- Meta row: blue dot "vutr" · teal dot "luc" · "272 posts" · "Pack shipped Jun 20"
- Inline warning block (amber background, 10px): ⚠ "14 new posts added to vault since pack was shipped (vutr: 11 · luc: 3) — re-extraction recommended"

Card B — Amber "New content":
- "CAP Theorem and Consistency Models" | amber badge "↻ New content"
- Meta: teal dot "luc" · "47 posts" · "Pack shipped Jun 15"
- Warning: ⚠ "8 new posts added (luc: 8) — re-extraction recommended"

Card C — Green "Shipped" (green border, very light green background):
- "Apache Spark Internals" | green badge "✓ Shipped"
- Meta: blue dot "vutr" · "225 posts"
- Green detail row: "✓ vutr_spark.pdf · Pass 5 · all ≥ 9.0 · Jun 27 · vault unchanged since"

Card D — Green "Shipped":
- "System Design Decision Frameworks" | green badge "✓ Shipped"
- Meta: teal dot "luc" · "47 posts"
- Green detail: "✓ luc_sysdesign.pdf · Pass 3 · Jun 25 · vault unchanged"

Card E — Blue "Selected" (blue border, light blue background):
- "Iceberg, Delta Lake and Hudi — Open Table Formats" | blue badge "✓ Selected"
- Meta: blue dot "vutr" · "31 posts matched" · "💡 Suggested"

Below the list, a blue-bordered inset panel "Chapters — Iceberg, Delta Lake and Hudi" with 5 numbered text inputs pre-filled with chapter titles.

**Examiners section:** 2×2 grid of examiner cards. vutr (blue selected border/fill) and lucsystemdesign (amber selected border/fill) are selected. sdcourse and ben-dicken unselected. Below: amber pill "👥 Joint mode — 5 questions each per chapter, asked in parallel"

**Right column — Run Preview + Controls:**

Legend block: 4 items in a 2×2 grid showing the 4 topic card states with their color swatches and labels.

Section label "Run preview":

Vault status bar: green dot · "Both vaults ready" · "· 272 posts · 31 matched to topic"

Preview card (secondary background, all rows): Authors / Topic / Posts matched / Chapters / Examiners / Questions per chapter / Scoring / Pass threshold / Output PDF / Drive upload / Git commit

"Topics needing attention" section: Two amber warning cards (Kafka — 14 new posts, CAP Theorem — 8 new posts) each with ⚠ icon, bold title, tertiary sub-text.

"▶ Start pipeline" primary button (full width, blue). "Save as draft" secondary button.

---

### Screen 3 — Run Detail (Pipeline Console)

**Layout:** Split screen. 210px left sidebar + remainder main area.

**Sidebar (light secondary background, right border):**

Header block (bottom border):
- "Kafka — Stream Processing" (12px/500)
- "Started 10:02 · Pass 2" (10px/tertiary)
- Author tag pills: small blue pill "vutr" + small teal pill "luc"
- Green animated badge "● Running"

Stage list (5 stages with 1px vertical connectors between):

Stage 1 — Done: 28px green circle with ✓ icon | "Content ingestion" / "272 posts merged · 5 chapters"
Stage 2 — Done: 28px green circle with ✓ icon | "Pack generation" / "vutr_luc_kafka.pdf · 2.4 MB"
Stage 3 — Active: Animated SVG ring (2px blue arc rotating on grey circle track, 28px) with small blue inner circle and refresh icon | "Verification loop" / "Pass 2 · joint examination" — row has 2px blue left edge accent
Stage 4 — Pending: 28px grey outlined circle with users icon | "Sign-off gate" / "vutr · luc · Justin · Alex"
Stage 5 — Pending: 28px grey outlined circle with upload icon | "Delivery" / "Drive · git · PR"

**Main area:**

Top bar (bottom border): "Verification — Pass 2" (12px/500) | right: amber pill "👥 Joint · 5 agents active"

**Agent strip** (horizontal scroll, 10px 14px padding, bottom border, 4 cards with 8px gap):

Card 1 — Joint examiner (blue+teal dual dots at top, blue-to-teal gradient left border 2px):
- Two 6px dots: blue + teal
- "vutr + luc (joint)" (11px/500)
- "Scoring Ch 3 together · 10 questions" (10px/tertiary)
- Blue "running" badge
- "6,057 tokens combined" (10px/tertiary)

Card 2 — Justin (teal left border):
- "Justin Sung" / "Answering all 10 Ch 3 questions" / green "running" / "4,102 tokens"

Card 3 — Alex (amber left border):
- "Alex Chen" / "Clarity audit · Ch 3" / amber "running" / "1,544 tokens"

Card 4 — Queued (grey left border):
- Two 6px dots: blue + teal
- "vutr + luc (joint)" / "Ch 4 questions · queued" / grey "queued" / "—"

**Score grid** (5 equal cells, secondary background, 8px radius each, 5px gap):

Each cell layout (top to bottom):
- Chapter label: "Ch 1" (10px/500/tertiary)
- Two small 6px dots side by side (blue + teal) — the joint examiner indicator
- Primary score: "9.2 / 9.3" (15px/500, green if passed, red if failed, tertiary dash if pending)
- Sub-label: "acc / cov" (9px/tertiary)
- Thin horizontal divider
- Alex row: small amber "alex" badge + score number (11px/500)
- Threshold: "all ✓" (9px/green) or "acc below ✗" (9px/red) or "scoring…" (9px/tertiary)

Cell states:
- Ch 1: 9.2/9.3 green · alex 9.1 green · "all ✓"
- Ch 2: 8.8/9.1 red on acc · alex 9.0 green · "acc below ✗"
- Ch 3: —/— tertiary · alex — · "scoring…"
- Ch 4: —/— · "queued"
- Ch 5: —/— · "queued"

**Gaps section** (bottom border, always visible):

Section header: "Gaps to fix (2)" (10px/500/uppercase/tertiary) with right-aligned count.

Two gap items (white background, thin border, 8px radius, 5px 10px padding):
- Tag (blue-teal gradient "Ch 2 · joint") + "ISR shrink trade-off missing — no discussion of availability vs. durability when ISR drops to 1"
- Tag (amber "Ch 2 · alex") + "'In-sync replica' used before definition — needs inline DEFINE on first use"

**Live log** (monospace, always visible, fills remaining height):

Section header: "Live log" (10px/uppercase/tertiary) | "15 events" (10px/tertiary right)

Log lines (11px monospace, 1.75 line height):
```
10:02:01  system   Pass 2 · joint mode · vutr + luc · 5 chapters · 10 q per chapter
10:02:03  vutr     Generating 5 questions for Ch 1 (Kafka fundamentals)
10:02:03  luc      Generating 5 questions for Ch 1 (system design angle)
10:02:07  justin   Answering 10 Ch 1 questions from joint pool
10:02:07  alex     Auditing Ch 1 for clarity gaps
10:02:15  system   Ch 1 joint score: acc 9.2 / cov 9.3 · alex 9.1 — all ✓  [green]
10:02:23  system   Ch 2 joint score: acc 8.8 / cov 9.1 · alex 9.0 — acc below threshold  [red]
10:02:24  vutr     Generating 5 questions for Ch 3 (Replication, ISR)
10:02:24  luc      Generating 5 questions for Ch 3 (failure handling angle)
10:02:25  justin   Answering 10 Ch 3 questions…  [blinking cursor block]
```

Agent name colors: vutr = #185FA5, luc = #0F6E56, justin = #0F6E56, alex = #854F0B, system = #888780. Pass lines: #3B6D11. Fail lines: #A32D2D.

---

### Screen 4 — Sign-off Gate + Delivery

**Layout:** Full-width, two-column (50/50), vertical divider.

**Top bar:** "← Run detail" · "vutr — Spark Internals · Sign-off gate" | right: amber badge "● Awaiting Alex"

**Left column:**

Green banner (green border + light green background, 10px 14px padding, 8px radius):
Large green ✓ icon | "All chapters passed ≥ 9.0" (12px/500/green) / "Verification complete · awaiting tri-agent sign-off" (11px/dark green)

Final score grid (same 5-cell layout as screen 3, all cells filled with green passing scores). Each cell: blue+teal dual dots, e.g. "9.2 / 9.3" green, alex score green, "all ✓" green.

Section label "Sign-off"

Three sign-off cards (stacked, 8px gap):

Card 1 — Approved (green border, light green card header):
- Header: "vu" avatar (blue circle, white text) | "vutr (examiner)" / "Technical accuracy · Spark internals" | green badge "✓ Approved"
- Body: checklist of 3 green ✓ criteria rows (11px)

Card 2 — Approved (same pattern):
- "JS" avatar (teal circle) | "Justin Sung" / "Pedagogical quality · WHY→WHAT→HOW" | green "✓ Approved"
- Body: checklist of 3 green ✓ criteria

Card 3 — Pending (default border, default header):
- "AC" avatar (amber circle) | "Alex Chen" / "Clarity · no blockers for a 15-year-old" | amber/grey "Running…" badge
- Body: italic grey placeholder "Auditing final PDF for remaining BLOCKERS…"

**Right column:**

Section label "Delivery checklist"

Five delivery step rows (each a card with thin border, 8px radius):

Step 1 — Done: green circle ✓ icon | "PDF generated" / "output/vutr_spark.pdf · 2.1 MB" | "Done" green text

Step 2 — Waiting: grey upload icon | "Google Drive upload" / "Learning Packs → Spark & Ben Dicken PDFs" | "Waiting" grey text — monospace detail row: `python3 scripts/gdrive_upload.py output/vutr_spark.pdf`

Step 3 — Waiting: grey git-commit icon | "Git commit" / "scripts/generate_vutr_spark.py + persona files" | "Waiting" grey — detail: `feat(vutr): Spark internals — 5 chapters, all ≥9.0 (pass 4)`

Step 4 — Waiting: grey branch icon | "Push branch" / "claude/eager-gates-UqFZF → origin" | "Waiting" — detail: `git push origin HEAD`

Step 5 — Waiting: grey PR icon | "Open pull request" / "gh pr create → syedamber91/knowledge-toolkit" | "Waiting" — detail: `gh pr create --title "feat(vutr): Spark internals..."`

Explanatory note block (secondary background, 8px radius, 11px/tertiary): "Delivery runs automatically once all three agents approve. If Alex rejects, a one-round fix is applied and sign-off re-runs before delivery."

"🚀 Ship — waiting for Alex" primary button — greyed out / disabled state (50% opacity). Full width.

"View Alex audit in progress" secondary button. Full width, outline style.

---

### Component Variants to Include

Please generate component variants for:

1. **Stage icon states:** done (green fill + check), active (animated ring + inner icon), pending (grey outline + icon)
2. **Status dots:** running (blue pulse), done (solid green), warning (solid amber), failed (solid red), pending (solid grey)
3. **Stage pills:** Verification (blue), Done (green), Sign-off (amber), Generating (grey), Stalled (red)
4. **Topic cards:** Suggested (plain), Shipped (green), New content (amber), Selected (blue)
5. **Agent cards:** vutr (blue left border), luc/justin (teal left border), alex (amber left border), joint (gradient left border), queued (grey left border)
6. **Score cells:** All passed, Acc failed, Queued, Scoring in progress
7. **Sign-off cards:** Approved (green), Rejected (red), Running (amber/pending)
8. **Delivery steps:** Done (green icon), Waiting (grey icon), In progress (blue animated icon)

---

### Frame Setup

- Frame width: 1440px (desktop)
- 4 frames, one per screen, arranged left to right with 80px gap
- Frame names: "Run List", "Pack Builder", "Run Detail", "Sign-off + Delivery"
- Use Auto Layout throughout
- All text styles should be defined as Figma text styles
- All colors should be defined as Figma color variables using the hex values above
