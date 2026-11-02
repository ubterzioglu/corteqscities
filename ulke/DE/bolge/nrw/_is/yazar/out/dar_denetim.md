# NRW editör sonrası dar denetim

**Sayım: ciddi 0 / orta 3 / küçük 10** (14 karttan 9'unda bulgu var; 5 kart temiz).

Yöntem: `editor_farki.md`'deki her SONRA metninin yeni ya da değişen cümleleri, kartın kendi kaynak metniyle (`kaynak_dizini.jsonl` → `text_file`) karşılaştırıldı. Kart başına en az 2 yeni claim'in quote'u anlam bakımından kontrol edildi. Hiçbir kart dosyasına dokunulmadı.

Canlı açılan sayfa: yok (görev gereği indirilmiş kopyalar kullanıldı). Güncellik kontrolü yapılmadı: WBS gelir sınırları, Mieterschutzverordnung ek listesi ve süreleri, KiBiz 2026/27 sürümü, LÖG NRW (2018 sürümü) için yeni bir değişiklik olup olmadığına bakılmadı.

Bulgusuz kartlar (değişen cümleler kaynakla uyumlu, kontrol edilen claim quote'ları iddiayı kanıtlıyor):
- nrw-resmi-tatiller (Allerheiligen: § 6 Abs. 2 "alle in Absatz 1 genannten Veranstaltungen von 5 Uhr bis 18 Uhr" ile birebir uyumlu)
- nrw-okul-tatilleri-2026-27-ve-2027-28 (3 hareketli gün ve Berufsschule istisnası kaynakta var)
- nrw-turkce-anadil-dersi-hsu (15/18 öğrenci, Sprachprüfung dengeleme, Oberstufe, konsolosluk dersi 12.1/12.2 kaynakla uyumlu)
- nrw-okul-girisi-saglik-muayenesi-ve-saglik-nedeniyle-erteleme (§ 54 Abs. 4 katılım yükümlülüğü, § 35 Abs. 3 erteleme: uyumlu)
- nrw-duman-dedektoru-rauchwarnmelder-odalar-ve-sorumlu (§ 2 Abs. 7 tanımı ve § 47 Abs. 2 uyumlu)

---

### nrw-okul-sistemi-ve-yeni-gelen-cocugun-okula-yerlesmesi: orta
- Bulgu: Yeni `note` cümlesi iki şeyi yanlış kapsamlıyor. (1) "1 Ağustos 2029'dan itibaren okul zorunlusu olacak çocuklar için okul, kayıtta Almanca düzeyini saptar": kayıtta düzey saptama (§ 36 Abs. 3 Satz 1) tarih sınırı olmadan herkes için geçerlidir; yalnız Vorkurs'a zorunlu kılma (Satz 2) 2029'a bağlıdır. (2) "Bu yükümlülük 1 Ağustos 2029'dan önce okul zorunlusu olacak çocuklara uygulanmaz": kaynak "uygulanmaz" demekle bitmiyor, ikinci cümlesi bu çocuklar için Satz 2'nin 31 Temmuz 2026'ya kadar geçerli eski sürümünün uygulanmaya devam ettiğini söylüyor. Kart bunu atladığı için okuyucu bu çocuklar için hiçbir dil zorunluluğu olmadığını sanabilir.
- Kanıt: https://recht.nrw.de/lrgv/gesetz/01082026-schulgesetz-nrw-schulg/ (§ 36 Abs. 3) "Bei der Anmeldung zu einer Schule mit Primarstufe stellt die Schule fest, ob die Kinder die deutsche Sprache hinreichend beherrschen" ve (Abs. 6) "Die Verpflichtung nach § 36 Absatz 3 Satz 2 gilt nicht für Kinder, die vor dem 1. August 2029 schulpflichtig werden. Liegen bei diesen Kindern die Voraussetzungen des Absatzes 3 vor, ist § 36 Absatz 3 Satz 2 in der bis zum 31. Juli 2026 geltenden Fassung weiter anzuwenden."
- Düzeltme: Cümleyi şöyle ayır: "Okul, ilkokula kayıtta çocuğun Almanca düzeyini saptar. Yetersizse ve çocuk 1 Ağustos 2029'da ya da sonrasında okul zorunlusu oluyorsa kabulden önceki okul yılında okulun Vorkurs'una katılmayı zorunlu kılar; 1 Ağustos 2029'dan önce okul zorunlusu olacak çocuklara bu yeni zorunluluk uygulanmaz, onlar için bu hükmün 31 Temmuz 2026'ya kadar geçerli eski sürümü geçerli kalır." Eski sürümün içeriği kaynakta yoksa son cümleyi "eski sürüm uygulanmaya devam eder" ile sınırla, içerik ekleme.

### nrw-emlak-alim-vergisi-grunderwerbsteuer-orani-ve-odeme: orta
- Bulgu: `cost` alanına eklenen "arsa ve bina tek sözleşmeyle alınıyorsa bina yapım bedeli de matraha girer" kaynağı daraltıyor. Kaynak "tek sözleşme" demiyor; "einheitliches Vertragswerk" (bütünleşik sözleşme düzeni) diyor ve ölçüt, taşınmazın yapılı ya da yapılacak durumda edinilmesidir. Okuyucu arsa ve inşaatı ayrı sözleşmelere bölerse yapım bedelinin matrah dışında kalacağını sanabilir.
- Kanıt: https://www.finanzamt.nrw.de/steuerinfos/privatpersonen/haus-und-grund/grunderwerbsteuer-wissenswertes-beim-grundstuecks-oder "die Gebäudeerrichtungskosten, sofern Gegenstand eines Erwerbsvorgangs das Grundstück im bebauten (noch zu bebauendem) Zustand ist (sogenanntes einheitliches Vertragswerk)"
- Düzeltme: "tek sözleşmeyle alınıyorsa" yerine "taşınmaz yapılı ya da yapılacak durumda (bütünleşik sözleşme düzeni, einheitliches Vertragswerk) edinildiğinde bina yapım bedeli de matraha girer" yaz. Claim -20'nin Türkçe iddia metnini de aynı biçimde düzelt (quote doğru).

### nrw-resmi-islemde-widerspruch-yok-dogrudan-dava: orta
- Bulgu: Editörün yeniden yazdığı alan sayımında "okul hukuku" kayıtsız şartsız geçiyor (summary, subtitle, steps: "örneğin okul"). Kaynakta istisna yalnız "okulların kendi çıkardığı işlemler" için (§ 110 Abs. 2 Nr. 3 a); okul denetim makamının ya da başka makamın işlemleri bu istisnaya girmez. Kartın kendi `note` alanı bunu doğru yazıyor, summary ve steps ise genelliyor. Okuyucu okul alanındaki her işlemde Widerspruch gerektiğini düşünebilir.
- Kanıt: https://recht.nrw.de/lrgv/gesetz/24122024-gesetz-ueber-die-justiz-im-land-nordrhein-westfalen-justizgesetz-nordrhein/ (§ 110 Abs. 2) "3. im Bereich des a) Schulrechts, soweit sie von Schulen erlassen werden,"
- Düzeltme: Summary'deki "okul hukuku" ve steps'teki "örneğin okul" ifadelerini "okulun kendi çıkardığı işlemler (okul hukuku)" yap.

### nrw-resmi-islemde-widerspruch-yok-dogrudan-dava: küçük (1)
- Bulgu: Summary'ye eklenen "Anlatılan yol yalnız idare mahkemesine giden işlemler içindir; sosyal mahkeme ve mali mahkeme yolları bunun dışındadır" cümlesi iki kaynakta da yok ve claim'i yok. Doğru ve okuyucuyu koruyan bir kapsam notu, ama kaynaksız.
- Kanıt: https://www.justiz.nrw/BS/lebenslagen/verwaltungsrecht/klageverfahren/vorverfahren_07 yalnızca "Anfechtungs- oder Verpflichtungsklage" ve VwGO'dan söz eder; sosyal ya da mali mahkemeden söz etmez.
- Düzeltme: Ya bu cümleyi kaynaklı bir claim'e bağla (kaynak ekleme sınırı varsa) ya da "Bu sayfa yalnız VwGO kapsamındaki idari işlemler içindir" biçiminde kaynağın sınırına çek ve sosyal/mali mahkeme adlarını sil.

### nrw-resmi-islemde-widerspruch-yok-dogrudan-dava: küçük (2)
- Bulgu: "NRW'de ... doğrudan dava açılır" kuralı eyalet yasasıdır (JustG NRW). Kaynaklar eyalet ve belediye makamlarının işlemleriyle sınırlandığını yazmıyor; federal makam işlemlerinde (örneğin federal kurumların VwGO yoluna giden kararları) bu kuralın uygulanıp uygulanmadığı kartta belli değil. Kaynakla doğrulanamadı; yalnız işaret ediyorum.
- Kanıt: kaynaklarda yok (JustG NRW § 110 Abs. 1 metni makam ayrımı yapmıyor).
- Düzeltme: Kaynak bulunamazsa dokunma; bulunursa summary'ye "NRW eyalet ve belediye makamlarının işlemleri için" kapsamını ekle.

### nrw-magaza-acilis-saatleri-ve-acik-pazar: küçük
- Bulgu: "tüm belediye alanı için yalnız bir Advent Pazarı serbest olabilir" doğru ama eksik: Serbest bırakma belirli bölge, mahalle ya da ticaret kolu ile sınırlıysa bölge başına bir Advent Pazarı, belediye genelinde toplam en çok iki Advent Pazarı serbest bırakılabilir.
- Kanıt: https://recht.nrw.de/lrgv/gesetz/30032018-gesetz-zur-regelung-der-ladenoeffnungszeiten-ladenoeffnungsgesetz-loeg-nrw/ (§ 6 Abs. 4) "Erfolgt die Freigabe nach Absatz 1 beschränkt auf bestimmte Bezirke, Ortsteile und Handelszweige, darf nur ein Adventssonntag je Bezirk, Ortsteil und Handelszweig freigegeben werden, insgesamt dürfen jedoch nicht mehr als zwei Adventssonntage je Gemeinde freigegeben werden."
- Düzeltme: Cümleye "bölge ya da mahalle bazında serbest bırakılırsa bölge başına bir, belediye genelinde en çok iki Advent Pazarı" ekle.

### nrw-kita-ucreti-jugendamt-ve-ucretsiz-donem: küçük
- Bulgu: Steps'e eklenen "Ücretsiz çocuk kardeş indiriminde ücret ödüyormuş gibi sayılır" belirsiz. Kaynak, ücretsiz çocuğun kardeş düzenlemesinde (kardeş sayısı ve indirim hesabında) ücret ödenecekmiş gibi dikkate alınacağını söylüyor; okuyucu ücretsiz çocuktan ücret alınacağı anlamını çıkarabilir.
- Kanıt: https://recht.nrw.de/lrgv/gesetz/01082026-gesetz-zur-fruehen-bildung-und-foerderung-von-kindern-kinderbildungsgesetz/ (§ 51 Abs. 4) "Bei Geschwisterregelungen sind Kinder, deren Tagesbetreuung gemäß § 50 Absatz 1 elternbeitragsfrei ist, so zu berücksichtigen, als ob für sie ein Elternbeitrag zu leisten wäre."
- Düzeltme: "Kardeş indirimi hesaplanırken ücretsiz çocuk da, sanki ücret ödenecekmiş gibi, kardeş sayısına katılır; aile hem kardeş indiriminden hem ücretsizlikten tam yararlanmalıdır" yaz.

### nrw-u-muayeneleri-takip-sistemi-zentrale-stelle: küçük
- Bulgu: `timing` alanına eklenen "Werktag (Pazar ve resmî tatil dışındaki günler)" tanımı kaynakta yok; yönetmelik Werktag'ı tanımlamıyor. Ayrıca summary ve note "Jugendamt aileyle iletişime geçip geçmeyeceğine kendisi karar verir" diyor; LZG sayfası bu kararı "Kommune"ye veriyor, yönetmelik ise "Träger der öffentlichen Jugendhilfe"yi sayıyor. Anlam yakın, ama claim -22'nin kaynağındaki özne farklı.
- Kanıt: https://www.lzg.nrw.de/ges_foerd/kindergesundheit/zentrale-stelle/index.html "Die Kommune wird dann in eigener Zuständigkeit prüfen und entscheiden, ob sie mit den Eltern/Sorgeberechtigten Kontakt aufnimmt."
- Düzeltme: Parantezi sil ("beş iş günü içinde" ya da "beş Werktag içinde" yeter) ve karar cümlesinde "Jugendamt (belediye)" de.

### nrw-kilise-vergisi-orani-ve-kiliseden-cikis: küçük
- Bulgu: Summary'ye eklenen "Protestan, Roma Katolik ve Yahudi cemaatlerin vergisini NRW'de Finanzamt toplar" kaynaktaki "beispielsweise" (örneğin) kaydını düşürüyor; liste kapalı bir liste gibi okunuyor (kaynak diğer dinî toplulukları dışlamıyor).
- Kanıt: https://www.finanzamt.nrw.de/steuer-abc "Die Kirchensteuern für beispielsweise die evangelische, römisch katholische und jüdisch israelitische Kirche werden in Nordrhein-Westfalen durch die Finanzämter eingezogen"
- Düzeltme: "Örneğin Protestan, Roma Katolik ve Yahudi cemaatlerin vergisini..." yaz.

### nrw-kira-tavani-ve-kira-artis-siniri-mieterschutzverordnung: küçük (1)
- Bulgu: `note`'a eklenen "Aynı basın bildirisi Mietpreisbremse için 31 Aralık 2025 sınırından söz eder; yürürlükteki yönetmelik ... 31 Aralık 2029 olarak yazar" okuyucuya dönük metinde kaynaklar arası çelişki açıklaması, yani iç denetim notu. Okuyucunun bilmesi gereken tek şey yürürlükteki 2029 tarihi; summary bu tarihi zaten veriyor. Eski basın bildirisinin 2025 sınırını kartta tekrarlamak karışıklık yaratır.
- Kanıt: https://recht.nrw.de/lrgv/rechtsverordnung/07112025-mieterschutzverordnung-nrw-mietschvo-nrw/ (§ 3 Abs. 2) "§ 1 Absatz 1 tritt mit Ablauf des 31. Dezember 2029 außer Kraft. Im Übrigen tritt diese Verordnung mit Ablauf des 28. Februar 2030 außer Kraft."
- Düzeltme: İlk cümleyi sil; note yalnız 1 Mart 2025 öncesi satış geçiş kuralı ile başlasın. Claim -13'ü de (basın bildirisi 2025 sınırı) sil ya da gaps.md'ye taşı.

### nrw-kira-tavani-ve-kira-artis-siniri-mieterschutzverordnung: küçük (2)
- Bulgu: Steps'in ilk satırı yeniden yazılırken "yönetmelik ekindeki belediye listesine bak" eylemi düşmüş. Kart artık okuyucuya listenin nerede olduğunu söylemiyor (şehir adı yazılmaması doğru, ama listeye bakma yönlendirmesi kalabilir). Summary yalnız "yönetmelik ekinde sayılan belediyelerde" diyor.
- Kanıt: https://recht.nrw.de/lrgv/rechtsverordnung/07112025-mieterschutzverordnung-nrw-mietschvo-nrw/ (§ 1 Abs. 1) "bestimmen sich nach der Anlage zu dieser Verordnung."
- Düzeltme: Steps'in başına "Yönetmeliğin ekindeki (Anlage) belediye listesine bak; aşağıdaki üç kural yalnız o listedeki belediyelerde geçerlidir" cümlesini geri koy (belediye adı yazmadan).

### nrw-wbs-gelir-siniri-2025-ve-basvuru: küçük (1)
- Bulgu: Editör "oturum belgesi"ni "ikamet belgesi (Aufenthaltsbescheinigung)" yaptı (steps ve documents). Türkçede "ikamet belgesi" çoğunlukla adres kayıt belgesini (Meldebescheinigung) akla getirir; kartın kilise bölümü Meldebescheinigung'u "adres kayıt belgesi" diye çeviriyor, yani paket içinde terim tutarsız. Kaynaktaki bağlam (Avrupa dışından gelenin oturum hakkı) oturum hakkını gösteren belgeyi kastediyor.
- Kanıt: https://www.mhkbd.nrw/themenportal/wohnberechtigungsschein "Als notwendige Unterlagen sind Personalausweise, Reisepässe und ggf. Aufenthaltsbescheinigungen für jede haushaltsangehörige Person vorzulegen."
- Düzeltme: "gerekirse oturum hakkını gösteren belge (Aufenthaltsbescheinigung)" yaz.

### nrw-wbs-gelir-siniri-2025-ve-basvuru: küçük (2)
- Bulgu: "Avrupa dışı bir ülkeden (außereuropäisches Ausland) geliyorsan ... en az bir yıl kalma hakkın olmalı" cümlesine editör Almanca terimi ekledi ama Türk okuyucu için Türkiye'nin bu kapsama girip girmediği hâlâ belli değil (kaynak "außereuropäisches Ausland" diyor ve tanım vermiyor). Okuyucu Türkiye'nin kısmen Avrupa'da olduğunu düşünüp kuralı kendine uygulamayabilir. Kaynaktan yanıtlanamıyor.
- Kanıt: https://www.mhkbd.nrw/themenportal/wohnberechtigungsschein "Kommen Sie aus dem außereuropäischen Ausland, müssen Sie sich mindestens ein Jahr in der Bundesrepublik Deutschland und damit in Nordrhein-Westfalen aufhalten dürfen."
- Düzeltme: Cümleye "Hangi ülkelerin bu kapsama girdiğini Wohnungsamt'a sor" ekle (kaynaksız tanım ekleme).
