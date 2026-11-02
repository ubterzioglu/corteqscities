"""hedefli.py: hedefli L1 (kullanici karari 02.11.2026) - ajan girdilerini 27.10 teslimine (556343a6) gore
degisen/eklenen kayitlara indirir. hazirla_l1/l2 ciktilarini okur, yalniz OUT altina yazar.
Kullanim: python -I -X utf8 hedefli.py <OUT>"""
import collections
import json
import re
import shutil
import sys
from pathlib import Path

OUT = Path(sys.argv[1])


def JL(p: Path) -> list:
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def W(p: Path, rows: list) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


imp = json.loads((OUT / "impact.json").read_text(encoding="utf-8"))
deg = collections.defaultdict(set)
sil = collections.defaultdict(set)
for c in imp["changes"]:
    (sil if c["change"] == "deleted" else deg)[c["sheet"]].add(c["id"])
ozet = {"degisen": {k: len(v) for k, v in deg.items()}, "silinen": {k: sorted(v) for k, v in sil.items()}}

# ---- iddia: degisen Yanit/Sozluk kartlari + degisen kaynaga ya da baglantiya bagli kartlar
yan = {y["entry_id"]: y for y in JL(OUT / "_dump/Yanıtlar.jsonl")}
soz = {s["term_id"]: s for s in JL(OUT / "_dump/Sözlük.jsonl")}
kay = {k["source_id"]: k for k in JL(OUT / "_dump/Kaynaklar.jsonl")}
bag = JL(OUT / "_dump/Bağlantılar.jsonl")
deg_src = deg["Kaynaklar"]
deg_bag_entry = {b["entry_id"] for b in bag if b.get("action_id") in deg["Bağlantılar"]}


def src_ids(row: dict) -> set:
    return {s.strip() for s in re.split(r"[\n;|]", str(row.get("source_ids", ""))) if s.strip()}


kart_sec = set(deg["Yanıtlar"]) | set(deg["Sözlük"])
kart_sec |= {e for e, y in yan.items() if src_ids(y) & deg_src}
kart_sec |= {e for e, s in soz.items() if src_ids(s) & deg_src}
kart_sec |= {e for e in deg_bag_entry if e in yan or e in soz}
results = json.loads((OUT / "claim-script.json").read_text(encoding="utf-8-sig"))["results"]
by_entry = collections.defaultdict(list)
for r in results:
    by_entry[r["entry_id"]].append(r)
index = {r["url"]: r for r in JL(OUT / "kanitlar/snap/index.jsonl")}
sel = sorted(kart_sec, key=lambda e: (yan.get(e, {}).get("topic_id", ""), e))
N = max(1, -(-len(sel) // 11))
parts = [sel[i::N] for i in range(N)]
shutil.rmtree(OUT / "_iddia" / "girdi", ignore_errors=True)
for i, p in enumerate(parts, 1):
    d = OUT / "_iddia" / "girdi" / f"parti_{i:02d}"
    cards, claims, snaps = [], [], {}
    for e in p:
        card = yan.get(e) or soz.get(e)
        cards.append(card)
        for r in by_entry[e]:
            claims.append({k: r.get(k) for k in ("claim_id", "entry_id", "sheet", "_row", "field", "kind", "text", "sentence", "values", "result", "sources")})
        for sid in src_ids(card):
            if sid in kay:
                k = kay[sid]
                ix = index.get(k["url"])
                tf = ix.get("text_file") if ix else None
                snaps.setdefault(k["url"], {"snapshot_id": tf, "source_id": sid, "title": k.get("title"), "file": str(OUT / "kanitlar" / "snap" / tf) if tf else None})
    W(d / "kartlar.jsonl", cards)
    W(d / "iddialar.jsonl", claims)
    W(d / "kaynaklar.jsonl", [{"url": u, **v} for u, v in snaps.items()])
ozet["iddia"] = {"kart": len(sel), "parti": [len(p) for p in parts], "iddia": sum(len(by_entry[e]) for e in sel)}

# ---- mekan + mahalle + rota: degisen kayitlar ya da degisen kaynak/baglanti
g = OUT / "_l" / "girdi"
mek_rows = JL(g / "mekan_A.jsonl") + JL(g / "mekan_B.jsonl")
mek_sec = [m for m in mek_rows if m["entry_id"] in deg["Mekânlar"] or src_ids(m) & deg_src or m["entry_id"] in deg_bag_entry]
mah_sec = [m for m in JL(g / "mahalleler.jsonl") if m["entry_id"] in deg["Mahalleler"] or src_ids(m) & deg_src or m["entry_id"] in deg_bag_entry]
rot_sec = [r for r in JL(g / "rotalar.jsonl") if r["route_id"] in deg["Rotalar"] or src_ids(r) & deg_src]
W(OUT / "_l" / "hedefli" / "mekan.jsonl", mek_sec)
W(OUT / "_l" / "hedefli" / "mahalleler.jsonl", mah_sec)
W(OUT / "_l" / "hedefli" / "rotalar.jsonl", rot_sec)
ozet["mekan"] = len(mek_sec)
ozet["mahalle"] = len(mah_sec)
ozet["rota"] = len(rot_sec)

# ---- foto + lisans: degisen kareler + on elemede flag/reject
dec = json.loads((OUT / "_foto/decisions.json").read_text(encoding="utf-8"))["decisions"]
supheli = {d["candidate_id"] for d in dec if d.get("decision") != "keep"}
foto_sec = set(deg["Fotoğraflar"]) | set(deg["Kanıtlar"]) | set(deg["FotoğrafKaynakları"]) | supheli
items = [r for r in JL(OUT / "_foto/items.jsonl") if r.get("key") in foto_sec]
shutil.rmtree(OUT / "_foto" / "hedefli", ignore_errors=True)
W(OUT / "_foto" / "hedefli" / "items.jsonl", items)
lis = [r for r in JL(g / "lisans_zinciri.jsonl") if r.get("photo_id") in foto_sec]
W(OUT / "_l" / "hedefli" / "lisans_zinciri.jsonl", lis)
ozet["foto"] = {"degisen": len(foto_sec - supheli), "supheli": len(supheli), "pafta_kare": len(items), "lisans": len(lis)}
(OUT / "_analiz" / "hedefli-ozet.json").write_text(json.dumps(ozet, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps(ozet, ensure_ascii=False))
