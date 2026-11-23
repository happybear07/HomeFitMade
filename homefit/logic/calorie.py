"""칼로리 추정 (E-4).

kcal = MET × 3.5 × 체중(kg) ÷ 200 × 운동 시간(분)
- 운동 시간은 실제로 끝낸 세트의 운동 시간만 센다. 휴식은 넣지 않는다(SOURCES.md 규칙 6, 보수적 추정).
"""
from __future__ import annotations

from ..models import Exercise, RoutineItem
from .recommend import work_seconds


def kcal_per_kg(met: float, seconds: float) -> float:
    return met * 3.5 / 200 * (seconds / 60)


def kcal_for_items(items: list[dict], exercises_by_id: dict[str, Exercise], weight_kg: float) -> float:
    """items: [{"id", "unit", "reps", "sets_done"}, ...] — 기록에 저장되는 모양."""
    total = 0.0
    for it in items:
        ex = exercises_by_id.get(it["id"])
        if ex is None:
            continue
        seconds = it["sets_done"] * work_seconds(it["unit"], it["reps"])
        total += kcal_per_kg(ex.met, seconds) * weight_kg
    return total


def routine_kcal_per_kg(items: list[RoutineItem], exercises_by_id: dict[str, Exercise]) -> float:
    """계획한 세트를 모두 했을 때 체중 1kg당 칼로리(routines.json의 calories_per_kg와 같은 값)."""
    return sum(kcal_per_kg(exercises_by_id[it.id].met, it.sets * work_seconds(it.unit, it.reps)) for it in items)
