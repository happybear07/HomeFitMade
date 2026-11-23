"""exercises.json 검사 (B-2, B-3). 서버 시작 때 실행해서, 틀리면 무엇이 틀렸는지 알려 주고 멈춘다.

출처(SOURCES.md)까지 보는 전체 검사는 data/check_data.py가 한다. 여기서는 앱이 동작하는 데 필요한 것만 본다.
"""
from __future__ import annotations

from .models import LEVELS, PARTS

REQUIRED = ("id", "name", "part", "level", "unit", "joint_load", "alternative", "met", "description", "cautions")
LOADS = ("낮음", "보통", "높음")


def validate_exercises(raw) -> list[str]:
    if not isinstance(raw, list) or not raw:
        return ["exercises.json이 비어 있거나 목록 형식이 아닙니다."]
    errors: list[str] = []
    ids: dict[str, dict] = {}
    for d in raw:
        eid = d.get("id", "?") if isinstance(d, dict) else "?"
        missing = [k for k in REQUIRED if not isinstance(d, dict) or k not in d]
        if missing:
            errors.append(f"[{eid}] 필수 항목 없음: {', '.join(missing)}")
            continue
        if eid in ids:
            errors.append(f"[{eid}] id가 중복됨")
        ids[eid] = d
        if d["part"] not in PARTS:
            errors.append(f"[{eid}] part는 {'/'.join(PARTS)} 중 하나여야 함: {d['part']}")
        if d["level"] not in LEVELS:
            errors.append(f"[{eid}] level 값 오류: {d['level']}")
        if d["unit"] not in ("회", "초"):
            errors.append(f"[{eid}] unit은 회/초 중 하나여야 함: {d['unit']}")
        if d["joint_load"] not in LOADS:
            errors.append(f"[{eid}] joint_load 값 오류: {d['joint_load']}")
        if not isinstance(d["met"], (int, float)) or d["met"] <= 0:
            errors.append(f"[{eid}] met는 양수여야 함")
    for eid, d in ids.items():
        alt = d.get("alternative")
        if d.get("joint_load") == "높음":
            if alt not in ids:
                errors.append(f"[{eid}] 관절 부담 '높음'인데 대체 운동({alt})이 목록에 없음")
            elif ids[alt].get("joint_load") == "높음":
                errors.append(f"[{eid}] 대체 운동 {alt}도 관절 부담이 '높음'")
    for part in PARTS:
        if not any(d.get("part") == part and d.get("level") == "초급" for d in ids.values()):
            errors.append(f"{part}에 초급 운동이 없어 초급 루틴을 만들 수 없음")
    return errors
