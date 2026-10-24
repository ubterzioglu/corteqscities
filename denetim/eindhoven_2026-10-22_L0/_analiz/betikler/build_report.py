"""Writes DENETIM_OZETI.md and fills the K04 record from the final inventory comparison. Reads only OUT."""
import json
import sys
from collections import Counter
from pathlib import Path

OUT = Path(sys.argv[1])
XLSX_MTIME = sys.argv[2]


def jload(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


cr = jload(OUT / "check-results.json")
iss = jload(OUT / "issues.json")["issues"]
score = jload(OUT / "score.json")
k04 = jload(OUT / "_analiz" / "k04-karsilastirma.json")
va = jload(OUT / "validation-audit.json")
inv = jload(OUT / "dosya-envanteri.json")
u1 = jload(OUT / "url-checks.json")["summary"]
u2 = jload(OUT / "url-checks-sehir-sayfa.json")["summary"]
cs = jload(OUT / "claim-script.json")["summary"]

# ---- K04 kaydi: son envanter karsilastirmasindan
ok04 = k04["identical"] and not (k04["added"] or k04["removed"] or k04["changed"])
for rec in cr["checks"]:
    if rec["check_id"] == "K04":
        rec["durum"] = "geçti" if ok04 else "kaldı"
        rec["incelenen_kapsam"] = (f"Başta {k04['start_files']}, sonda {k04['end_files']} dosya; eklenen {len(k04['added'])}, silinen "
                                   f"{len(k04['removed'])}, değişen {len(k04['changed'])}; SHA listesi özeti {k04['start_list_digest']} / "
                                   f"{k04['end_list_digest']}; Excel SHA {k04['xlsx_sha_start']} → {k04['xlsx_sha_end']}. Son envanter "
                                   "tüm paket okumalarından sonra alındı.")
        if not ok04:
            rec["sınır_gerekçe"] = "SHA listeleri farklı: denetim geçersiz, baştan yapılmalı (SKILL kural 3)."
cr["meta"]["status_counts"] = dict(Counter(r["durum"] for r in cr["checks"]))
(OUT / "check-results.json").write_text(json.dumps(cr, ensure_ascii=False, indent=1), encoding="utf-8")
if not ok04:
    raise SystemExit("K04 KALDI: paket denetim sırasında değişti; rapor yazılmadı")

by = {r["check_id"]: r for r in cr["checks"]}
sc = cr["meta"]["status_counts"]
counts, minimum, target = va["structure"]["counts"], va["structure"]["minimum"], va["structure"]["target"]
p = {k: score["open_findings"][k] for k in ("P0", "P1", "P2")}
url_total = u1["unique_urls"] + u2["unique_urls"]
url_200 = u1["classes"]["ok_200"] + u2["classes"]["ok_200"]
url_3xx = u1["classes"]["redirect_ok"] + u2["classes"]["redirect_ok"]
url_bad = sum(u1["classes"][k] + u2["classes"][k] for k in ("not_found_404", "gone_410", "soft_404"))
url_other = sum(u1["classes"][k] + u2["classes"][k] for k in ("forbidden_403", "rate_limited_429", "server_5xx", "other_4xx",
                                                              "other_status", "intercepted"))
url_unc = sum(u1["classes"][k] + u2["classes"][k] for k in ("network_error", "not_tested", "invalid_url"))
xlsx_sha = cr["meta"]["xlsx_sha256"]
cov = score["coverage"]

first = (f"Editoryal hazır olma: %{score['editorial_percent']} | Denetim kapsamı: L0, yerel paket denetimi, doğrulanan alt sınır "
         f"(kısmi denetim); editoryal/görsel inceleme kart {cov['cards']['reviewed']}/{cov['cards']['total']}, fotoğraf "
         f"{cov['photos']['reviewed']}/{cov['photos']['total']}, kritik iddia {cov['critical_claims']['reviewed']}/{cov['critical_claims']['total']}; "
         f"script kapsamı {inv['totals']['files']}/{inv['totals']['files']} dosya, 2069/2069 satır, {url_total}/{url_total} URL | "
         f"Karar: {score['decision']} (açık P1: {', '.join(p['P1'])}; {score['decision_note']})")


def ids(status, exec_filter=None):
    return [r["check_id"] for r in cr["checks"] if r["durum"] == status]


def issue_line(i):
    return (f"- **{i['issue_id']} · {i['öncelik']} · {i['check_id']} · {i['kategori']}** — {i['tablo']} "
            f"(satır: {i['Excel_satırı'] if len(i['Excel_satırı']) < 120 else i['Excel_satırı'][:117] + '…'}); alan `{i['alan']}`. "
            f"Mevcut: {i['mevcut_değer'] if len(i['mevcut_değer']) < 220 else i['mevcut_değer'][:217] + '…'} Beklenen: {i['beklenen']} "
            f"Kanıt: {i['kanıt']}. Düzeltme: {i['önerilen_düzeltme']} Yeniden kontrol: {i['tekrar_kontrol_koşulu']}")


L = []
L.append(first)
L.append(f"Teknik/panel ilerlemesi: ölçülmedi (panel/UAT erişimi yok; bu yerel paket denetimidir) | Açık P0: {len(p['P0'])} | "
         f"Açık P1: {len(p['P1'])} ({', '.join(p['P1'])}) | P2 öneri: {len(p['P2'])} ({', '.join(p['P2'])})")
L.append(f"İncelenen paket: CITY-039 / eindhoven / Excel SHA-256 {xlsx_sha} / {cr['meta']['checked_on']} / v001")
L.append("")
L.append("> **Bu bir yayın onayı değildir.** L0 yalnız script kontrolüdür: LLM iddia denetimi ve görsel inceleme yapılmadı. "
         f"%{score['editorial_percent']} içerik kalitesi tahmini değil, script ile doğrulanabilen **alt sınırdır** (ham toplam "
         f"{score['raw_total']}/100; puanın tamamı E kategorisinden). Kontrol edilmeyen kısım başarısız sayılmaz, ama puan da almaz.")
L.append("")
L.append("## 1. Paket, şema ve tarih")
L.append(f"- Excel: `CITY-039_eindhoven_v001.xlsx` · {next(f['size'] for f in inv['files'] if f['path'].endswith('.xlsx')):,} bayt · "
         f"değiştirilme {XLSX_MTIME} · SHA-256 `{xlsx_sha}`".replace(",", "."))
L.append(f"- Şema: schema_version {va['structure']['schema_version']}; acceptance_version {va['structure']['acceptance_version']}; medya şeması "
         f"{va['media']['schema']}; 16 veri sekmesi (eksik 0).")
L.append(f"- Paket: {inv['totals']['files']} dosya, {inv['totals']['total_mb']} MB — kök 1 XLSX; Fotoğraflar 209; Lisans kanıtları 351; Teslimler 211.")
L.append(f"- Sabitleme (K04): başta ve sonda {k04['end_files']} dosya; eklenen/silinen/değişen 0; SHA listesi özeti `{k04['end_list_digest']}` "
         "her iki uçta aynı. Pakete hiçbir şey yazılmadı (validate_all yalnız `--mode audit`; check_delivery.py çalıştırılmadı).")
L.append(f"- Denetim tarihi {cr['meta']['checked_on']}; kademe L0; bağımsız denetçi; üretim notları (manifest, ACIK_KONULAR yorumları) kanıt sayılmadı.")
L.append("")
L.append("## 2. Berlin minimum – hedef – fiilî matrisi")
L.append("")
L.append("| Ölçü | Alt sınır | Hedef | Fiilî (ham/tekil) | Kullanılabilir (editoryal) | Sonuç |")
L.append("|---|---|---|---|---|---|")
names = {"answers": "Pratik yanıt", "places": "Gerçek mekân", "neighborhoods": "Mahalle", "topics": "Dolu konu",
         "photos": "Tekil mekân fotoğrafı", "hero_photos": "Farklı kapak", "routes": "Rota", "glossary": "Sözlük"}
gap_issue = {"places": "ISS-001", "photos": "ISS-002"}
for k, label in names.items():
    ok = counts[k] >= target[k]
    res = "hedef ✓" if ok else f"hedef ✗ ({counts[k] - target[k]}) → {gap_issue.get(k, '')}"
    L.append(f"| {label} | {minimum[k]} | {target[k]} | {counts[k]} | ölçülmedi (L0) | {res} |")
L.append("")
L.append("Fotoğraf kapsamı: fotoğraflı mekân **44/104**, fotoğraflı mahalle **14/16** (ISS-003). Fotoğraf satırı 209 = 201 tekil mekân "
         "karesi + 8 kapak (kapaklar mekân kareleriyle aynı dosya; rol ayrı, kare tek sayıldı).")
L.append("")
L.append("## 3. Kapsam matrisi")
L.append("")
L.append("| Alan | Script (L0) | Editoryal / görsel |")
L.append("|---|---|---|")
L.append("| Tablo kayıtları | 2069/2069 satır, 16/16 sekme | kart 0/409 |")
L.append(f"| Fotoğrafların gerçek baytları | {inv['summary']['images']}/{inv['summary']['images']} görsel dosya (209 JPEG + 201 WebP) çözüldü, SHA eşleşti | — |")
L.append("| Fotoğrafların görsel eşleşmesi | paftalar üretildi (7 pafta, 30'lu), bakılmadı | 0/209 |")
L.append("| Kaynak / hak zinciri | yapısal zincir 209/209 (dosya, hash, lisans etiketi-URL) | tamamlanan 0/209 (rights_status 209 'Bekliyor') |")
L.append(f"| Kritik / değişken iddialar | {cs['claims']} envanter; {cs['by_result']['supported']} dize eşleşmesi (doğrulama değil) | resmî kaynakta doğrulanan 0/{cs['claims']} |")
L.append(f"| Benzersiz URL'ler | {url_total}/{url_total} test edildi: 200 = {url_200}; 3xx→200 = {url_3xx}; 404/410/soft-404 = {url_bad}; "
         f"diğer = {url_other}; belirsiz = {url_unc} | anlamsal hedef 0/{url_total} |")
L.append("| Zorunlu sayfa alanları | 23/23 (yapı, tür, referans) | — |")
L.append("| Önizleme senaryoları | separate_stage | — |")
L.append("| İnsan paket kararı | yok, bekliyor (Teslimat.reviewer boş; editorial_status 'Taslak'; 627 insan alanı 'Bekliyor'); sürüm v001 | — |")
L.append("")
L.append(f"CHECK durumları (120): geçti {sc.get('geçti', 0)}, kısmi {sc.get('kısmi', 0)}, kaldı {sc.get('kaldı', 0)}, not_checked "
         f"{sc.get('not_checked', 0)}, uygulanmaz {sc.get('uygulanmaz', 0)}, separate_stage {sc.get('separate_stage', 0)}. "
         "Ayrıntı: `check-results.json`; puan tablosu: `score.md`.")
L.append("")
L.append("## 4. Öncelikli bulgular")
L.append("")
for pr in ("P0", "P1", "P2"):
    group = [i for i in iss if i["öncelik"] == pr]
    L.append(f"**{pr}** ({len(group)})" + ("" if group else ": yok"))
    L.append("")
    if group:
        L.extend(issue_line(i) for i in group)
        L.append("")
L.append("ISS-003'ün 62 kaydının tam listesi (entry_id ve satır) `issues.json` içindedir.")
L.append("")
L.append("## 5. Yanlış görseller (pafta / slot)")
L.append("")
L.append("L0'da paftalara bakılmadı; yanlış görsel tespiti yapılmadı (K59–K62 not_checked). Paftalar: `temas-sayfalari/sheet_01–07.jpg`. "
         "Yalnız script sinyalleri (karar değil, L1 için):")
L.append("- 8 kapak = mekân karesiyle aynı dosya (dHash mesafe 0): kapak-01…08 → sheet_07 slot 22–29; eşleri: 18-septemberplein-02 "
         "(sheet_05/3), klokgebouw-03 (sheet_04/15), van-abbemuseum-03 (sheet_01/3), henri-dunantpark-01 (sheet_03/9), huize-de-laak-01 "
         "(sheet_05/10), philips-stadion-psv-02 (sheet_02/17), eindhoven-centraal-01 (sheet_05/7), strijp-s-01 (sheet_04/8).")
L.append("- Fotoğraflar!60 `de-ontdekfabriek-02` (sheet_03/17): kaynak dosya adı 'Netherlands_Office_Philips_Eindhoven_Building.jpg', "
         "Pixabay kökenli CC0 — hedef yer ve köken L1'de bakılmalı.")
L.append("")
L.append("## 6. İddia düzeltmeleri ve resmî kaynak")
L.append("")
L.append("L0'da iddia denetimi yapılmadı (K29, K34, K35, K37, K40, K41 not_checked); düzeltme önerisi yok. L1 girdisi olarak script sinyalleri "
         f"({cs['by_result']['not_in_source']} 'not_in_source'):")
L.append("- 13 × '22 Ekim 2026' — IND ücret kartlarının cost alanındaki okuma tarihi notu (kaynakta beklenmez; içerik iddiası değil).")
L.append("- 4 × '9 hafta' — `ebeveyn-izni-ve-evlat-edinme-izni` (summary/steps/timing/cost); kaynakta rakamla bulunamadı.")
L.append("- 4 × DDW bilet fiyatı (84,50 / 104 / 91 euro) — `ddw-genc-ogrenci-aile-bileti`; kaynak snapshot'ında yok.")
L.append("- 2 × '401 saatte' — `eindhoven-havalimani-toplu-tasima`; büyük olasılıkla otobüs hattı numarası ayrıştırması (yanlış pozitif adayı).")
L.append("- Paketin `ACIK_KONULAR.txt` dosyası 4 açık P1 beyan ediyor (IND/SVB kaynak erişimi ve yorum); bağımsız denetimde kanıt sayılmadı, L1'de sınanmalı.")
L.append("")
L.append("## 7. Bağlantı ve teknik hatalar (kök nedene göre)")
L.append("")
L.append(f"- Kırık bağlantı: {url_bad}/{url_total}.")
L.append("- Geçici ağ hatası (1): rotterdam-bk.mfa.gov.tr/Mission/ShowInfoNote/417062 TLS el sıkışma zaman aşımı (Bağlantılar!492, Kaynaklar!62); "
         "yeniden denemede 200.")
L.append("- Alan adı taşınmış, çalışıyor (P2 bakım önerisi): consuwijzer.nl → consument.acm.nl (4 URL; Bağlantılar!91, !93, !99, !100, !101; "
         "Kaynaklar!85, !86, !87, !224); arnohuibers.nl → clownarno.nl (Bağlantılar!256, Kaynaklar!284); ijssportcentrum.nl/contact/ → "
         "ijssportcentrumeindhoven.sportfondsen.nl/ — iletişim sayfası yerine anasayfa (Bağlantılar!260, Kaynaklar!288).")
L.append("- Yalnız anasayfa kaynak (L1'de K51/K53): delichttoren.nl (Kaynaklar!354), marienhage.com (!355), hartvaneindhoven.nl (!356); "
         "knmi.nl sağlayıcı (Şehir!8). defabriekeindhoven.com/en/home → /en (anasayfadan anasayfaya, sorun değil).")
L.append("- Dosya yolu: web_file Windows '\\' ayırıcısı — tek kök neden, 209 Excel satırı + photo-provenance-v7.json + atıf CSV (ISS-004).")
L.append("- Teslim metaverisi: Teslimat satırı şablondan (ISS-006), teslim özeti/ilerleme kaydı son paketten önce üretilmiş (ISS-005).")
L.append("")
L.append("## 8. Düzeltme sırası")
L.append("")
L.append("1. **ISS-004** — web_file yollarını '/' ile yaz; photo-provenance-v7.json ve atıf CSV'sini yeniden üret. Kontrol: '\\' = 0, POSIX'te validate_all medya hatası 0.")
L.append("2. **ISS-003 + ISS-002** — fotoğrafsız 60 mekân + 2 mahalleye gerçek, ücretsiz-ticari lisanslı kare ekle (49 karelik açığı da kapatır). "
         "Kontrol: 'fotoğraf eksik' uyarısı 0; counts.photos ≥ 250.")
L.append("3. **ISS-001** — az dolu gruplara 16+ gerçek mekân ekle (yeni mekânlara fotoğrafla). Kontrol: counts.places ≥ 120.")
L.append("4. **ISS-007** — Yanıtlar!194 opstal zorunluluğunu resmî kaynakla çöz, iç notu kaldır.")
L.append("5. **ISS-006, ISS-005** — Teslimat satırını ve teslim özetlerini son paket durumundan yeniden üret.")
L.append("6. Yeni sürümle L0'ı yeniden çalıştır (yeni SHA), ardından **L1** (iddia denetçisi + tüm paftaların görsel incelemesi). "
         "L/V kontrolleri yapılmadan karar en iyi durumda 'KARAR İÇİN KANIT EKSİK' kalır.")
L.append("")
L.append("## 9. Çalıştırılmayan / tamamlanamayan kontroller")
L.append("")
nc = [r for r in cr["checks"] if r["durum"] == "not_checked"]
L.append(f"- **not_checked ({len(nc)})** — L (LLM+kaynak): " + ", ".join(r["check_id"] for r in nc if "exec L" in r["sınır_gerekçe"]) +
         "; V (görsel): " + ", ".join(r["check_id"] for r in nc if "exec V" in r["sınır_gerekçe"]) +
         "; script verisi yok: K64, K67, K107 (photo_candidates from-evidence 0 aday — paket `Lisans kanıtları/*.source-evidence.json` "
         "içermiyor, kanıt Excel Kanıtlar sekmesinde); script yok: K73, K81.")
L.append("- **separate_stage (10)** — Drive: K01, K03, K109, K110; önizleme: K92, K93, K94, K103, K111, K112.")
L.append("- **kısmi (13)** — " + ", ".join(r["check_id"] for r in cr["checks"] if r["durum"] == "kısmi") + " (eksik kısım her kaydın sınır_gerekçe alanında).")
L.append("- **uygulanmaz (3)** — K36 (D7/D8 yalnız Portekiz), K99 ve K118 (önceki denetim yok).")
L.append("- Karara etkisi: A–D kategorilerinin tamamı ölçülmedi (0 puan, 'kontrol edilemedi'/'kısmi'); yüzde yalnız E kategorisinden. "
         "Script'in kesin gösterdiği 4 P1 nedeniyle karar DÜZELTME GEREKLİ; bunlar kapansa bile L0'da karar en iyi durumda KANIT EKSİK olur.")
L.append("")
L.append("## 10. Denetim çıktıları")
L.append("")
L.append("`check-results.json` · `issues.json` · `criteria.json` · `score.json` / `score.md` · `url-checks.json` (Kaynaklar+Bağlantılar) · "
         "`url-checks-sehir-sayfa.json` (Şehir+SayfaAlanları) · `dosya-envanteri.json` / `_dosya-envanteri-son.json` · `validation-audit.json` · "
         "`text-quality.json` · `xlsx-fidelity.json` · `claims.jsonl` / `claim-script.json` · `kanitlar/snap/` (352 taze snapshot) · "
         "`_dump/` · `_foto/` (candidates 0, plan, decisions, items) · `temas-sayfalari/` (7 pafta, dhash.json) · `_render/` (bağımsız "
         "teslim özeti yeniden hesabı) · `_analiz/` (çapraz kontroller, K04, snapshot karşılaştırması, betikler) · `_cache/`.")
L.append("")
L.append("Not (SKILL'e ek, paket dışı): url_check `--retry-transient` ile iki kez çalıştı (ikinci geçiş geçici hatayı yeniden denedi); "
         "Şehir+SayfaAlanları için ayrı url_check; KAPSAM eşlemesi için xlsx_fidelity (girdi şablonu ekler_eindhoven/CITY-039_eindhoven_v001.xlsx) "
         "ve render_summary (`_render/`); kaynak snapshot'larının taze indirmeyle karşılaştırması `_analiz/` altında. "
         "KAPSAM 'Kismi' varsayılanından sapmalar: K04, K05, K16 'geçti' (eksik kısım bu denetimde tamamlandı: K04 baş/son SHA "
         "karşılaştırması, K05 çoklu Excel kontrolü envanterden, K16 EkDetaylar 0 satır); K82 'kaldı' (bulgu var); K64, K67, K107 "
         "'not_checked' (aday verisi yok).")
(OUT / "DENETIM_OZETI.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print(first)
