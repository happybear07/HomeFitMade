"""Extract embedded swagger JSON from a data.go.kr openapi page and summarize. usage: extract_swagger.py page.html out.json"""
import re, sys, json
s = open(sys.argv[1], encoding='utf-8').read()
m = re.search(r'const swaggerJson = `(.*?)`;', s, re.S)
spec = json.loads(m.group(1))
json.dump(spec, open(sys.argv[2], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('host', spec.get('host'), spec.get('basePath'), spec.get('schemes'))
for p, ops in spec.get('paths', {}).items():
    for verb, op in ops.items():
        print('PATH', verb.upper(), p, '|', op.get('summary'), '|', op.get('description', '')[:200])
        for prm in op.get('parameters', []):
            print('   param', prm.get('name'), prm.get('required'), prm.get('description'))
def walk(d, pre=''):
    if isinstance(d, dict):
        if 'properties' in d:
            for k, v in d['properties'].items():
                desc = v.get('description', '') if isinstance(v, dict) else ''
                print('   field', pre + k, '|', desc[:120], '|', v.get('example', '') if isinstance(v, dict) else '')
                walk(v, pre + k + '.')
        for k in ('items', 'schema'):
            if k in d: walk(d[k], pre)
        if '$ref' in d:
            pass
for name, df in spec.get('definitions', {}).items():
    print('DEF', name); walk(df)
