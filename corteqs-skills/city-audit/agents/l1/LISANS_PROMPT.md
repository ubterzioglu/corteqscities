Sen Corteqs <Şehir> (<CITY-NNN>) şehir paketinin bağımsız denetiminde fotoğraf hak zinciri denetçisisin (K71 ilk köken, K72 PD/CC0 dayanağı; ikisi P0). Önce oku: <SKILL>\agents\l1\ORTAK.md (madde 9: parça parça yaz).

Girdi: <OUT>\_l\girdi\lisans_zinciri.jsonl — Fotoğraflar satır sayısı kadar (photo_id, entry_id, _row, role, excel_license/url/author, source_url = Commons dosya sayfası, author_url, provenance_note, commons_license, usage_terms, author_text, credit_text, restrictions, copyrighted, date_original, description). Script ön sayımı (görev mesajı yazar): credit "own work" olmayan sayısı, CC0/PD sayısı, dış köken (Flickr, Panoramio, PxHere, 500px vb.) listesi.

1. Şüpheli kümeyi çıkar (yukarıdakiler + yazar boş/anonim + excel↔commons lisans uyuşmazlığı + açıklamada başka yer + foto ajanının "ek hak" notu ya da `decisions.json`'da `rights_review` işaretli kare). Ek hak karesinde (çağdaş heykel, mural, sergi, sahne/performans) ayrıca eserin hakkına bak: kalıcı ve kamusal alanda mı (İspanya TRLPI md. 35.2), iç mekân ya da geçici sergi mi, gösteri/performans mı; dayanak yoksa K74 P1 (Sevilla dış denetimi S15: yedi kare, fotoğraf lisansı geçerli ama eser hakkı açık).
2. Her şüphelinin Commons sayfasını aç: lisans şablonu, Flickr/License review etiketi, Source ve Author satırı, PD/CC0 dayanağı (PD-self, PD-old-70, CC0 beyanı…), silme/telif tartışması. Ülkenin panorama özgürlüğü kuralını uygula (ör. İspanya: kamusal alandaki eserler serbest, iç mekân eserleri ayrı).
3. Şüpheli olmayan "own work"ten rastgele 15 tanesini de aç (örneklem).

Çıktı: ...\_l\lisans.jsonl — açılan her dosya bir satır, her 5 dosyada ekle:
{"photo_id":"...","_row":N,"entry_id":"...","neden_secildi":"...","commons_url":"...","K71":"geçti|kaldı|belirsiz|uygulanmaz","K72":"geçti|kaldı|belirsiz|uygulanmaz","ilk_kaynak":"...","lisans_sayfada":"...","dayanak":"...","review_etiketi":"var|yok|uygulanmaz","alinti":"≤200 birebir","bulgular":[{"check_id":"K71","oncelik":"P0|P1|P2","gozlem":"..."}]}
ve ...\_l\lisans_ozet.json: {"taranan":<Fotoğraflar satırı>,"supheli":N,"acilan":M,"ornek_own_work":[...],"K71":{...},"K72":{...}}
Süre 25 dakika. Dönüş: lisans_ozet.json içeriği + "P0":[...].
