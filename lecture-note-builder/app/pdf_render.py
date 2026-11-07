"""DOCX -> PDF via LibreOffice (optional) and heading page lookup for the TOC."""
from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from pathlib import Path


def render_pdf(docx: Path, out_dir: Path | None = None) -> Path | None:
    exe = shutil.which("soffice") or shutil.which("libreoffice")
    if not exe:
        return None
    out_dir = out_dir or docx.parent
    with tempfile.TemporaryDirectory() as profile:
        try:
            subprocess.run(
                [exe, f"-env:UserInstallation=file://{profile}", "--headless", "--convert-to", "pdf",
                 "--outdir", str(out_dir), str(docx)],
                check=True, capture_output=True, timeout=180,
            )
        except (subprocess.SubprocessError, OSError):
            return None
    pdf = out_dir / (docx.stem + ".pdf")
    return pdf if pdf.exists() else None


def page_texts(pdf: Path) -> list[str]:
    exe = shutil.which("pdftotext")
    if not exe:
        return []
    txt = subprocess.run([exe, "-layout", str(pdf), "-"], capture_output=True, text=True).stdout
    return txt.split("\f")


def heading_pages(pdf: Path, headings: list[str], skip_pages: int = 1) -> dict[int, int]:
    """First page (after the cover/TOC page) where each heading appears."""
    pages = page_texts(pdf)
    norm = lambda s: re.sub(r"\s+", "", s)
    result: dict[int, int] = {}
    for i, h in enumerate(headings):
        for pn, text in enumerate(pages, start=1):
            if pn <= skip_pages:
                continue
            if norm(h) in norm(text):
                result[i] = pn
                break
    return result
