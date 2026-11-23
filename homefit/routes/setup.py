"""S1 정보 입력 (A-1~A-6)"""
from datetime import date

from flask import Blueprint, redirect, render_template, request, url_for

from .. import config
from .. import context as ctx
from ..logic.body import bmi, bmi_category
from ..models import LEVELS

bp = Blueprint("setup", __name__)

LEVEL_HINT = {   # ACSM 2009의 초보·중급·고급 정의
    "초급": "운동을 막 시작했거나 쉰 지 오래됐어요",
    "중급": "6개월쯤 꾸준히 운동해 왔어요",
    "고급": "몇 년 동안 꾸준히 운동해 왔어요",
}


def _number(text: str, low: float, high: float, label: str, unit: str):
    try:
        value = float(text)
    except (TypeError, ValueError):
        return None, f"{label}를 숫자로 입력해 주세요"
    if not low <= value <= high:
        return None, f"{label}는 {low:g}~{high:g}{unit} 사이로 입력해 주세요"
    return value, None


@bp.route("/setup", methods=["GET", "POST"])
def edit():
    user = ctx.users().get()
    form = {"height": "", "weight": "", "level": "초급"}
    if user:
        form = {"height": f"{user['height_cm']:g}", "weight": f"{user['weight_kg']:g}", "level": user["level"]}
    errors = {}

    if request.method == "POST":
        form = {k: request.form.get(k, "").strip() for k in ("height", "weight", "level")}
        height, errors["height"] = _number(form["height"], *config.HEIGHT_RANGE, "키", "cm")
        weight, errors["weight"] = _number(form["weight"], *config.WEIGHT_RANGE, "몸무게", "kg")
        if form["level"] not in LEVELS:
            errors["level"] = "운동 경험을 골라 주세요"
        errors = {k: v for k, v in errors.items() if v}
        if not errors:
            same_level = user is not None and user["level"] == form["level"]
            ctx.users().save({
                "height_cm": height, "weight_kg": weight, "level": form["level"],
                # 난이도를 바꾸면 자동 조정 배율은 처음(1.0)부터 다시 시작
                "rep_multiplier": user.get("rep_multiplier", 1.0) if same_level else 1.0,
                "adjust_reason": user.get("adjust_reason") if same_level else None,
                "updated": date.today().isoformat(),
            })
            return redirect(url_for("home.index"))

    value = None
    try:
        if "height" not in errors and "weight" not in errors and form["height"] and form["weight"]:
            value = bmi(float(form["height"]), float(form["weight"]))
    except ValueError:
        value = None
    return render_template(
        "setup.html", form=form, errors=errors, levels=LEVELS, level_hint=LEVEL_HINT,
        bmi=value, category=bmi_category(value) if value else None,
        marker=min(max(value or 0, 12), 34) / 35 * 100, first_time=user is None,
    )
