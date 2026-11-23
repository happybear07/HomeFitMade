"""S2 홈 (E-2, E-3, F-1~F-4)"""
from datetime import date

from flask import Blueprint, redirect, render_template, request, url_for

from .. import context as ctx
from ..logic.recommend import build_routine, estimate_minutes
from ..logic.streak import STAGES, gap_days, gap_stage, streak_days, week_marks

bp = Blueprint("home", __name__)

MOOD = {"g0": "happy", "g1": "sad", "g2": "angry", "g3": "fallen"}


@bp.get("/")
def index():
    user = ctx.users().get()
    if user is None:
        return redirect(url_for("setup.edit"))   # 처음 사용자(A-4)

    today = date.today()
    records = ctx.records().all()
    gap, streak = gap_days(records, today), streak_days(records, today)
    stage = gap_stage(gap)
    # 발표 시연용: /?stage=g2 처럼 붙이면 그 단계 화면을 미리 본다(기록은 바뀌지 않음)
    if request.args.get("stage") in STAGES:
        stage = request.args["stage"]
        gap = {"g0": gap, "g1": max(gap, 3), "g2": max(gap, 7), "g3": max(gap, 14)}[stage]

    routine = build_routine(user["level"], ctx.user_bmi(user), ctx.exercises().all,
                            multiplier=user.get("rep_multiplier", 1.0))
    return render_template(
        "home.html", stage=stage, mood=MOOD[stage], gap=gap, streak=streak,
        has_records=bool(records), done_today=any(d == today and m == "done" for d, m in week_marks(records, today)),
        week=week_marks(records, today), today=today, user=user,
        routine=routine, minutes=estimate_minutes(routine.items), by_id=ctx.exercises().by_id,
    )
