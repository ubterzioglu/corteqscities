import json

# rota düzeltmesi
p = 'routes_master.json'
routes = json.load(open(p, encoding='utf-8'))
for r in routes:
    if r['slug'] == 'philips-mirasi':
        r['stops'] = ["philips-museum", "lichttoren", "witte-dame", "de-admirant", "strijp-s", "klokgebouw", "watertoren"]
        r.pop('note', None)
json.dump(routes, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# district title düzeltmesi
p2 = 'districts_master.json'
d = json.load(open(p2, encoding='utf-8'))
for x in d:
    if x['slug'] == 'leenderheide':
        x['title'] = 'Leenderheide'
json.dump(d, open(p2, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# rota durak doğrulaması
places = {pl['slug'] for pl in json.load(open('places_master.json', encoding='utf-8'))}
bad = [(r['slug'], s) for r in routes for s in r['stops'] if s not in places]
print('routes:', len(routes), 'bad stops:', bad)
