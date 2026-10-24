"""Yer adi icindeki gun-ay tarih degildir (claim_extract tarih kurali, A5).

Yer adi sayilir: ay adina bitisik ya da tireli yer eki ('18 Septemberplein', '1 Oktoberstraße', '18 September-plein') ve
yilsiz, eksiz ay adindan HEMEN sonra buyuk harfle gelen yer adi sozcugu ('19 Mayıs Caddesi', '12 Eylül Sk.', '17 Juni Straße').
Tarih kalir: '18 september', '1 meiviering', '20 Kasım Cuma', '18 Eylül Markt'ta' (Markt tek basina meydan adidir), ek almis
ay ('4 Mayısta …'), yilli tarih ('1 Mayıs 2026 Sokak şenliği') ve araya baska ad giren yer ('4 Mayıs Dam Meydanı'nda').
Karar (V4): '30 Ağustos Zafer Bulvarı' turu Turk sokak adi da bu yuzden tarih sayilir; NL/DE paketlerinde nadirdir, gercek
tarihi silmemek onceliklidir.
"""
from __future__ import annotations

import re

PLACE_WORDS = ("plein", "straat", "laan", "weg", "singel", "kade", "gracht", "dreef", "steeg", "hof", "markt", "park",
               "pad", "dijk", "plantsoen", "boulevard", "brug", "poort", "wal", "veld", "baan", "ring", "allee", "passage",
               "straße", "strasse", "platz", "gasse", "damm", "ufer", "brücke", "chaussee")
_PLACE_ALTS = "(?:" + "|".join(sorted(PLACE_WORDS, key=lambda w: (-len(w), w))) + ")"  # yalniz harf: kacis gerekmez
PLACE_TAIL = re.compile(_PLACE_ALTS, re.IGNORECASE)  # 'Septemberplein(garage)': ay adina bitisik; 'meiviering' degil
PLACE_AFTER = re.compile(rf"-{_PLACE_ALTS}(?!\w)", re.IGNORECASE)  # '18 September-plein'
# Ayri yazilinca yalniz cadde/sokak turu sozcuk; 'Markt', 'Plein', 'Park', 'Ring', 'Singel' tek basina meydan/yol adidir
# ('18 Eylül Markt'ta' = tarih + Eindhoven Markt meydani). Turkce iyelik eki ad tamlamasini gosterir ('Parkı' evet, 'Park'ta' hayir).
SEPARATE_PLACE = frozenset({"Straat", "Laan", "Weg", "Dreef", "Steeg", "Plantsoen", "Straße", "Strasse", "Str.", "Platz", "Allee",
                            "Gasse", "Sokak", "Sok.", "Sk.", "Cad.", "Bulv.", "Mah."})
TR_PLACE_STEMS = ("caddesi", "sokağı", "meydanı", "bulvarı", "parkı", "köprüsü", "mahallesi", "stadyumu")
NEXT_WORD = re.compile(r"\s+(?P<w>[^\W\d_]\w*\.?)")


def place_word(word: str) -> bool:
    """Buyuk harfle ayri yer adi sozcugu: listede ('Straße', 'Sk.') ya da Turkce iyelikli ('Caddesi', 'Meydanı')."""
    return word[:1].isupper() and (word in SEPARATE_PLACE or word.rstrip(".") in SEPARATE_PLACE  # 'Sk.' / cumle sonu 'Laan.'
                                   or word.lower().startswith(TR_PLACE_STEMS))


def in_place_name(m: re.Match, text: str) -> bool:
    """Tarih eslesmesi bir yer adinin parcasi mi; m gruplari: t = ay adina bitisik ek, y = yil."""
    if PLACE_TAIL.match(m.group("t")) or PLACE_AFTER.match(text, m.end("t")):
        return True
    if m.group("y") or m.group("t"):
        return False  # yilli ya da ek almis tarih yer adinin parcasi olamaz
    nxt = NEXT_WORD.match(text, m.end())
    return nxt is not None and place_word(nxt.group("w"))
