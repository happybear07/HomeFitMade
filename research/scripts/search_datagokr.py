"""Search data.go.kr dataset list for fitness keywords; print titles + links (stdlib only)."""
import re, sys, html, urllib.request, urllib.parse
KW = sys.argv[1:] or ['운동처방']
seen = set()
for kw in KW:
    q = urllib.parse.urlencode({'keyword': kw, 'perPage': '50', 'currentPage': '1'})
    req = urllib.request.Request('https://www.data.go.kr/tcs/dss/selectDataSetList.do?' + q,
                                 headers={'User-Agent': 'Mozilla/5.0 (student research script)'})
    s = urllib.request.urlopen(req, timeout=60).read().decode('utf-8', 'replace')
    tot = re.search(r'총\s*<strong>\s*([\d,]+)', s)
    print('==', kw, 'total', tot.group(1) if tot else '?')
    for m in re.finditer(r'<a[^>]+href="(/data/(\d+)/(fileData|openapi|standard)\.do)[^"]*"[^>]*>(.*?)</a>', s, re.S):
        t = html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', m.group(4)))).strip()
        if t and m.group(1) not in seen and re.search('체육|체력|운동|건강|스포츠', t):
            seen.add(m.group(1)); print('  ', m.group(1), '|', t[:140])
