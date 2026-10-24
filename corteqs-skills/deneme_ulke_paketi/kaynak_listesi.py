import json,sys
W,t=sys.argv[1],sys.argv[2]
idx={}
for l in open(f"{W}/kaynak_dizini.jsonl",encoding="utf-8"):
    r=json.loads(l); idx[r["url"]]=r
ok=json.load(open(f"{W}/snap_kesif_{t}/eklenen.json",encoding="utf-8"))["map"]
out=[]
for l in open(f"{W}/kesif/{t}/selected.jsonl",encoding="utf-8"):
    r=json.loads(l); sid=ok.get(r["url"])
    if not sid: continue
    i=idx[r["url"]]
    out.append({"source_id":sid,"cards":r["cards"],"url":r["url"],"title":i["title"],"publisher":i["publisher"],"lang":i.get("lang"),"text_file":i["text_file"],"must_contain":r["must_contain"],"why":r["why"]})
with open(f"{W}/yazar/{t}_kaynaklar.jsonl","w",encoding="utf-8",newline="\n") as f:
    for o in out: f.write(json.dumps(o,ensure_ascii=False)+"\n")
print(t,len(out))
