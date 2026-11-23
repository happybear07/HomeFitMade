# 공개 운동 데이터셋 조사 (open_datasets.md)

- 조사일: 2026-11-17
- 목적: `exercises.json`(맨몸운동 20개)을 보강할 수 있는 공개·재사용 가능한 운동 데이터와 한국 실제 운동처방 데이터를 찾고, 맨몸운동 부분만 추려 보는 것
- 원칙: 공식 API 문서, 공식 다운로드 버튼, 공개 GitHub raw 파일만 사용했습니다. 로그인, API 키 발급, CAPTCHA 우회는 하지 않았고 robots.txt를 지켰습니다. 요청에 개인정보를 넣지 않았습니다.
- 내려받은 원자료: `raw/<출처>/`(JSON/CSV만). 가공 스크립트: `research/scripts/`(표준 라이브러리만 사용, `python -I`로 실행)
- `exercises.json`, `routines.json`, `check_data.py`, `SOURCES.md`는 **수정하지 않았습니다**.

## 한눈에 보기

| 출처 | 라이선스 | 접근 방법 | 전체 / 맨몸 후보 | 우리 20개와 겹침 | 쓸 만한 필드 |
|---|---|---|---|---|---|
| **국민체력100 측정결과 API** (data.go.kr 15108938) | 이용허락범위 제한 없음 | **API 키 필요**(무료, 자동승인). 명세만 확보 | 개인 측정 기록(건수 미확인) | - | 나이·성별·BMI·체력 측정값 + **`pres_note`(운동처방내용)** |
| **국민체력100 동영상 정보 API** (data.go.kr 15108846) | 공공누리 제1유형(출처표시) | **API 키 필요**(무료, 자동승인). 명세만 확보 | 미확인 | - | 운동처방가이드: 연령대·체력요인·**체력수준**·운동명(한국어)·운동부위·근육명(한/영)·세트·반복·권장주기 |
| **국민체력100 운동처방 빈도 논문** (Yun & Lee, 2025) | 논문 CC BY-NC 4.0 | PDF 공개 | 처방 종류 617개 중 상위 20 + 체력요인별 상위 | 14개 정리 중 8개 겹침 | 한국 성인 47.5만 명에게 실제 처방된 운동 빈도, 한국어 운동명 |
| **국민체력100 인증기준** (nfa.kspo.or.kr) | 공단 누리집(별도 라이선스 표기 없음, 숫자만 인용) | 공개 페이지(로그인 불필요) | 성인 1–3등급 × 성별 × 연령 9구간 | - | 연령·성별별 체력 기준, 3등급의 BMI 조건 |
| 국민체력100 합성 데이터 2종 (data.go.kr 15165476, 15165474) | 이용허락범위 제한 없음 | 공식 다운로드 버튼(로그인 불필요) | 20,000행 / 150,000행 | - | 운동처방 없음 → 우리 용도로는 가치 낮음 |
| **free-exercise-db** (yuhonas) | Unlicense(퍼블릭 도메인) | GitHub raw | 876 / **80** | 13개(우리 id 12종) | primaryMuscles, secondaryMuscles, level, mechanic, force, 단계별 설명 |
| **wger** | 운동 설명 CC-BY-SA 3.0/4.0(항목별), 일부 CC0 / 코드 AGPL-3.0 | GitHub의 공식 fixture 파일 (wger.de API는 robots.txt가 막음) | 872 / **115** | 23개(우리 id 16종) | 주·보조 근육, 카테고리, 설명, 항목별 저작자 |
| ExerciseDB (AscendAPI) | 독점. 저장·대량수집 금지 | RapidAPI 키 필요 | 미조사 | - | **사용 불가** |

두 영어 데이터셋을 합치면 우리 20개 중 **19개**가 대응 항목을 가집니다(V-up만 없음). 그래서 `primary_muscles` 같은 필드를 출처 있는 값으로 채울 수 있습니다.

---

## 1. 국민체력100 / 국민체육진흥공단 데이터 (가장 중요)

### 1-1. 국민체력100 체력인증센터 측정결과 정보 (오픈 API) ★
- 페이지: https://www.data.go.kr/data/15108938/openapi.do
- 제공: 서울올림픽기념국민체육진흥공단 디지털혁신팀. 등록 2022-12-02, 수정 2025-05-19, 활용신청 451건
- 라이선스: **이용허락범위 제한 없음**, 무료
- 접근: **공공데이터포털 회원가입 + 활용신청 후 인증키 필요**(개발계정 자동승인, 하루 10,000건, 한 번에 최대 1,000건). 지시대로 가입·키 발급은 하지 않았고, 페이지에 들어 있는 Swagger 명세만 저장했습니다 → `raw/kspo_datagokr/api_15108938_measure_result_swagger.json`
- 호출 주소: `https://apis.data.go.kr/B551014/SRVC_NFA_TEST_RESULT/TODZ_NFA_TEST_RESULT_NEW`
  - 필수: `serviceKey`, `pageNo`, `numOfRows`, `resultType`(json/xml)
  - 선택 필터: `age_class`(연령대), `age_gbn`(연령구분), `cert_gbn`(상장구분=인증등급), `test_sex`(성별), `starttest_ym`·`endtest_ym`(측정연월 범위)
- 응답 필드(측정 1건 = 1행):
  - 인적 정보: `age_class`, `age_degree`(나이), `age_gbn`, `test_sex`, `test_ym`, `cert_gbn`(등급)
  - 신체: `item_f001` 신장, `item_f002` 체중, `item_f003` 체지방률, `item_f004` 허리둘레, `item_f018` **BMI**, `item_f042` 허리둘레-신장비
  - 체력: 악력(좌/우/상대/절대), `item_f009` 윗몸말아올리기, `item_f019` 교차윗몸일으키기, `item_f012` 앉아윗몸앞으로굽히기, `item_f020` 20m 왕복오래달리기, 트레드밀·스텝검사 VO2max, `item_f022` 제자리멀리뛰기, `item_f023` 의자에앉았다일어서기, `item_f024` 6분걷기 등 약 50개
  - **`pres_note`: 운동처방내용**
- 의미: 한 행에 **BMI·나이·성별·체력 측정값·등급과 그 사람이 받은 운동처방**이 같이 들어 있습니다. 키만 있으면 "BMI 25 이상인 사람에게 실제로 어떤 운동이 처방되었나", "등급별로 처방이 어떻게 다른가"를 직접 집계할 수 있습니다. 이번 조사에서 찾은 자료 중 **BMI·연령·체력에 따른 처방 차이를 실제 한국 데이터로 확인할 수 있는 유일한 공개 경로**입니다.
- 한계(확인 못 함): `pres_note`가 자유 텍스트인지, 운동 목록 코드인지 모릅니다. 전체 건수, 개인 식별 방지 처리 수준, 측정 기간도 키 없이는 확인할 수 없었습니다.
- **팀이 얻는 방법**: 팀원 1명이 data.go.kr에 가입 → 위 페이지에서 [활용신청] → 목적에 "대학 수업 프로젝트(비영리)"를 적으면 개발계정이 자동승인됨 → 마이페이지의 "일반 인증키(Decoding)"로 위 주소를 호출합니다. 인증키는 코드나 저장소에 넣지 말고 `.env` 같은 환경변수로 관리해야 합니다. 앱이 실행 중에 이 API를 부를 필요는 없고, 한 번 집계한 결과(예: 등급별 상위 처방 운동)만 데이터 파일에 출처와 함께 넣는 편이 안전합니다.

### 1-2. 국민체력100 동영상 정보 (오픈 API) ★
- 페이지: https://www.data.go.kr/data/15108846/openapi.do (등록 2022-12-01, 수정 2025-05-19, 활용신청 263건)
- 라이선스: **공공누리 제1유형(출처표시)**, 무료. 키 발급 방식은 1-1과 같음(자동승인, 하루 10,000건)
- 명세 저장: `raw/kspo_datagokr/api_15108846_swagger.json`. 호출 주소: `https://apis.data.go.kr/B551014/SRVC_TODZ_VDO_PKG/<기능>`
- 기능 7개: 체력인증측정방법, 운동처방동영상, 근골격계운동, 생애주기별표준운동, 목적별루틴운동, 전체 동영상 목록, **운동처방가이드(`TODZ_VDO_TRNG_GUIDE_I`)**
- 운동처방가이드 응답 필드: `aggrp_nm` 연령대, `ftns_fctr_nm` 체력요인, **`ftns_lvl_nm` 체력수준**, `trng_nm` 운동명, `tool_nm` 소도구·기구명, `trng_mscl_class`·`trng_mscl_part` 운동부위, `trng_mscl_nm`·`trng_mscl_eng_nm` 근육명(한국어·영어), `trng_hr_nm` 운동시간, `set_cnt_nm` 세트수, `rptt_tcnt_nm` 반복횟수, `ecrg_cycl_nm` 권장주기, `trng_plc_nm` 운동장소 + 영상 URL·설명
- 의미: **공단이 정한 "연령대 × 체력요인 × 체력수준 → 운동·세트·반복" 표**를 공식 한국어 운동명과 함께 받을 수 있는 경로입니다. `tool_nm`이 비어 있거나 "맨몸"인 행만 고르면 우리 데이터의 한국어 이름, 부위, 근육, 세트·반복의 근거로 바로 쓸 수 있습니다. 영상은 팀이 직접 찍으므로 필요 없지만, 동작 확인용으로 영상 URL을 참고할 수 있습니다.
- 한계: 키가 없어 실제 행 수와 `ftns_lvl_nm` 값(예: 1~3등급인지, 상/중/하인지)을 확인하지 못했습니다. 영상 파일 자체의 공공누리 유형은 API 메타데이터와 다를 수 있습니다.

### 1-3. 국민체력100 운동처방 빈도 논문 (공개 PDF) ★ 바로 쓸 수 있는 근거
- Yun HJ, Lee O. *Analysis of Exercise Prescription Status and Patterns by Health and Physical Fitness Level of Korean Adults: Applying Korea National Fitness Award Data.* 한국체육과학회지(Korean Journal of Sport Science) 2025;36(3):288–297. doi:10.24985/kjss.2025.36.3.288 (교신저자 소속 한국스포츠과학원). 논문 라이선스 CC BY-NC 4.0
- 자료: 공단이 연구진에게 **제공한** 2018.1–2023.4 국민체력100 체력측정·운동처방 데이터 1,145,612명 중 성인 475,555명. 운동처방 종류는 617개. 원자료는 공개되지 않았습니다(연구용 제공).
- 정리 파일: `research/candidates_nfa100_prescription.json`(맨몸운동 14개, 기구·유산소 종목은 제외 목록에 따로 기록)
- 주요 결과(논문 표의 숫자):
  - 전체 처방 상위: 1위 **앉았다일어서기** 121,244건, 2위 **엎드려버티기** 118,648, 3위 **윗몸올리기** 101,289, 4위 달리기, 5위 **팔굽혀펴기** 78,935, 7위 **한 발 앞으로 두고 앉았다 일어서기**(Sit-to-stand with one foot forward) 77,198, 8위 **누워서엉덩이들어올리기** 67,770, 13위 **누워서다리들어올리기** 40,206, 14위 **버피** 39,040
  - 체력요인별로 처방이 다름(3등급 기준 미달자 대상, "그 운동을 처방받은 사람 중 미달자 비율"):
    - 근지구력 미달 → 누워서다리들어올리기(0.440), 누워서팔다리동시에들어올리기(0.433), 누워서하늘자전거(0.418), 네발기기자세로팔다리들기(0.400), 엎드려서팔다리들기(0.392): **누워서 하는 코어 운동**
    - 근력 미달(상대악력 기준) → 팔꿈치굽히기, 허리굽혀팔뒤로들기, 물병옆으로들어올리기, 뒤로 팔굽혀펴기: **상체 근력 운동**(물병 같은 소도구 사용)
    - 심폐지구력 미달 → 수영, 계단 오르내리기, 줄넘기 등 유산소
    - 유연성 미달 → 각종 스트레칭
- 한계: 운동 **종류만** 분석했고 강도·빈도·시간(FITT)은 없습니다(논문이 직접 한계로 적음). BMI·비만 여부별 분석은 없습니다. 영문 표기만 있고 한국어 이름이 본문에 없는 운동도 있습니다. 우리가 붙인 "앉았다일어서기=스쿼트" 같은 대응은 이름으로 추정한 것이라 국민체력100 영상으로 확인해야 합니다.

### 1-4. 국민체력100 인증기준 (공개 웹 페이지)
- https://nfa.kspo.or.kr/reserve/0/selectMeasureGradeItemListByAgeSe.kspo (로그인 불필요, robots.txt 허용 경로). 위 논문도 이 기준으로 "체력수준 미달"을 정의했습니다.
- 정리 파일: `research/nfa100_adult_grade_standards.json`(성인 만19–64세, 1·2·3등급 × 남녀 × 5세 단위 9구간)
- 항목: 20m 왕복오래달리기, 트레드밀/스텝 VO2max, 상대악력, **교차윗몸일으키기(회)**, 앉아윗몸앞으로굽히기 (+1·2등급은 민첩성·순발력 항목)
- **3등급은 BMI 18.5 이상 25 미만**, 체지방률 남 7–27%, 여 16–37% 조건이 붙습니다. 4등급 = 심폐지구력과 근력이 3등급 이상, 5등급 = 둘 중 하나가 3등급 이상, 6등급 = 그 외.
- 예: 교차윗몸일으키기 3등급 기준 남 19–24세 42회, 60–64세 19회 / 여 19–24세 23회, 60–64세 7회
- 한계: 웹 페이지 표에서 숫자만 뽑았습니다. 기준이 "이상"인지 "이하"인지, 측정 시간(예: 교차윗몸일으키기 60초)은 원문에서 다시 확인해야 합니다. 원본 HTML은 프로젝트에 저장하지 않았습니다.

### 1-5. 국민체력100 합성 데이터 2종 (파일 다운로드)
- 간소화 체력측정 결과(합성) https://www.data.go.kr/data/15165476/fileData.do → `raw/kspo_datagokr/datagokr_15165476.csv` (20,000행; 성별, 나이 10–95세, 혈압, 신장, 체중, 악력, 심박수, 8자보행, 근력, VO2max. 계산한 BMI 평균 23.9)
- 체력측정 참여 현황(합성) https://www.data.go.kr/data/15165474/fileData.do → `raw/kspo_datagokr/datagokr_15165474.csv` (150,000행; 측정구분, 나이, 성별, 측정일, 센터코드, 연령구분, 참여구분)
- 둘 다 2026-09-15 등록, **이용허락범위 제한 없음**, "로그인 없이 다운로드" 가능. 공식 [다운로드] 버튼과 같은 요청 순서를 스크립트(`datagokr_filedownload.py`)로 재현했고, 포털이 CAPTCHA를 요구하면 멈추도록 했습니다(이번에는 요구하지 않음).
- 한계: **실제 회원이 아닌 합성 데이터**이고 **운동처방이 없습니다**. 앱 화면의 "또래 평균과 비교" 같은 부가 기능에나 쓸 수 있습니다.

### 1-6. 그 밖에 확인한 공단 자료
- 측정건수 정보 API(15114286): 센터별 월 측정건수·주소뿐이라 우리 용도와 무관. 명세만 `raw/kspo_datagokr/api_15114286_swagger.json`에 저장
- 검색에 나온 "장애인 체력측정별 운동처방"(data.go.kr 연계데이터 1311104)과 "센터별 체력통계"(845290)는 문화 빅데이터 플랫폼 연계 페이지로, 2026-11-17에 data.go.kr 연계 페이지가 HTTP 500, DCAT 메타데이터 주소가 응답 시간 초과였습니다. 장애인 대상 자료라 우리 범위와도 다릅니다.
- 문화 빅데이터 플랫폼(bigdata-culture.kr): 목록이 자바스크립트로 불러와져 스크립트로는 검색 결과를 볼 수 없었습니다. "체력측정 및 운동처방 종합데이터"라는 이름의 공개 파일은 찾지 못했습니다(논문들은 이 데이터를 공단에서 **제공받았다**고만 씀).

---

## 2. free-exercise-db
- https://github.com/yuhonas/free-exercise-db (별 2,144개, 최근 push 2026-09-27)
- 라이선스: **The Unlicense**(퍼블릭 도메인 헌정). 출처 표시 의무 없음(그래도 SOURCES.md에 적는 것을 권장)
- 접근: GitHub raw `dist/exercises.json` 1개 파일 → `raw/free_exercise_db/exercises.json`(+ `LICENSE.md`, `schema.json`)
- 개수: 전체 876 → 장비 "body only" 111 + 장비 미기재 77 = 188 → 스트레칭 85개, 철봉·운동공·러닝 드릴 등 23개 제외 → **맨몸 후보 80개** (`research/candidates_free_exercise_db.json`)
  - 우리 20개와 같은 운동 13개(우리 id 12종), 가까운 변형 31개, 새 운동 36개
  - 부위: 코어 33, 하체 25, 상체 22 / 난이도: 초급 69, 중급 11
- 쓸 만한 필드: `primaryMuscles`, `secondaryMuscles`, `level`(beginner/intermediate/expert), `mechanic`(compound/isolation), `force`(push/pull/static), 단계별 `instructions`, 이미지(우리는 사용 안 함)
- 한계:
  - 원래 출처가 문서화되어 있지 않습니다(다른 운동 사이트 데이터를 옮긴 것으로 보이나 README에 근거 없음). 퍼블릭 도메인이라 써도 되지만 **"학술 근거"로 인용할 자료는 아닙니다**.
  - 난이도가 우리 기준과 크게 다릅니다. 마운틴 클라이머, 플라이오 푸시업, 스플릿 점프가 모두 beginner, 플랭크도 beginner입니다(우리: 고급, 고급, 고급, 중급). level은 가져오지 않는 편이 낫습니다.
  - 마운틴 클라이머의 주 근육이 quadriceps로 되어 있어 자동 부위 매핑이 우리(코어)와 다릅니다.
  - 한국어 이름이 없습니다.

## 3. wger
- https://wger.de (오픈소스 운동 기록 앱), 코드 https://github.com/wger-project/wger
- 라이선스: **운동 설명은 항목마다 CC-BY-SA 4.0(103개)/3.0(7개)/CC0(5개)**, 각 항목에 `license_author`가 있음. 코드는 AGPL-3.0. CC-BY-SA 항목을 쓰면 **저작자(wger + license_author) 표시와 라이선스 링크가 필요하고, 그 문장을 고쳐 쓴 결과물도 CC-BY-SA로 공개해야 합니다**. 그래서 문장은 가져오지 말고 근육 같은 사실 정보만 참고하는 것을 권장합니다.
- 접근: wger.de의 robots.txt가 `Disallow: /api/v2`(모든 봇)라서 **REST API는 호출하지 않았습니다**. 대신 공식 GitHub 저장소의 데이터 fixture(`wger/exercises/fixtures/*.json`, `wger/core/fixtures/licenses.json`, `languages.json`)를 raw로 받았습니다 → `raw/wger/`
- 개수: 운동 872개(영어 번역 872, **한국어 번역 0**) → 장비가 "none (bodyweight exercise)" 또는 "Gym mat"인 것 243개(장비 미기재 303개는 제외) → 기계·밴드·폼롤러·스트레칭·영어가 아닌 항목 116개, 같은 이름(좌/우, HD 중복) 12개 제외 → **맨몸 후보 115개** (`research/candidates_wger.json`)
  - 우리 20개와 같은 운동 23개(우리 id 16종), 변형 35개, 새 운동 57개
  - 주 근육이 있는 것 83개, 설명이 있는 것 113개. **난이도 정보 없음**
- 한계: 누구나 편집하는 데이터라 품질이 고르지 않습니다. "장비 없음"인데 실제로는 기계나 TRX인 항목, 근육 정보가 이상한 항목(예: Wall Slides의 주 근육에 hamstrings)이 있습니다. 부위는 wger 카테고리(Arms/Legs/Abs…)로 매겼기 때문에 "Hip Raise, Lying"이 '상체(Back)'로 잡히는 등 검토가 필요합니다.

## 4. ExerciseDB (사용 불가)
- AscendAPI가 운영하는 상용 데이터(RapidAPI 키 필요). 이용약관이 **데이터 저장 금지, 매번 API로 새로 요청, 대량 수집 금지**를 명시합니다. GitHub에 있는 "exercisedb-api" 저장소들은 코드만 MIT이고 데이터 출처가 불분명합니다. 우리 프로젝트(정적 JSON 파일)에는 맞지 않아 받지 않았습니다.

---

## 우리 데이터에 반영할 만한 것

### A. 추가할 만한 운동 (8개)
국민체력100 처방 빈도(한국 근거)를 1순위로, 두 공개 데이터셋에 있는지를 2순위로 골랐습니다. level과 joint_load는 **팀 판단 제안**입니다.

| 제안 id | 이름(국민체력100 명칭) | 부위 | 제안 level | 제안 joint_load | 근거 |
|---|---|---|---|---|---|
| split_squat | 스플릿 스쿼트(한 발 앞으로 두고 앉았다 일어서기) | 하체 | 초급~중급 | 보통 | 국민체력100 전체 7위(77,198건). wger `Split squats`(991). 리버스 런지보다 쉬운 단계로 하체 진행을 채움 |
| lying_leg_raise | 레그 레이즈(누워서다리들어올리기) | 코어 | 중급 | 낮음 | 국민체력100 13위, **근지구력 미달자 특이 처방 1위**. wger `Lying Leg Raise`(1313), `Leg Raises, Lying`(377) |
| superman | 슈퍼맨(엎드려서팔다리들기) | 코어(허리) | 초급 | 낮음 | 근지구력 미달자 특이 처방. wger `Superman`(636). 엎드려 하는 등·허리 운동이 지금 데이터에 없음 |
| bicycle_crunch | 바이시클 크런치(누워서하늘자전거) | 코어 | 중급 | 낮음 | 근지구력 미달자 특이 처방. wger `bicycle crunches`(1412), free-exercise-db `Air_Bike`(beginner) |
| burpee | 버피 | 전신(앱에서는 하체 또는 별도 '전신') | 고급 | **높음** | 국민체력100 14위(39,040건). wger `4-count burpees`(997). BMI 25 이상이면 제외 규칙 대상, 대체: 맨몸 스쿼트 |
| incline_push_up | 인클라인 푸시업(책상·의자 짚고) | 상체 | 초급 | 낮음 | free-exercise-db `Incline_Push-Up`(beginner). 벽 푸시업과 무릎 푸시업 사이 단계 |
| single_leg_glute_bridge | 한 발 글루트 브릿지 | 하체 | 중급 | 낮음 | free-exercise-db `Single_Leg_Glute_Bridge`, wger `Single Leg Glute Bridge`(1740). 국민체력100 8위(누워서엉덩이들어올리기)의 진행 단계 |
| calf_raise | 카프 레이즈(발뒤꿈치 들기) | 하체 | 초급 | 낮음 | wger `Double Leg Calf Raise`(1243). 서서 하는 저충격 하체 운동이라 BMI 25 이상 대체 후보로 유용 |

추가로 검토할 것: 리버스 크런치(free-exercise-db `Reverse_Crunch`, wger 1772, 코어 초급), 의자에 앉았다 일어서기(국민체력100 어르신 측정 항목이자 SOURCES.md의 NIDDK 예시, 하체 초급·관절 부담 낮음).

### B. 추가할 만한 필드
1. **`primary_muscles` / `secondary_muscles`**: 두 데이터셋에서 19개 운동의 근육 정보를 출처와 함께 가져올 수 있습니다. 예(free-exercise-db 기준, 없으면 wger):
   - push_up: 주 chest / 보조 shoulders, triceps · chair_dip: triceps / chest, shoulders · bodyweight_squat: quadriceps / glutes, hamstrings · glute_bridge: glutes / hamstrings · jump_squat: quadriceps / calves, glutes, hamstrings · crunch, plank, dead_bug, side_plank: abdominals · bird_dog: abdominals / shoulders, glutes(wger 1572) · wall_sit: quadriceps, hamstrings(wger 718) · pike_push_up: wger는 chest로 적었으나 일반적으로 어깨 운동이라 팀 검토 필요
   - 근육 이름은 영어 그대로 두고 화면용 한국어(가슴, 삼두, 대퇴사두 등)는 팀이 매핑하면 됩니다. 국민체력100 동영상 API의 `trng_mscl_nm`(한국어 근육명)을 받으면 공식 표기로 맞출 수 있습니다.
2. **`mechanic`**(compound/isolation): free-exercise-db에 있음. ACSM2009의 "다관절 운동 먼저" 순서 규칙을 코드로 구현할 때 근거 필드가 됩니다.
3. **`name_nfa`**(국민체력100 명칭): 앉았다일어서기, 엎드려버티기, 윗몸올리기, 팔굽혀펴기, 누워서엉덩이들어올리기, 네발기기자세로팔다리들기 등. 화면에 "국민체력100 명칭"으로 같이 보여 주면 한국 공식 처방과 연결된다는 점을 보여 줄 수 있습니다.
4. **`refs`**(교차 참조 id): `{"free_exercise_db": "Pushups", "wger": 1551}`처럼 적어 두면 데이터 추적성이 생깁니다.
5. **`nfa_prescription_rank`**(선택): 국민체력100 처방 빈도 순위. 같은 조건의 후보 중 "한국에서 더 많이 처방된 운동"을 먼저 고르는 정렬 기준으로 쓸 수 있습니다(지금 규칙 3의 MET 정렬을 대신하거나 보완).

### C. BMI·연령·체력수준으로 루틴을 나눌 근거가 있는가
- **체력수준·연령: 근거 있음.**
  - 국민체력100은 연령·성별별 등급 기준을 공개합니다(`nfa100_adult_grade_standards.json`). 공단의 운동처방가이드 API도 `연령대 × 체력요인 × 체력수준`으로 운동을 나눕니다(명세로 확인, 내용은 키가 필요).
  - Yun & Lee(2025)는 47.5만 명의 실제 처방에서 **부족한 체력요인에 따라 처방 운동이 달라진다**는 것을 보여 줍니다(근지구력 부족 → 누워서 하는 코어 운동, 근력 부족 → 상체 근력 운동, 심폐 부족 → 유산소).
  - 앱 아이디어: 사용자가 집에서 교차윗몸일으키기 같은 항목을 스스로 측정해 입력하면 연령·성별 기준과 비교해 초급/중급/고급을 추천할 수 있습니다. 다만 측정 방법을 화면에서 정확히 안내해야 하고, 결과는 공식 인증이 아니라는 고지가 필요합니다.
- **BMI: 직접 근거 없음.**
  - 공개된 자료 중 "BMI 구간별로 처방 운동이 다르다"를 보여 주는 것은 없습니다. 국민체력100은 BMI를 3등급 **조건**으로 쓸 뿐입니다(18.5–25).
  - 위 논문의 "심폐지구력 부족 → 수영"이 비만인의 관절 부담과 관련 있다는 설명은 논문 저자의 해석(논의)이라 간접 근거에 그칩니다.
  - **측정결과 API(1-1)의 `pres_note` + `item_f018`(BMI)을 집계하면 직접 확인할 수 있습니다.** 팀원이 키를 받아 예를 들어 BMI 25 미만 / 25 이상별 처방 상위 운동을 비교하면, 지금 "BMI 25 이상이면 점프 운동 제외" 규칙(규칙 4)을 한국 실제 데이터로 뒷받침하거나 수정할 수 있습니다.

---

## 확인 못 한 것
1. 측정결과 API `pres_note`의 실제 형식(자유 텍스트? 운동 목록?)과 전체 행 수, 기간. API 키가 필요해 호출하지 않았습니다.
2. 동영상 API 운동처방가이드의 실제 내용(`ftns_lvl_nm` 값, 맨몸운동 행 수, 세트·반복 값). 같은 이유입니다.
3. 국민체력100 처방 운동명과 일반 운동명의 정확한 대응(예: "윗몸올리기"가 크런치인지 싯업인지, "Backward push-up"이 의자 딥스인지, "Standing upper body raise"가 무엇인지). 국민체력100 영상으로 확인해야 합니다.
4. 인증기준 표의 기준 방향(이상/이하)과 측정 시간·방법. 웹 페이지 숫자만 뽑았습니다.
5. 문화 빅데이터 플랫폼(bigdata-culture.kr)의 공단 데이터 상품 목록. 자바스크립트로 불러와져 스크립트로 볼 수 없었고, data.go.kr의 연계 페이지(845290, 1311104)는 HTTP 500 또는 응답 시간 초과였습니다.
6. free-exercise-db의 원래 데이터 출처(README에 없음).
7. wger.de 실시간 API의 최신 데이터. robots.txt 때문에 GitHub fixture(마지막 수정 2026-04 무렵)를 썼으므로 웹사이트와 조금 다를 수 있습니다.
8. 국민체력100 영상 각각의 공공누리 유형(API 메타데이터는 제1유형이지만 기존 SOURCES.md의 소개 기사는 제3유형).
9. ExerciseDB는 라이선스 때문에 데이터를 받지 않았습니다.
10. 처방 운동명 일부의 한국어 표기(논문 본문에 영문만 있는 것: Sit-to-stand with one foot forward, Backward push-up, Standing upper body raise).

## 파일 목록
- `research/candidates_free_exercise_db.json`: 맨몸 후보 80개(정규화 필드 + `in_our_data`, `overlap`, `not_in_our_data_ids`)
- `research/candidates_wger.json`: 맨몸 후보 115개(항목별 라이선스·저작자 포함)
- `research/candidates_nfa100_prescription.json`: 국민체력100 처방 빈도 중 맨몸운동 14개
- `research/nfa100_adult_grade_standards.json`: 국민체력100 성인 인증기준(1–3등급)
- `raw/free_exercise_db/`, `raw/wger/`, `raw/kspo_datagokr/`: 원자료(JSON/CSV)와 API 명세
- `research/scripts/`: 가공 스크립트(`build_candidates.py`, `parse_nfa_grades.py`, `datagokr_filedownload.py`, `extract_swagger.py`, `search_datagokr.py` 외)
