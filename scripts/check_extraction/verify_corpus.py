"""Deterministic verification of every proposed check across the WHOLE admitted
corpus (forensic pilot + the 11 remaining tags).

Same contract as verify_claims.py, generalised over all 222 admitted notes and
both answer files. Two independent checks per proposal, because they fail
differently:

  QUOTE  -- is the quoted sentence really in the cited note? (fabricated grounding)
  NUMBER -- is every number of the claimed threshold really in that note?
            (invented threshold -- the failure this project exists to prevent)

Citation apparatus is stripped from BOTH the quote and the threshold before
comparison. Skipping that step made the pilot's first run report 18 fabrications
that were all artifacts of this checker; see
docs/CHECK-EXTRACTION-PILOT-2026-07-29.md sec. 3.
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


def norm(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    for a, b in (("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"'), ("–", "-"), ("—", "-")):
        text = text.replace(a, b)
    text = _REF_CITE_RE.sub(" ", text)
    text = _FOOTNOTE_RE.sub(" ", text)
    text = re.sub(r"\*\*|__|\*|`|\[|\]", "", text)
    return re.sub(r"\s+", " ", text).strip().lower().strip('"\' ')


_BODIES = {s: norm(t) for s, t in NOTES.items()}


def quote_matches(quote: str, body: str) -> bool:
    nq = norm(quote)
    if len(nq) > 15 and nq in body:
        return True
    for piece in sorted(re.split(r"[,;-]| - ", nq), key=len, reverse=True):
        piece = piece.strip()
        if len(piece) >= 40:
            return piece in body
    return False


def resolve(raw: str) -> str | None:
    cand = norm(raw).replace(" ", "-")
    if cand in NOTES:
        return cand
    hits = [s for s in NOTES if s in cand or cand in s]
    return hits[0] if len(hits) == 1 else (hits[0] if hits else None)


def main() -> None:
    rows = []
    for slot, answer in ANSWERS.items():
        if answer.startswith("__ERROR__"):
            continue
        theme = slot.split(":")[1].split("__")[0]
        for m in BLOCK_RE.finditer(answer):
            thr = m.group("thr").strip()
            slug = resolve(m.group("src").strip())
            body = _BODIES.get(slug, "")
            quote_ok = bool(slug) and quote_matches(m.group("quote").strip(), body)

            if "none stated" in thr.lower():
                verdict = "ADVISORY" if quote_ok else "ADVISORY-UNGROUNDED"
                num_ok = None
            else:
                nums = NUM_RE.findall(_FOOTNOTE_RE.sub(" ", _REF_CITE_RE.sub(" ", thr)))
                if not nums:
                    num_ok, verdict = None, ("ADVISORY" if quote_ok else "ADVISORY-UNGROUNDED")
                else:
                    num_ok = all(n in body for n in nums)
                    verdict = "NUMERIC-VERIFIED" if (num_ok and quote_ok) else "REJECTED"

            rows.append({"theme": theme, "test": m.group("test").strip(), "threshold": thr,
                         "slug": slug, "quote": m.group("quote").strip(),
                         "quote_ok": quote_ok, "num_ok": num_ok, "verdict": verdict})

    json.dump(rows, open("/tmp/corpus_verified.json", "w"), indent=1)
    c = Counter(r["verdict"] for r in rows)
    print(f"proposals parsed : {len(rows)}")
    for k in ("NUMERIC-VERIFIED", "ADVISORY", "ADVISORY-UNGROUNDED", "REJECTED"):
        print(f"  {k:22s} {c[k]:4d}")
    print(f"  unresolvable source   {sum(1 for r in rows if r['slug'] is None):4d}")

    print("\nby theme (numeric-verified / total):")
    per = Counter(); tot = Counter()
    for r in rows:
        tot[r["theme"]] += 1
        if r["verdict"] == "NUMERIC-VERIFIED":
            per[r["theme"]] += 1
    for t in sorted(tot, key=lambda x: -per[x]):
        print(f"  {t:20s} {per[t]:3d} / {tot[t]:3d}")

    cited = {r["slug"] for r in rows if r["slug"]}
    print(f"\ncoverage: {len(cited)}/{len(NOTES)} admitted notes cited by >=1 proposal")
    missing = sorted(set(NOTES) - cited)
    print(f"uncited ({len(missing)}) -- these need the residual per-note pass")
    for s in missing[:25]:
        print("   ", s)
    if len(missing) > 25:
        print(f"    ... and {len(missing)-25} more")


if __name__ == "__main__":
    main()
