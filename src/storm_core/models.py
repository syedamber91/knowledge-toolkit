from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class Verdict(str, Enum):
    KEEP = "KEEP"
    WATCHLIST = "WATCHLIST"
    CUT = "CUT"


class Grade(str, Enum):
    A = "A"
    B = "B"
    C = "C"


class Evidence(BaseModel):
    claim: str
    source: str
    date: Optional[str] = None
    grade: Grade
    status: str = "confirmed"  # confirmed | corrected | demoted


class Finding(BaseModel):
    title: str
    detail: str
    reliability: int = Field(ge=1, le=10)
    supported_by: List[str] = []
    challenged_by: List[str] = []
    evidence: List[Evidence] = []


class Contradiction(BaseModel):
    topic: str
    positions: Dict[str, str] = {}
    resolution: str = ""


class StormReport(BaseModel):
    topic: str
    mode: str
    summary: str
    verdict: Verdict
    lenses: List[str] = []
    findings: List[Finding] = []
    contradictions: List[Contradiction] = []
    halal_note: str = ""
    generated: str  # ISO date supplied by caller (never a now() default)
