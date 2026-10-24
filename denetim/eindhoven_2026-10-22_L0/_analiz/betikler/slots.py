import json,sys
d=json.load(open(sys.argv[1],encoding='utf-8'))
print(type(d).__name__, list(d.keys())[:5] if isinstance(d,dict) else len(d))
sheets=d['sheets'] if isinstance(d,dict) and 'sheets' in d else d
loc={}
for s in sheets:
    name=s.get('file') or s.get('sheet') or s.get('name')
    for it in s.get('items',[]):
        loc[it['key']]=(name,it['slot'])
want=['eindhoven:photo:kapak-0%d'%i for i in range(1,9)]+['eindhoven:photo:van-abbemuseum-03','eindhoven:photo:philips-stadion-psv-02','eindhoven:photo:henri-dunantpark-01','eindhoven:photo:strijp-s-01','eindhoven:photo:klokgebouw-03','eindhoven:photo:18-septemberplein-02','eindhoven:photo:eindhoven-centraal-01','eindhoven:photo:huize-de-laak-01','eindhoven:photo:de-ontdekfabriek-02']
for w in want: print(w, loc.get(w))
print('first sheet keys', list(sheets[0].keys()))
