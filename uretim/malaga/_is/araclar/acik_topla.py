"""Workflow sonuclarindaki 'open' notlarini toplar (acik konular icin ham liste).

Kullanim: python acik_topla.py <out.jsonl> <journal.jsonl> ...
Satir: {part, label, not}. '-I' komut notlari (ana dongu istem hatasi) ayiklanir. Tek satir JSON ozet.
"""
import collections
import json
import sys

out, sayi = [], collections.Counter()
for j in sys.argv[2:]:
    etiket = {}
    for satir in open(j, encoding="utf-8"):
        x = json.loads(satir)
        if x.get("type") == "started":
            etiket[x.get("agentId")] = x.get("label")
        if x.get("type") != "result" or not isinstance(x.get("result"), dict):
            continue
        r = x["result"]
        for n in r.get("open") or []:
            if "-I" in n and ("common" in n or "modül" in n or "modul" in n):
                continue
            out.append({"part": r.get("part"), "label": etiket.get(x.get("agentId")), "not": n})
            sayi[r.get("part")] += 1
open(sys.argv[1], "w", encoding="utf-8").write("".join(json.dumps(o, ensure_ascii=False) + "\n" for o in out))
print(json.dumps({"not": len(out), "parca": dict(sayi)}, ensure_ascii=False))
