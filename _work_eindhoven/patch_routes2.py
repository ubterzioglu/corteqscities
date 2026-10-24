import json
p = 'routes_master.json'
routes = json.load(open(p, encoding='utf-8'))
for r in routes:
    if 'piet-hein-eek' in r['stops']:
        r['stops'] = [s for s in r['stops'] if s != 'piet-hein-eek']
json.dump(routes, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('routes fixed')
