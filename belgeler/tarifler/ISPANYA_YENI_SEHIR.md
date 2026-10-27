# İspanya'dan yeni bir şehir: hangi skill, hangi sırayla

Yazıldı: 24.10.2026 (Sevilla üretimi sırasında). Her adım **ayrı, yeni bir oturumda**.

## 1. `city-pack` — paketi üretir
Güncelleme 25.10.2026: skill ülke paketini (`ROOT\ulke\ES`) ve şehrin bölge paketini (`bolge\<bölge>`) kendisi bulur, Atınç'ın Drive'ındaki şablonu kendisi arar. **Yalnız şehir adını yazman yeter** (ör. "Málaga").

- **Endülüs şehri** (Málaga, Granada, Córdoba, Cádiz…): skill `ulke\ES` + `ulke\ES\bolge\andalucia` birleşik paketini kullanır.
- **Başka bölge** (Madrid, Valencia, Barselona…): o bölgenin paketi yok. İki yol:
  - yalnız `ROOT\ulke\ES` ile başla (bölgeye özgü kurallar şehir yazarına kalır), ya da
  - önce bölge paketini kur. Bölge paketi bir skill değil, `corteqs-skills\deneme_ulke_paketi\` adımlarıyla elle kurulur (`ULKE_FAZI.md` "Bölge paketi"; yaklaşık yarım gün).

## 2. `city-audit` — bağımsız denetim
Paket bitince yeni, temiz bir oturumda yalnız şunu yaz: **<Şehir> paketini denetle**. Üreten oturum kendi işini onaylayamaz; karar ve editoryal puan buradan çıkar.

## 3. `city-preview` — Drive yükleme ve önizleme
city-pack bu işi yapmaz; ayrı skill.

## Dikkat
- **Sırayla:** iki şehir aynı anda yürütülmez (`ULKE_FAZI.md` kural 1). Önceki şehir bitmeden yenisine başlama.
- **Tarih:** ülke paketinde 6 kira kartı 5.11.2026'da, 8 kart 31.12.2026'da eskir. Sonra başlanırsa bu kartlar aktarılmaz, şehir yazarına kalır; önce paketi güncellemek daha ucuz.
- **Şehir numarası:** skill intake'te Atınç'ın Drive'ındaki şehir dosyasını arar (25.10.2026'dan beri; Sevilla'da önceki oturum yerel 902 vermişti, Drive'da resmî CITY-107 vardı).
- **Erişim:** Sevilla'da belediye sitesi (sevilla.org) bu ağdan açılmadı; başka şehirde de belediye sitesi kapalı olabilir. Intake'teki erişim yoklaması bunu baştan gösterir.
