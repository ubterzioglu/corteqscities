import json,glob,sys,re,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
W=r'C:\temp_private\corteqs\0000_newera\uretim\malaga\_is'
for f in sorted(glob.glob(W+r'\data\parcalar\Yanıtlar.*.jsonl')):
    for l in open(f,encoding='utf-8'):
        d=json.loads(l); print(f.split('.')[-2], d['order'], d['slug'],'|',d['title'][:80])
print('----dizin')
for l in open(W+r'\kaynak_dizini.jsonl',encoding='utf-8'):
    d=json.loads(l)
    tf=d.get('text_file','')
    if re.search(r'nacimiento|natalidad|bebe|recién|infantil|familia|escolar|padr',d.get('url','')+d.get('title',''),re.I):
        print(d['source_id'],d['url'],'|',d.get('title','')[:70])
