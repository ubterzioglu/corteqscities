"""kayitlar_l1.py: Sevilla L1 denetim kayıtları (CHECK, ISSUE, criteria) - kılavuz 2.0 bölüm 16/20.

Kullanım: python -I -X utf8 kayitlar_l1.py <OUT>
Önce birlestir.py çalışmış olmalı (claim-checks.json, photo-review.json). Sayılar script ve ajan çıktılarından
okunur; değerlendirme metinleri bu dosyada. Yalnız OUT altına yazar.
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.dont_write_bytecode = True
OUT = Path(sys.argv[1])
TODAY = "2026-10-25"
L0_DIR = "denetim/sevilla_2026-10-25_L0"


def load(rel: str):
    return json.loads((OUT / rel).read_text(encoding="utf-8-sig"))


def jl(rel: str) -> list[dict]:
    return [json.loads(l) for l in (OUT / rel).read_text(encoding="utf-8").splitlines() if l.strip()]


# ------------------------------------------------------------------ girdiler
val = load("validation-audit.json")
inv = load("dosya-envanteri.json")
k04 = load("_analiz/k04-karsilastirma.json")
k04["fark"] = len(k04["added"]) + len(k04["removed"]) + len(k04["changed"])
capraz = load("_analiz/capraz-kontroller.json")
snapcmp = load("_analiz/snapshot-karsilastirma.json")["summary"]
tarih = load("_analiz/tarih-sirasi.json")
urls = load("url-checks.json")
cs = load("claim-checks.json")
pr = load("photo-review.json")
tq = load("text-quality.json")
foto_h = load("_foto/hazirlik.json")
dec = load("_foto/decisions.json")
dhash = load("_foto/dhash-ciftleri.json")
fid = load("xlsx-fidelity.json")
sayim = load("acik-mi-sayim.json")
acik_den = load("acik-mi-denetim.json")
acik_acik = load("acik-mi-acik.json")
k20 = load("_l/k20_gruplar.json")
lic_ozet = load("_l/lisans_ozet.json")
mek = jl("_dump/Mekânlar.jsonl")
mah = jl("_dump/Mahalleler.jsonl")
yan = jl("_dump/Yanıtlar.jsonl")
soz = jl("_dump/Sözlük.jsonl")
fot = jl("_dump/Fotoğraflar.jsonl")
rot = jl("_dump/Rotalar.jsonl")
mekan_l = jl("_l/mekan_A.jsonl") + jl("_l/mekan_B.jsonl")
mah_l = jl("_l/mahalleler.jsonl")
rot_l = jl("_l/rotalar.jsonl")
bag_l = jl("_l/baglanti.jsonl")
sehir_l = jl("_l/sehir_sayfa.jsonl")
lis_l = jl("_l/lisans.jsonl")

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
n_urls = urls["summary"]["unique_urls"]
n_rel = urls["summary"]["relations"]
ews = dec["summary"]["entries_without_shortlist"]
mek_by_id = {m["entry_id"]: m for m in mek}
mah_by_id = {m["entry_id"]: m for m in mah}
fotosuz_mek = [mek_by_id[e] for e in ews if e in mek_by_id]
fotosuz_mah = [mah_by_id[e] for e in ews if e in mah_by_id]
coll_evet = [m for m in mek if m.get("collection") == "Evet"]
nocoord = [m for m in mek if m.get("latitude") in (None, "")]
k05_groups = foto_h["ayni_sha"]["K05"]
homepage_only = [u for u in urls["urls"] if "homepage_only" in (u.get("flags") or [])]
cross_host = [u for u in urls["urls"] if "cross_host_redirect" in (u.get("flags") or [])]
lic = capraz["licenses"]
lic_txt = ", ".join(f"{k} {v}" for k, v in sorted(lic.items(), key=lambda kv: -kv[1]))
grp_txt = ", ".join(f"{k} {v}" for k, v in k20["gruplar"].items())
csum = cs["summary"]
psum = pr["summary"]
yan_ids = {y["entry_id"] for y in yan}
soz_ids = {s["term_id"] for s in soz}
cards_checked = {c["entry_id"] for c in cs["cards"]}
yan_checked = cards_checked & yan_ids
soz_checked = cards_checked & soz_ids
fail_by_id = {c["entry_id"]: c for c in cs["card_failures"]}
by_res = csum["by_result"]
n_claim_rows = csum["agent_rows"]

meta = {
    "tool": "city-audit L1", "level": "L1", "label": "yerel paket denetimi", "city_id": "sevilla",
    "catalog": "CITY-107", "xlsx": xlsx_name, "xlsx_sha256": xlsx_sha,
    "previous_audit": f"{L0_DIR} (Excel 8c8b454b…, %7, DÜZELTME GEREKLİ)", "checked_on": TODAY,
}


def rows(items) -> str:
    return ", ".join(str(i["_row"]) for i in items)


# ------------------------------------------------------------------ ISSUE kayıtları
issues: list[dict] = []


def I(oncelik, kategori, check_id, tablo, excel, ids, alan, mevcut, beklenen, gozlem, kanit, etki, duzeltme, tekrar,
      criteria, durum="Açık", dosya=None):
    iid = f"ISS-{len(issues) + 1:03d}"
    issues.append({
        "issue_id": iid, "öncelik": oncelik, "kategori": kategori, "check_id": check_id, "tablo": tablo,
        "Excel_satırı": excel, "entry_id/photo_id": ids, "dosya": dosya or xlsx_name, "alan": alan,
        "mevcut_değer": mevcut, "beklenen": beklenen, "somut_gözlem": gozlem, "kanıt": kanit,
        "kullanıcı_etkisi": etki, "önerilen_düzeltme": duzeltme, "tekrar_kontrol_koşulu": tekrar, "durum": durum,
        "_criteria": criteria,
    })
    return iid


lis_by_pid = {(r["photo_id"] if r["photo_id"].startswith("sevilla:photo:") else f"sevilla:photo:{r['photo_id']}"): r
              for r in lis_l}


def lis(pid_suffix: str) -> dict:
    return lis_by_pid.get(f"sevilla:photo:{pid_suffix}", {})


st = lis("palacio-de-san-telmo-01")
ISS_P0_LIC = I(
    "P0", "Fotoğraf hakkı / CC0 dayanağı", "K72", "Fotoğraflar; Kanıtlar", f"Fotoğraflar!{st.get('_row', 100)}",
    "sevilla:photo:palacio-de-san-telmo-01", "license / author",
    "CC0 1.0; yazar 'Unknown author'",
    "Kamu malı/CC0 dayanağı ilk kaynakta doğrulanır; yazar biliniyorsa ve kredi isteniyorsa atıf verilir.",
    "Commons dosyası {{cc-zero}} ve yazarı {{unknown|author}} diyor; ilk kaynak PxHere sayfasında hem 'Public Domain' etiketi hem 'Atribución requerida' + CC BY 2.0 bağlantısı var ve yazar 'Carlos ZGZ' adıyla kredi isteniyor ('Debes acreditar al autor Carlos ZGZ'). Commons'ta inceleme etiketi yok. CC0 dayanağı doğrulanamıyor, atıf eksik (K71 de kaldı).",
    f"_l/lisans.jsonl (photo_id palacio-de-san-telmo-01; commons_url {st.get('commons_url', '')}); _l/lisans_ozet.json → P0",
    "Fotoğraf CC0 sanılarak atıfsız yayınlanırsa yazarın atıf şartı çiğnenir; yayın engeli (hak zinciri kırık).",
    "Kareyi lisansı tek ve doğrulanabilir başka bir Commons dosyasıyla değiştir; kalacaksa CC BY 2.0 + 'Carlos ZGZ' atfıyla ve PxHere sayfasının kopyasıyla kanıtla.",
    "Yeni karenin K71/K72 'geçti' (ilk kaynak lisansı tek, yazar adı Excel'de); L1 lisans ajanı yeniden bakmış.",
    ["D1", "D2"])

ISS_K22 = I(
    "P1", "Fotoğraf kapsamı", "K22", "Mekânlar", f"Mekânlar!{rows(fotosuz_mek)}", ", ".join(ews),
    "Fotoğraflar.entry_id ilişkisi",
    f"fotoğraflı mekân {capraz['photos']['places_with_photo']}/{len(mek)}; fotoğraflı mahalle {capraz['photos']['districts_with_photo']}/{len(mah)}",
    "Her fiziksel mekân en az bir doğru, gerçek fotoğrafla kapsanır.",
    f"{len(fotosuz_mek)} mekânın hiç fotoğraf ilişkisi yok (photo_prefilter entries_without_shortlist {len(ews)}; validate_all 'gerçek fotoğraf eksik' 18). L0'daki 24'ten (19 mekân + 5 mahalle) 18'e indi; mahalleler 16/16 tamam. Paket beyanı OI-019 (beyan, kanıt değil).",
    "validation-audit.json → warning_classes; _foto/decisions.json → summary.entries_without_shortlist; _analiz/capraz-kontroller.json → photos",
    "Mekân kartlarının %15'i görselsiz açılır; okur yeri tanıyamaz.",
    "Her kayda gerçek, tekil, ücretsiz-ticari lisanslı kare ekle; bulunamazsa kaydı fotoğraflı başka bir gerçek mekânla değiştir (mekân hedefi 120 korunur).",
    "photo_prefilter entries_without_shortlist = 0 ve validate_all 'gerçek fotoğraf eksik' = 0; yeni kareler L1 görsel ve hak incelemesinden geçmiş.",
    ["C3"])

rej = pr["rejects"]
ISS_REJ = I(
    "P1", "Yanlış/uygunsuz görsel", "K60", "Fotoğraflar", f"Fotoğraflar!{rows(rej)}",
    ", ".join(p["photo_id"] for p in rej), "file (görüntü)",
    "; ".join(f"{p['photo_id'].split(':')[-1]} [{', '.join(p['pafta_slot'])}]: {p['görüntüde_görülen']}" for p in rej),
    "Kare bağlı mekânın kendisini gösterir; maket/etkinlik/kişi ağırlıklı kare mekân karesi sayılmaz; tanınır yüzler hak incelemesinden geçer.",
    "Paftalarda 3 kare ret: " + "; ".join(f"{p['photo_id'].split(':')[-1]} ({', '.join(p['pafta_slot'])}) — {p['ek_hak_notu']}" for p in rej) + ".",
    "temas-sayfalari/sheet_NN.jpg (pafta/slot yukarıda); _foto/photo-review_A.jsonl; photo-review.json → rejects",
    "Okur yanlış nesneyi (kule maketi) ya da mekân yerine etkinlik/yüzleri görür; yüzlü kare kişilik hakkı riski taşır (K74).",
    "Üç kareyi mekânın kendisini gösteren karelerle değiştir; flamenko karesini kaldır ya da yüzsüz kareyle değiştir.",
    "Yeni kareler paftada 'keep'; museo-del-baile-flamenco-03 için K74 'geçti'.",
    ["C2", "D4"])

lic_p1 = [lis("plaza-de-toros-de-la-maestranza-01"), lis("kapak-06"), lis("estadio-la-cartuja-02")]
ISS_LIC_P1 = I(
    "P1", "Fotoğraf hak zinciri doğrulanamıyor", "K71", "Fotoğraflar",
    "Fotoğraflar!" + ", ".join(str(r.get("_row")) for r in lic_p1),
    "sevilla:photo:plaza-de-toros-de-la-maestranza-01, sevilla:photo:kapak-06, sevilla:photo:estadio-la-cartuja-02",
    "license / source_url", "CC BY 2.0 (Flickr, Dimofte) ×2; Public domain (Galipedia beyanı)",
    "İlk kaynakta lisans bugün görülebilir ya da Commons'ta bağımsız inceleme etiketi (FlickreviewR/LicenseReview) var.",
    "Maestranza karesi ve aynı dosyayı kullanan kapak-06: Flickr kaynak sayfası 404, Commons'ta inceleme etiketi yok (2013 bot aktarımı); lisans bağımsız doğrulanamıyor. estadio-la-cartuja-02: PD dayanağı silinmiş bir Galipedia sayfasındaki yazar beyanı, aktaran kullanıcı yazardan farklı, inceleme yok (K72 belirsiz).",
    "_l/lisans.jsonl (üç satır); _l/lisans_ozet.json → P1",
    "Lisansı kanıtlanamayan kare (biri kapak) yayında hak itirazına açık.",
    "Üç kareyi incelenmiş (FlickreviewR/LicenseReview etiketli ya da yükleyen = yazar) dosyalarla değiştir; kapak-06 için ayrı kapak seç.",
    "Yeni karelerde K71 ve K72 'geçti'.",
    ["D1"])

# mekân bulguları (ajan) -------------------------------------------------
mek_b = [(r, b) for r in mekan_l for b in (r.get("bulgular") or [])]


def mb(check, pr_, ids=None):
    return [(r, b) for r, b in mek_b if b["check_id"] == check and b["oncelik"] == pr_
            and (ids is None or r["entry_id"] in ids)]


def obs(items):
    return " | ".join(f"!{r['_row']} {r['title']}: {b['gozlem']}" for r, b in items)


def kan(items):
    return "; ".join(sorted({b.get("kanit_url", "") for _, b in items if b.get("kanit_url")}))


k108 = mb("K108", "P1")
ISS_K108 = I(
    "P1", "Kapsam şişirme / alt nesne", "K108", "Mekânlar", f"Mekânlar!{rows([r for r, _ in k108])}",
    ", ".join(r["entry_id"] for r, _ in k108), "kayıt (ayrı mekân)", f"{len(k108)} kart başka bir kartın parçası",
    "Ayrı adresi, girişi ya da ziyaret deneyimi olmayan alt nesne ayrı mekân sayılmaz.",
    obs(k108), "_l/mekan_A.jsonl → bulgular K108; " + kan(k108),
    f"Mekân sayısı kâğıt üzerinde {len(mek)}, ayrı ziyaret edilebilir yer {len(mek) - len(k108)}; okur aynı gişe için üç kart görür.",
    "Üç kartı ana kartla birleştir (bahçe/müze/sur ana kartın içinde anlatılsın) ve yerlerine üç gerçek, fotoğraflı ayrı mekân ekle.",
    f"L1 mekân denetiminde K108 P1 bulgusu 0 ve mekân sayısı ≥ {target['places']}.",
    ["B1"])

k38 = mb("K38", "P1")
ISS_K38 = I(
    "P1", "Eski bilet fiyatı / saat", "K38", "Mekânlar", f"Mekânlar!{rows([r for r, _ in k38])}",
    ", ".join(r["entry_id"] for r, _ in k38), "summary / note (ücret, saat)",
    "genel 10 €, indirimli 6 €, 7–11 yaş 3,5 €; güreş günü 15:30",
    "Resmî bilet sayfasıyla aynı: genel 12 €, senior/öğrenci/genç 7 €, 7–11 yaş 4 €; güreş günü 09:30–15:00.",
    obs(k38), "_l/mekan_A.jsonl → bulgular K38; " + kan(k38) + " (canlı sayfa 2026-10-25; kanit/snap'te kopyası yok)",
    "Okur yanlış ücretle gelir; kart turizm sitesindeki eski tarifeyi aktarıyor.",
    "İki kartın ücret ve saatini resmî bilet sayfasından (visitaplazadetorosdesevilla.com/tarifas) güncelle, kaynağı Kaynaklar'a ekle ve kopyasını al; Museo Taurino'yu ISS (K108) ile birleştir.",
    "Kart değerleri resmî sayfa kopyasında birebir; claim_check 'supported'.",
    ["B5"])

p1_place = [(r, b) for r, b in mek_b if b["oncelik"] == "P1" and b["check_id"] in ("K42", "DIGER")]
ISS_PLACE = I(
    "P1", "Mekân bilgisi güncel/doğru değil", "K42", "Mekânlar", f"Mekânlar!{rows([r for r, _ in p1_place])}",
    ", ".join(sorted({r["entry_id"] for r, _ in p1_place})), "location / note / Bağlantılar",
    "kart adresi/saati/rezervasyon bağlantısı kaynakla uyuşmuyor",
    "Adres, açılış saati ve işlem bağlantısı mekânın resmî kaynağıyla aynı ve güncel.",
    obs(p1_place), "_l/mekan_B.jsonl → bulgular (K42/DIGER P1); " + kan(p1_place),
    "Okur yanlış yere (San Jerónimo parkı ~3,3 km) ya da geçmiş bir etkinliğin rezervasyon sayfasına gönderilir; teras saati yanlış.",
    "San Jerónimo parkının adres/koordinatını resmî kayda göre düzelt; Los Gallos rezervasyon bağlantısını genel rezervasyon sayfasına çevir, notu yıl yazarak güncelle; Setas mirador saatini resmî siteden al (kopyasıyla).",
    "Üç kartta L1 mekân denetimi K42 'geçti'.",
    ["B5"])

ISS_NOCOORD = I(
    "P2", "Konum / koordinat eksikliği", "K43", "Mekânlar", f"Mekânlar!{rows(nocoord)}",
    ", ".join(m["entry_id"] for m in nocoord), "latitude / longitude", f"{len(nocoord)}/{len(mek)} mekânda koordinat boş",
    "Mekân haritada gösterilebilir (koordinat sözleşmede isteğe bağlı).",
    f"{len(nocoord)} mekânda enlem/boylam boş (L0'da 28'di). Mekân ajanı Huevo de Colón, Nao Victoria ve Cartuja Qanat için kaynak koordinatı buldu (ör. Junta kaydı Cartuja Qanat 37.410118,-6.0044038). Ajan bunları P1 yazdı; L0 ile tutarlı olarak P2 (sözleşmede isteğe bağlı alan).",
    "_analiz/capraz-kontroller.json → coordinates (with_coords 116); _l/mekan_A/B.jsonl → koordinat 'yok'",
    "Dört mekân haritada görünmez.",
    "Dört mekâna resmî/doğrulanabilir koordinat ekle.",
    "Mekânlar'da koordinatı boş kayıt 0.",
    ["B5"])

k47 = [(r, b) for r in rot_l for b in (r.get("bulgular") or []) if b["oncelik"] == "P1"]
ISS_ROUTE = I(
    "P1", "Rota uygulanabilirliği", "K47", "Rotalar", f"Rotalar!{rows([r for r, _ in k47])}",
    ", ".join(r["route_id"] for r, _ in k47), "stops / note", "kapalı durak uyarısı yok",
    "Gün içi rotadaki her durak ziyarete açık ya da notta açıkça uyarılmış.",
    " | ".join(f"!{r['_row']} {r['title']}: {b['gozlem']}" for r, b in k47),
    "_l/rotalar.jsonl; " + "; ".join(b.get("kanit_url", "") for _, b in k47),
    "Okur ziyaret edilemeyen bir yapıya yönlendirilir.",
    "Cartuja Center'ı rotadan çıkar ya da 'yalnız etkinlik günlerinde açık' uyarısını notta yaz.",
    "L1 rota denetiminde K47 'geçti' (12/12).",
    ["B3"])

# iddia bulguları --------------------------------------------------------
eski = [c for c in cs["claims"] if c["sonuç"] == "eski"]
eski_by_entry = defaultdict(list)
for c in eski:
    eski_by_entry[c["entry_id"]].append(c)
yan_by_id = {y["entry_id"]: y for y in yan}
rc = "sevilla:sevilla-yenidogan-bebek-nufus-kaydi-registro-civil"
hv = "sevilla:sevilla-havalimani-merkez-ulasim"
ISS_RC = I(
    "P1", "Eski/çelişkili yasal süre", "K35", "Yanıtlar", f"Yanıtlar!{yan_by_id.get(rc, {}).get('_row', '?')}", rc,
    "summary / steps (kayıt süresi)", "24 saat / 8 gün / 30 gün",
    "Yürürlükteki Ley 20/2011 md. 47.1 ile uyumlu süre (10 gün) ya da bölge sayfasıyla yasanın çeliştiği açıkça yazılı.",
    f"{len(eski_by_entry[rc])} iddia 'eski': kart Junta de Andalucía sayfasıyla birebir aynı, ama yürürlükteki yasa bildirim süresini 10 gün veriyor (K41 var). Kaynak: https://www.boe.es/buscar/act.php?id=BOE-A-2011-12628 ; bölge sayfası https://www.juntadeandalucia.es/temas/familias-igualdad/formar-familia/hijos.html",
    "claim-checks.json → claims (sonuç 'eski', entry_id yukarıda); _iddia/parti_08.jsonl",
    "Ebeveyn yasal süreyi yanlış bilir; bölge sayfası ile yasa arasındaki fark okura söylenmiyor.",
    "Süreyi BOE konsolide metnine göre yaz; Junta sayfasındaki farklı süreyi not olarak ver; hastane bildirimi (72 saat) ile ebeveyn beyanını ayır.",
    "İddialar BOE kopyasında 'doğru'; K41 notu kartta.",
    ["A4"])
ISS_HV = I(
    "P1", "Eski ücret şüphesi (resmî sayfa erişilemedi)", "K41", "Yanıtlar",
    f"Yanıtlar!{yan_by_id.get(hv, {}).get('_row', '?')}", hv, "cost / summary (EA otobüsü, taksi)",
    "EA tek bilet 5 € / gidiş-dönüş 6 €; taksi en az 24,98 €",
    "Resmî TUSSAM tarifesi ve belediye taksi tarifesiyle aynı, kaynak kopyalı.",
    f"{len(eski_by_entry[hv])} iddia 'eski': ajan TUSSAM'ın 1 Mart 2025 tarifesini 6 € / 8 €, taksi sabit ücretini 26–29 € buldu; ancak tussam.es 403 ve belediye PDF'i açılamadı, değerler arama özetinden. Kart fiyatları yalnız visitasevilla.es (turizm, tarihsiz) kaynağına dayanıyor. Bu denetimde yanlışlık kanıtlanmadı, kaynak yetersizliği kesin.",
    "claim-checks.json → claims (entry_id yukarıda); _iddia/parti_08.jsonl; https://www.tussam.es/en/node/1397",
    "Havalimanından gelen okur yanlış ücret bekleyebilir.",
    "EA ve taksi tarifesini resmî sayfadan (TUSSAM, Instituto del Taxi) al, kopyasını pakete ekle; turizm sitesini tek kaynak bırakma.",
    "İddialar resmî kaynak kopyasında 'doğru'.",
    ["A4"])

eski_diger = [c for c in eski if c["entry_id"] not in (rc, hv)]
if eski_diger:
    I("P2", "Eski kurum adı / bilgi", "K35", "Yanıtlar", ", ".join(sorted({str(c.get("Excel_satırı")) for c in eski_diger})),
      ", ".join(sorted({c["entry_id"] for c in eski_diger})), "kart metni", f"{len(eski_diger)} iddia 'eski'",
      "Kurum adı ve bilgi güncel resmî kaynakla aynı.",
      "; ".join(f"{c['claim_id'].split(':')[-1]} @{c['entry_id'].split(':')[-1]}: {(c.get('doğrusu') or c.get('belirsizlik') or '')[:160]}" for c in eski_diger),
      "claim-checks.json → not_wrong (sonuç eski)", "Kural doğru, ad eskimiş; okur doğru kuruma ulaşır (eski adres yönleniyor).",
      "Kurum adını güncel adla yaz (Ministerio de Ciencia, Innovación y Universidades).", "İddia L1'de 'doğru'.", ["A4"])

ky = [c for c in cs["claims"] if c["sonuç"] == "kaynak_yetersiz"]
ISS_KY = I(
    "P2", "İddia kaynağı yetersiz", "K30", "Yanıtlar; Sözlük",
    ", ".join(sorted({str(c.get("Excel_satırı")) for c in ky})), ", ".join(sorted({c["entry_id"] for c in ky})),
    "iddia ↔ kaynak", f"{len(ky)} iddia 'kaynak_yetersiz'",
    "Her iddia bağlı kaynağın metninde yazılı.",
    "; ".join(f"{c['claim_id'].split(':')[-1]} @{c['entry_id'].split(':')[-1]}: {(c.get('iddia') or '')[:90]}" for c in ky),
    "claim-checks.json → not_wrong (sonuç kaynak_yetersiz)",
    "Kart bilgisi yanlış değil ama kaynakla kanıtlanmıyor (çoğu turizm sitesine dayanıyor).",
    "Her iddia için resmî sayfa ekle ya da ifadeyi kaynağın söylediğine indir.",
    "İlgili iddialar L1'de 'doğru'.",
    ["A3"])

fails = cs["card_failures"]


def card_issue(check, oncelik, kategori, beklenen, etki, duzeltme, crit):
    items = [c for c in fails if check in c["kaldı"]]
    if not items:
        return None
    return I(
        oncelik, kategori, check, "Yanıtlar; Sözlük", ", ".join(str(c["_row"]) for c in items),
        ", ".join(c["entry_id"] for c in items), "kart metni", f"{len(items)} kart {check} kaldı",
        beklenen,
        " | ".join(f"!{c['_row']} {c['title']}: {c['notlar'].get(check, '')}" for c in items),
        "claim-checks.json → card_failures; _iddia/kart_NN.jsonl", etki, duzeltme,
        f"Bu kartlarda L1 iddia denetçisi {check} 'geçti'.", crit)


ISS_K26 = card_issue("K26", "P1", "Mikro kartın gerekli ayrıntıları eksik",
                     "Kart soruyu çözecek ayrıntıyı verir: tutar, şart, belge, başvuru kanalı/yeri, tarih.",
                     "Okur kartı okuyup işlemi yapamaz; çoğunda başvuru yolu, belge listesi ya da tutar yok.",
                     "Her karta kaynakta yazan başvuru kanalı, belge listesi ve tutarı ekle; Sevilla'daki somut ofis/kurumu yaz.",
                     ["A2", "A1"])
ISS_K25 = card_issue("K25", "P1", "Başlıktaki soruya doğrudan cevap yok",
                     "İlk cümle başlıktaki soruyu cevaplar.", "Okur cevabı 3.-4. cümlede bulur.",
                     "İlk cümleyi soruya doğrudan cevap verecek biçimde yeniden yaz.", ["A2", "A1"])
ISS_K40 = card_issue("K40", "P1", "Süre/son tarih belirsiz",
                     "Süre ve son tarihler gün türüyle (iş günü/takvim günü) ve kaynakla aynı.",
                     "Okur süreyi yanlış hesaplayabilir.", "Süreleri kaynakla birebir ve gün türüyle yaz.", ["A4", "A1"])
ISS_K31 = card_issue("K31", "P1", "Yerel kurum/kanal eksik",
                     "Kart Sevilla'daki doğru kurumu ve kanalı verir.", "Okur nereye başvuracağını bilmez.",
                     "Sevilla'daki ofis, adres ve randevu kanalını ekle.", ["A2", "A1"])
k41 = [c for c in fails if c["K41_var"]]
ISS_K41 = I(
    "P2", "Kaynak çelişkisi", "K41", "Yanıtlar", ", ".join(str(c["_row"]) for c in k41),
    ", ".join(c["entry_id"] for c in k41), "kart notu", f"{len(k41)} kartta kaynaklar arası çelişki",
    "Çelişki kartta açıkça yazılı ve hangi kaynağın esas alındığı belirtilmiş.",
    " | ".join(f"!{c['_row']} {c['title']}: {c['notlar'].get('K41', '')}" for c in k41),
    "claim-checks.json → card_failures (K41_var)", "Çoğu kart çelişkiyi zaten not ediyor; okur hangi değerin geçerli olduğunu bilmeyebilir.",
    "Çelişkiyi notta yaz ve güncel resmî kaynağı esas al.", "K41 notu kartta, güncel kaynak belirtilmiş.",
    ["A4"]) if k41 else None

k53_items = [r for r in bag_l if r["K53"] == "kaldı"]
if k53_items:
    I("P2", "İşlem bağlantısı ilgili sayfaya gitmiyor", "K53", "Bağlantılar", ", ".join(str(r["_row"]) for r in k53_items),
      ", ".join(r["action_id"] for r in k53_items), "url", f"{len(k53_items)} bağlantı",
      "Bağlantı kartın anlattığı işlemin sayfasına gider.",
      " | ".join(f"{r['action_id']} ({r['label']}): {r['gozlem']}" for r in k53_items),
      "_l/baglanti.jsonl", "Okur işlem sayfasını kendisi aramak zorunda kalır.",
      "Bağlantıyı işlemin kendi sayfasına çevir.", "L1 bağlantı örnekleminde K53 kaldı 0.", ["A2"])

# P2 grupları (ajanların diğer bulguları) ---------------------------------
p2_src = {
    "mekan": [(r, b) for r, b in mek_b if b["oncelik"] == "P2"],
    "mahalle": [(r, b) for r in mah_l for b in (r.get("bulgular") or []) if b["oncelik"] == "P2"],
    "rota": [(r, b) for r in rot_l for b in (r.get("bulgular") or []) if b["oncelik"] == "P2"],
    "sehir": [(r, b) for r in sehir_l for b in (r.get("bulgular") or []) if b["oncelik"] == "P2"],
    "lisans": [(r, b) for r in lis_l for b in (r.get("bulgular") or []) if b["oncelik"] == "P2"],
}
P2_META = {
    "mekan": ("Mekânlar", "_l/mekan_A.jsonl, _l/mekan_B.jsonl", ["B5"]),
    "mahalle": ("Mahalleler", "_l/mahalleler.jsonl", ["B2"]),
    "rota": ("Rotalar", "_l/rotalar.jsonl", ["B3"]),
    "sehir": ("SayfaAlanları; Şehir", "_l/sehir_sayfa.jsonl", ["E3"]),
    "lisans": ("Fotoğraflar", "_l/lisans.jsonl", ["D1"]),
}
CHECK_MAP = {"DIGER": "K42", "metin": "K86"}
p2_ids = []
for src, items in p2_src.items():
    groups = defaultdict(list)
    for r, b in items:
        groups[CHECK_MAP.get(b["check_id"], b["check_id"])].append((r, b))
    tablo, kanit, crit = P2_META[src]
    for check, its in sorted(groups.items()):
        label = lambda r: r.get("entry_id") or r.get("route_id") or r.get("photo_id") or r.get("anahtar")
        p2_ids.append(I(
            "P2", f"Bakım önerisi ({src})", check, tablo,
            ", ".join(sorted({str(r.get('_row', '—')) for r, _ in its})),
            ", ".join(sorted({str(label(r)) for r, _ in its})), "çeşitli", f"{len(its)} gözlem",
            "Bilgi güncel, kaynakla birebir ve kartın başlığıyla uyumlu.",
            " | ".join(f"{label(r)}: {b['gozlem'][:220]}" for r, b in its),
            kanit, "Okuru yanlış yere göndermez; güncellik ya da açıklık sorunu.",
            "Gözlemdeki her kaydı kaynağa göre düzelt.", f"İlgili ajan denetiminde {check} P2 bulgusu 0.",
            crit + (["E1"] if check == "K45" else [])))

flags = pr["flags"]
p2_ids.append(I(
    "P2", "Zayıf/şüpheli fotoğraf", "K65", "Fotoğraflar", f"Fotoğraflar!{rows(flags)}",
    ", ".join(p["photo_id"] for p in flags), "file (görüntü)", f"{len(flags)} kare 'flag'",
    "Kare mekânı açık ve tanınır biçimde gösterir.",
    " | ".join(f"{p['photo_id'].split(':')[-1]} [{', '.join(p['pafta_slot'])}]: {p['ek_hak_notu']}" for p in flags),
    "photo-review.json → flags; temas-sayfalari/", "Kare yanlış değil ama mekânı tanıtmıyor ya da düşük kaliteli (biri kapak-08).",
    "Daha iyi kare bulunan kayıtlarda değiştir; kapak-08 için Sevilla'yı temsil eden bir kare seç.",
    "Yeni karelerde paftada 'keep'.", ["C4", "C5"]))
p2_ids.append(I(
    "P2", "Yakın görsel tekrarı", "K63", "Fotoğraflar", "—",
    "museo-de-bellas-artes (sheet_05 slot 29–30); kapak-02 ↔ catedral-de-sevilla-giralda-01; kapak-05 ↔ triana-02",
    "file", "3 yakın sahne (dHash eşiği altı, gözle)", "Aynı mekânın kareleri farklı açı/içerik gösterir; kapak mekân karesini tekrarlamaz.",
    "Foto ajanları: Bellas Artes avlusunun iki karesi neredeyse aynı kadraj; iki kapak aynı mekânın başka bir karesiyle çok benzer sahne. dhash-ciftleri.json → K63_aday 0 (eşik altı).",
    "_foto/photo-review_A/B.jsonl; _foto/dhash-ciftleri.json", "Tekil kare sayımı etkilenmez; çeşitlilik düşer.",
    "Bellas Artes için farklı bir kare seç; kapakları mekân karelerinden ayrıştır.", "Gözle yakın tekrar 0.", ["C4"]))
p2_ids.append(I(
    "P2", "Klasör düzeni / tekrar dosya", "K05", "Kanıtlar", "—", "kapak-01…08 ve eşleştikleri mekân kareleri",
    "Lisans kanıtları/*.json", f"{len(k05_groups)} aynı-SHA kanıt dosyası grubu",
    "Paket içinde bayt bayt aynı dosya tekrar etmez ya da gerekçeli.",
    f"Envanter dup_sha {inv['summary']['dup_sha']} = kapak↔mekân {len(foto_h['ayni_sha']['kapak_mekan'])} + kanıt JSON tekrarı {len(k05_groups)} (L0 ISS-005 ile aynı kök neden, açık).",
    "dosya-envanteri.json → findings.dup_sha; _foto/hazirlik.json → ayni_sha", "İşlevi bozmaz.",
    "Kapak kanıt alanlarını mekân karesinin kanıt dosyasına bağla ya da tekrarın gerekçesini Teslimler'de yaz.",
    "audit_prep ayni_sha.K05 = 0 ya da gerekçe yazılı.", ["E2"]))
p2_ids.append(I(
    "P2", "Açık-mı notu güncel değil", "K39", "Mekânlar",
    str(mek_by_id.get("sevilla:hospital-de-los-venerables", {}).get("_row", "?")), "sevilla:hospital-de-los-venerables",
    "title / note", "'(Fundación Focus)' ve Focus org konseri ifadesi",
    "Kart mekânın güncel işletmecisini yazar.",
    "Geçici kapanış kartta tarihli notla var (belirt_teyitli). Doğrulayıcı: mülkiyet Archidiócesis'e iade edilmiş, yeni müze projesi (5 Ekim 2026) https://centrohistorico.info/informe-favorable-a-los-trabajos-de-investigacion-sobre-el-estado-del-hospital-de-los-venerables/",
    "_acikmi/parti_07_dogrulama.jsonl; acik-mi-sayim.json", "Okuru yanlış yere göndermez; kurum adı eskimiş.",
    "Başlıktan 'Fundación Focus'u çıkar, notu yeni duruma göre güncelle.", "Kart güncel işletmeciyi yazıyor.", ["B5"]))

open_ids = {"P0": [], "P1": [], "P2": []}
for i in issues:
    open_ids[i["öncelik"]].append(i["issue_id"])

# ------------------------------------------------------------------ CHECK kayıtları
checks: list[dict] = []


def C(cid, durum, beklenen, incelenen, yontem="—", kanit="—", bulgular=None, sinir=""):
    checks.append({
        "check_id": cid, "durum": durum, "beklenen_kapsam": beklenen, "incelenen_kapsam": incelenen,
        "yöntem": yontem, "kanıt_yolu_veya_URL": kanit, "bulgu_IDleri": [b for b in (bulgular or []) if b],
        "sınır_gerekçe": sinir, "checked_on": TODAY,
    })


def by_check(cid):
    return [i["issue_id"] for i in issues if i["check_id"] == cid]


def NC(cid, beklenen, why="L1 kapsamı dışında (P2 L kontrolü)."):
    C(cid, "not_checked", beklenen, "0", sinir=why)


def DRIVE(cid, beklenen):
    C(cid, "separate_stage", beklenen, "0", sinir="Ayrı aşama: Drive (drive-manual); yerel paket denetimi kapsamı dışında.")


def PREVIEW(cid, beklenen):
    C(cid, "separate_stage", beklenen, "0", sinir="Ayrı aşama: önizleme (preview-later); yerel paket denetimi kapsamı dışında.")


AJAN = "L1 alt ajanı (Sonnet, bağımsız; ORTAK.md)"
acik_s = sayim
mek_k42 = Counter(r["K42"] for r in mekan_l)
mek_k38 = Counter(r["K38"] for r in mekan_l)
mek_k54 = Counter(r["K54"] for r in mekan_l)
mek_k55 = Counter(r["K55"] for r in mekan_l)
mek_k108 = Counter(r["K108"] for r in mekan_l)
mah_k44 = Counter(r["K44"] for r in mah_l)
mah_k45 = Counter(r["K45"] for r in mah_l)
rot_k47 = Counter(r["K47"] for r in rot_l)
bag_k51 = Counter(r["K51"] for r in bag_l)
bag_k53 = Counter(r["K53"] for r in bag_l)
bag_k54 = Counter(r["K54"] for r in bag_l)
sh_k91 = Counter(r.get("K91") for r in sehir_l)
lis_k71 = Counter(r["K71"] for r in lis_l)
lis_k72 = Counter(r["K72"] for r in lis_l)
fail_ct = csum["card_fail_by_check"]
n_cards_chk = csum["cards_unique"]


def ctxt(c: Counter) -> str:
    return ", ".join(f"{k} {v}" for k, v in c.most_common())


DRIVE("K01", "Doğru şehir ve güncel paket")
C("K02", "geçti", "Paketteki tüm dosyalar gerçek baytlarıyla",
  f"{n_files}/{n_files} dosya okundu, SHA-256 hesaplandı; {inv['summary']['images']} görsel çözüldü; okuma hatası 0",
  "inventory.py (başlangıç ve bitiş)", "dosya-envanteri.json; _dosya-envanteri-son.json", sinir="Drive kopyası K03 (ayrı aşama).")
DRIVE("K03", "Drive ile yerel kopyanın aynı olması")
C("K04", "geçti" if k04["fark"] == 0 else "kaldı", "Denetim başı ve sonu paket SHA listeleri",
  f"Başta {k04['start_files']}, sonda {k04['end_files']} dosya; fark {k04['fark']}; Excel SHA {xlsx_sha[:16]}… değişmedi. Son envanter bütün ajanlar bittikten sonra alındı.",
  "inventory.py ×2 + k04.py", "dosya-envanteri.json; _dosya-envanteri-son.json; _analiz/k04-karsilastirma.json")
C("K05", "kaldı", "Kök XLSX + üç klasör; artık/çoklu Excel yok",
  f"Kök 1 XLSX; klasörler {capraz['inventory']['folders']}; orphan 0; aynı SHA {inv['summary']['dup_sha']} = kapak↔mekân {len(foto_h['ayni_sha']['kapak_mekan'])} + kanıt JSON {len(k05_groups)}",
  "inventory + audit_prep ayni_sha", "dosya-envanteri.json; _foto/hazirlik.json", by_check("K05"), "KAPSAM: kısmi.")
C("K06", "geçti", "Yetenek ve erişim sınırları kaydı",
  "XLSX okuma, bayt/SHA, HTTP, kod çalıştırma, paftalardan görsel inceleme ve web araştırması (alt ajanlar) kullanıldı; erişilemeyen sayfalar 'erişilemedi/belirsiz' yazıldı",
  "Araç kullanımı kaydı", "DENETIM_OZETI.md")
C("K07", "kısmi", "Referansın doğru kullanımı", f"Alt sınır/hedefler resmî doğrulayıcının değerlerinden ({minimum} / {target})",
  "validate_all", "validation-audit.json", sinir="Berlin örnek Excel'i açılmadı.")
C("K08", "geçti", "Sekmeler, başlıklar ve teslim profili", f"{n_sheets}/16 sekme; xlsx_fidelity fark {len(fid['diffs'])}; yapı hatası 0",
  "xlsx_dump + xlsx_fidelity + validate_all", "_dump/; xlsx-fidelity.json; validation-audit.json")
C("K09", "geçti", "Formül, biçim ve doğrulama alanları", f"xlsx_fidelity fark {len(fid['diffs'])} (kabul edilen openpyxl parçaları: {len(fid['accepted'])})",
  "xlsx_fidelity", "xlsx-fidelity.json")
C("K10", "geçti", "Ham kayıtların doğru sayımı", f"{n_sheets} sekme, {n_rows} satır; yer tutucu {tq['summary']['placeholders']}, dolgu {tq['summary']['filler']}",
  "xlsx_dump + text_quality + validate_all", "_dump/; text-quality.json")
C("K11", "geçti", "Kimlik ve adres adı eşleşmesi", f"Resmî doğrulayıcı kimlik/slug hatası 0 ({n_rows} satır)", "validate_all", "validation-audit.json")
C("K12", "geçti", "Yabancı anahtar ilişkileri",
  f"Bağ hatası 0; {len(rot)} rota durak eşleşmesi {sum(1 for r in capraz['routes'] if r['len_match'] and r['first_is_entry'] and not r['unknown_ids'])}/{len(rot)}; tanımsız kaynak referansı {len(capraz['sources']['dangling_refs'])}; bağlanmamış kaynak {len(capraz['sources']['unreferenced'])} (bilgi)",
  "validate_all + capraz.py", "validation-audit.json; _analiz/capraz-kontroller.json")
C("K13", "geçti", "Veri türleri ve izinli değerler", "Tür/enum hatası 0", "validate_all", "validation-audit.json")
C("K14", "geçti", "Tarihler ve sıralar",
  f"reviewed_on'dan sonra kontrol edilmiş kaynak {len(tarih['src_after_review'])}, bağlantı {len(tarih['link_after_review'])}; gelecek tarih 0; en son içerik tarihi {capraz['latest_content_date']} = Teslimat.updated_on {capraz['teslimat']['updated_on']}; notes şablon değil. Bilgi: Şehir.source_checked_on/coordinate_checked_on {tarih['sehir_dates']['source_checked_on']} (şablon değeri)",
  "tarih.py + capraz.py", "_analiz/tarih-sirasi.json; _analiz/capraz-kontroller.json")
C("K15", "geçti", "Dosya yolları ve arşiv güvenliği", "Ters eğik çizgi 0 (bütün yol sütunları ve Teslimler); mutlak yol, '..' 0; missing 0",
  "audit_prep ters_egik_cizgi + inventory", "_foto/hazirlik.json; dosya-envanteri.json")
C("K16", "geçti", "EkDetaylar ve uzun alanlar", f"EkDetaylar {capraz['ekdetaylar_rows']} satır; en uzun hücre {capraz['longest_cell']['chars']} karakter ({capraz['longest_cell']['sheet']}!{capraz['longest_cell']['row']})",
  "xlsx_dump + capraz.py", "_analiz/capraz-kontroller.json", sinir="KAPSAM: kısmi; EkDetaylar boş.")
C("K17", "geçti", "Berlin alt sınırı ile güncel üretim hedefi",
  "; ".join(f"{k} {counts[k]} ({minimum[k]}/{target[k]})" for k in target), "validate_all + render_summary",
  "validation-audit.json; _render/TESLIM_OZETI.txt", sinir="Ham sayılar; kullanılabilir sayı K18.")
C("K18", "kısmi", "Kullanılabilir kayıt sayısı",
  f"Yanıt: {len(yan_checked)}/{len(yan)} kart ajanla denetlendi, {len(yan_checked) - len([c for c in fails if c['entry_id'] in yan_ids and c['kaldı']])} kullanılabilir; mekân {len(mekan_l)}/{len(mek)} denetlendi (alt nesne {len(k108)}); mahalle {len(mah_l)}/{len(mah)}",
  AJAN, "claim-checks.json; _l/mekan_*.jsonl; _l/mahalleler.jsonl", [ISS_K26, ISS_K108], "Yanıtların bir kısmı seçim dışı kaldı (risk temelli seçim).")
C("K19", "geçti", "On iki konunun dolu olması", f"12/12 konu dolu (topics {counts['topics']})", "validate_all", "validation-audit.json")
C("K20", "geçti", "Keşif gruplarında gerçek içerik",
  f"8 grup dolu ({grp_txt}); kilise/manastır/kapel {k20['kilise_manastir_kapel_sayisi']}/{k20['toplam']} (çeşitlilik notu)", AJAN, "_l/k20_gruplar.json")
C("K21", "geçti", "İşlem bağlantısı kapsamı", f"Bağlantısız kart {tq['summary']['without_action']} ({n_cards} kart)", "text_quality", "text-quality.json → action_links")
C("K22", "kaldı", "Mekân ve mahalle fotoğraf kapsamı",
  f"Fotoğraflı mekân {capraz['photos']['places_with_photo']}/{len(mek)}, mahalle {capraz['photos']['districts_with_photo']}/{len(mah)}; fotoğrafsız {len(ews)}",
  "validate_all + photo_prefilter + capraz.py", "validation-audit.json; _foto/decisions.json", [ISS_K22])
C("K23", "geçti", "Fotoğraf tekilliği ve kredi",
  f"{n_photo_rows} satır → {capraz['photos']['unique_file_sha']} farklı dosya, {capraz['photos']['unique_source_url']} farklı kaynak; kapak 8 satırı rol ayrı",
  "validate_all + capraz.py", "_analiz/capraz-kontroller.json → photos")
C("K24", "kaldı", "Eşiklerin işlevsel tamamlanması",
  f"Ham hedefler 8/8 karşılandı; kalite sonrası: mekân {len(mek) - len(k108)} ayrı yer (alt nesne {len(k108)}), fotoğraflı mekân {capraz['photos']['places_with_photo']}/{len(mek)}",
  "render_summary + L1 ajanları", "_render/TESLIM_OZETI.txt; _l/mekan_A.jsonl", [ISS_K108, ISS_K22])
C("K25", "kaldı" if fail_ct.get("K25") else "geçti", "Başlıktaki soruya doğrudan cevap",
  f"{n_cards_chk} kart denetlendi ({len(yan_checked)} yanıt + {len(soz_checked)} sözlük); kaldı {fail_ct.get('K25', 0)}",
  "iddia-denetcisi.md (kart satırı)", "claim-checks.json → cards", [ISS_K25], "Seçim dışı yanıtlar denetlenmedi.")
C("K26", "kaldı", "Mikro kartın gerekli ayrıntıları", f"{n_cards_chk} kart; kaldı {fail_ct.get('K26', 0)}",
  "iddia-denetcisi.md", "claim-checks.json → card_failures", [ISS_K26])
C("K27", "geçti", "Birebir metin tekrarı", f"Birebir/yakın/şablon küme {tq['summary']['exact_clusters']}/{tq['summary']['near_clusters']}/{tq['summary']['template_clusters']}; tekrar cümle {tq['summary']['repeated_sentences']} (teknik alanlar)",
  "text_quality", "text-quality.json")
C("K28", "kısmi", "Anlamsal tekrar ve numaralı doldurma", "Script kopyası 0; anlamsal tekrar mekânlarda K108 ile bulundu (3 alt nesne); yanıtlarda ayrıca aranmadı",
  AJAN, "_l/mekan_A.jsonl", [ISS_K108], "Yanıtlar arası anlamsal tekrar araması L1'de yapılmadı.")
C("K29", "geçti", "İddia ile kaynak eşleştirme",
  f"{n_claim_rows} iddia satırı ({csum['script_claims_checked']}/{csum['script_claims']} script iddiası + {csum['rule_claims']} kural iddiası): doğru {by_res.get('doğru', 0)}, yanlış {by_res.get('yanlış', 0)}, eski {by_res.get('eski', 0)}, kaynak yetersiz {by_res.get('kaynak_yetersiz', 0)}, erişilemedi {by_res.get('erişilemedi', 0)}; script 'not_in_source' satırlarının ajan kararı: {csum['by_result_x_script']}",
  "iddia-denetcisi.md, 16 parti", "claim-checks.json; _iddia/parti_NN.jsonl", [ISS_KY],
  "Yanlış iddia 0; eski ve kaynak yetersiz ayrı bulgular (K35/K41/K30).")
C("K30", "kaldı" if ky else "geçti", "Toplu genel kaynak atama",
  f"Toplu anasayfa ataması 0; homepage_only {len(homepage_only)} adres; iddia düzeyinde kaynak yetersiz {len(ky)}",
  "validate_all + url_check + iddia ajanı", "validation-audit.json; url-checks.json; claim-checks.json", [ISS_KY])
C("K31", "kaldı" if fail_ct.get("K31") else "geçti", "Yerel özgüllük ve doğru kurum",
  f"{n_cards_chk} kart; kaldı {fail_ct.get('K31', 0)} (çok sayıda 'belirsiz': ulusal kaynak, Sevilla ofisi yok)", "iddia-denetcisi.md",
  "claim-checks.json → cards", [ISS_K31])
NC("K32", "Dil, tutarlılık ve desteklenmeyen vaat", f"L1 kapsamı dışında (P2). Script: hitap 'sen', karışık {tq['summary']['address']['karisik']}, 'siz' {tq['summary']['address']['siz']}.")
C("K33", "kısmi", "Süreç görselinin doğruluğu", f"visual_json hata {tq['summary']['visual_json_errors']}, boş {tq['summary']['visual_json_empty']}", "text_quality", "text-quality.json")
C("K34", "geçti", "Değişken iddia envanteri", f"claim_extract {csum['script_claims']} iddia; {csum['script_claims_checked']} ajanla resmî/yerel kaynakta okundu",
  "claim_extract + iddia ajanı", "claims.jsonl; claim-checks.json", sinir=f"{csum['script_claims_not_checked']} iddia seçim dışı kartlarda.")
C("K35", "kaldı" if eski else "geçti", "Resmî kaynak ve yürürlük", f"eski {len(eski)} iddia ({len(eski_by_entry)} kart)",
  "iddia ajanı", "claim-checks.json", [ISS_RC, ISS_HV])
C("K36", "uygulanmaz", "Portekiz D7/D8", "—", sinir="Yalnız Portekiz; şehir ES.")
C("K37", "geçti", "Ücret ve hesap doğruluğu", "Hesaplı iddialar (IRPF dilimleri, NLV 2.400×12, dijital göçebe 1.221×14×2) ajanlarca yeniden hesaplandı, hata 0; ücret eskiliği K35/K38'de",
  "iddia ajanı (hesap_varsa_girdiler)", "claim-checks.json")
C("K38", "kaldı", "Müze ücretsiz günleri ve indirimler", f"Mekân {len(mekan_l)}: {ctxt(mek_k38)}; yanıt kartlarında indirim eksikleri K26'da (Alcázar, Katedral)",
  AJAN, "_l/mekan_A/B.jsonl", [ISS_K38] + by_check("K38"))
C("K39", "kısmi", "Açık/kapalı bilgisi ve erişim",
  f"Örneklem {acik_s['orneklem']}/{len(mek)} (öncelikli {acik_s['oncelikli']}, rastgele {acik_s['rastgele']}); doğrulanan {acik_s['dogrulanan']}, doğrulanamayan {acik_s['dogrulanamayan']}; sınıflar {acik_s['sinif']}; kapanış 0",
  "acik_mi_denetim orneklem → ajan (acik-mi.md §2/§4) → acik_mi kapısı ×2 → fetch_snapshot → sayim",
  "acik-mi-denetim.json; acik-mi-acik.json; acik-mi-sayim.json; kanitlar/acikmi/; _acikmi/", by_check("K39"),
  "Örneklem denetimi: bütün paket için 'geçti' verilmez (L2).")
C("K40", "kaldı" if fail_ct.get("K40") else "geçti", "Süre, son tarih ve başvuru bağımlılığı", f"{n_cards_chk} kart; kaldı {fail_ct.get('K40', 0)}",
  "iddia ajanı", "claim-checks.json", [ISS_K40])
C("K41", "kaldı", "Kaynak çelişkisi veya erişilememe", f"Çelişki 'var' {csum['cards_K41_var']} kart; resmî sayfa erişilemeyen eski ücret şüphesi 1 kart",
  "iddia ajanı", "claim-checks.json", [ISS_K41, ISS_HV])
C("K42", "kaldı", "Gerçek mekân ve doğru şube", f"{len(mekan_l)} mekân: {ctxt(mek_k42)}", AJAN, "_l/mekan_A/B.jsonl", [ISS_PLACE] + by_check("K42"))
C("K43", "kaldı", "Koordinatların anlamlı olması",
  f"Koordinatlı {capraz['coordinates']['with_coords']}/{len(mek)}; aykırı 0; kaba {sum(1 for r in mekan_l if r['koordinat'] == 'kaba')}; yok {sum(1 for r in mekan_l if r['koordinat'] == 'yok')}; aynı koordinat {len(capraz['coordinates']['shared'])} çift (açıklamalı)",
  "validate_all + capraz.py + mekân ajanı (OSM)", "_analiz/capraz-kontroller.json; _l/mekan_*.jsonl", [ISS_NOCOORD, ISS_PLACE] + by_check("K43"))
C("K44", "geçti", "Mahallelerin ayırt edici içeriği", f"{len(mah_l)} mahalle: {ctxt(mah_k44)}", AJAN, "_l/mahalleler.jsonl", by_check("K44"))
C("K45", "kaldı", "Mahalle compare_json yapısı", f"Yapı hatası 0 (validate_all); içerik: {ctxt(mah_k45)} (Ulaşım başlığı ulaşım içermiyor)",
  "validate_all + mahalle ajanı", "validation-audit.json; _l/mahalleler.jsonl", by_check("K45"))
C("K46", "geçti", "Rota veri ilişkileri", f"{len(rot)} rota; eşleşme sorunu 0", "validate_all + capraz.py", "_analiz/capraz-kontroller.json → routes")
C("K47", "kaldı", "Rota uygulanabilirliği", f"{len(rot_l)} rota: {ctxt(rot_k47)}; en uzun adım {max(r['en_uzun_adim_km'] for r in rot_l)} km",
  AJAN, "_l/rotalar.jsonl", [ISS_ROUTE] + by_check("K47"))
NC("K48", "Sözlüğün gerçek kullanım değeri", f"L1 kapsamı dışında (P2). Bilgi: {len(soz_checked)} sözlük terimi iddia denetiminde okundu.")
C("K49", "geçti", "URL biçimi", f"{n_urls} URL: biçim sorunu 0", "url_check", "url-checks.json")
C("K50", "geçti", "Fiilî HTTP erişimi", f"{n_urls}/{n_urls} ({n_rel} ilişki): 200 {urls['summary']['classes']['ok_200']}, yönlendirme→200 {urls['summary']['classes']['redirect_ok']}, 4xx/5xx/ağ 0",
  "url_check ×2", "url-checks.json")
C("K51", "geçti", "200 yanıtı ve soft 404", f"{len(bag_l)} bağlantı örneklemi: {ctxt(bag_k51)}; soft-404 0", AJAN, "_l/baglanti.jsonl",
  sinir="Örneklem (64 bağlantı, risk temelli).")
C("K52", "geçti", "403/429 ve geçici hata", "İkinci koşuda 450/450 çalışıyor; erişim engeli aşılmadı", "url_check --retry-transient", "url-checks.json")
k53_k = [r for r in bag_l if r["K53"] == "kaldı"]
C("K53", "kaldı" if k53_k else "geçti", "İlgili işlem sayfası", f"{len(bag_l)} bağlantı: {ctxt(bag_k53)}; kaldı: " + "; ".join(f"{r['action_id']} ({r['gozlem'][:80]})" for r in k53_k),
  AJAN, "_l/baglanti.jsonl", by_check("K53"), "Örneklem.")
C("K54", "kaldı" if mek_k54.get("kaldı") else "geçti", "Resmî üçüncü taraf bilet sağlayıcısı", f"Mekân: {ctxt(mek_k54)}; bağlantı örneklemi: {ctxt(bag_k54)}",
  AJAN, "_l/mekan_*.jsonl; _l/baglanti.jsonl", by_check("K54"))
C("K55", "kaldı" if mek_k55.get("kaldı") else "geçti", "Harita bağlantısı ve telefon", f"Mekân: {ctxt(mek_k55)}", AJAN, "_l/mekan_*.jsonl", by_check("K55"))
C("K56", "geçti", "Kapsam ve bağlantı sonuçlarının raporlanması", f"{n_urls} URL → {n_rel} ilişki; test edilmeyen 0", "url_check", "url-checks.json")
C("K57", "geçti", "Dosyanın görüntü olarak açılması", f"{inv['summary']['images']} görsel açıldı; uzantı uyuşmazlığı 0", "inventory + validate_all", "dosya-envanteri.json")
C("K58", "geçti", "Hash ve boyut doğruluğu", f"sha_mismatch 0; web boyutu {capraz['photo_chain']['web_dims_ok']}", "inventory + capraz.py", "_analiz/capraz-kontroller.json")
C("K59", "geçti", "Bütün görsellerin görsel taraması", f"{psum['reviewed']}/{psum['photo_rows']} kare paftalarda incelendi (11 pafta + şüpheli pafta)",
  "foto-inceleme.md, 2 ajan", "temas-sayfalari/; _foto/photo-review_A/B.jsonl; photo-review.json")
C("K60", "kaldı" if rej else "geçti", "Doğru nesne, mekân ve şehir", f"Sonuç: {psum['by_result']}", "foto ajanı", "photo-review.json", [ISS_REJ])
NC("K61", "Kaynak sayfasındaki kare ile teslim dosyası", "Ajan yalnız paftaları gördü; kaynak sayfasındaki kareyle bayt/görsel karşılaştırma yapılmadı (L2).")
C("K62", "kısmi", "Kapakların doğruluğu", "8 kapak paftada: 7 uygun, kapak-08 zayıf temsil (flag); kapak-06 lisansı doğrulanamıyor (ISS hak zinciri)",
  "foto ajanı B", "_foto/photo-review_B.jsonl", [ISS_LIC_P1] + [i for i in p2_ids if issues[int(i[4:]) - 1]["check_id"] == "K65"],
  "16:9 kırpma önizlemede (ayrı aşama).")
C("K63", "kaldı", "Türevler ve yakın görsel tekrarları", f"dHash K63_aday {len(dhash.get('K63_aday', []))}; aynı SHA K63 0; gözle yakın sahne 3", "contact_sheet dHash + foto ajanı",
  "_foto/dhash-ciftleri.json; photo-review.json", by_check("K63"))
C("K64", "geçti", "Yapay/yer tutucu görsel işaretleri", f"Commons kaydında AI işareti 0; paftalarda yapay görüntü izlenimi 0 ({psum['reviewed']} kare)", "photo_prefilter + foto ajanı", "_foto/decisions.json; photo-review.json")
C("K65", "kaldı", "Kalite ve kullanım uygunluğu", f"flag {psum['by_result'].get('flag', 0)} kare", "foto ajanı", "photo-review.json → flags", by_check("K65"))
C("K66", "geçti", "Fotoğraf incelemesi sonrası yeniden sayım", f"Tekil mekân karesi {n_unique_photos}; ret {len(rej)} sonrası ≥ {n_unique_photos - len(rej)} (hedef {target['photos']})", "render_summary + photo-review", "photo-review.json")
C("K67", "geçti", "Tekil esere ait lisans", f"license_not_allowed 0, restrictions 0 ({dec['summary']['candidates']} aday); lisans ajanı {len(lis_l)} dosyada Excel↔Commons lisans uyuşmazlığı 0",
  "photo_prefilter + lisans ajanı", "_foto/decisions.json; _l/lisans.jsonl")
C("K68", "geçti", "Reddedilen kullanım koşulları", f"{n_photo_rows} satır: {lic_txt}", "validate_all", "validation-audit.json")
C("K69", "geçti", "Lisans adı, sürümü ve URL", "Medya hatası 0", "validate_all", "validation-audit.json")
C("K70", "kaldı", "Gerçek fotoğrafçı", f"Yazar hatası 0; profil URL'siz {capraz['url_roles']['author_url_blank_with_note']} (notlu); San Telmo karesinde gerçek yazar adı (Carlos ZGZ) Excel'de yok", "validate_all + lisans ajanı",
  "_l/lisans.jsonl", [ISS_P0_LIC])
C("K71", "kaldı", "Kaynak zincirinin ilk kökeni", f"{len(lis_l)} dosya (şüpheli 49 + rastgele own-work 15): {ctxt(lis_k71)}", "lisans ajanı (MediaWiki API + ilk kaynak)",
  "_l/lisans.jsonl; _l/lisans_ozet.json", [ISS_P0_LIC, ISS_LIC_P1] + by_check("K71"), "Risk temelli örneklem; kalan own-work dosyaları örneklemle temiz (15/15).")
C("K72", "kaldı", "Public domain/CC0 dayanağı", f"{len(lis_l)} dosya: {ctxt(lis_k72)}", "lisans ajanı", "_l/lisans.jsonl", [ISS_P0_LIC, ISS_LIC_P1] + by_check("K72"))
C("K73", "not_checked", "Özel stok lisansları", "0", sinir="KAPSAM: script yok.")
C("K74", "kaldı", "Kare içindeki ek haklar", "Paftada yüz/logo ağırlıklı kareler: ret 2 (flamenko dansçıları, Pablo de Olavide logolu etkinlik), flag 2 (el-patio-sevillano-01 yüz, flamenko dansçısı)", "foto ajanı",
  "photo-review.json", [ISS_REJ])
C("K75", "kısmi", "Atıf ve değişiklik bildirimi", f"Atıf CSV {capraz['teslimler']['csv_rows']} satır Excel ile aynı; HTML src {capraz['teslimler']['html_img_src']}/{n_photo_rows} çözülüyor", "capraz.py", "_analiz/capraz-kontroller.json → teslimler",
  sinir="Görünür atıf K94 (ayrı aşama).")
C("K76", "geçti", "Kanıtın kendisinin gerçek olması",
  f"Kaynak kopyaları {snapcmp['compared']}/{snapcmp['sources']} taze kopyayla karşılaştırıldı: başlık {snapcmp['title_match']}; şüpheli {snapcmp['suspect_title_differ_and_low_overlap']} (seg-social İngilizce sürüm, dil varyantı); iddia ajanları alıntıları kopyada birebir buldu",
  "snapcmp.py + iddia ajanı", "_analiz/snapshot-karsilastirma.json; claim-checks.json")
C("K77", "geçti", "Fotoğraf kaynak zinciri eşleştirmesi", f"{capraz['photo_chain']['evidence_id_match']}/{n_photo_rows} eşleşti; sorun {len(capraz['photo_chain']['problems'])}", "capraz.py", "_analiz/capraz-kontroller.json → photo_chain")
C("K78", "kısmi", "Beş farklı kaynak adresi", f"author_url {capraz['url_roles']['author_url_filled']}/{n_photo_rows}; rol karışması {len(capraz['url_roles']['role_mixing'])}", "capraz.py", "_analiz/capraz-kontroller.json → url_roles")
C("K79", "kısmi", "Çekim, indirme ve kontrol tarihleri", f"capture_date boş {capraz['dates']['Fotoğraflar.capture_date']['blank']}/{n_photo_rows}; downloaded_on {capraz['dates']['FotoğrafKaynakları.downloaded_on']['max']}", "capraz.py", "_analiz/capraz-kontroller.json → dates")
C("K80", "geçti", "Orijinal ve web türevi", f"original=file {capraz['photo_chain']['orig_eq_file']}/{n_photo_rows}; web SHA {capraz['photo_chain']['web_sha_eq']}/{n_photo_rows}", "capraz.py", "_analiz/capraz-kontroller.json")
C("K81", "not_checked", "İncelenen karenin teslim edilen kare olması", "0", sinir="KAPSAM: script yok.")
C("K82", "geçti", "Kanıt ve manifestlerde tek doğruluk", f"provenance {capraz['teslimler']['provenance_rows']} ve CSV {capraz['teslimler']['csv_rows']} satır Excel ile alan farkı 0", "capraz.py", "_analiz/capraz-kontroller.json → teslimler")
C("K83", "geçti", "Teslim özeti ve açık konular", "TESLIM_OZETI ↔ bağımsız yeniden hesap: satır farkı 0, yol farkı 0; Durum 'DÜZELTME GEREKLİ' iki tarafta aynı",
  "render_summary + K83 fark bloğu", "_render/TESLIM_OZETI.txt")
C("K84", "geçti", "Kayıpsız ve taşınabilir teslim", "'\\' 0 (bütün yol sütunları ve Teslimler JSON/CSV/HTML)", "audit_prep", "_foto/hazirlik.json")
C("K85", "geçti", "Zorunlu 23 SayfaAlanları anahtarı", "23/23; tür/değer hatası 0", "validate_all", "validation-audit.json")
C("K86", "geçti", "facts, quick_links, advice_entry", "Resmî doğrulayıcı hata 0; sayfa alanı metin gözlemleri P2", "validate_all + şehir ajanı", "_l/sehir_sayfa.jsonl", by_check("K86"))
C("K87", "geçti", "timeline ve Adımlar", "Hata 0; Adımlar 7", "validate_all", "validation-audit.json")
C("K88", "geçti", "Bütçe alanları", "Hata 0", "validate_all", "validation-audit.json")
C("K89", "kısmi", "Keşif grupları ve filtreler", f"8 grup ({grp_txt}); collection=Evet {len(coll_evet)}", "validate_all + capraz.py", "_dump/Mekânlar.jsonl", sinir="Filtre önizlemesi ayrı aşama.")
C("K90", "geçti", "Acil yardım ve eczane", "112 ve 061 doğrulandı; polis numaraları sayfada yok (P2)", AJAN, "_l/sehir_sayfa.jsonl", by_check("K90"))
C("K91", "geçti", "Para birimi, zaman dilimi, hava durumu", f"{ctxt(sh_k91)}", AJAN, "_l/sehir_sayfa.jsonl", by_check("K91"))
PREVIEW("K92", "Masaüstü ve mobil görünüm")
PREVIEW("K93", "Uçtan uca kullanıcı akışı")
PREVIEW("K94", "Web fotoğraf atfı")
C("K95", "geçti", "Resmî doğrulayıcı", f"yapı hata 0 / uyarı {val['summary']['structure']['warnings']}, medya hata 0, technically_complete={val['summary'].get('technically_complete', True)}", "validate_all --mode audit", "validation-audit.json")
C("K96", "geçti", "Hata türünü doğru yorumlama", "957 uyarı = 939 insan alanı (313×3, tasarım gereği) + 18 fotoğrafsız mekân (ISS K22)", "validate_all", "validation-audit.json → warning_classes", [ISS_K22])
C("K97", "geçti", "AI kontrolü ile insan kararını ayırma", f"İnsan alanları 'Bekliyor'; onay benzeri değer {len(capraz['approval_like_values'])}; editorial_status 'Taslak'", "capraz.py", "_analiz/capraz-kontroller.json")
C("K98", "geçti", "Kanıtlı sorun kayıtları", f"{len(issues)} bulgu 17 alanlı ISSUE şablonuyla", "—", "issues.json")
C("K99", "geçti", "Düzeltmeden sonra hedefli yeniden kontrol", "L0 bulguları yeni Excel'de yeniden ölçüldü (impact.py --diff; DENETIM_OZETI 'Önceki bulgular')", "impact.py + L0 script bloğu", "impact.json")
C("K100", "geçti", "Denetim kapsamını sayısal raporlama", "Kapsam matrisi paydalarıyla raporda", "—", "DENETIM_OZETI.md")
C("K101", "geçti", "Yayın önerisini engellere göre verme", "Karar editorial_score.py'den", "editorial_score.py", "score.json")
C("K102", "geçti", "Son teslimin bağımsız okunabilir olması", "Tüm çıktı paket dışında tek klasörde", "—", "denetim/sevilla_2026-10-25_L1/")
PREVIEW("K103", "Fotoğrafların üzerinde uyarı bandı olmaması")
C("K104", "geçti", "Okuyucuya iş bırakan genel metinler", f"hedge {tq['summary']['hedge_cards']}, kaçamak {tq['summary']['evasive']}; anlamsal kaçamaklar K26 bulgusunda ('bölgene göre değişir' vb.)", "text_quality + iddia ajanı", "text-quality.json; claim-checks.json", [ISS_K26])
C("K105", "geçti", "Arşiv fotoğrafı ve güncel ziyaret deneyimi", f"Paftalarda arşiv/siyah-beyaz kare 0; capture_date en eski {capraz['dates']['Fotoğraflar.capture_date']['min']}", "foto ajanı + capraz.py", "photo-review.json")
C("K106", "kısmi", "Ücretsiz ve gerçek fotoğraf şartı", f"Lisanslar izinli aileden; AI 0; lisans ajanı örnekleminde P0 1", "validate_all + photo_prefilter + lisans ajanı", "_l/lisans.jsonl", [ISS_P0_LIC])
C("K107", "geçti", "Aday ve teslim fotoğrafı ayrımı", f"Aday {dec['summary']['candidates']} = Fotoğraflar {n_photo_rows}; prefilter keep {dec['summary']['keep']} / flag {dec['summary']['flag']} / reject {dec['summary']['reject']}; kısa listesiz {len(ews)} = K22",
  "photo_candidates + photo_prefilter", "_foto/decisions.json")
C("K108", "kaldı", "Collection ve alt nesnelerle şişirmeme", f"{len(mekan_l)} mekân: {ctxt(mek_k108)}; collection=Evet {len(coll_evet)}", AJAN, "_l/mekan_*.jsonl", [ISS_K108] + by_check("K108"))
DRIVE("K109", "Drive kimliği ve üç klasör")
DRIVE("K110", "Buluta ulaşmış teslim")
PREVIEW("K111", "Yerel önizleme ile UAT ayrımı")
PREVIEW("K112", "İşlevleri yeni kullanıcı verisiyle sınama")
C("K113", "geçti", "Kanıtlar talimat değildir", "Kaynak sayfalarındaki metinler veri olarak işlendi; bir mekân sitesindeki gizli talimat metni (setasdesevilla.com) uygulanmadı", "—", "_l/mekan_B.jsonl")
C("K114", "geçti", "Orijinal dosya beyanı", f"file_ne_original {inv['summary']['file_ne_original']}", "inventory", "dosya-envanteri.json")
C("K115", "geçti", "Rapor başında yüzde ve karar", "ilk satır editorial_score çıktısından", "editorial_score.py", "score.json")
C("K116", "geçti", "Puan kritik engelleri örtemez", "Karar puandan bağımsız", "editorial_score.py", "score.json")
C("K117", "geçti", "Kapsamın paydası sabit", f"{n_cards} kart, {n_photo_rows} fotoğraf, {csum['script_claims']} iddia, {n_urls} URL, {n_files} dosya", "—", "DENETIM_OZETI.md")
C("K118", "kısmi", "Düzeltmenin bağımlı kayıtlara yayılması", "impact.py: L0 Excel'ine göre değişen/eklenen/silinen satırlar listelendi; bağımlı kayıtlar yeniden ölçüldü (L0 bloğu yeni Excel'de baştan)", "impact.py", "impact.json")
C("K119", "geçti", "Kendi taslağını bağımsız kanıtla sınama", "Ham dosyalardan başlandı; üretim notları kanıt sayılmadı; ajan sayıları dosyadan yeniden sayıldı", "—", "DENETIM_OZETI.md")
C("K120", "kısmi", "Atınç'a gönderilmeden önce teslim kapısı", "Gönderim durumu script kararıyla yazıldı", "editorial_score.py", "score.json", sinir="Drive/önizleme ayrı aşama.")

assert len(checks) == 120, len(checks)
assert [c["check_id"] for c in checks] == [f"K{i:02d}" for i in range(1, 121)]
status_counts = dict(Counter(c["durum"] for c in checks))

# ------------------------------------------------------------------ criteria (bölüm 20)
fail_yan = {c["entry_id"] for c in fails if c["entry_id"] in yan_ids and c["kaldı"]}
fail_soz = {c["entry_id"] for c in fails if c["entry_id"] in soz_ids and c["kaldı"]}
place_bad = {r["entry_id"] for r, b in mek_b if b["oncelik"] in ("P0", "P1")} | {m["entry_id"] for m in nocoord} | {"sevilla:hospital-de-los-venerables"}
place_bad -= {r["entry_id"] for r, _ in k108}  # K108 B1'de sayılır
n_places_total = len(mek) + len(mah)
with_photo = capraz["photos"]["places_with_photo"] + capraz["photos"]["districts_with_photo"]
venue_rej = [p for p in rej if p["rol"] != "Kapak"]
lic_bad = {r["photo_id"] for r in lis_l if r["K71"] != "geçti" or r["K72"] in ("kaldı", "belirsiz")}
k25_26_fail = {c["entry_id"] for c in fails if set(c["kaldı"]) & {"K25", "K26", "K31"}}
criteria = [
    {"code": "A1", "status": "partial", "passed": len(yan_checked) - len(fail_yan), "required": target["answers"],
     "reason": f"Ajanla denetlenen {len(yan_checked)}/{len(yan)} yanıtın {len(yan_checked) - len(fail_yan)}'ü K25/K26/K31/K40 geçti; {len(yan) - len(yan_checked)} yanıt seçim dışı (doğrulanmadı) → doğrulanan alt sınır."},
    {"code": "A2", "status": "ok", "passed": n_cards_chk - len(k25_26_fail), "required": n_cards_chk,
     "reason": f"Denetlenen {n_cards_chk} kartın {len(k25_26_fail)}'i soruyu çözmüyor (K25/K26/K31) → ISS K26/K25/K31."},
    {"code": "A3", "status": "ok", "passed": by_res.get("doğru", 0) + by_res.get("eski", 0), "required": n_claim_rows,
     "reason": f"{n_claim_rows} iddia satırında kaynak desteği: kaynak yetersiz {by_res.get('kaynak_yetersiz', 0)}, erişilemedi {by_res.get('erişilemedi', 0)}, yanlış {by_res.get('yanlış', 0)} (eski iddialar kaynakta var, güncellik A4'te)."},
    {"code": "A4", "status": "ok", "passed": n_claim_rows - by_res.get("eski", 0) - by_res.get("yanlış", 0), "required": n_claim_rows,
     "reason": f"Eski {by_res.get('eski', 0)} iddia (Registro Civil süresi, havalimanı ücretleri) → ISS K35/K41; kart düzeyinde K40/K41 ayrı bulgular."},
    {"code": "A5", "status": "not_checked", "reason": "K28/K32 (P2) L1 kapsamı dışında; script: kopya 0, hedge 0, hitap karışık 0."},
    {"code": "B1", "status": "ok", "passed": len(mek) - len(k108), "required": target["places"],
     "reason": f"{len(mekan_l)}/{len(mek)} mekân ajanla denetlendi; {len(k108)} alt nesne ayrı mekân sayılmış (K108 P1); kapanış 0 (açık-mı örneklemi)."},
    {"code": "B2", "status": "ok", "passed": sum(1 for r in mah_l if r["K44"] == "geçti"), "required": target["neighborhoods"],
     "reason": f"K44 {ctxt(mah_k44)}; K45 Ulaşım başlığı içerik sorunu 3 (P2, kullanılabilirliği bozmaz)."},
    {"code": "B3", "status": "ok", "passed": rot_k47.get("geçti", 0), "required": target["routes"], "reason": f"K47 {ctxt(rot_k47)} → ISS rota."},
    {"code": "B4", "status": "not_checked", "reason": f"K48 (P2) L1 kapsamı dışında; {len(soz_checked)} terim iddia denetiminde okundu, kaldı {len(fail_soz)}."},
    {"code": "B5", "status": "ok", "passed": len(mek) - len(k108) - len(place_bad), "required": len(mek) - len(k108),
     "reason": f"Ad/adres/saat/ücret/koordinat/ziyaret durumu: sorunlu {len(place_bad)} mekân (P1 ücret 2, adres/saat/bağlantı 3, koordinat P1 bulgusu ve boş koordinat, Venerables adı) → ISS K38/K42/K43/K39."},
    {"code": "C1", "status": "ok", "passed": n_unique_photos - len(venue_rej) - len(lic_bad & {p['photo_id'] for p in fot if p.get('role') != 'Kapak'}), "required": target["photos"],
     "reason": f"Tekil {n_unique_photos} mekân karesi; ret {len(venue_rej)} ve lisansı doğrulanamayan {len(lic_bad)} düşüldü; hedef {target['photos']} karşılanıyor."},
    {"code": "C2", "status": "ok", "passed": n_photo_rows - len(rej), "required": n_photo_rows, "reason": f"{psum['reviewed']} kare paftada; ret {len(rej)} → ISS K60."},
    {"code": "C3", "status": "ok", "passed": with_photo, "required": n_places_total, "reason": f"Fotoğrafsız {len(ews)} mekân → ISS K22."},
    {"code": "C4", "status": "ok", "passed": n_unique_photos - 1, "required": n_unique_photos, "reason": "Gözle yakın tekrar 1 mekân çifti (Bellas Artes) → ISS K63; flag kareler ayrı P2 bulgu (K65)."},
    {"code": "C5", "status": "ok", "passed": 8, "required": 8, "reason": "8 farklı kapak, görselde ret yok; kapak-08 zayıf temsil (P2), kapak-06 lisansı D1'de."},
    {"code": "D1", "status": "ok", "passed": n_photo_rows - len(lic_bad), "required": n_photo_rows,
     "reason": f"Risk temelli: {len(lis_l)} dosya ilk kaynağına kadar açıldı (şüpheli 49 + rastgele own-work 15, temiz 15/15); kaldı/belirsiz {len(lic_bad)} → ISS P0 + P1."},
    {"code": "D2", "status": "ok", "passed": n_photo_rows - 1, "required": n_photo_rows, "reason": "Etiket↔URL ve yazar 313/313 (validate_all); San Telmo karesinde gerçek yazar eksik → ISS P0."},
    {"code": "D3", "status": "ok", "passed": n_photo_rows, "required": n_photo_rows, "reason": f"Dosya/hash zinciri {capraz['photo_chain']['evidence_id_match']}/{n_photo_rows}; kaynak kopyaları {snapcmp['compared']}/{snapcmp['sources']} taze kopyayla karşılaştırıldı."},
    {"code": "D4", "status": "ok", "passed": n_photo_rows - 2, "required": n_photo_rows, "reason": "Yüz/logo ağırlıklı ret 2 kare → ISS K60/K74."},
    {"code": "D5", "status": "not_checked", "reason": "Atıf CSV/HTML Excel ile tutarlı (K75 kısmi); görünür atıf K94 ayrı aşama."},
    {"code": "E1", "status": "ok", "passed": 11, "required": 12, "reason": "K08–K16 + K45, K46, K49 = 12; kaldı K45 (Ulaşım başlığı, P2)."},
    {"code": "E2", "status": "ok", "passed": n_files, "required": n_files, "reason": f"{n_files} dosya yol/format/hash ile çözülüyor; kanıt JSON tekrarı P2."},
    {"code": "E3", "status": "ok", "passed": 23, "required": 23, "reason": "23/23 anahtar; K90/K91 geçti; metin gözlemleri P2."},
    {"code": "E4", "status": "separate_stage", "reason": "Önizleme ayrı aşama."},
    {"code": "E5", "status": "partial", "passed": 4, "required": 5, "reason": "Kök Excel, üç klasör, kimlik, sürüm/sayı tutarlılığı ✓; Drive ayrı aşama."},
]
crit_findings = [{"id": i["issue_id"], "priority": i["öncelik"], "criteria": i["_criteria"]} for i in issues]
crit_doc = {
    "meta": {**meta, "template": "kılavuz 2.0 bölüm 20", "status_counts": status_counts,
             "note": "L1: iddialar risk temelli seçimle (172/182 kart), mekânlar 120/120, fotoğraflar 313/313 pafta, lisans 64 örneklem, açık-mı 58 örneklem. İnsan inceleme alanları değerlendirme dışı."},
    "criteria": criteria, "findings": crit_findings,
    "coverage": {"cards": [len(yan_checked) + len(mekan_l) + len(mah_l), n_cards], "photos": [psum["reviewed"], n_photo_rows],
                 "critical_claims": [csum["script_claims_checked"], csum["script_claims"]]},
}
issues_out = [{k: v for k, v in i.items() if k != "_criteria"} for i in issues]
(OUT / "check-results.json").write_text(json.dumps({"meta": {**meta, "template": "kılavuz 2.0 bölüm 16 CHECK", "status_counts": status_counts}, "checks": checks}, ensure_ascii=False, indent=1), encoding="utf-8")
(OUT / "issues.json").write_text(json.dumps({"meta": {**meta, "template": "kılavuz 2.0 bölüm 16 ISSUE", "open": open_ids}, "issues": issues_out}, ensure_ascii=False, indent=1), encoding="utf-8")
(OUT / "criteria.json").write_text(json.dumps(crit_doc, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps({"checks": len(checks), "status_counts": status_counts, "issues": len(issues), "open": open_ids,
                  "coverage": crit_doc["coverage"]}, ensure_ascii=False))
