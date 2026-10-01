---
title: Quickstart
kind: cookbook
source: Introduction > Quick start
source_url: https://docs.typesafe.ai/introduction/quickstart
tags: [api-sdk, system-one]
topics: [topic-agent-integration]
---
# Quickstart
> Four ways in: Playground, HTTP API (`POST /v1/systemone`), Python SDK, agent skill. Contains the canonical request and response shapes.

## What it is / How it works
Sample state used throughout: *"Hi, I've been trying to connect my Stripe account for 3 days and the integration keeps failing. I'm losing sales. Please help ASAP."*

### 1. Playground ("Try it")
Open console.typesafe.ai/playground, log in, paste text as state, add a question, e.g. Noul `"Does this message express urgency?"`:
```json
{ "urgency": { "type": "noul", "instructions": "Does this message express urgency?" } }
```
Then add Choice/Score/Noul questions together and see all results at once.

### 2. HTTP API ("Call it")
Get an API key at console.typesafe.ai/keys. Full reference: [[http-api-reference]].
```http
POST https://api.typesafe.ai/v1/systemone
Authorization: Bearer <API_KEY>
Content-Type: application/json
```
Minimal cURL body: `{"state": "...", "model": "jev-latest", "questions": {"urgency": {"type":"noul","instructions":"..."}}}` with header `Authorization: Bearer $TYPESAFE_API_KEY`.

**Request body (3 mixed questions):**
```json
{ "state": "<the Stripe message>", "model": "jev-latest",
  "questions": {
    "department": { "type": "choice", "instructions": "Which team should handle this",
      "criteria": { "billing": "Payment or subscription issues",
                    "technical": "Bugs or integration problems",
                    "sales": "Pricing or account questions" } },
    "frustration": { "type": "score", "instructions": "How frustrated the customer appears",
      "criteria": ["Calm, just stating facts","Frustrated but civil","Very angry, strong language"] },
    "is_urgent": { "type": "noul", "instructions": "The message conveys urgency or time-sensitivity" } } }
```
Choice `criteria` = object keyed by option name; Score `criteria` = ordered list (index = level, 0-based); Noul has only `instructions` here.

**Response body (as in source):**
| Field | Value |
| - | - |
| `model` | `jev-1.13.0` (the versioned ID that answered) |
| `answers.department` | type choice; `choice: "technical"`; `confidence: 0.78`; `probabilities`: technical 0.85, sales 0.0, billing 0.15 |
| `answers.frustration` | type score; `score: 1.0`; `confidence: 1.0`; `legend` {"0": "Calm, just stating facts", "1": "Frustrated but civil", "2": "Very angry, strong language"}; `probabilities` {0: 0.0, 1: 1.0, 2: 0.0} |
| `answers.is_urgent` | type noul; `noul: 1.0` (no confidence / probabilities field shown) |
| `usage` | `input_tokens: 392`, `output_tokens: 65` |
Observation (from the numbers): Choice confidence 0.78 is *not* the max probability (0.85) — confidence is a separate quantity; see [[confidence]].

### 3. Python SDK ("Code it")
- Requires **Python >= 3.10**. Install: `pip install typesafe-sdk` or `uv add typesafe-sdk`.
- Client reads `TYPESAFE_API_KEY` from env and calls `jev-latest` by default. More: [[sdk-overview]], [[sdk-python]].
```python
from typesafe_sdk import Choice, Noul, Score, TypeSafeClient
client = TypeSafeClient()
response = client.system_one(
    state=ticket,
    questions={
        "department": Choice(instructions="Which team should handle this",
            criteria={"billing": "Payment or subscription issues",
                      "technical": "Bugs or integration problems",
                      "sales": "Pricing or account questions"}),
        "frustration": Score(instructions="How frustrated the customer appears",
            criteria=["Calm, just stating facts","Frustrated but civil","Very angry, strong language"]),
        "is_urgent": Noul(instructions="The message conveys urgency or time-sensitivity"),
    })
print(response.answers["department"].choice)  # "technical"
print(response.answers["frustration"].score)  # 1.0
print(response.answers["is_urgent"].noul)     # 1.0
```

### 4. Agent skill ("Vibe it")
Install the TypeSafe skill ([[typesafe-agent-skill]]):
- **Claude Code:** `claude plugin marketplace add typesafe-ai/skills` then `claude plugin install typesafe@typesafe-ai`.
- **Other agents:** `npx skills add typesafe-ai/skills --skill typesafe-ai` (choose your agent when prompted; project-local by default; add `-g` for global).
- **Copy-paste prompt option:** tells the agent to install via one method only, notes SKILL.md at github.com/typesafe-ai/skills/blob/main/skills/typesafe-ai/SKILL.md (raw: raw.githubusercontent.com/typesafe-ai/skills/main/skills/typesafe-ai/SKILL.md), then use the skill on the project.
Example coding-agent prompt: build a simple CLI that uses the TypeSafe API to evaluate supplied documents on multiple dimensions; use the TypeSafe skill; ask me what kinds of documents and dimensions.

## When to use / when NOT to use
Playground = zero-code exploration; HTTP = any language; Python SDK = Python>=3.10 apps (JS SDK exists, see [[sdk-javascript]]); agent skill = let a coding agent write the integration. Jev can't replace the coding agent's own LLM ([[jev-with-coding-agents]]).

## Numbers & limits
| Item | Value |
| - | - |
| Endpoint | `https://api.typesafe.ai/v1/systemone` (POST) |
| Auth | `Authorization: Bearer <API_KEY>`; env `TYPESAFE_API_KEY` |
| Python | >= 3.10, package `typesafe-sdk` |
| Example usage | 392 input tokens, 65 output tokens (3 questions) |
| Default model | `jev-latest` (-> `jev-1.13.0`, see [[models-and-versions]]) |

## Gotchas
- Use one agent-skill install method only.
- `jev-latest` alias moves on new releases; log the response `model` ([[models-and-versions]]).

## Related
[[jev-introduction]] · [[http-api-reference]] · [[sdk-python]] · [[typesafe-agent-skill]] · [[models-and-versions]] · [[state]] · [[topic-agent-integration]]
