# İspanya ulusal paketi — yazar ek kuralları (3 bağımsız denetimden çıkan dersler)

Bu kurallar `city-pack\agents\ortak-kurallar.md` ve `yanit-yazari.md`'ye EK olarak geçerlidir; çelişirse bunlar geçer.

1. Şehir-nötr yaz: başlıkta ve metinde şehir adı yok; şehre/bölgeye bağlanan adres, ofis, randevu yazma. Bölgeye göre değişen şeyi "bölgeye göre değişir" diye çerçevele, rakam verme.
2. Kart başına en çok 2 source_ids. Cümle yalnız kartın kendi kaynağında yazıyorsa yazılır.
3. Havale cümlesi YASAK: "resmî sayfadan teyit et", "resmî sayfada yazar", "bu kartta yok", "burada açıklanmıyor". Cevabı yaz ya da o bilgiyi hiç yazma. Eksik bilgi karta değil `gaps.md`'ye gider.
4. Başlıktaki soruya ilk cümlede cevap ver (örn. "Hayır, ayrı izin gerekmez").
5. Kaynakta olmayan hesap, yuvarlama, çarpma/bölme, "yaklaşık" ekleme YOK. Kaynak aylık veriyorsa aylık, yıllık veriyorsa yıllık yaz. Sayıyı kaynaktaki hâliyle yaz.
6. Tarihe duyarlı sayıda (oran, eşik, ücret, süre) kaynak sayfanın yılını/tarihini karta yaz ("2026 için", "Renta 2025 kılavuzuna göre"). Kaynakta yıl yoksa "güncel tarife" de, tarih uydurma.
7. Türk okuyucu için: AB/AEA serbest dolaşım rejimi Türk vatandaşına uygulanmaz; kart AB vatandaşını anlatıyorsa bunu bir cümleyle söyle. Türkiye-İspanya ikili anlaşması yalnız kaynakta açıkça varsa yazılır.
8. Kaynağın kanıtlamadığı bir yerde kesin konuşma ("isteğe bağlı", "zorunlu değil", "herkes") — kaynağın söylediği kapsamla sınırla.
9. Çeviri dikkati: "carta de naturaleza" ödül değil; "educación secundaria postobligatoria" = zorunlu eğitim sonrası lise düzeyi; "folio" = sayfa değil, noter terimi olarak bırak ya da açıkla.
10. Her kartta ≥1 işlem/bilgi bağlantısı (kaynaklardan biri olabilir). Her sayı/şart/süre için ayrı claim, quote kaynaktan BİREBİR (≤200 karakter).
11. valid_until.json: tarihe duyarlı kartlar için kaynaktaki bitiş (örn. "Hasta el 31 de diciembre de 2026" → 2026-12-31); bilinmiyorsa null.
12. Başlık/özet/adımlar birbirini yalanlamasın; kart yalnız kaynağın kapsadığı yönü (örn. yalnız İspanya'da düzenlenen belge) kapsıyorsa başlık da öyle olsun.
