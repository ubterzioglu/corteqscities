"""city-pack SKILL.md faz kurallari (skill-son-hal-3): B13 intake sablonu (Atinc dosyasi ya da make_template; bos
sablonda 8/16 Sehir hatasi), B15 acik_mi kapisi, A14 teslim sirasi, B16 hitap standardi ve bunlarin incelemesinin
bulgulari (tek kaynakli kapanistan cikis, city-audit karsiligi, 901, uygulama editorunun gorevleri, standarttaki
ornek, priority). skill-son-hal-5 (Baris kararlari 23.10.2026; kullanici yalniz 'Tilburg' yazar): hitap 'sen', olcum
kosusu, run_log notu, yalniz sehir adi tetikleyicisi, var olan uretim. Sonda city-audit SKILL.md'nin B15 karsiligi
(skill-son-hal-4 W2 ve incelemesi): L1 acik-mi orneklemesi
(uretim beyani kapisi, acik_mi_denetim ile orneklem ve parti dosyalari, bagimsiz supheci ajan, kayit kusurunda yeni
ajan, ikinci kapi ve kanit kopyasi, siniflar ve P derecesi, sayilar ve K39 durumu). test_skill_commands.py'den ayrildi
(800 satir siniri); SKILL.md okuma ve bolum yardimcilari ile ayristirilmis komutlar oradan, acik-mi satir uretecleri
test_acik_mi.py'den gelir; aracin kendi kurallari test_acik_mi_denetim.py'de.
Ag yok, toolkit script'i alt surec olarak calismaz: faz 7 teslim sirasi gercek inventory ve render_summary main()'leriyle
mini pakette, tek kaynakli kapanis ve denetimin acik-mi adimi SKILL.md'deki komutlarla gercek acik_mi, acik_mi_denetim
ve (sahte tasimayla) fetch_snapshot main()'leriyle tmp_path'te denenir.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from collections import Counter
from dataclasses import dataclass
from pathlib import Path, PureWindowsPath
from types import MappingProxyType

import pytest
import yaml

import acik_mi
import acik_mi_denetim
import address_forms
import common
import fetch_snapshot
import inventory
import make_template
import render_summary
import skill_commands_helpers as sc
import test_acik_mi as am
from test_skill_commands import (ADDRESS_FLAG, HITAP_FILE, VARIABLES_BY_SKILL, _containing, _parsed, _section,
                                 _skill_text, _starting)
from test_web_fetch import FakeTransport, ok


# --- city-pack SKILL.md: skill-son-hal-3 (B13 sablon, B15 acik-mi kapisi, A14 teslim sirasi, B16 hitap) ---

ATINC_BLANK = ("currency", "title", "intro", "reviewed_on", "timezone", "language")  # 8 hata (currency, timezone x2)
DERIVED_BLANK = ("latitude", "longitude", "coordinate_source_url", "coordinate_checked_on", "source_url",
                 "source_checked_on", "priority", "editorial_status")  # Atinc katalogdan doldurur: turetilmiste +8
CHAIN = re.compile(r"^& \$PY \$TK\\(?P<tool>validate_all|inventory|render_summary)\.py (?P<args>.+)$|^Copy-Item (?P<copy>.+)$")
INVENTORY_COPY = "Teslimler/dosya-envanteri.json"
EMIT = {"summary": {"structure": {"errors": 0, "warnings": 0}, "media": {"errors": 0}, "technically_complete": True}}


def test_city_pack_intake_uses_atinc_file_or_derives_the_template():
    """B13: Atinc'in sehir dosyasi varsa o, yoksa make_template (Berlin ornegi; ad CITY-NNN_<city_id>_v001.xlsx: intake
    numarayi ve teslim adini addan okur; _is\\sablon.xlsx asilla ayni SHA). Numara bilinmiyorsa 900+ ve Teslimat notu
    YEREL DENEME (aracin sabitleri); priority = 3. Bos sablonda Sehir hatalari Atinc'te 8, turetilmiste 16 (arac 8
    katalog alanini yazmaz); KUR temiz, faz 3 kapisi ve Sehir yazari ikisini de tanir; koordinat uydurulmaz."""
    text = _skill_text("city-pack")
    intake = _section(text, "### 1. intake")
    (command, ns), = [(c, n) for c, n in _parsed("city-pack") if c.script == "make_template"]
    out = re.search(r"--out (\S+)", command.args)[1]
    assert command.text in intake and re.fullmatch(r"\$WORK\\_is\\\w+\\CITY-<[^<>]+>_<city_id>_v001\.xlsx", out), out
    assert PureWindowsPath(ns.base).name == "CITY-000_berlin_ornek_v001.xlsx"
    needed = ("ekler*", r"references\sablon_turetme.md", r"`_is\sablon.xlsx`", "SHA-256", "900+", "YEREL DENEME",
              "`priority` = 3", "`open_items`")
    assert [phrase for phrase in needed if phrase not in intake] == []
    assert make_template.LOCAL_TRIAL_FROM == 900 and "YEREL DENEME" in make_template.LOCAL_TRIAL_NOTE
    b10 = _containing(intake, "B10:")
    assert {*ATINC_BLANK, *DERIVED_BLANK} <= set(re.findall(r"`([a-z_]+)`", b10)) and "**8**" in b10 and "**16**" in b10
    tables = {s: make_template.TableSpec(k, s, None, ()) for k, s in (("metadata", "Teslimat"), ("city", "Şehir"))}
    opts = make_template.Options(Path("b"), Path("o"), "x", "X", "Y", "YY", "EU", "city", 901, None, "e")
    written = make_template.identity_values(opts, make_template.Contract("x", "1", tables, None), "b")["Şehir"]
    assert not set(written) & {*ATINC_BLANK, *DERIVED_BLANK}, written  # arac yazmaz: bos sablonda hata
    kur = _containing(_section(text, "## KUR bloğu: birleştir → kur → kapılar"), "**KUR temiz**")
    gate = _starting(_section(text, "### 3. answers"), "- Kapı:")
    writer = _containing(_section(text, "### 4. places"), "1 sayfa yazarı")
    assert all("şablon Şehir hataları" in line for line in (kur, gate, writer)) and "8 Şehir hatası" not in text
    assert "16" in kur and [n for n in DERIVED_BLANK if f"`{n}`" not in writer] == [] and "uydurulmaz" in writer


def test_city_pack_places_closes_only_after_the_open_check_gate():
    """B15 (P0): kendi sitesinin varligi acik kaniti degil; places'ta acik-mi.md ajanlari ve acik_mi kapisi (butun liste,
    varsayilan yil, rapor acik-mi klasoru disinda); kapi places kapisinda. Inceleme ORTA-1: yalniz 5 kod 'P0' deniyordu;
    kural 4'e gore digerleri open_items'a yazilip faz kapanabilirdi ('cikis 0 sart' ile celiski). Kural: bu kapida
    open_items yolu yok, aracin her bulgu kodu duzeltecek rolle anilir (tek istisna tek kaynakli kapanis)."""
    places = _section(_skill_text("city-pack"), "### 4. places")
    (command, ns), = [(c, n) for c, n in _parsed("city-pack") if c.script == "acik_mi"]
    work = PureWindowsPath(VARIABLES_BY_SKILL["city-pack"]["WORK"], "_is")
    assert command.text in places and PureWindowsPath(ns.acik_mi) == work / "acik_mi" and ns.min_year is None
    assert [PureWindowsPath(p) for p in (*ns.mekanlar, *ns.kaynaklar)] == [work / "data" / "parcalar",
                                                                          work / "kaynak_dizini.jsonl"]
    assert not PureWindowsPath(ns.out).is_relative_to(work / "acik_mi")
    assert (sc.SKILLS["city-pack"].parent / "agents" / "acik-mi.md").is_file() and r"`AGENTS\acik-mi.md`" in places
    assert "kendi sitesinin varlığı kanıt sayılmaz" in _containing(places, "Şart:")
    rule = _starting(places, "- Çıkış 0 olmadan places kapanmaz")
    assert "kural 4" in rule and "her bulgu düzeltilir" in rule and "P0'dır" not in places, rule
    assert [code for code in acik_mi.CODES if f"`{code}`" not in rule] == [], rule
    assert "açık-mı kapısı çıkış 0" in _starting(places, "- Kapı:")


def _deliver_chain() -> list[tuple[str, str]]:
    """Faz 7'nin ilk kod blogundaki emit, envanter, ozet ve kopya satirlari sirasiyla: (arac ya da 'copy', ham arguman)."""
    block = _section(_skill_text("city-pack"), "### 7. deliver").split("```")[1]
    return [(m["tool"] or "copy", m["args"] or m["copy"]) for m in map(CHAIN.match, block.splitlines()) if m]


def test_city_pack_delivery_writes_only_the_inventory_after_the_last_count(tmp_path, package, capsys):
    """A14 (L0b ISS-005, pilot L0): faz 7 sirasi gercek inventory ve render_summary ile mini pakette iki kez (ilk teslim,
    zincir tekrari). Son envanterden sonra pakete yalniz envanter kopyasi yazilir: kopya disindaki her dosyanin SHA'si
    son envanterle tutar, ozetin dosya sayisi paketinki, ILERLEME_KAYDI'nda gun basina tek girdi. Pilot sirasi (envanter >
    ozet BIR kez > envanter > kopya) ilk teslimde ozete eksik sayi yazar (5/9); emit ilk sayimdan once."""
    chain = _deliver_chain()
    tools = [tool for tool, _ in chain]
    assert tools[0] == "validate_all" and tools[-2:] == ["inventory", "copy"], tools
    work, pkg = tmp_path / "work", package["root"]
    (work / "_is").mkdir(parents=True)
    for path, body in ((work / "manifest.json", "{}"), (work / "_is" / "validation_emit.json", json.dumps(EMIT)),
                       (work / "_is" / "notlar.md", "")):
        path.write_text(body, encoding="utf-8")
    values = MappingProxyType({"WORK": str(work), "PKG": str(pkg), "EXCEL": str(package["xlsx"])})
    mains = {"inventory": inventory.main, "render_summary": render_summary.main}
    for _ in ("ilk teslim", "zincir tekrari"):
        for tool, args in [step for step in chain if step[0] != "validate_all"]:  # emit gercek araclari ister
            argv = sc.to_argv(args, values)
            if tool == "copy":
                shutil.copyfile(argv[0], argv[1])
            else:
                assert mains[tool](argv) != 2, (tool, argv)
        capsys.readouterr()
        listed = {f["path"]: f["sha256"] for f in json.loads((pkg / INVENTORY_COPY).read_text(encoding="utf-8"))["files"]}
        actual = {p.relative_to(pkg).as_posix(): common.sha256_file(p) for p in pkg.rglob("*") if p.is_file()}
        assert [path for path, sha in actual.items() if path != INVENTORY_COPY and listed.get(path) != sha] == []
        counted = re.search(r"Paket: (\d+) dosya", (pkg / "Teslimler" / "TESLIM_OZETI.txt").read_text(encoding="utf-8"))
        assert int(counted[1]) == len(actual), "ozetteki dosya sayisi son sayim degil"
    days = render_summary.ENTRY_HEAD.findall((pkg / "Teslimler" / "ILERLEME_KAYDI.txt").read_text(encoding="utf-8"))
    assert len(days) == len(set(days)), days


ADDRESS_STANDARD = "sen"  # B16, Baris karari 23.10.2026 (duzeltilmis): Berlin ornegi gibi (Yanitlar 212/212 "sen")
COMMON_RULES = sc.SKILLS["city-pack"].parent / "agents" / "ortak-kurallar.md"
PROJECT_RULES = sc.REPO_ROOT / "CLAUDE.md"  # kullanici yalniz sehir adi yazar; city-pack baslar
EXAMPLES = re.compile(r'"([^"]+)"')


def _intake_standard(text: str) -> str:
    """Intake'te `_is\\yazar\\hitap.txt`'ye yazilan hitap standardi (kapilarin --address-standard'i)."""
    decided = HITAP_FILE.search(_section(text, "### 1. intake"))
    assert decided, "intake'te hitap.txt satiri yok"
    return decided["standard"]


def _examples_after(line: str, lead: str) -> list[str]:
    """`lead (` ile acilan parantezdeki tirnakli ornekler (yoksa bos liste)."""
    found = re.search(re.escape(lead) + r" \(([^)]*)\)", line)
    return EXAMPLES.findall(found[1]) if found else []


def test_city_pack_address_standard_is_sen():
    """B16 (Baris karari 23.10.2026, duzeltilmis): okura 'sen' diye hitap edilir, Berlin ornegi gibi (Yanitlar 212/212
    'sen'); ilk 'kisisiz' karari yanlis olcume dayaniyordu, gecersiz. Intake'te sorulmaz; hitap.txt'ye 'sen' yazilir,
    gorev mesajiyla gider; Sozluk ve Konular kisisiz kalabilir. Ortak kurallar §2 ayni karari tasir: ornek emirler
    aracta 'sen', kisisiz bilgi cumlesi ornegi kisisiz. Eski kararin izi kalmaz (SKILL.md'de 'hitapsız', ortak
    kurallarda 'doğrudan hitap etme'); KAPSAM.md'deki K32 da ayni standardi anar."""
    text = _skill_text("city-pack")
    intake = _section(text, "### 1. intake")
    rule = _containing(intake, "Hitap standardı (B16")
    needed = ('"sen"', "Berlin", "Sorulmaz", "görev mesajı", "Sözlük", "Konular", "kişisiz")
    assert [phrase for phrase in needed if phrase not in rule] == [], rule
    assert _intake_standard(text) == ADDRESS_STANDARD, rule
    assert "hitapsız" not in text and "hitap kararı)" not in intake, "eski kisisiz kararin ya da sorunun izi"
    common_rules = COMMON_RULES.read_text(encoding="utf-8")
    line = _containing(common_rules, "diye hitap et")
    needed = ('**Okuyucuya "sen" diye hitap et**', "Berlin", "Bir kayıt içinde biçim değişmez", "Sözlük", "kişisiz")
    assert [phrase for phrase in needed if phrase not in line] == [], line
    assert "doğrudan hitap etme" not in common_rules and "kişisiz anlatım kullan" not in common_rules, common_rules
    commands, plain = _examples_after(line, "emir 2. tekil"), _examples_after(line, "kişisiz kalabilir")
    assert commands and {address_forms.form_of(example) for example in commands} == {ADDRESS_STANDARD}, commands
    assert plain and {address_forms.form_of(example) for example in plain} == {"hitapsiz"}, plain
    flags = set(ADDRESS_FLAG.findall((sc.TOOLKIT / "KAPSAM.md").read_text(encoding="utf-8")))
    assert flags == {ADDRESS_STANDARD}, f"KAPSAM.md K32 --address-standard {sorted(flags)}"


# --- skill-son-hal-3 incelemesinin bulgulari (2 ORTA, 5 DUSUK) ---

SINGLE_SOURCE = "Kapandı; ikinci bağımsız kaynak bulunamadı (belediye ve yerel gazete arandı)."
AUDIT_OPEN_CHECK = re.compile(r"acik[_-]mi|açık[- ]mı", re.I)  # city-audit'te acik-mi orneklemesinin izi
EDITOR_TASKS = MappingProxyType({"2": "Çelişkide resmî kurum esas.", "6": "Şema:", "7": "Defter:"})
EDITOR_DELETE_BANS = ("Görev 4–5 açılmadıysa kayıt silme veya ekleme yok", "kapanmış veya taşınmış görünen mekânı silme")


def test_city_pack_single_source_closure_closes_after_the_human_decision(tmp_path, capsys):
    """Inceleme ORTA-1 (B15): 'ikinci_kaynak_yok' icin 'karar gelmeden faz kapanmaz' yaziyordu, karardan sonraki adim
    yoktu. Gercek kapi 'sil' satiri durdukca her kosuda bulgu verir (mekan silinse de, 'tut' dense de): ana dongu fazi
    ya kapatamaz ya da dogrulayicinin dosyasini kendisi degistirir. SKILL.md'deki yol: yeni dogrulayici satiri kararla
    yeniden yazar; 'tut' -> ret + dokunma (temiz), 'sil' + ikinci kaynak gerekce'de (temiz); ikinci kaynak yoksa yalniz
    silinen mekanin 'ikinci_kaynak_yok'u kalir ve yalniz o durumda places cikis 1 ile kapanir."""
    scans = {"spor": [am.scan("golf", "kapalı"), am.scan("museum")]}
    single = am.verify("golf", "sil", "onay", tarama_durum="kapalı", gerekce=SINGLE_SOURCE)
    keep = am.verify("golf", "dokunma", "ret", tarama_durum="kapalı", gerekce="İnsan kararı: tut.")

    def run(slugs: tuple[str, ...], row: dict) -> tuple[int, dict]:
        result = am.gate(tmp_path, capsys, [am.venue(slug) for slug in slugs], scans, {"spor": [row]})
        return result.code, dict(result.codes())

    assert run(("golf", "museum"), single) == (1, {"sil_listede": 1, "ikinci_kaynak_yok": 1})  # karar beklenir
    assert run(("golf", "museum"), keep) == (0, {})
    assert run(("museum",), {**single, "gerekce": am.SECOND}) == (0, {})
    assert run(("museum",), single) == (1, {"ikinci_kaynak_yok": 1})  # tek istisna
    places = _section(_skill_text("city-pack"), "### 4. places")
    rule = _containing(places, "Tek kaynaklı kapanış")
    needed = ("`owner: insan`", "karar gelmeden faz kapanmaz", "yeni şüpheci doğrulayıcı", "elle değiştirmez",
              '"tut" → `ret` + `dokunma`', '"sil" → ikinci bağımsız kaynak', "`gerekce`",
              "yalnız insan kararıyla silinen mekânların `ikinci_kaynak_yok`", "çıkış 1")
    assert [phrase for phrase in needed if phrase not in rule] == [], rule
    assert "`ikinci_kaynak_yok`" in _starting(places, "- Kapı:")


def test_city_pack_names_the_missing_audit_sampling_as_open_work():
    """Inceleme ORTA-2 (B15): city-pack 'city-audit L1 (K39) mekanlari ayni kanit kurallariyla ornekler' diyordu;
    city-audit SKILL.md'de karsiligi yoktu (L1, K39'a kilavuz yontemiyle bakiyordu: mekanin kendi sitesi, B15'in
    kapattigi acik). Karsiligi yokken city-pack bunu acik is diye anar; skill-son-hal-4 W2'den beri var (L1 orneklemi,
    L2'de butun mekanlar, acik_mi_denetim): cumle onu anar, uretimin acik_mi dosyalari denetimde beyandir."""
    sampled = bool(AUDIT_OPEN_CHECK.search(_skill_text("city-audit")))
    line = _containing(_section(_skill_text("city-pack"), "### 4. places"), "city-audit")
    assert line and ("açık iş" in line) != sampled, line
    needed = ("K39", "`acik_mi_denetim`", "L1", "L2", "beyandır") if sampled else ()
    assert [phrase for phrase in needed if phrase not in line] == [], line


def test_city_pack_local_trial_numbers_start_at_901():
    """Inceleme DUSUK-3 (B13): 'baska sehrin kullanmadigi ilk numara' uretim\\ altinda hic sablon_kaynak yokken 900
    verir (make_template 900'u de yerel deneme sayar). Baris'in varsayilani (devir: Tilburg 901, Dortmund 902) ve
    sablon_turetme.md ornegi 901: kural 901'den baslar."""
    rule = _containing(_section(_skill_text("city-pack"), "### 1. intake"), "yerel deneme numarası")
    assert "901'den başla" in rule and "900 verilmez" in rule, rule
    assert make_template.LOCAL_TRIAL_FROM <= 901
    reference = (sc.SKILLS["city-pack"].parent / "references" / "sablon_turetme.md").read_text(encoding="utf-8")
    assert "--city-number 901" in reference


def test_city_pack_open_check_editor_gets_numbered_tasks():
    """Inceleme DUSUK-4 (B15, kural 13): acik-mi uygulama editorunun acik gorevleri numarayla yazili (editor.md'deki
    adlariyla 2, 6, 7 + acik-mi.md §5). editor.md'de silmeyi iki kural engeller; SKILL.md ikisini de aynen anar ve §5'in
    silmesini ikisinden muaf tutar (eskiden yalniz biri). Durak silinirse rota parcasi da duzenlenecek dosyalardadir."""
    editor = (sc.SKILLS["city-pack"].parent / "agents" / "editor.md").read_text(encoding="utf-8")
    tasks = dict(re.findall(r"^(\d)\. \*\*([^*]+)\*\*", editor, re.M))
    assert {number: tasks.get(number) for number in EDITOR_TASKS} == dict(EDITOR_TASKS)
    rule = _containing(_section(_skill_text("city-pack"), "### 4. places"), "Bugün açık mı (B15")
    assert "açık görevler 2, 6, 7 ve §5" in rule and "rota parçası" in rule, rule
    assert [ban for ban in EDITOR_DELETE_BANS if ban not in editor or f'{ban}"' not in rule] == [], rule


def test_common_rules_allowed_step_example_follows_the_address_standard():
    """Inceleme DUSUK-6 (B16): yazarlar ortak kurallar §6'daki izinli islem adimi ornegini kopyalar; ornek intake'in
    hitap standardinda yazilir (standart 'hitapsiz'ken "... numara aranır" olmustu; 'sen' standardinda yine
    "... numarayı ara"). Ornegin dolgu kapilarina takilmadigina test_agent_instructions bakar."""
    rules = COMMON_RULES.read_text(encoding="utf-8")
    allowed = EXAMPLES.findall(_starting(rules, "2. Okuyucuya iş bırakan"))[-1]
    assert allowed.startswith("Randevu için") and address_forms.form_of(allowed) == _intake_standard(
        _skill_text("city-pack")), allowed


def test_city_pack_priority_is_not_asked_and_source_url_goes_to_atinc():
    """Inceleme DUSUK-5: sablon_turetme.md 'teslime gelinirse kullaniciya sor' diyor, SKILL.md 'Sehir yazari 3 yazar';
    intake o dosyayi okuttugu icin gecerli olani SKILL.md soyler (kural 12: kullaniciya teknik karar sorulmaz).
    source_url'nin anlami (Atinc'in sablonlarinda InterNations sehir listesi) ayni maddede Atinc'a sorulur."""
    rule = _containing(_section(_skill_text("city-pack"), "### 1. intake"), "`priority`'nin anlamı")
    needed = ("`priority` = 3", "kullanıcıya sorulmaz", "sablon_turetme.md", "`owner: atinc`", "`source_url`")
    assert [phrase for phrase in needed if phrase not in rule] == [], rule


# --- city-pack SKILL.md: skill-son-hal-5 (kullanici yeni oturumda yalniz 'Tilburg' yazar) ---

RUN_NOTE = re.compile(r'--note "(?P<note>[^"]*)"')
TRIGGERS = ('"şehir paketi üret"', '"CITY-NNN hazırla"', '"<şehir> paketi"', '"city-pack"', "city-audit")


def test_city_pack_sessions_and_audit_handoff_need_no_extra_input():
    """skill-son-hal-5 incelemesi: (1) sehir birden cok oturuma yayilirsa olcum eksik kalmasin diye her oturumun kaydi
    _is\\oturumlar.txt'ye yazilir ve faz 7 olcumu oradan kurulur; (2) teslim mesaji kullaniciya yazacagi tam metni verir;
    (3) teslim edilmis sehir yeniden yazilinca once denetim onerilir; (4) baska sehrin paketi kaynak listesi sayilmaz."""
    text = _skill_text("city-pack")
    intake = _section(text, "### 1. intake")
    deliver = _section(text, "### 7. deliver")
    assert intake.count("oturumlar.txt") >= 2 and "oturumlar.txt" in deliver, (intake, deliver)
    assert "paketini denetle**" in _starting(deliver, "- Kullanıcıya:")
    first = _containing(intake, "İlk adım: bu şehir daha önce üretildi mi?")
    assert "paketini denetle" in first and "ortam.ps1" in first and "dosya yoksa" in first, first
    assert "başka şehirlerinki değil" in _section(text, "### 2. sources")


def test_city_pack_production_is_a_measurement_run():
    """Baris karari (3): her sehir bir olcum kosusudur. Uretim sirasinda skill ve arac kutusu degismez; gorulen skill/
    arac sorunu WORK\\_is\\notlar_skill.md'ye (tarih, faz, sorun, oneri) yazilir, sehir teslim edilince ayri bir
    gelistirme turunda ele alinir. Teslimden sonra kullaniciya yeni, temiz oturumda city-audit L0 denir."""
    text = _skill_text("city-pack")
    rule = _containing(_section(text, "## Değişmez kurallar"), "ölçüm koşusu")
    needed = ("değiştirilmez", "`AGENTS`", "`TK`", r"`WORK\_is\notlar_skill.md`", "tarih, faz, sorun, öneri",
              "pakete girmez", "geliştirme turu")
    assert [phrase for phrase in needed if phrase not in rule] == [], rule
    message = _starting(_section(text, "### 7. deliver"), "- Kullanıcıya:")
    needed = ("temiz bir oturumda", "`city-audit` L0", "notlar_skill.md", "geliştirme turu")
    assert [phrase for phrase in needed if phrase not in message] == [], message
    assert "notlar_skill.md" in _starting(_section(text, "## Sabit yollar"), "WORK\\_is\\ ")  # dosya duzeni


def test_city_pack_run_log_note_is_built_by_the_skill():
    """Baris karari: run_log --note'u skill kurar ve komut satirinda acikca yazar: '<N>. şehir; ülke paketi: yok;
    hitap: <intake standardi>'. N = bu sehir disindaki uretim\\*\\RUN_LOG.csv sayisi + 1 (pilot 1., notu 'ilk deneme';
    --score'lu yeniden kosuda not ayni). Ulke paketini skill kendisi kurmaz (yoksa 'yok'). Eski 'gelistirmeyle karisik
    kosuda' istisnasi kalkar: her sehir olcum kosusudur."""
    text = _skill_text("city-pack")
    (command, namespace), = [(c, ns) for c, ns in _parsed("city-pack") if c.script == "run_log"]
    note = RUN_NOTE.search(command.text)
    expected = f"<N>. şehir; ülke paketi: yok; hitap: {_intake_standard(text)}"
    assert note and note["note"] == expected and namespace.note, command.text
    rule = _containing(_section(text, "### 7. deliver"), "`<N>` =")
    needed = (r"`ROOT\uretim\*\RUN_LOG.csv`", "bu şehir dışındaki", "+ 1", '"ilk deneme"', "`manifest.country_pack`",
              "`hitap.txt`", "`--score`", "$_.Directory.Name -ne $CITY")
    assert [phrase for phrase in needed if phrase not in rule] == [], rule
    assert "Geliştirmeyle karışık" not in text
    pack = _containing(_section(text, "### 1. intake"), "Ülke paketi (`manifest.country_pack`")
    assert "skill kurmaz" in pack and "`ülke paketi: yok`" in pack, pack


def test_city_pack_description_triggers_on_a_bare_city_name():
    """Proje kurali (ROOT\\CLAUDE.md): kullanici yalniz bir sehir adi yazarsa city-pack baslar. description bu
    tetikleyiciyi de soyler, eskileri kalir; frontmatter gecerli YAML (ad city-pack, description en cok 1024)."""
    head = re.match(r"---\n(?P<yaml>.*?)\n---\n", _skill_text("city-pack"), re.S)
    meta = yaml.safe_load(head["yaml"]) if head else {}
    description = str(meta.get("description", ""))
    assert meta.get("name") == "city-pack" and 0 < len(description) <= 1024, meta
    needed = ('kullanıcı yalnız bir şehir adı yazdığında (ör. "Tilburg")', *TRIGGERS)
    assert [phrase for phrase in needed if phrase not in description] == [], description
    project = PROJECT_RULES.read_text(encoding="utf-8")
    assert "## Kullanıcı yalnız bir şehir adı yazarsa" in project and "`city-pack` skill'ini çağır" in project


def test_city_pack_intake_first_checks_for_an_existing_production():
    """Proje kurali: sehrin uretim\\<city_id>\\manifest.json'u varsa yeni uretim baslatilmaz; durum ozetlenir, tek
    soruyla tek oneri (devam / yeni surum / bastan). Intake'in ILK adimi ayni kural, hicbir dosya yazilmadan: teslim
    edilmemisse manifest'teki fazdan devam, teslim edilmisse yeni surum (v002) onerisi."""
    intake = _section(_skill_text("city-pack"), "### 1. intake")
    first = _starting(intake, "- ")
    needed = (r"`ROOT\uretim\<city_id>\manifest.json`", "hiçbir dosya yazmadan", "yeni üretim başlatılmaz",
              "`manifest_check`", "`phase`", "`delivered`", "tek soru", "tek öneri", "devam", "yeni sürüm (v002)",
              "baştan", "CLAUDE.md")
    assert [phrase for phrase in needed if phrase not in first] == [], first
    project = _containing(PROJECT_RULES.read_text(encoding="utf-8"), r"manifest.json")
    needed = (r"`uretim\<city_id>\manifest.json`", "yeni üretim başlatma", "tek öneri", "devam / yeni sürüm / baştan")
    assert [phrase for phrase in needed if phrase not in project] == [], project


# --- city-audit SKILL.md: B15 acik-mi orneklemesi (skill-son-hal-4 W2 ve incelemesi) ---

AUDIT_L1 = "## L1: riske göre LLM + görsel (varsayılan)"
AUDIT_STEP = "**Bugün açık mı (K39"  # L1'deki adimin ilk satiri
AUDIT_ROLES = ("uretim", "orneklem", "denetim", "kanit", "acik", "kopya", "sayim")  # adimin komutlari, sirasiyla
AUDIT_TOOLS = MappingProxyType({"acik_mi": acik_mi.main, "acik_mi_denetim": acik_mi_denetim.main})
AUDIT_SILENT = ("eski_kanit", "footer_kanit", "eylem_celiski", "kaynak_izi_yok")  # denetim kapisinda cikmaz
AUDIT_EXCEL = b"teslim"
FOOTER_ONLY = MappingProxyType({"kanit_alinti": "© 2019 Golfbaan", "kanit_tarihi": "tarihsiz (footer © 2019)"})
OLD_NEWS = MappingProxyType({"kanit_alinti": "Golfbaan Welschap blijft open", "kanit_tarihi": "2019-03-01 (haber)"})
CLOSED_URL, SECOND_URL = "https://nieuws.example/yer", "https://gemeente.example/nieuws/sluiting"  # am.verify("yer")
CLOSURE = MappingProxyType({"eylem": "sil", "kanit_alinti": "De golfbaan sluit definitief",
                            "gerekce": f"Kapanış iki kaynakta. İkinci kaynak: {SECOND_URL} «definitief gesloten»"})
AUDIT_PAGES = MappingProxyType({CLOSED_URL: "De golfbaan sluit definitief. Het museum blijft gewoon open.",
                                SECOND_URL: "Het terrein is definitief gesloten."})


@dataclass(frozen=True)
class AuditCase:
    """Tek mekanli senaryo: kart notu, ajan satiri (None: atladi), denetim kapisinin kodlari, sayim sinifi, yeni ajana
    gider mi, SKILL.md'deki sinif satiri (onek, ifadeler)."""
    note: str
    row: MappingProxyType | None
    gate: MappingProxyType
    sinif: str
    retry: bool
    line: tuple[str, tuple[str, ...]]


def _case(note, row, gate, sinif, retry, line) -> AuditCase:
    return AuditCase(note, None if row is None else MappingProxyType(dict(row)), MappingProxyType(gate), sinif, retry,
                     line)


AUDIT_CASES = MappingProxyType({
    "kalici-kapanis": _case("", CLOSURE, {"sil_listede": 1}, "kapanis_iki_kaynak", False, (
        "- **P0**", ("`sil_listede`", "`ikinci_kaynak_yok` olmadan", "`kapanis_iki_kaynak`", "K42", "B1", "rota"))),
    "tek-kaynak": _case("", {"eylem": "sil", "sonuc": "onay", "gerekce": SINGLE_SOURCE},
                        {"sil_listede": 1, "ikinci_kaynak_yok": 1}, "kapanis_teyitsiz", True,
                        ("- **P1**", ("`sil_listede`", "`kapanis_teyitsiz`", "`ikinci_kaynak_yok`", "insan"))),
    "kopya-tutmuyor": _case("", {**CLOSURE, "gerekce": f"İkinci kaynak: {SECOND_URL} «al gesloten sinds 2020»"},
                            {"sil_listede": 1}, "kapanis_teyitsiz", True,
                            ("- **P1**", ("`kapanis_teyitsiz`", "teyit edilemeyen"))),
    "not-yok": _case("", {"eylem": "kartta belirt"}, {"not_yok": 1}, "belirt_teyitli", False,
                     ("- **P1**", ("`not_yok`", "`belirt_teyitli`", "taşınma"))),
    "not-guncel": _case(am.NOTE, {"eylem": "kartta belirt"}, {}, "belirt_teyitli", False,
                        ("- **P1**", ("`kartta belirt`", "`belirt_teyitli`", "`yeni_bilgi`"))),
    "belirt-teyitsiz": _case("", {"eylem": "kartta belirt", "kanit_url": "https://nieuws.example/weg"}, {"not_yok": 1},
                             "belirt_teyitsiz", True, ("- Bulgu değil", ("`belirt_teyitsiz`", "doğrulanamadı"))),
    "not-eskimis": _case(am.NOTE, {"eylem": "dokunma"}, {}, "acik_dogrulandi", False,
                         ("- **P2**", ("`ret` + `dokunma`", "`acik_dogrulandi`"))),
    "acik": _case("", {"eylem": "dokunma"}, {}, "acik_dogrulandi", False,
                  ("- Bulgu değil", ("`ret` + `dokunma`", "`acik_dogrulandi`", "doğrulandı"))),
    "telif-satiri": _case("", {"eylem": "dokunma", **FOOTER_ONLY}, {}, "dogrulanamadi", True,
                          ("- Bulgu değil", ("`footer_kanit`", "telif", "doğrulanamadı"))),
    "eski-tarih": _case("", {"eylem": "dokunma", **OLD_NEWS}, {}, "dogrulanamadi", True,
                        ("- Bulgu değil", ("`eski_kanit`", "doğrulanamadı"))),
    "belirsiz": _case("", {"eylem": "dokunma", "sonuc": "onay"}, {}, "dogrulanamadi", False,
                      ("- Bulgu değil", ("`onay` + `dokunma`", "`dogrulama_yok`", "doğrulanamadı"))),
    "atlandi": _case("", None, {"dogrulama_yok": 1, "bos_alinti": 1, "bos_url": 1}, "dogrulanamadi", False, (
        "- Kayıt kusuru", ("`dogrulama_yok`", "`bos_alinti`", "`bos_url`", "yeni ajan", "doğrulanamadı"))),
})


def _audit_step() -> str:
    """city-audit L1'deki acik-mi adimi: kalin basligindan L1'in bir sonraki kalin baslikli paragrafina kadar."""
    l1 = _section(_skill_text("city-audit"), AUDIT_L1)
    start = l1.find(AUDIT_STEP)
    assert start >= 0, f"city-audit L1'de '{AUDIT_STEP}' adimi yok"
    end = l1.find("\n**", start + len(AUDIT_STEP))
    return l1[start:] if end < 0 else l1[start:end]


def _lines_starting(text: str, prefix: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip().startswith(prefix)]


def _block_after(prefix: str) -> list[str]:
    """Adimda `prefix` ile baslayan maddeden sonraki ilk kod blogunun satirlari (bas bosluksuz)."""
    lines = [line.strip() for line in _audit_step().splitlines()]
    start = next(index for index, line in enumerate(lines) if line.startswith(prefix))
    fence = next(index for index in range(start + 1, len(lines)) if lines[index].startswith("```"))
    end = next(index for index in range(fence + 1, len(lines)) if lines[index].startswith("```"))
    return lines[fence + 1:end]


def _role(command: sc.Command, namespace: argparse.Namespace) -> str:
    variables = VARIABLES_BY_SKILL["city-audit"]
    if command.script == "acik_mi":
        out = PureWindowsPath(variables["OUT"])
        folders = {PureWindowsPath(variables["ACIKMI"]): "uretim", out / acik_mi_denetim.BATCH_DIR: "denetim",
                   out / acik_mi_denetim.OPEN_DIR: "acik"}
        return folders.get(PureWindowsPath(namespace.acik_mi), "?")
    return {"acik_mi_denetim": getattr(namespace, "command", "?"), "fetch_snapshot": "kopya"}.get(command.script, "?")


def _audit_commands() -> dict[str, tuple[sc.Command, argparse.Namespace]]:
    """Adimdaki toolkit komutlari rolune gore; her rol tam bir kez."""
    step = _audit_step()
    found: dict[str, list[tuple[sc.Command, argparse.Namespace]]] = {}
    for command, namespace in _parsed("city-audit"):
        if command.text in step:
            found.setdefault(_role(command, namespace), []).append((command, namespace))
    assert {role: len(rows) for role, rows in found.items()} == dict.fromkeys(AUDIT_ROLES, 1), \
        {role: [command.id for command, _ in rows] for role, rows in found.items()}
    return {role: rows[0] for role, rows in found.items()}


def _audit_values(tmp_path: Path, acikmi: str = "") -> MappingProxyType:
    """SKILL.md degiskenleri, OUT/XLSX/ACIKMI tmp_path'te (ACIKMI bos: uretim beyani yok)."""
    return MappingProxyType({**VARIABLES_BY_SKILL["city-audit"], "OUT": str(tmp_path / "out"),
                             "XLSX": str(tmp_path / "paket" / "teslim.xlsx"), "ACIKMI": acikmi})


def _run_documented(capsys, role: str, values, *extra, routes=AUDIT_PAGES) -> tuple[int, dict]:
    """SKILL.md'deki komut, gercek main()'le (fetch_snapshot sahte tasimayla): (cikis, son stdout satirinin JSON'u)."""
    command, _ = _audit_commands()[role]
    argv = [*sc.to_argv(command.args, values), *map(str, extra)]
    if command.script == "fetch_snapshot":
        pages = {url: ok(f"<html><body><main><p>{body}</p></main></body></html>".encode()) for url, body in routes.items()}
        code = fetch_snapshot.main(argv, transport=FakeTransport(pages), sleep=lambda seconds: None,
                                   clock=lambda: "2026-10-23")
    else:
        code = AUDIT_TOOLS[command.script](argv)
    lines = capsys.readouterr().out.strip().splitlines()
    return code, json.loads(lines[-1]) if lines else {}


def _audit_pipeline(tmp_path: Path, capsys, cards: list[dict], rows: list[dict], values=None) -> dict[str, tuple]:
    """Adim SKILL.md'deki sirayla: orneklem, ajan satirlari (parti_01), kapi, kanit, ikinci kapi, kopya, sayim (yil
    am.MIN_YEAR'a sabit)."""
    values = values or _audit_values(tmp_path)
    out, xlsx = Path(values["OUT"]), Path(values["XLSX"])
    am.write_jsonl(out / acik_mi_denetim.VENUES, cards)
    xlsx.parent.mkdir(parents=True, exist_ok=True)
    xlsx.write_bytes(AUDIT_EXCEL)
    results = {"orneklem": _run_documented(capsys, "orneklem", values)}
    if rows:
        am.write_jsonl(out / acik_mi_denetim.BATCH_DIR / f"parti_01{acik_mi.VERIFY_SUFFIX}.jsonl", rows)
    for role in ("denetim", "kanit", "acik", "kopya", "sayim"):
        extra = ("--min-year", am.MIN_YEAR) if role in ("denetim", "acik") else ()
        results[role] = _run_documented(capsys, role, values, *extra)
    return results


def test_city_audit_open_check_runs_its_commands_in_order():
    """W2 incelemesi: uretim beyani -> orneklem -> denetim kapisi -> kanit -> ikinci kapi -> kanit kopyasi -> sayim;
    yazan her komutun ciktisi bir sonrakinin girdisi (adlar aracin sabitleri)."""
    commands = _audit_commands()
    lines = [commands[role][0].line for role in AUDIT_ROLES]
    assert lines == sorted(lines), dict(zip(AUDIT_ROLES, lines))
    out = PureWindowsPath(VARIABLES_BY_SKILL["city-audit"]["OUT"])
    gate, second, copy = (commands[role][1] for role in ("denetim", "acik", "kopya"))
    assert [PureWindowsPath(path) for path in gate.mekanlar] == [out / acik_mi_denetim.SAMPLE_NAME]
    assert PureWindowsPath(gate.out) == out / acik_mi_denetim.AUDIT_REPORT
    assert [PureWindowsPath(path) for path in second.mekanlar] == [out / acik_mi_denetim.OPEN_LIST]
    assert PureWindowsPath(second.out) == out / acik_mi_denetim.OPEN_REPORT
    evidence = out.joinpath(*acik_mi_denetim.EVIDENCE_DIR.parts)
    assert PureWindowsPath(copy.out_dir) == evidence and PureWindowsPath(copy.urls) == evidence / acik_mi_denetim.URLS_NAME
    assert PureWindowsPath(copy.must_contain) == evidence / acik_mi_denetim.EVIDENCE_NAME
    for prefix in ("- Örneklem", "- Açık kanıtı"):  # cikis 2'de sonraki komutlar eski dosyalarla calismaz
        block = _block_after(prefix)
        assert block[1].startswith("if ($LASTEXITCODE -eq 2) { throw"), (prefix, block)


def test_city_audit_open_check_reruns_the_production_gate_on_the_delivered_list():
    """W2 (B15): uretimin acik-mi klasoru (`ACIKMI`, Girdi satirinda) beyandir; kapi teslim Excel'inin dokumuyle
    (L0 xlsx_dump: Mekânlar ve Kaynaklar) yeniden calisir, raporu OUT'a yazar. Inceleme: cikis 2'de yalniz komut ya da
    yol duzeltilir (uretimin dosyasi degil); eski rapor once silinir, rapor yoksa ornekleyici ACIKMI'yi okumaz."""
    variables = VARIABLES_BY_SKILL["city-audit"]
    assert "ACIKMI" in variables, "Girdi satirinda `ACIKMI` (uretimin acik-mi klasoru) yok"
    assert "yoksa boş" in _containing(_skill_text("city-audit"), "$ACIKMI="), "PowerShell basinda $ACIKMI tanimi"
    command, made = _audit_commands()["uretim"]
    dump = PureWindowsPath(next(ns.out_dir for c, ns in _parsed("city-audit") if c.script == "xlsx_dump"))
    assert [PureWindowsPath(p) for p in made.mekanlar] == [dump / "Mekânlar.jsonl"]
    assert [PureWindowsPath(p) for p in made.kaynaklar or []] == [dump / "Kaynaklar.jsonl"]
    out = PureWindowsPath(variables["OUT"])
    assert made.min_year is None and PureWindowsPath(made.out) == out / acik_mi_denetim.PRODUCTION_REPORT
    assert _block_after("- Üretim beyanı") == [
        rf"Remove-Item -LiteralPath $OUT\{acik_mi_denetim.PRODUCTION_REPORT} -ErrorAction Ignore", command.text]
    rule = _starting(_audit_step(), "- Üretim beyanı")
    needed = ("`ACIKMI`", "kanıt değil", "örneklem önceliği", "çıkış 2", "yalnız komut ya da yol düzeltilir",
              "üretimin dosyası düzeltilmez", "üretim beyanı okunamadı", "(a), (b) ve (d)")
    assert [phrase for phrase in needed if phrase not in rule] == [], rule


def _production(tmp_path: Path) -> Path:
    """Uretim acik-mi klasoru: yer01 footer kaniti (a), yer02 dogrulamasiz belirsiz (a+b), yer03 kapali + ret +
    dokunma (d); kalanlar tarihli kanitla acik."""
    folder = tmp_path / "uretim" / "acik_mi"
    special = {"yer01": am.scan("yer01", **FOOTER_ONLY), "yer02": am.scan("yer02", "belirsiz"),
               "yer03": am.scan("yer03", "kapalı")}
    slugs = [f"yer{index:02d}" for index in range(1, 21)]
    am.write_jsonl(folder / "spor.jsonl", [special.get(slug) or am.scan(slug) for slug in slugs])
    am.write_jsonl(folder / "spor_dogrulama.jsonl", [am.verify("yer03", tarama_durum="kapalı")])
    return folder


def test_city_audit_open_check_samples_risky_and_random_venues(tmp_path, capsys):
    """W2: orneklem en az 8 ve %10; oncelikliler (uretim kapisinin bulgulari, 'belirsiz' kalanlar, tarihli notlu
    kartlar, inceleme: cekismeli kararlar) hepsi; rastgele kisim en az n/2, oncelikliler n'yi doldursa da, sira
    sha256((excel_sha256 kucuk harf + entry_id).encode('utf-8')). SKILL.md'deki komutlarla: uretim beyani raporu ->
    orneklem."""
    rule = _starting(_audit_step(), "- Örneklem")
    needed = ("en az 8", "%10", "acik-mi-uretim.json", "`belirsiz`", "`onay` + `dokunma`", "itibarıyla", "(d)",
              "`kapalı`", "`taşındı`", "`ret` + `dokunma`", "rastgele", "⌈n/2⌉", "doldursa da",
              "`sha256((excel_sha256 + entry_id).encode('utf-8'))`", "küçük harf", "baştan kurar")
    assert [phrase for phrase in needed if phrase not in rule] == [], rule
    assert [field for field in acik_mi.TEXT_FIELDS if f"`{field}`" not in rule] == [], rule
    values = _audit_values(tmp_path, str(_production(tmp_path)))
    out = Path(values["OUT"])
    cards = [am.venue(f"yer{index:02d}", note=am.NOTE if index == 4 else "") for index in range(1, 21)]
    am.write_jsonl(out / acik_mi_denetim.VENUES, cards)
    am.write_jsonl(out / "_dump" / "Kaynaklar.jsonl", [])
    Path(values["XLSX"]).parent.mkdir(parents=True)
    Path(values["XLSX"]).write_bytes(AUDIT_EXCEL)
    assert _run_documented(capsys, "uretim", values, "--min-year", am.MIN_YEAR)[0] == 1
    code, summary = _run_documented(capsys, "orneklem", values)
    sample = [json.loads(line) for line in (out / acik_mi_denetim.SAMPLE_NAME).read_text(encoding="utf-8").splitlines()]
    assert [(row["entry_id"], row["neden"]) for row in sample[:4]] == [
        (am.eid("yer01"), "a"), (am.eid("yer02"), "a+b"), (am.eid("yer03"), "d"), (am.eid("yer04"), "c")]
    excel = hashlib.sha256(AUDIT_EXCEL).hexdigest()
    rest = sorted((card["entry_id"] for card in cards[4:]),
                  key=lambda entry: hashlib.sha256((excel + entry).encode("utf-8")).hexdigest())
    assert [(row["entry_id"], row["neden"]) for row in sample[4:]] == [(entry, "rastgele") for entry in rest[:4]]
    assert (code, summary["uretim"], summary["oncelikli"], summary["rastgele"]) == (0, "okundu", 4, 4)


def test_city_audit_unreadable_production_files_are_skipped_not_repaired(tmp_path, capsys):
    """W2 incelemesi: uretimin JSONL'i bozuksa kapi cikis 2 verir ve rapor yazmaz (eski rapor SKILL.md'nin ilk
    satiriyla silinmistir); orneklem (a), (b), (d) olmadan secilir, uretimin dosyasina dokunulmaz."""
    folder = _production(tmp_path)
    broken = folder / "spor_dogrulama.jsonl"
    broken.write_text("{bozuk\n", encoding="utf-8")
    before = broken.read_bytes()
    values = _audit_values(tmp_path, str(folder))
    out = Path(values["OUT"])
    am.write_jsonl(out / acik_mi_denetim.VENUES, [am.venue(f"yer{index:02d}") for index in range(1, 21)])
    am.write_jsonl(out / "_dump" / "Kaynaklar.jsonl", [])
    Path(values["XLSX"]).parent.mkdir(parents=True)
    Path(values["XLSX"]).write_bytes(AUDIT_EXCEL)
    assert _run_documented(capsys, "uretim", values)[0] == 2
    assert not (out / acik_mi_denetim.PRODUCTION_REPORT).exists()
    code, summary = _run_documented(capsys, "orneklem", values)
    assert (code, summary["uretim"], summary["oncelikli"]) == (0, "rapor yok", 0) and broken.read_bytes() == before


def test_city_audit_open_check_agent_is_an_independent_skeptic():
    """W2: ajan kartlari yazmamis, acik-mi.md §2 (kendi sitesi acik kaniti degil) + §4 supheci rolu; uretimin acik-mi
    dosyalari verilmez; yalniz OUT'a yazar. Inceleme: 'onay' = belirsiz kaldi tanimi §4'un tek kaynakli kapanisiyla
    ('onay' + 'sil') celismez; ikinci kaynak kanit kopyasinin okudugu bicimde. AGENTS satiri acik-mi.md'yi anar."""
    step = _audit_step()
    assert "kendi sitesi" in step.splitlines()[0], step.splitlines()[0]
    agent = _starting(step, "- Doğrulama:")
    needed = (r"`AGENTS\acik-mi.md`", "§2", "§4", "şüpheci", "kartları yazmamış", "üretimin açık-mı dosyaları verilmez",
              "25 dk", "`ret` = durumu kanıtla belirledi", "`onay` = belirsiz kaldı", "`onay` + `sil`", "«")
    assert [phrase for phrase in needed if phrase not in agent] == [], agent
    assert acik_mi_denetim.SECOND_SOURCE.findall(f"İkinci kaynak: {SECOND_URL} «definitief gesloten»") == [
        (SECOND_URL, "definitief gesloten")]
    constants = _containing(_skill_text("city-audit"), "AGENTS  =")
    named = re.findall(r"[\w-]+\.md", constants)
    assert "acik-mi.md" in named, constants
    assert [name for name in named if not (sc.SKILLS["city-pack"].parent / "agents" / name).is_file()] == []


@pytest.mark.parametrize("case", list(AUDIT_CASES))
def test_city_audit_open_check_classes_match_the_real_tools(tmp_path, capsys, case):
    """W2 ve incelemesi: belgelenen komutlar gercek araclarla zincir halinde calisir; denetim kapisinin kodlari, sayim
    sinifi ve yeni ajan karari senaryonun beklenenidir; SKILL.md'deki sinif satiri (P0/P1/P2, bulgu degil, kayit
    kusuru) onlari anar. Telif satiri ve eski tarih artik ikinci kapida bulgu verir (eskiden temiz geciyordu)."""
    spec = AUDIT_CASES[case]
    rows = [] if spec.row is None else [am.verify("yer", **{"tarama_durum": "belirsiz", **spec.row})]
    results = _audit_pipeline(tmp_path, capsys, [am.venue("yer", note=spec.note)], rows)
    out = tmp_path / "out"
    report = json.loads((out / acik_mi_denetim.AUDIT_REPORT).read_text(encoding="utf-8"))
    assert (results["denetim"][0], dict(Counter(item["code"] for item in report["findings"]))) == (
        1 if spec.gate else 0, dict(spec.gate))
    assert results["sayim"][0] == 0, results["sayim"]
    (venue,) = json.loads((out / acik_mi_denetim.COUNT_NAME).read_text(encoding="utf-8"))["mekanlar"]
    assert (venue["sinif"], venue["yeni_ajan"]) == (spec.sinif, spec.retry), venue
    prefix, phrases = spec.line
    lines = _lines_starting(_audit_step(), prefix)
    assert any(all(phrase in line for phrase in phrases) for line in lines), (prefix, phrases, lines)


def test_city_audit_open_check_names_every_gate_code():
    """W2: kapinin her kodu adimda anilir; denetim kapisinda cikamayanlar ('belirsiz' tarama satiri, --kaynaklar yok)
    kayit kusuru satirinda 'çıkmaz' diye yazilidir ve senaryolarda gercekten cikmaz. Inceleme: eski_kanit ve
    footer_kanit ikinci kapinin isidir (acik kaniti), kanit kopyasinin bulgusu evidence_missing."""
    step = _audit_step()
    assert [code for code in acik_mi.CODES if f"`{code}`" not in step] == [], step
    defects = _starting(step, "- Kayıt kusuru")
    assert "çıkmaz" in defects and [code for code in AUDIT_SILENT if f"`{code}`" not in defects] == [], defects
    produced = {code for spec in AUDIT_CASES.values() for code in spec.gate}
    assert not produced & set(AUDIT_SILENT), produced
    evidence = _starting(step, "- Açık kanıtı")
    named = ("`eski_kanit`", "`footer_kanit`", "`dogrulama_yok`", "`evidence_missing`", "`sayim`", "«")
    assert [phrase for phrase in named if phrase not in evidence] == [], evidence
    assert {spec.sinif for spec in AUDIT_CASES.values()} == set(acik_mi_denetim.CLASSES)
    assert [name for name in acik_mi_denetim.CLASSES if f"`{name}`" not in step] == [], step


def test_city_audit_new_agent_rewrites_only_its_venue_row(tmp_path, capsys):
    """W2 incelemesi (DUSUK): yeni ajan ayni parti dosyasinda yalniz o mekanin satirini yeniden yazar, oteki satirlar
    aynen kalir. Denemede yeni satir baska dosyaya yazilmisti: eski gecersiz satir ('doğrulandı') yerinde kaldi, kapi
    gecersiz_sonuc vermeyi surdurdu. Kanit yetmeyen mekan da bir kez yeni ajana gider."""
    rule = _starting(_audit_step(), "- Kayıt kusuru")
    needed = ("aynı `parti_NN_dogrulama.jsonl`", "yalnız o mekânın satırını", "öteki satırlar aynen kalır",
              "elle değiştirmez", "başka dosyaya", "İkinci denemede", "`sayim`")
    assert [phrase for phrase in needed if phrase not in rule] == [], rule
    retry = _starting(_audit_step(), "- Kanıtı yetmeyen")
    assert all(phrase in retry for phrase in ("`yeni_ajan`", "bir kez", "kesindir")), retry
    values = _audit_values(tmp_path)
    out = Path(values["OUT"])
    am.write_jsonl(out / acik_mi_denetim.VENUES, [am.venue("yer"), am.venue("golf")])
    Path(values["XLSX"]).parent.mkdir(parents=True)
    Path(values["XLSX"]).write_bytes(AUDIT_EXCEL)
    assert _run_documented(capsys, "orneklem", values)[0] == 0
    batch = out / acik_mi_denetim.BATCH_DIR
    other = am.verify("golf")
    am.write_jsonl(batch / "parti_01_dogrulama.jsonl", [am.verify("yer", sonuc="doğrulandı"), other])
    gate = ("denetim", values, "--min-year", am.MIN_YEAR)
    assert _run_documented(capsys, *gate)[1]["by_code"] == {"gecersiz_sonuc": 1}
    am.write_jsonl(batch / "parti_02_dogrulama.jsonl", [am.verify("yer")])  # yanlis: baska dosya
    assert _run_documented(capsys, *gate)[1]["by_code"] == {"gecersiz_sonuc": 1}
    (batch / "parti_02_dogrulama.jsonl").unlink()
    am.write_jsonl(batch / "parti_01_dogrulama.jsonl", [am.verify("yer"), other])  # dogru: ayni dosya, yalniz o satir
    assert _run_documented(capsys, *gate)[0] == 0


def test_city_audit_k39_is_partial_from_a_sample_and_full_only_at_l2():
    """W2: kilavuz 'orneklemden tum pakete GECTI cikarma': L1'de K39 bulgu yoksa kismi, varsa kaldi; geçti yalniz L2'de
    butun mekanlarla (acik_mi_denetim orneklem --tam). Inceleme: sayilar elle degil acik-mi-sayim.json'dan; sil/kartta
    belirt sinifi sonuc'a bakmaz; P0 ISSUE'da mekanin durak oldugu rotalar. Diger L kontrolleri K39'a bakmaz."""
    text = _skill_text("city-audit")
    check = _starting(_audit_step(), "- CHECK:")
    needed = ("`kaldı`", "`kısmi`", "`geçti` çıkmaz", "doğrulanamayan", "acik-mi-sayim.json", "elle sayılmaz")
    assert [phrase for phrase in needed if phrase not in check] == [], check
    classes = _starting(_audit_step(), "- Sınıflama")
    assert all(phrase in classes for phrase in ("K39", "B5", "`sonuc`'a bakmaz", "`stop_entry_ids`")), classes
    other = _containing(_section(text, AUDIT_L1), "**Diğer L kontrolleri:**")
    assert "K39" in other and "açık-mı" in other, other
    l2 = _section(text, "## L2: tam")
    needed = ("açık-mı", "bütün mekânlar", "`geçti`", "`acik_mi_denetim orneklem --tam`", "`dogrulanamayan` 0")
    assert [phrase for phrase in needed if phrase not in l2] == [], l2
