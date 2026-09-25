# Video mode

Turns a topic into a narrated explainer video (Remotion or Manim) instead of an HTML page. Same governing rule as page mode — no information loss — but a completely different deliverable shape, and it fails in different ways. Read this whole file before starting one; it is the entire skill for this mode, not a supplement to the page-mode sections above.

This file is a distillation of a real build (two full videos, ~30 minutes combined, one Remotion + one Manim) that shipped only after a first pass was rejected for being rushed, jargon-heavy, and disconnected scene to scene. Everything below is the fix for that, made the default rather than something to discover again by being told a second time.

Contents:
1. What video mode is not
2. The shared pipeline contract
3. The five things that make a video actually stick — all five, every time
4. Reusable code patterns (copy these, don't re-derive them)
5. QA — the step that catches real bugs, not a formality
6. Delivery — file size and the compression fix
7. Environment traps specific to this pipeline
8. Things that go wrong

---

## 1. What video mode is not

**Not page content read aloud.** A page's plain-language-first device, anchors, and glossary all exist because a reader can stop, re-read, and jump around. A viewer can't. A script that would make a fine page paragraph is *too fast* as narration — the fix isn't a faster reader, it's fewer words per idea, a slower pace, and a memory device (§3) doing the work a table of contents does on a page.

**Not one analogy per topic.** A different metaphor for hashing, a different one for encryption, a different one for TLS is *disconnected* — exactly what a viewer complained about. One scenario, established once, carried through every topic, is what makes the whole video feel like one thing instead of twelve.

**Not "add a video output" to an existing text pipeline.** The technical stack (TTS, a frame-accurate timing contract, a renderer) is genuinely separate infrastructure from the HTML page-builder above. Don't try to reuse `page-system.md`'s CSS/component approach here — it doesn't apply.

---

## 2. The shared pipeline contract

Both renderers below consume the exact same three artifacts, built once by a shared script:

```
script.json   →  generate_tts.py  →  audio/<beat_id>.wav (one per beat)
                                      master.wav (all beats concatenated with a fixed gap)
                                      timeline.json (the single source of truth)
```

`script.json` is a flat list of beats: `{"id": "...", "visual": "...", "text": "..."}`. `text` is the ONLY thing that ever changes hand-timing — editing it and re-running the TTS step automatically reflows every scene after it, in both renderers. Never hand-type a duration anywhere.

`timeline.json` carries, per beat: `duration_seconds` / `duration_frames` (renderer-appropriate), plus `fps` and `gap_seconds` at the top level. Remotion reads `duration_frames` directly into `Series.Sequence`. Manim reads `duration_seconds` through a small `PacedScene` mixin (§4) that pads a scene to match its own narration exactly.

**TTS defaults, baked in — do not ask, do not use engine defaults:**
- `speed: 0.85` (i.e. 15% slower than the engine's normal pace). The first pass at `1.0` was explicitly called out as "rushing through the content." Treat 0.85 as the floor, not a ceiling — slower again if the topic is genuinely dense.
- `gap: 0.6` seconds between beats, not the engine's default (often 0.3–0.4). The extra half-second is breathing room between topics, which matters more once §3's callback lines are landing right before a topic change.
- Kokoro (`kokoro-onnx`) is the engine used so far — free, local, no API key, two distinct voices (`am_michael`, `am_onyx`) used to tell two videos in a series apart. Any local or API TTS with a `speed` control works the same way; the contract above doesn't care which.

**Renderer choice is a project decision, not a rule derived from content.** Remotion (React, `Series`/`Series.Sequence`, `spring()`/`interpolate()`) suits system-diagram-style content — boxes, arrows, dashboards, anything that reads like a UI. Manim (`Scene`, `self.play()`) suits anything more mathematical or when the video is one of a course/lecture-style series already using Manim elsewhere. Both are equally capable of every device in §3 — the two videos this pattern came from used one of each, on purpose, to prove neither renderer is required for the pattern to work.

---

## 3. The five things that make a video actually stick — all five, every time

These are not optional enhancements. A video built without any one of them is the video that got rejected.

### a. Slower, deliberate pace
Covered in §2 — `speed: 0.85`, `gap: 0.6`. Applies to every video by default.

### b. Every jargon term defined in plain language, at first use
The exact translation of page mode's Device 1 ("plain language first, real term second") into narration: the moment a technical word is spoken for the first time, the SAME sentence (or the very next one) explains it in plain words a non-specialist would follow — never assume the term, never define it three beats later, never rely on the viewer to already know it. `SHA` becomes "a family of one-way scrambling functions"; `cipher` becomes "the wheel that turns your message into gibberish and back"; `PKCE` gets its acronym expanded and its purpose stated in one breath. Do this inline in the spoken script, not only as an on-screen chip — a viewer who looks away for two seconds still needs to follow.

### c. ONE running scenario, chained through every single transition
The single biggest fix. Pick one real-world scenario at the very start — a nightclub bouncer for rate limiting, a teenager's diary and a day at an amusement park for authentication concepts — and never leave it. Concretely, every scene:

1. **Opens** with a short "scenario panel": the analogy's own illustration plus 2–3 plain sentences restating what's about to happen in the story ("Riya presses a wax seal onto her diary's flap..."), *before* any technical content appears.
2. **Carries a persistent small icon** in a fixed corner for the rest of the scene — a constant visual reminder that the technical content about to appear is still inside the same story.
3. **Closes** with one callback sentence that explicitly ties the just-taught technical idea back to the scenario ("Just like Riya's wax seal: a hash proves nothing was touched. It never hides what's written.") This is the memory-chaining device itself — write it as a single, quotable, standalone sentence, not a recap paragraph.

If the source material genuinely splits into distinct clusters that one metaphor can't stretch across (e.g. "verifying data" vs. "granting access"), chain a **second act** rather than abandoning the device — a new scenario introduced with its own short transition scene ("Act 2 — ..."), still opening/closing every subsequent scene the same way. Two connected scenarios beats one strained one, which beats disconnected ones.

### d. Illustrated diagrams for the scenario itself, not only the technical content
The existing technical diagrams (boxes and arrows explaining the real mechanism) stay — this adds a second, small layer: simple, schematic icons of the analogy's own objects (a bouncer at a velvet rope, a wax seal, a decoder wheel, a wristband), drawn from plain shapes with no external image assets, used as (1) the scenario panel's illustration and (2) the persistent corner icon. Build a small reusable icon library once per video — 5–10 icon functions is typical — rather than one-off art per scene, so the same wristband reads as "the same wristband" every time it reappears.

### e. Visual pacing that tracks the ACTUAL narration length, not a guess
The defect that would otherwise undo all of the above: once narration gets slower and scripts get richer (from doing b–d properly), a scene's hand-built animation sequence — timed once, against an earlier, shorter draft — finishes in a fraction of the real narration time, and the rest plays out as a long, static, dead screen. Measured on a real build: a scene with ~114 seconds of narration had its entire animated sequence finish in ~17 seconds, leaving 85% of the scene motionless. See §4 for the fix (`hold_until`).

---

## 4. Reusable code patterns

Copy these; they are the direct fix for §3's mechanics, not illustrative pseudocode.

**Manim: proportional pacing.** A fixed-second `self.wait()` was the bug. Replace end-of-section waits with a *fraction of the beat's own total duration*, so a scene's content redistributes itself automatically however long the narration turns out to be — no re-tuning needed when a script is edited:

```python
class PacedScene:
    BEAT_ID: str = ""

    def _init_pacing(self):
        self._elapsed = 0.0

    def p(self, *animations, run_time=1.0, **kwargs):
        self.play(*animations, run_time=run_time, **kwargs)
        self._elapsed += run_time

    def w(self, seconds):
        if seconds > 0:
            self.wait(seconds)
            self._elapsed += seconds

    def hold_until(self, fraction: float):
        """Wait until this scene has consumed `fraction` of its own total
        narration length -- e.g. hold_until(0.5) right before a Part-2
        transition means Part 1 lingers for the first half of the beat's
        real narration, whatever that beat's own length turns out to be."""
        target = beat_duration(self.BEAT_ID) * fraction
        remaining = target - self._elapsed
        self.w(remaining)

    def finish(self):
        target = beat_duration(self.BEAT_ID)
        remaining = target - self._elapsed
        if remaining > 0.05:
            self.wait(remaining)
```

Use it at every natural break: `self.hold_until(0.5)` before a scene's own internal Part-2 transition, `self.hold_until(0.88)` right before the closing callback line fades in (so the callback holds on screen for the final stretch rather than the raw technical content sitting there unexplained), then `self.finish()` to mop up the remainder. For Remotion, the equivalent is computing each `Series.Sequence`'s `durationInFrames` straight from `timeline.json` (already the contract in §2) and placing transition components at fixed *fractions* of that duration rather than a fixed frame offset.

**The scenario panel / callback line shape**, renderer-agnostic:

```python
def scenario_panel(icon, act_label, title, lines, accent, icon_scale=1.3):
    """Icon on the left; act label + short title + 2-3 plain-language
    lines on the right. Fades in at scene start, fades out before the
    technical content begins."""
    ...

def callback_line(text, accent):
    """One boxed sentence, bottom of frame, tying the scene's content
    back to the running analogy. Fades in before the scene's final hold
    and stays up through it."""
    ...

def act_corner(act_number):
    """A small (≈40-60px) version of the current act's icon, fixed in a
    screen corner for the whole scene except the title card."""
    ...
```

**A persistent icon must be excluded from any "fade out everything" transition.** A scene that clears its screen between an internal Part 1 and Part 2 (`FadeOut(*self.mobjects)` in Manim, or unmounting a wrapper in Remotion) will also wipe the corner icon unless it's explicitly held back: `FadeOut(*[m for m in self.mobjects if m is not corner])`. This is an easy, silent regression — the icon just vanishes for the rest of the scene with no error.

---

## 5. QA — the step that catches real bugs, not a formality

A successful render (exit code 0, correct duration) proves timing sync, nothing about layout. On the real build, this exact step caught three genuine visual bugs that a clean render hid completely: two result boxes rendering exactly on top of each other, a two-column checklist overlapping mid-screen, and a two-line subtitle overflowing into a neighbouring box.

**Before calling a video done:**
1. Render at draft quality first (Remotion's fast preset, Manim's `-ql`) and smoke-test every scene, not just the first one — a bug can be scene-specific.
2. Extract actual frames — not just the first second — at several points per scene: right after the scenario panel, mid-technical-content, and right at the closing callback. Use `ffmpeg -ss <t> -vframes 1` (or render a short `--frames` range in Remotion) and **look at the image**, not just confirm the command exited 0.
3. Specifically check every scene transition and every place a persistent element (a corner icon, a caption) sits near other content — that's where the real bugs above were found, because the two elements were built independently and never checked against each other in the same frame.
4. Only after draft-quality QA passes on every scene, render at final quality.

---

## 6. Delivery — file size and the compression fix

Check the rendered file's size **before** attempting to send it, not after a failed delivery. A default Remotion + Kokoro pipeline can produce an unnecessarily bloated audio track — one real build shipped AAC at 317 kbps (roughly double what's audible as a difference for spoken narration), pushing an otherwise-reasonable video over a 30 MB delivery limit for no perceptual gain.

Fix, if oversized:

```bash
ffmpeg -y -i input.mp4 -c:v libx264 -crf 24 -preset medium -c:a aac -b:a 128k output.mp4
```

`crf 24` is visually indistinguishable from source for mostly-static, UI-style content (boxes, text, simple icons) and shrinks the video track substantially; `128k` AAC is standard for spoken narration. Re-verify duration and that audio/video are both still present after re-encoding — never assume a compression pass preserved sync.

---

## 7. Environment traps specific to this pipeline

Worth stating once so a future session doesn't rediscover these from scratch, in a sandboxed/proxied environment:

- **GitHub release assets are reachable through a restrictive egress proxy; Hugging Face often is not.** If a TTS/model download from HF fails, check whether the same model ships as a GitHub release instead.
- **`apt-get install ffmpeg` can fail on a broken mirror; `pip install imageio-ffmpeg` bundles a static binary** that can be symlinked to `/usr/local/bin/ffmpeg` as a reliable fallback.
- **Manim can hit a legacy-setuptools conflict on an old system Python** (an `AttributeError: install_layout` from a dependency's `setup.py`). An isolated venv with a fresh `pip`/`setuptools` sidesteps it cleanly.
- **A sandboxed environment's default headless Chrome download can be network-blocked for Remotion.** If a pre-installed Playwright Chromium exists on the box (check `/opt/pw-browsers/` or similar), point Remotion at it directly and force the modern headless protocol, since a full modern Chrome binary no longer supports the legacy headless mode Remotion's default flow expects:
  ```bash
  npx remotion render <entry> <Composition> <out> \
    --browser-executable=/path/to/chrome \
    --chrome-mode=chrome-for-testing
  ```
- **A Remotion composition's registered ID may not match its component's file/export name** — check the actual `<Composition id="...">` registration rather than guessing from the filename when a render call reports "could not find composition."

---

## 8. Things that go wrong

**Treating "video" as a faster way to make a page.** It isn't — narration pacing, the running-analogy device, and proportional visual pacing are all *video-specific* problems with no page-mode equivalent. Read this whole file, not just the page-mode sections.

**A second (or third) analogy per topic, "because it fits better here."** It doesn't read as better-fitting to a viewer — it reads as the video losing its thread. Extend the existing scenario into a new act (§3c) before introducing an unrelated one.

**Timing a scene's animations against the CURRENT draft of the script.** The moment the script text changes — and it will, once jargon definitions and scenario callbacks are added — a hand-tuned animation sequence goes stale and leaves a long dead hold at the end. Use `hold_until` fractions (§4), never a fixed-second guess, for anything meant to fill "the rest of the scene."

**Skipping frame-level QA because the render exited cleanly.** A clean exit proves the render pipeline works; it says nothing about whether two elements collide in the same frame. Three real bugs were caught this way on one build (§5) — always do it.

**Sending a video without checking its file size first.** A delivery-limit failure after the whole render pipeline has already run is a wasted round trip; check the size and pre-emptively compress (§6) before attempting to send.

**Assuming a jargon term was defined because it's on screen.** A caption chip is not the same as the spoken narration actually explaining the term in plain language — check the *script text* for the plain-language sentence, not just the visual layout.
