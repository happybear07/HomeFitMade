import pytest

from homefit.logic.calorie import kcal_for_items, routine_kcal_per_kg
from homefit.logic.recommend import build_routine


def test_intermediate_normal_per_kg(exercises, by_id):
    routine = build_routine("중급", 21.0, exercises)
    assert routine_kcal_per_kg(routine.items, by_id) == pytest.approx(0.705, abs=0.001)


def test_only_done_sets_count_and_rest_excluded(by_id):
    # 푸시업 MET 3.8, 15회 = 45초. 2세트 = 90초 = 1.5분 → 3.8 × 3.5 × 70 / 200 × 1.5
    items = [{"id": "push_up", "unit": "회", "reps": 15, "sets_done": 2, "rest_sec": 45}]
    assert kcal_for_items(items, by_id, 70) == pytest.approx(3.8 * 3.5 * 70 / 200 * 1.5)


def test_time_based_unit(by_id):
    items = [{"id": "plank", "unit": "초", "reps": 30, "sets_done": 3}]
    assert kcal_for_items(items, by_id, 60) == pytest.approx(2.8 * 3.5 * 60 / 200 * 1.5)
