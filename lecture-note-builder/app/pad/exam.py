"""PAD (파드) = 기출문제 모음 parsing.

Input: the 기출문제 PDF section of a lecture handout (text-based PDF; needs
`pdftotext`). Each question becomes an *exam unit* (number >= EXAM_BASE) that
notes can cite via `slide_refs`, exactly like script units. Rule enforced by the
validator: BLUE text is only for content that was actually 기출 (cites a PAD unit).
"""
from __future__ import annotations

import re
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

EXAM_BASE = 1000  # PAD units are numbered 1001, 1002, ... (script paragraphs use 1..999)

# Header: "20학번 (2022년) 김태규 교수님. (감염과 면역)"  or  "20학번 김인범교수님" (year / course optional)
_HDR = re.compile(r"^\s*(\d{2})학번\s*(?:\((\d{4})년\))?\s*([^\s.(]+?)\s*교수님\.?\s*(?:\((.+?)\))?\s*$")
_ANS = re.compile(r"^\s*(?:정답|답)\s*[:：]\s*(.*)$")
_ANS_BARE = re.compile(r"^\s*(?:정답\s+|답\s+(?=\d[\d,\s번)]*$))(\d.*)$")  # "정답 3번. 짤입니다." / bare "답 5" (no colon)
_ANS_INLINE = re.compile(r"^(.*?\S)\s+(?:정답|답)\s*[:：]\s*(\S.*)$")
_QSTART = re.compile(r"^(서술형\s*)?(\d+)\.\s+(\S.*)$")
_FOOTER = re.compile(r"^-\s*\d+\s*-$")
_END = re.compile(r"수고하셨습니다")


@dataclass
class ExamItem:
    number: int  # unit number (1001+)
    cohort: str  # "20학번"
    year: int  # 0 when the handout does not print the exam year
    professor: str
    course: str
    q_no: int  # question number as printed in the handout
    question: str  # question + choices
    answer: str
    commentary: str
    header_note: str = ""  # "b" when the same "year / professor" header appears again (keeps labels unique)
    signals: list[str] = field(default_factory=list)  # lecturer / handout-writer cues found in the commentary

    @property
    def label(self) -> str:
        head = (f"{self.year}({self.cohort})" if self.cohort else f"{self.year}{self.header_note}") if self.year else self.cohort
        return f"PAD {head} Q{self.q_no}"

    @property
    def title(self) -> str:
        return f"기출 {self.year}년 {self.cohort} {self.professor} Q{self.q_no}".replace("  ", " ") if self.year else \
            f"기출 {self.cohort} {self.professor} Q{self.q_no}"

    @property
    def when(self) -> str:
        return (f"{self.year}년({self.cohort})" if self.cohort else f"{self.year}년") if self.year else self.cohort


def pdf_text(path: str | Path) -> str:
    exe = shutil.which("pdftotext")
    if not exe:
        raise RuntimeError("pdftotext(poppler-utils)가 필요합니다.")
    return subprocess.run([exe, "-layout", str(path), "-"], capture_output=True, text=True, check=True).stdout


def parse_exam_text(text: str) -> list[ExamItem]:
    """Best-effort parser for 기출 handouts. Handles sequential and arbitrary question numbers,
    "정답 : 2번" / "답: 5" answers (also inline and on the next line), 서술형 items and scanned
    questions that only have an answer. Always spot-check the result (printed by the CLI)."""
    items: list[ExamItem] = []
    hdr = None  # (cohort, year, prof, course)
    note: list[str] = []
    cur: dict | None = None
    expected = 1
    prev_blank = True

    def close():
        nonlocal cur
        if cur is not None:
            items.append(ExamItem(
                number=EXAM_BASE + len(items) + 1, cohort=hdr[0], year=int(hdr[1] or 0), professor=hdr[2] + " 교수님",
                course=hdr[3] or "", q_no=cur["no"], question=" ".join(cur["q"]).strip(),
                answer=cur["ans"], commentary=" ".join(cur["c"]).strip(), header_note=cur["note"],
            ))
            cur = None

    for raw in text.replace("\f", "\n").splitlines():
        s = raw.strip()
        blank_before, prev_blank = prev_blank, not s
        if not s or s == "기출문제" or _FOOTER.match(s):
            continue
        if s.isdigit() and len(s) <= 2 and not (cur is not None and cur.get("pending")):
            continue  # bare page number between pages
        if _END.search(s):
            close(); break
        h = _HDR.match(s)
        if h:
            close()
            hdr = (f"{h.group(1)}학번", h.group(2), h.group(3).strip(), h.group(4))
            note, expected = [], 1
            continue
        if hdr is None:
            continue
        q = _QSTART.match(s)
        if q:
            n = int(q.group(2))
            after_answer = cur is None or bool(cur["ans"]) or cur.get("pending")
            if after_answer and (cur is None or n == expected or blank_before):
                close()
                stem = ("[서술형] " if q.group(1) else "") + q.group(3)
                cur = {"no": n, "q": [stem], "ans": "", "c": [], "note": " ".join(note), "pending": False}
                expected = n + 1
                continue
        if cur is not None and cur.get("pending"):  # "답 :" was empty -> the answer is the next text line
            cur["ans"], cur["pending"] = s, False
            continue
        a = _ANS.match(s) or _ANS_BARE.match(s)
        inline = None if a else _ANS_INLINE.match(s)
        if a or inline:
            if cur is None:  # scanned-image question: only the answer is text
                cur = {"no": 1, "q": ["(시험지 스캔 이미지 — 문항 텍스트 없음)"], "ans": "", "c": [], "note": " ".join(note), "pending": False}
                expected = 2
            if inline:
                cur["q"].append(inline.group(1))
            val = (a.group(1) if a else inline.group(2)).strip()
            if cur["ans"]:
                cur["c"].append(s)  # repeated answer line -> commentary
            elif val:
                cur["ans"] = val
            else:
                cur["pending"] = True
            continue
        if cur is None:
            note.append(s)
        elif cur["ans"]:
            cur["c"].append(s)
        else:
            cur["q"].append(s)
    close()
    return attach_signals(items)


_DOCX_HDR = re.compile(r"^\s*(\d{4})년\s*([^\s.(]+?)\s*교수님\s*$")
_DOCX_Q = re.compile(r"^\s*(\d+)\.\s+(\S.*)$")
_DOCX_ANS = re.compile(r"^\s*(?:정답|답)\s*[|:：]\s*(.*)$")
_DOCX_COMMENT = re.compile(r"^\s*(?:공식\s*해설|작성자\s*해설|해설)\s*[|:：]\s*(.*)$")


def parse_exam_docx(path: str | Path) -> list[ExamItem]:
    """PAD as a Word file: "2025년 주지현 교수님" headers, "27. question" + unnumbered or "1)" options,
    "답 | 1" / "답: 3)", "해설 | …" / "공식해설:" / "작성자 해설:" (the writer's commentary follows the answer).
    Lines such as "아래로는 전부 ○○ 교수님입니다." are skipped. Spot-check the result (the CLI prints it)."""
    from docx import Document

    items: list[ExamItem] = []
    hdr: tuple[int, str] | None = None
    cur: dict | None = None
    seen: dict[tuple[int, str], int] = {}
    part = ""

    def close():
        nonlocal cur
        if cur is not None and hdr is not None:
            items.append(ExamItem(number=EXAM_BASE + len(items) + 1, cohort="", year=hdr[0], professor=hdr[1] + " 교수님",
                                  course="", q_no=cur["no"], question=" ".join(cur["q"]).strip(), answer=cur["ans"],
                                  commentary=" ".join(cur["c"]).strip(), header_note=part))
        cur = None

    for p in Document(str(path)).paragraphs:
        s = " ".join(p.text.split())
        if not s or s.startswith("아래로는"):
            continue
        h = _DOCX_HDR.match(s)
        if h:
            close()
            hdr = (int(h.group(1)), h.group(2).strip())
            seen[hdr] = seen.get(hdr, 0) + 1
            part = "" if seen[hdr] == 1 else "bcdefgh"[min(seen[hdr] - 2, 6)]
            continue
        if hdr is None:
            continue
        q = _DOCX_Q.match(s)
        if q and (cur is None or cur["ans"]):
            close()
            cur = {"no": int(q.group(1)), "q": [q.group(2)], "ans": "", "c": []}
            continue
        if cur is None:
            continue
        a = _DOCX_ANS.match(s)
        if a and not cur["ans"]:
            cur["ans"] = a.group(1).strip()
            continue
        if cur["ans"]:
            c = _DOCX_COMMENT.match(s)
            cur["c"].append(c.group(1).strip() if c else s)
        else:
            cur["q"].append(s)
    close()
    return attach_signals(items)


def parse_exam_pdf(path: str | Path) -> list[ExamItem]:
    """PAD file: .docx (Word) or a text-based PDF."""
    if str(path).lower().endswith(".docx"):
        return parse_exam_docx(path)
    return parse_exam_text(pdf_text(path))


# ---------------------------------------------------------------- exam signals (facts the handout writer put in the commentary)
SIGNAL_PATTERNS: list[tuple[str, str, str]] = [  # (signal, regex, shown label)
    ("출제예고", r"출제\s*예고", "출제예고"),
    ("강조안함", r"강조(?:한|하신)?\s*(?:부분|내용)?(?:은|이|는)?\s*(?:아닙니다|아니었|없었|전혀)|강조\s*(?:안|하지\s*않)", "강조 안 함"),
    ("미수업", r"(?:배운\s*적\s*(?:이\s*)?없|안\s*배웠|배우지\s*않)", "‘배우지 않았다’ 언급(문항 또는 선지)"),
    ("선지미수업", r"(?:등장한\s*적\s*없|언급(?:한\s*적|된\s*적)?\s*없)", "‘수업에 나온 적 없다’ 언급"),
    ("족보반복", r"\(\s*\d{4}\s*년\s*짤\s*\)|짤\)|짤입니다|동일한\s*문제|유형이\s*(?:완전히\s*)?같", "이전 기출 반복"),
]


def exam_signals(text: str) -> list[str]:
    import re as _re

    return [sig for sig, pat, _ in SIGNAL_PATTERNS if _re.search(pat, text)]


def signal_label(sig: str) -> str:
    return next((lab for s_, _, lab in SIGNAL_PATTERNS if s_ == sig), sig)


def attach_signals(items: list[ExamItem]) -> list[ExamItem]:
    for it in items:
        it.signals = exam_signals(f"{it.question} {it.commentary}")
    return items


def exam_history(items: list[ExamItem], professor: str = "") -> str:
    """Facts only (counted from the PAD file, no prediction): how many questions per year / professor and which
    commentary cues exist. Shown on the cover so the reader sees the exam trend at a glance."""
    if not items:
        return ""
    from collections import Counter

    prof = professor.replace("교수님", "").strip()
    mine = [i for i in items if prof and prof in i.professor]
    other = [i for i in items if i not in mine] if prof else []
    if all(i.year for i in items):
        yrs = lambda xs: ", ".join(f"{y}년 {n}" for y, n in sorted(Counter(i.year for i in xs).items()))
        L = [f"기출(PAD) {len(items)}문항 ({min(i.year for i in items)}–{max(i.year for i in items)}년)."]
    else:  # handout prints cohorts ("20학번") instead of exam years
        yrs = lambda xs: ", ".join(f"{c} {n}" for c, n in sorted(Counter(i.when for i in xs).items(), reverse=True))
        L = [f"기출(PAD) {len(items)}문항 ({yrs(items)})."]
    if prof:
        L.append(f"{prof} 교수님 {len(mine)}문항({yrs(mine)})" + (f", 다른 교수님 {len(other)}문항({yrs(other)})." if other else "."))
    for sig, _, lab in SIGNAL_PATTERNS:
        hit = [i for i in items if sig in i.signals]
        if hit:
            L.append(f"해설 {lab}: " + ", ".join(i.label.replace("PAD ", "") for i in hit) + ".")
    return " ".join(L)
