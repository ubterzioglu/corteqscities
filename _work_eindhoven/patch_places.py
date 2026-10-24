import json

p = 'places_master.json'
places = json.load(open(p, encoding='utf-8'))
DROP = {'witte-dorp', 'sint-jozefkerk', 'baltan-laboratories', 'piet-hein-eek', 'wielewaal'}
places = [x for x in places if x['slug'] not in DROP]

# yeniden adlandır
for x in places:
    if x['slug'] == 'strijp-s-markt-weekly':
        x['slug'] = 'haftalik-pazarlar'
        x['title'] = 'Eindhoven haftalık pazarları'
        x['addr'] = 'Markt / 18 Septemberplein / Woenselse Markt'
        x['visit_note'] = "Şehrin pazar ritmi meydanlara yayılır: salı günleri 18 Septemberplein'de kumaş ve taze gıda pazarı (9.00-16.00), cumartesileri Woenselse Markt'ta 105+ tezgâhlı şehrin en büyük pazarı (10.00-17.00) ve Catharinaplein'de tasarım/vintage pazarı kurulur. Kibbeling ve worstenbroodje pazar klasiğidir."

ADD = [
{"slug":"philips-nederland-gebouw","title":"Philips Nederland binası","group":"Tarih ve mimari","district":"Woensel-Zuid","addr":"Boschdijk 525, 5621? Eindhoven","visit_note":"1960'lardan kalma eski Philips Nederland merkez binası, Boschdijk üzerindeki anıtsal ofis mimarisiyle Philips döneminin kurumsal yüzünü temsil eder; yapı yeniden işlevlendirme sürecindedir, dışarıdan görülür."},
{"slug":"herdgang","title":"De Herdgang (PSV antrenman tesisi)","group":"Spor","district":"Woensel-Zuid","visit_note":"PSV'nin antrenman ve gençlik kompleksi; açık sahalarda A takım idmanları izlenebilir ve akademi maçları oynanır. Kulüp kültürünü saha kenarından görmek isteyenler için kulüp sitesinden açık günleri kontrol edin."},
{"slug":"winkelcentrum-woensel","title":"Winkelcentrum Woensel (WoensXL)","group":"Yeme ve içme","district":"Woensel-Zuid","addr":"Winkelcentrum Woensel, 5625 AA? Eindhoven","visit_note":"Kuzeyin alışveriş ve çarşı merkezi; uluslararası marketler, fırınlar ve haftalık pazarıyla (çarşamba) Woensel'in gündelik kalbidir. Porthos kulesi merkezin siluet işaretidir."},
{"slug":"porthos-toren","title":"Porthos konut kulesi","group":"Tarih ve mimari","district":"Woensel-Zuid","visit_note":"2003'te tamamlanan 71 m'lik konut kulesi, Woensel'in dönüşen siluetinde çağdaş mimarinin işaret fişeğidir; Winkelcentrum Woensel'in hemen yanındaki meydanla birlikte okunur."},
{"slug":"tue-auditorium","title":"TU/e Auditorium","group":"Tarih ve mimari","district":"Binnenstad","addr":"Groene Loper 3? / Den Dolech, 5612 Eindhoven","visit_note":"1950'lerde TH Eindhoven kampüsüyle birlikte açılan anıtsal auditorium binası; dönemin modernist kampüs mimarisinin ve şehrin teknik üniversite kimliğinin simgelerindendir."},
{"slug":"oorlogsmonument-fellenoord","title":"Fellenoord savaş mezarlığı anıtı","group":"Tarih ve mimari","district":"Woensel-Zuid","visit_note":"Fellenoord mezarlığındaki savaş anıtı, 1940-45 kurbanlarını ve 1944 bombardımanının şehir hafızasını taşır; Markt'taki kurtuluş anıtı ve istasyondaki plakalarla birlikte anma rotasının parçasıdır."}
]
places.extend(ADD)
json.dump(places, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
g = {}
for x in places:
    g[x['group']] = g.get(x['group'], 0) + 1
print('places:', len(places), g)

# rota slug güncellemesi
rp = 'routes_master.json'
routes = json.load(open(rp, encoding='utf-8'))
for r in routes:
    r['stops'] = ['haftalik-pazarlar' if s == 'strijp-s-markt-weekly' else s for s in r['stops']]
json.dump(routes, open(rp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('routes patched')
