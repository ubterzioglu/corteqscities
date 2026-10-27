import json,pathlib,sys
I=pathlib.Path(r"C:\temp_private\corteqs\0000_newera\uretim\malaga\_is")
idx={}
for l in (I/"kaynak_dizini.jsonl").open(encoding="utf-8"):
    if l.strip():
        r=json.loads(l); idx[r["source_id"]]=r
extra={"planlama":["malaga:kaynak:292"]}
topics=sys.argv[1].split(",")
for k in topics:
    ids=[]
    for d in sorted(I.glob("snap_kesif_*")):
        if d.name==f"snap_kesif_{k}" or d.name.startswith(f"snap_kesif_{k}_"):
            e=I/d.name/"eklenen.json"
            if e.exists():
                for sid in json.loads(e.read_text(encoding="utf-8")).get("map",{}).values():
                    if sid not in ids: ids.append(sid)
    for sid in extra.get(k,[]):
        if sid not in ids: ids.append(sid)
    with open(I/"yazar"/f"{k}_kaynaklar.jsonl","w",encoding="utf-8",newline="\n") as f:
        for sid in ids:
            r=idx[sid]; f.write(json.dumps({k2:r.get(k2) for k2 in ("source_id","url","title","publisher","text_file")},ensure_ascii=False)+"\n")
    print(k,len(ids))