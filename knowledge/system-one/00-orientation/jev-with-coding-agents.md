---
title: Jev With Coding Agents
kind: playbook
source: Introduction > Jev with coding agents
source_url: https://docs.typesafe.ai/introduction/coding-agents
tags: [agent-tooling, system-one]
topics: [topic-agent-integration, topic-model-selection]
---
# Jev With Coding Agents
> Jev is NOT a drop-in LLM for Claude Code/Cursor/etc. Use your coding agent to write code that calls Jev; install the TypeSafe agent skill for correct integrations.

## What it is / How it works
- Jev is **not** a drop-in replacement for the LLM behind Claude Code, Cursor, opencode, Copilot, Muse Spark, Grok Bot or similar. Use the coding agent as usual to write code that uses Jev to make decisions.
- Jev **does not**: generate text, write code, hold a conversation, stream text, call tools, edit files from natural-language instructions. There is **no `model: "jev-latest"` setting** that turns a coding agent into a Jev-powered agent.
- Jev **does**: take a [[state]] + typed [[primitives-overview|questions]] and return a `choice` (+ per-option probabilities), a `score` on your rubric, or a `noul` (0–1) for a true/false statement.

## When to use / when NOT to use
Intent -> action table (source):
| You wanted to... | Do this |
| - | - |
| Make your coding agent better at writing code that uses TypeSafe | Install the TypeSafe agent skill ([[typesafe-agent-skill]]): gives Claude Code, Codex and others full context on Jev API, primitives, patterns |
| Use Jev inside an app/agent you're building (routing, classification, scoring, guardrails, structured decisions) | [[quickstart]], then [[how-to-build-with-system-one]] and [[patterns-overview]] (e.g. [[confidence-gated-routing]], [[intent-routing]]) |
| Replace/swap the model powering a coding agent | **Not what Jev is for.** Keep an LLM-based coding agent; use Jev separately where the product needs a fast, calibrated, structured decision |
| Try Jev before writing code | Playground (console.typesafe.ai/playground): paste text as state, add questions |

### When Jev is worth reaching for (inside an app/agent)
- Route a request to one of a fixed set of destinations and know how confident the routing is.
- Score something on a rubric (urgency, quality, risk) and branch on the number.
- Check whether a statement is true of a document/message/record before taking an action.
- Replace a fragile prompt that asks an LLM to "return JSON" with a call that returns typed values by construction.

## Worked example(s)
None here; see [[quickstart]] for the "Vibe it" coding-agent prompt and install commands.

## Numbers & limits
None.

## Gotchas
- Searching for a "Jev as the model for my coding agent" setting is a dead end; the docs say explicitly there is none.
- Coding agents rely on streaming/tool-calling LLMs; Jev solves a different problem.

## Related
[[jev-introduction]] · [[system-one-model-category]] · [[quickstart]] · [[typesafe-agent-skill]] · [[jev-mcp-server]] · [[patterns-overview]] · [[topic-agent-integration]]
