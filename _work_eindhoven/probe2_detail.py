import json
d = json.load(open('commons_probe2.json', encoding='utf-8'))
for k in ['speeltuin','dierenweide','stroomhuis','tue-metaforum','kanaal2','dommel2','muziekkoepel','sectie-c2','oorlogsmonument','meerhoven-arch','villa-de-laak']:
    v = d.get(k)
    if not v: continue
    print('=====', k)
    for u in v['usable'][:8]:
        print('  -', u['title'][:95], '|', u['license'])
