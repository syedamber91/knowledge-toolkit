"""T6 combination: Nemotron (generator) + Jev and/or Laya (cheap verifiers that can only say "no").

One Nemotron reply per (row, rep) is generated once and shared by every arm, so arms differ ONLY by
the gate. A gate can turn an answer into a refusal, never the reverse, and fails closed: a verifier
that errors or is unreachable counts as "no" and is reported, not hidden.
Arms: nemotron | nemotron+jev | nemotron+laya | nemotron+jev+laya. Scoring is the same code scorer
as t6_models (a model never grades a model). Advisory-only tiers: this measures them, it gates nothing
in the repo.

usage (VPS; NVIDIA_API_KEY and TYPESAFE_API_KEY as project environment variables, LAYA_DIR = the one installed copy):
  t6_combo.py --golden docs/vps-extraction/golden.jsonl docs/vps-extraction/golden_new.jsonl \
     --data BIOCON/data --ar BIOCON/annual-report/FY26 \
     --model <nemotron-nim-id> --laya-dir $LAYA_DIR --reps 3 --out docs/vps-extraction/combo-table.md
"""
import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path

from vps_extraction.t6_models import (ANSWERABLE, build_prompt, load_key, nim_call, parse_reply, score_row)

ARMS = {"nemotron": [], "nemotron+jev": ["jev"], "nemotron+laya": ["laya"], "nemotron+jev+laya": ["jev", "laya"]}


def gate(reply, hits, question, verifiers, errors=None, mins=None):
    """Keep an answer only if every verifier accepts it. Refusals and empty replies pass through."""
    if not reply or reply.get("refuse") is True:
        return reply
    cited = next((h for h in hits if h["label"] == reply.get("cite")), None)
    if cited is None:
        return {"refuse": True, "gated_by": "cite"}
    for i, v in enumerate(verifiers):
        try:
            p = v(question, str(reply.get("answer", "")), cited["snippet"])
        except Exception as e:  # fail closed, but count it
            if errors is not None:
                errors.append((i, type(e).__name__))
            return {"refuse": True, "gated_by": i}
        if p < (mins[i] if mins else 0.5):
            return {"refuse": True, "gated_by": i}
    return reply


def _find_verdict(x):
    if isinstance(x, dict):
        if "verdict" in x:
            return x
        x = list(x.values())
    if isinstance(x, list):
        for y in x:
            r = _find_verdict(y)
            if r:
                return r
    return None


def jev_verifier(call):
    """call = jev_hook.call_jev: (tool, args) -> (result, error). Returns P(supported); non-verified = 0."""
    def v(question, answer, excerpt):
        res, err = call("jev_verify", {"claims": [f"The answer to '{question}' is: {answer}"],
                                       "evidence": [{"id": "excerpt", "text": excerpt}]})
        if err:
            raise RuntimeError(err)
        r = _find_verdict(res)
        if not r:
            raise RuntimeError("unknown jev_verify result shape")
        return float(r.get("confidence", 0.0)) if r["verdict"] == "verified" else 0.0
    return v


def laya_verifier(agent):
    q = {"ok": {"type": "noul", "instructions": "The excerpt states that this answer is correct for the question.",
                "criteria": {"false": "The excerpt does not state this answer.", "true": "The excerpt states this answer."}}}

    def v(question, answer, excerpt):
        return float(agent.predict({"question": question, "answer": answer, "excerpt": excerpt}, q)["answers"]["ok"]["noul"])
    return v


def run_arms(rows, hits, replies, arms, mins=None):
    """replies[row_id] = [reply per rep]. arms = {name: [verifier callables]}."""
    n_reps = len(next(iter(replies.values())))
    out = {}
    for name, vs in arms.items():
        reps, errors, blocked_right, caught_wrong = [], [], 0, 0
        for k in range(n_reps):
            rep = []
            for r in rows:
                raw = replies[r["id"]][k]
                base = score_row(r, hits[r["id"]], raw)
                gated = score_row(r, hits[r["id"]], gate(raw, hits[r["id"]], r["question"], vs, errors, mins))
                blocked_right += base and not gated
                caught_wrong += (not base) and gated
                rep.append(gated)
            reps.append(rep)
        out[name] = {"reps": reps, "errors": len(errors), "blocked_right": blocked_right, "caught_wrong": caught_wrong}
    return out


def _load_call_jev():
    spec = importlib.util.spec_from_file_location("jev_hook", Path(__file__).resolve().parents[2] / ".claude/hooks/jev_hook.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.call_jev


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--golden", nargs="+", required=True, type=Path)
    ap.add_argument("--data", required=True, type=Path)
    ap.add_argument("--ar", required=True, type=Path)
    ap.add_argument("--env", type=Path, help="optional .env file; the NVIDIA_API_KEY environment variable wins")
    ap.add_argument("--model", required=True, help="the Nemotron NIM model id")
    ap.add_argument("--laya-dir", type=Path, default=os.environ.get("LAYA_DIR"), help="default: $LAYA_DIR")
    ap.add_argument("--jev-min", type=float, default=0.5)
    ap.add_argument("--laya-min", type=float, default=0.5, help="zero-shot Laya is overconfident; tune on a held-out split, not these rows")
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("-k", type=int, default=5)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if not a.laya_dir:
        ap.error("--laya-dir or the LAYA_DIR environment variable is required")
    from laya import Agent
    from vps_extraction.ask import ask
    from vps_extraction.eval_multi_index import load_chunks
    from vps_extraction.multi_index import build
    from vps_extraction.page_index import build_index
    key = load_key(a.env)
    rows = [r for f in a.golden for r in map(json.loads, f.open()) if r["kind"] in ANSWERABLE or r["kind"] == "not_in_corpus"]
    ar, multi = build_index(a.ar), build(load_chunks(a.data))
    hits = {r["id"]: ask(r["question"], ar, multi, a.k, width=900)["hits"] for r in rows}
    replies = {r["id"]: [] for r in rows}
    for _ in range(a.reps):
        for r in rows:
            try:
                replies[r["id"]].append(parse_reply(nim_call(key, a.model, build_prompt(r["question"], hits[r["id"]]))))
            except Exception as e:  # kind only: the request carries the key
                print(f"{r['id']}: {type(e).__name__}", file=sys.stderr)
                replies[r["id"]].append(None)
    verifiers = {"jev": jev_verifier(_load_call_jev()), "laya": laya_verifier(Agent(str(a.laya_dir), device="cpu"))}
    mins = {"jev": a.jev_min, "laya": a.laya_min}
    lines = [f"# combo-table ({len(rows)} rows, {a.reps} reps, generator {a.model}, top-{a.k} hits)\n",
             f"Noise floor: one row = {100 / len(rows):.1f} points; a gap below that is a tie (pick the cheaper arm).\n",
             "| arm | min % | max % | blocked right | caught wrong | verifier errors |", "|---|---|---|---|---|---|"]
    for name, names in ARMS.items():
        res = run_arms(rows, hits, replies, {name: [verifiers[n] for n in names]}, [mins[n] for n in names])[name]
        pct = [100 * sum(rep) / len(rep) for rep in res["reps"]]
        lines.append(f"| {name} | {min(pct):.1f} | {max(pct):.1f} | {res['blocked_right']} | {res['caught_wrong']} | {res['errors']} |")
    a.out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
