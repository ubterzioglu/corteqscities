"""Aynı baytlı kanıt dosyası paylaşan mekân fotoğraf çiftleri: Excel satırları ve kanıt içeriği (yalnız okur)."""
import json, sys, re
from pathlib import Path
OUT = Path(sys.argv[1]); PKG = Path(sys.argv[2])
def L(p): return json.loads((OUT/p).read_text(encoding='utf-8-sig'))
def JL(p): return [json.loads(l) for l in (OUT/p).read_text(encoding='utf-8').splitlines() if l.strip()]
inv = L('dosya-envanteri.json')
fot = {p['photo_id']: p for p in JL('_dump/Fotoğraflar.jsonl')}
kan = {p.get('photo_id'): p for p in JL('_dump/Kanıtlar.jsonl')}
fk = {p['photo_id']: p for p in JL('_dump/FotoğrafKaynakları.jsonl')}
pairs = set()
for g in inv['findings']['dup_sha']:
    fs = g['files']
    if not all(f.startswith('Lisans kanıtları/') for f in fs): continue
    stems = [re.sub(r'\.(source|license)-evidence\.json$', '', Path(f).name) for f in fs]
    if any(s.startswith('kapak-') for s in stems): continue
    pairs.add(tuple(sorted(stems)))
print('mekan cifti:', len(pairs))
for a, b in sorted(pairs):
    pa, pb = f'sevilla:photo:{a}', f'sevilla:photo:{b}'
    ra, rb = fot.get(pa, {}), fot.get(pb, {})
    print('==', a, '<->', b)
    for pid, r in ((pa, ra), (pb, rb)):
        print('  ', pid, 'row', r.get('_row'), 'file', r.get('file'), '| src', r.get('source_url'), '| author', r.get('author'), '| lic', r.get('license'))
        k = kan.get(pid, {})
        print('     kanit src_snap', k.get('source_snapshot_file'), '| lic_snap', k.get('license_snapshot_file'))
    ev = PKG/'Lisans kanıtları'/f'{a}.source-evidence.json'
    try:
        j = json.loads(ev.read_text(encoding='utf-8-sig'))
        s = json.dumps(j, ensure_ascii=False)
        m = re.findall(r'File:[^"\\]{3,90}', s)
        print('   evidence File: refs', sorted(set(m))[:4])
    except Exception as e:
        print('   evidence okunamadi', e)
# fotograf baytlari ayni mi?
sha = {f['path']: f['sha256'] for f in inv['files']}
for a, b in sorted(pairs):
    fa = fot.get(f'sevilla:photo:{a}', {}).get('file'); fb = fot.get(f'sevilla:photo:{b}', {}).get('file')
    print('foto sha ayni?', a, b, sha.get(str(fa).replace('\\', '/')) == sha.get(str(fb).replace('\\', '/')))
