"""address_forms: okura dogrudan hitap olcumu (B16; standart city-pack intake'te, Baris karari 23.10.2026: 'sen').

Turkce ornek cumleler: dogru pozitifler ('siz', 'sen', karisik) ve yanlis pozitif listesi (-iz/-uz ile biten yaygin
kelimeler, ozel adlar, tirnak icindeki alinti, Hollandaca/Almanca kelimeler, ilgi eki, 3. tekil emir, ad okumasi).
"""
from __future__ import annotations

import copy
import json

import pytest

import address_forms as af

SIZ = [
    "Başvurunuzu belediyeye yapabilirsiniz.",
    "Pasaportunuzu ve kira sözleşmenizi yanınıza alın.",
    "Randevu alın.",
    "Formu doldurun ve ücreti ödeyin.",
    "Kimlik kartını unutmayın.",
    "DigiD'niz yoksa önce DigiD alın.",
    "Yeni BSN'inizi işverene bildirin.",
    "Size uygun sigortayı seçin.",
    "Türk vatandaşıysanız ek belge istenir.",
    "Bu karar sizin için bağlayıcıdır.",
    "Gelir ve giderleri karşılaştırın.",
    "Okul seçimini okula sorun.",
    "Sözleşmeyi imzalamadan önce kontrol edin.",
    "Saat 9'da orada olun.",
    "Taşındıktan sonra 5 gün içinde kaydolmanız gerekir.",
    "Emin olun.",
    "Hesabınızdan otomatik çekilir.",
    "Eindhoven'dasınız.",
    "Kendiniz başvurursunuz.",
    "Kutuyu kaldırımdan 50 cm uzağa koyun.",
    "Talebinizi e-posta ile yazın.",
    "Seçin",
    "Çocuğunuz için bir okul bulun.",
    "Belgelerin kopyalarını çıkarın.",
    "IBAN'ınızı ve CAO'nuzu hazırlayın.",
    "Bisikletinizi kilitleyin; kartınızı okutun.",
]
SEN = [
    "Başvurunu belediyeye yapabilirsin.",
    "Randevu al.",
    "Formu doldur ve ücreti öde.",
    "Kimlik kartını unutma.",
    "DigiD'in yoksa önce başvur.",
    "Sana uygun sigortayı seç.",
    "Türk vatandaşıysan ek belge istenir.",
    "Bu karar senin için bağlayıcıdır.",
    "Ev sahibinden teyit al; adres kayıt belgesini sakla.",
    "Gerçekten taşındığın adresi kaydettir.",
    "Hakkın varsa itiraz edebilirsin.",
    "Hollandaca biliyorsan kursa gerek yok.",
    "İşe başlamadan önce sözleşmeni kontrol et.",
    "Wooniezie'ye kayıt ol.",
    "Emin ol.",
    "Bunu yapmalısın.",
    "Formu doldurduysan bekle.",
    "Başvurman gerekir.",
    "Gideceğin adresi belirle.",
    "Bu tutarı hesaba kat.",
    "UWV ile iletişime geç.",
    "Ayrıntılı bilgi edin.",
    "Biliyor musun?",
    "Çocuğun varsa okul kaydı gerekir.",
    "Randevu al",
    "Teslim sırasında hazır bulun.",  # bulunmak'in 2. tekil emri (bulmak'in 2. cogulu degil)
    "BRP'ye geçsen de numara aynı kalır.",
    "Eindhoven'da hayatı kurman için gereken bilgiler.",
    # 'hepinizin' (ev halki: sen + birlikte oturanlar) cogul 'siz' degil; sen metnini karisik yapmaz
    "Senin ve birlikte oturduğun kişilerin, hepinizin adreste kayıtlı olması gerekir.",
    "Değişiklikten iki ay önce yazılı talepte bulun.",  # X-DA bulunmak (talepte bulun) 2. tekil emir
    "Belgeyi sen getir; evliliği ikiniz de beyan edin.",  # 'ikiniz de ... edin': cogul ozne, resmi 'siz' degil
    # cogul 'siz' = sen + es/aile (Eindhoven: 7 karisik sanilan kartin kalibi); resmi 'siz' degil
    "Huurtoeslag için sen ve varsa toeslagpartner'in şu şartları sağlamalısınız: ev sahibiyle kira sözleşmeniz olmalı.",
    "Partnerin ve çocukların seninle taşınıyorsa hep birlikte gidersiniz.",
    "Seçimi doğum bildiriminde yap: Inwonersplein'a iki ebeveyn birlikte gidin.",
    "Çocuğun için başvurabilirsin. Eşin için belge yalnızca tezgâhta alınır ve evli ya da kayıtlı ortak olmanız "
    "ile aynı adreste yaşamanız gerekir.",
    "Evli olmayan partnersen en az 6 aydır birlikte yaşadığını ya da sürdürülebilir bir ilişkiniz olduğunu kanıtla.",
    "Ayda en az 20 saat çalışırsan, bunu açıkça kararlaştırmasanız bile iş sözleşmen vardır.",
    "Aile üyesiysen ve birlikte başka bir AB ülkesinde yaşadıysanız oturum izni gerekmez.",
    "Doğumu internetten bildir; tanıma için iki ebeveyn de tezgâha gidin.",  # yalniz 'iki ebeveyn' ipucu
    "Evli olmayan partnersen ilişkinizi ortak kira sözleşmesiyle kanıtla.",  # yalniz iliski adi
    # dal ornekleri: kesmeden sonra -DAsIn, -DIgIn, parantezli aciklama atlanir, iki heceli 2. tekil genis zaman
    "Eindhoven'dasın.",
    "Taşındığın adres önemli.",
    "Randevu al (online).",
    "Pazarda her şeyi yersin.",
    "Formu ona versen yeter.",
    "Bisikletini kilitle; kartını okut.",
]
HITAPSIZ = [
    "Başvuru belediyeye yapılır.",
    "Randevu çevrimiçi alınır.",
    "Kartla ödeme yapılabilir.",
    "Henüz karar verilmedi.",
    "Yalnız hafta sonları açık.",
    "Deniz kıyısında sekiz kilometrelik yol var.",
    "Dokuz ikiz kule ve yüz metrelik iskele.",
    "Semiz kuzu ve beniz rengi.",
    "Elbiz mağazası Akdeniz ürünleri satıyor.",
    "Sergiyi Deniz Yalnız açtı.",
    'Belediye "Randevunuzu iptal edin, formu doldur" diye yazıyor.',
    "Kaynakta 'Formu doldurun ve gönderin' yazıyor.",
    "Belediye sitesi “Kayıt olun, sonra bekleyin” diyor.",
    "Mensen, witwassen ve fietsen Hollandaca sözcüklerdir.",
    "Almanca sözlükte müssen ve Essen geçer.",
    "Atıklar yeşil kutuya (groene bak) atılır.",
    "GFT-bak her hafta boşaltılır.",
    "Eindhoven'in merkezi ve belediyenin binası yakın.",
    "Dersin içeriği ve kursun ücreti sayfada.",
    "Polisin numarası 112'dir.",
    "Belge gönderilsin diye beklenir; hava güzel olsun.",
    "Kurum belgeyi göndersin.",
    "Nisan ayında insan çok; şahsen başvuru yapılır.",
    "Biraz zaman gerekir.",
    "Burada izin yok ve sorun var.",
    "Bu ciddi bir sorun.",
    "Çocuklar için oyun alanı ve koyun çiftliği var.",
    "Menüde çabuk bozulan et ve balık yok.",
    "Yaz ve kış saatleri farklıdır.",
    "En kalabalık mevsim yaz.",
    "Havuz yalnızca yazın açık.",
    "Ayrıntılar https://example.org/randevunuzu-alin-ve-gel adresinde.",
    "Adresimi nasıl kaydettiririm?",
    "Uzman danışman ve göçmen öğretmen gerekir.",
    "Deniz kenarında bir koy.",
    "Toplantı 18 Septemberplein'de yapılır.",
    "Kira yardımı (huurtoeslag) her ay ödenir.",
    "Bilet 13,50 euro; müze salıdan pazara açık.",
    "Ödeme",
    "",
    # Eindhoven gercek verisinden: 3. tekil genis zaman 'cikar' ve -nIz'e benzeyen alinti kelime (unlu uyumu bozuk)
    "Çocuk sınava girer ve sonunda kesin tavsiye çıkar.",
    "Fesih bedeli hangi durumlarda çıkar",
    "Etkinliği kulüp organize ediyor; sistem mekanize ve harmonize edildi.",
    "Bu izin uzun zaman için geçerli; uzman için ve göçmen için ayrı kurallar var, çimen için sulama gerekir.",
    "Mahalle çevre yolunun hemen içinde; belge tamamen gerekli değil, kısmen şart.",
    # Eindhoven metninden (W1 incelemesi; kisisiz yeniden yazimdan sonra da kalir): liste ogesi ve 'var olan'
    "Irk, inanç, siyasi görüş, cinsiyet veya engellilik nedeniyle ayrımcılık yasaktır.",
    "Adres bir kişinin ya da kurumun var olan adresi olmalı.",
    # ilgi eki: -DIk/-AcAk ile biten ad ve unlu uyumu bozuk alinti ad (plastik, butik)
    "Geleceğin teknolojileri burada geliştirilir.",
    "Plastiğin ve metalin ayrı toplanması gerekir.",
    "Butiğin açılış saatleri değişir.",
    "Yiyeceğin fiyatı yüksek; fındığın fiyatı arttı.",
    "Sandığın yeri belediyedir ve mantığın basit.",
    # -mAn + icin/gerek: meslek/kisi adi ve unlu uyumu bozuk alinti (examen, Müslüman)
    "Inburgering examen için kayıt gerekir.",
    "Staatsexamen için Hollandaca B1 gerekir.",
    "Müslüman için helal seçenek var; her seçmen için ayrı oy pusulası, her salon için bir denetmen gerekir.",
    # emir sozluguyle cakisan ad/sifat: liste ogesi, sifat ve derece zarfindan, baglactan, mastardan, cogul addan sonra
    "Hayvanlar arasında keçi, tavşan, koyun.",
    "Merkezde park yeri bulmak sorun.",
    "Plaj en kalabalık yazın.",
    "Şehir en canlı yazın, kışın sakin.",
    "Duvarlar çok kalın.",
    "Kale duvarları oldukça kalın.",
    "Çiftlikte inek ve koyun.",
    "Ödeme nakit ya da çek.",
    "Sahilde sakin koy.",
    "Çocuklar aç.",
    "Festival sezonu yaz.",
    "Park hem kışın hem yazın.",
    "Organik atık kutusunun adı GFT bak.",  # Hollandaca 'bak' (kutu): kisaltmadan sonra
    "Yeşil kutu: groene bak.",  # Hollandaca sifattan sonra
    # genel -yIn/-DIrIn: ilgi eki ve zaman zarfi (yalniz noktalamayla biten yan cumlede sayilir)
    "Okul müdürün ve öğretmenin onayıyla kayıt yapılır.",
    "Otobüsler sabahleyin, öğlen ve akşamleyin sık.",
    "Kahvaltı sabahleyin ve akşamleyin.",
    # 1. cogul: n ile biten govde + -Iz (biz baglami)
    "Bundan eminiz.",
    "Hepimiz insanız.",
    "Biz bu şehre tutkunuz.",  # govde listede yok: yalniz 'biz' baglami
    # iyelik + var/yok/olmali: ad ve sifat okumasi
    "Tuvalette sabun yok.",
    "Başvuru sahibi Hollanda'da sakin olmalı.",
    "Bahçede zeytin var; bölgede din yok.",
    "Parkta çocuklar için oyun var.",
    "Başvuru sahibi ergin olmalıdır.",  # -gIn sifati (ergin, yorgun) iyelik degil
    # 3. tekil emir (-DIrsIn), iki heceli -rsIn (ilgi eki) ve Hollandaca -rsen
    "İşveren sözleşmeyi değerlendirsin.",
    "Kurum belgeyi yazdırsın; işveren başvuruyu sürdürsün.",
    "Okul kaydı kesinleştirsin diye belge istenir.",
    "Bursun miktarı yıllık belirlenir.",
    "Pazarda kersen satılır; persen sıkmak demektir.",
    "Banka günlük wisselkoersen listesini yayımlar.",  # uc heceli Hollandaca -rsen: harf cifti (oe)
    # dal ornekleri
    "Al, yeşil ve mavi renkler kullanılır.",  # ilk kelimede virgul yan cumle sonu sayilmaz (al = kirmizi)
    "Yaz: sıcak ve güneşli.",  # ad okumasi olan emir cumlenin ilk kelimesi olamaz
    "Sorun: park yeri az.",
    "Eksen kuzey-güneyin.",  # tireli bilesikte emir kurali uygulanmaz
    "Sorumluluk bireyin.",  # genel emir kuralinin ad listesi
    "Bu meydan köyün.",  # iki heceli -yIn emir sayilmaz
    "Eski bir mayın bulundu.",  # kisa -mAyIn olumsuz emir degil
    "Ayrıntılar https://example.org/randevunuzu adresinde.",  # web adresi okunmaz
    "Belge Haag'enız.",  # kesmeden sonra unlu uyumu bozuk ek (Turkce ek degil) okunmaz
    "Henüzden belli değil; benizi soluk.",
]
MIXED = [
    "Randevunuzu alın ve formu doldur.",
    "Başvurabilirsin; belgelerinizi getirin.",
    # Eindhoven'daki 3 gercek karisik kartin kalibi: ayni kayitta resmi 'siz' ve 'sen'
    "Lodewijkstraat kapalı, Acht'a gidin.\nAtığını türlerine göre ayır.",
    "Taşınmayı tezgâhta bildirebilirsin.\nBiriyle birlikte oturacaksanız onayı da ekleyin.\nKimliğinizi hazırlayın.",
    "Vatandaşı değilsen izin notu olmalıdır.\nGeçerli pasaportunuzu hazırlayın.",
]


@pytest.mark.parametrize("text", SIZ)
def test_siz_sentences(text):
    marks = af.markers(text)
    assert af.form_of(text) == "siz", marks
    assert marks.siz and not marks.sen


@pytest.mark.parametrize("text", SEN)
def test_sen_sentences(text):
    marks = af.markers(text)
    assert af.form_of(text) == "sen", marks
    assert marks.sen and set(marks.siz) <= set(marks.plural)


@pytest.mark.parametrize(("text", "form"), [("Partnerinizle ikiniz de başvurabilirsiniz.", "siz"),
                                            ("İkiniz de başvuru yapabilir.", "siz"),
                                            ("Formu doldur. İkiniz de beyan edin.", "sen"),
                                            ("Formu doldur. Beyan edin. İkiniz de imzalayın.", "karisik"),
                                            ("Başvurabilirsin; siz de başvurabilirsiniz.", "karisik")])
def test_plural_you_counts_as_address_but_not_as_formal_siz(text, form):
    assert af.form_of(text) == form, af.markers(text)
    report = af.address_report({"Sözlük": [{"_row": 8, "term_id": "x:t0", "definition": text}]}, "sen")
    assert report[form] == 1 and [f["reason"] for f in report["findings"]] == ([] if form == "sen" else
                                                                               ["karisik" if form == "karisik" else
                                                                                "standart_disi"])


@pytest.mark.parametrize("text", HITAPSIZ)
def test_impersonal_and_false_positive_sentences(text):
    assert af.markers(text) == af.Marks((), (), ()), text
    assert af.form_of(text) == "hitapsiz"


@pytest.mark.parametrize("text", MIXED)
def test_mixed_sentences(text):
    assert af.form_of(text) == "karisik", af.markers(text)


def test_markers_keep_surface_words_in_order_without_repeats():
    marks = af.markers("Randevunuzu alın. Randevunuzu kaybederseniz yeniden alın; sen de gelebilirsin.")
    assert marks.siz == ("Randevunuzu", "alın", "kaybederseniz")
    assert marks.sen == ("sen", "gelebilirsin")


def test_capitalised_first_word_is_read_but_proper_names_mid_sentence_are_not():
    assert af.markers("Kendiniz başvurursunuz.").siz == ("Kendiniz", "başvurursunuz")
    assert af.markers("Sergi Deniz ve Sinan Yıldırımsınız tarafından açıldı.") == af.Marks((), ())
    assert af.markers("BSN numaranızı yazın.").siz == ("numaranızı", "yazın")


def test_json_values_are_read_as_separate_clauses():
    visual = json.dumps({"kind": "steps", "items": [{"title": "Tüketimi öğrenin"}, {"title": "Karşılaştırın"}]})
    assert af.markers(visual).siz == ("öğrenin", "Karşılaştırın")
    assert af.markers('{"Ulaşım": "Tren istasyonu bu bölgede."}') == af.Marks((), ())
    assert af.markers("[bozuk json") == af.Marks((), ())


@pytest.mark.parametrize(("text", "sen"), [
    ("Randevu al, belge gerekmez.", ("al",)),  # virgul yan cumle sonudur
    ("Randevu al ve belgeleri getir.", ("al", "getir")),  # baglac yan cumle sonudur
    ("Randevu al (online) ve bekle.", ("al", "bekle")),  # parantezli aciklama atlanir
    ("Numarayı ara, sonra randevu al.", ("ara", "al")),  # ad okumasi olan emir de virgulle biten yan cumlede sayilir
])
def test_clause_end_rules_for_imperatives(text, sen):
    assert af.markers(text) == af.Marks((), sen), text


# Eindhoven verisinde ilk duzeltme denemesinin kaybettigi gercek isaretler (eski/yeni kod karsilastirmasi)
@pytest.mark.parametrize(("text", "siz", "sen"), [
    ("Yardım gerekirse Toeslagenservicepunt ara ya da e-posta gönder.", (), ("ara", "gönder")),
    ("Kutuyu kaldırımdan uzağa koyun, kapağı kapatın.", ("koyun", "kapatın"), ()),
    ("İlacınızı Catharina Apotheek'ten alın.", ("İlacınızı", "alın"), ()),
    ("Yeni huisarts'a sorun.", ("sorun",), ()),
    ("Aktı yeminli tercümana çevirtirsin.", (), ("çevirtirsin",)),  # ettirgen -t + genis zaman, 3. tekil emir degil
    ("Özet oluşturun ya da 1400'ü arayın.", ("oluşturun", "arayın"), ()),
    ("Mahalle merkezinin programında tamir buluşması ara.", (), ("ara",)),  # Berlin: -mAsI ad tamlamasi, mastar degil
    ("Bize adınızı yazın.", ("adınızı", "yazın"), ()),  # 'biz' baglami yalniz eksiz -Iz'i 1. cogul sayar
    ("Şartlar için huurtoeslag'a bak.", (), ("bak",)),  # Turkce ekli Hollandaca ad yabanci sayilmaz ('GFT bak' degil)
])
def test_real_imperatives_after_names_commas_and_conjunctions_are_kept(text, siz, sen):
    assert af.markers(text) == af.Marks(siz, sen), text


def test_plural_cue_is_clause_level_and_joint_sen_address_is_text_level():
    plural = af.markers("Biriyle birlikte oturacaksanız onayı ekleyin; kimliğinizi hazırlayın.")
    assert plural.plural == ("oturacaksanız", "ekleyin") and not plural.joint
    joint = af.markers("Sen ve partnerin başvurursunuz; kira sözleşmeniz olmalı.")
    assert joint.joint and joint.plural == joint.siz == ("başvurursunuz", "sözleşmeniz")


# --- kayit duzeyi rapor -------------------------------------------------------------------------------

def _sheets() -> dict:
    visual = json.dumps({"kind": "steps", "items": [{"title": "Randevu al"}]})
    answers = [
        {"_row": 8, "entry_id": "x:a0", "title": "Kayıt nasıl yapılır?", "summary": "Başvuru belediyeye yapılır.",
         "steps": "Randevu çevrimiçi alınır."},
        {"_row": 9, "entry_id": "x:a1", "summary": "Başvurunuzu yapabilirsiniz.", "steps": "Randevu alın."},
        {"_row": 10, "entry_id": "x:a2", "summary": "Başvuru belediyeye yapılır.", "visual_json": visual},
        {"_row": 11, "entry_id": "x:a3", "summary": "Başvurunuzu yapabilirsiniz.", "steps": "Randevu al.",
         "keywords": "randevunuzu alın"},
    ]
    places = [{"_row": 8, "entry_id": "x:p0", "title": "Kaydolun Müzesi", "summary": "Henüz açılmadı; yalnız hafta sonu.",
               "note": "Gitmeden saatlere bakın."}]
    terms = [{"_row": 8, "term_id": "x:t0", "term": "zorgtoeslag", "definition": "Sağlık sigortası katkısı; başvurursun."}]
    return {"Yanıtlar": answers, "Mekânlar": places, "Sözlük": terms, "Konular": [{"_row": 8, "topic_id": "x:k0"}]}


def test_report_counts_forms_per_record_and_sheet():
    report = af.address_report(_sheets())
    assert {k: report[k] for k in ("standard", "records", *af.FORMS)} == {
        "standard": "off", "records": 7, "hitapsiz": 2, "siz": 2, "sen": 2, "karisik": 1}
    assert report["by_sheet"]["Yanıtlar"] == {"records": 4, "hitapsiz": 1, "siz": 1, "sen": 1, "karisik": 1}
    assert report["by_sheet"]["Konular"] == {"records": 1, "hitapsiz": 1, "siz": 0, "sen": 0, "karisik": 0}
    assert list(report["by_sheet"]) == ["Yanıtlar", "Mekânlar", "Konular", "Sözlük"]  # yalniz var olan sayfalar
    assert report["findings"] == []  # off: yalniz olcum
    mixed = next(i for i in report["items"] if i["id"] == "x:a3")
    assert mixed == {"sheet": "Yanıtlar", "row": 11, "id": "x:a3", "form": "karisik",
                     "fields": {"summary": "siz", "steps": "sen"}, "siz": ["Başvurunuzu", "yapabilirsiniz"], "sen": ["al"]}
    assert next(i for i in report["items"] if i["id"] == "x:a2")["fields"] == {"visual_json": "sen"}
    assert next(i for i in report["items"] if i["id"] == "x:p0")["fields"] == {"note": "siz"}  # baslik (mekan adi) okunmaz


def test_place_title_is_a_name_and_is_not_read():
    places = [{"_row": 8, "entry_id": "x:p0", "title": "Müzeyi gezin", "summary": "Sanat müzesi."}]
    assert af.address_report({"Mekânlar": places})["hitapsiz"] == 1


@pytest.mark.parametrize(("standard", "expected"), [
    ("hitapsiz", [("x:a1", "standart_disi"), ("x:a2", "standart_disi"), ("x:a3", "karisik"), ("x:p0", "standart_disi"),
                  ("x:t0", "standart_disi")]),
    ("siz", [("x:a2", "standart_disi"), ("x:a3", "karisik"), ("x:t0", "standart_disi")]),
    ("sen", [("x:a1", "standart_disi"), ("x:a3", "karisik"), ("x:p0", "standart_disi")]),
    ("off", []),
])
def test_findings_follow_the_standard_and_mixed_is_always_a_finding(standard, expected):
    report = af.address_report(_sheets(), standard)
    assert [(f["id"], f["reason"]) for f in report["findings"]] == expected
    assert all(f["siz"] or f["sen"] for f in report["findings"])  # kayit kimligi + ornek kelimeler


def test_report_is_pure_and_rejects_unknown_standard():
    sheets = _sheets()
    snapshot = copy.deepcopy(sheets)
    assert af.address_report(sheets, "hitapsiz") == af.address_report(copy.deepcopy(sheets), "hitapsiz")
    assert sheets == snapshot
    with pytest.raises(ValueError):
        af.address_report(sheets, "biz")


def test_examples_are_capped_per_form():
    text = "Belgenizi, pasaportunuzu, kimliğinizi, sözleşmenizi, adresinizi, numaranızı ve kartınızı getirin."
    report = af.address_report({"Yanıtlar": [{"_row": 8, "entry_id": "x:a0", "summary": text}]})
    assert report["items"][0]["siz"] == ["Belgenizi", "pasaportunuzu", "kimliğinizi", "sözleşmenizi", "adresinizi"]
    assert af.MAX_EXAMPLES == 5 and len(af.markers(text).siz) == 8


def test_joint_sen_address_in_one_field_makes_the_record_plural_not_mixed():
    summary = "Huurtoeslag için sen ve varsa toeslagpartner'in şu şartları sağlamalısınız."
    steps = "Ev sahibiyle kira sözleşmenizin bulunduğunu kontrol et."
    joint = {"_row": 8, "entry_id": "x:a0", "summary": summary, "steps": steps}
    alone = {"_row": 9, "entry_id": "x:a1", "summary": "Kirayı ödediğini gösteren dökümleri hazırla.", "steps": steps}
    report = af.address_report({"Yanıtlar": [joint, alone]}, "sen")
    assert [(i["id"], i["form"], i["fields"]) for i in report["items"]] == [
        ("x:a0", "sen", {"summary": "sen", "steps": "sen"}),
        ("x:a1", "karisik", {"summary": "sen", "steps": "karisik"})]
    assert [(f["id"], f["reason"]) for f in report["findings"]] == [("x:a1", "karisik")]


# sayfa -> (kimlik anahtari, okura gorunen metin alanlari): sozlesme; bir alan dusurulurse bu test kirilir
EXPECTED_FIELDS = {
    "Yanıtlar": ("entry_id", ("title", "subtitle", "summary", "steps", "documents", "timing", "cost", "note",
                              "visual_json")),
    "Mekânlar": ("entry_id", ("subtitle", "summary", "note")),
    "Mahalleler": ("entry_id", ("subtitle", "summary", "note", "tags", "compare_json")),
    "Rotalar": ("route_id", ("title", "note")),
    "Adımlar": ("step_id", ("title", "description", "when")),
    "Konular": ("topic_id", ("title", "description")),
    "Sözlük": ("term_id", ("definition",)),
    "SayfaAlanları": ("field_id", ("value",)),
    "Şehir": ("city_id", ("title", "tagline", "intro")),
    "Fotoğraflar": ("photo_id", ("caption",)),
}


def test_every_reader_visible_field_of_every_sheet_is_read():
    sheets = {sheet: [{"_row": 8, id_key: f"{sheet}:0", **{field: "Formu doldurun." for field in fields}}]
              for sheet, (id_key, fields) in EXPECTED_FIELDS.items()}
    report = af.address_report(sheets)
    assert report["by_sheet"] == {sheet: {"records": 1, "hitapsiz": 0, "siz": 1, "sen": 0, "karisik": 0}
                                  for sheet in EXPECTED_FIELDS}
    assert {i["id"]: set(i["fields"]) for i in report["items"]} == {
        f"{sheet}:0": set(fields) for sheet, (_, fields) in EXPECTED_FIELDS.items()}


def test_link_labels_are_counted_apart_and_never_findings():
    links = [{"_row": 8 + i, "action_id": f"a{i}", "entry_id": "x:a0", "label": label}
             for i, label in enumerate(["Bilgi al", "Haritada aç", "Randevu alın", "Resmî sayfa"])]
    sheets = {"Yanıtlar": [{"_row": 8, "entry_id": "x:a0", "summary": "Başvuru belediyeye yapılır."}],
              "Bağlantılar": links}
    report = af.address_report(sheets, "hitapsiz")
    assert report["labels"] == {"records": 4, "hitapsiz": 1, "siz": 1, "sen": 2, "karisik": 0}
    assert report["records"] == 1 and report["findings"] == [] and "Bağlantılar" not in report["by_sheet"]
    assert af.address_report({})["labels"] == {"records": 0, "hitapsiz": 0, "siz": 0, "sen": 0, "karisik": 0}


def test_skipped_sheets_are_reported_and_summarised():
    report = af.address_report(_sheets(), "siz", skipped={"Rotalar": "Rotalar: yinelenen teknik anahtar"})
    assert report["skipped"] == [{"sheet": "Rotalar", "error": "Rotalar: yinelenen teknik anahtar"}]
    summary = af.address_summary(report)
    assert summary == {"standard": "siz", "records": 7, "hitapsiz": 2, "siz": 2, "sen": 2, "karisik": 1, "findings": 3,
                       "labels": {"records": 0, "hitapsiz": 0, "siz": 0, "sen": 0, "karisik": 0},
                       "skipped": ["Rotalar"]}
    assert af.address_report(_sheets())["skipped"] == []
