import json, glob, os
ROOT = r"C:\temp_private\corteqs\0000_newera\eindhoven_qwen38_max"
rows = []
for f in glob.glob(os.path.join(ROOT, 'Lisans kanıtları', '*.state.json')):
    r = json.load(open(f, encoding='utf-8'))
    if r['photo_id'] == 'eindhoven:foto:kapak-skyline-01':
        r['caption'] = 'Berenkuil kavşağı alt geçidi: duvar resimleri panoraması'
    if r['photo_id'] == 'eindhoven:foto:kapak-evoluon-01':
        r['caption'] = 'Evoluon kubbesi ve Evoluon kulesi'
    json.dump(r, open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    rows.append(r)
# seçim sırasına göre diz
sel = json.load(open('photo_selection.json', encoding='utf-8'))
order = {s['photo_id']: i for i, s in enumerate(sel)}
rows.sort(key=lambda r: order.get(r['photo_id'], 9999))
json.dump(rows, open('photos_rows.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('photos_rows:', len(rows))
