# 홈핏 메이트 (HomeFit Mate)

공학컴퓨터프로그래밍 기말 프로젝트 · 조: 간장고장고장장 (고의찬, 강군호, 장선민)

키·몸무게(BMI)와 운동 경험으로 집에서 할 맨몸운동 루틴을 추천하고, 운동을 쉰 날이 길어질수록 곰 마스코트와 화면이 바뀌는 로컬 웹앱입니다.

## 실행

[uv](https://docs.astral.sh/uv/)만 있으면 됩니다. 처음 실행할 때 uv가 가상환경과 Flask를 알아서 설치합니다.

```
uv run app.py
```

브라우저에서 http://127.0.0.1:5000 을 엽니다.

테스트:

```
uv run pytest
```

## 핵심 로직은 어디에 있나

| 기능 | 파일 · 함수 |
|---|---|
| BMI 계산·분류 (A-3) | `homefit/logic/body.py` · `bmi()`, `bmi_category()` |
| 루틴 추천·예상 시간 (C-1~C-7) | `homefit/logic/recommend.py` · `build_routine()`, `estimate_minutes()` |
| 칼로리 (E-4) | `homefit/logic/calorie.py` · `kcal_for_items()` |
| 공백 일수·연속 일수·공백 단계 (E-2, E-3, F-1) | `homefit/logic/streak.py` · `gap_days()`, `streak_days()`, `gap_stage()` |
| 난이도 자동 조정 (H-1~H-3) | `homefit/logic/adjust.py` · `next_multiplier()` |

`homefit/logic/`의 파일은 Flask, 파일 입출력, 오늘 날짜를 쓰지 않는 순수 함수입니다. 추천 규칙은 `data/routines.json`의 정답 루틴 15개로 테스트합니다(`tests/test_logic_recommend.py`).

## 폴더

```
app.py                 실행 진입점
homefit/
  logic/               ★ 핵심 로직(순수 함수)
  storage/             JSON 읽기·쓰기(원자적 저장, 손상 파일 복구)
  routes/              화면 전환(홈, 정보 입력, 루틴, 운동·휴식·완료, 기록, 관리자)
  validate.py          시작할 때 exercises.json 검사
templates/, static/    화면(디자인 토큰은 static/css/tokens.css)
data/                  운동 데이터 26개와 출처(SOURCES.md). user.json·records.json은 실행 중 생김
docs/                  아키텍처 설계, 기능명세서
design/                화면 설계 HTML(design/index.html)
research/              운동 데이터 조사·검증 자료
tests/                 pytest
```

자세한 설계는 `docs/architecture.md`에 있습니다.

## 시연 팁

- 홈 주소 뒤에 `?stage=g1`, `g2`, `g3`를 붙이면 운동을 쉰 단계별 화면을 미리 볼 수 있습니다(기록은 바뀌지 않음).
- 시범 영상은 정보 입력 화면 오른쪽 위 **관리자**에서 운동별 mp4(50MB 이하)로 올립니다. 영상은 `static/videos/`에 저장되고 Git에는 올라가지 않습니다.
