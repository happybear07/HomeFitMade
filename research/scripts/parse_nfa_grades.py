"""Parse the adult (19-64) 국민체력100 certification standards from the public NFA page HTML.

usage: python -I -X utf8 parse_nfa_grades.py SAVED_PAGE.html OUT.json
The page (https://nfa.kspo.or.kr/reserve/0/selectMeasureGradeItemListByAgeSe.kspo) is public, no login.
Only numbers are extracted; the HTML itself is not kept in the project.
"""
import html
import json
import re
import sys

src, out = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8', errors='replace').read()
t = re.sub(r'(?is)<(script|style).*?</\1>', ' ', s)
t = html.unescape(re.sub(r'<[^>]+>', ' ', t))
t = re.sub(r'\s+', ' ', t)
start = t.find('성인기(만19세~64세) 인증기준')
end = t.find('어르신기(만65세 이상) 인증기준', start)
seg = t[start:end]

COLS_12 = ['shuttle_run_20m_reps', 'treadmill_step_vo2max_ml_kg_min', 'relative_grip_pct', 'cross_situp_reps',
           'sit_and_reach_cm', 'shuttle_10m_sec', 'reaction_time_sec', 'standing_long_jump_cm', 'air_time_sec']
COLS_3 = COLS_12[:5]
AGES = ['19~24', '25~29', '30~34', '35~39', '40~44', '45~49', '50~54', '55~59', '60~64']

grades = {}
for g in ('1', '2', '3'):
    a = seg.find(f'{g} 등급 페이지')
    b = seg.find(f'{int(g) + 1} 등급', a + 10)
    block = seg[a:b]
    cols = COLS_12 if g in ('1', '2') else COLS_3
    res = {}
    for sex, label in (('남', 'M'), ('여', 'F')):
        i = block.find(f'{sex} 19~24')
        j = block.find(' | ', i) if ' | ' in block[i:] else len(block)
        nxt = block.find('여 19~24', i + 5) if sex == '남' else len(block)
        part = block[i:nxt]
        rows = {}
        for k, age in enumerate(AGES):
            p = part.find(age)
            q = part.find(AGES[k + 1]) if k + 1 < len(AGES) else len(part)
            nums = re.findall(r'\d+(?:\.\d+)?', part[p + len(age):q])
            rows[age] = dict(zip(cols, [float(n) for n in nums[:len(cols)]]))
        res[label] = rows
    grades[g] = res

body_comp_3 = {
    'BMI_range': '18.5 이상 25 미만 (남녀 공통)',
    'body_fat_pct_range': {'M': '7% 초과 27% 미만', 'F': '16% 초과 37% 미만'},
}
doc = {
    'source': '국민체력100 인증기준 (서울올림픽기념국민체육진흥공단)',
    'source_url': 'https://nfa.kspo.or.kr/reserve/0/selectMeasureGradeItemListByAgeSe.kspo',
    'accessed': '2026-11-17',
    'note': '성인기(만19~64세) 1·2·3등급 기준값. 표 값은 해당 등급의 기준(이상/이하 방향은 항목별로 다름: '
            '횟수·거리·VO2max·악력·유연성은 이상, 달리기 시간·반응시간은 이하로 해석). 3등급은 신체조성(BMI·체지방률) 조건 포함. '
            '4등급=심폐지구력과 근력이 3등급 이상, 5등급=심폐지구력 또는 근력이 3등급 이상, 6등급=그 외. '
            '웹 페이지에서 숫자만 추출했으며 이상/이하 방향과 측정 방법은 원문으로 다시 확인해야 함.',
    'columns': {
        'shuttle_run_20m_reps': '20m 왕복오래달리기(회)', 'treadmill_step_vo2max_ml_kg_min': '트레드밀/스텝검사(ml/kg/min)',
        'relative_grip_pct': '상대악력(%)', 'cross_situp_reps': '교차윗몸일으키기(회)',
        'sit_and_reach_cm': '앉아윗몸앞으로굽히기(cm)', 'shuttle_10m_sec': '10m 왕복달리기(초)',
        'reaction_time_sec': '반응시간(초)', 'standing_long_jump_cm': '제자리멀리뛰기(cm)', 'air_time_sec': '체공시간(초)'},
    'grade_3_body_composition': body_comp_3,
    'grades': grades,
}
json.dump(doc, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps(grades['3']['M']['19~24'], ensure_ascii=False), json.dumps(grades['1']['F']['60~64'], ensure_ascii=False))
