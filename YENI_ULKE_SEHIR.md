# Yepyeni bir ülkeden şehir: tarif

Yazıldı: 24.10.2026 (Sevilla üretimi sırasında). İspanya için ayrı not: `ISPANYA_YENI_SEHIR.md`.

## 0. Önce tek karar: o ülkeden kaç şehir gelecek?
Atınç'ın Drive kataloğunda (`CITY-NNN · <Şehir> · <Ülke> · <id>` klasörleri) o ülkenin şehirlerini say.

| Durum | Yol | Neden |
|---|---|---|
| 1–2 şehir | **A: Doğrudan şehir** (ülke paketi yok) | Paket kurmanın maliyeti geri dönmez |
| 3 ve fazla şehir | **B: Önce ülke paketi, sonra şehirler** | Ulusal bilgi (vize, vergi, sağlık, iş, kira hakları) bir kez araştırılır; İspanya'da 105 kart hazır geldi |

Varsayılan: sayı bilinmiyorsa A. Aksini söylemezsen böyle yapılır.

## Yol A — doğrudan şehir (Bakersfield yolu)
1. **`city-pack`** — yeni oturumda:
   > <Şehir> paketi. Atınç'ın Drive'ındaki şablonu ara.
   Skill gerisini bulur (ülke, dil, saat dilimi, Wikidata, mekân havuzu, erişim yoklaması). Ülke paketi verilmediği için bütün 12 konu sıfırdan yazılır.
   Ölçü: Bakersfield ~7 saat, ~130 ajan (bütçe aşıldı; skill'de artık ≤60 ajan hedefi var).
2. **`city-audit`** — yeni, temiz oturumda: **<Şehir> paketini denetle**.
3. **`city-preview`** — Drive yükleme ve önizleme.

## Yol B — önce ülke paketi
Ülke paketi bir skill DEĞİL; `corteqs-skills\deneme_ulke_paketi\` altındaki script'lerle, İspanya'da yapıldığı gibi elle kurulur. Tarif: `ULKE_FAZI.md`. Ek yazar kuralları: `YAZAR_KURALLARI.md` (İspanya'nın 3 bağımsız denetiminden çıkan dersler; ülkeden bağımsız).

1. **Ülke paketi** (bir kez, ayrı oturum): `ROOT\ulke\<ÜLKE_KODU>\`
   - Keşif → `add_sources` → yazar (şehir-nötr kart: şehir adı yerine `{sehir}`, `entry_id = <kod>:<slug>`) → `pack_check` → bağımsız denetim → editör → kurulum:
     `pack_build.py <ulke\XX> --country XX --version 1 --topics <konular>`
   - Tarihe duyarlı kartlara `valid_until` yazılır (asgari ücret, vergi dilimi, vize ücreti, tatiller).
   - İspanya'da paket 96 ulusal kart çıktı; kesif konusu ülke paketine girmez.
2. **Bölge paketi** (ülke bölgeye göre kural değiştiriyorsa): `ROOT\ulke\XX\bolge\<ad>\`, aynı akış, `pack_build ... --region <ad>`. Federal ya da güçlü bölgeli ülkelerde (Almanya eyaletleri, ABD eyaletleri, İspanya özerk bölgeleri) gerekir; merkezî ülkelerde (Hollanda, Portekiz) çoğu zaman gerekmez.
3. **Şehir** — yeni oturumda, paketi açıkça ver (skill ülke paketini yalnız kullanıcı verirse kullanır):
   > <Şehir> paketi. Ülke paketi var: `ROOT\ulke\XX` (+ bölge `ROOT\ulke\XX\bolge\<ad>`). `corteqs-skills\deneme_ulke_paketi\ULKE_FAZI.md`'deki "city-pack ile birlikte kullanım" adımlarını uygula. Atınç'ın Drive'ındaki şablonu ara. Ülke, bölge ve şehir fazının süre ve token'ını ayrı ölç.
4. **`city-audit`**, sonra **`city-preview`** (Yol A'daki gibi).

## Her iki yolda dikkat
- **Sırayla:** iki şehir aynı anda yürütülmez; biri bitmeden yenisi başlamaz.
- **Şablon ve numara:** skill Atınç'ın Drive'ındaki şehir dosyasını kendiliğinden aramıyor; başlangıç mesajına "Atınç'ın Drive'ındaki şablonu ara" ekle. Drive'da yoksa skill Berlin örneğinden şablon türetir ve 900+ yerel deneme numarası verir.
- **Erişim:** yeni ülkede hangi resmî sitelerin bu ağdan açıldığı bilinmiyor. Intake'teki erişim yoklaması (≈40 adres) bunu gösterir; Sevilla'da belediye sitesinin tamamen kapalı olduğu böyle çıktı. Kapalı site aşılmaz, açık konuya yazılır.
- **Dil:** kaynaklar yerel dilde okunur, kartlar Türkçe ve "sen" hitabıyla yazılır; `must_contain` kanıt ifadeleri sayfanın kendi dilindedir.
- **Ölçüm:** ülke ve bölge paketi kuruluyorsa süre ve token'ı en baştan kaydet (`phase_usage mark`, oturum kaydı). İspanya paketleri bulut oturumunda kurulduğu için ölçümleri yok; bu hatayı tekrarlama.
- **Ülke paketi daha olgunlaşınca** (Sevilla ve bir Endülüs şehri sonrası) skill'e `country` fazı olarak eklenmesi planlanıyor; o zamana kadar bu tarif geçerli.

## Ölçülmüş örnek: Almanya paketi (25.10.2026)
Yol B tek oturumda, baştan ölçümlü yapıldı: 113 kart / 2120 iddia / 193 kaynak; **2 sa 21 dk**, 3,9 M çıktı token, 52 Sonnet ajanı (konu başına keşif + yazar + denetçi + editör, grup başına dar denetim + kısa editör). İspanya paketi (96 kart) kabaca 12 M ajan token'ı ve iki güne yayılmıştı; fark, konuların paralel yürütülmesi ve görev metinlerinin dosyada tutulmasından. Ayrıntı: `corteqs-skills\deneme_ulke_paketi\ULKE_FAZI.md` "İkinci ülke: Almanya"; şehir başlatma: `ALMANYA_YENI_SEHIR.md`.
