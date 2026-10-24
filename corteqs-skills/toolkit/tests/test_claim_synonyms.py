"""claim_synonyms: Turkce kart degeri <-> EN/NL/DE/TR kaynak bicimi (ceviri es anlamlilari, A4) ve asiri eslesme korumalari."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

import claim_check as cc

FILLER = "Algemene informatie over de dienstverlening en de voorwaarden. " * 12
URL = "https://www.example.org/info"


def _age(v):
    return {"kind": "age", "value": v}


def _dur(v, unit):
    return {"kind": "duration", "value": v, "unit": unit}


def _time(v):
    return {"kind": "time", "value": v}


def _day(v, ordinal=None):
    return {"kind": "weekday", "value": v, **({"ordinal": ordinal} if ordinal is not None else {})}


def _level(value, text):
    return cc.match_value(value, cc.normalize_text(text))[0]


HOURS_NL = "Openingstijden: ma t/ do 08.00 - 22.30 uur vrij & za 08.00 - 04.30 uur"
HOURS_NL_2 = "Openingstijden: ma t/m za 07.00 - 01.00 uur zo 11.00 - 01.00 uur"
CONSULATE = "ÇALIŞMA SAATLERİ Pazartesi - Cuma 08:30 - 12:30 / 13:00 - 17:00"
GLOW = "Entering is not possible between 6:30 PM and 12:30 AM."
DAF = "Opened: Tuesday to Sunday, from 10 a.m. till 5 p.m The DAF Museum is closed on Mondays."
FREE_ENTRY = "Toegang vrij, za en zo 12.00 - 17.00 uur."


@pytest.mark.parametrize("value,text", [
    # yas: on ekli (aged/ages/age of/under/over/onder de/ouder dan), aralikli ve 'X or older' bicimleri
    (_age(12), "Secondary schools for newcomers aged 12 to 18 are called ISK."),
    (_age(18), "Secondary schools for newcomers aged 12 to 18 are called ISK."),
    (_age(11), "The ISE Secondary Department (ages 11-18) offers the IB."),
    (_age(18), "The ISE Secondary Department (ages 11-18) offers the IB."),
    (_age(17), "Are you aged between 12 and 17 and do you have a youth ticket?"),
    (_age(6), "A free hunt is available for children aged 6-15."),
    (_age(15), "A free hunt is available for children aged 6-15."),
    (_age(13), "Admission Adults € 16 Children under age 13 Free"),
    (_age(30), "Students under the age of 30 who are here to study."),
    (_age(8), "Only years from the age of 8 on count towards the period."),
    (_age(21), "You are disabled and under 21 You are under 21 and live at home."),
    (_age(12), "Are you under 12 or over 65? Then you get a discount."),
    (_age(65), "Are you under 12 or over 65? Then you get a discount."),
    (_age(12), "Children under 12 must go to the embassy."),
    (_age(18), "The premium is €159 per person (over 18)."),
    (_age(50), "Arrangements for employees who are 50 or older."),
    (_age(18), "Visitors aged 18 and over must buy a ticket."),
    (_age(13), "Parents help their child with the age of 13 and under."),
    (_age(4), "Mijn situatie verandert Mijn kind wordt 4 Mijn kind gaat naar school"),
    (_age(0), "Mini's Tussen 0 tot en met 3 jaar ontdekt jouw kind"),
    (_age(4), "Voor kinderen van 4 tot en met 12 jaar (basisschoolleeftijd)."),
    (_age(5), "Children from 5 till 15 years: € 7,00 p/p."),
    (_age(18), "Kinderen onder de 18 betalen geen premie."),
    (_age(18), "Je moet ouder dan 18 zijn."),
    (_age(5), "Kinderen vanaf vijf jaar."),
    (_age(18), "18 yaş altı çocuklar prim ödemez."),
    # yalin under/over: izinli baglam (modal 'may', 'free', 'go', 65s) ve 'X and under'; yaziyla sayi 'age of' sonrasi
    (_age(12), "Children under 12 may travel free of charge."),
    (_age(65), "Residents over 65 may apply for a discount."),
    (_age(4), "Kids under 4 go free."),
    (_age(65), "Over 65s travel free."),
    (_age(12), "Children 12 and under go free."),
    (_age(1), "Children from the age of one pay half."),
    # sure: yaziyla sayi (1-10, TR/EN/NL), tireli birim, aralik, Hollandaca bilesik, sifat, Turkce ek beyaz listesi
    (_dur(5, "week"), "The vacancy has been open for at least five weeks."),
    (_dur(3, "month"), "Work in the Netherlands for less than three months."),
    (_dur(5, "year"), "In de afgelopen vijf jaar zijn de banen gegroeid."),
    (_dur(2, "day"), "Two working days later, you will receive a letter."),
    (_dur(2, "year"), "For a maximum period of two years in a university."),
    (_dur(2, "year"), "Een lening voor meer dan twee jaar."),
    (_dur(1, "month"), "Hebt u een maand lang de tijd om op te zeggen."),
    (_dur(1, "month"), "Eén maand van tevoren informeren."),
    (_dur(1, "year"), "Most are fixed for one year."),
    (_dur(10, "day"), "Binnen tien dagen betalen."),
    (_dur(2, "week"), "İki hafta içinde başvur."),
    (_dur(10, "day"), "On gün içinde ödenir."),
    (_dur(2, "week"), "Binnen twee tot drie weken."),
    (_dur(3, "week"), "Binnen twee tot drie weken."),
    (_dur(12, "week"), "Talent100 is a 12-week career re-entry program."),
    (_dur(6, "month"), "Less than 4 months in a 6-month period."),
    (_dur(5, "year"), "Five-year renewal € 85,00"),
    (_dur(16, "day"), "Entitled to 16 statutory holiday days per year."),
    (_dur(1, "year"), "You receive, at least 1 consecutive year, money."),
    (_dur(4, "year"), "Gedurende de eerste 4 levensjaren bezoek je het bureau."),
    (_dur(20, "day"), "Je hebt recht op 20 vakantiedagen."),
    (_dur(2, "year"), "2 senelik sözleşme."), (_dur(6, "month"), "6 aylık oturum izni."), (_dur(5, "day"), "5 iş günü sürer."),
    # saat: a.m./p.m. (noktali, bitisik), 00:xx = 12:xx AM, gece yarisi, ogle
    (_time("10:00"), DAF), (_time("17:00"), DAF),
    (_time("17:00"), "Our opening hours are from 5:00 p.m. to 8:00 a.m. on weekdays."),
    (_time("08:00"), "Our opening hours are from 5:00 p.m. to 8:00 a.m. on weekdays."),
    (_time("00:30"), GLOW), (_time("18:30"), GLOW),
    (_time("10:00"), "Open 10am-5pm daily."),
    (_time("00:00"), "Closed to traffic between 6:00 pm and midnight."),
    (_time("12:00"), "Lunch break from 12 pm."),
    # gun: Turkce adlar (ek beyaz listesi), NL/EN kisaltmalar yalniz takvim baglaminda (saat, saat araligi, gun araligi)
    (_day("monday"), CONSULATE), (_day("friday"), CONSULATE),
    (_day("sunday"), "Pazar günü kapalıdır."), (_day("tuesday"), "Salıları kapalı."),
    (_day("monday"), "Pazartesi'den Cuma'ya 09:00-17:00."), (_day("friday"), "Pazartesi'den Cuma'ya 09:00-17:00."),
    (_day("monday"), HOURS_NL), (_day("thursday"), HOURS_NL), (_day("friday"), HOURS_NL), (_day("saturday"), HOURS_NL),
    (_day("sunday"), HOURS_NL_2),
    (_day("friday"), "Open Mon-Fri 9:00-17:00."),
    (_day("friday"), "Open Mon - Fri."),
    (_day("tuesday"), "Tue: 10.00-17.00"),
    (_day("saturday"), "za 10-16 uur"), (_day("sunday"), "zo 12-17 uur"), (_day("saturday"), "Sa 10-16"),
    (_day("saturday"), FREE_ENTRY), (_day("sunday"), FREE_ENTRY), (_day("friday"), "ma t/m vrij 9-17 uur"),
    (_day("sunday", 3), "Her ayın üçüncü pazarı kurulur."),
    (_day("sunday", -1), "Ayın son pazarı açık."), (_day("sunday", -1), "Every last Sunday of the month."),
])
def test_translation_synonyms_match_at_unit_level(value, text):
    level, snippet = cc.match_value(value, cc.normalize_text(text))
    assert level == "unit" and snippet


@pytest.mark.parametrize("value,text,level", [
    (_age(18), "Doorstromen na 12 tot 18 maanden.", "number"),  # ay, yas degil
    (_age(18), "Babies aged 12 to 18 months.", "number"),
    (_age(12), "Babies aged 12 to 18 months.", "number"),  # aralik sonundaki birim ilk sayiyi da bozar
    (_age(6), "Baby swimming for babies aged 6-12 months.", "number"),
    (_age(5), "All within 5 minutes walking distance.", "number"),
    (_age(12), "Het duurt over 12 weken.", "number"),
    (_age(18), "We praten over 18 september.", "number"),
    (_age(18), "Kosten onder de 18 euro.", "number"),
    (_age(5), "Vijftig jaar geleden.", None),  # 'vijf' kelime parcasi
    # yalin over/under + sayim ismi, binlik grup, 'of N and over', yaziyla sayi ve Hollandaca 'een' belirteci yas degil
    (_age(50), "Eindhoven has over 50 nationalities.", "number"),
    (_age(30), "Students from over 30 countries study here.", "number"),
    (_age(25), "Classes have under 25 students.", "number"),
    (_age(65), "There are over 65 companies on campus.", "number"),
    (_age(18), "Over 18 000 visitors came.", "number"),
    (_age(50), "Orders of 50 and over ship free.", "number"),
    (_age(18), "Talks continue over 18 May.", "number"),  # buyuk harfli 'May' ay adi, modal 'may' degil
    (_age(2), "The museum is spread over two floors.", None),
    (_age(1), "All services under one roof.", None),
    (_age(1), "Dit hangt af van de leeftijd van een kind.", None),
    (_age(1), "Mijn zoon wordt een tiener.", None),
    (_dur(5, "week"), "Vijftig weken.", None),
    (_dur(5, "week"), "Er waren vijf mensen.", None),  # yaziyla sayi birimsiz kanit degil
    (_dur(1, "week"), "Een keer per week.", None),
    (_dur(2, "week"), "Twee keer per week.", None),
    (_dur(2, "week"), "2 per week.", "number"),
    (_dur(1, "month"), "Once a month.", None),  # 'a' sayi kelimesi degil
    (_dur(10, "day"), "Open on working days from 9 to 5.", None),  # Ingilizce 'on' Turkce 'on' (10) degil
    (_dur(9, "week"), "Parents get paid the first 9 of the 26 weeks parental leave.", "number"),
    # Turkce birim ekleri claim_extract beyaz listesiyle: 'senet', 'güncel', 'ayrı', 'yıldız' birim degil
    (_dur(2, "year"), "2 senet imzalanır.", "number"), (_dur(3, "day"), "3 güncel bilgi.", "number"),
    (_dur(2, "month"), "2 ayrı başvuru gerekir.", "number"), (_dur(5, "year"), "5 yıldızlı otel.", "number"),
    (_time("12:30"), GLOW, None),  # 12:30 AM = 00:30
    (_time("10:00"), "Open until 10:00 pm.", None),  # 22:00
    (_time("18:30"), "Open until 6 pm.", None),  # dakika dusmez
    (_time("10:00"), "Bus 10 Amsterdam Centraal.", None),
    (_time("24:00"), "Lunch break from 12 pm.", None),  # elle yazilmis 24:00 oglen degil
    (_day("friday"), "Cumartesi kapalı.", None),
    (_day("sunday"), "Pazartesi açık.", None),
    (_day("sunday"), "Pazarlama ekibi hafta içi çalışır.", None), (_day("tuesday"), "Salıncak parkı yenilendi.", None),
    (_day("monday"), "De montage van de fiets kost tijd.", None),  # Almanca 'Montag' + e: montaj, pazartesi degil
    (_day("wednesday"), HOURS_NL_2, None),  # 'ma t/m za' araligi genisletilmez
    (_day("sunday"), "Het is zo mooi in de zomer.", None),
    (_day("thursday"), "Things to do in Eindhoven.", None),
    (_day("thursday"), "Things to do 2-4 times a week.", None),  # saat araligi degil
    (_day("monday"), "Ma en pa gaan uit eten.", None),
    (_day("friday"), "Vrij parkeren in het centrum.", None),
    # 'vrij'/'zo' yalniz dakikali saat ya da saat araligindan once veya -, /, &, t/m ile; 'son' yalniz Turkce gun adiyla
    (_day("friday"), FREE_ENTRY, None),
    (_day("sunday"), "Het duurt zo 2 uur voordat je klaar bent.", None),
    (_day("sunday"), "Open op maandag en zo verder.", None),
    (_day("sunday", -1), "Visit your son on Sunday.", "number"),
])
def test_translation_synonyms_do_not_overmatch(value, text, level):
    assert _level(value, text) == level


def _claim(cid: str, values: list[dict]) -> dict:
    return {"claim_id": cid, "entry_id": cid.split(":#")[0], "sheet": "Yanıtlar", "_row": 8, "field": "summary",
            "kind": values[0]["kind"], "text": "x", "sentence": "Örnek cümle.", "values": values,
            "source_ids": ["s0"], "sources": [{"source_id": "s0", "url": URL}], "missing_source_ids": []}


def _index(root: Path, body: str) -> cc.SnapshotIndex:
    (root / "a.txt").write_text(body, encoding="utf-8")
    (root / "index.jsonl").write_text(json.dumps({"url": URL, "status": 200, "text_file": "a.txt"}) + "\n", encoding="utf-8")
    return cc.load_snapshots(root, "toolkit", min_chars=500)


def test_translated_card_claims_are_supported_in_unit_mode(tmp_path):
    body = (f"{FILLER} Secondary schools for newcomers aged 12 to 18. Two working days later you get a letter. "
            f"{DAF} {CONSULATE} Baby swimming for babies aged 6-12 months. {FILLER}")
    index = _index(tmp_path, body)
    claims = [_claim("e:a:#1", [_age(12), _age(18)]), _claim("e:a:#2", [_dur(2, "day")]),
              _claim("e:a:#3", [_time("10:00"), _time("17:00")]), _claim("e:a:#4", [_day("monday")]),
              _claim("e:a:#5", [_day("friday")]), _claim("e:a:#6", [_age(6)])]
    results = cc.check_claims(claims, index, mode="unit")["results"]
    assert [r["result"] for r in results] == ["supported"] * 5 + ["not_in_source"]  # '6-12 months' 6 yas degil
    assert all(r["value_levels"] == ["unit"] * len(r["values"]) for r in results[:5])


def test_synonym_tables_live_in_claim_synonyms_and_files_stay_small():
    """Tablolar claim_synonyms'ta; claim_check, claim_synonyms ve test_claim_check toolkit sinirinin (400 satir) altinda."""
    import claim_synonyms as cs

    assert cc.NUMERIC_TEMPLATES is cs.NUMERIC_TEMPLATES and cc.day_rx is cs.day_rx and cc.UNIT_WORDS is cs.UNIT_WORDS
    for path in (Path(cc.__file__), Path(cs.__file__), Path(__file__).with_name("test_claim_check.py")):
        assert len(path.read_text(encoding="utf-8").splitlines()) < 400, path.name
