from lib import add

C = dict(
    slug='birlesik-muze-bileti-ve-bono-arte-xperience',
    title="Málaga'da birkaç müzeyi tek biletle gezmenin yolu var mı (Bono Arte Xperience ve ortak biletler)?",
    subtitle="Bono Arte Xperience 16,50 € (indirimli 9,50 €): Casa Natal, Pompidou ve Museo Ruso, 1 hafta; ikili ortak biletler 9,50-10 €",
    summary=("Evet: Bono Arte Xperience ile Museo Casa Natal Picasso, Centre Pompidou Málaga ve Colección del Museo Ruso'yu 1 hafta içinde gezersin; "
             "genel fiyat 16,50 €, indirimli 9,50 €'dur. Yalnız iki müze istersen Casa Natal + Pompidou ortak bileti 10 € (indirimli 6 €), Casa Natal + Museo Ruso 9,50 € (indirimli 5 €) tutar. "
             "Sadece Pompidou'ya gidiyorsan sürekli koleksiyon 7 €, geçici sergi 4 €, ikisi birlikte (combinada) 9 €'dur; indirimli fiyatlar 4 €, 2,50 € ve 5,50 €."),
    keywords="Bono Arte Xperience, ortak bilet, entrada conjunta, Casa Natal Picasso, Centre Pompidou Málaga, Museo Ruso, müze kartı",
    stages='planning;new;settled', src=['277', '282'], order=1205, featured='Hayır',
    steps=[
        "Üç müzeyi (Casa Natal, Pompidou, Museo Ruso) bir hafta içinde gezeceksen Bono Arte Xperience al: 16,50 € ya da indirimli 9,50 €.",
        "İki müze yetiyorsa ortak bilet seç: Casa Natal + Pompidou 10 € (indirimli 6 €), Casa Natal + Museo Ruso 9,50 € (indirimli 5 €).",
        "Yalnız Pompidou'ya gideceksen sürekli koleksiyon (7 €), geçici sergi (4 €) ya da ikisini birden (9 €) seç.",
        "İndirimli bilet için 65 yaş üstü, 26 yaş altı öğrenci, büyük aile ya da Üniversite kongre katılımcısı olduğunu belgele.",
    ],
    documents=["İndirim hakkını gösteren belge (yaş, öğrenci ya da büyük aile belgesi)"],
    timing="Bono Arte Xperience 1 hafta geçerlidir",
    cost="Bono 16,50 € (indirimli 9,50 €); Casa Natal + Pompidou 10 € (6 €); Casa Natal + Museo Ruso 9,50 € (5 €)",
    note="Çevrimiçi satışta bilet başına 0,30 € ek yönetim ücreti vardır.",
    links=[('Tarifeyi gör', '277'), ('Tarifeyi gör', '282')],
    claims=[
        ('summary', "Bono Arte Xperience 3 müze 1 hafta: genel 16,50 €, indirimli 9,50 €", "16,50; 9,50", "EUR", "1 hafta", '277', "Bono Arte Xperience (3 museos durante 1 semana)** 16,50 € 9,50 €"),
        ('summary', "Bonoya dahil müzeler: Casa Natal Picasso, Centre Pompidou Málaga, Colección Museo Ruso", "", "", "", '277',
         "Museos incluidos en el bono: Museo Casa Natal Picasso, Centre Pompidou Málaga, Colección Museo Ruso"),
        ('summary', "Pompidou combinada 9 € (indirimli 5,50 €), sürekli koleksiyon 7 € (4 €), geçici sergi 4 € (2,50 €)", "9; 5,50; 7; 4; 2,50", "EUR", "", '277',
         "Combinada (semipermanente + temporal) 9 € 5,50 € Exposición semipermanente 7 € 4 € Exposición temporal 4 € 2,50 €"),
        ('steps', "Pompidou indirimli bilet: 65 yaş üstü, 26 yaşa kadar öğrenci, büyük aile, Üniversite kongre katılımcıları", "65; 26", "yaş", "", '277',
         "La entrada reducida se aplica a mayores de 65 años, estudiantes de hasta 26 años, familias numerosas y participantes en las actividades congresuales realizadas por la Universidad."),
        ('note', "Pompidou çevrimiçi satışta 0,30 € ek yönetim ücreti", "0,30", "EUR", "", '277', "Conlleva un cargo de gestión adicional de 0,30 €."),
        ('summary', "Casa Natal + Pompidou ortak bilet: genel 10 €, indirimli 6 €", "10; 6", "EUR", "", '282', "Entrada conjunta Museo Casa Natal + Centre Pompidou Málaga. General: 10 €. Reducida: 6 €"),
        ('summary', "Casa Natal + Museo Ruso ortak bilet: genel 9,50 €, indirimli 5 €", "9,50; 5", "EUR", "", '282', "Entrada conjunta Museo Casa Natal + Colección del Museo Ruso. General: 9,50 €. Reducida: 5 €"),
        ('summary', "Üç müzelik ortak bilet: genel 16,50 €, indirimli 9,50 €", "16,50; 9,50", "EUR", "", '282',
         "Entrada conjunta Museo Casa Natal + Centre Pompidou Málaga + Colección del Museo Ruso. General: 16,50 €. Reducida: 9,50 €"),
    ],
)

D = dict(
    slug='ab-vatandasi-sarti-museo-de-malaga-ve-alcazaba',
    title="Türk vatandaşı olarak Museo de Málaga'ya ne ödersin; Alcazaba'da 'AB vatandaşı' indirimi kimlere uygulanır?",
    subtitle="Museo de Málaga: AB vatandaşı ücretsiz, diğer uyruklar 1,50 €; Alcazaba'da 65 yaş üstü, emekli, işsiz ve öğrenci indirimi AB vatandaşlarına yazılı",
    summary=("Museo de Málaga (Palacio de la Aduana) akredite AB vatandaşlarına ücretsizdir; diğer uyruklar 1,50 € öder, yani Türk vatandaşı olarak girişte 1,50 € ödersin. "
             "Alcazaba ve Gibralfaro'da indirimli bilet (3 €, ortak biletle 5 €) şu gruplara tanınır: Avrupa Gençlik Kartı sahipleri, engellilik oranı en az %33 olanlar ve büyük aile kartı sahipleri; "
             "65 yaş üstü, emekli ya da yasal işsiz olanlar ile öğrenciler için sayfada 'AB vatandaşı' şartı yazılıdır."),
    keywords="Museo de Málaga, Palacio de la Aduana, AB vatandaşı, diğer uyruklar, Alcazaba indirim, Türk vatandaşı müze, otras nacionalidades",
    stages='planning;new;settled', src=['280', '276'], order=1206, featured='Hayır',
    steps=[
        "Museo de Málaga'ya (Plaza Aduana s/n) gitmeden önce uyruğunun fiyatı belirlediğini bil: AB vatandaşı akreditasyonla ücretsiz, diğer uyruklar 1,50 €.",
        "Müzeye salı-cumartesi 09:00-21:00, pazar ve resmî tatillerde 09:00-15:00 arasında git; pazartesi kapalıdır.",
        "10 kişiyi geçen grupla (en çok 30 kişi) gidiyorsan, ziyaretlerin rehberli olmadığını bil.",
        "Alcazaba'da indirimli bilet alacaksan Avrupa Gençlik Kartı, %33+ engellilik belgesi ya da büyük aile kartını göster; 65 yaş, emeklilik, işsizlik ve öğrencilik indirimi sayfada AB vatandaşlarına yazılıdır.",
    ],
    documents=["Uyruğu gösteren kimlik belgesi", "Alcazaba indirimi için: Avrupa Gençlik Kartı, engellilik belgesi ya da büyük aile kartı"],
    timing="Museo de Málaga: salı-cumartesi 09:00-21:00, pazar ve resmî tatiller 09:00-15:00, pazartesi kapalı",
    cost="Museo de Málaga: AB vatandaşı ücretsiz, diğer uyruklar 1,50 €; Alcazaba indirimli 3 € (ortak biletle 5 €)",
    note="Alcazaba'da genel tarife 7 €, ortak bilet 10 €'dur; tüm bilet fiyatları Alcazaba kartında.",
    links=[('Ziyaret bilgisi', '280'), ('Tarifeyi gör', '276')],
    claims=[
        ('cost', "Museo de Málaga: akredite AB vatandaşları ücretsiz", "0", "EUR", "", '280', "Ciudadanos de la UE acreditados: gratuita."),
        ('cost', "Museo de Málaga: diğer uyruklar 1,50 €", "1,50", "EUR", "", '280', "Otras nacionalidades: 1,50 euros."),
        ('location', "Museo de Málaga adresi: Plaza Aduana s/n, 29015 Málaga", "", "", "", '280', "Plaza Aduana s/n, 29015 Málaga"),
        ('timing', "Museo de Málaga salı-cumartesi 09:00-21:00, pazar ve resmî tatiller 09:00-15:00, pazartesi kapalı", "09:00-21:00; 09:00-15:00", "saat", "", '280',
         "Martes a sábado de 09:00 a 21:00; domingos y festivos de 09:00 a 15:00. Lunes cerrado"),
        ('steps', "Grup 10 kişiden başlar, en çok 30 kişi", "10; 30", "kişi", "", '280', "Se considerará grupo a partir de 10 personas. El número máximo por grupo será de 30 personas."),
        ('steps', "Grup ziyaretleri rehberli değildir", "", "", "", '280', "Las visitas no son guiadas."),
        ('summary', "Alcazaba indirimli bilet 3 €, ortak (Alcazaba + Gibralfaro) 5 €", "3; 5", "EUR", "", '276', "REDUCIDA 3,00 € REDUCIDA CONJUNTA (Alcazaba y Castillo de Gibralfaro) 5,00 €"),
        ('summary', "Alcazaba indirimi: Avrupa Gençlik Kartı sahipleri", "", "", "", '276', "Titulares del carnet joven europeo."),
        ('summary', "Alcazaba indirimi: AB vatandaşı olup 65 yaş üstü, emekli ya da yasal işsiz olanlar", "65", "yaş", "", '276', "Ciudadanos de la UE mayores de 65 años, jubilados/as o en situación legal de desempleo."),
        ('summary', "Alcazaba indirimi: öğrenci olduğunu belgeleyen AB vatandaşları", "", "", "", '276', "Ciudadanos de la UE que acrediten su condición de estudiantes."),
        ('summary', "Alcazaba indirimi: engellilik oranı en az %33", "33", "%", "", '276', "Personas con discapacidad igual o superior al 33%."),
        ('summary', "Alcazaba indirimi: büyük aile kartı sahipleri", "", "", "", '276', "Titulares del carnet de familia numerosa."),
        ('note', "Alcazaba genel 7 €, ortak bilet 10 €", "7; 10", "EUR", "", '276', "GENERAL 7,00 € CONJUNTA (Alcazaba + Castillo de Gibralfaro) 10,00 €"),
    ],
)

ALC = dict(
    slug='alcazaba-ve-gibralfaro-bilet-fiyatlari-ve-saatleri',
    title="Alcazaba ve Gibralfaro Kalesi'ne giriş ne kadar, saat kaçta açık ve ne zaman ücretsiz?",
    subtitle="Genel 7 €, Alcazaba + Gibralfaro ortak bilet 10 €; yaz 09:00-20:00, kış 09:00-18:00; pazar 14:00'dan sonra ücretsiz",
    summary=("Alcazaba'ya tek başına 7 €, Alcazaba + Gibralfaro ortak biletine 10 € ödersin; indirimli tarife 3 € (ortak biletle 5 €), 10 kişiden grup tarifesi 5 € (ortak biletle 8 €). "
             "1 Nisan-31 Ekim arası 09:00-20:00 (son giriş 19:00), 1 Kasım-31 Mart arası 09:00-18:00 (son giriş 17:00) açıktır. "
             "6 yaş altı çocuklar ücretsizdir; şu an her pazar 14:00'dan sonra herkes ücretsiz girer."),
    keywords="Alcazaba Málaga, Castillo de Gibralfaro, giriş ücreti, bilet fiyatı, pazar ücretsiz, entrada conjunta, horarios",
    stages='planning;new;settled', src=['276'], order=1207, featured='Hayır',
    steps=[
        "Bilet türünü seç: yalnız Alcazaba (7 €) ya da Alcazaba + Gibralfaro ortak bilet (10 €).",
        "Yaz döneminde (1 Nisan-31 Ekim) en geç 19:00'da, kış döneminde (1 Kasım-31 Mart) en geç 17:00'de içeri gir; son giriş kapanıştan bir saat önceki gruptur.",
        "Ücretsiz girmek istiyorsan pazar günü 14:00'dan sonra git.",
        "10 kişilik grupla gidiyorsan grup tarifesini (5 € ya da ortak biletle 8 €) iste.",
    ],
    timing="Yaz 1 Nisan-31 Ekim: 09:00-20:00; kış 1 Kasım-31 Mart: 09:00-18:00; ücretsiz: pazar 14:00'dan sonra",
    cost="Genel 7 €, ortak bilet 10 €, indirimli 3 € (ortak 5 €), grup 5 € (ortak 8 €)",
    note="Giriş ücretsiz olan gruplar: 6 yaş altı çocuklar ve ruhsatlı turist rehberleri (mesleki faaliyette).",
    links=[('Tarifeyi gör', '276')],
    claims=[
        ('timing', "Kış saatleri: 1 Kasım-31 Mart 09:00-18:00, son giriş 17:00", "09:00-18:00", "saat", "1 Kasım-31 Mart", '276', "Invierno: Del 1 noviembre al 31 de marzo de 9:00 a 18:00 (último pase a las 17.00)"),
        ('timing', "Yaz saatleri: 1 Nisan-31 Ekim 09:00-20:00, son giriş 19:00", "09:00-20:00", "saat", "1 Nisan-31 Ekim", '276', "Verano: Del 1 abril al 31 de octubre de 09:00 a 20:00 (último pase a las 19.00)"),
        ('steps', "Son giriş kapanıştan bir saat önce", "1", "saat", "", '276', "El último pase será una hora antes de la hora de cierre."),
        ('cost', "Genel tarife 7 €, ortak bilet 10 €", "7; 10", "EUR", "", '276', "GENERAL 7,00 € CONJUNTA (Alcazaba + Castillo de Gibralfaro) 10,00 €"),
        ('cost', "Grup tarifesi 5 €, grup ortak bilet 8 €", "5; 8", "EUR", "", '276', "GRUPOS (Min. 10 pax.) 5,00 € GRUPOS CONJUNTA (Alcazaba y Castillo de Gibralfaro) 8,00 €"),
        ('cost', "İndirimli tarife 3 €, indirimli ortak bilet 5 €", "3; 5", "EUR", "", '276', "REDUCIDA 3,00 € REDUCIDA CONJUNTA (Alcazaba y Castillo de Gibralfaro) 5,00 €"),
        ('steps', "Grup tarifesi 10 kişiden başlar", "10", "kişi", "", '276', "Tarifa grupos: a partir de 10 personas"),
        ('summary', "6 yaş altı çocuklar ücretsiz", "6", "yaş", "", '276', "Personas menores de 6 años."),
        ('summary', "Şu an her pazar 14:00'dan sonra herkes için ücretsiz", "14:00", "saat", "her pazar", '276', "Actualmente: todos los domingos a partir de las 14:00."),
        ('note', "Resmî turist rehberleri mesleki faaliyetlerinde ücretsiz", "", "", "", '276', "Guías oficiales de turismo en el ejercicio de su actividad profesional."),
    ],
)

TR = dict(
    slug='teatro-romano-ucretsiz-giris-ve-saatler',
    title="Málaga Roma Tiyatrosu'na (Teatro Romano) giriş ücretsiz mi, hangi saatlerde açık, ne zaman kapanır?",
    subtitle="Ücretsiz, rezervasyonsuz; salı-cumartesi 10:00-18:00, pazar ve resmî tatil 10:00-16:00; aşırı sıcakta kapanabilir",
    summary=("Teatro Romano'ya giriş ücretsizdir ve serbest ziyaret için rezervasyon gerekmez; yalnız güvenlik için kapasite sınırı vardır. "
             "Salı-cumartesi 10:00-18:00, pazar ve resmî tatillerde 10:00-16:00 açıktır; kapanıştan önceki son 30 dakikada içeri girilemez. "
             "AEMET turuncu ya da kırmızı sıcaklık uyarısı verirse alan halka kapanabilir. Adres: Calle Alcazabilla s/n."),
    keywords="Teatro Romano Málaga, Roma Tiyatrosu, ücretsiz giriş, Alcazabilla, saatler, aşırı sıcak kapanış, enclave arqueológico",
    stages='planning;new;settled', src=['281'], order=1208, featured='Hayır',
    steps=[
        "Calle Alcazabilla s/n adresine git; serbest ziyaret için rezervasyon yapma, sıra kapasiteye göre yürür.",
        "Salı-cumartesi 10:00-18:00, pazar ve resmî tatillerde 10:00-16:00 arasında, en geç kapanıştan 30 dakika önce gir.",
        "Rehberli ziyaret istersen 951 501 115'i ara ya da TRomanoMalaga.aaiicc@juntadeandalucia.es adresine yaz ve rezervasyon yaptır.",
        "Yaz aylarında AEMET turuncu ya da kırmızı uyarı varsa gitmeden önce telefonla ya da e-postayla alanın açık olup olmadığını sor.",
    ],
    timing="Salı-cumartesi 10:00-18:00; pazar ve resmî tatiller 10:00-16:00; pazartesi kapalı; 1 ve 6 Ocak, 1 Mayıs, 24, 25 ve 31 Aralık kapalı",
    cost="Ücretsiz",
    note="Hayvan girişi yasaktır (engelli yardım köpekleri hariç). Diğer resmî tatillerde açık olup olmadığını e-postayla sor.",
    links=[('Ziyaret bilgisi', '281')],
    claims=[
        ('cost', "Giriş ücretsiz, güvenlik için kapasite sınırı var", "0", "EUR", "", '281', "Gratuito. Acceso permitido hasta límite de aforo por seguridad de visitantes y estructuras."),
        ('timing', "Salı-cumartesi 10:00-18:00, pazar ve resmî tatiller 10:00-16:00", "10:00-18:00; 10:00-16:00", "saat", "", '281', "De martes a sábado de 10:00 a 18:00 h. Domingos y festivos de 10:00 a 16:00 h."),
        ('timing', "Kapalı günler: 1 ve 6 Ocak, 1 Mayıs, 24, 25, 31 Aralık", "", "", "", '281', "Cerrado: 1 y 6 de enero, 1 de mayo, 24, 25 y 31 de diciembre."),
        ('steps', "Serbest ziyaret için rezervasyon gerekmez", "", "", "", '281', "No es necesario reservar entrada para la visita libre."),
        ('steps', "Rehberli ziyaret için rezervasyon önerilir: tel. 951 501 115", "951 501 115", "", "", '281', "Para las visitas guiadas se recomienda reserva, a través del teléfono 951 501 115"),
        ('steps', "Kapanıştan önceki son 30 dakikada giriş yok", "30", "dakika", "", '281', "No se permitirá el acceso de los visitantes al enclave en los 30 minutos previos al cierre."),
        ('steps', "Aşırı sıcakta alan halka kapanabilir", "", "", "", '281', "este enclave podrá cerrar sus puertas al público ante episodios de temperaturas excesivas"),
        ('steps', "Kapanış kararında AEMET turuncu ve kırmızı uyarıları esas alınır", "", "", "", '281',
         "se tomarán en consideración los avisos de alerta nivel naranja y alerta nivel rojo notificados por la Agencia Estatal de Meteorología (AEMET)"),
        ('note', "Hayvan girişi yasak, engelli yardım köpekleri hariç", "", "", "", '281', "no está permitida la entrada con animales, a excepción de los perros de asistencia a personas con discapacidad"),
        ('note', "Diğer resmî tatillerde açıklık e-postayla sorulur", "", "", "", '281', "En otros festivos nacionales, autonómicos y/o locales, consultar apertura por correo electrónico."),
        ('location', "Adres: Calle Alcazabilla, s/n, 29015 Málaga", "", "", "", '281', "Calle Alcazabilla, s/n, 29015 Málaga"),
        ('steps', "E-posta: TRomanoMalaga.aaiicc@juntadeandalucia.es", "", "", "", '281', "TRomanoMalaga.aaiicc@juntadeandalucia.es"),
    ],
)

KAT = dict(
    slug='malaga-katedrali-giris-ucretleri',
    title="Málaga Katedrali'ne giriş ne kadar; Málaga sakinleri, çocuklar ve engelliler ücretsiz mi?",
    subtitle="Genel 10 € (sesli rehber dahil); Málaga sakinleri, engelliler ve 13 yaş altı ücretsiz (sesli rehbersiz); kapıdan ya da çevrimiçi aynı fiyat",
    summary=("Katedral'e genel giriş 10 €'dur ve ücrete sesli rehber dahildir. Málaga'da oturanlar, engelliler ve 13 yaş altı çocuklar için giriş ücretsizdir; bu ücretsiz bilet sesli rehberi kapsamaz ve yalnız Katedral için geçerlidir. "
             "Diğer fiyatlar: 65 yaş üstü 9 €, 13-17 yaş 6 €, 18-25 yaşındaki öğrenciler 7 €, 15'ten fazla kişilik gruplar 7 €. "
             "Biletin kapıdan ya da çevrimiçi aynı fiyatı vardır. İçeride 'decoro' ile giyinmek zorunludur."),
    keywords="Catedral de Málaga, katedral giriş ücreti, Málaga sakini ücretsiz, entrada gratuita residentes, sesli rehber, VR deneyimi",
    stages='planning;new;settled', src=['287'], order=1209, featured='Hayır',
    steps=[
        "Bilet türünü yaşına ve statüne göre seç: genel 10 €, 65 yaş üstü 9 €, 13-17 yaş 6 €, 18-25 yaş öğrenci 7 €, grup (15+ kişi) 7 €.",
        "Málaga'da oturuyorsan, engellisen ya da 13 yaşın altındaysan ücretsiz (GRATUITA) bileti iste; sesli rehber bu biletle verilmez.",
        "Bileti Katedral'in kapısından ya da çevrimiçi al; fiyat aynıdır.",
        "Ziyaret için uygun giyin (vestir con decoro); 26 Ekim-29 Mart arasında pazartesi-cuma 10:30-18:30, cumartesi 10:30-18:00, pazar 14:00-18:00 gidebilirsin.",
    ],
    timing="26 Ekim-29 Mart: pazartesi-cuma 10:30-18:30, cumartesi 10:30-18:00, pazar 14:00-18:00; son giriş kapanıştan 45 dakika önce",
    cost="Genel 10 €; 65+ 9 €; 13-17 yaş 6 €; öğrenci 7 €; grup 7 €; Málaga sakini, engelli ve 13 yaş altı ücretsiz; Katedral + VR deneyimi 15 €",
    note="Ücretsiz bilet yalnız Katedral'i kapsar ve sesli rehber içermez. Katedral + 360° sanal gerçeklik deneyimi bileti genel 15 €'dur.",
    links=[('Bilet al', '287'), ('Tarifeyi gör', '287')],
    claims=[
        ('cost', "Katedral genel 10 €, grup 7 €, 65+ 9 €, 13-17 yaş 6 €, öğrenci 7 €, okul grubu 4 €, Málaga ücretsiz", "10; 7; 9; 6; 7; 4", "EUR", "",
         '287', "Catedral 10.00 € 7.00 € 9.00 € 6.00 € 7.00 € 4.00 € GRATIS*"),
        ('summary', "65 yaş üstü: MAYORES", "65", "yaş", "", '287', "MAYORES → mayores de 65 años"),
        ('summary', "Grup bileti 15'ten fazla kişi için", "15", "kişi", "", '287', "GRUPOS → más de 15 personas"),
        ('summary', "Genç bileti 13-17 yaş", "13; 17", "yaş", "", '287', "JÓVENES → de 13 a 17 años"),
        ('summary', "Öğrenci bileti 18-25 yaş", "18; 25", "yaş", "", '287', "ESTUDIANTES → estudiantes de 18 a 25 años"),
        ('summary', "Ücretsiz bilet: Málaga'da oturanlar, engelliler, 13 yaş altı", "13", "yaş", "", '287',
         "GRATUITA* (Catedral) → residentes en Málaga, personas con capacidades diferentes y menores de 13 años"),
        ('summary', "Ücretsiz bilet sesli rehber içermez, yalnız Katedral için geçerlidir", "", "", "", '287', "* La entrada GRATUITA no incluye audioguía y es válida solo para la Catedral."),
        ('summary', "Giriş fiyatı sesli rehberi içerir (10 dilde)", "10", "dil", "", '287', "El precio de la entrada individual incluye GRATIS el uso de una audioguía disponible en 10 idiomas"),
        ('steps', "Bilet kapıdan alınır", "", "", "", '287', "Puede adquirir su entrada directamente en la puerta de la Catedral."),
        ('steps', "Çevrimiçi bilet kapıdakiyle aynı fiyatta", "", "", "", '287', "También puede adquirir su entrada online en el botón de más abajo (evitando colas y al mismo precio que en taquilla)."),
        ('steps', "Ziyaret için uygun giyinmek gerekir", "", "", "", '287', "Es necesario VESTIR CON DECORO en el interior del templo."),
        ('timing', "26 Ekim-29 Mart saatleri", "10:30-18:30; 10:30-18:00; 14:00-18:00", "saat", "26 Ekim-29 Mart", '287',
         "Del 26 de Octubre al 29 de Marzo Lunes a Viernes: 10:30 a 18:30. Sábados: 10:30 a 18:00 Domingo: 14:00 a 18:00"),
        ('timing', "Son giriş kapanıştan 45 dakika önce", "45", "dakika", "", '287', "*Último acceso 45 minutos antes del cierre. Desalojo 10 minutos antes del cierre."),
        ('cost', "Katedral + VR deneyimi genel 15 €", "15", "EUR", "", '287', "Catedral + Experiencia VR 15.00 €"),
    ],
)

add([C, D, ALC, TR, KAT])
