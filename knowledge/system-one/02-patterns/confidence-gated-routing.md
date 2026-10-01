---
title: Confidence Gated Routing
kind: pattern
source: Patterns > Confidence-gated routing
source_url: https://docs.typesafe.ai/patterns/confidence-routing
tags: [patterns, confidence, routing]
topics: [topic-calibration, topic-routing]
---
# Confidence-Gated Routing
> The answer says WHAT; confidence says WHETHER to act. Set per-action thresholds by risk, escalate to a human or ask for confirmation in the middle band.

## What it is / How it works
- Confidence ([[confidence]]) is a second decision axis next to the answer itself. Being intentional about gating on it yields systems that are both reliable and safe.
- Per-action thresholds reflect the **consequence of acting on a wrong classification**.

## When to use / when NOT to use
- Use whenever actions differ in risk (read-only vs money-moving).
- Interpret low confidence in the context of the system and stakes ([[intent-routing]] repeats this for Score confidence).

## Worked example — voice banking commands
One request: command + a Choice `intent` question -> intent answer + confidence. (Question definition is a rendered component, not captured.)
Decision logic (diagram + code):
| Condition | Action |
| - | - |
| confidence < 0.6 (any intent) | route to a support agent (human) |
| `check_balance`, confidence >= 0.6 | show the balance (low stakes; worst case user hears the balance read out) |
| `approve_transfer`, 0.6 <= confidence <= 0.85 | ask the user to confirm: "Just to confirm: you would like to approve this transfer, is that correct?" |
| `approve_transfer`, confidence > 0.85 | approve the transfer automatically |
| any other intent | route to a support agent |
```python
action = response.answers["intent"]
if action.confidence < 0.6: route_to_support_agent(account_id)
elif action.choice == "check_balance": show_balance(account_id)
elif action.choice == "approve_transfer":
    if action.confidence > 0.85: approve_transfer(account_id)
    else: ask_user_to_confirm("Just to confirm: ...")
else: route_to_support_agent(account_id)
```
Rationale (source): the **0.6 floor** catches anything the model is genuinely uncertain about; above it each action type has its own threshold. Transfers need very high confidence (>0.85), otherwise the system asks the user to confirm.

## Numbers & limits
| Threshold | Meaning |
| - | - |
| 0.6 | global floor; below -> human |
| 0.85 | auto-approve line for high-stakes `approve_transfer` (strictly greater than; exactly 0.85 falls to confirm per the code) |
All illustrative; calibrate on your data by plotting confidence vs accuracy ([[how-to-build-with-system-one]] step 8).

## Gotchas
- Thresholds are per action, not global; a three-way outcome (act / confirm / escalate) beats a binary gate for risky actions.
- Don't transfer a threshold across question types (Noul vs Choice): [[jev-1-13-jaggedness]] #8.
- Confidence is only returned for Choice and Score ([[jev-introduction]]).

## Related
[[patterns-overview]] · [[confidence]] · [[intent-routing]] · [[cb-classification-using-confidence]] · [[how-to-build-with-system-one]] · [[topic-calibration]] · [[topic-routing]]
