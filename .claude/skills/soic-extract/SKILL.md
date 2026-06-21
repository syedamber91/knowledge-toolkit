---
name: soic-extract
description: Extract lesson transcripts and AI summaries from the SOIC Learnyst portal and sync them into the Obsidian vault at /Users/syedamberiqbal/Documents/Obsidian Vault/SOIC
trigger: /soic-extract
---

# SOIC Portal Extraction Skill

You are an expert at extracting content from the SOIC membership portal (learn.soic.in) and storing it in the Obsidian vault. Follow this skill exactly.

## Project paths

| Path | Purpose |
|------|---------|
| `/Users/syedamberiqbal/Documents/workspace/Claude_Code/SOIC_Scraper/` | Project root |
| `data/content.json` | Canonical data store (relative to project root) |
| `/Users/syedamberiqbal/Documents/Obsidian Vault/SOIC/` | Obsidian vault output |
| `.venv/bin/python` | Project virtualenv Python |

Run all Python commands from the project root using `.venv/bin/python`.

---

## Portal architecture (READ THIS FIRST)

The SOIC portal is a **Learnyst "Bodhi"** Next.js + Web Components PWA:

- **Auth**: localStorage-only (`lystATK` JWT). No HTTP session cookies. Pages load as SSR shells and only hydrate client-side when the user is actively logged in.
- **Shadow DOM**: All lesson UI lives inside open shadow roots of `bodhi-*` custom elements.
- **No href links**: Navigation is JS-router-driven. Lesson IDs only appear in the URL after the framework navigates.
- **Key constraint**: Pages only hydrate when Chrome has an active authenticated session. **Never reload a tab** — use `location.href = newUrl` for client-side routing which keeps React alive.

### Critical: hydration check before starting

Before any extraction, verify the tab is hydrated:

```javascript
function* walk(root){ for(const el of root.querySelectorAll('*')){ yield el; if(el.shadowRoot) yield* walk(el.shadowRoot); } }
const all = [...walk(document)];
const bodhiTags = [...new Set(all.filter(el => el.tagName?.toLowerCase().startsWith('bodhi-')).map(e => e.tagName))];
const tabs = all.filter(el => ['Transcript','Summary'].includes((el.textContent||'').trim()) && el.children.length === 0).map(e => e.textContent.trim());
({bodhiTags, tabs, bodyLen: document.body.innerText.length, url: location.href})
```

If `bodhiTags` is empty or `bodyLen` is 0, **the page is not hydrated**. Ask the user to open Chrome and navigate to a SOIC lesson page, then try again. DO NOT reload the tab — it will break hydration.

---

## Course and lesson data

### REST API (for discovery)

```python
import urllib.request, json

TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJ1aWQiOjEyNDkyODEyLCJzaWQiOjExMDk5OCwiZXhwIjoxNzgyNzYyNTU3LCJ0eXAiOjQsImxvayI6IjAwMDAiLCJpc0FkbWluIjpmYWxzZSwidG9rIjoiWDhEMnJuWkE1MkV2aEw5TjVTV3VIUSIsInRpbWUiOjE3ODE4OTg1NTd9.HyT-oQClk7JeqIfv0NZZ34GngfvAP3EzVvDUFoQNrow"
# Note: token expires 2026-08-29. Refresh from localStorage.lystATK if expired.

def api_get(path):
    req = urllib.request.Request(f"https://apig.learnyst.com/{path}",
                                  headers={"Authorization": f"Bearer {TOKEN}"})
    return json.loads(urllib.request.urlopen(req).read())

# Get all lessons for a course
lessons = api_get("learner/v2/lessons?course_id=145316")  # Level 3
# Full lesson detail (includes attachment metadata)
detail = api_get("learner/v1/lessons/2110384")
```

### Known Level 3 lesson IDs (course_id=145316, section_id=340917)

| Lesson ID | Title | Type | Duration |
|-----------|-------|------|---------|
| 2172995 | What you will Learn in this Course? Intro | video | 1m 48s |
| 2110384 | Why Valuation Matters + Odd Meter! | video | 2h 3m 8s |
| 2111873 | Art of Business Valuation-Different Methods | video | 2h 17m 41s |
| 2101461 | How Buffett Actually Invests? Valuation Methods | video | 2h 30m 29s |
| 4207666 | Portfolio Allocation Approach | video | 2h 9m 51s — **no transcript/summary** |
| 3633621 | Part 1 Valuation Across Industries | video | 2h 31m 58s |
| 3649709 | Part 2 Finding Intrinsic Value Across Sectors | video | 2h 9m 2s |
| 3843911 | Part 1 Financial Modelling | video | 1h 16m 31s |
| 3868816 | Part 2 Financial Modelling | video | 1h 54m 34s |
| 2208287 | Links To Best Talks on Valuation | article | — |
| 2173004 | What you will Learn in this Course? Conclusion | video | 5m 43s |
| 2156434 | QUIZ | quiz | — |
| 2156435 | Remember & Share- Key Points to Remember | article | — |

Lesson URL pattern:
`https://learn.soic.in/learn/home/SOIC-Course/how-to-value-a-company/section/340917/lesson/{lessonId}`

---

## Step-by-step extraction procedure

### Step 1 — Verify hydrated tab

Use `mcp__Claude_in_Chrome__list_connected_browsers` and `mcp__Claude_in_Chrome__tabs_context_mcp` to find available tabs. Check hydration with the JS snippet above. Use the tab titled "SOIC- Seeking Wisdom" if present — it is usually the hydrated one.

If no hydrated tab exists, tell the user: *"Please open Chrome, navigate to any SOIC lesson page, and let me know when it's loaded."*

### Step 2 — Navigate to a lesson (client-side routing)

```javascript
location.href = 'https://learn.soic.in/learn/home/SOIC-Course/how-to-value-a-company/section/340917/lesson/{LESSON_ID}';
```

Wait 10 seconds, then verify the new lesson is loaded before extracting.

### Step 3 — Extract AI summary

```javascript
await new Promise(r => setTimeout(r, 9000));
function* walk(root){ for(const el of root.querySelectorAll('*')){ yield el; if(el.shadowRoot) yield* walk(el.shadowRoot); } }
// Click Summary tab
const btn = [...walk(document)].find(el => (el.textContent||'').trim() === 'Summary' && el.children.length === 0);
if (btn) btn.click();
await new Promise(r => setTimeout(r, 5000));
// Extract from bodhi-ai-lesson-summary shadow root
const comp = [...walk(document)].find(el => el.tagName?.toLowerCase() === 'bodhi-ai-lesson-summary');
const sr = comp?.shadowRoot;
const text = sr ? (sr.querySelector('.summary-container') || sr).innerText || '' : '';
// Check for "not available" state
const notAvailable = sr?.innerHTML?.includes('not available') || false;
localStorage.setItem('soic_summary_{LESSON_ID}', text);
({len: text.length, notAvailable, preview: text.slice(0, 100)})
```

### Step 4 — Extract transcript

```javascript
// Click Transcript tab
function* walk(root){ for(const el of root.querySelectorAll('*')){ yield el; if(el.shadowRoot) yield* walk(el.shadowRoot); } }
const btn = [...walk(document)].find(el => (el.textContent||'').trim() === 'Transcript' && el.children.length === 0);
if (btn) btn.click();

// Poll for container (up to 15s)
let sr, container;
for (let i = 0; i < 30; i++) {
  await new Promise(r => setTimeout(r, 500));
  const comp = [...walk(document)].find(el => el.tagName?.toLowerCase() === 'bodhi-lesson-transcript');
  sr = comp?.shadowRoot;
  container = sr?.querySelector('.transcript-container');
  if (container) break;
}

if (!container) {
  // Check if "not available"
  const msg = sr?.innerHTML?.slice(0, 200) || 'no component';
  ({error: 'no container', msg})
} else {
  // Scroll to load all virtualized entries
  const seen = new Map();
  let lastCount = 0, stableRounds = 0;
  while (stableRounds < 4) {
    sr.querySelectorAll('[data-timestamp]').forEach(e => {
      const ts = e.getAttribute('data-timestamp');
      const text = (e.innerText || e.textContent || '').replace(/^\s*\d+:\d+:\d+\s*/,'').trim();
      if (ts && text) seen.set(ts, text);
    });
    container.scrollTop += 5000;
    await new Promise(r => setTimeout(r, 600));
    if (seen.size === lastCount) stableRounds++;
    else { stableRounds = 0; lastCount = seen.size; }
  }
  const sorted = [...seen.entries()].sort(([a],[b]) => a.localeCompare(b));
  const text = sorted.map(([ts,t]) => `[${ts}] ${t}`).join('\n');
  localStorage.setItem('soic_transcript_{LESSON_ID}', text);
  ({count: sorted.length, chars: text.length, last: sorted[sorted.length-1]})
}
```

### Step 5 — Download all data to disk

After extracting all lessons, download via blob (avoids MCP string truncation):

```javascript
// Download summaries
const summaryIds = ['2172995','2110384','2111873','2101461','4207666','3633621','3649709','3843911','3868816','2173004'];
const summaries = {};
for (const id of summaryIds) summaries[id] = localStorage.getItem('soic_summary_' + id) || '';
const blob1 = new Blob([JSON.stringify(summaries)], {type:'application/json'});
const a1 = Object.assign(document.createElement('a'), {href: URL.createObjectURL(blob1), download: 'soic_summaries.json'});
document.body.appendChild(a1); a1.click(); document.body.removeChild(a1);

// Download transcripts
const transcriptIds = ['2172995','2110384','2111873','2101461','3633621','3649709','3843911','3868816','2173004'];
const transcripts = {};
for (const id of transcriptIds) transcripts[id] = localStorage.getItem('soic_transcript_' + id) || '';
const blob2 = new Blob([JSON.stringify(transcripts)], {type:'application/json'});
const a2 = Object.assign(document.createElement('a'), {href: URL.createObjectURL(blob2), download: 'soic_transcripts.json'});
document.body.appendChild(a2); a2.click(); document.body.removeChild(a2);

'downloads triggered'
```

Files land in `~/Downloads/`.

### Step 6 — Update content.json

```python
import json

catalog = json.load(open('data/content.json'))
summaries = json.load(open('/Users/syedamberiqbal/Downloads/soic_summaries.json'))
transcripts = json.load(open('/Users/syedamberiqbal/Downloads/soic_transcripts.json'))

level3 = next(c for c in catalog['courses'] if 'Level 3' in c['title'])
for module in level3['modules']:
    for lesson in module['lessons']:
        lid = lesson.get('url','').split('/lesson/')[-1]
        if lid in summaries and summaries[lid]:
            lesson['ai_summary'] = summaries[lid]
        if lid in transcripts and transcripts[lid]:
            lesson['body_text'] = transcripts[lid]

json.dump(catalog, open('data/content.json','w'), indent=2)
print('content.json saved')
```

### Step 7 — Regenerate Obsidian vault

```bash
SOIC_VAULT_DIR="/Users/syedamberiqbal/Documents/Obsidian Vault/SOIC" \
  .venv/bin/python -c "
from src.soic_toolkit.vault import build_vault
from src.soic_toolkit.models import Catalog
build_vault(Catalog.model_validate_json(open('data/content.json').read()))
"
```

---

## Rules and guardrails

- **Personal use only** — this is the user's own membership. Crawl politely.
- **NEVER download, decrypt, or rip DRM-protected video/audio.** Only capture text the authenticated page renders.
- **NEVER store passwords.** The lystATK token is a session JWT, not a password.
- **NEVER reload a tab** during an extraction session — it breaks hydration. Always use `location.href` for navigation.
- **Ask before moving to a new chapter/level** — the user wants to control scope.
- **`body_text` is for transcripts only** — do not put AI summaries there.
- **Transcripts go in separate files** — `vault.py` writes transcripts to `{lesson-slug}-transcript.md` in the same directory as the lesson note, and links from the main note via `[[slug-transcript|📄 Full transcript →]]`. Never embed the full transcript inline in the lesson note.

---

## Handling common failures

| Symptom | Cause | Fix |
|---------|-------|-----|
| `bodhiTags: []`, `bodyLen: 0` | Page not hydrated | Ask user to open Chrome + navigate to SOIC |
| Tab CDP timeout (45s) | Renderer frozen | Use a different tab; create new MCP tab if needed |
| `count: 0` from transcript extraction | Tab click re-rendered component | Skip the click, poll for container directly |
| `"not available"` in shadow root | Portal hasn't generated this content yet | Skip, note as unavailable |
| `bodyLen: 0` but `htmlLen > 100000` | SSR shell only, no hydration | Do not reload; get a fresh hydrated tab |
| MCP string truncation at ~1000 chars | Tool limitation | Use `localStorage` + blob download trick (Step 5) |

---

## Checking what's already captured

```python
import json
catalog = json.load(open('data/content.json'))
level3 = next(c for c in catalog['courses'] if 'Level 3' in c['title'])
for m in level3['modules']:
    for l in m['lessons']:
        lid = l.get('url','').split('/lesson/')[-1]
        has_summary = bool(l.get('ai_summary','').strip())
        has_transcript = bool(l.get('body_text','').strip())
        print(f"{lid:10} summary={'✅' if has_summary else '❌'} transcript={'✅' if has_transcript else '❌'}  {l['title'][:50]}")
```

---

## Adding a new course/level

1. Discover course_id via REST API: `api_get("learner/v17/courses/course_ids?seo_title=SOIC-Course")`
2. Get lessons: `api_get(f"learner/v2/lessons?course_id={course_id}")`
3. Get lesson IDs and build URL pattern from `_buildManifest.js` or existing patterns
4. Add course entry to `data/content.json` manually or via crawler
5. Run extraction loop (Steps 2–7) for new lessons
