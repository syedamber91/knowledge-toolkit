"""One page = one chunk, searched with SQLite FTS5 (BM25). No model, no network.

Pages are files named pNNN.md; the number is the page (an annual report's "AR pN"). Anything else
(manifest.json) is ignored. A number is only ever "answered" if its digits are on a retrieved page;
otherwise the answer is a refusal. This proves the digits are on that page, not that they belong to
the line item asked about -- a human or label check is still needed for that.
"""
import re
import sqlite3
from pathlib import Path

_PAGE = re.compile(r"^p(\d+)\.md$")


_YEAR = re.compile(r"\b(?:FY\s?(?:20)?\d{2}\s?-\s?(\d{2})|FY\s?20(\d{2})|FY\s?(\d{2})|(\d{2})\s?FY)\b", re.I)


def normalize_years(text: str) -> str:
    """26FY, FY 2026, FY2025-26 -> FY26. Years only; nothing question-specific."""
    return _YEAR.sub(lambda m: "FY" + next(g for g in m.groups() if g), text)


def build_index(pages_dir) -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.execute("create table pages(page integer primary key, text text)")
    conn.execute("create virtual table fts using fts5(text, content='pages', content_rowid='page')")
    for f in sorted(Path(pages_dir).iterdir()):
        m = _PAGE.match(f.name)
        if m:
            conn.execute("insert into pages values (?, ?)", (int(m.group(1)), f.read_text(errors="replace")))
    for page, text in conn.execute("select page, text from pages").fetchall():
        conn.execute("insert into fts(rowid, text) values (?, ?)", (page, normalize_years(text)))
    return conn


def _terms(query: str):
    return re.findall(r"[A-Za-z0-9]+", query)


_STOP = frozenset("a an and are as at be by did do does for from how in is it its of on or s the to was were what when which who with".split())


def query_terms(query: str):
    """Question words minus filler (what/was/the/...) so they cannot outweigh the real clue."""
    return [t for t in _terms(normalize_years(query)) if t.lower() not in _STOP]


def match_expr(terms) -> str:
    """OR of quoted terms. A long word also matches by its first 8 letters, so 'capitalised' finds
    'capitalisation' (BM25 alone sees two different words). Short words stay exact."""
    parts = []
    for t in terms:
        parts.append(f'"{t}"')
        if len(t) >= 10:
            parts.append(f'"{t[:8]}"*')
    return " OR ".join(parts)


def search(conn, query: str, k: int = 5):
    """[(page, bm25_score)] best first; any-word match so a long question still finds the page."""
    terms = query_terms(query)
    if not terms:
        return []
    match = match_expr(terms)
    rows = conn.execute("select rowid, bm25(fts) from fts where fts match ? order by bm25(fts) limit ?",
                        (match, k)).fetchall()
    return [(page, score) for page, score in rows]


def _has_number(text: str, number: str) -> bool:
    """Whole-number match: 999 is not found inside 11,999, 9990 or 0.999."""
    pat = r"(?<![\d,])(?<!\d\.)" + re.escape(number) + r"(?!\d)(?!,\d)(?!\.\d)"
    return re.search(pat, text) is not None


def answer_or_refuse(conn, query: str, number: str, k: int = 5) -> dict:
    for page, _ in search(conn, query, k):
        text = conn.execute("select text from pages where page=?", (page,)).fetchone()[0]
        if _has_number(text, number):
            return {"status": "ok", "page": page}
    return {"status": "refuse"}
