"""CLI:  python -m app.cli build lecture.pptx --script lecture.txt --out outputs/"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .generate_notes import AnthropicBackend, OfflineBackend, PrecomputedBackend
from .pipeline import run_pipeline

DEFAULT_TEMPLATE = Path(__file__).resolve().parent.parent / "templates" / "medical.yaml"
DEFAULT_TEMPLATE_MOM = Path(__file__).resolve().parent.parent / "templates" / "mom.yaml"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="mednote")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="PPTX (+ script) -> DOCX/MD lecture note")
    b.add_argument("pptx", nargs="?", help="PPTX (optional if the script has [mm:ss–mm:ss] block headers)")
    b.add_argument("--script", help="TXT/DOCX lecture script")
    b.add_argument("--template", default=str(DEFAULT_TEMPLATE))
    b.add_argument("--out", default="outputs")
    b.add_argument("--title")
    b.add_argument("--backend", choices=["offline", "anthropic"], default="offline")
    b.add_argument("--model")
    b.add_argument("--note-json", help="use pre-authored topics (note.json) instead of a backend")
    b.add_argument("--date", help="YYYY-MM-DD")
    b.add_argument("--subject")
    b.add_argument("--professor")
    b.add_argument("--author")
    b.add_argument("--period", help="예: 4교시")
    b.add_argument("--edition", help="표지 우측 라벨 (예: 기본편)")
    b.add_argument("--series", help="표지 큰 제목 (예: 시리즈명)")
    b.add_argument("--comment", help="작성자 코멘트 (use \\n for new lines)")
    b.add_argument("--exam-pdf", help="PAD(기출문제) PDF; 파랑 글씨는 여기 나온 내용에만 허용")
    b.add_argument("--toc", choices=["ai", "heuristic", "unit"],
                   help="목차 생성: ai(전체 흐름 판단, 기본: 스크립트 단독) / heuristic(오프라인) / unit(슬라이드별, PPTX 기본)")
    b.add_argument("--outline-json", help="수정한 목차(outline.json)를 그대로 사용")
    b.add_argument("--figures", nargs="+", metavar="PATH",
                   help="그림·사진 자료: PDF(강의록/슬라이드) · PPTX · 이미지 폴더. 본문 관련 문장 옆에 자동 배치")
    b.add_argument("--figures-json", help="수정한 figures.json(배치 결과)을 다시 적용")
    b.add_argument("--max-figures-per-topic", type=int, default=6)
    b.add_argument("--summary-figures", type=int, default=4, help="요약 정리 쪽에 넣을 핵심 그림 썸네일 수 (0 = 끔)")
    b.add_argument("--keep-text-images", action="store_true", help="글자뿐인 슬라이드 이미지도 그림으로 사용")
    b.add_argument("--no-auto-blue", action="store_true", help="오프라인 모드에서 PAD 자동 대조(파랑 표시)를 끈다")
    b.add_argument("--meta-json", help="표지 정보 JSON: comment, tips(공부 전략), objectives(학습목표) … (목록은 줄바꿈 문자열 또는 배열)")
    b.add_argument("--no-pdf", action="store_true")
    pr = sub.add_parser("prepare", help="API 없이: Claude Code가 직접 노트를 쓰기 위한 작업 패킷(brief/) 생성")
    pr.add_argument("--script", required=True)
    pr.add_argument("--exam-pdf")
    pr.add_argument("--figures", nargs="+", metavar="PATH")
    pr.add_argument("--template", default=str(DEFAULT_TEMPLATE_MOM))
    pr.add_argument("--out", default="outputs/work")
    a = ap.parse_args(argv)
    if a.cmd == "prepare":
        from .prepare import prepare_brief

        brief = prepare_brief(a.script, a.out, a.template, a.exam_pdf, a.figures)
        print(f"작업 패킷: {brief}  → Claude Code에서 `/make-lecture-note` 를 실행하거나 {brief / 'TASK.md'} 를 따르세요.")
        return 0
    if not a.pptx and not a.script:
        ap.error("pptx 또는 --script 필요")

    if a.note_json:
        backend = PrecomputedBackend.from_json(a.note_json)
    else:
        backend = OfflineBackend(auto_blue=not a.no_auto_blue) if a.backend == "offline" else AnthropicBackend(model=a.model)
    meta = {k: v for k in ("date", "subject", "professor", "author", "period", "edition", "series") if (v := getattr(a, k))}
    if a.meta_json:
        import json as _json

        for k, v in _json.loads(Path(a.meta_json).read_text(encoding="utf-8")).items():
            meta.setdefault(k, "\n".join(v) if isinstance(v, list) else str(v))
    if a.comment:
        meta["comment"] = a.comment.replace("\\n", "\n")
    report, paths = run_pipeline(a.pptx, a.out, a.template, a.script, backend, a.title, meta, pdf=not a.no_pdf, exam_pdf=a.exam_pdf, toc=a.toc, outline_json=a.outline_json,
                                 figures=a.figures, figures_json=a.figures_json,
                                 max_figures_per_topic=a.max_figures_per_topic,
                                 keep_text_images=a.keep_text_images,
                                 summary_figures=a.summary_figures)
    for k, v in paths.items():
        print(f"{k:12s} {v}")
    print(f"coverage {report.slide_coverage:.0%}  errors {len(report.errors)}")
    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main())
