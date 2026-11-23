"""앱 조립: 설정 → 데이터 검사 → 저장소 준비 → 블루프린트 등록."""
from __future__ import annotations

import secrets
from pathlib import Path
from types import SimpleNamespace

from flask import Flask, flash, render_template

from . import config, views
from .storage import ExerciseRepo, RecordRepo, UserRepo, load_json
from .storage import jsonfile
from .validate import validate_exercises


def _secret_key(data_dir: Path) -> str:
    path = data_dir / config.SECRET_FILE
    if not path.exists():
        data_dir.mkdir(parents=True, exist_ok=True)
        path.write_text(secrets.token_hex(32), encoding="utf-8")
    return path.read_text(encoding="utf-8").strip()


def create_app(overrides: dict | None = None) -> Flask:
    """overrides: 테스트에서 DATA_DIR, VIDEO_DIR 등을 임시 폴더로 바꿀 때 쓴다."""
    settings = {"DATA_DIR": config.DATA_DIR, "VIDEO_DIR": config.VIDEO_DIR, **(overrides or {})}
    data_dir, video_dir = Path(settings["DATA_DIR"]), Path(settings["VIDEO_DIR"])

    app = Flask(__name__, template_folder=str(config.TEMPLATE_DIR), static_folder=str(config.STATIC_DIR))
    app.config.update(settings)
    app.config["MAX_CONTENT_LENGTH"] = config.MAX_UPLOAD_MB * 1024 * 1024   # 넘으면 Flask가 413을 낸다
    app.secret_key = _secret_key(data_dir)

    # 운동 데이터가 틀리면 여기서 멈춘다(NFR-4)
    raw = load_json(data_dir / config.EXERCISE_FILE, None)
    errors = validate_exercises(raw)
    if errors:
        raise SystemExit("exercises.json 검사 실패:\n  - " + "\n  - ".join(errors))

    video_dir.mkdir(parents=True, exist_ok=True)
    app.extensions["homefit"] = SimpleNamespace(
        exercises=ExerciseRepo(raw),
        users=UserRepo(data_dir / config.USER_FILE),
        records=RecordRepo(data_dir / config.RECORD_FILE),
        video_dir=video_dir,
    )

    views.register(app)

    from .routes import admin, home, records, routine, setup, workout
    for bp in (home.bp, setup.bp, routine.bp, workout.bp, records.bp, admin.bp):
        app.register_blueprint(bp)

    @app.before_request
    def _notice_recovered_files():
        while jsonfile.recovered:
            broken = jsonfile.recovered.pop()
            flash(f"저장 파일이 손상돼 새로 시작했어요. 원래 파일은 {broken.name}로 옮겨 두었어요.", "error")

    @app.errorhandler(404)
    def _not_found(e):
        return render_template("message.html", title="페이지를 찾을 수 없어요",
                               body="주소를 다시 확인해 주세요."), 404

    @app.errorhandler(500)
    def _server_error(e):
        app.logger.exception("처리하지 못한 오류")
        return render_template("message.html", title="문제가 생겼어요",
                               body="잠시 후 다시 시도해 주세요. 기록은 지워지지 않았어요."), 500

    return app
