# Claude Code output styles — install, switch, and choose

How to make Claude Code's prose readable, how to switch styles back and forth,
and which style to reach for. Relevant to this repo because most of the work here
is *reading* generated output — extraction checks, synthesis reviews, learning
packs — where dense default prose costs real time.

> **The thing everyone gets wrong first:** an output style is part of the system
> prompt, and Claude Code reads the system prompt **once at session start**.
> Changing the style does nothing to the conversation you're in until you run
> `/clear` or open a new session.

## 1. What an output style is

A markdown file appended to Claude Code's system prompt. It changes **how Claude
responds** — role, tone, format. It does not change what Claude knows, and it
does not make answers more correct.

Reach for one when you keep re-prompting for the same voice every turn. For facts
about the project itself, use `CLAUDE.md` instead — different mechanism, different
purpose.

Styles apply to the **main conversation only**. Subagents run their own system
prompt and ignore the style; a fork inherits the parent's and keeps it. Worth
knowing here, since a lot of this repo's pipelines run through subagents
(`ben-dicken`, `justin-sung`, `vutr`, …) whose voices are set by their own agent
definitions and will not follow your style.

## 2. Switching back and forth

### Option A — the picker

1. Run `/config`, select **Output style**.
2. Pick a style.
3. Run `/clear` or start a new session. *Until you do, nothing changes.*

Your choice is saved to `.claude/settings.local.json` in the current project.

Note that `/config` is an interactive terminal dialog — it does not open in every
harness (the desktop and web apps, for example). Use Option B there.

### Option B — edit the setting directly

```json
{
  "outputStyle": "ELI5"
}
```

| Scope | File | Use for |
|---|---|---|
| This project only | `.claude/settings.local.json` | Per-repo styles — the usual choice |
| Project, shared | `.claude/settings.json` | Committed; applies to everyone |
| Everywhere | `~/.claude/settings.json` | Your global default |

Use `"Default"` to go back to stock behaviour.

Because the setting is per-project, different repos hold different styles
simultaneously, and switching one does not disturb another. An unfamiliar
codebase can sit on `Explanatory` while a familiar one stays terse.

### `/output-style` no longer exists

Deprecated in v2.1.73, removed in v2.1.91. `/config` or the `outputStyle` setting
are the only routes now.

## 3. Built-in styles

| Style | What it does | Reach for it when |
|---|---|---|
| **Default** | The stock software-engineering system prompt. | You already know the domain. |
| **Proactive** | Executes immediately, makes reasonable assumptions, prefers action over planning. Stronger than auto mode, but permission prompts still fire. | You trust the direction and want fewer check-ins. |
| **Explanatory** | Adds educational "Insights" while working — architecture, codebase patterns, why this choice. | A repo you don't know yet. |
| **Learning** | Shares insights *and* leaves `TODO(human)` markers for you to implement. | You're deliberately practising. |

Explanatory and Learning produce longer responses by design, so they cost more
output tokens. Any custom style raises input tokens too, though prompt caching
absorbs most of that after the first request in a session.

## 4. Creating a custom style

Drop a markdown file in one of these. The filename becomes the style name unless
frontmatter sets `name`.

| Level | Directory |
|---|---|
| User (all projects) | `~/.claude/output-styles/` |
| Project | `.claude/output-styles/` |
| Managed policy | `.claude/output-styles/` in the managed settings directory |

### Frontmatter

| Field | Purpose | Default |
|---|---|---|
| `name` | Style name, if not the filename | filename |
| `description` | Shown in the `/config` picker | none |
| `keep-coding-instructions` | Keep Claude Code's built-in engineering instructions (scoping, comments, verification) | `false` |
| `force-for-plugin` | Plugin styles only: apply automatically when the plugin is enabled | `false` |

**Set `keep-coding-instructions: true` for any style used while coding.** Leave it
out and you drop Claude Code's engineering instructions entirely — correct for a
writing assistant, wrong for anything touching a repo.

## 5. Two styles worth having

### ELI5

Optimises for **your energy budget**. Source: Ray Amjad, *"Opus 5 Is Exhausting.
Anthropic Reveals The Fix."* (2026-08-05).

```markdown
---
name: ELI5
description: keep it simple pls
keep-coding-instructions: true
---

It's been a long day and my brain is fried, talk to me like I'm 5.

Small words, short sentences, short paragraphs. If you have to use
a big word, explain it right after. Only return what's actually necessary.

Just tell me what you did, did it work, what do I do now.

If I have to decide something: 2 options max, the context I need to pick fast,
and which one you'd go with.

Keep paths and commands exact. I have no brain cells left for the rest.
```

### STE100

Optimises for **zero ambiguity**, not brevity. Based on ASD-STE100, the aerospace
*Simplified Technical English* standard for maintenance manuals: ~900 approved
words, one meaning per word, active voice, no metaphor, short sentences.

```markdown
---
name: STE100
description: Simplified Technical English — plain, unambiguous, procedural
keep-coding-instructions: true
---

Write in Simplified Technical English (ASD-STE100).

Use one meaning per word. Do not use a word as both a noun and a verb.
Use active voice. Use present tense. Write short sentences, maximum 20 words.
Use no more than three nouns in a row.

Use the plain word, not the technical synonym, when both are correct:
"use" not "leverage", "start" not "spin up", "cause" not "drive".
Keep real technical terms exact: file paths, function names, commands, flags.

Do not use metaphor, analogy, or figurative language.
Do not use synonyms for variety. Repeat the same word for the same thing.

Write actions as numbered steps. One action per step.
State the result of each action.

State facts and uncertainty separately. If you did not verify something, say so.
```

## 6. Which one, when

| Style | Optimises for | Best for | Cost |
|---|---|---|---|
| Default | Information density | Domains you know | Jargon load; you re-read to parse |
| ELI5 | Your energy | End of day, triage, "did it work?" | Drops nuance — bad when the nuance *is* the answer |
| STE100 | Zero ambiguity | Runbooks, incidents, procedures you'll execute | Stilted in conversation |
| Explanatory | Your understanding | New repo | Long; noise once you know it |
| Learning | Your skill | Practice | Slow; wrong for shipping |
| Proactive | Momentum | Clear direction, low ambiguity | Assumes rather than asks |

**ELI5 vs STE100 is the real choice** — both fight the same problem from opposite
ends. ELI5 cuts cognitive load: short words, decisions pre-narrowed, permission to
skim. STE100 cuts ambiguity: one meaning per word, numbered steps, no metaphor.
It is not shorter and not conceptually simpler — just impossible to misread.

They diverge on hard content. Ask about a subtle piece of logic and ELI5 will
simplify it into a clean answer that quietly drops the distinction that *was* the
bug. STE100 keeps every distinction and states them flatly.

**Rule of thumb:** ELI5 when you want a verdict. STE100 when you're about to
execute something. Default when you already know the domain.

> **None of these make Claude more correct.** They shape prose only. ELI5's
> confident two-option framing can make a shaky answer feel more settled than it
> is — worth remembering, because you'll be using it exactly when you're tired.

### A caution specific to this repo

The verification loops here (`docs/LEARNING_PACK_VERIFICATION_WORKFLOW.md`,
`docs/CHECK-EXTRACTION-PILOT-2026-07-29.md`) grade content on *accuracy and
coverage*. Do not run those under ELI5. A style that is instructed to return "only
what's actually necessary" and cap decisions at two options is actively wrong for
a pass whose job is to surface everything that is missing.

## 7. Finding your own style

1. When output annoys you, `/branch` off that conversation so you keep the context.
2. Ask Claude to rewrite that same output in ~5 different styles.
3. Pick the one you actually understood; ask Claude to turn it into a style file.
4. Adjust over time — if answers start feeling too thin, raise the technical level.

Styles are not set-once. Anthropic's own team reportedly swaps them by project, by
task, and by how tired they are.

## Sources

- <https://code.claude.com/docs/en/output-styles> — canonical reference for the
  settings key, file locations, frontmatter, and built-ins.
- Ray Amjad, *"Opus 5 Is Exhausting. Anthropic Reveals The Fix."*, 2026-08-05 —
  <https://youtu.be/szjakRcw7V0>. Source of the ELI5 style and the branch-and-compare
  technique. Note the video says "exploratory"; the real style name is
  **Explanatory**, and it predates the `/output-style` removal.
