"""Dump the 459 tagged notes + split flag to output/system_one_train/notes.jsonl so the VPS needs no vault access."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import OUT, load_notes, split
notes = load_notes(); train, _ = split(notes); tr = {n["slug"] for n in train}
with open(OUT / "notes.jsonl", "w") as f:
    for n in notes: f.write(json.dumps({**n, "split": "train" if n["slug"] in tr else "test"}) + "\n")
print(len(notes), "notes,", len(tr), "train")
