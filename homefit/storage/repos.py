"""데이터 파일별 저장소. routes는 이 클래스만 쓰고 파일 경로는 모른다."""
from __future__ import annotations

import uuid
from pathlib import Path

from ..models import Exercise
from .jsonfile import load_json, save_json, write_lock


class ExerciseRepo:
    """exercises.json (읽기 전용). 시작할 때 한 번 읽어 메모리에 둔다."""

    def __init__(self, raw: list[dict]):
        self.raw = raw
        self.all = [Exercise.from_dict(d) for d in raw]
        self.by_id = {e.id: e for e in self.all}

    @classmethod
    def load(cls, path: Path) -> "ExerciseRepo":
        return cls(load_json(path, []))


class UserRepo:
    """user.json: 키, 몸무게, 난이도, 난이도 배율. 없으면 처음 사용자."""

    def __init__(self, path: Path):
        self.path = path

    def get(self) -> dict | None:
        user = load_json(self.path, None)
        return user if isinstance(user, dict) and "height_cm" in user else None

    def save(self, user: dict) -> None:
        with write_lock:
            save_json(self.path, user)


class RecordRepo:
    """records.json: 운동 기록 목록(오래된 것 → 최근)."""

    def __init__(self, path: Path):
        self.path = path

    def all(self) -> list[dict]:
        data = load_json(self.path, [])
        return data if isinstance(data, list) else []

    def get(self, record_id: str) -> dict | None:
        return next((r for r in self.all() if r.get("id") == record_id), None)

    def append(self, record: dict) -> dict:
        """읽기 → 추가 → 원자적 저장을 한 잠금 안에서 한다."""
        with write_lock:
            records = self.all()
            record = {"id": uuid.uuid4().hex[:12], **record}
            records.append(record)
            save_json(self.path, records)
        return record

    def update(self, record_id: str, **fields) -> None:
        with write_lock:
            records = self.all()
            for r in records:
                if r.get("id") == record_id:
                    r.update(fields)
            save_json(self.path, records)
