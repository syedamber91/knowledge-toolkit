"""Forensic pilot, verification stage -- the load-bearing part.

NotebookLM proposes; this decides. Mirrors the G2 discipline already used on
concept notes (`soic_wiki.gates.verify_cited_quotes`): a claim is only trusted
if the text it cites actually contains it. Zero LLM, zero cost, so it can gate
every future extraction run without adding to the token bill.

Two independent things are checked per proposed test, because they fail in
different ways:

  QUOTE  -- does the quoted sentence really appear in the cited note?
            Catches fabricated grounding (the documented "cash cow" failure,
            where a real-sounding quote was attributed to a timestamp that
            never contained it).
  NUMBER -- does the claimed threshold really appear in that note?
            Catches the failure this whole project is built to prevent: an
            invented threshold laundered into a "trusted" numeric rule.

A test may legitimately have no number: THRESHOLD: NONE STATED is a PASS that
yields an advisory check, not a numeric one. That distinction is the entire
"no invented thresholds" invariant, enforced mechanically.
"""

from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter

NOTES = {n["slug"]: n["text"] for n in json.load(open("/tmp/forensic_notes.json"))}
ANSWERS = json.load(open("/tmp/forensic_answers.json"))

BLOCK_RE = re.compile(
    r"TEST:\s*(?P<test>.+?)\s*\n+\s*THRESHOLD:\s*(?P<thr>.+?)\s*\n+\s*SOURCE:\s*(?P<src>.+?)\s*\n+\s*QUOTE:\s*(?P<quote>.+?)(?=\n\s*TEST:|\Z)",
    re.S,
)
NUM_RE = re.compile(r"\d+(?:\.\d+)?")


# NotebookLM returns each quote wrapped in the citation apparatus the notes
# themselves use -- "(MODULA 00:20:23-00:20:33, MODULA 00:23:07)" -- plus its
# own footnote markers "[2]". Neither is part of the sentence being quoted, so
# both must be stripped before a verbatim comparison. Leaving them in made the
# first run reject 10 claims whose numbers all verified against the source: a
# false-positive rate produced entirely by the checker, not the model.
_REF_CITE_RE = re.compile(r"\(\s*[A-Z]{3,8}\s+\d{2}:\d{2}:\d{2}[^)]*\)")
_FOOTNOTE_RE = re.compile(r"\[\d+\]")


def norm(text: str) -> str:
    """Fold the differences that are formatting, not meaning."""
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("’", "'").replace("‘", "'")
    text = text.replace("“", '"').replace("”", '"')
    text = text.replace("–", "-").replace("—", "-")
    text = _REF_CITE_RE.sub(" ", text)
    text = _FOOTNOTE_RE.sub(" ", text)
    text = re.sub(r"\*\*|__|\*|`|\[|\]", "", text)   # markdown + editorial brackets
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower().strip('"\' ')


def quote_matches(quote: str, body: str) -> bool:
    """Verbatim presence, tolerant of the model quoting a fragment.

    Falls back to the longest comma/dash-delimited clause of >=40 chars so a
    quote that merely trims a trailing subordinate clause still verifies --
    but never below 40 chars, which would start matching generic phrasing.
    """
    nq = norm(quote)
    if len(nq) > 15 and nq in body:
        return True
    for piece in sorted(re.split(r"[,;-]| - ", nq), key=len, reverse=True):
        piece = piece.strip()
        if len(piece) >= 40:
            return piece in body
    return False


def resolve_source(raw: str) -> str | None:
    """Map NotebookLM's source label back to a real note slug."""
    cand = norm(raw).replace(" ", "-")
    if cand in NOTES:
        return cand
    for slug in NOTES:
        if slug in cand or cand in slug:
            return slug
    return None


def main() -> None:
    rows = []
    for theme, answer in ANSWERS.items():
        if answer.startswith("__ERROR__"):
            continue
        for m in BLOCK_RE.finditer(answer):
            test = m.group("test").strip()
            thr = m.group("thr").strip()
            src_raw = m.group("src").strip()
            quote = m.group("quote").strip()

            slug = resolve_source(src_raw)
            body = norm(NOTES[slug]) if slug else ""

            quote_ok = bool(slug) and quote_matches(quote, body)
            none_stated = "none stated" in thr.lower()

            if none_stated:
                num_ok, verdict = None, "ADVISORY"
            else:
                # Strip citation apparatus BEFORE harvesting numbers: a
                # "(SOICC 00:14:01)" marker would otherwise contribute 00/14/01
                # as if they were part of the claimed threshold.
                thr_clean = _FOOTNOTE_RE.sub(" ", _REF_CITE_RE.sub(" ", thr))
                nums = NUM_RE.findall(thr_clean)
                # every number in the claimed threshold must appear in the note
                num_ok = bool(nums) and all(n in body for n in nums)
                if not nums:
                    num_ok, verdict = None, "ADVISORY"
                else:
                    verdict = "NUMERIC-VERIFIED" if (num_ok and quote_ok) else "REJECTED"

            if verdict == "ADVISORY" and not quote_ok:
                verdict = "ADVISORY-UNGROUNDED"

            rows.append({"theme": theme, "test": test, "threshold": thr,
                         "source_raw": src_raw, "slug": slug, "quote": quote,
                         "quote_ok": quote_ok, "num_ok": num_ok, "verdict": verdict})

    json.dump(rows, open("/tmp/forensic_verified.json", "w"), indent=1)
    c = Counter(r["verdict"] for r in rows)
    print(f"proposed tests parsed : {len(rows)}")
    for k in ("NUMERIC-VERIFIED", "ADVISORY", "ADVISORY-UNGROUNDED", "REJECTED"):
        print(f"  {k:22s} {c[k]:3d}")
    unresolved = sum(1 for r in rows if r["slug"] is None)
    print(f"  unresolvable source    {unresolved:3d}")
    print()
    print("=== REJECTED (threshold or quote not found in the cited note) ===")
    for r in rows:
        if r["verdict"] == "REJECTED":
            print(f"  [{r['theme']}] {r['threshold'][:60]!r} <- {r['slug']}  "
                  f"(quote_ok={r['quote_ok']} num_ok={r['num_ok']})")
    print()
    print("=== NUMERIC-VERIFIED ===")
    for r in rows:
        if r["verdict"] == "NUMERIC-VERIFIED":
            print(f"  [{r['theme']}] {r['threshold'][:70]}")
            print(f"       {r['test'][:95]}")
    cited = {r["slug"] for r in rows if r["slug"]}
    print(f"\ncoverage: {len(cited)}/{len(NOTES)} seeded notes cited by >=1 proposed test")
    missing = sorted(set(NOTES) - cited)
    print(f"notes cited by NOTHING ({len(missing)}) -- these bound the recall risk:")
    for s in missing:
        print("   ", s)


if __name__ == "__main__":
    main()
