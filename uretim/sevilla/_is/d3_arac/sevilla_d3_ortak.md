# Sevilla 3. düzeltme turu — ortak kurallar (bütün ajanlar)

ROOT = C:\temp_private\corteqs\0000_newera · WORK = ROOT\uretim\sevilla · Python = ROOT\.venv\Scripts\python.exe · TK = ROOT\corteqs-skills\toolkit\scripts
Bash her komut sonunda zararsız bir "cwd" hatasıyla çıkış 1 verebilir; komutun kendi çıktısına bak. Türkçe karakterli yollarda Python kullan (`-I`, `sys.stdout.reconfigure(encoding='utf-8')`).

Dayanak: ROOT\Sevilla_Detayli_Denetim_20261025.md (bağımsız dış denetim). Bulgu bölümleri 304–800. satırlar arasında; yalnız sana verilen S kodlarını oku (grep "S0X / P").

Önce oku: ROOT\corteqs-skills\city-pack\agents\ortak-kurallar.md (kaynak kuralları §4 / add_sources, iddia defteri biçimi, hitap "sen", yasak kalıplar) ve ROOT\corteqs-skills\city-pack\agents\editor.md (değişiklik kaydı biçimi). Sana özel talimat dosyası görev mesajında.

Kurallar:
- Yalnız şu dosyaları düzenle: WORK\_is\data\parcalar\<Sekme>.<parça>.jsonl ve WORK\_is\claims\<parça>.jsonl. Birleşik data\*.jsonl, Excel ve paket klasörü elle düzenlenmez; KUR'u ana döngü çalıştırır.
- Şu 6 slug'a DOKUNMA (İspanya ülke paketinde ayrıca düzeltiliyor): oturum-izni-yenileme, aile-birlesimi-ile-oturum, kalici-oturum-bes-yil, arraigo-kok-salma-oturumu, kar-amaci-gutmeyen-oturum-vizesi, libro-de-familia-nedir.
- Yalnız resmî ya da işletmenin kendi kaynağından yaz; turizm portalı ücret/saat kaynağı değildir. Yeni kaynak: add_sources (must_contain = sayfada birebir kısa ifade), dönen kimlik kaydın source_ids'ine; her yeni/değişen sayı ve kural için defterde birebir alıntılı satır; çıkan bilginin defter satırı silinir. Sayfa açılmıyorsa değeri uydurma: değeri karttan çıkar, dönüşte bildir.
- visit_status her zaman "" (sitede fotoğraf üstü bant). Kapanış `note`'a tarihli tek cümle: "<gün> <ay> <yıl> itibarıyla … (<kaynak adı>)". Kontrol tarihi 26 Ekim 2026.
- Okura denetim işi bırakma: "kontrol et / doğrula / teyit et" kalıbı yok; kaynaklar çelişiyorsa resmî/işletme kaynağı esas, öteki "X'e göre …" diye ayrılır, okura ne yapacağı söylenir.
- slug ve entry_id değişmez. Kart metnine iç not yazma.
- Önce düzenleyeceğin dosyaların yedeğini al: <geçici klasörün>\yedek\.
- Her değişikliği WORK\_is\denetim\<grup>-d3_degisiklik.jsonl'e yaz (editor.md biçimi: entry_id, alan, eski, yeni, bulgu_claim_id = "dis:S0X", gerekce, alinti).
- Bitirmeden: kendi dokunduğun parça dosyalarının JSON satırlarının geçerli olduğunu Python ile doğrula.
- Bütçe en çok ~40 dakika; bitirdiğin kısmı kaydet, bitmeyeni dönüşte yaz.

Dönüş (kısa, Türkçe, en çok 15 satır): bulgu başına ne yaptın (değişen entry_id'ler), eklenen kaynaklar, açılamayan sayfalar, açık kalanlar.
