from __future__ import annotations

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Float, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

class Run(Base):
    __tablename__ = "runs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String)        # "vutr · Spark Internals"
    authors: Mapped[list] = mapped_column(JSON)       # ["vutr", "luc"]
    examiners: Mapped[list] = mapped_column(JSON)     # ["vutr", "luc"]
    topic: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="running")  # running|done|stalled
    current_stage: Mapped[str] = mapped_column(String, default="ingestion")
    # ingestion|generation|verification|sign-off|delivery
    current_pass: Mapped[int] = mapped_column(Integer, default=1)
    pdf_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    chapters: Mapped[list["Chapter"]] = relationship(back_populates="run", cascade="all, delete-orphan")
    sign_offs: Mapped[list["SignOff"]] = relationship(back_populates="run", cascade="all, delete-orphan")
    delivery_steps: Mapped[list["DeliveryStep"]] = relationship(back_populates="run", cascade="all, delete-orphan")

class Chapter(Base):
    __tablename__ = "chapters"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("runs.id"))
    index: Mapped[int] = mapped_column(Integer)       # 0-4
    title: Mapped[str] = mapped_column(String)
    run: Mapped["Run"] = relationship(back_populates="chapters")
    passes: Mapped[list["PassRecord"]] = relationship(back_populates="chapter", cascade="all, delete-orphan")

class PassRecord(Base):
    __tablename__ = "pass_records"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    chapter_id: Mapped[int] = mapped_column(ForeignKey("chapters.id"))
    pass_num: Mapped[int] = mapped_column(Integer)
    acc_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cov_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    alex_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    chapter: Mapped["Chapter"] = relationship(back_populates="passes")
    gaps: Mapped[list["Gap"]] = relationship(back_populates="pass_record", cascade="all, delete-orphan")

class Gap(Base):
    __tablename__ = "gaps"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    pass_record_id: Mapped[int] = mapped_column(ForeignKey("pass_records.id"))
    source_tag: Mapped[str] = mapped_column(String)   # "Ch 2 · joint"
    description: Mapped[str] = mapped_column(Text)
    pass_record: Mapped["PassRecord"] = relationship(back_populates="gaps")

class SignOff(Base):
    __tablename__ = "sign_offs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("runs.id"))
    agent: Mapped[str] = mapped_column(String)        # "vutr", "justin", "alex"
    role: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="pending")  # pending|approved|rejected
    criteria: Mapped[list] = mapped_column(JSON, default=list)
    run: Mapped["Run"] = relationship(back_populates="sign_offs")

class DeliveryStep(Base):
    __tablename__ = "delivery_steps"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("runs.id"))
    index: Mapped[int] = mapped_column(Integer)       # 0-4
    label: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="waiting")  # waiting|uploading|done
    detail: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    run: Mapped["Run"] = relationship(back_populates="delivery_steps")

class Topic(Base):
    __tablename__ = "topics"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    authors: Mapped[list] = mapped_column(JSON, default=list)
    post_count: Mapped[int] = mapped_column(Integer, default=0)
    authors_post_count: Mapped[dict] = mapped_column(JSON, default=dict)  # {"author": count}
    suggested_chapters: Mapped[list] = mapped_column(JSON, default=list)  # pre-determined from vault
    status: Mapped[str] = mapped_column(String, default="suggested")  # suggested|shipped|needsUpdate
    shipped_run_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    post_count_at_ship: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    shipped_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
