"""S4 운동 진행·휴식, S5 완료 (D-1~D-5, E-1, E-4, H-1~H-3)

진행 상태는 session["workout"]에 둔다. 모든 POST는 처리 후 리다이렉트한다(새로고침 중복 방지).
기록은 마지막 세트를 끝낸 POST(또는 그만하기)에서 한 번만 저장한다.
"""
from datetime import date, datetime

from flask import Blueprint, redirect, render_template, request, session, url_for

from .. import context as ctx
from ..logic.adjust import next_multiplier
from ..logic.calorie import kcal_for_items
from ..logic.recommend import performed_minutes
from ..logic.streak import streak_days
from .routine import PART_OPTIONS, current_routine

bp = Blueprint("workout", __name__)

FEEDBACK = ("쉬웠어요", "적당해요", "힘들었어요")


def _state():
    return session.get("workout")


def _save(state: dict, completed: bool) -> None:
    """기록 저장 → 난이도 배율 조정 → 세션 정리."""
    user = ctx.users().get()
    items = [
        {**it, "sets_planned": it["sets"], "sets_done": state["done"][k], "skipped": k in state["skipped"]}
        for k, it in enumerate(state["items"])
    ]
    for it in items:
        it.pop("sets")
    record = ctx.records().append({
        "date": date.today().isoformat(),
        "started_at": state["started_at"],
        "completed": completed,
        "level": user["level"],
        "part": state["part"],
        "multiplier": state["multiplier"],
        "items": items,
        "minutes": performed_minutes(items),
        "calories": round(kcal_for_items(items, ctx.exercises().by_id, user["weight_kg"])),
        "feedback": None,
    })
    new_mult, reason = next_multiplier(ctx.records().all(), user.get("rep_multiplier", 1.0))
    if reason:
        ctx.users().save({**user, "rep_multiplier": new_mult, "adjust_reason": reason})
    session.pop("workout", None)
    session["last_record_id"] = record["id"]


def _advance(state: dict) -> str:
    """다음 운동으로 넘어간다. 루틴이 끝났으면 저장하고 완료 화면 주소를 돌려준다."""
    state["i"] += 1
    state["set"] = 1
    if state["i"] >= len(state["items"]):
        if not any(state["done"]):          # 전부 건너뛰었으면 기록하지 않는다
            session.pop("workout", None)
            return url_for("home.index")
        _save(state, completed=True)        # 건너뛴 운동이 있어도 끝까지 왔으면 완료(skipped에 남김)
        return url_for("workout.complete")
    session["workout"] = state
    return url_for("workout.rest")


@bp.post("/workout/start")
def start():
    user = ctx.users().get()
    if user is None:
        return redirect(url_for("setup.edit"))
    part = request.form.get("part", "전신")
    routine = current_routine(user, part if part in PART_OPTIONS else "전신")
    session["workout"] = {
        "items": [it.to_session() for it in routine.items],
        "i": 0, "set": 1, "done": [0] * len(routine.items), "skipped": [],
        "part": routine.part, "multiplier": routine.multiplier,
        "started_at": datetime.now().isoformat(timespec="seconds"),
        "rest_sec": 0,
    }
    return redirect(url_for("workout.show"))


@bp.get("/workout")
def show():
    state = _state()
    if not state:
        return redirect(url_for("routine.show"))
    item = state["items"][state["i"]]
    ex = ctx.exercises().by_id[item["id"]]
    return render_template("workout.html", state=state, item=item, ex=ex, video=ctx.video_url(ex.id))


@bp.post("/workout/set-done")
def set_done():
    state = _state()
    if not state:
        return redirect(url_for("routine.show"))
    i = state["i"]
    item = state["items"][i]
    state["done"][i] = min(item["sets"], state["done"][i] + 1)
    state["rest_sec"] = item["rest_sec"]
    if state["done"][i] < item["sets"]:
        state["set"] += 1
        session["workout"] = state
        return redirect(url_for("workout.rest"))
    return redirect(_advance(state))


@bp.post("/workout/skip")
def skip():
    state = _state()
    if not state:
        return redirect(url_for("routine.show"))
    state["skipped"].append(state["i"])
    state["rest_sec"] = 0
    return redirect(_advance(state))


@bp.post("/workout/stop")
def stop():
    state = _state()
    if state and any(state["done"]):
        _save(state, completed=False)
        session.pop("last_record_id", None)
    session.pop("workout", None)
    return redirect(url_for("home.index"))


@bp.get("/rest")
def rest():
    state = _state()
    if not state:
        return redirect(url_for("routine.show"))
    if not state.get("rest_sec"):
        return redirect(url_for("workout.show"))
    item = state["items"][state["i"]]
    return render_template("rest.html", state=state, item=item, ex=ctx.exercises().by_id[item["id"]],
                           rest_sec=state["rest_sec"])


@bp.get("/complete")
def complete():
    record = ctx.records().get(session.get("last_record_id", ""))
    if record is None:
        return redirect(url_for("home.index"))
    by_id = ctx.exercises().by_id
    done_items = [it for it in record["items"] if it["sets_done"] > 0]
    parts = {}
    for it in done_items:
        part = by_id[it["id"]].part if it["id"] in by_id else "기타"
        parts[part] = parts.get(part, 0) + 1
    return render_template("complete.html", record=record, parts=parts, count=len(done_items),
                           streak=streak_days(ctx.records().all(), date.today()), feedback=FEEDBACK)


@bp.post("/complete/feedback")
def feedback():
    rid = session.get("last_record_id")
    value = request.form.get("feedback")
    if rid and value in FEEDBACK:
        ctx.records().update(rid, feedback=value)
    return redirect(url_for("workout.complete"))
