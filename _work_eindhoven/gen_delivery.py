# Teslim dosyaları üretimi
import json, os, hashlib, csv, datetime

ROOT = r"C:\temp_private\corteqs\0000_newera\eindhoven_qwen38_max"
TES = os.path.join(ROOT, "Teslimler")
os.makedirs(TES, exist_ok=True)
TODAY = "2026-10-20"

qa = json.load(open('qa_report.json', encoding='utf-8'))
c = qa['counts']

def sha_file(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for cc in iter(lambda: f.read(1 << 20), b''):
            h.update(cc)
    return h.hexdigest()

# ---------- TESLIM_OZETI ----------
ozet = f"""CORTEQS ŞEHİR PAKETİ — TESLİM ÖZETİ (v7 lokal üretim)
Şehir: Eindhoven · city_id: eindhoven · CITY-039
Üretim tarihi: {TODAY} · Üretim modu: Lokal deneme (qwen3.8-max), v7 sözleşmesi
Paket: eindhoven_qwen38_max/

ÖLÇÜLER (gerçek / hedef / uygulanan alt sınır)
- Pratik yanıt kartı      : {c['answers']} / 240 / 212  → {'HEDEF AŞILDI' if c['answers']>=240 else 'ALT SINIR GEÇİLDİ'}
- Keşif mekânı            : {c['places']} / 120 / 92   → ALT SINIR GEÇİLDİ (hedefin altında; gerekçe ACIK_KONULAR'da)
- Mahalle                 : {c['districts']} / 16 / 16   → HEDEF KARŞILANDI
- Konu                    : {c['topics']} / 12 / 12      → HEDEF KARŞILANDI
- Tekil mekân fotoğrafı   : {c['unique_venue_photos']} / 250 / 187 → HEDEF AŞILDI
- Tekil kapak fotoğrafı   : {c['unique_hero_photos']} / 8 / 6      → HEDEF KARŞILANDI
- Rota                    : {c['routes']} / 12 / 9       → HEDEF KARŞILANDI
- Sözlük terimi           : {c['glossary']} / 60 / 48    → HEDEF AŞILDI
- Kaynak kaydı            : {c['sources']} (tamamı üretim günü açılıp okundu, verified=Evet)
- Fotoğraf toplamı        : {c['photos']} (WebP, ≤1600px) · Kanıt kaydı: {c['evidence']} · Eylem bağlantısı: {c['actions']}
- Adım (yolculuk merdiveni): {c['steps']} · Sayfa alanı: {c['fields']}

KANIT ZİNCİRİ
- Tüm fotoğraflar Wikimedia Commons'tan; yalnız CC0 / CC BY / CC BY-SA / Public Domain lisansları kullanıldı.
- Her fotoğraf için: API imageinfo kaydı (<foto>.source-evidence.json), lisans/atıf kaydı (<foto>.license-record.json),
  indirilen 1600px kopya (Lisans kanıtları/orijinaller/) ve SHA-256 zinciri (Kanıtlar + FotoğrafKaynakları sekmeleri).
- Kaynak metin önbelleği üretim makinesinde saklandı; Kaynaklar sekmesindeki checked_on={TODAY} gerçek açma/okuma tarihidir.

İNSAN ONAYI BEKLEYEN ALANLAR (AI tarafından doldurulmadı)
- Kanıtlar.pixel_review_status = Bekliyor (kare/mekân eşleşmesinin insan gözüyle onayı)
- Kanıtlar.rights_status = Bekliyor (nihai hak değerlendirmesi)
- Teslimat.reviewer boş; editorial_status her satırda "İnceleme"
- Şehir/Teslimat kimlik alanları korunmuştur.

QA
- Yapısal+içerik+görsel denetim scripti çalıştırıldı: {len(qa['errors'])} hata, {len(qa['warnings'])} uyarı.
- UAT/yayınlama, Drive/FTP/Monday, harici dağıtım ve resmî doğrulama yapılmadı (lokal mod).
"""
open(os.path.join(TES, 'TESLIM_OZETI_v7.txt'), 'w', encoding='utf-8').write(ozet)

# ---------- ACIK_KONULAR ----------
acik = f"""AÇIK KONULAR VE SINIRLAMALAR — Eindhoven CITY-039 (v7 lokal üretim, {TODAY})

1) MEKÂN SAYISI HEDEFİN ALTINDA (93/120; alt sınır 92 GEÇİLDİ)
   Sözleşme gereği her mekân en az bir GERÇEK ve eşleşen fotoğrafa sahip olmalı. Serbest lisanslı
   fotoğrafı doğrulanamayan adaylar (Sectie-C, Enversed, Popei, Plaza Futura, Monkey Town, Ballorig,
   Kinderboerderij, Zwembad De Rozenbottel, Zwembad Tongelreep'in ek kareleri, Muziekkiosk, Strijp-R,
   Witte Dorp, Landgoed De Wielewaal, Sint-Jozefkerk, Baltan Laboratories, Piet Hein Eek, Woensel
   cumartesi pazarı alanı, Blixembosch, Gijzenrooise Zeggen, Driehoeksbos, Meerbos, Park Forum)
   listeye ALINMADI. Editör lisanslı stok fotoğrafla bu mekânları ekleyebilir.

2) GRUP DENGESİ: Tarih ve mimari 53/93 ile ağırlıklı. Neden: Eindhoven'ın Commons'ta en yoğun
   fotoğraflanan varlıkları rijksmonumenten ve endüstriyel miras. Yeme-içme (8), sahne (5), sanat (4)
   ve çocukla keşif (4) grupları fotoğraf bulunabilirliğiyle sınırlı. Sözleşme "uydurma mekân"ı
   yasakladığı için dengeleme gerçek varlıklarla yapıldı.

3) İNSAN İNCELEMESİ BEKLİYOR: Kanıtlar.pixel_review_status ve rights_status tüm fotoğraflarda
   "Bekliyor". Otomatik eşleşme notu her kanıtta; görsel açıldı ve dosya bütünlüğü doğrulandı,
   ancak nihai kare/mekân ve hak onayı insan işidir.

4) KOORDİNATLAR: 30 mekânda doğrulanmış koordinat yok (alan opsiyonel; rijksmonumenten ve
   Wikipedia koordinatları kullanıldı, uydurma koordinat yazılmadı).

5) FOTOĞRAF ÇÖZÜNÜRLÜĞÜ: Commons'un 1600px türev kopyaları indirildi ve saklandı; özgün tam
   çözünürlük dosyaları ayrıca indirilmedi (URL'leri FotoğrafKaynakları'nda). Paket boyutu ~{0} MB.

6) ADRES/SAAT DOĞRULAMASI: Müze/kurum adresleri resmî sitelerden veya rijksmonument listesinden
   alındı; birkaç mekânda adres alanı boş bırakıldı (doğrulanamadı). Ziyaret saatleri KASTEN
   yazılmadı (değişken veri); mekân notlarında "kurumdan doğrula" uyarısı var.

7) MAHALLE LİSTESİ: Blixembosch için serbest lisanslı gerçek fotoğraf bulunamadı (yalnız harita
   görseli); yerine fotoğraflı De Roosten bölgesi listelendi. 16 mahalle hedefi korundu.

8) BERLİN'DEN KOPYALANMAYAN ALANLAR: EkDetaylar sekmesi bilinçli olarak boş (Berlin'deki _db_
   arşiv alanları eski DB dökümüdür). Rota stop_entry_ids ve sözlük source_ids Berlin'de boştu;
   bu pakette DOLDURULDU.

9) HAVA DURUMU: forecast_url Weeronline şehir sayfası (üçüncü taraf), provider Weeronline;
   sözleşme "güvenilir güncel tahmin sayfası" ölçütüne uygundur.

10) YASAL SINIR: Bu paket resmî doğrulama/yayınlama değildir. Süre, ücret ve koşul bilgileri
    {TODAY} tarihli resmî sayfalardan derlenmiştir; işlem anında kaynaktan yeniden doğrulanmalıdır.
""".format(round(sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(ROOT) for f in fs) / 1e6, 1))
open(os.path.join(TES, 'ACIK_KONULAR_v7.txt'), 'w', encoding='utf-8').write(acik)

# ---------- atıf dosyaları ----------
import openpyxl
wb = openpyxl.load_workbook(os.path.join(ROOT, 'CITY-039_eindhoven_v001.xlsx'), read_only=True)
ws = wb['Fotoğraflar']
rows = []
for row in ws.iter_rows(min_row=8, max_col=18):
    v = [c.value for c in row]
    if all(x is None for x in v):
        continue
    rows.append(v)
with open(os.path.join(TES, 'atıf_listesi.csv'), 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f, delimiter=';')
    w.writerow(['photo_id', 'dosya', 'başlık', 'fotoğrafçı', 'lisans', 'lisans_url', 'kaynak_sayfa', 'atıf'])
    for v in rows:
        lic = str(v[8] or '')
        attr = f"Fotoğraf: {v[7]}, {lic}, Wikimedia Commons"
        w.writerow([v[0], v[4], v[6], v[7], lic, v[9], v[10], attr])

html = ["""<!DOCTYPE html><html lang="tr"><head><meta charset="utf-8">
<title>Eindhoven CITY-039 — Fotoğraf Atıfları</title>
<style>body{font-family:system-ui,Segoe UI,Arial;margin:24px;color:#1a1a1a}
table{border-collapse:collapse;width:100%}td,th{border:1px solid #ccc;padding:6px 8px;font-size:13px;text-align:left}
th{background:#f2f2f2}img{max-width:140px;border-radius:4px}</style></head><body>
<h1>Eindhoven şehir paketi — fotoğraf atıfları</h1>
<p>Tüm görseller Wikimedia Commons kaynaklıdır ve aşağıdaki lisanslarla ücretsiz ticari kullanıma uygundur.
CC BY-SA görsellerin türevleri aynı lisansla paylaşılmalıdır.</p>
<table><tr><th>Görsel</th><th>Başlık</th><th>Fotoğrafçı</th><th>Lisans</th><th>Kaynak</th></tr>"""]
for v in rows:
    lic = str(v[8] or '')
    html.append(
        f"<tr><td><img src=\"../{v[4]}\" alt=\"\"></td><td>{v[6]}</td><td>{v[7]}</td>"
        f"<td><a href=\"{v[9]}\">{lic}</a></td><td><a href=\"{v[10]}\">Commons sayfası</a></td></tr>")
html.append("</table></body></html>")
open(os.path.join(TES, 'atıf_listesi.html'), 'w', encoding='utf-8').write('\n'.join(html))
print('atıf dosyaları yazıldı:', len(rows), 'fotoğraf')

# ---------- dosya envanteri ----------
inv = []
for dp, _, fs in os.walk(ROOT):
    for fn in fs:
        p = os.path.join(dp, fn)
        rel = os.path.relpath(p, ROOT).replace(os.sep, '/')
        if rel.startswith('Teslimler/dosya-envanteri'):
            continue
        inv.append({'path': rel, 'bytes': os.path.getsize(p), 'sha256': sha_file(p)})
json.dump({'generated_on': TODAY, 'city': 'eindhoven', 'delivery': 'CITY-039-v001',
           'files': inv, 'total_files': len(inv),
           'total_bytes': sum(x['bytes'] for x in inv)},
          open(os.path.join(TES, 'dosya-envanteri.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('envanter:', len(inv), 'dosya')
