import json, os, glob

ROOT = r"C:\temp_private\corteqs\0000_newera\eindhoven_qwen38_max"
sel = json.load(open('photo_selection.json', encoding='utf-8'))
removed = 0
for s in sel:
    key = s['file'].split('/')[-1]
    sp = os.path.join(ROOT, 'Lisans kanıtları', key + '.state.json')
    if os.path.exists(sp):
        st = json.load(open(sp, encoding='utf-8'))
        if st.get('commons_title') != s['meta']['title']:
            for pat in [key + '.state.json', key + '.source-evidence.json', key + '.license-record.json']:
                p = os.path.join(ROOT, 'Lisans kanıtları', pat)
                if os.path.exists(p):
                    os.remove(p)
            for p in glob.glob(os.path.join(ROOT, 'Lisans kanıtları', 'orijinaller', key + '.*')):
                os.remove(p)
            for p in glob.glob(os.path.join(ROOT, 'Fotoğraflar', key + '.*')):
                os.remove(p)
            removed += 1
            print('cleaned', key, '->', s['meta']['title'][:60])
print('cleaned total:', removed)
