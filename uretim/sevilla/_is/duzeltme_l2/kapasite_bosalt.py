"""Kaynak kapasitesi (≤500): iddia defterinde hiç kullanılmayan ve kaydın başka kaynağı bulunan kaynakları kayıtların
source_ids'inden çıkarır (city-pack KUR kuralı: "iddiası olmayan kaynaklar (kaydın başka kaynağı varsa) kayıtlardan çıkarılır").

Kullanım: python -I -X utf8 kapasite_bosalt.py <WORK_is> <hedef_bosaltma> [--uygula]
Önce turizm portalı ve yeni eklenmemiş kaynaklar seçilir. Değişiklik kaydı: denetim/<parça>-d11_degisiklik.jsonl (bulgu_claim_id "kapasite").
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

IS, HEDEF = Path(sys.argv[1]), int(sys.argv[2])
UYGULA = "--uygula" in sys.argv
P = IS / "data" / "parcalar"
claim_src = defaultdict(int)
for p in (IS / "claims").glob("*.jsonl"):
    for l in p.read_text(encoding="utf-8").splitlines():
        if l.strip():
            c = json.loads(l)
            for k in ("source_id", "source_ids"):
                for s in re.split(r"[\n;|,]", str(c.get(k) or "")):
                    if s.strip():
                        claim_src[s.strip()] += 1
url = {}
for l in (IS / "kaynak_dizini.jsonl").read_text(encoding="utf-8").splitlines():
    if l.strip():
        r = json.loads(l)
        url[r["source_id"]] = r.get("url", "")
# kayıt -> kaynaklar, kaynak -> kayıtlar
recs = {}
users = defaultdict(set)
for p in sorted(P.glob("*.jsonl")):
    if p.name.startswith(("Fotoğraf", "Kanıtlar", "FotoğrafKaynakları", "Bağlantılar", "Adımlar")):
        continue
    rows = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
    for i, r in enumerate(rows):
        if "source_ids" not in r:
            continue
        rid = r.get("entry_id") or r.get("term_id") or r.get("route_id") or r.get("field_id") or r.get("key") or f"{p.name}#{i}"
        srcs = [s.strip() for s in re.split(r"[\n;|]", str(r.get("source_ids") or "")) if s.strip()]
        recs[(p.name, i, rid)] = srcs
        for s in srcs:
            users[s].add((p.name, i, rid))
used = set(users) | set(claim_src)
aday = []
for s, us in users.items():
    if claim_src.get(s):
        continue
    if all(len(recs[u]) >= 2 for u in us):
        sira = (0 if re.search(r"visitasevilla|turismo|andalucia\.org", url.get(s, ""), re.I) else 1, int(s.split(":")[-1]) if s.split(":")[-1].isdigit() else 0)
        aday.append((sira, s, sorted(us)))
aday.sort()
secilen = aday[:HEDEF]
print(json.dumps({"kullanilan": len(used), "aday": len(aday), "secilen": len(secilen)}, ensure_ascii=False))
for _, s, us in secilen:
    print(s, url.get(s, "")[:90], "|", ", ".join(u[2].split(":")[-1] for u in us))
if UYGULA and secilen:
    cikar = defaultdict(set)
    for _, s, us in secilen:
        for (fname, i, rid) in us:
            cikar[(fname, i, rid)].add(s)
    by_file = defaultdict(dict)
    for (fname, i, rid), ss in cikar.items():
        by_file[fname][i] = (rid, ss)
    for fname, edits in by_file.items():
        p = P / fname
        rows = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
        parca = fname.split(".")[1]
        logp = IS / "denetim" / f"{parca}-d11_degisiklik.jsonl"
        log = []
        for i, (rid, ss) in edits.items():
            eski = rows[i]["source_ids"]
            sep = ";" if ";" in str(eski) else ("\n" if "\n" in str(eski) else ";")
            kalan = [x.strip() for x in re.split(r"[\n;|]", str(eski)) if x.strip() and x.strip() not in ss]
            rows[i]["source_ids"] = sep.join(kalan)
            log.append({"entry_id": rid, "alan": "source_ids", "eski": eski, "yeni": rows[i]["source_ids"], "bulgu_claim_id": "kapasite",
                        "gerekce": "Kaynaklar sekmesi kapasitesi 500: iddia defterinde dayanağı olmayan kaynak, kaydın başka kaynağı olduğu için çıkarıldı (KUR kapasite kuralı).", "alinti": ""})
        p.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
        with logp.open("a", encoding="utf-8") as f:
            for x in log:
                f.write(json.dumps(x, ensure_ascii=False) + "\n")
    print("uygulandı:", {k: len(v) for k, v in by_file.items()})
