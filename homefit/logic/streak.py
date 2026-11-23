"""공백 일수, 연속 일수, 공백 단계 (E-2, E-3, F-1).

연속·공백 계산은 "완료한 날짜의 집합"으로 한다. 하루에 기록이 여러 건이어도 하루로 센다.
"""
from __future__ import annotations

import calendar
from datetime import date, timedelta

STAGES = ("g0", "g1", "g2", "g3")


def completed_dates(records: list[dict]) -> set[date]:
    return {date.fromisoformat(r["date"]) for r in records if r.get("completed")}


def stopped_dates(records: list[dict]) -> set[date]:
    """중단 기록만 있고 완료 기록은 없는 날짜."""
    stopped = {date.fromisoformat(r["date"]) for r in records if not r.get("completed")}
    return stopped - completed_dates(records)


def gap_days(records: list[dict], today: date) -> int:
    """오늘 − 마지막으로 완료한 날짜. 완료 기록이 없으면 0(첫 사용자는 기본 화면, E-3)."""
    done = completed_dates(records)
    if not done:
        return 0
    return max(0, (today - max(done)).days)


def streak_days(records: list[dict], today: date) -> int:
    """오늘 완료했으면 오늘부터, 아니면 어제부터 거꾸로 이어진 완료 날짜 수."""
    done = completed_dates(records)
    day = today if today in done else today - timedelta(days=1)
    count = 0
    while day in done:
        count += 1
        day -= timedelta(days=1)
    return count


def gap_stage(gap: int) -> str:
    """0~2일 g0(기본), 3~6일 g1(시무룩), 7~13일 g2(화남), 14일 이상 g3(쓰러짐)."""
    if gap <= 2:
        return "g0"
    if gap <= 6:
        return "g1"
    if gap <= 13:
        return "g2"
    return "g3"


def _mark(day: date, today: date, done: set[date], stopped: set[date]) -> str:
    if day in done:
        return "done"
    if day == today:
        return "today"
    if day > today:
        return "later"
    if day in stopped:
        return "stopped"
    return "empty"


def week_marks(records: list[dict], today: date) -> list[tuple[date, str]]:
    """홈 헤더의 이번 주(월~일) 7칸: done / stopped / today / later / empty."""
    done, stopped = completed_dates(records), stopped_dates(records)
    monday = today - timedelta(days=today.weekday())
    return [(d, _mark(d, today, done, stopped)) for d in (monday + timedelta(days=i) for i in range(7))]


def month_marks(records: list[dict], year: int, month: int, today: date) -> list[tuple[date, str]]:
    """기록 화면 달력: 그 달 1일~말일의 표시 상태."""
    done, stopped = completed_dates(records), stopped_dates(records)
    last = calendar.monthrange(year, month)[1]
    return [(d, _mark(d, today, done, stopped)) for d in (date(year, month, n) for n in range(1, last + 1))]
