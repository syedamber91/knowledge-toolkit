"""Build Laya-format rows (state / questions / gold) from the SOIC tagged notes.
One noul question per tag per note ("Is this note substantially about <tag>?"), same schema as
LocalLLaMA/typed-decisions so Laya's own MPS/Kaggle training script can consume it.
Tag definitions below are MINE (derived from the tag names), not from the vault - edit them if they drift."""
import json
from common import TAGS

DEFS = {
    "valuation": "valuing a business or stock: multiples, DCF, price vs value, SOTP, margin of safety",
    "quality-moat": "business quality and competitive advantage: moat, pricing power, ROCE/ROE, management quality",
    "forensic": "spotting accounting red flags, governance issues, earnings manipulation, free-float or promoter risk",
    "growth-drivers": "what drives revenue/profit growth: demand, capacity, new products, market share, operating leverage",
    "cyclicality": "business or sector cycles: commodity/rate/demand cycles and where in the cycle a company sits",
    "leverage-risk": "debt, interest coverage, balance-sheet and financing risk",
    "capital-allocation": "how management uses cash: capex, M&A, dividends, buybacks, reinvestment returns",
    "sector-macro": "sector structure and macro or policy forces acting on a sector",
    "technicals-timing": "price charts, trend, moving averages, relative strength, entry/exit timing",
    "position-sizing-portfolio": "position sizing, diversification, portfolio construction and risk limits",
    "behavioral-psychology": "investor psychology, biases, discipline and decision-making habits",
    "company-case-study": "a worked analysis of one specific named company",
}
STATE_CHARS = 3200  # ~800 tokens; Laya max_len is 1024 incl. the question


def question(tag):
    return {"type": "noul",
            "instructions": f"This note is substantially about {DEFS[tag]}.",
            "criteria": {"false": "The note does not substantially cover this.", "true": "The note substantially covers this."}}


def row(n, split):
    qs = {t: question(t) for t in TAGS}
    gold = {t: {"type": "noul", "label": "true" if t in n["tags"] else "false",
                "probabilities": {"false": 0.0 if t in n["tags"] else 1.0, "true": 1.0 if t in n["tags"] else 0.0}} for t in TAGS}
    return {"id": n["slug"], "split": split, "state": json.dumps({"title": n["title"], "note": n["text"][:STATE_CHARS]}),
            "questions": json.dumps(qs), "gold": json.dumps(gold)}
