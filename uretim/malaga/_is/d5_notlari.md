# Son tam denetim (d5) editörlerine taşınacak notlar

- oturum: NIE ve TIE kartlarında harç tutarı yok (K26 "ne öder"). Tutarlar malaga:kaynak:004'te (NIE 9,84; ilk TIE 16,08; TIE yenileme 19,30 euro — editör kaynaktan birebir doğrulasın). Kart başına 2 source_ids sınırı yüzünden eklenemedi: kartın zayıf kaynağı 004 ile değiştirilerek (değiştir-boşalt) eklenecek.
- Kaynaklar sekmesi araştırma notlarında okura iş bırakan ifade (warning-scan K104): malaga:kaynak:209, 216, 275 `summary`. Ana döngü teslimden önce kaynak_taslak notlarını düzeltecek.
- Ana döngü notu: toolkit script'leri `-I` ile çağrılmaz (common modülü yola girmez); `-X utf8` yeter.
- gunluk: spor tesisleri kartında 3 source_ids (doğrulama turu kaynak 243'ü ekledi) — kural 20 sınırı 2; zayıf kaynak çıkarılacak ya da OMAC bilgisi OMAC kartına bırakılacak.
- gunluk: Campanillas OMAC adresi kaynak 428'in 2. sayfasında olabilir (pageNum=2); kartta Campanillas yok.
- aile: dogan-bebegin-registro-civil kartında Málaga Registro Civil ofis adresi/telefonu yok (K26 nereye); bilgi malaga-registro-civil-ofisi kartında var — değiştir-boşalt ile kaynak eklenebilir.
- aile: okul başvuru dönemi Junta sayfalarında çelişkili (takvim 1 Mart–7 Nisan; SSS 1–31 Mart) — kartlarda atıfla yazıldı; tutarlılık turunda tek dil.
- aile + gunluk: doğrulayıcının hafif hatali_duzeltme/eksik_kalan satırları doğrulama turunun kapsamı dışında kaldı (aile 11, gunluk 2) — d5 denetimi yeniden bakacak.
