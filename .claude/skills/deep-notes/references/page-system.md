# The page system

The scaffold for a deep-notes page. Reuse the **structure**; choose fresh **colour and type** for every subject.

Contents:
1. Choosing this page's identity
2. Theme tokens — the three-state pattern
3. The CSS baseline
4. Component inventory
5. Building the file safely

---

## 1. Choosing this page's identity

Before writing CSS, decide three things and write them down:

**Palette — 5 to 7 named values.** Derive them from the subject's own world. A chapter about data lakes, streams and pipelines earned deep teal and a cool blue-grey paper. A chapter on soil science would earn something else entirely. Pick a neutral with a slight hue bias toward the accent — a pure mid-grey reads as unconsidered.

You need, at minimum:
- `paper` (page ground) and `surface` (cards) — plus `surface-2` for table headers and insets
- `ink`, `ink-2`, `muted` — three levels of text
- `line`, `line-soft` — borders
- one **accent** for "the thing being taught"
- one **warm** colour for money, caution, and the adjacent-but-different
- one **cool** colour for the neighbouring domain (in a data-engineering page: the ML pipeline)
- optionally one **flag** colour for "this is the problem" — used sparingly, it makes a failure argument land hard

Keep colour meaning consistent down the whole page. If teal means "your job" in section 1, it cannot mean "optional" in section 5.

**Type — three roles.**
- a **display** face with character, for headings and the plain-language lines
- a **body** face, readable at 17px for long stretches
- a **mono** face for anchors, tool names, commands and figures

Google Fonts is the only font host an Artifact can reach. Link it directly and always declare a real fallback stack. Avoid the defaults everyone reaches for (Inter, Space Grotesk as the "safe" sans). A grotesque display against a serif body against a mono utility is a solid, non-generic trio — but it is not the only one.

**Layout — one sentence.** The pattern that works: a narrow reading column (about 70ch, centred) with figures and tables breaking out to a wider band (about 1080px). Text stays comfortable; diagrams get room.

---

## 2. Theme tokens — the three-state pattern

The viewer has **three** states, not two. An explicit choice stamps `data-theme="dark"` or `data-theme="light"` on the root; the default "system" setting stamps *nothing*, and only `prefers-color-scheme` separates light from dark.

So every colour must be defined on bare `:root` first, then *redefined* in two more places. Style components through the tokens only — a colour whose sole definition lives inside a media query or a `[data-theme]` block simply does not exist in the un-stamped state, and the page renders one theme's text on the other theme's ground.

```css
:root{
  /* the COMPLETE light palette lives here */
  --paper:#E8EFF1; --surface:#FFFFFF; --surface-2:#F1F7F8;
  --ink:#0B2027; --ink-2:#37535E; --muted:#6B858E;
  --line:#C7D9DE; --line-soft:#DCE9EC;
  --accent:#0C7A87; --accent-ink:#0A5F69; --accent-soft:#D5EDF0;
  --warm:#9A5A00; --warm-soft:#F7E6C9;
  --cool:#3B4CA8; --cool-soft:#E1E5F8;
  --flag:#A8332B; --flag-soft:#F8DEDB;
  --shadow:0 1px 2px rgba(11,32,39,.05),0 8px 24px -12px rgba(11,32,39,.18);
  --display:"Your Display",ui-sans-serif,system-ui,sans-serif;
  --body:"Your Body",Georgia,serif;
  --mono:"JetBrains Mono",ui-monospace,Menlo,monospace;
  --col:70ch; --wide:1080px;
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    /* redefine ONLY the colour tokens; the guard lets an explicit light choice win */
    --paper:#061619; --surface:#0D2229; --surface-2:#123039;
    --ink:#E0EDF0; --ink-2:#AEC6CD; --muted:#7F9BA4;
    --line:#1D3F48; --line-soft:#16333B;
    --accent:#3ECAD6; --accent-ink:#7CE0E9; --accent-soft:#0D383F;
    --warm:#E9B061; --warm-soft:#3A2B10;
    --cool:#98A4F5; --cool-soft:#1C2350;
    --flag:#F2897E; --flag-soft:#3D1A16;
    --shadow:0 1px 2px rgba(0,0,0,.4),0 8px 24px -12px rgba(0,0,0,.7);
  }
}
:root[data-theme="dark"]{
  /* the same dark block again, so the explicit toggle also wins */
}
```

Two more rules that keep each theme resolving as a set:

- `body` must set `background:var(--paper)` explicitly. A transparent body borrows the host's ground and the page breaks in one theme.
- Never write a literal colour on an element. Every colour comes from the token set that matches the surface behind it.

Before publishing, scan the stylesheet for any colour declared *only* inside a media or `[data-theme]` block. That is the classic unreadable-artifact bug.

Two safe literals: pure `#fff` and near-black text placed on a saturated fill you drew yourself (a label inside a coloured SVG rect). Those are contrast decisions, not theme decisions.

---

## 3. The CSS baseline

The component CSS below is subject-independent — copy it and only swap the token values and font names above it.

```css
*{box-sizing:border-box}
body{margin:0; background:var(--paper); color:var(--ink);
  font-family:var(--body); font-size:17px; line-height:1.62; -webkit-font-smoothing:antialiased}
.wrap{max-width:var(--wide); margin:0 auto; padding:0 20px 100px}
.col{max-width:var(--col); margin-left:auto; margin-right:auto}
p{margin:0 0 .9em}
h1,h2,h3,h4{font-family:var(--display); font-weight:800; letter-spacing:-.015em;
  text-wrap:balance; margin:0}
h2{font-size:clamp(28px,4.4vw,38px); line-height:1.1}
h3{font-size:clamp(21px,2.8vw,25px); line-height:1.2; font-weight:600}
h4{font-size:17px; line-height:1.3; font-weight:600; letter-spacing:0}
.eyebrow{font-family:var(--mono); font-size:11px; font-weight:600;
  letter-spacing:.14em; text-transform:uppercase; color:var(--muted)}

/* section rhythm */
section{margin-top:76px}
.block{margin-top:44px}
.lechead{border-top:3px solid var(--ink); padding-top:18px; margin-bottom:34px}
.lechead .row{display:flex; flex-wrap:wrap; align-items:baseline; gap:14px; margin-bottom:10px}
.lecnum{font-family:var(--mono); font-size:12px; font-weight:600; color:var(--surface);
  background:var(--ink); padding:4px 9px; border-radius:2px; letter-spacing:.08em}

/* the two signature devices */
.stamp{display:inline-block; font-family:var(--mono); font-size:11px; color:var(--muted);
  border:1px solid var(--line); border-radius:2px; padding:2px 7px; margin-bottom:10px; white-space:nowrap}
.plain{font-family:var(--display); font-weight:400; font-size:clamp(19px,2.5vw,22px);
  line-height:1.42; color:var(--ink); margin:0 0 .7em; text-wrap:pretty}
.plain em{font-style:normal; background:var(--accent-soft);
  box-shadow:0 0 0 3px var(--accent-soft); border-radius:1px}
.term{font-family:var(--mono); font-size:.82em; font-weight:600; color:var(--accent-ink);
  background:var(--accent-soft); padding:1px 6px; border-radius:2px; white-space:nowrap}

/* cards */
.card{background:var(--surface); border:1px solid var(--line); border-radius:4px;
  padding:20px 22px; box-shadow:var(--shadow)}
.card .sub{font-size:14.5px; color:var(--ink-2)}
.card p:last-child{margin-bottom:0}
.grid{display:grid; gap:14px}
@media(min-width:700px){
  .g2{grid-template-columns:1fr 1fr}
  .g3{grid-template-columns:repeat(3,1fr)}
  .g4{grid-template-columns:repeat(4,1fr)}
}

/* callouts */
.note{border-left:3px solid var(--accent); background:var(--accent-soft);
  padding:14px 18px; border-radius:0 3px 3px 0; font-size:15.5px}
.note.warn{border-left-color:var(--warm); background:var(--warm-soft)}
.note.bad{border-left-color:var(--flag); background:var(--flag-soft)}
.note.alt{border-left-color:var(--cool); background:var(--cool-soft)}
.note strong{font-family:var(--display); font-weight:600}

/* tables — always inside .scroll so the page body never scrolls sideways */
.scroll{overflow-x:auto; -webkit-overflow-scrolling:touch; margin:0 -4px; padding:0 4px 4px}
table{border-collapse:collapse; width:100%; font-size:14.5px; min-width:520px;
  background:var(--surface); border:1px solid var(--line); border-radius:4px}
th,td{text-align:left; padding:10px 13px; border-bottom:1px solid var(--line-soft); vertical-align:top}
thead th{font-family:var(--mono); font-size:10.5px; letter-spacing:.1em; text-transform:uppercase;
  color:var(--muted); font-weight:600; background:var(--surface-2); border-bottom:1px solid var(--line)}
tbody tr:last-child td{border-bottom:0}
td.num{font-family:var(--mono); font-variant-numeric:tabular-nums; white-space:nowrap}
.mono{font-family:var(--mono); font-size:.88em}

/* pills */
.pills{display:flex; flex-wrap:wrap; gap:6px; margin:8px 0 0}
.pill{font-family:var(--mono); font-size:11.5px; padding:3px 8px; border-radius:2px;
  background:var(--surface-2); border:1px solid var(--line); color:var(--ink-2)}
.pill.on{background:var(--accent-soft); border-color:var(--accent);
  color:var(--accent-ink); font-weight:600}

/* proportional bars — for any arithmetic argument */
.bars{display:flex; flex-direction:column; gap:9px}
.bar{display:grid; grid-template-columns:minmax(120px,1.05fr) 1fr auto; gap:12px;
  align-items:center; font-size:14px}
.bar .lbl{font-family:var(--display); font-weight:600; font-size:14px; line-height:1.25}
.bar .track{height:14px; background:var(--surface-2); border:1px solid var(--line-soft);
  border-radius:2px; overflow:hidden}
.bar .fill{height:100%; background:var(--accent); opacity:.85}
.bar .fill.f{background:var(--flag)}
.bar .fill.c{background:var(--cool)}
.bar .fill.w{background:var(--warm)}
.bar .val{font-family:var(--mono); font-variant-numeric:tabular-nums;
  font-size:12.5px; color:var(--ink-2)}

/* figures */
figure{margin:0}
figcaption{font-size:13.5px; color:var(--muted); margin-top:10px}
.fig{background:var(--surface); border:1px solid var(--line); border-radius:4px;
  padding:18px; box-shadow:var(--shadow)}
.fig svg{display:block; width:100%; height:auto}
.svgtitle{font-family:var(--display); font-weight:600}
.svglbl{font-family:var(--mono); font-weight:400}

/* recall cards — auto-numbered */
.recall{counter-reset:r}
.recall .card{position:relative; padding-left:56px}
.recall .card::before{counter-increment:r; content:counter(r,decimal-leading-zero);
  position:absolute; left:20px; top:19px; font-family:var(--mono);
  font-size:12px; font-weight:600; color:var(--accent)}

/* glossary */
.gloss{display:grid; gap:0; font-size:14.5px}
.gloss div{display:grid; grid-template-columns:minmax(140px,auto) 1fr; gap:16px;
  padding:9px 0; border-bottom:1px solid var(--line-soft)}
.gloss div:last-child{border-bottom:0}
.gloss dt{font-family:var(--mono); font-size:12.5px; font-weight:600; color:var(--accent-ink)}
.gloss dd{margin:0; color:var(--ink-2)}

/* code */
code{font-family:var(--mono); font-size:.85em; background:var(--surface-2);
  border:1px solid var(--line-soft); padding:1px 5px; border-radius:2px}
pre{font-family:var(--mono); font-size:12.5px; line-height:1.7; background:var(--surface-2);
  border:1px solid var(--line); border-radius:4px; padding:14px 16px; overflow-x:auto; margin:0}
pre code{background:none; border:0; padding:0; font-size:inherit}

footer{margin-top:80px; padding-top:22px; border-top:1px solid var(--line);
  font-size:13.5px; color:var(--muted)}
:focus-visible{outline:2px solid var(--accent); outline-offset:2px}
@media (prefers-reduced-motion:reduce){*{animation:none!important; transition:none!important}}
```

Note the specificity discipline: `.card` and `.note` never fight over padding because callouts are `.note`, not `.card.note`. Keep it that way.

---

## 4. Component inventory

| Class | Use for |
|---|---|
| `.col` | wrap prose in this; omit it to let a figure or table break out wide |
| `.eyebrow` | small uppercase mono label above a heading |
| `.lechead` | the header block that opens each major section |
| `.stamp` | the source anchor: `[12:00 – 17:00]`, `p. 41`, `§3.2` |
| `.plain` | the big plain-language line; wrap the key phrase in `<em>` to highlight it |
| `.term` | the real industry term, inline |
| `.card` + `.grid.g2/.g3/.g4` | 2–6 sibling concepts |
| `.note` / `.warn` / `.bad` / `.alt` | a rule, a caution, a failure, a neighbouring-domain aside |
| `.scroll` > `table` | any comparison or enumeration |
| `.pills` > `.pill` | a run of tool names |
| `.bars` > `.bar` | any proportional argument |
| `.fig` > `svg` + `figcaption` | a figure; caption carries the anchor and the "so what" |
| `.recall` > `.grid.g2` > `.card` | end-of-page recall claims |
| `.gloss` | the abbreviation decoder |

---

## 5. Building the file safely

These pages run 40–150 KB. Build in passes:

1. `Write` the head (title, font link, full `<style>`), the hero, and the orientation figure.
2. Append each subsequent section with a heredoc:

```bash
cd <dir> && cat >> page.html <<'HTMLEOF'
<section>
  ...
</section>
HTMLEOF
```

Quote the delimiter (`<<'HTMLEOF'`) so the shell does not expand `$` or backticks inside your HTML.

3. If you opened `<div class="wrap">` in pass 1, strip its closing tag before appending and re-add it at the very end — or simply leave the wrap unclosed until the final append.

4. Validate before publishing:

```bash
python3 -c "
s=open('page.html').read()
print('bytes:',len(s)); print('figures:',s.count('<svg'))
for t in ['div','section','svg','table','figure','g']:
    o=s.count('<'+t+'>')+s.count('<'+t+' ')
    print('balanced',t+':', o-s.count('</'+t+'>'))
"
```

Every number must be `0`. Unbalanced `<div>` is the failure that eats half a page with no error.

**Artifact constraints worth remembering:** no `<!DOCTYPE>`, `<html>`, `<head>` or `<body>` tags — write the page content directly, starting with `<title>`. Google Fonts is the only reachable external host; everything else must be inline. Wide content scrolls inside its own container, never the body.
