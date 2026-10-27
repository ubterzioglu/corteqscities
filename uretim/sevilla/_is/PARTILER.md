# Sevilla d3 kalan işler — minik partiler (26.10.2026, oturum 26a5348e)

Devir: `belgeler\devir\DEVIR_2026-10-26_sevilla_d3_ve_skill.md`. Bu dosya o belgenin "Kaldığı yer" listesinin parti durumudur.

| Parti | İş | Durum |
|---|---|---|
| 0 | Eski geçici klasörden araçlar ve bulgular → `_is\d3_arac\` | bitti |
| 1 | Kaynaklar 504 → 500: 8 kaynak yalnız buton adresiydi; 5 buton çıktı (`denetim\kapasite-d3_degisiklik.jsonl`); KUR temiz (`kur_d3.ps1`, `kur_d3.log`) | bitti |
| 2 | Fibes fotoğrafı (`foto_d3b\`): 346 foto, 136/136 kayıt fotoğraflı. Ara Excel'e bir sonraki KUR'la girer | bitti (KUR bekliyor) |
| 3 | İspanya denetim sonuçları → `ulke\ES\_is\denetim\<kart>-d2/d3/d4_{iddia,karar}.jsonl` (32 dosya; son tur 7/7 temiz) | bitti |
| 4a/4b/4d | 64 bulgu: kartlar 16 / mekânlar 22 / mahalleler 12 → 3 Sonnet editör (`d3_arac\parti4_ortak.md`, `bulgu_4X.json`) | çalışıyor |
| 4c | Rotalar 14 bulgu; 4b bitince (portal kaynakları rotalardan da çıkar). Girdi: `_is\rota_mesafe.jsonl` (40 bacak, OSM yaya) | bekliyor |
| 5 | `gorsel_kalite --flag-ratios` (varsayılan 16:9,4:3): 116 işaret; 98'i dikey kare. kapak-01 + plaza-de-espana-01 → "Plaza de España (Sevilla) - 01" (`foto_d3b\kapak01.py`) | bitti (karar: dikey kareler önizlemede) |
| 6 | `kanit_teslim.py`, `rota_mesafe.py` (yeni); `kanit_kapsami` 3 hata (photos/rows, paket-kontrol, provenance listesi) + `--pkg` dest; `iddia_defteri` term_id/route_id sahipli iddiaları düşürüyordu (B4 0/60'ın nedeni); skill: deliver, places (rota bacakları, mekân doğrulama), foto `ek_hak`, iddia-denetçisi md 9, yer-yazarı Sözlük, city-audit L0 | 2. tam test koşuyor |
| 4a/4b | bitti (4a 12 uygulandı/4 ret; 4b 19 uygulandı, 3 rotaya, 2 koordinat açık; kaynak 574, 575 eklendi, 540 ve 390 boşaldı → 390 rotadan çıkınca 500). 4d takıldı, durduruldu → WF1 mahalle ön düzeltmesi; 4c → WF2 rota ön düzeltmesi | |
| 5b | Dikey kare değişimi: 112 işaretli, 61'i yatay yedekle değişti (`foto_dikey\uygula.py`, `karar.jsonl`); 346 foto | bitti |
| 7-WF | WF1 `wf_1c5f9706-360` (12 konu + sözlük + mahalle; planlama başında danışma kartı), WF2 `wf_93b6e601-208` (5 mekân birimi + rota), WF3 `wf_65161031-ca7` (foto denetimi → `foto\inceleme\denetim_<n>[b].jsonl`) | çalışıyor |
| 7 | Tam son denetim (onaylı): girdi `d3_arac\d5_hazirla.py --yaz` → `denetim\<parça>-d5_kartlar.jsonl` (448 kayıt, 5.855 defter satırı). Plan: 12 kart + 4 mekân + 1 mahalle + 1 rota + 1 sözlük denetçisi, dalga başına ≤5; foto `ek_hak` ana döngüde (12 pafta) | bekliyor (maliyet sorusu) |
| 8 | Teslim zinciri (yeni deliver: gorsel_kalite → kanit_teslim → … → kanit_kapsami) → manifest_check | bekliyor |
