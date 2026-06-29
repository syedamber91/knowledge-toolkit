from datetime import datetime
from pydantic import BaseModel

class GapOut(BaseModel):
    id: int
    source_tag: str
    description: str
    model_config = {"from_attributes": True}

class PassRecordOut(BaseModel):
    id: int
    pass_num: int
    acc_score: float | None
    cov_score: float | None
    alex_score: float | None
    gaps: list[GapOut] = []
    model_config = {"from_attributes": True}

class ChapterOut(BaseModel):
    id: int
    index: int
    title: str
    passes: list[PassRecordOut] = []
    model_config = {"from_attributes": True}

class SignOffOut(BaseModel):
    id: int
    agent: str
    role: str
    status: str
    criteria: list[str] = []
    model_config = {"from_attributes": True}

class DeliveryStepOut(BaseModel):
    id: int
    index: int
    label: str
    status: str
    detail: str | None
    model_config = {"from_attributes": True}

class RunOut(BaseModel):
    id: int
    title: str
    authors: list[str]
    examiners: list[str]
    topic: str
    status: str
    current_stage: str
    current_pass: int
    pdf_path: str | None
    started_at: datetime
    chapters: list[ChapterOut] = []
    sign_offs: list[SignOffOut] = []
    delivery_steps: list[DeliveryStepOut] = []
    model_config = {"from_attributes": True}

class RunCreate(BaseModel):
    authors: list[str]
    examiners: list[str]
    topic: str
    chapter_titles: list[str]  # exactly 5

class StatsOut(BaseModel):
    total_runs: int
    passed_this_week: int
    avg_passes_to_ship: float
    tokens_this_month: int

class TopicOut(BaseModel):
    id: int
    name: str
    authors: list[str]
    post_count: int
    status: str
    post_count_at_ship: int | None
    shipped_at: datetime | None
    model_config = {"from_attributes": True}
