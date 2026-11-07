"""Tiny inline markup used inside Statement.text so one paragraph can mix colours,
like the MOM notes do:

  {r|red}     lecturer emphasis / "시험에 나온다"
  {b|BLUE}    appeared in the PAD (기출) - the lecturer's own PAD (or any PAD when the template has one blue)
  {c|cyan}    appeared in a PAD of ANOTHER professor (only when the template declares `exam_other`)
  {g|gray}    low importance          {p|purple}  needs checking
  {y|...}     yellow highlight (study tip / "this matters")      {u|...}  underline
  **bold**    key term
"""
from __future__ import annotations

import re

LETTERS = "rbgpcyu"
_COLOR = re.compile(r"\{([" + LETTERS + r"])\|(.*?)\}", re.S)
_BOLD = re.compile(r"\*\*(.+?)\*\*", re.S)
COLORS = {"r": "emphasis", "b": "exam", "c": "exam_other", "g": "minor", "p": "verify", "y": "highlight", "u": "underline"}
PAD_TAGS = ("exam", "exam_other")  # colours that need a PAD citation
LEAK = re.compile(r"[{}]|\b[" + LETTERS + r"]\|")


def runs(text: str) -> list[tuple[str, str | None, bool]]:
    """-> [(text, colour_tag|None, bold)]"""
    out: list[tuple[str, str | None, bool]] = []
    pos = 0
    pieces: list[tuple[str, str | None]] = []
    for m in _COLOR.finditer(text):
        if m.start() > pos:
            pieces.append((text[pos : m.start()], None))
        pieces.append((m.group(2), COLORS[m.group(1)]))
        pos = m.end()
    if pos < len(text):
        pieces.append((text[pos:], None))
    for chunk, col in pieces:
        bp = 0
        for b in _BOLD.finditer(chunk):
            if b.start() > bp:
                out.append((chunk[bp : b.start()], col, False))
            out.append((b.group(1), col, True))
            bp = b.end()
        if bp < len(chunk):
            out.append((chunk[bp:], col, False))
    return out


def strip(text: str) -> str:
    return "".join(t for t, _, _ in runs(text))


def tags_used(text: str) -> set[str]:
    return {c for _, c, _ in runs(text) if c}
