"""Acceptance: decisions.json + audit ground truth -> confusion table (by photo_index)."""
import json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
acc = Path(sys.argv[1])
cands = {json.loads(l)['candidate_id']: json.loads(l) for l in (acc / 'candidates.jsonl').read_text(encoding='utf-8').splitlines() if l.strip()}
dec = json.loads((acc / 'decisions.json').read_text(encoding='utf-8'))
by_idx = {cands[d['candidate_id']]['photo_index']: d for d in dec['decisions']}
GT = {
    'wrong': [255, 258, 22, 136, 26, 28, 168, 236, 156, 158, 232, 233, 240, 241, 2, 148, 149, 162, 164, 140, 247, 248, 249],
    'archive': [27, 53, 54, 55, 169, 170, 269, 270],
    'lowres': [1, 12, 19, 57, 65, 82, 86, 87, 88, 143, 146, 147, 205],
    'rights': [4, 43, 44, 45, 49, 50, 51, 79, 80, 111, 112, 260, 261],
}
labelled = {i for v in GT.values() for i in v}
GT['good'] = sorted(set(by_idx) - labelled)
expected_code = {'archive': 'archive', 'lowres': ('low_resolution', 'panorama'), 'rights': 'rights_review'}
rows = []
for cat, ids in GT.items():
    r = sum(by_idx[i]['decision'] == 'reject' for i in ids)
    f = sum(by_idx[i]['decision'] == 'flag' for i in ids)
    k = sum(by_idx[i]['decision'] == 'keep' for i in ids)
    extra = ''
    if cat in expected_code:
        codes = expected_code[cat] if isinstance(expected_code[cat], tuple) else (expected_code[cat],)
        extra = f" right_code={sum(any(c in by_idx[i]['reasons'] for c in codes) for i in ids)}"
    rows.append(f"{cat:8} n={len(ids):3} reject={r:3} flag={f:3} keep={k:3}{extra}")
print('\n'.join(rows))
mode = sys.argv[2] if len(sys.argv) > 2 else ''
show = {'wrong': GT['wrong'], 'good': [i for i in GT['good'] if by_idx[i]['decision'] != 'keep']}
for cat in (['wrong', 'good'] if mode == 'v' else ['wrong']):
    print(f'--- {cat}')
    for i in show[cat]:
        d = by_idx[i]
        if cat == 'good' or d['decision'] == 'keep' or mode == 'v':
            print(f"#{i} {d['decision']} {d['reasons']} | {cands[d['candidate_id']]['title'][:70]}")
summary = {cat: {k: sum(by_idx[i]['decision'] == k for i in ids) for k in ('reject', 'flag', 'keep')} for cat, ids in GT.items()}
review = sum(1 for d in dec['decisions'] if d['decision'] == 'flag')
(acc / 'acceptance_confusion.json').write_text(json.dumps({'confusion': summary, 'flagged_to_visual_review': review,
    'shortlist_entries': len(dec['shortlists'])}, indent=2), encoding='utf-8')
