"""S6 운동 기록 (E-5)"""
import math
from datetime import date

from flask import Blueprint, render_template, request

from .. import context as ctx
from ..logic.streak import month_marks, streak_days
from ..models import PARTS

bp = Blueprint("records", __name__)

DONUT_COLOR = {"상체": "#D1A08A", "하체": "#1C7460", "코어": "#111111"}
R = 56
CIRC = 2 * math.pi * R


def _month(arg: str | None, today: date) -> tuple[int, int]:
    try:
        y, m = (int(x) for x in (arg or "").split("-"))
        date(y, m, 1)
        return y, m
    except ValueError:
        return today.year, today.month


def _donut(sets: dict[str, int]) -> list[dict]:
    """도넛 조각(stroke-dasharray). 조각 사이에 3px 틈을 둔다."""
    total = sum(sets.values())
    out, offset = [], 0.0
    for part in PARTS:
        if not total or not sets[part]:
            continue
        length = CIRC * sets[part] / total
        out.append({"color": DONUT_COLOR[part], "dash": f"{max(length - 3, 0.1):.1f} {CIRC:.1f}", "offset": f"{-offset:.1f}"})
        offset += length
    return out


@bp.get("/records")
def show():
    today = date.today()
    year, month = _month(request.args.get("month"), today)
    all_records = ctx.records().all()
    in_month = [r for r in all_records if r["date"].startswith(f"{year:04d}-{month:02d}")]
    marks = month_marks(all_records, year, month, today)

    by_id = ctx.exercises().by_id
    sets = {p: 0 for p in PARTS}
    for r in in_month:
        for it in r["items"]:
            if it["id"] in by_id:
                sets[by_id[it["id"]].part] += it["sets_done"]
    weakest = min(PARTS, key=lambda p: sets[p]) if sum(sets.values()) else None

    prev_m = (year - 1, 12) if month == 1 else (year, month - 1)
    next_m = (year + 1, 1) if month == 12 else (year, month + 1)
    return render_template(
        "records.html", year=year, month=month, marks=marks,
        lead=(date(year, month, 1).weekday() + 1) % 7,   # 일요일 시작 달력의 앞 빈칸 수
        done_days=sum(1 for _, m in marks if m == "done"),
        stopped=sum(1 for r in in_month if not r.get("completed")),
        streak=streak_days(all_records, today),
        sets=sets, total_sets=sum(sets.values()), donut=_donut(sets), circ=CIRC, weakest=weakest,
        recent=list(reversed(all_records))[:5],
        prev=f"{prev_m[0]:04d}-{prev_m[1]:02d}", next=f"{next_m[0]:04d}-{next_m[1]:02d}",
    )
