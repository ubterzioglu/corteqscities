# Corteqs şehir paketleri (0000_newera)

## Kullanıcı yalnız bir şehir adı yazarsa
Mesaj yalnız bir şehir adından (ya da "<şehir> paketi" gibi kısa bir istekten) ibaretse — ör. "Tilburg", "Dortmund":

1. Başka bilgi isteme. Hemen `city-pack` skill'ini çağır ve intake'i o şehirle başlat.
2. Skill gerisini kendisi bulur ve kurallarını kendisi uygular: şehir kimliği, ülke, şablon (Atınç'ın dosyası yoksa Berlin örneğinden türetme), yerel deneme numarası, hitap, ölçüm.
3. Yalnız gerçekten bulunamayan ya da karar gerektiren bir şey çıkarsa tek öneriyle sor ("aksini söylemezsen böyle yapıyorum").
4. O şehrin `uretim\<city_id>\manifest.json` dosyası zaten varsa yeni üretim başlatma. Durumu iki üç cümleyle özetle, ne yapılacağını tek öneriyle sor (devam / yeni sürüm / baştan).

## Çalışma biçimi
- Sade Türkçe, jargonsuz; kararları tek öneriyle sor.
- Karar gerektirmeyen işleri beklemeden yap; uzun işleri paralel çalıştır ve kısa durum raporu ver.
- Bu ortamda bekleme: uzun işi PowerShell `run_in_background` ile çalıştır, bitişi onun bildirimiyle al. Monitor aracı `/c/...` yollarını görmüyor (sessiz kalır); Bash her komut sonunda zararsız bir "cwd" hatasıyla çıkış 1 verebilir, script'in kendi çıktısına bak. Türkçe karakterli yollarda sayımları Python'la yap.
- Şehir üretimi ve denetimi için skill yeterli; `DEVIR_*.md` belgelerini okuma (yalnız kullanıcı geçmişi sorarsa).
