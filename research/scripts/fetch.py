"""Tiny fetch helper: python -I fetch.py URL OUTFILE [key=value ...] (query params UTF-8 encoded)."""
import sys, urllib.request, urllib.parse
url, out = sys.argv[1], sys.argv[2]
params = [tuple(a.split('=', 1) ) for a in sys.argv[3:]]
if params:
    url += ('&' if '?' in url else '?') + urllib.parse.urlencode(params)
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (student research script)'})
with urllib.request.urlopen(req, timeout=60) as r:
    data = r.read()
    print(r.status, len(data), r.headers.get('Content-Type'))
open(out, 'wb').write(data)
