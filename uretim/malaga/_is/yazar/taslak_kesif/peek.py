import json, glob, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
P = r'C:\temp_private\corteqs\0000_newera\uretim\malaga\_is\data\parcalar'
slugs = []
for f in glob.glob(P + r'\Yanıtlar.*.jsonl'):
    for l in open(f, encoding='utf-8'):
        d = json.loads(l)
        slugs.append((d['slug'], d['title']))
print(len(slugs))
for s in slugs:
    if any(k in (s[0] + s[1]).lower() for k in ('muze', 'müze', 'spor', 'kesif', 'doga', 'plaj', 'cocuk', 'park')):
        print(s)
# sample
f = P + r'\Yanıtlar.gunluk.jsonl'
l = open(f, encoding='utf-8').readline()
print(l)
f = P + r'\Bağlantılar.gunluk.jsonl'
print(open(f, encoding='utf-8').readline())
c = r'C:\temp_private\corteqs\0000_newera\uretim\malaga\_is\claims\gunluk.jsonl'
print(open(c, encoding='utf-8').readline())
print(open(r'C:\temp_private\corteqs\0000_newera\uretim\malaga\_is\yazar\hitap.txt', encoding='utf-8').read())
# kaynak dizini urls
for l in open(r'C:\temp_private\corteqs\0000_newera\uretim\malaga\_is\kaynak_dizini.jsonl', encoding='utf-8'):
    d = json.loads(l)
    if d['source_id'].split(':')[-1] in [str(n) for n in range(275, 292)]:
        print(d['source_id'], d.get('url'), d.get('final_url'))
