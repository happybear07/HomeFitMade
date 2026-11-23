"""Print visible text of a saved HTML file (stdlib). usage: python -I html_text.py FILE [start_marker] [maxchars]
Drops <script>/<style>, header/nav menus are kept, so pass a start_marker to skip them."""
import re, sys, html
s = open(sys.argv[1], encoding='utf-8', errors='replace').read()
s = re.sub(r'(?is)<(script|style)[^>]*>.*?</\1>', ' ', s)
s = re.sub(r'(?i)<br\s*/?>|</(p|li|tr|div|h\d)>', '\n', s)
s = re.sub(r'(?i)</t[dh]>', ' | ', s)
t = html.unescape(re.sub(r'<[^>]+>', ' ', s))
t = re.sub(r'[ \t\r]+', ' ', t); t = re.sub(r'\n\s*\n+', '\n', t)
if len(sys.argv) > 2 and sys.argv[2]:
    i = t.find(sys.argv[2]); t = t[max(i, 0):]
mx = int(sys.argv[3]) if len(sys.argv) > 3 else 20000
sys.stdout.reconfigure(encoding='utf-8')
print(t[:mx])
