import re,sys,html
s=open(sys.argv[1],encoding='utf-8',errors='replace').read()
seen=set()
for m in re.finditer(r'<a[^>]+href="(/data/(\d+)/(fileData|openapi|standard)\.do)[^"]*"[^>]*>(.*?)</a>',s,re.S):
    t=re.sub(r'<[^>]+>','',m.group(4)); t=html.unescape(re.sub(r'\s+',' ',t)).strip()
    if not t or m.group(1) in seen: continue
    seen.add(m.group(1)); print(m.group(1),'|',t[:150])
