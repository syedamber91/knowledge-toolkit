"""Seed the remaining admitted concept notes across several NotebookLM
notebooks, one source per note, resumable.

Chunked at CHUNK notes per notebook rather than one giant notebook: the
per-notebook source cap is not documented anywhere we control, and discovering
it at source 51 of 184 would waste the whole run. Chunking also means a single
notebook going bad costs one chunk, not everything.

Resumable by design -- state records which notes are already seeded and which
notebook holds them, so a re-run after an auth expiry or a network blip picks
up exactly where it stopped instead of re-uploading.
"""
from __future__ import annotations

import json
import sys
import time

sys.path.insert(0, "/Users/syedamberiqbal/Documents/workspace/Claude_Code/SOIC_Scraper/.claude/worktrees/soic-method/src")

from soic_senses.notebook_client import add_text_source, create_notebook
from soic_senses.notebook_preflight import require_auth

STATE = "/tmp/corpus_nb_state.json"
CHUNK = 45


def main() -> None:
    notes = json.load(open("/tmp/rest_notes.json"))
    try:
        state = json.load(open(STATE))
    except FileNotFoundError:
        state = {"notebooks": {}, "seeded": {}}

    require_auth(job_hours=1.0)

    chunks = [notes[i:i + CHUNK] for i in range(0, len(notes), CHUNK)]
    print(f"{len(notes)} notes -> {len(chunks)} notebooks of <={CHUNK}", flush=True)

    for ci, chunk in enumerate(chunks):
        key = f"corpus{ci}"
        if key not in state["notebooks"]:
            state["notebooks"][key] = create_notebook(f"SOIC Check-Extraction -- corpus {ci}")
            json.dump(state, open(STATE, "w"))
            print(f"created {key}: {state['notebooks'][key]}", flush=True)
        nbid = state["notebooks"][key]

        for n in chunk:
            if n["slug"] in state["seeded"]:
                continue
            for attempt in (1, 2, 3):
                try:
                    add_text_source(nbid, n["text"], n["slug"])
                    state["seeded"][n["slug"]] = key
                    json.dump(state, open(STATE, "w"))
                    print(f"  {key} ok {n['slug']}", flush=True)
                    break
                except Exception as exc:  # noqa: BLE001
                    msg = f"{type(exc).__name__}: {exc}"
                    print(f"  {key} attempt {attempt} FAIL {n['slug']}: {msg}", flush=True)
                    # An expired session will not heal by retrying -- stop the
                    # whole run so the operator refreshes once, rather than
                    # grinding through 180 notes failing three times each.
                    if "Authentication expired" in msg:
                        print("AUTH EXPIRED -- stopping; refresh and re-run to resume", flush=True)
                        return
                    if attempt < 3:
                        time.sleep(3 * attempt)

    print(f"\nSEED_DONE seeded={len(state['seeded'])}/{len(notes)} "
          f"notebooks={list(state['notebooks'].values())}", flush=True)


if __name__ == "__main__":
    main()
