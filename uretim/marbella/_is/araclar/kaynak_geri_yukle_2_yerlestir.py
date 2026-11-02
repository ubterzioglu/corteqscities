import json,os,shutil,collections
W='/home/user/corteqscities/uretim/marbella/_is'; S=''+__import__('os').environ.get('GERI','/tmp/geri')+''
idx={}
for l in open(S+'/refetch/index.jsonl',encoding='utf-8'):
    d=json.loads(l); idx[d['url']]=d
rows=[json.loads(l) for l in open(W+'/kaynak_dizini.jsonl',encoding='utf-8')]
st=collections.Counter(); failed=[]
for r in rows:
    if os.path.exists(r['text_file']): st['var']+=1; continue
    d=idx.get(r['url'])
    if not d or not d.get('text_file'):
        failed.append({"source_id":r['source_id'],"url":r['url'],"hata":(d or {}).get('error') or (d or {}).get('status')}); continue
    shutil.copy(S+'/refetch/'+os.path.basename(d['text_file']),r['text_file'])
    if r.get('html_file') and d.get('html_file'): shutil.copy(S+'/refetch/'+os.path.basename(d['html_file']),W+'/'+r['html_file'])
    st['ayni' if d.get('html_sha256')==r.get('html_sha256') else 'farkli']+=1
json.dump({"tarih":"2026-11-02","not":"snap_* klasörleri git dışı; bulut oturumu kapanınca kayboldu. ulke/ES kaynakları repodan kopyalandı, kalanlar yeniden indirildi (fetch_snapshot). 'farkli' = sayfa 28-29.10'dakinden farklı (dinamik içerik ya da güncelleme).","sayilar":dict(st),"indirilemeyen":failed},open(W+'/kaynak_geri_yukleme.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
print(dict(st),len(failed))
for f in failed: print(f)
