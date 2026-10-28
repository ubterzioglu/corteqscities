"""Workflow gunlugunden etiket basina durum: bitti / hata / suruyor (+ secili sonuc alanlari).

Kullanim: python akis_durum.py <journal.jsonl> [<alan> ...]
"""
import json
import sys

basladi, sonuc, hata = {}, {}, {}
for satir in open(sys.argv[1], encoding="utf-8"):
    x = json.loads(satir)
    t, aid = x.get("type"), x.get("agentId")
    if t == "started":
        basladi[aid] = x.get("label")
    elif t == "result":
        sonuc[aid] = x.get("result")
    elif t in ("error", "failed"):
        hata[aid] = str(x.get("error") or x)[:120]
alanlar = sys.argv[2:]
for aid, label in basladi.items():
    if aid in sonuc:
        r = sonuc[aid] if isinstance(sonuc[aid], dict) else {}
        ek = {k: r.get(k) for k in alanlar if k in r}
        print(f"BITTI  {label:28s} {json.dumps(ek, ensure_ascii=False)}")
    elif aid in hata:
        print(f"HATA   {label:28s} {hata[aid]}")
    else:
        print(f"YOK    {label:28s} (sonuc yok: hata ya da suruyor)")
