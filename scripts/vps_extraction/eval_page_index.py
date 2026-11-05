"""Score page_index on the golden page_grep rows: is the gold page in the top-k, and does a made-up number get refused?"""
import json
import sys
from pathlib import Path

from vps_extraction.page_index import answer_or_refuse, build_index, search

KS = (1, 3, 5, 10)


def fake(token: str) -> str:
    """Same shape, different digits (keeps commas/dots), e.g. 172,695 -> 839,047. Never equals the real token."""
    swap = str.maketrans("0123456789", "5678901234")
    return token.translate(swap)


def main(golden: Path, pages_dir: Path) -> None:
    conn = build_index(pages_dir)
    rows = [r for r in map(json.loads, golden.open()) if r["kind"] == "page_grep"]
    hits = {k: 0 for k in KS}
    misses, false_pass, answered = [], [], 0
    for r in rows:
        ranked = [p for p, _ in search(conn, r["question"], max(KS))]
        for k in KS:
            if set(ranked[:k]) & set(r["pages"]):
                hits[k] += 1
        if not set(ranked[:5]) & set(r["pages"]):
            misses.append((r["id"], r["question"], r["pages"], ranked[:5]))
        a = answer_or_refuse(conn, r["question"], r["tokens"][0], k=5)
        answered += a["status"] == "ok" and a["page"] in r["pages"]
        t = r["tokens"][0]
        if fake(t) == t:  # no digits to change (e.g. "Nil"): cannot make a fabrication, skip
            continue
        f = answer_or_refuse(conn, r["question"], fake(t), k=5)
        if f["status"] == "ok":
            false_pass.append(r["id"])
    n = len(rows)
    print(f"rows={n}")
    for k in KS:
        print(f"hit@{k}: {hits[k]}/{n}")
    print(f"answered with a gold page (k=5): {answered}/{n}")
    print(f"fabricated number wrongly accepted: {len(false_pass)}/{n} {false_pass}")
    for m in misses:
        print("MISS", m)


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
