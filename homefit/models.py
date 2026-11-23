"""데이터 모양. logic/과 storage/가 같은 모양을 쓰도록 여기 한 곳에 정의한다."""
from __future__ import annotations

from dataclasses import dataclass, field

LEVELS = ("초급", "중급", "고급")
LEVEL_RANK = {"초급": 1, "중급": 2, "고급": 3}
PARTS = ("상체", "하체", "코어")


@dataclass(frozen=True)
class Exercise:
    id: str
    name: str
    part: str
    level: str
    unit: str            # "회" 또는 "초"
    joint_load: str      # "낮음" | "보통" | "높음"
    alternative: str | None
    met: float
    description: str = ""
    cautions: str = ""
    name_en: str = ""

    @property
    def is_high_load(self) -> bool:
        return self.joint_load == "높음"

    @classmethod
    def from_dict(cls, d: dict) -> "Exercise":
        return cls(
            id=d["id"], name=d["name"], part=d["part"], level=d["level"], unit=d["unit"],
            joint_load=d["joint_load"], alternative=d.get("alternative"), met=float(d["met"]),
            description=d.get("description", ""), cautions=d.get("cautions", ""),
            name_en=d.get("name_en", ""),
        )


@dataclass(frozen=True)
class RoutineItem:
    id: str
    unit: str
    reps: int            # 횟수형이면 회, 시간형이면 초
    sets: int
    rest_sec: int

    def as_dict(self) -> dict:
        """routines.json 정답 파일과 같은 모양"""
        return {"id": self.id, "reps": self.reps, "sets": self.sets, "rest_sec": self.rest_sec}

    def to_session(self) -> dict:
        return {"id": self.id, "unit": self.unit, "reps": self.reps, "sets": self.sets, "rest_sec": self.rest_sec}


@dataclass
class Routine:
    level: str
    part: str                        # "전신" 또는 부위 이름
    items: list[RoutineItem]
    multiplier: float = 1.0
    substitutions: list[tuple[str, str]] = field(default_factory=list)  # (원래 id, 대체 id)
    short: bool = False              # 부위 선택 모드에서 후보가 모자라 짧아진 루틴
