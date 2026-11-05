"""Score call_grep / announcement_grep / deck_grep golden rows against the one multi-source index.

usage: eval_multi_index.py GOLDEN.jsonl BIOCON_DATA_DIR
Gold hit = a retrieved chunk of the right source whose label starts with the row's date (calls: the
call's date from source_file, + page in row.pages; announcements: row_date; decks: date in source_file).
Fake check: same-shape wrong digits must not be found on any retrieved chunk (else a refusal would fail).
"""
import gzip
import json
import re
import sys
from pathlib import Path

from vps_extraction.multi_index import (build, chunk_announcements, chunk_call, chunk_deck_layout, search)
from vps_extraction.page_index import _has_number

KINDS = {"call_grep": "call", "announcement_grep": "announcement", "deck_grep": "deck"}


def fake(token: str) -> str:
    return token.translate(str.maketrans("0123456789", "5678901234"))


def load_chunks(data: Path):
    chunks = []
    for f in sorted((data / "calls").glob("call-*.txt.gz")):
        m = re.search(r"call-(\d{4}-\d{2}-\d{2})-(q\dfy\d{2})", f.name)
        chunks += chunk_call(gzip.open(f, "rt", errors="replace").read(), m.group(1), m.group(2))
    for f in sorted((data / "decks-layout").glob("deck-*.txt")):
        chunks += chunk_deck_layout(f.read_text(errors="replace"))
    seen = set()
    for f in ("announcements-2021-2026-08-30.csv", "announcements-latest.csv"):
        for c in chunk_announcements((data / f).read_text(errors="replace")):
            if c.label not in seen:
                seen.add(c.label)
                chunks.append(c)
    return chunks


def is_gold(row, source, label) -> bool:
    if source != KINDS[row["kind"]]:
        return False
    if row["kind"] == "announcement_grep":
        return label.startswith(row["row_date"])
    date = re.search(r"(\d{4}-\d{2}-\d{2})", row["source_file"]).group(1)
    if row["kind"] == "deck_grep":
        return date in label and any(label.endswith(f" p{p}") for p in row["pages"])
    return label.startswith(date + " p") and int(label.rsplit(" p", 1)[1]) in row["pages"]


def main(golden: Path, data: Path) -> None:
    chunks = load_chunks(data)
    conn = build(chunks)
    text_of = {(c.source, c.label): c.text for c in chunks}
    rows = [r for r in map(json.loads, golden.open()) if r["kind"] in KINDS]
    print(f"chunks={len(chunks)} rows={len(rows)}")
    for kind in KINDS:
        kr = [r for r in rows if r["kind"] == kind]
        if not kr:
            continue
        ranks, fakes, misses = [], [], []
        for r in kr:
            # each K is a real search(k=K): the one-per-source rule depends on K
            hit_k = {K: any(is_gold(r, h[0], h[1]) for h in search(conn, r["question"], k=K)) for K in (1, 3, 5, 10)}
            hits = search(conn, r["question"], k=5)
            ranks.append(min((K for K in hit_k if hit_k[K]), default=None))
            if not hit_k[5]:
                misses.append((r["id"], r["question"], [h[1] for h in hits]))
            for t in r["tokens"]:
                if re.search(r"\d", t):
                    ft = fake(t)
                    if any(_has_number(text_of[(h[0], h[1])], ft) for h in hits):
                        fakes.append((r["id"], t, ft))
        n = len(kr)
        print(f"[{kind}] rows={n} " + " ".join(f"hit@{k}={sum(1 for x in ranks if x and x <= k)}/{n}" for k in (1, 3, 5, 10))
              + f" fake_accepted={len(fakes)} {fakes}")
        for m in misses:
            print("  MISS", m)


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
