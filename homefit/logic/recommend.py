"""루틴 추천 (C-1~C-5, C-7).

규칙은 docs/architecture.md 5-2와 같고, data/routines.json 정답 15개로 검증한다(tests/test_logic_recommend.py).
"""
from __future__ import annotations

from ..models import LEVEL_RANK, PARTS, Exercise, Routine, RoutineItem
from .body import OBESE_BMI
from .util import round_half_up

# ② 사용자 난이도별 부위 개수
PART_COUNT = {
    "초급": {"상체": 1, "하체": 2, "코어": 1},
    "중급": {"상체": 2, "하체": 2, "코어": 1},
    "고급": {"상체": 2, "하체": 2, "코어": 2},
}
# ⑤ 사용자 난이도별 (횟수형 회, 시간형 초, 세트, 휴식 초)
DOSE = {
    "초급": (10, 20, 2, 60),
    "중급": (15, 30, 3, 45),
    "고급": (20, 45, 3, 60),
}
JUMP_DOSE = (6, 3, 90)   # 관절 부담 '높음'(점프) 운동: 6회 × 3세트, 휴식 90초. 배율 적용 안 함
SEC_PER_REP = 3          # 횟수형 1회에 걸리는 시간(예상 시간·칼로리 계산용)


def work_seconds(unit: str, reps: int) -> int:
    """한 세트의 운동 시간(휴식 제외)."""
    return reps * SEC_PER_REP if unit == "회" else reps


def _sorted_candidates(exercises: list[Exercise], part: str, level: str) -> list[Exercise]:
    """① 난이도가 사용자 이하인 후보를 ③ 정렬 규칙으로 줄 세운다."""
    order = {e.id: i for i, e in enumerate(exercises)}
    cands = [e for e in exercises if e.part == part and LEVEL_RANK[e.level] <= LEVEL_RANK[level]]
    cands.sort(key=lambda e: (
        e.level != level,          # 1) 사용자 난이도와 같은 운동 먼저
        -LEVEL_RANK[e.level],      # 2) 그다음 난이도 높은 순
        -e.met,                    # 3) MET 높은 순
        order[e.id],               # 4) 파일 순서(결과가 항상 같게)
    ))
    return cands


def _pick(cands: list[Exercise], count: int, bmi: float, by_id: dict[str, Exercise],
          substitutions: list[tuple[str, str]]) -> list[Exercise]:
    """④ BMI 25 이상이면 '높음' 운동을 대체 운동으로 바꾸며 count개를 뽑는다(중복 없이)."""
    picked: list[Exercise] = []
    for e in cands:
        if len(picked) == count:
            break
        if bmi >= OBESE_BMI and e.is_high_load and e.alternative in by_id:
            alt = by_id[e.alternative]
            if alt.id in {p.id for p in picked}:
                continue
            substitutions.append((e.id, alt.id))
            e = alt
        if e.id in {p.id for p in picked}:
            continue
        picked.append(e)
    return picked


def _dose(e: Exercise, level: str, multiplier: float) -> RoutineItem:
    """⑤ 횟수·세트·휴식과 ⑥ 난이도 배율."""
    if e.is_high_load:
        reps, sets, rest = JUMP_DOSE
        return RoutineItem(e.id, e.unit, reps, sets, rest)
    reps_n, secs, sets, rest = DOSE[level]
    base = secs if e.unit == "초" else reps_n
    reps = round_half_up(base * multiplier)
    if multiplier > 1 and reps == base:
        reps += 1                  # 배율이 1보다 크면 최소 +1
    return RoutineItem(e.id, e.unit, max(1, reps), sets, rest)


def build_routine(level: str, bmi: float, exercises: list[Exercise],
                  part: str | None = None, multiplier: float = 1.0) -> Routine:
    """사용자 난이도, BMI, 운동 목록으로 오늘의 루틴을 만든다.

    part가 None이나 "전신"이면 상체·하체·코어를 난이도별 개수만큼,
    특정 부위면 그 부위에서만 min(난이도별 합계, 후보 수)개를 뽑는다(⑧).
    """
    by_id = {e.id: e for e in exercises}
    subs: list[tuple[str, str]] = []
    chosen: list[Exercise] = []
    if part in (None, "전신"):
        for p in PARTS:
            chosen += _pick(_sorted_candidates(exercises, p, level), PART_COUNT[level][p], bmi, by_id, subs)
        short = False
    else:
        want = sum(PART_COUNT[level].values())
        chosen = _pick(_sorted_candidates(exercises, part, level), want, bmi, by_id, subs)
        short = len(chosen) < want
    items = [_dose(e, level, multiplier) for e in chosen]
    return Routine(level=level, part=part or "전신", items=items, multiplier=multiplier,
                   substitutions=subs, short=short)


def estimate_minutes(items: list[RoutineItem]) -> float:
    """⑦ 예상 시간(분, 소수 첫째 자리). 운동별 sets × (세트 운동시간 + 휴식)."""
    total = sum(it.sets * (work_seconds(it.unit, it.reps) + it.rest_sec) for it in items)
    return round(total / 60, 1)


def performed_minutes(items: list[dict]) -> float:
    """실제로 끝낸 세트만으로 다시 계산한 시간. items: [{"unit","reps","rest_sec","sets_done"}]"""
    total = sum(it["sets_done"] * (work_seconds(it["unit"], it["reps"]) + it["rest_sec"]) for it in items)
    return round(total / 60, 1)
