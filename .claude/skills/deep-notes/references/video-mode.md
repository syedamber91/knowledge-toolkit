# Video mode

Turns a topic into a narrated explainer video (Remotion or Manim) instead of an HTML page. Same governing rule as page mode — **no information loss** — but a different deliverable, and it fails in different ways. Read this whole file before starting one; it is the entire skill for this mode.

**Where this came from.** Three rounds of the same two videos (rate limiting, auth & security). Round 1 was rejected as rushed and jargon-heavy. Round 2 fixed pace, jargon and added one running analogy — and was *still* rejected, for three reasons that are now the core of this file:

1. **Pros, cons, best practices and trade-offs were bullet slides.** "Written down in plain text — which I don't even recall five minutes after watching." Nothing moved while those points were spoken.
2. **Explanations were only "okay".** Each concept needs a kid-level version *and* a real computer / HLD use case, so the viewer never needs to reopen the book.
3. **Alternatives were taught in silo.** Four options, no use cases, no side-by-side, no "use this one over that one when…".

Round 3 fixes all three and is the pattern below. The rule that ties it together: **if the narrator says it, something on screen is doing it.**

Contents:
1. Scope: read everything first
2. The teaching loop — every concept, every time
3. Show, don't list
4. Alternatives: race, scorecard, decision tree
5. Structure of the whole video
6. The timing contract (TTS → timeline → scenes)
7. Simulations are code, and they are verified
8. Building scenes (and splitting work across agents)
9. QA
10. Rendering, episodes, delivery
11. Environment traps
12. Things that go wrong

---

## 1. Scope: read everything first

Read **every** source for the topic — each persona's lecture in the vault, not just the first one found. The rate-limiting v3 script came from three lectures, and each contributed worked numbers the others lacked. Build an inventory (every mechanism, worked example with its numbers, caveat, best practice, trade-off, named real system) and write the script against it — the same inventory discipline as page mode.

- **Every worked number comes from the source.** A window of 10s with a limit of 5, a request at 12s rejected — use the lecture's own numbers so the video and the book agree.
- **Real-world examples not in the source are allowed but flagged** in the script file as outside the course (e.g. "AWS API Gateway uses a token bucket" was flagged). Never present them as course content.
- **Length follows content, not a target.** Rate limiting's full coverage came to ~34 minutes. That is fine — split into episodes (§10) rather than cutting material.

---

## 2. The teaching loop — every concept, every time

Each concept (an algorithm, an attack, a component, a best practice) runs the same five steps, each a separate cue so the picture changes with it:

| Step | What the narrator does | What the screen does |
|---|---|---|
| 1. **Kid version** | An everyday object that works the same way: a clicker that resets on the clock, a notebook of arrival times, a game's ability charges, a printer queue. | That object, drawn and moving. |
| 2. **The mechanism, live, with real numbers** | Walks the worked example: "one… three… five… the sixth is rejected." | A simulation plays at the narrator's pace: requests fall, counters tick, the 6th dot turns red *on the word* "rejected". |
| 3. **Where computers use it** | One or two concrete systems a 15-year-old recognises: a free weather API's daily quota; a login page's "5 wrong tries in any 15 minutes". | A card per use case, drawn as that system (phone, login form), not a text list. |
| 4. **Break it, live** | The weakness, *demonstrated*: the fixed-window edge burst, the sliding log's memory growth, the token bucket's flood. | The same simulation driven into the failure, zoomed in on the moment it fails. |
| 5. **Takeaway** | One sentence: when to reach for it. | Short on-screen stamp (≤8 words). |

The kid version always comes first. The running analogy from round 2 (the nightclub bouncer) still frames the whole video — progress bar icon, chapter cards, callbacks — but each concept also gets its **own** kid object in step 1. One frame story, many concrete objects: that is not the "disconnected analogies" failure, because the frame story never drops.

---

## 3. Show, don't list

A bullet list on screen is the failure mode. Replace every list with a vignette:

- **A pro** is shown by the mechanism succeeding (the burst absorbed, the queue draining at a steady 1 per second).
- **A con** is shown by driving the same simulation into the failure (the flood, the backed-up queue, the two limiters that both read "2 left").
- **A best practice** is a **before/after**: the broken version plays, then the fixed version plays with the same input. ("Watch the door all night" is a live dashboard with a spike crossing a threshold, not the sentence "monitor your limits".)
- **A trade-off** is a see-saw or dial that moves as the narrator says "too low… too high".
- **A number** is a counter that changes, never a static figure.

Design rules for every scene (put these in the project's scene guide so agents follow them):
- **Every cue changes the picture.** If a cue's narration could play over the previous frame unchanged, the scene is missing a beat.
- **On-screen labels ≤ 8 words.** Subtitles carry the sentence; the screen carries the picture.
- **Fixed state colours across the whole video**: blue = waiting, green = accepted, red = rejected, amber = queued. Never reuse them for anything else.
- Emoji are fine for objects (install Noto Color Emoji first). Never an emoji as the only carrier of meaning.
- **No text-only slides**, including recaps. The recap is a memory map (§5).

---

## 4. Alternatives: race, scorecard, decision tree

Whenever the source teaches several options for one job (six rate-limiting algorithms, four API gateway types, three OAuth flows), add a comparison chapter with three scenes in this order:

1. **The race.** The *same* input through every option at once, one lane each, with a live score per lane ("10 through", "5 through", "7 queued"). The results must come from the real simulations (§7), not invented. The narrator walks lane by lane and the lane being discussed lights up while the others dim.
2. **The scorecard.** A grid of options × properties, filled in cell by cell *as the narrator says it*, colour-coded (green good, amber middling, red bad). Cells are words from the race the viewer just watched ("weak edges", "every timestamp").
3. **The decision tree.** Questions asked in order, each with a real example ("must what's behind you get a perfectly steady flow? — payments"), a marker walking down them, and a "yes →" arrow to the answer. Ends with the course's own rule where it has one.

Taught in silo, options are forgotten; raced against each other on the same input, the differences are the lesson.

---

## 5. Structure of the whole video

- **Cold open**: the promise, shown as a roadmap of the chapters, each lighting as it is named.
- **Chapters** (typically 6–8), each opening with a chapter card ("Part 4 of 8 · Head to head").
- **Chapter progress bar** at the top of every scene: the frame-story icon plus one segment per chapter, current one expanded with its title. It tells the viewer where they are in a 30-minute video.
- **Burned-in subtitles** at the bottom, one short line at a time, on the same clock as the scene (§6).
- **Active-recall quiz**: 5–6 questions, each shown, then a silent pause (`pause_after` ≈ 3–4s) so the viewer answers before the reveal; answered questions collect as chips along the bottom.
- **Memory map**: the whole video on one screen — every concept as an icon with its one-line "use it for", arranged around the frame-story character. This is the one screen the viewer should be able to recall from.
- **Closing**: one line.

Screen budget at 1280×720: progress bar y 0–44, content y 50–628, subtitles y 636–712. Keep content out of the subtitle band.

---

## 6. The timing contract (TTS → timeline → scenes)

Narration drives everything. Nothing on screen is timed by a hand-typed number.

**Script format** — beats split into cues:

```json
{"id": "fixed", "visual": "fixed_window", "cues": [
  {"id": "fw_kid", "text": "First, the kid version. ..."},
  {"id": "fw_w1",  "text": "Requests arrive at one, three, five, seven and nine seconds. ...", "pause_after": 1.5}
]}
```

Generate `script.json` from a Python builder (`build_script.py`) so cue ids and texts live in one reviewable place.

**TTS (`shared/generate_tts.py`)**: synthesises each cue separately (content-hash cache, so editing one cue re-synthesises only that cue), concatenates with `--cue-gap 0.35` between cues and `--gap 0.6` between beats, at `--speed 0.85`. `pause_after` adds silence after a cue so an animation can play with nobody talking over it.

**Measured segments.** Timing by character position alone drifted up to 1.45s inside long cues (measured over 723 clause boundaries: median 0.21s, 15 over 1s). So each cue is split at punctuation into clauses, and each clause start is snapped to the nearest real silence found by RMS energy analysis of the audio. `timeline.json` carries, per cue: `start_frame`, `spoken_frames`, and `segments: [{char_start, start_frame}]`. Within a clause, position is interpolated; across clauses, it is measured.

**Scenes read a cue clock**, never a frame number:

```ts
const c = useCues(beat);
c.start('fw_w1')                 // frame the cue starts
c.word('fw_w1', 'rejected')      // frame that word is spoken (measured segments)
c.fadeAt('fw_w1', 'rejected')    // 0→1 ramp starting at that word
c.reached('fw_w1'), c.progress('fw_w1'), c.between('a', 'b')
```

`word()` throws on a missing phrase, and a checker script (`check_scenes.py`) verifies every visual is registered and every cue id and `c.word` phrase exists in the script, so a script edit that breaks a scene fails before rendering.

**Simulation clocks are pinned to spoken words**, e.g. the sim time reaches 5s exactly when the narrator says "five":

```ts
const simT = interpolate(f,
  [c.start('fw_w1'), c.word('fw_w1', 'one'), c.word('fw_w1', 'three'), c.word('fw_w1', 'five')],
  [0, 1, 3, 5], clamp);
```

**Remotion placement**: one `<Sequence from={beat.start_frame}>` per beat — absolute placement, not `Series`, so rounding never accumulates. Subtitles use the same `frameOfChar` clock, so subtitle, voice and animation agree.

(For Manim, the round-2 `PacedScene.hold_until(fraction)` mixin still works for filling a beat; for word-level sync, read the same `timeline.json` cue frames and `self.wait()` to them. Remotion is the easier fit for live simulations.)

---

## 7. Simulations are code, and they are verified

Every mechanism is a pure function in one file (`src/sim/algorithms.ts`): input arrival times → a decision per request (`accepted` / `rejected` / `queued` + `servedAt`). Scenes render these decisions; they never decide anything themselves.

- **Verify each against the lecture's worked example before building its scene** (run the TS directly with `node --experimental-strip-types`). This caught a real mismatch: the sliding log accepted the lecture's 12s request because of `<=` vs `<` at the window edge.
- **The race (§4) uses the same functions on one shared input**, so its scores are true. Record the measured results in the build notes.
- **Arrival dots land at their arrival time** (they fall *before* it). A dot that starts falling at its arrival time lands late, and the counter disagrees with the stamp on screen — a real bug from round 3.

---

## 8. Building scenes (and splitting work across agents)

- Shared UI primitives in `src/lib/` (Stage, Heading, Label, Card, Dot, Arrow, Stamp, Meter; TimeAxis, ArrivalTrack, Bucket, CountBox). Scenes are pure functions of the frame.
- A **scene guide** (`SCENE_GUIDE.md`) in the project with the design rules from §3, the screen budget from §5, and the cue-clock API. Every agent reads it first.
- **Parallel build**: give each agent its own folder (`src/scenes/part1/`, `part2/`, …) and its own `index.ts` exporting a visual-name → component map; a registry spreads them all, with a placeholder fallback for anything missing. No two agents edit the same file.
- Add `tsconfig.json` (`strict`, `noUnusedLocals`, `noEmit`) and run `npx tsc -p .` — it catches dead code and bad props agents leave behind.

---

## 9. QA

A clean render proves nothing about layout. Round 3's still review caught about a dozen real defects the render hid: overlapping "429" labels, a latency bar drawn over a box, a label wrapping out of its card, a flood of 60 dots that rendered as 4 (they overlapped), axis labels drawn over a lane, a translucent overlay letting the previous scene bleed through.

1. `tsc` and `check_scenes.py` clean.
2. `npx remotion bundle` once, then take stills from the bundle at **cue-anchored** moments (`qa_stills.sh bundle beat:cue:secs …`, which resolves the absolute frame from `timeline.json`). Pick the moment each cue's key event happens, plus every phase an agent flagged as unsure.
3. **Look at every still.** Check: does the picture match the subtitle in that frame? Any overlaps, wraps, or elements at the screen edge? Does a counter agree with what's drawn?
4. Fix, re-bundle, re-shoot only the changed stills, look again.
5. Only then the full render.

---

## 10. Rendering, episodes, delivery

- Full render in the background with its log; a 34-minute video took ~30+ minutes.
- **Episodes**: cut at chapter boundaries (read chapter start times from `timeline.json`) into ~8–15-minute parts with `ffmpeg -ss … -to …` re-encoding, so each part starts on a chapter card.
- **Check file size before sending.** If over the delivery limit (30 MiB here), re-encode: `ffmpeg -y -i in.mp4 -c:v libx264 -crf 24 -preset medium -c:a aac -b:a 128k out.mp4`. Re-check duration and that audio is still present.

---

## 11. Environment traps

- **GitHub release assets are often reachable through a restrictive egress proxy; Hugging Face often is not.** Fetch TTS models from a GitHub release if HF fails.
- **`pip install imageio-ffmpeg`** bundles a static ffmpeg you can symlink to `/usr/local/bin/ffmpeg` when apt fails.
- **Manim** on an old system Python can hit `AttributeError: install_layout`; use an isolated venv.
- **Remotion's Chrome download can be blocked.** Point it at a pre-installed Chromium and force the modern protocol:
  ```bash
  npx remotion render src/index.ts <CompositionId> out.mp4 \
    --browser-executable=/opt/pw-browsers/chromium-*/chrome-linux/chrome \
    --chrome-mode=chrome-for-testing
  ```
- The composition id is whatever `<Composition id="…">` says, not the filename.

---

## 12. Things that go wrong

**A list of pros, cons or best practices on screen.** The single most-rejected pattern. Every item becomes a vignette (§3).

**Options explained one after another and never compared.** Add the race, scorecard and decision tree (§4).

**Only the kid version, or only the technical version.** Both, every concept, kid first, then a real computer use case (§2).

**Timing by guessed frame offsets.** They drift. Use `c.word()` on measured segments (§6).

**Scenes that decide outcomes themselves.** Outcomes come from verified simulations (§7), or the race lies.

**Skipping still review because the render exited cleanly.** It hid a dozen defects in round 3 (§9).

**Cutting content to hit a length.** Split into episodes instead (§10).
