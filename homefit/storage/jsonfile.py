"""JSON 파일 읽기·쓰기 (NFR-3). 파일을 여는 코드는 storage/ 안에만 둔다."""
from __future__ import annotations

import json
import os
import threading
from datetime import datetime
from pathlib import Path

write_lock = threading.Lock()   # Flask 개발 서버는 요청을 스레드로 처리하므로 쓰기를 한 번에 하나씩

# 손상돼서 옮겨 둔 파일 목록. 화면에 한 번 안내하고 비운다(homefit/__init__.py).
recovered: list[Path] = []


def save_json(path: Path, data) -> None:
    """원자적 저장: 임시 파일에 다 쓴 뒤 한 번에 바꿔치기한다. 중간에 꺼져도 반쪽 파일이 남지 않는다."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, path)


def load_json(path: Path, default):
    """파일이 없으면 default. 손상됐으면 지우지 않고 .broken-날짜로 옮긴 뒤 default."""
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        backup = path.with_name(f"{path.stem}.broken-{datetime.now():%Y%m%d-%H%M%S}{path.suffix}")
        path.rename(backup)
        recovered.append(backup)
        return default
