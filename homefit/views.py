"""화면에만 쓰는 표시용 도우미(색, 날짜 글자, 횟수 글자). 계산 규칙은 여기 두지 않는다."""
from __future__ import annotations

from datetime import date

from flask import Flask

DOW = "월화수목금토일"
PART_TONE = {          # (배경, 아이콘·글자)
    "상체": ("#F6E9E3", "#A8735C"),
    "하체": ("#D8F7EE", "#1C7460"),
    "코어": ("#ECE7E6", "#111111"),
}
DISCLAIMER = "본 프로그램의 추천은 일반적인 운동 안내이며 의학적 조언을 대신하지 않습니다."


def part_bg(part: str) -> str:
    return PART_TONE.get(part, PART_TONE["코어"])[0]


def part_fg(part: str) -> str:
    return PART_TONE.get(part, PART_TONE["코어"])[1]


def amount(unit: str, reps: int) -> str:
    return f"{reps}{'초' if unit == '초' else '회'}"


def dose(item, sets_word: bool = False) -> str:
    """{'unit','reps','sets'} 딕셔너리나 RoutineItem → '17회 × 3' / '30초 × 3세트'"""
    get = item.get if isinstance(item, dict) else lambda k: getattr(item, k)
    return f"{amount(get('unit'), get('reps'))} × {get('sets')}{'세트' if sets_word else ''}"


def ko_date(value) -> str:
    d = date.fromisoformat(value) if isinstance(value, str) else value
    return f"{d.month}월 {d.day}일 {DOW[d.weekday()]}"


def minutes_text(m: float) -> str:
    return f"{max(1, round(m))}분"


def register(app: Flask) -> None:
    app.jinja_env.filters.update(part_bg=part_bg, part_fg=part_fg, dose=dose, ko_date=ko_date,
                                 amount=amount, minutes=minutes_text)
    app.jinja_env.globals.update(DISCLAIMER=DISCLAIMER)
