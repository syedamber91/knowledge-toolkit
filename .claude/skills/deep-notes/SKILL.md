---
name: deep-notes
description: Turn a source you want to LEARN — a course chapter or lecture, a transcript, a spec, documentation, a research paper, a long report — into either (a) a diagram-rich, skimmable HTML study page published as an Artifact, covering every topic and sub-topic with nothing summarised away, at your choice of diagram density (balanced, heavy, or max for both figures and tables), with an optional layer of relatable real-world examples pitched at a 15-year-old, or (b) a narrated explainer VIDEO (Remotion or Manim) built around one continuous running analogy that chains every topic together for recall. Use the HTML mode whenever someone asks to "make notes", "break down this chapter", "help me learn/retain this", "make this easy to remember", "turn this into something I can study from", "explain this visually", asks for notes "with diagrams and tables", asks for examples "a teenager/15-year-old/kid would get", or wants a chapter/lecture/paper rendered as an informative, eye-catching, easy-to-skim page. Use the video mode whenever someone asks for a "video", "voiceover", "explainer video", wants something they can "just watch and remember", asks for a scenario/analogy/story to understand a topic, or asks to turn a chapter/topic into a narrated walkthrough. Also use either mode when they name a chapter or lecture from a vault, course or folder and ask you to teach it or render it. Prefer this over writing notes in chat: the deliverable is a published page or a video file the user keeps, not terminal text. Do NOT use it for a quick one-paragraph answer, a code review, or a genuine summary request where the user explicitly wants things left out.
trigger: /deep-notes
---

# /deep-notes

Render a source into something a person can actually learn from: every topic and sub-topic present, arranged so it can be skimmed in two minutes, read in twenty, or watched start to finish and remembered.

Two output types, chosen by the user or inferred from how they asked:

- **Page mode** (default) — an HTML Artifact. Not a chat message, not a markdown file — a page the user keeps and returns to. Covered by the rest of this file.
- **Video mode** — a narrated MP4 (Remotion or Manim), built around one continuous running analogy that chains every topic together. Covered in `references/video-mode.md` — **read that file in full before starting a video**; the rest of this SKILL.md is written for page mode and its density/figure guidance does not apply to video the same way.

## Usage

```
/deep-notes <path or description of the source> [balanced | heavy | max] [+eli15]
/deep-notes <path or description of the source> video [+eli15]
```

If the user did not say which density they want (page mode) or asked for `video` with no further detail, **ask before building.** It changes how long the run takes and what the output feels like, and it is cheap to ask:

- **balanced** — a figure where an idea is genuinely spatial, sequential or comparative; tables and card grids everywhere else. Roughly one figure per major section. On a dense six-part chapter, expect ~9 figures and ~14 tables.
- **heavy** — diagram-led. Every mechanism, worked number, before/after and architecture gets its own figure. Tables reserved for pure enumerations. Expect 20–30 figures on a dense chapter.
- **max** — both at once: `heavy`'s full figure set **and** `balanced`'s full table set, on the same page. Nothing is rendered one way instead of another; the mechanisms get drawn *and* the specifics get tabulated. The reference page for that is one where a figure teaches the shape of an idea and a table underneath it carries the exact values. Expect 25+ figures, 15+ tables, and a file two to three times the size of either single mode. Use it when the page is a long-term reference rather than a first read.
- **video** — a narrated MP4, typically 10–20 minutes for a dense topic, built entirely on the pattern in `references/video-mode.md`: slower deliberate narration, every jargon term defined in plain language the moment it appears, ONE running scenario established at the start and revisited at every single topic transition with a callback line, and illustrated diagrams for that scenario alongside the technical diagrams. This is a different deliverable shape from a page — do not treat it as "page content read aloud."

**Density changes rendering, never coverage.** A `balanced` page and a `heavy` page from the same source contain the same facts. If you find yourself dropping a detail because you chose `balanced`, you have misunderstood the setting — put the detail in a table instead.

`max` is the exception that proves this: it does not *add* facts either, because the other two modes were never allowed to lose any. What it adds is **redundancy of rendering** — the same fact reachable both by looking and by reading. That is genuinely useful for revision, and genuinely wasteful for a first pass. Say so when offering it.

**`+eli15` is a second, independent toggle — ask about it alongside density, not instead of it.** It turns on device 7 below: one relatable, real-life example per major concept, pitched at a 15-year-old. It never changes density, coverage, or the technical rigor of the rest of the page — it adds one extra callout per concept, nothing more.

---

## The one rule that matters: no information loss

Everything else in this skill serves this. A study page fails the moment its reader has to go back to the source for something the source actually said.

**Read the entire source first.** All of it, in full, before writing a single line of the page. Not the index, not a summary, not the first file and an assumption about the rest. If it is six lecture transcripts, read six lecture transcripts.

**Then build an inventory.** Before you write any HTML, list — for yourself, in your thinking or a scratch file — every:

- named tool, product, service, library, format
- number: sizes, durations, prices, counts, thresholds, versions, timestamps
- domain, industry, use case, or example the source enumerates
- caveat, gotcha, trap, "you must" and "do not"
- definition, and the exact words used for it
- worked example with its actual figures
- command, flag, and file path
- opinion or judgement the author expresses (these are often the most memorable part)

Then write the page against that inventory and check every item made it. This inventory step is the whole anti-summarisation mechanism. Skipping it is how pages quietly lose a third of their content.

**Bans that keep you honest:**

- No "etc." No "and others." No "among many." If the source names ten domains, all ten appear on the page.
- No "the author then discusses X." Say what X *is*.
- No collapsing two examples into one because they make the same point. The reader may only remember one of them.
- No dropping a number because it seems minor. Numbers are what make a page trustworthy.

**Skimmability does not come from cutting.** It comes from structure — cards, tables, chips, headings, figures — so the eye can land anywhere and get something. A dense page with good structure skims better than a thin page of paragraphs. Never trade coverage for brevity; trade paragraphs for tables.

---

## What makes these pages work

Six devices, learned from pages that landed. Use them all. A seventh — the 15-year-old example — is optional: use it only when `+eli15` was requested.

### 1. Plain language first, real term second

Every concept gets a big plain-language sentence, then the industry term as a small mono chip. The reader learns the idea and the vocabulary in one pass, and can skim just the plain lines on a re-read.

> Park the raw stuff in a `Data Lake`: any size, any shape.

Write the plain line so a bright twelve-year-old follows it. Write the term exactly as the field writes it. Never soften a technical term into vagueness — pair it, don't replace it.

### 2. Anchors back to the source

Every block carries where it came from: a `[mm:ss]` timestamp for video, a page number for a PDF, a section number for a spec, a heading for docs. Small mono chip, above the block.

This is what makes the page a study aid rather than a rewrite. The reader who wants more goes straight to the right minute of the video.

### 3. Figures that show mechanism

A figure earns its place when it shows something prose cannot: a flow, a split, a hierarchy, a before/after, a spatial arrangement, an arithmetic argument. Six boxes and arrows for what is really a list is decoration — use a card grid.

The best figure in either reference page was a seven-step process where exactly one step was highlighted as "the part you write." It taught a whole design philosophy in one image.

### 4. Structure that encodes something true

Numbered markers only where order actually matters. A staircase layout only when each step genuinely depends on the last. Colour meaning something consistent — one hue for "the thing being taught", one for "the problem", one for "the adjacent thing that isn't yours".

If a structural device would look the same on any page about anything, drop it.

### 5. Recall cards at the end

Ten to fifteen single-sentence cards, each one thing the reader should still know next month. Numbered, because they are a checklist. Written as claims, not topics: "Map transforms, reduce aggregates" beats "The map and reduce phases."

### 6. A glossary that decodes everything

Every abbreviation and jargon term used anywhere on the page, expanded in one line. Readers of technical material drown in acronyms; this is the single most-thanked section.

### 7. A 15-year-old example (only with `+eli15`)

Not the same job as device 1. Device 1 translates *vocabulary* — a jargon term into a plain sentence, one line, inline with the explanation. This device translates the *mechanism itself* into a scenario from an actual teenager's life, as its own callout, one per major concept (same granularity as a figure — not one per paragraph).

A valid example must satisfy every one of these, or it doesn't earn its place:

- **It maps element-for-element, not vibe-for-vibe.** If the concept has three moving parts, the scenario needs the same three, doing the equivalent job. "It's like a filing cabinet" that doesn't say what the drawers, the labels, and the search step correspond to is decoration, not an example — the same "no information loss" bar the rest of this skill holds everywhere else applies here too.
- **It comes from an actual 15-year-old's world**, not an adult's world simplified: a group chat, a multiplayer game's matchmaking or leaderboard, a class timetable, splitting a pizza bill or allowance with friends, a sports team's roster and substitutions, a streaming queue or playlist, a school's locker/hall-pass system, a social feed's ranking. Not "imagine you're a manager" or "like a company's supply chain" — that's an adult analogy wearing a younger label.
- **It says the mapping out loud.** Name each part of the scenario next to the technical part it stands for — the reader should never have to infer the correspondence.
- **One example, fully mapped, beats three half-mapped ones.** Do not stack multiple weak analogies hoping one lands.

Render it as its own callout, visually distinct from a warning or a definition — a label like `IF YOU WERE 15` above the block reads well. It sits alongside the section's other blocks (anchor → plain line → figure/table → **ELI15 callout**) and counts toward the alternation rule in the page skeleton — never stack it directly against another callout-shaped block.

---

## Workflow

1. **Locate and read the source, completely.** If it is a folder or a vault chapter, find every file that belongs to it and read each. Report the scope back — "6 lectures, 2h 29m" — so the user knows nothing was skipped.

2. **Confirm density, and whether to add `+eli15`,** if not given. Density: `balanced`, `heavy` or `max`. `+eli15`: yes/no.

3. **Build the inventory** described above.

4. **Plan the visual identity.** Read `references/page-system.md` for the scaffold. Derive palette and typefaces from the *subject* — a chapter about distributed storage and data lakes earned a water palette; a chapter on financial controls would not. Do reuse the component structure — that is what the reference file is for.

   **Continuity beats novelty within one body of work.** If this page belongs to a series you have already made pages for — another chapter of the same course, another part of the same spec, a re-render of the same source at a different density — **keep the established palette and typefaces.** A twenty-chapter course should look like one course, and a reader comparing two renderings of the same material should be comparing the material, not the paint. Derive a fresh identity when the *subject* is genuinely new, not merely because the file is.

   When you keep an identity, say so in your report, so the user knows it was a decision rather than an oversight.

5. **Plan the figures.** Read `references/diagram-library.md`. List every figure you intend to draw and what each one proves. Cut any that only decorate.

6. **Write the page.** Long files are normal — 40–150 KB. Write the head plus the first section with `Write`, then append later sections with a bash heredoc (`cat >> file <<'HTMLEOF'`). This avoids one enormous tool call and lets you validate as you go.

7. **Validate before publishing:**

```bash
python3 -c "
s=open('PAGE.html').read()
print('bytes:',len(s)); print('figures:',s.count('<svg'))
for t in ['div','section','svg','table','figure']:
    print('balanced',t+':', s.count('<'+t+'>')+s.count('<'+t+' ')-s.count('</'+t+'>'))
"
```

Every balance number must be `0`. An unclosed `<div>` silently swallows the rest of the page.

8. **Publish as an Artifact.** Give it a real name in `<title>` — a short noun phrase specific to this subject, not "Study Notes". Pass a `favicon` and a one-sentence `description`.

9. **Report back in the user's terms:** what you read, how many figures, the link, and one line on what to do next.

---

## Page skeleton

The order that works, whatever the subject:

```
Hero            — subject, one-sentence thesis, scope chips (lectures / pages / duration / figure count)
Orientation     — ONE figure that holds the whole source. The reader should be able to
                  stop here and still have the shape of it.
Section per unit— one per lecture / chapter / major part. Each opens with a header block
                  (number, duration/page range, one-line "what this part is for"), then
                  alternating blocks: anchor chip → plain line → figure or table or cards
                  → ELI15 callout (only if `+eli15`).
Recall          — 10–15 numbered claim cards
Glossary        — every abbreviation, one line each
Footer          — what this was built from, and the honest claim that nothing was cut
```

Within a section, vary the block type. Three tables in a row reads as a spreadsheet; three figures in a row reads as a slideshow. Alternate.

---

## Choosing figure vs table vs cards

| The content is… | Render as |
|---|---|
| A flow, pipeline, or sequence of stages | **Figure** — boxes and arrows |
| A part-to-whole or a carve-up | **Figure** — nested or divided rectangles |
| A before/after, or two competing designs | **Figure** — side-by-side panels |
| An arithmetic argument ("400s becomes 105s") | **Figure** — proportional bars, or a chain of terms with × and = |
| A layered architecture or ecosystem | **Figure** — a stack |
| A comparison across 3+ named attributes | **Table** |
| A long enumeration of tools per category | **Table** with a category column |
| 3–6 sibling concepts, each needing a sentence | **Card grid** |
| A single sharp warning, rule, or trap | **Callout** — coloured left border |
| A definition worth dwelling on | **Big plain line in a bordered card** |

In `heavy` mode, push rows 1–5 harder: an arithmetic argument that `balanced` would state in a sentence becomes a bar chart; a two-way comparison that `balanced` would table becomes a side-by-side figure. The *facts* stay identical either way.

In `max` mode, stop choosing. Anything with a shape gets its figure **and** anything with values gets its table, generally in that order — figure first to teach the mechanism, table underneath to pin the specifics. Two rules keep this from becoming noise: the table must carry something the figure genuinely cannot (exact values, extra rows, per-item caveats) rather than restating its labels, and the alternation rule below still applies, so a figure-plus-its-table counts as one block, not two.

---

## Reference files

- `references/page-system.md` — the HTML/CSS scaffold: theme tokens for all three theme states, the component classes (`.card`, `.note`, `.stamp`, `.plain`, `.term`, `.bars`, `.fig`, `.gloss`, `.recall`), layout rules, and the swap points where you choose this page's own palette and type. Read it before writing any HTML.
- `references/diagram-library.md` — the recurring inline-SVG figure archetypes with coordinates that work, plus the theming rules that keep figures legible in light and dark. Read it before drawing any figure.
- `references/video-mode.md` — the full video pipeline: the shared script/TTS/timeline contract, the running-analogy device (scenario panel, callback line, persistent corner icon), the proportional-pacing fix that keeps visuals tracking narration length however long a script grows, and the QA/delivery checklist. Read it in full before starting any video — it is the whole skill for that mode, not a supplement to the sections above.

---

## Things that go wrong

**Working from an index instead of the source.** A vault chapter note listing three lecture links is not the chapter. Open the lectures.

**Deciding a section is "just admin" and cutting it.** Course housekeeping, pricing, instructor background and setup caveats are exactly the details people forget and need. The cost lecture in the reference page is one of its most useful sections.

**Letting the density toggle eat content.** `balanced` means fewer *figures*, never fewer *facts*.

**Colours defined only inside a dark-mode block.** The most common way one of these pages ends up unreadable. Define every colour on bare `:root` first — `references/page-system.md` covers this properly.

**A title like "Chapter 2 Notes".** It sits in a gallery beside dozens of others. Name it for its subject.

**Claiming completeness you did not verify.** Before writing the footer line about nothing being cut, actually re-walk your inventory. If something genuinely did not fit, say what and why — do not quietly drop it and claim otherwise.

**An `+eli15` example that's decorative.** "It's kind of like TikTok" with no stated mapping is worse than no example — it teaches nothing and wastes the reader's trust. Every part of the concept needs a named counterpart in the scenario, or cut it.

**An `+eli15` example dressed as a kid's version of an adult analogy.** "Imagine you're the manager of a small team" is not a 15-year-old's world. Use their actual world: school, games, group chats, allowance, sports teams, streaming.
