"""S7 관리자 · 시범 영상 업로드 (G-1~G-3)  담당: 고의찬

- 파일 이름은 사용자가 올린 이름이 아니라 운동 id로 정한다: static/videos/{id}.mp4
  → 경로 조작(../) 문제가 생기지 않고, exercises.json을 다시 쓸 필요가 없다.
- 50MB 제한은 app.config["MAX_CONTENT_LENGTH"]가 막고(413), 여기서는 확장자와 mp4 시그니처를 본다.
"""
from flask import Blueprint, abort, flash, redirect, render_template, request, send_from_directory, url_for

from .. import config
from .. import context as ctx

bp = Blueprint("admin", __name__)


def is_mp4(head: bytes) -> bool:
    """mp4 파일은 4~8번째 바이트가 'ftyp'이다(ISO base media file format)."""
    return len(head) >= 12 and head[4:8] == b"ftyp"


@bp.get("/admin/videos")
def videos():
    exercises = ctx.exercises().all
    rows = [(e, ctx.video_path(e.id).exists()) for e in exercises]
    return render_template("admin.html", rows=rows, registered=sum(1 for _, ok in rows if ok),
                           selected=request.args.get("ex", ""), max_mb=config.MAX_UPLOAD_MB)


@bp.post("/admin/videos")
def upload():
    exercise_id = request.form.get("exercise_id", "")
    file = request.files.get("video")
    back = url_for("admin.videos", ex=exercise_id)
    if exercise_id not in ctx.exercises().by_id:
        flash("운동을 골라 주세요.", "error")
        return redirect(back)
    if file is None or not file.filename:
        flash("영상 파일을 골라 주세요.", "error")
        return redirect(back)
    if not file.filename.lower().endswith(".mp4"):
        flash(f"{file.filename}는 올릴 수 없어요. mp4만 가능해요.", "error")
        return redirect(back)
    head = file.stream.read(12)
    file.stream.seek(0)
    if not is_mp4(head):
        flash(f"{file.filename}는 mp4 영상이 아니에요. 파일을 다시 확인해 주세요.", "error")
        return redirect(back)
    file.save(ctx.video_path(exercise_id))
    flash(f"{ctx.exercises().by_id[exercise_id].name} 영상을 등록했어요.", "ok")
    return redirect(back)


@bp.get("/videos/<exercise_id>.mp4")
def video_file(exercise_id):
    if exercise_id not in ctx.exercises().by_id:
        abort(404)
    return send_from_directory(ctx.video_path(exercise_id).parent, f"{exercise_id}.mp4", mimetype="video/mp4")


@bp.app_errorhandler(413)
def too_large(e):
    flash(f"{config.MAX_UPLOAD_MB}MB 이하 파일만 올릴 수 있어요.", "error")
    return redirect(url_for("admin.videos"))
