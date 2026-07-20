"""Rule extraction — the first LLM stage.

The model never copies text. It returns ``start``/``end`` character offsets
into the raw ``body_text``; the verifier slices the corpus itself. This makes
fabrication impossible by construction and stops the model from silently
repairing ASR while transcribing.

``llm`` is injected so the stage is testable offline with a canned queue.
"""

from __future__ import annotations

import json
from typing import Callable, List, Optional

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

    out: List[Rule] = []
    for raw in payload.get("rules", []) or []:
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

        fields = {
            "rule_key": key,
            "tier": raw.get("tier", "graded"),
            "kind": raw.get("kind", "threshold"),
            "stage": raw.get("stage", "screen"),
            "operator": raw.get("operator"),
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
        if raw.get("value") is not None:
            fields["value"] = raw["value"]
        elif raw.get("value_min") is not None and raw.get("value_max") is not None:
            fields["value_range"] = {"min": raw["value_min"], "max": raw["value_max"]}

        try:
            out.append(Rule(**fields))
        except ValueError:
            continue
    return out
