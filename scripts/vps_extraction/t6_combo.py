"""T6 combination: Nemotron (generator) + Jev and/or Laya (cheap verifiers that can only say "no").

One Nemotron reply per (row, rep) is generated once and shared by every arm, so arms differ ONLY by
the gate. A gate can turn an answer into a refusal, never the reverse, and fails closed: a verifier
that errors or is unreachable counts as "no" and is reported, not hidden.
Arms: nemotron | nemotron+jev | nemotron+laya | nemotron+jev+laya. Scoring is the same code scorer
as t6_models (a model never grades a model). Advisory-only tiers: this measures them, it gates nothing
in the repo.

usage (VPS; NVIDIA_API_KEY and TYPESAFE_API_KEY as project environment variables, LAYA_CHECKPOINT optional):
  t6_combo.py --golden docs/vps-extraction/golden.jsonl docs/vps-extraction/golden_new.jsonl \
     --data BIOCON/data --ar BIOCON/annual-report/FY26 \
     --model <nemotron-nim-id> --reps 3 --out docs/vps-extraction/combo-table.md
"""
import argparse
import json
import os
import sys
from pathlib import Path

from vps_extraction.t6_models import ANSWERABLE, build_prompt, parse_reply, score_row

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


_INSTR = "The excerpt states that the proposed answer is correct for the question."


def jev_verifier(client, noul_cls):
    """client = typesafe_sdk.TypeSafeClient() and noul_cls = typesafe_sdk.Noul (the path soic-ladder's
    jev_vs_nemotron.py already runs on the VPS). One noul question; returns P(yes)."""
    def v(question, answer, excerpt):
        text = f"Question: {question}\nProposed answer: {answer}\nExcerpt: {excerpt}"
        return float(client.system_one(state=text, questions={"ok": noul_cls(instructions=_INSTR)}).nouls["ok"].noul)
    return v


def laya_verifier(agent):
    """agent = laya.load(...) (the soic-ladder pattern); one noul question, P(yes)."""
    q = {"ok": {"type": "noul", "instructions": "The excerpt states that the proposed answer is correct for the question.",
                "criteria": {"false": "The excerpt does not state this answer.", "true": "The excerpt states this answer."}}}

    def v(question, answer, excerpt):
        text = f"Question: {question}\nProposed answer: {answer}\nExcerpt: {excerpt}"
        return float(agent.system_one(text, q)["answers"]["ok"]["noul"])
    return v


def collect_replies(rows, hits, reps, generate):
    """generate(prompt) -> (text, error_or_None). Returns ({id: [parsed reply per rep]}, [(id, reason)])."""
    replies, errors = {r["id"]: [] for r in rows}, []
    for _ in range(reps):
        for r in rows:
            text, err = generate(build_prompt(r["question"], hits[r["id"]]))
            if err:
                errors.append((r["id"], err))
            replies[r["id"]].append(parse_reply(text) if text else None)
    return replies, errors


def check_error_rate(errors, total, limit=0.5):
    """A table built from failed calls is a lie (every arm 0%). Stop instead, naming the reasons."""
    if total and len(errors) / total > limit:
        reasons = sorted({e[1] for e in errors})[:3]
        raise SystemExit(f"t6_combo: {len(errors)} of {total} Nemotron calls failed; no table written. Reasons: {reasons}")


def nim_generate(model):
    """The soic-ladder client (retries, key scrubbing, reasoning kept apart); needs src/ on PYTHONPATH."""
    from soic_ladder.commentary_llm import call_nvidia_parts

    def generate(prompt):
        parts, meta = call_nvidia_parts(prompt, model, max_tokens=900, system="/no_think")
        if parts is None:
            return None, meta.summary
        return parts.content, (None if parts.content.strip() else f"empty content (finish={parts.finish_reason})")
    return generate


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


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--golden", nargs="+", required=True, type=Path)
    ap.add_argument("--data", required=True, type=Path)
    ap.add_argument("--ar", required=True, type=Path)
    ap.add_argument("--model", default="nvidia/nemotron-3-super-120b-a12b",
                    help="Nemotron NIM id; default is the one soic-ladder's 2026-08-30 briefs used (not re-checked against NIM today)")
    ap.add_argument("--laya-checkpoint", default=os.environ.get("LAYA_CHECKPOINT"),
                    help="local Laya dir; default $LAYA_CHECKPOINT, else the published typed-decisions checkpoint (as soic-ladder does)")
    ap.add_argument("--jev-min", type=float, default=0.5)
    ap.add_argument("--laya-min", type=float, default=0.5, help="zero-shot Laya is overconfident; tune on a held-out split, not these rows")
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("-k", type=int, default=5)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    import laya
    from typesafe_sdk import Noul, TypeSafeClient
    from vps_extraction.ask import ask
    from vps_extraction.eval_multi_index import load_chunks
    from vps_extraction.multi_index import build
    from vps_extraction.page_index import build_index
    rows = [r for f in a.golden for r in map(json.loads, f.open()) if r["kind"] in ANSWERABLE or r["kind"] == "not_in_corpus"]
    ar, multi = build_index(a.ar), build(load_chunks(a.data))
    hits = {r["id"]: ask(r["question"], ar, multi, a.k, width=900)["hits"] for r in rows}
    replies, errors = collect_replies(rows, hits, a.reps, nim_generate(a.model))
    for rid, why in errors[:5]:
        print(f"{rid}: {why}", file=sys.stderr)
    check_error_rate(errors, len(rows) * a.reps)
    verifiers = {"jev": jev_verifier(TypeSafeClient(), Noul), "laya": laya_verifier(laya.load(a.laya_checkpoint) if a.laya_checkpoint else laya.load("convaiinnovations/laya", subfolder="typed-decisions"))}
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
