import json,os,shutil,re
W='/home/user/corteqscities/uretim/marbella/_is'; U='/home/user/corteqscities/ulke/ES'
rows=[json.loads(l) for l in open(W+'/kaynak_dizini.jsonl',encoding='utf-8')]
ok=0; urls=[]; miss=[]
for r in rows:
    tf=r['text_file']; d=os.path.dirname(tf); os.makedirs(d,exist_ok=True)
    b=os.path.basename(tf)
    m=re.match(r'marbella_kaynak_\d+_(.+)\.txt$',b)
    if m:
        src=m.group(1)
        cand=[U+'/kaynaklar/'+src+'.txt', U+'/bolge/andalucia/kaynaklar/'+src+'.txt']
        c=[x for x in cand if os.path.exists(x)]
        if c:
            shutil.copy(c[0],tf); h=c[0][:-4]+'.html'
            if os.path.exists(h) and r.get('html_file'): shutil.copy(h,W+'/'+r['html_file'])
            ok+=1; continue
        miss.append(b)
    else: urls.append(r['url'])
open(''+__import__('os').environ.get('GERI','/tmp/geri')+'/urls.txt','w').write('\n'.join(dict.fromkeys(urls))+'\n')
print(ok,len(urls),miss[:5],len(miss))
