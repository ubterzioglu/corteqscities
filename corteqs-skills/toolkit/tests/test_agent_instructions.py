"""Sehirden bagimsiz ajan talimatlari: city-pack/agents/ortak-kurallar.md, yer-yazari.md, editor.md (S3'un testi).

Neyi sinar:
- sehre/ulkeye/ortama ozgu kalinti yok; yer tutucular tanimli; komut satirlari toolkit'in GERCEK argparse'indan
  gecer ve paylasilan dosyalara degil <TMP>'ye yazar;
- add_sources klasoru: her ajan kosusu YENI, role ozgu klasor (snap_<gorev>-<rol><sira>); ana dongunun kaynak
  kesfi klasorleriyle (city-pack SKILL.md'den canli okunur) ve baska rol/kosuyla cakismaz; sahte tasimayla belgelenen
  kosular kesfin eklenen.json haritasini (B3 eslemesi dahil) silmez;
- yanit yazarinin dosya yollari ortak kurallarda; merge_package yalniz o yollari okur (rol dosyasindaki eski
  data/Yanıtlar.<topic_id>.jsonl birlesmez); kendi kontrol satir sayisini dogrulatir;
- belgelenen anahtar siralari = merge_package kapisi = resmi sema (araclar/arac schema_definition.py, salt okunur);
- SayfaAlanlari tablosu = resmi web sozlesmesi (web_contract.py, ast ile okunur) = merge_package PAGE_KEYS;
- iddia defteri ornegi ve sahip tablosu (Adimlar dahil) = merge_package; yasaklanan dolgu ifadeleri kapida yakalanir;
- dunya kutusu yalniz koordinatsiz parcada (o kutuyla yer degistirmis koordinat yakalanmaz);
- belgelenen bicimle yazilmis mini parcalar merge_package'dan TEMIZ gecer; belgenin dayandigi ret davranislari
  (source_urls, uydurma alinti, http baglanti) gercekten bulgu uretir; xlsx_dump Sehir dokumu belgelendigi gibidir.
Ag yok; yazma yalniz tmp_path. araclar/arac, ekler, SKILL.md ve agents salt okunur (sablon tmp_path'e kopyalanip
okunur; resmi sema bayt kodu yazilmadan yuklenir). Yollar bu dosyanin yerinden turetilir (depo koku = toolkit/../..).
'real' isaretli testler gercek araclar/arac ya da ekler sablonu yoksa atlanir (pytest.ini; bu makinede vardir).
KIRMA_AGENTS_DIR: yalniz kirma (mutasyon) denemesi icin agents klasorunun bozulmus kopyasi; normalde verilmez.
Calistirma (toolkit klasorunden):
  $env:PYTHONDONTWRITEBYTECODE=1; <PY> -m pytest -q -p no:cacheprovider tests\\test_agent_instructions.py
"""
from __future__ import annotations

import ast
import importlib.util
import json
import os
import re
import shutil
import sys
from pathlib import Path, PureWindowsPath

import pytest

import add_sources
import merge_package as mp
import skill_commands_helpers as sc
import text_quality as tq
import xlsx_dump
from web_fetch import RawResponse

TOOLKIT = Path(__file__).resolve().parent.parent
SKILLS = TOOLKIT.parent
ROOT = SKILLS.parent  # SKILL.md'deki ROOT
AGENTS = Path(os.environ.get("KIRMA_AGENTS_DIR") or SKILLS / "city-pack" / "agents")
SKILL_MD = SKILLS / "city-pack" / "SKILL.md"
CONTENT = ROOT / "araclar" / "arac" / "core" / "content_delivery"
TEMPLATE = ROOT / "ekler" / "CITY-003_aberdeen_v001.xlsx"  # pilot disi bir sehrin sablonu (yalniz kopyasi okunur)
needs_schema = pytest.mark.skipif(
    not ((CONTENT / "schema_definition.py").is_file() and (CONTENT / "web_contract.py").is_file()),
    reason="gercek araclar/arac klasoru yok")
needs_template = pytest.mark.skipif(not TEMPLATE.is_file(), reason="ekler sablonu yok")

NEW_FILES = ("ortak-kurallar", "yer-yazari", "editor")
SHEETS_BY_FILE = {"ortak-kurallar": ("Yanıtlar", "Bağlantılar", "Adımlar"),
                  "yer-yazari": ("Mekânlar", "Mahalleler", "Sözlük", "SayfaAlanları", "Şehir", "Rotalar")}
FAKE = {"<city_id>": "ornek-sehir", "<WORK>": r"C:\sahte\uretim\ornek-sehir", "<TK>": str(TOOLKIT / "scripts"),
        "<PY>": r"C:\sahte\.venv\Scripts\python.exe", "<TMP>": r"C:\sahte\gecici\gorev_w", "<gorev>": "m1",
        "<konu>": "kesif", "<rol>": "yazar", "<sira>": "1", "<tarih>": "2026-01-15", "<bbox>": "51.3,51.55,5.3,5.6"}
BANNED = ("eindhoven", "city-039", "tilburg", "dortmund", "aberdeen", "hollanda", "rijksoverheid", "belastingdienst",
          "ind.nl", "svb", "rdw", "pdok", "huisarts", "gemeente", "c:\\", "temp_private", "appdata", "scratchpad",
          "baris", "2026-10-")
KEY_BLOCK = re.compile(r"Anahtar sırası \((?P<sheet>[^)\n]+)\):\n```text\n(?P<keys>[^`]+?)\n```")
COMMAND = re.compile(r"^\s*& <PY> <TK>\\(?P<script>\w+)\.py(?P<args>[^\n]*)$", re.M)
PLACEHOLDER = re.compile(r"<[A-Za-z_]+>")
LEDGER_KEYS = ["claim_id", "entry_id", "field", "claim", "value", "unit", "period", "source_id", "url", "quote"]
SNAP_TOKEN = re.compile(r"snap_[A-Za-z0-9_<>-]*")
AGENT_SIDE = ("<gorev>", "<rol>", "<sira>")  # SKILL.md'de ajan klasorunu anlatan adlar (ana dongu adi degil)
PART_NAMES = ("planlama", "oturum", "resmi", "ev", "fatura", "para", "saglik", "is", "aile", "ulasim", "gunluk", "kesif",
              "m1", "m2", "mahalle", "sozluk", "sayfa", "rota", "mekan", "ek")
TR_ASCII = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")
WORLD_BOX = "-90,90,-180,180"
SOUTH_BOX = "-34.7,-34.5,-58.5,-58.3"  # guney yarikure: kutu '-' ile baslar
OLD_ANSWER_PATH = "data/Yanıtlar.<topic_id>.jsonl"  # yanit-yazari.md'deki eski (gecersiz) yol

CITY, BBOX, DATE = "ornek-sehir", "40.0,41.0,10.0,11.0", "2026-01-15"
SOURCES = {
    "001": "Registration at the town hall costs 25 euro and takes 5 working days. Bring a valid passport.",
    "002": "Museum Square 1, 1234 AB Example City. Open Tuesday to Sunday from 10:00 to 17:00. Adults pay 12 euro.",
    "003": "The North district lies along the river. Bus 5 runs every 10 minutes. The park has a playground. "
           "In an emergency call 112.",
    "004": "The residence card is issued by the immigration office.",
}
PAGE_TEXT = " ".join(["The town hall registers new residents within five days of arrival."] * 12)  # ince degil
PAGE = f"<html><head><title>Kayit</title></head><body><main><p>{PAGE_TEXT}</p></main></body></html>".encode()


# ------------------------------------------------------------------ okuma yardimcilari

def read(name: str) -> str:
    return (AGENTS / f"{name}.md").read_text(encoding="utf-8")


def key_orders(text: str) -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    for match in KEY_BLOCK.finditer(text):
        assert match["sheet"] not in found, f"iki kez: {match['sheet']}"
        found[match["sheet"]] = [k.strip() for k in match["keys"].replace("\n", " ").split(",") if k.strip()]
    return found


def section(text: str, start: str, end: str | None = None) -> str:
    head = text.index(start)
    return text[head:text.index(end, head + len(start))] if end else text[head:]


def placeholder_rows() -> dict[str, str]:
    part = section(read("ortak-kurallar"), "## 1. Yer tutucular", "## 2.")
    return {m[1]: m[2] for m in re.finditer(r"^\| `(<[^`]+>)` \| (.+) \|$", part, re.M)}


def placeholder_table() -> set[str]:
    return set(placeholder_rows())


def substitute(text: str) -> str:
    for name, value in FAKE.items():
        text = text.replace(name, value)
    return text


def fill(template: str, values: dict[str, str]) -> str:
    """Yer tutuculari verilen degerlerle doldurur; dolmadan kalan yer tutucu test hatasidir."""
    for name, value in values.items():
        template = template.replace(name, value)
    assert not PLACEHOLDER.search(template), template
    return template


def json_block_after(text: str, marker: str) -> str:
    return re.search(r"```json\n(?P<body>.+?)\n```", text[text.index(marker):], re.S)["body"]


def generic_json(block: str) -> dict:
    """Ornek JSON satiri; <yer tutucu>lar ornek degere cevrilir, anahtar sirasi korunur."""
    return json.loads(re.sub(r"<[^<>\"]+>", "x", block))


def backticked(line: str) -> list[str]:
    return re.findall(r"`([^`]+)`", line)


def line_starting(text: str, prefix: str) -> str:
    return next(line for line in text.splitlines() if line.startswith(prefix))


def command_args(script: str) -> str:
    found = [m["args"] for m in COMMAND.finditer(read("ortak-kurallar")) if m["script"] == script]
    assert len(found) == 1, (script, found)
    return found[0]


def add_sources_args() -> str:
    return command_args("add_sources")


def agent_subdir_template() -> str:
    return re.search(r"--subdir (\S+)", add_sources_args())[1]


def skill_snaps() -> tuple[set[str], set[str], str]:
    """city-pack SKILL.md (salt okunur): (ana dongu klasor adlari, ana donguye ayrilmis onekler, faz 2 kesif klasoru).
    Ajan klasorunu anlatan adlar (<gorev>/<rol>/<sira>) ana dongu adi sayilmaz."""
    text = SKILL_MD.read_text(encoding="utf-8").translate(TR_ASCII)
    tokens = set(SNAP_TOKEN.findall(text)) - {"snap_"}
    prefixes = {t for t in tokens if t.endswith("_") and "<" not in t}
    names = {t for t in tokens - prefixes if not any(p in t for p in AGENT_SIDE)}
    return names, prefixes, re.search(r"add_sources\.py[^\n]*--subdir (\S+)", text)[1]


def instances(template: str) -> set[str]:
    """Ana dongu klasor kalibinin gercekci ornekleri (<konu>, <ad>, <n> ...: parca adlari ve 1-3)."""
    names = {template}
    for hole in PLACEHOLDER.findall(template):
        names = {n.replace(hole, value, 1) for n in names for value in (*PART_NAMES, "1", "2", "3")}
    return names


def documented_result_path() -> str:
    part = section(read("ortak-kurallar"), "## 4. Kaynaklar", "## 5.")
    return re.search(r"Sonuç `([^`]+\\eklenen\.json)`", part)[1]


def answer_files() -> list[str]:
    part = section(read("ortak-kurallar"), "### Yazacağın dosyalar (yanıt yazarı)", "### Yanıtlar")
    return re.findall(r"`(<WORK>\\_is\\[^`]+\.jsonl)`", part)


def page_table() -> dict[str, tuple[str, str, str]]:
    pattern = (r"^\| `(?P<key>[a-z_]+)` \| (?P<type>Metin|Sayı|Mantıksal|JSON) \| (?P<label>[^|]+) \| "
               r"(?P<body>[^\n]*) \|$")
    return {m["key"]: (m["type"], m["label"].strip(), m["body"]) for m in re.finditer(pattern, read("yer-yazari"), re.M)}


def group_labels() -> dict[str, str]:
    line = line_starting(read("yer-yazari"), "- `place_groups` etiketleri")
    return dict(re.findall(r"(\w+) = ([^,]+?)(?=, \w+ = |\.$)", line.split(":", 1)[1].strip()))


@pytest.fixture(scope="module")
def official() -> dict[str, list[dict]]:
    """Resmi sema (Atinc'in araci, salt okunur): araclar/arac'a __pycache__ yazilmaz, ayar geri yuklenir."""
    spec = importlib.util.spec_from_file_location("resmi_schema_definition", CONTENT / "schema_definition.py")
    module = importlib.util.module_from_spec(spec)
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return {t["sheet"]: [f for f in t["fields"] if not f.get("readonly")] for t in module.TABLES.values()}


@pytest.fixture(scope="module")
def web() -> dict:
    tree = ast.parse((CONTENT / "web_contract.py").read_text(encoding="utf-8"))
    wanted = {"BUDGET_KEYS", "GROUP_KEYS", "TEXT_KEYS", "ARRAY_FIELDS", "URL_KEYS"}
    return {node.targets[0].id: ast.literal_eval(node.value) for node in tree.body
            if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name) and node.targets[0].id in wanted}


# ------------------------------------------------------------------ metin testleri

@pytest.mark.parametrize("name", NEW_FILES)
def test_new_file_is_city_independent_and_compact(name):
    text = read(name)
    leftovers = [token for token in BANNED if token in text.casefold()]
    assert leftovers == [], f"{name}: sehre/ortama ozgu kalinti {leftovers}"
    assert len(text.splitlines()) <= 220, f"{name}: {len(text.splitlines())} satir"


def test_role_files_point_to_common_rules_and_roles_exist():
    for name in ("yer-yazari", "editor"):
        assert "`ortak-kurallar.md`" in read(name)[:1500], name
    assert "`yer-yazari.md`" in read("editor")[:1500]
    assert "iç denetim notu" in read("yer-yazari")[:1500]
    head = read("ortak-kurallar")[:800]
    for role in ("yanit-yazari.md", "mekan-yazari.md", "yer-yazari.md", "editor.md"):
        assert f"`{role}`" in head and (AGENTS / role).is_file(), role


def test_placeholder_table_defines_every_command_placeholder():
    table = placeholder_table()
    assert table == set(FAKE)
    assert {"<city_id>", "<WORK>", "<TK>", "<PY>"} <= table
    for name in NEW_FILES:
        text = read(name)
        for must in ("<city_id>", "<WORK>"):
            assert must in text, f"{name}: {must} yok"
        for match in COMMAND.finditer(text):
            used = set(PLACEHOLDER.findall(match.group(0)))
            assert used <= table, f"{name}: tanimsiz yer tutucu {used - table}"


def test_commands_pass_real_argparse_and_write_only_to_tmp():
    commands = [(name, m["script"], m["args"]) for name in NEW_FILES for m in COMMAND.finditer(read(name))]
    assert {script for _, script, _ in commands} == {"add_sources", "merge_package", "xlsx_dump"}
    tmp = PureWindowsPath(FAKE["<TMP>"])
    for name, script, args in commands:
        argv = substitute(args).split()
        namespace, error = sc.parse_quietly(sc.load_parser(script), argv)
        assert error == "" and namespace is not None, f"{name}: {script} {argv}: {error}"
        if script == "merge_package":
            assert namespace.city_id == FAKE["<city_id>"] and isinstance(namespace.bbox, mp.Box)
            assert PureWindowsPath(namespace.data_out).is_relative_to(tmp), "paylasilan data ezilir"
            assert PureWindowsPath(namespace.out).is_relative_to(tmp), "paylasilan rapor ezilir"
            for box in (WORLD_BOX, SOUTH_BOX):  # '-' ile baslayan kutu secenek sanilmamali (yoksa cikis 2)
                other, problem = sc.parse_quietly(sc.load_parser(script), fill(args, {**FAKE, "<bbox>": box}).split())
                assert problem == "" and other.bbox == mp.parse_bbox(box), f"{name}: --bbox {box}: {problem}"
        if script == "add_sources":
            assert add_sources.SUBDIR_RE.match(namespace.subdir), namespace.subdir
            assert add_sources.TOPIC_RE.match(namespace.topic) and add_sources.CITY_RE.match(namespace.city_id)
            assert PureWindowsPath(namespace.candidates).is_relative_to(tmp)
            # belgedeki sonuc yolu komutun kendi --subdir'inden turemeli (sabit bir paylasilan yol degil)
            produced = PureWindowsPath(namespace.out or PureWindowsPath(namespace.work, namespace.subdir,
                                                                        add_sources.DETAIL_NAME))
            assert PureWindowsPath(substitute(documented_result_path())) == produced
        if script == "xlsx_dump":
            assert PureWindowsPath(namespace.out_dir).is_relative_to(tmp) and namespace.sheets == "Şehir"


def test_agent_snap_folder_is_new_per_run_and_never_shared():
    """eklenen.json her kosuda bastan yazilir: ajan klasoru ana dongununkiyle ve baska rol/kosuyla cakismamali."""
    template, common = agent_subdir_template(), read("ortak-kurallar")
    names, prefixes, discovery = skill_snaps()
    assert "<konu>" in discovery and discovery in names, f"SKILL.md faz 2 kesif klasoru: {discovery}"
    main_loop = set().union(*(instances(name) for name in names))
    owner: dict[str, tuple[str, str, str]] = {}
    for gorev in PART_NAMES:  # yanit yazarinda <gorev> = <konu>: ayni slug iki tarafta da denenir
        for rol in ("yazar", "editor"):
            for sira in ("1", "2", "3"):
                folder = fill(template, {"<gorev>": gorev, "<rol>": rol, "<sira>": sira})
                assert add_sources.SUBDIR_RE.match(folder), folder
                assert folder not in main_loop, f"{folder}: ana dongunun klasoru (eklenen.json ezilir)"
                assert not folder.startswith(tuple(prefixes)), f"{folder}: ana donguye ayrilmis onek {prefixes}"
                assert folder not in owner, f"{folder}: {owner.get(folder)} ile ayni klasor"
                owner[folder] = (gorev, rol, sira)
    sources = section(common, "## 4. Kaynaklar", "## 5.")
    tokens = set(SNAP_TOKEN.findall(sources))
    assert {t for t in tokens if t.endswith("_") and "<" not in t} == prefixes, "ayrilmis onek SKILL.md ile ayni olmali"
    examples = {t for t in tokens if "<" not in t and not t.endswith("_")}
    assert examples and examples <= set(owner), f"ornek klasor adi kaliba uymuyor: {examples - set(owner)}"
    rows = placeholder_rows()
    assert "`yazar`" in rows["<rol>"] and "`editor`" in rows["<rol>"]
    assert "aynı `--subdir`" not in common and "Test-Path" in sources
    assert f"`--subdir {template}`" in read("yer-yazari") and "`<rol>` = `editor`" in read("editor")


def _page_transport(method: str, url: str, headers: object, timeout: float, body_limit: int) -> RawResponse:
    return RawResponse(200, {"Content-Type": "text/html; charset=utf-8"}, PAGE)


def _add_sources(argv: list[str]) -> int:
    return add_sources.main(argv, transport=_page_transport, sleep=lambda _: None, clock=lambda: DATE)


def _eklenen(work: Path, subdir: str) -> dict[str, str]:
    return json.loads((work / subdir / add_sources.DETAIL_NAME).read_text(encoding="utf-8"))["map"]


def test_documented_add_sources_runs_keep_every_eklenen_json(tmp_path):
    """Sahte tasima: kesif + yazar + iki editor kosusu ayni konuda (yanit yazarinda <gorev> = <konu>)."""
    work, konu = tmp_path / "_is", "saglik"
    work.mkdir()
    shared, shared_text = "https://ortak.example/sayfa", work / "ortak.txt"
    shared_text.write_text(PAGE_TEXT, encoding="utf-8")
    _jsonl(work / "kaynak_dizini.jsonl", [{"source_id": f"{CITY}:kaynak:001", "topic": "planlama", "url": shared,
                                          "final_url": shared, "text_file": str(shared_text)}])
    _jsonl(work / "kaynak_taslak.jsonl", [{"source_id": f"{CITY}:kaynak:001", "city_id": CITY, "url": shared}])
    discovery = fill(skill_snaps()[2], {"<konu>": konu})  # SKILL.md faz 2'deki ana dongu komutunun klasoru
    _jsonl(tmp_path / "kesif.jsonl", [{"url": "https://kesif.example/1", "publisher": "Kurum"},
                                      {"url": shared, "publisher": "Kurum"}])  # B3: baska konuda kayitli adres
    assert _add_sources([str(work), "--candidates", str(tmp_path / "kesif.jsonl"), "--subdir", discovery,
                         "--topic", konu, "--city-id", CITY]) == 0
    expected = {discovery: {"https://kesif.example/1": f"{CITY}:kaynak:002", shared: f"{CITY}:kaynak:001"}}
    for number, (rol, sira) in enumerate([("yazar", "1"), ("editor", "1"), ("editor", "2")], start=3):
        values = {"<WORK>": str(tmp_path), "<TMP>": str(tmp_path / f"{rol}_w"), "<gorev>": konu, "<konu>": konu,
                  "<rol>": rol, "<sira>": sira, "<city_id>": CITY}
        argv = fill(add_sources_args(), values).split()
        url = f"https://yeni.example/{rol}{sira}"
        _jsonl(Path(argv[argv.index("--candidates") + 1]), [{"url": url, "publisher": "Kurum"}])
        assert _add_sources(argv) == 0
        expected[argv[argv.index("--subdir") + 1]] = {url: f"{CITY}:kaynak:{number:03d}"}
    assert len(expected) == 4, f"iki kosu ayni klasoru kullandi: {sorted(expected)}"
    assert {subdir: _eklenen(work, subdir) for subdir in expected} == expected
    # kuralin nedeni: kesif klasoru yeniden kullanilinca B3 eslemesi (baska konudan gelen kimlik) silinir
    _jsonl(tmp_path / "tekrar.jsonl", [{"url": "https://yeni.example/tekrar", "publisher": "Kurum"}])
    assert _add_sources([str(work), "--candidates", str(tmp_path / "tekrar.jsonl"), "--subdir", discovery,
                         "--topic", konu, "--city-id", CITY]) == 0
    assert shared not in _eklenen(work, discovery)


@pytest.mark.real
@needs_schema
@pytest.mark.parametrize("name, sheet", [(n, s) for n, sheets in SHEETS_BY_FILE.items() for s in sheets])
def test_key_order_matches_merge_gate_and_official_schema(name, sheet, official):
    documented = key_orders(read(name))[sheet]
    assert documented == mp.SHEETS[sheet], "merge_package kapisi"
    assert documented == [f["key"] for f in official[sheet]], "resmi sema"


def test_each_key_order_is_documented_exactly_once():
    seen = sorted(sheet for name in NEW_FILES for sheet in key_orders(read(name)))
    assert seen == sorted(sheet for sheets in SHEETS_BY_FILE.values() for sheet in sheets)


@pytest.mark.real
@needs_schema
def test_enums_match_gate_and_official_schema(official):
    places = {f["key"]: f for f in official["Mekânlar"]}
    yer, ortak = read("yer-yazari"), read("ortak-kurallar")
    groups = backticked(line_starting(yer, "- `group`:"))[1:]
    settings = backticked(line_starting(yer, "- `setting`:"))[1:]
    assert len(groups) == 8 and set(groups) == mp.GROUPS == set(places["group"]["choices"])
    assert set(settings) == mp.SETTINGS == set(places["setting"]["choices"])
    stages = [v for v in backticked(line_starting(ortak, "- `stages`:"))[1:] if ";" not in v]
    official_stages = next(f for f in official["Yanıtlar"] if f["key"] == "stages")["choices"]
    assert set(stages) == mp.STAGES == set(official_stages)
    assert group_labels() == {key: label for label, key in places["group"]["choice_map"].items()}
    assert "`editorial_status` = `Taslak`" in ortak


@pytest.mark.real
@needs_schema
def test_page_field_table_matches_web_contract_and_gate(web):
    rows = page_table()
    assert len(rows) == 23 and set(rows) == mp.PAGE_KEYS
    assert {k for k, v in rows.items() if v[0] == "JSON"} == set(web["ARRAY_FIELDS"])
    assert {k for k, v in rows.items() if v[0] == "Metin"} == set(web["TEXT_KEYS"]) | set(web["URL_KEYS"]) | {
        "advice_entry"}
    for key, (minimum, fields) in web["ARRAY_FIELDS"].items():
        body = rows[key][2]
        assert [f for f in fields if f'"{f}"' not in body] == [], key
        assert (f"tam şu {minimum} anahtar" if key in ("budget_fields", "place_groups") else f"en az {minimum} ×") in body
    budget = [k for k in backticked(rows["budget_fields"][2]) if re.fullmatch(r"[a-z]+", k)]
    groups = [k for k in backticked(rows["place_groups"][2]) if re.fullmatch(r"[a-z]+", k)]
    assert tuple(budget) == web["BUDGET_KEYS"] and tuple(groups) == web["GROUP_KEYS"]
    assert tuple(group_labels()) == web["GROUP_KEYS"]
    assert "-730..730" in rows["timeline"][2] and r"`^\+?[0-9*#]{2,20}$`" in rows["emergency"][2]
    reserved_sentence = line_starting(read("yer-yazari"), "- Ayrılmış anahtarlar").split(". ")[0]  # 2. cumle Berlin
    assert set(backticked(reserved_sentence)) == mp.RESERVED_PAGE_KEYS


def owner_table() -> dict[str, tuple[str, str]]:
    return {m["sheets"]: (m["key"], m["value"]) for m in re.finditer(
        r"^\| (?P<sheets>[^|`]+?) \| `(?P<key>[a-z_]+)` \| `(?P<value>[^`]+)`",
        section(read("ortak-kurallar"), "## 5.", "## 6."), re.M)}


def test_claim_ledger_example_and_owner_table_match_gate():
    text = read("ortak-kurallar")
    assert list(generic_json(json_block_after(text, "## 5. İddia defteri"))) == LEDGER_KEYS
    owners = owner_table()
    assert {key for key, _ in owners.values()} == set(mp.CLAIM_OWNER_KEYS)
    assert owners["Şehir"] == ("entry_id", "<city_id>")
    assert owners["Adımlar"] == ("entry_id", "<city_id>:<slug>"), "adim iddiasinin sahibi bagli kaydin entry_id'si"
    assert (owners["Sözlük"][0], owners["SayfaAlanları"][0], owners["Rotalar"][0]) == ("term_id", "field_id", "route_id")


def _caught(phrase: str) -> bool:
    return bool(mp.FILLER.search(phrase) or tq.hedge_hits(phrase)
                or any(p.search(tq.normalize(phrase)) for p in tq.EVASIVE))


def test_banned_filler_is_caught_by_gates_and_allowed_step_is_not():
    text = read("ortak-kurallar")
    quoted = re.findall(r'"([^"]+)"', line_starting(text, "2. Okuyucuya iş bırakan"))
    banned, allowed = quoted[:-1], quoted[-1]
    assert len(banned) >= 7
    assert [p for p in banned if not _caught(p)] == [], "kapida yakalanmayan yasak ifade"
    assert not _caught(allowed), f"izinli islem adimi kapiya takiliyor: {allowed}"
    assert [v for v in mp.PLACEHOLDERS if f"`{v}`" not in text.casefold()] == []


def test_internal_note_ban_section_is_complete():
    part = section(read("ortak-kurallar"), "## 7. İç denetim notu yasağı", "## 8.")
    assert "K104" in part and "`gaps`" in part and "`open`" in part and "X'e göre" in part
    assert any("doğrulanamadı" in quote for quote in re.findall(r'"([^"]+)"', part))
    assert "§7" in read("editor")


def test_editor_change_log_matches_pilot_verifier_format():
    text = read("editor")
    row = generic_json(json_block_after(text, "## Değişiklik kaydı"))
    assert list(row) == ["entry_id", "alan", "eski", "yeni", "bulgu_claim_id", "gerekce", "alinti"]
    for must in ("Çelişkide resmî kurum esas", "Kural gözden geçirmesi", "`hatali_duzeltme`", "`eksik_kalan`",
                 "`kural_gozden_gecirme`", "`dogrulama`", "`oneri`"):
        assert must in text, must
    # kaynak cumlesi olmayan mekanik degisiklikte alinti bos, gerekce zorunlu (alinti uydurulmasin)
    quote_rule = line_starting(text, "- `alinti`")
    for must in ("`visual_json`", "`kayit_silindi`", "`iddia_defteri:<claim_id>`", "`gerekce`", "uydurma"):
        assert must in quote_rule, must
    assert "Aynı yetki düzeyindeki iki resmî kurum" in text  # ulusal kurum ile belediye cakismasi kural 2'de


def test_place_rules_keep_plan_coordinates_and_pilot_numbers():
    text = read("yer-yazari")
    line = line_starting(text, "- `latitude`/`longitude`:")
    for must in ("aynı koordinat", "`coord_range`", "değiştirme", "`open`"):
        assert must in line, must
    assert "19'u bu yüzden" not in text and "19 mekân kaynağının 15'i" in text


# ------------------------------------------------------------------ davranis: belgelenen bicim kapidan gecer

def _jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def _rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _row(sheet: str, values: dict) -> dict:
    """Belgelenen anahtar sirasiyla satir (eksik/fazla anahtar = test hatasi)."""
    order = {**key_orders(read("ortak-kurallar")), **key_orders(read("yer-yazari"))}[sheet]
    assert set(values) == set(order), (sheet, set(values) ^ set(order))
    return {key: values[key] for key in order}


def _claim(n: int, owner_key: str, owner: str, sid: str, quote: str, url: str | None = None) -> dict:
    claim = {"claim_id": f"C-ornek-{n}", owner_key: owner, "field": "note", "claim": "ornek iddia", "value": "",
             "unit": "", "period": "", "source_id": sid, "url": url or f"https://ornek.example/{sid[-3:]}",
             "quote": quote}
    return {key: claim[key] for key in [LEDGER_KEYS[0], owner_key, *LEDGER_KEYS[2:]]}


def _common(slug: str, title: str, sid: str, order: int) -> dict:
    return {"entry_id": f"{CITY}:{slug}", "city_id": CITY, "slug": slug, "title": title, "subtitle": "",
            "summary": f"{title} için kısa ve somut özet.", "keywords": "ornek, deneme", "stages": "planning;new",
            "source_ids": f"{CITY}:kaynak:{sid}", "reviewed_on": DATE, "order": order, "featured": "Hayır",
            "editorial_status": "Taslak"}


def _action(slug: str, sid: str) -> dict:
    return _row("Bağlantılar", {"action_id": f"{CITY}:action:{slug}-1", "city_id": CITY, "entry_id": f"{CITY}:{slug}",
                                "label": "Bilgi al", "url": f"https://ornek.example/{sid}", "checked_on": DATE,
                                "order": 1})


def _page_rows() -> list[dict]:
    budget = [k for k in backticked(page_table()["budget_fields"][2]) if re.fullmatch(r"[a-z]+", k)]
    arrays = {
        "facts": [{"value": "25 euro", "label": f"Bilgi {i}", "entry": "kayit-yaptirma"} for i in range(4)],
        "quick_links": [{"label": f"Bağlantı {i}", "entry": "kayit-yaptirma"} for i in range(3)],
        "timeline": [{"title": f"Hatırlatıcı {i}", "note": "Kişisel hatırlatıcı.", "offset": -30 + i,
                      "entry": "kayit-yaptirma"} for i in range(4)],
        "budget_fields": [{"key": key, "label": f"Etiket {key}"} for key in budget],
        "place_groups": [{"key": key, "label": label} for key, label in group_labels().items()],
        "emergency": [{"tel": "112", "number": "112", "label": "Acil yardım", "desc": "Hayati tehlikede ara."}],
    }
    rows = []
    for key, (value_type, label, _) in page_table().items():
        if value_type == "JSON":
            value = json.dumps(arrays[key], ensure_ascii=False)
        elif key in ("emergency_url", "pharmacy_url"):
            value = "https://ornek.example/003"
        else:
            value = "kayit-yaptirma" if key == "advice_entry" else f"Örnek {key} metni."
        rows.append(_row("SayfaAlanları", {"field_id": f"{CITY}:field:{key}", "city_id": CITY, "key": key,
                                           "label": label, "value_type": value_type, "value": value,
                                           "reviewed_on": DATE}))
    return rows


def _city_row() -> dict:
    return _row("Şehir", {
        "city_id": CITY, "name": "Örnek Şehir", "country": "Örnek Ülke", "country_code": "XX", "region": "EU",
        "kind": "city", "title": "Örnek Şehir.", "intro": "Yeni gelenler için kısa giriş.", "currency": "EUR",
        "currency_symbol": "€", "currency_label": "Euro", "language": "Örnekçe", "timezone": "Europe/Berlin",
        "latitude": 40.5, "longitude": 10.5, "coordinate_source_url": "https://ornek.example/koordinat",
        "coordinate_checked_on": DATE, "coordinate_note": "", "source_url": "https://ornek.example/katalog",
        "source_checked_on": DATE, "source_position": 1, "reviewed_on": DATE, "priority": 3, "aliases": "",
        "locality": "", "tagline": "Örnek şehir cümlesi.", "directory_order": "",
        "forecast_url": "https://ornek.example/hava", "provider_url": "https://ornek.example/",
        "forecast_label": "Hava tahmini", "hero_photo_id": "", "editorial_notes": "", "editorial_status": "Taslak"})


@pytest.fixture()
def mini_work(tmp_path: Path) -> Path:
    work = tmp_path / "_is"
    parts = work / "data" / "parcalar"
    index, draft = [], []
    for sid, body in SOURCES.items():
        text_file = work / "snap" / f"{sid}.txt"
        text_file.parent.mkdir(parents=True, exist_ok=True)
        text_file.write_text(body, encoding="utf-8")
        url = f"https://ornek.example/{sid}"
        index.append({"source_id": f"{CITY}:kaynak:{sid}", "url": url, "final_url": url, "title": f"Kaynak {sid}",
                      "publisher": "Örnek kurum", "text_file": str(text_file)})
        draft.append({"source_id": f"{CITY}:kaynak:{sid}", "city_id": CITY, "title": f"Kaynak {sid}",
                      "publisher": "Örnek kurum", "url": url, "checked_on": DATE, "topic": f"{CITY}:genel",
                      "summary": "Deneme kaynağı.", "verified": "Hayır"})
    _jsonl(work / "kaynak_dizini.jsonl", index)
    _jsonl(work / "kaynak_taslak.jsonl", draft)

    answers = [_row("Yanıtlar", {**_common(slug, title, "001", 101 + i), "topic_id": f"{CITY}:genel",
                                 "steps": "Randevu al.\nPasaportunu götür.", "documents": "Geçerli pasaport",
                                 "timing": "5 iş günü", "cost": "25 euro", "note": "", "visual_json": ""})
               for i, (slug, title) in enumerate([("kayit-yaptirma", "Kayıt nasıl yaptırılır?"),
                                                  ("pasaport-getirme", "Kayda hangi belge götürülür?")])]
    places = [_row("Mekânlar", {**_common(f"yer-{i}", f"Örnek Yer {i}", "002", 2001 + i), "group": group,
                                "district": "Merkez", "setting": sorted(mp.SETTINGS)[i % 3],
                                "location": "Museum Square 1, 1234 AB", "latitude": 40.1 + i / 100,
                                "longitude": 10.1 + i / 100, "visit_status": "", "note": "", "collection": "Hayır",
                                "media_key": ""})
              for i, group in enumerate(sorted(mp.GROUPS))]
    compare = json.dumps({"Ulaşım": "Otobüs 5 her 10 dakikada.", "Yaşam ritmi": "Nehir kıyısı sakin.",
                          "Konut tipi": "Apartman daireleri.", "Yeşil alan": "Oyun alanlı park."}, ensure_ascii=False)
    hoods = [_row("Mahalleler", {**_common(f"semt-{i}", f"Örnek Semt {i}", "003", 1301 + i),
                                 "location": "Kuzey bölgesi", "tags": "Nehir kıyısı\nOyun alanı",
                                 "compare_json": compare, "note": "", "media_key": ""}) for i in range(2)]
    terms = [_row("Sözlük", {"term_id": f"{CITY}:term:{n:03d}", "city_id": CITY, "term": f"Terim {n}",
                             "definition": "Göç idaresinin verdiği oturum kartı.", "source_ids": f"{CITY}:kaynak:004",
                             "reviewed_on": DATE, "order": n, "editorial_status": "Taslak"}) for n in (1, 2)]
    stops = places[:3]
    route = _row("Rotalar", {"route_id": f"{CITY}:route:001", "city_id": CITY, "title": "Örnek rota",
                             "tag": "Yarım gün · Kültür", "stops": "\n".join(p["title"] for p in stops),
                             "stop_entry_ids": ";".join(p["entry_id"] for p in stops), "entry_id": stops[0]["entry_id"],
                             "note": "Yürüyüş rotası; müze salıdan pazara açık.", "reviewed_on": DATE,
                             "source_ids": f"{CITY}:kaynak:002", "order": 1, "editorial_status": "Taslak"})

    _jsonl(parts / "Yanıtlar.genel.jsonl", answers)
    _jsonl(parts / "Bağlantılar.genel.jsonl", [_action(a["slug"], "001") for a in answers])
    _jsonl(parts / "Mekânlar.m1.jsonl", places)
    _jsonl(parts / "Bağlantılar.m1.jsonl", [_action(p["slug"], "002") for p in places])
    _jsonl(parts / "Mahalleler.mahalle.jsonl", hoods)
    _jsonl(parts / "Bağlantılar.mahalle.jsonl", [_action(h["slug"], "003") for h in hoods])
    _jsonl(parts / "Sözlük.sozluk.jsonl", terms)
    _jsonl(parts / "SayfaAlanları.sayfa.jsonl", _page_rows())
    _jsonl(parts / "Şehir.sayfa.jsonl", [_city_row()])
    _jsonl(parts / "Rotalar.rota.jsonl", [route])

    claims = work / "claims"
    _jsonl(claims / "genel.jsonl", [_claim(1, "entry_id", f"{CITY}:kayit-yaptirma", f"{CITY}:kaynak:001",
                                           "Registration at the town hall costs 25 euro")])
    _jsonl(claims / "m1.jsonl", [_claim(2, "entry_id", places[0]["entry_id"], f"{CITY}:kaynak:002",
                                        "Open Tuesday to Sunday from 10:00 to 17:00.")])
    _jsonl(claims / "mahalle.jsonl", [_claim(3, "entry_id", hoods[0]["entry_id"], "",  # yalniz url ile
                                             "bus 5 runs every 10 MINUTES.", url="https://ornek.example/003")])
    _jsonl(claims / "sozluk.jsonl", [_claim(4, "term_id", f"{CITY}:term:001", f"{CITY}:kaynak:004",
                                            "issued by the immigration office")])
    _jsonl(claims / "sayfa.jsonl", [
        _claim(5, "field_id", f"{CITY}:field:emergency", f"{CITY}:kaynak:003", "In an emergency call 112."),
        _claim(6, "entry_id", CITY, f"{CITY}:kaynak:003", "The North district lies along the river.")])
    _jsonl(claims / "rota.jsonl", [_claim(7, "route_id", f"{CITY}:route:001", f"{CITY}:kaynak:002",
                                          "Adults pay 12 euro.")])
    return work


def _merge(work: Path, tmp_path: Path, bbox: str = BBOX) -> tuple[int, dict]:
    """Ortak kurallar §8'deki komut AYNEN (yer tutucular dolu): --bbox bicimi ve <TMP> ciktilari belgedeki gibi."""
    argv = fill(command_args("merge_package"), {"<WORK>": str(work.parent), "<city_id>": CITY, "<bbox>": bbox,
                                                "<TMP>": str(tmp_path)}).split()
    report = Path(argv[argv.index("--out") + 1])
    report.unlink(missing_ok=True)  # onceki kosunun raporu yanlislikla okunmasin
    code = mp.main(argv)
    assert code != 2, f"belgelenen komut kullanim hatasi verdi: {argv}"
    return code, json.loads(report.read_text(encoding="utf-8"))


def test_documented_formats_pass_merge_package_cleanly(mini_work, tmp_path):
    code, report = _merge(mini_work, tmp_path)
    assert (report["issues"], report["quote_miss_list"]) == ([], [])
    assert code == 0 and report["claims"] == 7
    assert report["rows"] == {"Yanıtlar": 2, "Mekânlar": 8, "Mahalleler": 2, "Bağlantılar": 12, "Rotalar": 1,
                              "Sözlük": 2, "SayfaAlanları": 23, "Şehir": 1}
    # belgelenen --data-out/--out: paylasilan <is>/data ve <is>/birlestir_rapor.json'a dokunulmaz
    assert not (mini_work / "data" / "Yanıtlar.jsonl").exists() and not (mini_work / "birlestir_rapor.json").exists()
    assert (tmp_path / "birlesik" / "Kaynaklar.jsonl").is_file()


def test_answer_writer_files_are_documented_and_only_they_are_merged(mini_work, tmp_path):
    files = answer_files()
    names = [PureWindowsPath(f).name for f in files]
    assert names == ["Yanıtlar.<gorev>.jsonl", "Bağlantılar.<gorev>.jsonl", "Adımlar.<gorev>.jsonl", "<gorev>.jsonl"]
    parts = mini_work / "data" / "parcalar"
    values = {"<WORK>": str(mini_work.parent), "<gorev>": "genel"}
    assert [Path(fill(f, values)) for f in files] == [parts / "Yanıtlar.genel.jsonl", parts / "Bağlantılar.genel.jsonl",
                                                      parts / "Adımlar.genel.jsonl", mini_work / "claims" / "genel.jsonl"]
    # rol dosyasi eski yolu andikca ortak kurallar onu acikca gecersiz saymali (rol dosyasi duzelince bu kosul duser)
    if f"`{OLD_ANSWER_PATH}`" in read("yanit-yazari"):
        assert f"`{OLD_ANSWER_PATH}`" in section(read("ortak-kurallar"), "### Yazacağın dosyalar (yanıt yazarı)",
                                                 "### Yanıtlar")
    # eski yol ve ':'li parca adi gercekten birlesmez (':' Windows'ta ek akisa yazilir)
    lost = [{**r, "entry_id": f"{CITY}:x-{r['slug']}", "slug": f"x-{r['slug']}", "title": f"X {r['title']}",
             "topic_id": f"{CITY}:genel2"} for r in _rows(parts / "Yanıtlar.genel.jsonl")]
    for path in (mini_work / OLD_ANSWER_PATH.replace("<topic_id>", f"{CITY}:genel2"),
                 parts / f"Yanıtlar.{CITY}:genel2.jsonl"):
        _jsonl(path, lost)
    _, report = _merge(mini_work, tmp_path)
    assert report["per_topic"].get("genel") == 2 and "genel2" not in report["per_topic"]
    # bu yuzden kendi kontrol, raporda kendi satirlarinin okundugunu dogrulatir ("bulgu 0" yetmez)
    final = section(read("ortak-kurallar"), "## 8. Bitirmeden")
    assert "`per_topic.<gorev>`" in final and "`rows.<Sekme>`" in final and r"`<TMP>\birlesik\<Sekme>.jsonl`" in final
    assert "§8" in line_starting(read("editor"), "- Ortak kurallar §8")


def test_step_claims_are_owned_by_the_linked_entry(mini_work, tmp_path):
    steps = [_row("Adımlar", {"step_id": f"{CITY}:step:{n}", "city_id": CITY, "entry_id": f"{CITY}:kayit-yaptirma",
                              "title": f"Adım {n}", "when": "İlk hafta", "description": "Belediyede kayıt yaptır.",
                              "order": n}) for n in range(1, 5)]
    _jsonl(mini_work / "data" / "parcalar" / "Adımlar.genel.jsonl", steps)
    quote, sid = "Registration at the town hall costs 25 euro", f"{CITY}:kaynak:001"
    _jsonl(mini_work / "claims" / "adim.jsonl", [
        _claim(20, *owner_table()["Adımlar"][:1], steps[0]["entry_id"], sid, quote),  # belgelenen sahip
        _claim(21, "step_id", steps[0]["step_id"], sid, quote),
        _claim(22, "entry_id", steps[0]["step_id"], sid, quote)])
    _, report = _merge(mini_work, tmp_path)
    assert report["rows"]["Adımlar"] == 4 and report["issues"] == []
    assert {m[1]: m[2] for m in report["quote_miss_list"]} == {"C-ornek-21": "sahip_yok", "C-ornek-22": "sahip_yok"}


def test_world_box_is_only_for_parts_without_coordinates(mini_work, tmp_path):
    row = placeholder_rows()["<bbox>"]
    for must in (WORLD_BOX, "koordinatsız", "Mekânlar", "Şehir", "`open`", r"`<WORK>\_is\ortam.ps1`"):
        assert must in row, must
    assert "`<bbox>` yoksa" in section(read("ortak-kurallar"), "## 8. Bitirmeden")
    parts = mini_work / "data" / "parcalar"
    places = _rows(parts / "Mekânlar.m1.jsonl")
    swapped = {**places[0], "latitude": places[0]["longitude"], "longitude": places[0]["latitude"]}
    _jsonl(parts / "Mekânlar.m1.jsonl", [swapped, *places[1:]])
    code, report = _merge(mini_work, tmp_path)
    assert code == 1 and report["issue_kinds"] == {"coord_range": 1}
    code, report = _merge(mini_work, tmp_path, bbox=WORLD_BOX)
    assert code == 0 and report["issues"] == []  # dunya kutusu yer degistirmis koordinati hic gostermez


def test_gate_rejects_what_the_docs_forbid(mini_work, tmp_path):
    parts, claims = mini_work / "data" / "parcalar", mini_work / "claims"
    place = _rows(parts / "Mekânlar.m1.jsonl")[0]
    stray = {**place, "entry_id": f"{CITY}:yeni-yer", "slug": "yeni-yer", "title": "Yeni Yer", "latitude": 40.9,
             "longitude": 10.9, "source_ids": "", "source_urls": "https://yeni.example/sayfa"}
    _jsonl(parts / "Mekânlar.m9.jsonl", [stray])
    http_action = {**_action("yeni-yer", "002"), "url": "http://ornek.example/002"}
    _jsonl(parts / "Bağlantılar.m9.jsonl", [http_action])
    _jsonl(claims / "m9.jsonl", [_claim(8, "entry_id", place["entry_id"], f"{CITY}:kaynak:002",
                                        "Adults pay 10 euro.")])  # kaynakta 12 euro: uydurma alinti
    code, report = _merge(mini_work, tmp_path)
    kinds = report["issue_kinds"]
    assert code == 1
    assert {"source_urls_unmapped", "source_ids", "action_url"} <= set(kinds), kinds
    assert [m for m in report["quote_miss_list"] if "alinti_metinde_yok" in m] != []


@pytest.mark.real
@needs_template
def test_city_row_dump_is_as_documented(tmp_path):
    copy = tmp_path / "sablon.xlsx"
    shutil.copyfile(TEMPLATE, copy)
    out = tmp_path / "sablon"
    assert xlsx_dump.main([str(copy), "--out-dir", str(out), "--sheets", "Şehir"]) == 0
    rows = _rows(out / "Şehir.jsonl")
    documented = key_orders(read("yer-yazari"))["Şehir"]
    present = [key for key in rows[0] if key != "_row"]
    assert len(rows) == 1 and "_row" in rows[0]
    assert present == [key for key in documented if key in present], "dokum sirasi belgelenen siradan farkli"
    assert set(present) < set(documented), "dokum yalniz dolu alanlari verir; tam satiri ajan kurar"
    assert len(documented) == 33 and "33 anahtar" in read("yer-yazari")
