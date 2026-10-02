"""Enforcement: every PDF in this repo is read through ``media_core.pdf_text`` and nowhere else.

A direct pypdf / pdfplumber / fitz / pdftotext call silently returns an empty string for a scanned or image-only page
(measured in the 2026-10-02 spike: 18 of 58 facts lost, with zero errors). The single reader fails loudly instead, so a second reader
anywhere in the repo is a bug. This test is the tripwire.
"""

import ast
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ALLOWED = REPO / "src" / "media_core" / "pdf_text.py"
SCAN = ["src", "scripts", "mcp_servers", "webapp/backend", ".claude"]
BANNED_MODULES = {
    "pypdf", "PyPDF2", "pdfplumber", "fitz", "pymupdf", "pdfminer", "pdftotext", "camelot", "tabula",
    "liteparse", "pytesseract", "tesserocr", "llama_parse", "llama_cloud_services", "unstructured",
}
BANNED_COMMANDS = ("pdftotext", "pdftoppm", "pdfimages", "tesseract")
# Explicit, reasoned exceptions (repo-relative path prefixes). Keep this list short; a new entry needs a reason.
EXEMPT = {
    ".claude/skills/last30days/": "vendored third-party social-media research skill (mvanhorn/last30days-skill); "
                                  "its optional corpus feature shells out to pdftotext. Do not use it on financial filings.",
}


def violations_in_source(source: str) -> list[str]:
    """Names of banned PDF readers used by a piece of Python source."""
    try:
        tree = ast.parse(source)
    except SyntaxError:  # newer syntax than this interpreter: fall back to a line scan rather than skip the file
        mods = "|".join(sorted(BANNED_MODULES))
        found = [m.group(1) for m in re.finditer(rf"^\s*(?:import|from)\s+({mods})\b", source, re.M)]
        return found + [c for c in BANNED_COMMANDS if re.search(rf"""['"]{c}['"]""", source)]
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found += [a.name for a in node.names if a.name.split(".")[0] in BANNED_MODULES]
        elif isinstance(node, ast.ImportFrom) and node.module and node.module.split(".")[0] in BANNED_MODULES:
            found.append(node.module)
        elif isinstance(node, ast.Constant) and isinstance(node.value, str) and node.value in BANNED_COMMANDS:
            found.append(node.value)
    return found


def test_the_checker_catches_every_kind_of_direct_pdf_reader():
    assert violations_in_source("import pypdf") == ["pypdf"]
    assert violations_in_source("from pdfplumber import open") == ["pdfplumber"]
    assert violations_in_source("import fitz as f") == ["fitz"]
    assert violations_in_source("from liteparse import LiteParse") == ["liteparse"]
    assert violations_in_source("subprocess.run(['pdftotext', 'a.pdf', '-'])") == ["pdftotext"]
    assert violations_in_source("import json\nfrom pathlib import Path\nprint('pdf')") == []


def test_a_file_this_python_cannot_parse_is_still_scanned_not_skipped():
    # e.g. a vendored script using newer syntax than the interpreter running the tests
    assert violations_in_source("import pdfplumber\nx = ((( not valid python") == ["pdfplumber"]
    assert violations_in_source("from fitz import open\nx = ((( oops") == ["fitz"]
    assert violations_in_source("x = ((( oops\nimport json") == []


def find_offenders(repo: Path) -> list[str]:
    offenders = []
    for top in SCAN:
        for py in (repo / top).rglob("*.py"):
            rel = py.relative_to(repo)  # judge the path inside the repo: the repo itself may sit under .../worktrees/
            if ("worktrees" in rel.parts or "node_modules" in rel.parts or rel == ALLOWED.relative_to(REPO)
                    or any(rel.as_posix().startswith(prefix) for prefix in EXEMPT)):
                continue
            bad = violations_in_source(py.read_text(encoding="utf-8", errors="ignore"))
            if bad:
                offenders.append(f"{rel.as_posix()}: {sorted(set(bad))}")
    return offenders


def test_the_scan_still_works_when_the_repo_itself_lives_inside_a_worktrees_folder(tmp_path):
    repo = tmp_path / ".claude" / "worktrees" / "wt"  # exactly where this repo is checked out
    (repo / "src" / "media_core").mkdir(parents=True)
    (repo / "src" / "x.py").write_text("import pdfplumber\n")
    (repo / "src" / "media_core" / "pdf_text.py").write_text("import pypdf\n")  # the one allowed reader
    (repo / ".claude" / "worktrees" / "other" / "src").mkdir(parents=True)
    (repo / ".claude" / "worktrees" / "other" / "src" / "y.py").write_text("import fitz\n")  # a different checkout: ignored
    assert find_offenders(repo) == ["src/x.py: ['pdfplumber']"]


def test_no_file_reads_pdfs_except_media_core_pdf_text():
    offenders = find_offenders(REPO)
    assert not offenders, (
        "Read PDFs through media_core.pdf_text.extract_pdf_text (native text, OCR on image-only pages, fails loudly). "
        "Direct readers found:\n  " + "\n  ".join(offenders)
    )


def test_the_single_reader_exists_where_the_guard_expects_it():
    assert ALLOWED.exists(), "update ALLOWED in this test if media_core.pdf_text moved"


def test_every_exemption_still_points_at_something_that_exists():
    stale = [prefix for prefix in EXEMPT if not (REPO / prefix).exists()]
    assert not stale, f"remove these exemptions, the code is gone: {stale}"
