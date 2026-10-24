"""kayitlar.py: L0b denetim kayitlari (CHECK, ISSUE, onceki bulgu durumu, criteria) - kilavuz bolum 16/20.

Kullanim: python -I -X utf8 kayitlar.py <OUT> <CHECKS_YAML>
Girdi yalniz OUT altindaki script ciktilari (paket okunmaz). Cikti: OUT/check-results.json, OUT/issues.json,
OUT/onceki-bulgu-durumu.json, OUT/criteria.json.
"""
from __future__ import annotations

import collections
import json
import sys
from pathlib import Path

import yaml

sys.dont_write_bytecode = True
OUT, CHECKS = Path(sys.argv[1]), Path(sys.argv[2])
DAY = "2026-10-23"
XLSX = "CITY-039_eindhoven_v001.xlsx"
XLSX_SHA = "18b0c295710b6fb4b15b49a409b03f333ace00fa07cb9ab9dd347a83bb9e135b"
PREV_SHA = "01c130e64d683ba05cee94275aa52056f4eba1b1867d4408ab27df04dec25815"


def load(name: str):
    return json.loads((OUT / name).read_text(encoding="utf-8"))


def jl(name: str) -> list[dict]:
    with open(OUT / name, encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


cap = load("_analiz/capraz-kontroller.json")
onc = load("_analiz/onceki-karsilastirma.json")
k04 = load("_analiz/k04-karsilastirma.json")
snap = load("_analiz/snapshot-karsilastirma.json")["summary"]
val = load("validation-audit.json")
tq = load("text-quality.json")["summary"]
url = load("url-checks.json")["summary"]
claims = load("claim-script.json")["summary"]
dec = load("_foto/decisions.json")["summary"]
routes = {r["_row"]: r["route_id"] for r in jl("_dump/Rotalar.jsonl")}
checks_yaml = yaml.safe_load(CHECKS.read_text(encoding="utf-8"))["checks"]

photos = cap["photos"]
counts = val["structure"]["counts"]
places_wo = photos["places_total"] - photos["places_with_photo"]
districts_wo = photos["districts_total"] - photos["districts_with_photo"]
no_photo = places_wo + districts_wo

# ------------------------------------------------------------------ ISSUE kayitlari (acik olanlar)
iss003_ids = onc["iss003"]["now_without_ids"]
iss003_rows = onc["iss003"]["now_without_rows"]
late = onc["k14_review_before_source"]
for item in late:
    if item["sheet"] == "Rotalar":
        item["id"] = routes.get(item["row"], item["id"])
late_rows = "; ".join(f"{i['sheet']}!{i['row']}" for i in late)
late_ids = ", ".join(i["id"] for i in late)
new_places_wo = [x["entry_id"] for x in onc["iss003"]["new_without"]]


def issue(**kw) -> dict:
    keys = ("issue_id", "öncelik", "kategori", "check_id", "tablo", "Excel_satırı", "entry_id/photo_id", "dosya", "alan",
            "mevcut_değer", "beklenen", "somut_gözlem", "kanıt", "kullanıcı_etkisi", "önerilen_düzeltme",
            "tekrar_kontrol_koşulu", "durum")
    return {k: kw[k] for k in keys}


groups = cap["photos"]["group_counts"]
issues = [
    issue(issue_id="ISS-001", öncelik="P1", kategori="Berlin kapsamı / mekân hedefi", check_id="K17", tablo="Mekânlar",
          Excel_satırı=f"8–126 ({counts['places']} kayıt)", **{"entry_id/photo_id": "—"}, dosya=XLSX,
          alan="kayıt sayısı (places)", mevcut_değer=str(counts["places"]),
          beklenen="hedef 120 (asgari 92 karşılandı)",
          somut_gözlem=("Resmî doğrulayıcı sayımı places=119, minimum=92, target=120; hedefe 1 mekân eksik. Önceki "
                        "denetimde 104 idi: 15 mekân eklendi, çıkan yok (impact: Mekânlar added 15). Grup dağılımı: "
                        + ", ".join(f"{k} {v}" for k, v in sorted(groups.items(), key=lambda x: -x[1])) + "."),
          kanıt=("validation-audit.json → structure.counts.places / target.places; _render/TESLIM_OZETI.txt; "
                 "_analiz/onceki-karsilastirma.json → places_added"),
          kullanıcı_etkisi="Keşif bölümü Berlin üretim hedefinin 1 kayıt altında; kalite oranı eksik hedefi örtmez (kılavuz bölüm 20).",
          önerilen_düzeltme=("En az 1 gerçek, açık, kaynaklı ve şehir kapsamındaki mekân ekle (en az dolu grup: Müzeler 11); "
                             "alt nesne/collection ile şişirme yapma (K108); yeni kayıt fotoğraflı olsun (ISS-003)."),
          tekrar_kontrol_koşulu="validate_all structure.counts.places ≥ 120 ve yeni kayıtlar L1'de K39/K42/K108 ile doğrulanmış.",
          durum="Açık"),
    issue(issue_id="ISS-002", öncelik="P1", kategori="Berlin kapsamı / fotoğraf hedefi", check_id="K17",
          tablo="Fotoğraflar", Excel_satırı="8–233 (226 satır)", **{"entry_id/photo_id": "—"},
          dosya=f"{XLSX}; Fotoğraflar/", alan="tekil mekân karesi sayısı (photos)", mevcut_değer=str(counts["photos"]),
          beklenen="hedef 250 (asgari 187 karşılandı)",
          somut_gözlem=("226 fotoğraf satırı (218 Mekân + 8 Kapak) → 218 farklı dosya / 218 farklı kaynak sayfası; 8 kapak "
                        "mekân kareleriyle aynı SHA (rol ayrı, kare bir kez sayılır). Hedefe 32 tekil kare eksik "
                        "(önceki denetimde 201, eksik 49)."),
          kanıt=("validation-audit.json → structure.counts.photos, media.different_files; dosya-envanteri.json "
                 "findings.dup_sha (8); _foto/hazirlik.json ayni_sha.kapak_mekan 8"),
          kullanıcı_etkisi="Galeri derinliği Berlin hedefinin altında; fotoğrafsız 66 kayıtla birlikte görsel kapsam zayıf (ISS-003).",
          önerilen_düzeltme="En az 32 yeni, tekil, gerçek ve ücretsiz-ticari lisanslı kare ekle; önce fotoğrafsız 64 mekân + 2 mahalleye.",
          tekrar_kontrol_koşulu="validate_all structure.counts.photos ≥ 250 (SHA/kaynak tekil) ve yeni kareler L1 görsel incelemesinden geçmiş.",
          durum="Açık"),
    issue(issue_id="ISS-003", öncelik="P1", kategori="Fotoğraf kapsamı", check_id="K22", tablo="Mekânlar; Mahalleler",
          Excel_satırı=("Mekânlar!" + ",".join(map(str, iss003_rows["Mekânlar"])) + "; Mahalleler!"
                        + ",".join(map(str, iss003_rows["Mahalleler"]))),
          **{"entry_id/photo_id": ", ".join(iss003_ids)}, dosya=XLSX, alan="Fotoğraflar.entry_id ilişkisi",
          mevcut_değer=(f"fotoğraflı mekân {photos['places_with_photo']}/{photos['places_total']}; fotoğraflı mahalle "
                        f"{photos['districts_with_photo']}/{photos['districts_total']}"),
          beklenen="Her fiziksel mekân ve mahalle en az bir doğru, gerçek fotoğrafla kapsanır (collection istisnası kullanılmamış: 119/119 'Hayır').",
          somut_gözlem=(f"{places_wo} mekân + {districts_wo} mahalle hiç fotoğraf ilişkisine sahip değil (önceki denetimde "
                        "60 + 2 = 62). Önceki 62 kaydın hiçbiri fotoğraf almadı; yeni eklenen 15 mekândan 4'ü fotoğrafsız ("
                        + ", ".join(new_places_wo) + "). Grup bazında fotoğrafsız mekân: "
                        + ", ".join(f"{k} {v}" for k, v in photos["group_without_photo"].items()) + "."),
          kanıt=("validation-audit.json → warning_classes ('Mekân / mahalleye bağlı gerçek fotoğraf eksik' 64 + 2); "
                 "_foto/decisions.json → summary.entries_without_shortlist (66); _analiz/capraz-kontroller.json → "
                 "photos.places_without_photo; _analiz/onceki-karsilastirma.json → iss003"),
          kullanıcı_etkisi="Mekân kartlarının %54'ü görselsiz açılır; kullanıcı yeri tanıyamaz, keşif deneyimi ve güven zayıflar.",
          önerilen_düzeltme=("Her kayda en az bir gerçek, tekil, ücretsiz-ticari lisanslı kare ekle; uygun kare yoksa kaydın "
                             "kapsamda kalmasına editoryal karar ver (collection etiketiyle kaçma)."),
          tekrar_kontrol_koşulu="validate_all uyarı sınıfı 'gerçek fotoğraf eksik' = 0; yeni kareler L1 görsel (K59–K61) ve hak (K67–K74) incelemesinden geçmiş.",
          durum="Açık"),
    issue(issue_id="ISS-005", öncelik="P2", kategori="Teslim özeti / ilerleme kaydı", check_id="K83", tablo="—",
          Excel_satırı="—", **{"entry_id/photo_id": "—"},
          dosya="Teslimler/ILERLEME_KAYDI.txt; Teslimler/dosya-envanteri.json",
          alan="son ilerleme kaydı; paket envanterindeki ILERLEME_KAYDI.txt SHA'sı",
          mevcut_değer=(f"ILERLEME_KAYDI: {onc['iss005']['records']} kayıt, son {onc['iss005']['identical_trailing']} kayıt "
                        "birebir aynı (2026-10-23, Faz: deliver); son kayıtta 'İndirilmiş fotoğraflar: "
                        f"{onc['iss005']['last_downloaded_photos']}', 'Araştırılan resmî kaynaklar: "
                        f"{onc['iss005']['last_official_sources']}'"),
          beklenen=("Son kayıt teslim edilen paketi gösterir (226 fotoğraf satırı / 218 dosya; 397 kaynak) ve aynı kayıt "
                    "tekrar eklenmez; paket envanteri teslim edilen her dosyanın gerçek SHA'sını taşır."),
          somut_gözlem=("TESLIM_OZETI.txt artık ölçümle birebir aynı (851 dosya, 224.97 MB; satır farkı 0) — önceki "
                        "ISS-005'in özet kısmı kapandı. Kalan: ILERLEME_KAYDI son kaydı eski sayılar taşıyor ve her özet "
                        "koşusunda aynı kayıt yeniden eklenmiş; Teslimler/dosya-envanteri.json 851 yolu kapsıyor ama "
                        "ILERLEME_KAYDI.txt için yazdığı SHA gerçek dosyayla tutmuyor (sayımdan sonra yeniden yazılmış; "
                        "dosya-envanteri.json'un kendi SHA'sı doğası gereği tutmaz)."),
          kanıt=("Teslimler/ILERLEME_KAYDI.txt (salt okunur); _analiz/onceki-karsilastirma.json → iss005; "
                 "_analiz/capraz-kontroller.json → teslimler.pkg_inventory.sha_differs; _analiz/k04-karsilastirma.json "
                 "(k83_summary_line_diffs 0, k83_path_diffs 0)"),
          kullanıcı_etkisi="Teslimi okuyan kişi faz/sayı durumunu eski görür; paket manifesti bir dosyada gerçek hash'i göstermez (işlevi bozmaz).",
          önerilen_düzeltme=("ILERLEME_KAYDI'nı son paket durumundan (fotoğraf, kaynak sayıları) tek kayıtla yeniden üret; "
                             "envanteri tüm özet dosyaları yazıldıktan sonra al."),
          tekrar_kontrol_koşulu="ILERLEME_KAYDI son kaydı ölçümle aynı, tekrar kayıt yok; paket envanteri ↔ denetim envanteri SHA farkı yalnız dosya-envanteri.json.",
          durum="Açık"),
    issue(issue_id="ISS-006", öncelik="P2", kategori="Teslim kaydı / tarih", check_id="K14", tablo="Teslimat",
          Excel_satırı="8", **{"entry_id/photo_id": "city-039-v001"}, dosya=XLSX, alan="updated_on",
          mevcut_değer="updated_on 2026-10-22",
          beklenen=f"updated_on son içerik güncellemesini gösterir (en son içerik tarihi {cap['latest_content_date']}).",
          somut_gözlem=("notes artık teslim içeriğini doğru tarif ediyor (şablon metni 'içerik üretilmedi' kalktı) ve "
                        "updated_on 2026-10-12 → 2026-10-22 güncellendi; ancak paket 23 Ekim'de yeniden üretildi: "
                        "Kaynaklar.checked_on 18 satırda, Bağlantılar.checked_on 2 satırda 2026-10-23; TESLIM_OZETI "
                        "'Excel sürümü/tarihi: v001 · 2026-10-23' diyor."),
          kanıt="_dump/Teslimat.jsonl; _analiz/capraz-kontroller.json → dates, latest_content_date; impact.json (Teslimat changed: notes, updated_on)",
          kullanıcı_etkisi="Teslim kaydı paketin son güncelleme gününü bir gün eski gösteriyor; sürüm/tarih takibi tutarsız.",
          önerilen_düzeltme="Teslimat.updated_on'u son içerik değişikliğinin tarihine (2026-10-23) çek; alan Atınç'a aitse ona bildir.",
          tekrar_kontrol_koşulu="Teslimat.updated_on ≥ en son reviewed_on/checked_on ve TESLIM_OZETI tarihiyle aynı.",
          durum="Açık"),
    issue(issue_id="ISS-007", öncelik="P2", kategori="Metin kalitesi / kaynak dayanağı (kısmen kapandı)",
          check_id="K104", tablo="Yanıtlar", Excel_satırı="194",
          **{"entry_id/photo_id": "eindhoven:ev-sigortalari-opstal-inboedel-aansprakelijkheid"}, dosya=XLSX,
          alan="summary; note",
          mevcut_değer=("summary: 'Holland Expat Center South'a göre opstalverzekering (bina sigortası) mülk sahipleri için "
                        "zorunludur.' note: 'Holland Expat Center South, mülk sahipleri için opstal sigortasını zorunlu "
                        "olarak belirtiyor.'"),
          beklenen=("Kural resmî/hukuki kaynakla doğrulanıp yazılır (yasal zorunluluk mu, ipotek/VvE şartı mı) veya kesin "
                    "olmayan kural kesin gibi sunulmaz."),
          somut_gözlem=("Okuyucuya bırakılan doğrulama cümlesi ('sayfa bu kuralın yasal dayanağını göstermiyor') ve iç not "
                        "('resmî bir kaynakla doğrulanamadı') kaldırıldı; text_quality bu kartta hedge 0 → K104 belirtisi "
                        "kapandı. Ancak kaynak değişmedi (source_ids yalnız eindhoven:kaynak:097, Holland Expat Center "
                        "South); 'zorunludur' ifadesi artık çekincesiz. Önceki tekrar kontrol koşulunun ikinci yarısı "
                        "(L1'de K29/K35/K41 'supported') L0'da ölçülemez."),
          kanıt="text-quality.json → hedges.items (Yanıtlar!194 yok); impact.json (changed: note, steps, subtitle, summary); _analiz/onceki-karsilastirma.json → iss007",
          kullanıcı_etkisi="Zorunluluk bilgisi yalnız aracı kuruma dayanıyor; yanlışsa okuyucu gereksiz/yanlış yükümlülük algılar.",
          önerilen_düzeltme="Opstal zorunluluğunu resmî/hukuki kaynakla doğrula ve metni buna göre yaz (ör. 'ipotekli alımda banka şart koşar').",
          tekrar_kontrol_koşulu="L1 iddia denetiminde (K29/K35/K41) iddia resmî kaynakta 'supported'; text_quality hedge bu kartta 0 (karşılandı).",
          durum="Açık (kısmen kapandı)"),
    issue(issue_id="ISS-008", öncelik="P2", kategori="İnceleme tarihi / kaynak tarihi sırası", check_id="K14",
          tablo="Mekânlar; Rotalar", Excel_satırı=late_rows, **{"entry_id/photo_id": late_ids}, dosya=XLSX,
          alan="reviewed_on", mevcut_değer=f"reviewed_on 2026-10-22 ({len(late)} kayıt)",
          beklenen="reviewed_on, kaydın dayandığı kaynakların checked_on tarihinden önce olamaz; 23 Ekim'de değişen kayıtlar 2026-10-23 taşır.",
          somut_gözlem=(f"{len(late)} kayıt 2026-10-23'te kontrol edilmiş kaynaklara (kaynak:390–405, 407) dayanıyor ama "
                        "reviewed_on 2026-10-22; bunların "
                        f"{sum(1 for i in late if i['text_dated_23_10'])}'sının metninde '23.10.2026' tarihli not var "
                        "(POM taşınması, Happy Canoe sezonu, iki oyun bahçesi, Next Level Escape Rooms, rota 005). "
                        "Kayıtlar: " + late_ids + "."),
          kanıt="_analiz/onceki-karsilastirma.json → k14_review_before_source, sources_checked_2026_10_23; _dump/Kaynaklar.jsonl (checked_on)",
          kullanıcı_etkisi="Kartlarda gösterilen 'son kontrol' tarihi gerçek kontrolden eski; tarih takibi ve yeniden kontrol planı yanıltıcı.",
          önerilen_düzeltme="Bu kayıtların reviewed_on değerini gerçek inceleme tarihine (2026-10-23) güncelle; birleştirme adımında reviewed_on ≥ max(kaynak checked_on) kuralını script kapısı yap.",
          tekrar_kontrol_koşulu="Her kayıtta reviewed_on ≥ bağlı kaynakların en geç checked_on değeri (bu denetimin k14 taraması 0 kayıt).",
          durum="Açık"),
]

# ------------------------------------------------------------------ onceki bulgu durumu (K99)
prev = [
    {"issue_id": "ISS-001", "öncelik": "P1", "check_id": "K17", "önceki": "mekân 104/120 (−16)",
     "şimdi": f"mekân {counts['places']}/120 (−1)", "durum": "sürüyor",
     "kanıt": "validation-audit.json → structure.counts.places 119; impact.json Mekânlar added 15, deleted 0",
     "L0b_açık": True, "not": "15 mekân eklendi (Golfbaan Welschap pakette yok); hedefe 1 kayıt kaldı."},
    {"issue_id": "ISS-002", "öncelik": "P1", "check_id": "K17", "önceki": "tekil mekân karesi 201/250 (−49)",
     "şimdi": f"tekil mekân karesi {counts['photos']}/250 (−32)", "durum": "sürüyor",
     "kanıt": "validation-audit.json → counts.photos 218, media.different_files 218; Fotoğraflar added 17",
     "L0b_açık": True, "not": "17 yeni kare eklendi."},
    {"issue_id": "ISS-003", "öncelik": "P1", "check_id": "K22", "önceki": "fotoğrafsız 60 mekân + 2 mahalle (44/104, 14/16)",
     "şimdi": f"fotoğrafsız {places_wo} mekân + {districts_wo} mahalle ({photos['places_with_photo']}/119, 14/16)",
     "durum": "sürüyor",
     "kanıt": "validation-audit.json warning_classes 64 + 2; _analiz/onceki-karsilastirma.json → iss003 (closed 0, new_without 4)",
     "L0b_açık": True, "not": "Önceki 62 kaydın hiçbiri fotoğraf almadı; yeni 4 fotoğrafsız mekân eklendi (62 → 66)."},
    {"issue_id": "ISS-004", "öncelik": "P1", "check_id": "K84", "önceki": "web_file 209/209 '\\' ayırıcı (+JSON/CSV/HTML)",
     "şimdi": "web_file 0/226 '\\'; photo-provenance-v7.json 0/452, atıf CSV 0/452, atıf HTML 0/226, normalized-tables 0/850",
     "durum": "kapandı",
     "kanıt": "_foto/hazirlik.json → ters_egik_cizgi (tüm yollar 0/n); _analiz/capraz-kontroller.json → backslash_cells (yalnız Kanıtlar.source_evidence_json JSON kaçışları, yol değil)",
     "L0b_açık": False, "not": "Mutlak yerel yol / '..' / geçici URL de yok."},
    {"issue_id": "ISS-005", "öncelik": "P2", "check_id": "K83", "önceki": "TESLIM_OZETI 763 dosya/199.68 MB ↔ ölçülen 772; ILERLEME_KAYDI 'İndirilmiş fotoğraflar: 0'",
     "şimdi": "TESLIM_OZETI = ölçüm (851/224.97 MB, satır farkı 0); ILERLEME_KAYDI son kayıt 'İndirilmiş fotoğraflar: 209', 'resmî kaynaklar: 352' ve 4× aynı kayıt; paket envanterinde ILERLEME_KAYDI.txt SHA'sı tutmuyor",
     "durum": "değişti", "kanıt": "_analiz/k04-karsilastirma.json (k83 farkları 0); _analiz/onceki-karsilastirma.json → iss005; capraz-kontroller.json → teslimler.pkg_inventory.sha_differs",
     "L0b_açık": True, "not": "Özet kısmı kapandı; ilerleme kaydı kısmı farklı değerlerle sürüyor."},
    {"issue_id": "ISS-006", "öncelik": "P2", "check_id": "K14", "önceki": "updated_on 2026-10-12; notes şablon ('içerik üretilmedi')",
     "şimdi": "notes doğru; updated_on 2026-10-22 < en son içerik tarihi 2026-10-23", "durum": "değişti",
     "kanıt": "_dump/Teslimat.jsonl; capraz-kontroller.json → latest_content_date; impact.json (Teslimat: notes, updated_on)",
     "L0b_açık": True, "not": "notes kısmı kapandı; tarih bir gün geride."},
    {"issue_id": "ISS-007", "öncelik": "P2", "check_id": "K104", "önceki": "Yanıtlar!194 'yasal dayanağını göstermiyor' + iç not",
     "şimdi": "uyarı ve iç not kaldırıldı (hedge 0); kaynak aynı (yalnız kaynak:097 HEC South), 'zorunludur' çekincesiz",
     "durum": "değişti", "kanıt": "text-quality.json hedges (Yanıtlar!194 yok); impact.json; onceki-karsilastirma.json → iss007",
     "L0b_açık": True, "not": "K104 belirtisi kapandı; tekrar kontrol koşulunun L1 yarısı (resmî kaynakta 'supported') bekliyor → açık (kısmen)."},
]

# ------------------------------------------------------------------ CHECK kayitlari
L_TEXT = "0 (LLM + kaynak incelemesi yapılmadı)"
L_WHY = "L0 kademesi: exec L kontrolleri çalıştırılmaz (SKILL)."
V_TEXT = "0 (görsel inceleme yapılmadı)"
V_WHY = "L0 kademesi: exec V kontrolleri çalıştırılmaz; paftalar üretildi ama bakılmadı (SKILL)."
links_sum = url["relations_by_sheet"]
C: dict[str, tuple] = {}


def c(cid, durum, incelenen, yontem, kanit, bulgular=(), sinir="", beklenen=None):
    C[cid] = (durum, beklenen, incelenen, yontem, kanit, list(bulgular), sinir)


c("K02", "geçti", "851/851 dosya okundu, SHA-256 hesaplandı; 444 görsel (226 JPEG + 218 WebP) çözüldü; okuma hatası 0",
  "inventory.py (başlangıç ve bitiş)", "dosya-envanteri.json; _dosya-envanteri-son.json",
  sinir="Drive kopyasıyla karşılaştırma K03 (ayrı aşama).", beklenen="Paketteki tüm dosyalar gerçek baytlarıyla")
c("K04", "geçti", (f"Başta {k04['start_files']}, sonda {k04['end_files']} dosya; eklenen 0, silinen 0, değişen 0; SHA "
                   f"listesi özeti {k04['sha_list_digest_start']} / {k04['sha_list_digest_end']}; Excel SHA "
                   f"{k04['xlsx_sha_start']} → {k04['xlsx_sha_end']}. Son envanter tüm paket okumalarından sonra alındı "
                   "(05:06:35 → 05:30:00)."),
  "inventory.py ×2 + SKILL fark bloğu + Python SHA listesi karşılaştırması", "dosya-envanteri.json; _dosya-envanteri-son.json; _analiz/k04-karsilastirma.json",
  sinir="KAPSAM: kısmi; baş/son karşılaştırması bu denetimde tamamlandı.", beklenen="Denetim başı ve sonu paket SHA listeleri")
c("K05", "geçti", ("Kök: 1 XLSX; Fotoğraflar 226, Lisans kanıtları 396, Teslimler 228 (10 dosya + WebKopyalari 218); "
                   "orphan 0; aynı SHA grupları 8'i de kapak↔mekân (K05 sınıfı 0); .download-cache yok; ikinci Excel yok; "
                   "Teslimler'deki 10 dosya resmî araç çıktısı"),
  "inventory.py findings + audit_prep ayni_sha + dosya listesi", "dosya-envanteri.json; _foto/hazirlik.json; _analiz/capraz-kontroller.json → inventory, teslimler.files",
  sinir="KAPSAM: kısmi; çoklu Excel ve artık denetimi envanter listesinden yapıldı.",
  beklenen="Kök XLSX + Fotoğraflar, Lisans kanıtları, Teslimler; artık/orphan/çoklu Excel yok")
c("K06", "geçti", "XLSX okuma, bayt/SHA, HTTP erişimi ve kod çalıştırma fiilen kullanıldı; görsel inceleme ve LLM iddia denetimi L0 dışı (yapılmadı, GEÇTİ sayılmadı)",
  "Araç kullanımının kaydı", "DENETIM_OZETI.md bölüm 9", beklenen="Yetenek ve erişim sınırları kaydı")
c("K07", "kısmi", "Alt sınır/hedefler resmî doğrulayıcının acceptance_version 2026-10-13.1 değerlerinden", "validate_all structure.minimum/target",
  "validation-audit.json", sinir="Berlin örnek Excel'i bu L0 denetiminde açılmadı.", beklenen="Referansın doğru kullanımı")
c("K08", "geçti", "16/16 sekme (missing_sheets 0); yapı girdi şablonuyla aynı (xlsx_fidelity diffs 0); resmî doğrulayıcı yapı hatası 0",
  "xlsx_dump + xlsx_fidelity + validate_all", "_dump/summary.json; xlsx-fidelity.json; validation-audit.json")
c("K09", "geçti", "xlsx_fidelity fark 0 (kabul edilen openpyxl parça farkları: sharedStrings kaldırıldı, docProps eklendi); formül sütunları Konular.used_count, Fotoğraflar.unique_hero_count, unique_venue_count",
  "xlsx_fidelity (şablon: ekler_eindhoven/CITY-039_eindhoven_v001.xlsx, salt okunur) + xlsx_dump", "xlsx-fidelity.json; _dump/summary.json")
c("K10", "geçti", "16 sekme, 2199 satır; tekrar kimlik 0, boş anahtar 0; yer tutucu: text_quality 0; validate_all ek kontrolünün 1 adayı (Yanıtlar!177 steps 'Hazırlık yapın: DigiD'iniz (veya Avrupa girişiniz)…') yer tutucu değil",
  "xlsx_dump + text_quality + validate_all extras", "_dump/summary.json; text-quality.json; validation-audit.json → extras.placeholders",
  sinir="Editoryal kullanılabilir sayı K18 (L) kapsamında.")
c("K11", "geçti", "Resmî doğrulayıcı kimlik/slug hatası 0 (2199 satır)", "validate_all --mode audit --new-content", "validation-audit.json")
c("K12", "geçti", "Resmî doğrulayıcı bağ hatası 0; ek: 12 rota 4–5 durak, stops↔stop_entry_ids eşleşmesi ve ilk durak = entry_id sorunsuz; fotoğraf entry_id'leri 226/226 tanımlı; pixel_review_file = file 226/226; source_ids'te tanımsız kaynak 0",
  "validate_all + capraz.py", "validation-audit.json; _analiz/capraz-kontroller.json → routes, photos, sources")
c("K13", "geçti", "Resmî doğrulayıcı tür/enum hatası 0. Bilgi: photo-provenance-v7.json ve atıf CSV'sinde downloaded_on '2026-10-23 00:00:00' biçiminde, Excel'de tarih",
  "validate_all", "validation-audit.json; _analiz/capraz-kontroller.json → teslimler")
c("K14", "kaldı", ("İçerik tarihleri: reviewed_on 2026-10-22 (tüm kartlar), Kaynaklar.checked_on 2026-10-22 ×379 / 2026-10-23 ×18, "
                   "Bağlantılar.checked_on 2026-10-23 ×2; gelecek tarih 0; sıra çakışması 0 (gruplar içinde). Teslimat.updated_on "
                   f"2026-10-22 < 2026-10-23 (ISS-006); {len(late)} kayıtta reviewed_on < bağlı kaynak checked_on (ISS-008)"),
  "capraz.py + onceki.py tarih taramaları + validate_all", "_analiz/capraz-kontroller.json → dates; _analiz/onceki-karsilastirma.json → k14_review_before_source",
  ["ISS-006", "ISS-008"])
c("K15", "geçti", "Fotoğraflar.file 226, FotoğrafKaynakları.original_file 226 ve web_file 226, Kanıtlar.pixel_review_file 226, Kaynaklar.snapshot_file 397 yolun tamamı '/' ile; Teslimler JSON/CSV/HTML yollarında '\\' 0; mutlak yol, '..', paket dışına taşan bağlantı 0; envanter missing 0",
  "audit_prep ters_egik_cizgi + capraz.py yol taraması + inventory", "_foto/hazirlik.json; _analiz/capraz-kontroller.json; dosya-envanteri.json",
  sinir="Unicode normalizasyon çakışması ayrıca aranmadı (envanter yolları tekil).")
c("K16", "geçti", "EkDetaylar 0 satır; UzunAlanlar yok; en uzun hücre 11106 karakter (Kanıtlar!130.source_evidence_json); long_values_restored 0",
  "xlsx_dump + paket-kontrol-v7.json okuması", "_dump/summary.json; _analiz/capraz-kontroller.json → longest_cell",
  sinir="KAPSAM: kısmi; EkDetaylar boş olduğundan gölge alan denetimi konusuz.")
c("K17", "kaldı", (f"answers 289 (212/240 ✓); places {counts['places']} (92/120 ✗ −1); neighborhoods 16 (12/16 ✓); topics 12 (12/12 ✓); "
                   f"photos {counts['photos']} (187/250 ✗ −32); hero_photos 8 (6/8 ✓); routes 12 (9/12 ✓); glossary 60 (48/60 ✓)"),
  "validate_all + render_summary (bağımsız yeniden hesap)", "validation-audit.json → structure.counts/minimum/target; _render/TESLIM_OZETI.txt",
  ["ISS-001", "ISS-002"], "Editoryal kullanılabilir sayı L (K18); burada ham/tekil sayılar.")
for cid in ("K18", "K19", "K20", "K25", "K26", "K28", "K29", "K31", "K32", "K34", "K35", "K37", "K38", "K39", "K40", "K41",
            "K42", "K44", "K47", "K48", "K51", "K53", "K54", "K55", "K71", "K72", "K90", "K91", "K108"):
    c(cid, "not_checked", L_TEXT, "—", "—", sinir=L_WHY)
extra_l = {
    "K19": " Konu başına ham yanıt 12/12 konu dolu.",
    "K20": " Grup başına mekân: " + ", ".join(f"{k} {v}" for k, v in groups.items()) + ".",
    "K29": f" claim_check: {claims['claims']} sayısal iddianın {claims['by_result']['supported']}'i taze kaynak kopyasında dize olarak bulundu (doğrulama değil); 23 'not_in_source' önceki denetimle birebir aynı.",
    "K34": f" claim_extract envanteri: {claims['claims']} iddia / {claims['entries']} kart; resmî kaynakta doğrulanan 0.",
    "K39": " L1 ipucu: 23 Ekim'de tarihli not eklenen 5 mekân (POM, Happy Canoe, Speeltuin Philipsdorp, Sint Joseph Speeltuin, Next Level Escape Rooms) ve TAC yenilemesi.",
    "K41": " L1 ipucu: Yanıtlar!194 opstal 'zorunlu' iddiası tek kaynakla (ISS-007).",
    "K42": " L1 ipucu: aynı koordinatlı 3 çift (kazerne/kazerne-expo, 18-septemberplein/centrale-markt-18-septemberplein, brouwerij-het-veem/str-eat-bars-kitchens); yeni 15 mekân.",
    "K51": " url_check sinyalleri: soft-404 0; anasayfaya yönlenen 2 (defabriekeindhoven /en/home→/en; ijssportcentrum /contact/→sportfondsen anasayfa); yalnız anasayfa kaynak 13 (9'u yeni mekânların kendi sitesi).",
    "K55": " L1 ipucu: TAC harita noktası ile adres (Ventoselaan 1) aynı parselde mi.",
    "K71": " L1 ipucu: Fotoğraflar!60 de-ontdekfabriek-02 (Pixabay kökenli CC0 Commons dosyası).",
    "K72": " L1 ipucu: CC0 1.0 7 + Public domain 2 dosya (PD ikisinde license_url = Commons dosya sayfası).",
    "K90": " SayfaAlanları emergency_url (government.nl 112) ve pharmacy_url (huisartsenpostenoostbrabant.nl) 200.",
    "K91": " forecast_url knmi.nl ulusal tahmin sayfası; şehre özgülüğü L.",
    "K108": " L1 ipucu: aynı koordinatlı 3 çift alt nesne/şişirme açısından.",
}
for cid, text in extra_l.items():
    d = C[cid]
    C[cid] = (d[0], d[1], d[2], d[3], d[4], d[5], d[6] + text)
c("K21", "geçti", "Bağlantısız 0, yalnız harita 0 (424/424 kart)", "text_quality action_links", "text-quality.json → action_links",
  sinir="Bağlantının doğru işleme gitmesi K53 (L).")
c("K22", "kaldı", f"Fotoğraflı mekân {photos['places_with_photo']}/119, mahalle 14/16; collection=Hayır 119/119",
  "validate_all uyarı sınıfı + capraz.py", "validation-audit.json; _analiz/capraz-kontroller.json → photos", ["ISS-003"],
  "Fotoğrafın doğru yeri göstermesi K60 (V), L0'da bakılmadı.")
c("K23", "geçti", "226 satır → 218 farklı dosya, 218 farklı kaynak sayfası; 8 kapak satırı mekân karesiyle aynı SHA (rol ayrı: kapak 8, mekân 218); author/license 226/226 dolu",
  "validate_all media + capraz.py", "validation-audit.json → media; _analiz/capraz-kontroller.json → photos")
c("K24", "kısmi", "Asgari eşiklerin tamamı ham sayımla karşılanıyor; hedef eksikleri ayrı görünür (ISS-001/002). Kalite sonrası yeniden sayım L/V sonuçları olmadan yapılamadı",
  "render_summary", "_render/TESLIM_OZETI.txt", ["ISS-001", "ISS-002"], "L/V elemesi yapılmadığından kullanılabilir sayı yok.")
c("K27", "geçti", ("13 birebir küme (26 kayıt): 8'i kapak↔mekân aynı kaynak dosyasının modifications metni; 5'i yakın kart "
                   "çiftlerinde ortak alan (cost: Yanıtlar!145/!147, !271/!272; documents: !44/!45, !163/!164; timing: "
                   "!53/!54); önceki denetimle aynı içerik"),
  "text_quality", "text-quality.json → exact_duplicates, near_duplicates", sinir="Ortak alanların meşruiyeti anlamsal olarak K28 (L).")
c("K30", "kısmi", "Toplu anasayfa ataması 0 (validate_all ek kontrol); url_check 'homepage_only' 13 adres (Kaynaklar 12 ilişki: 4 eski + 9 yeni mekân sitesi; Şehir!8 knmi.nl)",
  "validate_all extras + url_check flags", "validation-audit.json → extras.homepage_only_sources; url-checks.json", sinir="İddia bazında gerçek destek K29 (L).")
c("K33", "kısmi", "visual_json 6/289 kartta dolu ve geçerli, hata 0; 283 boş (isteğe bağlı)", "text_quality visual_json",
  "text-quality.json → visual_json", sinir="Görselin steps ile anlamsal uyumu L.")
c("K36", "uygulanmaz", "—", "—", "—", sinir="D7/D8 kısmı yalnız Portekiz (PT) için; şehir NL. Hollanda vize/oturum kuralları K35 (L) altında, L0'da not_checked.")
c("K43", "kısmi", "119 koordinat aralıkta (enlem 51.4083–51.4938, boylam 5.3992–5.5260); aynı koordinatlı 3 çift: kazerne/kazerne-expo, 18-septemberplein/centrale-markt-18-septemberplein, brouwerij-het-veem/str-eat-bars-kitchens (önceki denetimle aynı)",
  "validate_all (aralık) + extra_checks.shared_coordinates + capraz.py", "validation-audit.json → extras.shared_coordinates; _analiz/capraz-kontroller.json → coordinates",
  sinir="Harita/adres doğrulaması L/V; aynı bina/meydan olabilir (L1'de K42/K108 ile).")
c("K45", "geçti", "Resmî doğrulayıcı hata 0", "validate_all", "validation-audit.json")
c("K46", "geçti", "12 rota, durak 4–5; stops/ID uzunluk-sıra eşleşmesi, ilk durak = entry_id, tanımsız durak 0; rota 009 durakları erfgoedhuis→daf-museum→jazzclub-osje→het-koelhuis",
  "validate_all + capraz.py", "_analiz/capraz-kontroller.json → routes")
c("K49", "geçti", "401 benzersiz URL: biçim sorunu 0, geçersiz 0", "url_check (biçim) + validate_all", "url-checks.json → summary.format_issues")
c("K50", "kısmi", (f"401/401 test edildi (984 ilişki: Bağlantılar 581, Kaynaklar 397, Şehir 4, SayfaAlanları 2): 200 = 360, "
                   "yönlendirme→200 = 38, 404/410/soft-404 = 0, 403 = 0, 5xx/ağ = 0; erişim teyidi açık 3 (429: "
                   "cafewilhelmina.nl /, /agenda, /contact)"),
  "url_check --retry-transient ×2", "url-checks.json; _log/url-checks-kosu1.json",
  sinir="3 adres hız sınırı (429) nedeniyle doğrulanamadı; bozuk sayılmaz, L1'de ajan açar. Fotoğraf kaynak/lisans/dosya URL'leri K78 kapsamında, L0'da test edilmedi.")
c("K52", "geçti", "İlk geçişte 1 adres 429 (cafewilhelmina.nl); fetch_snapshot aynı alan adında 3 adres 429; --retry-transient ile bir kez yeniden denendi, 3 adres yine 429 → 'erişim teyidi açık'. 403 yok; erişim engeli aşılmadı",
  "url_check ×2 + fetch_snapshot ×2 (--retry-transient)", "url-checks.json; kanitlar/snap/index.jsonl; _log/")
c("K56", "geçti", "401 benzersiz URL → 984 ilişki; test edilmeyen 0; hatalar alan adına göre gruplu (www.cafewilhelmina.nl: 429 ×3)",
  "url_check", "url-checks.json → summary")
c("K57", "geçti", "444 görsel (226 JPEG + 218 WebP) açıldı; uzantı/format uyuşmazlığı 0; bozuk 0", "inventory + validate_all media",
  "dosya-envanteri.json; validation-audit.json → media.checks.image_decoding")
c("K58", "geçti", "Beyan SHA = ölçülen (sha_mismatch 0); web_width/height beyanı = ölçülen 226/226", "inventory + capraz.py (PIL boyut)",
  "dosya-envanteri.json; _analiz/capraz-kontroller.json → photo_chain")
for cid in ("K59", "K60", "K61", "K62", "K65", "K74", "K105"):
    c(cid, "not_checked", V_TEXT, "—", "—", sinir=V_WHY)
C["K59"] = C["K59"][:6] + (V_WHY + " Paftalar: temas-sayfalari/sheet_01–08.jpg (226 kare).",)
C["K60"] = C["K60"][:6] + (V_WHY + " L1 ipucu: prefilter 'flag' 4 kare (next-nature-museum-01 sheet_01/13, dynamo-03 sheet_02/15, kapak-05 sheet_08/13, kapak-08 sheet_08/16).",)
C["K62"] = C["K62"][:6] + (V_WHY + " 8 kapak (Fotoğraflar!226–233) mekân kareleriyle aynı dosya; kapak-05 ve kapak-08 'place_mismatch' işaretli.",)
c("K63", "geçti", "dHash (eşik 5) 226 kare: 8 yakın çift, hepsi mesafe 0 kapak↔mekân aynı dosya (rol ayrı, tek kare sayıldı); K63_aday 0; aynı SHA K63 sınıfı 0",
  "contact_sheet dHash + audit_prep ciftler/hazirla", "temas-sayfalari/dhash.json; _foto/dhash-ciftleri.json; _foto/hazirlik.json",
  sinir="Algısal eşleşme tek başına karar değil; görsel teyit L1.")
c("K64", "kısmi", "226 adayın Commons kaydında yapay görüntü işareti (ai_generated) 0", "photo_candidates from-evidence + photo_prefilter",
  "_foto/candidates.jsonl; _foto/decisions.json", sinir="KAPSAM: kısmi; piksel analizi ve görsel inceleme L1.")
c("K66", "kısmi", "Teknik kredi sayımı: 218 mekân + 8 kapak (resmî); 226 ilişki", "render_summary + validate_all",
  "_render/TESLIM_OZETI.txt; validation-audit.json", sinir="Görsel inceleme yapılmadığından doğrulanmış sayı yok.")
c("K67", "kısmi", "226 adayın Commons lisans alanı: izinli liste dışı (license_not_allowed) 0; kısıt (restrictions) 0",
  "photo_candidates from-evidence + photo_prefilter", "_foto/candidates.jsonl; _foto/decisions.json",
  sinir="KAPSAM: kısmi; tekil eserin lisansı ve görsel eşleşme L1.")
c("K68", "geçti", "226 satır: " + ", ".join(f"{k} {v}" for k, v in sorted(cap["licenses"].items(), key=lambda x: -x[1])) + "; reddedilen kullanım koşulu 0",
  "validate_all", "validation-audit.json; _analiz/capraz-kontroller.json → licenses")
c("K69", "geçti", "license_label_url geçti (226), medya hatası 0", "validate_all", "validation-audit.json → media.checks")
c("K70", "geçti", "Yazar hatası 0 (--new-content); 23 fotoğrafta bağımsız profil URL'si yok, provenance_note ile açıklanmış (provenance_status 'Eksik alan var' 23)",
  "validate_all --new-content", "validation-audit.json → media.open_provenance_points", sinir="Yazarın gerçek fotoğrafçı olduğunun kaynakta okunması K71 (L).")
c("K73", "not_checked", "0", "—", "—", sinir="KAPSAM: script yok (SKILL: K73 not_checked). L1 adayı: Fotoğraflar!60 de-ontdekfabriek-02 (Pixabay kullanıcısı olafpictures, CC0).")
c("K75", "kısmi", "fotograf-atiflari-v7.csv 226 satır Excel ile alan alan aynı (downloaded_on biçimi hariç); modifications 226/226 dolu; atıf önizleme HTML'inde 226 göreli src'nin tamamı pakette çözülüyor",
  "capraz.py (CSV/HTML ↔ Excel)", "_analiz/capraz-kontroller.json → teslimler", sinir="Görünür atıf önizlemesi K94 (ayrı aşama).")
c("K76", "kısmi", (f"Kaynaklar: 397 kayıt → 396 snapshot dosyası (kaynak:098 ve :101 aynı sayfa), SHA eşleşiyor 397/397; taze "
                   f"indirmeyle karşılaştırma {snap['compared']}/397: başlık eşleşmesi {snap['title_match']} + 1 (iki tarafta da başlık "
                   f"yok, metin örtüşmesi 1.0); örtüşme medyanı {snap['overlap_median']}; örtüşme < 0,5: {snap['overlap_lt_0_5']}; şüpheli 0; "
                   "karşılaştırılamayan 3 (taze kopya 429)"),
  "snapcmp.py (toolkit extract_page ile iki taraf aynı biçimde)", "_analiz/snapshot-karsilastirma.json; kanitlar/snap/index.jsonl",
  sinir="Fotoğraf kanıtları (Kanıtlar.source_evidence_json, 226) kaynak sayfayla karşılaştırılmadı (L1).")
c("K77", "geçti", "226/226 photo_id Fotoğraflar↔FotoğrafKaynakları↔Kanıtlar eşleşti; original_file=file ve original_sha256=sha256 226/226; evidence_id 226/226",
  "validate_all + capraz.py", "_analiz/capraz-kontroller.json → photo_chain")
c("K78", "kısmi", "author_url 203/226 (23 boş, provenance_note ile); rol karışması: 2 Public domain karede license_url = source_url (Commons dosya sayfası, PD dayanağı)",
  "capraz.py", "_analiz/capraz-kontroller.json → url_roles", sinir="Bu URL'lerin erişim sonucu L0'da test edilmedi; PD dayanağı K72 (L).")
c("K79", "kısmi", "capture_date 181/226 dolu, 45 boş; tek varsayılan tarih yok (en sık 2013-06-28 ×9, 2025-05-16 ×9); downloaded_on 226/226 2026-10-23 (download-progress-v7.json ile aynı), source_checked_on ve Kanıtlar.checked_on 226/226 2026-10-22; kanıt JSON retrieved_on 2026-10-23",
  "capraz.py tarih taraması", "_analiz/capraz-kontroller.json → dates, teslimler.download_progress", sinir="Tarih dayanaklarının kaynakta okunması L.")
c("K80", "geçti", "original_file = Fotoğraflar.file 226/226, SHA eşit; web_file WebP (218 tekil), SHA ve ölçüler beyanla aynı 226/226; derivation 226/226 dolu",
  "inventory + capraz.py", "_analiz/capraz-kontroller.json → photo_chain")
c("K81", "not_checked", "0", "—", "—", sinir="KAPSAM: script yok (SKILL: K81 not_checked). Bilgi: pixel_review_file = file 226/226; pixel_review_status insan alanı (tasarım gereği 'Bekliyor', değerlendirme dışı).")
c("K82", "kaldı", "photo-provenance-v7.json ve atıf CSV ↔ Excel: 226 satır, tüm alanlar aynı; normalized-tables-v7.json sekme sayıları Excel ile aynı; Teslimler/dosya-envanteri.json 851 yolu kapsıyor, 849 SHA aynı; farklı 2: dosya-envanteri.json (kendi hash'i, doğası gereği) ve ILERLEME_KAYDI.txt (sayımdan sonra yeniden yazılmış)",
  "capraz.py", "_analiz/capraz-kontroller.json → teslimler", ["ISS-005"], "normalized-tables-v7.json alan bazında karşılaştırılmadı.")
c("K83", "kaldı", "TESLIM_OZETI ↔ bağımsız yeniden hesap: satır farkı 0 (tarih ve MB dahil); paket envanteri ↔ denetim envanteri yol farkı 0; ACIK_KONULAR sayı satırı aynı; ILERLEME_KAYDI son kaydı eski (209 fotoğraf, 352 kaynak) ve 4× tekrar",
  "render_summary + SKILL K83 fark bloğu + k04.py", "_render/TESLIM_OZETI.txt; _analiz/k04-karsilastirma.json; Teslimler/ILERLEME_KAYDI.txt",
  ["ISS-005"], "ACIK_KONULAR'daki üretici beyanları kanıt sayılmadı; yalnız sayısal tutarlılık denetlendi.")
c("K84", "geçti", "'\\' 0: Excel yol sütunları (file, *_file) ve Teslimler JSON/CSV/HTML; mutlak yerel yol, geçici URL ve paket dışına çıkan bağlantı 0; tüm göreli yollar paket kökünden çözülüyor (missing 0)",
  "audit_prep ters_egik_cizgi + capraz.py + inventory", "_foto/hazirlik.json; _analiz/capraz-kontroller.json",
  sinir="Paket başka ortamda (Linux) fiilen açılıp denenmedi.")
c("K85", "geçti", "23/23 anahtar mevcut; tür/değer hatası 0", "validate_all", "validation-audit.json; _dump/SayfaAlanları.jsonl")
c("K86", "geçti", "Resmî doğrulayıcı hata 0 (slug çözümü dahil)", "validate_all", "validation-audit.json")
c("K87", "geçti", "timeline hata 0; Adımlar 10 kayıt (≥4)", "validate_all", "validation-audit.json")
c("K88", "geçti", "Resmî doğrulayıcı hata 0", "validate_all", "validation-audit.json")
c("K89", "kısmi", "8 temel grup, her grupta 11–16 mekân (" + ", ".join(f"{k} {v}" for k, v in groups.items()) + "); tarih payı 15/119 (eşik 0,35 altında)",
  "validate_all + capraz.py", "validation-audit.json → extras.history_share", sinir="Filtre önizlemesi ayrı aşama.")
c("K95", "geçti", "validate_all --mode audit --new-content: yapı hata 0 / uyarı 744, medya hata 0, technically_complete=True",
  "validate_all", "validation-audit.json", sinir="ready modu çalıştırılmadı: insan onayı beklediği için beklenen şekilde kapalı.")
c("K96", "geçti", "744 uyarı: 678 insan inceleme alanı (226 × 3; tasarım gereği 'Bekliyor', içerik bozukluğu değil) + 66 fotoğrafsız yer (tek kök neden, ISS-003)",
  "validate_all warning_classes", "validation-audit.json → warning_classes")
c("K97", "geçti", "Kanıtlar metadata/pixel/rights 678/678 'Bekliyor'; editorial_status tüm sekmelerde 'Taslak' (Onaylandı/Doğrulandı değeri 0); Teslimat.reviewer boş",
  "capraz.py durum taraması", "_analiz/capraz-kontroller.json → status_values, approval_like_values",
  sinir="İnsan inceleme alanları tasarım gereği 'Bekliyor'; içerikleri değerlendirme dışı (görev kuralı).")
c("K98", "geçti", "Açık 7 bulgu (3 P1 + 4 P2) 17 alanlı ISSUE şablonuyla; önceki 7 bulgunun durumu ayrı dosyada", "—", "issues.json; onceki-bulgu-durumu.json")
c("K99", "geçti", "impact.py --diff önceki Excel (SHA 01c130e6…, denetim kaydındaki SHA ile aynı kopya): changed 432, added 130, deleted 0; önceki 7 bulgu gerçek dosya farkıyla sınıflandı (kapandı 1, sürüyor 3, değişti 3)",
  "impact.py --diff + onceki.py", "impact.json; onceki-bulgu-durumu.json; _onceki/CITY-039_eindhoven_v001_2026-10-22.xlsx",
  sinir="L1 gerektiren kapanış koşulları (ISS-007 ikinci yarısı) L0'da ölçülemedi.")
c("K100", "geçti", "Kapsam matrisi paydalarıyla DENETIM_OZETI.md'de", "—", "DENETIM_OZETI.md bölüm 3")
c("K101", "geçti", "Karar editorial_score.py'den; açık P1'ler karar kapısı", "editorial_score.py", "score.json")
c("K102", "geçti", "Tüm çıktı tek klasörde (paket dışı)", "—", "denetim/eindhoven_2026-10-23_L0b/")
c("K104", "kısmi", "424 kart: dolgu 0, hedge kalıbı 1 kart (Yanıtlar!206 'kuruma sorun' meşru işlem adımı), kaçamak ilk cümle 1 kart (Yanıtlar!247 tutarları veriyor: 50/250/290/150 euro); önceki ISS-007 kartında hedge 0",
  "text_quality + kart okuması (script çıktısı)", "text-quality.json → hedges, evasive_answers", ["ISS-007"],
  "ISS-007'nin kapanışı L1 iddia denetimine (K29/K35/K41) bağlı.")
c("K106", "kısmi", "Lisanslar 226/226 ücretsiz ticari kullanıma izin veren aileden (CC BY/BY-SA/CC0/PD), medya hatası 0; Commons kaydında AI etiketi 0",
  "validate_all + photo_prefilter", "validation-audit.json; _foto/decisions.json", sinir="Piksel kökeni/AI üretimi görsel incelemesi (V) yapılmadı.")
c("K107", "kısmi", (f"Aday {dec['candidates']} = Fotoğraflar satırı 226; prefilter keep {dec['keep']} / flag {dec['flag']} / reject {dec['reject']}; "
                    "teslim: 226 ilişki, tekil mekân karesi 218, tekil kapak 8 (ayrı yazıldı, toplanmadı); kısa listesiz kayıt 66 = K22 sayısı"),
  "photo_candidates + photo_prefilter + render_summary", "_foto/candidates.jsonl; _foto/decisions.json; _render/TESLIM_OZETI.txt",
  sinir="KAPSAM: kısmi; 'flag' 4 kare L1 girdisi.")
c("K113", "geçti", "Excel, kaynak sayfaları ve üretim notları veri olarak işlendi; hiçbir içerik talimatı uygulanmadı; üretim notları (DEVIR, ACIK_KONULAR yorumları) kanıt sayılmadı",
  "—", "DENETIM_OZETI.md")
c("K114", "geçti", "original_file 226/226 = teslim JPEG (Commons'tan ≤1600 px küçültülmüş indirme; modifications'ta beyan), SHA eşleşiyor (file_ne_original 0)",
  "inventory + validate_all", "dosya-envanteri.json; validation-audit.json")
c("K115", "geçti", "25 alt ölçüt pay/payda; ilk satır editorial_score çıktısından", "editorial_score.py", "criteria.json; score.json")
c("K116", "geçti", "Karar puandan bağımsız; açık P1'ler ayrı karar kapısı", "editorial_score.py", "score.json")
c("K117", "geçti", "424 kart, 226 fotoğraf satırı/218 dosya, 2139 değişken iddia, 401 URL, 851 dosya, 23 sayfa alanı; paydadan çıkarılan kayıt yok",
  "—", "DENETIM_OZETI.md bölüm 3")
c("K118", "kısmi", "impact.py bağımlılık raporu: 562 değişiklikten 861 etkilenen kayıt, 32 kontrol önerisi; script kontrolleri bu denetimde yeniden koşuldu",
  "impact.py --diff", "impact.json → checks, impacts", sinir="Önerilen L/V kontrolleri (K25, K29, K42, K59–K62 …) L1'de.")
c("K119", "geçti", "Ham dosyalardan başlandı; üretim özeti/manifest/DEVIR yorumları kanıt sayılmadı; sonuçlar script çıktısına dayanıyor",
  "—", "DENETIM_OZETI.md")
c("K120", "kısmi", "Gönderim durumu script kararıyla açıkça yazıldı", "editorial_score.py", "score.json",
  sinir="K01–K120'nin L/V/E kısımları L0'da açık.")
for cid, why in (("K01", "Drive (drive-manual)"), ("K03", "Drive (drive-manual)"), ("K109", "Drive (drive-manual)"),
                 ("K110", "Drive (drive-manual)"), ("K92", "önizleme (preview-later)"), ("K93", "önizleme (preview-later)"),
                 ("K94", "önizleme (preview-later)"), ("K103", "önizleme (preview-later)"),
                 ("K111", "önizleme (preview-later)"), ("K112", "önizleme (preview-later)")):
    c(cid, "separate_stage", "0", "—", "—", sinir=f"Ayrı aşama: {why}; yerel paket denetimi kapsamı dışında.")

check_rows = []
for item in checks_yaml:
    cid = item["id"]
    if cid not in C:
        raise SystemExit(f"eksik kontrol: {cid}")
    durum, beklenen, incelenen, yontem, kanit, bulgular, sinir = C[cid]
    check_rows.append({"check_id": cid, "durum": durum, "beklenen_kapsam": beklenen or item["title"],
                       "incelenen_kapsam": incelenen, "yöntem": yontem, "kanıt_yolu_veya_URL": kanit,
                       "bulgu_IDleri": bulgular, "sınır_gerekçe": sinir, "checked_on": DAY})
status_counts = dict(collections.Counter(r["durum"] for r in check_rows))
meta = {"tool": "city-audit L0", "level": "L0", "label": "yerel paket denetimi", "city_id": "eindhoven",
        "catalog": "CITY-039", "xlsx": XLSX, "xlsx_sha256": XLSX_SHA, "previous_audit": "denetim/eindhoven_2026-10-22_L0",
        "previous_xlsx_sha256": PREV_SHA, "checked_on": DAY}
(OUT / "check-results.json").write_text(json.dumps({"meta": {**meta, "template": "kılavuz 2.0 bölüm 16 CHECK",
                                                             "status_counts": status_counts}, "checks": check_rows},
                                                   ensure_ascii=False, indent=1), encoding="utf-8")
(OUT / "issues.json").write_text(json.dumps({"meta": {**meta, "template": "kılavuz 2.0 bölüm 16 ISSUE",
                                                      "open": {p: [i["issue_id"] for i in issues if i["öncelik"] == p]
                                                               for p in ("P0", "P1", "P2")},
                                                      "closed_since_previous": ["ISS-004"],
                                                      "new_since_previous": ["ISS-008"]},
                                             "issues": issues}, ensure_ascii=False, indent=1), encoding="utf-8")
(OUT / "onceki-bulgu-durumu.json").write_text(json.dumps({"meta": {**meta, "note": "K99: her önceki bulgu gerçek dosya farkıyla (impact.py --diff) sınıflandı; durum ∈ kapandı | sürüyor | değişti."},
                                                          "previous": prev,
                                                          "new": [{"issue_id": "ISS-008", "öncelik": "P2", "check_id": "K14",
                                                                   "özet": f"{len(late)} kayıtta reviewed_on 2026-10-22 < bağlı kaynak checked_on 2026-10-23"}]},
                                                         ensure_ascii=False, indent=1), encoding="utf-8")

# ------------------------------------------------------------------ criteria.json (bolum 20)
E1_LIST = ("K08", "K09", "K10", "K11", "K12", "K13", "K14", "K15", "K16", "K45", "K46", "K49")
e1_pass = sum(1 for cid in E1_LIST if C[cid][0] == "geçti")
criteria = [
    {"code": "A1", "status": "not_checked", "reason": "Kullanılabilir/özgün kart sayımı K18 (L) yapılmadı; ham 289 ≥ 240 (sayısal açık yok)."},
    {"code": "A2", "status": "not_checked", "reason": "Kartın soruyu çözmesi K25/K26 (L) yapılmadı."},
    {"code": "A3", "status": "not_checked", "reason": "İddia-kaynak desteği K29 (L) yapılmadı; claim_check dize eşleşmesi (2116/2139) destek kanıtı sayılmaz."},
    {"code": "A4", "status": "not_checked", "reason": "Kritik/güncel doğruluk K34/K35 (L) yapılmadı; 0/2139 resmî kaynakta doğrulandı."},
    {"code": "A5", "status": "not_checked", "reason": "Dil/konu değeri K28/K32 (L) yapılmadı; script: tam kart kopyası yok, hedge 1/424 meşru; ISS-007 kısmen açık."},
    {"code": "B1", "status": "partial", "passed": 0, "required": 120,
     "reason": "Ham 119 (üst sınır) < 120 → ISS-001; kimlik/şube/açıklık doğrulaması K39/K42 (L) yapılmadı; doğrulanan alt sınır 0."},
    {"code": "B2", "status": "not_checked", "reason": "Ham 16/16; yerel somut karşılaştırma K44 (L) yapılmadı."},
    {"code": "B3", "status": "partial", "passed": 0, "required": 12,
     "reason": "Durak bağları 12/12 script ile geçti (K46); fiziksel uygulanabilirlik K47 (L) yapılmadı; doğrulanan alt sınır 0."},
    {"code": "B4", "status": "not_checked", "reason": "Ham 60/60; anlam/kaynak K48 (L) yapılmadı."},
    {"code": "B5", "status": "not_checked", "reason": "Koordinat aralığı geçti, 3 ortak koordinat çifti; ad/adres/harita/ziyaret durumu doğrulaması L/V yapılmadı."},
    {"code": "C1", "status": "partial", "passed": 0, "required": 250,
     "reason": "Tekil 218 kare (üst sınır) < 250 → ISS-002; görsel/hak doğrulaması V/L yapılmadı; doğrulanan alt sınır 0."},
    {"code": "C2", "status": "not_checked", "reason": "Görsel-kaynak-caption eşleşmesi K59–K62 (V) yapılmadı."},
    {"code": "C3", "status": "partial", "passed": 0, "required": 135,
     "reason": f"Herhangi bir fotoğrafı olan yer {photos['places_with_photo'] + photos['districts_with_photo']}/135 (üst sınır); 66 yer fotoğrafsız → ISS-003; doğru kare teyidi V; doğrulanan alt sınır 0."},
    {"code": "C4", "status": "partial", "passed": 0, "required": 218,
     "reason": "Aynı-kare tekrarı yalnız kapak rolünde (dHash 8 çift, rol ayrı); kırpma/netlik K65 (V) yapılmadı; doğrulanan alt sınır 0."},
    {"code": "C5", "status": "not_checked", "reason": "8 farklı kapak var (kapaklar arası tekrar yok); kapak doğruluğu K62 (V) ve uyarı bandı K103 (önizleme) yapılmadı."},
    {"code": "D1", "status": "not_checked", "reason": "Eser bazlı ücretsiz ticari izin teyidi: K67 script'i 226 adayda izinsiz lisans/kısıt 0 buldu (kısmi), K71/K72 (L) yapılmadı; etiketler 226/226 izinli aileden."},
    {"code": "D2", "status": "partial", "passed": 0, "required": 218,
     "reason": "Etiket↔URL tutarlılığı ve yazar alanı 218/218 (K69/K70); kaynakla eşleşme okunmadı; doğrulanan alt sınır 0."},
    {"code": "D3", "status": "partial", "passed": 0, "required": 218,
     "reason": "Dosya/hash zinciri 218/218 tutarlı (K77/K80/K114), kaynak snapshot'ları taze kopyayla 394/394 tutarlı (K76 kısmi); foto kanıtları açılmadı; doğrulanan alt sınır 0."},
    {"code": "D4", "status": "not_checked", "reason": "Kareye özgü ek haklar K74 (V) yapılmadı; rights_status insan alanı (tasarım gereği 'Bekliyor', değerlendirme dışı)."},
    {"code": "D5", "status": "not_checked", "reason": "Atıf CSV 226/226 Excel ile tutarlı (K75 kısmi); hedef görünümde kontrol K94 ayrı aşama."},
    {"code": "E1", "status": "ok", "passed": e1_pass, "required": len(E1_LIST),
     "reason": f"Sabit liste (başlangıçta): bölüm 02 K08–K16 + K45, K46, K49 = {len(E1_LIST)} atomik kontrol; kaldı: K14 (ISS-006, ISS-008)."},
    {"code": "E2", "status": "ok", "passed": 850, "required": 851,
     "reason": "851 beklenen dosyanın tamamı yol/format/hash ile çözülüyor; paket envanterinde ILERLEME_KAYDI.txt SHA'sı gerçek dosyayla tutmuyor (ISS-005; dosya-envanteri.json'un kendi hash'i sayılmadı)."},
    {"code": "E3", "status": "ok", "passed": 23, "required": 23, "reason": "23/23 zorunlu anahtar; resmî doğrulayıcı tür/değer/referans hatası 0."},
    {"code": "E4", "status": "separate_stage", "reason": "Web işlevleri önizleme senaryoları ayrı aşama (preview-later)."},
    {"code": "E5", "status": "partial", "passed": 3, "required": 5,
     "reason": "Kök Excel ✓, üç klasör ✓, kimlik eşleşmesi ✓; bulut dosyaları (Drive) ayrı aşama — kontrol edilmedi; sürüm/sayı tutarlılığı ✗ (ISS-005, ISS-006)."},
]
findings = [{"id": "ISS-001", "priority": "P1", "criteria": ["B1"]},
            {"id": "ISS-002", "priority": "P1", "criteria": ["C1"]},
            {"id": "ISS-003", "priority": "P1", "criteria": ["C3"]},
            {"id": "ISS-005", "priority": "P2", "criteria": ["E2", "E5"]},
            {"id": "ISS-006", "priority": "P2", "criteria": ["E1", "E5"]},
            {"id": "ISS-007", "priority": "P2", "criteria": ["A5"]},
            {"id": "ISS-008", "priority": "P2", "criteria": ["E1"]}]
(OUT / "criteria.json").write_text(json.dumps({
    "meta": {**meta, "template": "kılavuz 2.0 bölüm 20", "status_counts": status_counts,
             "note": "L0: L ve V ölçütleri not_checked; partial ölçütlerde 'passed' doğrulanan alt sınırdır. İnsan inceleme alanları değerlendirme dışı."},
    "criteria": criteria, "findings": findings,
    "coverage": {"cards": [0, 424], "photos": [0, 226], "critical_claims": [0, 2139]}}, ensure_ascii=False, indent=1),
    encoding="utf-8")
print(json.dumps({"status_counts": status_counts, "checks": len(check_rows), "issues": len(issues),
                  "E1": f"{e1_pass}/{len(E1_LIST)}"}, ensure_ascii=False))
