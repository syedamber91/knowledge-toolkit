"""One FTS5 index over many sources. Each chunk keeps (source, label) so every hit is citable.

call = one page (form-feed split) of an earnings-call transcript; deck = one slide page from the
decks-layout files; announcement = one CSV row. Same year-spelling fix and BM25 as page_index.
Derived files (qa-pairs, management-text, deck-numbers) are NOT indexed: they repeat the raw text.
"""
import csv
import io
import re
import sqlite3
from typing import NamedTuple

from vps_extraction.page_index import match_expr, normalize_years, query_terms


class Chunk(NamedTuple):
    source: str
    label: str
    text: str
    tags: str = ""  # searchable but not shown: e.g. the quarter, which lives in the file name


def chunk_call(text: str, date: str, quarter: str = ""):
    return [Chunk("call", f"{date} p{i}", t, quarter) for i, t in enumerate(text.split("\f"), 1) if t.strip()]


_DECK_HDR = re.compile(r"^=== (\S+) page (\d+) ===$", re.M)


def chunk_deck_layout(text: str):
    heads = list(_DECK_HDR.finditer(text))
    out = []
    for i, m in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        body = text[m.end():end].strip()
        if body:
            out.append(Chunk("deck", f"{m.group(1)} p{m.group(2)}", body))
    return out


def chunk_announcements(csv_text: str):
    out = []
    for r in csv.DictReader(io.StringIO(csv_text)):
        label = f"{r['sort_date'][:10]} {r['desc']} {r['url']}"
        out.append(Chunk("announcement", label, f"{r['desc']}. {r['text']}"))
    return out


def build(chunks) -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.execute("create table chunks(id integer primary key, source text, label text, text text, tags text)")
    conn.execute("create virtual table fts using fts5(text, content='chunks', content_rowid='id')")
    for c in chunks:
        cur = conn.execute("insert into chunks(source, label, text, tags) values (?,?,?,?)",
                           (c.source, c.label, c.text, c.tags))
        conn.execute("insert into fts(rowid, text) values (?, ?)",
                     (cur.lastrowid, normalize_years(f"{c.tags} {c.label} {c.text}")))
    return conn


_QUARTER = re.compile(r"\bq([1-4])\s?fy\s?(?:20)?(\d{2})\b", re.I)
_POOL = 200  # candidates fetched before the quarter and one-per-source rules reorder them


def query_quarter(query: str):
    """'Q3FY24' / 'Q3 FY 2024' in the question -> 'q3fy24'; None if no quarter was asked."""
    m = _QUARTER.search(normalize_years(query))
    return f"q{m.group(1)}fy{m.group(2)}" if m else None


_SOURCE_WORDS = (("call", r"calls?|transcripts?"), ("deck", r"decks?|slides?|presentations?"),
                 ("announcement", r"announcements?|press release|filings?"))


def query_source(query: str):
    """'... in the Q4FY24 call' -> 'call'; None if no source word, or if two sources are named."""
    found = [s for s, w in _SOURCE_WORDS if re.search(rf"\b(?:{w})\b", query, re.I)]
    return found[0] if len(found) == 1 else None


def search(conn, query: str, k: int = 5, source: str = None):
    """[(source, label, bm25)] best first; optional restriction to one source.

    Two general rules on top of BM25 (neither is about any one question):
    - a quarter named in the question puts chunks of that quarter first (it is in the file name,
      not the page text, so BM25 cannot weigh it enough);
    - a source word ("call", "deck", "press release") puts that source first, so short deck pages
      cannot push out the call the question named. (A forced slot per source was tried: it cost
      more hits than it won, so it is not used.)
    """
    terms = query_terms(query)
    if not terms:
        return []
    match = match_expr(terms)
    sql = ("select c.source, c.label, bm25(fts), c.tags from fts join chunks c on c.id = fts.rowid "
           "where fts match ?" + (" and c.source = ?" if source else "") + " order by bm25(fts) limit ?")
    args = (match, source, _POOL) if source else (match, _POOL)
    rows = conn.execute(sql, args).fetchall()
    want = query_source(query)
    if want:
        hit = [r for r in rows if r[0] == want]
        rows = hit + [r for r in rows if r[0] != want]
    q = query_quarter(query)
    if q:
        hit = [r for r in rows if q in f"{r[3]} {r[1]}".lower()]
        rows = hit + [r for r in rows if r not in hit]
    return [r[:3] for r in rows[:k]]
