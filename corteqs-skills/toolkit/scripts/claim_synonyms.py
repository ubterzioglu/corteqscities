"""claim_synonyms: claim_check'in ceviri es anlamlisi tablolari (Turkce kart degeri <-> EN/NL/DE/TR kaynak bicimi).

Yalniz regex parcalari ve kuruculari (words_rx, names_rx, day_rx, ordinal_day_rx); ag ya da dosya erisimi yok. Hepsi 'unit':
  yas  : 'aged 12 to 18', 'ages 4-11', '(the) age of 8', 'onder de 18', 'ouder dan 18', 'under 21', 'over 65', '50 or older',
         '12 and under', '0 tot en met 3 jaar', '5 till 15 years', '18 yaş', 'kind wordt 4'. Ardindan birim gelen sayi yas
         degildir; aralikta aralik sonuna bakilir ('aged 12 to 18 months', 'aged 6-12 months': 12 ve 6 yas degil).
         Yalin under/over/below/above yalniz izinli baglamla: noktalama, and/or, years/jaar/old, are/must/may/pay/zijn...
         ('under 12 may', 'over 65?'); 'over 50 nationalities', 'Over 18 000 visitors', 'Orders of 50 and over' yas degil.
         Yaziyla sayi on ekten sonra yalniz age/aged/ages/leeftijd ile ('the age of one'; 'leeftijd van een kind' degil).
  sure : yaziyla 1-10 yalniz birimle (een maand, one year, two working days, vijf jaar, iki hafta; 'on' yalniz Turkce birimle),
         tireli birim ('12-week'), sifat ('16 statutory holiday days'), bilesik ('levensjaren', 'vakantiedagen').
  saat : '10.00' = '10:00' = '10 uur' = '10 a.m.' = '10am'; '00:30' = '12:30 AM'; '00:00' = 'midnight'; '10:00 pm' 10:00 degil
  gun  : Turkce adlar (pazartesi..pazar), kisaltmalar (ma/di/wo/do/vr/za/zo, Mon..Sun, Pzt..Paz) yalniz takvim baglaminda:
         saatten ya da saat araligindan once ('za 08.00', 'Tue: 10.00', 'za 10-16 uur', 'Sa 10-16') veya gun araliginda
         ('ma t/m za', 'Mon-Fri'). 'vrij'/'zo' (Hollandaca 'serbest'/'boyle') yalniz dakikali saat/saat araligindan once ya da
         -, /, &, t/m ile ('Toegang vrij, za en zo', 'zo 2 uur', 'maandag en zo verder' cuma/pazar degil).
         Turkce 'son' (ayin son pazari) yalniz Turkce gun adiyla ('your son on Sunday' degil).
Turkce birim ve gun ekleri claim_extract'in beyaz listesidir: '2 senet', '3 güncel', 'Pazarlama', 'salıncak' eslesmez.
"""
from __future__ import annotations

import re
from typing import Iterable

from claim_extract import PREFIX_PCT, SCALES, TR_DAY_SUFFIX, UNIT_PATTERNS, alternation as _alts

# Yaziyla sayilar (EN/NL/TR); yalniz yas ve sure degerlerinde, birim kelimesiyle birlikte gecerlidir.
# Hollandaca 'een' hem sayi hem belirtectir: birim hemen ardindan gelmeli ('een maand' = 1 maand, 'een keer per week' degil).
NUMBER_WORDS = {1: ("one", "een", "één", "eén", "bir"), 2: ("two", "twee", "iki"), 3: ("three", "drie", "üç"),
                4: ("four", "vier", "dört"), 5: ("five", "vijf", "beş"), 6: ("six", "zes", "altı"), 7: ("seven", "zeven", "yedi"),
                8: ("eight", "acht", "sekiz"), 9: ("nine", "negen", "dokuz"), 10: ("ten", "tien", "on")}
ARTICLES = frozenset({"een", "bir"})  # belirtec de olan sayi kelimesi yas on ekinden sonra sayilmaz: 'leeftijd van een kind'
WORD_GUARDS = {"on": r"(?=\s(?:iş\s)?(?:saat|gün|hafta|ay|yıl|sene|yaş))"}  # Ingilizce 'on (working days)' Turkce 10 degil
WORDED_KINDS = frozenset({"age", "duration"})


def words_rx(words: Iterable[str]) -> str:
    """Tam kelime secenekleri ('vijf' 'vijftig' icinde eslesmez); bazi kelimeler WORD_GUARDS baglami ister."""
    ordered = sorted(set(words), key=lambda w: (-len(w), w))
    return r"\b(?:" + "|".join(re.escape(w) + WORD_GUARDS.get(w, "") for w in ordered) + r")\b"


ANY_NUMBER_WORD = words_rx(w for ws in NUMBER_WORDS.values() for w in ws)
RANGE_WORDS = r"(?:-|tot\sen\smet|tot|t/m|à|a|of|to|or|bis|en|and|till|until|untill|through|thru)"
RANGE_LINK = rf"(?:\s?{RANGE_WORDS}\s?(?:\d+(?:[.,]\d+)?|{ANY_NUMBER_WORD}))?\s?"
_UNITS = {  # NL/EN/DE bilesikleri ('werkdagen', 'levensjaren'); Turkce ekli bicimler claim_extract.UNIT_PATTERNS'tan gelir
    "hour": r"(?:uur|uren|hours?|hrs?|stunden?)(?!\w)",
    "day": r"(?:werk|kalender|vakantie|verlof|school|business |working |calendar )?(?:dagen|dag|days?|tagen?|tage)(?!\w)",
    "week": r"(?:werk|school|vakantie)?(?:weken|weeks?|wochen?)(?!\w)",
    "month": r"(?:maanden|maand|months?|monaten?|monate)(?!\w)",
    "year": r"(?:levens|kalender|school|dienst)?(?:jaren|jaar|years?|jahren?|jahre)(?!\w)",
}
UNIT_WORDS = {unit: f"(?:{rx}|{UNIT_PATTERNS[unit]})" for unit, rx in _UNITS.items()}
UNIT_MODIFIERS = (r"(?:(?:statutory|consecutive|full|whole|extra|additional|paid|unpaid|holiday|vacation|leave|school"
                  r"|wettelijke|aaneengesloten|opeenvolgende|volle|hele|betaalde|onbetaalde|vakantie|verlof)\s){0,2}")
SCALE_WORDS = {n: _alts(w for w, s in SCALES.items() if s == n) + r"(?!\w)" for n in set(SCALES.values())}

AGE_LINK = r"(?:-|to|and|en|tot\sen\smet|tot|t/m|till|until)"
AGE_RANGE_HEAD = r"(?:\d{1,3}\s?" + AGE_LINK + r"\s?)?"  # aralikta ikinci sayi: 'aged 12 to 18'
AGE_RANGE_TAIL = r"(?>(?:\s?" + AGE_LINK + r"\s?(?:\d{1,3}(?!\d)|" + ANY_NUMBER_WORD + r"))?)"  # atomik: birim aralik sonunda
AGE_WORD_PREFIX = r"\b(?:aged?|ages|(?:the\s)?age\sof|(?:de\s)?leeftijd\svan)\s(?:between\s|tussen\s)?"
AGE_COMPARE_PREFIX = r"\b(?:(?:onder|boven)\sde|younger\sthan|older\sthan|jonger\sdan|ouder\sdan)\s"
AGE_BARE_PREFIX = r"\b(?:under|over|below|above)\s"
AGE_TURNS = r"\b(?:kind|child|zoon|dochter|son|daughter)\s(?:\w+\s)?(?:wordt|turns?)\s"
MONTH_NAMES = (("januari", "january", "januar", "jan"), ("februari", "february", "februar", "feb"),
               ("maart", "march", "märz", "mrt", "mar"), ("april", "apr"), ("mei", "may", "mai"), ("juni", "june", "jun"),
               ("juli", "july", "jul"), ("augustus", "august", "aug"), ("september", "sept", "sep"),
               ("oktober", "october", "okt", "oct"), ("november", "nov"), ("december", "dezember", "dec", "dez"))
SHORT_MONTHS = frozenset({"jan", "feb", "mrt", "mar", "apr", "may", "jun", "jul", "aug", "sep", "sept", "okt", "oct", "nov",
                          "dec", "dez"})  # kelime de olabilir ('may' modal): yalniz ardindan gun/yil sayisi gelirse ay
NOT_AGE_UNIT = (r"(?!\s\d{3}\b)(?!\s?(?:[%€°]|:\d|(?:euros?|eur|cent|procent|percent|keer|times|min(?:uten|utes?|s)?"
                r"|sec(?:onds?|onden)?|uur|uren|hours?|hrs?|dagen|dag|days?|weken|weeks?|maanden|maand|months?|km|kilomet\w*"
                r"|meters?|m2?|cm|mm|kg|kilo\w*|gram|liter\w*|graden|degrees|stuks|pieces|items|people|persons?|personen|mensen"
                r"|plaatsen|places|locaties|locations|" + _alts(n for ns in MONTH_NAMES for n in ns if n not in SHORT_MONTHS)
                + r")(?!\w)|" + _alts(SHORT_MONTHS) + r"\.?\s?\d))")
BARE_AGE_NEXT = (r"(?=['’]?s?(?:\s?(?:[-.,;:!?)/]|$)|\s(?:and|or|years?|yrs?|old|jaar|jaren|are|must|(?-i:may)|can|need|pay"
                 r"|get|go|travel|free|zijn|betalen|moeten|mogen|krijgen|gratis)(?!\w)))")  # yalin over/under: izinli baglam
NUMERIC_TEMPLATES = {  # {n}: rakam|kelime, {d}: yalniz rakam, {w}: rakam|belirtec olmayan kelime; digerleri TEMPLATE_PARTS
    "money": r"(?:€|\beur\b|\beuro\b)\s?{n}|{n}\s?(?:€|eur\b|euros?\b)",
    "percent": r"{n}\s?(?:%|procent\b|percent\b|prozent\b)|" + PREFIX_PCT + r"\s?{n}",
    "age": (r"{n}{link}(?:jaar|jaren|years?|yrs?|jahre?|yaş\w*)(?!\w)|{n}-?jarig\w*|{d}\+|{n}-?years?-olds?"
            r"|{n}\s(?:or|and|en|of)\s(?:older|younger|ouder|jonger)(?!\w)|(?<!\bof\s){d}\s(?:or|and)\s(?:over|above|up|under)(?!\w)"
            r"|{word_prefix}{head}{w}{tail}{not_unit}|{compare_prefix}{head}{d}{tail}{not_unit}|{turns}{d}{tail}{not_unit}"
            r"|{bare_prefix}{head}{d}{tail}{bare_next}"),
    "duration": r"{n}{link}-?{mods}{unit}",
}
TEMPLATE_PARTS = {"link": RANGE_LINK, "mods": UNIT_MODIFIERS, "word_prefix": AGE_WORD_PREFIX, "compare_prefix": AGE_COMPARE_PREFIX,
                  "bare_prefix": AGE_BARE_PREFIX, "turns": AGE_TURNS, "head": AGE_RANGE_HEAD, "tail": AGE_RANGE_TAIL,
                  "not_unit": NOT_AGE_UNIT, "bare_next": BARE_AGE_NEXT}

DAY_NAMES = {"monday": ("maandag", "monday", "montag"), "tuesday": ("dinsdag", "tuesday", "dienstag"),
             "wednesday": ("woensdag", "wednesday", "mittwoch"), "thursday": ("donderdag", "thursday", "donnerstag"),
             "friday": ("vrijdag", "friday", "freitag"), "saturday": ("zaterdag", "saturday", "samstag"),
             "sunday": ("zondag", "sunday", "sonntag")}
TR_DAY_NAMES = {"monday": "pazartesi", "tuesday": "salı", "wednesday": "çarşamba", "thursday": "perşembe", "friday": "cuma",
                "saturday": "cumartesi", "sunday": "pazar"}
TR_DAY_TAIL = TR_DAY_SUFFIX.pattern + r"(?!\w)"  # 'Pazartesi'den', 'Salıları'; 'Pazarlama', 'salıncak', 'Cumartesi' (cuma) degil
NAME_TAIL = r"(?!es?\b)\w*"  # NL/EN/DE bilesik serbest ('donderdagmiddag', 'Sundays'); 'montage' (Montag + e) degil
DAY_ABBREVIATIONS = {  # 'per' (Turkce persembe) 'per 2 uur' ile, 'zat'/'zon' Hollandaca kelimelerle karistigi icin yok
    "monday": ("ma", "mo", "mon", "pzt"), "tuesday": ("di", "tu", "tue", "tues", "sal"), "wednesday": ("wo", "wed", "çar", "çrş"),
    "thursday": ("do", "th", "thu", "thur", "thurs", "prş"), "friday": ("vr", "vrij", "fr", "fri", "cum"),
    "saturday": ("za", "sa", "sat", "cmt", "cts"), "sunday": ("zo", "su", "sun", "paz")}
LOOSE_ABBREVIATIONS = frozenset({"vrij", "zo"})  # Hollandaca 'serbest'/'boyle' de: yalniz kati saat ya da -, /, &, t/m ile
ANY_DAY = (rf"(?:{_alts(n for ns in DAY_NAMES.values() for n in ns)}{NAME_TAIL}|{_alts(TR_DAY_NAMES.values())}{TR_DAY_TAIL}"
           rf"|{_alts(a for abbrs in DAY_ABBREVIATIONS.values() for a in abbrs)}(?!\w))")
DAY_LINK = r"\s?(?:-|/|&|,|t/m?|tot|en|and|to|till|through|thru)\s?"
TIGHT_LINK = r"\s?(?:-|/|&|t/m?)\s?"
CLOCK_RANGE = (r"\d{1,2}(?:[.:]\d{2})?\s?-\s?(?:\d{1,2}(?:[.:]\d{2})?\s?(?:uur|uhr|u|h)(?!\w)"
               r"|(?:1\d|2[0-4])(?:[.:]\d{2})?(?![.:,]?\d))")  # 'za 10-16 uur', 'Sa 10-16'; 'do 2-4 times' degil
CLOCK = r"\s?:?\s?(?:" + CLOCK_RANGE + r"|\d{1,2}(?:[.:]\d{2}|\s?(?:uur|u|h|am|pm|a\.m|p\.m)(?!\w)))"
STRICT_CLOCK = r"\s?:?\s?(?:" + CLOCK_RANGE + r"|\d{1,2}(?:[.:]\d{2}|\s?(?:am|pm|a\.m|p\.m)(?!\w)))"  # 'zo 2 uur' saat degil
ORDINAL_WORDS = {1: ("eerste", "first", "erste", "1e", "1ste", "1st"), 2: ("tweede", "second", "zweite", "2e", "2de", "2nd"),
                 3: ("derde", "third", "dritte", "3e", "3de", "3rd"), 4: ("vierde", "fourth", "vierte", "4e", "4de", "4th"),
                 -1: ("laatste", "last", "letzte")}
TR_ORDINALS = {1: ("ilk", "birinci"), 2: ("ikinci",), 3: ("üçüncü",), 4: ("dördüncü",), -1: ("son",)}
AMPM = {"am": r"a\.?\s?m\b\.?", "pm": r"p\.?\s?m\b\.?"}
CLOCK_WORDS = {(0, "00"): (r"\bmidnight\b", r"\bmiddernacht\b", r"(?<![\d.,:])24[:.]00(?!\d)"), (12, "00"): (r"\bnoon\b",)}


def names_rx(day: str) -> str:
    """Tam gun adi: NL/EN/DE bilesikleriyle ('donderdagavond', 'Sundays'), Turkce yalniz claim_extract ekleriyle."""
    return rf"(?:{_alts(DAY_NAMES[day])}{NAME_TAIL}|{re.escape(TR_DAY_NAMES[day])}{TR_DAY_TAIL})"


def day_rx(day: str) -> str:
    """Tam gun adi ya da kisaltma yalniz takvim baglaminda: 'za 08.00', 'za 10-16 uur', 'ma t/m za', 'Mon - Fri'."""
    abbrs = DAY_ABBREVIATIONS[day]
    groups = [(_alts(group), clock, link) for group, clock, link in (
        (tuple(a for a in abbrs if a not in LOOSE_ABBREVIATIONS), CLOCK, DAY_LINK),
        (tuple(a for a in abbrs if a in LOOSE_ABBREVIATIONS), STRICT_CLOCK, TIGHT_LINK)) if group]
    before = "|".join(rf"{abbr}(?!\w)\.?(?={clock}|{link}{ANY_DAY})" for abbr, clock, link in groups)
    after = "|".join(rf"{link}{abbr}" for abbr, _clock, link in groups)  # ANY_DAY bir kez denenir (hiz)
    return rf"\b(?:{names_rx(day)}|{before}|{ANY_DAY}\.?(?:{after})(?!\w))"


def ordinal_day_rx(day: str, ordinal: int) -> str:
    """'derde zondag', 'last Sunday', 'ayın son pazarı': Turkce sira kelimesi yalniz Turkce gun adiyla."""
    return (rf"\b{_alts(ORDINAL_WORDS[ordinal])}\s(?:\w+\s)?{names_rx(day)}"
            rf"|\b{_alts(TR_ORDINALS[ordinal])}\s(?:\w+\s)?{re.escape(TR_DAY_NAMES[day])}{TR_DAY_TAIL}")
