"""routes에서 저장소를 꺼내 쓰는 짧은 함수들."""
from __future__ import annotations

from pathlib import Path

from flask import current_app, url_for

from .logic.body import bmi
from .storage import ExerciseRepo, RecordRepo, UserRepo


def _h():
    return current_app.extensions["homefit"]


def exercises() -> ExerciseRepo:
    return _h().exercises


def users() -> UserRepo:
    return _h().users


def records() -> RecordRepo:
    return _h().records


def video_path(exercise_id: str) -> Path:
    """시범 영상 경로는 규칙으로 정한다: static/videos/{운동 id}.mp4 (exercises.json은 고치지 않는다)."""
    return _h().video_dir / f"{exercise_id}.mp4"


def video_url(exercise_id: str) -> str | None:
    if not video_path(exercise_id).exists():
        return None
    return url_for("admin.video_file", exercise_id=exercise_id)


def user_bmi(user: dict) -> float:
    return bmi(user["height_cm"], user["weight_kg"])
