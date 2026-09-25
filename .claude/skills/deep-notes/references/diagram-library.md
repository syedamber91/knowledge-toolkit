# The diagram library

Inline-SVG figure archetypes that carry teaching weight, with coordinates that work. Adapt them; do not treat them as a fixed set.

Contents:
1. Rules that apply to every figure
2. The archetypes
3. Density: what changes between balanced, heavy and max
4. When *not* to draw

---

## 1. Rules that apply to every figure

**Use `viewBox="0 0 1000 H"` with a plain `<svg>` inside `.fig`.** Width 1000 keeps arithmetic easy; the CSS makes it fluid. Choose `H` to fit the content, typically 150–470.

**Colour comes from the page's tokens.** Inline SVG reads CSS variables: `fill="var(--accent-soft)"`, `stroke="var(--accent)"`. This is what keeps figures legible in both themes.

Two exceptions where a literal is correct: `#fff` or a near-black on a saturated fill you drew yourself, and a small set of hand-picked hues when a figure needs several *distinguishable* categories (four partitions, six coloured blocks). Those hues must work on both grounds — mid-saturation, mid-lightness. Test mentally against near-black and near-white.

**Two text classes, always.** `class="svgtitle"` for names and headings inside a figure; `class="svglbl"` for labels, units and asides. They pick up the display and mono faces. Set `font-size` inline (typically 9–17) and `text-anchor="middle"` for centred text.

**Give every figure `role="img"` and an `aria-label`** describing what it shows.

**Caption it.** `<figcaption>` carries the source anchor and the "so what" — the sentence the figure exists to prove. A figure without a caption makes the reader guess why they're looking at it.

**Arrows.** Cheap and consistent:

```xml
<g stroke="var(--accent)" stroke-width="2" fill="var(--accent)">
  <path d="M152 104 h 14"/>
  <path d="M166 104 l -7 -4 v 8 z"/>
</g>
```

The line is a `path` with `stroke`; the head is a filled triangle. For a dashed "this is different" arrow add `stroke-dasharray="5 4"`.

---

## 2. The archetypes

### A. Pipeline / stage flow
**Proves:** a thing moves through ordered stages.

Six boxes across 1000 units: width 150, gap 20, so `x` = 0, 170, 340, 510, 680, 850. Boxes at `y=56 h=96`. Arrows at the vertical midpoint in the 20-unit gaps.

Inside each box, three lines: a small stage label (`STOP 3`), the stage name in `svgtitle` at 16px, then one or two mono detail lines.

Two upgrades that earn their place:
- a **reverse arrow above** the row, dashed and in a second colour, when something flows the other way (requirements, control, feedback)
- a **bracket underneath** spanning a subset — `d="M170 178 v 10 H 830 v -10"` — labelled with what that span means ("this stretch is your job")

Colour the boxes by ownership, not decoratively: muted/dashed for "not yours", accent for "yours", cool for "the next team's".

### B. Definition ladder
**Proves:** a term is built from simpler terms.

Four boxes across, equal width ~215 with gaps, arrows between. Each box: the word in `svgtitle`, a plain gloss underneath in `svglbl`. Highlight only the final box with the accent border — that's the term being defined. Put the source's exact definition sentence underneath the row as centred `svglbl` text.

### C. Split / fan-out
**Proves:** one big thing becomes many small things.

A wide box at top (the whole), dashed lines fanning down to 3–5 boxes below (the parts). Give each part box internal detail — small filled rects representing its contents — so the reader sees the parts are the same *kind* of thing as the whole.

Label the naming underneath: "in HDFS these are called DataNodes."

### D. Proportional argument
**Proves:** an arithmetic claim, visually.

Two or more horizontal bars, `x=0`, width proportional to the values, at different `y`. Label above in `svglbl`, value at the right in `svgtitle` at 16px. Use the flag colour for the bad number and the accent for the good one.

For a parallel-execution argument, draw the first bar solid and the others as thin ghost bars underneath, then annotate "the other three run in parallel — not after". That distinction is exactly where readers go wrong.

For pure numbers, the CSS `.bars` component is often better than SVG — it's less code, aligns digits with `tabular-nums`, and skims well. Reach for SVG only when the layout itself carries meaning.

### E. Term chain
**Proves:** a calculation, step by step.

Boxes separated by `×` and `=` glyphs in `svgtitle` at 24px. Each box: the number large (20–26px), the unit small underneath. The final box gets the accent border. Reads left to right like the equation it is.

### F. Multi-step anatomy
**Proves:** an internal process, and who owns each step.

The highest-value figure type. Lay steps in two rows of three or four, with a connector wrapping from the end of row one to the start of row two:

```xml
<path d="M890 148 V 172 H 110 V 196" stroke="var(--accent)" stroke-width="2" fill="none"/>
```

Each step gets a `svglbl` header above the box (`STEP 4 · WRITE TO MEMORY`) and detail inside.

**Highlight the one step the reader is responsible for** with the flag colour and a thicker stroke. Then put a full-width summary bar underneath: "Of these seven steps, you write exactly one." That contrast is the teaching.

### G. Many-to-many redistribution
**Proves:** a shuffle, a join, a routing.

Three source boxes along the top, each containing 4 small coloured rects. Four destination boxes along the bottom, each in one of those colours. Curved connectors between:

```xml
<path d="M44 80 C 44 110, 120 120, 120 200" stroke="var(--warm)" stroke-width="1.3" fill="none"/>
```

Colour is what makes this readable — every P1 rect the same hue, landing in the P1 destination. Put a full-width labelled band between the two rows naming the operation ("THE COPY PHASE — moved over the network. This is the expensive part.").

### H. Layer stack
**Proves:** an architecture, and what sits on what.

Full-width bars stacked bottom-up in dependency order, `height` 42–58, gaps of ~16. Two lines each: the name in `svgtitle`, its job in `svglbl`.

The teaching move: draw a **bypass**. When some tools skip a layer, split that layer's row — solid box on the left for what uses it, a dashed empty box on the right labelled "these go straight past". That single visual answers the question people actually have.

### I. Side-by-side comparison
**Proves:** two designs differ, and the difference has consequences.

Split at `x=0..470` and `x=530..1000`. Identical internal grid on both sides so only the arrangement differs. Small `svglbl` header above each half naming it. A verdict line under each half in `svgtitle`.

Then a full-width band underneath with the *consequence* — the sentence the comparison exists to deliver.

### J. Nested hierarchy
**Proves:** a container format, a nesting doll.

Outer full-width bars for header and footer. Between them, a large bordered region; inside that, 2–3 sibling regions; inside the first one, the leaf blocks. Draw the first sibling in full detail and the others at reduced opacity with "same shape inside" — this shows repetition without 3× the drawing.

### K. Numbered flow with an annotation list
**Proves:** a protocol, a request lifecycle.

Boxes positioned to reflect the real topology (client left, coordinator centre, workers right). Arrows between them. Numbered circles on the arrows:

```xml
<circle cx="200" cy="92" r="14" fill="var(--cool)"/>
<text x="200" y="97" text-anchor="middle" class="svgtitle" font-size="13" fill="#fff">1</text>
```

Then the numbered steps written out as `svglbl` lines below the diagram, each opening with a bold `tspan` for the step name. Diagram and prose reinforce each other.

### L. Annotated problem diagram
**Proves:** why a naive approach fails.

Draw the naive design on the left half. On the right half, stack `PROBLEM 1..4` headings in the flag colour, each with two lines of explanation. Close with a full-width flag-coloured band stating the conclusion.

This is how you make a failure argument land before revealing the fix. Follow it immediately with the same diagram redrawn with the fix in place — the visual echo does the work.

### M. Chapter / source map
**Proves:** the shape of the whole source.

Every major unit as a box across the top, sized to fit, with its duration or page range as an `svglbl` label above. Arrows between them if order matters. Underneath, a dashed bracket spanning everything with the one-line thesis of the source.

Use this as the orientation figure. A reader who stops here still leaves with the shape.

---

## 3. Density: what changes

| Content | balanced | heavy | max |
|---|---|---|---|
| Orientation of the whole source | figure (always) | figure (always) | figure (always) |
| A process with 3+ ordered steps | figure | figure | figure + a who-does-what table |
| An architecture or layering | figure | figure | figure + a per-layer table |
| An arithmetic argument | `.bars` component or a sentence | archetype D or E | archetype D or E, **plus** `.bars` with the exact values |
| A two-way comparison | table | archetype I, **plus** the table | archetype I **plus** the table |
| A worked allocation example | table or `.bars` | archetype D with staged states | staged figure **plus** the `.bars` walk-through |
| A failure argument | `.note.bad` callout | archetype L, then the fix redrawn | archetype L, the fix redrawn, **plus** the measured numbers as `.bars` |
| A definition worth dwelling on | bordered card with `.plain` | archetype B | archetype B **plus** the bordered card |
| A container format's internals | table | archetype J | archetype J **plus** the level-by-level table |
| A list of tools per category | table | table (unchanged — a list is a list) | table (unchanged) |

Note the last row. Some content is a table in every mode. `heavy` is not "draw everything"; it is "draw everything that has a shape." And `max` is not "draw everything twice" — a table only joins a figure when it carries values, extra rows or per-item caveats the figure cannot hold. A table that just restates a figure's labels is padding; cut it.

Note "plus the table" wherever it appears: a figure often *joins* a table rather than replacing it. That is coverage-preserving by construction, and in `max` it is the default rather than the exception.

---

## 4. When *not* to draw

- **A list with no relationship between items.** Ten industries that use data are a two-column card grid or a bulleted pair of lists, not a diagram.
- **A single fact.** "MSK costs $0.43/hour" is a table row.
- **Something you would have to invent to draw.** If the source does not say how the parts connect, do not guess a topology. Say what the source says.
- **A repeat of the previous figure with one label changed.** Merge them, or use opacity to show the variant inside the first.
- **Three figures in a row.** In every mode, alternate figure → table/cards → figure. An unbroken run of diagrams reads as a slideshow and stops teaching. In `max`, a figure and the table that pins its values count as **one** block for this rule — they belong together — so keep varying what comes after that pair.

The test for any figure: *what does a reader know after looking at this that they would not know from the sentence next to it?* If the answer is "nothing", it is decoration — cut it and keep the sentence.
