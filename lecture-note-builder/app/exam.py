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

_HDR = re.compile(r"^\s*(\d{2})학번\s*\((\d{4})년\)\s*([^\s.(]+\s*교수님)\.?\s*(?:\((.+?)\))?\s*$")
_ANS = re.compile(r"정답\s*[:：]?\s*(.+?)\s*$")
_END = re.compile(r"수고하셨습니다")


@dataclass
class ExamItem:
    number: int  # unit number (101+)
    cohort: str  # "20학번"
    year: int
    professor: str
    course: str
    q_no: int
    question: str  # question + choices
    answer: str
    commentary: str
    header_note: str = ""

    @property
    def label(self) -> str:
        return f"PAD {self.year}({self.cohort}) Q{self.q_no}"

    @property
    def title(self) -> str:
        return f"기출 {self.year}년 {self.cohort} {self.professor} Q{self.q_no}"


def pdf_text(path: str | Path) -> str:
    exe = shutil.which("pdftotext")
    if not exe:
        raise RuntimeError("pdftotext(poppler-utils)가 필요합니다.")
    return subprocess.run([exe, "-layout", str(path), "-"], capture_output=True, text=True, check=True).stdout


def parse_exam_text(text: str) -> list[ExamItem]:
    lines = [ln.rstrip() for ln in text.replace("\f", "\n").splitlines()]
    items: list[ExamItem] = []
    hdr = None  # (cohort, year, prof, course)
    note: list[str] = []
    cur: dict | None = None
    expected = 1

    def close():
        nonlocal cur
        if cur is not None:
            items.append(ExamItem(
                number=EXAM_BASE + len(items) + 1, cohort=hdr[0], year=int(hdr[1]), professor=hdr[2],
                course=hdr[3] or "", q_no=cur["no"], question=" ".join(cur["q"]).strip(),
                answer=cur["ans"], commentary=" ".join(cur["c"]).strip(), header_note=cur["note"],
            ))
            cur = None

    for raw in lines:
        s = raw.strip()
        if not s or s == "기출문제":
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
        q = re.match(r"^(\d+)\.\s+(\S.*)$", s)
        if q and int(q.group(1)) == expected and (cur is None or cur["ans"] or cur["no"] + 1 == int(q.group(1))):
            close()
            cur = {"no": int(q.group(1)), "q": [q.group(2)], "ans": "", "c": [], "note": " ".join(note)}
            expected += 1
            continue
        a = _ANS.match(s)
        if a:
            if cur is None:  # scanned-image question: only the answer is text
                cur = {"no": 1, "q": ["(시험지 스캔 이미지 — 문항 텍스트 없음)"], "ans": "", "c": [], "note": " ".join(note)}
                expected = 2
            cur["ans"] = a.group(1).strip()
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
