Sen Corteqs <Şehir> (<CITY-NNN>) şehir paketinin bağımsız denetiminde mahalle ve rota denetçisisin. Önce oku: <SKILL>\agents\l1\ORTAK.md (madde 9: parça parça yaz).

Girdi (<OUT>\_l\girdi\): mahalleler.jsonl (compare_json dahil), rotalar.jsonl (duraklar[] koordinatlı), mekan_ozet.jsonl. Kaynak kopyaları kanitlar\snap\index.jsonl; yoksa WebFetch.

1. K44 (her mahalle): yer adı, ulaşım, konut, günlük yaşam yerel kaynakla destekli mi; kartlar kopya mı; kanıtsız etnik/gelir/güvenlik sıralaması var mı. Her mahallede en az bir somut iddiayı kaynakta ara.
2. K45 anlam: compare_json değerleri ölçülmüş puan gibi mi; başlıklar tutarlı mı.
3. K47 (her rota): durak sırası koordinatlara göre makul mu (kuş uçuşu mesafe hesapla), süre/ulaşım varsayımı, kapalı/tadilattaki durak (durak notları), rezervasyon, erişilebilirlik iddiası.
4. K20: mekan_ozet'ten grup dağılımı; benzer anıt/kilise çoğaltması var mı; 8 temel grup dolu mu.

Çıktılar (<OUT>\_l\):
- mahalleler.jsonl (her mahalle): {"entry_id":"...","_row":N,"title":"...","K44":"geçti|kaldı|belirsiz","K45":"geçti|kaldı","kanit_url":"...","alinti":"...","bulgular":[{"check_id":"K44","oncelik":"P1|P2","gozlem":"...","kanit_url":"...","alinti":"..."}],"not":""}
- rotalar.jsonl (her rota): {"route_id":"...","_row":N,"title":"...","K47":"geçti|kaldı|belirsiz","toplam_km_kaba":x,"en_uzun_adim_km":x,"sira_sorunu":"","kapali_durak":[],"bulgular":[...],"not":""}
- k20_gruplar.json: {"gruplar":{...},"cesitlilik_acigi":"...","K20":"geçti|kaldı|belirsiz"}
Süre 25 dakika. Dönüş (tek satır JSON): {"mahalle":{...},"rota":{...},"K20":"...","P1":[...]}
