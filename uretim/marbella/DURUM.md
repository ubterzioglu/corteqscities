# Marbella (CITY-080) — nerede kaldı (devir notu)

Yazıldı: 2 Kasım 2026. Üretim oturumu: bulut (claude.ai/code), `session_01CvxEJ9YWLNBW8jDmXMD3RF`; 28–29 Ekim 2026'da çalıştı, 29 Ekim'de haftalık kullanım limiti dolunca durdu. Bütün iş GitHub'da **`marbella-uretim`** dalında (main'e birleştirilmedi).

## Kısaca
- **Bitti:** intake, sources, answers. Places fazının neredeyse tamamı.
- **Yarıda:** places fazının son adımı. m3 mekân parçasının (21 mekân) **editör turu** çalışmadı: denetim, çürütme ve mekân doğrulama dosyaları hazır, bulgular uygulanmadı.
- **Başlanmadı:** photos, assemble, deliver.
- Manifest: `phase: places`, `places: running`. `manifest_check` en son temizdi.

## Yeni oturumda ilk iş
1. Dalı al: `git fetch origin marbella-uretim` ve `git checkout marbella-uretim` (ya da `git pull`).
2. **Ortam:** Bu oturum Linux'taydı (`ROOT=/home/user/corteqscities`, `PY=/home/user/venv/bin/python`), PowerShell yoktu. Komutlar `_is/ortam.sh` ve `_is/kur.sh` ile çalıştı. Windows'ta `_is/ortam.ps1` hazır (aşağıda); `manifest.json` içindeki `paths.*` ve `country_pack.path` Linux yolu: Windows'ta çalışılacaksa ROOT'a göre çevrilmeli (`/home/user/corteqscities` → `C:\temp_private\corteqs\0000_newera`, `/` → `\`). `kaynak_dizini.jsonl` içindeki `text_file` yolları göreli, değişmez.
3. `manifest_check` → temizse aşağıdaki "Sıradaki adımlar".
4. Bu oturumu `_is/oturumlar.txt`'ye ekle (ilk satır bulut oturumunun kaydı; faz 7 ölçümünde o kayıt bu makinede yok, `run_log` gap verecek: kanıtıyla `open_items`'a yaz).

## Sayılar (2 Kasım 2026, parça dosyalarından)
| | Sayı | Asgari / hedef |
|---|---|---|
| Yanıtlar (kart) | 229 (105 ülke+Endülüs, 124+ Marbella) | 212 / 240 |
| Konular | 12 | 12 |
| Mekânlar | 99 | 92 / 120 |
| Mahalleler | 12 | 12 / 16 |
| Sözlük | 60 | 48 / 60 |
| Rotalar | 12 | 9 / 12 |
| Şehir + SayfaAlanları | 1 + 23 | — |
| Kaynak dizini | 429 (pakette kullanılan ~400) | Kaynaklar sekmesi ≤500 |
| Fotoğraf | 0 | 187 / 250, kapak 6 / 8 |

Mekân grupları: Doğa ve açık hava 33, Tarih ve mimari 27, Spor 9, Çocuklarla keşif 8, Müzeler 8, Sanat 6, Sahne 6, Yeme ve içme 2. Yakın çevre gezisi 17 (Mijas, Estepona, Fuengirola, Juanar; sınır 20). BBOX yakın çevre için genişletildi: `36.40,36.62,-5.18,-4.62`.

En son KUR (mekânlar yazıldıktan sonra): birleştirme ihlali 0, alıntı uyuşmazlığı 0, kurulumda red 0, `validate_all` yapı hatası 0, medya 0, hitap bulgusu 0, warning-scan 0. Mekân editörleri sonrası KUR yeniden çalıştırılmadı.

## Biten fazlar (özet)
- **intake:** Atınç'ın Drive şablonu `ekler/marbella/CITY-080_marbella_v001.xlsx` (delivery_id kopyada küçük harf: OI-002). Ülke + Endülüs paketi uygulandı (105 kart, eskimiş 0). Wikidata QID Q484799, havuz 179 aday (küçük: OI-004).
- **sources:** 4 keşif ajanı, 286 kaynak, her konuda ≥12.
- **answers:** 6 yazar + 12 parça için tam denetim zinciri (denetim → çürütme → editör → ek denetim → doğrulayıcı → doğrulama turu). 134 Marbella kartının hepsi denetlendi. Editörler 5 ülke kartını değiştirdi → assemble d5'te denetlenecek (OI-007).
- **places:** 3 seçim turu (ikinci ve üçüncüsü kullanıcı kararıyla: 80 → 101 mekân), 3 mekân yazarı, mahalle+sözlük, sayfa ve rota yazarı. "Bugün açık mı": 2 tarayıcı + 2 şüpheci doğrulayıcı + uygulama editörü; **kapı `acik_mi.py` çıkış 0**; kalıcı kapanmış mekân yok, 7 karta tarihli not (Casa Consistorial reformda, Castillo iç alanı kapalı, Auditorio kışın kapalı, Carlos Cabezas yeni saha, Represa pump track inşaatı, Torres Vigía merkezi geçici kapalı, San Pedro pazarı yenileme planı). Rota bacakları ölçüldü (`rota_mesafe.jsonl`, 36/36, problem 0).
- **Yer denetimi** (`_is/araclar/yer_zinciri.js` workflow; ucuz yol: çürütme ve doğrulayıcı yalnız ciddi bulguda): mahalle, sözlük, rota, m1, m2 bitti; **m3 editörü çalışmadı.** K108 ile iki mekân silindi: `centro-tecnico-de-alto-rendimiento` (Represa'ya taşındı), `hospital-real-de-la-misericordia` (Capilla de San Juan de Dios ile aynı yapı; rota 007 güncellendi).

## Sıradaki adımlar
1. **m3 editör turu** (yer_zinciri.js'teki `editorIstemi`, parça `m3`, dosyalar `Mekânlar.m3.jsonl`, `Bağlantılar.m3.jsonl`, `Rotalar.rota.jsonl`, `claims/m3.jsonl`). Girdiler hazır: `denetim/m3_iddia.jsonl` (ciddi 1, orta 16, hafif 25), `m3_karar.jsonl` (18 düzelt), `m3_teyit.jsonl` (ciddi bulgu "kısmen"), `m3_mekan-dogrulama.jsonl` (12 "kaldı"). Ciddi bulgu olduğu için ardından doğrulayıcı (+ gerekirse doğrulama turu). m2 doğrulama turunun bıraktığı not: `capilla-de-san-juan-de-dios-marbella` kartına kaynak:272'deki adres/işlev bilgisi eklenmeli (Hospital Real silindi, kapel artık yapının tek kaydı) ve keşif Yanıtlar kartlarında "Hospital Real" geçen metinler bu kayda göre kontrol edilmeli.
2. **Ana döngü kararları (places kapanmadan):**
   - `parque-del-mediterraneo`: K108 teyitli (adresi plaj adı, koordinatı El Pinillo ile aynı) ama rota durağı; ya rotadan çıkarılıp silinir ya El Pinillo kartında anlatılır. Silinirse mekân 98 olur (asgari 92 üstünde).
   - `parque-vigil-de-quinones` ve `polideportivo-paco-cantos` aynı koordinatı paylaşıyor (CartoCiudad yakın portal): resmî adres kaydıyla ayrı koordinat bulunmazsa open_items.
   - Sözlük `term:054 Cercanías`: Marbella'da tren yok; terim kalsın mı karar.
3. **Mekân doğrulama satırları (B5):** editörlerin değiştirdiği mekân ve mahallelerde `*_mekan-dogrulama.jsonl` satırları güncellenmedi ("kaldı" satırları: m1 9, m2 5, mahalle 5, m3 12). `kanit_teslim` her kaydın en az bir "geçti" satırını ister: assemble adım 0'da (d5/d6) değişen kayıtlar yeniden denetlenip `<parça>-d5_mekan-dogrulama.jsonl` yazılmalı.
4. KUR → places kapısı → `manifest` places done → `mark places end` → `manifest_check`.
5. **photos:** Bu bulut oturumunda **Wikimedia 429** verdi (Commons API, `upload.wikimedia.org` dahil; Openverse zaman aşımı) → `foto/search.jsonl` ve `candidates.jsonl` BOŞ. Kendi bilgisayarında (başka çıkış adresi) yeniden çalıştır: `foto/arama.sh` sırası (commons_search → photo_sources `--sources openverse,smithsonian,europeana` → from-search). Önce `photo_candidates.py plan-from-xlsx` yeniden çalışmalı: `foto/venues.jsonl` hâlâ silinen iki mekânı içeriyor, QID ekleme adımı (`mekan/selected.jsonl` → `wikidata`) yeniden yapılır. 15 mekânın koordinatı yok (Wikidata/CartoCiudad'da bulunamadı); fotoğrafsız mekân teslim edilmez (K22): bulunamazsa places yeniden açılır.
6. **assemble:** ucuz yol kararı (OI-009): d5 son tam denetim yalnız yer parçaları, değişen kayıtlar ve 5 ülke kartı (OI-007) üzerinde; yanıt kartları zaten tam denetlendi. Teslim zinciri.
7. **deliver** + RUN_LOG; sonra yeni oturumda `city-audit` ("Marbella paketini denetle").

## Dikkat
- **Tarih:** ülke paketinde 6 kira kartı **5 Kasım 2026**'da, 8 kart 31 Aralık 2026'da eskir. 5 Kasım'dan sonra teslim edilecekse önce o kartların kaynağı yenilenmeli (`country_apply` stale listesi) ya da kartlar şehir yazarına kalır.
- **Maliyet:** intake–answers 82 ajan (hedef ≤60); kullanıcı kalan fazlar için "ucuz yol"u seçti (OI-009). places'ta ~25 ajan daha kullanıldı. Ölçüm: `_is/phase_log.jsonl` (bulut oturumunun kaydı `/root/.claude/projects/...` bu makinede yok).
- **Erişim haritası:** `_is/kesif/KESIF_TALIMAT.md` (sede.marbella.es, malaga.es, hidralia.es, puertobanus.com, museosdeandalucia.es, benahavis.es, ojen.es, istan.es kapalı; hcs.es kopyası gzip bozuk).
- **Açık konular:** `manifest.json` → `open_items` (OI-001 … OI-009). Bilgi eksikleri listesi OI-008'de (şehir otobüsü bileti, su tarifesi, IBI takvimi, nöbetçi eczane yerine CGCOF bulucu kullanıldı vb.).
- **Skill/araç notları:** `_is/notlar_skill.md` (Linux ortamı, Wikidata 429, Atınç delivery_id, hcs.es gzip). Teslimden sonra ayrı geliştirme turu.

## Dosya haritası (yalnız yeni olanlar)
- `_is/ortam.sh`, `_is/ortam.ps1`, `_is/kur.sh` (KUR bloğu, Linux), `_is/foto/arama.sh`
- `_is/araclar/`: `hazirla_denetim.py`, `kartlar_txt.py` (Málaga'dan), `cevap_zinciri.js` (yanıt denetim workflow'u), `yer_zinciri.js` (yer denetim workflow'u; Linux yollarıyla)
- `_is/yazar/`: `YAZAR_GOREV.md`, `YER_GOREV.md`, `donus_*.jsonl`, `<konu>_eksikler.json`
- `_is/mekan/`: `SECIM_GOREV.md`, `secim_{1,2,3}.jsonl`, `selected.jsonl`, `plan_m{1,2,3}.jsonl`, `mevcut_secim.txt`
- `_is/acik_mi/`: tarama ve doğrulama dosyaları; `_is/acik_mi_rapor.json` (çıkış 0)
- `_is/denetim/`: bütün denetim turları; `kur-ana_degisiklik.jsonl` (ana döngünün küçük düzeltmeleri: 3 K104 cümlesi, pharmacy_url, kaynak:380 yayıncısı)
