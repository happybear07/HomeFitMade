"""
홈핏 메이트 - Flask 웹 서버 (담당: 장선민)

화면 흐름: 홈(/) → 루틴 추천(/routine) → 운동 진행(/workout/<번호>) → 완료(/done)
처음 실행하면 정보 입력(/profile) 화면으로 먼저 이동한다.
"""
import calendar
import os
from datetime import date

from flask import Flask, render_template, request, redirect, url_for, session, flash

from services import storage, stage, routine

# exe로 묶였을 때도 화면 파일(templates, static)을 찾을 수 있게 경로를 지정
app = Flask(__name__,
            template_folder=os.path.join(storage.RESOURCE, "templates"),
            static_folder=os.path.join(storage.RESOURCE, "static"))
app.secret_key = "homefit-dev-key"  # 세션(오늘의 루틴 저장)에 필요


def current_stage():
    """마지막 운동 후 지난 일수로 화면 단계를 구한다.
    발표 시연용으로 주소 뒤에 ?days=10 처럼 붙이면 그 일수로 미리 볼 수 있다."""
    preview = request.args.get("days")
    if preview is not None and preview.isdigit():
        days = int(preview)
    else:
        days = storage.days_since_last_workout()
    return stage.get_stage(days), days


@app.context_processor
def inject_stage():
    """모든 화면(base.html)에서 단계 정보를 쓸 수 있게 넘겨준다."""
    st, days = current_stage()
    return {"stage": st, "days": days}


@app.route("/")
def home():
    user = storage.load_user()
    if user is None:
        return redirect(url_for("profile"))
    return render_template("home.html", user=user, streak=storage.streak())


@app.route("/profile", methods=["GET", "POST"])
def profile():
    user = storage.load_user() or {}
    if request.method == "POST":
        try:
            height = float(request.form["height"])
            weight = float(request.form["weight"])
            if not (100 <= height <= 230 and 25 <= weight <= 250):
                raise ValueError
        except (KeyError, ValueError):
            flash("키는 100~230cm, 몸무게는 25~250kg 사이 숫자로 입력해주세요.")
            return render_template("profile.html", user=request.form)
        level = request.form.get("level", "초급")
        storage.save_user({"height": height, "weight": weight, "level": level})
        return redirect(url_for("home"))
    bmi = routine.bmi(user) if user.get("height") else None
    return render_template("profile.html", user=user, bmi=bmi)


@app.route("/routine")
def routine_page():
    user = storage.load_user()
    if user is None:
        return redirect(url_for("profile"))
    part = request.args.get("part", "전신")
    items = routine.recommend(user, part)
    session["routine"] = items
    return render_template("routine.html", items=items, part=part,
                           parts=["전신", "상체", "하체", "코어"],
                           minutes=routine.estimate_minutes(items))


@app.route("/workout/<int:idx>")
def workout(idx):
    items = session.get("routine")
    if not items:
        return redirect(url_for("routine_page"))
    if idx >= len(items):
        return redirect(url_for("done"))
    ex = items[idx]
    return render_template("workout.html", ex=ex, idx=idx, total=len(items),
                           has_video=storage.video_exists(ex.get("video")))


@app.route("/done")
def done():
    items = session.pop("routine", None)
    if items:
        user = storage.load_user() or {}
        kcal = routine.estimate_calories(items, user.get("weight", 60))
        storage.add_record([e["name"] for e in items], kcal)
    else:
        kcal = None
    return render_template("done.html", kcal=kcal, streak=storage.streak())


@app.route("/history")
def history():
    """운동 기록: 이번 달 달력, 통계, 배지"""
    today = date.today()
    year = int(request.args.get("y", today.year))
    month = int(request.args.get("m", today.month))
    if not 1 <= month <= 12:
        year, month = today.year, today.month
    info = storage.summary()
    weeks = calendar.Calendar(firstweekday=6).monthdayscalendar(year, month)
    prev_ym = (year - 1, 12) if month == 1 else (year, month - 1)
    next_ym = (year + 1, 1) if month == 12 else (year, month + 1)
    badges = [
        ("첫 운동", "운동을 처음 완료", info["count"] >= 1),
        ("3일 연속", "3일 연속 운동", info["best_streak"] >= 3),
        ("일주일 챌린지", "7일 연속 운동", info["best_streak"] >= 7),
        ("열 번째 운동", "운동 10회 완료", info["count"] >= 10),
        ("천 칼로리", "누적 1000kcal 소모", info["calories"] >= 1000),
        ("한 달의 기적", "30일 연속 운동", info["best_streak"] >= 30),
    ]
    return render_template("history.html", info=info, weeks=weeks, year=year,
                           month=month, today=today, prev_ym=prev_ym,
                           next_ym=next_ym, badges=badges)


@app.route("/exercises")
def exercise_list():
    """운동 도감: 전체 운동 목록과 부위 필터"""
    part = request.args.get("part", "전체")
    items = storage.load_exercises()
    if part != "전체":
        items = [e for e in items if e["part"] == part]
    return render_template("exercises.html", items=items, part=part,
                           parts=["전체", "상체", "하체", "코어"])


@app.route("/exercises/<name>")
def exercise_detail(name):
    ex = next((e for e in storage.load_exercises() if e["name"] == name), None)
    if ex is None:
        return render_template("message.html", title="운동을 찾을 수 없어요",
                               body="운동 도감에서 다시 골라주세요."), 404
    return render_template("exercise_detail.html", ex=ex,
                           has_video=storage.video_exists(ex.get("video")))


@app.route("/stages")
def stages_preview():
    """발표 시연용: 4단계 화면을 한눈에 비교"""
    samples = [(1, "0~2일"), (4, "3~6일"), (10, "7~13일"), (20, "14일 이상")]
    return render_template("stages.html",
                           samples=[(d, label, stage.get_stage(d)) for d, label in samples])


@app.errorhandler(404)
def not_found(e):
    return render_template("message.html", title="페이지를 찾을 수 없어요",
                           body="주소를 다시 확인해주세요."), 404


if __name__ == "__main__":
    app.run(debug=True)
