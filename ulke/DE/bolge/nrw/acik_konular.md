# NRW (Nordrhein-Westfalen) bölge paketi v1 — açık konular (2026-11-02)

Kapsam: 14 kart, 6 konu (gunluk 2, aile 4, saglik 2, para 1, ev 4, resmi 1), 273 iddia, 21 kaynak (de-nw:kaynak:NNN), 3 tarihli kart. Süreç: erişim yoklaması (18 adres, hepsi açık; mik.nrw.de TLS) → keşif (2 ajan, 25 aday kaynağın 25'i `add_sources`'ta kabul) → yazar (2) → `pack_check` → bağımsız denetim (2; 1 ciddi / 13 orta / 27 küçük) → editör (2) → editör sonrası dar denetim (1; 0 ciddi / 3 orta / 10 küçük) → dar düzeltme (script, `_is\dar_duzelt.py`) → `pack_check` 6/6 temiz → `pack_build --region nrw` → `pack_merge` (DE v2 + NRW v1: 127 kart, 0 çakışma).
Denetim dosyaları: `_is\denetim\` (denetim_A/B, dar_denetim, editor_farki, degisiklik_A/B/dar). Kart başı karar dosyası (`*_karar.jsonl`) üretilmedi: iddia defterinde bu kartlar ulusal paketteki gibi "denetlenmemiş" görünebilir.
Ölçüm: 18:15–19:35 (1 sa 20 dk), 0,55 M çıktı, 2,77 M önbellek dışı girdi, 9 Sonnet ajanı. `_is\phase_usage.csv`, `_is\phase_log.jsonl`.
Kural: şehir yazarı bu boşlukları kendi bilgisinden doldurmaz; kaynaklı şehir kartı yazar.

## Klasör adı
Paket `ulke\DE\bolge\nrw` (kısa ad). Şehir skill'i bölgeyi `bolge\<bölge_slug>` diye arar; NRW şehri için doğru yol bu klasördür (`ulke\DE\bolge\BOLGELER.md`). NRW şehirleri: Aachen, Bielefeld, Bochum, Bonn, Dortmund, Duisburg, Düsseldorf, Essen, Köln.

## Tarihe duyarlı kartlar (valid_until)
- 2027-07-31: nrw-kita-ucreti-jugendamt-ve-ucretsiz-donem (KiBiz 01.08.2026 sürümü; 01.08.2027 sürümü recht.nrw.de'de listeli, o tarihte yenile)
- 2028-04-22: nrw-okul-tatilleri-2026-27-ve-2027-28
- 2029-12-31: nrw-kira-tavani-ve-kira-artis-siniri-mieterschutzverordnung (yönetmelik §3)
- Tarihsiz ama yıl bağımlı: nrw-wbs-gelir-siniri-2025-ve-basvuru (EEWo NRW, 1.1.2025'ten beri tutarlar; yeni tutar yayımlanınca yenile), kilise vergisi %9 ve 30 Euro çıkış ücreti (sayfalar tarihsiz, "güncel tarife").

## Şehir katmanına giden konular
- Kira tavanı: yönetmelik ekindeki (Anlage) belediye listesi; {sehir} listede mi → şehir yazarı yönetmelik ekinden yazar.
- Açık pazar günleri (verkaufsoffener Sonntag) ve Kurort istisnası (yıl 40 gün): belediye yönetmeliği.
- Kita: Jugendamt'ın ücret tablosu ve kardeş indirimi, Kita portalı ve kayıt yolu.
- WBS: başvuru yeri (Wohnungsamt/Sozialamt), çevrim içi başvuru, ücret.
- HSU (Türkçe anadil dersi): başvuru formu ve süresi, dersin verildiği okullar (Schulamt / Bezirksregierung; Detmold sayfası şehir adı içerdiği için alınmadı).
- Okul kaydı takvimi (Grundschule Anmeldung), Schulamt adresi.

## Kaynak sınırı ya da kaynak yokluğu yüzünden yazılmayanlar
- Tatil kartı: 2026/2027 tarihleri (Feiertagsgesetz NRW yalnız günleri sayar; hareketli günlerin tarihi kaynakta yok). v2 aday: resmî yıllık tatil listesi (im.nrw ya da land.nrw) ile tarihli kart.
- Itiraz kartı (JustG NRW §110): sosyal mahkeme (Jobcenter, emeklilik; SGG §78) ve mali mahkeme (Finanzamt Einspruch; AO §347) yollarında itirazın sürdüğü karta yazılmadı (2 kaynak sınırı; kart yalnız idare mahkemesi yoluyla sınırlandı). Dava süresi (VwGO §74) ulusal kartta. v2 aday: "Jobcenter ve Finanzamt kararına itiraz NRW'de de var" ayrı kartı.
- Kira tavanı: %10 ve %15 için BGB §556d/§558 ve istisnalar (§556e/f) eklenmedi; rakamlar land.nrw basın bildirisinden (29.01.2025) tarihle.
- Duman dedektörü: ilk kurulumu kimin yaptığı yalnız 2012 basın bildirisinde; BauO NRW §47'de yok, yazılmadı.
- WBS: geçerlilik süresi ve ücret tutarı; "außereuropäisches Ausland" kuralının Türkiye için anlamı (WFNG NRW §18 listede yok).
- Kilise vergisi: verginin çıkış ayının sonunda bitmesi (KiStG; 2 kaynak sınırı); noter onaylı beyan ücreti.
- Okul sistemi: Vollzeitschulpflicht süresi (SchulG §37) ve kayıt takvimi.
- Okul giriş muayenesi: kapsamı ve çağrı zamanı.
- Ayrıntı: `_is\gaps_toplu.md` (keşif ve yazar/editör gaps dosyaları birleşik).

## Dar denetimde uygulanmayan küçük bulgular
- WBS "Avrupa dışı" için "Wohnungsamt'a sor" önerisi: havale cümlesi olurdu, uygulanmadı (yukarıda açık konu).
- Itiraz kuralının federal makam işlemlerine uygulanıp uygulanmadığı: kaynakta yok, dokunulmadı.
