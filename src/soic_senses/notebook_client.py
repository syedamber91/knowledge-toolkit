"""Live company-notebook query sense: NotebookLM, productionizing ask_notebook.py.

This is the third piece both the Venus Pipes and KEI Industries experiments
depended on: the screener client fetches numbers, this fetches the
qualitative interrogation a persona-style deep-dive actually runs on
(the "ask 7 questions of the company's notebook" pattern from the PI
Industries POC). Every answer here is a live NotebookLM response, receipts-
tagged so a downstream write-up can cite exactly which question produced it.

Cannot be exercised live in this sandbox -- notebooklm_mcp isn't installed
and no cached auth is reachable here -- so every import of that package is
deferred into a small seam (`_load_cached_tokens` / `_build_client`) that
tests replace with a mock. The seam is also the graceful-degradation point:
a company with no registered notebook_id never reaches NotebookLM at all,
so a caller (e.g. a decision-engine briefing) can catch
NotebookUnavailableError and fall back to screener-only analysis, clearly
labeled, exactly as the plan requires.
"""

from __future__ import annotations

import datetime
import json
from pathlib import Path
from typing import Dict, List, Optional, Union

import yaml


class NotebookUnavailableError(Exception):
    """Raised when a company has no registered notebook_id.

    Callers should catch this and fall back to screener-only analysis
    rather than treating it as a hard failure -- most companies in the
    corpus don't have a NotebookLM notebook yet.
    """


class NotebookAuthError(Exception):
    """Raised when there is no cached NotebookLM auth token."""


class NotebookQueryError(Exception):
    """Raised when the NotebookLM client itself raises during a query
    (expired session, RPC error, timeout, ...). Wraps the original
    exception's message rather than letting the underlying exception type
    leak across the seam.
    """


def load_notebook_registry(path: Union[str, Path]) -> Dict[str, str]:
    """Load the company -> notebook_id map from configs/notebooks.yaml."""
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    return dict(data.get("notebooks", {}))


def resolve_notebook_id(company: str, registry: Dict[str, str]) -> str:
    """Look up a company's notebook_id, case-insensitively.

    Raises NotebookUnavailableError (naming the company) rather than
    returning None -- the caller is expected to catch this specific
    error and degrade gracefully, not to check a sentinel value.
    """
    key = company.upper()
    for registered_company, notebook_id in registry.items():
        if registered_company.upper() == key:
            return notebook_id
    raise NotebookUnavailableError(
        f"No notebook registered for {company!r} -- fall back to screener-only analysis"
    )


def _load_cached_tokens():
    from notebooklm_mcp.auth import load_cached_tokens

    return load_cached_tokens()


def _build_client(tokens):
    from notebooklm_mcp.api_client import NotebookLMClient

    return NotebookLMClient(
        cookies=tokens.cookies,
        csrf_token=tokens.csrf_token,
        session_id=tokens.session_id,
    )


def _require_client():
    tokens = _load_cached_tokens()
    if not tokens:
        raise NotebookAuthError("no cached tokens (~/.notebooklm-mcp/auth.json)")
    return _build_client(tokens)


def create_notebook(title: str) -> str:
    """Create a new NotebookLM notebook, returning its notebook_id.

    Raises NotebookQueryError (naming the title) if the client call
    returns None -- notebooklm_mcp's own convention for "the RPC didn't
    give back a usable result" -- rather than returning None onward and
    letting a caller silently proceed with no notebook.
    """
    client = _require_client()
    notebook = client.create_notebook(title=title)
    if not notebook:
        raise NotebookQueryError(f"create_notebook returned no result for title {title!r}")
    return notebook.id


def add_text_source(notebook_id: str, text: str, title: str) -> None:
    """Add a pasted-text source to a notebook (the only way to get a raw
    transcript into NotebookLM -- there is no file-upload API).

    Raises NotebookQueryError (naming the notebook_id) if the client call
    returns None.
    """
    client = _require_client()
    result = client.add_text_source(notebook_id, text, title=title)
    if not result:
        raise NotebookQueryError(f"add_text_source returned no result for notebook {notebook_id!r}")


def list_notebooks() -> List[object]:
    """List all NotebookLM notebooks visible to the cached session."""
    client = _require_client()
    return client.list_notebooks()


def ask_notebook(
    notebook_id: str,
    question: str,
    conversation_id: Optional[str] = None,
    timeout: float = 120.0,
) -> Dict[str, object]:
    """Ask one question of a NotebookLM notebook, returning
    {answer, conversation_id, turn_number}.

    Raises NotebookAuthError if there's no cached session, and
    NotebookQueryError (wrapping the underlying message) if the query
    itself fails -- mirroring ask_notebook.py's auth-vs-query distinction
    without depending on its exit-code convention.
    """
    tokens = _load_cached_tokens()
    if not tokens:
        raise NotebookAuthError("no cached tokens (~/.notebooklm-mcp/auth.json)")

    client = _build_client(tokens)
    try:
        result = client.query(
            notebook_id,
            query_text=question,
            conversation_id=conversation_id,
            timeout=timeout,
        )
    except Exception as exc:  # noqa: BLE001 - deliberately broad: wrap, never leak the client's exception type
        raise NotebookQueryError(str(exc)) from exc

    return {
        "answer": result.get("answer", ""),
        "conversation_id": result.get("conversation_id"),
        "turn_number": result.get("turn_number"),
    }


def append_receipt(
    log_path: Union[str, Path],
    company: str,
    question: str,
    result: Dict[str, object],
) -> str:
    """Append one Q&A receipt to a JSONL log, tagged with a stable,
    per-company incrementing [Qn] -- fixing the POC's v1/v2 citation
    drift, where re-running a question could silently reuse or skip a
    tag. The tag is derived by counting this company's prior entries in
    the same log file, so it's stable across process restarts.
    """
    log_path = Path(log_path)
    existing_count = 0
    if log_path.exists():
        for line in log_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            if json.loads(line).get("company") == company:
                existing_count += 1

    tag = f"[Q{existing_count + 1}]"
    entry = {
        "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "company": company,
        "tag": tag,
        "question": question,
        **result,
    }
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return tag


def query_company(
    company: str,
    question: str,
    registry_path: Union[str, Path],
    log_path: Optional[Union[str, Path]] = None,
    conversation_id: Optional[str] = None,
) -> Dict[str, object]:
    """Resolve a company to its notebook, ask a question, and (if
    log_path is given) log a receipt. Returns the answer dict plus the
    receipt's tag.

    Raises NotebookUnavailableError WITHOUT calling ask_notebook when
    the company has no registered notebook -- the graceful-degradation
    point the caller (e.g. a decision-engine briefing) is meant to catch.
    """
    registry = load_notebook_registry(registry_path)
    notebook_id = resolve_notebook_id(company, registry)

    result = ask_notebook(notebook_id, question, conversation_id=conversation_id)

    tag = "[unlogged]"
    if log_path is not None:
        tag = append_receipt(log_path, company=company, question=question, result=result)

    return {**result, "tag": tag}
