"""The one place PDFs are read: native text first, OCR only on pages with no text layer.

Offline: OCR is injected (the same seam idea as the Instagram ``post_fetch``). One integration test runs real
LiteParse OCR and skips itself when LiteParse / Pillow are not installed.
"""

import io
import sys

import pytest

from media_core.pdf_text import OcrUnavailable, PdfTextError, _ranges, extract_pdf_text

LONG = "Standalone total assets as at 31 March 2017 were 10346.32 crores"


def make_pdf(pages):
    """Minimal PDF. A str page has a native text layer; None is an image-only page (a 'scan', no text layer)."""
    n = 4 + 2 * len(pages)
    kids = " ".join(f"{6 + 2 * i} 0 R" for i in range(len(pages)))
    objs = {
        1: b"<< /Type /Catalog /Pages 2 0 R >>",
        2: f"<< /Type /Pages /Kids [{kids}] /Count {len(pages)} >>".encode(),
        3: b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        4: (b"<< /Type /XObject /Subtype /Image /Width 2 /Height 2 /ColorSpace /DeviceRGB "
            b"/BitsPerComponent 8 /Length 12 >>\nstream\n" + bytes(12) + b"\nendstream"),
    }
    for i, text in enumerate(pages):
        content_id, page_id = 5 + 2 * i, 6 + 2 * i
        content = b"q 400 0 0 400 100 300 cm /Im0 Do Q" if text is None else f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET".encode()
        objs[content_id] = b"<< /Length %d >>\nstream\n" % len(content) + content + b"\nendstream"
        objs[page_id] = (f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents {content_id} 0 R "
                         "/Resources << /Font << /F1 3 0 R >> /XObject << /Im0 4 0 R >> >> >>").encode()
    out, offsets = b"%PDF-1.4\n", {}
    for k in sorted(objs):
        offsets[k] = len(out)
        out += f"{k} 0 obj\n".encode() + objs[k] + b"\nendobj\n"
    xref = len(out)
    out += f"xref\n0 {n + 1}\n".encode() + b"0000000000 65535 f \n"
    out += b"".join(f"{offsets[k]:010d} 00000 n \n".encode() for k in sorted(objs))
    out += f"trailer\n<< /Size {n + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    return out


def write(tmp_path, pages):
    p = tmp_path / "doc.pdf"
    p.write_bytes(make_pdf(pages))
    return p


def no_ocr(path, pages):
    raise AssertionError(f"OCR must not run, but was asked for pages {pages}")


def test_born_digital_pdf_is_read_natively_and_never_ocred(tmp_path):
    res = extract_pdf_text(write(tmp_path, [LONG, "Second page has plenty of native text too"]), ocr=no_ocr)
    assert [p.source for p in res.pages] == ["native", "native"]
    assert "10346.32" in res.pages[0].text
    assert res.ocr_pages == [] and res.empty_pages == []


def test_only_pages_without_a_text_layer_are_sent_to_ocr(tmp_path):
    calls = []

    def ocr(path, pages):
        calls.append(list(pages))
        return {2: "Revenue from operations 3602.20 read by OCR"}

    res = extract_pdf_text(write(tmp_path, [LONG, None, LONG]), ocr=ocr)
    assert calls == [[2]]
    assert [p.source for p in res.pages] == ["native", "ocr", "native"]
    assert "3602.20" in res.pages[1].text
    assert res.ocr_pages == [2]


def test_page_numbers_are_one_based_and_match_the_pdf(tmp_path):
    res = extract_pdf_text(write(tmp_path, [LONG, LONG, LONG]), ocr=no_ocr)
    assert [p.page for p in res.pages] == [1, 2, 3]


def test_a_sparse_native_page_counts_as_needing_ocr(tmp_path):
    seen = []

    def ocr(path, pages):
        seen.append(list(pages))
        return {1: "Standalone Financials Revenue 5,671 PBDIT 1,321"}

    res = extract_pdf_text(write(tmp_path, ["Hi", LONG]), ocr=ocr)  # 'Hi' is a title only: charts are images
    assert seen == [[1]]
    assert res.pages[0].source == "ocr"
    assert "5,671" in res.pages[0].text


def test_ocr_that_finds_less_than_the_native_text_does_not_replace_it(tmp_path):
    res = extract_pdf_text(write(tmp_path, ["Hi there"]), ocr=lambda path, pages: {1: ""})
    # native 'Hi there' (8 chars) is sparse -> OCR is tried; OCR returned nothing -> native text is kept, page is not empty
    assert res.pages[0].text == "Hi there"
    assert res.pages[0].source == "native"


def test_missing_ocr_backend_fails_loudly_instead_of_returning_blanks(tmp_path):
    def unavailable(path, pages):
        raise OcrUnavailable("install it")

    with pytest.raises(OcrUnavailable):
        extract_pdf_text(write(tmp_path, [LONG, None]), ocr=unavailable)


def test_missing_ocr_backend_can_be_tolerated_explicitly(tmp_path):
    def unavailable(path, pages):
        raise OcrUnavailable("install it")

    res = extract_pdf_text(write(tmp_path, [LONG, None]), ocr=unavailable, allow_missing_ocr=True)
    assert res.pages[1].source == "empty"
    assert res.empty_pages == [2]
    assert res.warnings and "OCR" in res.warnings[0]


def test_default_backend_names_the_install_command_when_liteparse_is_absent(tmp_path, monkeypatch):
    monkeypatch.setitem(sys.modules, "liteparse", None)  # makes `import liteparse` raise ImportError
    with pytest.raises(OcrUnavailable, match=r"pip install .*ocr"):
        extract_pdf_text(write(tmp_path, [None]))


def test_a_blank_divider_page_is_marked_empty_but_is_not_an_error(tmp_path):
    res = extract_pdf_text(write(tmp_path, [LONG, None]), ocr=lambda path, pages: {2: ""})
    assert res.pages[1].source == "empty"
    assert res.empty_pages == [2]


def test_a_document_with_no_recoverable_text_is_an_error(tmp_path):
    with pytest.raises(PdfTextError, match="no text"):
        extract_pdf_text(write(tmp_path, [None, None]), ocr=lambda path, pages: {})


def test_an_unreadable_file_is_a_pdf_text_error_not_a_raw_library_error(tmp_path):
    bad = tmp_path / "bad.pdf"
    bad.write_bytes(b"this is not a pdf")
    with pytest.raises(PdfTextError, match="bad.pdf"):
        extract_pdf_text(bad, ocr=no_ocr)


def test_one_page_pypdf_chokes_on_is_sent_to_ocr_and_does_not_kill_the_read(tmp_path, monkeypatch):
    from pypdf import PageObject

    real, calls = PageObject.extract_text, {"n": 0}

    def flaky(self, *a, **k):
        calls["n"] += 1
        if calls["n"] == 2:
            raise ValueError("pypdf choked on this page")
        return real(self, *a, **k)

    monkeypatch.setattr(PageObject, "extract_text", flaky)
    seen = []

    def ocr(path, pages):
        seen.append(list(pages))
        return {2: "page two recovered by OCR after pypdf failed"}

    res = extract_pdf_text(write(tmp_path, [LONG, LONG, LONG]), ocr=ocr)
    assert seen == [[2]]
    assert [p.source for p in res.pages] == ["native", "ocr", "native"]


def test_ocr_page_list_is_compressed_into_ranges_liteparse_understands():
    assert _ranges([1, 2, 3, 7, 9, 10]) == "1-3,7,9-10"
    assert _ranges([5]) == "5"


def test_cli_writes_one_text_file_per_page_and_reports_counts(tmp_path, capsys):
    from media_core.pdf_text import main

    pdf = write(tmp_path, [LONG, "Second page has plenty of native text too"])
    out = tmp_path / "pages"
    assert main([str(pdf), "--out", str(out)]) == 0
    assert (out / "p001.txt").read_text().startswith("Standalone total assets")
    assert (out / "p002.txt").exists()
    assert "2 pages, 0 OCR, 0 empty" in capsys.readouterr().out


def test_cli_exits_nonzero_with_a_clear_message_when_the_pdf_cannot_be_read(tmp_path, capsys):
    from media_core.pdf_text import main

    bad = tmp_path / "bad.pdf"
    bad.write_bytes(b"nope")
    assert main([str(bad), "--out", str(tmp_path / "o")]) == 1
    assert "cannot read" in capsys.readouterr().err


def test_real_liteparse_ocr_reads_a_scanned_page(tmp_path):
    pytest.importorskip("liteparse")
    PIL = pytest.importorskip("PIL.Image")
    from PIL import ImageDraw, ImageFont

    img = PIL.new("RGB", (1000, 300), "white")
    ImageDraw.Draw(img).text((40, 100), "Total assets 10346.32", fill="black", font=ImageFont.load_default(size=60))
    buf = io.BytesIO()
    img.save(buf, format="PDF", resolution=150)
    pdf = tmp_path / "scan.pdf"
    pdf.write_bytes(buf.getvalue())

    res = extract_pdf_text(pdf)
    assert res.pages[0].source == "ocr"
    assert "10346" in res.pages[0].text.replace(",", "").replace(" ", "")
