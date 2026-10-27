# Editör görevi — Sevilla (CITY-107), ikinci düzeltme turu (denetim turu)

Önce oku: `C:\temp_private\corteqs\0000_newera\.claude\skills\city-pack\agents\ortak-kurallar.md`, sonra `...\agents\editor.md`. Kayıtları sen yazmadın, denetimi de sen yapmadın.

## Değerler
- `<city_id>` = `sevilla`; `<WORK>` = `C:\temp_private\corteqs\0000_newera\uretim\sevilla`
- `<TK>` = `C:\temp_private\corteqs\0000_newera\corteqs-skills\toolkit\scripts`; `<PY>` = `C:\temp_private\corteqs\0000_newera\.venv\Scripts\python.exe`
- `<tarih>` = `2026-10-25`; `<bbox>` = `37.30,37.45,-6.03,-5.89`; **hitap: `sen`**
- Tur: **denetim turu, açık görevler 1, 2, 6, 7** + aşağıdaki **K25/K26/K31/K40 tamamlama**. Kart ekleme ve silme yok (görev 4–5 kapalı). `entry_id`/slug değişmez.

## Neden bu tur
Bağımsız denetim (L1) kart başına dört şeye baktı ve kartların çoğu kaldı. Bu turun asıl işi bu dört ölçütü **her verilen kartta** geçirmek:
- **K25**: kartın ilk cümlesi başlıktaki soruyu doğrudan cevaplar (ör. başlık "Kimler yararlanır?" → ilk cümle "Yararlananlar: …").
- **K26** (işlem anlatan kartta): okur kartı okuyunca işi yapabilmeli:
  1. **nereye**: başvuru kanalı (çevrim içi sayfa, Sevilla'daki ofis adı ve adresi, randevu yolu),
  2. **ne getir**: belge listesi,
  3. **ne öder**: tutar ya da "ücretsiz" (dönemiyle),
  4. **ne kadar sürer / son tarih**: gün türüyle (iş günü / takvim günü).
  Bilgi değil işlem anlatan kartta bunlardan kaynakta olan her şey yazılır. Kaynakta yoksa yeni resmî kaynak bulunur (aşağıda); bulunamazsa o öğe yazılmaz ve `open`'a "K26: <öğe> kaynakta yok" diye gider. "Siteye bakın / kurumdan doğrulayın" dolgusu yasak.
- **K31**: doğru ve güncel yerel kurum (Sevilla'da işi yapan ofis; bakanlık adı güncel).
- **K40**: süre ve son tarih belirsiz değil (kaç gün, hangi gün türü, neyden itibaren).

## Girdi
- Grubun iş listesi: `<WORK>\_is\duzeltme2\<grup>_kartlar.jsonl` (görev mesajında `<grup>`). Satır başına bir kart: `entry_id`, `topic`, `title`, `durum`:
  - `kaldi:K26,...` → L1 denetçisi bu ölçütlerde kaldı dedi; `K26_not` vb. eksik öğeyi söyler. Hepsini kapat.
  - `denetlenmedi` → L1 bu karta bakmadı. Dört ölçütü kendin uygula; geçmeyeni düzelt.
  - `issues` alanı varsa o kartın denetim bulgusu (önerilen düzeltme ve kanıt adresiyle) — görev 1 olarak uygula. Kanıttaki adres kaynak listesinde yoksa `add_sources` ile ekle.
  - `not` ve `K41` (eski bilgi) notları da bulgudur.
- Düzenlenecek dosyalar (yalnız verilen konuların): `<WORK>\_is\data\parcalar\Yanıtlar.<konu>.jsonl`, `Bağlantılar.<konu>.jsonl`, `<WORK>\_is\claims\<konu>.jsonl` (planlama'da `Adımlar.planlama.jsonl` yalnız bir adımın metni değişen kartla çelişirse).
- Kaynak metinleri: `<WORK>\_is\kaynak_dizini.jsonl` → `text_file`.
- Değişiklik kaydı: `<WORK>\_is\denetim\<konu>-d2_degisiklik.jsonl` (konu başına; `editor.md` biçimi). L1 notundan gelen değişiklikte `bulgu_claim_id` = `L1-<ölçüt>` (ör. `L1-K26`), `issues`'tan gelende ISS kimliği (ör. `ISS-010`), kendi dört ölçüt kontrolünden gelende `L1-oz-<ölçüt>`.

## Ülke paketi kartları
`order` 9000+ satırlar ülke/Endülüs paketinden gelir. Bu turda onlar da iş listesindeyse aynı ölçütlerle düzeltilir (Sevilla ofisi, kanal, belge eklenir); genel kural metnini değiştirme, yalnız eksik öğeyi ekle.

## Yeni kaynak
- Ortak kurallar §4: `add_sources`, her koşu yeni `snap_<konu>-editor<sira>` klasörü (klasör varsa sıra bir artar; `snap_kesif_` öneki kullanılmaz). Konu başına en çok 4 yeni kaynak; kart başına ≤2 `source_ids`, ≤2 Bağlantılar satırı.
- Yalnız resmî yayıncının derin sayfası (devlet, Junta de Andalucía, Diputación, belediye şirketleri: Emasesa, Emvisesa, Lipasam vb., resmî kurum). Ticari site, blog, Wikipedia, anasayfa yok. Şehir turizm portalı ücret/saat/işlem için kaynak değildir.
- Erişim haritası: `<WORK>\_is\kesif\KESIF_TALIMAT.md` "Bilinen erişim durumu" bölümü. Engelli alan adlarını deneme (sevilla.org, sede.sevilla.org, tussam.es, lipasam.es, aena.es, femas.es, sede.administracionespublicas.gob.es, mivau.gob.es, transportes.gob.es). Engelli sitenin aynası ya da yan alan adı kaynak olmaz; yedek, aynı bilgiyi veren başka resmî kurumdur.
- Tarihe duyarlı bilgide (ücret, süre, yaş eşiği, 2026 kural değişikliği) kaynağın tarihinden sonra yeni kural çıktı mı diye ara.

## Parça parça yaz
Her konuyu bitirince dosyalarını ve değişiklik kaydını hemen yaz (sonra öteki konuya geç). Kesilirsen yazdığın kalır.

## Bitirmeden
Ortak kurallar §8'deki `merge_package` kontrolü (çıktılar `<TMP>`'ye): kendi parçanı ilgilendiren bulgu 0. Ardından `text_quality` (ortak kurallar) kendi kartlarında dolgu ve hitap bulgusu 0 ("siz" yok).

## Sınırlar
**Alt ajan başlatma.** Geçici dosyalar yalnız `<TMP>` = `C:\Users\BARIS-~1\AppData\Local\Temp\claude\c--temp-private-corteqs-0000-newera\56c9766a-06a1-495c-9d57-190d48973e42\scratchpad\<grup>_w\`. Bütçe 60 dakika / 200 araç çağrısı; dolunca bitirdiğin konularla dön, kalan kartları `open`'a yaz.

## Dönüş
Konu başına `editor.md`'deki tek satır JSON (`part` = `<konu>-d2`) ve ek alanlar `"k26_kapanan":n, "k26_acik":["entry_id: öğe"]`; hepsi tek JSON nesnesinde: `{"<konu>": {...}, ...}`
