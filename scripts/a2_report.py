"""A2 acceptance report: T2-T5 against the regenerated notes.

T2  no denied phrase taught as SOIC terminology (oracle denial check)
T3  hollow-admission count < 40 (proxy for the old wiki's 146 depth-gate
    markers — honest caveat: the old number came from a depth-check stage this
    rebuild doesn't run; the comparable signal is how often a note must admit
    its source lacks substance)
T4  >= 80% of span-resolvable oracle spans covered by the evidence spans the
    notes were WRITTEN from (recomputed deterministically from the ledger)
T5  zero citations from ineligible lessons
Plus the cited-quote verification and frequency gates over every note.
"""

from __future__ import annotations

import base64
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, "/Users/syedamberiqbal/Library/Mobile Documents/"
                   "iCloud~md~obsidian/Documents/learning-vault/src")

from de_toolkit.vault import slugify  # noqa: E402

from soic_method.corpus import load_corpus  # noqa: E402
from soic_method.eligibility import apply_eligibility, load_eligibility  # noqa: E402
from soic_wiki.gates import (CorpusIndex, audit_terms,  # noqa: E402
                             split_cited_quotes, verify_cited_quotes)
from soic_wiki.oracle import (OracleSpan, check_denials,  # noqa: E402
                              extract_denials, parse_legend,
                              parse_oracle_spans, span_recall)
from soic_wiki.pipeline import Beat  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
A2 = ROOT / "out" / "a2"

HOLLOW = re.compile(
    r"(source does not|excerpts do not|no (specific|worked|numeric)|"
    r"not stated in the excerpt|does not (give|provide|contain))", re.I)


def gh(p: str) -> str:
    o = subprocess.run(["gh", "api",
                        "repos/syedamber91/learning-vault-invest/contents/" + p,
                        "--jq", ".content"],
                       capture_output=True, text=True, check=True).stdout
    return base64.b64decode(o).decode()


def main() -> int:
    elig = load_eligibility(ROOT / "configs" / "course_eligibility.yaml")
    all_lessons = apply_eligibility(load_corpus(ROOT / "data" / "content.json"), elig)
    eligible_ids = {l.lesson_id for l in all_lessons if l.eligible}
    by_id = {l.lesson_id: l for l in all_lessons}
    by_slug = {slugify(l.title): l for l in all_lessons if l.eligible}
    refs = json.loads((A2 / "refs.json").read_text())
    ref_to_lesson = {r: by_id[lid] for lid, r in refs.items()}

    notes = {}
    for f in sorted((A2 / "notes").glob("*.md")):
        notes[f.stem] = f.read_text(encoding="utf-8")
    print("notes on disk: %d / 22" % len(notes))
    if len(notes) < 22:
        print("NOT ALL NOTES PRESENT — report is partial")

    # --- T2: oracle denials -------------------------------------------------
    dn = (extract_denials(gh("poc/soic/enrichment_valuechain.md"), "vc")
          + extract_denials(gh("poc/soic/enrichment_frameworks.md"), "fw"))
    viol = check_denials(notes, dn)
    # A mention that explicitly DISPOSITIONS the phrase is compliant: the
    # denial ban is on TEACHING it as SOIC's terminology, and a note saying
    # "nowhere does the instructor name this technique X" is the disposition
    # working, not a violation. Check EVERY occurrence (first-only missed a
    # note whose sole mention sat inside its own disclaimer), with a window
    # wide enough to hold a full disposition sentence.
    DISPO = ("artifact", "asr", "debris", "not his", "never uses",
             "nowhere", "does not name", "not a term", "collision")
    real_viol = []
    for v in viol:
        ctx = notes[v.note_slug].lower()
        bad = False
        start = 0
        while True:
            i = ctx.find(v.phrase, start)
            if i < 0:
                break
            window = ctx[max(0, i - 600):i + 600]
            if not any(d in window for d in DISPO):
                bad = True
                break
            start = i + 1
        if bad:
            real_viol.append(v)
    t2 = len(real_viol) == 0

    # --- T3: hollow admissions ----------------------------------------------
    hollow = sum(len(HOLLOW.findall(t)) for t in notes.values())
    t3 = hollow < 40

    # --- T4: oracle span recall ---------------------------------------------
    fw = gh("poc/soic/enrichment_frameworks.md")
    vc = gh("poc/soic/enrichment_valuechain.md")
    legend = {**parse_legend(fw), **parse_legend(vc)}
    oracle = parse_oracle_spans(fw, legend, by_slug) + parse_oracle_spans(vc, legend, by_slug)
    # Dedupe: the enrichment files cite some spans more than once, and a
    # duplicate span must not count twice against recall.
    seen = set()
    oracle = [o for o in oracle
              if (k := (o.lesson_id, o.start, o.end)) not in seen
              and not seen.add(k)]

    # Measured from the DELIVERABLE: the (REF HH:MM:SS) citations the notes
    # actually carry — not from re-running selection, which can drift from
    # what a given note was written against. An oracle span counts as covered
    # when any note cites a timestamp inside it (±90s tolerance for the
    # enrichment layer's minute-granularity stamps).
    cite_re = re.compile(r"\(([A-Z][A-Z0-9]*)\s+(\d{2}):(\d{2}):(\d{2})")
    cited = set()
    for text in notes.values():
        for m in cite_re.finditer(text):
            ref = m.group(1)
            lesson = ref_to_lesson.get(ref)
            if lesson is None:
                continue
            secs = int(m.group(2)) * 3600 + int(m.group(3)) * 60 + int(m.group(4))
            cited.add((lesson.lesson_id, secs))

    def to_secs(ts):
        h, mnt, s = (int(x) for x in ts.split(":"))
        return h * 3600 + mnt * 60 + s

    TOL = 90
    hit = 0
    for o in oracle:
        lo, hi = to_secs(o.ts_start) - TOL, to_secs(o.ts_end) + TOL
        if any(lid == o.lesson_id and lo <= s <= hi for lid, s in cited):
            hit += 1
    recall = hit / max(len(oracle), 1)
    t4 = recall >= 0.80

    # --- T5: ineligible citations -------------------------------------------
    # Checked at BOTH layers: the beats every note was built from, and the
    # refs the notes actually cite.
    beats = [Beat(**b) for b in json.loads((A2 / "all_beats.json").read_text())]
    bad_lessons = {b.lesson_id for b in beats} - eligible_ids
    bad_lessons |= {lid for lid, _ in cited} - eligible_ids
    t5 = not bad_lessons

    # --- cited-quote verification + frequency gates -------------------------
    idx = CorpusIndex(all_lessons)
    total_cited = total_verified = 0
    uncited_flagged = {}
    for slug, text in notes.items():
        checks = verify_cited_quotes(text, ref_to_lesson)
        total_cited += len(checks)
        total_verified += sum(c.verified for c in checks)
        parts = split_cited_quotes(text)
        stats = audit_terms(parts["uncited"], all_lessons, index=idx)
        for t, s in stats.items():
            if s.suspect:
                uncited_flagged.setdefault(t, []).append(slug)

    print()
    print("=" * 70)
    print("A2 ACCEPTANCE REPORT")
    print("=" * 70)
    print("T2 denied-phrase violations : %d real (of %d mentions) -> %s"
          % (len(real_viol), len(viol), "PASS" if t2 else "FAIL"))
    for v in real_viol:
        print("     VIOLATION: %s asserts %r" % (v.note_slug, v.phrase))
    print("T3 hollow admissions        : %d (old wiki: 146; bar <40) -> %s"
          % (hollow, "PASS" if t3 else "FAIL"))
    print("T4 oracle span recall       : %.0f%% of %d spans (bar >=80%%) -> %s"
          % (recall * 100, len(oracle), "PASS" if t4 else "FAIL"))
    print("T5 ineligible citations     : %d -> %s"
          % (len(bad_lessons), "PASS" if t5 else "FAIL"))
    print()
    print("cited quotes verified       : %d/%d (%.0f%%)"
          % (total_verified, total_cited,
             100.0 * total_verified / max(total_cited, 1)))
    print("uncited flagged terms       : %d" % len(uncited_flagged))
    for t, slugs in sorted(uncited_flagged.items())[:15]:
        print("     %r in %s" % (t, ",".join(slugs[:3])))

    verdict = t2 and t3 and t4 and t5
    print()
    print("A2 VERDICT: %s" % ("PASS" if verdict else "FAIL"))
    (A2 / "acceptance.json").write_text(json.dumps({
        "t2_pass": t2, "t3_hollow": hollow, "t4_recall": recall,
        "t5_bad_lessons": sorted(bad_lessons),
        "cited_quotes": [total_verified, total_cited],
        "uncited_flagged": {k: v for k, v in uncited_flagged.items()},
        "verdict": verdict}, indent=1), encoding="utf-8")
    return 0 if verdict else 1


if __name__ == "__main__":
    raise SystemExit(main())
