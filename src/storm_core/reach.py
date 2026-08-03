"""Optional retrieval-breadth layer for the STORM research lane.

Wraps Agent Reach (Panniantong/Agent-Reach, MIT) so a STORM lens agent can pull
dated evidence from Exa / X / Reddit / RSS through ONE uniform, structured call
instead of ad-hoc scraping.

Three rules this module exists to enforce -- see
docs/superpowers/specs/2026-08-03-agent-reach-evaluation.md:

1. **Absent-safe.** Agent Reach not installed, config missing, command renamed
   upstream, subprocess failing or hanging -- every one of those is a SKIP WITH
   A REASON, never an exception. STORM must run exactly as it did before this
   module existed when the layer is unavailable.
2. **Opt-in.** Off unless STORM_REACH_ENABLED is truthy.
3. **No hardcoded argv.** Every command lives in configs/reach_channels.yaml,
   because Agent Reach installs unpinned and deliberately swaps backends.

The `run` and `which` seams are injected so the whole module is unit-testable
offline with no Agent Reach install and no network -- the same seam pattern
instagram_toolkit uses for `post_fetch`.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import yaml
from pydantic import BaseModel

from storm_core import config

# (returncode, stdout, stderr)
RunResult = Tuple[int, str, str]
RunFn = Callable[[Sequence[str]], RunResult]
WhichFn = Callable[[str], Optional[str]]

_URL_RE = re.compile(r"https?://\S+")
_SNIPPET_MAX = 500

_TITLE_KEYS = ("title", "headline", "name", "text", "content", "body")
_URL_KEYS = ("url", "link", "permalink", "href")
_SNIPPET_KEYS = ("snippet", "summary", "description", "text", "content", "body", "excerpt")
_DATE_KEYS = ("date", "published", "published_at", "created_at", "created", "timestamp")
_AUTHOR_KEYS = ("author", "user", "username", "handle", "by", "screen_name")
_LIST_KEYS = ("results", "items", "data", "entries", "posts", "tweets")


class ReachChannel(BaseModel):
    name: str
    label: str = ""
    requires_auth: bool = False
    enabled: bool = True
    argv: List[str] = []


class ChannelStatus(BaseModel):
    name: str
    available: bool
    reason: str = ""
    executable: str = ""
    requires_auth: bool = False


class ReachResult(BaseModel):
    channel: str
    title: str = ""
    url: str = ""
    snippet: str = ""
    published: Optional[str] = None
    author: Optional[str] = None


class ReachSearch(BaseModel):
    query: str
    enabled: bool
    results: List[ReachResult] = []
    channels_used: List[str] = []
    # channel name -> why it produced nothing
    channels_skipped: Dict[str, str] = {}


# --------------------------------------------------------------------------
# registry
# --------------------------------------------------------------------------

def load_channels(path: Optional[Path] = None) -> List[ReachChannel]:
    """Read the channel registry. A missing/unreadable file yields [] (absent-safe)."""
    p = Path(path) if path is not None else config.REACH_CONFIG
    if not p.exists():
        return []
    try:
        raw = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return []
    out: List[ReachChannel] = []
    for entry in raw.get("channels") or []:
        if not isinstance(entry, dict):
            continue
        # YAML 1.1 turns bare `off`/`on`/`no`/`yes` into booleans, so a channel
        # named that way arrives as False rather than a string. Coerce instead of
        # dropping it silently -- a vanished channel is exactly the kind of quiet
        # failure this repo refuses to ship. (Quote such names in the registry.)
        name = entry.get("name")
        if name is None or not str(name).strip():
            continue
        entry = {**entry, "name": str(name)}
        try:
            out.append(ReachChannel(**entry))
        except Exception:
            continue
    return out


def pinned_ref(path: Optional[Path] = None) -> str:
    """The Agent Reach ref this registry was written against ('' if unrecorded)."""
    p = Path(path) if path is not None else config.REACH_CONFIG
    if not p.exists():
        return ""
    try:
        raw = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return ""
    return str(raw.get("pinned_ref") or "")


def _select(channels: List[ReachChannel], only: Optional[Sequence[str]]) -> List[ReachChannel]:
    if not only:
        return channels
    wanted = {c.strip().lower() for c in only if c and c.strip()}
    return [c for c in channels if c.name.lower() in wanted]


# --------------------------------------------------------------------------
# probe
# --------------------------------------------------------------------------

def probe(
    only: Optional[Sequence[str]] = None,
    *,
    path: Optional[Path] = None,
    which: Optional[WhichFn] = None,
) -> List[ChannelStatus]:
    """Report per-channel availability without executing anything."""
    which = which or shutil.which
    statuses: List[ChannelStatus] = []
    for ch in _select(load_channels(path), only):
        if not ch.enabled:
            statuses.append(ChannelStatus(
                name=ch.name, available=False, reason="disabled in registry",
                requires_auth=ch.requires_auth))
            continue
        if not ch.argv:
            statuses.append(ChannelStatus(
                name=ch.name, available=False, reason="no argv configured",
                requires_auth=ch.requires_auth))
            continue
        exe = which(ch.argv[0])
        statuses.append(ChannelStatus(
            name=ch.name,
            available=bool(exe),
            reason="" if exe else f"{ch.argv[0]} not on PATH (is Agent Reach installed?)",
            executable=exe or "",
            requires_auth=ch.requires_auth,
        ))
    return statuses


# --------------------------------------------------------------------------
# search
# --------------------------------------------------------------------------

def _default_run(argv: Sequence[str]) -> RunResult:
    proc = subprocess.run(
        list(argv),
        capture_output=True,
        text=True,
        timeout=config.REACH_TIMEOUT_SEC,
        check=False,
    )
    return proc.returncode, proc.stdout or "", proc.stderr or ""


def _render_argv(argv: Sequence[str], query: str, limit: int) -> List[str]:
    return [a.replace("{query}", query).replace("{limit}", str(limit)) for a in argv]


def _first(d: dict, keys: Sequence[str]) -> str:
    for k in keys:
        v = d.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
        if isinstance(v, (int, float)):
            return str(v)
    return ""


def _clip(text: str) -> str:
    text = " ".join((text or "").split())
    return text if len(text) <= _SNIPPET_MAX else text[: _SNIPPET_MAX - 1] + "…"


def _from_mapping(channel: str, d: dict) -> ReachResult:
    title = _first(d, _TITLE_KEYS)
    snippet = _first(d, _SNIPPET_KEYS)
    return ReachResult(
        channel=channel,
        title=_clip(title),
        url=_first(d, _URL_KEYS),
        snippet=_clip(snippet or title),
        published=_first(d, _DATE_KEYS) or None,
        author=_first(d, _AUTHOR_KEYS) or None,
    )


def normalize(channel: str, stdout: str) -> List[ReachResult]:
    """Best-effort stdout -> ReachResult[].

    Agent Reach fronts several independent CLIs with no shared output contract,
    so: try JSON, then fall back to URL-bearing lines, then to the raw text as a
    single result. Returning the raw text is deliberate -- an unparsed answer is
    still evidence a lens can read, whereas dropping it silently would hide a
    format change behind an empty result set.
    """
    text = (stdout or "").strip()
    if not text:
        return []

    try:
        payload = json.loads(text)
    except (ValueError, TypeError):
        payload = None

    if payload is not None:
        rows = None
        if isinstance(payload, list):
            rows = payload
        elif isinstance(payload, dict):
            for k in _LIST_KEYS:
                if isinstance(payload.get(k), list):
                    rows = payload[k]
                    break
            if rows is None:
                rows = [payload]
        if rows is not None:
            out: List[ReachResult] = []
            for row in rows:
                if isinstance(row, dict):
                    out.append(_from_mapping(channel, row))
                elif isinstance(row, str) and row.strip():
                    out.append(ReachResult(channel=channel, snippet=_clip(row)))
            if out:
                return out

    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    with_urls = [ln for ln in lines if _URL_RE.search(ln)]
    if with_urls:
        results = []
        for ln in with_urls:
            m = _URL_RE.search(ln)
            url = m.group(0).rstrip(".,);]") if m else ""
            results.append(ReachResult(channel=channel, url=url, snippet=_clip(ln)))
        return results

    return [ReachResult(channel=channel, snippet=_clip(text))]


def search(
    query: str,
    only: Optional[Sequence[str]] = None,
    limit: int = 5,
    *,
    path: Optional[Path] = None,
    run: Optional[RunFn] = None,
    which: Optional[WhichFn] = None,
    enabled: Optional[bool] = None,
) -> ReachSearch:
    """Query the configured channels. Never raises on a channel failure."""
    is_on = config.reach_enabled() if enabled is None else enabled
    channels = _select(load_channels(path), only)

    if not is_on:
        return ReachSearch(
            query=query,
            enabled=False,
            channels_skipped={c.name: "reach layer disabled (set STORM_REACH_ENABLED=1)"
                              for c in channels} or {"*": "reach layer disabled"},
        )

    run = run or _default_run
    which = which or shutil.which

    out = ReachSearch(query=query, enabled=True)
    statuses = {s.name: s for s in probe(only, path=path, which=which)}

    for ch in channels:
        status = statuses.get(ch.name)
        if status is None or not status.available:
            out.channels_skipped[ch.name] = status.reason if status else "unknown channel"
            continue
        argv = _render_argv(ch.argv, query, limit)
        try:
            code, stdout, stderr = run(argv)
        except subprocess.TimeoutExpired:
            out.channels_skipped[ch.name] = f"timed out after {config.REACH_TIMEOUT_SEC}s"
            continue
        except Exception as exc:  # noqa: BLE001 - absent-safe by contract
            out.channels_skipped[ch.name] = f"{type(exc).__name__}: {exc}"
            continue
        if code != 0:
            detail = _clip(stderr) or f"exit {code}"
            out.channels_skipped[ch.name] = f"command failed: {detail}"
            continue
        results = normalize(ch.name, stdout)
        if not results:
            out.channels_skipped[ch.name] = "no results"
            continue
        out.results.extend(results[:limit] if limit and limit > 0 else results)
        out.channels_used.append(ch.name)

    return out
