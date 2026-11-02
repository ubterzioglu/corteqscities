import sys, re, html, urllib.request, ssl, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def get(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120 Safari/537.36", "Accept-Language": "de-DE,de;q=0.9"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read()
        ct = r.headers.get_content_charset() or 'utf-8'
        final = r.geturl()
    try:
        t = raw.decode(ct, errors='replace')
    except Exception:
        t = raw.decode('utf-8', errors='replace')
    return t, final

def strip(t):
    t = re.sub(r'(?is)<(script|style|noscript)[^>]*>.*?</\1>', ' ', t)
    t = re.sub(r'(?i)<br\s*/?>|</p>|</li>|</h\d>|</tr>|</div>', '\n', t)
    t = re.sub(r'(?s)<[^>]+>', ' ', t)
    t = html.unescape(t)
    t = t.replace('\xa0', ' ')
    t = re.sub(r'[ \t]+', ' ', t)
    t = re.sub(r'\n\s*\n+', '\n', t)
    return t

if __name__ == '__main__':
    url = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else 'head'
    try:
        raw, final = get(url)
    except Exception as e:
        print('HATA', url, repr(e)[:200]); sys.exit(0)
    t = strip(raw)
    print('FINAL', final, 'len', len(t))
    if mode == 'head':
        n = int(sys.argv[3]) if len(sys.argv) > 3 else 3000
        print(t[:n])
    elif mode == 'links':
        pat = sys.argv[3] if len(sys.argv) > 3 else ''
        for m in re.finditer(r'(?is)<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', raw):
            href, txt = m.group(1), re.sub(r'<[^>]+>', ' ', m.group(2)).strip()
            if re.search(pat, href + ' ' + txt, re.I):
                print(href, '|', re.sub(r'\s+', ' ', html.unescape(txt))[:100])
    else:  # grep: keywords
        kws = sys.argv[2:]
        for kw in kws:
            for m in list(re.finditer(re.escape(kw), t, re.I))[:3]:
                s = max(0, m.start() - 250); e = min(len(t), m.end() + 450)
                print('---', kw, '---'); print(t[s:e])
