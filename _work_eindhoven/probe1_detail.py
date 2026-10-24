import json
d = json.load(open('commons_probe.json', encoding='utf-8'))
for k in ['psv-museum','stadsbrouwerij','usine','kerkdorp-acht','woenselse-watermolen','dommel-eindhoven','kanaal-eindhoven','prinsenjagt','ton-smits-huis','muziekgebouw','cafe-wilhelmina','jan-louwers-stadion','sportpark-aalsterweg','station-eindhoven-centraal','stadskantoor','hoge-herde','w-hal-tue','sint-theresiakerk','philips-observatorium','gemeentelijke-hbs']:
    v = d.get(k)
    if not v:
        print('=====', k, 'NO PROBE'); continue
    print('=====', k, v['usable_count'])
    for u in v['usable'][:5]:
        print('  -', u['title'][:95], '|', u['license'])
