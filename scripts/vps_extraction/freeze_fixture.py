"""Save fetched bytes + a sidecar (source_url, fetched_at, sha256). Verify later."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def freeze(body: bytes, source_url: str, out_dir, name: str, now: str = None) -> Path:
    if not body:  # empty read / shell page must fail loudly, never be saved
        raise ValueError(f"empty body from {source_url}")
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    p = out / name
    p.write_bytes(body)
    meta = {
        "source_url": source_url,
        "fetched_at": now or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sha256": _sha(body),
    }
    (out / f"{name}.meta.json").write_text(json.dumps(meta, indent=2))
    return p


def verify(path) -> bool:
    p = Path(path)
    meta = json.loads(Path(f"{p}.meta.json").read_text())
    return _sha(p.read_bytes()) == meta["sha256"]
