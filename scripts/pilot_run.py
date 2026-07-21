"""Task 11 pilot run.

The extractor and refuter roles are played by the operating agent (Claude),
reading real router-flagged spans and recording judgments here, rather than by
a wired API client. That is a deliberate, human-approved choice for a pilot of
this size (see the pilot report). Every judgment below is traceable to a real
span in the real corpus; nothing is invented.

Pipeline order matches the plan: route -> extract -> verify -> corroborate ->
refute -> reconcile -> publish.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from soic_method.corpus import load_corpus, normalize_slice, resolve_timestamp
from soic_method.corroborate import corroborate
from soic_method.eligibility import apply_eligibility, load_eligibility
from soic_method.models import Citation, Rule, Span
from soic_method.publish import write_bundle
from soic_method.reconcile import reconcile
from soic_method.refute import refute
from soic_method.router import find_candidates
from soic_method.verify import verify_rule

ROOT = Path(__file__).resolve().parents[1]

# --- EXTRACTION -------------------------------------------------------------
# (lesson_id, candidate_index_within_lesson, anchor_digits, rule fields...)
# anchor_digits locates a tight citation window inside the router's candidate
# span, so the citation is the sentence stating the rule, not the whole window.
EXTRACTIONS = [
    # Lesson 3586296 "Tools To Find Epic Stocks" -- the core screen, stated twice.
    dict(lesson="3586296", cand=2, anchor="15%", key="screen.sales_growth.floor",
         kind="threshold", op="gte", value=15, unit="percent", note="CAND8 core screen"),
    dict(lesson="3586296", cand=2, anchor="20%", key="screen.pat_growth.floor",
         kind="threshold", op="gte", value=20, unit="percent", note="CAND8 core screen"),
    dict(lesson="3586296", cand=2, anchor="15%", key="screen.roc.floor",
         kind="threshold", op="gte", value=15, unit="percent", note="CAND8 core screen"),
    dict(lesson="3586296", cand=7, anchor="15%", key="screen.sales_growth.floor",
         kind="threshold", op="gte", value=15, unit="percent", note="CAND13 restatement"),
    dict(lesson="3586296", cand=7, anchor="20%", key="screen.pat_growth.floor",
         kind="threshold", op="gte", value=20, unit="percent", note="CAND13 restatement"),
    dict(lesson="3586296", cand=7, anchor="15%", key="screen.roc.floor",
         kind="threshold", op="gte", value=15, unit="percent", note="CAND13 restatement"),
    # P/E stated as a 15-30 band here...
    dict(lesson="3586296", cand=5, anchor="15 to 30", key="screen.pe.ceiling",
         kind="range", op=None, vmin=15, vmax=30, unit="multiple", note="CAND11 P/E band"),
    # Lesson 4150532 "Part 2 Scalable Businesses" -- cross-lesson corroboration.
    dict(lesson="4150532", cand=2, anchor="15%", key="screen.sales_growth.floor",
         kind="threshold", op="gte", value=15, unit="percent", note="CAND18 cross-lesson"),
    dict(lesson="4150532", cand=2, anchor="20%", key="screen.pat_growth.floor",
         kind="threshold", op="gte", value=20, unit="percent", note="CAND18 cross-lesson"),
    # ...but as a <50/<40 ceiling here. REAL conflict, not synthetic.
    dict(lesson="4150532", cand=3, anchor="50", key="screen.pe.ceiling",
         kind="range", op=None, vmin=40, vmax=50, unit="multiple", note="CAND19 P/E ceiling"),
    # Lesson 4924001 "Screen Domestic Businesses" -- market cap floor.
    dict(lesson="4924001", cand=1, anchor="1000", key="screen.market_cap.floor",
         kind="threshold", op="gte", value=1000, unit="crore", note="CAND2 market cap"),
    # A company's own guidance, NOT a SOIC rule -- included deliberately so the
    # refuter has a genuine reported-speech case to kill.
    dict(lesson="4924001", cand=0, anchor="20%", key="screen.ebitda_margin.floor",
         kind="threshold", op="gte", value=20, unit="percent",
         note="CAND1 Usha Martin company guidance -- expect REFUTED"),
    # Garbled ASR, semantically empty -- expect refuted for incoherence.
    dict(lesson="4150549", cand=1, anchor="500", key="screen.roc.floor",
         kind="threshold", op="gte", value=500, unit="percent",
         note="CAND21 garbled ASR -- expect REFUTED"),
]

# --- REFUTER JUDGMENTS ------------------------------------------------------
# Keyed by note. True = refuted (killed).
REFUTER = {
    "CAND8 core screen": False,
    "CAND13 restatement": False,
    "CAND11 P/E band": False,
    "CAND18 cross-lesson": False,
    "CAND19 P/E ceiling": False,
    "CAND2 market cap": False,
    # Ishmohit is quoting Usha Martin management's own raised guidance, not
    # stating a screening rule of his own. Reported speech about a company.
    "CAND1 Usha Martin company guidance -- expect REFUTED": True,
    # "if you get 3000% margin, if you get 500% then roc will explode" is
    # ASR-garbled beyond recovery; no coherent rule is supportable.
    "CAND21 garbled ASR -- expect REFUTED": True,
}


def main() -> int:
    elig = load_eligibility(ROOT / "configs" / "course_eligibility.yaml")
    lessons = apply_eligibility(load_corpus(ROOT / "data" / "content.json"), elig)
    by_id = {l.lesson_id: l for l in lessons}

    cands = {}
    for l in lessons:
        if l.eligible and (l.course_title.startswith("Level 5")
                           or l.module_title == "Identifying Scalable Businesses"):
            cands[l.lesson_id] = find_candidates(l)

    built, skipped = [], []
    for e in EXTRACTIONS:
        lesson = by_id[e["lesson"]]
        span = cands[e["lesson"]][e["cand"]].span
        raw = lesson.body_text[span.start:span.end]
        i = raw.find(e["anchor"])
        if i < 0:
            skipped.append((e["note"], "anchor %r not in span" % e["anchor"]))
            continue
        lo = max(span.start, span.start + i - 260)
        hi = min(span.end, span.start + i + 260)
        fields = dict(
            tier="graded", kind=e["kind"], stage="screen", rule_key=e["key"],
            operator=e["op"], unit=e["unit"],
            citations=[Citation(
                lesson_id=lesson.lesson_id, lesson_url=lesson.url,
                timestamp=resolve_timestamp(lesson.body_text, lo),
                span=Span(start=lo, end=hi),
                transcript_fidelity=lesson.transcript_fidelity,
                text_hash=lesson.text_hash)],
        )
        if e["kind"] == "range":
            fields["value_range"] = {"min": e["vmin"], "max": e["vmax"]}
        else:
            fields["value"] = e["value"]
        built.append((e["note"], Rule(**fields)))

    # --- GATE 1: verify -----------------------------------------------------
    verified, rejected = [], []
    for note, rule in built:
        res = verify_rule(rule, by_id)
        (verified if res.ok else rejected).append((note, rule, res.reasons))

    # --- GATE 1b: corroborate ----------------------------------------------
    corroborated = [(n, corroborate(r, by_id)) for n, r, _ in verified]

    # --- GATE 2: refute -----------------------------------------------------
    survived, killed = [], []
    for note, rule in corroborated:
        verdict = REFUTER[note]
        llm = lambda _p, v=verdict: json.dumps({"refuted": v, "reason": note})
        (survived if refute(rule, by_id, llm) else killed).append((note, rule))

    # --- GATE 3: reconcile --------------------------------------------------
    # resolutions.yaml is hand-maintained; the pipeline reads it, never writes it.
    res_path = ROOT / "configs" / "resolutions.yaml"
    resolutions = {}
    if res_path.exists():
        import yaml
        resolutions = yaml.safe_load(res_path.read_text(encoding="utf-8")) or {}
    out = reconcile([r for _, r in survived], by_id, resolutions)
    if resolutions:
        print("applied %d human resolution(s) from configs/resolutions.yaml"
              % len(resolutions))

    dest = ROOT / "out" / "pilot-bundle"
    write_bundle(out, by_id, dest)

    print("=" * 66)
    print("PILOT RESULTS")
    print("=" * 66)
    print("extracted            : %d" % len(built))
    if skipped:
        for n, why in skipped:
            print("  SKIPPED %s (%s)" % (n, why))
    print("Gate 1 verified      : %d" % len(verified))
    print("Gate 1 rejected      : %d  (rate %.0f%%)"
          % (len(rejected), 100.0 * len(rejected) / max(len(built), 1)))
    for n, _r, reasons in rejected:
        print("    - %s :: %s" % (n, reasons))
    print("Gate 2 survived      : %d" % len(survived))
    print("Gate 2 refuted       : %d" % len(killed))
    for n, _r in killed:
        print("    - %s" % n)
    print("Gate 3 active rules  : %d" % len(out.rules))
    print("Gate 3 drafts        : %d" % len(out.drafts))
    print("Gate 3 CONFLICTS     : %d" % len(out.conflicts))
    for grp in out.conflicts:
        vals = [(r.value if r.value is not None else
                 (r.value_range.min, r.value_range.max)) for r in grp]
        print("    - %s :: %s" % (grp[0].rule_key, vals))
    print()
    print("status / corroboration breakdown:")
    for r in out.rules:
        v = r.value if r.value is not None else (r.value_range.min, r.value_range.max)
        print("    %-30s %-12s corrob=%d  status=%s"
              % (r.rule_key, v, r.corroboration, r.status))
    print()
    print("bundle written to: %s" % dest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
