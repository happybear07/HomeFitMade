import json

import pytest

from homefit.logic.calorie import routine_kcal_per_kg
from homefit.logic.recommend import build_routine, estimate_minutes
from homefit.logic.util import round_half_up

from .conftest import DATA

REP_BMI = {"저체중": 17.5, "정상": 21.0, "비만 전단계(과체중)": 24.0, "1단계 비만": 27.5, "2단계 이상 비만": 32.0}
FIXTURES = json.loads((DATA / "routines.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("fx", FIXTURES, ids=lambda f: f"{f['bmi_category']}-{f['level']}")
def test_matches_reference_routines(fx, exercises, by_id):
    """data/routines.json 정답 15개와 운동 목록, 횟수·세트·휴식, 예상 시간, kg당 칼로리가 같아야 한다."""
    routine = build_routine(fx["level"], REP_BMI[fx["bmi_category"]], exercises)
    assert [it.as_dict() for it in routine.items] == fx["exercises"]
    assert estimate_minutes(routine.items) == fx["estimated_minutes"]
    assert routine_kcal_per_kg(routine.items, by_id) == pytest.approx(fx["calories_per_kg"], abs=0.002)


def test_obese_bmi_replaces_high_load_and_records_reason(exercises, by_id):
    routine = build_routine("고급", 27.5, exercises)
    assert all(not by_id[it.id].is_high_load for it in routine.items)
    assert routine.substitutions                       # 대체 이유를 화면에 보여 줄 수 있어야 함
    assert len({it.id for it in routine.items}) == len(routine.items)   # 대체로 중복이 생기지 않음


def test_normal_bmi_keeps_jump_with_jump_dose(exercises, by_id):
    routine = build_routine("고급", 21.0, exercises)
    jumps = [it for it in routine.items if by_id[it.id].is_high_load]
    assert jumps and all((it.reps, it.sets, it.rest_sec) == (6, 3, 90) for it in jumps)


def test_part_mode_short_routine(exercises, by_id):
    routine = build_routine("초급", 21.0, exercises, part="상체")
    assert routine.items and all(by_id[it.id].part == "상체" for it in routine.items)
    assert routine.short                                # 초급 상체 후보가 4개보다 적다


def test_part_mode_full_count(exercises, by_id):
    routine = build_routine("중급", 21.0, exercises, part="하체")
    assert len(routine.items) == 5 and not routine.short
    assert all(by_id[it.id].part == "하체" for it in routine.items)


def test_multiplier_uses_half_up_rounding(exercises, by_id):
    routine = build_routine("중급", 21.0, exercises, multiplier=1.1)
    rep_items = [it for it in routine.items if it.unit == "회" and not by_id[it.id].is_high_load]
    assert rep_items and all(it.reps == 17 for it in rep_items)   # 15 × 1.1 = 16.5 → 17


def test_multiplier_not_applied_to_jumps(exercises, by_id):
    routine = build_routine("고급", 21.0, exercises, multiplier=1.3)
    assert all(it.reps == 6 for it in routine.items if by_id[it.id].is_high_load)


def test_round_half_up():
    assert round(16.5) == 16           # 파이썬 기본 round()의 함정
    assert round_half_up(16.5) == 17
    assert round_half_up(16.49) == 16
