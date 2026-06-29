from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
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
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run

@router.post("", response_model=RunOut, status_code=201)
def create_run(body: RunCreate, db: Session = Depends(get_db)):
    if len(body.chapter_titles) != 5:
        raise HTTPException(status_code=422, detail="chapter_titles must have exactly 5 items")
    title = " · ".join(body.authors) + " · " + body.topic
    run = Run(title=title, authors=body.authors, examiners=body.examiners,
              topic=body.topic, status="running", current_stage="ingestion")
    db.add(run); db.flush()
    for i, t in enumerate(body.chapter_titles):
        db.add(Chapter(run_id=run.id, index=i, title=t))
    for agent in body.examiners:
        db.add(SignOff(run_id=run.id, agent=agent, role="Examiner", status="pending"))
    db.add(SignOff(run_id=run.id, agent="justin", role="Pedagogy reviewer", status="pending"))
    db.add(SignOff(run_id=run.id, agent="alex", role="Clarity auditor", status="pending"))
    for idx, (label, detail) in enumerate(zip(DELIVERY_STEP_LABELS, DELIVERY_STEP_DETAILS)):
        db.add(DeliveryStep(run_id=run.id, index=idx, label=label, status="waiting",
                            detail=detail.format(topic=body.topic.lower().replace(" ", "_"))))
    db.commit(); db.refresh(run)
    return run
