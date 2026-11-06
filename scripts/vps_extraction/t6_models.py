"""T6: does a free model answer the golden questions from SHORT retrieved text, at least as well as before?

For each golden row: retrieve top-k hits with ask(), show the model only those hits, demand JSON
{"answer", "cite"} or {"refuse": true}, then score with code (no model grades a model):
pass = every number of the row's tokens is in the answer AND on the cited hit AND the cite is a
hit that was shown; an unanswerable row passes only on refusal. Run 3 reps per model; report
min-max and the noise floor (one row = 100/N points; a gap smaller than that is a tie).

usage (on the VPS, where the key lives):
  t6_models.py --golden docs/vps-extraction/golden.jsonl docs/vps-extraction/golden_new.jsonl \
     --data BIOCON/data --ar BIOCON/annual-report/FY26 \
     --models <nim-model-id>,<nim-model-id> --reps 3 --out docs/vps-extraction/model-table.md
The key is read from the NVIDIA_API_KEY environment variable (or an optional --env file) and never printed or logged.
"""
import argparse
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

from vps_extraction.page_index import _has_number

URL = "https://integrate.api.nvidia.com/v1/chat/completions"
ANSWERABLE = {"page_grep", "announcement_grep", "call_grep", "deck_grep"}


def load_key(env_path=None) -> str:
    """NVIDIA_API_KEY from the environment (project env var) first, else from an optional .env file."""
    if os.environ.get("NVIDIA_API_KEY"):
        return os.environ["NVIDIA_API_KEY"]
    if env_path is None:
        raise RuntimeError("NVIDIA_API_KEY is not set in the environment and no --env file was given")
    for line in Path(env_path).read_text().splitlines():
        k, _, v = line.partition("=")
        if k.strip() == "NVIDIA_API_KEY" and v.strip().strip("'\""):
            return v.strip().strip("'\"")
    raise RuntimeError(f"NVIDIA_API_KEY not set in {env_path}")


def shown_text(h) -> str:
    """The text the model sees AND the scorer checks: the long page text if ask() gave it, else the short snippet."""
    return h.get("shown") or h.get("text") or h["snippet"]


def find_hit(hits, cite):
    """The shown hit a cite points at. Tolerates brackets, case, trailing junk ('AR p324] (annual-report)') and a
    truncated long label, but never guesses: 'AR p10' does not match 'AR p1'. None if nothing or more than one fits."""
    c = str(cite or "").strip().strip("[]").strip().lower()
    if not c:
        return None
    for h in hits:
        if h["label"].lower() == c:
            return h
    near = [h for h in hits if c.startswith(h["label"].lower()) and not c[len(h["label"]):][:1].isalnum()]
    if not near and len(c) >= 12:
        near = [h for h in hits if h["label"].lower().startswith(c)]
    return near[0] if len(near) == 1 else None


def build_prompt(question: str, hits) -> str:
    shown = "\n\n".join(f"[{h['label']}] ({h['source']})\n{shown_text(h)}" for h in hits)
    return ("Answer ONLY from the excerpts below. Copy numbers exactly, with their units. "
            "If the excerpts do not contain the answer, refuse; never guess.\n\n"
            f"{shown}\n\nQuestion: {question}\n\n"
            'Reply with JSON only: {"answer": "...", "cite": "<the [label] of the excerpt>"} '
            'or {"refuse": true}.')


def parse_reply(text: str):
    m = re.search(r"\{.*\}", text or "", re.S)
    if not m:
        return None
    try:
        out = json.loads(m.group(0))
    except ValueError:
        return None
    if not isinstance(out, dict):
        return None
    if isinstance(out.get("cite"), str):  # the prompt shows labels as [label]; accept the copy with brackets
        out["cite"] = out["cite"].strip().strip("[]").strip()
    return out


def _numbers(tokens):
    return [n for t in tokens for n in re.findall(r"\d[\d,]*(?:\.\d+)?", t)]


def _facts_present(row, answer, text) -> bool:
    nums = _numbers(row["tokens"])
    if nums:
        return all(_has_number(answer, n) and _has_number(text, n) for n in nums)
    words = [t.lower() for t in row["tokens"] if t.strip()]  # a row with no digits is checked on its words
    return bool(words) and all(w in answer.lower() and w in text.lower() for w in words)


def score_row(row, hits, reply) -> bool:
    return verdict(row, hits, reply) == "right"


UTILITY = {"right": 1, "refused": 0, "none": 0, "wrong": -1}  # a refusal beats a silent wrong number


def verdict(row, hits, reply) -> str:
    """right | refused | wrong | none (no usable reply). Unanswerable rows: refusing is right, answering is wrong."""
    if not reply:
        return "none"
    refused = reply.get("refuse") is True
    if row["kind"] not in ANSWERABLE:
        return "right" if refused else "wrong"
    if refused:
        return "refused"
    cited = find_hit(hits, reply.get("cite"))
    return "right" if cited and _facts_present(row, str(reply.get("answer", "")), shown_text(cited)) else "wrong"


def why_wrong(row, hits, reply) -> str:
    """The first reason score_row would fail this reply ("ok" if it passes). For the report, not for scoring."""
    if reply is None:
        return "no JSON in reply"
    if row["kind"] not in ANSWERABLE:
        return "ok" if reply.get("refuse") is True else "answered an unanswerable row"
    if reply.get("refuse") is True:
        return "refused an answerable row"
    cited = find_hit(hits, reply.get("cite"))
    if cited is None:
        return "cite is not a shown label"
    answer = str(reply.get("answer", ""))
    nums = _numbers(row["tokens"])
    if nums:
        if not all(_has_number(answer, n) for n in nums):
            return "number missing from answer"
        if not all(_has_number(shown_text(cited), n) for n in nums):
            return "number not on the cited hit"
        return "ok"
    return "ok" if _facts_present(row, answer, shown_text(cited)) else "words missing from answer or cited hit"


def summarize(results: dict) -> dict:
    """results: {model: [rep: [bool per row]]} -> min/max % over reps, plus the one-row noise floor."""
    out, n = {}, 0
    for model, reps in results.items():
        pct = [100 * sum(r) / len(r) for r in reps]
        out[model] = {"min": min(pct), "max": max(pct), "reps": len(reps)}
        n = len(reps[0])
    out["noise_floor"] = 100 / n if n else None
    return out


def nim_call(key: str, model: str, prompt: str) -> str:
    body = json.dumps({"model": model, "temperature": 0, "max_tokens": 400,
                       "messages": [{"role": "user", "content": prompt}]}).encode()
    req = urllib.request.Request(URL, body, {"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)["choices"][0]["message"]["content"]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--golden", nargs="+", required=True, type=Path)
    ap.add_argument("--data", required=True, type=Path)
    ap.add_argument("--ar", required=True, type=Path)
    ap.add_argument("--env", type=Path, help="optional .env file; the NVIDIA_API_KEY environment variable wins")
    ap.add_argument("--models", required=True)
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("-k", type=int, default=5)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    from vps_extraction.ask import ask
    from vps_extraction.eval_multi_index import load_chunks
    from vps_extraction.multi_index import build
    from vps_extraction.page_index import build_index
    key = load_key(a.env)
    rows = [r for f in a.golden for r in map(json.loads, f.open())
            if r["kind"] in ANSWERABLE or r["kind"] == "not_in_corpus"]
    ar, multi = build_index(a.ar), build(load_chunks(a.data))
    hits = {r["id"]: ask(r["question"], ar, multi, a.k, width=900)["hits"] for r in rows}
    results = {}
    for model in a.models.split(","):
        results[model] = []
        for _ in range(a.reps):
            rep = []
            for r in rows:
                try:
                    reply = parse_reply(nim_call(key, model, build_prompt(r["question"], hits[r["id"]])))
                except Exception as e:  # report the failure kind, never the request (it carries the key)
                    print(f"{model} {r['id']}: {type(e).__name__}", file=sys.stderr)
                    reply = None
                rep.append(score_row(r, hits[r["id"]], reply))
            results[model].append(rep)
    s = summarize(results)
    lines = [f"# model-table ({len(rows)} rows, {a.reps} reps, top-{a.k} hits)\n",
             f"Noise floor: one row = {s['noise_floor']:.1f} points; a gap below that is a tie (pick the cheaper model).\n",
             "| model | min % | max % |", "|---|---|---|"]
    lines += [f"| {m} | {v['min']:.1f} | {v['max']:.1f} |" for m, v in s.items() if m != "noise_floor"]
    a.out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
