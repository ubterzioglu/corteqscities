"""L2 hazırlığı (yalnız OUT altına yazar; PKG yalnız okunur).

Kullanım: python -I -X utf8 l2_hazirla.py <OUT> <PKG>
- Sonnet çıktılarını (durdurulan workflow'un yarım işleri + iddia 01/02) OUT/_sonnet/ altına taşır.
- L1 seçiminde olmayan bütün Yanıtlar + Sözlük kartları için yeni iddia partileri kurar.
- Bağlantılar (575), Kaynaklar (500), lisans zinciri (334), mekânlar (120) için tam kapsam partileri.
- K61: teslimdeki özgün dosyanın SHA-1'i ile Commons kaydının SHA-1'i.
- K105: 2014 öncesi çekim tarihli kareler.
"""
import collections
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

OUT = Path(sys.argv[1])
PKG = Path(sys.argv[2])


def JL(p):
    return [json.loads(l) for l in (OUT / p).read_text(encoding='utf-8').splitlines() if l.strip()]


def L(p):
    return json.loads((OUT / p).read_text(encoding='utf-8-sig'))


def W(p, rows):
    p = OUT / p
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows), encoding='utf-8')


def chunks(rows, n):
    size = -(-len(rows) // n)
    return [rows[i * size:(i + 1) * size] for i in range(n)]


ozet = {}

# 1) Sonnet çıktıları yedeğe
moves = ['_l/mekan_A.jsonl', '_l/mekan_B.jsonl', '_l/mahalleler.jsonl', '_l/rotalar.jsonl', '_l/k20_gruplar.json',
         '_l/lisans.jsonl', '_l/lisans_ozet.json', '_l/baglanti.jsonl', '_l/sehir_sayfa.jsonl',
         '_foto/karsi_foto.jsonl', '_iddia/karsi_01.jsonl', '_iddia/karsi_02.jsonl',
         '_iddia/parti_01.jsonl', '_iddia/kart_01.jsonl', '_iddia/parti_02.jsonl', '_iddia/kart_02.jsonl']
moved = []
for m in moves:
    src = OUT / m
    if src.exists():
        dst = OUT / '_sonnet' / m
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        moved.append(m)
ozet['sonnet_yedek'] = moved

# 2) iddia: L1 seçiminde olmayan kartlar
yan = JL('_dump/Yanıtlar.jsonl')
soz = JL('_dump/Sözlük.jsonl')
mek = JL('_dump/Mekânlar.jsonl')
mah = JL('_dump/Mahalleler.jsonl')
rot = JL('_dump/Rotalar.jsonl')
kay = {k['source_id']: k for k in JL('_dump/Kaynaklar.jsonl')}
index = {r['url']: r for r in JL('kanitlar/snap/index.jsonl')}
by_entry = collections.defaultdict(list)
for r in L('claim-script.json')['results']:
    by_entry[r['entry_id']].append(r)
girdi = OUT / '_iddia' / 'girdi'
mevcut = sorted(d for d in girdi.glob('parti_*') if d.is_dir())
secili = set()
for d in mevcut:
    for c in JL(f'_iddia/girdi/{d.name}/kartlar.jsonl'):
        secili.add(c.get('entry_id') or c.get('term_id'))
kalan = [y for y in yan if y['entry_id'] not in secili] + [s for s in soz if s['term_id'] not in secili]
kalan.sort(key=lambda c: (str(c.get('topic_id') or 'zz'), c.get('entry_id') or c.get('term_id')))
start = 1 + max(int(d.name.split('_')[1]) for d in mevcut)
yeni = []
for k, part in enumerate(chunks(kalan, -(-len(kalan) // 11))):
    nn = f'{start + k:02d}'
    claims, snaps = [], {}
    for card in part:
        e = card.get('entry_id') or card.get('term_id')
        for r in by_entry.get(e, []):
            claims.append({f: r.get(f) for f in ('claim_id', 'entry_id', 'sheet', '_row', 'field', 'kind', 'text',
                                                  'sentence', 'values', 'result', 'sources')})
            for s in r.get('sources', []):
                sid = s.get('snapshot_id')
                if sid:
                    snaps[s['url']] = {'snapshot_id': sid, 'source_id': s.get('source_id'),
                                       'title': kay.get(s.get('source_id'), {}).get('title'),
                                       'file': str(OUT / 'kanitlar' / 'snap' / sid)}
        for sid in re.split(r'[\n;|]', str(card.get('source_ids') or '')):
            sid = sid.strip()
            if sid and sid in kay:
                kr = kay[sid]
                ix = index.get(kr['url']) or {}
                tf = ix.get('text_file')
                snaps.setdefault(kr['url'], {'snapshot_id': tf, 'source_id': sid, 'title': kr.get('title'),
                                             'file': str(OUT / 'kanitlar' / 'snap' / tf) if tf else None})
    d = f'_iddia/girdi/parti_{nn}'
    W(f'{d}/kartlar.jsonl', part)
    W(f'{d}/iddialar.jsonl', claims)
    W(f'{d}/kaynaklar.jsonl', [{'url': u, **v} for u, v in snaps.items()])
    yeni.append({'parti': nn, 'kart': len(part), 'iddia': len(claims)})
ozet['iddia'] = {'L1_secili': len(secili), 'kalan_kart': len(kalan), 'yeni_partiler': yeni}

# 3) bağlantılar: hepsi, 8 parti (aynı kartın bağlantıları bir arada)
url_info = {u['ham_URL']: {f: u.get(f) for f in ('erişim_sonucu', 'HTTP_durumu', 'son_URL', 'sayfa_başlığı', 'flags')}
            for u in L('url-checks.json')['urls']}
title_by = {y['entry_id']: y.get('title') for y in yan}
title_by.update({m['entry_id']: m.get('title') for m in mek})
title_by.update({m['entry_id']: m.get('title') for m in mah})
bag = JL('_dump/Bağlantılar.jsonl')
brows = [{**b, 'kart_basligi': title_by.get(b['entry_id']), 'url_check': url_info.get(b['url'])} for b in bag]
for i, part in enumerate(chunks(brows, 8), 1):
    W(f'_l/girdi/baglanti_tam_{i:02d}.jsonl', part)
ozet['baglanti'] = {'satir': len(brows), 'parti': 8}

# 4) kaynaklar: hepsi, 10 parti; her kaynağı kullanan kayıtlar
src_cards = collections.defaultdict(list)
for sheet, rows, idk in (('Yanıtlar', yan, 'entry_id'), ('Sözlük', soz, 'term_id'), ('Mekânlar', mek, 'entry_id'),
                         ('Mahalleler', mah, 'entry_id'), ('Rotalar', rot, 'route_id'),
                         ('Şehir', JL('_dump/Şehir.jsonl'), None), ('SayfaAlanları', JL('_dump/SayfaAlanları.jsonl'), None)):
    for r in rows:
        for sid in re.split(r'[\n;|]', str(r.get('source_ids') or '')):
            sid = sid.strip()
            if sid:
                src_cards[sid].append({'sheet': sheet, 'id': r.get(idk) if idk else sheet,
                                       'title': r.get('title') or r.get('term') or r.get('key')})
krows = []
for kr in kay.values():
    ix = index.get(kr['url']) or {}
    krows.append({**kr, 'kartlar': src_cards.get(kr['source_id'], [])[:15],
                  'kart_sayisi': len(src_cards.get(kr['source_id'], [])),
                  'taze_kopya': str(OUT / 'kanitlar' / 'snap' / ix['text_file']) if ix.get('text_file') else None,
                  'taze_baslik': ix.get('title'), 'url_check': url_info.get(kr['url'])})
for i, part in enumerate(chunks(krows, 10), 1):
    W(f'_l/girdi/kaynak_{i:02d}.jsonl', part)
ozet['kaynak'] = {'satir': len(krows), 'parti': 10, 'kullanilmayan': [r['source_id'] for r in krows if not r['kart_sayisi']]}

# 5) lisans zinciri: hepsi, 4 parti
lz = JL('_l/girdi/lisans_zinciri.jsonl')
for i, part in enumerate(chunks(lz, 4), 1):
    W(f'_l/girdi/lisans_tam_{i:02d}.jsonl', part)
ozet['lisans'] = {'satir': len(lz), 'parti': 4}

# 6) mekânlar: 4 pay
mrows = JL('_l/girdi/mekan_A.jsonl') + JL('_l/girdi/mekan_B.jsonl')
for i, part in enumerate(chunks(mrows, 4), 1):
    W(f'_l/girdi/mekan_P{i}.jsonl', part)
ozet['mekan'] = {'satir': len(mrows), 'pay': 4}

# 7) K61: teslim özgün dosyası <-> Commons SHA-1
cand = {c['photo_id']: c for c in JL('_foto/candidates.jsonl')}
fk = {p['photo_id']: p for p in JL('_dump/FotoğrafKaynakları.jsonl')}
k61 = {'esit': 0, 'farkli': [], 'yok': []}
for pid, c in cand.items():
    f = fk.get(pid, {}).get('original_file')
    p = PKG / f if f else None
    if not p or not p.exists() or not c.get('sha1'):
        k61['yok'].append({'photo_id': pid, 'original_file': f, 'commons_sha1': c.get('sha1')})
        continue
    h = hashlib.sha1(p.read_bytes()).hexdigest()
    if h == str(c['sha1']).lower():
        k61['esit'] += 1
    else:
        k61['farkli'].append({'photo_id': pid, 'original_file': f, 'sha1': h, 'commons_sha1': c['sha1'],
                              'commons_size': [c.get('width'), c.get('height')]})
(OUT / '_analiz' / 'k61_sha1.json').write_text(json.dumps(k61, ensure_ascii=False, indent=1), encoding='utf-8')
ozet['K61'] = {'esit': k61['esit'], 'farkli': len(k61['farkli']), 'yok': len(k61['yok'])}

# 8) K105: 2014 öncesi çekim
fot = JL('_dump/Fotoğraflar.jsonl')
eski = [{'photo_id': p['photo_id'], 'entry_id': p.get('entry_id'), 'capture_date': p.get('capture_date')}
        for p in fot if re.match(r'\d{4}', str(p.get('capture_date') or '')) and int(str(p['capture_date'])[:4]) < 2014]
W('_foto/eski_cekim.jsonl', eski)
ozet['K105_2014_oncesi'] = len(eski)

print(json.dumps(ozet, ensure_ascii=False))
