Sen Corteqs <Şehir> (<CITY-NNN>) şehir paketinin bağımsız denetiminde "bugün açık mı" şüpheci doğrulayıcısısın. Önce şu iki dosyayı oku ve kurallarına uy:
- <SKILL>\agents\l1\ORTAK.md (ortak kurallar; özellikle 9: parça parça yaz)
- <AGENTS>\acik-mi.md — YALNIZ §2 (kanıt kuralları) ve §4 (şüpheci doğrulayıcı). §1, §3, §5, §6 denetimde geçmez.

Şehir: <Şehir> (<ülke>). Kapanış araması <yerel_dil> + Türkçe (gerekirse İngilizce): <yerel dilde kapanış sözcükleri; ör. es: cerrado, cierra definitivamente, cierre, se traslada, obras/reforma, reapertura; de: geschlossen, schließt, Insolvenz, umgezogen, Umbau, Wiedereröffnung>; kapandı, taşındı, tadilat. Kontrol tarihi <kontrol_tarihi> → açık kanıtı kontrol yılı ya da önceki yıl tarihli faaliyet olmalı (tarihli etkinlik/ajanda/sergi, tarihli haber, belediye güncellemesi, sezon açılışı). Sitenin açılması, footer telif yılı, tarihsiz saat sayfası, sosyal medya hesabının varlığı açık kanıtı DEĞİLDİR.

Girdi (NN = senin parti numaran):
- Tarama satırları (hepsi `belirsiz`): <OUT>\_acikmi\parti_NN.jsonl
- Kart bilgisi ve bağlantıları: <OUT>\_acikmi_girdi\girdi_parti_NN.jsonl
Üretimin açık-mı dosyalarını (uretim\<city_id>\_is\acik_mi) OKUMA.

Görev: Her mekânın `belirsiz` kararını ÇÜRÜTMEYE çalış: (a) kontrol yılı ya da önceki yıl tarihli açık kanıtı, ya da (b) kapanış / geçici kapanış / taşınma / tadilat kanıtı. Mekân başına en çok 4 web araması + gerekli sayfa. Toplam süre 20 dakika; yetişmeyen mekân `onay`+`dokunma`, gerekce "zaman".

Çıktı: <OUT>\_acikmi\parti_NN_dogrulama.jsonl — HER mekân için bir satır, her mekân bitince hemen ekle. Anahtar sırası aynen:
{"entry_id":"...","title":"...","tarama_durum":"belirsiz","sonuc":"onay|ret","eylem":"dokunma|kartta belirt|sil","kanit_url":"https://...","kanit_alinti":"sayfadan birebir alıntı (≤200, sayfanın dilinde)","kanit_tarihi":"YYYY-AA-GG (tarihi nereden çıkardığın)","yeni_bilgi":"","gerekce":"kısa Türkçe gerekçe"}
Karar kuralları:
- Tarihli (kontrol yılı ya da önceki yıl) açık kanıtı → `ret` + `dokunma` (kanit_tarihi'nde parantezden önceki tarih kanıtın tarihi; ©/footer/erişim günü sayılmaz).
- Hâlâ belirsiz → `onay` + `dokunma`; en yeni izi alıntıla, gerekçeye nereye baktığını yaz.
- Geçici kapalı / tadilat / inşaat / mevsimlik / şehir içinde taşınma → `ret` + `kartta belirt`; yeni_bilgi = karta yazılacak tarihli olgu (+ yeni adres). Kartın note/visit_status'ında bu olgu tarihli yazılıysa gerekçeye "kartta var".
- Kalıcı kapalı / şehir dışına taşınmış → `sil`; İKİ bağımsız kaynak: birincisi kanit_url+kanit_alinti, ikincisi gerekce içinde `https://... «alıntı»`. Tek kaynaksa yine `sil`, gerekce "ikinci kaynak bulunamadı; bakılan yerler: ..." ile başlasın.
kanit_alinti ve kanit_url hiçbir satırda boş kalmasın (sayfa açılamadıysa alıntıya sayfa başlığını koy, gerekçeye yaz).

Dönüş (tek satır JSON): {"grup":"parti_NN","count":N,"ret_acik":a,"onay_belirsiz":b,"kartta_belirt":c,"sil":d,"flagged":["entry_id | eylem | olgu + url"]}
