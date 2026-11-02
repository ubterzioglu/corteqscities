"""Mekan kayitlarini parcalardan cikarir (fotografsiz ya da tekrar mekanin yedekle degistirilmesi; Barış karari).

Kullanim: python sil_mekan.py <_is> <neden> <entry_id> [...]
Once yedek: <_is>/yedek_silinen/<zaman>/; Rotalar, SayfaAlanlari ya da Mahalleler'de kullaniliyorsa hicbirini silmez (cikis 1).
Mekanlar.*, Baglantilar.* ve claims/* satirlarini cikarir; denetim/mekan_degistir_degisiklik.jsonl'e satir yazar.
Tek satir JSON ozet. Cikis 0 tamam, 1 kullanim var, 2 kayit bulunamadi.
"""
import datetime
import json
import pathlib
import shutil
import sys

work, neden, hedef = pathlib.Path(sys.argv[1]), sys.argv[2], set(sys.argv[3:])
parc = work / "data" / "parcalar"


def jl(p):
    return [json.loads(l) for l in p.read_text(encoding="utf-8-sig").splitlines() if l.strip()]


def yaz(p, rows):
    p.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


kullanim = []
for p in list(parc.glob("Rotalar.*.jsonl")) + list(parc.glob("SayfaAlanları.*.jsonl")) + list(parc.glob("Mahalleler.*.jsonl")):
    metin = p.read_text(encoding="utf-8")
    for e in hedef:
        slug = e.split(":", 1)[1]
        if e in metin or f'"{slug}"' in metin:
            kullanim.append(f"{p.name}: {e}")
if kullanim:
    print(json.dumps({"durum": "kullaniliyor", "kullanim": kullanim}, ensure_ascii=False))
    sys.exit(1)
bulunan = {r["entry_id"]: p for p in parc.glob("Mekânlar.*.jsonl") for r in jl(p) if r["entry_id"] in hedef}
if set(bulunan) != hedef:
    print(json.dumps({"durum": "bulunamadi", "eksik": sorted(hedef - set(bulunan))}, ensure_ascii=False))
    sys.exit(2)
yedek = work / "yedek_silinen" / datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
yedek.mkdir(parents=True)
sayi = {"Mekânlar": 0, "Bağlantılar": 0, "claims": 0}
log = []
for p in list(parc.glob("Mekânlar.*.jsonl")) + list(parc.glob("Bağlantılar.*.jsonl")) + list((work / "claims").glob("*.jsonl")):
    rows = jl(p)
    kalan = [r for r in rows if r.get("entry_id") not in hedef]
    if len(kalan) != len(rows):
        shutil.copy2(p, yedek / p.name)
        cikan = [r for r in rows if r.get("entry_id") in hedef]
        anahtar = "claims" if p.parent.name == "claims" else p.name.split(".")[0]
        sayi[anahtar] += len(cikan)
        if anahtar == "Mekânlar":
            log += [{"entry_id": r["entry_id"], "alan": "kayit_silindi", "eski": r.get("title", ""), "yeni": "",
                     "bulgu_claim_id": "mekan_degistir", "gerekce": neden, "alinti": ""} for r in cikan]
        yaz(p, kalan)
with open(work / "denetim" / "mekan_degistir_degisiklik.jsonl", "a", encoding="utf-8") as f:
    f.write("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in log))
print(json.dumps({"durum": "tamam", "silinen": sayi, "yedek": str(yedek)}, ensure_ascii=False))
