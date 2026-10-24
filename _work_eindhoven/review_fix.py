import json
sel = json.load(open('photo_selection.json', encoding='utf-8'))
check = ['de-bergen-horeca','philips-stadion','effenaar','parktheater','hightech-campus','herdgang',
 'tue-auditorium','winkelcentrum-woensel','porthos-toren','philips-nederland-gebouw',
 'oorlogsmonument-fellenoord','bevrijdingsmonument','genneper-parken','oude-toren-woensel',
 'grote-markt','mah-oud-gestel','kapak-glow','kapak-doga','kapak-strijps','kapak-merkez',
 'mu-arthouse','kazerne-design','strijp-s','haftalik-pazarlar','vershal-het-veem','w-hal-tue',
 'tue-atlas','molen-annemie','watertoren','catharinaplein','sportpark-aalsterweg','cafe-wilhelmina',
 'design-academy','strijp-s-markt-weekly','oude-toren','18-septemberplein']
lines = []
for s in sel:
    if s['media_key'] in check:
        lines.append(f"{s['media_key']:30s} {s['role']:6s} {s['meta']['title'][:105]}")
print('\n'.join(lines))
