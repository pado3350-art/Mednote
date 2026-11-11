"""새 PAD 파일: 기출 문항마다 ‘문제 · 정답 · 이번 강의 기준 해설’을 한 문서로 쓴다 (③ PAD 섹션).

이번 강의 기준 해설 = (1) 노트에서 그 문항을 근거로 파랑이 된 문장(`slide_refs`에 문항 번호가 있는 문장·표)과 그 소절,
(2) 필요하면 `pad_notes.json`으로 직접 쓴 해설({"1001": {"answer": "...", "explanation": "..."}}).
스크립트에 없는 내용은 만들지 않는다: 근거 문장이 없으면 ‘이번 강의에서 직접 다루지 않음’(또는 ‘미수업’)으로 적는다.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from ..models import LectureNote
from .exam import ExamItem


def _plain(s: str) -> str:
    return re.sub(r"\{[a-z]\|([^}]*)\}", r"\1", s).replace("**", "").strip()


def evidence(note: LectureNote, number: int) -> list[tuple[str, str]]:
    """[(소절 제목, 근거 문장 또는 표 요약)] for the note statements that cite PAD unit `number`."""
    out: list[tuple[str, str]] = []
    for t in note.topics:
        if t.role == "front":
            continue
        for sts in t.sections.values():
            for st in sts:
                if number not in st.slide_refs or st.kind in ("figure", "diagram", "quiz"):
                    continue
                if st.kind == "rows":
                    cells = " / ".join(" · ".join(_plain(c).replace("\n", ", ") for c in row) for row in st.rows[:4])
                    text = "표: " + cells
                elif st.kind == "check":
                    text = f"{_plain(st.text)} → {st.answer}" + (f" ({_plain(st.explanations[0])})" if st.explanations else "")
                else:
                    text = _plain(st.text)
                if text and (t.heading, text) not in out:
                    out.append((t.heading, text))
        for b in t.basics if number in t.basics_refs else []:
            if (t.heading, _plain(b)) not in out:
                out.append((t.heading, _plain(b)))
    return out


def load_authored(path: str | Path | None) -> dict[int, dict]:
    if not path:
        return {}
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return {int(k): v for k, v in raw.items()}


def pad_commentary(items: list[ExamItem], note: LectureNote, authored: dict[int, dict] | None = None) -> str:
    """Markdown of the new PAD file."""
    authored = authored or {}
    L = [f"# {note.title} — 기출(PAD) 해설", "",
         "문제와 정답은 PAD 파일 그대로이고(파랑 = PAD 내용), ‘이번 강의 기준 해설’은 이번 스크립트로 쓴 노트의 근거 문장입니다.", ""]
    for it in items:
        ev = evidence(note, it.number)
        au = authored.get(it.number, {})
        L += [f"## {it.title}", ""]
        if it.signals:
            L += [f"- 출제 신호: {', '.join(it.signals)}"]
        L += [f"- 문제: {it.question.strip()}", f"- 정답: {au.get('answer') or it.answer.strip() or '(PAD에 없음)'}"]
        if it.commentary.strip():
            L += [f"- PAD 해설: {it.commentary.strip()}"]
        L += ["", "**이번 강의 기준 해설**", ""]
        if au.get("explanation"):
            L += [au["explanation"].strip(), ""]
        if ev:
            L += [f"- [{h}] {t}" for h, t in ev]
        elif not au.get("explanation"):
            L += ["- 이번 시간 범위 밖(미수업)입니다." if "미수업" in it.signals else "- 이번 스크립트에서 직접 다루지 않았습니다."]
        L += [""]
    covered = sum(1 for it in items if evidence(note, it.number) or authored.get(it.number, {}).get("explanation"))
    L += ["---", f"이번 강의에서 다룬 기출 {covered}/{len(items)}문항"]
    return "\n".join(L) + "\n"


def write_pad_commentary(items: list[ExamItem], note: LectureNote, out_md: str | Path, authored: dict[int, dict] | None = None) -> tuple[Path, Path]:
    """Writes <out_md> and a DOCX next to it (PAD parts in blue, the lecture-based commentary in black)."""
    from docx import Document
    from docx.shared import RGBColor

    out_md = Path(out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(pad_commentary(items, note, authored), encoding="utf-8")
    authored = authored or {}
    doc = Document()
    doc.add_heading(f"{note.title} — 기출(PAD) 해설", 0)
    blue = RGBColor(0x1F, 0x4E, 0xC8)
    for it in items:
        doc.add_heading(it.title, 2)
        for label, text in (("문제", it.question.strip()), ("정답", authored.get(it.number, {}).get("answer") or it.answer.strip()),
                            ("PAD 해설", it.commentary.strip())):
            if text:
                p = doc.add_paragraph()
                p.add_run(f"{label}: ").bold = True
                p.add_run(text).font.color.rgb = blue
        doc.add_paragraph().add_run("이번 강의 기준 해설").bold = True
        au = authored.get(it.number, {}).get("explanation")
        ev = evidence(note, it.number)
        if au:
            doc.add_paragraph(au.strip())
        for h, t in ev:
            doc.add_paragraph(f"[{h}] {t}", style="List Bullet")
        if not ev and not au:
            doc.add_paragraph("이번 시간 범위 밖(미수업)입니다." if "미수업" in it.signals else "이번 스크립트에서 직접 다루지 않았습니다.")
    out_docx = out_md.with_suffix(".docx")
    doc.save(out_docx)
    return out_md, out_docx
