"""Stage 2: align script segments to slides.

1. If the script has explicit [슬라이드 N] markers -> use them (confidence 1.0).
2. Otherwise: character-bigram cosine similarity + monotonic DP (lecture
   follows slide order). Low-similarity segments are reported, never hidden.
"""
from __future__ import annotations

import math
import re
from collections import Counter

from .models import AlignedSlide, Segment, Slide

_STRIP = re.compile(r"[\s\W_]+", re.UNICODE)


def _bigrams(text: str) -> Counter:
    t = _STRIP.sub("", text.lower())
    if len(t) < 2:
        return Counter([t]) if t else Counter()
    return Counter(t[i : i + 2] for i in range(len(t) - 1))


def _cosine(a: Counter, b: Counter) -> float:
    if not a or not b:
        return 0.0
    dot = sum(v * b.get(k, 0) for k, v in a.items())
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    return dot / (na * nb) if na and nb else 0.0


def _similarity_assign(segments: list[Segment], slides: list[Slide]) -> list[tuple[int, float]]:
    """Return [(slide_index, score)] per segment, non-decreasing slide_index."""
    n, m = len(segments), len(slides)
    sv = [_bigrams(s.plain_text()) for s in slides]
    gv = [_bigrams(g.text) for g in segments]
    score = [[_cosine(gv[i], sv[j]) for j in range(m)] for i in range(n)]

    NEG = float("-inf")
    STAY = 1e-6  # zero-score segments stay with the previous slide
    dp = [[NEG] * m for _ in range(n)]
    back = [[0] * m for _ in range(n)]
    dp[0] = list(score[0])
    for i in range(1, n):
        best, best_k = NEG, 0  # running max of dp[i-1][k] for k <= j
        for j in range(m):
            if dp[i - 1][j] >= best:
                best, best_k = dp[i - 1][j], j
            stay = dp[i - 1][j] + STAY
            if stay > best:
                dp[i][j], back[i][j] = stay + score[i][j], j
            else:
                dp[i][j], back[i][j] = best + score[i][j], best_k
    j = max(range(m), key=lambda x: dp[n - 1][x])
    path = [0] * n
    for i in range(n - 1, -1, -1):
        path[i] = j
        j = back[i][j]
    return [(path[i], score[i][path[i]]) for i in range(n)]


def align(
    segments: list[Segment], slides: list[Slide], min_confidence: float = 0.15
) -> list[AlignedSlide]:
    result = {s.number: AlignedSlide(slide_number=s.number) for s in slides}
    if not segments or not slides:
        return list(result.values())

    numbers = {s.number for s in slides}
    has_markers = any(g.slide_hint is not None for g in segments)

    if has_markers:
        last = slides[0].number
        for g in segments:
            if g.slide_hint is not None and g.slide_hint in numbers:
                last = g.slide_hint
                conf = 1.0
            elif g.slide_hint is not None:  # marker points to a missing slide
                conf = 0.0
            else:
                conf = 0.5  # before the first marker: assume slide 1
            _place(result[last], g, conf, "marker", min_confidence)
    else:
        for g, (idx, sc) in zip(segments, _similarity_assign(segments, slides)):
            _place(result[slides[idx].number], g, sc, "similarity", min_confidence)

    return [result[s.number] for s in slides]


def _place(a: AlignedSlide, g: Segment, conf: float, method: str, min_conf: float) -> None:
    a.segments.append(g)
    a.method = method  # type: ignore[assignment]
    a.confidence = conf if len(a.segments) == 1 else min(a.confidence, conf)
    if conf < min_conf:
        a.low_confidence_segment_ids.append(g.id)
