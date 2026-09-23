---
name: learn-by-doing
description: Use when the user wants to learn or practice a Udemy Vault course by doing rather than reading notes — asks for hands-on missions, labs, exercises or a course project from a course, reports finishing a mission step, asks where they are in their missions, or invokes /learn-by-doing. Not for study notes (use /deep-notes).
trigger: /learn-by-doing
---

# /learn-by-doing

The owner learns by building. You plan, coach, and check. You never build it for them.

## Commands

```
/learn-by-doing <course> map      # course project + missions + lecture coverage + Mission 0
/learn-by-doing <course> next     # build the next mission, give the first step
/learn-by-doing <course> done     # owner reports; ask for proof; grade; log
/learn-by-doing <course> status   # progress
```

`<course>` = folder name under `courses/` in the vault, or a fuzzy title. Match it against `index.yaml` `courses:`. If more than one course matches, ask.

## Paths

- Vault: `$UDEMY_VAULT_DIR`, otherwise `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Udemy Vault`.
- Section notes: `courses/<course>/<N>-<slug>.md`. They list lectures as `[[lectures/<course>/<stem>|Title]]`.
- Lectures: `lectures/<course>/<stem>.md`, with a `## Transcript` section in `[HH:MM:SS]` per-minute blocks.
- Practice: `practice/<course>/00-map.md`, `00-limits.md`, `00-log.md`, `NN-<slug>.md`.
- Checks (run from the repo root):
  ```bash
  python3 scripts/learn_by_doing.py check-map <course>
  python3 scripts/learn_by_doing.py check-quirks practice/<course>/NN-<slug>.md
  python3 scripts/learn_by_doing.py status <course>
  ```

## Hard rules

1. **The owner builds.** Each step gives a goal and a "done when" rule. Never a copy-paste solution. Give hints only when asked, smallest hint first.
2. **Every step has a where tag:**
   | Tag | Runs on | Needs |
   |---|---|---|
   | `[AWS]` | company dev AWS account, office VPN. You cannot see it | cost note, cleanup, proof the owner pastes |
   | `[LOCAL]` | owner's Mac (Docker if a server is needed) | free. You may check files or run their tests yourself, read-only. **Say so first.** |
   | `[TRIAL]` | owner's personal Snowflake trial | cost note (credits), XS warehouse, auto-suspend on, proof the owner pastes |
   Course defaults: AWS courses → `[AWS]`. dbt, DuckDB, Spark, Kafka, Iceberg → `[LOCAL]`. Snowflake → `[TRIAL]`. A step can override the default (DuckDB reading S3 = `[AWS]`).
3. **Every `[AWS]` step uses the company limits in `00-limits.md`.** Use only the IAM roles listed there. **Never write a "create an IAM role" step.** If a service needs a role that isn't listed, say so and turn it into a question for the owner's platform team. Use the allowed region only. Put the required tags and the name prefix on every resource.
4. **Never ask for** access keys, secret keys, passwords, tokens, session cookies, or full ARNs with account IDs. Tell the owner to replace account IDs with `123456789012`. If they paste a secret anyway, tell them to rotate it, and never repeat it.
5. **Every `[AWS]` and `[TRIAL]` step has a cost note and a cleanup.** A mission is not `done` until the cleanup is proven.
6. **Quote quirks word for word.** Every quote must pass `check-quirks`. If one fails, copy the exact transcript text or drop the quirk. Never loosen a quote just to make it pass.
7. **Skip nothing.** Every lecture appears in the map exactly once, and `check-map` must pass.
8. **Obsidian tables:** inside a table cell, write a wikilink alias as `[[target\|Title]]`. A bare `|` breaks the table.
9. Edit only `practice/<course>/**` and the one link line in `courses/<course>.md`.

## `map`

1. Resolve the course. Read `courses/<course>.md` and every `courses/<course>/*.md` section note, in order.
2. Read every lecture title. If a title doesn't say what the lecture teaches, skim its transcript.
3. Pick **one course project**: a realistic build that needs every section. A section that doesn't fit becomes a **side quest**. Side quests are still built and checked.
4. Number the missions: `00` is the limits mission, then one mission per section in course order (`01`, `02`, …). A section with only intro, outro or admin lectures can share a neighbouring mission. A section with more than ~25 lectures splits into several missions, one per service group, so each mission keeps 3-8 steps. A section note with no lectures (e.g. practice exams) gets no mission.
5. Label every lecture with one kind:
   - `build`: a step makes the owner do it.
   - `theory`: a quick "why" check.
   - `skip`: only for intros, outros, course admin, or "UI changed" notices. Always add a note saying why.
6. Write `00-map.md`, `00-limits.md`, and `00-log.md` from the templates below.
7. At the end of `courses/<course>.md`, add this line if it isn't there yet. A vault rebuild can remove it, so check on every command:
   `Practice: [[practice/<course>/00-map|Learn by doing]]`
8. Run `check-map`. Fix every error and re-run until it prints `OK`.
9. Tell the owner the project in two lines and the number of missions, and say that Mission 0 comes first.

### `00-map.md` template

```markdown
---
course: <course>
project: <one line>
---

# <Course title> — learn by doing

## Course project
<3-6 lines: what gets built end to end, and which section adds which piece.>

## Missions
- 00 · [[practice/<course>/00-limits|Mission 0 — your limits]]
- 01 · [[practice/<course>/01-<slug>|<title>]] — section <N> — adds <piece>
- 07 · [[practice/<course>/07-<slug>|<title>]] — section <N> — side quest

## Lecture coverage
| Lecture | Mission | Kind | Note |
|---|---|---|---|
| [[lectures/<course>/<stem>\|<title>]] | 01 | build | |
| [[lectures/<course>/<stem>\|<title>]] | 01 | skip | section intro |
```

### `00-limits.md` template (Mission 0)

```markdown
---
course: <course>
mission: "00"
status: not-started
---

# Mission 0 — your limits

These checks only read. Nothing here costs money or creates anything.

## Steps
1. [AWS] Who am I? Run `aws sts get-caller-identity`. **Send:** the output, with the account ID blanked out.
2. [AWS] Allowed region(s). **Send:** the list of regions your company allows.
3. [AWS] Roles you may use. Run `aws iam list-roles --query "Roles[].RoleName"`. If that's denied, ask your platform team. **Send:** the names of the roles you're allowed to pass to Glue, Lambda, EMR, Redshift, and so on.
4. [AWS] Required tags and name prefix. **Send:** the tag keys and the prefix.
5. [AWS] Guard rails. **Send:** anything you already know is blocked, e.g. public S3 buckets, the Billing console, QuickSight, Bedrock, certain services or instance sizes.
6. [TRIAL] Snowflake trial (Snowflake courses only). **Send:** the trial end date and the credits left.
7. [LOCAL] Tools. Run `docker --version; python3 --version`, plus the course's own tools (`dbt --version`, `duckdb --version`, …). **Send:** the output.

Drop the steps that don't apply to the course (no [AWS] steps for a local-only course, no [TRIAL] step outside Snowflake).

## Your limits
- Region:
- Roles allowed:
- Required tags:
- Name prefix:
- Known blocks:
- Snowflake trial ends:
- Local tools:

## Your log
```

Fill in `## Your limits` from the owner's answers, then set `status: done`.

### `00-log.md`

Append-only: one line per event, newest last. Never rewrite old lines.
```markdown
# Log — <course>

- 2026-09-23 — map built: 17 missions, 317 lectures (check-map OK)
- 2026-09-24 — Mission 00 done
- 2026-09-25 — Mission 01 built (check-quirks OK)
- 2026-09-26 — Mission 01 step 2 pass
- 2026-09-27 — Mission 01 cleanup verified — done
```

## `next`

1. If `00-limits.md` is not `done`, do Mission 0 first.
2. Run `status` and take the lowest mission that isn't `done`. If that mission is already `in-progress`, show its next open step and stop there.
3. **Read every transcript for that mission's lectures in full.** No skimming. For a big section, run Sonnet subagents in parallel, about 10 lectures each. Ask each one to return, per lecture:
   - what can be built
   - the key facts
   - **quirk candidates, copied word for word with their `[HH:MM:SS]`**

   Quirks to hunt for: "watch out", "be careful", "gotcha", "common mistake", "exam", "remember", limits and numbers, defaults, "new", "changed", "deprecated", cost warnings, "don't".
4. Write `NN-<slug>.md` from the template below. Where you can, turn a quirk into a step that lets the owner **see it happen**.
5. Run `check-quirks`. Fix every error and re-run until it prints `OK`.
6. Set `status: in-progress`, add a line to `00-log.md`, and give the owner Step 1 only.

### Mission template

```markdown
---
course: <course>
mission: "NN"
section: <section title>
where: AWS | LOCAL | TRIAL
status: not-started
---

# Mission NN — <title>

Map: [[practice/<course>/00-map|Course map]] · Limits: [[practice/<course>/00-limits|Your limits]]

## Goal
<What you build, and where it plugs into the course project.>

## Steps
### 1. <name> [AWS]
- Teaches: [[lectures/<course>/<stem>|<title>]]
- Do: <the goal, not the code. Use the prefix, tags, region, and allowed role from your limits.>
- Done when: <a rule you can check, e.g. "the crawler made 1 table with 3 partitions">
- Cost: <what gets billed, a rough size, and how to keep it small>
- Send: <exact command(s), e.g. `aws glue get-table --database-name <prefix>_raw --name events --query "Table.PartitionKeys"`>

## Quirks
- "<verbatim quote>" — [[lectures/<course>/<stem>|<title>]] @ HH:MM:SS — <what it means for you>

## Theory checks
- [[lectures/<course>/<stem>|<title>]]: <why-question>

## Cleanup
- Delete: <every resource this mission made>
- Send: <a list or describe command that shows it's gone>

## Your log
```

## `done`

1. The owner says which step(s) they finished. If they haven't sent the proof the step asks for, ask for exactly that and nothing more.
2. Check the proof against the step's **Done when**, and give one verdict:
   - **pass**
   - **almost**: name the one fix
   - **redo**: say what went wrong, and name the lecture (+ timestamp) that covers it
3. Theory checks: the owner answers in their own words. Grade the answer against the lecture text. If they miss, name the lecture and timestamp to rewatch.
4. Under `## Your log`, add the date, the step, a short summary of the proof (never secrets), and the verdict. Add one line to `00-log.md`.
5. Give the next open step. When every step, every theory check, and the cleanup has passed, set `status: done`, log it, and offer `next`.
6. For `[LOCAL]` steps you may check the result yourself. Say what you'll run first, and only read.

## `status`

Run `status` and print its output as is. Then give the current mission's next open step in one line.

## Common mistakes

| Mistake | Fix |
|---|---|
| Writing the solution code into a step | State the goal and the "done when" rule. Hints only when asked. |
| A "create an IAM role" step in the company account | Use a role from `00-limits.md`, or turn it into a platform-team question. |
| Quirk paraphrased inside quotes | Quotes mean exact transcript text. Put paraphrase after the timestamp. |
| `\|` missing in a coverage-table link | The cells shift: `check-map` reports `bad kind '<mission>'` and `mission '<kind>' not in ## Missions`. Escape the pipe. |
| Mission marked done with resources still running | Cleanup proof comes first. No proof, no `done`. |
| Asking for a full `get-caller-identity` or ARN | Ask for it with the account ID blanked. |
