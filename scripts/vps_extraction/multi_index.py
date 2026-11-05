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

from vps_extraction.page_index import normalize_years, query_terms


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
    conn.execute("create table chunks(id integer primary key, source text, label text, text text)")
    conn.execute("create virtual table fts using fts5(text, content='chunks', content_rowid='id')")
    for c in chunks:
        cur = conn.execute("insert into chunks(source, label, text) values (?,?,?)", (c.source, c.label, c.text))
        conn.execute("insert into fts(rowid, text) values (?, ?)",
                     (cur.lastrowid, normalize_years(f"{c.tags} {c.label} {c.text}")))
    return conn


def search(conn, query: str, k: int = 5, source: str = None):
    """[(source, label, bm25)] best first; optional restriction to one source."""
    terms = query_terms(query)
    if not terms:
        return []
    match = " OR ".join(f'"{t}"' for t in terms)
    sql = ("select c.source, c.label, bm25(fts) from fts join chunks c on c.id = fts.rowid "
           "where fts match ?" + (" and c.source = ?" if source else "") + " order by bm25(fts) limit ?")
    args = (match, source, k) if source else (match, k)
    return conn.execute(sql, args).fetchall()
