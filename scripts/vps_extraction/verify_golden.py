"""Mechanically check golden rows that CAN be checked. Others return ok=None (human / retrieval test)."""
import json
import re
import sys
from pathlib import Path

from vps_extraction.golden_candidates import check_row

_ARITH = re.compile(r"^[\d\s.+\-*/()]+$")


def verify_row(row, pages_dir, fixture_text):
    k = row["kind"]
    if k == "page_grep":
        r = check_row({"pages": row["pages"], "numbers": row["tokens"]}, pages_dir)
        return {"id": row["id"], "ok": not r["missing"], "missing": r["missing"]}
    if k == "fixture_grep":
        miss = [t for t in row["tokens"] if t not in (fixture_text or "")]
        return {"id": row["id"], "ok": not miss, "missing": miss}
    if k == "derived":
        if not _ARITH.match(row["calc"]):
            raise ValueError(f"not plain arithmetic: {row['calc']}")
        got = eval(row["calc"], {"__builtins__": {}})  # ponytail: regex-gated arithmetic only
        return {"id": row["id"], "ok": abs(got - row["value"]) <= row.get("tol", 0.5), "got": got}
    return {"id": row["id"], "ok": None}


if __name__ == "__main__":
    gold, pages, fx = sys.argv[1:4]
    ft = Path(fx).read_text(encoding="utf8", errors="replace")
    res = [verify_row(json.loads(l), pages, ft) for l in Path(gold).read_text().splitlines() if l.strip()]
    for r in res:
        print(r)
    print("checked:", sum(r["ok"] is not None for r in res), "pass:", sum(r["ok"] is True for r in res),
          "fail:", sum(r["ok"] is False for r in res), "needs-human:", sum(r["ok"] is None for r in res))
