"""Builds check-results.json, issues.json, criteria.json for the L0 audit from script outputs.

Reads only OUT (audit folder), checks.yaml and the scratch analysis outputs. Never writes to PKG.
Usage: build_records.py <OUT> <CHECKS_YAML> <SCRATCH>
"""
import json
import shutil
import sys
from collections import Counter
from pathlib import Path

import yaml

OUT, CHECKS, SCR = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
DATE = "2026-10-22"
XLSX_NAME = "CITY-039_eindhoven_v001.xlsx"


def jload(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def dump(name):
    with (OUT / "_dump" / f"{name}.jsonl").open(encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


# ---------------------------------------------------------------- inputs
va = jload(OUT / "validation-audit.json")
inv = jload(OUT / "dosya-envanteri.json")
tq = jload(OUT / "text-quality.json")
uc = jload(OUT / "url-checks.json")
uc2 = jload(OUT / "url-checks-sehir-sayfa.json")
cs = jload(OUT / "claim-script.json")
fid = jload(OUT / "xlsx-fidelity.json") if (OUT / "xlsx-fidelity.json").exists() else None
dh = jload(OUT / "temas-sayfalari" / "dhash.json")
dec = jload(OUT / "_foto" / "decisions.json")
ana = jload(SCR / "analyze_out.json")
snap = jload(SCR / "snapcmp_out.json")
claims_n = sum(1 for line in (OUT / "claims.jsonl").open(encoding="utf-8") if line.strip())
cand_n = sum(1 for line in (OUT / "_foto" / "candidates.jsonl").open(encoding="utf-8") if line.strip())

places, districts, answers = dump("Mekânlar"), dump("Mahalleler"), dump("Yanıtlar")
photos, prov = dump("Fotoğraflar"), dump("FotoğrafKaynakları")
row_of = {r["entry_id"]: r["_row"] for r in (*places, *districts, *answers)}
counts, minimum, target = va["structure"]["counts"], va["structure"]["minimum"], va["structure"]["target"]

# copy analysis evidence into OUT (paket disi)
AN = OUT / "_analiz"
(AN / "betikler").mkdir(parents=True, exist_ok=True)
shutil.copyfile(SCR / "analyze_out.json", AN / "capraz-kontroller.json")
shutil.copyfile(SCR / "snapcmp_out.json", AN / "snapshot-karsilastirma.json")
for script in ("analyze.py", "snapcmp.py", "build_items.py", "build_records.py", "k04.py", "paths.py", "provcmp.py",
               "celltype.py", "invcmp.py"):
    if (SCR / script).exists():
        shutil.copyfile(SCR / script, AN / "betikler" / script)

# derived numbers
web_bs = ana["backslash_paths"]["FotoğrafKaynakları.web_file"]
no_photo_places = ana["places_without_photo"]
no_photo_districts = ana["districts_without_photo"]
shared = va["extras"]["shared_coordinates"]["items"]
shared_txt = "; ".join(" / ".join(f"{e.split(':', 1)[1]} (Mekânlar!{row_of.get(e)})" for e in it["entry_ids"])
                       for it in shared)
u1, u2 = uc["summary"], uc2["summary"]
url_total = u1["unique_urls"] + u2["unique_urls"]
url_200 = u1["classes"]["ok_200"] + u2["classes"]["ok_200"]
url_3xx = u1["classes"]["redirect_ok"] + u2["classes"]["redirect_ok"]
url_bad = sum(u1["classes"][k] + u2["classes"][k] for k in ("not_found_404", "gone_410", "soft_404"))
url_open = sum(u1["verdicts"][k] + u2["verdicts"][k] for k in ("erişim teyidi açık",))
lic = Counter(p["license"] for p in photos)
lic_txt = ", ".join(f"{k} {v}" for k, v in lic.most_common())
groups_txt = ", ".join(f"{k} {v}" for k, v in sorted(ana["group_counts"].items(), key=lambda kv: -kv[1]))
not_in_src = [r for r in cs["results"] if r["result"] != "supported"]
nis_by_kind = Counter(r["kind"] for r in not_in_src)
exact = tq["exact_duplicates"]
exact_photo = sum(1 for c in exact if c["sheet"] == "Fotoğraflar")
exact_ans = [c for c in exact if c["sheet"] == "Yanıtlar"]
exact_ans_txt = "; ".join(f"{c['field']}: " + "/".join(f"!{m['row']}" for m in c["members"]) for c in exact_ans)
hedges = tq["hedges"]["items"]
pkg_inv_note = ("Teslimler/dosya-envanteri.json 763 dosyayı kapsıyor; 763 ortak dosyanın SHA'sı denetim envanteriyle "
                "aynı; sonradan yazılan 9 Teslimler çıktısı (ACIK_KONULAR.txt, ILERLEME_KAYDI.txt, TESLIM_OZETI.txt, "
                "dosya-envanteri.json, fotograf-atif-onizleme.html, fotograf-atiflari-v7.csv, normalized-tables-v7.json, "
                "paket-kontrol-v7.json, photo-provenance-v7.json) o sayımda yok")

# ---------------------------------------------------------------- issues
ISSUES = [
    {
        "issue_id": "ISS-001", "öncelik": "P1", "kategori": "Berlin kapsamı / mekân hedefi", "check_id": "K17",
        "tablo": "Mekânlar", "Excel_satırı": f"{min(r['_row'] for r in places)}–{max(r['_row'] for r in places)} (104 kayıt)",
        "entry_id/photo_id": "—", "dosya": XLSX_NAME, "alan": "kayıt sayısı (places)",
        "mevcut_değer": str(counts["places"]), "beklenen": f"hedef {target['places']} (asgari {minimum['places']} karşılandı)",
        "somut_gözlem": f"Resmî doğrulayıcı sayımı places={counts['places']}, minimum={minimum['places']}, "
                        f"target={target['places']}; hedefe {target['places'] - counts['places']} mekân eksik. Grup dağılımı: {groups_txt}.",
        "kanıt": "validation-audit.json → structure.counts.places / structure.target.places; _render/TESLIM_OZETI.txt (bağımsız yeniden hesap)",
        "kullanıcı_etkisi": "Keşif bölümü Berlin üretim standardının altında; kalite oranı eksik hedefi örtmez (kılavuz bölüm 20).",
        "önerilen_düzeltme": "En az 16 gerçek, kaynaklı, şehir kapsamındaki mekân ekle; az dolu gruplara (Doğa ve açık hava 9, "
                             "Müzeler 10, Yeme ve içme 10) öncelik ver; alt nesne/collection ile şişirme yapma (K108).",
        "tekrar_kontrol_koşulu": "validate_all structure.counts.places ≥ 120 ve yeni kayıtlar L1'de K42/K108 ile doğrulanmış.",
        "durum": "Açık",
    },
    {
        "issue_id": "ISS-002", "öncelik": "P1", "kategori": "Berlin kapsamı / fotoğraf hedefi", "check_id": "K17",
        "tablo": "Fotoğraflar", "Excel_satırı": f"{min(p['_row'] for p in photos)}–{max(p['_row'] for p in photos)} (209 satır)",
        "entry_id/photo_id": "—", "dosya": XLSX_NAME + "; Fotoğraflar/",
        "alan": "tekil mekân karesi sayısı (photos)", "mevcut_değer": str(counts["photos"]),
        "beklenen": f"hedef {target['photos']} (asgari {minimum['photos']} karşılandı)",
        "somut_gözlem": f"209 fotoğraf satırı → {va['media']['different_files']} farklı dosya / {va['media']['different_source_pages']} "
                        "farklı kaynak sayfası; 8 kapak satırı mekân kareleriyle aynı SHA (rol ayrı, kare tek sayılır). "
                        f"Hedefe {target['photos'] - counts['photos']} tekil kare eksik.",
        "kanıt": "validation-audit.json → structure.counts.photos, media.different_files; dosya-envanteri.json findings.dup_sha (8); "
                 "temas-sayfalari/dhash.json (8 çift, mesafe 0)",
        "kullanıcı_etkisi": "Galeri derinliği Berlin standardının altında; fotoğrafsız kayıtlarla birleşince görsel kapsam zayıf (ISS-003).",
        "önerilen_düzeltme": "En az 49 yeni, tekil, gerçek ve ücretsiz-ticari lisanslı kare ekle; önce fotoğrafsız 60 mekân + 2 mahalleyi kapat.",
        "tekrar_kontrol_koşulu": "validate_all structure.counts.photos ≥ 250 (SHA/kaynak tekil) ve yeni kareler L1 görsel incelemesinden geçmiş.",
        "durum": "Açık",
    },
    {
        "issue_id": "ISS-003", "öncelik": "P1", "kategori": "Fotoğraf kapsamı", "check_id": "K22",
        "tablo": "Mekânlar; Mahalleler",
        "Excel_satırı": "Mekânlar!" + ",".join(str(x["row"]) for x in no_photo_places) + "; Mahalleler!" +
                        ",".join(str(x["row"]) for x in no_photo_districts),
        "entry_id/photo_id": ", ".join(x["entry_id"] for x in (*no_photo_places, *no_photo_districts)),
        "dosya": XLSX_NAME, "alan": "Fotoğraflar.entry_id ilişkisi",
        "mevcut_değer": f"fotoğraflı mekân {ana['places_with_photo']}/104; fotoğraflı mahalle {ana['districts_with_photo']}/16",
        "beklenen": "Her fiziksel mekân ve mahalle en az bir doğru, gerçek fotoğrafla kapsanır (collection istisnası kullanılmamış: 104/104 'Hayır').",
        "somut_gözlem": f"{len(no_photo_places)} mekân + {len(no_photo_districts)} mahalle hiç fotoğraf ilişkisine sahip değil. "
                        "Grup bazında fotoğrafsız mekân: " + ", ".join(f"{k} {v}" for k, v in ana["group_photo_gap"].items()) + ".",
        "kanıt": "validation-audit.json → warning_classes ('Mekân / mahalleye bağlı gerçek fotoğraf eksik' 60 + 2); "
                 "_analiz/capraz-kontroller.json → places_without_photo, districts_without_photo; _render/ACIK_KONULAR.txt",
        "kullanıcı_etkisi": "Mekân kartlarının %58'i görselsiz açılır; kullanıcı yeri tanıyamaz, keşif deneyimi ve güven zayıflar.",
        "önerilen_düzeltme": "Her kayda en az bir gerçek, tekil, ücretsiz-ticari lisanslı kare ekle; uygun kare yoksa kaydın kapsamda "
                             "kalmasına editoryal karar ver (collection etiketiyle kaçma).",
        "tekrar_kontrol_koşulu": "validate_all uyarı sınıfı 'gerçek fotoğraf eksik' = 0; yeni kareler L1 görsel (K59–K61) ve hak (K67–K74) incelemesinden geçmiş.",
        "durum": "Açık",
    },
    {
        "issue_id": "ISS-004", "öncelik": "P1", "kategori": "Teslim taşınabilirliği / dosya yolu", "check_id": "K84",
        "tablo": "FotoğrafKaynakları (+ Teslimler/photo-provenance-v7.json, Teslimler/fotograf-atiflari-v7.csv)",
        "Excel_satırı": f"{min(r['_row'] for r in prov)}–{max(r['_row'] for r in prov)} ({web_bs['backslash']}/{web_bs['total']})",
        "entry_id/photo_id": "209 fotoğraf satırının tamamı (ör. eindhoven:photo:van-abbemuseum-01)",
        "dosya": XLSX_NAME + "; Teslimler/photo-provenance-v7.json; Teslimler/fotograf-atiflari-v7.csv", "alan": "web_file",
        "mevcut_değer": web_bs["example"],
        "beklenen": "Teslimler/WebKopyalari/<sha>.webp ('/' ayırıcı; sözleşme özeti ve paketteki diğer tüm yol alanları gibi)",
        "somut_gözlem": "web_file 209/209 değerde Windows '\\' ayırıcısı var; Fotoğraflar.file, original_file, pixel_review_file ve "
                        "Kaynaklar.snapshot_file '/' kullanıyor; paketin kendi Teslimler/dosya-envanteri.json'u aynı WebP'leri '/' ile "
                        "listeliyor. PurePosixPath ayrıştırması değeri tek parça dosya adı olarak görüyor.",
        "kanıt": "_dump/FotoğrafKaynakları.jsonl (web_file); _analiz/capraz-kontroller.json → backslash_paths; "
                 "araclar/arac/core/content_delivery/validation_context.py safe_file() Path(value) kullanır → Linux/macOS'ta "
                 "'Dosya bulunamadı' (kod okumasından çıkarım; Linux'ta fiilen çalıştırılmadı); photo-provenance-v7.json 209 ve CSV 209 '\\' yol",
        "kullanıcı_etkisi": "Paket Windows dışı ortamda (sunucu/Linux içe aktarımı) açıldığında 201 WebP web kopyası bulunamaz; "
                            "resmî doğrulayıcı ve web aktarımı medya hatası verir.",
        "önerilen_düzeltme": "web_file değerlerini '/' ayırıcıya çevir; photo-provenance-v7.json ve fotograf-atiflari-v7.csv'yi aynı "
                             "araçla yeniden üret.",
        "tekrar_kontrol_koşulu": "Paketteki tüm yol alanlarında '\\' sayısı 0; validate_all --new-content POSIX ortamında medya hatası 0.",
        "durum": "Açık",
    },
    {
        "issue_id": "ISS-005", "öncelik": "P2", "kategori": "Teslim özeti / ilerleme kaydı", "check_id": "K83",
        "tablo": "—", "Excel_satırı": "—", "entry_id/photo_id": "—",
        "dosya": "Teslimler/TESLIM_OZETI.txt; Teslimler/ILERLEME_KAYDI.txt; Teslimler/dosya-envanteri.json",
        "alan": "Paket boyutu satırı; son ilerleme kaydı",
        "mevcut_değer": "TESLIM_OZETI: 'Paket: 763 dosya, 199.68 MB (ölçülen)'; ILERLEME_KAYDI son kayıt: 'Faz: photos … "
                        "İndirilmiş fotoğraflar: 0 … Sonraki somut adım: commons_search -> … -> indirme'",
        "beklenen": f"Özet teslim edilen paketi tarif eder: {inv['totals']['files']} dosya, {inv['totals']['total_mb']} MB "
                    "(ya da 'Teslimler çıktıları hariç' notu); son kayıt 209 satır / 201 dosyanın indirildiğini gösterir.",
        "somut_gözlem": pkg_inv_note + ". Özetin geri kalanı (sekme sayıları, Berlin matrisi, fotoğraflı mekân 44/104, mahalle 14/16) "
                        "denetimin bağımsız yeniden hesabıyla (_render/TESLIM_OZETI.txt) aynı.",
        "kanıt": "dosya-envanteri.json (denetim) ↔ Teslimler/dosya-envanteri.json; _render/TESLIM_OZETI.txt",
        "kullanıcı_etkisi": "Teslimi okuyan kişi paket boyutu ve faz durumu hakkında eski bilgi görür (işlevi bozmaz).",
        "önerilen_düzeltme": "TESLIM_OZETI ve ILERLEME_KAYDI'nı son paket durumundan yeniden üret veya sayım kapsamını açıkça yaz.",
        "tekrar_kontrol_koşulu": "TESLIM_OZETI dosya/MB değeri denetim envanteriyle eşleşir; ILERLEME_KAYDI son kaydı teslim durumunu gösterir.",
        "durum": "Açık",
    },
    {
        "issue_id": "ISS-006", "öncelik": "P2", "kategori": "Teslim kaydı / tarih", "check_id": "K14",
        "tablo": "Teslimat", "Excel_satırı": "8", "entry_id/photo_id": "city-039-v001", "dosya": XLSX_NAME,
        "alan": "updated_on; notes",
        "mevcut_değer": "updated_on 2026-10-12; notes 'Çalışma dosyası; içerik üretilmedi; UAT durumu: Üretilecek. Katalog tarihleri "
                        "kaynak kaydını gösterir; rehber doğrulaması değildir.'",
        "beklenen": "updated_on son güncellemeyi gösterir (içerik reviewed_on/checked_on 2026-10-22); notes teslim edilen içeriği doğru tarif eder.",
        "somut_gözlem": "Girdi şablonundaki (ekler_eindhoven/CITY-039_eindhoven_v001.xlsx) Teslimat satırıyla yalnız delivery_id farklı "
                        "(CITY-039-v001 → city-039-v001); updated_on ve notes aynen kalmış. Paket 289 yanıt, 104 mekân, 209 fotoğraf satırı içeriyor.",
        "kanıt": "_dump/Teslimat.jsonl; şablon dökümü (xlsx_dump, ekler_eindhoven/CITY-039_eindhoven_v001.xlsx Teslimat)",
        "kullanıcı_etkisi": "Yönetim/teslim kaydı paketin içeriksiz olduğunu söylüyor; sürüm/tarih takibi yanıltıcı.",
        "önerilen_düzeltme": "updated_on ve notes'u güncelle; alan Atınç'a aitse ona bildir (reviewer boş kalmalı).",
        "tekrar_kontrol_koşulu": "Teslimat.updated_on ≥ son içerik tarihi ve notes içerik durumunu doğru yansıtıyor.",
        "durum": "Açık",
    },
    {
        "issue_id": "ISS-007", "öncelik": "P2", "kategori": "Metin kalitesi / okuyucuya bırakılan doğrulama", "check_id": "K104",
        "tablo": "Yanıtlar", "Excel_satırı": str(hedges[0]["row"]) if hedges else "194",
        "entry_id/photo_id": "eindhoven:ev-sigortalari-opstal-inboedel-aansprakelijkheid", "dosya": XLSX_NAME,
        "alan": "summary; note",
        "mevcut_değer": "summary: '… opstalverzekering … mülk sahipleri için zorunludur; sayfa bu kuralın yasal dayanağını göstermiyor.' "
                        "note: 'Opstal zorunluluğu yalnız Holland Expat Center South sayfasında geçiyor; yasal dayanağı resmî bir kaynakla doğrulanamadı.'",
        "beklenen": "Kural resmî kaynakla doğrulanıp yazılır veya kesin olmayan kural kesin gibi sunulmaz; iç editoryal doğrulama notu "
                    "kullanıcı metninde yer almaz (K104).",
        "somut_gözlem": "text_quality hedge kalıbı 'resmi_kaynaktan_dogrula' bu kartta; aynı taramada işaretlenen Yanıtlar!206 "
                        "('kuruma sorun' meşru işlem adımı) ve Yanıtlar!247 (tutarları veriyor: 50/250/290/150 euro) bulgu sayılmadı.",
        "kanıt": "text-quality.json → hedges.items, evasive_answers.items; _dump/Yanıtlar.jsonl satır 194",
        "kullanıcı_etkisi": "Okuyucu kartın doğrulayamadığı bir zorunluluğu kendisi doğrulamak zorunda; zorunluluk bilgisi yanlışsa yanıltıcı olabilir.",
        "önerilen_düzeltme": "Opstal zorunluluğunu resmî/hukuki kaynakla doğrula (yasal zorunluluk mu, ipotek şartı mı) ve metni buna göre "
                             "yeniden yaz; iç notu kaldır.",
        "tekrar_kontrol_koşulu": "text_quality hedge bu kartta 0 ve L1 iddia denetiminde (K29/K35/K41) iddia 'supported'.",
        "durum": "Açık",
    },
]
FINDING_CRITERIA = {"ISS-001": ["B1"], "ISS-002": ["C1"], "ISS-003": ["C3"], "ISS-004": ["E1", "E2"],
                    "ISS-005": ["E5"], "ISS-006": ["E1", "E5"], "ISS-007": ["A5"]}

# ---------------------------------------------------------------- checks
checks = yaml.safe_load(CHECKS.read_text(encoding="utf-8"))["checks"]
by_id = {c["id"]: c for c in checks}
V, A = "validation-audit.json", "_analiz/capraz-kontroller.json"


def rec(durum, beklenen, incelenen, yontem, kanit, bulgu=(), sinir=""):
    return {"durum": durum, "beklenen_kapsam": beklenen, "incelenen_kapsam": incelenen, "yöntem": yontem,
            "kanıt_yolu_veya_URL": kanit, "bulgu_IDleri": list(bulgu), "sınır_gerekçe": sinir}


S = {
    "K02": rec("geçti", "Paketteki tüm dosyalar gerçek baytlarıyla", f"{inv['totals']['files']}/{inv['totals']['files']} dosya okundu, "
               f"SHA-256 hesaplandı; {inv['summary']['images']} görsel çözüldü; okuma hatası {inv['summary']['errors']}",
               "inventory.py (başlangıç ve bitiş)", "dosya-envanteri.json; _dosya-envanteri-son.json",
               sinir="Drive kopyasıyla karşılaştırma K03 (ayrı aşama)."),
    "K04": rec("geçti", "Denetim başı ve sonu paket SHA listeleri", "(son adımda doldurulur)",
               "inventory.py ×2 + SHA listesi karşılaştırma betiği", "dosya-envanteri.json; _dosya-envanteri-son.json; _analiz/k04-karsilastirma.json"),
    "K05": rec("geçti", "Kök XLSX + Fotoğraflar, Lisans kanıtları, Teslimler; artık/orphan/çoklu Excel yok",
               "Kök: 1 XLSX; Fotoğraflar 209, Lisans kanıtları 351, Teslimler 211 dosya; orphan 0; Teslimler'deki 10 dosya resmî araç "
               "çıktısı (check_delivery, delivery_tools, download_media); ikinci Excel yok",
               "inventory.py findings + dosya listesi", "dosya-envanteri.json (folders, findings.orphans, orphans_excluded)",
               sinir="KAPSAM: kısmi; çoklu Excel denetimi envanter listesinden yapıldı."),
    "K08": rec("geçti", "16 veri sekmesi, başlık satırları ve teslim profili", "16/16 sekme (missing_sheets 0); yapı girdi şablonuyla aynı; "
               "resmî doğrulayıcı yapı hatası 0", "xlsx_dump + xlsx_fidelity (şablon: ekler_eindhoven/CITY-039_eindhoven_v001.xlsx) + validate_all",
               f"_dump/summary.json; xlsx-fidelity.json; {V}"),
    "K09": rec("geçti", "Formül, veri doğrulama, donmuş bölme, tablo yapıları", "xlsx_fidelity fark 0 (kabul edilen openpyxl parça farkları: "
               "sharedStrings kaldırıldı, docProps eklendi); formül sütunları Konular.used_count, Fotoğraflar.unique_hero_count/unique_venue_count",
               "xlsx_fidelity + xlsx_dump", "xlsx-fidelity.json; _dump/summary.json"),
    "K10": rec("geçti", "Sekme bazlı ham satır / tekil kimlik / yer tutucu", "16 sekme, 2069 satır; tekrar kimlik 0, boş anahtar 0; yer "
               "tutucu: text_quality 0; validate_all ek kontrolünün 1 adayı (Yanıtlar!177 steps, alıntılı başlık 'belastingaangifte 2025?') yanlış pozitif",
               "xlsx_dump + text_quality + validate_all ek kontrol", f"_dump/summary.json; text-quality.json; {V} extras.placeholders",
               sinir="Editoryal kullanılabilir sayı K18 (L) kapsamında."),
    "K11": rec("geçti", "entry_id = city_id:slug, ASCII kimlikler", "Resmî doğrulayıcı kimlik/slug hatası 0 (2069 satır)", "validate_all", V),
    "K12": rec("geçti", "Tüm yabancı anahtarlar", "Resmî doğrulayıcı bağ hatası 0; ek: 12 rota 2–8 durak, stops↔stop_entry_ids eşleşmesi "
               "sorunsuz; pixel_review_file = file 209/209", "validate_all + çapraz kontrol", f"{V}; {A}"),
    "K13": rec("geçti", "Tür, enum, liste, JSON alanları", "Resmî doğrulayıcı tür/enum hatası 0. Bilgi: photo-provenance-v7.json ve atıf CSV'sinde "
               "downloaded_on '2026-10-22 00:00:00' biçiminde, Excel dökümünde YYYY-MM-DD (bulgu açılmadı)", "validate_all + manifest karşılaştırması",
               f"{V}; _analiz/betikler/provcmp.py"),
    "K14": rec("kaldı", "checked_on/reviewed_on/updated_on ve sıra alanları", "İçerik tarihleri: reviewed_on 2026-10-22 (tüm kartlar), "
               "checked_on 2026-10-22 (352 kaynak); sıra çakışması 0 (resmî doğrulayıcı). Teslimat.updated_on 2026-10-12 şablondan kopya",
               "validate_all + şablon karşılaştırması", f"{V}; _dump/Teslimat.jsonl", ["ISS-006"]),
    "K15": rec("kaldı", "Tüm göreli dosya yolları güvenli ve tek anlamlı", "Fotoğraflar.file 209, original_file 209, pixel_review_file 209, "
               f"snapshot_file 352 '/' ile; web_file {web_bs['backslash']}/{web_bs['total']} '\\' ile. Mutlak yol, '..', sembolik bağlantı yok",
               "inventory + validate_all + yol ayırıcı taraması", f"{A} → backslash_paths", ["ISS-004"],
               "Windows'ta çözülüyor; POSIX'te tek parça dosya adı (PurePosixPath gösterimi)."),
    "K16": rec("geçti", "EkDetaylar, uzun alanlar, 32.767 sınırı", f"EkDetaylar 0 satır; UzunAlanlar yok; en uzun hücre {ana['longest_cell'][0]} "
               f"karakter ({ana['longest_cell'][1]}); long_values_restored 0", "xlsx_dump + validate_all", f"_dump/summary.json; {A}",
               sinir="KAPSAM: kısmi; EkDetaylar boş olduğundan gölge alan denetimi konusuz."),
    "K17": rec("kaldı", "8 sayı için alt sınır / hedef / fiilî", "; ".join(
               f"{k} {counts[k]} ({minimum[k]}/{target[k]} {'✓' if counts[k] >= target[k] else '✗'})"
               for k in ("answers", "places", "neighborhoods", "topics", "photos", "hero_photos", "routes", "glossary")) +
               f"; acceptance_version {va['structure']['acceptance_version']}", "validate_all (resmî sayım) + render_summary yeniden hesap",
               f"{V} structure.counts/minimum/target; _render/TESLIM_OZETI.txt", ["ISS-001", "ISS-002"],
               "Editoryal kullanılabilir sayı L (K18); burada ham/tekil sayılar."),
    "K21": rec("geçti", "409 kart (yanıt+mekân+mahalle) için en az bir işlem bağlantısı", "Bağlantısız 0, yalnız harita 0 (409/409)",
               "text_quality action_links + çapraz kontrol", "text-quality.json action_links; " + A,
               sinir="Bağlantının doğru işleme gitmesi K53 (L)."),
    "K22": rec("kaldı", "Her mekân/mahalle için fotoğraf ilişkisi", f"Fotoğraflı mekân {ana['places_with_photo']}/104, mahalle "
               f"{ana['districts_with_photo']}/16; collection=Hayır 104/104", "validate_all uyarıları + çapraz kontrol",
               f"{V} warning_classes; {A}", ["ISS-003"], "Fotoğrafın doğru yeri göstermesi K60 (V), L0'da bakılmadı."),
    "K23": rec("geçti", "SHA/kaynak kümeleri, rol bazlı sayım", f"209 satır → {va['media']['different_files']} farklı dosya, "
               f"{va['media']['different_source_pages']} farklı kaynak sayfası; 8 kapak satırı mekân karesiyle aynı SHA (rol ayrı: kapak 8, mekân 201); "
               "dHash yakın eşler yalnız bu 8 çift", "validate_all media + inventory dup_sha + contact_sheet dHash",
               f"{V} media; dosya-envanteri.json findings.dup_sha; temas-sayfalari/dhash.json"),
    "K24": rec("kısmi", "Kalite kontrolleri sonrası yeniden sayım", "Asgari eşiklerin tamamı ham sayımla karşılanıyor; hedef eksikleri ayrı "
               "görünür (ISS-001/002). Kalite sonrası yeniden sayım L/V sonuçları olmadan yapılamadı", "render_summary + validate_all",
               "_render/TESLIM_OZETI.txt", ["ISS-001", "ISS-002"], "L/V elemesi yapılmadığından kullanılabilir sayı yok."),
    "K27": rec("geçti", "Başlık/summary/steps/documents/timing/cost/note birebir tekrar", f"{tq['summary']['exact_clusters']} birebir küme "
               f"({tq['summary']['exact_records']} kayıt): {exact_photo}'i kapak↔mekân aynı kaynak dosyasının modifications metni; "
               f"{len(exact_ans)}'i yakın kart çiftlerinde ortak alan ({exact_ans_txt}). Tam kart kopyası yok; Yanıtlar'da ≥3 kayıtlık şablon kümesi yok",
               "text_quality", "text-quality.json exact_duplicates / template_duplicates",
               sinir="Ortak alanların meşruiyeti anlamsal olarak K28 (L)."),
    "K30": rec("kısmi", "Konular arası toplu genel kaynak ataması", "Toplu anasayfa ataması 0 (validate_all ek kontrol); url_check "
               "'homepage_only' 3 kaynak (Kaynaklar!354–356: mekânların kendi siteleri)", "extra_checks + url_check",
               f"{V} extras.homepage_only_sources; url-checks.json", sinir="İddia bazında gerçek destek K29 (L)."),
    "K33": rec("kısmi", "visual_json yapısı ve doğruluğu", f"visual_json {tq['visual_json']['valid']}/{tq['visual_json']['total']} kartta dolu ve "
               f"geçerli, hata 0; {tq['visual_json']['empty']} boş (isteğe bağlı)", "text_quality", "text-quality.json visual_json",
               sinir="Görselin steps ile anlamsal uyumu L."),
    "K43": rec("kısmi", "Koordinat aralığı ve anlamlılığı", f"104 koordinat aralıkta; aynı koordinatlı 3 çift: {shared_txt}",
               "validate_all + extra_checks.shared_coordinates", f"{V} extras.shared_coordinates",
               sinir="Harita/adres doğrulaması L/V; aynı bina/meydan olabilir (L1'de K42/K108 ile)."),
    "K45": rec("geçti", "16 mahalle compare_json", "Resmî doğrulayıcı hata 0", "validate_all", V),
    "K46": rec("geçti", "12 rota durak ilişkileri", "Durak 2–8, stops/ID uzunluk-sıra eşleşmesi, ilk durak = entry_id: sorun 0",
               "validate_all + çapraz kontrol", f"{V}; {A} routes_problems"),
    "K49": rec("geçti", "Tüm içerik URL'lerinin biçimi", f"{url_total} benzersiz URL: biçim sorunu 0, geçersiz 0", "validate_all + url_check",
               "url-checks.json; url-checks-sehir-sayfa.json"),
    "K50": rec("geçti", "İçerik URL'lerinin fiilî HTTP erişimi (Kaynaklar, Bağlantılar, Şehir, SayfaAlanları)",
               f"{url_total}/{url_total} test edildi: 200 {url_200}, yönlendirme→200 {url_3xx}, bozuk {url_bad}, erişim teyidi açık {url_open}; "
               f"{u1['relations'] + u2['relations']} ilişki", "url_check --retry-transient (taze önbellek, OUT/_cache)",
               "url-checks.json; url-checks-sehir-sayfa.json",
               sinir="Fotoğraf kaynak/lisans/dosya URL'lerinin erişimi K78 kapsamında, L0'da test edilmedi."),
    "K52": rec("geçti", "403/429/geçici hata ayrımı", "İlk geçişte 1 TLS el sıkışma zaman aşımı (rotterdam-bk.mfa.gov.tr/Mission/ShowInfoNote/417062); "
               "yeniden denemede 200. 403/429 yok; erişim engeli aşılmadı", "url_check --retry-transient + fetch_snapshot yeniden deneme",
               "url-checks.json; kanitlar/snap/index.jsonl"),
    "K56": rec("geçti", "Benzersiz URL ↔ ilişki geri dağıtımı", f"{u1['unique_urls']} benzersiz URL → {u1['relations']} ilişki (Kaynaklar 352, "
               f"Bağlantılar 562) + {u2['unique_urls']} → {u2['relations']}; test edilmeyen 0; hatalar alan adına göre gruplu",
               "url_check", "url-checks.json (urls[], relations[]); url-checks-sehir-sayfa.json"),
    "K57": rec("geçti", "Tüm görsel dosyalar gerçek çözücüyle", f"{inv['summary']['images']} görsel (209 JPEG + 201 WebP) açıldı; uzantı/format "
               "uyuşmazlığı 0; bozuk 0", "inventory + validate_all image_decoding", f"dosya-envanteri.json; {V} media.checks"),
    "K58": rec("geçti", "SHA, bayt ve piksel ölçüleri", "Beyan SHA = ölçülen (sha_mismatch 0); web_width/height beyanı = ölçülen 209/209; "
               "ölçüler çeşitli (tek varsayılan yok)", "inventory + çapraz kontrol", f"dosya-envanteri.json; {A} web_dims_top"),
    "K63": rec("geçti", "SHA/kaynak + algısal yakın tekrar", f"dHash (eşik {dh['threshold']}) 209 kare: {len(dh['pairs'])} yakın çift, hepsi mesafe 0 "
               "kapak↔mekân aynı dosya (rol ayrı, tek kare sayıldı); başka yakın tekrar yok", "contact_sheet dHash + inventory dup_sha",
               "temas-sayfalari/dhash.json", sinir="Algısal eşleşme tek başına karar değil; görsel teyit L1."),
    "K64": rec("not_checked", "AI/yer tutucu köken işaretleri", "0", "photo_rules (photo_prefilter üzerinden)", "_foto/candidates.jsonl (0 satır); _foto/decisions.json",
               sinir=f"photo_candidates from-evidence {cand_n} aday döndü: paket 'Lisans kanıtları/*.source-evidence.json' içermiyor "
                     "(kanıt Excel Kanıtlar sekmesinde); photo_rules çalışacak aday yok. Piksel analizi L0 dışı."),
    "K66": rec("kısmi", "Görsel inceleme sonrası kullanılabilir kare sayımı", "Teknik kredi sayımı: 201 mekân + 8 kapak (resmî)",
               "render_summary + validate_all", f"_render/TESLIM_OZETI.txt; {V}", sinir="Görsel inceleme yapılmadığından doğrulanmış sayı yok."),
    "K67": rec("not_checked", "Her karenin tekil eser sayfasındaki lisans", "0", "photo_candidates + photo_rules (KAPSAM)", "_foto/candidates.jsonl (0 satır)",
               sinir="from-evidence 0 aday → Commons lisans alanı kontrolü çalışmadı; etiket/URL tutarlılığı K69'da ayrıca geçti."),
    "K68": rec("geçti", "NC/ND/editorial-only/ücretli koşul yok", f"209 satır: {lic_txt}; reddedilen koşul yok", "validate_all + lisans dağılımı",
               f"{V} media; _dump/Fotoğraflar.jsonl"),
    "K69": rec("geçti", "Lisans etiketi/sürüm ↔ resmî URL", "license_label_url geçti (209), medya hatası 0", "validate_all", f"{V} media.checks"),
    "K70": rec("geçti", "Yazar alanı ve profil kaydı", f"Yazar hatası 0 (--new-content); {len(ana['author_url_empty'])} fotoğrafta bağımsız profil URL'si yok, "
               "provenance_note ile açıklanmış (sözleşmeye uygun)", "validate_all --new-content", f"{V} media.open_provenance_points",
               sinir="Yazarın gerçek fotoğrafçı olduğunun kaynakta okunması K71 (L)."),
    "K73": rec("not_checked", "Özel açık/ücretsiz stok lisansları", "0", "—", "—",
               sinir="KAPSAM: script yok (SKILL: K73 not_checked). L1 adayı: Fotoğraflar!60 de-ontdekfabriek-02 (Pixabay kullanıcısı "
                     "olafpictures, Commons'ta CC0 1.0)."),
    "K75": rec("kısmi", "Atıf ve değişiklik kaydı", "fotograf-atiflari-v7.csv 209 satır Excel ile alan alan aynı (downloaded_on biçimi hariç); "
               "modifications 209/209 dolu", "manifest karşılaştırması", "_analiz/betikler/provcmp.py; Teslimler/fotograf-atiflari-v7.csv (paket)",
               sinir="Görünür atıf önizlemesi K94 (ayrı aşama)."),
    "K76": rec("kısmi", "Kaynak ve fotoğraf kanıtlarının gerçek yanıt olması", f"Kaynaklar: 352 kayıt → {ana['source_snapshot_files_unique']} snapshot "
               f"dosyası, SHA eşleşiyor; taze indirmeyle başlık eşleşmesi {snap['title_match']}/{snap['sources']} (kalan {snap['title_differ']}'u "
               f"başlıksız taze yanıt, metin örtüşmesi ≥0,97); metin örtüşmesi medyan {snap['overlap_median']}, <0,5 olan {snap['overlap_lt_0_5_all']}",
               "fetch_snapshot + snapshot karşılaştırma betiği", "kanitlar/snap/index.jsonl; _analiz/snapshot-karsilastirma.json",
               sinir="Fotoğraf kanıtları (Kanıtlar.source_evidence_json, 209) kaynak sayfayla karşılaştırılmadı (L1)."),
    "K77": rec("geçti", "photo_id → kaynak zinciri tekil eşleşmesi", "209/209 photo_id Fotoğraflar↔FotoğrafKaynakları↔Kanıtlar eşleşti; "
               "original_file=file ve original_sha256=sha256 209/209", "validate_all + çapraz kontrol", f"{V} media; {A}"),
    "K78": rec("kısmi", "Beş URL rolü ve erişimi", f"Rol karışması 0; author_url {209 - len(ana['author_url_empty'])}/209 (kalan not ile boş)",
               "çapraz kontrol", f"{A} k78_role_mixups, author_url_empty", sinir="Bu URL'lerin erişim sonucu L0'da test edilmedi."),
    "K79": rec("kısmi", "capture_date / downloaded_on / source_checked_on dayanakları", f"capture_date {209 - ana['capture_date_empty']}/209 dolu, "
               f"{ana['capture_date_empty']} boş; tek varsayılan tarih yok (en sık {ana['capture_date_top'][1][0]} ×{ana['capture_date_top'][1][1]}); "
               "downloaded_on ve source_checked_on 209/209 2026-10-22", "çapraz kontrol", A, sinir="Tarih dayanaklarının kaynakta okunması L."),
    "K80": rec("geçti", "original_file ↔ web türevi ilişkisi", "original_file = Fotoğraflar.file 209/209, SHA eşit; web_file WebP, SHA ve ölçüler "
               "beyanla aynı 209/209; derivation 209/209 dolu", "inventory + çapraz kontrol", f"dosya-envanteri.json; {A}",
               sinir="web_file yol ayırıcısı ISS-004 (K84) altında."),
    "K81": rec("not_checked", "İncelenen kare = teslim karesi", "0", "—", f"{A} pixel_review_file_mismatch",
               sinir="KAPSAM: script yok (SKILL: K81 not_checked). Bilgi: pixel_review_file = file 209/209 ama pixel_review_status "
                     "209/209 'Bekliyor'; eşleştirilecek gerçek inceleme kaydı yok."),
    "K82": rec("kaldı", "Excel ↔ manifestler ↔ envanter alan bazında", "photo-provenance-v7.json ve atıf CSV ↔ Excel: 209 satır, tüm alanlar "
               f"aynı (downloaded_on biçimi hariç). {pkg_inv_note}. Çelişki: aynı WebP'ler dosya-envanteri.json'da '/', Excel/photo-provenance/CSV'de '\\'",
               "manifest ve envanter karşılaştırma betikleri", "_analiz/betikler/provcmp.py, invcmp.py; " + A, ["ISS-004"],
               "normalized-tables-v7.json alan bazında karşılaştırılmadı."),
    "K83": rec("kaldı", "TESLIM_OZETI, ACIK_KONULAR, ILERLEME_KAYDI ↔ ölçüm", "TESLIM_OZETI sayıları bağımsız yeniden hesapla aynı (sekme "
               "sayıları, Berlin matrisi, 44/104, 14/16); farklar: paket boyutu 763/199.68 MB ↔ 772/204.04 MB, ILERLEME_KAYDI son kaydı eski, "
               "Teslimat satırı şablondan", "render_summary (OUT/_render) + envanter karşılaştırması", "_render/TESLIM_OZETI.txt; dosya-envanteri.json",
               ["ISS-005", "ISS-006"], "ACIK_KONULAR'daki üretici beyanları kanıt sayılmadı; yalnız sayısal tutarlılık denetlendi."),
    "K84": rec("kaldı", "Başka ortamda kayıpsız okunabilirlik", "Mutlak yerel yol yok (Excel + Teslimler metin dosyaları tarandı); web_file 209 yol "
               "'\\' ayırıcılı → POSIX'te çözülmez", "yol taraması + PurePosixPath ayrıştırması + resmî safe_file() kod okuması",
               f"{A} backslash_paths; _analiz/betikler/paths.py", ["ISS-004"], "Paket Linux'ta fiilen açılıp denenmedi (çıkarım)."),
    "K85": rec("geçti", "23 zorunlu SayfaAlanları anahtarı", f"23/23 anahtar mevcut ({', '.join(ana['sayfa_keys'][:3])} … emergency); tür/değer hatası 0",
               "validate_all + çapraz kontrol", f"{V}; {A} sayfa_keys"),
    "K86": rec("geçti", "facts, quick_links, advice_entry", "Resmî doğrulayıcı hata 0 (slug çözümü dahil)", "validate_all", V),
    "K87": rec("geçti", "timeline ve Adımlar", f"timeline hata 0; Adımlar {ana['adimlar_count']} kayıt (≥4)", "validate_all", V),
    "K88": rec("geçti", "budget_fields 10 anahtar", "Resmî doğrulayıcı hata 0", "validate_all", V),
    "K89": rec("kısmi", "place_groups ve filtreler", f"8 temel grup, her grupta 9–16 mekân ({groups_txt})", "validate_all + çapraz kontrol",
               f"{V}; {A} group_counts", sinir="Filtre önizlemesi ayrı aşama."),
    "K95": rec("geçti", "Resmî doğrulayıcı tam paketle", f"validate_all --mode audit --new-content: yapı hata {va['summary']['structure']['errors']} / "
               f"uyarı {va['summary']['structure']['warnings']}, medya hata {va['summary']['media']['errors']}, technically_complete="
               f"{va['summary']['technically_complete']}", "validate_all.py <xlsx> <pkg> --tools araclar/arac --mode audit --new-content", V,
               sinir="ready modu çalıştırılmadı: insan onayı (reviewer, Onaylandı, Doğrulandı) beklediği için beklenen şekilde kapalı. "
                     "689 uyarı = 627 insan inceleme alanı (209×3) + 62 fotoğrafsız yer."),
    "K97": rec("geçti", "AI ile insan kararının ayrılması", "Kanıtlar metadata/pixel/rights 627/627 'Bekliyor'; editorial_status tüm sekmelerde "
               "'Taslak' (Onaylandı yok); Teslimat.reviewer boş; completion_credit onay sayılmıyor (sözleşme)", "xlsx_dump alan dağılımı + validate_all",
               f"_dump/Kanıtlar.jsonl; _dump/Teslimat.jsonl; {V} warning_classes"),
    "K99": rec("uygulanmaz", "Düzeltme sonrası hedefli yeniden kontrol", "—", "—", "—", sinir="İlk denetim; önceki denetim/düzeltme yok, impact.py çalıştırılmadı."),
    "K100": rec("geçti", "Kapsamın sayısal raporu", "Kapsam matrisi paydalarıyla DENETIM_OZETI.md'de", "editorial_score + rapor", "DENETIM_OZETI.md; score.json"),
    "K104": rec("kaldı", "Okuyucuya doğrulama işi bırakan metinler", f"409 kart: dolgu 0, hedge kalıbı {tq['hedges']['cards_with_hedge']} kart, kaçamak ilk "
                "cümle 1 kart. Ayrım: Yanıtlar!206 'kuruma sorun' meşru işlem adımı; Yanıtlar!247 tutarları veriyor; Yanıtlar!194 iç doğrulama notu kullanıcı metninde",
                "text_quality + işaretli metnin deterministik kontrolü", "text-quality.json hedges, evasive_answers; _dump/Yanıtlar.jsonl", ["ISS-007"]),
    "K106": rec("kısmi", "Ücretsiz ve gerçek fotoğraf şartı", "Lisanslar 209/209 ücretsiz ticari kullanıma izin veren aileden (CC BY/BY-SA/CC0/PD), "
                "medya hatası 0", "validate_all lisans", f"{V} media", sinir="AI üretimi/piksel kökeni (V) ve photo_rules AI etiketi (aday 0) incelenmedi."),
    "K107": rec("not_checked", "Aday / seçilen / ret / teslim ayrımı", "0", "photo_candidates + photo_prefilter", "_foto/candidates.jsonl (0); _foto/decisions.json",
                sinir="Paket kanıt JSON dosyası içermiyor; from-evidence 0 aday, prefilter keep/flag/reject 0 → aday kümesi ölçülemedi."),
    "K114": rec("geçti", "original_file beyanı ↔ gerçek bayt", "original_file 209/209 = teslim JPEG (Commons'tan ≤1600 px küçültülmüş indirme; "
                "modifications'ta beyan edilmiş), SHA eşleşiyor (file_ne_original 0); kamera orijinali iddiası yok; original_file_url tam çözünürlük",
                "inventory + validate_all", f"dosya-envanteri.json; {V}"),
    "K115": rec("geçti", "Rapor başında editoryal yüzde ve karar", "25 alt ölçüt pay/payda; ilk satır editorial_score çıktısından",
                "editorial_score.py", "criteria.json; score.json; score.md; DENETIM_OZETI.md"),
    "K118": rec("uygulanmaz", "Düzeltmenin bağımlılara yayılması", "—", "—", "—", sinir="Önceki denetim/düzeltme yok."),
}

M = {
    "K06": rec("geçti", "Yetenek ve erişim sınırları kaydı", "XLSX okuma, bayt/SHA, HTTP erişimi ve kod çalıştırma fiilen kullanıldı; görsel "
               "inceleme ve LLM iddia denetimi L0 dışı (yapılmadı, GEÇTİ sayılmadı)", "süreç kaydı", "DENETIM_OZETI.md (çalıştırılmayan kontroller)"),
    "K07": rec("kısmi", "Berlin referansı ve sürümleri", "Alt sınır/hedefler resmî doğrulayıcının acceptance_version 2026-10-13.1 değerlerinden",
               "validate_all", V, sinir="Berlin örnek Excel'i bu L0 denetiminde açılmadı."),
    "K96": rec("geçti", "Hata türlerinin kök nedene göre gruplanması", "689 uyarı: 627 insan inceleme alanı (onay, içerik bozukluğu değil) + 62 "
               "fotoğrafsız yer (tek kök neden)", "validate_all warning_classes", V),
    "K98": rec("geçti", "Kanıtlı sorun kayıtları", f"{len(ISSUES)} bulgu, 17 alanlı ISSUE şablonuyla", "issues.json", "issues.json"),
    "K101": rec("geçti", "Karar engellere göre", "Karar editorial_score.py'den; açık P1'ler karar kapısı", "editorial_score", "score.json"),
    "K102": rec("geçti", "Bağımsız okunabilir tek denetim paketi", "Tüm çıktı tek klasörde (paket dışı)", "süreç", "DENETIM_OZETI.md"),
    "K113": rec("geçti", "İçerik talimat değildir", "Excel, kaynak sayfaları ve üretim notları veri olarak işlendi; hiçbir içerik talimatı uygulanmadı; "
                "üretim notları kanıt sayılmadı", "süreç", "—"),
    "K116": rec("geçti", "Puan engelleri örtmez", "Karar puandan bağımsız; açık P1'ler ayrı karar kapısı", "editorial_score", "score.json"),
    "K117": rec("geçti", "Sabit ve görünür paydalar", f"409 kart, 209 fotoğraf satırı/201 dosya, {claims_n} değişken iddia, {url_total} URL, "
                f"{inv['totals']['files']} dosya, 23 sayfa alanı; paydadan çıkarılan kayıt yok", "süreç", "criteria.json; DENETIM_OZETI.md"),
    "K119": rec("geçti", "Bağımsız kanıtla yeniden sınama", "Ham dosyalardan başlandı; üretim özeti/manifest yorumları kanıt sayılmadı; sonuçlar "
                "script çıktısına dayanıyor", "süreç", "—"),
    "K120": rec("kısmi", "Teslim kapısı", "Gönderim durumu script kararıyla açıkça yazıldı", "editorial_score", "score.json",
                sinir="K01–K120'nin L/V/E kısımları L0'da açık."),
}

L_NOTES = {
    "K18": "Ham sayım K10/K17'de; kullanılabilirlik (kopya/yanlış şehir/kaynak çelişkisi) L.",
    "K19": "Konu başına ham yanıt 22–26 (12/12 konu dolu): " + ", ".join(f"{k.split(':')[1]} {v}" for k, v in ana["answers_per_topic"].items()) + ".",
    "K20": f"Grup başına mekân: {groups_txt}; shopping grubu yok (ek grup, hata değil).",
    "K25": "text_quality kaçamak ilk cümle sinyali 1 (Yanıtlar!247); kart tutarları veriyor.",
    "K29": f"claim_check: {claims_n} sayısal iddianın {cs['summary']['by_result']['supported']} tanesi kaynak snapshot'ında dize olarak bulundu "
           f"(tutarlılık, doğruluk değil); {len(not_in_src)} 'not_in_source' ({', '.join(f'{k} {v}' for k, v in nis_by_kind.items())}) → L1 girdisi.",
    "K34": f"claim_extract envanteri: {claims_n} iddia / {cs['summary']['entries']} kart; resmî kaynakta doğrulanan 0 (L0).",
    "K39": "L1 ipucu: IJssportcentrum kaynağı yeniden açılış duyurusu ('Wij zijn weer open', 17 Ekim 2026).",
    "K42": f"L1 ipucu: aynı koordinatlı 3 çift ({shared_txt}).",
    "K51": "url_check sinyalleri: soft-404 0; anasayfaya yönlenen 2 (defabriekeindhoven.com/en/home → /en; ijssportcentrum.nl/contact/ → "
           "sportfondsen anasayfası, Bağlantılar!260/Kaynaklar!288); anasayfa-yalnız kaynak 3 + knmi.nl sağlayıcı; alan adı değişen 6 "
           "(consuwijzer → consument.acm.nl ×4, arnohuibers.nl → clownarno.nl, ijssportcentrum.nl → sportfondsen.nl).",
    "K53": "İşlem-hedef anlam eşleşmesi L.",
    "K71": "L1 ipucu: Fotoğraflar!60 (Pixabay kökenli Commons dosyası) ve profil URL'siz 21 fotoğraf.",
    "K72": "L1 ipucu: CC0 1.0 7 + Public domain 2 dosya.",
    "K90": "emergency_url (government.nl 112) ve pharmacy_url (huisartsenpostenoostbrabant.nl Centrale Dienstapotheek) 200; içerik doğruluğu L.",
    "K91": "forecast_url knmi.nl ulusal tahmin sayfası; şehre özgülüğü L.",
    "K108": f"L1 ipucu: aynı koordinatlı çiftler alt nesne/şişirme açısından ({shared_txt}).",
}
V_NOTES = {
    "K59": "Paftalar: temas-sayfalari/sheet_01–07.jpg (209 kare, 30'luk).",
    "K60": "L1 ipucu: Fotoğraflar!60 dosya adı 'Netherlands_Office_Philips_Eindhoven_Building.jpg' → De Ontdekfabriek (yalnız ad sinyali, karar değil).",
    "K62": "8 kapak (Fotoğraflar!209–216) mekân kareleriyle aynı dosya; kapak doğruluğu V.",
}

records = []
for c in checks:
    cid, ex = c["id"], c["exec"]
    if c.get("scope") in ("drive-manual", "preview-later"):
        stage = "Drive (drive-manual)" if c["scope"] == "drive-manual" else "önizleme (preview-later)"
        r = rec("separate_stage", c["title"], "0", "—", "—", sinir=f"Ayrı aşama: {stage}; yerel paket denetimi kapsamı dışında.")
    elif cid in S:
        r = S[cid]
    elif cid in M:
        r = M[cid]
    elif cid == "K36":
        r = rec("uygulanmaz", c["title"], "—", "—", "_dump/Şehir.jsonl (country_code NL)",
                sinir="D7/D8 kısmı yalnız Portekiz (PT) için; şehir NL. Hollanda vize/oturum kuralları K35 (L) altında, L0'da not_checked.")
    elif ex == "L":
        r = rec("not_checked", c.get("pass", c["title"]), "0 (LLM + kaynak incelemesi yapılmadı)", "—", "—",
                sinir="L0 kademesi: exec L kontrolleri çalıştırılmaz (SKILL). " + L_NOTES.get(cid, ""))
    elif ex == "V":
        r = rec("not_checked", c.get("pass", c["title"]), "0 (görsel inceleme yapılmadı)", "—", "temas-sayfalari/",
                sinir="L0 kademesi: exec V kontrolleri çalıştırılmaz; paftalar üretildi ama bakılmadı (SKILL). " + V_NOTES.get(cid, ""))
    else:
        raise SystemExit(f"eslenmemis kontrol: {cid} {ex}")
    records.append({"check_id": cid, **r, "checked_on": DATE})

assert len(records) == 120, len(records)
known = {i["issue_id"] for i in ISSUES}
for r in records:
    for b in r["bulgu_IDleri"]:
        assert b in known, (r["check_id"], b)
status_counts = Counter(r["durum"] for r in records)
meta = {"tool": "city-audit L0", "level": "L0", "label": "yerel paket denetimi", "city_id": "eindhoven", "catalog": "CITY-039",
        "xlsx": XLSX_NAME, "xlsx_sha256": next(f["sha256"] for f in inv["files"] if f["path"] == XLSX_NAME), "checked_on": DATE,
        "template": "kılavuz 2.0 bölüm 16 CHECK", "status_counts": dict(status_counts)}
(OUT / "check-results.json").write_text(json.dumps({"meta": meta, "checks": records}, ensure_ascii=False, indent=1), encoding="utf-8")
(OUT / "issues.json").write_text(json.dumps({"meta": {**meta, "template": "kılavuz 2.0 bölüm 16 ISSUE"}, "issues": ISSUES},
                                            ensure_ascii=False, indent=1), encoding="utf-8")

# ---------------------------------------------------------------- criteria
def crit(code, status, reason, passed=None, required=None):
    item = {"code": code, "status": status, "reason": reason}
    if passed is not None:
        item["passed"] = passed
    if required is not None:
        item["required"] = required
    return item


e2_total = inv["totals"]["files"]
web_files_bs = len({str(r["web_file"]) for r in prov if "\\" in str(r["web_file"])})  # farkli WebP dosyasi
e2_pass = e2_total - web_files_bs
criteria = [
    crit("A1", "not_checked", "Kullanılabilir/özgün kart sayımı K18 (L) yapılmadı; ham 289 ≥ 240 (sayısal açık yok)."),
    crit("A2", "not_checked", "Kartın soruyu çözmesi K25/K26 (L) yapılmadı."),
    crit("A3", "not_checked", f"İddia-kaynak desteği K29 (L) yapılmadı; claim_check dize eşleşmesi ({cs['summary']['by_result']['supported']}/{claims_n}) destek kanıtı sayılmaz."),
    crit("A4", "not_checked", f"Kritik/güncel doğruluk K34/K35 (L) yapılmadı; 0/{claims_n} resmî kaynakta doğrulandı."),
    crit("A5", "not_checked", "Dil/konu değeri K28/K32 (L) yapılmadı; script: tam kart kopyası yok, hedge 2/409 (ISS-007)."),
    crit("B1", "partial", f"Ham {counts['places']} (üst sınır) < 120 → ISS-001; kimlik/şube doğrulaması K42 (L) yapılmadı; doğrulanan alt sınır 0.", 0, 120),
    crit("B2", "not_checked", "Ham 16/16; yerel somut karşılaştırma K44 (L) yapılmadı."),
    crit("B3", "partial", "Durak bağları 12/12 script ile geçti (K46); fiziksel uygulanabilirlik K47 (L) yapılmadı; doğrulanan alt sınır 0.", 0, 12),
    crit("B4", "not_checked", "Ham 60/60; anlam/kaynak K48 (L) yapılmadı."),
    crit("B5", "not_checked", "Koordinat aralığı geçti, 3 ortak koordinat çifti; ad/adres/harita/ziyaret durumu doğrulaması L/V yapılmadı."),
    crit("C1", "partial", f"Tekil {counts['photos']} kare (üst sınır) < 250 → ISS-002; görsel/hak doğrulaması V/L yapılmadı; doğrulanan alt sınır 0.", 0, 250),
    crit("C2", "not_checked", "Görsel-kaynak-caption eşleşmesi K59–K62 (V) yapılmadı."),
    crit("C3", "partial", f"Herhangi bir fotoğrafı olan yer {ana['places_with_photo'] + ana['districts_with_photo']}/120 (üst sınır); "
                          f"{len(no_photo_places) + len(no_photo_districts)} yer fotoğrafsız → ISS-003; doğru kare teyidi V; doğrulanan alt sınır 0.", 0, 120),
    crit("C4", "partial", "Aynı-kare tekrarı yalnız kapak rolünde (dHash 8 çift, rol ayrı); kırpma/netlik K65 (V) yapılmadı; doğrulanan alt sınır 0.", 0, 201),
    crit("C5", "not_checked", "8 farklı kapak var (kapaklar arası tekrar yok); kapak doğruluğu K62 (V) ve uyarı bandı K103 (önizleme) yapılmadı."),
    crit("D1", "not_checked", "Eser bazlı ücretsiz ticari izin teyidi: K67 script'i aday üretmedi, K71/K72 (L) yapılmadı; etiketler 209/209 izinli aileden."),
    crit("D2", "partial", "Etiket↔URL tutarlılığı ve yazar alanı 201/201 (K69/K70); kaynakla eşleşme okunmadı; doğrulanan alt sınır 0.", 0, 201),
    crit("D3", "partial", "Dosya/hash zinciri 201/201 tutarlı (K77/K80/K114); kanıt gerçekliği K76 kısmi (foto kanıtları açılmadı); web_file yolu ISS-004; doğrulanan alt sınır 0.", 0, 201),
    crit("D4", "not_checked", "Kareye özgü ek haklar K74 (V) yapılmadı; rights_status 209/209 'Bekliyor'."),
    crit("D5", "not_checked", "Atıf CSV 209/209 Excel ile tutarlı (K75 kısmi); hedef görünümde kontrol K94 ayrı aşama."),
    crit("E1", "ok", "Sabit liste (başlangıçta): bölüm 02 K08–K16 + K45, K46, K49 = 12 atomik kontrol; kaldı: K14 (ISS-006), K15 (ISS-004).", 10, 12),
    crit("E2", "ok", f"{e2_total} beklenen dosyanın tamamı çözülüyor ve SHA eşleşiyor; {web_files_bs} WebP'nin Excel/manifest yolu '\\' (ISS-004).", e2_pass, e2_total),
    crit("E3", "ok", "23/23 zorunlu anahtar; resmî doğrulayıcı tür/değer/referans hatası 0.", 23, 23),
    crit("E4", "separate_stage", "Web işlevleri önizleme senaryoları ayrı aşama (preview-later)."),
    crit("E5", "partial", "Kök Excel ✓, üç klasör ✓, kimlik eşleşmesi ✓; bulut dosyaları (Drive) ayrı aşama — kontrol edilmedi; "
                          "sürüm/sayı tutarlılığı ✗ (ISS-005, ISS-006).", 3, 5),
]
findings = [{"id": i["issue_id"], "priority": i["öncelik"], "criteria": FINDING_CRITERIA.get(i["issue_id"], [])} for i in ISSUES]
crit_doc = {"meta": {**meta, "note": "L0: L ve V ölçütleri not_checked; partial ölçütlerde 'passed' doğrulanan alt sınırdır."},
            "criteria": criteria, "findings": findings,
            "coverage": {"cards": [0, 409], "photos": [0, 209], "critical_claims": [0, claims_n]}}
(OUT / "criteria.json").write_text(json.dumps(crit_doc, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps({"checks": len(records), "status_counts": dict(status_counts), "issues": len(ISSUES),
                  "criteria": len(criteria), "e2": [e2_pass, e2_total]}, ensure_ascii=False))
