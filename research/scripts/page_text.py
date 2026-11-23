"""Fetch a page and print visible text (stdlib). usage: python -I page_text.py URL [maxchars] [start_marker]"""
import re, sys, html, urllib.request
url = sys.argv[1]; mx = int(sys.argv[2]) if len(sys.argv) > 2 else 6000
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (student research script)'})
s = urllib.request.urlopen(req, timeout=60).read().decode('utf-8', 'replace')
s = re.sub(r'(?is)<(script|style)[^>]*>.*?</\1>', ' ', s)
t = html.unescape(re.sub(r'<[^>]+>', ' ', s)); t = re.sub(r'\s+', ' ', t)
if len(sys.argv) > 3:
    i = t.find(sys.argv[3]); t = t[max(i, 0):]
print(t[:mx])
