"""passages.jsonl -> Laya-format train rows (one 12-way choice question each). usage: make_laya_choice_jsonl.py IN OUT [LIMIT]"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from laya_choice_data import row
rows = [json.loads(l) for l in open(sys.argv[1])]
if len(sys.argv) > 3: rows = rows[: int(sys.argv[3])]
with open(sys.argv[2], "w") as f:
    for r in rows: f.write(json.dumps(row(r["id"], r["text"], r["tags"])) + "\n")
print(len(rows), "rows ->", sys.argv[2])
