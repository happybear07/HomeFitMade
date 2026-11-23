"""
JSON 파일 저장/불러오기

※ 임시 구현입니다. 기록·공백 일수 계산은 강군호 담당이므로
   함수 이름과 반환값 형태만 유지하면 내부는 자유롭게 바꿔도 됩니다.
"""
import json
import os
import shutil
import sys
from datetime import date, timedelta

if getattr(sys, "frozen", False):
    # exe 실행: 화면 파일은 exe 내부, 기록은 exe 옆 data 폴더에 저장
    RESOURCE = sys._MEIPASS
    BASE = os.path.dirname(sys.executable)
else:
    RESOURCE = BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
USER_FILE = os.path.join(DATA, "user.json")
RECORD_FILE = os.path.join(DATA, "records.json")
EXERCISE_FILE = os.path.join(DATA, "exercises.json")


def _read(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default  # 파일이 없거나 손상돼도 프로그램이 멈추지 않게


def _write(path, data):
    os.makedirs(DATA, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_user():
    return _read(USER_FILE, None)


def save_user(user):
    _write(USER_FILE, user)


def load_exercises():
    if not os.path.isfile(EXERCISE_FILE):
        # exe 첫 실행: 기본 운동 데이터를 data 폴더로 복사해서 수정할 수 있게
        bundled = os.path.join(RESOURCE, "data", "exercises.json")
        if os.path.isfile(bundled):
            os.makedirs(DATA, exist_ok=True)
            shutil.copy(bundled, EXERCISE_FILE)
    return _read(EXERCISE_FILE, [])


def load_records():
    return _read(RECORD_FILE, [])


def add_record(names, kcal):
    records = load_records()
    records.append({"date": date.today().isoformat(), "exercises": names,
                    "completed": True, "calories": kcal})
    _write(RECORD_FILE, records)


def _workout_dates():
    return sorted({date.fromisoformat(r["date"]) for r in load_records()
                   if r.get("completed")})


def days_since_last_workout():
    """기록이 없으면 None"""
    dates = _workout_dates()
    if not dates:
        return None
    return (date.today() - dates[-1]).days


def streak():
    """오늘(또는 어제)까지 연속으로 운동한 일수"""
    dates = set(_workout_dates())
    day = date.today()
    if day not in dates:
        day -= timedelta(days=1)
    count = 0
    while day in dates:
        count += 1
        day -= timedelta(days=1)
    return count


def video_exists(path):
    return bool(path) and os.path.isfile(os.path.join(RESOURCE, path))


def summary():
    """기록 화면용 통계"""
    records = [r for r in load_records() if r.get("completed")]
    dates = _workout_dates()
    best = cur = 0
    prev = None
    for d in dates:
        cur = cur + 1 if prev and (d - prev).days == 1 else 1
        best = max(best, cur)
        prev = d
    return {
        "count": len(records),
        "days": len(dates),
        "calories": sum(r.get("calories", 0) for r in records),
        "best_streak": best,
        "dates": {d.isoformat() for d in dates},
        "recent": list(reversed(records[-5:])),
    }
