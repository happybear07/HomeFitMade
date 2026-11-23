"""Mirror data.go.kr's public '다운로드' button for a fileData dataset (no login).
Stops if the portal asks for a CAPTCHA (needCaptcha) - we never bypass it.
usage: python -I datagokr_filedownload.py PUBLIC_DATA_PK OUT_DIR"""
import sys, re, json, os, urllib.request, urllib.parse, http.cookiejar
pk, out_dir = sys.argv[1], sys.argv[2]
UA = {'User-Agent': 'Mozilla/5.0 (student research script)'}
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
def get(url, data=None):
    body = urllib.parse.urlencode(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body, headers=dict(UA, Referer=f'https://www.data.go.kr/data/{pk}/fileData.do'))
    return op.open(req, timeout=90)
page = get(f'https://www.data.go.kr/data/{pk}/fileData.do').read().decode('utf-8', 'replace')
m = re.search(r"fn_fileDataDown\('(\d+)',\s*'([^']*)',\s*'([^']*)',\s*'([^']*)'", page)
assert m, 'download button not found'
_, detail_pk, atch, sn = m.groups()
r = json.loads(get('https://www.data.go.kr/tcs/dss/selectFileDataDownload.do',
                   {'publicDataDetailPk': detail_pk, 'publicDataPk': pk, 'atchFileId': atch,
                    'fileDetailSn': sn, 'publicDataTyCode': 'PR0051'}).read().decode('utf-8'))
assert r.get('status') is True, r
atch, sn = r['atchFileId'], r['fileDetailSn']
name = r['dataSetFileDetailInfo'].get('dataNm') or pk
lim = json.loads(get('https://www.data.go.kr/cmm/cmm/check-limit.json', {'atchFileId': atch, 'fileDetailSn': sn}).read().decode('utf-8'))
if lim.get('needCaptcha'):
    sys.exit('Portal requires CAPTCHA for this download - stopping (download manually in a browser).')
url = 'https://www.data.go.kr/cmm/cmm/fileDownload.do?' + urllib.parse.urlencode({'atchFileId': atch, 'fileDetailSn': sn, 'dataNm': name})
resp = get(url); data = resp.read()
cd = resp.headers.get('Content-Disposition', '')
ext = '.csv'
mm = re.search(r'filename\*?=(?:UTF-8\'\')?"?([^";]+)', cd)
if mm:
    fn = urllib.parse.unquote(mm.group(1)); ext = os.path.splitext(fn)[1].lower() or ext
assert ext in ('.csv', '.json', '.xlsx', '.xls', '.zip'), ext
out = os.path.join(out_dir, f'datagokr_{pk}{ext}')
open(out, 'wb').write(data)
print('saved', out, len(data), 'bytes; content-disposition:', cd[:200])
