"""L1 açık-mı doğrulama satırlarından 'ret' olanları L2 tam örneklemin partilerine taşır.

Kullanım: python -I -X utf8 acikmi_tasima.py <OUT>
Yedek: OUT/_acikmi_l1 (orneklem --tam öncesi kopya). 'onay' (belirsiz) satırları taşınmaz: o mekânlar Opus'la yeniden denenir.
Çıktı: OUT/_acikmi/parti_NN_dogrulama.jsonl (yalnız taşınan satırlar) ve ajan gereken partilerin listesi.
"""
import json
import sys
from pathlib import Path

OUT = Path(sys.argv[1])
YEDEK = OUT / '_acikmi_l1'
rows = {}
for f in sorted(YEDEK.glob('parti_*_dogrulama.jsonl')):
    for line in f.read_text(encoding='utf-8').splitlines():
        if line.strip():
            r = json.loads(line)
            if r.get('sonuc') == 'ret' and r.get('entry_id'):
                rows[r['entry_id']] = r
tasindi, gerekli, toplam = 0, [], 0
for pf in sorted((OUT / '_acikmi').glob('parti_*.jsonl')):
    if '_dogrulama' in pf.name:
        continue
    ids = [json.loads(l)['entry_id'] for l in pf.read_text(encoding='utf-8').splitlines() if l.strip()]
    toplam += len(ids)
    keep = [rows[i] for i in ids if i in rows]
    if keep:
        (OUT / '_acikmi' / f'{pf.stem}_dogrulama.jsonl').write_text(
            ''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in keep), encoding='utf-8')
        tasindi += len(keep)
    if len(keep) < len(ids):
        gerekli.append(pf.stem.split('_')[1])
print(json.dumps({'mekan': toplam, 'ret_satir_l1': len(rows), 'tasindi': tasindi,
                  'yeniden_denenecek': toplam - tasindi, 'ajan_gereken_partiler': gerekli}, ensure_ascii=False))
