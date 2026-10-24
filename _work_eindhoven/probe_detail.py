import json, sys
f = sys.argv[1] if len(sys.argv) > 1 else 'commons_probe3.json'
keys = sys.argv[2:] if len(sys.argv) > 2 else None
d = json.load(open(f, encoding='utf-8'))
for k, v in d.items():
    if keys and k not in keys:
        continue
    print('=====', k, v['usable_count'])
    for u in v['usable'][:6]:
        print('  -', u['title'][:95], '|', u['license'])
