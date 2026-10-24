# Ek kaynak kayıtları (2. tur fetchlerden) — data_sources.json'a eklenir
import json, os, glob

CITY = "eindhoven"

SRC2 = {
 "gemeente-en": ("Eindhoven İngilizce belediye portalı","Gemeente Eindhoven","resmi","Belediyenin İngilizce giriş sayfası; ürün ve hizmet listelerine bağlantı."),
 "hermes-parkfly": ("Park+Fly Eindhoven","Hermes / Q-Park","ulasim","Terminal M kapalı otopark + 401 otobüsüyle ücretsiz havalimanı aktarması; kombineli tarife."),
 "ns-dalvoordeel": ("NS Dal Voordeel abonmanı","NS","ulasim","Yoğun saat dışı yolculukta indirim sağlayan NS Flex abonmanı."),
 "gemeente-verkeer": ("Trafik ve ulaşım genel sayfası","Gemeente Eindhoven","ulasim","Belediyenin trafik, bisiklet, park ve bölge düzenlemeleri ana sayfası."),
 "rdw-overschrijven": ("Araç ruhsat devri (kenteken overschrijven)","RDW","ulasim","İkinci el araçta devir şartları: 18+, BRP kaydı, kimlik, tenaamstellingscode; online veya lokette yapılır."),
 "gemeente-parkeergarages": ("Parkeren genel sayfası (garajlar, tarifeler)","Gemeente Eindhoven","ulasim","Merkez garajları, sokak tarifeleri ve park rehberi."),
 "gemeente-pr": ("P+R Parkeren en Reizen","Gemeente Eindhoven","ulasim","İki P+R alanı: Meerhoven (batı) ve Genneper Parken (güney); park+otobüs kombineli ucuz merkez erişimi."),
 "gemeente-pr-genneper": ("P+R Genneper Parken","Gemeente Eindhoven","ulasim","Aalsterweg 316; 641 yer, 24/7; hat 7/317/318/408 ile merkeze ~10 dk; otobüs bileti makineden indirimli."),
 "hermes-pr": ("Park+Ride Hermes uygulaması","Hermes","ulasim","P+R'den merkeze 401/402/403 (Meerhoven) ve 7/317/318/408 (Genneper) hatları; park kartı+ucuz bilet kombinasyonu."),
 "gemeente-zero-emissie": ("Zero-emissiezone ve milieuzone","Gemeente Eindhoven","ulasim","2025'ten beri Ring içinde sıfır emisyon bölgesi (kamyonet/kamyon); 2027'den itibaren Euro-4 altı dizel otomobillere milieuzone; ihlal cezası €130/€320."),
 "tie-central-market": ("Central Market (salı pazarı)","This is Eindhoven","gunluk","Her salı 18 Septemberplein'de 9.00-16.00 kurulan merkez pazarı; kumaş, taze gıda, Türk lezzetleri."),
 "tie-woenselse-markt": ("Woenselse Markt (cumartesi pazarı)","This is Eindhoven","gunluk","Her cumartesi 10.00-17.00 Woenselse Markt'ta kurulan, şehrin en büyük ve çok kültürlü pazarı."),
 "summacollege": ("Summa College (bölgesel MBO)","Summa College","aile","Brainport odaklı mesleki eğitim kurumu; teknik, bakım, ekonomi ve yaratıcı programlar."),
 "gemeente-vog": ("VOG başvurusu","Gemeente Eindhoven","resmi","Verklaring omtrent het gedrag: DigiD ile online veya balie'den başvuru; iş/gönüllülük için iyi hal belgesi."),
 "discriminatie-nl": ("Discriminatie.nl ulusal bildirim noktası","Antidiscriminatievoorzieningen","gunluk","Ayrımcılık bildiriminde ücretsiz danışmanlık, kayıt ve destek; anonim bildirim mümkün."),
 "college-rechten-mens": ("College voor de Rechten van de Mens","College voor de Rechten van de Mens","gunluk","Ayrımcılık vakalarında bağlayıcı nitelikte oordeel veren ulusal insan hakları kurumu."),
 "ind-decision-periods": ("IND karar süreleri","IND","oturum","İzin türlerine göre yasal karar süreleri ve gecikme durumu."),
 "ind-partner": ("Partner oturum izni","IND","oturum","Eş/partner için aile birleşimi izni; ilişki ve gelir şartları."),
 "ind-gvva": ("Yabancı çalıştırma (GVVA)","IND","oturum","İşverenin tek başvuruyla oturum+çalışma izni aldığı GVVA prosedürü."),
 "ind-eu-register": ("AB vatandaşı IND kaydı","IND","oturum","AB/AEA/İsviçre vatandaşları için kayıt/kart seçenekleri; çoğu durumda gerekmez."),
 "ind-eu-family": ("AB vatandaşı aile üyesi doğrulaması","IND","oturum","AB vatandaşının AB dışı pasaportlu aile üyeleri için 'verification against EU law' belgesi."),
 "ind-extension": ("Oturum izni uzatma","IND","oturum","Geçici izinlerin uzatma başvurusu; bitişten önce ve sponsor/gelir şartlarıyla."),
 "ind-my-ind": ("My IND portalı","IND","oturum","Başvuru durumu, mesajlar ve dijital işlemler için kişisel IND portalı."),
 "ind-biometrics": ("Biyometri randevusu","IND","oturum","Fotoğraf, imza ve parmak izi verme süreci; davet mektubuyla randevu."),
 "ind-self-employed": ("Serbest meslek oturum izni","IND","oturum","Kendi işini kuracaklar için puanlama sistemi; Türk vatandaşları için ortaklık hukuku istisnaları."),
 "ind-permanent": ("Kalıcı oturum izni","IND","oturum","5 yıl kesintisiz kalış + gelir + inburgering ile kalıcı izin başvurusu."),
 "ind-lost-stolen": ("Kayıp/çalıntı oturum belgesi","IND","oturum","Yedek belge başvurusu ve geçici kanıt düzeni."),
 "ind-travel-return": ("İzinle seyahat ve dönüş vizesi","IND","oturum","Kart yenilenirken/başvuru sürerken seyahat kuralları; terugkeervisum."),
 "mijn-overheid": ("Mijn Overheid portalı","Logius / Rijksoverheid","resmi","Berichtenbox dijital tebligat kutusu ve kişisel kamu verileri portalı."),
 "gemeente-akte-bs": ("Burgerlijke Stand akte/uittreksel","Gemeente Eindhoven","resmi","Doğum/evlilik/ölüm olay belgelerinin (akte) alındığı sayfa; olay belediyesinden alınır."),
 "gemeente-briefadres": ("Briefadres (posta adresi) kaydı","Gemeente Eindhoven","resmi","Sabit ikameti olmayanlar için posta adresi kaydı; onaylı adres üzerinden BRP sürer."),
 "gemeente-adresonderzoek": ("Adresonderzoek başvurusu","Gemeente Eindhoven","resmi","Adreste yaşamayan kişilerin kaydı için belediye incelemesi."),
 "gemeente-rijbewijs": ("Rijbewijs işlemleri","Gemeente Eindhoven","ulasim","Ehliyet başvuru/yenileme ve değişim işlemlerinin belediye sayfası."),
 "gemeente-trouwen": ("Evlilik ve kayıtlı ortaklık","Gemeente Eindhoven","aile","Trouwen/geregistreerd partnerschap bildirimi, tören seçenekleri ve yabancı belge kuralları."),
 "gemeente-overlijden": ("Ölüm bildirimi","Gemeente Eindhoven","resmi","Vefat bildirimi genelde cenaze firması tarafından yapılır; defin/kremasyon izni süreci."),
 "consuwijzer-energie": ("Bağımsız enerji karşılaştırma","Consumentenbond","fatura","Enerji fiyatları, sözleşme koşulları ve tedarikçi değişimi için bağımsız tüketici karşılaştırması."),
 "acm-energie": ("ACM enerji piyasası denetimi","ACM","fatura","Enerji piyasası kuralları, tedarikçi değişimi ve tüketici haklarının düzenleyici kurumu."),
 "brabantwater-verhuizen": ("Brabant Water taşınma bildirimi","Brabant Water","fatura","Yeni adres için su aboneliği bildirim ve devir kanalı."),
 "ennatuurlijk": ("Ennatuurlijk ısı şebekesi","Ennatuurlijk","fatura","Bölgesel ısıtma (stadsverwarming) tedarikçisi; bazı Eindhoven mahallelerinde gaz yerine ısı şebekesi vardır."),
 "eindhovenduurzaam": ("Eindhoven Duurzaam","Gemeente Eindhoven / yerel ortaklar","fatura","Şehrin sürdürülebilirlik portalı: enerji tasarrufu, yalıtım sübvansiyonları, yerel programlar."),
 "rijksoverheid-pensioen": ("Pensioen sistemi","Rijksoverheid","para","AOW + işveren pensioeni + gönüllü üçüncü katman yapısı."),
 "rijksoverheid-minimumloon-qa": ("Asgari ücret soru-cevap","Rijksoverheid","is","Saatlik asgari ücret, yaş basamakları ve ocak/temmuz güncellemeleri."),
 "gemeente-inkomen": ("Gelir ve sosyal destekler","Gemeente Eindhoven","para","Bijstand, borç yardımı (schuldhulpverlening) ve gelir desteklerinin belediye ana sayfası."),
 "fraudehelpdesk": ("Fraudehelpdesk","Fraudehelpdesk","para","Dolandırıcılık bildirim, uyarı ve mağdur destek merkezi."),
 "thuisarts": ("Thuisarts.nl sağlık bilgisi","Huisartsen (NHG)","saglik","Aile hekimlerinin hazırladığı güvenilir hasta bilgi portalı; şikayet bazlı yönlendirme."),
 "zorgkaart": ("ZorgkaartNederland","Patiëntenfederatie","saglik","Sağlık kurumu/huisarts değerlendirmeleri ve arama rehberi."),
 "werknl": ("werk.nl iş arama portalı","UWV","is","Kamu iş ilanları, iş arama araçları ve WW yükümlülük portalı."),
 "rijksoverheid-cao": ("Arbeidsovereenkomst ve CAO","Rijksoverheid","is","İş sözleşmesi türleri, CAO kapsamı, fesih ve hastalıkta maaş kuralları."),
 "kvk": ("KVK ticaret odası","Kamer van Koophandel","is","Şirket kaydı, KVK numarası ve girişimci başlangıç adımları."),
 "nuffic-idw": ("IDW diploma denklik değerlendirme","Nuffic/IDW","aile","Yabancı diplomaların Hollanda eşdeğerliğinin resmî değerlendirme kurumu."),
 "arbeidsinspectie": ("Nederlandse Arbeidsinspectie","Arbeidsinspectie","is","Çalışma koşulları denetimi; kayıt dışı çalışma ve ihlal bildirimleri."),
 "rijksoverheid-kinderopvang": ("Kinderopvang sistemi","Rijksoverheid","aile","Çocuk bakım türleri, LRK kayıt zorunluluğu ve kalite kuralları."),
 "gemeente-onderwijs": ("Onderwijs genel sayfası","Gemeente Eindhoven","aile","Belediyenin eğitim hizmetleri: okul kaydı, leerplicht, yeni gelen çocuklar."),
 "rijksoverheid-leerplicht": ("Leerplicht (zorunlu eğitim)","Rijksoverheid","aile","5 yaş tam zorunluluk, 18'e kadar kısmi yükümlülük ve izin kuralları."),
 "rijksoverheid-schoolvakanties": ("Okul tatilleri","Rijksoverheid","aile","Üç bölge (Noord/Midden/Zuid) tatil takvimi; Eindhoven Zuid bölgesindedir."),
 "studielink": ("Studielink yükseköğretim başvurusu","DUO/hoş kurumlar","aile","HBO ve üniversite başvurularının ulusal dijital sistemi."),
 "fontys": ("Fontys University of Applied Sciences","Fontys","aile","Eindhoven merkezli uygulamalı bilimler üniversitesi."),
 "jeugdfonds": ("Jeugdfonds Sport & Cultuur","Jeugdfonds","aile","Düşük gelirli ailelerin çocukları için spor/kültür üyelik ve malzeme desteği."),
 "gemeente-sport": ("Spor ve hareket","Gemeente Eindhoven","kesif","Şehrin spor tesisleri, kulüp desteği ve hareket programları."),
 "thisiseindhoven": ("This is Eindhoven resmî şehir rehberi","This is Eindhoven","kesif","Şehrin resmî ziyaretçi organizasyonu; etkinlik takvimi ve keşif rehberi."),
 "ddw": ("Dutch Design Week","DDW Foundation","kesif","Her ekim sonunda düzenlenen, Kuzey Avrupa'nın en büyük tasarım etkinliği."),
 "gemeente-vrije-tijd": ("Vrije tijd (serbest zaman)","Gemeente Eindhoven","kesif","Belediyenin serbest zaman, park ve etkinlik sayfaları."),
}

def main():
    cache_meta = {}
    for f in glob.glob(os.path.join("cache", "*.json")):
        d = json.load(open(f, encoding="utf-8"))
        cache_meta[os.path.basename(f)[:-5]] = d
    existing = json.load(open("data_sources.json", encoding="utf-8"))
    have = {s["source_id"].split(":")[-1] for s in existing}
    order = max((s["order"] for s in existing), default=0) + 1
    added = 0
    for cid, (title, pub, topic, note) in SRC2.items():
        if cid in have:
            continue
        m = cache_meta.get(cid)
        if not m or m.get("status") != 200:
            print("WARN cache missing/failed:", cid)
            continue
        existing.append({
            "source_id": f"eindhoven:kaynak:{cid}",
            "city_id": CITY, "title": title, "publisher": pub,
            "url": m.get("final_url") or m["url"],
            "checked_on": "2026-10-20", "topic": topic, "summary": note,
            "verified": "Evet", "order": order,
        })
        order += 1
        added += 1
    json.dump(existing, open("data_sources.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("added:", added, "total:", len(existing))

if __name__ == "__main__":
    main()
