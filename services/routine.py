"""
루틴 추천

※ 임시 구현입니다. 추천 알고리즘·칼로리 계산은 강군호 담당이므로
   recommend()가 운동 딕셔너리 리스트를 돌려주기만 하면 화면은 그대로 동작합니다.
"""
from services.storage import load_exercises

LEVELS = {"초급": 0, "중급": 1, "고급": 2}
SCALE = {"초급": 0.7, "중급": 1.0, "고급": 1.4}


def bmi(user):
    h = user["height"] / 100
    return round(user["weight"] / (h * h), 1)


def recommend(user, part="전신"):
    level = user.get("level", "초급")
    exercises = [e for e in load_exercises()
                 if LEVELS.get(e["level"], 0) <= LEVELS[level]]
    if bmi(user) >= 25:  # 관절 부담이 큰 운동 제외
        exercises = [e for e in exercises if e.get("joint_load") != "높음"]
    parts = ["상체", "하체", "코어"] if part == "전신" else [part]

    result = []
    for p in parts:
        picks = [e for e in exercises if e["part"] == p]
        picks.sort(key=lambda e: LEVELS.get(e["level"], 0), reverse=True)
        for e in picks[: (2 if part == "전신" else 4)]:
            item = dict(e)
            item["reps"] = max(1, round(e["reps"] * SCALE[level]))
            result.append(item)
    return result


def estimate_minutes(items):
    sec = sum(e["sets"] * (e["reps"] * (1 if e.get("unit") == "초" else 3) + 30) for e in items)
    return max(1, round(sec / 60))


def estimate_calories(items, weight):
    total = 0
    for e in items:
        sec = e["sets"] * e["reps"] * (1 if e.get("unit") == "초" else 3)
        total += e.get("met", 5) * 3.5 * weight / 200 * (sec / 60)
    return round(total)
