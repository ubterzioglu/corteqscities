import json
probes = {}
for f in ['commons_probe.json', 'commons_probe2.json', 'commons_probe3.json', 'commons_probe_dc.json', 'commons_probe_dc2.json']:
    probes.update(json.load(open(f, encoding='utf-8')))
for k in ['piet-hein-eek', 'genneper-parken', 'strijp-r', 'oranje-rood-hockey', 'sportpark-aalsterweg', 'jan-louwers-stadion', 'mah-binnenstad2']:
    v = probes.get(k)
    print('=====', k)
    if not v:
        continue
    for u in v['usable'][:10]:
        print('  -', u['title'][:95], '| w=', u['width'])
