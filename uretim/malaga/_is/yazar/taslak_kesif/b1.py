from lib import add

NO_GROUP = ('steps', "Ücretsiz günlerde ve saatlerde grup rezervasyonu ve resmî rehber anlatımı kabul edilmez", "", "", "", '282',
            "En los días y tramos horarios con entrada gratuita no se aceptan reservas de grupos ni las explicaciones a grupos por parte de guías oficiales.")

P = dict(
    slug='picasso-muzeleri-ucretsiz-giris-gunleri',
    title="Museo Picasso Málaga ve Casa Natal Picasso'ya hangi gün ve saatte ücretsiz girilir?",
    subtitle="Museo Picasso: pazar günü son iki saat ve yılda 4 gün; Casa Natal: pazar 16:00-20:00 ve yılda 5 gün",
    summary=("Museo Picasso Málaga'da her pazar kapanıştan önceki son iki saat herkese ücretsizdir (kasalar kapanıştan yarım saat önce kapanır); "
             "ayrıca 28 Şubat, 18 Mayıs, 27 Eylül ve müzenin açılış yıldönümü olan 27 Ekim'de giriş ücretsizdir. "
             "Casa Natal Picasso'da her pazar 16:00-20:00 arası ücretsizdir; ek olarak 28 Şubat, Mayıs'taki Noche en Blanco, 18 Mayıs, 27 Eylül "
             "ve Picasso'nun doğumunu anma günü olan 25 Ekim'de giriş ücretsizdir."),
    keywords="Museo Picasso Málaga, Casa Natal Picasso, ücretsiz müze, pazar ücretsiz, Noche en Blanco, entrada gratuita, Picasso doğum günü",
    stages='planning;new;settled', src=['275', '282'], order=1201, featured='Evet',
    steps=[
        "Casa Natal için pazar günü 16:00-20:00 arasını seç; müzeye kabul kapanıştan 15 dakika önce biter.",
        "Museo Picasso için pazar günü kapanıştan önceki son iki saati seç: Kasım-Şubat 16:00'dan, Mart-Haziran ve Eylül-Ekim 17:00'den, Temmuz-Ağustos 18:00'den başlar.",
        "28 Şubat, 18 Mayıs ve 27 Eylül'ü iki müze için de ücretsiz gün olarak takvimine yaz; 27 Ekim yalnız Museo Picasso'da, 25 Ekim yalnız Casa Natal'da ücretsizdir.",
        "Grupla gidiyorsan ücretsiz günleri ve saatleri seçme: Casa Natal bu zamanlarda grup rezervasyonu almaz.",
    ],
    timing="Her pazar; 28 Şubat, 18 Mayıs, 27 Eylül; Museo Picasso'da 27 Ekim; Casa Natal'da Mayıs'ta bir cumartesi (Noche en Blanco) ve 25 Ekim",
    cost="Ücretsiz",
    note="Ücretsiz girişler yalnız müze ziyaretini kapsar; kültürel ve eğitsel etkinlikler ücretsiz değildir.",
    links=[('Tarifeyi gör', '275'), ('Tarifeyi gör', '282')],
    claims=[
        ('summary', "Museo Picasso pazarları kapanıştan önceki son iki saatte herkese ücretsiz", "son 2 saat", "saat", "her pazar", '275',
         "Entrada libre para todos los públicos cada domingo durante las dos últimas horas de apertura (cierre de taquillas media hora antes)"),
        ('summary', "Museo Picasso 28 Şubat (Endülüs Günü) ve 18 Mayıs (Müzeler Günü) ücretsiz", "28 Şubat; 18 Mayıs", "gün", "yıllık", '275',
         "Día de Andalucía (28 febrero), Día Internacional de los Museos (18 mayo)"),
        ('summary', "Museo Picasso 27 Eylül (Dünya Turizm Günü) ve 27 Ekim (açılış yıldönümü) ücretsiz", "27 Eylül; 27 Ekim", "gün", "yıllık", '275',
         "Día Mundial del Turismo (27 septiembre) y Aniversario de apertura del museo (27 octubre)"),
        ('steps', "Museo Picasso Kasım-Şubat arası 18:00'da kapanır; son iki saat 16:00'da başlar (hesap)", "18:00", "saat", "Kasım-Şubat", '275', "Noviembre-febrero: de 10 a 18 h"),
        ('steps', "Museo Picasso Mart-Haziran arası 19:00'da kapanır; son iki saat 17:00'de başlar (hesap)", "19:00", "saat", "Mart-Haziran", '275', "Marzo-junio: de 10 a 19 h"),
        ('steps', "Museo Picasso Eylül-Ekim arası 19:00'da kapanır; son iki saat 17:00'de başlar (hesap)", "19:00", "saat", "Eylül-Ekim", '275', "Septiembre-octubre: de 10 a 19 h"),
        ('steps', "Museo Picasso Temmuz-Ağustos arası 20:00'de kapanır; son iki saat 18:00'de başlar (hesap)", "20:00", "saat", "Temmuz-Ağustos", '275', "Julio-agosto: de 10 a 20 h"),
        ('note', "İndirim ve ücretsizlikler yalnız müze ziyaretine uygulanır, kültürel ve eğitsel etkinliklere uygulanmaz", "", "", "", '275',
         "Los descuentos y gratuidades solamente se aplicarán a las tarifas para visitar el Museo, no a las actividades culturales ni educativas."),
        ('summary', "Casa Natal pazarları 16:00-20:00 arası ücretsiz", "16:00-20:00", "saat", "her pazar", '282', "La entrada es gratuita todos los domingos de 16:00 a 20:00 h"),
        ('steps', "Casa Natal'da kabul kapanıştan 15 dakika önce biter", "15", "dakika", "", '282', "La admisión de público terminará 15 minutos antes del cierre del museo."),
        ('summary', "Casa Natal 28 Şubat (Endülüs Günü) ücretsiz", "28 Şubat", "gün", "yıllık", '282', "Día de Andalucía (28 de febrero)"),
        ('summary', "Casa Natal Noche en Blanco (Mayıs, değişken tarih) ücretsiz", "Mayıs", "", "yıllık", '282', "Noche en blanco (mayo, en fecha variable)"),
        ('summary', "Casa Natal 18 Mayıs ücretsiz", "18 Mayıs", "gün", "yıllık", '282', "Día Internacional de los Museos (18 de mayo)"),
        ('summary', "Casa Natal 27 Eylül ücretsiz", "27 Eylül", "gün", "yıllık", '282', "Día Internacional del Turismo (27 de septiembre)"),
        ('summary', "Casa Natal 25 Ekim (Picasso'nun doğumunu anma günü) ücretsiz", "25 Ekim", "gün", "yıllık", '282', "Conmemoración del nacimiento de Pablo Ruiz Picasso (25 de octubre)"),
        NO_GROUP,
    ],
)

Q = dict(
    slug='pompidou-ve-thyssen-ucretsiz-giris-gunleri',
    title="Centre Pompidou Málaga ve Museo Carmen Thyssen'e hangi gün ve saatte ücretsiz girilir?",
    subtitle="İkisinde de pazar 16:00'dan sonra ücretsiz; Thyssen'de 28 Şubat, 24 Mart, 18 Mayıs, 27 Eylül; Pompidou'da Noche en Blanco, 18 Mayıs, 27 Eylül",
    summary=("Centre Pompidou Málaga'da pazar günleri 16:00'dan kapanışa kadar herkes ücretsiz girer; Museo Carmen Thyssen'de de pazarları 16:00'dan sonra giriş ücretsizdir. "
             "Thyssen yılda dört gün (28 Şubat Endülüs Günü, 24 Mart müze yıldönümü, 18 Mayıs Müzeler Günü, 27 Eylül Turizm Günü) ve Noche en Blanco'da belirli saatlerde ücretsizdir. "
             "Pompidou'nun ücretsiz özel günleri Noche en Blanco (Mayıs'ta bir cumartesi), 18 Mayıs ve 27 Eylül'dür."),
    keywords="Centre Pompidou Málaga, Carmen Thyssen, pazar ücretsiz, ücretsiz müze günü, Noche en Blanco, entrada gratuita domingo",
    stages='planning;new;settled', src=['277', '279'], order=1202, featured='Hayır',
    steps=[
        "Pompidou için pazar günü 16:00 ile 20:00 arasını seç; kabul kapanıştan 30 dakika önce biter.",
        "Thyssen için pazar günü 16:00'dan sonrasını seç; müze 20:00'de kapanır.",
        "28 Şubat, 24 Mart, 18 Mayıs ve 27 Eylül'ü Thyssen'in; Mayıs'taki Noche en Blanco, 18 Mayıs ve 27 Eylül'ü Pompidou'nun ücretsiz günleri olarak kaydet.",
        "Pompidou'ya grupla gidiyorsan ücretsiz saatleri seçme: bu zamanlarda grup rezervasyonu kabul edilmez.",
    ],
    timing="Her pazar 16:00'dan sonra; yıllık özel günler (Thyssen: 4 gün, Pompidou: 3 gün)",
    cost="Ücretsiz",
    note="Pompidou salı günleri, Thyssen pazartesi günleri kapalıdır (Thyssen lunes festivo günlerinde açıktır).",
    links=[('Tarifeyi gör', '277'), ('Bilgi al', '279')],
    claims=[
        ('summary', "Pompidou pazarları 16:00'dan kapanışa kadar herkese ücretsiz", "16:00", "saat", "her pazar", '277', "para todo el público los domingos a partir de las 16:00 horas y hasta la hora de cierre"),
        ('summary', "Pompidou'da Noche en Blanco ücretsiz günlerden biri", "Mayıs", "", "yıllık", '277', "Noche en Blanco (un sábado de mayo, en fecha variable)"),
        ('summary', "Pompidou'da 18 Mayıs ücretsiz gün", "18 Mayıs", "gün", "yıllık", '277', "Día Internacional de los Museos (18 de mayo)"),
        ('summary', "Pompidou'da 27 Eylül ücretsiz gün", "27 Eylül", "gün", "yıllık", '277', "Día Internacional del Turismo (27 de septiembre)"),
        ('steps', "Pompidou salı dışında 09:30-20:00 açıktır", "9:30-20:00", "saat", "", '277', "9:30 - 20:00h (incluyendo festivos)"),
        ('steps', "Pompidou'ya kabul kapanıştan 30 dakika önce biter", "30", "dakika", "", '277', "La admisión del público se permite hasta 30 minutos antes del cierre del museo."),
        ('note', "Pompidou her salı kapalıdır", "salı", "", "", '277', "Cerrado todos los martes, 25 de diciembre y 1 de enero."),
        ('steps', "Pompidou ücretsiz günlerde ve saatlerde grup rezervasyonu ve resmî rehber anlatımı kabul etmez", "", "", "", '277',
         "En los días y tramos horarios con entrada gratuita no se aceptan reservas de grupos ni las explicaciones a grupos por parte de guías oficiales."),
        ('summary', "Thyssen pazarları 16:00'dan sonra ücretsiz", "16:00", "saat", "her pazar", '279', "Además, todos los domingos, a partir de las 16.00h el acceso gratuito."),
        ('summary', "Thyssen'de 28 Şubat, 24 Mart, 18 Mayıs ve 27 Eylül ücretsiz", "28 Şubat; 24 Mart; 18 Mayıs; 27 Eylül", "gün", "yıllık", '279',
         "el 28 de febrero (Día de Andalucía), el 24 de marzo (Aniversario del Museo), el 18 de Mayo (Día Internacional de los Museos) y el 27 de septiembre (Día Internacional del Turismo)"),
        ('summary', "Thyssen Noche en Blanco'da belirli saatlerde ücretsiz açılır", "", "", "Mayıs", '279', "el Museo abre sus puertas de forma gratuita determinadas horas del día"),
        ('steps', "Thyssen salı-pazar 10:00-20:00 arası açıktır", "10:00-20:00", "saat", "", '279', "Martes a domingo: Abierto de 10.00 a 20.00 h."),
        ('note', "Thyssen pazartesi kapalıdır (festivo pazartesiler hariç)", "pazartesi", "", "", '279', "Lunes cerrado (excepto lunes festivos)."),
    ],
)

B1 = dict(
    slug='picasso-ve-thyssen-ucretsiz-giris-kategorileri',
    title="İşsizsen, Málaga Üniversitesi öğrencisiysen ya da engelli kartın varsa Museo Picasso ve Thyssen'e ücretsiz girer misin?",
    subtitle="SEPE kayıtlı işsiz, UMA öğrencisi, öğretmen, engelli ve basın ücretsiz; çocuk eşiği Picasso'da 17, Thyssen'de 18 yaş altı",
    summary=("Evet: SEPE'ye (devlet iş kurumu) kayıtlı işsizler, Universidad de Málaga (UMA) öğrencileri, öğretmenler, engelli kişiler, basın mensupları ve ICOM üyeleri "
             "Museo Picasso Málaga'ya ücretsiz girer; engelli ziyaretçiyle bir refakatçi de ücretsizdir. Thyssen'de de işsizler, UMA öğrencileri, "
             "engellilik oranı en az %33 olanlar, Bellas Artes ve Historia del Arte öğretmen ve öğrencileri ücretsizdir. Çocuk eşiği Picasso'da 17 yaş altı, "
             "Thyssen'de 18 yaş altıdır (13 yaş altı yetişkinle). Genel bilet Picasso'da 13 € (indirimli 11 €), Thyssen'de 12 € (arkeolojik alanla 15 €; indirimli 8 € ve 10 €); "
             "Thyssen'de indirimi Málaga ili sakinleri de alır."),
    keywords="ücretsiz müze, işsiz, SEPE, UMA öğrencisi, engelli, Museo Picasso, Thyssen, reducida, tarifa gratuita",
    stages='planning;new;settled', src=['275', '278'], order=1203, featured='Hayır',
    steps=[
        "Hangi kategoride olduğunu belirle: işsiz, UMA öğrencisi, öğretmen, engelli, basın ya da ICOM üyesi.",
        "Kategorini gösteren akreditasyon belgesini (ör. SEPE kaydı, UMA öğrenci kartı, engellilik belgesi) yanında götür; Thyssen ücretsizliği belgeyle (con acreditación) tanır.",
        "Picasso müzesi biletleri çevrimiçi satar; tükenmişse ve az yoğun anlarda kasadan da alınır.",
        "Thyssen'de Málaga ili sakiniysen indirimli bilet (8 €, arkeolojik alanlı bilette 10 €) için bunu belgeyle göster.",
    ],
    documents=["Kategoriyi gösteren akreditasyon belgesi (işsizlik kaydı, öğrenci kartı ya da engellilik belgesi gibi)"],
    timing="Müze açık olduğu her gün; Thyssen tarifeleri 2026'dan itibaren geçerli",
    cost="Ücretsiz (kategoriye göre); genel bilet Picasso 13 €, Thyssen 12 €",
    note="Picasso'da indirimli bilet 65 yaş üstü, Avrupa Gençlik Kartı sahipleri ve 26 yaş altı öğrenciler içindir. Thyssen'de indirimli bilet 65 yaş üstü ve emekliler, 26 yaş altı öğrenciler, Carné Joven Euro sahipleri, Málaga ili sakinleri ve büyük aileler içindir.",
    links=[('Bilgi al', '275'), ('Tarifeyi gör', '278')],
    claims=[
        ('summary', "Museo Picasso: SEPE'ye kayıtlı işsizler ücretsiz", "", "", "", '275', "Desempleados inscritos en el SEPE"),
        ('summary', "Museo Picasso: UMA öğrencileri ücretsiz", "", "", "", '275', "Estudiantes de la Universidad de Málaga (UMA)"),
        ('summary', "Museo Picasso: 17 yaş altı ücretsiz", "17", "yaş", "", '275', "Menores de 17 años"),
        ('summary', "Museo Picasso: engelli kişi ve bir refakatçisi ücretsiz", "", "", "", '275', "Personas con diversidad funcional (y un acompañante)"),
        ('summary', "Museo Picasso: öğretmenler ücretsiz", "", "", "", '275', "Docentes"),
        ('summary', "Museo Picasso: ICOM üyeleri ücretsiz", "", "", "", '275', "Miembros del ICOM"),
        ('summary', "Museo Picasso: gazeteciler ücretsiz", "", "", "", '275', "Periodistas"),
        ('summary', "Museo Picasso genel bilet 13 €, indirimli 11 €", "13; 11", "EUR", "", '275', "13€ / Reducida 11€"),
        ('note', "Museo Picasso indirimli bilet: Avrupa Gençlik Kartı sahipleri", "", "", "", '275', "Titulares del Carné Joven Europeo"),
        ('note', "Museo Picasso indirimli bilet: 65 yaş üstü", "65", "yaş", "", '275', "Mayores de 65 años"),
        ('note', "Museo Picasso indirimli bilet: 26 yaş altı öğrenciler", "26", "yaş", "", '275', "Estudiantes menores de 26 años"),
        ('summary', "Thyssen: 18 yaş altı ve yetişkin eşliğinde 13 yaş altı ücretsiz", "18; 13", "yaş", "", '278', "Menores de 18 años y menores de 13 acompañados"),
        ('summary', "Thyssen: engellilik oranı en az %33 olanlar ücretsiz", "33", "%", "", '278', "Personas con discapacidad igual o superior al 33%"),
        ('summary', "Thyssen: SEPE'ye kayıtlı işsizler ücretsiz", "", "", "", '278', "Desempleados inscritos en el Servicio Público de Empleo Estatal"),
        ('summary', "Thyssen: UMA öğrencileri ücretsiz", "", "", "", '278', "Estudiantes de la Universidad de Málaga"),
        ('summary', "Thyssen: Bellas Artes / Historia del Arte öğretmen ve öğrencileri ücretsiz", "", "", "", '278', "Profesores y alumnos de enseñanza reglada en Bellas Artes o Historia del Arte"),
        ('summary', "Thyssen genel bilet 12 € (arkeolojik alanla 15 €)", "12; 15", "EUR", "2026", '278', "12 € / 15 € con yacimiento"),
        ('summary', "Thyssen indirimli bilet 8 € (arkeolojik alanla 10 €)", "8; 10", "EUR", "2026", '278', "8 € / 10 € con yacimiento"),
        ('note', "Thyssen indirimli bilet: Málaga ili sakinleri", "", "", "", '278', "Residentes en la provincia de Málaga"),
        ('note', "Thyssen indirimli bilet: 65 yaş üstü ve emekliler", "65", "yaş", "", '278', "Mayores de 65 años y pensionistas"),
        ('note', "Thyssen indirimli bilet: büyük aileler", "", "", "", '278', "Familias numerosas"),
        ('timing', "Thyssen tarifeleri 2026'dan itibaren geçerli", "2026", "", "", '278', "Tarifas válidas a partir de 2026."),
        ('steps', "Thyssen ücretsiz tarife akreditasyonla (belgeyle) tanınır", "", "", "", '278', "Tarifa gratuita (con acreditación):"),
        ('steps', "Picasso'da biletler çevrimiçi satışa sunulur, tükenirse kasadan alınır", "", "", "", '275',
         "Todas nuestras entradas están a la venta online. Si están agotadas, en momentos de poca afluencia también se pueden adquirir en la taquilla del Museo."),
    ],
)

B2 = dict(
    slug='pompidou-ve-casa-natal-ucretsiz-giris-kategorileri',
    title="Avrupa Gençlik Kartın, belediye kütüphane üyeliğin ya da işsizlik kaydın varsa Pompidou ve Casa Natal Picasso'ya ücretsiz girer misin?",
    subtitle="İkisinde de işsizler, 18 yaş altı, engelliler ve gençlik kartı sahipleri ücretsiz; Casa Natal'da Málaga belediye kütüphanesi üyeleri de",
    summary=("Centre Pompidou Málaga'da resmen işsiz olanlar, 18 yaş altı, Carné Joven Euro sahipleri, belgeli engelliler, sanat tarihi ve güzel sanatlar öğretmen ve öğrencileri, "
             "müze çalışanları ve ICOM üyeleri, resmî turist rehberleri ve basın kartlıları her gün ücretsiz girer. Casa Natal Picasso'da liste benzerdir; "
             "buna ek olarak Málaga belediye kütüphanesi üyeleri (kartla) ve 30 yaş altı Avrupa Gençlik Kartı sahipleri ücretsizdir, engelli kişinin zorunlu refakatçisi de ücretsiz girer. "
             "Çocuk eşiği iki müzede de 18 yaş altıdır; Casa Natal'da 13 yaş altı çocuk yetişkinle girmelidir."),
    keywords="Pompidou Málaga ücretsiz, Casa Natal ücretsiz, Carné Joven, kütüphane üyeliği, işsiz, engelli, ücretsiz müze",
    stages='planning;new;settled', src=['277', '282'], order=1204, featured='Hayır',
    steps=[
        "Kategorini belirle: işsiz, 18 yaş altı, gençlik kartı, belediye kütüphanesi üyesi, engelli, öğretmen ya da öğrenci (sanat tarihi/güzel sanatlar).",
        "Kategoriyi kanıtlayan belgeyi yanına al: Casa Natal ücretsizliği için kütüphane üyeliğini kartla (carnet) göstermen gerekir.",
        "Engelli ziyaretçiysen Casa Natal'da zorunlu refakatçin de ücretsiz girer; bunu girişte söyle.",
        "13 yaş altı çocukla Casa Natal'a gidiyorsan çocuğun yanında bir yetişkin olsun.",
    ],
    documents=["Kategoriyi gösteren belge (işsizlik kaydı, gençlik kartı, kütüphane üyelik kartı, engellilik belgesi gibi)"],
    timing="Müze açık olduğu her gün",
    cost="Ücretsiz (kategoriye göre)",
    note="Casa Natal'da Avrupa Gençlik Kartı için üst yaş sınırı 30'dur.",
    links=[('Tarifeyi gör', '277'), ('Tarifeyi gör', '282')],
    claims=[
        ('summary', "Pompidou: resmen işsizler, 18 yaş altı ve Carné Joven Euro sahipleri ücretsiz", "18", "yaş", "", '277',
         "personas en situación oficial de desempleo, menores de 18 años, poseedores del carnet joven euro"),
        ('summary', "Pompidou: belgeli engelliler ücretsiz", "", "", "", '277', "personas discapacitadas con acreditación"),
        ('summary', "Pompidou: sanat tarihi ve güzel sanatlar üniversite öğretmen ve öğrencileri ücretsiz", "", "", "", '277',
         "profesorado universitario de Historia del Arte y Bellas Artes, alumnos universitarios de Historia del Arte y Bellas Artes"),
        ('summary', "Pompidou: müze çalışanları, ICOM üyeleri, resmî rehberler ve basın kartlıları ücretsiz", "", "", "", '277',
         "empleados de museos y miembros del ICOM, guías turísticos con acreditación oficial, poseedores de carné de prensa"),
        ('summary', "Casa Natal: 18 yaş altı ücretsiz, 13 yaş altı yetişkinle", "18; 13", "yaş", "", '282', "Menores de 18 años (los menores de 13 años deben ir acompañados por un adulto)"),
        ('summary', "Casa Natal: 30 yaş altı Avrupa Gençlik Kartı sahipleri ücretsiz", "30", "yaş", "", '282', "Poseedores del carnet joven europeo (menores de 30 años)"),
        ('summary', "Casa Natal: Málaga belediye kütüphanesi üyeleri kartla ücretsiz", "", "", "", '282', "Socios de las bibliotecas municipales de Málaga, acreditados con carnet"),
        ('summary', "Casa Natal: resmen işsizler ücretsiz", "", "", "", '282', "Personas en situación oficial de desempleo"),
        ('summary', "Casa Natal: engelli kişinin zorunlu refakatçisi de ücretsiz", "", "", "", '282',
         "También podrá acceder al museo de forma gratuita la persona que lo acompañe, siempre y cuando ésta sea imprescindible para que pueda realizar su visita"),
        ('summary', "Casa Natal: sanat tarihi/güzel sanatlar öğretmen ve öğrencileri ücretsiz", "", "", "", '282', "Docentes y estudiantes universitarios de Historia del Arte y Bellas Artes, acreditados"),
    ],
)

add([P, Q, B1, B2])
