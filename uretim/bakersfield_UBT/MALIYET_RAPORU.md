# Bakersfield (CITY-901): maliyet raporu, 23.10.2026

**Sonuç:** Bu şehir için hedeflenenden çok daha fazla token harcandı. Sorumlusu Claude (bu oturumdaki asistan); kullanıcı talimatı değildi.

## Ne oldu
- Yaklaşık 100 alt ajan çalıştı. Kabaca 40 milyon token üstü harcandı (ajan raporlarındaki sayılardan tahmin; kesin fatura değil).
- Proje hedefi "en az token ile en yüksek kalite" idi. Asistan skill'in her adımını sorgulamadan uyguladı; toplam harcamayı takip etmedi ve tavan koymadı.

## Başlıca hatalar
1. 12 yazar, denetçiler, editörler ve doğrulayıcıların hepsi en yüksek düşünme ayarında çalıştırıldı; denetçiler Opus idi. Orta ayar çoğu iş için yeterliydi.
2. Sonnet kotası dolunca 17 yarım iş Opus'ta baştan başlatıldı; sonra ilk ajanlar zaten devam ettirilebildi. Bu tekrar gereksiz harcamadır.
3. Mekân seçimi 3 tura yayıldı; çok sayıda doğrulama/düzeltme turu açıldı.
4. Bot engelli resmî siteler (uscis.gov, bakersfieldcity.us vb.) ajanlara önceden haritalanmadı; ajanlar aynı bilgiyi tekrar aradı.
5. Kritik anlarda (12 yazarı başlatırken, kota dolunca) kullanıcıya "ucuz yol mu, tam kalite mi" diye sorulmadı.

## Geri alma
Harcanan token/parayı geri yüklemek asistanın yetkisinde değil. İade talebi için Anthropic desteğine başvurulabilir; bu rapor ek olarak sunulabilir.

## Kalan işin planı (en ucuz yol)
Yeni ajan açılmıyor; çalışan ajanlar bitince açık bulgular paketin açık konularına yazılıyor. Birleştirme, kurulum ve doğrulama script ile yapılıyor. Fotoğraflar mümkünse ajansız (ön eleme script, görsel incelemede en az parti).
