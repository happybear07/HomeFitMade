from datetime import date

import pytest

from homefit.logic.streak import gap_days, gap_stage, month_marks, streak_days, week_marks

TODAY = date(2026, 11, 21)


def recs(*days, completed=True):
    return [{"date": d, "completed": completed} for d in days]


@pytest.mark.parametrize("records, gap, streak, stage", [
    (recs("2026-11-17", "2026-11-18", "2026-11-19", "2026-11-20", "2026-11-21"), 0, 5, "g0"),
    (recs("2026-11-17", "2026-11-18", "2026-11-19", "2026-11-20"), 1, 4, "g0"),
    (recs("2026-11-18"), 3, 0, "g1"),
    ([], 0, 0, "g0"),
    (recs("2026-11-07"), 14, 0, "g3"),
])
def test_table_from_architecture(records, gap, streak, stage):
    assert gap_days(records, TODAY) == gap
    assert streak_days(records, TODAY) == streak
    assert gap_stage(gap_days(records, TODAY)) == stage


@pytest.mark.parametrize("gap, stage", [(0, "g0"), (2, "g0"), (3, "g1"), (6, "g1"), (7, "g2"), (13, "g2"), (14, "g3"), (40, "g3")])
def test_stage_boundaries(gap, stage):
    assert gap_stage(gap) == stage


def test_stopped_records_do_not_count():
    records = recs("2026-11-20", completed=False) + recs("2026-11-14")
    assert gap_days(records, TODAY) == 7
    assert streak_days(records, TODAY) == 0


def test_week_marks():
    records = recs("2026-11-17") + recs("2026-11-18", completed=False)
    marks = dict(week_marks(records, TODAY))       # 2026-11-21은 토요일, 주는 11-16(월)~11-22(일)
    assert marks[date(2026, 11, 16)] == "empty"
    assert marks[date(2026, 11, 17)] == "done"
    assert marks[date(2026, 11, 18)] == "stopped"
    assert marks[TODAY] == "today"
    assert marks[date(2026, 11, 22)] == "later"


def test_month_marks_length():
    assert len(month_marks([], 2026, 2, TODAY)) == 28
