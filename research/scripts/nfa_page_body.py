"""Extract the content body of saved nfa.kspo.or.kr pages (stdlib only).
usage: python -I nfa_page_body.py OUT.txt FILE.html [FILE.html ...]
Drops scripts/styles/comments, turns table cells into ' | ', keeps text from the
page's content heading (after the left menu's last item) up to the footer ('협력기관')."""
import sys, re, html

out = open(sys.argv[1], 'w', encoding='utf-8')
for fn in sys.argv[2:]:
    s = open(fn, encoding='utf-8', errors='replace').read()
    s = re.sub(r'(?is)<(script|style)[^>]*>.*?</\1>', ' ', s)
    s = re.sub(r'(?is)<!--.*?-->', ' ', s)
    s = re.sub(r'(?i)</t[dh]>', ' | ', s)
    s = re.sub(r'(?i)</(p|li|tr|h\d|caption)>|<br\s*/?>', '\n', s)
    t = html.unescape(re.sub(r'<[^>]+>', ' ', s))
    t = re.sub(r'[ \t\r]+', ' ', t)
    t = re.sub(r'\s*\n\s*', '\n', t)
    # body starts after the last occurrence of the left-menu item '스포츠활동과 건강관리'
    i = t.rfind('스포츠활동과 건강관리')
    j = t.find('협력기관', i if i >= 0 else 0)
    body = t[i if i >= 0 else 0: j if j > 0 else None]
    out.write(f'\n===== {fn}\n{body}\n')
out.close()
