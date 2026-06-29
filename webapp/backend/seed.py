"""Run once to populate dev data: python seed.py"""
from datetime import datetime, timedelta
from database import SessionLocal, engine, Base
from models import Run, Chapter, PassRecord, SignOff, DeliveryStep, Topic

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
