"""Foto adim 6: inceleme secimlerini foto/selected.jsonl'de birlestirir (skill photos 6; pilot kurallari).

Kullanim: python foto_secim_birlestir.py <_is> [--ust 3]
- selected_*.jsonl: verify varsa yalniz ok:true (caption_fix varsa o alt yazi); verify yoksa (ana dongu incelemesi) alinir.
- Kayit foto/venues.jsonl (ve foto_*/venues.jsonl) icinde olmali (silinen mekanin karesi duser).
- Kayit basina en cok --ust kare; ayni Commons dosyasi iki kayda verilmez.
- Hak zinciri on kontrolu (K71/K72): dis kaynaktan aktarilmis (Flickr, Panoramio, PxHere, 500px, Pixabay) ve inceleme
  etiketi (FlickreviewR, LicenseReview, reviewed) yoksa kare secilmez.
- Ayni kayitta onizleme dHash farki <=5 olan ikinci kare atilir (image_hash.dhash).
- covers.jsonl kapaklari eklenir. Tek satir JSON ozet (venue_photos, covers, entries_with_photo, dropped).
"""
import collections
import json
import pathlib
import re
import sys

sys.path.insert(0, r"C:\temp_private\corteqs\0000_newera\corteqs-skills\toolkit\scripts")
import image_hash  # noqa: E402

work = pathlib.Path(sys.argv[1])
ust = int(sys.argv[sys.argv.index("--ust") + 1]) if "--ust" in sys.argv else 3
inc = work / "foto" / "inceleme"


def jl(p):
    return [json.loads(l) for l in p.read_text(encoding="utf-8-sig").splitlines() if l.strip()] if p.is_file() else []


kayit = set()
for p in [work / "foto" / "venues.jsonl", *work.glob("foto_*/venues.jsonl")]:
    kayit |= {r["entry_id"] for r in jl(p) if r.get("role") in ("venue", "district")}
mekan_simdi = {r["entry_id"] for p in (work / "data" / "parcalar").glob("Mekânlar.*.jsonl") for r in jl(p)} | \
              {r["entry_id"] for p in (work / "data" / "parcalar").glob("Mahalleler.*.jsonl") for r in jl(p)}
aday = {}
for p in [work / "foto" / "candidates.jsonl", *work.glob("foto_*/candidates.jsonl")]:
    for c in jl(p):
        aday[c["candidate_id"]] = c
onizleme = {}
for p in [*(work / "foto").glob("tur*/items.jsonl"), *work.glob("foto_*/**/items.jsonl")]:
    for r in jl(p):
        k = r.get("key") or r.get("candidate_id")
        yol = r.get("preview") or r.get("path") or r.get("preview_path")
        if k and yol:
            onizleme[k] = yol
dogrula = {}
for p in inc.glob("verify_*.jsonl"):
    for r in jl(p):
        dogrula[r["key"]] = r
DIS = re.compile(r"flickr|panoramio|pxhere|500px|pixabay", re.I)
INCELEME = re.compile(r"flickrevie|licensereview|license review|reviewed|panoramio_review|flickreview", re.I)
dusen = collections.Counter()
secilen, sayi, dosya, hashler = [], collections.Counter(), set(), collections.defaultdict(list)
for p in sorted(inc.glob("selected_*.jsonl")):
    for r in jl(p):
        k, e = r["key"], r["entry_id"]
        v = dogrula.get(k)
        if v is not None and not v.get("ok"):
            dusen["ikinci_goz_red"] += 1
            continue
        if e not in kayit or e not in mekan_simdi:
            dusen["kayit_yok"] += 1
            continue
        if sayi[e] >= ust:
            dusen["ust_sinir"] += 1
            continue
        cf = k.split("|", 1)[1]
        if cf in dosya:
            dusen["ayni_dosya"] += 1
            continue
        c = aday.get(k, {})
        iz = " ".join(str(c.get(x, "")) for x in ("credit_text", "usage_terms", "author_text", "description_text", "categories"))
        if DIS.search(iz) and not INCELEME.search(iz):
            dusen["hak_zinciri"] += 1
            continue
        h = None
        if k in onizleme and pathlib.Path(onizleme[k]).is_file():
            try:
                h = image_hash.dhash(onizleme[k])
            except Exception:  # bozuk onizleme: dHash kontrolu atlanir
                h = None
        if h is not None and any(image_hash.hamming(h, o) <= 5 for o in hashler[e]):
            dusen["yakin_kopya"] += 1
            continue
        if h is not None:
            hashler[e].append(h)
        alt = (v or {}).get("caption_fix") or r.get("caption")
        secilen.append({"key": k, "entry_id": e, "role": "Mekân", "caption": alt, "seen": r.get("seen", "")})
        sayi[e] += 1
        dosya.add(cf)
kapak = 0
for r in jl(inc / "covers.jsonl"):
    secilen.append({"key": r["key"], "entry_id": "", "role": "Kapak", "caption": r["caption"], "seen": r.get("seen", "")})
    kapak += 1
(work / "foto" / "selected.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in secilen), encoding="utf-8")
fotosuz = sorted(e for e in mekan_simdi if sayi[e] == 0)
print(json.dumps({"venue_photos": sum(sayi.values()), "covers": kapak, "entries_with_photo": len(sayi),
                  "dropped": dict(dusen), "fotosuz": fotosuz}, ensure_ascii=False))
