"""Jev run #2 (owner-approved 2026-10-03, option A): ALL spoken test passages, same 12 noul questions as run #1
PLUS one 13-way choice question (12 tags + "none") in the SAME call. Never prints passage text or the key. stdlib only.
  jev_label2.py run PASSAGES OUT.jsonl"""
import json, os, sys, time, urllib.request, urllib.error
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import TAGS
from laya_data import DEFS
from jev_label import QUESTIONS as NOULS, URL

CHOICE = {"type": "choice", "instructions": "Which investing topic is this lecture passage mainly about?",
          "criteria": {**{t: DEFS[t] for t in TAGS}, "none": "None of these topics (small talk, admin, or off-topic)."}}
Q = {**NOULS, "topic": CHOICE}


def call(key, text, tries=4):
    body = json.dumps({"state": text, "model": "jev-latest", "questions": Q}).encode()
    for k in range(tries):
        req = urllib.request.Request(URL, body, {"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
        try:
            return json.load(urllib.request.urlopen(req, timeout=60))
        except urllib.error.HTTPError as e:
            if e.code in (429, 529) and k < tries - 1: time.sleep(2 ** (k + 1)); continue
            raise SystemExit(f"HTTP {e.code} from Jev (stopping; body not printed)")
        except urllib.error.URLError:
            if k < tries - 1: time.sleep(2 ** (k + 1)); continue
            raise SystemExit("network error talking to Jev")


def main():
    key = os.environ.get("TYPESAFE_API_KEY") or sys.exit("TYPESAFE_API_KEY not set")
    rows = [json.loads(l) for l in open(sys.argv[2])]
    done = {json.loads(l)["id"] for l in open(sys.argv[3])} if os.path.exists(sys.argv[3]) else set()
    with open(sys.argv[3], "a") as f:
        for i, r in enumerate(rows):
            if r["id"] in done: continue
            res = call(key, r["text"]); a = res["answers"]
            f.write(json.dumps({"id": r["id"], "note": r["note"], "tags": r["tags"], "model": res.get("model"),
                                "jev": {t: a[t]["noul"] for t in TAGS}, "choice": a["topic"]["probabilities"]}) + "\n"); f.flush()
            if i % 100 == 0: print(f"{i}/{len(rows)}", flush=True)
    print("done", len(rows))


if __name__ == "__main__":
    main()
