"""Malaga L0 kayitlari: issues.json + criteria.json (sayilar dosyalardan okunur)."""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parents[1]
j = lambda p: json.loads((OUT / p).read_text(encoding="utf-8"))
inv = j("dosya-envanteri.json")
val = j("validation-audit.json")["summary"]
ready = j("validation-ready.json")["summary"]["ready_scan"]
paket = j("_analiz/paket-duzeltme.json")
url = j("url-checks.json")["summary"]
dec = j("_foto/decisions.json")["summary"]
kk = j("kanit-kapsami.json")
sha = next(f["sha256"] for f in inv["files"] if f["path"].endswith(".xlsx"))
kart_satir = ", ".join(str(k["satir"]) for k in paket["kart"])
acik_url = url["verdicts"].get("erişim teyidi açık", 0)

ISS = [
 ("ISS-001", "P0", "güncellik", "K35", "Yanıtlar", 39, "malaga:yeni-turistik-daire-yasagi-43-mahalle", "summary, steps",
  "43 mahallede yasak; %4,53 üstü 32 mahallede %8 tavanına kadar ve altında yeni turistik daire açılabilir",
  "23.08.2025'ten beri bütün belediye alanında yeni turistik daire (VUT) en çok 3 yıl ya da yeni düzenleme onaylanana dek askıda",
  "Kart Ocak/Mayıs 2025 bölgesel kuralını güncel izin sonucu gibi veriyor. Paketin ACIK_KONULAR'ı 'turistik daire askı kararı' kaynağını bulamadığını yazıyor.",
  "Málaga Belediyesi duyurusu (malaga.eu ANUDocumentDisplayer/178062) ve BOP 22.08.2025; dış denetim R01",
  "Okur yasak olan bir işi yapılabilir sanır (ruhsat başvurusu, yatırım)", "Askı kararını kaynak kopyasıyla ekle, eski eşikleri 'önceki dönem' diye ayır; kopyası yoksa kartı sınırla",
  "Kart güncel kuralı resmî kaynakla anlatıyor", ["A4"]),
 ("ISS-002", "P0", "doğruluk", "K26", "Yanıtlar", 129, "malaga:aile-birlesimi-ile-oturum", "summary, steps, note",
  "Gelir şartı: iki kişilik aile için IPREM %150, ek kişi %50 (tek kural)",
  "Biri çocuk iki kişilik ailede yıllık IMV garantisinin %110'u + ek çocuk başına %10 ayrıca yazılı; izin sonrası vize/giriş/TIE sırası",
  "İspanya ülke paketi bu bulguyu kendi d2 turunda 'orta' buldu ve 26.10 d3'te düzeltti; Málaga paketin 25.10 kopyasıyla kuruldu, düzeltme gelmedi.",
  "ulke\\ES\\_is\\denetim\\oturum-d3_degisiklik.jsonl; _analiz\\paket-duzeltme.json; dış denetim R02 (bu denetimde canlı kaynak ayrıca açılmadı)",
  "Çocuklu aileler gelir şartını yanlış hesaplar", "Ülke paketinin güncel kartını şehre uygula, yerel kanal ekle", "Kartta IMV istisnası ve izin sonrası adımlar var", ["A2", "A4"]),
 ("ISS-003", "P1", "teslim", "K118", "Yanıtlar", kart_satir, ";".join(k["entry_id"] for k in paket["kart"]), "çeşitli",
  f"{paket['alan']} alan ülke paketinin eski metni",
  "Ülke paketinin 26.10 düzeltmeleri şehirde",
  f"{len(paket['kart'])} kartta paketin kaydettiği düzeltme teslim Excel'inde yok (ISS-002 bunlardan biri).",
  "_analiz\\paket-duzeltme.json (betikler\\paket_duzeltme.py)", "Bilinen ve düzeltilmiş hatalar okura gider",
  "pack_merge + country_apply yeniden; şehir değişiklikleriyle birleştir; değişen kartlar tam denetimden", "paket_duzeltme.py çıkış 0", ["A4"]),
 ("ISS-004", "P1", "fotoğraf", "K62", "Şehir", 8, "malaga", "hero_photo_id", "(boş)", "Kapak satırına bağlı kimlik (ör. malaga:photo:kapak-01)",
  f"Hazır kip taraması: {ready['human_gate']} insan onayı alanı + {ready['blockers']} engel ('Şehir: ana kapak fotoğrafı gerekli.'); taslak kip 0 hata verdi.",
  "validation-ready.json (validate_all --ready-scan)", "Şehir sayfası ana görselsiz", "hero_photo_id = uygun kapak", "ready_scan.blockers 0", ["C5"]),
 ("ISS-005", "P1", "teslim", "K83", "Teslimler", "-", "TESLIM_OZETI.txt; ACIK_KONULAR.txt; Teslimat!8", "Durum, notes, editor",
  "TEKNİK KONTROL GEÇTİ; 0 engelleyici; 'Drive'a yüklenmedi'; Hazırlayan Atınç",
  "Hazır kip engeli ve bilinen güncellik açığı engelleyici; sorumlu yönetim atamasıyla aynı; Drive durumu iddia edilmez",
  "Özet geçti derken ISS-001/004 açık; ACIK_KONULAR turistik daire askısını 'bilgi' gibi listeliyor.",
  "Teslimler\\TESLIM_OZETI.txt, _dump\\Teslimat.jsonl; dış denetim MAL-007", "Teslim alan kişi paketi hazır sanar",
  "Yeni render_summary (hazır kip engeli + Drive satırı) ile zinciri yeniden çalıştır", "Özet DÜZELTME GEREKLİ ya da engel 0", ["E5"]),
 ("ISS-006", "P2", "hak", "K74", "Kanıtlar", "8-349", "342 kanıt", "rights_basis", "Her karede aynı genel lisans cümlesi",
  "Kareye özgü ek hak sonucu (foto-inceleme-v7.jsonl'deki ek_hak)",
  f"Ön elemede {dec['flag']} kare işaretli (iç mekân/eser 4); dış denetim #151, #160, #294.",
  "_foto\\decisions.json; dış denetim MAL-004", "Dış denetim D4'ü kanıtsız sayar", "photo_rows yeni sürümüyle adım 6–7", "rights_basis kareye özgü", ["D4"]),
 ("ISS-007", "P2", "hak", "K80", "FotoğrafKaynakları", "-", "325 ilişki", "derivation", "Özgün teslim dosyası korundu",
  "Teslim dosyasının Commons küçültmesi olduğu ve orijinal baytların pakette olmadığı",
  "325/342 indirme adresi /thumb/; Fotoğraflar.modifications bunu söylüyor, derivation söylemiyor.",
  "Teslimler\\photo-provenance-v7.json; dış denetim MAL-005", "Hak zinciri yanlış okunur", "photo_rows yeni sürümü", "derivation küçültmeyi adlandırıyor", ["D3"]),
 ("ISS-008", "P2", "bağlantı", "K52", "Kaynaklar/Bağlantılar", "-", "-", "url", f"{acik_url} adres erişim teyidi açık", "erişim teyidi", "403/5xx/ağ hatası; bozuk 0",
  "url-checks.json", "-", "L1'de açılır", "-", ["E2"]),
]
keys = ("issue_id öncelik kategori check_id tablo Excel_satırı entry_id/photo_id alan mevcut_değer beklenen somut_gözlem "
        "kanıt kullanıcı_etkisi önerilen_düzeltme tekrar_kontrol_koşulu").split()
issues = [dict(zip(keys, row[:7] + row[7:15])) | {"dosya": "CITY-075_malaga_v001.xlsx", "durum": "Açık"} for row in ISS]
for issue, row in zip(issues, ISS):
    issue["kanıt"], issue["kullanıcı_etkisi"] = row[11], row[12]
(OUT / "issues.json").write_text(json.dumps(issues, ensure_ascii=False, indent=1), encoding="utf-8")

C = lambda code, status, reason, **kw: {"code": code, "status": status, "reason": reason, **kw}
crit = [
 C("A1", "not_checked", "Ham 244 ≥ 240; kullanılabilirlik K18 (L) yapılmadı."),
 C("A2", "not_checked", "K25/K26 (L) yapılmadı; ISS-002 bilinen eksik."),
 C("A3", "not_checked", "claim_check dize eşleşmesi destek kanıtı değil (supported 1107/2559)."),
 C("A4", "partial", "ISS-001 (P0, teyitli), ISS-002 (P0), ISS-003 (P1: 7 kart ülke paketi düzeltmesi yok); doğrulanan alt sınır 0.", passed=0, required=244),
 C("A5", "not_checked", "Hitap 'sen' bulgusu 0, kopya kümesi 0; dil değeri L."),
 C("B1", "not_checked", "Ham 120/120; açık-mı K39 (L) yapılmadı."),
 C("B2", "not_checked", "Ham 16/16; K44 (L)."),
 C("B3", "not_checked", "Ham 12/12; durak bağları resmî doğrulayıcıda geçti; K47 (L)."),
 C("B4", "not_checked", "Ham 62/60; K48 (L)."),
 C("B5", "not_checked", "Koordinat aralığı geçti; L/V."),
 C("C1", "not_checked", "Tekil 334 ≥ 250; görsel inceleme V yapılmadı."),
 C("C2", "not_checked", "K59–K62 (V)."),
 C("C3", "not_checked", "Fotoğraflı yer 136/136 (üst sınır); doğru kare V."),
 C("C4", "not_checked", f"dHash K63_aday 0; ön eleme flag {dec['flag']}; K65 (V)."),
 C("C5", "partial", "8 farklı kapak; hero_photo_id boş (ISS-004).", passed=0, required=8),
 C("D1", "not_checked", f"K67 script: ret 0, flag {dec['flag']}; K71/K72 (L)."),
 C("D2", "not_checked", "Lisans/yazar alanları dolu; 48 author_url boş; kaynakla eşleşme okunmadı."),
 C("D3", "partial", "Hash zinciri tutarlı (K04 0, ters eğik çizgi 0); derivation küçültmeyi adlandırmıyor (ISS-007).", passed=0, required=342),
 C("D4", "partial", "rights_basis genel (ISS-006).", passed=0, required=342),
 C("D5", "not_checked", "Atıf CSV/HTML var; görünür atıf önizlemede (K94 ayrı aşama)."),
 C("E1", "ok", "Resmî doğrulayıcı yapı 0, medya 0, 23 sayfa alanı.", passed=12, required=12),
 C("E2", "ok", f"{inv['totals']['files']} dosya yol/hash çözülüyor; K04 fark 0; CSV'ler RFC 4180 ile sağlam (dış denetim MAL-006 okuyucu farkı).", passed=1, required=1),
 C("E3", "ok", "23/23 zorunlu anahtar.", passed=23, required=23),
 C("E4", "separate_stage", "Web işlevleri önizleme aşaması."),
 C("E5", "partial", "Teslim özeti/sorumlu/Drive satırı tutarsız (ISS-005).", passed=0, required=5),
]
findings = [{"id": i["issue_id"], "priority": i["öncelik"], "criteria": row[15]} for i, row in zip(issues, ISS)]
meta = {"tool": "city-audit L0", "level": "L0", "label": "yerel paket denetimi", "city_id": "malaga", "catalog": "CITY-075",
        "xlsx": "CITY-075_malaga_v001.xlsx", "xlsx_sha256": sha, "checked_on": "2026-11-02",
        "external_audit": "Malaga_Detayli_Denetim_Raporu_20261102.pdf (%70, aynı SHA)",
        "kanit_kapsami": {"alt_sinir": kk["alt_sinir"], "onizleme_ile_azami": kk["onizleme_ile_azami"], "eksik": kk["eksik"]}}
(OUT / "criteria.json").write_text(json.dumps({"meta": meta, "criteria": crit, "findings": findings,
                                               "coverage": {"cards": [0, 244], "photos": [0, 334], "critical_claims": [0, 2559]}},
                                              ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps({"issues": len(issues), "P0": sum(i["öncelik"] == "P0" for i in issues), "P1": sum(i["öncelik"] == "P1" for i in issues)}))
