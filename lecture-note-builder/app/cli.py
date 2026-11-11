"""CLI:  python -m app.cli build lecture.pptx --script lecture.txt --out outputs/"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .write.generate_notes import AnthropicBackend, OfflineBackend, PrecomputedBackend
from .pipeline import run_pipeline

DEFAULT_TEMPLATE = Path(__file__).resolve().parent.parent / "templates" / "medical.yaml"
DEFAULT_TEMPLATE_MOM = Path(__file__).resolve().parent.parent / "templates" / "mom_mixed.yaml"  # mixed style = default (L10)


def _feedback(a) -> int:
    from .write import feedback as fbk

    if a.fcmd == "diff":
        rep = fbk.build_report(a.original, a.edited, a.lecture_type)
        jp, mp = fbk.save_report(rep, a.out)
        print(f"변경 {len(rep.changes)}건 · 규칙 후보 {len(rep.candidates)}개 (모두 미승인)")
        for k, v in rep.counts.items():
            print(f"  {fbk.CATEGORIES[k]:8s} {v}")
        print(f"report_json  {jp}\nreport_md    {mp}")
        print("※ 어떤 규칙도 저장·적용되지 않았습니다. 리포트를 보고 `feedback approve`로 승인한 것만 저장됩니다.")
        return 0
    if a.fcmd == "approve":
        try:
            rules = fbk.approve(a.report, a.ids, a.lecture_type, a.store, a.note, a.rule)
        except ValueError as e:
            print(f"오류: {e}")
            return 2
        for r in rules:
            print(f"승인 저장: {r.id} v{r.version} [{fbk.CATEGORIES.get(r.category, r.category)}] {r.rule}")
        print(f"저장소: {a.store or fbk.RULE_STORE} (v{fbk.load_store(a.store).store_version})")
        return 0
    if a.fcmd == "reject":
        fbk.reject(a.report, a.ids)
        print(f"거절 표시: {', '.join(a.ids)}")
        return 0
    if a.fcmd == "rules":
        if a.retire:
            r = fbk.retire(a.retire, a.store, a.reason)
            print(f"사용 중지: {r.id} v{r.version}")
            return 0
        print(fbk.approved_rules_markdown(a.lecture_type, a.store) or "승인된 규칙이 없습니다.")
        return 0
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(fbk.store_markdown(a.store), encoding="utf-8")
    print(f"rules_md     {out}")
    return 0


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
    b.add_argument("--pad-notes", help="새 PAD 파일에 넣을 직접 쓴 해설 JSON: {\"1001\": {\"answer\": \"...\", \"explanation\": \"...\"}}")
    b.add_argument("--meta-json", help="표지 정보 JSON: comment, tips(공부 전략), objectives(학습목표) … (목록은 줄바꿈 문자열 또는 배열)")
    b.add_argument("--name", help="출력 파일 기본 이름 (기본: 입력 파일 이름)")
    b.add_argument("--uncovered-pad", choices=["reference", "omit"], default="reference",
                   help="수업에서 다루지 않았다고 PAD 해설에 적힌 문항: reference(파랑 Reference로 싣기, 기본) / omit(생략 허용, 경고 없음)")
    b.add_argument("--no-pdf", action="store_true")
    pr = sub.add_parser("prepare", help="API 없이: Claude Code가 직접 노트를 쓰기 위한 작업 패킷(brief/) 생성")
    pr.add_argument("--script", required=True)
    pr.add_argument("--exam-pdf")
    pr.add_argument("--figures", nargs="+", metavar="PATH")
    pr.add_argument("--template", default=str(DEFAULT_TEMPLATE_MOM))
    pr.add_argument("--out", default="outputs/work")
    fb = sub.add_parser("feedback", help="수정한 DOCX와 AI 원본 DOCX 비교 → 수정 패턴 리포트 → (사용자 승인 후) 학습 규칙")
    fsub = fb.add_subparsers(dest="fcmd", required=True)
    fd = fsub.add_parser("diff", help="두 DOCX 비교, JSON·Markdown 리포트 저장 (규칙은 저장하지 않음)")
    fd.add_argument("original", help="AI가 생성한 원본 DOCX")
    fd.add_argument("edited", help="사용자가 수정한 DOCX")
    fd.add_argument("--out", default="feedback/reports")
    fd.add_argument("--lecture-type", default="", help="참고용 강의 유형 메모")
    fa = fsub.add_parser("approve", help="사용자가 승인한 후보만 학습 규칙으로 저장")
    fa.add_argument("report", help="feedback diff가 만든 JSON 리포트")
    fa.add_argument("--ids", nargs="+", required=True, help="승인할 후보 ID (예: R1 R3)")
    fa.add_argument("--lecture-type", nargs="+", required=True,
                    help="적용 강의 유형: all / concept_chain / list_intro / clinical")
    fa.add_argument("--note", default="", help="메모")
    fa.add_argument("--rule", default="", help="규칙 문장을 직접 지정 (후보 1개일 때)")
    fa.add_argument("--store")
    fj = fsub.add_parser("reject", help="후보를 거절로 표시 (규칙 저장소는 건드리지 않음)")
    fj.add_argument("report")
    fj.add_argument("--ids", nargs="+", required=True)
    fr = fsub.add_parser("rules", help="승인된 규칙 보기 / 사용 중지")
    fr.add_argument("--lecture-type", default="")
    fr.add_argument("--retire", help="사용 중지할 규칙 ID (예: L2)")
    fr.add_argument("--reason", default="")
    fr.add_argument("--store")
    fe = fsub.add_parser("export", help="승인된 규칙 전체를 Markdown으로 저장")
    fe.add_argument("--out", default="style_rules/approved_rules.md")
    fe.add_argument("--store")
    cm = sub.add_parser("compare-mom", help="생성 노트 PDF를 사람이 쓴 MOM PDF와 비교: 쪽 채움·글자 수·문체를 재고 남은 차이를 나열")
    cm.add_argument("mom", help="사람이 쓴 MOM PDF (비교 전용. 노트 생성에는 글을 읽지 않는다)")
    cm.add_argument("ours", help="생성한 노트 PDF")
    cm.add_argument("--note", help="생성 노트의 note.json (표 칸 문체, 제목 길이, 개념 Check 검사)")
    cm.add_argument("--out", help="리포트를 저장할 Markdown 경로")
    a = ap.parse_args(argv)
    if a.cmd == "compare-mom":
        from .design.mom_compare import compare, format_report

        report = format_report(compare(a.mom, a.ours, a.note))
        print(report)
        if a.out:
            Path(a.out).parent.mkdir(parents=True, exist_ok=True)
            Path(a.out).write_text(report, encoding="utf-8")
        return 0
    if a.cmd == "feedback":
        return _feedback(a)
    if a.cmd == "prepare":
        from .write.prepare import prepare_brief

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
    report, paths = run_pipeline(a.pptx, a.out, a.template, a.script, backend, a.title, meta, pdf=not a.no_pdf, pad_uncovered=a.uncovered_pad, exam_pdf=a.exam_pdf, toc=a.toc, outline_json=a.outline_json,
                                 figures=a.figures, figures_json=a.figures_json,
                                 max_figures_per_topic=a.max_figures_per_topic,
                                 keep_text_images=a.keep_text_images,
                                 summary_figures=a.summary_figures, name=a.name, pad_notes=a.pad_notes)
    for k, v in paths.items():
        print(f"{k:12s} {v}")
    print(f"coverage {report.slide_coverage:.0%}  errors {len(report.errors)}")
    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main())
