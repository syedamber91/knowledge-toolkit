"""One 12-way CHOICE question per passage, soft gold = uniform over the passage's tags.
(12 yes/no questions per passage would be 12x the items: far too slow on a CPU-only VPS.)"""
import json
from common import TAGS
from laya_data import DEFS

QID = "topic"
QUESTION = {"type": "choice", "instructions": "Which investing topics is this lecture passage mainly about?",
            "criteria": {t: DEFS[t] for t in TAGS}}


def row(rid, text, tags):
    p = {t: (1.0 / len(tags) if t in tags else 0.0) for t in TAGS}
    return {"id": rid, "state": json.dumps({"passage": text}), "questions": json.dumps({QID: QUESTION}),
            "gold": json.dumps({QID: {"type": "choice", "label": tags[0], "probabilities": p}})}
