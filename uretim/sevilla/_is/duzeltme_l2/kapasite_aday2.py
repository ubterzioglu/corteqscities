"""Gerçekten boşaltılabilir kaynak adayları (merge_package sayımıyla): kaynak = kayıtların source_ids'i ∪ Bağlantılar
adresleri. Aday: tek kayıtta kullanılan, kaydın başka kaynağı olan, ≤4 iddiaya dayanak kaynak. Bağlantı satırı bu
kaynağın adresini kullanıyorsa, satır kaydın başka bir kaynağının adresine çevrilmeli ya da (kaydın başka bağlantısı
varsa) silinmeli; bu bilgi satıra yazılır. Turizm portalı ve bağlantısız olanlar önce.
Çıktı: duzeltme_l2/kapasite_aday2.jsonl. Yalnız okur + o dosyayı yazar.

Kullanım: python -I -X utf8 kapasite_aday2.py <WORK_is>
"""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

IS = Path(sys.argv[1])
P = IS / "data" / "parcalar"
TUR_RX = re.compile(r"visitasevilla|turismo|andalucia\.org|spain\.info", re.I)


def jl(p: Path) -> list:
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def ids(v) -> list:
    return [s.strip() for s in re.split(r"[\n;|]", str(v or "")) if s.strip()]


kd = {r["source_id"]: r for r in jl(IS / "kaynak_dizini.jsonl")}
url2src = {str(r.get("url", "")).strip(): s for s, r in kd.items()}
users = defaultdict(list)          # kaynak -> [(parça, kayıt)]
rec_src = {}                       # kayıt -> kaynaklar
links = defaultdict(list)          # kayıt -> [(action_id, url, kaynak)]
for p in sorted(P.glob("*.jsonl")):
    parca = p.name.split(".")[1]
    if p.name.startswith("Bağlantılar"):
        for r in jl(p):
            links[r.get("entry_id")].append((r.get("action_id"), r.get("url"), url2src.get(str(r.get("url", "")).strip())))
        continue
    for r in jl(p):
        if "source_ids" not in r:
            continue
        rid = r.get("entry_id") or r.get("term_id") or r.get("route_id")
        rec_src[rid] = ids(r["source_ids"])
        for s in rec_src[rid]:
            users[s].append((parca, rid))
link_users = defaultdict(set)
for rid, ls in links.items():
    for _, _, s in ls:
        if s:
            link_users[s].add(rid)
cl = defaultdict(list)
for p in (IS / "claims").glob("*.jsonl"):
    for c in jl(p):
        cl[c.get("source_id")].append({"claim_id": c.get("claim_id"), "field": c.get("field"), "claim": str(c.get("claim"))[:140]})
rows = []
for s, us in users.items():
    if len(us) != 1:
        continue
    parca, rid = us[0]
    if link_users.get(s, set()) - {rid}:
        continue  # başka kaydın bağlantısı bu adresi kullanıyor
    diger = [x for x in rec_src.get(rid, []) if x != s]
    if not diger or len(cl.get(s, [])) > 4:
        continue
    bag = [a for a, _, src in links.get(rid, []) if src == s]
    diger_bag = [a for a, _, src in links.get(rid, []) if src != s]
    url = str((kd.get(s) or {}).get("url", ""))
    rows.append({"parca": parca, "source_id": s, "url": url, "kayit": rid, "kaydin_diger_kaynaklari": diger,
                 "iddia_sayisi": len(cl.get(s, [])), "turizm": bool(TUR_RX.search(url)),
                 "bu_adresi_kullanan_baglanti": bag, "kaydin_diger_baglantilari": len(diger_bag), "iddialar": cl.get(s, [])})
rows.sort(key=lambda r: (not r["turizm"], bool(r["bu_adresi_kullanan_baglanti"]), r["iddia_sayisi"]))
(IS / "duzeltme_l2" / "kapasite_aday2.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
print(json.dumps({"aday": len(rows), "baglantisiz": sum(1 for r in rows if not r["bu_adresi_kullanan_baglanti"]),
                  "turizm": sum(r["turizm"] for r in rows), "parca": dict(Counter(r["parca"] for r in rows)),
                  "parca_baglantisiz": dict(Counter(r["parca"] for r in rows if not r["bu_adresi_kullanan_baglanti"]))},
                 ensure_ascii=False))
