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


def _short(it: ExamItem) -> str:
    return (f"{it.cohort} Q{it.q_no}" if it.cohort else f"{it.year}년 Q{it.q_no}") if (it.cohort or it.year) else f"Q{it.q_no}"


def group_items(items: list[ExamItem], note: LectureNote, authored: dict[int, dict] | None = None) -> list[list[ExamItem]]:
    """Past questions of the same TYPE share one lecture-based commentary (written once per type).
    The author may name the type in pad_notes.json (`"group": "..."`); otherwise questions that the SAME parts of this lecture
    answer (identical evidence) form a type. Items without evidence stay alone. Order = first appearance."""
    authored = authored or {}
    groups: list[list[ExamItem]] = []
    keyed: dict[object, list[ExamItem]] = {}
    for it in items:
        name = (authored.get(it.number, {}).get("group") or "").strip()
        ev = frozenset(evidence(note, it.number))
        key = name or (ev if ev else None)
        if key is None:
            groups.append([it])
        elif key in keyed:
            keyed[key].append(it)
        else:
            keyed[key] = [it]
            groups.append(keyed[key])
    return groups


def group_evidence(group: list[ExamItem], note: LectureNote) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for it in group:
        for e in evidence(note, it.number):
            if e not in out:
                out.append(e)
    return out


def group_title(group: list[ExamItem], note: LectureNote, authored: dict[int, dict]) -> str:
    name = next((authored[i.number]["group"] for i in group if authored.get(i.number, {}).get("group")), "")
    if name:
        return name
    heads = list(dict.fromkeys(h for h, _ in group_evidence(group, note)))
    return " · ".join(heads) if heads else "이번 강의 범위 밖"


def _explanations(group: list[ExamItem], authored: dict[int, dict]) -> list[str]:
    seen: list[str] = []
    for it in group:
        e = (authored.get(it.number, {}).get("explanation") or "").strip()
        if e and e not in seen:
            seen.append(e)
    return seen


def pad_commentary(items: list[ExamItem], note: LectureNote, authored: dict[int, dict] | None = None) -> str:
    """Markdown of the new PAD file: one block per question TYPE (repeated questions merged), the lecture-based commentary once."""
    authored = authored or {}
    groups = group_items(items, note, authored)
    L = [f"# {note.title} — 기출(PAD) 해설", "",
         f"기출 {len(items)}문항을 {len(groups)}개 유형으로 묶었습니다. 문제·정답·PAD 해설은 PAD 파일 그대로이고(파랑 = PAD 내용), "
         "‘이번 강의 기준 해설’은 이번 스크립트로 쓴 노트의 근거 문장과 직접 쓴 해설이며 유형마다 한 번만 씁니다.", ""]
    covered = 0
    for gi, g in enumerate(groups, start=1):
        ev = group_evidence(g, note)
        title = group_title(g, note, authored)
        L += [f"## 유형 {gi}. {title} ({len(g)}문항: {', '.join(_short(i) for i in g)})", ""]
        for it in g:
            au = authored.get(it.number, {})
            L += [f"### {it.title}", ""]
            if it.signals:
                L += [f"- 출제 신호: {', '.join(it.signals)}"]
            L += [f"- 문제: {it.question.strip()}", f"- 정답: {au.get('answer') or it.answer.strip() or '(PAD에 없음)'}"]
            if it.commentary.strip():
                L += [f"- PAD 해설: {it.commentary.strip()}"]
            if au.get("answer_note"):
                L += [f"- 이번 강의로 보면: {au['answer_note'].strip()}"]
            L += [""]
        L += ["**이번 강의 기준 해설**", ""]
        exps = _explanations(g, authored)
        for e in exps:
            L += [e, ""]
        if ev:
            L += [f"- [{h}] {t}" for h, t in ev]
        elif not exps:
            L += ["- 이번 시간 범위 밖(미수업)입니다." if any("미수업" in i.signals for i in g) else "- 이번 스크립트에서 직접 다루지 않았습니다."]
        if ev or exps:
            covered += sum(1 for i in g if authored.get(i.number, {}).get("covered") is not False)
        L += [""]
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
    groups = group_items(items, note, authored)
    doc = Document()
    doc.add_heading(f"{note.title} — 기출(PAD) 해설", 0)
    doc.add_paragraph(f"기출 {len(items)}문항을 {len(groups)}개 유형으로 묶었습니다. 파랑 = PAD 내용, 검정 = 이번 강의 기준 해설(유형마다 한 번).")
    blue = RGBColor(0x1F, 0x4E, 0xC8)
    for gi, g in enumerate(groups, start=1):
        ev = group_evidence(g, note)
        heads = group_title(g, note, authored)
        doc.add_heading(f"유형 {gi}. {heads} ({len(g)}문항: {', '.join(_short(i) for i in g)})", 1)
        for it in g:
            au = authored.get(it.number, {})
            doc.add_heading(it.title, 3)
            for label, text in (("문제", it.question.strip()), ("정답", au.get("answer") or it.answer.strip()), ("PAD 해설", it.commentary.strip())):
                if text:
                    p = doc.add_paragraph()
                    p.add_run(f"{label}: ").bold = True
                    p.add_run(text).font.color.rgb = blue
            if au.get("answer_note"):
                p = doc.add_paragraph()
                p.add_run("이번 강의로 보면: ").bold = True
                p.add_run(au["answer_note"].strip())
        doc.add_paragraph().add_run("이번 강의 기준 해설").bold = True
        exps = _explanations(g, authored)
        for e in exps:
            doc.add_paragraph(e)
        for h, t in ev:
            doc.add_paragraph(f"[{h}] {t}", style="List Bullet")
        if not ev and not exps:
            doc.add_paragraph("이번 시간 범위 밖(미수업)입니다." if any("미수업" in i.signals for i in g) else "이번 스크립트에서 직접 다루지 않았습니다.")
    out_docx = out_md.with_suffix(".docx")
    doc.save(out_docx)
    return out_md, out_docx
