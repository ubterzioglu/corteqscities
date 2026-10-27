"""hazirla_l2.py: diger L kontrolleri icin girdiler. python -I -X utf8 hazirla_l2.py <OUT>"""
import json, sys, collections, hashlib, re
from pathlib import Path
OUT = Path(sys.argv[1])
def JL(p): return [json.loads(l) for l in (OUT/p).read_text(encoding='utf-8').splitlines() if l.strip()]
def L(p): return json.loads((OUT/p).read_text(encoding='utf-8-sig'))
def W(p, rows):
    p.parent.mkdir(parents=True, exist_ok=True); p.write_text(''.join(json.dumps(r, ensure_ascii=False)+'\n' for r in rows), encoding='utf-8')
mek = JL('_dump/Mekânlar.jsonl'); mah = JL('_dump/Mahalleler.jsonl'); rot = JL('_dump/Rotalar.jsonl'); bag = JL('_dump/Bağlantılar.jsonl')
kay = {k['source_id']: k for k in JL('_dump/Kaynaklar.jsonl')}
links = collections.defaultdict(list)
for b in bag: links[b['entry_id']].append({'label': b['label'], 'url': b['url'], '_row': b['_row']})
def srcs(row): return [{'source_id': s.strip(), 'url': kay.get(s.strip(),{}).get('url'), 'title': kay.get(s.strip(),{}).get('title')} for s in re.split(r'[\n;|]', str(row.get('source_ids',''))) if s.strip()]
# mekanlar iki parca
rows = [{**m, 'baglantilar': links.get(m['entry_id'], []), 'kaynaklar': srcs(m)} for m in mek]
half = (len(rows)+1)//2
W(OUT/'_l'/'girdi'/'mekan_A.jsonl', rows[:half]); W(OUT/'_l'/'girdi'/'mekan_B.jsonl', rows[half:])
# mahalle + rota
W(OUT/'_l'/'girdi'/'mahalleler.jsonl', [{**m, 'baglantilar': links.get(m['entry_id'], []), 'kaynaklar': srcs(m)} for m in mah])
mek_by = {m['entry_id']: m for m in mek}
rrows = []
for r in rot:
    ids = [s.strip() for s in re.split(r'[\n;|]', str(r.get('stop_entry_ids',''))) if s.strip()]
    rrows.append({**r, 'kaynaklar': srcs(r), 'duraklar': [{'entry_id': i, 'title': mek_by.get(i,{}).get('title'), 'location': mek_by.get(i,{}).get('location'), 'lat': mek_by.get(i,{}).get('latitude'), 'lon': mek_by.get(i,{}).get('longitude'), 'group': mek_by.get(i,{}).get('group'), 'note': mek_by.get(i,{}).get('note')} for i in ids]})
W(OUT/'_l'/'girdi'/'rotalar.jsonl', rrows)
W(OUT/'_l'/'girdi'/'mekan_ozet.jsonl', [{k: m.get(k) for k in ('entry_id','_row','title','group','district','location','collection','latitude','longitude')} for m in mek])
# baglantilar: ornek 60 + homepage_only + cross_host
urls = L('url-checks.json')['urls']
flagged = {u['ham_URL'] for u in urls if any(f in (u.get('flags') or []) for f in ('homepage_only','cross_host_redirect'))}
url_info = {u['ham_URL']: {k: u.get(k) for k in ('erişim_sonucu','HTTP_durumu','son_URL','sayfa_başlığı','flags')} for u in urls}
yan = {y['entry_id']: y for y in JL('_dump/Yanıtlar.jsonl')}
sel = [b for b in bag if b['url'] in flagged]
rest = [b for b in bag if b['url'] not in flagged]
rest.sort(key=lambda b: hashlib.sha256(b['action_id'].encode()).hexdigest())
sample = sel + rest[:60]
def card_title(e): 
    c = yan.get(e) or mek_by.get(e) or next((m for m in mah if m['entry_id']==e), {})
    return c.get('title')
W(OUT/'_l'/'girdi'/'baglantilar_ornek.jsonl', [{**b, 'kart_basligi': card_title(b['entry_id']), 'url_check': url_info.get(b['url'])} for b in sample])
sehir = JL('_dump/Şehir.jsonl'); sayfa = JL('_dump/SayfaAlanları.jsonl')
W(OUT/'_l'/'girdi'/'sehir_sayfa.jsonl', sehir + sayfa)
# lisans zinciri: kompakt kanit listesi
cands = JL('_foto/candidates.jsonl')
print('cand keys', list(cands[0].keys()))
fot = {p['photo_id']: p for p in JL('_dump/Fotoğraflar.jsonl')}
fk = {p['photo_id']: p for p in JL('_dump/FotoğrafKaynakları.jsonl')}
comp = []
for c in cands:
    pid = c.get('photo_id') or c.get('candidate_id'); p = fot.get(pid, {}); s = fk.get(pid, {})
    rec = c.get('original_api_record') or c.get('api_record') or {}
    em = (rec.get('extmetadata') or rec.get('imageinfo',[{}])[0].get('extmetadata') if isinstance(rec, dict) else None) or {}
    def v(k): 
        x = em.get(k); return (x.get('value') if isinstance(x, dict) else x)
    comp.append({'photo_id': pid, 'entry_id': p.get('entry_id'), '_row': p.get('_row'), 'file': p.get('file'), 'license': p.get('license'), 'license_url': p.get('license_url'), 'author': p.get('author'), 'source_url': p.get('source_url'), 'author_url': s.get('author_url'), 'provenance_note': s.get('provenance_note'), 'commons': {'LicenseShortName': v('LicenseShortName'), 'Artist': re.sub('<[^>]+>','',str(v('Artist') or ''))[:120], 'Credit': re.sub('<[^>]+>','',str(v('Credit') or ''))[:160], 'AttributionRequired': v('AttributionRequired'), 'Copyrighted': v('Copyrighted'), 'Restrictions': v('Restrictions'), 'ImageDescription': re.sub('<[^>]+>','',str(v('ImageDescription') or ''))[:160], 'DateTimeOriginal': v('DateTimeOriginal')}})
W(OUT/'_l'/'girdi'/'lisans_zinciri.jsonl', comp)
own = sum(1 for c in comp if 'own work' in (c['commons']['Credit'] or '').lower() or 'propio' in (c['commons']['Credit'] or '').lower())
print(json.dumps({'mekan_A': half, 'mekan_B': len(rows)-half, 'mahalle': len(mah), 'rota': len(rot), 'baglanti_ornek': len(sample), 'flagged_links': len(sel), 'lisans': len(comp), 'own_work_credit': own, 'licenses': dict(collections.Counter(c['license'] for c in comp)), 'commons_lic': dict(collections.Counter(c['commons']['LicenseShortName'] for c in comp))}, ensure_ascii=False))
