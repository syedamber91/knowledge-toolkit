"""Rule extraction — the first LLM stage.

The model never copies text. It returns ``start``/``end`` character offsets
into the raw ``body_text``; the verifier slices the corpus itself. This makes
fabrication impossible by construction and stops the model from silently
repairing ASR while transcribing.

``llm`` is injected so the stage is testable offline with a canned queue.
"""

from __future__ import annotations

import json
from typing import Callable, Dict, List, Optional

from .corpus import resolve_timestamp
from .models import Candidate, Citation, LessonRecord, Rule, Span

PROMPT_TEMPLATE = """You are extracting investing RULES from a lecture transcript.

The transcript below is annotated with character offsets. Every 100 characters a
marker of the form <<offset:N>> gives the offset of the following character.

CRITICAL: do not quote or retype any text. Identify the exact character range
that states the rule and return its `start` and `end` offsets. The system
slices the transcript itself.

Choose `rule_key` from this controlled vocabulary only. If the rule fits none
of them, return null — do not invent a key:
{vocabulary}

Return JSON only:
{{"rules": [{{"tier": "graded"|"knockout", "kind": "threshold"|"range"|"boolean",
  "stage": "screen"|"sector"|"valuation"|"exit",
  "rule_key": "<from the vocabulary above, or null>",
  "operator": "gte"|"lte"|null, "value": <number|null>,
  "value_min": <number|null>, "value_max": <number|null>,
  "unit": "<string|null>", "conviction": "absolute"|"strong"|"preference",
  "start": <int>, "end": <int>}}]}}

Return an empty list if the passage states no rule. Prefer returning nothing
over guessing. The span you return must literally contain the number and the
comparative wording.

Report the values you actually see. A single cutoff has `value` and an
`operator`; a band has `value_min` and `value_max` and no operator; a rule
with no number at all has `kind` "boolean". The system derives `kind` from
which of those you fill in, and discards anything it cannot reconcile.

TRANSCRIPT:
{annotated}
"""


def _annotate(text: str, start: int, every: int = 100) -> str:
    parts = []
    for i in range(0, len(text), every):
        parts.append("<<offset:%d>>%s" % (start + i, text[i:i + every]))
    return "".join(parts)


def build_extract_prompt(
    lesson: LessonRecord,
    cand: Candidate,
    rule_keys: Optional[List[str]] = None,
) -> str:
    chunk = lesson.body_text[cand.span.start:cand.span.end]
    keys = rule_keys or []
    vocabulary = "\n".join("- " + k for k in keys) if keys else "(none yet — return null)"
    return PROMPT_TEMPLATE.format(
        annotated=_annotate(chunk, cand.span.start),
        vocabulary=vocabulary,
    )


def _value_shape(
    value: object, vmin: object, vmax: object,
    operator: object, raw_kind: object,
) -> Optional[Dict[str, object]]:
    """Reconcile the model's `kind` with the values it actually returned.

    Returns the `kind`/`operator`/`value`/`value_range` fields to build the
    rule with, or ``None`` when the two cannot be made consistent -- in
    which case the rule is dropped at extraction rather than allowed to
    fail downstream for a reason that misdescribes the fault.

    The three self-consistent shapes, and nothing else:

    * both bounds present  -> ``kind="range"``, ``operator=None``. A band
      ("between 40 and 50 times earnings") has no single directional sense,
      and verify.py's range exemption keys on exactly this pairing.
    * a scalar value       -> ``kind="threshold"`` and an operator is
      REQUIRED. A threshold with no comparative direction cannot be
      verified: "18% ROC" alone does not say floor or ceiling.
    * neither              -> only legal if the model actually said
      ``kind="boolean"``. A `threshold` with no number is malformed, not a
      boolean rule, so it is dropped instead of silently reclassified.
    """
    if vmin is not None and vmax is not None:
        return {"kind": "range", "operator": None,
                "value_range": {"min": vmin, "max": vmax}}
    if value is not None:
        if operator is None:
            return None
        return {"kind": "threshold", "operator": operator, "value": value}
    if raw_kind == "boolean":
        return {"kind": "boolean", "operator": None}
    return None


def extract_rules(
    lesson: LessonRecord,
    cand: Candidate,
    llm: Callable[[str], str],
    rule_keys: Optional[List[str]] = None,
) -> List[Rule]:
    allowed = set(rule_keys or [])
    try:
        payload = json.loads(llm(build_extract_prompt(lesson, cand, rule_keys)))
    except (ValueError, TypeError):
        return []

    if not isinstance(payload, dict):
        return []
    raw_rules = payload.get("rules")
    if not isinstance(raw_rules, list):
        return []

    out: List[Rule] = []
    for raw in raw_rules:
        try:
            start, end = int(raw["start"]), int(raw["end"])
        except (KeyError, TypeError, ValueError):
            continue
        if start < 0 or end > len(lesson.body_text) or end <= start:
            continue

        # Controlled vocabulary: an invented key is discarded, not accepted.
        key = raw.get("rule_key")
        if key not in allowed:
            key = None

        # `kind` is DERIVED from the value shape, never taken from the model.
        # The two used to be independent, so a model returning
        # {"kind": "threshold", "value_min": 40, "value_max": 50,
        #  "operator": null} for "between 40 and 50 times earnings" built a
        # rule whose bounds verified fine and which Gate 1 then killed with
        # "unhandled operator None" -- a schema-shape mismatch reported as an
        # operator fault, in rejected.jsonl, the file the spec designates as
        # the calibration signal and fabrication alarm. Deriving the shape
        # also removes one more routing decision from the model's control
        # (final-branch-review.md I4, and cf. C1).
        vmin, vmax = raw.get("value_min"), raw.get("value_max")
        value, operator = raw.get("value"), raw.get("operator")
        shape = _value_shape(value, vmin, vmax, operator, raw.get("kind"))
        if shape is None:
            continue           # cannot be made self-consistent: drop it

        fields = {
            "rule_key": key,
            "tier": raw.get("tier", "graded"),
            "stage": raw.get("stage", "screen"),
            "unit": raw.get("unit"),
            "conviction": raw.get("conviction", "preference"),
            "citations": [
                Citation(
                    lesson_id=lesson.lesson_id,
                    lesson_url=lesson.url,
                    timestamp=resolve_timestamp(lesson.body_text, start),
                    span=Span(start=start, end=end),
                    transcript_fidelity=lesson.transcript_fidelity,
                    text_hash=lesson.text_hash,
                )
            ],
        }
        fields.update(shape)

        try:
            out.append(Rule(**fields))
        except ValueError:
            # Covers pydantic's ValidationError too (it subclasses
            # ValueError), which is what an out-of-vocabulary `tier`,
            # `stage` or `conviction` from the model now raises. A rule the
            # model described with an enum value the schema does not
            # recognise is DROPPED, not published on a guessed default --
            # the whole point of closing those enums is that an
            # unrecognised value must not route past the gates.
            continue
    return out
