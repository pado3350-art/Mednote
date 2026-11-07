"""Tiny inline markup used inside Statement.text so one paragraph can mix colours,
like the MOM notes do:  {r|red=강조} {b|BLUE=기출 only} {g|gray=덜 중요} {p|purple=검증필요}  and **bold**."""
from __future__ import annotations

import re

_COLOR = re.compile(r"\{([rbgp])\|(.*?)\}", re.S)
_BOLD = re.compile(r"\*\*(.+?)\*\*", re.S)
COLORS = {"r": "emphasis", "b": "exam", "g": "minor", "p": "verify"}


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
