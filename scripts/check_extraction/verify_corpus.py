"""Deterministic verification of every proposed check across the admitted corpus.

TWO CHECKS PER PROPOSAL, and the second is CONDITIONAL ON THE FIRST:

  QUOTE  -- is the quoted sentence really present, verbatim, in the cited note?
  NUMBER -- does every number of the claimed threshold appear INSIDE THAT
            QUOTE? (not merely somewhere in the note)

The conditional structure is the whole point, and v1 got it wrong. v1 tested
each threshold number against the ENTIRE note body, independently of the quote.
Measured consequence (2026-07-29, seed-independent, re-run twice): a v1
"NUMERIC-VERIFIED" threshold also passed against a RANDOMLY CHOSEN UNRELATED
note 34% of the time overall, and 44% of the time for single-number thresholds
like `above 20%` or `2.5`. That is barely better than a coin flip, so v1's
0.7% rejection rate was evidence the test was easy to pass -- NOT evidence the
model was honest. Anchoring the number inside the already-verified quote span
makes a random-note pass essentially impossible, because the quote must match
first.

Expect this to REDUCE the verified count relative to v1. That reduction is the
honest number; v1's was inflated.

Citation apparatus (`(MODULA 00:20:23-00:20:33)`, `[2]`) is stripped from quote
AND threshold before comparison -- skipping that made v1's first run report 18
fabrications that were all artifacts of this checker.
"""
from __future__ import annotations

import json
import pathlib
import re
import unicodedata
from collections import Counter

VAULT = pathlib.Path(
    "/Users/syedamberiqbal/Library/Mobile Documents/iCloud~md~obsidian/"
    "Documents/Learning Vault Invest/wiki/personas/soic/concepts"
)
ROUTING = json.load(open("/tmp/polycab_routing.json"))
NOTES = {
    r["slug"]: (VAULT / f"{r['slug']}.md").read_text(encoding="utf-8")
    for r in ROUTING if r["tier"] != "D-excluded"
}

ANSWERS = {}
for path, tag in (("/tmp/forensic_answers.json", "forensic"),
                  ("/tmp/corpus_answers.json", "corpus")):
    try:
        for k, v in json.load(open(path)).items():
            ANSWERS[f"{tag}:{k}"] = v
    except FileNotFoundError:
        pass

BLOCK_RE = re.compile(
    r"TEST:\s*(?P<test>.+?)\s*\n+\s*THRESHOLD:\s*(?P<thr>.+?)\s*\n+\s*SOURCE:\s*(?P<src>.+?)\s*\n+\s*QUOTE:\s*(?P<quote>.+?)(?=\n\s*TEST:|\Z)",
    re.S,
)
NUM_RE = re.compile(r"\d+(?:\.\d+)?")
_REF_CITE_RE = re.compile(r"\(\s*[A-Z]{3,8}\s+\d{2}:\d{2}:\d{2}[^)]*\)")
_FOOTNOTE_RE = re.compile(r"\[\d+\]")

# Numbers a threshold may legitimately state that will NOT appear in the quote
# because they are units/scale words rendered as digits elsewhere. Kept empty
# deliberately -- any exception here is a hole in the gate, so it must be
# argued for explicitly rather than accumulated by convenience.
NUMBER_EXEMPTIONS: set[str] = set()


def strip_citations(text: str) -> str:
    return _FOOTNOTE_RE.sub(" ", _REF_CITE_RE.sub(" ", text))


def norm(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    for a, b in (("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"'), ("–", "-"), ("—", "-")):
        text = text.replace(a, b)
    text = strip_citations(text)
    text = re.sub(r"\*\*|__|\*|`|\[|\]", "", text)
    return re.sub(r"\s+", " ", text).strip().lower().strip('"\' ')


_BODIES = {s: norm(t) for s, t in NOTES.items()}


def matched_quote_span(quote: str, body: str) -> str | None:
    """Return the normalised quote text that was actually found in the note.

    Returns the span so the caller can anchor the number check to it. The
    fragment fallback (v1) accepted the FIRST clause over 40 chars and ignored
    the rest, so a quote could verify on one genuine clause while the remainder
    was paraphrase. Now every clause of >=40 chars must be present; a quote
    that only partly matches does not verify at all.
    """
    nq = norm(quote)
    if len(nq) > 15 and nq in body:
        return nq
    pieces = [p.strip() for p in re.split(r"[,;]| - ", nq)]
    long_pieces = [p for p in pieces if len(p) >= 40]
    if long_pieces and all(p in body for p in long_pieces):
        return " ".join(long_pieces)
    return None


def resolve(raw: str) -> tuple[str | None, bool]:
    """Resolve a model-supplied source label to a slug.

    Returns (slug, ambiguous). v1 had dead code here -- both branches of its
    ternary returned hits[0], so an ambiguous label silently took whichever
    slug dict order happened to yield. Ambiguity is now reported so it can be
    counted rather than hidden.
    """
    cand = norm(raw).replace(" ", "-")
    if cand in NOTES:
        return cand, False
    hits = sorted(s for s in NOTES if s in cand or cand in s)
    if not hits:
        return None, False
    return hits[0], len(hits) > 1


def main() -> None:
    rows = []
    for slot, answer in ANSWERS.items():
        if answer.startswith("__ERROR__"):
            continue
        theme = slot.split(":")[1].split("__")[0]
        for m in BLOCK_RE.finditer(answer):
            thr = m.group("thr").strip()
            quote = m.group("quote").strip()
            slug, ambiguous = resolve(m.group("src").strip())
            body = _BODIES.get(slug, "")

            span = matched_quote_span(quote, body) if slug else None
            quote_ok = span is not None

            nums = [n for n in NUM_RE.findall(strip_citations(thr))
                    if n not in NUMBER_EXEMPTIONS]
            stated = "none stated" not in thr.lower() and bool(nums)

            if not stated:
                num_ok = None
                verdict = "ADVISORY" if quote_ok else "ADVISORY-UNGROUNDED"
            else:
                # THE conditional check: numbers must sit inside the verified quote.
                num_ok = quote_ok and all(n in span for n in nums)
                verdict = "NUMERIC-VERIFIED" if num_ok else (
                    "REJECTED-NUMBER-NOT-IN-QUOTE" if quote_ok else "REJECTED-QUOTE-NOT-FOUND")

            rows.append({"theme": theme, "test": m.group("test").strip(), "threshold": thr,
                         "slug": slug, "ambiguous_source": ambiguous, "quote": quote,
                         "quote_ok": quote_ok, "num_ok": num_ok, "verdict": verdict})

    json.dump(rows, open("/tmp/corpus_verified_v2.json", "w"), indent=1)
    c = Counter(r["verdict"] for r in rows)
    print(f"proposals parsed : {len(rows)}")
    for k in ("NUMERIC-VERIFIED", "ADVISORY", "ADVISORY-UNGROUNDED",
              "REJECTED-NUMBER-NOT-IN-QUOTE", "REJECTED-QUOTE-NOT-FOUND"):
        print(f"  {k:30s} {c[k]:4d}")
    print(f"  {'ambiguous source label':30s} {sum(1 for r in rows if r['ambiguous_source']):4d}")

    print("\nby theme (numeric-verified / total):")
    per, tot = Counter(), Counter()
    for r in rows:
        tot[r["theme"]] += 1
        if r["verdict"] == "NUMERIC-VERIFIED":
            per[r["theme"]] += 1
    for t in sorted(tot, key=lambda x: -per[x]):
        print(f"  {t:22s} {per[t]:3d} / {tot[t]:3d}")

    cited = {r["slug"] for r in rows if r["slug"]}
    print(f"\ncoverage: {len(cited)}/{len(NOTES)} admitted notes cited")


if __name__ == "__main__":
    main()
