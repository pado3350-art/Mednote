"""Slide pictures for the antibiotics note - taken from the human MOM PDF as IMAGES ONLY (its text is never read).

  python -m examples.abx_figs <MOM.pdf> [--out inputs/abx_figs]

pdfimages extracts every embedded picture (named img-<page>-<num>.png); the five real slide pictures are picked by
page/num, renamed, and the two PK/PD curves (f3, f4) are also placed side by side as f34_time_conc.png (the MOM itself
shows them in one table). Icons (160 px) are skipped. The page/num ids belong to THIS MOM file; for another lecture list
them first with `pdfimages -list <MOM.pdf>` and look at the pictures.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image

PICKS = {  # published name -> pdfimages file (page-num)
    "f1_quadrant.png": "img-002-012.png",  # 획득 경로 x 면역 4사분면 (slide)
    "f2_static_cidal.png": "img-006-033.png",  # bacteriostatic vs bactericidal curve
    "f3_time_dep.png": "img-003-017.png",  # time-dependent antibiotics
    "f4_conc_dep.png": "img-003-018.png",  # concentration-dependent antibiotics
    "f5_pkpd_index.png": "img-003-019.png",  # Cmax/MIC, AUC/MIC, T>MIC per drug
}


def side_by_side(a: str | Path, b: str | Path, out: str | Path, gap: int = 30) -> Path:
    """Two pictures on one white canvas (left, right), top aligned."""
    ia, ib = Image.open(a).convert("RGB"), Image.open(b).convert("RGB")
    canvas = Image.new("RGB", (ia.width + ib.width + gap, max(ia.height, ib.height)), "white")
    canvas.paste(ia, (0, 0))
    canvas.paste(ib, (ia.width + gap, 0))
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out)
    return Path(out)


def extract(mom_pdf: str | Path, out_dir: str | Path = "inputs/abx_figs") -> list[Path]:
    exe = shutil.which("pdfimages")
    if not exe:
        raise SystemExit("pdfimages(poppler-utils)가 필요합니다")
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run([exe, "-png", "-p", str(mom_pdf), f"{tmp}/img"], check=True, capture_output=True)
        done = []
        for name, src in PICKS.items():
            f = Path(tmp) / src
            if not f.exists():
                raise SystemExit(f"{src} 가 없습니다. 다른 MOM 파일이면 `pdfimages -list`로 번호를 다시 확인하세요")
            shutil.copy(f, out / name)
            done.append(out / name)
        done.append(side_by_side(out / "f3_time_dep.png", out / "f4_conc_dep.png", out / "f34_time_conc.png"))
    return done


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("mom_pdf")
    ap.add_argument("--out", default="inputs/abx_figs")
    for p in extract(**{"mom_pdf": ap.parse_args().mom_pdf, "out_dir": ap.parse_args().out}):
        print(p)
