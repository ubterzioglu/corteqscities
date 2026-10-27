"""atif_kontrol.py: D5/K75 — paket içi atıf önizlemesindeki (Teslimler/fotograf-atif-onizleme.html) her karenin
yazar, kaynak, lisans bağlantısı, değişiklik notu ve görsel dosyası Excel ile birebir mi (PKG yalnız okunur).

Kullanım: python -I -X utf8 atif_kontrol.py <OUT> <PKG>
Çıktı: OUT/_analiz/atif-kontrol.json
"""
import html
import json
import re
import sys
from pathlib import Path

OUT, PKG = Path(sys.argv[1]), Path(sys.argv[2])


def JL(p):
    return [json.loads(l) for l in (OUT / p).read_text(encoding='utf-8').splitlines() if l.strip()]


fot = {p['photo_id']: p for p in JL('_dump/Fotoğraflar.jsonl')}
fk = {p['photo_id']: p for p in JL('_dump/FotoğrafKaynakları.jsonl')}
doc = (PKG / 'Teslimler' / 'fotograf-atif-onizleme.html').read_text(encoding='utf-8')
arts = re.findall(r'<article>(.*?)</article>', doc, re.S)
rows, sorun = [], []
seen = set()
for a in arts:
    pid_m = re.search(r'<small>([^<]+)</small>', a)
    pid = html.unescape(pid_m.group(1)).strip().split()[0] if pid_m else None
    links = [(html.unescape(h), html.unescape(re.sub('<[^>]+>', '', t)).strip()) for h, t in re.findall(r'<a href="([^"]+)">(.*?)</a>', a, re.S)]
    src = re.search(r'<img[^>]+src="([^"]+)"', a)
    notlar = re.findall(r'<p>(Kaynak dosyanın değişiklik notu:.*?)</p>', a, re.S)
    p, k = fot.get(pid, {}), fk.get(pid, {})
    hrefs = {h for h, _ in links}
    texts = {t for _, t in links}
    kontrol = {
        'kimlik': bool(p),
        'yazar_adi': bool(p) and str(p.get('author') or '').strip() in texts,
        'kaynak': bool(p) and p.get('source_url') in hrefs,
        'lisans_url': bool(p) and p.get('license_url') in hrefs,
        'lisans_adi': bool(p) and str(p.get('license') or '').strip() in texts,
        'yazar_url': (not k.get('author_url')) or k.get('author_url') in hrefs,
        'degisiklik_notu': bool(notlar),
        'gorsel_dosya': bool(src) and (PKG / 'Teslimler' / html.unescape(src.group(1)).replace('../Teslimler/', '')).exists(),
    }
    ok = all(kontrol.values())
    rows.append({'photo_id': pid, 'ok': ok, **kontrol})
    if pid:
        seen.add(pid)
    if not ok:
        sorun.append({'photo_id': pid, 'eksik': [x for x, v in kontrol.items() if not v],
                      'excel': {x: p.get(x) for x in ('author', 'source_url', 'license', 'license_url')}, 'html_links': links[:6]})
ozet = {'article': len(arts), 'excel_kare': len(fot), 'eslesen_kimlik': len(seen & set(fot)), 'tam_dogru': sum(1 for r in rows if r['ok']),
        'sorunlu': len(sorun), 'eksik_tur': {}}
for s in sorun:
    for x in s['eksik']:
        ozet['eksik_tur'][x] = ozet['eksik_tur'].get(x, 0) + 1
(OUT / '_analiz' / 'atif-kontrol.json').write_text(json.dumps({'ozet': ozet, 'sorun': sorun}, ensure_ascii=False, indent=1), encoding='utf-8')
print(json.dumps({**ozet, 'ilk_sorun': sorun[:3]}, ensure_ascii=False))
