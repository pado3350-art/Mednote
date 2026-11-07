"""Offline PAD (기출) matching: which note sentences contain content that appeared in the 기출 questions?

Token = English term / identifier (hla-b, nkg2d, stria, ...). A sentence matches a PAD item when it shares enough
*informative* tokens with the item's question + answer + explanation (tokens that appear in most items - e.g.
'class' - are ignored). Matches are deterministic and explainable; the validator still enforces the colour rule.
"""
from __future__ import annotations

import re
from collections import Counter

from .exam import ExamItem

_TOK = re.compile(r"[A-Za-z][A-Za-z0-9\-]{2,}")
STOP = {"the", "and", "for", "that", "this", "with", "from", "are", "was", "not", "into", "but", "has", "have",
        "can", "its", "their", "which", "also", "only", "all", "one", "two"}


def tokens(text: str) -> set[str]:
    return {t.lower().strip("-") for t in _TOK.findall(text) if t.lower() not in STOP}


class PadMatcher:
    def __init__(self, items: list[ExamItem]):
        self.items = items
        self.tok = {it.number: tokens(f"{it.question} {it.answer} {it.commentary}") for it in items}
        df: Counter = Counter()
        for ts in self.tok.values():
            df.update(ts)
        n = max(len(items), 1)
        # informative = not shared by most items (always keep rare ones when there are few items)
        self.informative = {t for t, c in df.items() if c / n <= 0.4 or n <= 3}

    def match(self, text: str, max_refs: int = 3) -> list[int]:
        st = tokens(text)
        if len(st) < 2:
            return []
        scored = []
        for num, it_tokens in self.tok.items():
            shared = {t for t in (st & it_tokens) if t in self.informative}
            rare_long = [t for t in shared if len(t) >= 7]
            ok = len(shared) >= 3 or (len(shared) == 2 and len(text) <= 170) or (len(shared) == 1 and rare_long and len(text) <= 120)
            if ok and len(shared) / len(st) >= 0.25:
                scored.append((len(shared), num))
        scored.sort(reverse=True)
        return sorted(n for _, n in scored[:max_refs])
