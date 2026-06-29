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

# Seed topics — authors_post_count gives per-author vault breakdown
#               suggested_chapters are pre-determined from vault content density
TOPICS = [
    {
        "name": "Apache Spark",
        "authors": ["vutr"],
        "authors_post_count": {"vutr": 47},
        "post_count": 47,
        "status": "shipped",
        "suggested_chapters": [
            "Spark Architecture & Execution Model",
            "Shuffle, Partitioning & Data Locality",
            "Catalyst Optimizer & Tungsten",
            "Memory Management & Spilling",
            "Structured Streaming Internals",
        ],
    },
    {
        "name": "Kafka",
        "authors": ["lucsystemdesign", "vutr"],
        "authors_post_count": {"lucsystemdesign": 31, "vutr": 22},
        "post_count": 53,
        "status": "suggested",
        "suggested_chapters": [
            "Kafka Architecture & Log Storage",
            "Partitions, Replication & Leader Election",
            "Consumer Groups & Offset Management",
            "Exactly-once Semantics & Transactions",
            "Kafka Streams & ksqlDB",
        ],
    },
    {
        "name": "Iceberg",
        "authors": ["vutr"],
        "authors_post_count": {"vutr": 18},
        "post_count": 18,
        "status": "needsUpdate",
        "suggested_chapters": [
            "Table Format & Snapshot Model",
            "Hidden Partitioning & Partition Evolution",
            "Schema Evolution & Column Mapping",
            "Time Travel & Branching",
            "Compaction, Maintenance & Engine Integration",
        ],
    },
    {
        "name": "dbt",
        "authors": ["vutr", "lucsystemdesign"],
        "authors_post_count": {"vutr": 8, "lucsystemdesign": 4},
        "post_count": 12,
        "status": "suggested",
        "suggested_chapters": [
            "dbt Project Structure & DAG",
            "Models, Sources & Seeds",
            "Tests, Documentation & Freshness",
            "Materializations & Incremental Patterns",
            "dbt Cloud, CI/CD & Environment Management",
        ],
    },
    {
        "name": "ClickHouse",
        "authors": ["vutr"],
        "authors_post_count": {"vutr": 22},
        "post_count": 22,
        "status": "suggested",
        "suggested_chapters": [
            "MergeTree Engine & Data Organisation",
            "Primary Keys, Sparse Indexes & Skipping Indexes",
            "Aggregating, Replacing & Collapsing MergeTree",
            "Distributed Tables & Sharding",
            "Query Optimization & Materialized Views",
        ],
    },
    {
        "name": "Raft Consensus",
        "authors": ["sdcourse"],
        "authors_post_count": {"sdcourse": 15},
        "post_count": 15,
        "status": "suggested",
        "suggested_chapters": [
            "Leader Election & Term Management",
            "Log Replication & Commitment Rules",
            "Safety, Liveness & Network Partitions",
            "Membership Changes & Joint Consensus",
            "Raft in Practice: etcd, CockroachDB, TiKV",
        ],
    },
    {
        "name": "Database Internals",
        "authors": ["ben-dicken"],
        "authors_post_count": {"ben-dicken": 18},
        "post_count": 18,
        "status": "shipped",
        "suggested_chapters": [
            "Storage Engines: B-Trees vs LSM-Trees",
            "Indexing Strategies & Access Patterns",
            "Transactions, MVCC & Isolation Levels",
            "Query Execution & Join Algorithms",
            "Replication & Distributed Consistency",
        ],
    },
]

for td in TOPICS:
    t = Topic(
        name=td["name"],
        authors=td["authors"],
        authors_post_count=td["authors_post_count"],
        post_count=td["post_count"],
        suggested_chapters=td["suggested_chapters"],
        status=td["status"],
        post_count_at_ship=td["post_count"] - 6 if td["status"] in ("shipped", "needsUpdate") else None,
        shipped_at=datetime.utcnow() - timedelta(days=14) if td["status"] in ("shipped", "needsUpdate") else None,
    )
    db.add(t)
db.commit()
db.close()
print("Seeded OK")
