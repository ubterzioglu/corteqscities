"""hazirla_l1.py: L1 ajan girdileri (yalniz OUT altina yazar). python -I -X utf8 hazirla_l1.py <OUT>"""
import json, sys, collections, hashlib, re
from pathlib import Path
OUT = Path(sys.argv[1])
def L(p): return json.loads((OUT/p).read_text(encoding='utf-8-sig'))
def JL(p): return [json.loads(l) for l in (OUT/p).read_text(encoding='utf-8').splitlines() if l.strip()]
def W(p, rows):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(''.join(json.dumps(r, ensure_ascii=False)+'\n' for r in rows), encoding='utf-8')
yan = {y['entry_id']: y for y in JL('_dump/Yanıtlar.jsonl')}
soz = {s['term_id']: s for s in JL('_dump/Sözlük.jsonl')}
kay = {k['source_id']: k for k in JL('_dump/Kaynaklar.jsonl')}
bag = JL('_dump/Bağlantılar.jsonl')
mek = JL('_dump/Mekânlar.jsonl'); mah = JL('_dump/Mahalleler.jsonl'); rot = JL('_dump/Rotalar.jsonl')
cs = L('claim-script.json'); results = cs['results']
tq = L('text-quality.json')
index = {r['url']: r for r in JL('kanitlar/snap/index.jsonl')}
# ---- iddia secimi
by_entry = collections.defaultdict(list)
for r in results: by_entry[r['entry_id']].append(r)
unsup_entries = {e for e,rs in by_entry.items() if any(r['result']!='supported' for r in rs)}
# sayisal olmayan kural iceren kartlar
rule_rx = re.compile(r'ücret|şart|başvur|yasak|gerek|zorunlu|izin|randevu|muaf|ceza', re.I)
rule_entries = {e for e,y in yan.items() if rule_rx.search(' '.join(str(y.get(k) or '') for k in ('summary','steps','cost','note')))}
hedge_entries = set()
for key in ('hedges','evasive_answers'):
    v = tq.get(key)
    if isinstance(v, dict):
        for it in v.get('items', []): hedge_entries.add(it.get('entry_id'))
    elif isinstance(v, list):
        for it in v: hedge_entries.add(it.get('entry_id') if isinstance(it, dict) else None)
hedge_entries.discard(None)
# ACIK_KONULAR beyani: metinde gecen kart slug'lari (yalniz oncelik)
CITY = next(iter(yan)).split(':')[0]  # city_id öneki
P01 = {f'{CITY}:{t}' for t in ('oturum', 'saglik', 'para', 'ev', 'is')}
all_claim_entries = set(by_entry)
selected = set(unsup_entries) | (rule_entries & all_claim_entries) | (hedge_entries & all_claim_entries)
# P0/P1 konulardan supported-only kartlardan %20 ornek (deterministik: sha sira)
sup_only = sorted(e for e in all_claim_entries - selected if yan.get(e,{}).get('topic_id') in P01)
sup_only.sort(key=lambda e: hashlib.sha256(e.encode()).hexdigest())
n_sample = -(-len(sup_only)*20//100)
selected |= set(sup_only[:n_sample])
sel = sorted(selected, key=lambda e: (yan.get(e,{}).get('topic_id',''), e))
# parti: ~13 kart
N = max(1, -(-len(sel) // 11))  # parti başına ~11 kart
parts = [sel[i::N] for i in range(N)]
summary = {'claim_entries': len(all_claim_entries), 'unsup_entries': len(unsup_entries), 'rule_entries': len(rule_entries & all_claim_entries), 'hedge_entries': len(hedge_entries), 'sup_only_P01': len(sup_only), 'sampled_sup_only': n_sample, 'selected_entries': len(sel), 'claims_in_selected': sum(len(by_entry[e]) for e in sel), 'unsup_claims_in_selected': sum(1 for e in sel for r in by_entry[e] if r['result']!='supported'), 'parts': [len(p) for p in parts]}
for i, p in enumerate(parts, 1):
    d = OUT/'_iddia'/'girdi'/f'parti_{i:02d}'
    cards, claims, snaps = [], [], {}
    for e in p:
        card = yan.get(e) or soz.get(e)
        cards.append(card)
        for r in by_entry[e]:
            claims.append({k: r.get(k) for k in ('claim_id','entry_id','sheet','_row','field','kind','text','sentence','values','result','sources')})
            for s in r.get('sources', []):
                sid = s.get('snapshot_id')
                if sid: snaps[s['url']] = {'snapshot_id': sid, 'source_id': s.get('source_id'), 'title': kay.get(s.get('source_id'),{}).get('title'), 'file': str(OUT/'kanitlar'/'snap'/sid)}
        for sid in re.split(r'[\n;|]', str(card.get('source_ids',''))):
            sid = sid.strip()
            if sid and sid in kay:
                k = kay[sid]; ix = index.get(k['url'])
                if ix and ix.get('text_file'): snaps.setdefault(k['url'], {'snapshot_id': ix['text_file'], 'source_id': sid, 'title': k.get('title'), 'file': str(OUT/'kanitlar'/'snap'/ix['text_file'])})
                else: snaps.setdefault(k['url'], {'snapshot_id': None, 'source_id': sid, 'title': k.get('title'), 'file': None})
    W(d/'kartlar.jsonl', cards); W(d/'iddialar.jsonl', claims)
    W(d/'kaynaklar.jsonl', [{'url': u, **v} for u,v in snaps.items()])
(OUT/'_iddia'/'secim-ozeti.json').write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding='utf-8')
print('IDDIA', json.dumps(summary, ensure_ascii=False))
print('index keys', list(next(iter(index.values())).keys()))
# ---- acik-mi girdileri
links = collections.defaultdict(list)
for b in bag: links[b.get('entry_id')].append({k: b.get(k) for k in ('label','url','kind','_row') if k in b})
mek_by = {m['entry_id']: m for m in mek}
import glob
for pf in sorted((OUT/'_acikmi').glob('parti_*.jsonl')):
    if '_dogrulama' in pf.name: continue
    rows = [json.loads(l) for l in pf.read_text(encoding='utf-8').splitlines() if l.strip()]
    g = []
    for r in rows:
        m = mek_by.get(r['entry_id'], {})
        g.append({'entry_id': r['entry_id'], '_row': m.get('_row'), 'title': m.get('title'), 'location': m.get('location'), 'district': m.get('district'), 'group': m.get('group'), 'summary': m.get('summary'), 'note': m.get('note'), 'visit_status': m.get('visit_status'), 'baglantilar': links.get(r['entry_id'], [])})
    W(OUT/'_acikmi_girdi'/f'girdi_{pf.stem}.jsonl', g)  # _acikmi'ye YAZMA: acik_mi kapısı oradaki her jsonl'i tarama sayar
print('ACIKMI partiler', [p.name for p in sorted((OUT/'_acikmi').glob('parti_*.jsonl'))])
print('MEKAN keys', list(mek[0].keys())); print('MAH keys', list(mah[0].keys())); print('ROT keys', list(rot[0].keys())); print('BAG keys', list(bag[0].keys()))


