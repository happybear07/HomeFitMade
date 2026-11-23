# 홈핏 메이트 데이터 출처와 규칙 (SOURCES.md)

- 작성일·자료 확인일: **2026-11-17** (v1) / **v2 재검증·추가: 2026-11-23** (v1 사본: `SOURCES_v1.md`, `exercises_v1.json`, `routines_v1.json`)
- 대상 파일: `exercises.json`(맨몸운동 26개: v1 20개 + v2 추가 6개), `routines.json`(BMI 5범주 × 난이도 3 = 참조 루틴 15개), `check_data.py`(검사기)
- v2 재검증 결과와 수정 목록 전체: `research/data_verification.md`
- 이 문서는 세 부분으로 나뉩니다. **1. 출처**: 실제로 열어 본 자료와 거기서 가져온 값. **2. 구현 규칙**: 팀원이 그대로 코드로 옮길 수 있는 규칙. **3. 팀 판단**: 출처로 직접 뒷받침되지 않는 값.

> ⚠️ **건강 관련 고지**: BMI는 키와 체중만으로 계산하므로 근육량과 지방량을 구분하지 못합니다(근육이 많은 사람도 '비만'으로 나올 수 있음). 대한비만학회 진단 지침도 BMI와 허리둘레를 함께 보라고 권고합니다. 홈핏 메이트는 일반적인 운동 안내 도구이며 **의학적 진단이나 처방이 아닙니다**. 질환(심혈관·대사·신장 질환, 관절 통증 등)이 있으면 운동 전에 의사와 상담하라는 안내를 앱 화면에 표시해야 합니다.

---

## 1. 출처 목록

`exercises.json`의 `sources` 배열에는 아래 **출처 키**(굵은 대문자)가 들어갑니다. `check_data.py`는 이 키가 이 문서에 있는지 확인합니다.

### COMPENDIUM2024: 2024 성인 신체활동 열량 목록 (MET 값)
- 이름: *2024 Adult Compendium of Physical Activities: A third update of the energy costs of human activities*
- 저자/기관: Herrmann SD, Willis EA, Ainsworth BE 외. *Journal of Sport and Health Science* 2024;13(1):6–12. doi:10.1016/j.jshs.2023.10.010
- 연도: 2024
- URL(실제 열람):
  - https://pacompendium.com/conditioning-exercise/ (Conditioning Exercise 대분류 코드표)
  - https://pmc.ncbi.nlm.nih.gov/articles/PMC10818145/ (논문 본문)
  - https://pacompendium.com/unite-conversions (단위 변환 공식)
- 확인일: 2026-11-17
- 가져온 값:
  - 사용한 코드와 MET(코드표 원문 그대로):

    | 코드 | MET | 원문 설명 | 사용한 운동 |
    |---|---|---|---|
    | 02020 | 7.5 | Calisthenics (e.g., pushups, sit ups, pull-ups, jumping jacks, burpees, battling ropes), vigorous effort | clap_push_up, jump_squat, split_squat_jump, mountain_climber |
    | 02022 | 3.8 | Calisthenics (e.g., pushups, sit ups, pull-ups, lunges), moderate effort | push_up, chair_dip, reverse_lunge, v_up |
    | 02024 | 2.8 | Calisthenics (e.g., curl ups, abdominal crunches, plank), light effort | crunch, plank, side_plank, dead_bug |
    | 02030 | 3.5 | Calisthenics, light or moderate effort, general (e.g., back exercises), going up & down from floor | bird_dog |
    | 02056 | 3.0 | Body weight resistance exercises (e.g., squat, lunge, push-up, crunch), general | wall_push_up, knee_push_up, bodyweight_squat, glute_bridge, wall_sit |
    | 02057 | 6.5 | Body weight resistance exercises (e.g., squat, lunge, push-up, crunch), high intensity | pike_push_up, bulgarian_split_squat |
    | 02214 | 11.0 | High intensity interval exercise, burpees, mountain climbers, squat jumps, Tabata, vigorous effort | **사용하지 않음** (아래 '팀 판단' 참고) |

  - MET 정의: 1 MET = 안정 시 산소섭취량 3.5 mL/kg/분(약 1.0 kcal/kg/시간). 논문 본문에서 확인.
  - 열량 공식: 단위 변환 페이지의 "METS × 3.5 × 체중(kg) ÷ 200 = kcal/분".
  - 한계(논문 본문): Compendium 값은 개인의 정확한 에너지 소비량이 아니라 출발점 수준의 추정치라고 명시되어 있습니다.
  - **v2 재확인(2026-11-23, 코드표 HTML 저장: `raw/verify/compendium_conditioning.html`, 행 목록 `raw/verify/compendium_conditioning_rows.txt`)**: 위 7개 코드의 MET 값과 설명이 코드표와 글자 그대로 일치합니다. 코드표 하단 문구는 "빨간색 코드는 추정값이고 나머지는 발표된 문헌으로 뒷받침된다"는 뜻이며, HTML에서 빨간색(`color:#b80000`)으로 표시된 코드는 02090, 02135, 02143, 02160뿐입니다. 따라서 **우리가 쓰는 코드(02020, 02022, 02024, 02030, 02056, 02057)는 모두 문헌 기반 값**입니다(v1의 "확인하지 못함"을 정정).
  - v2 추가 운동이 쓰는 코드도 위 표 안에 있습니다: 02030(prone_y_t_raise, prone_arm_leg_raise), 02056(wall_calf_raise, single_leg_glute_bridge, single_leg_rdl), 02024(lying_leg_raise). 모두 "근사 매핑"입니다.
  - 참고로 같은 표에 02340 Sit to stand exercise, 6-12 times/min = 2.8, 02344 Sit to stand exercise, 18-24 times/min = 4.0이 있습니다(의자 앉았다 일어서기 후보 검토에 사용, 최종적으로 추가하지 않음).
  - **표준 MET의 한계**(https://pacompendium.com/corrected-mets/ , 2026-11-23 열람): 1 MET = 3.5 mL/kg/분은 표준값이며, 체질량이 크거나 나이가 많은 사람은 Harris-Benedict 식으로 보정한 'corrected MET'가 더 높게 나올 수 있다고 설명합니다. 개인 처방에는 보정값을, 집단 비교에는 표준값을 쓰라고 합니다. 앱은 표준 MET를 씁니다(팀 판단, 화면에 "추정치" 표시 권장).

### ACSM2009: ACSM 저항운동 진행 모델 공식 입장문 (난이도별 반복·세트·휴식)
- 이름: *American College of Sports Medicine Position Stand: Progression Models in Resistance Training for Healthy Adults*
- 저자/기관: Ratamess NA, Alvar BA, Evetoch TK, Housh TJ, Kibler WB, Kraemer WJ, Triplett NT / American College of Sports Medicine. *Medicine & Science in Sports & Exercise* 2009;41(3):687–708. doi:10.1249/MSS.0b013e3181915670
- 연도: 2009
- URL(실제 열람): https://sfu.ca/~ryand/kin343/ACSMresistance.pdf (대학 강의용 PDF 사본. 학술지 페이지 https://journals.lww.com/acsm-msse/fulltext/2009/03000/progression_models_in_resistance_training_for.26.aspx 는 결제 요구(HTTP 402)로 열리지 않았고, PubMed 페이지는 자동 접근이 차단됨)
- 확인일: 2026-11-17
- 가져온 값(요약 및 Table 2):
  - 대상 정의: 초보자 = 저항운동 경험이 없거나 수년간 쉬었던 사람, 중급 = 약 6개월 꾸준히 운동한 사람, 고급 = 수년간 운동한 사람.
  - 초보자는 운동당 **1–3세트**(근거등급 A). 중급·고급은 다세트로 진행(A).
  - 근비대: 초보·중급은 8–12회 × 1–3세트, 휴식 **1–2분**(C).
  - **국소 근지구력(맨몸운동 볼륨의 주 근거)**: 초보·중급은 가벼운 부하로 **10–15회**(A). 고급은 다세트 **10–25회 이상**(C). 휴식은 15–20회 이상 세트에 **1–2분**, 10–15회 세트에 **1분 미만**(C).
  - 파워(점프류): 운동당 1–3세트, 3–6회, 실패 지점까지 하지 않음(A). 강도가 낮은 보조 운동은 휴식 1–2분.
  - 반복 속도: 초보는 느리거나 보통 속도, 보통 속도 = 단축성 1–2초 + 신장성 1–2초.
  - 빈도: 전신 운동 기준 초보 주 2–3회, 중급 주 3–4회, 고급 주 4–5회(근지구력은 중급 전신 주 3회).
  - 진행: 목표 횟수보다 1–2회 더 할 수 있으면 부하를 높임(맨몸운동에서는 더 어려운 변형으로 바꾸는 근거로 사용).
  - 운동 순서: 큰 근육군 운동을 작은 근육군보다 먼저, 다관절 운동을 단관절보다 먼저.
  - **v2 재확인(2026-11-23, 같은 PDF를 `raw/verify/acsm2009_progression.pdf`로 받아 본문·Table 2 대조)**: 위 값은 대부분 원문과 일치합니다. 다만 다음 두 가지를 정정합니다.
    1. "중급·고급은 다세트로 진행(A)": Table 2에는 A로, 본문 근거 문단에는 **B**로 적혀 있어 원문 안에서 등급이 다릅니다.
    2. 파워 운동 휴식: 원문은 "강도가 높을 때 핵심 운동은 세트 사이 **최소 2–3분**, 보조 운동이나 강도가 낮은 운동은 1–2분"이며 근거 등급은 **D**(가장 낮음)입니다. 맨몸 점프는 외부 부하가 0%인 저강도 파워 운동이라 1–2분 쪽(90초)에 해당한다고 본 것은 팀 해석입니다.
    3. 진행 기준은 "목표보다 1–2회 더 할 수 있는 상태가 **연속 2회 운동**에서 나타나면"(B)입니다.

### KSSO2022_DX: 대한비만학회 2022 비만 진료지침, 진단 부분 (BMI 기준)
- 이름: *Diagnosis of Obesity: 2022 Update of Clinical Practice Guidelines for Obesity by the Korean Society for the Study of Obesity*
- 저자/기관: Haam JH, Kim BT, Kim EM, Kwon H, Kang JH, Park JH, Kim KK, Rhee SY, Kim YH, Lee KY / 대한비만학회. *Journal of Obesity & Metabolic Syndrome* 2023;32(2):121–129
- 연도: 2023(진료지침 2022 개정판, 8판)
- URL(실제 열람): https://pmc.ncbi.nlm.nih.gov/articles/PMC10327686/
- 확인일: 2026-11-17
- 가져온 값(Table 2, 한국 성인 BMI 분류, kg/m²):

  | 분류 | BMI |
  |---|---|
  | 저체중 (Underweight) | < 18.5 |
  | 정상 (Normal) | 18.5–22.9 |
  | 비만 전단계 (Pre-obese, 과체중) | 23–24.9 |
  | 1단계 비만 (Class I) | 25–29.9 |
  | 2단계 비만 (Class II) | 30–34.9 |
  | 3단계 비만 (Class III, 고도비만) | ≥ 35 |

  - 앱에서는 2단계와 3단계를 묶어 "2단계 이상 비만(≥30)" 하나로 씁니다(과제 요구사항).
  - **WHO 비교**(같은 논문): WHO는 인종·성별과 관계없이 BMI 25 이상을 과체중, 30 이상을 비만으로 정의합니다. 한국 기준이 더 낮은 이유는 아시아인이 더 낮은 BMI에서 동반질환 위험이 높아지기 때문입니다.
  - 허리둘레 기준: 남성 90cm 이상, 여성 85cm 이상이면 복부비만. BMI와 함께 보도록 권고합니다.
  - v2 재확인(2026-11-23, 학회지 페이지 https://www.jomes.org/journal/view.html?doi=10.7570/jomes23031 , PMC는 자동 접근 차단): 저자, 32(2):121–129, Table 2의 6단계 기준, 허리둘레, WHO 비교(25 과체중·30 비만) 모두 일치. 논문은 WHO 아시아·태평양 지역 기준(과체중 23, 비만 25)을 학회가 채택했다고 설명합니다.

### KSSO2022: 대한비만학회 2022 비만 진료지침, 평가·치료 부분 (운동 권고)
- 이름: *Evaluation and Treatment of Obesity and Its Comorbidities: 2022 Update of Clinical Practice Guidelines for Obesity by the Korean Society for the Study of Obesity*
- 저자/기관: Kim KK, Haam JH, Kim BT 외 / 대한비만학회. *Journal of Obesity & Metabolic Syndrome* 2023;32(1):1–24. doi:10.7570/jomes23016
- 연도: 2023(진료지침 2022)
- URL(실제 열람): https://pmc.ncbi.nlm.nih.gov/articles/PMC10088549
- 확인일: 2026-11-17
- 가져온 값: BMI 25 이상 비만(1단계 25.0–29.9, 2단계 30.0–34.9, 3단계 ≥35.0, 23–24.9 비만 전단계)을 다시 확인했습니다. 체중 감량을 위해 유산소 운동 주 150분 이상(주 3–5회), **큰 근육군 저항운동 주 2–3회**, 유산소와 저항운동 병행을 권고합니다. 심혈관·대사·신장 질환 증상이나 병력이 있으면 의사 상담 후 운동을 시작하라고 합니다.
- 주의: 이 지침에는 비만인을 위한 관절 부담별 운동 선택(저충격 운동) 권고가 **없습니다**. 근골격계 질환(골관절염, 요통 등)은 비만 동반질환으로만 나옵니다.
- v2 재확인(2026-11-23, https://www.jomes.org/journal/view.html?doi=10.7570/jomes23016): 유산소 주 150분 이상·주 3–5일(I, A), 큰 근육군 저항운동 주 2–3회(I, A), 병행 권고(I, A), 의사 상담 권고(R4-1, I, A) 모두 일치. 운동 강도는 "저강도~중강도로 시작"하라는 문장이 있습니다.

### NIDDK: 미국 국립당뇨병·소화기·신장질환연구소, "Staying Active at Any Size"
- 저자/기관: National Institute of Diabetes and Digestive and Kidney Diseases (NIH)
- 연도: 최종 검토 2016년 7월
- URL(실제 열람): https://www.niddk.nih.gov/health-information/weight-management/staying-active-at-any-size
- 확인일: 2026-11-17
- 가져온 내용: 걷기나 수중 운동처럼 부상 가능성이 낮은 활동을 제시하고, 수영·수중 운동이 걷기·춤·자전거보다 관절 부담이 적다고 설명합니다. 비활동적이었다면 천천히 시작하고, 관절·발·발목·다리 통증이 생기면 전문가와 상담하라고 합니다. 의자에서 일어났다 앉기처럼 자기 체중을 이용한 근력운동을 예로 듭니다. → **관절 부담 제외 규칙의 근거(간접)**.

### GMU: 조지메이슨대 교육·인간발달대학 기사 "Exercise tips for reducing risk of injury in obese individuals"
- 저자/기관: George Mason University College of Education and Human Development (Kinesiology 부교수 Charles Robison 인터뷰). 작성자 이름은 나오지 않습니다.
- 연도: 2024(URL 날짜 2024-02-23)
- URL(실제 열람): https://cehd.gmu.edu/features/2024/02/23/exercise-tips-for-reducing-risk-of-injury-in-obese-individuals
- 확인일: 2026-11-17
- 가져온 내용: 비만인은 달리기·조깅·점프 같은 고강도 활동이 관절·힘줄·연골 부상 위험이 크므로 피하고, 저충격 운동을 하라고 권합니다. → **"BMI 25 이상이면 점프(높음) 운동 제외" 규칙의 직접 근거**. 다만 대학 홍보 기사로, 학술 지침보다 근거 수준이 낮습니다.

### ACE_LIB: 미국운동협회(ACE) 운동 라이브러리 (동작 설명·난이도 참고)
- 저자/기관: American Council on Exercise
- 연도: 웹 페이지(연도 표기 없음)
- 확인일: 2026-11-17
- 가져온 값: 각 페이지의 **Difficulty(난이도)**, 단계별 동작 설명, 자세 주의점. 한국어 설명은 이를 참고해 팀이 새로 쓴 문장입니다(번역·복제 아님). ACE 콘텐츠는 저작권이 있으므로 영상·이미지는 쓰지 않고 링크만 참고합니다.

  | 우리 id | ACE 페이지(실제 열람) | ACE 난이도 | 우리 level |
  |---|---|---|---|
  | knee_push_up | https://www.acefitness.org/resources/everyone/exercise-library/13/bent-knee-push-up/ (v2에서 개별 페이지 확인) | Beginner | 초급 |
  | push_up | https://www.acefitness.org/resources/everyone/exercise-library/41/push-up/ | Intermediate | 중급 |
  | bodyweight_squat | https://www.acefitness.org/resources/everyone/exercise-library/135/bodyweight-squat/ | Beginner | 초급 |
  | glute_bridge | https://www.acefitness.org/resources/everyone/exercise-library/49/glute-bridge/ | Beginner | 초급 |
  | jump_squat | https://www.acefitness.org/resources/everyone/exercise-library/116/squat-jumps/ | Beginner | **중급(팀 판단으로 상향)** |
  | split_squat_jump | https://www.acefitness.org/resources/everyone/exercise-library/234/cycled-split-squat-jump/ | Intermediate | **고급(팀 판단으로 상향)** |
  | bulgarian_split_squat | https://www.acefitness.org/resources/everyone/exercise-library/366/bulgarian-split-squat/ (ACE는 벤치·덤벨 사용 버전) | Advanced | 고급 (v2에서 확인, v1의 "찾지 못함" 정정) |
  | reverse_lunge | https://www.acefitness.org/resources/everyone/exercise-library/94/forward-lunge/ (맨몸 포워드 런지). 리버스 런지 페이지 https://www.acefitness.org/resources/everyone/exercise-library/319/reverse-lunge/ 는 바벨 버전 | Intermediate | 중급 |
  | crunch | https://www.acefitness.org/resources/everyone/exercise-library/52/crunch/ | Beginner | 초급 |
  | dead_bug | https://www.acefitness.org/resources/everyone/exercise-library/147/supine-dead-bug/ (v2에서 라이브러리 페이지 확인. v1은 ACE 교육 기사 인용) | Beginner | 초급 |
  | plank | https://www.acefitness.org/resources/everyone/exercise-library/32/front-plank/ | Intermediate | 중급 |
  | side_plank | https://www.acefitness.org/resources/everyone/exercise-library/101/side-plank-with-straight-leg/ | Intermediate | 중급 |
  | bird_dog | https://www.acefitness.org/resources/everyone/exercise-library/14/bird-dog/ | Intermediate | 중급 |
  | mountain_climber | https://www.acefitness.org/resources/everyone/exercise-library/258/mountain-climbers/ | Advanced | 고급 |

  - ACE의 마운틴 클라이머는 양발이 잠깐 공중에 뜨는 변형입니다. 우리는 발을 번갈아 당기는(공중에 뜨지 않는) 일반형을 설명했고, 그래서 관절 부담을 '보통'으로 두었습니다.
  - **v2 추가 운동(2026-11-23 열람)**:

    | 우리 id | ACE 페이지 | ACE 난이도 | 우리 level |
    |---|---|---|---|
    | prone_y_t_raise | https://www.acefitness.org/resources/everyone/exercise-library/249/prone-scapular-shoulder-stabilization-series-i-y-t-w-o-formation/ (I·Y·T·W·O 시리즈 중 Y·T만 사용) | Intermediate | 중급 |
    | wall_calf_raise | https://www.acefitness.org/resources/everyone/exercise-library/73/standing-calf-raises-wall/ | Beginner | 초급 |
    | single_leg_glute_bridge | https://www.acefitness.org/resources/everyone/exercise-library/145/glute-bridge-single-leg-progression/ | Intermediate | 중급 |
    | single_leg_rdl | https://www.acefitness.org/resources/everyone/exercise-library/329/single-leg-romanian-deadlift/ (No Equipment) | Advanced | 고급 |
    | prone_arm_leg_raise | https://www.acefitness.org/resources/everyone/exercise-library/53/contralateral-limb-raises/ (같은 목록의 양팔·양다리 버전 https://www.acefitness.org/resources/everyone/exercise-library/9/supermans/ 도 Beginner) | Beginner | 초급 |

  - **v2 정정**: v1은 bulgarian_split_squat와 v_up의 ACE 난이도를 "찾지 못함"이라 했지만 둘 다 페이지가 있습니다. 불가리안(Advanced)은 위 표에 반영했습니다. V-up 페이지 https://www.acefitness.org/resources/everyone/exercise-library/242/v-ups/ 는 **Intermediate**이지만, 앉은 자세에서 팔꿈치로 지지하고 다리를 드는 단계별 변형 시리즈라 우리 v_up(누운 자세에서 팔다리를 동시에 들어 올리는 잭나이프형)과 동작이 다릅니다. 그래서 v_up의 '고급'은 팀 판단으로 유지합니다.
  - 그 밖의 운동(chair_dip, pike_push_up, clap_push_up, wall_sit)은 ACE 무장비 목록 102개(`raw/verify/ace_noequip_all.tsv`)와 사이트맵에서 페이지를 찾지 못해 level이 **팀 판단**입니다. wall_push_up은 아래 NIA_WTG(운동을 처음 시작하는 사람용 예시 운동)로 '초급'을 간접 확인했습니다.
  - ACE 마운틴 클라이머의 부위 표기는 Butt/Hips, Full Body, Legs - Thighs입니다. 우리가 '코어'로 둔 것은 팀 판단입니다.

### MCST_NFA: 국민체력100 운동 동영상 가이드 소개 기사 (시연 영상 후보)
- 이름: 「집에서 가만히 '확찐자' 될 거야? <국민체육진흥공단 '국민체력 100' 운동 동영상 가이드>」
- 저자/기관: 문화체육관광부 대학생기자단(문화체육관광부 누리집)
- 연도: 2020-04-06
- URL(실제 열람): https://www.mcst.go.kr/site/s_policy/comm/studentNews/studentNewsView.jsp?pSeq=5200
- 확인일: 2026-11-17
- 가져온 내용: 국민체력100 누리집(국민체육진흥공단 운영)에 '부위별 운동영상', '체력항목별 운동영상', '목적별 운동루틴 영상' 메뉴가 있었고, 기사 시점의 영상 목록 주소는 `http://nfa.kspo.or.kr/front/movie/movieTypeList.do` 입니다. 이 기사는 **공공누리 제3유형(출처표시 + 변경금지)** 으로 표시되어 있습니다.
- **확인하지 못한 것**: 2026-11-17에 위 영상 목록 주소를 열자 "요청하신 페이지의 사용권한이 없습니다."라는 안내만 나왔습니다. 현재 국민체력100 첫 화면(https://nfa.kspo.or.kr/)은 예약 안내 페이지로 넘어가며, 자동 도구로는 영상 메뉴까지 들어갈 수 없어 **운동별 영상 URL을 기록하지 못했습니다**. 팀원이 브라우저로 직접 들어가 메뉴와 영상별 URL, 그리고 각 영상의 공공누리 유형을 확인해야 합니다. 제3유형이면 출처를 밝히고 **편집·자르기 없이** 링크하거나 임베드만 할 수 있습니다.

### PAG2018: 미국인 신체활동 지침 2판 (관절 부담 규칙의 정부 근거)
- 이름: *Physical Activity Guidelines for Americans, 2nd edition*
- 저자/기관: U.S. Department of Health and Human Services (HHS)
- 연도: 2018
- URL(실제 열람): https://odphp.health.gov/sites/default/files/2019-09/Physical_Activity_Guidelines_2nd_edition.pdf (저장: `raw/verify/pag_2nd_edition.pdf`)
- 확인일: 2026-11-23
- 가져온 내용:
  - 7장 "Active and Safe"(89쪽): 부상 위험을 줄이려면 알맞은 종류의 활동을 고르라고 하며, 가장 안전한 활동은 중강도·저충격·비접촉 활동이라고 합니다. 걷기(저충격)는 달리기(고충격)의 부상 위험의 3분의 1 이하라고 설명합니다.
  - 같은 장(90쪽): 부상 위험은 평소 활동량과 새 활동량의 차이에 비례하므로 점진적으로 늘리라고 하고, 체력이 낮은 성인은 더 천천히 늘려야 하며 **"이 안내는 과체중·비만 성인에게 특히 해당된다"**고 적습니다.
  - 6장(83쪽): 골관절염이 있으면 저충격·통증 없음·관절 부상 위험이 낮은 활동을 권하며, 많은 근력운동이 이런 예라고 합니다.
- 의미: "BMI 25 이상이면 점프·착지 운동을 빼는" 규칙 4의 **방향**을 정부 지침으로 뒷받침합니다. 다만 BMI 숫자 경계나 '점프 금지'를 직접 정하지는 않습니다.

### MESSIER2005: 체중과 무릎 관절 하중 (동료심사 논문)
- 이름: Messier SP, Gutekunst DJ, Davis C, DeVita P. *Weight loss reduces knee-joint loads in overweight and obese older adults with knee osteoarthritis.* Arthritis & Rheumatism 2005;52(7):2026–2032. doi:10.1002/art.21139 (PMID 15986358)
- URL(실제 열람): NCBI E-utilities 초록 https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=15986358&rettype=abstract&retmode=text (PubMed 웹페이지는 자동 접근 시 쿠키 확인 화면만 나옴)
- 확인일: 2026-11-23
- 가져온 내용(초록): 과체중·비만 무릎 골관절염 노인 142명의 보행 분석에서 체중 1 kg 감소가 무릎 압박력 약 40.6 N 감소와 연관되어, 체중 1단위당 무릎 하중이 약 4단위 줄었다고 보고합니다. → 체중이 클수록 같은 동작에서 무릎 하중이 커진다는 **생체역학적 근거(간접)**. 대상이 무릎 골관절염 노인이고 걷기 동작이라 점프에 그대로 적용할 수는 없습니다.

### KDCA_PA2023: 질병관리청 보도자료 + 보건복지부 「한국인을 위한 신체활동 지침」
- 이름: 「야외활동하기 딱 좋은 가을, 적당한 운동으로 비만을 예방하세요」 (붙임 3: 한국인을 위한 신체활동 지침, 자료출처 보건복지부)
- 저자/기관: 질병관리청, 2023-10-18 보도
- 파일: `raw/nfa_docs/kdca_20231019_obesity_pa_guideline_press.pdf` (텍스트 추출: `raw/verify/kdca_20231019_press.txt`. 붙임 3은 그림이라 그림을 직접 보고 확인)
- 확인일: 2026-11-23
- 가져온 내용: 성인(만 19–64세) 중강도 유산소 주 150–300분 또는 고강도 75–150분, **근력운동 주 2일 이상**, 근력운동 예로 "팔굽혀 펴기, 턱걸이 등 맨몸 운동". 관절염이 있으면 적은 양부터 시작해 점차 늘리라고 합니다. 본문은 지역별 비만율(자가보고 BMI 25 이상) 통계입니다.
- **없는 것**: BMI에 따른 운동 종류 제한이나 점프 운동 제외 권고는 없습니다.

### KDCA_OBESITY: 국가건강정보포털 「비만」
- URL(실제 열람): https://health.kdca.go.kr/healthinfo/biz/health/gnrlzHealthInfo/gnrlzHealthInfo/gnrlzHealthInfoView.do?cntnts_sn=6694 (등록 2025-04-30, 수정 2026-07-29, 공공누리 제4유형)
- 확인일: 2026-11-23
- 가져온 내용: 유산소 주 150분 이상·주 3–5일, 큰 근육 중심 근력운동 주 2–3회, 둘을 함께 할 것, **개인 체력에 맞춰 저강도부터 시작**해 점차 늘릴 것. 체질량지수 30 이상에서 무릎 골관절염 위험이 약 4배라는 설명이 있습니다. 관절 부담에 따른 운동 선택 권고는 없습니다.

### KDCA_KNEE: 국가건강정보포털 「무릎관절염, 올바로 운동하기」
- URL(실제 열람): https://health.kdca.go.kr/healthinfo/biz/health/gnrlzHealthInfo/gnrlzHealthInfo/gnrlzHealthInfoView.do?cntnts_sn=5969 (등록 2022-07-19, 수정 2026-10-23)
- 확인일: 2026-11-23
- 가져온 내용: 걷기·수영·아쿠아로빅·실내 자전거를 관절 하중이 비교적 적은 운동으로 소개하고, 충격이 큰 구기 종목은 피하라고 합니다. 과체중(비만)을 무릎관절염의 악화 요인으로 꼽습니다. 근력운동 예로 벽에 기대는 월 스쿼트, **벽을 잡고 뒤꿈치 들기**, 누워서 다리 들기(무릎 편 한 다리 들기)를 그림으로 보여 줍니다. → wall_calf_raise의 출처, 관절 부담 규칙의 간접 근거.

### NIA_WTG: 미국 국립노화연구소 「Workout to Go」
- 이름: *Workout to Go: A Sample Exercise Routine from the National Institute on Aging at NIH* (Go4Life), Publication No. 11-4258, 2015년 3월 재인쇄
- URL(실제 열람): https://www.govinfo.gov/content/pkg/GOVPUB-HE20-PURL-gpo62941/pdf/GOVPUB-HE20-PURL-gpo62941.pdf (미국 정부 출판물 사본, 저장: `raw/verify/nia_workout_to_go_govinfo.pdf`). 원래 Go4Life 도메인(go4life.nia.nih.gov)은 2026-11-23에 DNS 조회가 되지 않음
- 확인일: 2026-11-23
- 가져온 내용: "운동을 처음 시작하거나 다시 시작하는 사람"을 위한 예시 루틴. **Wall Push-Up**(팔 길이보다 조금 더 먼 거리에서 어깨 높이로 벽 짚기, 1초 멈춤, 10–15회), **Toe Stand**(의자를 잡고 발끝으로 서기, 10–15회), 운동당 1세트 10–15회를 보여 주고 3세트까지 해 보라고 함. 안전 수칙: 숨 참지 않기, 반동 없이 천천히, 통증이 있으면 멈추기. → wall_push_up의 '초급'과 wall_calf_raise의 간접 근거. 노인 대상 자료라는 점에 주의.

### NFA_RX2025: 국민체력100 운동처방 빈도 (동료심사 논문)
- 이름: Yun HJ, Lee O. *Analysis of Exercise Prescription Status and Patterns by Health and Physical Fitness Level of Korean Adults: Applying Korea National Fitness Award Data.* 한국체육과학회지(Korean Journal of Sport Science) 2025;36(3):288–297. doi:10.24985/kjss.2025.36.3.288. 논문 CC BY-NC 4.0
- URL: https://kjss.sports.re.kr/assets/pdf/948/journal-36-3-288.pdf (저장: `raw/nfa_docs/yun_lee_2025_kjss_36_3_288.pdf`, 텍스트 `raw/nfa_docs/yun_lee_2025.txt`)
- 확인일: 2026-11-23 (저장된 텍스트에서 표 숫자를 다시 대조)
- 가져온 값: 2018.1–2023.4 국민체력100 성인 475,555명, 운동처방 617종. 전체 상위(Table 4): 1 앉았다일어서기 121,244, 2 엎드려버티기 118,648, 3 윗몸올리기 101,289, 5 팔굽혀펴기 78,935, 7 Sit-to-stand with one foot forward 77,198, 8 누워서엉덩이들어올리기 67,770, 13 누워서다리들어올리기 40,206, 14 버피 39,040. 근지구력 미달자 특이 처방(Table 7, n/전체 n): 누워서다리들어올리기 0.440(17,683), 누워서팔다리동시에들어올리기 0.433, 누워서하늘자전거 0.418, 네발기기자세로팔다리들기 0.400, 엎드려서팔다리들기 0.392(13,336). 본문에 한국어 운동명(엎드려서팔다리들기, 누워서다리들어올리기)이 나옵니다.
- 한계: 운동 **종류의 빈도**만 있고 강도·세트·반복·난이도는 없습니다. BMI별 분석도 없습니다. '엎드려서팔다리들기'가 교차(한 팔·반대 다리)인지 양팔·양다리 동시인지는 논문에 설명이 없습니다.

### 열어 보려 했지만 쓰지 못한 자료
- **ExRx.net** (예: https://exrx.net/WeightExercises/Quadriceps/BWSquat): HTTP 403 차단. 대신 ACE 운동 라이브러리를 썼습니다.
- **ACSM Exercise is Medicine 비만 안내문** (https://acsm.org/wp-content/uploads/EIM_Obesity_Flyer_English.pdf): HTTP 403 차단.
- **ACSM's Guidelines for Exercise Testing and Prescription** (11·12판): 유료 서적이라 원문을 확인하지 못했습니다. 그래서 "과체중·비만인에게 저충격 운동"이라는 ACSM 권고는 **직접 인용하지 않았고**, 관절 부담 규칙은 NIDDK와 GMU 자료에 기댑니다.
- **NSCA 자료**: 확인하지 못했습니다.
- **국가건강정보포털 등 한국어 공식 동작 설명**: 검색에서 찾지 못했습니다. 한국어 운동 이름은 국내에서 흔히 쓰는 표기(푸시업, 스쿼트, 플랭크 등)를 팀이 정했습니다.
- (v2, 2026-11-23) ACSM 골관절염 예방 인포그래픽 PDF와 EIM 비만 안내문: 둘 다 HTTP 403. 2024 Compendium 논문 PMC 페이지와 PubMed 웹페이지: 브라우저 확인 화면만 나옴(초록은 NCBI E-utilities로 확인). 국민체력100 영상 목록 주소: 여전히 "사용권한이 없습니다". 국민체력100 운동처방가이드 API(data.go.kr 15108846): 인증키가 필요해 호출하지 않음(체력수준별 처방 난이도 확인 불가).

---

## 2. 구현 규칙 (팀원이 그대로 코드로 옮길 수 있게)

### 규칙 1. BMI 계산과 범주 (출처: KSSO2022_DX, KSSO2022)
```
BMI = 체중(kg) / (키(m) × 키(m))
BMI < 18.5          → "저체중"
18.5 ≤ BMI < 23     → "정상"                (지침 표기 18.5–22.9)
23   ≤ BMI < 25     → "비만 전단계(과체중)"  (23–24.9)
25   ≤ BMI < 30     → "1단계 비만"          (25–29.9)
BMI ≥ 30            → "2단계 이상 비만"      (지침의 2단계 30–34.9 + 3단계 ≥35)
```
지침 표는 소수 첫째 자리까지만 쓰므로(22.9 다음이 23), 경계는 위처럼 "이상/미만"으로 처리합니다. 예를 들어 22.95는 '정상'입니다.

### 규칙 2. 난이도별 반복·세트·휴식 (출처: ACSM2009, 숫자 선택은 팀 판단)
맨몸운동은 무게를 바꿀 수 없으므로 **반복 횟수(근지구력 범위)와 동작 변형**으로 난이도를 조절합니다.

| 사용자 난이도 | 횟수형(회) | 시간형(초) | 세트 | 세트 간 휴식 | ACSM 근거 |
|---|---|---|---|---|---|
| 초급 | 10회 | 20초 | 2 | 60초 | 초보 1–3세트(A), 근지구력 10–15회(A), 초보 휴식 1–2분(C) |
| 중급 | 15회 | 30초 | 3 | 45초 | 다세트로 진행(A), 근지구력 10–15회(A), 10–15회 세트는 휴식 1분 미만(C) |
| 고급 | 20회 | 45초 | 3 | 60초 | 고급 근지구력 10–25회 이상, 다세트(C), 15–20회 이상 세트는 휴식 1–2분(C) |
| 예외: 관절 부담 '높음'(점프·플라이오메트릭) | 6회 | – | 3 | 90초 | 파워 운동 1–3세트, 3–6회, 실패까지 하지 않음(A), 휴식: 보조·저강도 운동 1–2분 / 고강도 핵심 운동 2–3분 이상(D) |

v2 재확인 메모(숫자는 바꾸지 않음): 초급 휴식 60초는 근비대 초보 휴식 1–2분(C)에는 들어가지만, 근지구력 10–15회 세트의 "1분 미만"(C)과는 경계값이라 **부분 일치**입니다. 점프 90초는 맨몸 점프를 '저강도 파워 운동'으로 본 팀 해석일 때만 범위 안입니다.

- 루틴의 reps/sets/rest_sec는 **운동 자체의 level이 아니라 사용자가 고른 난이도**를 따릅니다. 예: 고급 사용자가 중급 운동인 버드독을 하면 20회 × 3세트, 휴식 60초.
- `exercises.json`의 reps/sets/rest_sec 기본값은 "그 운동의 level에 위 표를 적용한 값"입니다.
- 한쪽씩 하는 운동(리버스 런지, 불가리안 스플릿 스쿼트, 데드버그, 버드독, 사이드 플랭크, v2의 한 발 글루트 브릿지, 한 발 루마니안 데드리프트, 엎드려 팔다리 교차 들기)의 reps는 **좌우 합계**입니다. 예: 리버스 런지 15회 ≈ 좌우 7–8회씩, 사이드 플랭크 30초 = 좌우 15초씩.
- 권장 빈도(화면 안내용, ACSM2009, KSSO2022): 초급 주 2–3회, 중급 주 3–4회, 고급 주 4–5회. 체중 감량이 목표라면 KSSO 권고대로 유산소 운동 주 150분 이상을 함께 안내합니다.

### 규칙 3. 후보 운동과 운동 개수 (팀 판단)
1. 후보: `level` 순위가 사용자 난이도 이하인 운동(초급=1, 중급=2, 고급=3). 초급 사용자는 초급 운동만, 고급 사용자는 전부 후보입니다.
2. 부위별 개수:

   | 난이도 | 상체 | 하체 | 코어 | 합계 |
   |---|---|---|---|---|
   | 초급 | 1 | 2 | 1 | 4 |
   | 중급 | 2 | 2 | 1 | 5 |
   | 고급 | 2 | 2 | 2 | 6 |

3. 부위 안의 정렬: ① 사용자 난이도와 같은 level 먼저(level 높은 순), ② MET 높은 순, ③ `exercises.json` 파일 순서. 위에서부터 개수만큼 고릅니다. 참조 루틴은 이 결정적 순서를 따랐고, 실제 앱은 같은 조건을 지키는 한 무작위로 골라도 됩니다.
4. 출력 순서는 상체 → 하체 → 코어입니다.

### 규칙 4. 관절 부담 제외와 대체 (출처: GMU, NIDDK, 대체 매핑은 팀 판단)
- `joint_load`: `낮음` / `보통` / `높음`. **높음 = 점프나 착지 충격이 있는 운동**(jump_squat, split_squat_jump, clap_push_up).
- **BMI ≥ 25(1단계 비만 이상)이면 `joint_load == "높음"` 운동을 고르지 않습니다.** 정렬 순서에서 높음 운동이 나오면 그 자리에 `alternative` 운동을 넣습니다. 대체 운동이 이미 루틴에 있으면 다음 후보로 넘어갑니다.
- `alternative`는 같은 부위이면서 관절 부담이 더 낮은 운동입니다(check_data.py가 검사).

  | 높음 운동 | → 대체 운동 |
  |---|---|
  | 점프 스쿼트 (jump_squat) | 맨몸 스쿼트 (bodyweight_squat, 보통) |
  | 점프 런지 (split_squat_jump) | 리버스 런지 (reverse_lunge, 보통) |
  | 클랩 푸시업 (clap_push_up) | 푸시업 (push_up, 보통) |

- BMI < 25(저체중·정상·비만 전단계)에는 이 제외 규칙을 적용하지 않습니다.
- **v2 근거 보강(규칙은 그대로)**: 미국 HHS 신체활동 지침(PAG2018)은 저충격 활동이 가장 안전하고 체력이 낮은 사람은 더 천천히 늘려야 하며 이는 과체중·비만 성인에게 특히 해당된다고 적습니다. Messier 2005(MESSIER2005)는 체중이 무릎 하중을 약 4배로 키운다는 생체역학 근거입니다. 질병관리청 국가건강정보포털(KDCA_OBESITY, KDCA_KNEE)은 저강도부터 시작하고, 무릎관절염에는 하중이 적은 운동을 하며 충격이 큰 종목을 피하라고 합니다. 대한비만학회 2022(KSSO2022)와 보건복지부 신체활동 지침(KDCA_PA2023)에는 관절 부담별 운동 선택 권고가 없습니다. ACSM의 비만인 운동 안내는 열지 못했습니다(403·유료). **어느 출처도 'BMI 25 이상 → 점프 제외'라는 경계를 직접 정하지 않으므로 경계값은 계속 팀 판단입니다.**

### 규칙 5. 부위 균형 (출처: KSSO2022 '큰 근육군 저항운동', ACSM2009 '주요 근육군·다관절 운동 우선', 개수는 팀 판단)
- 모든 루틴은 상체·하체·코어를 **각각 최소 1개** 포함해야 합니다(규칙 3의 개수표가 이를 보장).

### 규칙 6. 운동 시간과 소모 열량 (출처: COMPENDIUM2024, ACSM2009)
```
1회 동작 시간  = 3초          (ACSM 보통 속도: 단축성 1–2초 + 신장성 1–2초 → 2–4초의 중간값)
세트 작업시간  = reps × 3초 (unit=회)   또는   reps초 (unit=초)
운동별 시간    = sets × (세트 작업시간 + rest_sec)
estimated_minutes = Σ 운동별 시간 ÷ 60        (준비·정리운동 제외)

kcal/분 = MET × 3.5 × 체중(kg) ÷ 200          (pacompendium.com 단위 변환 공식)
루틴 kcal = Σ [ MET_i × 3.5 × 체중 ÷ 200 × (sets_i × 세트 작업시간_i ÷ 60) ]
calories_per_kg = 위 식에서 체중을 뺀 값(= kcal ÷ 체중)
```
- **휴식 시간은 열량 계산에서 뺐습니다**(작업 시간만 계산하는 보수적 추정, 팀 판단).
- 예(정상·초급, 키 170cm·BMI 21 → 60.7kg): 벽 푸시업 3.0 MET × 3.5 × 60.7 ÷ 200 × 1분 = 3.19 kcal. 4개 운동 합계는 약 13.3 kcal입니다(v2 `routines.json`과 같음. v1은 코어가 데드버그(2.8 MET)라 12.5 kcal, v2는 엎드려 팔다리 교차 들기(3.5 MET)로 바뀜).
- 참조 루틴의 calories_per_kg는 위 식의 운동별 합을 소수 셋째 자리로 반올림한 값이고, calorie_example.kcal은 반올림 전 값 × 체중을 소수 첫째 자리로 반올림한 값입니다.
- 고급 루틴은 BMI 25 이상에서 오히려 kcal가 더 높게 나옵니다. 점프 운동(6회)이 대체 운동(20회)으로 바뀌어 작업 시간이 길어지기 때문입니다.

---

## 3. 팀 판단 (근거 없음/추정)

아래 값은 출처에서 **직접 가져오지 않았습니다**. 발표나 보고서에서 "출처 기반"이라고 말하면 안 되는 부분입니다.

1. **운동 선정**: v1 20개는 집에서 기구 없이 할 수 있는 흔한 맨몸운동을 팀이 골랐습니다. v2 추가 6개는 4장의 기준(빈틈·권위 있는 출처·Compendium 코드)을 통과한 것만 넣었습니다. 팀 목표(15~20개)를 넘는 6개는 '확장 후보'이며, 발표 범위를 20개로 줄일 때는 v1 목록(`exercises_v1.json`)을 쓰면 됩니다.
2. **level(초급/중급/고급) 배정**:
   - ACE 난이도를 따른 것: knee_push_up, push_up, bodyweight_squat, glute_bridge, reverse_lunge(포워드 런지 기준), crunch, dead_bug, plank, side_plank, bird_dog, mountain_climber.
   - ACE 난이도보다 **올린 것**: jump_squat(ACE Beginner → 중급), split_squat_jump(ACE Intermediate → 고급). 착지 기술이 필요하고 관절 충격이 커서 올렸습니다. ACE 페이지도 스쿼트와 착지 동작을 먼저 익히라고 합니다.
   - 근거 없이 팀이 정한 것: chair_dip(중급), wall_sit(중급), pike_push_up(고급), clap_push_up(고급), v_up(고급: ACE 'V-ups'는 Intermediate지만 다른 형태의 동작).
   - v2에서 출처를 찾은 것: wall_push_up(초급, NIA_WTG 간접), bulgarian_split_squat(고급, ACE Advanced).
   - v2 추가 운동: ACE 난이도를 따른 것 = prone_y_t_raise, wall_calf_raise, single_leg_glute_bridge, single_leg_rdl, prone_arm_leg_raise. 팀 판단 = lying_leg_raise(중급; 국민체력100 논문에는 난이도가 없음).
3. **joint_load(낮음/보통/높음) 배정 전체**: 어떤 출처도 운동별 관절 부담 등급을 주지 않습니다. 점프·착지 충격이 있으면 '높음', 체중이 무릎이나 손목·어깨에 크게 실리면 '보통', 누워서 하거나 지지면이 넓으면 '낮음'으로 팀이 분류했습니다. 특히 파이크 푸시업(손목·어깨 부담)과 마운틴 클라이머를 '높음'이 아닌 '보통'으로 둔 것은 판단에 따라 달라질 수 있습니다. v2의 single_leg_rdl은 한 다리로 체중을 모두 지탱하므로 같은 기준에 따라 '보통'으로 두었습니다(무릎 굽힘은 작지만 지지면이 좁음).
4. **MET 매핑**: Compendium에는 운동별 전용 코드가 거의 없습니다(push-up, sit-up, lunge, squat, crunch, plank만 예시로 나옴). 각 운동을 동작이 가장 비슷한 예시와 강도(light/moderate/vigorous, general/high intensity)로 매핑한 것은 팀 판단이며, `met_source`에 "전용 코드가 없어 매핑"이라고 적었습니다. 점프 스쿼트와 마운틴 클라이머는 02214(HIIT, 11.0 MET)에 이름이 나오지만, 이 값은 타바타 같은 인터벌 세션 전체의 값이라서 세트와 휴식이 있는 우리 형식에는 02020(7.5)을 골랐습니다. v2 메모: 파이크 푸시업·불가리안 스플릿 스쿼트의 02057(6.5, high intensity)은 푸시업 3.8의 약 1.7배라 열량이 높게 잡혔을 수 있고, 월 싯(정적 자세)을 02056(3.0)에, 플랭크(정적)를 02024(2.8)에 둔 것도 서로 다른 판단입니다. v2 추가 운동의 02030·02056·02024 매핑도 모두 근사입니다. 같은 운동이 여러 코드의 예시에 나오므로(예: push-up은 02020·02022·02056·02057 모두에 있음) 강도 선택이 MET를 결정합니다.
5. **구체적 숫자**: 난이도별 10/15/20회, 20/30/45초, 2/3/3세트, 60/45/60초 휴식, 점프 운동 6회 × 3세트·90초는 ACSM **범위 안에서** 팀이 고른 대표값입니다(범위는 출처 기반, 개별 숫자는 팀 판단). 시간형 운동의 초 수는 출처가 전혀 없습니다(ACE는 플랭크를 "5초 이상" 버티라고만 함).
6. **부위별 운동 개수(4/5/6개)와 하체 2개 배정**: 팀 판단입니다. 큰 근육군 우선이라는 원칙(ACSM, KSSO)을 참고했습니다.
7. **정렬 규칙(같은 level 먼저 → MET 높은 순)**: 팀 판단입니다.
8. **1회 3초, 휴식은 열량에서 제외**: 3초는 ACSM 반복 속도 범위의 중간값이고, 휴식 제외는 보수적으로 추정하려는 팀 판단입니다.
9. **BMI 25를 관절 규칙의 경계로 쓴 것**: 과제 요구사항이자 팀 판단입니다. "비만인은 점프를 피하라"는 GMU 기사와 NIDDK의 저충격 활동 권고가 근거이지만, 어느 출처도 "BMI 25"라는 숫자를 관절 규칙의 경계로 제시하지는 않습니다. 대한비만학회가 BMI 25를 비만 기준으로 쓴다는 점에 맞춘 것입니다.
10. **저체중·정상·비만 전단계의 루틴이 같은 것**: 출처가 이 세 범주에 서로 다른 맨몸운동 구성을 제시하지 않아 같은 규칙을 적용했습니다(칼로리 예시 체중만 다름). 저체중에게 따로 권할 운동이나 영양 관련 내용은 이 데이터의 범위 밖입니다.
11. **칼로리 예시 체중**: 키 170cm에 범주 대표 BMI(17.5/21/24/27.5/32)를 가정해 계산한 값입니다.
12. **한국어 설명·주의사항 문장**: ACE 동작 설명을 참고해 팀이 직접 쓴 문장이며, 공식 한국어 출처 문장이 아닙니다.
13. **video 경로**: `static/videos/{id}.mp4`는 자리표시자입니다. 실제 파일은 없고, 저작권 문제가 없는 영상(예: 국민체력100 공공누리 영상)을 팀이 확인한 뒤 연결해야 합니다.

---

## 4. 운동 추가 기준 (2026-11-23 작성, 추가 작업 전에 먼저 정함)

v2에서 운동을 더하기 전에 아래 기준을 먼저 적었습니다. 후보는 **모든 기준을 통과해야** 추가합니다. 통과하지 못한 후보와 그 이유는 `research/data_verification.md`에 한 줄씩 남깁니다.

### 4-1. 빈틈 분석 (v1 운동 20개 기준)

| 부위 | 초급 | 중급 | 고급 |
|---|---|---|---|
| 상체 | 벽 푸시업(낮음), 무릎 푸시업(낮음) | 푸시업(보통), 의자 딥스(보통) | 파이크 푸시업(보통), 클랩 푸시업(높음) |
| 하체 | 맨몸 스쿼트(보통), 글루트 브릿지(낮음) | 리버스 런지(보통), 월 싯(보통), 점프 스쿼트(높음) | 불가리안 스플릿 스쿼트(보통), 점프 런지(높음) |
| 코어 | 데드버그(낮음), 크런치(낮음) | 플랭크, 사이드 플랭크, 버드독(모두 낮음) | 마운틴 클라이머(보통), 브이업(낮음) |

- **G1 엎드려 하는 등(척추 기립근) 운동이 없음.** 국민체력100에서 근지구력 미달자에게 특이적으로 처방된 '엎드려서팔다리들기'(Yun & Lee 2025, Table 7)도 빠져 있음.
- **G2 당기는/등 위쪽 상체 운동이 없음.** 상체 6개가 모두 미는 동작(푸시업 계열·딥스).
- **G3 관절 부담 '낮음' 선택지가 없는 칸:** 상체 중급·고급, 하체 중급·고급. BMI 25 이상 사용자는 '높음'만 빠지므로 규칙상 문제는 없지만, 무릎·손목 부담을 줄이고 싶은 사용자에게 줄 '낮음' 대안이 없음.
- **G4 엉덩관절 접기(힙 힌지)·종아리 운동이 없음.** 하체 7개가 스쿼트·런지·브릿지 패턴뿐.
- **G5 국민체력100 처방 상위인데 없는 운동:** 한 발 앞으로 두고 앉았다 일어서기(7위), 누워서다리들어올리기(13위, 근지구력 미달 특이 처방 1위), 버피(14위), 엎드려서팔다리들기, 누워서하늘자전거(Yun & Lee 2025, Table 4·7).

### 4-2. 추가 기준

1. **장비·공간**: 벽, 바닥(매트·수건), 튼튼한 의자 말고는 아무 기구도 필요 없고, 약 2 m × 2 m 안에서 할 수 있어야 한다.
2. **권위 있는 출처**: 아래 중 하나 이상에 같은 동작이 나와야 하고 URL을 기록한다. ACE 운동 라이브러리, NSCA·ACSM 자료, 미국 정부 보건기관 자료(NIH/NIA, HHS), 질병관리청·보건복지부 자료, 국민체력100 처방(Yun & Lee 2025), 동료심사 논문. free-exercise-db·wger 같은 공개 데이터셋은 보조 참고로만 쓰고 단독 근거로 인정하지 않는다.
3. **MET 코드**: 2024 Adult Compendium 코드에 매핑하고, 전용 코드가 아니면 `met_source`에 "근사"임을 적는다. 코드표에서 빨간색(추정값) 코드는 피한다.
4. **빈틈**: 4-1의 G1~G5 중 하나 이상을 채워야 한다.
5. **스키마**: 기존 키와 허용 값을 그대로 쓴다. part는 상체/하체/코어 중 하나로 분명히 나눌 수 있어야 한다('전신'은 규칙 3이 고르지 않으므로 제외).
6. **규칙과의 충돌 없음**: 구현 규칙(2장)을 바꾸지 않고 참조 루틴을 다시 만들었을 때, 관절 규칙 위반이 생기거나 한 루틴의 하체가 같은 동작 패턴만으로 채워지거나 점프 운동이 늘어나는 일이 없어야 한다. 바뀌는 루틴은 모두 기록한다.
7. **중복 없음**: 기존 운동과 사실상 같은 동작이면 추가하지 않고, 필요하면 기존 운동의 설명·주의사항에 변형으로 적는다.
8. **level·joint_load**: level은 출처의 난이도를 따르고, 출처에 난이도가 없으면 "팀 판단"으로 적는다. joint_load는 3장 3번의 팀 기준(점프·착지 충격 = 높음, 체중이 무릎·손목·어깨에 크게 실림 = 보통, 누워서·엎드려서 하거나 지지면이 넓음 = 낮음)을 그대로 쓴다.
9. **글**: 한국어 설명·주의사항은 출처 문장을 옮기지 않고 직접 쓴다. joint_load가 '높음'이면 같은 부위·더 낮은 부담의 alternative를 넣는다. video는 `static/videos/{id}.mp4`.
10. **개수**: 이번에는 4~8개만 더하고 전체는 28개를 넘지 않는다(팀 목표 15~20개를 넘는 부분은 '선택 후보'로 설명).
