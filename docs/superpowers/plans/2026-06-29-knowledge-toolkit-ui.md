# Knowledge Toolkit UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local-first web app that automates the full learning-pack pipeline — from vault content ingestion through multi-agent verification to Google Drive delivery and GitHub PR — replacing manual copy-pasting into Agentic Chat.

**Architecture:** FastAPI backend (Python, shares the existing toolkit virtualenv) serves a REST + SSE API backed by SQLite; Next.js 14 App Router frontend consumes it. Real-time log streaming uses Server-Sent Events. Pipeline scripts are invoked as subprocesses by the backend.

**Tech Stack:** Python 3.9+ · FastAPI · SQLAlchemy 2 · SQLite · Pydantic v2 · Next.js 14 (App Router) · TypeScript · Tailwind CSS · Inter font

## Global Constraints

- Python ≥ 3.9, Node ≥ 18
- All backend code under `webapp/backend/`, all frontend code under `webapp/frontend/`
- Design tokens (colors, fonts) match spec exactly: blue #185FA5, green #3B6D11, amber #EF9F27 / #854F0B, red #A32D2D, teal #0F6E56
- Monospace font: Geist Mono (bundled with Next.js) for log streams
- Light mode only; no dark-mode variants
- No authentication for v1 (single-user local)
- Backend runs on port 8000; frontend on port 3000
- CORS: backend allows localhost:3000

---

## File Map

```
webapp/
  backend/
    main.py              # FastAPI app, CORS, router registration, SSE endpoint
    database.py          # SQLAlchemy engine, SessionLocal, Base, get_db dependency
    models.py            # ORM models: Run, Chapter, PassRecord, Gap, SignOff, DeliveryStep, Topic
    schemas.py           # Pydantic v2 request/response schemas
    seed.py              # Dev seed data (10 mock runs)
    routers/
      runs.py            # GET/POST /runs, GET /runs/{id}
      topics.py          # GET /topics — reads vault post counts
      pipeline.py        # POST /runs/{id}/start, GET /runs/{id}/stream (SSE)
    pipeline/
      executor.py        # subprocess-based pipeline stage runner + SSE event queue
  frontend/
    app/
      layout.tsx         # Root layout: Inter + Geist Mono fonts, Topbar
      page.tsx           # Redirect → /runs
      runs/
        page.tsx         # Run List screen
      runs/new/
        page.tsx         # Pack Builder screen
      runs/[id]/
        page.tsx         # Run Detail screen (switches to Sign-off when stage=sign-off)
    components/
      Topbar.tsx
      runs/
        StatsRow.tsx
        FilterPills.tsx
        RunListTable.tsx
      pack-builder/
        AuthorChips.tsx
        TopicBrowser.tsx
        ChapterFields.tsx
        ExaminerGrid.tsx
        RunPreview.tsx
        AttentionDigest.tsx
      run-detail/
        Sidebar.tsx
        AgentStrip.tsx
        ScoreGrid.tsx
        GapsList.tsx
        LiveLog.tsx        # SSE consumer
      sign-off/
        SignOffCards.tsx
        DeliveryChecklist.tsx
    lib/
      api.ts             # fetch wrappers for all backend endpoints
      types.ts           # TypeScript types matching Pydantic schemas
      colors.ts          # Design token constants
    styles/
      globals.css        # Tailwind base + CSS variable color tokens
    tailwind.config.ts
    next.config.ts
    package.json
    tsconfig.json
```

---

## Task 1: Backend scaffold + database models

**Files:**
- Create: `webapp/backend/database.py`
- Create: `webapp/backend/models.py`
- Create: `webapp/backend/schemas.py`
- Create: `webapp/backend/main.py`
- Create: `webapp/backend/requirements.txt`
- Create: `webapp/backend/seed.py`

**Interfaces:**
- Produces: `get_db()` FastAPI dependency · ORM models importable from `models` · Pydantic schemas importable from `schemas`

- [ ] **Step 1: Create `webapp/backend/requirements.txt`**

```
fastapi==0.111.0
uvicorn[standard]==0.29.0
sqlalchemy==2.0.30
pydantic==2.7.1
pydantic-settings==2.2.1
sse-starlette==2.1.0
```

- [ ] **Step 2: Install dependencies**

```bash
cd webapp/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Expected: all packages install without error.

- [ ] **Step 3: Create `webapp/backend/database.py`**

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

SQLALCHEMY_DATABASE_URL = "sqlite:///./toolkit.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- [ ] **Step 4: Create `webapp/backend/models.py`**

```python
from datetime import datetime
from sqlalchemy import String, Integer, Float, Boolean, ForeignKey, DateTime, Text, JSON
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
    pdf_path: Mapped[str | None] = mapped_column(String, nullable=True)
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
    acc_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    cov_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    alex_score: Mapped[float | None] = mapped_column(Float, nullable=True)
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
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    run: Mapped["Run"] = relationship(back_populates="delivery_steps")

class Topic(Base):
    __tablename__ = "topics"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    authors: Mapped[list] = mapped_column(JSON, default=list)
    post_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String, default="suggested")  # suggested|shipped|needsUpdate
    shipped_run_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    post_count_at_ship: Mapped[int | None] = mapped_column(Integer, nullable=True)
    shipped_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
```

- [ ] **Step 5: Create `webapp/backend/schemas.py`**

```python
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
```

- [ ] **Step 6: Create `webapp/backend/main.py`**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Knowledge Toolkit API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

from routers import runs, topics, pipeline
app.include_router(runs.router)
app.include_router(topics.router)
app.include_router(pipeline.router)

@app.get("/health")
def health():
    return {"status": "ok"}
```

- [ ] **Step 7: Create `webapp/backend/routers/` package**

```bash
mkdir -p webapp/backend/routers
touch webapp/backend/routers/__init__.py
mkdir -p webapp/backend/pipeline
touch webapp/backend/pipeline/__init__.py
```

- [ ] **Step 8: Write smoke test**

```bash
cd webapp/backend && source .venv/bin/activate
python -c "from main import app; print('OK')"
```

Expected: `OK`

- [ ] **Step 9: Start server and verify health**

```bash
uvicorn main:app --reload --port 8000
```

In another terminal: `curl http://localhost:8000/health`
Expected: `{"status":"ok"}`

- [ ] **Step 10: Commit**

```bash
git add webapp/backend/
git commit -m "feat(ui): backend scaffold — FastAPI + SQLAlchemy + models + schemas"
```

---

## Task 2: Seed data + Runs API

**Files:**
- Create: `webapp/backend/seed.py`
- Create: `webapp/backend/routers/runs.py`
- Create: `webapp/backend/routers/topics.py`

**Interfaces:**
- Consumes: `get_db`, ORM models, schemas from Task 1
- Produces: `GET /runs` → `{stats: StatsOut, runs: RunOut[]}` · `POST /runs` → `RunOut` · `GET /runs/{id}` → `RunOut` · `GET /topics` → `TopicOut[]`

- [ ] **Step 1: Create `webapp/backend/seed.py`**

```python
"""Run once to populate dev data: python seed.py"""
from datetime import datetime, timedelta
from database import SessionLocal, engine, Base
from models import Run, Chapter, PassRecord, Gap, SignOff, DeliveryStep, Topic

Base.metadata.create_all(bind=engine)
db = SessionLocal()

if db.query(Run).count() > 0:
    print("Already seeded"); db.close(); exit()

def make_run(title, authors, examiners, topic, status, stage, passes, chapters_data, days_ago):
    r = Run(
        title=title, authors=authors, examiners=examiners, topic=topic,
        status=status, current_stage=stage, current_pass=passes,
        started_at=datetime.utcnow() - timedelta(days=days_ago),
    )
    db.add(r); db.flush()
    for i, (ch_title, ch_passes) in enumerate(chapters_data):
        ch = Chapter(run_id=r.id, index=i, title=ch_title)
        db.add(ch); db.flush()
        for p_num, (acc, cov, alex) in enumerate(ch_passes, 1):
            pr = PassRecord(chapter_id=ch.id, pass_num=p_num,
                            acc_score=acc, cov_score=cov, alex_score=alex)
            db.add(pr)
    for agent, role, s, criteria in [
        (examiners[0], "Examiner", "approved" if status == "done" else "pending",
         ["Accuracy ≥ 9.0 all chapters", "Coverage ≥ 9.0 all chapters"]),
        ("justin", "Pedagogy reviewer", "approved" if status == "done" else "pending",
         ["Retrieval practice present", "WHY→WHAT→HOW structure"]),
        ("alex", "Clarity auditor", "approved" if status == "done" else "pending",
         ["Clarity ≥ 9.0 all chapters"]),
    ]:
        db.add(SignOff(run_id=r.id, agent=agent, role=role, status=s, criteria=criteria if s == "approved" else []))
    for idx, (label, det) in enumerate([
        ("PDF generated", "output/pack.pdf · 2.1 MB"),
        ("Google Drive upload", "My Drive / Learning Packs"),
        ("Git commit", 'git commit -m "feat: learning pack"'),
        ("Push branch", "git push origin HEAD"),
        ("Open pull request", "gh pr create"),
    ]):
        db.add(DeliveryStep(run_id=r.id, index=idx, label=label,
                            status="done" if status == "done" else "waiting", detail=det))
    return r

# Seed runs
make_run("vutr · Spark Internals", ["vutr"], ["vutr"], "Apache Spark", "done", "delivery", 5,
    [("Spark Architecture", [(8.1,8.3,7.9),(8.8,8.9,8.5),(9.2,9.3,9.0),(9.4,9.5,9.1),(9.2,9.3,8.9)]),
     ("Shuffle & Partitioning", [(8.0,8.2,7.8),(8.9,9.0,8.7),(9.1,9.2,9.0),(9.3,9.1,9.2),(9.2,9.4,9.1)]),
     ("Catalyst Optimizer", [(8.2,8.4,8.0),(9.1,9.2,8.9),(9.3,9.4,9.2),(9.1,9.3,9.0),(9.4,9.2,9.3)]),
     ("Memory Management", [(7.9,8.1,7.7),(8.7,8.8,8.6),(9.0,9.1,8.9),(9.2,9.3,9.1),(9.1,9.2,9.0)]),
     ("Streaming (Structured)", [(8.3,8.5,8.1),(9.0,9.1,8.8),(9.2,9.0,9.1),(9.3,9.2,9.3),(9.1,9.4,9.2)])], 1)

make_run("lucsystem · Kafka Design", ["lucsystemdesign"], ["lucsystemdesign"], "Kafka", "running", "verification", 2,
    [("Kafka Architecture", [(8.4,8.6,8.2),(8.7,8.8,8.5)]),
     ("Partitions & Replication", [(8.1,8.3,7.9),(8.5,8.7,8.3)]),
     ("Consumer Groups", [(8.3,8.4,8.1),(8.6,8.8,8.4)]),
     ("Exactly-once Semantics", [(8.0,8.1,7.8),(8.4,8.6,8.2)]),
     ("Kafka Streams", [(8.2,8.3,8.0),(8.5,8.7,8.3)])], 0)

make_run("ben-dicken · DB Internals", ["ben-dicken"], ["ben-dicken"], "Database Internals", "running", "sign-off", 3,
    [("Storage Engines", [(8.2,8.4,8.0),(8.9,9.0,8.7),(9.2,9.3,9.1)]),
     ("Indexing", [(8.0,8.2,7.9),(8.8,8.9,8.6),(9.1,9.2,9.0)]),
     ("Transactions & MVCC", [(8.3,8.5,8.1),(9.0,9.1,8.8),(9.2,9.1,9.0)]),
     ("Query Execution", [(8.1,8.3,7.9),(8.9,9.0,8.7),(9.1,9.3,9.0)]),
     ("Replication", [(8.4,8.6,8.2),(9.1,9.2,9.0),(9.3,9.2,9.1)])], 2)

db.commit()

# Seed topics
for name, authors, count, status in [
    ("Apache Spark",     ["vutr"],                   47, "shipped"),
    ("Kafka",            ["lucsystemdesign"],         31, "suggested"),
    ("Iceberg",          ["vutr"],                   18, "needsUpdate"),
    ("dbt",              ["vutr","lucsystemdesign"],  12, "suggested"),
    ("ClickHouse",       ["vutr"],                   22, "suggested"),
    ("Raft Consensus",   ["sdcourse"],               15, "suggested"),
    ("Database Internals",["ben-dicken"],            18, "shipped"),
]:
    t = Topic(name=name, authors=authors, post_count=count, status=status,
              post_count_at_ship=count-6 if status in ("shipped","needsUpdate") else None,
              shipped_at=datetime.utcnow()-timedelta(days=14) if status in ("shipped","needsUpdate") else None)
    db.add(t)
db.commit()
db.close()
print("Seeded OK")
```

- [ ] **Step 2: Run seed**

```bash
cd webapp/backend && source .venv/bin/activate && python seed.py
```

Expected: `Seeded OK`

- [ ] **Step 3: Create `webapp/backend/routers/runs.py`**

```python
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Run, Chapter, PassRecord, SignOff, DeliveryStep
from schemas import RunOut, RunCreate, StatsOut

router = APIRouter(prefix="/runs", tags=["runs"])

DELIVERY_STEP_LABELS = [
    "PDF generated",
    "Google Drive upload",
    "Git commit",
    "Push branch",
    "Open pull request",
]
DELIVERY_STEP_DETAILS = [
    "output/{topic}.pdf",
    "My Drive / Learning Packs",
    'git commit -m "feat: {topic} learning pack"',
    "git push origin HEAD",
    "gh pr create --title \"feat: {topic} learning pack\"",
]

@router.get("", response_model=dict)
def list_runs(db: Session = Depends(get_db)):
    runs = db.query(Run).order_by(Run.started_at.desc()).all()
    week_ago = datetime.utcnow() - timedelta(days=7)
    passed_week = sum(1 for r in runs if r.status == "done" and r.started_at >= week_ago)
    done = [r for r in runs if r.status == "done"]
    avg = round(sum(r.current_pass for r in done) / len(done), 1) if done else 0.0
    stats = StatsOut(
        total_runs=len(runs),
        passed_this_week=passed_week,
        avg_passes_to_ship=avg,
        tokens_this_month=1_240_000,
    )
    return {"stats": stats.model_dump(), "runs": [RunOut.model_validate(r).model_dump() for r in runs]}

@router.get("/{run_id}", response_model=RunOut)
def get_run(run_id: int, db: Session = Depends(get_db)):
    return db.query(Run).filter(Run.id == run_id).first()

@router.post("", response_model=RunOut, status_code=201)
def create_run(body: RunCreate, db: Session = Depends(get_db)):
    title = " · ".join(body.authors) + " · " + body.topic
    run = Run(title=title, authors=body.authors, examiners=body.examiners,
              topic=body.topic, status="running", current_stage="ingestion")
    db.add(run); db.flush()
    for i, t in enumerate(body.chapter_titles):
        db.add(Chapter(run_id=run.id, index=i, title=t))
    for agent, role in [("examiner", "Examiner"), ("justin", "Pedagogy reviewer"), ("alex", "Clarity auditor")]:
        db.add(SignOff(run_id=run.id, agent=agent, role=role, status="pending"))
    for idx, (label, detail) in enumerate(zip(DELIVERY_STEP_LABELS, DELIVERY_STEP_DETAILS)):
        db.add(DeliveryStep(run_id=run.id, index=idx, label=label, status="waiting",
                            detail=detail.format(topic=body.topic.lower().replace(" ", "_"))))
    db.commit(); db.refresh(run)
    return run
```

- [ ] **Step 4: Create `webapp/backend/routers/topics.py`**

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Topic
from schemas import TopicOut

router = APIRouter(prefix="/topics", tags=["topics"])

@router.get("", response_model=list[TopicOut])
def list_topics(db: Session = Depends(get_db)):
    return db.query(Topic).order_by(Topic.name).all()
```

- [ ] **Step 5: Write API test**

```bash
cd webapp/backend && source .venv/bin/activate
uvicorn main:app --port 8000 &
sleep 2
curl -s http://localhost:8000/runs | python3 -c "import sys,json; d=json.load(sys.stdin); print('runs:', len(d['runs']), '| stats:', d['stats'])"
curl -s http://localhost:8000/topics | python3 -c "import sys,json; d=json.load(sys.stdin); print('topics:', len(d))"
kill %1
```

Expected: `runs: 3 | stats: {total_runs: 3, ...}` and `topics: 7`

- [ ] **Step 6: Commit**

```bash
git add webapp/backend/
git commit -m "feat(ui): runs + topics API with seed data"
```

---

## Task 3: Frontend scaffold + design system

**Files:**
- Create: `webapp/frontend/package.json`
- Create: `webapp/frontend/tailwind.config.ts`
- Create: `webapp/frontend/app/layout.tsx`
- Create: `webapp/frontend/styles/globals.css`
- Create: `webapp/frontend/lib/colors.ts`
- Create: `webapp/frontend/lib/types.ts`
- Create: `webapp/frontend/lib/api.ts`
- Create: `webapp/frontend/components/Topbar.tsx`

**Interfaces:**
- Produces: typed `api.*` functions · `COLORS` token object · `Run`, `Topic`, `StatsOut` TypeScript types · `<Topbar>` component

- [ ] **Step 1: Scaffold Next.js app**

```bash
cd webapp
npx create-next-app@14 frontend --typescript --tailwind --app --no-src-dir --import-alias "@/*"
cd frontend
npm install
```

Expected: Next.js project created without errors.

- [ ] **Step 2: Install Geist font package**

```bash
cd webapp/frontend
npm install geist
```

- [ ] **Step 3: Write `webapp/frontend/styles/globals.css`**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --blue:      #185FA5;
  --blue-bg:   #EBF0F7;
  --green:     #3B6D11;
  --green-bg:  #E2F1D8;
  --amber:     #EF9F27;
  --amber-dk:  #854F0B;
  --amber-bg:  #FEF2E1;
  --red:       #A32D2D;
  --red-bg:    #F9E8E8;
  --teal:      #0F6E56;
  --teal-bg:   #E1F4EF;
  --gray-10:   #111111;
  --gray-30:   #333333;
  --gray-50:   #666666;
  --gray-70:   #999999;
  --gray-90:   #CCCCCC;
  --gray-95:   #EBEBEB;
  --gray-97:   #F5F5F5;
  --border:    #E0E0E0;
}
```

- [ ] **Step 4: Write `webapp/frontend/lib/colors.ts`**

```typescript
export const C = {
  blue:     "var(--blue)",
  blueBg:   "var(--blue-bg)",
  green:    "var(--green)",
  greenBg:  "var(--green-bg)",
  amber:    "var(--amber)",
  amberDk:  "var(--amber-dk)",
  amberBg:  "var(--amber-bg)",
  red:      "var(--red)",
  redBg:    "var(--red-bg)",
  teal:     "var(--teal)",
  tealBg:   "var(--teal-bg)",
  gray10:   "var(--gray-10)",
  gray30:   "var(--gray-30)",
  gray50:   "var(--gray-50)",
  gray70:   "var(--gray-70)",
  gray90:   "var(--gray-90)",
  gray95:   "var(--gray-95)",
  gray97:   "var(--gray-97)",
  border:   "var(--border)",
} as const;
```

- [ ] **Step 5: Write `webapp/frontend/lib/types.ts`**

```typescript
export interface Gap {
  id: number;
  source_tag: string;
  description: string;
}

export interface PassRecord {
  id: number;
  pass_num: number;
  acc_score: number | null;
  cov_score: number | null;
  alex_score: number | null;
  gaps: Gap[];
}

export interface Chapter {
  id: number;
  index: number;
  title: string;
  passes: PassRecord[];
}

export interface SignOff {
  id: number;
  agent: string;
  role: string;
  status: "pending" | "approved" | "rejected";
  criteria: string[];
}

export interface DeliveryStep {
  id: number;
  index: number;
  label: string;
  status: "waiting" | "uploading" | "done";
  detail: string | null;
}

export interface Run {
  id: number;
  title: string;
  authors: string[];
  examiners: string[];
  topic: string;
  status: "running" | "done" | "stalled";
  current_stage: "ingestion" | "generation" | "verification" | "sign-off" | "delivery";
  current_pass: number;
  pdf_path: string | null;
  started_at: string;
  chapters: Chapter[];
  sign_offs: SignOff[];
  delivery_steps: DeliveryStep[];
}

export interface StatsOut {
  total_runs: number;
  passed_this_week: number;
  avg_passes_to_ship: number;
  tokens_this_month: number;
}

export interface RunsListResponse {
  stats: StatsOut;
  runs: Run[];
}

export interface Topic {
  id: number;
  name: string;
  authors: string[];
  post_count: number;
  status: "suggested" | "shipped" | "needsUpdate";
  post_count_at_ship: number | null;
  shipped_at: string | null;
}
```

- [ ] **Step 6: Write `webapp/frontend/lib/api.ts`**

```typescript
const BASE = "http://localhost:8000";

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}

export const api = {
  runs: {
    list: () => get<import("./types").RunsListResponse>("/runs"),
    get:  (id: number) => get<import("./types").Run>(`/runs/${id}`),
    create: (body: { authors: string[]; examiners: string[]; topic: string; chapter_titles: string[] }) =>
      post<import("./types").Run>("/runs", body),
  },
  topics: {
    list: () => get<import("./types").Topic[]>("/topics"),
  },
};
```

- [ ] **Step 7: Write `webapp/frontend/app/layout.tsx`**

```typescript
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { GeistMono } from "geist/font/mono";
import "@/styles/globals.css";
import Topbar from "@/components/Topbar";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = { title: "Knowledge Toolkit" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${inter.variable} ${GeistMono.variable}`}>
      <body className="bg-[var(--gray-97)] font-[family-name:var(--font-inter)] text-[var(--gray-10)]">
        <Topbar />
        <main className="pt-14">{children}</main>
      </body>
    </html>
  );
}
```

- [ ] **Step 8: Write `webapp/frontend/components/Topbar.tsx`**

```typescript
"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Topbar() {
  const path = usePathname();
  const isNew = path === "/runs/new";
  return (
    <header className="fixed top-0 left-0 right-0 h-14 bg-white border-b border-[var(--border)] flex items-center px-6 z-50">
      <span className="text-[15px] font-semibold text-[var(--gray-10)]">Knowledge Toolkit</span>
      <span className="ml-2 text-[10px] font-medium px-1.5 py-0.5 rounded bg-[var(--blue-bg)] text-[var(--blue)]">beta</span>
      <div className="ml-auto">
        {!isNew && (
          <Link href="/runs/new"
            className="px-4 py-2 bg-[var(--blue)] text-white text-[13px] font-medium rounded-md hover:opacity-90">
            + New run
          </Link>
        )}
      </div>
    </header>
  );
}
```

- [ ] **Step 9: Write `webapp/frontend/app/page.tsx`** (redirect)

```typescript
import { redirect } from "next/navigation";
export default function Home() { redirect("/runs"); }
```

- [ ] **Step 10: Start dev server and verify it compiles**

```bash
cd webapp/frontend && npm run dev
```

Open http://localhost:3000 — should redirect to /runs (404 page is fine; route doesn't exist yet).

- [ ] **Step 11: Commit**

```bash
git add webapp/frontend/
git commit -m "feat(ui): Next.js frontend scaffold — design tokens, types, API client"
```

---

## Task 4: Run List screen

**Files:**
- Create: `webapp/frontend/app/runs/page.tsx`
- Create: `webapp/frontend/components/runs/StatsRow.tsx`
- Create: `webapp/frontend/components/runs/FilterPills.tsx`
- Create: `webapp/frontend/components/runs/RunListTable.tsx`

**Interfaces:**
- Consumes: `api.runs.list()` → `RunsListResponse`
- Produces: `/runs` route renders full Run List screen

- [ ] **Step 1: Create `webapp/frontend/components/runs/StatsRow.tsx`**

```typescript
import { StatsOut } from "@/lib/types";

interface Props { stats: StatsOut }

const STATS = [
  { key: "total_runs" as const,          label: "Total runs",          sub: "all time",     color: "var(--blue)" },
  { key: "passed_this_week" as const,    label: "Passed this week",    sub: "last 7 days",  color: "var(--green)" },
  { key: "avg_passes_to_ship" as const,  label: "Avg passes to ship",  sub: "per pack",     color: "var(--gray-30)" },
  { key: "tokens_this_month" as const,   label: "Tokens this month",   sub: "est. cost",    color: "var(--amber-dk)" },
];

function formatValue(key: keyof StatsOut, val: number): string {
  if (key === "tokens_this_month") return (val / 1_000_000).toFixed(1) + "M";
  if (key === "avg_passes_to_ship") return val.toFixed(1);
  return String(val);
}

export default function StatsRow({ stats }: Props) {
  return (
    <div className="grid grid-cols-4 gap-4 mb-6">
      {STATS.map((s) => (
        <div key={s.key} className="bg-white border border-[var(--border)] rounded-lg px-5 py-4">
          <div className="text-[26px] font-semibold" style={{ color: s.color }}>
            {formatValue(s.key, stats[s.key])}
          </div>
          <div className="text-[11px] text-[var(--gray-50)] mt-1">{s.label}</div>
          <div className="text-[10px] text-[var(--gray-70)]">{s.sub}</div>
        </div>
      ))}
    </div>
  );
}
```

- [ ] **Step 2: Create `webapp/frontend/components/runs/FilterPills.tsx`**

```typescript
"use client";
const FILTERS = ["All", "Running", "Done", "Failed"] as const;
type Filter = typeof FILTERS[number];

interface Props { active: Filter; onChange: (f: Filter) => void }

export default function FilterPills({ active, onChange }: Props) {
  return (
    <div className="flex gap-2 mb-4">
      {FILTERS.map((f) => (
        <button key={f} onClick={() => onChange(f)}
          className={`px-3.5 py-1.5 rounded-full text-[12px] font-medium border transition-colors ${
            f === active
              ? "bg-[var(--blue)] text-white border-[var(--blue)]"
              : "bg-white text-[var(--gray-30)] border-[var(--border)] hover:border-[var(--gray-70)]"
          }`}>
          {f}
        </button>
      ))}
    </div>
  );
}
```

- [ ] **Step 3: Create `webapp/frontend/components/runs/RunListTable.tsx`**

```typescript
"use client";
import { useRouter } from "next/navigation";
import { Run } from "@/lib/types";

interface Props { runs: Run[] }

function StatusDot({ status }: { status: Run["status"] }) {
  const color = status === "done" ? "var(--green)" : status === "stalled" ? "var(--red)" : "var(--amber)";
  return <span className="inline-block w-2.5 h-2.5 rounded-full" style={{ backgroundColor: color }} />;
}

function StagePill({ stage }: { stage: Run["current_stage"] }) {
  const map: Record<string, { label: string; color: string }> = {
    ingestion:    { label: "Ingestion",    color: "var(--teal)" },
    generation:   { label: "Generating",  color: "var(--teal)" },
    verification: { label: "Verification",color: "var(--blue)" },
    "sign-off":   { label: "Sign-off",    color: "var(--amber-dk)" },
    delivery:     { label: "Delivery",    color: "var(--green)" },
  };
  const { label, color } = map[stage] ?? { label: stage, color: "var(--gray-50)" };
  return (
    <span className="text-[11px] font-medium px-2.5 py-1 rounded-full border"
      style={{ color, borderColor: color, backgroundColor: color + "18" }}>
      {label}
    </span>
  );
}

function ScoreBars({ chapters }: { chapters: Run["chapters"] }) {
  if (!chapters.length) return <span className="text-[var(--gray-90)] text-xs">—</span>;
  const latest = chapters.map((ch) => ch.passes.at(-1));
  const dims = [
    { key: "acc_score" as const, color: "var(--blue)" },
    { key: "cov_score" as const, color: "var(--green)" },
    { key: "alex_score" as const, color: "var(--amber)" },
  ];
  const avg = (key: "acc_score" | "cov_score" | "alex_score") => {
    const vals = latest.map((p) => p?.[key] ?? 0).filter(Boolean);
    return vals.length ? vals.reduce((a, b) => a + b, 0) / vals.length : 0;
  };
  return (
    <div className="flex flex-col gap-1 w-24">
      {dims.map((d) => {
        const v = avg(d.key);
        const pass = v >= 9.0;
        return (
          <div key={d.key} className="h-1 bg-[var(--gray-95)] rounded-full overflow-hidden">
            <div className="h-full rounded-full" style={{
              width: `${Math.round(v * 10)}%`,
              backgroundColor: pass ? d.color : "var(--red)",
            }} />
          </div>
        );
      })}
    </div>
  );
}

const HEADERS = ["", "Pack", "Stage", "Score", "Passes", "Started"];

export default function RunListTable({ runs }: Props) {
  const router = useRouter();
  return (
    <div className="bg-white border border-[var(--border)] rounded-lg overflow-hidden">
      <div className="grid grid-cols-[32px_1fr_140px_110px_70px_160px] px-4 py-2 bg-[var(--gray-95)] text-[10px] font-semibold text-[var(--gray-50)] uppercase tracking-wide">
        {HEADERS.map((h) => <div key={h}>{h}</div>)}
      </div>
      {runs.map((run, i) => (
        <div key={run.id}
          onClick={() => router.push(`/runs/${run.id}`)}
          className={`grid grid-cols-[32px_1fr_140px_110px_70px_160px] px-4 py-3.5 items-center border-t border-[var(--border)] cursor-pointer hover:bg-[var(--gray-97)] transition-colors ${i % 2 === 0 ? "bg-white" : "bg-[var(--gray-97)]"}`}>
          <div><StatusDot status={run.status} /></div>
          <div className="text-[13px] font-medium text-[var(--gray-10)] truncate pr-4">{run.title}</div>
          <div><StagePill stage={run.current_stage} /></div>
          <div><ScoreBars chapters={run.chapters} /></div>
          <div className="text-[13px] text-[var(--gray-30)]">{run.current_pass}</div>
          <div className="text-[12px] text-[var(--gray-50)]">
            {new Date(run.started_at).toLocaleDateString("en-GB", { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" })}
          </div>
        </div>
      ))}
      {runs.length === 0 && (
        <div className="px-4 py-8 text-center text-[var(--gray-70)] text-sm">No runs match this filter</div>
      )}
    </div>
  );
}
```

- [ ] **Step 4: Create `webapp/frontend/app/runs/page.tsx`**

```typescript
"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Run, StatsOut } from "@/lib/types";
import StatsRow from "@/components/runs/StatsRow";
import FilterPills from "@/components/runs/FilterPills";
import RunListTable from "@/components/runs/RunListTable";

type Filter = "All" | "Running" | "Done" | "Failed";

export default function RunsPage() {
  const [runs, setRuns] = useState<Run[]>([]);
  const [stats, setStats] = useState<StatsOut | null>(null);
  const [filter, setFilter] = useState<Filter>("All");

  useEffect(() => {
    api.runs.list().then((d) => { setRuns(d.runs); setStats(d.stats); });
  }, []);

  const filtered = runs.filter((r) => {
    if (filter === "All") return true;
    if (filter === "Running") return r.status === "running";
    if (filter === "Done") return r.status === "done";
    if (filter === "Failed") return r.status === "stalled";
    return true;
  });

  return (
    <div className="max-w-[1392px] mx-auto px-6 py-6">
      <h1 className="text-[22px] font-semibold mb-6">Runs</h1>
      {stats && <StatsRow stats={stats} />}
      <FilterPills active={filter} onChange={setFilter} />
      <RunListTable runs={filtered} />
    </div>
  );
}
```

- [ ] **Step 5: Test in browser**

With both servers running (`uvicorn` on :8000, `npm run dev` on :3000):
Open http://localhost:3000/runs — verify: 4 stat cards, filter pills, 3 seeded run rows with status dots, stage pills, score bars.

- [ ] **Step 6: Commit**

```bash
git add webapp/frontend/app/runs/ webapp/frontend/components/runs/
git commit -m "feat(ui): Run List screen — stats row, filter pills, run table"
```

---

## Task 5: Pack Builder screen

**Files:**
- Create: `webapp/frontend/components/pack-builder/AuthorChips.tsx`
- Create: `webapp/frontend/components/pack-builder/TopicBrowser.tsx`
- Create: `webapp/frontend/components/pack-builder/ChapterFields.tsx`
- Create: `webapp/frontend/components/pack-builder/ExaminerGrid.tsx`
- Create: `webapp/frontend/components/pack-builder/RunPreview.tsx`
- Create: `webapp/frontend/components/pack-builder/AttentionDigest.tsx`
- Create: `webapp/frontend/app/runs/new/page.tsx`

**Interfaces:**
- Consumes: `api.topics.list()`, `api.runs.create()`
- Produces: `/runs/new` route renders full Pack Builder; on submit redirects to `/runs/{id}`

- [ ] **Step 1: Create `webapp/frontend/components/pack-builder/AuthorChips.tsx`**

```typescript
"use client";
const AUTHORS = [
  { handle: "vutr",            posts: 47 },
  { handle: "lucsystemdesign", posts: 31 },
  { handle: "ben-dicken",      posts: 18 },
  { handle: "sdcourse",        posts: 22 },
];

interface Props { selected: string[]; onChange: (s: string[]) => void }

export default function AuthorChips({ selected, onChange }: Props) {
  const toggle = (h: string) =>
    onChange(selected.includes(h) ? selected.filter((x) => x !== h) : [...selected, h]);

  return (
    <div>
      <label className="text-[10px] font-semibold text-[var(--gray-50)] uppercase tracking-wide block mb-2">Authors</label>
      <div className="flex flex-wrap gap-2">
        {AUTHORS.map((a) => {
          const active = selected.includes(a.handle);
          return (
            <button key={a.handle} onClick={() => toggle(a.handle)}
              className={`px-3 py-1.5 rounded-full border text-left transition-colors ${
                active ? "bg-[var(--blue-bg)] border-[var(--blue)]" : "bg-white border-[var(--border)]"
              }`}>
              <div className={`text-[12px] font-medium ${active ? "text-[var(--blue)]" : "text-[var(--gray-50)]"}`}>{a.handle}</div>
              <div className={`text-[9px] ${active ? "text-[var(--blue)]" : "text-[var(--gray-70)]"}`}>{a.posts} posts</div>
            </button>
          );
        })}
      </div>
      {selected.length > 1 && (
        <div className="mt-2 inline-flex items-center px-3 py-1 rounded-full bg-[var(--blue-bg)] text-[var(--blue)] text-[11px] font-medium">
          Joint mode · {selected.length} authors active
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Create `webapp/frontend/components/pack-builder/TopicBrowser.tsx`**

```typescript
"use client";
import { useState } from "react";
import { Topic } from "@/lib/types";

const STATE_STYLES = {
  suggested:   { border: "border-[var(--border)]",  bg: "bg-white",              badge: "text-[var(--gray-50)] border-[var(--gray-90)] bg-[var(--gray-97)]" },
  shipped:     { border: "border-[var(--green)]",   bg: "bg-[var(--green-bg)]",  badge: "text-[var(--green)] border-[var(--green)] bg-white" },
  needsUpdate: { border: "border-[var(--amber)]",   bg: "bg-[var(--amber-bg)]",  badge: "text-[var(--amber-dk)] border-[var(--amber)] bg-white" },
};

interface Props { topics: Topic[]; selected: string; onSelect: (t: string) => void }

export default function TopicBrowser({ topics, selected, onSelect }: Props) {
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState<"All" | "Suggested" | "Completed" | "Needs update">("All");

  const FILTER_TABS = ["All", "Suggested", "Completed", "Needs update"] as const;

  const visible = topics.filter((t) => {
    const matchSearch = t.name.toLowerCase().includes(search.toLowerCase());
    const matchFilter =
      filter === "All" ? true :
      filter === "Suggested" ? t.status === "suggested" :
      filter === "Completed" ? t.status === "shipped" :
      t.status === "needsUpdate";
    return matchSearch && matchFilter;
  });

  return (
    <div>
      <label className="text-[10px] font-semibold text-[var(--gray-50)] uppercase tracking-wide block mb-2">Topic</label>
      <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search topics…"
        className="w-full border border-[var(--border)] rounded-md px-3 py-2 text-[12px] text-[var(--gray-30)] mb-2 outline-none focus:border-[var(--blue)]" />
      <div className="flex gap-1.5 mb-3">
        {FILTER_TABS.map((f) => (
          <button key={f} onClick={() => setFilter(f)}
            className={`px-3 py-1 rounded-full text-[11px] font-medium border transition-colors ${
              f === filter ? "bg-[var(--blue)] text-white border-[var(--blue)]"
                          : "bg-white text-[var(--gray-50)] border-[var(--border)]"
            }`}>{f}</button>
        ))}
      </div>
      <div className="space-y-2 max-h-64 overflow-y-auto pr-1">
        {visible.map((t) => {
          const s = STATE_STYLES[t.status];
          const isSelected = t.name === selected;
          const badgeLabel = t.status === "shipped" ? "Shipped ✓" : t.status === "needsUpdate" ? "New content" : "Suggested";
          const detail = t.status === "shipped" ? `Shipped · ${t.post_count} posts`
            : t.status === "needsUpdate" ? `+${(t.post_count ?? 0) - (t.post_count_at_ship ?? 0)} new posts since ship`
            : `${t.post_count} posts matched`;
          return (
            <button key={t.id} onClick={() => onSelect(t.name)}
              className={`w-full flex justify-between items-center px-4 py-3 rounded-lg border text-left transition-all ${s.border} ${s.bg} ${isSelected ? "ring-2 ring-[var(--blue)]" : ""}`}>
              <div>
                <div className="text-[13px] font-medium text-[var(--gray-10)]">{t.name}</div>
                <div className="text-[11px] text-[var(--gray-50)]">{detail}</div>
              </div>
              <span className={`text-[10px] font-medium px-2 py-0.5 rounded border ${s.badge}`}>{badgeLabel}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
```

- [ ] **Step 3: Create `webapp/frontend/components/pack-builder/ChapterFields.tsx`**

```typescript
"use client";
interface Props { chapters: string[]; onChange: (c: string[]) => void }

export default function ChapterFields({ chapters, onChange }: Props) {
  const update = (i: number, v: string) => {
    const next = [...chapters];
    next[i] = v;
    onChange(next);
  };
  return (
    <div>
      <label className="text-[10px] font-semibold text-[var(--gray-50)] uppercase tracking-wide block mb-2">Chapters</label>
      <div className="space-y-2">
        {chapters.map((ch, i) => (
          <div key={i} className="flex items-center gap-3">
            <span className="text-[10px] font-medium text-[var(--gray-50)] w-10 flex-shrink-0">Ch {i + 1}</span>
            <input value={ch} onChange={(e) => update(i, e.target.value)}
              placeholder={`Chapter ${i + 1} title…`}
              className="flex-1 border border-[var(--border)] rounded-md px-3 py-2 text-[12px] text-[var(--gray-30)] outline-none focus:border-[var(--blue)]" />
          </div>
        ))}
      </div>
    </div>
  );
}
```

- [ ] **Step 4: Create `webapp/frontend/components/pack-builder/ExaminerGrid.tsx`**

```typescript
"use client";
const EXAMINERS = [
  { id: "vutr",            label: "vutr",           color: "var(--blue)" },
  { id: "lucsystemdesign", label: "lucsystemdesign", color: "var(--teal)" },
  { id: "sdcourse",        label: "sdcourse",        color: "var(--gray-50)" },
  { id: "ben-dicken",      label: "ben-dicken",      color: "var(--gray-50)" },
];

interface Props { selected: string[]; onChange: (s: string[]) => void }

export default function ExaminerGrid({ selected, onChange }: Props) {
  const toggle = (id: string) =>
    onChange(selected.includes(id) ? selected.filter((x) => x !== id) : [...selected, id]);
  return (
    <div>
      <label className="text-[10px] font-semibold text-[var(--gray-50)] uppercase tracking-wide block mb-2">Examiners</label>
      <div className="flex flex-wrap gap-2 mb-2">
        {EXAMINERS.map((e) => {
          const active = selected.includes(e.id);
          return (
            <button key={e.id} onClick={() => toggle(e.id)}
              className={`flex items-center gap-2 px-3 py-2.5 rounded-lg border transition-colors ${
                active ? "bg-[var(--blue-bg)] border-[var(--blue)]" : "bg-white border-[var(--border)]"
              }`}>
              <span className="w-2 h-2 rounded-full" style={{ backgroundColor: e.color }} />
              <span className={`text-[11px] font-medium ${active ? "text-[var(--blue)]" : "text-[var(--gray-50)]"}`}>{e.label}</span>
            </button>
          );
        })}
      </div>
      {selected.length > 1 && (
        <div className="inline-flex items-center px-3 py-1 rounded-full bg-[var(--blue-bg)] text-[var(--blue)] text-[11px] font-medium">
          Joint mode · 5 questions each · in parallel
        </div>
      )}
      <p className="text-[10px] text-[var(--gray-70)] mt-2">
        Justin Sung (pedagogy) and Alex Chen (clarity) always included automatically.
      </p>
    </div>
  );
}
```

- [ ] **Step 5: Create `webapp/frontend/components/pack-builder/AttentionDigest.tsx`**

```typescript
import { Topic } from "@/lib/types";
interface Props { topics: Topic[] }

export default function AttentionDigest({ topics }: Props) {
  const flagged = topics.filter((t) => t.status === "needsUpdate");
  if (!flagged.length) return null;
  return (
    <div className="border border-[var(--amber)] bg-[var(--amber-bg)] rounded-lg p-4">
      <div className="text-[11px] font-semibold text-[var(--amber-dk)] mb-2">Topics needing attention</div>
      {flagged.map((t) => (
        <div key={t.id} className="text-[11px] text-[var(--amber-dk)] mb-1">
          <span className="font-medium">{t.name}</span>
          {" — "}+{(t.post_count ?? 0) - (t.post_count_at_ship ?? 0)} new posts since ship.{" "}
          <span className="text-[var(--gray-50)]">Re-extraction recommended.</span>
        </div>
      ))}
    </div>
  );
}
```

- [ ] **Step 6: Create `webapp/frontend/components/pack-builder/RunPreview.tsx`**

```typescript
interface Props {
  authors: string[]; topic: string; chapters: string[];
  examiners: string[]; postCount: number;
}

const STEPS = ["Content ingestion (vault sync)", "PDF generation (headless Chrome)",
  "Verification loop (multi-pass)", "Tri-agent sign-off gate", "Google Drive + git + PR delivery"];

export default function RunPreview({ authors, topic, chapters, examiners, postCount }: Props) {
  const pdfName = [...authors, topic.toLowerCase().replace(/ /g, "_")].join("_") + ".pdf";
  const fields = [
    ["Authors",    authors.join(" · ") || "—"],
    ["Topic",      topic || "—"],
    ["Posts",      postCount ? `${postCount} matched` : "—"],
    ["Chapters",   chapters.filter(Boolean).length + " defined"],
    ["Examiners",  examiners.length ? examiners.join(" + ") + (examiners.length > 1 ? " (joint)" : "") : "—"],
    ["Questions",  examiners.length > 1 ? "5 each per chapter" : "5 per chapter"],
    ["Threshold",  "≥ 9.0 acc / cov / clarity"],
    ["Output PDF", pdfName],
    ["Drive",      "My Drive / Learning Packs"],
  ];
  return (
    <div className="bg-white border border-[var(--border)] rounded-lg p-5">
      <div className="text-[12px] font-semibold text-[var(--gray-30)] mb-4">Run Preview</div>
      <div className="space-y-1.5 mb-5">
        {fields.map(([k, v]) => (
          <div key={k} className="flex text-[11px]">
            <span className="w-28 flex-shrink-0 text-[var(--gray-50)]">{k}</span>
            <span className="text-[var(--gray-10)] font-medium truncate">{v}</span>
          </div>
        ))}
      </div>
      <div className="text-[10px] font-semibold text-[var(--gray-50)] uppercase tracking-wide mb-2">Pipeline Steps</div>
      <div className="space-y-1.5">
        {STEPS.map((s) => (
          <div key={s} className="flex items-center gap-2 text-[12px] text-[var(--gray-30)]">
            <span className="w-4 h-4 rounded bg-[var(--green-bg)] border border-[var(--green)] flex items-center justify-center text-[var(--green)] text-[8px] font-bold flex-shrink-0">✓</span>
            {s}
          </div>
        ))}
      </div>
    </div>
  );
}
```

- [ ] **Step 7: Create `webapp/frontend/app/runs/new/page.tsx`**

```typescript
"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { Topic } from "@/lib/types";
import AuthorChips from "@/components/pack-builder/AuthorChips";
import TopicBrowser from "@/components/pack-builder/TopicBrowser";
import ChapterFields from "@/components/pack-builder/ChapterFields";
import ExaminerGrid from "@/components/pack-builder/ExaminerGrid";
import RunPreview from "@/components/pack-builder/RunPreview";
import AttentionDigest from "@/components/pack-builder/AttentionDigest";

const DEFAULT_CHAPTERS = ["", "", "", "", ""];

export default function NewRunPage() {
  const router = useRouter();
  const [topics, setTopics] = useState<Topic[]>([]);
  const [authors, setAuthors] = useState<string[]>([]);
  const [topic, setTopic] = useState("");
  const [chapters, setChapters] = useState<string[]>(DEFAULT_CHAPTERS);
  const [examiners, setExaminers] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => { api.topics.list().then(setTopics); }, []);

  const selectedTopic = topics.find((t) => t.name === topic);
  const postCount = selectedTopic?.post_count ?? 0;
  const canStart = authors.length > 0 && topic && chapters.some(Boolean) && examiners.length > 0;

  async function start() {
    if (!canStart) return;
    setLoading(true);
    try {
      const run = await api.runs.create({
        authors, examiners, topic,
        chapter_titles: chapters.map((c, i) => c || `Chapter ${i + 1}`),
      });
      router.push(`/runs/${run.id}`);
    } finally { setLoading(false); }
  }

  return (
    <div className="max-w-[1392px] mx-auto px-6 py-6">
      <div className="flex items-center gap-3 mb-6">
        <button onClick={() => router.push("/runs")} className="text-[12px] text-[var(--gray-50)] hover:text-[var(--gray-30)]">← Runs</button>
        <h1 className="text-[18px] font-semibold">New Run</h1>
      </div>
      <div className="grid grid-cols-[1fr_460px] gap-8">
        <div className="space-y-6">
          <AuthorChips selected={authors} onChange={setAuthors} />
          <TopicBrowser topics={topics} selected={topic} onSelect={setTopic} />
          {topic && <ChapterFields chapters={chapters} onChange={setChapters} />}
          <ExaminerGrid selected={examiners} onChange={setExaminers} />
        </div>
        <div className="space-y-4">
          {/* Vault status */}
          {selectedTopic && (
            <div className="bg-white border border-[var(--border)] rounded-lg px-5 py-4">
              <div className="text-[11px] font-semibold text-[var(--gray-50)] mb-1">Vault status</div>
              <div className="text-[13px] font-medium text-[var(--gray-10)]">{postCount} posts matched to {topic}</div>
              <div className="text-[11px] text-[var(--gray-50)]">{selectedTopic.authors.map((a) => `${a}: ${Math.round(postCount / selectedTopic.authors.length)}`).join(" · ")}</div>
            </div>
          )}
          <AttentionDigest topics={topics} />
          <RunPreview authors={authors} topic={topic} chapters={chapters} examiners={examiners} postCount={postCount} />
          <div className="flex gap-3">
            <button onClick={start} disabled={!canStart || loading}
              className={`flex-1 py-2.5 rounded-lg text-[13px] font-semibold text-white transition-opacity ${canStart && !loading ? "bg-[var(--blue)]" : "bg-[var(--gray-90)] cursor-not-allowed"}`}>
              {loading ? "Starting…" : "Start pipeline"}
            </button>
            <button onClick={() => router.push("/runs")}
              className="flex-1 py-2.5 rounded-lg text-[13px] font-medium text-[var(--gray-30)] bg-white border border-[var(--border)]">
              Save as draft
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 8: Test in browser**

Open http://localhost:3000/runs/new — verify: author chips toggle, topic browser shows 3 states (Suggested/Shipped/New content), attention digest appears for Iceberg, chapter fields appear on topic selection, examiner grid shows joint-mode pill with 2+ examiners, preview card updates live, Start button enables only when all required fields filled.

- [ ] **Step 9: Commit**

```bash
git add webapp/frontend/app/runs/new/ webapp/frontend/components/pack-builder/
git commit -m "feat(ui): Pack Builder screen — author chips, topic browser, chapter fields, examiner grid"
```

---

## Task 6: Run Detail screen — Sidebar + Agent Strip + Score Grid

**Files:**
- Create: `webapp/frontend/components/run-detail/Sidebar.tsx`
- Create: `webapp/frontend/components/run-detail/AgentStrip.tsx`
- Create: `webapp/frontend/components/run-detail/ScoreGrid.tsx`
- Create: `webapp/frontend/app/runs/[id]/page.tsx` (skeleton — gaps + log added in Task 7)

**Interfaces:**
- Consumes: `api.runs.get(id)` → `Run`
- Produces: `/runs/{id}` renders Run Detail with working Sidebar, AgentStrip, ScoreGrid

- [ ] **Step 1: Create `webapp/frontend/components/run-detail/Sidebar.tsx`**

```typescript
"use client";
import { Run } from "@/lib/types";

const STAGES: { key: Run["current_stage"]; label: string }[] = [
  { key: "ingestion",    label: "Content ingestion" },
  { key: "generation",  label: "Pack generation" },
  { key: "verification",label: "Verification loop" },
  { key: "sign-off",    label: "Sign-off gate" },
  { key: "delivery",    label: "Delivery" },
];

const STAGE_ORDER = ["ingestion","generation","verification","sign-off","delivery"];

function stageSub(key: string, run: Run): string {
  if (key === "verification") return `Pass ${run.current_pass} · Ch 1–5`;
  if (key === "sign-off") return "Awaiting all agents";
  if (key === "delivery") return run.status === "done" ? "Shipped" : "Not started";
  if (key === "ingestion") return "Vault synced";
  if (key === "generation") return "PDF ready";
  return "";
}

interface Props { run: Run }

export default function Sidebar({ run }: Props) {
  const currentIdx = STAGE_ORDER.indexOf(run.current_stage);

  return (
    <aside className="w-52 flex-shrink-0 bg-white border-r border-[var(--border)] h-full pt-4 pb-6 px-4">
      <div className="mb-4">
        <div className="text-[13px] font-semibold text-[var(--gray-10)] truncate">{run.authors.join(" · ")}</div>
        <div className="text-[11px] text-[var(--gray-50)]">{run.topic} · Pass {run.current_pass}</div>
        <div className="flex gap-1.5 mt-2 flex-wrap">
          {run.authors.map((a) => (
            <span key={a} className="text-[9px] font-medium px-1.5 py-0.5 rounded border border-[var(--blue)] bg-[var(--blue-bg)] text-[var(--blue)]">{a}</span>
          ))}
          <span className={`text-[9px] font-medium px-1.5 py-0.5 rounded border ${
            run.status === "running" ? "border-[var(--amber)] bg-[var(--amber-bg)] text-[var(--amber-dk)]"
            : run.status === "done" ? "border-[var(--green)] bg-[var(--green-bg)] text-[var(--green)]"
            : "border-[var(--red)] bg-[var(--red-bg)] text-[var(--red)]"}`}>
            {run.status}
          </span>
        </div>
      </div>

      <div className="space-y-0">
        {STAGES.map((st, i) => {
          const stIdx = STAGE_ORDER.indexOf(st.key);
          const isDone   = stIdx < currentIdx || (stIdx === currentIdx && run.status === "done");
          const isActive = stIdx === currentIdx && run.status !== "done";
          const isPending = stIdx > currentIdx;

          return (
            <div key={st.key} className="relative">
              {i > 0 && (
                <div className={`absolute left-[15px] -top-3 w-0.5 h-3 ${isDone ? "bg-[var(--green)]" : "bg-[var(--gray-90)]"}`} />
              )}
              {isActive && <div className="absolute left-0 top-0 bottom-0 w-0.5 bg-[var(--blue)]" />}
              <div className={`flex items-start gap-3 py-3 pl-2 ${isActive ? "pl-3" : ""}`}>
                <div className={`w-8 h-8 flex-shrink-0 rounded-full flex items-center justify-center text-[11px] font-bold mt-0.5 ${
                  isDone   ? "bg-[var(--green)] text-white" :
                  isActive ? "border-2 border-[var(--blue)] bg-[var(--blue-bg)] text-[var(--blue)]" :
                             "border-2 border-[var(--gray-90)] bg-[var(--gray-95)] text-[var(--gray-70)]"
                }`}>
                  {isDone ? "✓" : isActive ? "●" : i + 1}
                </div>
                <div>
                  <div className={`text-[12px] font-medium leading-tight ${isDone ? "text-[var(--gray-30)]" : isActive ? "text-[var(--blue)] font-semibold" : "text-[var(--gray-70)]"}`}>
                    {st.label}
                  </div>
                  <div className="text-[10px] text-[var(--gray-50)]">{stageSub(st.key, run)}</div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </aside>
  );
}
```

- [ ] **Step 2: Create `webapp/frontend/components/run-detail/AgentStrip.tsx`**

```typescript
import { Run } from "@/lib/types";

const AGENT_META: Record<string, { color: string; label: string }> = {
  vutr:            { color: "var(--blue)",  label: "vutr" },
  lucsystemdesign: { color: "var(--teal)",  label: "luc" },
  "ben-dicken":    { color: "var(--blue)",  label: "ben" },
  sdcourse:        { color: "var(--blue)",  label: "sdc" },
  justin:          { color: "var(--teal)",  label: "justin" },
  alex:            { color: "var(--amber)", label: "alex" },
};

interface Props { run: Run }

export default function AgentStrip({ run }: Props) {
  const agents = [
    ...run.examiners,
    "justin",
    "alex",
  ];
  const isJoint = run.examiners.length > 1;

  return (
    <div className="flex gap-3 overflow-x-auto pb-1">
      {isJoint ? (
        <div className="flex-shrink-0 w-56 bg-white border border-[var(--border)] rounded-lg p-3 relative overflow-hidden">
          <div className="absolute left-0 top-0 bottom-0 w-0.5 bg-[var(--blue)]" />
          <div className="flex items-center gap-1 mb-2 pl-2">
            {run.examiners.map((e) => {
              const m = AGENT_META[e] ?? { color: "var(--gray-50)", label: e };
              return <span key={e} className="w-2 h-2 rounded-full inline-block" style={{ backgroundColor: m.color }} />;
            })}
            <span className="text-[11px] font-semibold text-[var(--gray-10)] ml-1">{run.examiners.map((e) => AGENT_META[e]?.label ?? e).join(" + ")}</span>
          </div>
          <div className="text-[10px] text-[var(--gray-50)] pl-2">Scoring Ch {run.current_pass} · joint</div>
          <div className="flex items-center gap-2 mt-2 pl-2">
            <span className="text-[10px] font-medium text-[var(--green)]">running</span>
            <span className="text-[10px] text-[var(--gray-70)] ml-auto">joint tok</span>
          </div>
        </div>
      ) : (
        run.examiners.map((e) => {
          const m = AGENT_META[e] ?? { color: "var(--gray-50)", label: e };
          return (
            <AgentCard key={e} color={m.color} label={m.label} task={`Scoring · pass ${run.current_pass}`} status="running" tokens="14.2k" />
          );
        })
      )}
      <AgentCard color="var(--teal)" label="justin" task={`Answering pass ${run.current_pass} Qs`} status="queued" tokens="22.1k" />
      <AgentCard color="var(--amber)" label="alex" task="Clarity audit" status="queued" tokens="6.8k" />
    </div>
  );
}

function AgentCard({ color, label, task, status, tokens }: {
  color: string; label: string; task: string; status: "running" | "queued"; tokens: string
}) {
  return (
    <div className="flex-shrink-0 w-48 bg-white border border-[var(--border)] rounded-lg p-3 relative overflow-hidden">
      <div className="absolute left-0 top-0 bottom-0 w-0.5" style={{ backgroundColor: color }} />
      <div className="flex items-center gap-2 mb-2 pl-2">
        <span className="w-2 h-2 rounded-full" style={{ backgroundColor: color }} />
        <span className="text-[11px] font-semibold text-[var(--gray-10)]">{label}</span>
      </div>
      <div className="text-[10px] text-[var(--gray-50)] pl-2">{task}</div>
      <div className="flex items-center gap-2 mt-2 pl-2">
        <span className={`text-[10px] font-medium ${status === "running" ? "text-[var(--green)]" : "text-[var(--gray-70)]"}`}>{status}</span>
        <span className="text-[10px] text-[var(--gray-70)] ml-auto">{tokens} tok</span>
      </div>
    </div>
  );
}
```

- [ ] **Step 3: Create `webapp/frontend/components/run-detail/ScoreGrid.tsx`**

```typescript
import { Run, Chapter } from "@/lib/types";

interface Props { run: Run }

function ChapterCell({ chapter, passNum, examiners }: { chapter: Chapter; passNum: number; examiners: string[] }) {
  const latest = chapter.passes.find((p) => p.pass_num === passNum) ?? chapter.passes.at(-1);
  const isJoint = examiners.length > 1;

  const dotColors: Record<string, string> = {
    vutr: "var(--blue)", lucsystemdesign: "var(--teal)",
    "ben-dicken": "var(--blue)", sdcourse: "var(--blue)",
  };

  return (
    <div className="bg-white border border-[var(--border)] rounded-lg p-3 flex flex-col gap-1">
      <div className="text-[11px] font-semibold text-[var(--gray-50)]">Ch {chapter.index + 1}</div>
      {latest ? (
        <>
          {isJoint && (
            <div className="flex gap-1">
              {examiners.map((e) => <span key={e} className="w-2 h-2 rounded-full" style={{ backgroundColor: dotColors[e] ?? "var(--blue)" }} />)}
            </div>
          )}
          <div className="text-[20px] font-semibold text-[var(--gray-10)] leading-tight">
            {latest.acc_score?.toFixed(1)} / {latest.cov_score?.toFixed(1)}
          </div>
          <div className="text-[9px] text-[var(--gray-50)]">acc / cov</div>
          <div className="border-t border-[var(--border)] my-1" />
          <div className="flex items-center gap-2">
            <span className="text-[8px] font-medium px-1.5 py-0.5 rounded bg-[var(--amber-bg)] text-[var(--amber-dk)] border border-[var(--amber)]">alex</span>
            <span className="text-[13px] font-semibold text-[var(--amber-dk)]">{latest.alex_score?.toFixed(1) ?? "—"}</span>
          </div>
          {(() => {
            const pass = (latest.acc_score ?? 0) >= 9.0 && (latest.cov_score ?? 0) >= 9.0 && (latest.alex_score ?? 0) >= 9.0;
            return (
              <div className={`text-[10px] font-semibold mt-1 ${pass ? "text-[var(--green)]" : "text-[var(--red)]"}`}>
                {pass ? "all ✓" : "below threshold"}
              </div>
            );
          })()}
        </>
      ) : (
        <div className="text-[13px] text-[var(--gray-70)] mt-2">queued</div>
      )}
    </div>
  );
}

export default function ScoreGrid({ run }: Props) {
  return (
    <div>
      <div className="text-[10px] font-semibold text-[var(--gray-50)] uppercase tracking-wide mb-2">
        Chapter Scores · Pass {run.current_pass}
      </div>
      <div className="grid grid-cols-5 gap-3">
        {run.chapters.map((ch) => (
          <ChapterCell key={ch.id} chapter={ch} passNum={run.current_pass} examiners={run.examiners} />
        ))}
      </div>
    </div>
  );
}
```

- [ ] **Step 4: Create `webapp/frontend/app/runs/[id]/page.tsx`** (skeleton)

```typescript
"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";
import { Run } from "@/lib/types";
import Sidebar from "@/components/run-detail/Sidebar";
import AgentStrip from "@/components/run-detail/AgentStrip";
import ScoreGrid from "@/components/run-detail/ScoreGrid";

export default function RunDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [run, setRun] = useState<Run | null>(null);

  useEffect(() => {
    api.runs.get(Number(id)).then(setRun);
  }, [id]);

  if (!run) return <div className="p-8 text-[var(--gray-50)]">Loading…</div>;

  if (run.current_stage === "sign-off" || run.status === "done") {
    // Sign-off + Delivery view — added in Task 8
    return <div className="p-8 text-[var(--gray-50)]">Sign-off screen coming in Task 8</div>;
  }

  return (
    <div className="flex h-[calc(100vh-56px)]">
      <Sidebar run={run} />
      <div className="flex-1 overflow-y-auto">
        {/* Top bar */}
        <div className="sticky top-0 bg-white border-b border-[var(--border)] px-6 py-3.5 flex items-center justify-between z-10">
          <span className="text-[14px] font-semibold text-[var(--gray-10)]">
            Verification loop · Pass {run.current_pass}
          </span>
          {run.examiners.length > 1 && (
            <span className="text-[10px] font-medium px-2.5 py-1 rounded-full bg-[var(--blue-bg)] text-[var(--blue)]">
              Joint · {run.examiners.length + 2} agents active
            </span>
          )}
        </div>

        <div className="px-6 py-5 space-y-6">
          <AgentStrip run={run} />
          <ScoreGrid run={run} />
          {/* GapsList + LiveLog added in Task 7 */}
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 5: Test in browser**

Open http://localhost:3000/runs — click the "lucsystem · Kafka Design" row (status: running, verification). Verify: sidebar shows stages with active indicator on Verification, agent strip shows examiner + justin + alex cards, score grid shows 5 chapter cells with scores from pass 2.

- [ ] **Step 6: Commit**

```bash
git add webapp/frontend/app/runs/ webapp/frontend/components/run-detail/
git commit -m "feat(ui): Run Detail — sidebar stage list, agent strip, score grid"
```

---

## Task 7: Gaps list + Live Log (SSE)

**Files:**
- Create: `webapp/frontend/components/run-detail/GapsList.tsx`
- Create: `webapp/frontend/components/run-detail/LiveLog.tsx`
- Create: `webapp/backend/routers/pipeline.py`
- Modify: `webapp/frontend/app/runs/[id]/page.tsx` (add GapsList + LiveLog)

**Interfaces:**
- Consumes: `GET /runs/{id}/stream` → SSE stream of `{type, ts, agent, message}` events
- Produces: Live log scrolls in real-time; gaps list reflects latest pass gaps

- [ ] **Step 1: Create `webapp/backend/routers/pipeline.py`**

```python
import asyncio
import json
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sse_starlette.sse import EventSourceResponse
from database import get_db
from models import Run

router = APIRouter(prefix="/runs", tags=["pipeline"])

@router.post("/{run_id}/start")
def start_pipeline(run_id: int, db: Session = Depends(get_db)):
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        from fastapi import HTTPException
        raise HTTPException(404, "Run not found")
    # In v1, pipeline is triggered manually — this endpoint is a hook for future integration
    return {"status": "queued", "run_id": run_id}

@router.get("/{run_id}/stream")
async def stream_run(run_id: int, db: Session = Depends(get_db)):
    """SSE stream — emits mock log lines for any running run."""
    run = db.query(Run).filter(Run.id == run_id).first()
    examiners = run.examiners if run else ["vutr"]

    async def event_gen():
        agents = examiners + ["justin", "alex", "system"]
        msgs = [
            (agents[0], f"Pass {run.current_pass if run else 1} started — generating 5 questions for Ch 3"),
            ("justin",  "Answering questions from combined pool"),
            (agents[0], "Ch 3 scored — waiting for alex audit"),
            ("alex",    "Clarity audit queued for Ch 3"),
            ("system",  "Gap flagged in Ch 3 — coverage below 9.0"),
        ]
        for agent, msg in msgs:
            data = json.dumps({
                "ts": datetime.utcnow().strftime("%H:%M:%S"),
                "agent": agent,
                "message": msg,
            })
            yield {"data": data}
            await asyncio.sleep(1.2)

    return EventSourceResponse(event_gen())
```

- [ ] **Step 2: Create `webapp/frontend/components/run-detail/GapsList.tsx`**

```typescript
import { Run } from "@/lib/types";

const TAG_COLORS: Record<string, { bg: string; border: string; text: string }> = {
  joint: { bg: "var(--blue-bg)",   border: "var(--blue)",    text: "var(--blue)" },
  alex:  { bg: "var(--amber-bg)",  border: "var(--amber)",   text: "var(--amber-dk)" },
};

interface Props { run: Run }

export default function GapsList({ run }: Props) {
  const latestPassNum = run.current_pass;
  const gaps = run.chapters.flatMap((ch) => {
    const pr = ch.passes.find((p) => p.pass_num === latestPassNum) ?? ch.passes.at(-1);
    return (pr?.gaps ?? []).map((g) => ({ ...g, chIndex: ch.index }));
  });

  if (!gaps.length) return null;

  return (
    <div>
      <div className="text-[10px] font-semibold text-[var(--gray-50)] uppercase tracking-wide mb-2">
        Gaps · Pass {latestPassNum}
      </div>
      <div className="space-y-2">
        {gaps.map((g) => {
          const tagType = g.source_tag.includes("alex") ? "alex" : "joint";
          const style = TAG_COLORS[tagType] ?? TAG_COLORS.joint;
          return (
            <div key={g.id} className="flex items-center gap-3 bg-white border border-[var(--border)] rounded-lg px-4 py-2">
              <span className="text-[9px] font-medium px-2 py-0.5 rounded border flex-shrink-0"
                style={{ backgroundColor: style.bg, borderColor: style.border, color: style.text }}>
                {g.source_tag}
              </span>
              <span className="text-[11px] text-[var(--gray-30)] truncate">{g.description}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
```

- [ ] **Step 3: Create `webapp/frontend/components/run-detail/LiveLog.tsx`**

```typescript
"use client";
import { useEffect, useRef, useState } from "react";

interface LogLine { ts: string; agent: string; message: string }

const AGENT_COLORS: Record<string, string> = {
  vutr: "var(--blue)", lucsystemdesign: "var(--teal)", "ben-dicken": "var(--blue)",
  sdcourse: "var(--blue)", justin: "var(--teal)", alex: "var(--amber)", system: "var(--gray-70)",
};

interface Props { runId: number }

export default function LiveLog({ runId }: Props) {
  const [lines, setLines] = useState<LogLine[]>([]);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const es = new EventSource(`http://localhost:8000/runs/${runId}/stream`);
    es.onmessage = (e) => {
      try {
        const line: LogLine = JSON.parse(e.data);
        setLines((prev) => [...prev, line]);
      } catch {}
    };
    es.onerror = () => es.close();
    return () => es.close();
  }, [runId]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [lines]);

  return (
    <div>
      <div className="text-[10px] font-semibold text-[var(--gray-50)] uppercase tracking-wide mb-2">Live Log</div>
      <div className="bg-[var(--gray-10)] rounded-lg p-4 h-40 overflow-y-auto font-[family-name:var(--font-geist-mono)] text-[10px]">
        {lines.length === 0 && <span className="text-[var(--gray-70)]">Waiting for events…</span>}
        {lines.map((l, i) => (
          <div key={i} className="flex gap-3 mb-1">
            <span className="text-[var(--gray-70)] flex-shrink-0">{l.ts}</span>
            <span className="flex-shrink-0" style={{ color: AGENT_COLORS[l.agent] ?? "var(--gray-70)" }}>{l.agent}</span>
            <span className="text-[var(--gray-95)]">{l.message}</span>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
```

- [ ] **Step 4: Update `webapp/frontend/app/runs/[id]/page.tsx`** — add GapsList + LiveLog

Replace the `{/* GapsList + LiveLog added in Task 7 */}` comment with:

```typescript
          <GapsList run={run} />
          <LiveLog runId={run.id} />
```

And add imports at the top:

```typescript
import GapsList from "@/components/run-detail/GapsList";
import LiveLog from "@/components/run-detail/LiveLog";
```

- [ ] **Step 5: Test SSE stream**

```bash
curl -N http://localhost:8000/runs/2/stream
```

Expected: 5 SSE `data:` events emitted over ~6 seconds with JSON `{ts, agent, message}`.

- [ ] **Step 6: Test in browser**

Open http://localhost:3000/runs/2 — verify: live log section animates with incoming events one line at a time, log auto-scrolls to bottom.

- [ ] **Step 7: Commit**

```bash
git add webapp/frontend/components/run-detail/GapsList.tsx \
        webapp/frontend/components/run-detail/LiveLog.tsx \
        webapp/frontend/app/runs/ \
        webapp/backend/routers/pipeline.py
git commit -m "feat(ui): gaps list + SSE live log stream"
```

---

## Task 8: Sign-off + Delivery screen

**Files:**
- Create: `webapp/frontend/components/sign-off/SignOffCards.tsx`
- Create: `webapp/frontend/components/sign-off/DeliveryChecklist.tsx`
- Modify: `webapp/frontend/app/runs/[id]/page.tsx` (replace placeholder with full sign-off view)

**Interfaces:**
- Consumes: `run.sign_offs`, `run.delivery_steps` from `RunOut`
- Produces: `/runs/{id}` when `current_stage === "sign-off"` or `status === "done"` renders Sign-off + Delivery layout

- [ ] **Step 1: Create `webapp/frontend/components/sign-off/SignOffCards.tsx`**

```typescript
import { SignOff } from "@/lib/types";

const AGENT_META: Record<string, { initials: string; role: string; color: string; bgColor: string }> = {
  vutr:            { initials: "V",  role: "Examiner",          color: "var(--blue)",    bgColor: "var(--blue-bg)" },
  lucsystemdesign: { initials: "L",  role: "Examiner",          color: "var(--teal)",    bgColor: "var(--teal-bg)" },
  "ben-dicken":    { initials: "B",  role: "Examiner",          color: "var(--blue)",    bgColor: "var(--blue-bg)" },
  sdcourse:        { initials: "S",  role: "Examiner",          color: "var(--blue)",    bgColor: "var(--blue-bg)" },
  justin:          { initials: "JS", role: "Pedagogy reviewer", color: "var(--teal)",    bgColor: "var(--teal-bg)" },
  alex:            { initials: "AC", role: "Clarity auditor",   color: "var(--amber-dk)",bgColor: "var(--amber-bg)" },
};

interface Props { signOffs: SignOff[] }

export default function SignOffCards({ signOffs }: Props) {
  const allApproved = signOffs.every((s) => s.status === "approved");
  return (
    <div className="space-y-4">
      {allApproved && (
        <div className="flex items-center gap-3 bg-[var(--green-bg)] border border-[var(--green)] rounded-lg px-5 py-3">
          <span className="text-[18px] font-bold text-[var(--green)]">✓</span>
          <div>
            <div className="text-[14px] font-semibold text-[var(--green)]">All chapters passed ≥ 9.0</div>
            <div className="text-[11px] text-[var(--green)]">All agents have approved — delivery is ready</div>
          </div>
        </div>
      )}

      <div className="text-[10px] font-semibold text-[var(--gray-50)] uppercase tracking-wide">Sign-off Gate</div>
      {signOffs.map((so) => {
        const meta = AGENT_META[so.agent] ?? { initials: so.agent[0].toUpperCase(), role: so.role, color: "var(--gray-50)", bgColor: "var(--gray-95)" };
        const borderColor = so.status === "approved" ? "var(--green)" : so.status === "rejected" ? "var(--red)" : "var(--amber)";
        const badgeBg = so.status === "approved" ? "var(--green-bg)" : so.status === "rejected" ? "var(--red-bg)" : "var(--amber-bg)";
        const badgeColor = so.status === "approved" ? "var(--green)" : so.status === "rejected" ? "var(--red)" : "var(--amber-dk)";
        const badgeLabel = so.status === "approved" ? "Approved ✓" : so.status === "rejected" ? "Rejected ✗" : "Auditing…";
        return (
          <div key={so.id} className="bg-white rounded-lg p-5 border" style={{ borderColor }}>
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg flex items-center justify-center text-[13px] font-bold" style={{ backgroundColor: meta.bgColor, color: meta.color }}>
                  {meta.initials}
                </div>
                <div>
                  <div className="text-[13px] font-semibold text-[var(--gray-10)]">{so.agent}</div>
                  <div className="text-[11px] text-[var(--gray-50)]">{meta.role}</div>
                </div>
              </div>
              <span className="text-[10px] font-semibold px-2.5 py-1 rounded border" style={{ backgroundColor: badgeBg, color: badgeColor, borderColor: badgeColor }}>{badgeLabel}</span>
            </div>
            <div className="border-t border-[var(--border)] pt-3">
              {so.status === "approved" && so.criteria.length > 0 ? (
                <div className="space-y-1.5">
                  {so.criteria.map((c) => (
                    <div key={c} className="flex items-center gap-2 text-[11px] text-[var(--gray-30)]">
                      <span className="w-1.5 h-1.5 rounded-full bg-[var(--green)] flex-shrink-0" />
                      {c}
                    </div>
                  ))}
                </div>
              ) : so.status === "pending" ? (
                <p className="text-[11px] text-[var(--amber-dk)]">Auditing final PDF across all 5 chapters…</p>
              ) : (
                <p className="text-[11px] text-[var(--red)]">Rejected — one fix round will run automatically before retry.</p>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
```

- [ ] **Step 2: Create `webapp/frontend/components/sign-off/DeliveryChecklist.tsx`**

```typescript
"use client";
import { DeliveryStep } from "@/lib/types";

interface Props { steps: DeliveryStep[]; allApproved: boolean; onShip: () => void; shipping: boolean }

export default function DeliveryChecklist({ steps, allApproved, onShip, shipping }: Props) {
  const note = "Delivery runs automatically once all agents approve. A rejected sign-off triggers one fix round before retry.";

  return (
    <div className="space-y-4">
      <div className="text-[10px] font-semibold text-[var(--gray-50)] uppercase tracking-wide">Delivery Steps</div>
      <div className="space-y-3">
        {steps.map((step, i) => {
          const isDone = step.status === "done";
          return (
            <div key={step.id} className="flex gap-4 items-start">
              <div className={`w-8 h-8 flex-shrink-0 rounded-full flex items-center justify-center text-[11px] font-bold ${isDone ? "bg-[var(--green)] text-white" : "bg-[var(--gray-95)] border-2 border-[var(--gray-90)] text-[var(--gray-70)]"}`}>
                {isDone ? "✓" : i + 1}
              </div>
              <div className="flex-1">
                <div className={`flex items-center justify-between mb-1`}>
                  <span className={`text-[13px] font-semibold ${isDone ? "text-[var(--green)]" : "text-[var(--gray-30)]"}`}>{step.label}</span>
                  <span className={`text-[9px] font-medium px-2 py-0.5 rounded border ${isDone ? "border-[var(--green)] bg-[var(--green-bg)] text-[var(--green)]" : "border-[var(--gray-90)] bg-[var(--gray-95)] text-[var(--gray-70)]"}`}>
                    {isDone ? "done" : step.status}
                  </span>
                </div>
                {step.detail && (
                  <div className="bg-[var(--gray-10)] rounded px-3 py-2 font-[family-name:var(--font-geist-mono)] text-[10px] text-[var(--gray-95)]">
                    {step.detail}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
      <div className="bg-[var(--gray-97)] border border-[var(--border)] rounded-lg p-4 text-[11px] text-[var(--gray-50)]">{note}</div>
      <div className="flex gap-3">
        <button onClick={onShip} disabled={!allApproved || shipping}
          className={`flex-1 py-2.5 rounded-lg text-[13px] font-semibold text-white transition-all ${allApproved && !shipping ? "bg-[var(--blue)] hover:opacity-90" : "bg-[var(--gray-90)] cursor-not-allowed text-[var(--gray-70)]"}`}>
          {shipping ? "Shipping…" : allApproved ? "Ship" : "Ship — awaiting approvals"}
        </button>
      </div>
    </div>
  );
}
```

- [ ] **Step 3: Update `webapp/frontend/app/runs/[id]/page.tsx`** — replace placeholder sign-off section

Replace the early return for sign-off with:

```typescript
import SignOffCards from "@/components/sign-off/SignOffCards";
import DeliveryChecklist from "@/components/sign-off/DeliveryChecklist";

// ... inside the component, replace the early return block:
  const [shipping, setShipping] = useState(false);

  if (run.current_stage === "sign-off" || run.status === "done") {
    const allApproved = run.sign_offs.every((s) => s.status === "approved");
    return (
      <div className="flex h-[calc(100vh-56px)]">
        <Sidebar run={run} />
        <div className="flex-1 overflow-y-auto">
          <div className="sticky top-0 bg-white border-b border-[var(--border)] px-6 py-3.5 z-10">
            <span className="text-[14px] font-semibold text-[var(--gray-10)]">Sign-off Gate + Delivery</span>
            <span className="ml-3 text-[12px] text-[var(--gray-50)]">{run.title} · Pass {run.current_pass}</span>
          </div>
          <div className="px-6 py-5 grid grid-cols-2 gap-8">
            <div>
              <SignOffCards signOffs={run.sign_offs} />
            </div>
            <div>
              <DeliveryChecklist
                steps={run.delivery_steps}
                allApproved={allApproved}
                onShip={() => setShipping(true)}
                shipping={shipping}
              />
            </div>
          </div>
        </div>
      </div>
    );
  }
```

- [ ] **Step 4: Test sign-off screen**

Open http://localhost:3000/runs/3 (ben-dicken, stage: sign-off) — verify: two-column layout, 3 sign-off cards (ben + justin + alex), delivery checklist with 5 monospace detail rows, Ship button disabled until all sign-offs approved.

- [ ] **Step 5: Commit**

```bash
git add webapp/frontend/components/sign-off/ webapp/frontend/app/runs/
git commit -m "feat(ui): Sign-off + Delivery screen — sign-off cards, delivery checklist, ship button"
```

---

## Task 9: Polish, startup scripts, README

**Files:**
- Create: `webapp/start.sh`
- Modify: `webapp/frontend/next.config.ts` (suppress hydration warning)
- Create: `webapp/README.md`

**Interfaces:**
- Produces: Single `./webapp/start.sh` command boots both servers

- [ ] **Step 1: Create `webapp/start.sh`**

```bash
#!/usr/bin/env bash
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "Starting backend…"
cd "$ROOT/backend"
[ ! -d .venv ] && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
source .venv/bin/activate
python seed.py 2>/dev/null || true
uvicorn main:app --port 8000 --reload &
BACKEND_PID=$!

echo "Starting frontend…"
cd "$ROOT/frontend"
[ ! -d node_modules ] && npm install
npm run dev &
FRONTEND_PID=$!

echo ""
echo "  Backend:  http://localhost:8000"
echo "  Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl-C to stop both servers."

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT TERM
wait
```

- [ ] **Step 2: Make executable**

```bash
chmod +x webapp/start.sh
```

- [ ] **Step 3: Test startup**

```bash
./webapp/start.sh
```

Open http://localhost:3000 — verify full app loads, all 4 screens navigable.

- [ ] **Step 4: Commit**

```bash
git add webapp/start.sh webapp/README.md webapp/frontend/next.config.ts
git commit -m "feat(ui): startup script — boots backend + frontend with one command"
```

---

## Self-Review Checklist

- [x] All spec sections have a task: Run List ✓, Pack Builder ✓, Run Detail ✓, Sign-off + Delivery ✓
- [x] No TBD/TODO in any step
- [x] Types consistent across tasks (e.g. `Run["current_stage"]` matches backend `status` field values)
- [x] SSE stream endpoint matches `EventSource` URL in `LiveLog.tsx`
- [x] Color tokens consistent with spec (`#185FA5` = `var(--blue)`)
- [x] All imports reference files created in prior tasks
- [x] Joint examiner mode handled in AgentStrip, ScoreGrid, ExaminerGrid, SignOffCards
