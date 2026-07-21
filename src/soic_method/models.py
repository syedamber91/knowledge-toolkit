"""Pydantic types shared across every pipeline stage.

Offsets (`Span`) always index into a lesson's RAW ``body_text`` — markers
included. Normalization is applied to a slice, never globally, so there is no
offset map to keep in sync.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field, model_validator

TIER_KNOCKOUT = "knockout"
TIER_GRADED = "graded"

TIERS = (TIER_KNOCKOUT, TIER_GRADED)
KINDS = ("threshold", "range", "boolean")
STAGES = ("screen", "sector", "valuation", "exit")
CONVICTIONS = ("absolute", "strong", "preference")
OPERATORS = ("gte", "lte", "gt", "lt", "eq")
STATUSES = ("draft", "active", "conflicted", "unbound", "needs_audio_check")
FIDELITIES = ("verbatim", "translated")


def _require_in(field: str, value: str, allowed: tuple) -> None:
    if value not in allowed:
        raise ValueError(
            "%s %r is not one of %s" % (field, value, list(allowed))
        )


class Span(BaseModel):
    start: int = Field(ge=0)
    end: int = Field(ge=0)

    @model_validator(mode="after")
    def _ordered(self) -> "Span":
        if self.end <= self.start:
            raise ValueError("span end must exceed start")
        return self


class Citation(BaseModel):
    lesson_id: str
    lesson_url: str
    timestamp: str                     # "HH:MM:SS", nearest preceding marker
    span: Span
    transcript_fidelity: str = "verbatim"
    text_hash: str = ""                # sha256 of the lesson body_text

    @model_validator(mode="after")
    def _known_fidelity(self) -> "Citation":
        _require_in("transcript_fidelity", self.transcript_fidelity, FIDELITIES)
        return self


class Binding(BaseModel):
    # Never default to "bound" — the stock_analyzer column inventory is unverified.
    source: Optional[str] = None
    table: Optional[str] = None
    expr: Optional[str] = None
    status: str = "unbound"


class ValueRange(BaseModel):
    min: float
    max: float

    @model_validator(mode="after")
    def _ordered(self) -> "ValueRange":
        if self.max < self.min:
            raise ValueError("range max must be >= min")
        return self


class ScopeAttestation(BaseModel):
    lesson_id: str
    span: Span


class Rule(BaseModel):
    rule_key: Optional[str] = None     # None until the vocabulary names it
    tier: str
    kind: str                          # threshold | range | boolean
    stage: str                         # screen | sector | valuation | exit
    operator: Optional[str] = None
    value: Optional[float] = None
    value_range: Optional[ValueRange] = None
    unit: Optional[str] = None
    conviction: str = "preference"
    as_of: Optional[str] = None        # recording period, e.g. "2021-06"
    scope: Dict[str, str] = Field(default_factory=dict)
    scope_attestation: Optional[ScopeAttestation] = None
    binding: Binding = Field(default_factory=Binding)
    citations: List[Citation] = Field(default_factory=list)
    corroboration: int = 0
    status: str = "draft"

    @model_validator(mode="after")
    def _one_value_form(self) -> "Rule":
        if self.value is not None and self.value_range is not None:
            raise ValueError("rule carries both a scalar value and a range")
        return self

    @model_validator(mode="after")
    def _known_enums(self) -> "Rule":
        """Every enum field is closed at construction.

        These constants used to be declared and enforced nowhere, which made
        them documentation rather than a contract. That mattered because the
        two fields an LLM extractor picks freely -- ``kind`` and ``tier`` --
        are exactly the two that route a rule AROUND the deterministic gates:
        ``kind`` decides whether verify.py runs its value/direction checks at
        all and whether corroborate.py's Gate 1b applies, and ``tier`` decides
        whether the rule publishes as a hard exclusion. An unrecognised value
        must therefore be a construction error the extractor drops, not a
        silent route past verification (final-branch-review.md C1).
        """
        _require_in("tier", self.tier, TIERS)
        _require_in("kind", self.kind, KINDS)
        _require_in("stage", self.stage, STAGES)
        _require_in("conviction", self.conviction, CONVICTIONS)
        _require_in("status", self.status, STATUSES)
        if self.operator is not None:
            _require_in("operator", self.operator, OPERATORS)
        return self


class LessonRecord(BaseModel):
    lesson_id: str
    course_title: str
    module_title: str
    title: str
    url: str
    body_text: str
    ai_summary: str = ""
    text_hash: str = ""
    eligible: bool = False
    transcript_fidelity: str = "verbatim"


class Candidate(BaseModel):
    lesson_id: str
    span: Span
    signals: List[str] = Field(default_factory=list)


class VerifyResult(BaseModel):
    ok: bool
    reasons: List[str] = Field(default_factory=list)
