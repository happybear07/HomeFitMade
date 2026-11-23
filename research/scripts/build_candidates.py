"""Build normalized bodyweight-exercise candidate files from raw open datasets.

Run from anywhere with:  python -I -X utf8 build_candidates.py
Reads (untrusted, parsed as plain JSON only):
  raw/free_exercise_db/exercises.json   (yuhonas/free-exercise-db, Unlicense)
  raw/wger/*.json                       (wger-project/wger fixtures, CC-BY-SA per exercise)
  exercises.json                        (our own 20 exercises; read only)
Writes:
  research/candidates_free_exercise_db.json
  research/candidates_wger.json
"""
import html
import json
import os
import re

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
RAW = os.path.join(BASE, 'raw')
OUT = os.path.join(BASE, 'research')


def load(*p):
    with open(os.path.join(*p), encoding='utf-8') as f:
        return json.load(f)


# ---------------------------------------------------------------- muscle -> part
MUSCLE_PART = {
    # free-exercise-db muscle names
    'chest': '상체', 'shoulders': '상체', 'triceps': '상체', 'biceps': '상체', 'lats': '상체',
    'middle back': '상체', 'traps': '상체', 'forearms': '상체', 'neck': '상체',
    'quadriceps': '하체', 'hamstrings': '하체', 'glutes': '하체', 'calves': '하체',
    'adductors': '하체', 'abductors': '하체',
    'abdominals': '코어', 'lower back': '코어',
}
# wger muscle ids -> (english, part)
WGER_MUSCLE = {
    1: ('biceps', '상체'), 2: ('shoulders (anterior deltoid)', '상체'), 3: ('serratus anterior', '상체'),
    4: ('chest', '상체'), 5: ('triceps', '상체'), 6: ('abdominals (rectus abdominis)', '코어'),
    7: ('calves (gastrocnemius)', '하체'), 8: ('glutes', '하체'), 9: ('trapezius', '상체'),
    10: ('quadriceps', '하체'), 11: ('hamstrings', '하체'), 12: ('lats', '상체'), 13: ('brachialis', '상체'),
    14: ('obliques', '코어'), 15: ('calves (soleus)', '하체'), 16: ('lower back (erector spinae)', '코어'),
}
WGER_CATEGORY_PART = {8: '상체', 9: '하체', 10: '코어', 11: '상체', 12: '상체', 13: '상체', 14: '하체', 15: None}
WGER_CATEGORY_NAME = {8: 'Arms', 9: 'Legs', 10: 'Abs', 11: 'Chest', 12: 'Back', 13: 'Shoulders', 14: 'Calves', 15: 'Cardio'}
LEVEL_KO = {'beginner': '초급', 'intermediate': '중급', 'expert': '고급'}

# Things that are NOT doable at home with no equipment (bar, machine, bands, ...).
APPARATUS = re.compile(
    r'pull.?up|chin.?up|\bbar\b|v-bar|hanging|fingerboard|sloper|rings?\b|trx|suspend|machine|cable|'
    r'band\b|foam roll|medicine ball|exercise ball|dumbbell|kettlebell|barbell|plate\b|weighted|box\b|'
    r'ab wheel|leg wheel|treadmill|elliptical|stair ?master|rowing|cycling|bicicleta|stationary bike|exercise bike|jump rope|'
    r'inverted row|australian|bag training|hyperextension bench|front lever|planche|handstand|l-sit|frog stand|pendulum squat',
    re.I)
# A bench/chair/wall/step is common furniture; flag it but keep it.
FURNITURE = re.compile(r'bench|chair|wall|step|couch|sofa|table|elevat|decline', re.I)
STRETCH_OR_NOT_EXERCISE = re.compile(
    r'stretch|estiramiento|respiraci|meditaci|circles?\b|head turns|head tilts|chin tuck|rotation (left|right)?$|'
    r'neck|child.s pose|cow-cat|foam|open book|roll down|sit & reach|toe touch|leg swings|pancake|'
    r'shinbox|horse stance|butterfly stretch|dorsiflexion|sphinx|cobra|walking$|march or jog|wall drills|'
    r'linear .*technique|acceleration wall drill|moving claw|arm drill|carioca|trail running|wind sprints',
    re.I)

# ---------------------------------------------------------------- overlap with our 20 exercises
# pattern -> our id. "same" = essentially the same movement; "variant" = close variation.
OURS_SAME = [
    (r'^wall push.?ups?$', 'wall_push_up'),
    (r'^(knee|bent.?knee) push.?ups?$', 'knee_push_up'),
    (r'^(push.?ups?|pushups)$', 'push_up'),
    (r'^(chair dips?|bench dips( on floor hd)?)$', 'chair_dip'),
    (r'^pike push.?ups?$', 'pike_push_up'),
    (r'^(clap push.?up|plyo push.?up)$', 'clap_push_up'),
    (r'^bodyweight squat( hd)?$', 'bodyweight_squat'),
    (r'^(butt lift bridge|hip bridge|hip raise, lying)$', 'glute_bridge'),
    (r'^reverse lunges?$|^alternate back lunges$', 'reverse_lunge'),
    (r'^wall squat$', 'wall_sit'),
    (r'^(freehand jump squat|squat jump)$', 'jump_squat'),
    (r'^bulgarian split squats?( left| right)?$', 'bulgarian_split_squat'),
    (r'^(split jump|scissors jump)$', 'split_squat_jump'),
    (r'^dead bug$', 'dead_bug'),
    (r'^(crunch(es)?( hd)?|abdominal crunch)$', 'crunch'),
    (r'^(plank|front plank)$', 'plank'),
    (r'^(side plank( right)?|side bridge)$', 'side_plank'),
    (r'^(bird dog|quadriped arm and leg raise)$', 'bird_dog'),
    (r'^mountain climbers?$', 'mountain_climber'),
    (r'^v-?up$', 'v_up'),
]
OURS_VARIANT = [
    (r'incline push', 'wall_push_up'),
    (r'push.?up|pushup|press-ups', 'push_up'),
    (r'dips', 'chair_dip'),
    (r'jump squat|squat jump', 'jump_squat'),
    (r'squat', 'bodyweight_squat'),
    (r'glute bridge|bridge', 'glute_bridge'),
    (r'lunge', 'reverse_lunge'),
    (r'split squat', 'bulgarian_split_squat'),
    (r'crunch|sit-?up', 'crunch'),
    (r'side plank|side bridge', 'side_plank'),
    (r'plank', 'plank'),
    (r'jackknife', 'v_up'),
]


def overlap(name):
    n = re.sub(r'\s+', ' ', re.sub(r'[()]', '', name.replace('_', ' '))).strip().lower()
    if 'burpee' in n or 'squat thrust' in n:
        return None, None
    for pat, oid in OURS_SAME:
        if re.search(pat, n):
            return 'same', oid
    for pat, oid in OURS_VARIANT:
        if re.search(pat, n):
            return 'variant', oid
    return None, None


def short(text, n=300):
    text = re.sub(r'\s+', ' ', text).strip()
    return text if len(text) <= n else text[:n].rsplit(' ', 1)[0] + '…'


def strip_html(s):
    return html.unescape(re.sub(r'<[^>]+>', ' ', s or ''))


# ---------------------------------------------------------------- free-exercise-db
def build_fedb(ours_ids):
    data = load(RAW, 'free_exercise_db', 'exercises.json')
    out, stats = [], {'total': len(data), 'body_only_or_none_equipment': 0, 'excluded_stretching': 0,
                      'excluded_apparatus': 0}
    for x in data:
        if x.get('equipment') not in ('body only', None):
            continue
        stats['body_only_or_none_equipment'] += 1
        if x.get('category') == 'stretching':
            stats['excluded_stretching'] += 1
            continue
        name = x['name']
        instr_all = ' '.join(x.get('instructions') or [])
        if APPARATUS.search(name) or STRETCH_OR_NOT_EXERCISE.search(name) or \
                re.search(r'exercise ball|dumbbell|pull-up bar|chin-up bar|hyperextension', instr_all, re.I):
            stats['excluded_apparatus'] += 1
            continue
        prim = x.get('primaryMuscles') or []
        part = MUSCLE_PART.get(prim[0]) if prim else None
        kind, oid = overlap(name)
        furn = sorted(set(m.group(0).lower() for m in FURNITURE.finditer(name + ' ' + instr_all)))
        out.append({
            'source_id': x['id'],
            'name_en': name,
            'name_ko': None,
            'primary_muscles': prim,
            'secondary_muscles': x.get('secondaryMuscles') or [],
            'part': part,
            'level': LEVEL_KO.get(x.get('level')),
            'level_raw': x.get('level'),
            'category': x.get('category'),
            'mechanic': x.get('mechanic'),
            'force': x.get('force'),
            'equipment_raw': x.get('equipment'),
            'needs_furniture': furn,
            'instructions': short(' '.join((x.get('instructions') or [])[:3])),
            'license': 'Unlicense (public domain dedication)',
            'source_url': f'https://github.com/yuhonas/free-exercise-db/blob/main/exercises/{x["id"]}.json',
            'in_our_data': kind == 'same',
            'overlap': {'type': kind, 'our_id': oid} if kind else None,
        })
    stats['candidates'] = len(out)
    stats['not_in_our_data'] = sum(1 for c in out if not c['in_our_data'])
    return out, stats


# ---------------------------------------------------------------- wger
def build_wger():
    bases = {x['pk']: x['fields'] for x in load(RAW, 'wger', 'exercise-base-data.json')}
    trans = load(RAW, 'wger', 'translations.json')
    lic = {x['pk']: x['fields'] for x in load(RAW, 'wger', 'licenses.json')}
    tr_en = [t for t in trans if t['model'] == 'exercises.translation' and t['fields']['language'] == 2]
    tr_ko = [t for t in trans if t['model'] == 'exercises.translation' and t['fields']['language'] == 27]
    out, seen_names = [], set()
    stats = {'total_exercises': len(bases), 'english_translations': len(tr_en), 'korean_translations': len(tr_ko),
             'equipment_none_or_mat': 0, 'equipment_unspecified': sum(1 for b in bases.values() if not b['equipment']),
             'excluded_apparatus_or_stretch': 0, 'excluded_duplicate_name': 0}
    for t in tr_en:
        f = t['fields']
        b = bases.get(f['exercise'])
        if not b or not b['equipment'] or not set(b['equipment']) <= {4, 7}:
            continue
        stats['equipment_none_or_mat'] += 1
        name = f['name'].strip()
        desc = strip_html(f.get('description'))
        # wger is crowd-sourced: some "no equipment" entries are machines/bands, stretches or non-English.
        if APPARATUS.search(name) or STRETCH_OR_NOT_EXERCISE.search(name) or \
                re.search(r'[áéíóñ]|talons|arco|planche de', name, re.I) or \
                re.search(r'\bmachine\b|\bband\b|\bbar\b|foam roller', desc, re.I):
            stats['excluded_apparatus_or_stretch'] += 1
            continue
        key = re.sub(r'\b(hd|left|right)\b|[^a-z]', '', name.lower())
        if key in seen_names:
            stats['excluded_duplicate_name'] += 1
            continue
        seen_names.add(key)
        prim_ids, sec_ids = b['muscles'], b['muscles_secondary']
        part = WGER_CATEGORY_PART.get(b['category'])
        if part is None and prim_ids:  # Cardio category: fall back to first primary muscle
            part = WGER_MUSCLE[prim_ids[0]][1]
        kind, oid = overlap(name)
        L = lic.get(f['license'], {})
        out.append({
            'source_id': f'wger:exercise/{f["exercise"]}',
            'uuid': b['uuid'],
            'name_en': name,
            'name_ko': None,
            'primary_muscles': [WGER_MUSCLE[m][0] for m in prim_ids],
            'secondary_muscles': [WGER_MUSCLE[m][0] for m in sec_ids],
            'part': part,
            'part_basis': 'wger category' if WGER_CATEGORY_PART.get(b['category']) else
                          ('primary muscle (cardio category)' if prim_ids else 'unknown'),
            'wger_category': WGER_CATEGORY_NAME.get(b['category']),
            'level': None,
            'equipment_raw': ['Gym mat' if e == 4 else 'none (bodyweight exercise)' for e in b['equipment']],
            'instructions': short(desc) if desc.strip() else None,
            'license': L.get('short_name', str(f['license'])).strip(),
            'license_url': L.get('url'),
            'license_author': f.get('license_author') or None,
            'source_url': f'https://wger.de/en/exercise/{f["exercise"]}/view/',
            'raw_file_url': 'https://github.com/wger-project/wger/blob/master/wger/exercises/fixtures/translations.json',
            'in_our_data': kind == 'same',
            'overlap': {'type': kind, 'our_id': oid} if kind else None,
        })
    stats['candidates'] = len(out)
    stats['not_in_our_data'] = sum(1 for c in out if not c['in_our_data'])
    stats['with_primary_muscles'] = sum(1 for c in out if c['primary_muscles'])
    stats['with_instructions'] = sum(1 for c in out if c['instructions'])
    return out, stats


def main():
    ours = load(BASE, 'exercises.json')
    ours_ids = {e['id'] for e in ours}
    fedb, s1 = build_fedb(ours_ids)
    wg, s2 = build_wger()
    meta_common = {'generated': '2026-11-17', 'filter': 'bodyweight / no equipment, home-feasible (bars, machines, '
                   'bands, balls, stretching excluded; chair/wall/bench flagged in needs_furniture where detected)',
                   'part_mapping': 'first primary muscle -> 상체/하체/코어 (abdominals, lower back = 코어)',
                   'in_our_data': 'true if the movement is essentially one of our 20 exercises in exercises.json; '
                                  'overlap.type="variant" marks close variations'}
    for fn, items, stats, src in [
        ('candidates_free_exercise_db.json', fedb, s1,
         {'name': 'free-exercise-db', 'url': 'https://github.com/yuhonas/free-exercise-db',
          'raw': 'https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/dist/exercises.json',
          'license': 'Unlicense', 'attribution': 'not required (public domain); courtesy credit recommended'}),
        ('candidates_wger.json', wg, s2,
         {'name': 'wger', 'url': 'https://wger.de / https://github.com/wger-project/wger',
          'raw': 'https://raw.githubusercontent.com/wger-project/wger/master/wger/exercises/fixtures/',
          'license': 'exercise texts CC-BY-SA 3.0/4.0 per entry (see license, license_author); code AGPL-3.0',
          'attribution': 'required: credit wger + license_author, link license; derivatives must stay CC-BY-SA'}),
    ]:
        doc = {'source': src, 'meta': meta_common, 'stats': stats,
               'not_in_our_data_ids': [c['source_id'] for c in items if not c['in_our_data']],
               'items': items}
        with open(os.path.join(OUT, fn), 'w', encoding='utf-8') as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
        print(fn, json.dumps(stats, ensure_ascii=False))


if __name__ == '__main__':
    main()
