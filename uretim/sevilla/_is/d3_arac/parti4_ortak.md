# Sevilla 3. tur artığı (Parti 4) — ortak kurallar (bütün ajanlar)

ROOT = C:\temp_private\corteqs\0000_newera · WORK = ROOT\uretim\sevilla · PY = ROOT\.venv\Scripts\python.exe · TK = ROOT\corteqs-skills\toolkit\scripts · AGENTS = ROOT\corteqs-skills\city-pack\agents
Kontrol tarihi: 2026-10-26. Hitap: "sen". Şehir kutusu (bbox): 37.30,37.45,-6.03,-5.89.

## Ortam
- Python'u her zaman bir `.py` dosyasıyla çalıştır (`<PY> -I <TMP>\x.py`); komuta gömülü Python (`python - <<EOF`, `-c` ile uzun kod) yok, takılıyor. Türkçe karakterli yollarda Python kullan, `sys.stdout.reconfigure(encoding='utf-8')`.
- Bash her komut sonunda zararsız bir "cwd" hatasıyla çıkış 1 verebilir; komutun kendi çıktısına bak.
- Alt ajan başlatma. Bütçe en çok ~40 dakika; bitirdiğin kısmı kaydet, bitmeyeni dönüşte yaz.

## Önce oku
- AGENTS\ortak-kurallar.md (kaynak kuralları §4 / add_sources, iddia defteri biçimi, hitap, yasak kalıplar)
- AGENTS\editor.md (görev 1, 2, 6, 7 açık; değişiklik kaydı biçimi). Kural gözden geçirmesi (3), kart ekleme/silme (4, 5) kapalı.
- Görev mesajındaki bulgu dosyası (`WORK\_is\d3_arac\bulgu_4X.json`): her satır bir bulgu (`bulgu_no`, `entry_id`, `alan`, `iddia`, `sonuc`, `agirlik`, `alinti`, `dogrusu`, `_dosya`). `dogrusu` öneridir; kaynakla kendin doğrula, kaynağa uymuyorsa reddet ve kayda gerekçe yaz.

## Kurallar
- Yalnız görev mesajında sayılan dosyaları düzenle: `WORK\_is\data\parcalar\<Sekme>.<parça>.jsonl` ve `WORK\_is\claims\<parça>.jsonl`. Birleşik `data\*.jsonl`, Excel ve paket klasörü elle düzenlenmez; KUR'u ana döngü çalıştırır.
- Şu 7 kart İspanya ülke paketinden gelir, DOKUNMA: oturum-izni-yenileme, aile-birlesimi-ile-oturum, kalici-oturum-bes-yil, arraigo-kok-salma-oturumu, kar-amaci-gutmeyen-oturum-vizesi, libro-de-familia-nedir, registro-civil-ne-ise-yarar. Başka kartlar bunlarla çelişiyorsa öteki kartı bunlara uydur.
- Ücret, saat, işlem kuralı yalnız resmî kurumdan ya da işletmenin/mekânın kendi sitesinden. Turizm portalı (visitasevilla.es, Turismo de Sevilla, andalucia.org vb.) bunlar için kaynak değildir. Resmî sayfa açılmıyorsa değeri uydurma ve portalda bırakma: değeri kayıttan ve defterden çıkar, dönüşte bildir.
- **Kaynak kapasitesi: Kaynaklar 500/500 (sözleşme sınırı, aşılırsa paket kurulmaz).** Senin net yeni kaynak hakkın 0. Yeni kaynak eklediğinde aynı turda bir kaynağı tamamen boşaltmalısın: değiştirdiğin turizm portalı kaynağı başka hiçbir kayıtta, iddiada ve butonda kalmamalı. Bak: `<PY> -I WORK\_is\d3_arac\kaynak_kullanim.py <kaynak_id> [...]` (`serbest: true` = boşaldı). Boşaltamıyorsan yeni kaynak ekleme; bilgiyi var olan kaynakla yaz ya da çıkar ve dönüşte yaz. Bir kaydın `source_ids`'i en çok 2.
- Yeni kaynak: `add_sources` (ortak-kurallar §4; `--subdir snap_<gorev>-editor<sira>`, her koşu yeni klasör; `must_contain` = sayfada birebir kısa ifade). Dönen kimlik kaydın `source_ids`'ine; her yeni/değişen sayı ve kural için defterde birebir alıntılı satır; çıkan bilginin defter satırı silinir. Butonun (`Bağlantılar`) adresi de bir kaynak sayılır: butonu değiştirmen gerekiyorsa görev mesajında izin olmalı.
- Erişim: `sevilla.org` zaman aşımı, `tussam.es` 403 (deneme), `inclusion.gob.es` doğrudan 403 ama add_sources ile açılıyor, `mercadodelaferia.es` spam (kullanma). Bir alan adı bir kez 403/TLS/zaman aşımı verdiyse tekrar deneme.
- `visit_status` her zaman "" (sitede fotoğrafın üstüne bant basılır). Kapanış/istisna `note`'a tarihli tek cümle: "<gün> <ay> <yıl> itibarıyla … (<kaynak adı>)". Yılsız ya da geçmiş tarihli istisna yazma.
- Okura denetim işi bırakma: "kontrol et / doğrula / teyit et / telefonla sor" kalıbı yok. Kaynaklar çelişiyorsa resmî/işletme kaynağı esas; öteki silinmez, "X'e göre …, Y ise …" diye ayrılır ve okura ne yapacağı söylenir.
- slug ve entry_id değişmez. Kart metnine iç not yazma. Anahtar sırası ve alanlar korunur (dosyadaki öbür satırlara bak).
- Önce düzenleyeceğin dosyaların yedeğini al: `<TMP>\yedek\`.
- Her değişikliği `WORK\_is\denetim\<grup>-d4_degisiklik.jsonl`'e yaz (`<grup>` görev mesajında; satır: `entry_id, alan, eski, yeni, bulgu_claim_id, gerekce, alinti`; `bulgu_claim_id` = bulgunun `bulgu_no`'su, ör. "d3-07"). Reddettiğin bulgu için de satır yaz (`yeni` = null, `gerekce` "reddedildi: …").
- Kontrol (isteğe bağlı, dosyaları değiştirmez): `<PY> TK\merge_package.py WORK\_is --city-id sevilla --bbox=37.30,37.45,-6.03,-5.89 --data-out <TMP>\data --out <TMP>\birlestir.json`; kendi kayıtlarında `quote_miss` ve `issues` 0 olmalı, `sources_used` 500'ü geçmemeli (başka ajanlar da aynı anda çalışıyor; kendi kayıtlarına bak).
- Bitirmeden: dokunduğun parça dosyalarının her satırının geçerli JSON olduğunu Python ile doğrula.

## Dönüş (kısa, Türkçe, en çok 15 satır)
Bulgu başına ne yaptın (uygulandı / reddedildi / açık), değişen entry_id'ler, eklenen ve boşaltılan kaynak kimlikleri (net sayı), açılamayan sayfalar, açık kalanlar.
