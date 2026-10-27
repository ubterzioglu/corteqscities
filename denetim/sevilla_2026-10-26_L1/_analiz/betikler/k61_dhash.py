"""K61: teslim karesi <-> Commons'taki kare görsel karşılaştırması (dHash, 64 bit).

Kullanım: python -I -X utf8 k61_dhash.py <OUT> <PKG>
Commons küçük resmini (320 px) indirir (yalnız OUT/_cache/k61 altına), teslimdeki Fotoğraflar dosyasıyla dHash uzaklığını ölçer.
Çıktı: OUT/_analiz/k61_dhash.json
"""
import io
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image

OUT, PKG = Path(sys.argv[1]), Path(sys.argv[2])
CACHE = OUT / '_cache' / 'k61'
CACHE.mkdir(parents=True, exist_ok=True)
UA = 'CorteqsAudit/1.0 (denetim; corteqssocial@gmail.com)'


def JL(p):
    return [json.loads(l) for l in (OUT / p).read_text(encoding='utf-8').splitlines() if l.strip()]


def dhash(img: Image.Image) -> int:
    g = img.convert('L').resize((9, 8), Image.LANCZOS)
    px = list(g.getdata())
    bits = 0
    for row in range(8):
        for col in range(8):
            bits = (bits << 1) | (px[row * 9 + col] > px[row * 9 + col + 1])
    return bits


def fetch(url: str, dest: Path) -> bytes:
    if dest.exists() and dest.stat().st_size > 0:
        return dest.read_bytes()
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                data = r.read()
            dest.write_bytes(data)
            time.sleep(0.15)
            return data
        except urllib.error.HTTPError as e:
            if e.code in (400, 403, 404) or attempt == 3:
                raise
            time.sleep(2 * (attempt + 1))
        except Exception:  # noqa: BLE001
            if attempt == 3:
                raise
            time.sleep(2 * (attempt + 1))
    raise RuntimeError('fetch')


fot = {p['photo_id']: p for p in JL('_dump/Fotoğraflar.jsonl')}
rows, hata = [], []
for c in JL('_foto/candidates.jsonl'):
    pid = c['photo_id']
    p = fot.get(pid, {})
    local = PKG / str(p.get('file') or '')
    name = urllib.parse.unquote(str(c.get('source_url') or '').split('File:', 1)[-1])
    url = re.sub(r'/\d+px-', '/330px-', str(c.get('thumb_url') or ''))  # Wikimedia standart küçük resim adımı
    if not url:
        hata.append({'photo_id': pid, 'commons': name, 'hata': 'thumb_url yok'})
        continue
    try:
        data = fetch(url, CACHE / (pid.split(':')[-1] + '.jpg'))
        a = dhash(Image.open(io.BytesIO(data)))
        b = dhash(Image.open(local))
        d = bin(a ^ b).count('1')
        rows.append({'photo_id': pid, 'entry_id': p.get('entry_id'), 'file': p.get('file'), 'commons': name, 'mesafe': d})
    except Exception as e:  # noqa: BLE001
        hata.append({'photo_id': pid, 'commons': name, 'hata': str(e)[:200]})
rows.sort(key=lambda r: -r['mesafe'])
uzak = [r for r in rows if r['mesafe'] > 12]
ozet = {'olculen': len(rows), 'hata': len(hata), 'mesafe_0_6': sum(1 for r in rows if r['mesafe'] <= 6),
        'mesafe_7_12': sum(1 for r in rows if 6 < r['mesafe'] <= 12), 'mesafe_13_ustu': len(uzak)}
(OUT / '_analiz' / 'k61_dhash.json').write_text(json.dumps({'ozet': ozet, 'uzak': uzak, 'hata': hata, 'satirlar': rows},
                                                           ensure_ascii=False, indent=1), encoding='utf-8')
print(json.dumps({**ozet, 'uzak_ilk': [(r['photo_id'], r['mesafe']) for r in uzak[:15]]}, ensure_ascii=False))
