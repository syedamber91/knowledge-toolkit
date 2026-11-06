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

from vps_extraction.t6_models import ANSWERABLE, build_prompt, parse_reply, score_row, why_wrong

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


def check_error_rate(errors, total, limit=0.5, list_models=None):
    """A table built from failed calls is a lie (every arm 0%). Stop instead, naming the reasons.
    On a 404 (model withdrawn / not on this account) also name the Nemotron ids that ARE available."""
    if total and len(errors) / total > limit:
        reasons = sorted({e[1] for e in errors})[:3]
        msg = f"t6_combo: {len(errors)} of {total} Nemotron calls failed; no table written. Reasons: {reasons}"
        if list_models and any("status=404" in e[1] for e in errors):
            try:
                msg += f" Available nemotron ids on this account (pass one with --model): {list_models()}"
            except Exception as e:  # the listing is a courtesy; never hide the real failure behind it
                msg += f" (could not list models: {type(e).__name__})"
        raise SystemExit(msg)


def nemotron_ids():
    """GET /v1/models with the key from the environment (never printed); ids containing 'nemotron'."""
    import requests
    from soic_ladder.commentary_llm import NVIDIA_MODELS_URL, resolve_api_key
    r = requests.get(NVIDIA_MODELS_URL, headers={"Authorization": f"Bearer {resolve_api_key()}"}, timeout=60)
    r.raise_for_status()
    return sorted(m["id"] for m in r.json().get("data", []) if "nemotron" in m.get("id", "").lower())


def nim_generate(model, max_tokens=2000, timeout_seconds=300, call=None, sleep=None):
    """The soic-ladder client (retries 5xx, key scrubbing, reasoning kept apart); needs src/ on PYTHONPATH.
    Measured 2026-11-05: 29 of 132 Ultra calls died on the client's 120 s read timeout, which it does not retry,
    so wait longer and retry a timeout here (3 tries)."""
    if call is None:
        from soic_ladder.commentary_llm import call_nvidia_parts as call
    if sleep is None:
        import time
        sleep = time.sleep

    def generate(prompt):
        for attempt in range(3):
            parts, meta = call(prompt, model, max_tokens=max_tokens, timeout_seconds=timeout_seconds, system="/no_think")
            if parts is not None:
                return parts.content, (None if parts.content.strip() else f"empty content (finish={parts.finish_reason})")
            if "transport_error" not in meta.summary:
                break
            sleep(5 * (attempt + 1))
        return None, meta.summary
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


def cached(v):
    """Ask the verifier once per input, so a threshold sweep costs no extra model calls."""
    memo = {}

    def w(q, a, e):
        if (q, a, e) not in memo:
            memo[(q, a, e)] = v(q, a, e)
        return memo[(q, a, e)]
    return w


GRID = [round(0.05 * i, 2) for i in range(20)]  # 0.0 = never block


def _net(rows, hits, replies, verifier, t):
    """Answers gained (+) or lost (-) vs no gate, summed over reps, at threshold t."""
    plain = run_arms(rows, hits, replies, {"p": []})["p"]["reps"]
    gated = run_arms(rows, hits, replies, {"g": [verifier]}, [t])["g"]["reps"]
    return sum(map(sum, gated)) - sum(map(sum, plain))


def tune(rows, hits, replies, verifier, grid=GRID):
    """Pick the threshold on even rows (train), report it on odd rows (test). Ties go to the lowest."""
    train, test = rows[0::2], rows[1::2]
    tr = {t: _net(train, hits, replies, verifier, t) for t in grid}
    best = max(grid, key=lambda t: (tr[t], -t))
    return {"best": best, "train": tr, "test": {t: _net(test, hits, replies, verifier, t) for t in grid}}


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
    ap.add_argument("--max-tokens", type=int, default=2000, help="reasoning models need room to think before they answer")
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
    replies, errors = collect_replies(rows, hits, a.reps, nim_generate(a.model, a.max_tokens))
    for rid, why in errors[:5]:
        print(f"{rid}: {why}", file=sys.stderr)
    check_error_rate(errors, len(rows) * a.reps, list_models=nemotron_ids)
    verifiers = {"jev": cached(jev_verifier(TypeSafeClient(), Noul)), "laya": cached(laya_verifier(laya.load(a.laya_checkpoint) if a.laya_checkpoint else laya.load("convaiinnovations/laya", subfolder="typed-decisions")))}
    mins = {"jev": a.jev_min, "laya": a.laya_min}
    lines = [f"# combo-table ({len(rows)} rows, {a.reps} reps, generator {a.model}, top-{a.k} hits)\n",
             f"Generator calls that returned no usable reply: {len(errors)} of {len(rows) * a.reps} (those rows count as wrong in every arm).\n",
             f"Noise floor: one row = {100 / len(rows):.1f} points; a gap below that is a tie (pick the cheaper arm).\n",
             "| arm | min % | max % | blocked right | caught wrong | verifier errors |", "|---|---|---|---|---|---|"]
    for name, names in ARMS.items():
        res = run_arms(rows, hits, replies, {name: [verifiers[n] for n in names]}, [mins[n] for n in names])[name]
        pct = [100 * sum(rep) / len(rep) for rep in res["reps"]]
        lines.append(f"| {name} | {min(pct):.1f} | {max(pct):.1f} | {res['blocked_right']} | {res['caught_wrong']} | {res['errors']} |")
    lines += ["", "Threshold sweep (answers gained vs no gate, summed over reps; train = even rows, test = odd rows):", ""]
    for name in ("jev", "laya"):
        try:
            tu = tune(rows, hits, replies, verifiers[name])
        except Exception as e:  # a sweep is extra; never lose the table above
            lines.append(f"- {name}: sweep failed ({type(e).__name__})")
            continue
        lines.append(f"- {name}: best threshold on train = {tu['best']}; on test rows it gives {tu['test'][tu['best']]:+d} "
                     f"(at 0.5: {tu['test'][0.5]:+d}). Full test curve: " + ", ".join(f"{t}:{v:+d}" for t, v in tu["test"].items()))
    from collections import Counter
    why = Counter(why_wrong(r, hits[r["id"]], rep) for r in rows for rep in replies[r["id"]])
    lines += ["", "Why the plain Nemotron replies were right or wrong (all rows x reps, before any gate):", ""]
    lines += [f"- {k}: {v}" for k, v in why.most_common()]
    bad = [(r["id"], rep) for r in rows for rep in replies[r["id"]] if why_wrong(r, hits[r["id"]], rep) != "ok"][:6]
    lines += ["", "First wrong replies (parsed JSON, 200 chars):", ""] + [f"- {rid}: {json.dumps(rep)[:200]}" for rid, rep in bad]
    a.out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
