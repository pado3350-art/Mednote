"""Slide pictures for '노인정신질환 1' - taken from the human MOM PDF as IMAGES ONLY (its text is never read for writing).

  python -m examples.geri_figs <MOM.pdf> [--out inputs/geri_figs]

The MOM embeds every slide as a 1280x720 picture (img-<page>-<num>.png); only real pictures (graphs, MRI, test forms,
diagram tables) are picked - text-only slides are not used as figures.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path

PICKS = {
    "g01_population.png": "img-002-001.png",  # 세계와 한국의 인구구조 2019/2067 (¶2)
    "g02_scheltens_mri.png": "img-004-005.png",  # Normal / MCI / AD MRI, Scheltens' scale (¶4)
    "g03_wmh_mri.png": "img-004-006.png",  # DWM, banding, capping (PWM) (¶5)
    "g04_cerad_snsb.png": "img-012-029.png",  # CERAD-NP vs SNSB 인지 영역 (¶10)
    "g05_tmt.png": "img-015-037.png",  # Trail making test A, B (¶10)
    "g06_big5.png": "img-016-040.png",  # 성격 5요인 (McCrae & Costa) (¶11)
    "g07_memory_tree.png": "img-018-046.png",  # 기억의 분류 (¶12)
    "g08_dep_ad.png": "img-032-082.png",  # depression as risk factor / prodrome of AD (¶20)
    "g09_suicide.png": "img-043-113.png",  # 자살률 추이, OECD 비교 (¶27)
    "g10_poverty.png": "img-044-115.png",  # 노인 상대빈곤율 국제비교 (¶27)
}


def extract(mom_pdf: str | Path, out_dir: str | Path = "inputs/geri_figs") -> list[Path]:
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
    return done


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("mom_pdf")
    ap.add_argument("--out", default="inputs/geri_figs")
    a = ap.parse_args()
    for p in extract(a.mom_pdf, a.out):
        print(p)
