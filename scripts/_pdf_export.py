"""Shared headless-Chrome HTML-to-PDF export, used by the generate_*.py learning-pack scripts.

Extracted out of generate_sdcourse_luc.py, where this block had been
copy-pasted (Chrome path, CLI flags, and the stderr-substring success check)
from generate_vutr_spark.py, which had in turn copied it from
generate_learning_pack.py — three independent copies with no shared source
of truth. New generator scripts should import render_pdf() from here instead
of re-copying the subprocess invocation.
"""
import os
import subprocess

CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def render_pdf(html_path, pdf_path):
    """Render html_path to pdf_path via headless Chrome. Prints status; never raises."""
    try:
        result = subprocess.run(
            [CHROME_PATH, "--headless", "--disable-gpu",
             f"--print-to-pdf={pdf_path}",
             "--print-to-pdf-no-header", html_path],
            capture_output=True, text=True
        )
        if "bytes written" in result.stderr or "written to file" in result.stderr:
            size = os.path.getsize(pdf_path)
            print(f"PDF written: {pdf_path} ({size:,} bytes)")
        else:
            print("Chrome output:", result.stderr[-200:])
            print(f"HTML is ready at {html_path} — open in browser and Print → Save as PDF")
    except Exception as e:
        print(f"PDF generation error: {e}")
        print(f"HTML is ready at {html_path}")
