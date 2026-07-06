---
name: vault-ask
description: Answer a question by searching the captured Obsidian vaults (AI & Development, Stock Market/SOIC, Substack) and having a costlier model synthesize the final answer from only the notes routing surfaced. Use when the user asks a knowledge question that this repo's captured content might answer, or explicitly invokes /vault-ask.
trigger: /vault-ask
---

# Skill: Vault Ask

**Trigger:** `/vault-ask <question>`

This is the "presentation" half of the index + log + cross-links routing
pattern (see `CLAUDE.md` → Key conventions, and the Fable 5 / Karpathy deep
dive it came from). The insight: a personal knowledge base isn't valuable
because it was built with a fancy model — it's valuable because of the
routing that finds the right note fast. The expensive model only earns its
cost at the very end, turning what routing found into an answer that lands
for a human. **Do not skip straight to a costly model** — that defeats the
whole point of having cheap routing.

## Step 1 — Pick the vault(s)

| Vault | Env var (default) | Domain |
|-------|-------------------|--------|
| `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/AI & Development` | `MEDIA_VAULT_DIR` | YouTube + web + Instagram (AI/automation/dev content) |
| `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Stock Market Vault` | `SOIC_VAULT_DIR` | SOIC/Learnyst lesson transcripts |
| `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Substack` | `SUBSTACK_VAULT_DIR` | Substack posts |

Infer from the question's subject matter which vault(s) apply (AI/automation/
tooling → AI & Development; investing/stocks → Stock Market Vault; a named
newsletter/author → Substack). If genuinely ambiguous, search all three
rather than asking — routing is cheap.

## Step 2 — Route (cheap, mechanical — do this yourself, no subagent, no costly model)

Routing means using the vault's own index + cross-links, not reading
everything:

1. Check `Home.md` for the topic/source MOC (map-of-content) structure.
2. `grep -il` the question's key nouns/terms across `topics/*.md` — these are
   the cross-link hubs where every source that touched a topic is already
   collected in one file.
3. Also check `sources/*.md` (or `youtube/<channel>/`, `Substack/posts/<handle>/`)
   for source-specific MOCs if the question names a creator/publication.
4. From matched topic/source notes, follow their `[[wikilinks]]` to the
   individual note files they roll up (video/post notes) — these are the
   actual content to hand to the presenter.
5. Cap the routed set to roughly 6–12 note files. If a topic note alone
   already answers it, don't pull every linked note too.

If nothing matches, say so plainly and stop — do not invoke a costly model
to answer from nothing.

## Step 3 — Present (costly — dispatch a subagent on the most capable model)

Dispatch one `Agent` call with `model: "opus"` (fall back to the session's
top-tier model if opus isn't available). Give it:

- The user's original question, verbatim.
- The absolute paths of every note routing surfaced in Step 2 (it reads them
  itself — don't paste their contents into the prompt).
- An explicit instruction set:
  - Answer **only** from what these notes actually say — never fill gaps
    from general knowledge.
  - Cite the source note (title + creator) for every non-trivial claim.
  - If the routed notes don't fully answer the question, say what's missing
    rather than guessing.
  - Write for a curious beginner: plain language before jargon, define terms
    on first use — this is the "presenting it so it lands" step, not a raw
    transcript dump.

## Step 4 — Return

Relay the subagent's answer to the user, plus a short "sources" line listing
which notes it drew from. If routing found candidates in more than one
vault, either merge them into one presenter dispatch or run one dispatch per
vault and say which vault each part of the answer came from.

## Why split it this way

- Step 2 (routing) is pattern-matching over an index — a cheap/no-model
  operation is enough, and doing it first keeps Step 3's input small and
  relevant instead of dumping the whole vault into a costly model's context.
- Step 3 (presentation) is where quality of explanation matters most, so
  it's the one step worth paying for a stronger model.
- This mirrors `.claude/agents/nate-herk.md` / `jack-roberts.md`: those
  personas are themselves grounded-answer generators over a pre-synthesized
  reference file. `/vault-ask` generalizes the same shape to any vault
  content, not just persona-covered creators.
