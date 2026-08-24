"""Claims: one assertion from one lecture, with the quote that proves it.

A claim is minted from a lecture brief but VERIFIED against the raw
transcript. Minting and verifying against the same artifact would check a copy
against itself, which is how drift between transcript and brief stays
invisible.

`worked_example` cannot carry a bound. Treating a dated one-company
illustration as a universal rule is the single most common defect in this
corpus, so the schema refuses it rather than relying on anyone remembering.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel, model_validator

from soic_method.corpus import normalize_slice

CLAIM_TYPES = ("threshold", "scope", "mechanism",
               "disqualifier", "procedure", "worked_example")


def _norm(text: str) -> str:
    # normalize_slice is the sanctioned slice-comparison utility (whitespace
    # collapse + casefold + transcript-marker strip) -- reuse it rather than
    # duplicating a slightly weaker local normalizer.
    return normalize_slice(text or "")


class Claim(BaseModel):
    claim_id: str
    kind: str
    ref: str                      # lecture REF code
    ts: str                       # HH:MM:SS -- with ref, identifies the lesson
    quote: str                    # verbatim, checked against the transcript
    statement: str                # the claim in our own words
    source_brief: str
    metric: Optional[str] = None  # thresholds only
    bound: Optional[str] = None   # thresholds only, e.g. ">= 15"
    scopes: List[str] = []        # claim_ids of thresholds this scope governs

    @model_validator(mode="after")
    def _check(self):
        if self.kind not in CLAIM_TYPES:
            raise ValueError(f"unknown claim kind {self.kind!r}")
        if self.kind == "worked_example" and self.bound:
            raise ValueError(
                "a worked_example may not carry a bound -- a dated "
                "illustration must never be usable as a rule")
        if self.kind == "threshold" and not (self.metric and self.bound):
            raise ValueError("a threshold needs both a metric and a bound")
        if self.scopes and self.kind != "scope":
            raise ValueError("only a scope claim may govern thresholds")
        return self


def load_claims(path: Path) -> List[Claim]:
    return [Claim(**row) for row in json.loads(Path(path).read_text("utf-8"))]


def save_claims(path: Path, claims: List[Claim]) -> None:
    Path(path).write_text(
        json.dumps([c.model_dump() for c in claims], indent=2) + "\n",
        encoding="utf-8")


def verify_claim(claim: Claim, resolver) -> bool:
    """Is this claim's quote actually in the lecture window it cites?"""
    if resolver.resolve(claim.ref, claim.ts) is None:
        return False
    window = resolver.window(claim.ref, claim.ts)
    return _norm(claim.quote) in _norm(window)


def verify_all(claims: List[Claim], resolver) -> Dict[str, bool]:
    return {c.claim_id: verify_claim(c, resolver) for c in claims}
