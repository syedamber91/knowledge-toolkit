# /learn-by-doing — learn a Udemy course by building, not reading

Date: 2026-09-23
Status: design approved in chat, awaiting spec review

## Why

`/deep-notes` turns lectures into study pages. Reading them does not make the
material stick. The owner wants to learn every topic and sub-topic of a course
by **doing**: one real project for the whole course, plus small hands-on steps
per section, with the instructor's quirks kept and checked.

## What the owner said (constraints)

- Source: transcripts already in the Udemy Vault
  (`~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Udemy Vault`,
  20 courses / 2,499 lectures; `index.yaml` + `courses/<slug>/<n>-<section>.md`
  list every lecture).
- AWS work runs in the **company dev AWS account**, on office VPN. Claude
  cannot see it. The owner builds, then reports; Claude asks for precise proof.
- Company account limits: **cannot create IAM roles**, **region locked**,
  **required tags / name prefix**.
- dbt, DuckDB, Spark, Kafka, Iceberg run **locally** on the owner's Mac (free).
- Snowflake runs on a **personal trial** account.
- Granularity: one **mission per course section**, all feeding **one course
  project**.
- Generic for any Udemy Vault course; pilot on
  *AWS Certified Data Engineer Associate 2026 - Hands On!* (17 sections, 317
  lectures).
- Missions and progress live **in the Udemy Vault**.

## Approach (chosen: map first, missions just-in-time)

1. `map` reads every lecture title (and skims transcripts where the title is
   unclear), picks the course project, and assigns every lecture to a mission.
   A script proves no lecture is missing. Cheap, done once.
2. `next` builds one full mission at a time from a **full read** of that
   section's transcripts.

Rejected: writing all missions up front (long wait before any doing), and
purely one-at-a-time (project drift, skipped sub-topics go unnoticed).

## Commands

```
/learn-by-doing <course> map      # course map + Mission 0 (limits)
/learn-by-doing <course> next     # build next mission, give first goal
/learn-by-doing <course> done     # owner reports; Claude asks for proof, grades
/learn-by-doing <course> status   # progress per section
```

`<course>` is the course slug (folder name under `courses/`) or a fuzzy title
match; ambiguous → ask.

## Where each step runs — the "where" tag

| Tag | Runs on | Cost | Proof |
|---|---|---|---|
| `[AWS]` | company dev account, office VPN | real money | owner pastes small command output / screenshot |
| `[LOCAL]` | owner's Mac (Docker if a server is needed) | free | Claude may check files / run tests itself, read-only, after asking |
| `[TRIAL]` | personal Snowflake trial | trial credits | owner pastes query result |

Course default: AWS courses → `[AWS]`; dbt, DuckDB, Spark, Kafka, Iceberg →
`[LOCAL]`; Snowflake → `[TRIAL]`. A step may override (e.g. DuckDB reading from
S3 is `[AWS]`).

## Vault files

```
Udemy Vault/practice/<course>/
  00-map.md       course project, mission list, lecture coverage table
  00-limits.md    region, allowed IAM roles, required tags + name prefix,
                  Snowflake trial end date, local tool versions
  00-log.md       append-only: mission built / passed / cleanup verified
  01-<slug>.md    one note per mission
  ...
```

The course note (`courses/<course>.md`) gets one line linking to
`practice/<course>/00-map`. Nothing else in the vault is edited.

This follows the repo's index + log + cross-links rule: `00-map.md` is the
index, `00-log.md` the append-only log, and every step/quirk wikilinks its
lecture.

### `00-map.md`

- **Course project** — one realistic build that needs every section. For the
  pilot, e.g. a clickstream pipeline: raw events in S3 → Glue catalog →
  transform → Athena/Redshift → orchestration → security → monitoring.
- **Missions** — numbered list, each with the section it covers and the piece
  of the project it adds. A section that does not fit the project becomes a
  **side quest** (still built, still checked, not forced into the pipeline).
- **Lecture coverage** — machine-read table, one row per lecture:

  ```
  | Lecture | Mission | Kind | Note |
  |---|---|---|---|
  | [[lectures/<course>/8-aws-glue-40356180|AWS Glue]] | 08 | build | |
  | [[lectures/<course>/8-intro-analytics-40332226|Intro: Analytics]] | 08 | skip | section intro |
  ```

  `Kind` is `build`, `theory`, or `skip`. `skip` is only for intro/outro/
  course-admin lectures and requires a `Note`.

### Mission 0 — limits (`00-limits.md`)

Built by `map`. Safe, read-only checks the owner runs once, e.g.
`aws sts get-caller-identity` (account ID blanked), allowed region, names of
IAM roles the owner may pass to services, required tags and name prefix,
Snowflake trial end date, local `docker`/`python`/`dbt` versions. Every later
mission reads this file and uses: existing roles only (**never a "create role"
step**), the allowed region, the tags + prefix on every resource.

### Mission note (`NN-<slug>.md`)

Frontmatter: `course`, `mission`, `section`, `status`
(`not-started | in-progress | done`), `where` default.

Body, in order:

1. **Goal** — what gets built and where it plugs into the course project.
2. **Steps** — 3-8 builds. Each step: where tag, lecture wikilink(s) it teaches,
   what to do (goal-level, not copy-paste code), **done when** rule, **cost
   note** (`[AWS]`/`[TRIAL]`), **proof to send**.
3. **Quirks** — every gotcha from the section's transcripts: "watch out",
   common mistakes, exam traps, limits/numbers, "this changed". Format:
   `- "<verbatim quote>" — [[lectures/...|Title]] @ HH:MM:SS` then one line on
   what it means. Where possible a quirk is turned into a step that makes the
   owner see it happen.
4. **Theory checks** — 2-3 "why" questions per `theory` lecture.
5. **Cleanup** — what to delete, and the proof it is gone (a `list`/`describe`
   showing absence). A mission is not `done` until cleanup passes.
6. **Your log** — owner's pasted proof + Claude's verdict per step.

## The `done` loop

1. Owner says which step(s) they finished.
2. Claude asks for the exact proof listed in the step, if not already given.
3. Claude checks it against the **done when** rule.
   Verdict: **pass**, **almost** (one named fix), **redo** (what went wrong).
4. Theory checks: owner answers in own words; Claude grades against the lecture
   text and names the lecture (+ timestamp) to rewatch on a miss.
5. Verdicts are written to the mission's log; milestones to `00-log.md`.
6. When all steps + cleanup pass: `status: done`, map rows count as practiced.

**Never asked for:** access keys, passwords, tokens, session cookies, full ARNs
with account IDs (owner blanks them). `[LOCAL]` checks are read-only and
announced first.

## Checks script — `scripts/learn_by_doing.py`

Deterministic, no LLM, stdlib + existing deps only.

- `check-map <course>` — expected set = every lecture wikilink in
  `courses/<course>/*.md` section notes; actual set = lecture links in the
  coverage table. Fails on: missing lecture, duplicate lecture, unknown lecture,
  bad `Kind`, `skip` without a note, mission number with no mission listed.
- `check-quirks <mission file>` — for each quoted quirk: the quote, normalized
  (case, whitespace, punctuation), must appear in the cited lecture's transcript
  within the minute block at the cited timestamp or the block either side
  (transcript blocks are per-minute). Fails on any miss, printing which.
- `status <course>` — per section: lectures in `done` missions / total, plus
  current mission.

Claude runs `check-map` after `map` and `check-quirks` after `next`; a failure
is fixed before the owner sees the note.

Tests: `tests/test_learn_by_doing.py` with a tiny fixture vault under
`tests/fixtures/learn_by_doing/` (2 sections, ~5 lectures). Cover each failure
case above plus pass cases, and `status` counts.

## Skill file

`.claude/skills/learn-by-doing/SKILL.md` — the commands, the mission template,
the where-tag rules, the `done` loop, the never-ask list, and when to run the
script. Written via the `writing-skills` skill.

## Out of scope

- Claude touching the company AWS account or Snowflake directly.
- Generating full solution code (steps are goals; hints only when asked).
- Editing lecture/course notes beyond the one link line.
- Missions for courses not yet in the Udemy Vault.

## Pilot success

On the AWS Data Engineer course: `check-map` passes with all 317 lectures
assigned; Mission 0 and Mission 1 built; Mission 1's quirks pass
`check-quirks`; the owner completes one step through the `done` loop and the
verdict lands in the log.
