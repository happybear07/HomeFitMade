"""S3 루틴 추천 (C-1~C-7, H-3)"""
from flask import Blueprint, redirect, render_template, request, url_for

from .. import context as ctx
from ..logic.recommend import build_routine, estimate_minutes
from ..models import PARTS

bp = Blueprint("routine", __name__)

PART_OPTIONS = ("전신",) + PARTS


def current_routine(user: dict, part: str):
    return build_routine(user["level"], ctx.user_bmi(user), ctx.exercises().all,
                         part=part, multiplier=user.get("rep_multiplier", 1.0))


@bp.get("/routine")
def show():
    user = ctx.users().get()
    if user is None:
        return redirect(url_for("setup.edit"))
    part = request.args.get("part", "전신")
    if part not in PART_OPTIONS:
        part = "전신"
    routine = current_routine(user, part)
    by_id = ctx.exercises().by_id
    return render_template(
        "routine.html", routine=routine, part=part, parts=PART_OPTIONS, by_id=by_id,
        minutes=estimate_minutes(routine.items), adjust_reason=user.get("adjust_reason"),
        substitutions=[(by_id[a].name, by_id[b].name) for a, b in routine.substitutions],
    )
