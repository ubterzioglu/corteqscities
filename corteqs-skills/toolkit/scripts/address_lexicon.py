"""address_forms sozlugu (B16 okura hitap): isaret kelimeleri, ek kaliplari ve yanlis pozitif istisnalari.

Morfolojik cozumleyici yok: kural + kucuk sozluk. Listeler yalniz kurallarin ayiramadigi bicimleri tasir; her
listenin yaninda neyi disarida biraktigi yazili. Kurallar address_forms.py'de.
"""
from __future__ import annotations

import re

VOWELS, CONSONANTS, TR_ONLY = "aeıioöuü", "bcçdfgğhjklmnprsştvyz", frozenset("çğışöü")
BACK_VOWELS = frozenset("aıou")
HARMONY = {"a": "ı", "ı": "ı", "e": "i", "i": "i", "o": "u", "u": "u", "ö": "ü", "ü": "ü"}  # dar unlu uyumu
DUTCH_PAIRS = ("oe", "eu", "ij", "uu", "ui", "ee")  # Turkce kelimede yok ya da cok seyrek (groene, kersen degil)

SIZ_WORDS = frozenset({"siz", "size", "sizi", "sizin", "sizde", "sizden", "sizinle", "sizce", "sizler", "sizlere",
                       "sizleri", "sizlerin", "sizlerden", "sizindir", "sizinki"})
SEN_WORDS = frozenset({"sen", "sana", "seni", "senin", "sende", "senden", "seninle", "sence", "senindir", "seninki",
                       "kendin", "musun", "mısın", "misin", "müsün", "değilsin", "değilsen", "olsan", "kalsan"})
BIZ_WORDS = frozenset({"biz", "bize", "bizi", "bizim", "bizde", "bizden", "bizce", "bizler", "bizimle", "hepimiz",
                       "ikimiz", "birimiz", "çoğumuz"})

# emir: 2. tekil kok bicimi -> 2. cogul; yalniz yan cumle sonunda sayilir
IMPERATIVES: dict[str, str] = {
    "al": "alın", "ara": "arayın", "aç": "açın", "ayarla": "ayarlayın", "ayır": "ayırın", "ayırt": "ayırtın",
    "bak": "bakın", "başla": "başlayın", "başvur": "başvurun", "bekle": "bekleyin", "belirle": "belirleyin",
    "belirt": "belirtin", "bil": "bilin", "bildir": "bildirin", "bırak": "bırakın", "bul": "bulun", "çek": "çekin",
    "çevir": "çevirin", "çevirt": "çevirtin", "çık": "çıkın", "çalış": "çalışın",
    "danış": "danışın", "değerlendir": "değerlendirin", "değiştir": "değiştirin", "dene": "deneyin",
    "dinle": "dinleyin", "doğrula": "doğrulayın", "doldur": "doldurun", "dolaş": "dolaşın", "dön": "dönün",
    "dur": "durun", "düşün": "düşünün", "ekle": "ekleyin", "gel": "gelin", "getir": "getirin", "gez": "gezin",
    "geçir": "geçirin", "gir": "girin", "git": "gidin", "göster": "gösterin", "gönder": "gönderin", "gör": "görün",
    "görüş": "görüşün", "götür": "götürün", "harca": "harcayın", "hatırla": "hatırlayın", "hazırla": "hazırlayın",
    "hesapla": "hesaplayın", "ilet": "iletin", "imzala": "imzalayın", "incele": "inceleyin", "indir": "indirin",
    "iste": "isteyin", "izle": "izleyin", "kal": "kalın", "kaldır": "kaldırın", "kapat": "kapatın",
    "karşılaştır": "karşılaştırın", "katıl": "katılın", "kaydet": "kaydedin", "kaydettir": "kaydettirin",
    "kaydol": "kaydolun", "keşfet": "keşfedin", "kilitle": "kilitleyin", "kirala": "kiralayın", "konuş": "konuşun",
    "koy": "koyun", "kullan": "kullanın", "netleştir": "netleştirin", "oku": "okuyun", "okut": "okutun", "ol": "olun",
    "onayla": "onaylayın", "otur": "oturun", "öde": "ödeyin", "öğren": "öğrenin", "planla": "planlayın",
    "sağla": "sağlayın", "sakla": "saklayın", "say": "sayın", "seç": "seçin", "sor": "sorun", "sun": "sunun",
    "tamamla": "tamamlayın", "taşın": "taşının", "tıkla": "tıklayın", "tut": "tutun", "uğra": "uğrayın",
    "ulaş": "ulaşın", "uygula": "uygulayın", "uzat": "uzatın", "ver": "verin", "yap": "yapın", "yaptır": "yaptırın",
    "yatır": "yatırın", "yaz": "yazın", "yenile": "yenileyin", "yolla": "yollayın", "yükle": "yükleyin",
    "yürü": "yürüyün", "unutma": "unutmayın", "kaçırma": "kaçırmayın", "varsayma": "varsaymayın",
    "karıştırma": "karıştırmayın", "geciktirme": "geciktirmeyin", "et": "edin", "kat": "katın", "geç": "geçin",
}
# 'cikar' 2. tekil emir sayilmaz: 3. tekil genis zamanla ayni (bedel ... cikar); 2. cogulu 'cikarin' belirsiz degil
SIZ_IMPERATIVES = frozenset(IMPERATIVES.values()) | {"çıkarın"}
# ad/sifat okumasi da olan bicimler: yalniz acik emir baglaminda sayilir (bir sorun, mevsim yaz, kalin duvar, GFT bak)
GUARDED = frozenset({"ara", "alın", "gelin", "kalın", "sorun", "koy", "koyun", "yaz", "yazın", "görüş", "çek", "taşın",
                     "bak", "aç"})
# GUARDED kelimeden once gelince ad/sifat okumasi: belirleyici, sifat, derece zarfi, zaman adi
NOUN_GUARD = frozenset({
    "bir", "bu", "şu", "o", "her", "hiçbir", "tek", "başka", "ciddi", "büyük", "küçük", "önemli", "asıl", "ortak",
    "yaygın", "olası", "mevsim", "sezon", "yalnız", "yalnızca", "sadece", "özellikle", "genellikle", "geçen", "gelecek",
    "önümüzdeki", "tüm", "bütün", "uzun", "kısa", "sıcak", "serin", "güzel", "kötü", "iyi",
    "çok", "oldukça", "daha", "en", "pek", "biraz", "gayet", "epey", "fazla", "aşırı", "hem",
    "kalabalık", "canlı", "açık", "kapalı", "sakin", "yoğun", "sessiz", "hareketli", "ılık", "soğuk", "siyasi", "dini",
    "sosyal", "kültürel", "farklı", "aynı", "yeni", "eski", "dönem", "dönemi", "sezonu", "mevsimi", "kışın", "baharın"})
COORDINATORS = frozenset({"ve", "veya", "yahut", "hem", "ne"})  # liste ogesi: inek ve koyun, damat ve gelin
DUTCH_HOMOGRAPHS = frozenset({"bak"})  # Hollandaca ad (kutu): kisaltma/Hollandaca kelimeden sonra (GFT bak, groene bak)
INFINITIVE = ("mak", "mek")  # park yeri bulmak sorun; -mAsI degil (tamir bulusmasi ara: ad tamlamasi)
LIGHT_NOUNS = frozenset({"kontrol", "takip", "teyit", "not", "dikkat", "teslim", "talep", "park", "beyan", "tarif",
                         "sipariş", "tercih", "rezerve", "iptal", "aktive", "devam", "itiraz", "ziyaret", "şikayet",
                         "şikâyet", "organize", "hareket", "sohbet", "davet", "kabul", "yardım", "ihbar", "iade",
                         "rapor", "tespit", "tahmin", "test", "terk", "tamir", "transfer", "teklif", "rica", "elde",
                         "idare", "tavsiye", "tedarik", "tekrar", "telafi", "temin", "teşekkür", "tasarruf", "dahil",
                         "fark", "ilan"})
PREV_REQUIRED = {"et": LIGHT_NOUNS, "kat": frozenset({"hesaba"}),
                 "geç": frozenset({"iletişime", "irtibata", "temasa", "sepete", "harekete", "sıraya"})}
# 2. cogul emre benzeyen 2. tekil emir: 'bilgi edin' (edinmek), 'hazir bulun' / 'talepte bulun' (X-DA bulunmak)
REFLEXIVE = frozenset({"edin", "bulun"})
EDINMEK_NOUNS = frozenset({"bilgi", "fikir", "arkadaş", "alışkanlık", "deneyim", "tecrübe"})
LOCATIVE = ("da", "de", "ta", "te")

SIZ_STEMS_NOT = ("beniz", "geniz", "henüz", "yalnız", "anız")  # 'deniz' her yerde (Akdeniz, Karadeniz) ayrica
# n ile biten govde + 1. cogul -Iz (eminiz, insaniz, zenginiz): 2. cogul iyelik olamaz (o 'emininiz' olurdu)
N_STEMS_1PL = frozenset({"emin", "insan", "zengin", "memnun", "pişman", "üzgün", "sakin", "yorgun", "çalışkan", "kadın",
                         "müslüman", "göçmen", "uzman"})
# -Ir/-Ar + sIn bicimli ama 2. tekil olmayan uc+ heceliler (3. tekil emir); iki heceliler ve -DIrsIn kuralla disarida
R3SG_NOT = frozenset({"göndersin", "getirsin", "götürsün", "otursun", "göstersin", "bitirsin", "yatırsın", "çevirsin",
                      "geçirsin", "çağırsın", "aktarsın", "düşürsün"})
AORIST_2SG_SHORT = frozenset({"yersin"})  # iki heceli gercek 2. tekil genis zaman (ye-r-sin); dersin ilgi eki de olur
# iki heceli -rsAn yalniz tek heceli fiilde 2. tekildir (versen, girsen, dersen); kersen, persen Hollandaca
R_VERBS_1SYL = frozenset({"ver", "gir", "dur", "vur", "sür", "kur", "sar", "var", "kar", "yar", "kır", "der", "yer",
                          "er", "ger", "bur", "dür", "bür", "yor"})
COPULA_NOT = frozenset({"şahsen"})
# unsuzle biten ad/sifat + -In: 2. tekil iyelik okunmaz (ad ya da var/yok/olmali ile kullanilan sifat)
POSS_NOT = frozenset({
    "izin", "sorun", "kadın", "fırın", "zemin", "tahmin", "metin", "ekin", "akın", "altın", "yakın", "tribün", "düğün",
    "bütün", "gün", "bugün", "dün", "uygun", "uzun", "salgın", "yangın", "yaygın", "olgun", "coşkun", "keskin", "serin",
    "derin", "engin", "yetkin", "etkin", "seçkin", "belirgin", "zengin", "üzgün", "yorgun", "düzgün", "durgun",
    "kırgın", "sürgün", "taşkın", "baskın", "şaşkın", "çılgın", "bilgin", "mümkün",
    "sabun", "ürün", "oyun", "koyun", "burun", "boyun", "kabin", "vitrin", "kanun", "kantin", "benzin", "zeytin",
    "vitamin", "tütün", "turbin", "yasemin", "termin", "sakin", "emin", "kesin", "çetin", "kalın", "çirkin", "bitkin",
    "düşkün", "tutkun", "küskün", "suskun", "yatkın", "sıkkın", "bıkkın"})
# -mAn ile biten ad/sifat/zarf: 'icin/gerek' oncesinde 2. tekil eylem adi sayilmaz (unlu uyumu bozuklar kuralla)
MAN_NOT = frozenset({"zaman", "uzman", "danışman", "göçmen", "öğretmen", "yönetmen", "eğitmen", "eleman", "orman",
                     "liman", "duman", "roman", "alman", "tercüman", "kurban", "yazman", "düşman", "kahraman", "harman",
                     "değirmen", "şaman", "çimen", "egemen", "tümen", "seğmen", "türkmen", "hemen", "tamamen", "kısmen",
                     "seçmen", "denetmen", "gözetmen", "çevirmen", "okutman", "barmen", "kameraman", "yaman", "kocaman",
                     "şişman", "pişman", "koskocaman"})
# -DIk/-AcAk ile biten ad: ilgi eki -In (gelecegin, findigin) 2. tekil -DIgIn/-AcAgIn'e benzer
DIK_NOUNS = frozenset({"gelecek", "yiyecek", "içecek", "giyecek", "yakacak", "fındık", "sandık", "mantık", "kritik",
                       "estetik", "kozmetik", "istatistik", "lojistik", "artık", "kütük"})
# genel -yIn/-DIrIn emir kuralinin disarida biraktigi adlar (ilgi eki) ve zaman zarflari
GENERIC_NOT = frozenset({"olayın", "sarayın", "alayın", "güneyin", "kuzeyin", "yüzeyin", "düzeyin", "bireyin",
                         "dikeyin", "kolayın", "kültürün", "müdürün", "çadırın", "satırın", "takdirin", "tandırın",
                         "hatırın", "katırın", "sabahleyin", "akşamleyin", "geceleyin", "öğleyin"})
EXISTENTIAL = frozenset({"var", "yok", "varsa", "yoksa", "vardır", "yoktur", "varken", "yokken", "olmalı", "olmalıdır"})
MAN_NEED = ("gerek", "lazım", "şart", "zorunlu")  # basvurman gerekir/gerekli; 'icin' yalniz tam kelime (icinde degil)

# cogul 'siz' (hitaptir, resmi 'siz' degil; sen metnini karisik yapmaz): zamir, birlikte, es/partner, karsilikli eylem
PLURAL_YOU = ("hepiniz", "ikiniz", "biriniz", "hiçbiriniz", "herbiriniz", "bazılarınız", "çoğunuz", "kaçınız",
              "üçünüz", "dördünüz")
TOGETHER = frozenset({"birlikte", "beraber", "beraberce", "ortaklaşa"})
# 2. tekil iyelikli es/partner/aile (partnerin, esinle, toeslagpartner'in): sen + o = cogul 'siz'
COMPANION = re.compile(r"^(?:[^\W\d_']*partner'?[ıi]n|eşin|ortağın|sevgilin|nişanlın|ailen)(?:l[ae]|[ıi]n)?$")
RECIPROCAL = ("kararlaştır", "uzlaş", "evlen", "boşan", "tanış", "nikahlan", "nikâhlan")  # kararlastirmasaniz
RELATION = ("ilişki", "evliliğ", "birlikteliğ", "beraberliğ", "ortaklığ", "nikah", "nikâh")  # iliskiniz, evliliginiz
# metin duzeyi: 'sen ve X', 'X ve sen', 'sen dahil', 'senin, X'in ve' -> metindeki tum 2. cogul bicimler cogul 'siz'
JOINT = re.compile(r"(?<![^\W\d_])(?:(?:sen|senin|seni|sana)\s+(?:ve|dahil|ile)|senin\s*,"
                   r"|(?:ve|ile)\s+(?:sen|senin|seni|sana))(?![^\W\d_])")
CONJUNCTIONS = frozenset({"ve", "veya", "ya", "ama", "fakat"})  # yan cumle sonu (ilk kelimede sayilmaz)

_CASE = r"(?:[ıiuü]|[ae]|[dt][ae](?:n|ki)?|l[ae]|[ıiuü]n|[cç][ae]|[dt][ıiuü]r|ki)?"
SIZ_SUFFIX = re.compile(rf"(?P<v>[{VOWELS}])n(?P<w>[ıiuü])z(?P<case>{_CASE})$")
SIZ_AFTER_APOSTROPHE = re.compile(rf"^(?:.*(?P<v>[{VOWELS}]))?n(?P<w>[ıiuü])z{_CASE}$")
SIZ_NEGATIVE = re.compile(r"m[ae]y[ıi]n$")
SIZ_GENERIC = re.compile(r"(?:y[ıiuü]n|[dt][ıiuü]r[ıiuü]n)$")
SEN_TENSE = re.compile(
    r"(?:yors[ua]n|[ae]c[ae]ks[ıi]n|[ae]c[ae]ks[ae]n|m[ae]l[ıi]s[ıi]n|m[ae]l[ıi]ys[ae]n|m[ae]zs[ıi]n|m[ae]zs[ae]n"
    rf"|m[ıiuü]şs[ıiuü]n|m[ıiuü]şs[ae]n|(?<=[{VOWELS}])ys[ae]n"
    r"|(?<=[^\W\d_]{3})[dt][ae]s[ıi]n|(?<=[^\W\d_]{2})m[ae]s[ae]n)$")
SEN_AORIST = re.compile(r"(?<=[aeıiuü])rs(?P<v>[ıiuü]|[ae])n$")  # -Ir/-Ar + sIn/sAn
SEN_PARTICIPLE = re.compile(r"(?<=[^\W\d_]{2})(?:[dt](?P<i>[ıiuü])ğ[ıiuü]|(?P<a>[ae])c[ae]ğ[ıi])n$")  # -DIgIn/-AcAgIn
# ettirgen -DIr + 3. tekil emir: d her yerde (degerlendir-sin, yazdir-sin), t yalniz sert unsuzden sonra (yaptir-sin,
# kesinlestir-sin); r/l/n + t ettirgen -t'nin 2. tekil genis zamanidir (cevirt-ir-sin, ayirt-ir-sin)
R3SG_DIR = re.compile(r"(?:[çfhkpsşt]t|[^\W\d_]d)[ıiuü]rs[ıiuü]n$")
SEN_AFTER_APOSTROPHE = re.compile(r"(?:y?s[ae]n|y?s[ıiuü]n|[dt][ae]s[ıi]n|[dt][ae]ys[ae]n)")
COPULA_CONDITIONAL = re.compile(rf"(?<=[{CONSONANTS}])s[ae]n$")
POSSESSIVE = re.compile(rf"[{CONSONANTS}][ıiuü]n$")
ADJ_GIN = re.compile(rf"[{CONSONANTS}]g[ıiuü]n$")  # -gIn sifati (yorgun, ergin, dalgin): iyelik degil
VERBAL_NOUN = re.compile(r"m[ae]n$")
PLURAL_NOMINATIVE = re.compile(r"l[ae]r$")  # 'Cocuklar ac.': yalin cogul addan sonra yuklem sifat/ad
