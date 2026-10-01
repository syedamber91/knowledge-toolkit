---
title: Structure Recovery (Autoformat Cookbook)
kind: cookbook
source: Structure recovery (cookbooks/autoformat)
source_url: https://docs.typesafe.ai/cookbooks/autoformat
tags: [cookbook, classification, cost-latency]
topics: [topic-classification, topic-extraction, topic-cost-latency]
---
# Structure Recovery (Autoformat Cookbook)
> Rebuild Markdown from plain text that lost its formatting using two System One requests (stitch split sentences with Noul, classify blocks with Choice) while code does all rendering, so no output character is ever model-generated.

## What it is / How it works
Input: a team memo (build-system migration) whose markup was stripped: lines hard-wrapped mid-sentence, no heading markers, no list bullets, a bare shell command, an unmarked warning. Blank lines survived; every marker (`- `, `1.`, `#`) did not.

**Core design rule.** A text-generation rewrite could change words. Here the model never generates text; it only answers narrow questions ("does this line pick up mid-sentence?", "what kind of content is this block?"). Code renders. Result: every character of output comes from the input, and every judgment carries a probability. "The pipeline only chose boundaries, types, and markup."

**Two API requests per document, in sequence:**

| Pass | Primitive | One question per | Purpose |
|---|---|---|---|
| 1 stitch | `Noul` (yes/no, answer = P(yes)) | adjacent line pair (pairs split by a blank line are skipped) | merge lines whose break tore a sentence |
| 2 classify | `Choice` (+ companion questions) | merged block | heading / paragraph / list_item / quote / code / callout |

Pass 2 cannot be merged into pass 1 because the blocks only exist after pass 1 answered.

**Direct evidence stays in code, never sent to the model:** blank lines and explicit markers. The model only gets questions code cannot answer from the text.

**Preprocessing (code only, no model):** `to_lines` collapses whitespace, strips, drops blank lines but records a `gap` flag (a leading blank is not a break). `tag()` prefixes each item with an id: `L013| text` for lines, `B000| text` for blocks, with a blank line reproduced before gap items. The ids are ordinary text the model reads as part of the state; questions and answers refer to lines/blocks by id (same scheme as the semantic search cookbook, see [[cb-line-by-line-search]]). Memo = 28 non-blank lines.

**All behaviour is specified in the pass-2 criteria**: three dicts of one-line descriptions plus the step question's true/false criteria. "There is no other logic. To adapt the pipeline to your own documents, edit these descriptions."

### Pass 1: stitching
Question (per i, only if line i has no preceding blank line):
- instructions: "Does line L{i} pick up mid-sentence, continuing a sentence left unfinished at the end of line L{i-1}?"
- `NoulCriteria.true`: line starts in the middle of a sentence begun on the previous line (the break tore the sentence apart).
- `NoulCriteria.false`: line begins a new sentence, item, heading, or thought of its own.
All 16 pair questions go in a single request. Model `jev-1.12`; `client.system_one(state=tag(LINES,"L"), questions=..., model=...)`; join prob read from `response.answers[id].noul` (0.0 if absent).

**Merge cutoff depends on how the previous line ends (read in code):**
- previous line is *dangling* (no sentence-ending punctuation): join if P >= **0.2** (`JOIN_AFTER_DANGLING`)
- previous line ends with terminal punctuation (`. ! ? : ;` and ellipsis, optionally followed by closing quote/bracket; regex `[.!?:;…]["')\]]*$`): join only if P >= **0.5** (`JOIN_AFTER_TERMINAL`)
- never join across a gap (blank line).
Joined text is concatenated with a single space; block remembers its line indexes.

Result: 28 lines -> 17 blocks (11 line breaks healed). 16 questions, one request, 0.32 s.

### Pass 2: classification
Per block, in ONE request, up front (companion questions are asked before the type is known, to avoid a third round trip):
1. `type_B###` : `Choice`, "What kind of content is block B###?" with 6 options (criteria dict below).
2. `hlevel_B###` : `Choice` (title / section / subsection), asked only if block text length <= **90 chars** (`HEADING_MAX_CHARS`; longer blocks cannot render as headings so are not asked; default to "section" when absent).
3. `step_B###` : `Noul`, "Is block B### an instruction in a sequence where the order of the items matters?" true = one step of a procedure, items around it must happen in order; false = order irrelevant, a loose collection, or not a list item at all.
4. `callout_B###` : `Choice` (note / tip / warning), "What kind of aside is block B### ?"

Most companion answers are never read (e.g. step probability of a paragraph is ignored). Rationale: "An extra question adds little, since the state is most of the tokens and is sent once either way, while an extra round trip adds a full request of latency."

Option descriptions (the entire classifier spec):

| Question | Option | Description (condensed from source) |
|---|---|---|
| type | heading | short label/title naming the document or following section, not a full sentence of content |
| type | paragraph | running prose, one or more complete sentences |
| type | list_item | one entry in a list of parallel items (ingredient, feature, task, attendee); reads as one of several siblings |
| type | quote | words attributed to a person/source: quoted speech, citation, excerpt |
| type | code | code, shell command, terminal output, config snippet meant to be read verbatim |
| type | callout | warning, tip, or important note interrupting the flow to flag something the reader must not miss |
| hlevel | title / section / subsection | title of whole doc / major section heading / minor heading nested under a section |
| callout kind | note / tip / warning | neutral extra info / helpful suggestion or shortcut / caution about something that can go wrong or cause harm |

Pass 2 for the memo: 62 questions about 17 blocks, one request, 0.51 s. (62 = 17 type + 17 step + 17 callout + 11 hlevel `[inference: 11 blocks were <= 90 chars; the source gives only the total]`.)

### Rendering (code)
- Consecutive `list_item` blocks form one list; consecutive `code` blocks form one fenced block.
- List is **numbered if the mean of the items' step probabilities >= 0.5** (`STEP_THRESHOLD`), else bulleted. This is a group-level decision no single question asked directly.
- heading -> `#`/`##`/`###` by hlevel; quote -> `> text`; callout -> `> [!WARNING]` / `[!NOTE]` / `[!TIP]` then `> text`; paragraph -> raw text. Parts joined with blank lines.

## When to use / when NOT to use
Use when text structure must be recovered **without any chance of altered wording** (rewrite-risk is unacceptable), and you want per-decision probabilities (to flag uncertain blocks for review). Adapt by editing the criteria dicts.
Not stated in source as a limitation, but note: this cookbook is demonstrated on one memo only `[inference: generality untested in source]`. Explicit markers/blank lines are intentionally handled in code, not by the model.

## Worked example (memo)
Input (excerpt): "Migration to the new build system", then hard-wrapped paragraph lines, "What changes for you", "bun run build" on a bare line, a colon-ended sentence followed by 3 team lines, "Things to do before Monday" followed by 3 imperative lines, an unmarked warning, a quote attributed to Dana, a sign-off.

Stitched blocks (17): B000 title; B001 4 lines; B002 heading; B003 3 lines; B004 `bun run build`; B005 3 lines; B006 2 lines (intro sentence to team list); B007-B009 three team lines; B010 heading; B011-B013 three step lines; B014 3 lines (warning); B015 2 lines (Dana quote); B016 sign-off.

Pass-2 judgments:

| block | type | confidence | companion used |
|---|---|---|---|
| B000 Migration to the new build system | heading | 0.99 | level=title |
| B001 "Hi everyone, quick heads up..." | paragraph | 0.98 | - |
| B002 What changes for you | heading | 0.75 | level=section |
| B003 The old make targets... | paragraph | 0.89 | - |
| B004 bun run build | code | 1.00 | - |
| B005 Generated artifacts... | paragraph | 0.90 | - |
| B006 The cutover touches three teams... | paragraph | **0.43** | - |
| B007 The platform team | list_item | 0.99 | step=0.15 |
| B008 The web client team | list_item | 1.00 | step=0.16 |
| B009 Whoever still owns the release tooling | list_item | 0.99 | step=0.12 |
| B010 Things to do before Monday | heading | 0.96 | level=section |
| B011 Update your local toolchain to version 2.4 or later | list_item | 0.98 | step=0.86 |
| B012 Delete the old build cache directory | list_item | 0.99 | step=0.87 |
| B013 Run the doctor script and fix anything it flags | list_item | 0.92 | step=0.90 |
| B014 If the doctor script reports a red result... | callout | 0.65 | kind=warning |
| B015 As Dana put it in the kickoff, "..." | quote | 0.99 | - |
| B016 Thanks, and shout if anything looks off. | paragraph | 0.92 | - |

Rendered: `# title`, paragraphs, `## What changes for you`, fenced `bun run build`, paragraphs, the intro sentence then a **bulleted** 3-item list (step mean about 0.14), `## Things to do before Monday` then a **numbered** 1-3 list (step mean about 0.88), `> [!WARNING]` callout, `> ` quote, closing line. Team lines are bulleted (step ~0.1), the todo lines numbered (step ~0.9).

## Numbers & limits

| Item | Value |
|---|---|
| Model | `jev-1.12`; price constant `(0.042, 0.00)` $ per 1M tokens (input, output), "as of 2026-09" |
| Requests per document | 2 (round trips) |
| Pass 1 | 16 questions, 0.32 s |
| Pass 2 | 62 questions, 0.51 s |
| Total | 10,211 tokens, 0.8 s |
| Cost | see Gotchas: source gives conflicting figures ($0.0003 printed vs $0.0015 in prose) |
| Join cutoff after dangling line | 0.2 |
| Join cutoff after terminal punctuation | 0.5 |
| Heading max chars (hlevel asked) | 90 |
| Numbered-list threshold (mean step P) | 0.5 |
| Suggested review flag | block type confidence < 0.55 |
| Setup | `pip install ipython 'cooksafe>=0.2.0,<0.3.0'`; set `TYPESAFE_API_KEY`; `json_cache.json` ships with cookbook so re-render replays numbers without API; delete to re-run live. Client timeout 120 s |
| Document source | pinned GitHub gist `build-memo.txt` (commit-pinned URL) for reproducibility |

### Join probabilities from pass 1 (appendix)
Breaks that truly split a sentence score 0.39 and up; breaks the author meant score near zero.

| prob | line |
|---|---|
| 0.77 | L002 "happening next week..." |
| 0.62 | L003 "mode for three weeks..." |
| 0.39 | L004 "make the switch for real." (a true continuation, the lowest) |
| 0.42 | L007 "entrypoint is a single command..." |
| 0.59 | L008 "docs build that used to be separate." |
| 0.48 | L011 "uploads them to the registry..." |
| 0.40 | L012 "just creates merge conflicts." |
| 0.50 | L014 "list before you plan anything for Monday:" |
| 0.22 | L015 "The platform team" (follows a colon) |
| 0.11 | L016 "The web client team" |
| 0.12 | L017 "Whoever still owns the release tooling" |

Why two cutoffs: a single cautious 0.5 cutoff would break healthy paragraphs (L004 = 0.39 is a true continuation). A single low cutoff would clear L015 (0.22 > 0.2) and merge the team list into its introducing sentence (it follows a colon). No single threshold works for both cases; checking punctuation in code first separates the bands.

### Wording experiment: "mid-sentence" vs "same paragraph" (appendix)
First version asked: "Are lines L{i-1} and L{i} part of the same paragraph?" (true: same paragraph of running text; false: different paragraphs or different pieces of content). It failed: list items typed without bullets are a "paragraph" in the loose sense (adjacent, same topic), so the model says yes to nearly every pair and lists collapse.

| line | mid-sentence | same paragraph |
|---|---|---|
| L015 The platform team | 0.22 | 0.77 |
| L016 The web client team | 0.11 | 0.81 |
| L017 Whoever still owns the release tooling | 0.12 | 0.78 |
| L020 Delete the old build cache directory | 0.08 | 0.88 |
| L021 Run the doctor script and fix anything it flags | 0.05 | 0.91 |

Blocks after merge: **17** (mid-sentence) vs **12** (same paragraph). Lesson stated in source: "When a judgment call feeds a threshold, the question should name the narrowest fact that decides it." "Same paragraph" asks whether topic carries over (it does between list items); "picks up mid-sentence" asks about the text itself.

### The lowest-confidence block
B006 "The cutover touches three teams, so check whether you are on this list before you plan anything for Monday:" has type confidence 0.43; probabilities paragraph 0.53, list_item 0.24, callout 0.19. It is genuinely ambiguous (names what follows like a heading, is a complete sentence like a paragraph, sits where a callout would go). A UI can surface this: underline for review any block whose type confidence (probability behind the winning choice) is under 0.55. Note the winner still came out `paragraph` (correct).

## Gotchas
- **Cost figure is inconsistent in the source.** Code output prints `total 10,211 tokens 0.8s $0.0003`, while the prose and appendix text say "two round trips, 10,211 tokens, 0.8s, $0.0015". Computing from the stated price: 10,211 x $0.042/1M is about $0.00043 `[inference]`. Treat all three as unreliable; the order of magnitude is a fraction of a cent.
- Ask the narrowest objective fact (mid-sentence), not a topical judgment (same paragraph), whenever the answer feeds a threshold.
- Do not use one global threshold for the stitch step; condition it on a cheap code-readable fact (terminal punctuation).
- Companion questions are asked even when irrelevant; ignore irrelevant answers (step prob of a paragraph is meaningless).
- Do not send what code can read directly (blank lines, existing markers).
- Block ids and line ids are plain text in state; keep id schemes distinct (`L###` vs `B###`).

## Related
[[choice]] · [[noul]] · [[state]] · [[primitives-overview]] · [[confidence]] · [[cb-line-by-line-search]] · [[cb-parallel-questions]] · [[cb-hierarchical-classification]] · [[cb-classification-using-confidence]] · [[cookbooks-overview]] · [[topic-classification]] · [[topic-extraction]] · [[topic-cost-latency]]
