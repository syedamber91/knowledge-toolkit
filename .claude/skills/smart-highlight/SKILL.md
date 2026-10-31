---
name: smart-highlight
description: Pre-highlight a chapter or web page the way the user does, so a re-read takes minutes. Reads the live page, picks the key sentences, marks them in the user's color code (pink recall, yellow caution, green/blue/red for flow), then proofreads the result with a blind reader. Use for "highlight this chapter/page", "pre-highlight", "mark the important parts", AlgoMaster chapters, or any doc the user wants to skim fast. Trigger /smart-highlight.
---

# smart-highlight

Goal: the user re-reads **only the highlights** tomorrow and still gets the whole topic. They then add their own marks on top.

## The user's color code (stated by them, keep it)

| Color | Meaning | Use for |
|---|---|---|
| Pink `P` | remember / recall | definitions, the rule, the one line to retain |
| Yellow `Y` | caution | failure cases, costs, gotchas, "this breaks when..." |
| Blue `B` | the running example / story | every sentence of a worked example, so it reads as one block |
| Green `G`, Red `R` | easy-reading rotation | everything else; neighbours in a list get different colors; red is the rarest (~6%) |

Their own past highlights (518 across 9 chapters, measured): about 35% of the words, about 16 words per mark, mostly whole sentences, plus some short terms (`RAG`, `Semantic search`), each list item marked separately. They asked for dense. Start near that and go higher only when proofreading shows gaps.

## Hard rules

1. **Worked examples are highlighted in full**, every sentence from setup to outcome. A fragment strips the context and the user flagged this as a defect. Example text is blue; what goes wrong in it is yellow.
2. **Exact page text only.** Never reword. Marks are whole sentences or exact fragments, in document order, no overlaps.
3. **Never touch highlights this run did not create.** The account already holds the user's own. To replace one of mine, delete it by exact text, then add the new one.
4. **Read the live page**, not an old capture. AlgoMaster rewrote the ACID chapter after the vault copy was made. Stale text makes every mark miss.
5. **Target reader = a junior, entry-level engineer** unless the user says otherwise. They know SQL and rows, not internals.

## Workflow

1. **Get the page text** from the user's signed-in Chrome (`mcp__claude-in-chrome__*`; load with ToolSearch first). The built-in browser is not signed in. Read the whole chapter with `get_page_text`.
2. **Plan the marks** as `[color, exact text]` in document order. Cover every section and subtopic, every named term, every example, every tradeoff, every default or number. Aim for no gaps, then trim.
3. **Check the plan:** paste `references/algomaster-highlighter.js`, run `HL.check(list)`. Fix every MISS, OVERLAP and DUPTEXT first.
4. **Apply in chunks of 5** with `HL.apply(list.slice(a, a+5))`. Never more: the browser tool dies at 45s and the site returns HTTP 503 if you go faster than about one mark per 2-3 seconds, and a 503'd highlight shows on the page but is **not saved**.
5. **Verify against the server, not the page:** `HL.missing(list)` must come back `[]`. Redo whatever is listed. Reload the page and look at a screenshot.
6. **Proofread with a blind reader** (below). Add what it finds missing, once or twice, no more. Do not loop to chase a perfect score.
7. **Report:** count saved, colors, reader score before/after, what is still unfixable. Offer to delete or recolor anything.

## Blind-reader proofread

Spawn a fresh Sonnet agent (a fresh one each round, so it is not anchored). Give it **only the highlights in reading order with their colors, no chapter**, and the persona (junior engineer). Ask for: (A) explain it back using only the highlights, marking `[GUESS]`; (B) every spot it got lost, by number; (C) answers to 12-14 questions drawn from the chapter, or `CAN'T TELL`; (D) a 0-10 coverage score and the top gaps ranked.

Measured on the ACID chapter: the first pass of 71 marks scored 3/10 for a 5-year-old, 4/10 after +30; the junior persona gave 6/10. A reader never gets past what the page itself explains: if the page leaves a term undefined, highlighting cannot fix that. Say so, and offer a short plain-words note instead (AlgoMaster has a Notes tab per chapter) for things like comparison grids and code that cannot be marked cleanly.

## How AlgoMaster's highlighter works (verified 2026-11-01)

- Real toolbar: select text, five dots appear (yellow, green, blue, pink, red), plus Note and Ask AI. Saved to the account, so it syncs to every device. Notebook button at the bottom bar lists them with a trash icon.
- API (same-origin, signed in): `GET /api/v1/user/notebook?pageType=system-design` returns `highlights[]` with `id, pageId, link, text, color, createdAt`. `POST /api/v1/highlights` creates one. Colors are `#fef08a` yellow, `#bbf7d0` green, `#bfdbfe` blue, `#fbcfe8` pink, `#fca5a5` red.
- The toolbar only appears for the **full** synthetic mouse-event sequence fired **twice**; the helper does this. A single `mouseup` shows nothing.
- Text that is already highlighted shows no toolbar (`NOBTN`). To recolor: delete, reload, add again.
- After a delete or a failed save the page still shows the old state. **Reload before trusting the DOM.** `window` state (the helper) is lost on reload; keep the plan in `sessionStorage` and re-paste the helper.
- Only `system-design` was verified for `pageType`. For ai-engineering, lld, dsa, watch the Network tab for the real value before relying on `HL.missing`.

## Other websites

No native highlighter means no persistent marks from here. Options, honest about limits: (a) a text-fragment link (`url#:~:text=start,end&text=...`) opens the real page with the phrases lit, but it is per-visit, one color, and first match only; (b) a private reader page with the text and baked-in colors, which copies the content (personal use, say so). Ask the user which, do not pick silently.

## Do not

- Do not delete, edit or recolor the user's pre-existing highlights.
- Do not type or store the user's password; the signed-in Chrome session is enough.
- Do not publish highlighted copies of paid content anywhere public.
