import json
sel = json.load(open('photo_selection.json', encoding='utf-8'))
lines = []
cur = None
for s in sel:
    if s['media_key'] != cur:
        cur = s['media_key']
        lines.append(f"== {cur} ({s['role']})")
    m = s['meta']
    lines.append(f"   {m['title'][:110]} | {m['license']} | {m['author'][:40]}")
open('selection_review.txt', 'w', encoding='utf-8').write('\n'.join(lines))
print('rows:', len(sel))
