"""Extract text from a PDF with pypdf.
usage: uv run --with pypdf python -I pdf_text.py IN.pdf OUT.txt
Writes page-delimited text (=== page N ===) to OUT.txt as UTF-8."""
import sys
from pypdf import PdfReader

src, out = sys.argv[1], sys.argv[2]
r = PdfReader(src)
with open(out, 'w', encoding='utf-8') as f:
    for i, p in enumerate(r.pages, 1):
        f.write(f'\n=== page {i} ===\n')
        f.write(p.extract_text() or '')
print(len(r.pages), 'pages ->', out)
