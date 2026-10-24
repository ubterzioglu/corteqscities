import json

p = 'places_master.json'
places = json.load(open(p, encoding='utf-8'))

# Doğrulanmış adresler (resmî sitelerden/monument listesinden)
VERIFIED_ADDR = {
 'philips-museum': 'Emmasingel 31, 5611 AZ Eindhoven',
 'daf-museum': 'Tongelresestraat 27, 5613 DA Eindhoven',
 'kazerne-design': 'Paradijslaan 2-8, 5611 KN Eindhoven',
 'van-abbemuseum': 'Bilderdijklaan 10, 5611 MN Eindhoven',
 'stadskantoor': 'Stadhuisplein 1A, 5611 EM Eindhoven',
 'lichttoren': 'Mathildelaan 1, 5611 EK Eindhoven',
 'design-academy': 'Emmasingel 14, 5611 AZ Eindhoven',
 'cafe-100-watt': 'Bleekweg 1, 5611 EZ Eindhoven',
 'hightech-campus': 'High Tech Campus 1, 5656 AE Eindhoven',
 'tue-atlas': 'Groene Loper 5, 5612 AZ Eindhoven',
 'muziekgebouw': 'Lichttorenallee 50, 5611 BX Eindhoven',
 'eindhoven-airport-terminal': 'Luchthavenweg 25, 5657 EA Eindhoven',
 'philips-stadion': 'Frederiklaan 10A, 5616 NH Eindhoven',
}
MON_ADDR = {
 'klooster-marienhage': 'Augustijnendreef 15, 5611 GB Eindhoven',
 'molen-annemie': 'Boschdijk 1006, 5625 JC Eindhoven',
 'genneper-watermolen': 'Genneperweg 143, 5644 RD Eindhoven',
 'collse-watermolen': 'Collseweg 3-5, 5645 TL Eindhoven',
 'sint-petruskerk': 'Kloosterdreef 29, 5625 JW Eindhoven',
 'sint-lambertuskerk': 'Hoogstraat 84, 5654 CA Eindhoven',
 'steentjeskerk': 'Sint Antoniusstraat 5-9, 5611 EB Eindhoven',
 'heilig-hartkerk': 'Ploegstraat 1-3, 5623 NC Eindhoven',
 'sint-theresiakerk': 'Carmelitessenstraat 2, 5654 GA Eindhoven',
 'sint-martinuskerk': "'t Hofke 1, 5641 RA Eindhoven",
 'paterskerk': 'Tramstraat 37, 5611 EB Eindhoven',
 'clarissenklooster': 'Sint Claralaan 1, 5623 KC Eindhoven',
 'philips-observatorium': 'Alberdingk Thijmlaan 3, 5615 BB Eindhoven',
 'van-maerlantlyceum': 'Jacob van Maerlantlaan 11, 5614 LB Eindhoven',
 'gemeentelijke-hbs': 'Julianastraat 2, 5611 AN Eindhoven',
 'st-joriscollege': 'Elzentlaan 20, 5613 CS Eindhoven',
 'w-hal-tue': 'Den Dolech 2, 5612 AZ Eindhoven',
 'nutsschool-reigerlaan': 'Reigerlaan 3, 5614 NE Eindhoven',
 'mennen-poortgebouw': 'Bergstraat 26-30, 5611 JX Eindhoven',
 'kasteel-eckart': 'Nuenenseweg 1, 5641 LR Eindhoven',
 'sint-joriskerk': 'Sint Jorislaan 53, 5613 AZ Eindhoven',
 'oude-toren-woensel': 'Oude Torenstraat 1, 5625 EG Eindhoven',
 'sint-catharinakerk': 'Catharinaplein 1? / Hooghuisstraat 8, 5611 GW Eindhoven',
}

for pl in places:
    s = pl['slug']
    if s in VERIFIED_ADDR:
        pl['addr'] = VERIFIED_ADDR[s]
    elif s in MON_ADDR:
        pl['addr'] = MON_ADDR[s]
    else:
        a = pl.get('addr')
        if not a or '(kontrol)' in a or '?' in a:
            pl.pop('addr', None)

# Catharinakerk adresini monument listesinden düzelt (Catharinaplein 1)
for pl in places:
    if pl['slug'] == 'sint-catharinakerk':
        pl['addr'] = 'Hooghuisstraat 8, 5611 GW Eindhoven'
    if pl['slug'] == 'watertoren':
        pl.pop('addr', None)
    if pl['slug'] == 'raadhuis-tongelre':
        pl.pop('addr', None)

json.dump(places, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('cleaned', len(places), 'places')
groups = {}
for pl in places:
    groups[pl['group']] = groups.get(pl['group'], 0) + 1
print(groups)
