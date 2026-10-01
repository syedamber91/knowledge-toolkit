"""Write output/system_one_train/laya/{train,test}.jsonl (Laya typed-decisions schema)."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import OUT, load_notes, split
from laya_data import row

notes = load_notes(); train, test = split(notes)
d = OUT / "laya"; d.mkdir(exist_ok=True)
for name, ns in (("train", train), ("test", test)):
    with open(d / f"{name}.jsonl", "w") as f:
        for n in ns: f.write(json.dumps(row(n, name)) + "\n")
print(f"train={len(train)} notes ({len(train)*12} questions)  test={len(test)} notes ({len(test)*12} questions) -> {d}")
