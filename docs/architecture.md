# 홈핏 메이트 아키텍처 · 구현 설계 (v0.1)

- 작성일: 2026-11-23
- 기준 문서: 기능명세서 v0.1(`docs/홈핏메이트_기능명세서_v0.1.docx`), 운동 데이터(`exercises.json` 26개, `routines.json`, `SOURCES.md`, 검증 보고서 `research/data_verification.md`), 화면 설계 캔버스(S1~S7, 디자인 시스템 v0.6)
- 읽는 사람: 팀원 3명. 기능 ID(A-1, C-3 등)는 기능명세서와 같다.

---

## 0. 한 장 요약

| 결정 | 내용 | 이유 |
|---|---|---|
| 실행 | `uv run app.py` 한 줄. 의존성은 `pyproject.toml` 하나에 선언 | 교수님 조건 |
| 구조 | **routes(화면 전환) → logic(순수 함수) / storage(JSON 입출력)** 3층 | 핵심 로직 위치를 누구나 설명할 수 있게 |
| 핵심 로직 | `homefit/logic/` 아래 5개 파일. Flask와 파일을 import하지 않는 순수 함수 | 테스트가 쉽고, "추천은 어디 있어?"에 파일 하나로 답할 수 있음 |
| 데이터 | `exercises.json`은 읽기 전용. 쓰는 파일은 `user.json`, `records.json` 둘뿐 | 정리한 운동 데이터를 앱이 망가뜨리지 않게 |
| 진행 상태 | 운동 중 상태(몇 번째 운동, 몇 세트)는 Flask `session`에 저장 | DB 없이 새로고침에도 유지 |
| 검증 | `routines.json` 15개를 정답으로 쓰는 pytest. 아래 규칙으로 **15/15 재현 확인함** | 추천 알고리즘이 문서와 같은지 자동 확인 |

---

## 1. 전제와 제약

- 1인 사용자, 로컬 PC 실행, 로그인 없음.
- Python 3.11 이상, Flask 3.x, 데이터는 JSON 파일(DB 없음).
- 교수님 조건: ① `uv run app.py` 한 줄로 실행, ② 팀이 핵심 로직의 위치를 직접 설명할 수 있어야 함.
- 화면은 서버 렌더링(Jinja2). 타이머만 브라우저 JavaScript.

---

## 2. 전체 구조

```
브라우저 ──HTTP──▶ routes/      화면 전환만 한다 (요청 읽기 → 함수 호출 → 템플릿)
                    │   │
                    │   └──▶ storage/   JSON 읽기·쓰기, 손상 파일 복구
                    ▼
                 logic/        계산만 한다 (BMI, 추천, 칼로리, 공백·연속 일수, 난이도 조정)
                    ▲
                 models.py     데이터 모양(dataclass)
```

**지켜야 할 규칙 3개**

1. `logic/`의 파일은 `flask`, `open()`, `datetime.now()`를 쓰지 않는다. 필요한 값(오늘 날짜, 운동 목록, 기록)은 전부 인자로 받는다.
2. `routes/`의 함수는 20줄 안팎으로 유지한다. 계산이 들어가기 시작하면 `logic/`으로 옮긴다.
3. 파일을 읽고 쓰는 코드는 `storage/`에만 있다.

이렇게 하면 "추천 규칙은 `logic/recommend.py`의 `build_routine()`"처럼 기능 하나가 파일 하나, 함수 하나로 대응한다.

---

## 3. 폴더 구조와 담당

```
homefit-mate/
├─ pyproject.toml           의존성 (flask, 개발용 pytest)
├─ app.py                   실행 진입점: uv run app.py
├─ homefit/
│  ├─ __init__.py           create_app(): 설정, 블루프린트 등록, 시작 시 데이터 검사
│  ├─ config.py             경로, 업로드 제한(50MB), 기본값 상수
│  ├─ models.py             Exercise, User, RoutineItem, Routine, Record (dataclass)
│  ├─ logic/                ★ 핵심 로직 (순수 함수)
│  │  ├─ body.py            bmi(), bmi_category()                      A-3
│  │  ├─ recommend.py       build_routine(), estimate_minutes()        C-1~C-5, C-7
│  │  ├─ calorie.py         kcal_for_items()                            E-4
│  │  ├─ streak.py          gap_days(), streak_days(), gap_stage()      E-2, E-3, F-1
│  │  ├─ adjust.py          next_multiplier()                           H-1~H-3
│  │  └─ util.py            round_half_up()  (반올림 함정, 14장 참고)
│  ├─ storage/
│  │  ├─ jsonfile.py        load_json(), save_json() 원자적 저장, 손상 복구   NFR-3
│  │  └─ repos.py           ExerciseRepo, UserRepo, RecordRepo
│  ├─ validate.py           exercises.json 검사 (check_data.py 규칙 재사용)   B-2, B-3
│  └─ routes/
│     ├─ home.py            /                                          S2
│     ├─ setup.py           /setup                                     S1
│     ├─ routine.py         /routine                                   S3
│     ├─ workout.py         /workout, /rest, /complete                 S4, S5
│     ├─ records.py         /records                                   S6
│     └─ admin.py           /admin/videos                              S7
├─ templates/               base.html, macros.html, 화면별 html
├─ static/
│  ├─ css/tokens.css        디자인 토큰 (8장)
│  ├─ css/app.css
│  ├─ js/timer.js           운동·휴식 카운트다운                         D-5
│  ├─ img/bear/             곰 SVG 5종 (캔버스 Bear 컴포넌트에서 추출)
│  └─ videos/               시범 영상 {exercise_id}.mp4                 G-2
├─ data/
│  ├─ exercises.json        homefit_data에서 복사 (Git 관리)
│  ├─ user.json             실행 중 생성 (.gitignore)
│  ├─ records.json          실행 중 생성 (.gitignore)
│  └─ secret_key            세션용 키, 첫 실행 때 생성 (.gitignore)
├─ tools/check_data.py      데이터 검사 (validate.py를 호출)
└─ tests/                   pytest (11장)
```

| 담당 (기획서 역할 분담) | 파일 |
|---|---|
| 고의찬 (운동 데이터, 관리자, 타이머) | `data/exercises.json`, `validate.py`, `tools/check_data.py`, `routes/admin.py`, `static/js/timer.js`, `templates/admin.html`, `workout.html`의 타이머 부분 |
| 강군호 (추천, BMI·칼로리, 기록·공백 일수, 난이도 조정) | `logic/` 전체, `storage/`, `models.py`, `tests/test_logic_*.py` |
| 장선민 (Flask 구조, 화면, 공백 테마·마스코트) | `app.py`, `homefit/__init__.py`, `routes/`의 화면 전환, `templates/`, `static/css/`, `static/img/bear/` |

---

## 4. 데이터 설계

### 4-1. `exercises.json` (읽기 전용, 26개)

이미 정리한 파일을 그대로 쓴다. 앱은 이 파일을 **절대 쓰지 않는다**.

| 필드 | 예 | 쓰는 곳 |
|---|---|---|
| `id` | `push_up` | 모든 참조 키, 영상 파일 이름 |
| `name`, `name_en` | 푸시업 | 화면 표시 |
| `part` | 상체/하체/코어 | 추천 개수 배분, 부위 선택, 도넛 |
| `level` | 초급/중급/고급 | 후보 필터, 정렬 |
| `unit` | 회/초 | 횟수형/시간형 구분, 타이머 |
| `reps`, `sets`, `rest_sec` | 15, 3, 45 | 기본값 표시용. **루틴의 실제 값은 사용자 난이도로 정한다**(5-2) |
| `joint_load` | 낮음/보통/높음 | BMI 25 이상 제외 규칙 |
| `alternative` | `push_up` | `높음` 운동의 대체 운동 id |
| `met` | 3.8 | 칼로리 |
| `description`, `cautions` | | 운동 화면 |
| `video` | `static/videos/push_up.mp4` | 참고용. 실제 존재 여부는 파일로 확인(9장) |
| `met_source`, `sources` | | 출처 추적. 앱에서는 쓰지 않음 |

현재 데이터: 26개(상체 7, 하체 10, 코어 9). `높음` 3개(clap_push_up → push_up, jump_squat → bodyweight_squat, split_squat_jump → reverse_lunge). 2026-11-23 재검증 때 추가 기준(SOURCES.md 4장)을 통과한 6개를 더했고, 검증 결과는 `research/data_verification.md`에 있다. 이전 20개 버전은 `exercises_v1.json`.

### 4-2. `user.json`

```json
{
  "height_cm": 175,
  "weight_kg": 70,
  "level": "중급",
  "rep_multiplier": 1.0,
  "updated": "2026-11-23"
}
```

- BMI는 저장하지 않고 매번 계산한다(키·몸무게가 바뀌면 자동 반영).
- 파일이 없으면 "처음 사용자"로 보고 `/setup`으로 보낸다(A-4).

### 4-3. `records.json` (기록 목록)

```json
[
  {
    "date": "2026-11-21",
    "started_at": "2026-11-21T19:02:11",
    "completed": true,
    "level": "중급",
    "items": [
      {"id": "push_up", "unit": "회", "reps": 17, "sets_planned": 3, "sets_done": 3, "skipped": false}
    ],
    "minutes": 23.4,
    "calories": 49,
    "feedback": "적당해요"
  }
]
```

- `completed`: 완료 화면까지 갔으면 `true`(중간에 건너뛴 운동이 있어도), [그만하기]를 누르면 `false`.
- `minutes`, `calories`: 실제 수행한 세트로 다시 계산한 값.
- `feedback`: 선택 기능(I-3). 없으면 `null`.
- 하루에 기록이 여러 건이어도 된다. 연속·공백 계산은 **완료한 날짜의 집합**으로 한다.

### 4-4. 진행 중 운동 상태 (Flask `session`)

```python
session["workout"] = {
    "items": [{"id": "push_up", "unit": "회", "reps": 17, "sets": 3, "rest_sec": 45}, ...],
    "i": 0,            # 현재 운동 순서
    "set": 2,          # 현재 세트(1부터)
    "done": [3, 0, 0, 0, 0],   # 운동별 완료 세트 수
    "skipped": [],
    "started_at": "2026-11-23T19:02:11",
}
```

쿠키 한도(4KB)를 넘지 않도록 운동 설명은 넣지 않고 id만 넣는다. 화면에 필요한 이름·설명은 `ExerciseRepo`에서 찾는다.

### 4-5. 날짜 규칙

- 날짜는 `YYYY-MM-DD` 문자열, 실행 PC의 로컬 날짜(`date.today()`)를 쓴다.
- `date.today()`는 **routes에서만** 호출하고, logic에는 `today` 인자로 넘긴다. 그래야 "14일 쉰 상태" 같은 테스트를 날짜 조작 없이 할 수 있다.

---

## 5. 핵심 로직 설계

모든 함수는 순수 함수다. 숫자 기준은 `SOURCES.md` 2장 규칙에서 가져왔다.

### 5-1. `logic/body.py` — BMI (A-3)

```python
def bmi(height_cm: float, weight_kg: float) -> float: ...
def bmi_category(bmi: float) -> str: ...
```

| BMI | 분류 | 비고 |
|---|---|---|
| < 18.5 | 저체중 | |
| 18.5 ≤ BMI < 23 | 정상 | 지침 표기 18.5–22.9 |
| 23 ≤ BMI < 25 | 비만 전단계(과체중) | |
| 25 ≤ BMI < 30 | 1단계 비만 | 관절 부담 규칙 적용 시작 |
| ≥ 30 | 2단계 이상 비만 | |

경계는 "이상/미만"으로 처리한다. 22.95는 정상, 25.0은 1단계 비만이다. 화면에는 소수 첫째 자리까지 표시하되, **분류는 반올림 전 값으로** 한다. 예를 들어 24.96은 화면에 25.0으로 보이지만 분류는 비만 전단계이고, 관절 부담 규칙도 적용되지 않는다. 숫자만 보고 헷갈리지 않게 화면에는 분류명을 항상 같이 보여 준다.

### 5-2. `logic/recommend.py` — 루틴 추천 (C-1~C-5, C-7)

```python
def build_routine(level: str, bmi: float, exercises: list[Exercise],
                  part: str | None = None, multiplier: float = 1.0) -> Routine: ...
def estimate_minutes(items: list[RoutineItem], exercises_by_id: dict) -> float: ...
```

**① 후보 고르기**
- 운동 난이도가 사용자 난이도 **이하**인 것만 후보다(초급=1, 중급=2, 고급=3).

**② 부위별 개수**

| 사용자 난이도 | 상체 | 하체 | 코어 | 합계 |
|---|---|---|---|---|
| 초급 | 1 | 2 | 1 | 4 |
| 중급 | 2 | 2 | 1 | 5 |
| 고급 | 2 | 2 | 2 | 6 |

**③ 부위 안 정렬** (위에서부터 개수만큼 뽑는다)

```python
cands.sort(key=lambda e: (
    e.level != user_level,      # 1) 사용자 난이도와 같은 운동 먼저
    -LEVEL_RANK[e.level],       # 2) 그다음 난이도 높은 순
    -e.met,                     # 3) MET 높은 순
    file_order[e.id],           # 4) 파일 순서 (동점 처리, 결과가 항상 같게)
))
```

**④ 관절 부담 대체** (BMI ≥ 25)
- 뽑힌 운동이 `joint_load == "높음"`이면 그 자리에 `alternative`를 넣는다.
- 대체 운동이 이미 뽑혀 있으면 넣지 않고 다음 후보로 넘어간다(중복 방지).
- 대체가 일어나면 `Routine.substitutions`에 `(원래 id, 대체 id)`를 남겨서 화면에 이유를 보여 준다.

**⑤ 횟수·세트·휴식** — 운동의 기본값이 아니라 **사용자 난이도**로 정한다.

| 사용자 난이도 | 횟수형 | 시간형 | 세트 | 휴식 |
|---|---|---|---|---|
| 초급 | 10회 | 20초 | 2 | 60초 |
| 중급 | 15회 | 30초 | 3 | 45초 |
| 고급 | 20회 | 45초 | 3 | 60초 |
| `높음`(점프) 운동 | 6회 | – | 3 | 90초 |

**⑥ 난이도 배율** (H-1)
- `multiplier`를 횟수형·시간형에 곱하고 **반올림(round_half_up)** 한다. 1보다 크면 최소 +1.
- `높음`(점프) 운동은 배율을 적용하지 않는다(파워 운동은 3–6회 유지, ACSM 2009).
- 예: 중급 15회 × 1.1 = 16.5 → **17회**. 파이썬 `round(16.5)`는 16이므로 쓰면 안 된다.

**⑦ 예상 시간** (C-5)

```
세트 작업시간 = reps × 3초 (횟수형)  또는  reps초 (시간형)
운동별 시간   = sets × (세트 작업시간 + rest_sec)
예상 분       = 합계 ÷ 60  (소수 첫째 자리)
```

**⑧ 부위 선택 모드** (C-7, `part="하체"`)
- 그 부위 후보만 쓰고, 개수는 `min(난이도별 합계, 후보 수)`.
- 예: 초급 + 하체는 후보가 2개뿐이라 2개짜리 루틴이 된다. 화면에 "초급 하체 운동이 2개라 짧은 루틴이에요"라고 알려 준다(15장 열린 결정).

**검증 결과**: 위 ①~⑤, ⑦ 규칙을 그대로 구현해 `routines.json` 15개(BMI 5구간 × 난이도 3)와 비교했더니 **운동 목록, 횟수·세트·휴식, 예상 시간, kg당 칼로리가 15개 모두 일치**했다. 대표 BMI는 17.5 / 21 / 24 / 27.5 / 32를 썼다. 운동을 26개로 늘린 뒤 다시 만든 `routines.json`에도 15/15 일치한다(초급 루틴 5개는 코어가 dead_bug에서 MET가 더 높은 prone_arm_leg_raise로 바뀌었다. 정렬 규칙 ③의 결과다).

### 5-3. `logic/calorie.py` — 칼로리 (E-4)

```python
def kcal_for_items(items, exercises_by_id, weight_kg) -> float:
    # Σ  MET × 3.5 × 체중 ÷ 200 × (완료 세트 × 세트 작업시간 ÷ 60)
```

- 휴식 시간은 넣지 않는다(SOURCES.md 규칙 6, 보수적 추정).
- 완료 화면에는 정수로 표시하고 "추정치"라고 적는다.
- 예: 중급 정상 루틴은 kg당 0.705 → 70kg이면 약 49kcal.

### 5-4. `logic/streak.py` — 공백·연속 일수 (E-2, E-3, F-1)

```python
def completed_dates(records) -> set[date]: ...
def gap_days(records, today: date) -> int: ...       # 기록 없으면 0
def streak_days(records, today: date) -> int: ...
def gap_stage(gap: int) -> str: ...                   # "g0" | "g1" | "g2" | "g3"
```

- `gap_days` = 오늘 − 마지막으로 완료한 날짜. 완료 기록이 없으면 0(첫 사용자는 기본 화면, E-3).
- `streak_days`: 오늘 완료했으면 오늘부터, 아니면 어제부터 거꾸로 이어진 완료 날짜 수. 어제도 비어 있으면 0.
- `gap_stage`: 0~2일 → g0, 3~6일 → g1, 7~13일 → g2, 14일 이상 → g3.

| 테스트 예 (오늘 11-21) | 완료 날짜 | gap | streak | stage |
|---|---|---|---|---|
| 오늘까지 매일 | 17,18,19,20,21 | 0 | 5 | g0 |
| 어제까지 | 17,18,19,20 | 1 | 4 | g0 |
| 3일 쉼 | 18 | 3 | 0 | g1 |
| 기록 없음 | – | 0 | 0 | g0 |
| 2주 쉼 | 11-07 | 14 | 0 | g3 |

### 5-5. `logic/adjust.py` — 난이도 자동 조정 (H-1~H-3)

```python
def next_multiplier(records, current: float) -> tuple[float, str | None]:
    # 반환: (새 배율, 화면에 보여 줄 이유 또는 None)
```

| 조건 (가장 최근 기록 기준) | 결과 | 근거 |
|---|---|---|
| 최근 2건이 모두 `completed` | ×1.1 | ACSM 2009: 2회 연속 목표 초과 시 2–10% 증가 |
| 최근 3건 중 2건 이상 중단 | ×0.9 | 기능명세서 H-2 |
| 그 외 | 유지 | |

- 범위는 0.7~1.3으로 묶는다. 1.3 상한은 팀 판단이다(15장).
- 조정은 **기록이 저장될 때 한 번만** 실행한다. 홈 화면을 열 때마다 계산하면 배율이 계속 올라간다.
- 같은 날 두 번 완료해도 기록 2건으로 센다(단순하게). 막고 싶으면 날짜별 1건으로 묶는다(15장).
- 체감 피드백(I-3)을 쓴다면: "힘들었어요"는 완료여도 증가를 막고, "쉬웠어요" 2번은 증가 조건과 같게 본다.

---

## 6. 저장소 (storage)

```python
def save_json(path: Path, data) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, path)          # 같은 디스크 안에서는 한 번에 바뀐다(중간에 꺼져도 반쪽 파일 없음)

def load_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        backup = path.with_name(f"{path.stem}.broken-{datetime.now():%Y%m%d-%H%M%S}{path.suffix}")
        path.rename(backup)        # 손상된 파일은 지우지 않고 옮겨 둔다
        return default             # 화면에 "기록 파일이 손상돼 새로 시작했어요" 안내
```

- 쓰기는 모듈 수준 `threading.Lock()`으로 감싼다(Flask 개발 서버는 요청을 스레드로 처리한다).
- `RecordRepo.append(record)`는 "읽기 → 추가 → 원자적 저장"을 한 잠금 안에서 한다.
- `ExerciseRepo`는 시작할 때 한 번 읽고 메모리에 둔다(`by_id` 딕셔너리 포함). 관리자 화면에서 영상을 올려도 이 파일은 바뀌지 않는다.

---

## 7. 라우트와 화면 흐름

| 메서드 | 경로 | 화면 | 하는 일 | 쓰는 로직 |
|---|---|---|---|---|
| GET | `/` | S2 홈 | user 없으면 `/setup`으로. 공백 단계·연속 일수·오늘 루틴 미리보기 | streak, recommend |
| GET·POST | `/setup` | S1 | 입력 검증 → user.json 저장 → `/` | body |
| GET | `/routine?part=전신` | S3 | 루틴 생성, 대체·조정 이유 표시 | recommend |
| POST | `/workout/start` | – | 루틴을 session에 저장 → `/workout` | |
| GET | `/workout` | S4 | 현재 운동·세트 표시. 영상 없으면 "영상 준비 중" | |
| POST | `/workout/set-done` | – | 세트 +1. 남았으면 `/rest`, 운동 끝이면 다음 운동, 루틴 끝이면 기록 저장 → `/complete` | calorie, adjust |
| GET | `/rest` | S4 휴식 | 휴식 타이머, 다음 운동 | |
| POST | `/workout/skip` | – | 현재 운동 건너뛰기 | |
| POST | `/workout/stop` | – | `completed=false`로 기록 저장 → `/` | adjust |
| GET | `/complete` | S5 | 방금 저장한 기록 표시 | |
| POST | `/complete/feedback` | – | 체감 저장(선택, I-3) → `/` | |
| GET | `/records?month=2026-11` | S6 | 달력, 목록, 부위별 합계 | streak |
| GET·POST | `/admin/videos` | S7 | 등록 현황, 업로드 | |

**운동 진행 상태 전이** (기능명세서 3장 표와 같다)

```
/routine ──start──▶ /workout ──set-done(세트 남음)──▶ /rest ──타이머 끝/건너뛰기──▶ /workout
                       │  └─set-done(마지막 세트)──▶ 다음 운동 /workout
                       │  └─set-done(루틴 끝)────▶ 기록 저장 ──▶ /complete
                       └─stop──▶ 기록 저장(completed=false) ──▶ /
```

- 모든 POST는 처리 후 **리다이렉트**한다(새로고침으로 세트가 두 번 올라가는 것 방지, PRG 패턴).
- 기록 저장은 `/complete`를 여는 GET이 아니라 **마지막 `set-done` POST에서 한 번만** 한다. 저장 후 `session["workout"]`을 지우고 `session["last_record_id"]`만 남긴다.
- 시간형 운동(플랭크 등)은 `timer.js`가 0초가 되면 `set-done` 폼을 자동 제출한다(D-5).

---

## 8. 화면 구현 (템플릿, 디자인 토큰)

- `base.html`: 공통 `<head>`, 하단 탭, 의학 안내 문구(SR-1). `<body class="stage-{{ stage }}">`로 공백 단계를 넘긴다.
- `macros.html`: 캔버스의 부품을 Jinja 매크로로 만든다. `card()`, `button(kind="primary")`, `segmented(options, selected)`, `chip(text, tone)`, `bear(mood)`, `exercise_row(item)`.
- 곰은 캔버스 `Bear` 컴포넌트의 SVG 5종을 `static/img/bear/{mood}.svg`로 저장해 `<img>`로 쓴다(인라인 SVG를 복사하면 끝).
- 공백 단계 테마(F-3)는 CSS만으로 처리한다.

```css
/* static/css/tokens.css  (디자인 시스템 v0.6, 팔레트 03 민트 클레이) */
:root {
  --bg: #F0EBEA;          /* 뼈색 바탕 */
  --card: #FFFFFF;
  --text: #111111;        /* 팔레트에 글자색이 없어 추가한 중립색 */
  --text-sub: #5F5856;    /* 흰 카드 6.9, 뼈색 5.8 */
  --brand: #32B291;       /* 틸: 홈 헤더, 휴식 화면. 위 글자는 #111 */
  --cta: #4DFFCF;         /* 네온 민트: 주요 버튼, 재생 버튼. 위 글자는 #111 */
  --mint: #4BE1BB;
  --accent-text: #1C7460; /* 진한 틸: 강조 숫자, 링크 (파생색) */
  --mint-soft: #D8F7EE;   /* 연한 민트 칩 (파생색) */
  --clay: #D1A08A;        /* 클레이: 상체 표시, 장식 */
  --danger: #B42318;
  --radius-card: 24px; --radius-btn: 16px; --radius-sheet: 32px;
  --shadow-card: 0 1px 2px rgba(17,17,17,.04), 0 8px 24px rgba(17,17,17,.07);
  --shadow-cta: 0 10px 22px rgba(50,178,145,.35);
  --font: 'Inter', 'Noto Sans KR', sans-serif;
}
body.stage-g1 .app { filter: saturate(.55); }
body.stage-g3 .app { filter: grayscale(1); }
```

- **흰 글자를 민트·틸 위에 쓰지 않는다**(대비 2.6). 이 규칙은 디자인 시스템 v0.6과 `color-palettes` 스킬에 같은 내용이 있다.
- 폰트는 Google Fonts에서 Inter + Noto Sans KR을 불러온다. Pretendard와 같은 구성이다.

---

## 9. 시범 영상 업로드 (G-1~G-3)

```python
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024     # 넘으면 Flask가 413을 낸다

@app.errorhandler(413)
def too_large(e): ...   # flash("50MB 이하 파일만 올릴 수 있어요") → /admin/videos

# 저장
if exercise_id not in exercise_repo.by_id: abort(404)
if not file.filename.lower().endswith(".mp4"): flash(...); return redirect(...)
file.save(VIDEO_DIR / f"{exercise_id}.mp4")             # 파일 이름은 사용자 입력이 아니라 id로 정한다
```

- 영상 경로는 **규칙(`static/videos/{id}.mp4`)으로 계산**하고, 있는지는 `Path.exists()`로 확인한다. 그러면 업로드 때 `exercises.json`을 다시 쓸 필요가 없다. 기능명세서 G-2의 "video 경로 갱신"을 이 방식으로 바꾸자는 제안이다(15장).
- 확장자만으로는 부족하니, 파일 앞 12바이트에 `ftyp`가 있는지도 확인한다(mp4 시그니처). 표준 라이브러리만으로 된다.
- 업로드한 사용자 파일 이름은 쓰지 않으므로 경로 조작(`../`) 문제가 생기지 않는다.

---

## 10. 예외 처리 (NFR-3, NFR-4)

| 상황 | 동작 | 위치 |
|---|---|---|
| user.json 없음 | `/setup`으로 이동 | routes/home |
| user.json·records.json 손상 | `.broken-날짜` 이름으로 옮기고 기본값으로 시작, 안내 문구 | storage/jsonfile |
| exercises.json 손상·규칙 위반 | **서버 시작 시 중단**하고 무엇이 틀렸는지 출력 | validate.py (create_app) |
| 키·몸무게 숫자 아님, 범위 밖 | 저장하지 않고 폼에 오류 표시(키 100~250, 몸무게 20~300) | routes/setup |
| 영상 파일 없음 | "영상 준비 중" + 동작 설명 | templates/workout |
| 업로드 형식·용량 오류 | 저장하지 않고 이유 표시 | routes/admin |
| session에 운동 상태 없이 `/workout` 접근 | `/routine`으로 이동 | routes/workout |
| 알 수 없는 오류 | 500 화면에 "홈으로" 버튼, 콘솔에 로그 | `errorhandler(500)` |

---

## 11. 테스트

실행: `uv run pytest` (pytest는 `dev` 의존성 그룹. uv가 기본으로 함께 설치한다)

| 파일 | 확인할 것 |
|---|---|
| `test_logic_body.py` | 경계값 18.49 / 18.5 / 22.99 / 23 / 24.99 / 25 / 29.99 / 30 |
| `test_logic_recommend.py` | `routines.json` 15개 정답과 일치(대표 BMI 사용), 대체 중복 방지, 부위 선택 모드, 배율 1.1 → 15회가 17회 |
| `test_logic_calorie.py` | 중급 정상 kg당 0.705, 휴식 제외 |
| `test_logic_streak.py` | 5-4의 표 5개 경우 |
| `test_logic_adjust.py` | 2연속 완료 → 1.1, 3건 중 2건 중단 → 0.9, 하한 0.7·상한 1.3 |
| `test_storage.py` | 손상 파일 백업 후 기본값, 원자적 저장(`tmp_path` 사용) |
| `test_routes.py` | Flask `test_client`로 첫 실행 → /setup, 업로드 51MB → 413, .mov 거부 |

```python
# tests/test_logic_recommend.py 의 핵심
REP_BMI = {"저체중": 17.5, "정상": 21.0, "비만 전단계(과체중)": 24.0, "1단계 비만": 27.5, "2단계 이상 비만": 32.0}

@pytest.mark.parametrize("fx", load_fixtures(), ids=lambda f: f"{f['bmi_category']}-{f['level']}")
def test_matches_reference(fx, exercises):
    routine = build_routine(fx["level"], REP_BMI[fx["bmi_category"]], exercises)
    assert [i.as_dict() for i in routine.items] == fx["exercises"]
    assert estimate_minutes(routine.items, by_id(exercises)) == fx["estimated_minutes"]
```

---

## 12. 실행과 의존성

```toml
# pyproject.toml
[project]
name = "homefit-mate"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["flask>=3.0"]

[dependency-groups]
dev = ["pytest>=8"]
```

```python
# app.py
from homefit import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)
```

- `uv run app.py`가 처음 실행될 때 uv가 가상환경과 Flask를 자동으로 설치한다. 다른 설치 단계는 없다.
- `create_app()`이 하는 일: `data/` 폴더와 `secret_key` 만들기(없으면 `secrets.token_hex(32)`) → exercises.json 검사 → 블루프린트 등록.
- `.gitignore`: `data/user.json`, `data/records.json`, `data/*.broken-*`, `data/secret_key`, `static/videos/*.mp4`(용량), `.venv/`.

---

## 13. 구현 순서 (기획서 일정에 맞춤)

| 기간 | 할 일 | 끝났다는 기준 |
|---|---|---|
| ~11/25 (2주차 남은 기간) | 저장소 뼈대, `pyproject.toml`, `create_app`, storage, `logic/body.py`, exercises.json 복사·검사 | `uv run app.py`로 빈 홈이 뜨고 `uv run pytest`가 돈다 |
| 11/26~12/02 (3주차) | `recommend.py` + 15개 정답 테스트, `/setup`·`/`·`/routine`·`/workout`·`/rest`·`/complete`, 기록 저장, `streak.py`, 공백 단계 테마 | 정보 입력 → 루틴 → 운동 → 완료 → 홈이 끝까지 되고, 날짜를 바꾼 테스트 기록으로 g0~g3이 보인다 |
| 12/03~12/10 (4주차) | `adjust.py`, 칼로리 표시, 타이머, `/records`, `/admin/videos`, 예외 처리 표 전부, 통합 테스트, 발표 | 10장 표의 상황을 하나씩 재현해도 서버가 멈추지 않는다 |

먼저 `logic/`과 테스트를 만들고 화면을 붙이는 순서를 권한다. 화면 없이도 핵심 로직이 맞는지 확인할 수 있고, 세 사람이 동시에 일할 수 있다(강군호: logic, 장선민: 템플릿, 고의찬: 데이터·관리자).

---

## 14. 함정 체크리스트

- **반올림**: `round(16.5) == 16`(은행가 반올림). 횟수 계산은 `math.floor(x + 0.5)`로 만든 `round_half_up()`을 쓴다. 실제로 확인함.
- **오늘 날짜**: logic 안에서 `date.today()`를 부르면 테스트가 날마다 결과가 달라진다. 인자로 받는다.
- **JSON 한글**: `json.dumps(..., ensure_ascii=False)`, 파일은 `encoding="utf-8"`. 윈도우 기본 인코딩(cp949)에 기대지 않는다.
- **리로더**: `debug=True`는 코드를 두 번 실행해 첫 실행 파일을 두 번 만들려 한다. `use_reloader=False`로 끄거나, 만들기 전에 존재 여부를 확인한다.
- **세션 크기**: 쿠키는 4KB. 운동 설명을 세션에 넣지 않는다.
- **새로고침 중복 처리**: POST 뒤에는 항상 리다이렉트.
- **경로**: `pathlib.Path`로만 다룬다. 윈도우 `\`와 맥 `/`를 섞지 않는다.
- **표시 숫자**: BMI는 소수 첫째 자리, 칼로리는 정수, 분은 소수 첫째 자리. 계산은 반올림 전 값으로.

---

## 15. 팀이 정할 것 (열린 결정)

| 항목 | 제안 | 대안 |
|---|---|---|
| 난이도 배율 상한 | 1.3, 도달하면 "한 단계 어려운 운동으로 바꿔 볼까요?" 안내 | 상한 없음 |
| 영상 경로 | 규칙 `static/videos/{id}.mp4`로 계산, exercises.json은 안 씀 | 업로드 때 JSON의 `video` 필드 갱신(기능명세서 G-2 원안) |
| 부위 선택 시 개수 | `min(난이도별 합계, 후보 수)` + 안내 문구 | 세트를 늘려 시간 맞추기 |
| 같은 날 여러 번 완료 | 기록 2건으로 셈 | 날짜별 1건으로 합치기 |
| 체감 피드백(I-3) | 완료 화면에서 선택, 배율 조정에 반영 | 이번 버전에서 제외 |
| 부위별 도넛(기록 화면) | 레퍼런스에서 가져온 제안. 넣는다면 `items`의 part별 세트 합계 | 제외 |
| 건너뛴 운동이 있는 완료 | `completed=true`, `skipped`에 기록 | 하나라도 건너뛰면 `false` |
