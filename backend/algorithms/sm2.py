"""
SM-2 간격 반복 알고리즘 구현
Ebbinghaus 망각 곡선 기반, Anki 방식과 동일한 핵심 로직

quality 점수:
  0 - 완전히 잊음 (다시 처음부터)
  1 - 기억 못함
  2 - 어렴풋이 기억
  3 - 어려움 (오답이지만 기억)
  4 - 보통 (정답, 약간 망설임)
  5 - 완벽하게 기억
"""

from datetime import datetime, timedelta, timezone
from dataclasses import dataclass


@dataclass
class SM2Result:
    interval: int          # 다음 복습까지 일수
    repetitions: int       # 연속 성공 횟수
    easiness: float        # EF (Easiness Factor)
    next_due: datetime     # 다음 복습 예정 시각


def calculate_next_review(
    quality: int,
    repetitions: int,
    easiness: float,
    interval: int,
) -> SM2Result:
    """
    SM-2 알고리즘으로 다음 복습 파라미터 계산.

    Args:
        quality:     복습 품질 점수 (0~5)
        repetitions: 현재까지 연속 성공 복습 횟수
        easiness:    현재 Easiness Factor (최소 1.3)
        interval:    현재 복습 간격 (일)

    Returns:
        SM2Result: 업데이트된 파라미터와 다음 복습 시각
    """
    if quality < 0 or quality > 5:
        raise ValueError(f"quality는 0~5 사이여야 합니다. 입력값: {quality}")

    if quality >= 3:
        # 성공 복습
        if repetitions == 0:
            new_interval = 1
        elif repetitions == 1:
            new_interval = 6
        else:
            new_interval = round(interval * easiness)
        new_repetitions = repetitions + 1
    else:
        # 실패 복습 — 처음부터 재시작
        new_repetitions = 0
        new_interval = 1

    # EF 업데이트: EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    new_easiness = easiness + 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)
    new_easiness = max(1.3, new_easiness)  # 최솟값 1.3

    next_due = datetime.now(tz=timezone.utc) + timedelta(days=new_interval)

    return SM2Result(
        interval=new_interval,
        repetitions=new_repetitions,
        easiness=round(new_easiness, 4),
        next_due=next_due,
    )


def days_until_review(due_date: datetime) -> int:
    """복습까지 남은 일수 계산 (음수면 기한 초과)"""
    now = datetime.now(tz=timezone.utc)
    if due_date.tzinfo is None:
        due_date = due_date.replace(tzinfo=timezone.utc)
    delta = due_date - now
    return delta.days
