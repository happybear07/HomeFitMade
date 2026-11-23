# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""홈핏 메이트 데이터 검사기: exercises.json / routines.json 이 SOURCES.md 규칙을 지키는지 확인한다.
실행: uv run check_data.py  (표준 라이브러리만 사용)"""
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).parent
exercises = json.loads((HERE / "exercises.json").read_text(encoding="utf-8"))
routines = json.loads((HERE / "routines.json").read_text(encoding="utf-8"))
sources_md = (HERE / "SOURCES.md").read_text(encoding="utf-8")

PARTS = ["상체", "하체", "코어"]
LEVELS = ["초급", "중급", "고급"]
LOAD_RANK = {"낮음": 1, "보통": 2, "높음": 3}
# 대한비만학회 2022 기준: 범주 이름 -> BMI 하한
BMI_MIN = {"저체중": 0, "정상": 18.5, "비만 전단계(과체중)": 23, "1단계 비만": 25, "2단계 이상 비만": 30}
EX_KEYS = ["id", "name", "name_en", "part", "level", "unit", "reps", "sets", "rest_sec", "joint_load",
           "met", "met_source", "description", "cautions", "alternative", "video", "sources"]
RT_KEYS = ["bmi_category", "bmi_range", "level", "exercises", "estimated_minutes", "calories_per_kg",
           "calorie_example", "rationale"]

errors = []
def check(ok, msg):
    if not ok:
        errors.append(msg)

# 1) 운동 목록: 필수 키, 허용 값, 중복 id
by_id = {}
for e in exercises:
    eid = e.get("id", "?")
    missing = [k for k in EX_KEYS if k not in e]
    check(not missing, f"[운동 {eid}] 필수 키 누락: {missing}")
    if missing:
        continue
    check(eid not in by_id, f"[운동 {eid}] id 중복")
    by_id[eid] = e
    check(e["part"] in PARTS + ["전신"], f"[운동 {eid}] part 값 오류: {e['part']}")
    check(e["level"] in LEVELS, f"[운동 {eid}] level 값 오류: {e['level']}")
    check(e["unit"] in ("회", "초"), f"[운동 {eid}] unit 값 오류: {e['unit']}")
    check(e["joint_load"] in LOAD_RANK, f"[운동 {eid}] joint_load 값 오류: {e['joint_load']}")
    for k in ("reps", "sets", "rest_sec", "met"):
        check(isinstance(e[k], (int, float)) and e[k] > 0, f"[운동 {eid}] {k} 는 양수여야 함")
    check(e["met_source"].startswith("2024 Adult Compendium"), f"[운동 {eid}] met_source 가 Compendium 이 아님")
    for key in e["sources"]:
        check(key in sources_md, f"[운동 {eid}] 출처 키 {key} 가 SOURCES.md 에 없음")

# 2) 구성 규칙
# v2(2026-11-23): SOURCES.md 4장 기준 10번(전체 28개 이하)에 맞춰 상한을 20 -> 28로 변경
check(18 <= len(exercises) <= 28, f"운동 수는 18~28개여야 함 (현재 {len(exercises)})")
for part in PARTS:
    in_part = [e for e in by_id.values() if e["part"] == part]
    check(len(in_part) >= 5, f"{part} 운동이 5개 미만 ({len(in_part)})")
    for level in LEVELS:
        check(any(e["level"] == level for e in in_part), f"{part}에 {level} 운동이 없음")

# 3) 관절 부담 '높음' 운동과 대체 운동
high = [e for e in by_id.values() if e["joint_load"] == "높음"]
check(len(high) >= 3, f"관절 부담 '높음' 운동이 3개 미만 ({len(high)})")
for e in by_id.values():
    alt = e["alternative"]
    if e["joint_load"] != "높음":
        check(alt is None, f"[운동 {e['id']}] '높음'이 아니면 alternative 는 null 이어야 함")
    elif alt not in by_id:
        errors.append(f"[운동 {e['id']}] 대체 운동 {alt} 이(가) 목록에 없음")
    else:
        check(by_id[alt]["part"] == e["part"], f"[운동 {e['id']}] 대체 운동 부위가 다름")
        check(LOAD_RANK[by_id[alt]["joint_load"]] < LOAD_RANK["높음"], f"[운동 {e['id']}] 대체 운동의 관절 부담이 낮지 않음")

# 4) 루틴: 15개 조합, id 존재, BMI 25 이상 '높음' 금지, 3부위 포함, 칼로리 계산 일치
combos = {(r.get("bmi_category"), r.get("level")) for r in routines}
check(len(routines) == 15 and len(combos) == 15, "루틴은 BMI 5범주 x 난이도 3 = 15개(중복 없이)여야 함")
for r in routines:
    name = f"[루틴 {r.get('bmi_category')}/{r.get('level')}]"
    missing = [k for k in RT_KEYS if k not in r]
    check(not missing, f"{name} 필수 키 누락: {missing}")
    if missing:
        continue
    if r["bmi_category"] not in BMI_MIN:
        errors.append(f"{name} 알 수 없는 BMI 범주")
        continue
    ids = [x["id"] for x in r["exercises"]]
    unknown = [i for i in ids if i not in by_id]
    check(not unknown, f"{name} 없는 운동 id: {unknown}")
    known = [by_id[i] for i in ids if i in by_id]
    if BMI_MIN[r["bmi_category"]] >= 25:
        bad = [e["id"] for e in known if e["joint_load"] == "높음"]
        check(not bad, f"{name} BMI 25 이상인데 관절 부담 '높음' 운동 포함: {bad}")
    parts = {e["part"] for e in known}
    check(all(p in parts for p in PARTS), f"{name} 상체/하체/코어 중 빠진 부위: {set(PARTS) - parts}")
    ex = r["calorie_example"]
    check(abs(r["calories_per_kg"] * ex["weight_kg"] - ex["kcal"]) < 0.5, f"{name} 칼로리 예시 계산 불일치")

# 결과 출력
print(f"운동 {len(exercises)}개, 루틴 {len(routines)}개 검사")
for part in PARTS:
    counts = {lv: sum(1 for e in by_id.values() if e["part"] == part and e["level"] == lv) for lv in LEVELS}
    print(f"  {part}: " + ", ".join(f"{lv} {n}개" for lv, n in counts.items()))
print(f"  관절 부담 '높음': {', '.join(e['id'] + '→' + str(e['alternative']) for e in high)}")
if errors:
    print(f"\n실패: 문제 {len(errors)}건")
    for msg in errors:
        print("  - " + msg)
    sys.exit(1)
print("\n통과: 모든 검사를 만족합니다.")
