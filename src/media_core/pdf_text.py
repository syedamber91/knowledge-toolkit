"""The ONE place PDFs are read in this repo (financial filings, annual reports, decks, concall transcripts).

Native text first (pypdf, fast); only pages that come back with no usable text layer are OCR'd (LiteParse, local, optional
extra). Measured on 6 real filings (output/llama_extraction_spike): plain pypdf silently returned nothing for scanned and
image-only pages and lost 18 of 58 facts without raising; this module raises instead. Nothing else in the repo may import
a PDF/OCR library -- ``tests/test_pdf_ingest_guard.py`` fails the build if it does.

Local only: no document leaves the machine.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Callable, Dict, List, Literal, Optional, Sequence

from pydantic import BaseModel
from pypdf import PdfReader
from pypdf.errors import PyPdfError

MIN_CHARS = 20  # a page with fewer non-space characters than this has no usable text layer (title-only chart slides, scans)

OcrFn = Callable[[Path, Sequence[int]], Dict[int, str]]


class PdfTextError(RuntimeError):
    """The PDF could not be turned into text."""


class OcrUnavailable(PdfTextError):
    """Pages need OCR but no OCR backend is installed."""


class PageText(BaseModel):
    page: int  # 1-based, same numbering as the PDF viewer
    text: str
    source: Literal["native", "ocr", "empty"]


class PdfText(BaseModel):
    path: str
    pages: List[PageText]
    warnings: List[str] = []

    @property
    def ocr_pages(self) -> List[int]:
        return [p.page for p in self.pages if p.source == "ocr"]

    @property
    def empty_pages(self) -> List[int]:
        return [p.page for p in self.pages if p.source == "empty"]


def _ranges(pages: Sequence[int]) -> str:
    """[1,2,3,7,9,10] -> '1-3,7,9-10' (LiteParse ``target_pages`` syntax)."""
    out: List[str] = []
    run: List[int] = []
    for n in sorted(pages):
        if run and n == run[-1] + 1:
            run.append(n)
            continue
        if run:
            out.append(f"{run[0]}-{run[-1]}" if len(run) > 1 else f"{run[0]}")
        run = [n]
    if run:
        out.append(f"{run[0]}-{run[-1]}" if len(run) > 1 else f"{run[0]}")
    return ",".join(out)


def _native_pages(path: Path) -> List[str]:
    try:
        pages = PdfReader(str(path)).pages
        n = len(pages)
    except PyPdfError as e:
        raise PdfTextError(f"cannot read {path}: {e}") from e
    out: List[str] = []
    for i in range(n):
        try:
            out.append(pages[i].extract_text() or "")
        except Exception:  # a page pypdf chokes on is just a page that needs OCR, not a reason to lose the document
            out.append("")
    return out


def liteparse_ocr(path: Path, pages: Sequence[int]) -> Dict[int, str]:
    """Default OCR backend: LiteParse (pdfium + Tesseract) on just ``pages``."""
    try:
        from liteparse import LiteParse
    except ImportError as e:
        raise OcrUnavailable(
            "scanned or image-only pages need OCR but LiteParse is not installed: pip install -e '.[ocr]' (Python >= 3.10)"
        ) from e
    parser = LiteParse(ocr_enabled=True, ocr_language="eng", dpi=150, output_format="text", quiet=True,
                       target_pages=_ranges(pages))
    return {p.page_num: p.text for p in parser.parse(str(path)).pages}


def extract_pdf_text(path, *, ocr: Optional[OcrFn] = None, min_chars: int = MIN_CHARS,
                     allow_missing_ocr: bool = False) -> PdfText:
    """Per-page text for ``path``. Raises ``OcrUnavailable`` if pages need OCR and none is installed
    (``allow_missing_ocr=True`` downgrades that to a warning and marks the pages ``empty``), and ``PdfTextError``
    if no page yields any text at all."""
    path = Path(path)
    native = _native_pages(path)
    pages = {n: PageText(page=n, text=t, source="native") for n, t in enumerate(native, 1)}
    warnings: List[str] = []

    sparse = [n for n, t in enumerate(native, 1) if len(t.strip()) < min_chars]
    if sparse:
        try:
            found = (ocr or liteparse_ocr)(path, sparse)
        except OcrUnavailable as e:
            if not allow_missing_ocr:
                raise
            found = {}
            warnings.append(f"OCR unavailable, {len(sparse)} page(s) left empty: {e}")
        for n in sparse:
            recovered, kept = (found.get(n) or "").strip(), native[n - 1].strip()
            if len(recovered) > len(kept):
                pages[n] = PageText(page=n, text=recovered, source="ocr")
            elif not kept:
                pages[n] = PageText(page=n, text="", source="empty")

    result = PdfText(path=str(path), pages=[pages[n] for n in sorted(pages)], warnings=warnings)
    if not any(p.text.strip() for p in result.pages):
        raise PdfTextError(f"no text recovered from {path}")
    return result


def main(argv: Optional[Sequence[str]] = None) -> int:
    """``python -m media_core.pdf_text doc.pdf --out DIR`` writes DIR/p001.txt, p002.txt, ... (one file per page, the
    layout agents grep) and prints a one-line summary. Exit 1 with the reason on stderr if the PDF cannot be read."""
    import argparse

    ap = argparse.ArgumentParser(prog="python -m media_core.pdf_text", description=main.__doc__)
    ap.add_argument("pdf")
    ap.add_argument("--out", required=True, help="directory for the per-page text files")
    ap.add_argument("--allow-missing-ocr", action="store_true", help="leave image-only pages empty instead of failing")
    args = ap.parse_args(argv)
    try:
        res = extract_pdf_text(args.pdf, allow_missing_ocr=args.allow_missing_ocr)
    except PdfTextError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for p in res.pages:
        (out / f"p{p.page:03d}.txt").write_text(p.text, encoding="utf-8")
    print(f"{args.pdf}: {len(res.pages)} pages, {len(res.ocr_pages)} OCR, {len(res.empty_pages)} empty -> {out}")
    for w in res.warnings:
        print(f"warning: {w}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
