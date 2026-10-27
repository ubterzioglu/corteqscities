import json,glob,sys,re,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
W=r'C:\temp_private\corteqs\0000_newera\uretim\malaga\_is'
want={'saglik':['hamilelik-dogum-ve-cocuk-sagligi-haklari'],'resmi':['libro-de-familia-nedir','registro-civil-ne-ise-yarar','empadronamiento-nedir-neden-gerekir'],'is':['dogum-ve-babalik-izni-sureleri']}
for k,v in want.items():
    for l in open(W+rf'\data\parcalar\Yanıtlar.{k}.jsonl',encoding='utf-8'):
        d=json.loads(l)
        if d['slug'] in v:
            print('=====',d['slug'],d['source_ids']); print(d['summary'][:900]); print('NOTE',d['note'][:400]); print('STEPS',d['steps'][:500])
for p in glob.glob(W+r'\snap_*\*.txt')+glob.glob(W+r'\ulke_paketi\kaynaklar\*.txt'):
    t=open(p,encoding='utf-8',errors='ignore').read()
    for m in re.finditer(r'(?i)(inscri\w+ .{0,120}(ocho|8) d[ií]as|(ocho|8) d[ií]as.{0,120}(nacimiento|inscri))',t):
        print('HIT',p[-60:],m.group(0)[:200])
