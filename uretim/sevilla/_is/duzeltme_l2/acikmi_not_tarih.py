"""Açık-mı kapısının not_yok bulgusu için biçim düzeltmesi (yeni bilgi yok): iki 'kartta belirt' mekânının note alanına
kartta zaten kaynaklı olarak bulunan durumu "27 Ekim 2026 itibarıyla … (<kaynak adı>)" biçimiyle yazar. Değişiklik
kaydı: denetim/<parça>-d13_degisiklik.jsonl (bulgu_claim_id "acik_mi:not_yok").

Kullanım: python -I -X utf8 acikmi_not_tarih.py <WORK_is>
"""
import json
import sys
from pathlib import Path

IS = Path(sys.argv[1])
YENI = {
    ("mekan3", "sevilla:estadio-benito-villamarin-tur"):
        lambda eski: "27 Ekim 2026 itibarıyla tur Benito Villamarín'de değil, Real Betis'in şu anki evi Estadio La Cartuja'da yapılıyor "
                     "(Real Betis'in resmî tur sayfası). " + eski,
    ("mekan6", "sevilla:hospital-de-los-venerables"):
        lambda eski: "27 Ekim 2026 itibarıyla binanın ziyaret gün ve saatleri resmî duyurularda yer almıyor; kilisesi (Iglesia del Hospital "
                     "de los Venerables Sacerdotes) Cabildo Catedral'in duyurusuyla 30 Haziran 2026'ya kadar olağanüstü olarak ziyarete "
                     "açık kalmıştı (Cabildo Catedral de Sevilla).",
}
for (parca, eid), yap in YENI.items():
    p = IS / "data" / "parcalar" / f"Mekânlar.{parca}.jsonl"
    rows = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
    hit = [r for r in rows if r.get("entry_id") == eid]
    if len(hit) != 1:
        sys.exit(f"kayıt bulunamadı: {eid}")
    r = hit[0]
    eski = r.get("note") or ""
    if "itibarıyla" in eski:
        print("zaten tarihli:", eid)
        continue
    r["note"] = yap(eski)
    p.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in rows), encoding="utf-8")
    with (IS / "denetim" / f"{parca}-d13_degisiklik.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps({"entry_id": eid, "alan": "note", "eski": eski, "yeni": r["note"], "bulgu_claim_id": "acik_mi:not_yok",
                            "gerekce": "Açık-mı kapısı (acik-mi.md §5): 'kartta belirt' kartında kontrol yılı tarihli '… itibarıyla' notu "
                                       "zorunlu; kartta zaten kaynaklı olan durum tarihli biçimde yazıldı, yeni bilgi eklenmedi.",
                            "alinti": ""}, ensure_ascii=False) + "\n")
    print("güncellendi:", eid)
