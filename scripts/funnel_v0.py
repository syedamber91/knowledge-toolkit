"""Funnel v0: one sector -> gate verdicts -> reading shortlist + reasons table.

Screen only. Never buy/sell/hold. Offline, no model calls.
Spec: docs/FUNNEL-V0-CAVEMAN-SPEC.md. Run with the soic-ladder venv python.

  .venv/bin/python scripts/funnel_v0.py --industry Healthcare --corpus-dir healthcare
"""
from __future__ import annotations

import argparse
import csv
import random
import re
import sys
from pathlib import Path

LADDER = Path("/Users/syedamberiqbal/Documents/workspace/Claude_Code/soic-ladder")
PROV = Path("/Users/syedamberiqbal/Documents/workspace/Claude_Code/provenance/corpus")
GATE_ORDER = ["G0", "G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8"]
ADVICE = re.compile(r"\b(buy|sell|hold)\b", re.I)


def shortlist(verdicts, docs):
    """Pre-registered rule: CANDIDATE and >=1 concall and >=1 annual report on disk."""
    return sorted(
        c for c, v in verdicts.items()
        if v == "CANDIDATE" and docs.get(c, (0, 0))[0] >= 1 and docs.get(c, (0, 0))[1] >= 1
    )


def first_not_pass(rows):
    """rows = (gate, rule_id, outcome, value, check_rule). Earliest gate that is not PASS/N-A."""
    bad = [r for r in rows if r[2] not in ("PASS", "NOT_APPLICABLE")]
    return min(bad, key=lambda r: GATE_ORDER.index(r[0])) if bad else None


def random_control(pool, n, seed):
    return sorted(random.Random(seed).sample(sorted(pool), n))


def has_advice_words(text):
    return bool(ADVICE.search(text))


def count_docs(corpus_dir, code):
    base = PROV / corpus_dir / code

    def n(sub):
        p = base / sub
        return sum(1 for _ in p.iterdir()) if p.is_dir() else 0

    return n("transcripts"), n("annual_reports")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--industry", required=True)
    ap.add_argument("--corpus-dir", required=True)
    ap.add_argument("--as-of", default="2026-08-29")
    ap.add_argument("--export", default=str(LADDER / "docs/reports/q2-company-export/q2-company-export-2026-08-30.csv"))
    ap.add_argument("--db", default=str(LADDER / "runs/nifty500-2026-08-29.db"))
    ap.add_argument("--rules", default=str(LADDER / "rulebook/soic-ladder-rules-v1.yaml"))
    ap.add_argument("--registry", default=str(LADDER / "rulebook/vendor/metric-registry.yaml"))
    ap.add_argument("--out", default="output/funnel")
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()

    from soic_ladder.admissibility import resolve_attributes
    from soic_ladder.facts.store import SnapshotStore
    from soic_ladder.judge import judge_company, observe_company, write_engine_rules
    from soic_ladder.report import final_verdict, gate_verdicts
    from soic_ladder.rulebook import load_observations, load_rulebook

    rules = load_rulebook(Path(a.rules), Path(a.registry))
    observations = load_observations(Path(a.rules), Path(a.registry))
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    engine = write_engine_rules(rules, out / "engine-rules.yaml")
    store = SnapshotStore(Path(a.db))
    run_id = store.latest_run_id(a.as_of)

    with open(a.export, newline="", encoding="utf-8") as fh:
        universe = sorted(r["Code"] for r in csv.DictReader(fh) if r["Industry"] == a.industry)

    verdicts, docs, per, obs_cols = {}, {}, {}, {}
    for code in universe:
        metrics = store.metrics_for(run_id, code)
        attrs = resolve_attributes(code, metrics, sector=store.industry_for(run_id, code))
        outs = judge_company(code, rules, metrics, attrs, engine, Path(a.registry))
        gates = {g.gate: g.verdict for g in gate_verdicts(outs)}
        verdicts[code] = final_verdict(gate_verdicts(outs))
        docs[code] = count_docs(a.corpus_dir, code)
        per[code] = (gates, outs, bool(metrics))
        obs_cols[code] = {o.metric: o.value for o in observe_company(observations, metrics, Path(a.registry))}

    short = shortlist(verdicts, docs)
    gate_cols = [g for g in GATE_ORDER if any(g in per[c][0] for c in universe)]
    obs_names = sorted({m for d in obs_cols.values() for m in d})

    with open(out / f"funnel_{a.industry.lower()}_{a.as_of}.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["code", "final_verdict", *gate_cols, "abstain_metrics", "concalls_on_disk", "annual_reports_on_disk", "shortlisted", *[f"obs:{m}" for m in obs_names]])
        for c in universe:
            gates, outs, _ = per[c]
            ab = ";".join(o.metric for o in outs if o.outcome == "ABSTAIN")
            w.writerow([c, verdicts[c], *[gates.get(g, "") for g in gate_cols], ab, *docs[c], c in short, *[obs_cols[c].get(m, "") for m in obs_names]])

    nreasons = 0
    with open(out / f"reasons_{a.industry.lower()}_{a.as_of}.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["code", "first_failed_gate", "rule_id", "metric_value", "threshold", "fail_or_abstain", "concalls", "annual_reports"])
        for c in universe:
            if c in short:
                continue
            nreasons += 1
            fp = first_not_pass([(o.gate, o.rule_id, o.outcome, o.value, o.check_rule) for o in per[c][1]])
            if fp:
                w.writerow([c, fp[0], fp[1], fp[3], fp[4], fp[2], *docs[c]])
            else:
                w.writerow([c, "READING_DOCS", "needs>=1 concall and >=1 annual report", "", "", "NO_DOCS", *docs[c]])

    # Control: random 3 from names that pass every gate (not return-based).
    cands = [c for c in universe if verdicts[c] == "CANDIDATE"]
    ctrl = random_control(cands, min(3, len(cands)), a.seed) if cands else []
    base = sum(1 for c in universe if per[c][0].get("G0") == "PASS")
    abst = [c for c in universe if any(o.outcome == "ABSTAIN" for o in per[c][1])]
    summary = (
        f"Funnel v0 {a.industry} as of {a.as_of} (screen shortlist for reading, not advice)\n"
        f"universe={len(universe)}  with_metrics={sum(per[c][2] for c in universe)}  any_abstain={len(abst)}\n"
        f"pass_G0={base}  CANDIDATE(all gates)={len(cands)}\n"
        f"shortlist(rule: CANDIDATE + >=1 concall + >=1 annual report)={short}\n"
        f"control random_{len(ctrl)} (seed {a.seed}) from CANDIDATE={ctrl}\n"
        f"rows: shortlist {len(short)} + reasons {nreasons} = {len(short) + nreasons} (universe {len(universe)})\n"
    )
    (out / f"summary_{a.industry.lower()}_{a.as_of}.txt").write_text(summary, encoding="utf-8")
    print(summary)
    assert len(short) + nreasons == len(universe)
    assert not has_advice_words(summary)


if __name__ == "__main__":
    sys.exit(main())
