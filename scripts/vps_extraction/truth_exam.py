"""Exam rows from Claude's finished BIOCON truth table (truth-table.csv), plus the quarterly-filing text to search.

The table's values come from the 11 quarterly results filings, which the normal index does not hold; the
committed per-quarter statement excerpts (data/excerpts/consolidated-*.txt) are added as source "filing".
Caveat: the truth table is Claude's work, tied to XBRL for some quarters only; a mismatch means "check", not "wrong".
"""
import csv
from pathlib import Path

from vps_extraction.multi_index import Chunk

ITEMS = ["sale_of_products", "sale_of_services", "revenue_from_operations", "other_income", "total_income",
         "employee_benefits", "finance_costs", "depreciation", "other_expenses", "total_expenses",
         "profit_before_tax", "profit_for_period"]
MIN_VALUE = 1000


def truth_rows(path, items=ITEMS):
    rows = []
    for r in csv.DictReader(Path(path).open()):
        for it in items:
            try:
                n = abs(int(float(r[it])))
            except (KeyError, ValueError):
                continue
            if n < MIN_VALUE:
                continue
            label = it.replace("_", " ")
            rows.append({"id": f"T-{r['quarter_end']}-{it}", "kind": "filing_grep",
                         "question": f"Biocon consolidated {label} for the quarter ended {r['quarter_end']} (Rs million)?",
                         "expected": f"{n:,}", "tokens": [f"{n:,}"], "source": "truth-table.csv"})
    return rows


def filing_chunks(excerpt_dir):
    out = []
    for f in sorted(Path(excerpt_dir).glob("consolidated-*.txt")):
        date = f.stem.removeprefix("consolidated-")
        out.append(Chunk("filing", f"Filing {date}", f.read_text(errors="replace"), date))
    return out
