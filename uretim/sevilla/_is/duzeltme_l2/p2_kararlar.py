"""L2 denetiminin 29 P2 bulgusu için _is/duzeltme_kararlari.jsonl yazar ({issue_id, karar, neden}).
"yapıldı" yalnız değişiklik kaydı ya da teslim zinciri adımıyla kapanan bulgularda; kısmen yapılanlarda kapanan kayıtlar
nedene yazılır, karar "ertelendi" kalır.

Kullanım: python -I -X utf8 p2_kararlar.py <WORK_is>
"""
import json
import sys
from pathlib import Path

IS = Path(sys.argv[1])
KAPSAM = ("Kullanıcı kararı (26.10.2026 ~23:00): bu düzeltme turu 15 P1 ile script'le kapanan P2'lerle sınırlı, teslim "
          "bekleniyor; bulgu okuru yanıltmıyor (P2). Sonraki sürümde (v002) ele alınacak.")
K = {
    "ISS-003": ("yapıldı", "d11: ciudad-de-los-ninos-prado ayrı mekân olmadığı için silindi, bilgisi Prado kartına katıldı; yerine Parque de los Bermejales eklendi (d12 denetimi ve düzeltmesi dahil)."),
    "ISS-004": ("ertelendi", "12 mekânın 2'si (plaza-nueva, iglesia-de-santa-marina) d11/d12'de düzeltildi; kalan 10 mekân: " + KAPSAM),
    "ISS-005": ("ertelendi", KAPSAM),
    "ISS-006": ("ertelendi", KAPSAM),
    "ISS-007": ("ertelendi", KAPSAM),
    "ISS-008": ("ertelendi", "route:003'ün Costurero durağı notu d11'de düzeltildi; kalan 10 rotanın gözlemleri: " + KAPSAM),
    "ISS-009": ("ertelendi", KAPSAM),
    "ISS-010": ("ertelendi", "archivo-general-de-indias ve parque-magallanes yalnız kaynak kapasitesi işinde değişti (bağlantı bulgusu için değil); " + KAPSAM),
    "ISS-011": ("ertelendi", KAPSAM),
    "ISS-012": ("ertelendi", KAPSAM),
    "ISS-013": ("ertelendi", KAPSAM),
    "ISS-014": ("ertelendi", KAPSAM),
    "ISS-015": ("ertelendi", KAPSAM),
    "ISS-016": ("ertelendi", "Ana sayfa/yönlenen 47 kaynağın derin sayfa karşılığı kaynak kapasitesi (500) dolu olduğundan bu turda eklenmedi; " + KAPSAM),
    "ISS-017": ("ertelendi", KAPSAM),
    "ISS-018": ("ertelendi", KAPSAM),
    "ISS-022": ("yapıldı", "d11: doğum sonrası kartında ikamet ve başka zorunlu kapsam olmaması şartı yararlanıcıya (bebeğe) taşındı; d12 denetiminde bu bulgu yeniden çıkmadı (kartın öteki d12 bulguları d12 düzeltmesinde)."),
    "ISS-023": ("yapıldı", "d11: Sözlük term:052 ve mavi bölge kartı resmî kaynakla düzeltildi; d12 denetimi term:052'yi temiz, mavi bölge kartının iddialarını kaynakla birebir buldu (kalan hafif K26 bulgusu d12 düzeltmesinde)."),
    "ISS-025": ("ertelendi", "Mavi bölge kartı d11'de yeniden yazıldı (d12 denetiminde K25 bulgusu yok); sevilla-cevresi-dos-hermanas-alcala-rinconada-saglik-bolgeleri: " + KAPSAM),
    "ISS-027": ("ertelendi", "42 kartın 6'sı d11/d12'de değişti (3'ü tekrar kümesinde silindi); kalan 36 kartta kaynakta olmayan K26 öğesi: " + KAPSAM),
    "ISS-029": ("ertelendi", "Bisiklet/scooter ve mavi bölge kartları d11/d12'de düzeltildi; kalan 5 kart: " + KAPSAM),
    "ISS-030": ("ertelendi", "ZBE kartı d11/d12'de düzeltildi, iki kart tekrar kümesinde silindi; kalan 3 kart: " + KAPSAM),
    "ISS-032": ("ertelendi", "Havalimanı kartı d11'de düzeltildi, metro ve ikinci havalimanı kartı tekrar kümesinde silindi; kalan 3 kart: " + KAPSAM),
    "ISS-035": ("ertelendi", "P1 tekrar kümeleri (ISS-034) d11'de kapatıldı; bu bulgudaki 25 kartın 2'si d11/d12'de değişti; kalan küçük tekrarlar: " + KAPSAM),
    "ISS-037": ("ertelendi", "auditorio-cartuja-sevilla-01 karesi kaydı gösteriyor ama şüpheli işaretli; değiştirme ve kırpma kararı önizlemede (city-preview). " + KAPSAM),
    "ISS-041": ("ertelendi", KAPSAM),
    "ISS-042": ("yapıldı", "Teslim zincirinde artik_kanit_temizle: Excel'de karşılığı olmayan lisans kanıtı dosyaları paketten çıkarıldı."),
    "ISS-043": ("yapıldı", "Teslimat.updated_on teslim günüyle, notes bu düzeltme turuyla güncellendi."),
    "ISS-044": ("ertelendi", "gorsel_kalite teslim zincirinde yeniden çalıştı; dikey karelerin kırpma sonucu yalnız önizlemede (city-preview) ölçülür."),
}
rows = [{"issue_id": k, "karar": v[0], "neden": v[1]} for k, v in K.items()]
(IS / "duzeltme_kararlari.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
print(json.dumps({"p2": len(rows), "yapildi": sum(r["karar"] == "yapıldı" for r in rows),
                  "ertelendi": sum(r["karar"] == "ertelendi" for r in rows)}, ensure_ascii=False))
