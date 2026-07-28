"""Forensic pilot: seed a NotebookLM notebook with the 38 forensic-tagged
admitted concept notes, ONE SOURCE PER NOTE.

One-source-per-note (rather than batching several notes into one source) is
deliberate: the whole point of the pilot is to test whether NotebookLM can
propose checks that are then DETERMINISTICALLY verifiable against the note
that supposedly states them. That verification needs to know which note a
claim came from, so source granularity must match note granularity.
"""
from __future__ import annotations

import json
import sys
import time

sys.path.insert(0, "/Users/syedamberiqbal/Documents/workspace/Claude_Code/SOIC_Scraper/.claude/worktrees/soic-method/src")

from soic_senses.notebook_client import add_text_source, create_notebook

STATE = "/tmp/forensic_nb_state.json"


def main() -> None:
    notes = json.load(open("/tmp/forensic_notes.json"))
    try:
        state = json.load(open(STATE))
    except FileNotFoundError:
        state = {"notebook_id": None, "seeded": []}

    if not state["notebook_id"]:
        nb = create_notebook("SOIC Check-Extraction -- forensic (pilot)")
        state["notebook_id"] = nb
        json.dump(state, open(STATE, "w"))
        print(f"created notebook: {nb}", flush=True)
    nbid = state["notebook_id"]

    for i, n in enumerate(notes, 1):
        if n["slug"] in state["seeded"]:
            print(f"  [{i}/{len(notes)}] skip (already seeded) {n['slug']}", flush=True)
            continue
        for attempt in (1, 2, 3):
            try:
                add_text_source(nbid, n["text"], n["slug"])
                state["seeded"].append(n["slug"])
                json.dump(state, open(STATE, "w"))
                print(f"  [{i}/{len(notes)}] ok {n['slug']}", flush=True)
                break
            except Exception as exc:  # noqa: BLE001
                print(f"  [{i}/{len(notes)}] attempt {attempt} FAILED {n['slug']}: "
                      f"{type(exc).__name__}: {exc}", flush=True)
                if attempt == 3:
                    print(f"  [{i}/{len(notes)}] GIVING UP on {n['slug']}", flush=True)
                else:
                    time.sleep(3 * attempt)

    print(f"\nnotebook_id={nbid}  seeded={len(state['seeded'])}/{len(notes)}", flush=True)


if __name__ == "__main__":
    main()
