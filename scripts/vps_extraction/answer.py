"""answer: ask() finds the pages, a model reads them, CODE checks the result. No model grades a model.

The model returns {"answer", "cite"} or {"refuse": true}. The answer is kept only if the cite is a shown hit and
EVERY figure in the answer is on that cited page's text. Anything else is a refusal with its reason: never a
guess, never a silent fallback to memory. Measured (docs/vps-extraction/08-t4-retrieval.md Run 12-13): Nemotron Ultra
86-89% right on the golden exam, 78% on Claude's BIOCON truth table with 2 wrong of 117; Jev/Laya added nothing.
Limit: "the figure is on the cited page" proves provenance, not that it belongs to the line item asked about.
"""
import json
import re
from pathlib import Path

from vps_extraction.page_index import _has_number
from vps_extraction.t6_models import build_prompt, find_hit, parse_reply, shown_text

_FIGURE = re.compile(r"\d[\d,]*(?:\.\d+)?%?")


def numbers_in(text: str):
    """Figures worth verifying: with a comma, decimal point or %, or at least 3 digits. Drops 'FY26', '3 quarters'."""
    return [m for m in _FIGURE.findall(text or "")
            if re.search(r"[,.%]", m) or len(re.sub(r"\D", "", m)) >= 3]


def check_answer(reply, hits):
    """(ok, cited_hit_or_None, why_not). Every figure of the answer must be on the cited hit."""
    cited = find_hit(hits, (reply or {}).get("cite"))
    if cited is None:
        return False, None, "cite is not a shown excerpt"
    answer = str((reply or {}).get("answer", ""))
    figures = numbers_in(answer)
    if not figures:
        return False, cited, "the answer has no figure to verify"
    text = shown_text(cited)
    missing = [f for f in figures if not _has_number(text, f.rstrip("%"))]
    if missing:
        return False, cited, f"number {missing[0]} is not on the cited page"
    return True, cited, ""


def answer(question, hits, generate):
    """generate(prompt) -> (text, error_or_None). Returns {status, answer, cite, source, reason}."""
    text, err = generate(build_prompt(question, hits))
    if err or not text:
        return {"status": "refuse", "reason": f"model call failed: {err or 'empty reply'}"}
    reply = parse_reply(text)
    if reply is None:
        return {"status": "refuse", "reason": "no JSON in the model reply"}
    if reply.get("refuse") is True:
        return {"status": "refuse", "reason": "the model found no answer in the excerpts"}
    ok, cited, why = check_answer(reply, hits)
    if not ok:
        return {"status": "refuse", "reason": why}
    return {"status": "ok", "answer": str(reply["answer"]), "cite": cited["label"], "source": cited["source"], "reason": ""}


def group_questions(questions, hits_by_id, size=6):
    """Batches of at most `size`, with questions that share their top page kept together (so a page is sent once)."""
    by_top = {}
    for q in questions:
        hs = hits_by_id.get(q["id"]) or []
        by_top.setdefault(hs[0]["label"] if hs else "", []).append(q)
    flat = [q for qs in by_top.values() for q in qs]
    return [flat[i:i + size] for i in range(0, len(flat), size)]


def union_hits(group, hits_by_id):
    seen, out = set(), []
    for q in group:
        for h in hits_by_id.get(q["id"]) or []:
            if h["label"] not in seen:
                seen.add(h["label"])
                out.append(h)
    return out


def build_batch_prompt(group, hits_by_id) -> str:
    pages = "\n\n".join(f"[{h['label']}] ({h['source']})\n{shown_text(h)}" for h in union_hits(group, hits_by_id))
    qs = "\n".join(f"{i}. {q['question']}" for i, q in enumerate(group, 1))
    return ("Answer ONLY from the excerpts below. Copy numbers exactly, with their units. Each question needs its own answer. "
            "If the excerpts do not contain an answer, refuse that question; never guess.\n\n"
            f"{pages}\n\nQuestions:\n{qs}\n\n"
            'Reply with JSON only: {"answers": [{"q": 1, "answer": "...", "cite": "<the [label] of the excerpt>"}, '
            '{"q": 2, "refuse": true}, ...]} with one entry per question number.')


def parse_batch_reply(text):
    m = re.search(r"\{.*\}", text or "", re.S)
    if not m:
        return None
    try:
        items = json.loads(m.group(0)).get("answers")
    except (ValueError, AttributeError):
        return None
    if not isinstance(items, list):
        return None
    out = {}
    for it in items:
        if isinstance(it, dict) and isinstance(it.get("q"), int):
            r = {k: v for k, v in it.items() if k != "q"}
            if isinstance(r.get("cite"), str):
                r["cite"] = r["cite"].strip().strip("[]").strip()
            out[it["q"]] = r
    return out


def answer_batch(questions, hits_by_id, generate, size=6):
    """Grep once for everything, send each page once, ask `size` questions per call. Each answer is still
    code-checked against ITS cited page. generate(prompt) -> (text, error). Returns {question id: result}."""
    out = {}
    for group in group_questions(questions, hits_by_id, size):
        hits = union_hits(group, hits_by_id)
        text, err = generate(build_batch_prompt(group, hits_by_id))
        parsed = None if err or not text else parse_batch_reply(text)
        for i, q in enumerate(group, 1):
            if err or not text:
                out[q["id"]] = {"status": "refuse", "reason": f"model call failed: {err or 'empty reply'}"}
            elif parsed is None:
                out[q["id"]] = {"status": "refuse", "reason": "no JSON in the model reply"}
            elif i not in parsed:
                out[q["id"]] = {"status": "refuse", "reason": "no answer returned for this question"}
            elif parsed[i].get("refuse") is True:
                out[q["id"]] = {"status": "refuse", "reason": "the model found no answer in the excerpts"}
            else:
                ok, cited, why = check_answer(parsed[i], hits)
                out[q["id"]] = ({"status": "ok", "answer": str(parsed[i]["answer"]), "cite": cited["label"], "source": cited["source"], "reason": ""}
                                if ok else {"status": "refuse", "reason": why})
    return out


def ask_and_answer(question, ar_conn, multi_conn, generate, k=5, note=None, when=""):
    from vps_extraction.ask import ask
    hits = ask(question, ar_conn, multi_conn, k, width=900)["hits"]
    result = answer(question, hits, generate) if hits else {"status": "refuse", "reason": "nothing matched"}
    if note:
        write_answer_note(note, question, result, when)
    return result


def write_answer_note(path, question: str, result: dict, when: str) -> None:
    """Append one dated section to an Obsidian note. Never overwrites."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    head = f"\n## {when} - {question}\n"
    if result["status"] == "ok":
        body = f"**ANSWER** - {result['answer']}\n- source: `{result['source']} {result['cite']}` (figures checked against that page; not proof it is the line item asked about)\n"
    else:
        body = f"**REFUSE** - {result['reason']}\n"
    with path.open("a") as f:
        f.write(head + body)
