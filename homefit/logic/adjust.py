"""난이도 자동 조정 (H-1~H-3).

- 지금 배율로 한 기록 중 최근 2건이 모두 완료 → ×1.1 (ACSM 2009: 2회 연속 목표 달성 시 2~10% 증가)
- 지금 배율로 한 기록 중 최근 3건 안에 중단이 2건 이상 → ×0.9 (기능명세서 H-2)
- 그 외에는 그대로. 범위는 0.7~1.3(1.3 상한은 팀 판단)

"지금 배율로 한 기록"만 보는 이유: 배율을 올린 직후에는 새 배율로 2번을 더 끝내야 다시 오른다.
그렇지 않으면 매번 완료할 때마다 10%씩 올라 3번 만에 상한에 닿는다.
이 함수는 기록이 저장될 때 한 번만 부른다(홈을 열 때마다 부르면 배율이 계속 오른다).
"""
from __future__ import annotations

MIN_MULT, MAX_MULT = 0.7, 1.3
UP, DOWN = 1.1, 0.9


def _same_mult(r: dict, current: float) -> bool:
    return abs(r.get("multiplier", 1.0) - current) < 1e-6


def next_multiplier(records: list[dict], current: float) -> tuple[float, str | None]:
    """records는 시간 순서(오래된 것 → 최근). 반환: (새 배율, 화면에 보여 줄 이유 또는 None)."""
    recent = [r for r in records if _same_mult(r, current)]
    last2, last3 = recent[-2:], recent[-3:]

    hard = any(r.get("feedback") == "힘들었어요" for r in last2)
    if len(last2) == 2 and all(r.get("completed") for r in last2) and not hard and current < MAX_MULT:
        new = min(MAX_MULT, round(current * UP, 2))
        return new, "최근 2번 모두 끝까지 해서 횟수를 10% 늘렸어요"

    if len(last3) >= 2 and sum(1 for r in last3 if not r.get("completed")) >= 2 and current > MIN_MULT:
        new = max(MIN_MULT, round(current * DOWN, 2))
        return new, "최근에 중간에 멈춘 적이 많아서 횟수를 10% 줄였어요"

    return current, None
