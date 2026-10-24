"""acik_mi: places fazinin "bugun acik mi" kapisi (B15, P0) ve city-pack agents/acik-mi.md ile uyumu.

Ag yok; yazma yalniz tmp_path. Pilot ciktilari (uretim/eindhoven/_is, salt okunur) once tmp_path'e kopyalanir;
'real' isaretli testler pilot klasoru yoksa atlanir (pytest.ini; bu makinede vardir).
Calistirma: $env:PYTHONDONTWRITEBYTECODE=1; <PY> -m pytest -q -p no:cacheprovider tests\\test_acik_mi.py
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import shutil
import subprocess
import sys
import unicodedata
from collections import Counter
from dataclasses import dataclass
from pathlib import Path, PureWindowsPath

import pytest

import acik_mi
import skill_commands_helpers as sc

TOOLKIT = Path(__file__).resolve().parent.parent
SCRIPT, DOC = TOOLKIT / "scripts" / "acik_mi.py", TOOLKIT.parent / "city-pack" / "agents" / "acik-mi.md"
PILOT = TOOLKIT.parent.parent / "uretim" / "eindhoven" / "_is"
needs_pilot = pytest.mark.skipif(not (PILOT / "acik_mi").is_dir(), reason="pilot acik_mi klasoru yok")
CITY, MIN_YEAR, VENUES = "ornek", 2025, "Mekânlar.jsonl"  # kontrol yili = MIN_YEAR + 1 = 2026
NOTE = "5 Kasım 2026 itibarıyla kış arasında kapalı."
SECOND = "İkinci bağımsız kaynak: https://gemeente.example/nieuws/sluiting 'definitief gesloten'"


def write_jsonl(path: Path, rows: list[dict]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
    return path


def eid(slug: str) -> str:
    return f"{CITY}:{slug}"


def venue(slug: str, note: str = "", **extra) -> dict:
    return {"entry_id": eid(slug), "title": slug.title(), "subtitle": "", "summary": f"{slug.title()} özeti.",
            "source_ids": f"{CITY}:kaynak:001", "visit_status": "", "note": note, **extra}


def scan(slug: str, durum: str = "açık", **extra) -> dict:
    return {"entry_id": eid(slug), "title": slug.title(), "durum": durum, "kanit_url": f"https://{slug}.example/agenda",
            "kanit_alinti": "Concert op zaterdag 12 september 2026", "kanit_tarihi": "2026-09-12", "not": "", **extra}


def verify(slug: str, eylem: str = "dokunma", sonuc: str = "ret", **extra) -> dict:
    return {"entry_id": eid(slug), "title": slug.title(), "tarama_durum": "belirsiz", "sonuc": sonuc, "eylem": eylem,
            "kanit_url": f"https://nieuws.example/{slug}", "kanit_alinti": "Het museum blijft gewoon open.",
            "kanit_tarihi": "2026-05-01", "yeni_bilgi": "", "gerekce": "Tarihli haber açık olduğunu gösteriyor.",
            **extra}


@dataclass(frozen=True)
class Result:
    code: int
    summary: dict
    report: dict

    def codes(self) -> Counter:
        return Counter(item["code"] for item in self.report["findings"])

    def ids(self, code: str) -> list[str]:
        return sorted(item["entry_id"] for item in self.report["findings"] if item["code"] == code)


def run_main(capsys, argv: list) -> tuple[int, dict | None]:
    code = acik_mi.main([str(arg) for arg in argv])
    lines = capsys.readouterr().out.strip().splitlines()
    assert len(lines) <= 1, lines  # stdout tek satir JSON
    return code, json.loads(lines[0]) if lines else None


def gate(tmp_path: Path, capsys, venues: list[dict], scans: dict, verifs: dict | None = None, *extra: str,
         sources: list[dict] | None = None) -> Result:
    """<is>/acik_mi/<grup>.jsonl + <grup>_dogrulama.jsonl ve <is>/data/Mekânlar.jsonl yazar, kapiyi calistirir."""
    work, report = tmp_path / "_is", tmp_path / "rapor.json"
    shutil.rmtree(work, ignore_errors=True)
    (work / "acik_mi").mkdir(parents=True)
    for name, rows in [*scans.items(), *((f"{group}_dogrulama", rows) for group, rows in (verifs or {}).items())]:
        write_jsonl(work / "acik_mi" / f"{name}.jsonl", rows)
    argv = [work / "acik_mi", "--mekanlar", write_jsonl(work / "data" / VENUES, venues), "--min-year", MIN_YEAR,
            "--out", report]
    if sources is not None:
        argv += ["--kaynaklar", write_jsonl(work / "kaynak_dizini.jsonl", sources)]
    code, summary = run_main(capsys, [*argv, *extra])
    return Result(code, summary, json.loads(report.read_text(encoding="utf-8")))


# ------------------------------------------------------------------ temiz gecis, durum, kapsam

def test_clean_sweep_passes_with_counts_on_one_stdout_line(tmp_path, capsys):
    venues = [venue("museum"), venue("park"), venue("speeltuin", note="5 Kasım 2026 itibarıyla kış arasında kapalı.")]
    scans = {"muzeler": [scan("museum"), scan("park")], "cocuk": [scan("speeltuin", "geçici kapalı")]}
    verifs = {"muzeler": [], "cocuk": [verify("speeltuin", "kartta belirt", "onay", tarama_durum="geçici kapalı")]}
    result = gate(tmp_path, capsys, venues, scans, verifs)
    summary = result.summary
    assert result.code == 0 and result.report["findings"] == [] and summary["findings"] == 0
    assert (summary["tool"], summary["mekan"], summary["min_year"]) == ("acik_mi", 3, MIN_YEAR)
    assert (summary["tarama"], summary["dogrulama"]) == ({"dosya": 2, "satir": 3, "mekan": 3}, {"dosya": 2, "satir": 1})
    assert summary["durum"] == {"açık": 2, "geçici kapalı": 1}
    assert (summary["eylem"], summary["sonuc"]) == ({"kartta belirt": 1}, {"onay": 1})
    assert summary["listede_olmayan"] == {"tarama": 0, "dogrulama": 0} and summary["items"] == []


@pytest.mark.parametrize("durum", [*acik_mi.DURUMLAR, unicodedata.normalize("NFD", " açık ")])
def test_every_documented_status_is_accepted_after_normalization(tmp_path, capsys, durum):
    verifs = {} if durum == "açık" else {"g": [verify("yer", tarama_durum=durum)]}
    result = gate(tmp_path, capsys, [venue("yer")], {"g": [scan("yer", durum)]}, verifs)
    assert result.code == 0 and list(result.summary["durum"]) == [unicodedata.normalize("NFC", durum).strip()]


def test_unscanned_venue_bad_status_and_unverified_decision_are_findings(tmp_path, capsys):
    scans = {"g": [scan("a"), scan("b", "inşaat"), scan("c", "kapalı")]}  # d taranmadi; belgedeki deger 'insaat'
    result = gate(tmp_path, capsys, [venue(slug) for slug in "abcd"], scans)
    assert result.code == 1 and set(result.codes()) == {"tarama_yok", "gecersiz_durum", "dogrulama_yok"}
    assert result.ids("tarama_yok") == [eid("d")] and result.ids("gecersiz_durum") == [eid("b")]
    assert result.ids("dogrulama_yok") == [eid("b"), eid("c")]  # gecersiz durum da 'açık' degildir
    assert result.summary["durum"] == {"açık": 1, "inşaat": 1, "kapalı": 1}


def test_venue_scanned_in_two_groups_has_each_row_checked(tmp_path, capsys):
    """Pilotta bir mekan iki grubun taramasinda vardi; her satir ayri karardir."""
    scans = {"muzeler": [scan("abbehuis")], "sanat": [scan("abbehuis", "belirsiz")]}
    result = gate(tmp_path, capsys, [venue("abbehuis")], scans)
    assert result.ids("dogrulama_yok") == [eid("abbehuis")]
    assert result.summary["tarama"] == {"dosya": 2, "satir": 2, "mekan": 1}


def test_unknown_action_or_result_and_missing_ids_are_findings(tmp_path, capsys):
    scans = {"g": [scan(slug, "belirsiz") for slug in "abc"] + [{**scan("x"), "entry_id": ""}]}
    verifs = {"g": [verify("a", "silindi"), verify("b", "kartta_belirt"), verify("c", sonuc="evet"),
                    {**verify("y"), "entry_id": None}]}
    result = gate(tmp_path, capsys, [venue(slug) for slug in "abc"], scans, verifs)
    assert set(result.codes()) == {"gecersiz_eylem", "gecersiz_sonuc", "kimliksiz"}
    assert result.ids("gecersiz_eylem") == [eid("a"), eid("b")] and result.ids("gecersiz_sonuc") == [eid("c")]
    assert sorted(item["where"] for item in result.report["findings"] if item["code"] == "kimliksiz") == [
        "g.jsonl:4", "g_dogrulama.jsonl:4"]


# ------------------------------------------------------------------ eylemler: sil, kartta belirt

def test_deleted_venue_must_leave_the_list(tmp_path, capsys):
    """Pilot dersi: kapanmis golf sahasi 'sil' kararindan sonra listede kalirsa kapi gecmez."""
    scans = {"spor": [scan("golfbaan", "kapalı", kanit_alinti="will close its doors at the end of this year",
                           kanit_tarihi="2020")], "muzeler": [scan("museum")]}
    verifs = {"spor": [verify("golfbaan", "sil", "onay", tarama_durum="kapalı", gerekce=SECOND)]}
    listed = gate(tmp_path, capsys, [venue("golfbaan"), venue("museum")], scans, verifs)
    assert listed.code == 1 and dict(listed.codes()) == {"sil_listede": 1}
    assert listed.ids("sil_listede") == [eid("golfbaan")]
    removed = gate(tmp_path, capsys, [venue("museum")], scans, verifs)
    assert removed.code == 0 and removed.summary["listede_olmayan"] == {"tarama": 1, "dogrulama": 1}


def test_unlisted_venue_open_evidence_is_skipped_but_decisions_are_checked(tmp_path, capsys):
    """Listede olmayan mekan pakette degil: 'açık' kaniti aranmaz. 'açık' disi kararin dogrulamasi ve dogrulama
    satirinin kurallari (silinen mekanin iki kaynagi dahil) listeden bagimsizdir."""
    scans = {"g": [scan("a"), scan("eski", kanit_alinti="© 2026 Eski Yer", kanit_tarihi="tarihsiz"),
                   scan("kapali", "kapalı"), scan("silinen", "kapalı")]}
    verifs = {"g": [verify("silinen", "sil", "onay", tarama_durum="kapalı", gerekce="Kapandı.")]}
    result = gate(tmp_path, capsys, [venue("a")], scans, verifs)
    assert dict(result.codes()) == {"dogrulama_yok": 1, "ikinci_kaynak_yok": 1}
    assert result.ids("dogrulama_yok") == [eid("kapali")] and result.ids("ikinci_kaynak_yok") == [eid("silinen")]
    assert result.summary["listede_olmayan"] == {"tarama": 3, "dogrulama": 1}


def test_action_rules_do_not_depend_on_the_result_field(tmp_path, capsys):
    """Pilotta 'ret' + 'kartta belirt' satirlari vardi: kural eyleme gore isler."""
    scans = {"g": [scan("a", "belirsiz"), scan("b", "belirsiz")]}
    verifs = {"g": [verify("a", "sil", "ret"), verify("b", "kartta belirt", "ret")]}
    result = gate(tmp_path, capsys, [venue("a"), venue("b")], scans, verifs)
    assert result.ids("sil_listede") == [eid("a")] and result.ids("not_yok") == [eid("b")]


@pytest.mark.parametrize("durum, eylem, sonuc, celiski", [
    ("kapalı", "dokunma", "onay", True), ("kapalı", "kartta belirt", "onay", True),
    ("geçici kapalı", "dokunma", "onay", True), ("taşındı", "dokunma", "onay", True), ("insaat", "dokunma", "onay", True),
    ("kapalı", "sil", "onay", False), ("kapalı", "dokunma", "ret", False), ("kapalı", "kartta belirt", "ret", False),
    ("geçici kapalı", "kartta belirt", "onay", False), ("taşındı", "sil", "onay", False),
    ("insaat", "kartta belirt", "onay", False), ("belirsiz", "dokunma", "onay", False)])
def test_confirmed_closure_cannot_pass_with_the_card_untouched(tmp_path, capsys, durum, eylem, sonuc, celiski):
    """Onaylanan 'kapalı' yalniz 'sil'le; onaylanan 'geçici kapalı' / 'taşındı' / 'insaat' 'dokunma' ile gecmez.
    Durum dogrulama satirinin serbest metninden degil tarama satirindan okunur (pilotta 'belirsiz (KAPANMIŞ OLABİLİR)')."""
    row = verify("yer", eylem, sonuc, tarama_durum="belirsiz (KAPANMIŞ OLABİLİR)", gerekce=SECOND)
    listed = [venue("diger")] + ([] if eylem == "sil" else [venue("yer", note=NOTE)])
    result = gate(tmp_path, capsys, listed, {"g": [scan("yer", durum), scan("diger")]}, {"g": [row]})
    assert result.ids("eylem_celiski") == ([eid("yer")] if celiski else [])
    assert result.code == (1 if celiski else 0), result.codes()


def test_status_for_the_action_rule_comes_from_the_same_group_scan(tmp_path, capsys):
    """Iki grupta taranan mekan: dogrulama satiri kendi grubunun taramasiyla eslesir; grubunda taramasi yoksa
    mekanin butun tarama satirlarina bakilir."""
    scans = {"muzeler": [scan("yer")], "sanat": [scan("yer", "kapalı")]}
    verifs = {"muzeler": [verify("yer", "dokunma", "onay", tarama_durum="açık")],
              "sanat": [verify("yer", "dokunma", "onay", tarama_durum="kapalı")],
              "tarih": [verify("yer", "dokunma", "onay")]}
    result = gate(tmp_path, capsys, [venue("yer")], scans, verifs)
    assert sorted(item["where"] for item in result.report["findings"] if item["code"] == "eylem_celiski") == [
        "sanat_dogrulama.jsonl:1", "tarih_dogrulama.jsonl:1"]


@pytest.mark.parametrize("gerekce, ok", [
    ("Kapandı.", False), ("İkinci kaynak (gemeente.example): 'gesloten'", False),  # yalniz alan adi: tam adres yok
    ("Aynı sitenin arşivi: https://www.nieuws.example/archief 'gesloten'", False),
    ("Aynı sitenin alt alanı: https://archief.nieuws.example/x 'gesloten'", False),
    (SECOND, True), ("Belediye https://www.gemeente.example/x. Ayrıca https://nieuws.example/y", True)])
def test_delete_needs_a_second_independent_address_in_the_reason(tmp_path, capsys, gerekce, ok):
    """'sil' iki bagimsiz kaynak ister: ikincisinin tam adresi gerekce'de, kanit_url'den (nieuws.example) baska
    alan adinda. Mekan listeden cikmis olsa da denetlenir."""
    row = verify("golf", "sil", "onay", tarama_durum="kapalı", gerekce=gerekce)
    result = gate(tmp_path, capsys, [venue("museum")], {"g": [scan("golf", "kapalı"), scan("museum")]}, {"g": [row]})
    assert result.ids("ikinci_kaynak_yok") == ([] if ok else [eid("golf")])
    assert result.code == (0 if ok else 1)


def test_host_of_normalizes_and_survives_bad_addresses():
    assert acik_mi.host_of("https://WWW.Gemeente.example./nieuws,") == "gemeente.example"
    assert acik_mi.host_of("https://[kirik-ipv6/x") == "" and acik_mi.host_of("") == ""
    assert acik_mi.same_site("archief.nieuws.example", "nieuws.example")
    assert not acik_mi.same_site("oldnieuws.example", "nieuws.example")


GOOD_NOTES = ["5 Kasım 2026 itibarıyla oyun bahçesi kış arasında kapalı.", "Kasım 2026 itibarıyla kapalı.",
              "2026-11-05 itibarıyla yeni adresinde.", "05.11.2026 itibariyle kapalı.",
              "5 Kasım 2026 tarihi itibarıyla kapalı.", "Mekân 5 kasım 2026 itibarı ile tadilatta."]
BAD_NOTES = ["", "Kış aylarında kapalı.", "Konser 22 Kasım 2026'da.", "1 Ağustos 2022 itibarıyla yeni saatler.",
             "2026 itibarıyla kapalı.", "5 Kasım 2026'dan itibaren kapalı.",
             "1 Ocak 2025 itibarıyla giriş ücretli."]  # ozetteki eski cumle: not kontrol yili (2026) tarihli olmali


@pytest.mark.parametrize("note, ok", [(note, True) for note in GOOD_NOTES] + [(note, False) for note in BAD_NOTES])
def test_flagged_card_needs_a_recent_dated_as_of_note(tmp_path, capsys, note, ok):
    verifs = {"g": [verify("yer", "kartta belirt", "onay", tarama_durum="geçici kapalı")]}
    result = gate(tmp_path, capsys, [venue("yer", note=note)], {"g": [scan("yer", "geçici kapalı")]}, verifs)
    assert (result.code, result.ids("not_yok")) == ((0, []) if ok else (1, [eid("yer")]))


@pytest.mark.parametrize("field", ["subtitle", "summary", "note", "visit_status"])
def test_dated_note_counts_in_any_reader_text_field(tmp_path, capsys, field):
    card = {**venue("yer"), field: "5 Kasım 2026 itibarıyla tadilat nedeniyle kapalı."}
    verifs = {"g": [verify("yer", "kartta belirt", "onay", tarama_durum="insaat")]}
    assert gate(tmp_path, capsys, [card], {"g": [scan("yer", "insaat")]}, verifs).code == 0


def test_flagged_card_needs_its_note_and_with_sources_the_evidence_source(tmp_path, capsys):
    """Kaynak izi notun yerini tutmaz (editor kaynagi ekleyip notu unutabilir; kanit ana sayfaysa kart onu zaten
    tasir): tarihli not her zaman sart; --kaynaklar verilince kanit kaynaginin kimligi ayrica sart."""
    noted = venue("kano", note=NOTE, source_ids=f"{CITY}:kaynak:001; {CITY}:kaynak:009")
    bare, untraced = {**noted, "note": ""}, {**noted, "source_ids": f"{CITY}:kaynak:001"}
    scans = {"spor": [scan("kano", "belirsiz")]}
    verifs = {"spor": [verify("kano", "kartta belirt", kanit_url="https://www.kano.example/boeken/")]}
    sources = [{"source_id": f"{CITY}:kaynak:009", "url": "http://kano.example/old", "final_url": "https://kano.example/boeken"}]
    cases = [(noted, sources, {}), (noted, None, {}), (bare, sources, {"not_yok": 1}), (bare, None, {"not_yok": 1}),
             (untraced, sources, {"kaynak_izi_yok": 1}), (untraced, None, {}), (untraced, [], {"kaynak_izi_yok": 1})]
    for card, given, expected in cases:
        result = gate(tmp_path, capsys, [card], scans, verifs, sources=given)
        assert dict(result.codes()) == expected, (card["note"], card["source_ids"], given)


# ------------------------------------------------------------------ kanit: alinti, adres, tarih, footer

def test_missing_quote_or_url_is_a_finding_on_the_deciding_row(tmp_path, capsys):
    scans = {"g": [scan("a", kanit_alinti="  "), scan("b", kanit_url=""), scan("c", "belirsiz", kanit_alinti=""),
                   scan("d", "belirsiz", kanit_alinti="")]}
    verifs = {"g": [verify("c"), verify("d", kanit_alinti="")]}  # dogrulama satiri olan mekanda karar onundur
    result = gate(tmp_path, capsys, [venue(slug) for slug in "abcd"], scans, verifs)
    found = {(item["code"], item["entry_id"], item["where"]) for item in result.report["findings"]}
    assert found == {("bos_alinti", eid("a"), "g.jsonl:1"), ("bos_url", eid("b"), "g.jsonl:2"),
                     ("bos_alinti", eid("d"), "g_dogrulama.jsonl:2")}


@pytest.mark.parametrize("tarih, ok", [
    ("2026-09-12", True), ("2025-03", True), ("2026 (2027 kapanış takvimi)", True), ("2026-10-20..2027-09-12", True),
    ("2026-09-29 (sayfanın son güncellemesi)", True), ("2024-12-31", False), ("tarihsiz (site © 2019)", False), ("", False),
    # tarih parantezden oncedir (parantez kaynagini anlatir); footer / telif / erisim tarihi faaliyet tarihi degildir
    ("tarihsiz (footer © 2026)", False), ("2026 (site © 2026)", False), ("2026-10-22 (erişim günü)", False),
    ("2026 (footer)", False), ("© 2026", False), ("2026 (telif satırı)", False), ("2024 (2026 sergisi)", False),
    ("tarihsiz, son haber 2026", False)])
def test_open_needs_evidence_dated_this_or_last_year(tmp_path, capsys, tarih, ok):
    result = gate(tmp_path, capsys, [venue("yer")], {"g": [scan("yer", kanit_tarihi=tarih)]})
    assert result.ids("eski_kanit") == ([] if ok else [eid("yer")])


def test_min_year_is_adjustable_and_defaults_to_last_year(tmp_path, capsys):
    stricter = gate(tmp_path, capsys, [venue("yer")], {"g": [scan("yer", kanit_tarihi="2025-03")]}, None,
                    "--min-year", "2026")
    assert stricter.ids("eski_kanit") == [eid("yer")] and stricter.summary["min_year"] == 2026
    assert acik_mi.default_min_year(dt.date(2026, 10, 23)) == 2025
    _, summary = run_main(capsys, [tmp_path / "_is" / "acik_mi", "--mekanlar", tmp_path / "_is" / "data" / VENUES])
    assert summary["min_year"] == dt.date.today().year - 1


FOOTERS = ["Copyright PSV NV - © 2026", "© 2026 Neoseum, Next-Gen Reality B.V.", "© Paviljoen Genneper Parken 2026",
           "© 2026 Kazarne. All rights reserved.", "© 2026, De Oude Telefooncentrale.", "(c) 2025 Stadsbrouwerij",
           "Alle Rechte vorbehalten © 2026 Museum am Markt",
           "© 2026 Stichting Historische Producten. Alle rechten voorbehouden.",
           # sicil / vergi no, adres, posta kodu, telefon, e-posta: footer'da yaygin, rakamlari tarih degil
           "© 2026 Stichting X | KvK 17001910 | Alle rechten voorbehouden",
           "© 2026 Museum X, Stratumsedijk 2, 5611 ND Eindhoven",
           "© 2026 Café X | Oude Stadsgracht 15 | 040-2443131 | info@cafex.example",
           "© 2026 Museum am Markt GmbH · Marktplatz 3 · 44135 Dortmund · Tel. +49 231 123456",
           "© 2026 X B.V. | BTW NL001234567B01 | Ventoselaan 1 5611 BS Eindhoven | www.x.example"]
NOT_FOOTERS = ["30 / Fri / Bluesalive Venga ... © Stage Music café - 2026", "Vanaf 18 juli 2026",
               "Op 11 oktober gesloten i.v.m. de marathon", "Laatste update 21-9-2026", "",
               "© 2026 Effenaar | Concert zaterdag 12 september", "Bier van het vat, 12 oktober © 2026 Brouwerij",
               "Open dinsdag t/m zondag 10-17 uur © 2026 Museum X", "Opening 05.11.2026 © 2026 Galerie X"]


@pytest.mark.parametrize("quote, footer", [(q, True) for q in FOOTERS] + [(q, False) for q in NOT_FOOTERS])
def test_copyright_line_alone_is_not_open_evidence(quote, footer):
    assert acik_mi.is_footer_only(quote) is footer


def test_a_verification_row_takes_over_a_weak_open_row(tmp_path, capsys):
    scans = {"g": [scan("a", kanit_alinti="© 2026 Museum A"), scan("b", kanit_tarihi="tarihsiz")]}
    alone = gate(tmp_path, capsys, [venue("a"), venue("b")], scans)
    assert (alone.ids("footer_kanit"), alone.ids("eski_kanit")) == ([eid("a")], [eid("b")])
    assert gate(tmp_path, capsys, [venue("a"), venue("b")], scans, {"g": [verify("a"), verify("b")]}).code == 0


# ------------------------------------------------------------------ girdi, cikti, kullanim hatasi

def test_venue_list_from_parts_folder_or_pattern(tmp_path, capsys):
    parts = tmp_path / "parcalar"
    write_jsonl(parts / "Mekânlar.m1.jsonl", [venue("a")])
    write_jsonl(parts / unicodedata.normalize("NFD", "Mekânlar.m2.jsonl"), [venue("b")])  # baska sistemden gelen ad
    write_jsonl(parts / "Bağlantılar.m1.jsonl", [{"entry_id": eid("z")}])  # baska sekme okunmaz
    folder = write_jsonl(tmp_path / "acik_mi" / "g.jsonl", [scan("a"), scan("b")]).parent
    merged = write_jsonl(tmp_path / "data" / VENUES, [venue("a"), venue("b")])
    for specs in ([parts], [parts / "Mekânlar.m*.jsonl"], [merged, parts]):  # ayni kayit iki yerde: bir mekan
        code, summary = run_main(capsys, [folder, "--mekanlar", *specs, "--min-year", MIN_YEAR])
        assert (code, summary["mekan"]) == (0, 2), (specs, summary)


def test_unusable_input_exits_2_with_a_reason(tmp_path, capsys):
    folder = write_jsonl(tmp_path / "acik_mi" / "g.jsonl", [scan("a")]).parent
    venues = write_jsonl(tmp_path / "data" / VENUES, [venue("a")])
    cases = {
        "açık-mı klasörü yok": [tmp_path / "yok", "--mekanlar", venues],
        "--mekanlar bulunamadı": [folder, "--mekanlar", tmp_path / "yok.jsonl"],
        "mekân listesi boş": [folder, "--mekanlar", write_jsonl(tmp_path / "bos" / VENUES, [])],
        "Mekânlar.jsonl:1: entry_id yok": [folder, "--mekanlar", write_jsonl(tmp_path / "x" / VENUES, [{"title": "A"}])],
        "Mekânlar*.jsonl yok": [folder, "--mekanlar", folder],
        "desenine uyan dosya yok": [folder, "--mekanlar", tmp_path / "yok" / "Mekânlar*.jsonl"],
        "--kaynaklar bulunamadı": [folder, "--mekanlar", venues, "--kaynaklar", tmp_path / "yok_kaynak.jsonl"],
        "girdinin üstüne yazamaz": [folder, "--mekanlar", venues, "--out", venues],
        "klasörüne yazamaz": [folder, "--mekanlar", venues, "--out", folder / "rapor.json"],
        "--min-year": [folder, "--mekanlar", venues, "--min-year", "26"],
    }
    for reason, argv in cases.items():
        code, summary = run_main(capsys, argv)
        assert code == 2 and summary["tool"] == "acik_mi" and reason in summary["error"], (reason, summary)
    assert not (folder / "rapor.json").exists()
    for content, reason in [('{"entry_id": "ornek:a"}\n\n{oops\n'.encode(), "h.jsonl:3: geçersiz JSON"),
                            (b"[1, 2]\n", "h.jsonl:1: JSON nesnesi bekleniyor"),
                            ('{"title": "Müze"}\n'.encode("cp1252"), "UTF-8 değil")]:
        (folder / "h.jsonl").write_bytes(content)
        code, summary = run_main(capsys, [folder, "--mekanlar", venues])
        assert code == 2 and reason in summary["error"], summary
    assert run_main(capsys, [folder])[0] == 2  # --mekanlar zorunlu (argparse)


def test_gate_only_reads_its_inputs(tmp_path, capsys):
    folder = write_jsonl(tmp_path / "_is" / "acik_mi" / "g.jsonl", [scan("a"), scan("b", "kapalı")]).parent
    write_jsonl(folder / "g_dogrulama.jsonl", [verify("b", "sil", "onay")])
    venues = write_jsonl(tmp_path / "_is" / "data" / VENUES, [venue("a"), venue("b")])
    before = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in tmp_path.rglob("*") if path.is_file()}
    code, _ = run_main(capsys, [folder, "--mekanlar", venues, "--min-year", MIN_YEAR])
    after = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in tmp_path.rglob("*") if path.is_file()}
    assert code == 1 and after == before  # --out yok: hicbir dosya yazilmaz


def test_stdout_lists_the_first_findings_and_the_report_keeps_all(tmp_path, capsys):
    venues = [venue(f"yer-{n}") for n in range(acik_mi.MAX_ITEMS + 5)]
    result = gate(tmp_path, capsys, venues, {"g": []})
    assert result.code == 1 and result.summary["findings"] == len(venues) == len(result.report["findings"])
    assert len(result.summary["items"]) == acik_mi.MAX_ITEMS
    assert result.summary["by_code"] == {"tarama_yok": len(venues)}


def test_cli_prints_one_utf8_json_line(tmp_path):
    folder = write_jsonl(tmp_path / "acik_mi" / "g.jsonl", [scan("a", "geçici kapalı")]).parent
    venues = write_jsonl(tmp_path / "data" / VENUES, [venue("a")])
    result = subprocess.run([sys.executable, "-B", str(SCRIPT), str(folder), "--mekanlar", str(venues)],
                            capture_output=True, timeout=120)
    assert result.returncode == 1, result.stderr
    lines = result.stdout.decode("utf-8").splitlines()
    assert len(lines) == 1 and json.loads(lines[0])["durum"] == {"geçici kapalı": 1}


# ------------------------------------------------------------------ agents/acik-mi.md ile uyum

FAKE = {"<PY>": r"C:\sahte\.venv\Scripts\python.exe", "<TK>": str(TOOLKIT / "scripts"),
        "<WORK>": r"C:\sahte\uretim\ornek", "<TMP>": r"C:\sahte\gecici\acik_w", "<grup>": "muzeler"}
DOC_BANNED = ("eindhoven", "tilburg", "dortmund", "welschap", "c:\\", "temp_private", "appdata", "scratchpad", "baris",
              "2026-10-")
CLOSURE_WORDS = {"nl": ("gesloten", "failliet", "sluit", "verhuist", "verbouwing"),
                 "de": ("geschlossen", "insolvent", "schließt", "umgezogen", "Umbau"),
                 "tr": ("kapandı", "kapanıyor", "iflas", "taşındı", "tadilat")}
COMMAND = re.compile(r"^\s*& <PY> <TK>\\acik_mi\.py(?P<args>[^\n]*)$", re.M)


def doc_text() -> str:
    return DOC.read_text(encoding="utf-8")


def fill(template: str, values: dict[str, str]) -> str:
    for name, value in values.items():
        template = template.replace(name, value)
    assert not re.search(r"<[A-Za-z_]+>", template), template
    return template


def enum_values(prefix: str) -> list[str]:
    return re.findall(r"`([^`]+)`", next(line for line in doc_text().splitlines() if line.startswith(prefix)))[1:]


def test_doc_is_city_independent_compact_and_names_closure_words():
    text = doc_text()
    assert [token for token in DOC_BANNED if token in text.casefold()] == []
    assert len(text.splitlines()) <= 200, len(text.splitlines())
    for language, words in CLOSURE_WORDS.items():
        assert [word for word in words if word not in text] == [], language


def test_doc_lists_every_finding_code_and_the_single_source_path():
    gate_section = doc_text().split("## 6.", 1)[1]
    assert [code for code in acik_mi.CODES if f"`{code}`" not in gate_section] == []
    assert "open_items" in doc_text() and "ikinci kaynak bulunamadı" in doc_text()


def test_doc_enums_and_row_examples_match_the_gate():
    assert enum_values("- `durum`:") == list(acik_mi.DURUMLAR)
    assert enum_values("- `sonuc`:") == list(acik_mi.SONUCLAR)
    assert enum_values("- `eylem`:") == list(acik_mi.EYLEMLER)
    blocks = re.findall(r"```json\n(.+?)\n```", doc_text(), re.S)
    keys = [list(json.loads(re.sub(r"<[^<>\"]+>", "x", block))) for block in blocks]
    assert list(acik_mi.TARAMA_ALANLARI) in keys and list(acik_mi.DOGRULAMA_ALANLARI) in keys


def test_doc_gate_command_parses_and_writes_only_to_tmp():
    commands = [match["args"] for match in COMMAND.finditer(doc_text())]
    assert len(commands) == 1, commands
    namespace, error = sc.parse_quietly(sc.load_parser("acik_mi"), fill(commands[0], FAKE).split())
    assert error == "" and namespace is not None, error
    assert PureWindowsPath(namespace.out).is_relative_to(PureWindowsPath(FAKE["<TMP>"]))
    assert PureWindowsPath(namespace.acik_mi) == PureWindowsPath(FAKE["<WORK>"], "_is", "acik_mi")


def test_rows_written_as_documented_pass_the_documented_command(tmp_path, capsys):
    text, values = doc_text(), {"<WORK>": str(tmp_path), "<TMP>": str(tmp_path / "acik_w"), "<grup>": "muzeler"}
    for suffix, row, keys in [("", scan("museum", "belirsiz"), acik_mi.TARAMA_ALANLARI),
                              ("_dogrulama", verify("museum"), acik_mi.DOGRULAMA_ALANLARI)]:
        documented = re.search(rf"`(<WORK>\\_is\\acik_mi\\<grup>{suffix}\.jsonl)`", text)[1]
        write_jsonl(Path(fill(documented, values)), [{key: row[key] for key in keys}])
    write_jsonl(tmp_path / "_is" / "data" / "parcalar" / "Mekânlar.m1.jsonl", [venue("museum")])
    write_jsonl(tmp_path / "_is" / "kaynak_dizini.jsonl", [])
    code, summary = run_main(capsys, [*fill(COMMAND.search(text)["args"], values).split(), "--min-year", MIN_YEAR])
    assert code == 0 and (summary["mekan"], summary["dogrulama"]["satir"]) == (1, 1), summary


def test_doc_note_example_is_recognised_by_the_gate():
    examples = [quoted for quoted in re.findall(r'"([^"]*itibarıyla[^"]*)"', doc_text()) if re.search(r"\d{4}", quoted)]
    assert examples
    for example in examples:  # 'itibarıyla' tarihi ornegin ilk (en eski) yilidir; sonraki tarih yeniden acilis olabilir
        assert acik_mi.dated_note(example, min(int(year) for year in re.findall(r"\d{4}", example))), example


# ------------------------------------------------------------------ pilot ciktilari (salt okunur, kopya)

PILOT_FOOTER = ["eindhoven:de-oude-telefooncentrale", "eindhoven:kazerne-expo", "eindhoven:neoseum",
                "eindhoven:paviljoen-genneper-parken", "eindhoven:psv-museum"]
PILOT_NOTES = ["eindhoven:happy-canoe", "eindhoven:next-level-escape-rooms", "eindhoven:paviljoen-ongehoorde-muziek",
               "eindhoven:sint-joseph-speeltuin", "eindhoven:speeltuin-philipsdorp"]


def copy_pilot(tmp_path: Path) -> Path:
    work = tmp_path / "_is"
    shutil.copytree(PILOT / "acik_mi", work / "acik_mi")
    shutil.copytree(PILOT / "data" / "parcalar", work / "data" / "parcalar", ignore=lambda folder, names: [
        name for name in names if not unicodedata.normalize("NFC", name).startswith("Mekânlar")])
    shutil.copy2(PILOT / "data" / VENUES, work / "data" / VENUES)
    shutil.copy2(PILOT / "kaynak_dizini.jsonl", work / "kaynak_dizini.jsonl")
    return work


@pytest.mark.real
@needs_pilot
def test_gate_schema_is_the_pilot_schema():
    for path in sorted((PILOT / "acik_mi").glob("*.jsonl")):
        expected = acik_mi.DOGRULAMA_ALANLARI if path.stem.endswith("_dogrulama") else acik_mi.TARAMA_ALANLARI
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
        assert rows and all(tuple(row) == expected for row in rows), path.name


@pytest.mark.real
@needs_pilot
def test_pilot_outputs_smoke(tmp_path, capsys):
    """Pilot (120 tarama, 24 dogrulama, 5 'kartta belirt' uygulanmis) kapidan once yazildi: alintisiz bir 'açık' ve
    yalniz telif satiriyla 'açık' denen 5 mekan bulgu; kalan her kural temiz."""
    work, report = copy_pilot(tmp_path), tmp_path / "rapor.json"
    base = [work / "acik_mi", "--min-year", MIN_YEAR]
    code, summary = run_main(capsys, [*base, "--mekanlar", work / "data" / VENUES,
                                      "--kaynaklar", work / "kaynak_dizini.jsonl", "--out", report])
    assert code == 1 and summary["mekan"] == 119 and summary["listede_olmayan"] == {"tarama": 0, "dogrulama": 0}
    assert (summary["tarama"], summary["dogrulama"]) == ({"dosya": 8, "satir": 120, "mekan": 119}, {"dosya": 7, "satir": 24})
    assert summary["durum"] == {"açık": 96, "belirsiz": 21, "geçici kapalı": 1, "taşındı": 1, "insaat": 1}
    assert summary["eylem"] == {"dokunma": 19, "kartta belirt": 5} and summary["sonuc"] == {"ret": 19, "onay": 5}
    assert summary["by_code"] == {"bos_alinti": 1, "footer_kanit": 5}
    findings = json.loads(report.read_text(encoding="utf-8"))["findings"]
    assert sorted(item["entry_id"] for item in findings if item["code"] == "footer_kanit") == PILOT_FOOTER
    assert [item["entry_id"] for item in findings if item["code"] == "bos_alinti"] == ["eindhoven:landgoed-de-grote-beek"]
    code, parts = run_main(capsys, [*base, "--mekanlar", work / "data" / "parcalar"])  # parcalar, kaynaksiz: ayni
    assert (code, parts["mekan"], parts["by_code"]) == (1, 119, summary["by_code"])


@pytest.mark.real
@needs_pilot
def test_pilot_card_without_its_dated_note_is_caught(tmp_path, capsys):
    work = copy_pilot(tmp_path)
    venues = work / "data" / VENUES
    rows = [json.loads(line) for line in venues.read_text(encoding="utf-8").splitlines() if line.strip()]
    for row in (row for row in rows if row["entry_id"] in PILOT_NOTES):
        row["note"] = re.sub(r"\d{1,2} \w+ \d{4} itibarıyla[^.]*\.?", "", row["note"])
    write_jsonl(venues, rows)
    base = [work / "acik_mi", "--mekanlar", venues, "--min-year", MIN_YEAR]
    assert run_main(capsys, base)[1]["by_code"].get("not_yok") == 5
    # kanit kaynagi kartin source_ids'inde (kaynak izi tamam) ama not yok: kaynak izi notun yerini tutmaz
    by_code = run_main(capsys, [*base, "--kaynaklar", work / "kaynak_dizini.jsonl"])[1]["by_code"]
    assert by_code.get("not_yok") == 5 and "kaynak_izi_yok" not in by_code, by_code


@pytest.mark.real
@needs_pilot
def test_pilot_confirmed_seasonal_closure_left_untouched_is_caught(tmp_path, capsys):
    work = copy_pilot(tmp_path)
    path = work / "acik_mi" / "cocuk_dogrulama.jsonl"
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    write_jsonl(path, [{**row, "eylem": "dokunma"} if row["entry_id"] == "eindhoven:speeltuin-philipsdorp" else row
                       for row in rows])  # 'geçici kapalı' + 'onay'
    code, summary = run_main(capsys, [work / "acik_mi", "--mekanlar", work / "data" / VENUES, "--min-year", MIN_YEAR])
    assert code == 1 and summary["by_code"].get("eylem_celiski") == 1, summary["by_code"]
