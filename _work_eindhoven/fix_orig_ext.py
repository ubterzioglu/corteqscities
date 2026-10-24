import json, glob, os, urllib.parse

ROOT = r"C:\temp_private\corteqs\0000_newera\eindhoven_qwen38_max"
fixed = 0
for f in glob.glob(os.path.join(ROOT, 'Lisans kanıtları', '*.state.json')):
    r = json.load(open(f, encoding='utf-8'))
    rel = r['orig_rel']
    if '?' in rel or '&' in rel:
        base = rel.rsplit('.', 1)[0]
        path = urllib.parse.urlparse(r['orig_url']).path
        ext = os.path.splitext(path)[1].lower() or '.jpg'
        new_rel = base + ext
        old_abs = os.path.join(ROOT, rel.replace('/', os.sep))
        new_abs = os.path.join(ROOT, new_rel.replace('/', os.sep))
        if os.path.exists(old_abs):
            os.replace(old_abs, new_abs)
            r['orig_rel'] = new_rel
            json.dump(r, open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
            fixed += 1
print('renamed originals:', fixed)
