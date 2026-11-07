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
from dataclasses import dataclass
from pathlib import Path

EXAM_BASE = 1000  # PAD units are numbered 1001, 1002, ... (script paragraphs use 1..999)

# Header: "20학번 (2022년) 김태규 교수님. (감염과 면역)"  or  "20학번 김인범교수님" (year / course optional)
_HDR = re.compile(r"^\s*(\d{2})학번\s*(?:\((\d{4})년\))?\s*([^\s.(]+?)\s*교수님\.?\s*(?:\((.+?)\))?\s*$")
_ANS = re.compile(r"^\s*(?:정답|답)\s*[:：]\s*(.*)$")
_ANS_BARE = re.compile(r"^\s*정답\s+(\d.*)$")
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
    header_note: str = ""

    @property
    def label(self) -> str:
        head = f"{self.year}({self.cohort})" if self.year else self.cohort
        return f"PAD {head} Q{self.q_no}"

    @property
    def title(self) -> str:
        return f"기출 {self.year}년 {self.cohort} {self.professor} Q{self.q_no}" if self.year else \
            f"기출 {self.cohort} {self.professor} Q{self.q_no}"

    @property
    def when(self) -> str:
        return f"{self.year}년({self.cohort})" if self.year else self.cohort


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
    return items


def parse_exam_pdf(path: str | Path) -> list[ExamItem]:
    return parse_exam_text(pdf_text(path))
