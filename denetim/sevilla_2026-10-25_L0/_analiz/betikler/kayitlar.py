"""kayitlar.py: Sevilla L0 denetim kayitlari (CHECK, ISSUE, criteria) - kilavuz 2.0 bolum 16/20.

Kullanim: python -I -X utf8 kayitlar.py <OUT>
Sayilar script ciktilarindan okunur (validation-audit, dosya-envanteri, _foto, url-checks, claim-script, _analiz);
degerlendirme metinleri bu dosyada. Yalniz OUT altina yazar.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
OUT = Path(sys.argv[1])
TODAY = "2026-10-25"


def load(rel: str):
    return json.loads((OUT / rel).read_text(encoding="utf-8-sig"))


def jl(rel: str) -> list[dict]:
    return [json.loads(l) for l in (OUT / rel).read_text(encoding="utf-8").splitlines() if l.strip()]


val = load("validation-audit.json")
inv = load("dosya-envanteri.json")
inv_son = load("_dosya-envanteri-son.json")
k04 = load("_analiz/k04-karsilastirma.json")
capraz = load("_analiz/capraz-kontroller.json")
snapcmp = load("_analiz/snapshot-karsilastirma.json")
urls = load("url-checks.json")
urls1 = load("_analiz/url-checks-kosu1.json")
claims = load("claim-script.json")["summary"]
tq = load("text-quality.json")
foto_h = load("_foto/hazirlik.json")
dec = load("_foto/decisions.json")
dhash = load("_foto/dhash-ciftleri.json")
fid = load("xlsx-fidelity.json")
dump_summary = load("_dump/summary.json") if (OUT / "_dump" / "summary.json").exists() else {}
mek = jl("_dump/Mekânlar.jsonl")
mah = jl("_dump/Mahalleler.jsonl")
yan = jl("_dump/Yanıtlar.jsonl")
fot = jl("_dump/Fotoğraflar.jsonl")
kay = jl("_dump/Kaynaklar.jsonl")

counts = val["structure"]["counts"]
minimum = val["structure"]["minimum"]
target = val["structure"]["target"]
xlsx_sha = next(f["sha256"] for f in inv["files"] if f["path"].endswith(".xlsx"))
xlsx_name = next(f["path"] for f in inv["files"] if f["path"].endswith(".xlsx"))
n_files = inv["summary"]["files"]
n_rows = sum(capraz["sheet_rows"].values())
n_sheets = len(capraz["sheet_rows"])
n_cards = len(yan) + len(mek) + len(mah)
n_photo_rows = len(fot)
n_unique_photos = counts["photos"]
n_claims = claims["claims"]
n_urls = urls["summary"]["unique_urls"]
n_rel = urls["summary"]["relations"]
ews = dec["summary"]["entries_without_shortlist"]
mek_by_id = {m["entry_id"]: m for m in mek}
mah_by_id = {m["entry_id"]: m for m in mah}
fotosuz_mek = [mek_by_id[e] for e in ews if e in mek_by_id]
fotosuz_mah = [mah_by_id[e] for e in ews if e in mah_by_id]
coll_evet = [m for m in mek if m.get("collection") == "Evet"]
foto_entries = {p.get("entry_id") for p in fot}
coll_fotosuz = [m for m in coll_evet if m["entry_id"] not in foto_entries]
nocoord = [m for m in mek if m.get("latitude") in (None, "")]
k05_groups = foto_h["ayni_sha"]["K05"]
url1_net = [u for u in urls1["urls"] if u.get("class") == "network_error"]
homepage_only = [u for u in urls["urls"] if "homepage_only" in (u.get("flags") or [])]
cross_host = [u for u in urls["urls"] if "cross_host_redirect" in (u.get("flags") or [])]
lic = capraz["licenses"]
lic_txt = ", ".join(f"{k} {v}" for k, v in sorted(lic.items(), key=lambda kv: -kv[1]))
groups = capraz["photos"]["group_counts"]
grp_txt = ", ".join(f"{k} {v}" for k, v in groups.items())
by_result = claims["by_result"]

meta = {
    "tool": "city-audit L0", "level": "L0", "label": "yerel paket denetimi", "city_id": "sevilla",
    "catalog": "CITY-107", "xlsx": xlsx_name, "xlsx_sha256": xlsx_sha, "previous_audit": None,
    "checked_on": TODAY,
}

# ------------------------------------------------------------------ ISSUE kayitlari
def rows(items):
    return ", ".join(str(i["_row"]) for i in items)


issues = [
    {
        "issue_id": "ISS-001", "öncelik": "P1", "kategori": "Berlin kapsamı / yanıt hedefi", "check_id": "K17",
        "tablo": "Yanıtlar", "Excel_satırı": f"8–{7 + len(yan)} ({len(yan)} kayıt)", "entry_id/photo_id": "—",
        "dosya": xlsx_name, "alan": "kayıt sayısı (answers)", "mevcut_değer": str(counts["answers"]),
        "beklenen": f"hedef {target['answers']} (asgari {minimum['answers']} karşılandı)",
        "somut_gözlem": f"Resmî doğrulayıcı sayımı answers={counts['answers']}, minimum={minimum['answers']}, target={target['answers']}; hedefe 1 yanıt eksik. Konu dağılımı: ulaşım 22, para 21, resmî 21, günlük 20, iş 20, keşif 20, planlama 20, sağlık 20, ev 19, fatura 19, oturum 19, aile 18 (12/12 konu dolu).",
        "kanıt": "validation-audit.json → structure.counts.answers / target.answers; _render/TESLIM_OZETI.txt",
        "kullanıcı_etkisi": "Bilgi kartı bölümü Berlin üretim hedefinin 1 kayıt altında; kalite oranı eksik hedefi örtmez (kılavuz bölüm 20).",
        "önerilen_düzeltme": "En az 1 gerçek ihtiyaca cevap veren, resmî kaynaklı yanıt ekle (en az dolu konu: aile 18). Paketin kendi beyanına göre belediye sitesine (sevilla.org) erişim sorunu nedeniyle cevapsız kalan sorular var (ACIK_KONULAR OI-008); bunlardan biri kapatılabilir.",
        "tekrar_kontrol_koşulu": f"validate_all structure.counts.answers ≥ {target['answers']}; yeni kart L1'de K25/K29 ile doğrulanmış.",
        "durum": "Açık",
    },
    {
        "issue_id": "ISS-002", "öncelik": "P1", "kategori": "Berlin kapsamı / mekân hedefi", "check_id": "K17",
        "tablo": "Mekânlar", "Excel_satırı": f"8–{7 + len(mek)} ({len(mek)} kayıt)", "entry_id/photo_id": "—",
        "dosya": xlsx_name, "alan": "kayıt sayısı (places)", "mevcut_değer": str(counts["places"]),
        "beklenen": f"hedef {target['places']} (asgari {minimum['places']} karşılandı)",
        "somut_gözlem": f"Resmî doğrulayıcı sayımı places={counts['places']}, minimum={minimum['places']}, target={target['places']}; hedefe 20 mekân eksik. Grup dağılımı: {grp_txt}. 13 kayıt collection=Evet (ISS-007). Tarih ve mimari payı 32/100 (eşik %35'in altında).",
        "kanıt": "validation-audit.json → structure.counts.places / target.places; _render/TESLIM_OZETI.txt; _analiz/capraz-kontroller.json → photos.group_counts",
        "kullanıcı_etkisi": "Keşif bölümü Berlin üretim hedefinin %17 altında; Spor (5), Çocuklarla keşif (7) ve Yeme ve içme (8) grupları zayıf.",
        "önerilen_düzeltme": "En az 20 gerçek, açık, kaynaklı ve fotoğraflı mekân ekle; öncelik Spor, Çocuklarla keşif, Yeme ve içme. Alt nesne/collection ile şişirme yapma (K108).",
        "tekrar_kontrol_koşulu": f"validate_all structure.counts.places ≥ {target['places']} ve yeni kayıtlar L1'de K39/K42/K108 ile doğrulanmış.",
        "durum": "Açık",
    },
    {
        "issue_id": "ISS-003", "öncelik": "P1", "kategori": "Berlin kapsamı / mahalle hedefi", "check_id": "K17",
        "tablo": "Mahalleler", "Excel_satırı": f"8–{7 + len(mah)} ({len(mah)} kayıt)", "entry_id/photo_id": "—",
        "dosya": xlsx_name, "alan": "kayıt sayısı (neighborhoods)", "mevcut_değer": str(counts["neighborhoods"]),
        "beklenen": f"hedef {target['neighborhoods']} (asgari {minimum['neighborhoods']} karşılandı)",
        "somut_gözlem": f"Resmî doğrulayıcı sayımı neighborhoods={counts['neighborhoods']}, target={target['neighborhoods']}; hedefe 1 mahalle eksik. Paketin kendi beyanı (OI-010): 16. semt için iki resmî kaynak bulunamadı (belediye sitesi erişilemez) — beyan, kanıt değil.",
        "kanıt": "validation-audit.json → structure.counts.neighborhoods; _render/TESLIM_OZETI.txt",
        "kullanıcı_etkisi": "Mahalle rehberi hedefin 1 kayıt altında.",
        "önerilen_düzeltme": "1 mahalle daha ekle (iki resmî/yerel kaynakla, compare_json aynı başlıklarla); fotoğraflı olsun (ISS-004).",
        "tekrar_kontrol_koşulu": f"validate_all structure.counts.neighborhoods ≥ {target['neighborhoods']}; yeni kayıt L1'de K44 ile doğrulanmış.",
        "durum": "Açık",
    },
    {
        "issue_id": "ISS-004", "öncelik": "P1", "kategori": "Fotoğraf kapsamı", "check_id": "K22",
        "tablo": "Mekânlar; Mahalleler",
        "Excel_satırı": f"Mekânlar!{rows(fotosuz_mek)}; Mahalleler!{rows(fotosuz_mah)}",
        "entry_id/photo_id": ", ".join(ews), "dosya": xlsx_name, "alan": "Fotoğraflar.entry_id ilişkisi",
        "mevcut_değer": f"fotoğraflı mekân {capraz['photos']['places_with_photo']}/{len(mek)}; fotoğraflı mahalle {capraz['photos']['districts_with_photo']}/{len(mah)}",
        "beklenen": "Her fiziksel mekân ve mahalle en az bir doğru, gerçek fotoğrafla kapsanır.",
        "somut_gözlem": f"{len(fotosuz_mek)} mekân + {len(fotosuz_mah)} mahalle hiç fotoğraf ilişkisine sahip değil (photo_prefilter entries_without_shortlist {len(ews)}). Resmî doğrulayıcı uyarısı 15 + 5 = 20: fotoğrafsız 19 mekânın 4'ü collection=Evet olduğu için uyarıdan muaf (museo-arqueologico-de-sevilla, casa-fabiola-coleccion-bellver, centro-ceramica-triana, museo-historia-de-la-farmacia-us; bkz. ISS-007). Grup bazında fotoğrafsız mekân: Müzeler 5, Çocuklarla keşif 4, Yeme ve içme 3, Sahne ve müzik 3, Spor 2, Doğa ve açık hava 1, Sanat ve sergiler 1. Paket bunu beyan ediyor (ACIK_KONULAR OI-014: Commons'ta aday yok, Openverse bekletme); beyan kanıt değil.",
        "kanıt": "validation-audit.json → warning_classes ('gerçek fotoğraf eksik' 15 + 5); _foto/decisions.json → summary.entries_without_shortlist (24); _analiz/capraz-kontroller.json → photos",
        "kullanıcı_etkisi": "Mekân kartlarının %19'u ve mahalle kartlarının üçte biri görselsiz açılır; okur yeri tanıyamaz.",
        "önerilen_düzeltme": "Her kayda en az bir gerçek, tekil, ücretsiz-ticari lisanslı kare ekle (Openverse/Flickr CC, kurumun kendi CC fotoğrafı); uygun kare yoksa kaydın kapsamda kalmasına editoryal karar ver. collection etiketiyle muafiyet kullanma.",
        "tekrar_kontrol_koşulu": "photo_prefilter entries_without_shortlist = 0 ve validate_all 'gerçek fotoğraf eksik' = 0; yeni kareler L1 görsel (K59–K61) ve hak (K67–K74) incelemesinden geçmiş.",
        "durum": "Açık",
    },
    {
        "issue_id": "ISS-005", "öncelik": "P2", "kategori": "Klasör düzeni / tekrar dosya", "check_id": "K05",
        "tablo": "Kanıtlar", "Excel_satırı": "—", "entry_id/photo_id": "kapak-01…08 ve eşleştikleri 8 mekân karesi",
        "dosya": "Lisans kanıtları/*.source-evidence.json; *.license-evidence.json (16 dosya, 8 çift ×2)",
        "alan": "kanıt dosyası baytları", "mevcut_değer": f"{len(k05_groups)} aynı-SHA grubu (16 dosya)",
        "beklenen": "Paket içinde bayt bayt aynı dosya tekrar etmez ya da tekrar gerekçeli (aynı kaynak kaydının iki rol için kopyası).",
        "somut_gözlem": "Her kapak karesi bir mekân karesiyle aynı Commons dosyasıdır (8 kapak↔mekân çifti, zararsız). Bu 8 çiftin kaynak ve lisans kanıtı JSON'ları da ikişer kez yazılmış (kapak-NN.*-evidence.json = <mekân>-NN.*-evidence.json): 16 dosya byte bayt tekrar. Envanter dup_sha 24 = 8 foto çifti + 16 kanıt dosyası. Artık (.download-cache, ikinci Excel) yok.",
        "kanıt": "dosya-envanteri.json → findings.dup_sha (24); _foto/hazirlik.json → ayni_sha.K05 (16), kapak_mekan (8)",
        "kullanıcı_etkisi": "İşlevi bozmaz; paket boyutuna küçük ek yük ve iki kopyanın ileride ayrışma riski.",
        "önerilen_düzeltme": "Kapak satırının kanıt alanlarını mekân karesinin kanıt dosyasına bağla ya da tekrarın tasarım gereği olduğunu Teslimler'de belirt.",
        "tekrar_kontrol_koşulu": "audit_prep ayni_sha.K05 = 0 ya da tekrar gerekçesi Teslimler'de yazılı.",
        "durum": "Açık",
    },
    {
        "issue_id": "ISS-006", "öncelik": "P2", "kategori": "Konum / koordinat eksikliği", "check_id": "K43",
        "tablo": "Mekânlar", "Excel_satırı": f"Mekânlar!{rows(nocoord)}",
        "entry_id/photo_id": ", ".join(m["entry_id"] for m in nocoord), "dosya": xlsx_name,
        "alan": "latitude / longitude", "mevcut_değer": f"{len(nocoord)}/{len(mek)} mekânda koordinat boş",
        "beklenen": "Mekân haritada gösterilebilir: koordinat (sözleşmede isteğe bağlı) ya da harita bağlantısı.",
        "somut_gözlem": f"{len(nocoord)} mekânda latitude/longitude boş; bu mekânların Bağlantılar'ında harita bağlantısı da yok (paketin tamamında harita bağlantılı mekân 0/100; haritalama yalnız koordinatla yapılıyor). Hepsinde adres metni (location) dolu. Koordinatı olan 72 mekân aralıkta (enlem 37.361–37.426, boylam −6.011…−5.964). Aynı koordinatlı 1 çift (estadio-la-cartuja / estadio-benito-villamarin-tur) kart notuyla tutarlı: Betis turu yenileme süresince La Cartuja'da yapılıyor (L1'de K39/K42 teyidi).",
        "kanıt": "_analiz/capraz-kontroller.json → coordinates (with_coords 72); _dump/Mekânlar.jsonl; validation-audit.json → extras.shared_coordinates",
        "kullanıcı_etkisi": "28 mekân haritada görünmez; okur yalnız adres metniyle yer bulur. Sözleşme bunu hata saymıyor; Berlin örneğinde ve önceki şehirde (Eindhoven 119/119) koordinat tamdı.",
        "önerilen_düzeltme": "28 mekâna resmî/doğrulanabilir koordinat ekle (kurumun kendi sitesi, Wikidata ya da adresten doğrulama) veya Bağlantılar'a 'Haritada aç' bağlantısı.",
        "tekrar_kontrol_koşulu": "Mekânlar'da koordinatı boş kayıt 0 (ya da her birinde harita bağlantısı); L1'de K43/K55 ile nokta doğrulaması.",
        "durum": "Açık",
    },
    {
        "issue_id": "ISS-007", "öncelik": "P2", "kategori": "Veri modeli / collection etiketi", "check_id": "K22",
        "tablo": "Mekânlar", "Excel_satırı": f"Mekânlar!{rows(coll_evet)}",
        "entry_id/photo_id": ", ".join(m["entry_id"] for m in coll_evet), "dosya": xlsx_name,
        "alan": "collection", "mevcut_değer": f"collection=Evet {len(coll_evet)} kayıt (Müzeler grubunda 10/12)",
        "beklenen": "collection=Evet yalnız bir tesisin alt nesnesi/koleksiyonu için; bağımsız adres ve ziyaret deneyimi olan mekân collection değildir; etiket fotoğraf zorunluluğundan kaçmak için kullanılmaz (K108).",
        "somut_gözlem": f"13 kayıt collection=Evet: Museo de Bellas Artes, Museo Arqueológico, Museo de Artes y Costumbres Populares, Museo del Baile Flamenco, Casa Fabiola, Centro Cerámica Triana, Museo Taurino, Museo Histórico Militar, Museo Marítimo Torre del Oro, Museo Historia de la Farmacia, Convento de Santa Paula, Estadio Sánchez-Pizjuán turu, Casa de la Ciencia. Bunlar bağımsız adresli, kendi giriş ve saatleri olan müze/tesisler. Etkisi: resmî doğrulayıcı collection=Evet kayıtları fotoğraf uyarısından muaf tutuyor; 4 fotoğrafsız müze bu yüzden uyarı sayısına girmedi (validator 20, gerçek 24). Etiketin anlamsal doğruluğu K108 (L) kapsamında; L0 yalnız veri desenini raporlar.",
        "kanıt": "_dump/Mekânlar.jsonl → collection; validation-audit.json → warning_classes (15 mekân) ↔ _foto/decisions.json entries_without_shortlist (19 mekân)",
        "kullanıcı_etkisi": "Müze grubunun neredeyse tamamı 'koleksiyon' sayılıyor; önizlemede/filtrelerde collection ayrımı varsa müzeler yanlış sınıfta görünür, fotoğraf zorunluluğu da zayıflar.",
        "önerilen_düzeltme": "Bağımsız müze/tesislerde collection=Hayır yap; etiketi yalnız gerçek alt nesneler (ör. bir sarayın tek salonu) için bırak. Fotoğraf eksiğini ISS-004 ile kapat.",
        "tekrar_kontrol_koşulu": "collection=Evet yalnız gerekçeli alt nesnelerde; L1'de K108 'geçti'.",
        "durum": "Açık (L1 teyidi gerekir)",
    },
    {
        "issue_id": "ISS-008", "öncelik": "P2", "kategori": "İnceleme tarihi / bağlantı tarihi sırası", "check_id": "K14",
        "tablo": "Yanıtlar", "Excel_satırı": "82", "entry_id/photo_id": "sevilla:feria-de-abril-ulasim-park-ve-erisilebilirlik",
        "dosya": xlsx_name, "alan": "reviewed_on", "mevcut_değer": "reviewed_on 2026-10-24",
        "beklenen": "reviewed_on, kaydın bağlı bağlantılarının checked_on tarihinden önce olamaz.",
        "somut_gözlem": "Kartın Bağlantılar satırı 2026-10-25'te kontrol edilmiş, kart reviewed_on 2026-10-24. Kaynak checked_on ile çakışma 0 kayıt; bu tek kayıt bağlantı tarihiyle çakışıyor. Diğer tarih kontrolleri temiz: gelecek tarih 0, Teslimat.updated_on 2026-10-25 = en son içerik tarihi, notes şablon metni değil.",
        "kanıt": "_dump/Yanıtlar.jsonl (!82); _dump/Bağlantılar.jsonl (entry_id eşleşen satır, checked_on 2026-10-25); _analiz/capraz-kontroller.json → dates",
        "kullanıcı_etkisi": "Kartta gösterilen son kontrol tarihi gerçek kontrolden bir gün eski; önemsiz ama tarih takibini bozar.",
        "önerilen_düzeltme": "reviewed_on değerini 2026-10-25 yap; birleştirmede reviewed_on ≥ max(bağlı kaynak/bağlantı checked_on) kuralını script kapısı yap.",
        "tekrar_kontrol_koşulu": "Her kayıtta reviewed_on ≥ bağlı kaynak ve bağlantıların en geç checked_on değeri.",
        "durum": "Açık",
    },
]
open_ids = {"P0": [], "P1": [], "P2": []}
for i in issues:
    open_ids[i["öncelik"]].append(i["issue_id"])

# ------------------------------------------------------------------ CHECK kayitlari
checks: list[dict] = []


def C(cid, durum, beklenen, incelenen, yontem="—", kanit="—", bulgular=None, sinir=""):
    checks.append({
        "check_id": cid, "durum": durum, "beklenen_kapsam": beklenen, "incelenen_kapsam": incelenen,
        "yöntem": yontem, "kanıt_yolu_veya_URL": kanit, "bulgu_IDleri": bulgular or [], "sınır_gerekçe": sinir,
        "checked_on": TODAY,
    })


def L(cid, beklenen, ipucu=""):
    C(cid, "not_checked", beklenen, "0 (LLM + kaynak incelemesi yapılmadı)",
      sinir="L0 kademesi: exec L kontrolleri çalıştırılmaz (SKILL)." + (f" L1 ipucu: {ipucu}" if ipucu else ""))


def V(cid, beklenen, ipucu=""):
    C(cid, "not_checked", beklenen, "0 (görsel inceleme yapılmadı)",
      sinir="L0 kademesi: exec V kontrolleri çalıştırılmaz; paftalar üretildi ama bakılmadı (SKILL)." + (f" {ipucu}" if ipucu else ""))


def DRIVE(cid, beklenen):
    C(cid, "separate_stage", beklenen, "0", sinir="Ayrı aşama: Drive (drive-manual); yerel paket denetimi kapsamı dışında.")


def PREVIEW(cid, beklenen):
    C(cid, "separate_stage", beklenen, "0", sinir="Ayrı aşama: önizleme (preview-later); yerel paket denetimi kapsamı dışında.")


DRIVE("K01", "Doğru şehir ve güncel paket")
C("K02", "geçti", "Paketteki tüm dosyalar gerçek baytlarıyla",
  f"{n_files}/{n_files} dosya okundu, SHA-256 hesaplandı; {inv['summary']['images']} görsel (258 JPEG + 250 WebP) çözüldü; okuma hatası 0",
  "inventory.py (başlangıç ve bitiş)", "dosya-envanteri.json; _dosya-envanteri-son.json", sinir="Drive kopyasıyla karşılaştırma K03 (ayrı aşama).")
DRIVE("K03", "Drive ile yerel kopyanın aynı olması")
C("K04", "geçti", "Denetim başı ve sonu paket SHA listeleri",
  f"Başta {k04['start_files']}, sonda {k04['end_files']} dosya; eklenen {len(k04['added'])}, silinen {len(k04['removed'])}, değişen {len(k04['changed'])}; SHA listesi özeti {k04['sha_list_digest_start'][:16]}… iki uçta aynı; Excel SHA {xlsx_sha[:16]}… değişmedi. Son envanter tüm paket okumalarından (validate_all, capraz, snapcmp, ILERLEME_KAYDI okuması) sonra alındı.",
  "inventory.py ×2 + k04.py (SHA listesi karşılaştırması)", "dosya-envanteri.json; _dosya-envanteri-son.json; _analiz/k04-karsilastirma.json",
  sinir="KAPSAM: kısmi; baş/son karşılaştırması bu denetimde tamamlandı.")
C("K05", "kaldı", "Kök XLSX + Fotoğraflar, Lisans kanıtları, Teslimler; artık/orphan/çoklu Excel yok",
  f"Kök: 1 XLSX; Fotoğraflar 258, Lisans kanıtları 931, Teslimler 260 (10 dosya + WebKopyalari 250); orphan 0; .download-cache yok; ikinci Excel yok. Aynı SHA grupları 24: 8 kapak↔mekân (zararsız) + 16 kanıt JSON tekrarı (K05 sınıfı, ISS-005)",
  "inventory.py findings + audit_prep ayni_sha", "dosya-envanteri.json; _foto/hazirlik.json; _analiz/capraz-kontroller.json → inventory, teslimler.files",
  ["ISS-005"], "KAPSAM: kısmi; çoklu Excel ve artık denetimi envanter listesinden yapıldı.")
C("K06", "geçti", "Yetenek ve erişim sınırları kaydı",
  "XLSX okuma, bayt/SHA, HTTP erişimi ve kod çalıştırma fiilen kullanıldı; görsel inceleme ve LLM iddia denetimi L0 dışı (yapılmadı, GEÇTİ sayılmadı)",
  "Araç kullanımının kaydı", "DENETIM_OZETI.md bölüm 10")
C("K07", "kısmi", "Referansın doğru kullanımı",
  f"Alt sınır/hedefler resmî doğrulayıcının acceptance_version {val['structure'].get('acceptance_version')} değerlerinden",
  "validate_all structure.minimum/target", "validation-audit.json", sinir="Berlin örnek Excel'i bu L0 denetiminde açılmadı.")
C("K08", "geçti", "Sekmeler, başlıklar ve teslim profili",
  f"{n_sheets}/16 sekme (missing_sheets 0); yapı girdi şablonuyla aynı (xlsx_fidelity '{fid.get('fidelity')}'); resmî doğrulayıcı yapı hatası 0",
  "xlsx_dump + xlsx_fidelity + validate_all", "_dump/summary.json; xlsx-fidelity.json; validation-audit.json")
C("K09", "geçti", "Formül, biçim ve doğrulama alanları",
  f"xlsx_fidelity '{fid.get('fidelity')}' (kabul edilen openpyxl parça farkları: sharedStrings kaldırıldı, docProps eklendi); formül sütunları Konular.used_count, Fotoğraflar.unique_hero_count, unique_venue_count",
  "xlsx_fidelity (şablon: uretim/sevilla/_is/sablon_orijinal_kopya.xlsx, salt okunur) + xlsx_dump", "xlsx-fidelity.json; _dump/summary.json")
C("K10", "geçti", "Ham kayıtların doğru sayımı",
  f"{n_sheets} sekme, {n_rows} satır; tekrar kimlik 0, boş anahtar 0; yer tutucu: text_quality 0, validate_all ek kontrol 0; dolgu 0",
  "xlsx_dump + text_quality + validate_all extras", "_dump/summary.json; text-quality.json; validation-audit.json → extras.placeholders",
  sinir="Editoryal kullanılabilir sayı K18 (L) kapsamında.")
C("K11", "geçti", "Kimlik ve adres adı eşleşmesi", f"Resmî doğrulayıcı kimlik/slug hatası 0 ({n_rows} satır)", "validate_all --mode audit --new-content", "validation-audit.json")
C("K12", "geçti", "Yabancı anahtar ilişkileri",
  "Resmî doğrulayıcı bağ hatası 0; ek: 12 rota 3–6 durak, stops↔stop_entry_ids uzunluk eşleşmesi ve ilk durak = entry_id 12/12, tanımsız durak 0; fotoğraf entry_id'leri tanımlı; pixel_review_file = file 258/258; source_ids'te tanımsız kaynak 0; hiçbir karta bağlı olmayan kaynak 6 (kaynak:142, 143, 188, 439, 440, 445; bilgi)",
  "validate_all + capraz.py", "validation-audit.json; _analiz/capraz-kontroller.json → routes, photos, sources")
C("K13", "geçti", "Veri türleri ve izinli değerler",
  "Resmî doğrulayıcı tür/enum hatası 0. Bilgi: photo-provenance-v7.json ve atıf CSV'sinde downloaded_on '2026-10-25 00:00:00' biçiminde, Excel'de tarih",
  "validate_all", "validation-audit.json; _analiz/capraz-kontroller.json → teslimler")
C("K14", "kaldı", "Tarihler ve sıralar",
  "İçerik tarihleri: reviewed_on 2026-10-24/25, Kaynaklar.checked_on 2026-10-24 ×394 / 2026-10-25 ×22, Bağlantılar.checked_on 2026-10-24 ×371 / 2026-10-25 ×156; gelecek tarih 0; Teslimat.updated_on 2026-10-25 = en son içerik tarihi; notes şablon değil. reviewed_on < bağlı kaynak checked_on: 0 kayıt; reviewed_on < bağlı bağlantı checked_on: 1 kayıt (Yanıtlar!82, ISS-008). Şehir.source_checked_on ve coordinate_checked_on 2026-10-10 (şablon değerleri; reviewed_on 2026-10-25)",
  "capraz.py tarih taraması + ek kaynak/bağlantı sırası taraması + validate_all", "_analiz/capraz-kontroller.json → dates, latest_content_date; _dump/Teslimat.jsonl",
  ["ISS-008"])
C("K15", "geçti", "Dosya yolları ve arşiv güvenliği",
  "Fotoğraflar.file 258, FotoğrafKaynakları.original_file/web_file 258+258, Kanıtlar.*_file 3×258, Kaynaklar.snapshot_file 416 yolun tamamı '/' ile; Teslimler JSON/CSV/HTML yollarında '\\' 0; mutlak yol, '..', paket dışına taşan bağlantı 0; envanter missing 0. Bilgi: Teslimat.notes serbest metninde 'Teslimler\\ACIK_KONULAR.txt' yazımı (yol sütunu değil)",
  "audit_prep ters_egik_cizgi + capraz.py yol taraması + inventory", "_foto/hazirlik.json; _analiz/capraz-kontroller.json; dosya-envanteri.json",
  sinir="Unicode normalizasyon çakışması ayrıca aranmadı (envanter yolları tekil).")
C("K16", "geçti", "EkDetaylar ve uzun alanlar",
  f"EkDetaylar 0 satır; UzunAlanlar yok; en uzun hücre {capraz['longest_cell']['chars']} karakter (Kanıtlar!185.source_evidence_json); long_values_restored 0",
  "xlsx_dump + paket-kontrol-v7.json okuması", "_dump/summary.json; _analiz/capraz-kontroller.json",
  sinir="KAPSAM: kısmi; EkDetaylar boş olduğundan gölge alan denetimi konusuz.")
C("K17", "kaldı", "Berlin alt sınırı ile güncel üretim hedefi",
  f"answers {counts['answers']} ({minimum['answers']}/{target['answers']} ✗ −1); places {counts['places']} ({minimum['places']}/{target['places']} ✗ −20); neighborhoods {counts['neighborhoods']} ({minimum['neighborhoods']}/{target['neighborhoods']} ✗ −1); topics 12 (12/12 ✓); photos {counts['photos']} ({minimum['photos']}/{target['photos']} ✓); hero_photos 8 (6/8 ✓); routes 12 (9/12 ✓); glossary 60 (48/60 ✓)",
  "validate_all + render_summary (bağımsız yeniden hesap)", "validation-audit.json → structure.counts/minimum/target; _render/TESLIM_OZETI.txt",
  ["ISS-001", "ISS-002", "ISS-003"], "Editoryal kullanılabilir sayı L (K18); burada ham/tekil sayılar.")
L("K18", "Kullanılabilir kayıt sayısı")
L("K19", "On iki konunun dolu olması", "konu başına ham yanıt 18–22, 12/12 konu dolu.")
L("K20", "Keşif gruplarında gerçek içerik", f"grup başına mekân: {grp_txt}; collection=Evet 13 (ISS-007).")
C("K21", "geçti", "Yanıt/mekân/mahalle işlem bağlantısı kapsamı",
  f"Bağlantısız 0, yalnız harita 0 ({n_cards}/{n_cards} kart; 527 bağlantı). Bilgi: hiçbir mekânda harita bağlantısı yok, haritalama koordinatla (ISS-006)",
  "text_quality action_links + capraz.py", "text-quality.json → action_links", sinir="Bağlantının doğru işleme gitmesi K53 (L).")
C("K22", "kaldı", "Mekân ve mahalle fotoğraf kapsamı",
  f"Fotoğraflı mekân {capraz['photos']['places_with_photo']}/{len(mek)}, mahalle {capraz['photos']['districts_with_photo']}/{len(mah)}; fotoğrafsız {len(ews)} (19 mekân + 5 mahalle); collection=Evet 13/100, bunların 4'ü fotoğrafsız ve doğrulayıcı uyarısından muaf",
  "validate_all uyarı sınıfı + photo_prefilter + capraz.py", "validation-audit.json; _foto/decisions.json; _analiz/capraz-kontroller.json → photos",
  ["ISS-004", "ISS-007"], "Fotoğrafın doğru yeri göstermesi K60 (V), L0'da bakılmadı.")
C("K23", "geçti", "Fotoğraf tekilliği ve kredi",
  f"{n_photo_rows} satır → {capraz['photos']['unique_file_sha']} farklı dosya, {capraz['photos']['unique_source_url']} farklı kaynak sayfası; 8 kapak satırı mekân karesiyle aynı SHA (rol ayrı: kapak 8, mekân 250); author/license 258/258 dolu; mekân başına kare 1–3 (3 kare 74, 2 kare 11, 1 kare 6)",
  "validate_all media + capraz.py", "validation-audit.json → media; _analiz/capraz-kontroller.json → photos")
C("K24", "kısmi", "Eşiklerin işlevsel tamamlanması",
  "Asgari eşiklerin tamamı ham sayımla karşılanıyor; hedef eksikleri ayrı görünür (ISS-001/002/003). Kalite sonrası yeniden sayım L/V sonuçları olmadan yapılamadı",
  "render_summary", "_render/TESLIM_OZETI.txt", ["ISS-001", "ISS-002", "ISS-003"], "L/V elemesi yapılmadığından kullanılabilir sayı yok.")
L("K25", "Başlıktaki soruya doğrudan cevap")
L("K26", "Mikro kartın gerekli ayrıntıları")
C("K27", "geçti", "Birebir metin tekrarı",
  "Birebir kart kümesi 0, yakın küme 0, şablon küme 0, ortak adım 0; tekrar eden cümle 27, hepsi Fotoğraflar.modifications teknik alanında ('kırpma, rötuş ve renk düzeltmesi yapılmadı' ×257 ve boyut beyanları); kısa tekrar 1 grup (Yanıtlar.cost 'Ücretsiz' ×3, meşru)",
  "text_quality", "text-quality.json → exact_duplicates, near_duplicates, repeated_sentences, short_repeats", sinir="Ortak alanların meşruiyeti anlamsal olarak K28 (L).")
L("K28", "Anlamsal tekrar ve numaralı doldurma")
L("K29", "İddia ile kaynak eşleştirme",
  f"claim_check (unit modu): {n_claims} sayısal iddianın {by_result['supported']}'si taze kaynak kopyasında bulundu (doğrulama değil); {by_result['not_in_source']} 'not_in_source' — süre ({claims['by_kind']['duration']['not_in_source']}/445), hafta günü ({claims['by_kind']['weekday']['not_in_source']}/111) ve yaş ({claims['by_kind']['age']['not_in_source']}/96) türlerinde yoğun; Türkçe birim/gün adlarının İspanyolca kaynakta dize olarak bulunmaması beklenir, karar L1 ajanının.")
C("K30", "kısmi", "Toplu genel kaynak atama",
  f"Toplu anasayfa ataması 0 (validate_all ek kontrol); url_check 'homepage_only' {len(homepage_only)} adres (Kaynaklar 14 ilişki: mekânların kendi siteleri; Şehir!8 aemet.es). Kaynak sayısı: Yanıtlar 1 kaynak 80 / 2 kaynak 159; Mekânlar 1 kaynak 71 / 2 kaynak 29; Sözlük 1 kaynak 44",
  "validate_all extras + url_check flags + capraz.py", "validation-audit.json → extras.homepage_only_sources; url-checks.json; _analiz/capraz-kontroller.json",
  sinir="İddia bazında gerçek destek K29 (L).")
L("K31", "Yerel özgüllük ve doğru kurum", "Kaynaklar'ın 99'u visitasevilla.es (turizm ofisi), 79'u juntadeandalucia.es, 48'i boe.es; belediye (sevilla.org) yalnız 4 adres.")
L("K32", "Dil, tutarlılık ve desteklenmeyen vaat", "hitap standardı 'sen': karışık 0, 'siz' 0 (727 kayıt).")
C("K33", "kısmi", "Süreç görselinin doğruluğu", "visual_json 2/239 kartta dolu ve geçerli, hata 0; 237 boş (isteğe bağlı)", "text_quality visual_json", "text-quality.json → visual_json", sinir="Görselin steps ile anlamsal uyumu L.")
L("K34", "Değişken iddia envanteri", f"claim_extract envanteri: {n_claims} iddia / {claims['entries']} kart (para 394, tarih 397, süre 445, yüzde 215, saat 222, gün 111, yaş 96); resmî kaynakta doğrulanan 0.")
L("K35", "Resmî kaynak ve yürürlük", "ülke paketi (ES v9 + Endülüs v2) kartları: paket beyanına göre 6 kira kartının geçerliliği 2026-11-05'te bitiyor (OI-006) — L1'de yürürlük tarihi okunmalı.")
C("K36", "uygulanmaz", "Portekiz D7/D8 gibi vize tutarları", "—", sinir="D7/D8 kısmı yalnız Portekiz (PT) için; şehir ES. İspanya vize/oturum tutarları K35/K37 (L) altında, L0'da not_checked.")
L("K37", "Ücret ve hesap doğruluğu")
L("K38", "Müze ücretsiz günleri ve indirimler", "paket beyanı OI-009: Katedral işsiz indirimi kapsamı atıflı bırakıldı.")
L("K39", "Açık/kapalı bilgisi ve erişim",
  "tarihli 'itibarıyla' notu olan 4 mekân (Mekânlar!36 museo-arqueologico, !56 teatro-lope-de-vega, !71 isla-magica, !73 estadio-benito-villamarin-tur: tur La Cartuja'da); paket beyanı OI-011: 57 mekân 'belirsiz', Pabellón de la Navegación silindi — beyan kanıt değil, açık-mı örneklemi L1'de.")
L("K40", "Süre, son tarih ve başvuru bağımlılığı")
L("K41", "Kaynak çelişkisi veya erişilememe", "paket beyanı OI-009: EMVISESA iki sayfa çelişkisi, SAS randevu iki görüş.")
L("K42", "Gerçek mekân ve doğru şube", "aynı koordinatlı çift estadio-la-cartuja / estadio-benito-villamarin-tur (kart: Betis turu geçici olarak La Cartuja'da); collection=Evet 13 kayıt (ISS-007).")
C("K43", "kaldı", "Koordinatların anlamlı olması",
  f"Koordinatı olan {capraz['coordinates']['with_coords']}/{len(mek)} mekân aralıkta (enlem {capraz['coordinates']['lat_range'][0]}–{capraz['coordinates']['lat_range'][1]}, boylam {capraz['coordinates']['lon_range'][0]}…{capraz['coordinates']['lon_range'][1]}); şehir merkezi kopyası yok; aynı koordinatlı 1 çift (kart notuyla tutarlı); koordinatı boş {len(nocoord)} mekân, harita bağlantısı da yok (ISS-006)",
  "validate_all (aralık) + extra_checks.shared_coordinates + capraz.py + Bağlantılar harita taraması", "validation-audit.json → extras.shared_coordinates; _analiz/capraz-kontroller.json → coordinates",
  ["ISS-006"], "Harita/adres doğrulaması L/V; koordinat sözleşmede isteğe bağlı, bulgu kullanıcı etkisine göre P2.")
L("K44", "Mahallelerin ayırt edici içeriği")
C("K45", "geçti", "Mahalle compare_json yapısı", "Resmî doğrulayıcı hata 0 (15 mahalle)", "validate_all", "validation-audit.json")
C("K46", "geçti", "Rota veri ilişkileri",
  "12 rota, durak 3–6 (route:007 Flamenko akşamı 3 durak); stops/ID uzunluk-sıra eşleşmesi, ilk durak = entry_id, tanımsız durak 0; durak olan fotoğrafsız mekânlar: centro-ceramica-triana (002), mercado-de-la-encarnacion, bodega-gongora, mercado-lonja-del-barranco (009), casa-de-la-guitarra (007, fotoğraflı), guadalquivir-paseo-de-las-delicias (012)",
  "validate_all + capraz.py", "_analiz/capraz-kontroller.json → routes")
L("K47", "Rota uygulanabilirliği")
L("K48", "Sözlüğün gerçek kullanım değeri")
C("K49", "geçti", "URL biçimi ve güvenli hedef", f"{n_urls} benzersiz URL: biçim sorunu 0, geçersiz 0", "url_check (biçim) + validate_all", "url-checks.json → summary.format_issues")
C("K50", "geçti", "Fiilî HTTP erişimi",
  f"{n_urls}/{n_urls} test edildi ({n_rel} ilişki: Bağlantılar 527, Kaynaklar 416, Şehir 4, SayfaAlanları 2): 200 = {urls['summary']['classes']['ok_200']}, yönlendirme→200 = {urls['summary']['classes']['redirect_ok']}, 404/410/soft-404 = 0, 403 = 0, 429 = 0, 5xx/ağ = 0. İlk koşuda {len(url1_net)} adres ağ hatası/zaman aşımı (sede.dgt.gob.es ×2, dgt.es ×2, boe.es, madrid-emb.mfa.gov.tr); ikinci koşuda hepsi 200",
  "url_check --retry-transient ×2", "url-checks.json; _analiz/url-checks-kosu1.json",
  sinir="Fotoğraf kaynak/lisans/dosya URL'leri K78 kapsamında, L0'da test edilmedi.")
L("K51", "200 yanıtı ve soft 404",
  f"url_check sinyalleri: soft-404 0; anasayfaya yönlenen 0; yalnız anasayfa kaynak {len(homepage_only)} (mekânların kendi siteleri; paket OI-013'te 3'ünü beyan ediyor); farklı alan adına yönlenen 3: casadelaguitarra.es→flamencoensevilla.com, aussa.es→aussa.com, auditorionissancartuja.com→auditoriocartuja.com.")
C("K52", "geçti", "403/429 ve geçici hata",
  f"İlk geçişte {len(url1_net)} adres ağ hatası (zaman aşımı/bağlantı koptu); --retry-transient ile bir kez yeniden denendi, hepsi 200. fetch_snapshot ilk koşuda 3 kopya alınamadı, ikinci koşuda 416/416. 403/429 yok; erişim engeli aşılmadı, sertifika doğrulaması kapatılmadı",
  "url_check ×2 + fetch_snapshot ×2 (--retry-transient)", "url-checks.json; _analiz/url-checks-kosu1.json; kanitlar/snap/index.jsonl")
L("K53", "İlgili işlem sayfası")
L("K54", "Resmî üçüncü taraf bilet/rezervasyon sağlayıcısı")
L("K55", "Harita bağlantısı ve telefon", "harita bağlantısı hiçbir mekânda yok (koordinatla haritalanıyor); 28 mekân koordinatsız (ISS-006).")
C("K56", "geçti", "Kapsam ve bağlantı sonuçlarının raporlanması",
  f"{n_urls} benzersiz URL → {n_rel} ilişki; test edilmeyen 0; ilk koşu hataları alan adına göre gruplu (sede.dgt.gob.es, www.dgt.es, www.boe.es, madrid-emb.mfa.gov.tr)",
  "url_check", "url-checks.json → summary; _analiz/url-checks-kosu1.json")
C("K57", "geçti", "Dosyanın görüntü olarak açılması", f"{inv['summary']['images']} görsel (258 JPEG + 250 WebP) açıldı; uzantı/format uyuşmazlığı 0; bozuk 0", "inventory + validate_all media", "dosya-envanteri.json; validation-audit.json → media.checks.image_decoding")
C("K58", "geçti", "Hash ve boyut doğruluğu", f"Beyan SHA = ölçülen (sha_mismatch 0); web_width/height beyanı = ölçülen {capraz['photo_chain']['web_dims_ok']}", "inventory + capraz.py (PIL boyut)", "dosya-envanteri.json; _analiz/capraz-kontroller.json → chain")
V("K59", "Bütün görsellerin görsel taraması", "Paftalar: temas-sayfalari/sheet_01–09.jpg (258 kare, 30'lu).")
V("K60", "Doğru nesne, mekân ve şehir",
  "L1 ipucu: prefilter 'flag' 11 kare — basilica-del-gran-poder-03 (sheet_01/18, detail_interior), parque-infanta-elena-01/02/03 (sheet_03/3–5, detail_interior), huevo-de-colon-01/02 (sheet_06/14–15, statue_subject), museo-del-baile-flamenco-03 (sheet_03/20, rights_review), real-academia-bellas-artes-sevilla-03 (sheet_04/7, detail_interior), auditorio-cartuja-sevilla-02/03 (sheet_05/9–10, detail_interior), kapak-06 (sheet_09/16, place_mismatch).")
V("K61", "Kaynak sayfasındaki kare ile teslim dosyası")
V("K62", "Kapakların doğruluğu", "8 kapak (Fotoğraflar!258–265, sheet_09 slot 11–18) mekân kareleriyle aynı dosya; kapak-06 (= plaza-de-toros-de-la-maestranza-01) 'place_mismatch' işaretli.")
C("K63", "geçti", "Türevler ve yakın görsel tekrarları",
  f"dHash 258 kare: {dhash['dhash_cift']} yakın çift, hepsi kapak↔mekân aynı dosya (rol ayrı, tek kare sayıldı); K63_aday 0; aynı SHA K63 sınıfı 0",
  "contact_sheet dHash + audit_prep ciftler/hazirla", "temas-sayfalari/dhash.json; _foto/dhash-ciftleri.json; _foto/hazirlik.json",
  sinir="Algısal eşleşme tek başına karar değil; görsel teyit L1.")
C("K64", "kısmi", "Yapay/yer tutucu görsel işaretleri", f"{dec['summary']['candidates']} adayın Commons kaydında yapay görüntü işareti (ai_generated) 0", "photo_candidates from-evidence + photo_prefilter", "_foto/candidates.jsonl; _foto/decisions.json", sinir="KAPSAM: kısmi; piksel analizi ve görsel inceleme L1.")
V("K65", "Kalite ve kullanım uygunluğu")
C("K66", "kısmi", "Fotoğraf incelemesi sonrası yeniden sayım", f"Teknik kredi sayımı: {n_unique_photos} mekân + 8 kapak (resmî); {n_photo_rows} ilişki", "render_summary + validate_all", "_render/TESLIM_OZETI.txt; validation-audit.json", sinir="Görsel inceleme yapılmadığından doğrulanmış sayı yok.")
C("K67", "kısmi", "Tekil esere ait lisans", f"{dec['summary']['candidates']} adayın Commons lisans alanı: izinli liste dışı (license_not_allowed) 0; kısıt (restrictions) 0; rights_review işareti 1 (museo-del-baile-flamenco-03: kişiler/sahne, L1 girdisi)", "photo_candidates from-evidence + photo_prefilter", "_foto/candidates.jsonl; _foto/decisions.json", sinir="KAPSAM: kısmi; tekil eserin lisansı ve görsel eşleşme L1.")
C("K68", "geçti", "Proje tarafından reddedilen kullanım koşulları", f"258 satır: {lic_txt}; reddedilen kullanım koşulu 0", "validate_all", "validation-audit.json; _analiz/capraz-kontroller.json → licenses")
C("K69", "geçti", "Lisans adı, sürümü ve URL", "license_label_url geçti (258), medya hatası 0", "validate_all", "validation-audit.json → media.checks")
C("K70", "geçti", "Gerçek fotoğrafçı",
  f"Yazar hatası 0 (--new-content); {capraz['url_roles']['author_url_blank_with_note']} fotoğrafta bağımsız profil URL'si yok, provenance_note ile açıklanmış (provenance_status 'Eksik alan var' 52)",
  "validate_all --new-content + capraz.py", "validation-audit.json → media.open_provenance_points", sinir="Yazarın gerçek fotoğrafçı olduğunun kaynakta okunması K71 (L).")
L("K71", "Kaynak zincirinin ilk kökeni", "52 karede bağımsız fotoğrafçı profili yok; CC0 12 + Public domain 4 dosyanın kökeni.")
L("K72", "Public domain/CC0 dayanağı", "CC0 1.0 12 + Public domain 4 dosya; 4 karede license_url = source_url (Commons dosya sayfası): basilica-del-gran-poder-02, parque-del-alamillo-01, estadio-la-cartuja-02, jardines-torre-de-los-perdigones-02.")
C("K73", "not_checked", "Özel açık/ücretsiz stok lisansları", "0", sinir="KAPSAM: script yok (SKILL: K73 not_checked).")
V("K74", "Kare içindeki ek haklar", "L1 ipucu: museo-del-baile-flamenco-03 'rights_review'.")
C("K75", "kısmi", "Atıf ve değişiklik bildirimi",
  f"fotograf-atiflari-v7.csv {capraz['teslimler']['csv_rows']} satır Excel ile alan alan aynı (downloaded_on biçimi hariç); modifications 258/258 dolu; atıf önizleme HTML'inde {capraz['teslimler']['html_img_src']} göreli src'nin tamamı pakette çözülüyor",
  "capraz.py (CSV/HTML ↔ Excel)", "_analiz/capraz-kontroller.json → teslimler", sinir="Görünür atıf önizlemesi K94 (ayrı aşama).")
C("K76", "kısmi", "Kanıtın kendisinin gerçek olması",
  f"Kaynaklar: 416 kayıt → snapshot SHA eşleşiyor 416/416 (kaynak:178 ve :259 aynı sayfa, iki Junta adresi); taze indirmeyle karşılaştırma {snapcmp['summary']['compared']}/416: başlık eşleşmesi {snapcmp['summary']['title_match']}; örtüşme medyanı {snapcmp['summary']['overlap_median']}; şüpheli 1: kaynak:106 (Kaynaklar!113, seg-social.es) paket kopyası İspanyolca, taze kopya İngilizce sürüm (başlık farklı, örtüşme 0,07) — dil varyantı, uydurma kopya işareti değil, L1'de bakılır",
  "snapcmp.py (toolkit extract_page ile iki taraf aynı biçimde)", "_analiz/snapshot-karsilastirma.json; kanitlar/snap/index.jsonl",
  sinir="Fotoğraf kanıtları (Kanıtlar.source_evidence_json, 258) kaynak sayfayla karşılaştırılmadı (L1).")
C("K77", "geçti", "Fotoğraf kaynak zincirinin tekil eşleştirmesi",
  "258/258 photo_id Fotoğraflar↔FotoğrafKaynakları↔Kanıtlar eşleşti; original_file=file ve original_sha256=sha256 258/258; evidence_id 258/258",
  "validate_all + capraz.py", "_analiz/capraz-kontroller.json → chain")
C("K78", "kısmi", "Beş farklı kaynak adresi",
  f"author_url {capraz['url_roles']['author_url_filled']}/258 (52 boş, provenance_note ile); rol karışması 5: 4 karede license_url = source_url (CC0/PD dayanağı, Commons dosya sayfası), casa-roman-sevilla-02'de original_file_url = downloaded_file_url",
  "capraz.py", "_analiz/capraz-kontroller.json → url_roles", sinir="Bu URL'lerin erişim sonucu L0'da test edilmedi; PD dayanağı K72 (L).")
C("K79", "kısmi", "Çekim, indirme ve kontrol tarihleri",
  "capture_date 214/258 dolu, 44 boş; tek varsayılan tarih yok (en sık 2016-09-11 ×6); downloaded_on 258/258 2026-10-25 (download-progress-v7.json ile aynı), source_checked_on ve Kanıtlar.checked_on 258/258 2026-10-25",
  "capraz.py tarih taraması", "_analiz/capraz-kontroller.json → dates, teslimler.download_progress", sinir="Tarih dayanaklarının kaynakta okunması L.")
C("K80", "geçti", "Orijinal ve web türevi",
  f"original_file = Fotoğraflar.file 258/258, SHA eşit; web_file WebP ({capraz['photo_chain']['web_sha_eq']} tekil), SHA ve ölçüler beyanla aynı 258/258; derivation 258/258 dolu",
  "inventory + capraz.py", "_analiz/capraz-kontroller.json → chain")
C("K81", "not_checked", "İncelenen karenin teslim edilen kare olması", "0", sinir="KAPSAM: script yok (SKILL: K81 not_checked). Bilgi: pixel_review_file = file 258/258; pixel_review_status insan alanı ('Bekliyor', değerlendirme dışı).")
C("K82", "geçti", "Kanıt ve manifestlerde tek doğruluk",
  f"photo-provenance-v7.json ve atıf CSV ↔ Excel: 258 satır, tüm alanlar aynı; normalized-tables-v7.json sekme sayıları Excel ile aynı; Teslimler/dosya-envanteri.json {n_files} yolu kapsıyor, SHA farkı yalnız kendi dosyası (doğası gereği); download-progress SHA'ları Excel ile 258/258",
  "capraz.py", "_analiz/capraz-kontroller.json → teslimler; dosya-envanteri.json ↔ Teslimler/dosya-envanteri.json", sinir="normalized-tables-v7.json alan bazında karşılaştırılmadı.")
C("K83", "geçti", "Teslim özeti ve açık konular",
  "TESLIM_OZETI ↔ bağımsız yeniden hesap: satır farkı 0 (tarih ve MB dahil); Durum 'DÜZELTME GEREKLİ' iki tarafta aynı; paket envanteri ↔ denetim envanteri yol farkı 0; ACIK_KONULAR sayı satırları aynı (üretici beyanları kanıt sayılmadı); ILERLEME_KAYDI tek kayıt, sayılar ölçümle aynı (258 foto, 416 kaynak)",
  "render_summary + SKILL K83 fark bloğu + k04.py", "_render/TESLIM_OZETI.txt; _analiz/k04-karsilastirma.json; Teslimler/ILERLEME_KAYDI.txt (salt okunur)",
  sinir="ACIK_KONULAR'daki üretici beyanları kanıt sayılmadı; yalnız sayısal tutarlılık denetlendi.")
C("K84", "geçti", "Kayıpsız ve taşınabilir teslim",
  "'\\' 0: Excel yol sütunları (file, *_file; 2.064 yol) ve Teslimler JSON/CSV/HTML (4.853 yol/bağlantı); mutlak yerel yol, geçici URL ve paket dışına çıkan bağlantı 0; tüm göreli yollar paket kökünden çözülüyor (missing 0)",
  "audit_prep ters_egik_cizgi + capraz.py + inventory", "_foto/hazirlik.json; _analiz/capraz-kontroller.json", sinir="Paket başka ortamda (Linux) fiilen açılıp denenmedi.")
C("K85", "geçti", "Zorunlu 23 SayfaAlanları anahtarı", "23/23 anahtar mevcut; tür/değer hatası 0", "validate_all", "validation-audit.json; _dump/SayfaAlanları.jsonl")
C("K86", "geçti", "facts, quick_links, advice_entry", "Resmî doğrulayıcı hata 0 (slug çözümü dahil)", "validate_all", "validation-audit.json")
C("K87", "geçti", "timeline ve Adımlar ayrı kontroller", "timeline hata 0; Adımlar 7 kayıt (≥4)", "validate_all", "validation-audit.json")
C("K88", "geçti", "Bütçe alanları", "Resmî doğrulayıcı hata 0", "validate_all", "validation-audit.json")
C("K89", "kısmi", "Keşif grupları ve filtreler",
  f"8 temel grup, her grupta 5–32 mekân ({grp_txt}); tarih payı 32/100 (eşik 0,35 altında, ama Spor 5 ve Çocuklarla keşif 7 zayıf); her grupta collection=Hayır kayıt var",
  "validate_all + capraz.py", "validation-audit.json → extras.history_share", sinir="Filtre önizlemesi ayrı aşama.")
L("K90", "Acil yardım ve eczane", "SayfaAlanları emergency_url ve pharmacy_url 200.")
L("K91", "Şehir para birimi, zaman dilimi ve hava durumu", "forecast_url aemet.es Sevilla belediye tahmini (id41091); EUR, Europe/Madrid.")
PREVIEW("K92", "Masaüstü ve mobil görünüm")
PREVIEW("K93", "Uçtan uca kullanıcı akışı")
PREVIEW("K94", "Web fotoğraf atfı")
C("K95", "geçti", "Resmî doğrulayıcıyı tam paketle çalıştırma", f"validate_all --mode audit --new-content: yapı hata 0 / uyarı {val['structure']['warnings'] if isinstance(val['structure'].get('warnings'), int) else len(val['structure']['warnings'])}, medya hata 0, technically_complete={val['summary']['technically_complete']}", "validate_all", "validation-audit.json", sinir="ready modu çalıştırılmadı: insan onayı beklediği için beklenen şekilde kapalı.")
C("K96", "geçti", "Hata türünü doğru yorumlama", "794 uyarı: 774 insan inceleme alanı (258 × 3; tasarım gereği 'Bekliyor', içerik bozukluğu değil) + 20 fotoğrafsız yer (tek kök neden, ISS-004; collection=Evet 4 kayıt uyarı dışında, ISS-007)", "validate_all warning_classes", "validation-audit.json → warning_classes")
C("K97", "geçti", "AI kontrolü ile insan kararını ayırma", "Kanıtlar metadata/pixel/rights 774/774 'Bekliyor'; editorial_status tüm sekmelerde 'Taslak' (Onaylandı/Doğrulandı değeri 0); Teslimat.reviewer boş; TESLIM_OZETI 'Editör tarafından onaylandı: HAYIR'", "capraz.py durum taraması", "_analiz/capraz-kontroller.json → status_values, approval_like", sinir="İnsan inceleme alanları tasarım gereği 'Bekliyor'; içerikleri değerlendirme dışı (görev kuralı).")
C("K98", "geçti", "Kanıtlı sorun kayıtları", f"Açık {len(issues)} bulgu ({len(open_ids['P1'])} P1 + {len(open_ids['P2'])} P2) 17 alanlı ISSUE şablonuyla", "—", "issues.json")
C("K99", "uygulanmaz", "Düzeltmeden sonra hedefli yeniden kontrol", "—", sinir="Bu şehrin ilk denetimi; önceki denetim ve önceki Excel yok, impact.py --diff çalıştırılmadı.")
C("K100", "geçti", "Denetim kapsamını sayısal raporlama", "Kapsam matrisi paydalarıyla DENETIM_OZETI.md'de", "—", "DENETIM_OZETI.md bölüm 3")
C("K101", "geçti", "Yayın önerisini engellere göre verme", "Karar editorial_score.py'den; açık P1'ler karar kapısı", "editorial_score.py", "score.json")
C("K102", "geçti", "Son teslimin bağımsız okunabilir olması", "Tüm çıktı tek klasörde (paket dışı)", "—", "denetim/sevilla_2026-10-25_L0/")
PREVIEW("K103", "Fotoğrafların üzerinde uyarı bandı olmaması")
C("K104", "geçti", "Okuyucuya denetim işi bırakan genel metinler", f"{n_cards} kart: dolgu 0, hedge kalıbı 0, kaçamak ilk cümle 0, işlem bağlantısız 0", "text_quality", "text-quality.json → hedges, evasive_answers, filler", sinir="Anlamsal düzeyde okuyucuya bırakılan iş K32 (L).")
V("K105", "Arşiv fotoğrafı ve güncel ziyaret deneyimi", "capture_date en eski 2006-02-25; 44 karede çekim tarihi yok.")
C("K106", "kısmi", "Ücretsiz ve gerçek fotoğraf şartının kesin uygulanması", "Lisanslar 258/258 ücretsiz ticari kullanıma izin veren aileden (CC BY/BY-SA/CC0/PD), medya hatası 0; Commons kaydında AI etiketi 0", "validate_all + photo_prefilter", "validation-audit.json; _foto/decisions.json", sinir="Piksel kökeni/AI üretimi görsel incelemesi (V) yapılmadı.")
C("K107", "kısmi", "Aday fotoğraf sayısı ile teslim fotoğrafı ayrımı",
  f"Aday {dec['summary']['candidates']} = Fotoğraflar satırı {n_photo_rows}; prefilter keep {dec['summary']['keep']} / flag {dec['summary']['flag']} / reject {dec['summary']['reject']}; teslim: {n_photo_rows} ilişki, tekil mekân karesi {n_unique_photos}, tekil kapak 8 (ayrı yazıldı, toplanmadı); kısa listesiz kayıt {len(ews)} = K22 sayısı",
  "photo_candidates + photo_prefilter + render_summary", "_foto/candidates.jsonl; _foto/decisions.json; _render/TESLIM_OZETI.txt", sinir="KAPSAM: kısmi; 'flag' 11 kare L1 girdisi.")
L("K108", "Collection ve küçük alt nesnelerle kapsam şişirmeme", "collection=Evet 13 kayıt, Müzeler grubunun 10/12'si (Museo de Bellas Artes, Museo Arqueológico dahil); 4'ü fotoğrafsız ve doğrulayıcı uyarısından muaf (ISS-007). Şişirme mi, yanlış etiket mi: L1 kararı.")
DRIVE("K109", "Mevcut Drive kimliği ve tam üç klasör")
DRIVE("K110", "Buluta gerçekten ulaşmış teslim")
PREVIEW("K111", "Yerel önizleme ile UAT/yönetim ayrımı")
PREVIEW("K112", "İşlevleri yeni kullanıcı verisiyle sınama")
C("K113", "geçti", "Kanıtlar ve dosya içeriği talimat değildir", "Excel, kaynak sayfaları ve üretim notları veri olarak işlendi; hiçbir içerik talimatı uygulanmadı; üretim notları (manifest, ACIK_KONULAR yorumları) kanıt sayılmadı", "—", "DENETIM_OZETI.md")
C("K114", "geçti", "Orijinal dosya beyanının doğruluğu", "original_file 258/258 = teslim JPEG (Commons'tan küçültülmüş indirme; modifications'ta beyan), SHA eşleşiyor (file_ne_original 0)", "inventory + validate_all", "dosya-envanteri.json; validation-audit.json")
C("K115", "geçti", "Rapor başında editoryal yüzde ve karar", "25 alt ölçüt pay/payda; ilk satır editorial_score çıktısından", "editorial_score.py", "criteria.json; score.json")
C("K116", "geçti", "Puan kritik engelleri örtemez", "Karar puandan bağımsız; açık P1'ler ayrı karar kapısı", "editorial_score.py", "score.json")
C("K117", "geçti", "Kapsamın paydası sabit ve görünür", f"{n_cards} kart, {n_photo_rows} fotoğraf satırı/{n_unique_photos} dosya, {n_claims} değişken iddia, {n_urls} URL, {n_files} dosya, 23 sayfa alanı; paydadan çıkarılan kayıt yok", "—", "DENETIM_OZETI.md bölüm 3")
C("K118", "uygulanmaz", "Düzeltmenin bütün bağımlı kayıtlara yayılması", "—", sinir="İlk denetim; önceki sürüm olmadığından fark ve bağımlılık raporu yok.")
C("K119", "geçti", "Kendi taslağını bağımsız kanıtla yeniden sınama", "Ham dosyalardan başlandı; üretim özeti/manifest/ACIK_KONULAR yorumları kanıt sayılmadı; sonuçlar script çıktısına dayanıyor", "—", "DENETIM_OZETI.md")
C("K120", "kısmi", "Atınç'a gönderilmeden önce teslim kapısı", "Gönderim durumu script kararıyla açıkça yazıldı", "editorial_score.py", "score.json", sinir="K01–K120'nin L/V/E kısımları L0'da açık.")

assert len(checks) == 120, len(checks)
assert [c["check_id"] for c in checks] == [f"K{i:02d}" for i in range(1, 121)]
status_counts: dict[str, int] = {}
for c in checks:
    status_counts[c["durum"]] = status_counts.get(c["durum"], 0) + 1

# ------------------------------------------------------------------ criteria (bolum 20)
n_places_total = len(mek) + len(mah)
with_photo = capraz["photos"]["places_with_photo"] + capraz["photos"]["districts_with_photo"]
criteria = [
    {"code": "A1", "status": "partial", "passed": 0, "required": target["answers"], "reason": f"Ham {counts['answers']} (üst sınır) < {target['answers']} → ISS-001; kullanılabilir/özgün kart sayımı K18 (L) yapılmadı; doğrulanan alt sınır 0."},
    {"code": "A2", "status": "not_checked", "reason": "Kartın soruyu çözmesi K25/K26 (L) yapılmadı."},
    {"code": "A3", "status": "not_checked", "reason": f"İddia-kaynak desteği K29 (L) yapılmadı; claim_check dize eşleşmesi ({by_result['supported']}/{n_claims}) destek kanıtı sayılmaz."},
    {"code": "A4", "status": "not_checked", "reason": f"Kritik/güncel doğruluk K34/K35 (L) yapılmadı; 0/{n_claims} resmî kaynakta doğrulandı."},
    {"code": "A5", "status": "not_checked", "reason": "Dil/konu değeri K28/K32 (L) yapılmadı; script: kart kopyası 0, hedge 0, hitap karışıklığı 0."},
    {"code": "B1", "status": "partial", "passed": 0, "required": target["places"], "reason": f"Ham {counts['places']} (üst sınır) < {target['places']} → ISS-002; kimlik/şube/açıklık doğrulaması K39/K42 (L) yapılmadı; doğrulanan alt sınır 0."},
    {"code": "B2", "status": "partial", "passed": 0, "required": target["neighborhoods"], "reason": f"Ham {counts['neighborhoods']} (üst sınır) < {target['neighborhoods']} → ISS-003; yerel somut karşılaştırma K44 (L) yapılmadı; doğrulanan alt sınır 0."},
    {"code": "B3", "status": "partial", "passed": 0, "required": target["routes"], "reason": "Durak bağları 12/12 script ile geçti (K46); fiziksel uygulanabilirlik K47 (L) yapılmadı; doğrulanan alt sınır 0."},
    {"code": "B4", "status": "not_checked", "reason": "Ham 60/60; anlam/kaynak K48 (L) yapılmadı."},
    {"code": "B5", "status": "not_checked", "reason": "Koordinat aralığı geçti (72 mekân), 28 mekân koordinatsız ve haritasız (ISS-006); ad/adres/harita/ziyaret durumu doğrulaması L/V yapılmadı."},
    {"code": "C1", "status": "partial", "passed": 0, "required": target["photos"], "reason": f"Tekil {counts['photos']} kare (üst sınır) = hedef {target['photos']}; görsel/hak doğrulaması V/L yapılmadı; doğrulanan alt sınır 0."},
    {"code": "C2", "status": "not_checked", "reason": "Görsel-kaynak-caption eşleşmesi K59–K62 (V) yapılmadı."},
    {"code": "C3", "status": "partial", "passed": 0, "required": n_places_total, "reason": f"Herhangi bir fotoğrafı olan yer {with_photo}/{n_places_total} (üst sınır); {len(ews)} yer fotoğrafsız → ISS-004; doğru kare teyidi V; doğrulanan alt sınır 0."},
    {"code": "C4", "status": "partial", "passed": 0, "required": counts["photos"], "reason": "Aynı-kare tekrarı yalnız kapak rolünde (dHash 8 çift, rol ayrı); kırpma/netlik K65 (V) yapılmadı; doğrulanan alt sınır 0."},
    {"code": "C5", "status": "not_checked", "reason": "8 farklı kapak var (kapaklar arası tekrar yok); kapak doğruluğu K62 (V) ve uyarı bandı K103 (önizleme) yapılmadı; kapak-06 'place_mismatch' işaretli."},
    {"code": "D1", "status": "not_checked", "reason": "Eser bazlı ücretsiz ticari izin teyidi: K67 script'i 258 adayda izinsiz lisans/kısıt 0 buldu (kısmi), K71/K72 (L) yapılmadı; etiketler 258/258 izinli aileden."},
    {"code": "D2", "status": "partial", "passed": 0, "required": counts["photos"], "reason": "Etiket↔URL tutarlılığı ve yazar alanı 258/258 (K69/K70); kaynakla eşleşme okunmadı; doğrulanan alt sınır 0."},
    {"code": "D3", "status": "partial", "passed": 0, "required": counts["photos"], "reason": f"Dosya/hash zinciri 258/258 tutarlı (K77/K80/K114), kaynak snapshot'ları taze kopyayla {snapcmp['summary']['compared']}/416 karşılaştırıldı, 1 dil varyantı (K76 kısmi); foto kanıtları açılmadı; doğrulanan alt sınır 0."},
    {"code": "D4", "status": "not_checked", "reason": "Kareye özgü ek haklar K74 (V) yapılmadı; rights_status insan alanı (tasarım gereği 'Bekliyor', değerlendirme dışı)."},
    {"code": "D5", "status": "not_checked", "reason": "Atıf CSV 258/258 Excel ile tutarlı (K75 kısmi); hedef görünümde kontrol K94 ayrı aşama."},
    {"code": "E1", "status": "ok", "passed": 11, "required": 12, "reason": "Sabit liste: bölüm 02 K08–K16 + K45, K46, K49 = 12 atomik kontrol; kaldı: K14 (ISS-008, tek kayıt)."},
    {"code": "E2", "status": "ok", "passed": n_files, "required": n_files, "reason": f"{n_files} beklenen dosyanın tamamı yol/format/hash ile çözülüyor; paket envanteri ↔ ölçüm SHA farkı yalnız dosya-envanteri.json'un kendisi (doğası gereği)."},
    {"code": "E3", "status": "ok", "passed": 23, "required": 23, "reason": "23/23 zorunlu anahtar; resmî doğrulayıcı tür/değer/referans hatası 0."},
    {"code": "E4", "status": "separate_stage", "reason": "Web işlevleri önizleme senaryoları ayrı aşama (preview-later)."},
    {"code": "E5", "status": "partial", "passed": 4, "required": 5, "reason": "Kök Excel ✓, üç klasör ✓, kimlik eşleşmesi ✓, sürüm/sayı tutarlılığı ✓ (TESLIM_OZETI ve envanter ölçümle birebir); bulut dosyaları (Drive) ayrı aşama — kontrol edilmedi."},
]
crit_findings = [
    {"id": "ISS-001", "priority": "P1", "criteria": ["A1"]},
    {"id": "ISS-002", "priority": "P1", "criteria": ["B1"]},
    {"id": "ISS-003", "priority": "P1", "criteria": ["B2"]},
    {"id": "ISS-004", "priority": "P1", "criteria": ["C3"]},
    {"id": "ISS-005", "priority": "P2", "criteria": ["E2"]},
    {"id": "ISS-006", "priority": "P2", "criteria": ["B5"]},
    {"id": "ISS-007", "priority": "P2", "criteria": ["C3", "B1"]},
    {"id": "ISS-008", "priority": "P2", "criteria": ["E1"]},
]
crit_doc = {
    "meta": {**meta, "template": "kılavuz 2.0 bölüm 20", "status_counts": status_counts,
             "note": "L0: L ve V ölçütleri not_checked; partial ölçütlerde 'passed' doğrulanan alt sınırdır. İnsan inceleme alanları değerlendirme dışı."},
    "criteria": criteria, "findings": crit_findings,
    "coverage": {"cards": [0, n_cards], "photos": [0, n_photo_rows], "critical_claims": [0, n_claims]},
}

(OUT / "check-results.json").write_text(json.dumps({"meta": {**meta, "template": "kılavuz 2.0 bölüm 16 CHECK", "status_counts": status_counts}, "checks": checks}, ensure_ascii=False, indent=1), encoding="utf-8")
(OUT / "issues.json").write_text(json.dumps({"meta": {**meta, "template": "kılavuz 2.0 bölüm 16 ISSUE", "open": open_ids}, "issues": issues}, ensure_ascii=False, indent=1), encoding="utf-8")
(OUT / "criteria.json").write_text(json.dumps(crit_doc, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps({"checks": len(checks), "status_counts": status_counts, "issues": len(issues), "open": open_ids,
                  "cards": n_cards, "photos": n_photo_rows, "claims": n_claims, "urls": n_urls, "files": n_files}, ensure_ascii=False))
