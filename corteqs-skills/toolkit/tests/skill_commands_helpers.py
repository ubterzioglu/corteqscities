"""B1 metin-kod uyumu yardimcilari (test_skill_commands.py kullanir).

SKILL.md'deki `& $PY $TK\\<script>.py ...` komutlari PowerShell'in acacagi gibi argv'ye cevrilir ve script'in kendi
argparse'iyla ayristirilir. Script calistirilmaz (parser build_parser()/_parser()'dan ya da main() icindeki parse_args
aninda yakalanir); ag yok, dosya yazilmaz.

- Degiskenler skill basinadir ve SKILL.md'den okunur: 'Sabit yollar' blogundaki `AD = deger` satirlari, metindeki satir
  ici `AD = deger` tanimlari (`WORK =`, `PKG =`, `OUT =`) ve 'Girdi:' satirindaki `AD`'lar. Degerler sahtedir. Skill'in
  tanimlamadigi degisken hatadir: PowerShell onu bos dizeye acar (`--out $OUT\\tq.json` -> `--out \\tq.json`).
- PowerShell modeli bilerek dardir (to_argv); PowerShell'in farkli ayristirdigi yapi sessizce acilmaz, CommandError olur.
- Satir ici anmalar (`claim_check --mode unit`) parser'da olmali. Yalniz secenekli anma (`--mode number`) ayni cumledeki
  onceki script anmasina baglanir; cumlesinde script anmasi olmayan (`--partial` YOK) kapsam disidir.
- argparse'in genel bir iceri bakis API'si yok: ic alanlari (_actions, _SubParsersAction) yalniz subcommands() ve
  option_actions() kullanir.
"""
from __future__ import annotations

import argparse
import contextlib
import importlib
import io
import re
from collections.abc import Callable, Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path, PurePath, PureWindowsPath
from types import MappingProxyType
from unittest import mock

TOOLKIT = Path(__file__).resolve().parent.parent
SCRIPTS = TOOLKIT / "scripts"
REPO_ROOT = TOOLKIT.parent.parent  # SKILL.md'deki ROOT
SKILLS: Mapping[str, Path] = MappingProxyType(
    {name: TOOLKIT.parent / name / "SKILL.md" for name in ("city-pack", "city-audit")})

FAKE_ROOT = r"C:\sahte"
FAKE_PKG = FAKE_ROOT + r"\uretim\sahte-sehir\paket"
PLACEHOLDERS: Mapping[str, str] = MappingProxyType({  # bilerek birakilmis yer tutucular: her biri tek arguman
    "<faz>": "answers",
    "<city_id>": "sahte-sehir",
    "<teslim_adı>": "teslim",
    "<önceki.xlsx>": FAKE_ROOT + r"\onceki.xlsx",
    "<oturum.jsonl>": FAKE_ROOT + r"\oturum.jsonl",
    "<ara Excel'in bulunduğu klasör>": FAKE_PKG,
})
GENERIC_PLACEHOLDER = "sahte-deger"  # bilinmeyen yer tutucu da tek arguman olur
INPUT_VALUES: Mapping[str, str] = MappingProxyType(  # 'Girdi:' ile gelen, tanimi olmayan adlarin sahte degeri
    {"PKG": FAKE_PKG, "XLSX": FAKE_PKG + r"\teslim.xlsx", "LEVEL": "L1"})
REQUIRED_DEFINITIONS = ("ROOT", "PY", "TK", "CHECKS")  # $PY/$TK komut kalibinda acilmadan gecer: tanim sart
READ_ONLY_DESTS = frozenset({"package_root", "workbook", "xlsx"})  # PKG altini gosterebilen salt okunur girdiler
FLOW_OUTPUTS = ("--out", "--out-dir")
FLOW_INPUTS = ("--plan", "--candidates", "--claims", "--snapshots", "--inventory", "--validation",
               "--items", "--selected", "--input", "--urls", "--notes", "--manifest")
AGENT_FILES = frozenset({"items.jsonl", "selected.jsonl", "criteria.json", "urls.txt", "notlar.md", "manifest.json"})

FENCE = re.compile(r"^\s*(?:(?:[-*+]|\d+[.)])\s+)?(?:```|~~~)")  # '2. ```powershell' gibi liste icindeki cit dahil
INLINE = re.compile(r"`([^`\n]+)`")
CODE_OR_STOP = re.compile(r"`(?P<code>[^`\n]+)`|[.!?](?=\s|$)")  # satir ici kod ya da cumle sonu
TK_CALL = re.compile(r"(?P<prefix>&\s*\$PY\s+)?\$TK[\\/](?P<script>[\w.-]+?)\.py(?=\s|$)(?P<args>.*)")
BARE_CALL = re.compile(r"^(?P<script>[A-Za-z_]\w*)\.py\s+(?P<args>\S.*)$")  # satir ici: `impact.py $XLSX --diff ...`
OPTION = r"--[a-z][a-z0-9-]*(?:\s+[^-\s`]\S*)?"  # --secenek [deger]
SCRIPT_MENTION = re.compile(rf"^(?P<script>[a-z_][a-z0-9_]*)(?:\.py)?(?:\s+(?P<sub>[a-z][a-z0-9-]*))?"
                            rf"(?P<words>(?:\s+{OPTION})*)$")
OPTION_MENTION = re.compile(rf"^{OPTION}(?:\s+{OPTION})*$")
PLACEHOLDER = re.compile(r"<[^<>\n]+>")
DEFINITION = re.compile(r"(?P<name>[A-Z][A-Z0-9_]*)\s*=\s*(?P<value>(?:<[^<>\n]+>|[^\s<])+)")
CONSTANTS_HEADING = re.compile(r"^#+\s*Sabit yollar\s*$", re.IGNORECASE)
INPUT_LINE = re.compile(r"Girdi:(?P<rest>.*?)(?:Çıktı:|$)")
NAME = re.compile(r"[A-Z][A-Z0-9_]*")
# PowerShell (7.6'da denendi): kelime parcalari, degisken ve ozel sozdizimi
TOKEN = re.compile(r"""(?P<single>'[^']*')|(?P<double>"[^"]*")|(?P<bare>[^\s'";|]+)|(?P<space>\s+)|(?P<bad>.)""")
VARIABLE = re.compile(r"\$(?:\{(?P<braced>[^}]+)\}|(?P<name>[A-Za-z_]\w*))")
LEADING_VARIABLE = re.compile(r"^\$(?:\{[^}]*\}|[A-Za-z_]\w*)")
SAFE_AFTER_VARIABLE = ("", "\\", "/", "-")  # kelime basindaki $AD'dan sonra duz metin sayilanlar
WORD_START_SYNTAX = re.compile(r"^(?:@|--%$)")  # dizi/sozluk/splat, ayristirmayi durdur
PART_SYNTAX: Mapping[str, re.Pattern[str]] = MappingProxyType({
    "bare": re.compile(r"[(){}&<>`]|\$\(|\$[\d?^$]|\$[A-Za-z_]\w*:"),  # komut, betik blogu, yonlendirme, $(...)
    "double": re.compile(r"`|\$\(|\$[\d?^$]|\$[A-Za-z_]\w*:"),
})


class CommandError(ValueError):
    """SKILL.md komutu PowerShell olarak ayristirilamadi."""


@dataclass(frozen=True)
class Command:
    skill: str
    line: int
    script: str     # uzantisiz ad: 'build_xlsx'
    kind: str       # 'tk': $TK\x.py ... ; 'bare': satir ici kisa yazim `x.py arg ...`
    prefixed: bool  # '& $PY ' ile basliyor mu
    args: str       # '.py' sonrasi ham metin (yer tutucular dahil)
    text: str       # rapor icin ham komut

    @property
    def id(self) -> str:
        return f"{self.skill}:L{self.line}:{self.script}"


def _lines(text: str) -> Iterator[tuple[int, str, bool]]:
    """(satir no, satir, kod blogunda mi); cit satirlari atlanir."""
    in_block = False
    for number, line in enumerate(text.splitlines(), start=1):
        if FENCE.match(line):
            in_block = not in_block
            continue
        yield number, line, in_block


def _is_script(name: str) -> bool:
    return (SCRIPTS / f"{name}.py").is_file()


def extract_commands(skill: str, text: str) -> list[Command]:
    """Kod bloklarindaki satirlar ve blok disindaki satir ici `...` parcalari icindeki toolkit cagrilari."""
    commands: list[Command] = []
    for number, line, in_block in _lines(text):
        for piece in [line] if in_block else INLINE.findall(line):
            commands.extend(_calls(skill, number, piece.strip(), inline=not in_block))
    return commands


def _calls(skill: str, line: int, piece: str, inline: bool) -> list[Command]:
    found = []
    for match in TK_CALL.finditer(piece):
        found.append(Command(skill, line, match["script"], "tk", bool(match["prefix"]), match["args"],
                             match.group(0).strip()))
    bare = BARE_CALL.match(piece) if inline and not found else None
    if bare:
        found.append(Command(skill, line, bare["script"], "bare", False, bare["args"], piece))
    return found


# --- SKILL.md tanimlari: degiskenler ve sabit yollar ---

def _constant_lines(text: str) -> list[str]:
    """'Sabit yollar' basligindan sonraki ilk kod blogunun satirlari (baslik ya da blok yoksa bos)."""
    lines = text.splitlines()
    starts = [index for index, line in enumerate(lines) if CONSTANTS_HEADING.match(line.strip())]
    block: list[str] = []
    inside = False
    for line in lines[starts[0] + 1:] if starts else []:
        if FENCE.match(line):
            if inside:
                break
            inside = True
        elif inside:
            block.append(line)
        elif line.startswith("#"):
            break
    return block


def definitions(text: str) -> dict[str, str]:
    """Ham tanimlar: 'Sabit yollar' blogundaki `AD = deger` satirlari + metindeki satir ici `AD = deger` parcalari."""
    found: dict[str, str] = {}
    for line in _constant_lines(text):
        match = DEFINITION.match(line.strip())
        if match:
            found[match["name"]] = match["value"]
    for _, line, in_block in _lines(text):
        for piece in [] if in_block else INLINE.findall(line):
            match = DEFINITION.fullmatch(piece.strip())
            if match:
                found.setdefault(match["name"], match["value"])
    return found


def input_names(text: str) -> list[str]:
    """'Girdi:' satirinda ('Çıktı:'ya kadar) `AD` olarak anilan degiskenler."""
    names: list[str] = []
    for _, line, in_block in _lines(text):
        match = None if in_block else INPUT_LINE.search(line)
        pieces = INLINE.findall(match["rest"]) if match else []
        names.extend(piece.strip() for piece in pieces if NAME.fullmatch(piece.strip()))
    return names


def skill_variables(text: str) -> Mapping[str, str]:
    """SKILL.md'nin tanimladigi her degisken -> sahte deger. ROOT sahte koke gider, `AD\\...` onceki tanimdan acilir,
    yer tutucu sahte degere doner; yalniz 'Girdi:'de anilan adlar INPUT_VALUES'tan gelir."""
    values: dict[str, str] = {}
    for name, raw in definitions(text).items():
        values[name] = _fake_value(name, raw, values)
    for name in input_names(text):
        values.setdefault(name, INPUT_VALUES.get(name, f"{FAKE_ROOT}\\girdi\\{name.lower()}"))
    return MappingProxyType(values)


def _fake_value(name: str, raw: str, known: Mapping[str, str]) -> str:
    if re.match(r"^[A-Za-z]:\\", raw):  # gercek mutlak yol (ROOT)
        return FAKE_ROOT if name == "ROOT" else f"{FAKE_ROOT}\\{name.lower()}"
    head, sep, rest = raw.partition("\\")
    value = known[head] + sep + rest if head in known else raw
    return PLACEHOLDER.sub(_placeholder_value, value).rstrip("\\")


def _placeholder_value(match: re.Match[str]) -> str:
    return PLACEHOLDERS.get(match.group(0), GENERIC_PLACEHOLDER)


def path_problems(skill: str, text: str) -> list[str]:
    """'Sabit yollar' depoyla tutarli mi: zorunlu adlar tanimli, TK = ROOT\\<toolkit\\scripts>, depo icindeki her yol
    (ROOT\\corteqs-skills\\..., <bu skill>\\...) diskte var. Depo disi yollar (.venv, araclar, uretim) ortama bagli."""
    raw = definitions(text)
    problems = [f"{skill}: '{name} = ...' tanimi yok" for name in REQUIRED_DEFINITIONS if name not in raw]
    expected_tk = PureWindowsPath("ROOT", SCRIPTS.relative_to(REPO_ROOT))
    if "TK" in raw and PureWindowsPath(raw["TK"]) != expected_tk:
        problems.append(f"{skill}: TK = {raw['TK']} (beklenen {expected_tk})")
    for name, value in raw.items():
        target = _repo_target(skill, value)
        if target is not None and not target.exists():
            problems.append(f"{skill}: {name} = {value} -> {target} yok")
    return problems


def _repo_target(skill: str, value: str) -> Path | None:
    """Depo icindeki yolun diskteki karsiligi; depo disi yol icin None."""
    parts = PureWindowsPath(value).parts
    if parts[:1] == ("<bu skill>",):
        return SKILLS[skill].parent.joinpath(*parts[1:])
    if len(parts) > 1 and parts[0] == "ROOT" and parts[1].lower() == TOOLKIT.parent.name.lower():
        return REPO_ROOT.joinpath(*parts[1:])
    return None


# --- PowerShell arguman metni -> argv ---

def _expand(text: str, variables: Mapping[str, str]) -> str:
    """$AD / ${AD} -> sahte deger (PowerShell gibi buyuk-kucuk harf duyarsiz); tanimsiz ad hatadir."""
    known = {name.upper(): value for name, value in variables.items()}

    def value(match: re.Match[str]) -> str:
        name = match["braced"] or match["name"]
        if name.upper() not in known:
            raise CommandError(f"tanimsiz degisken ${name} (PowerShell bos dizeye acar)")
        return known[name.upper()]

    return VARIABLE.sub(value, text)


def _syntax_problem(parts: Sequence[tuple[str, str]]) -> str | None:
    """Kelimede PowerShell'in duz metin gibi acmadigi yapi varsa nedeni (ornekler PowerShell 7.6'da denendi)."""
    kinds = [kind for kind, _ in parts]
    first_kind, first = parts[0]
    if first_kind != "bare" and len(parts) > 1:
        return "tirnakla baslayan kelime devam ediyor (\"a\"b iki arguman, 'a'.Length uye erisimi)"
    if any(left != "bare" and right != "bare" for left, right in zip(kinds, kinds[1:])):
        return "bitisik tirnaklar (\"a\"\"b\" -> a\"b)"
    if first_kind == "bare" and WORD_START_SYNTAX.match(first):
        return f"kelime basinda {first[:3]!r} (dizi/sozluk/splat ya da --%)"
    leading = LEADING_VARIABLE.match(first) if first_kind == "bare" else None
    if leading:
        rest = first[leading.end():]
        follow = rest[:1] if rest else (parts[1][1][:1] if len(parts) > 1 else "")
        if follow not in SAFE_AFTER_VARIABLE:
            return f"degiskenden hemen sonra {follow!r} ($PKG.xlsx arguman duser, $PKG[0] dizin, $PKG=x bolunur)"
    for kind, raw in parts:
        found = PART_SYNTAX[kind].search(raw) if kind in PART_SYNTAX else None
        if found:
            return f"{found.group()!r} (komut, betik blogu, yonlendirme, $(...) ya da surucu nitelikli degisken)"
    bare_text = "".join(raw for kind, raw in parts if kind == "bare")
    if "," in bare_text and ("$" in "".join(raw for _, raw in parts) or len(parts) > 1):
        return "virgul + degisken/tirnak (dizi sayilir, $PKG,x acilmaz)"
    return None


def _word(parts: Sequence[tuple[str, str]], variables: Mapping[str, str], source: str) -> str:
    problem = _syntax_problem(parts)
    if problem:
        raise CommandError(f"desteklenmeyen PowerShell sozdizimi: {problem}: {source.strip()}")
    pieces = []
    for kind, raw in parts:
        if kind == "single":
            pieces.append(raw[1:-1])
        elif kind == "double":
            pieces.append(_expand(raw[1:-1], variables))
        else:
            pieces.append(_expand(raw, variables))
    return "".join(pieces)


def to_argv(args: str, variables: Mapping[str, str]) -> list[str]:
    """PowerShell arguman metni -> argv. Modellenen: duz kelime, '...' (acilmaz), "..." ($AD/${AD} acilir), kelime
    icinde tirnak birlestirme (a"b c"d), <yer tutucu> (tek arguman), kelime basindaki '#' (yorum). Geri kalani acik
    CommandError: ; | & ( ) { } < > ` $(...) @... --% , kelime basindaki $AD'dan sonra . [ : = , tirnakla baslayip
    devam eden kelime, bitisik tirnaklar, virgul + degisken, kapanmamis tirnak, tanimsiz degisken."""
    text = PLACEHOLDER.sub(_placeholder_value, args)
    argv: list[str] = []
    parts: list[tuple[str, str]] = []
    for match in TOKEN.finditer(text + " "):
        kind, raw = match.lastgroup or "bad", match.group()
        if kind == "bad":
            raise CommandError(f"desteklenmeyen PowerShell sozdizimi ({raw!r}): {args.strip()}")
        if kind == "bare" and not parts and raw.startswith("#"):
            break
        if kind != "space":
            parts.append((kind, raw))
        elif parts:
            argv.append(_word(parts, variables, args))
            parts = []
    return argv


# --- toolkit parser'lari ---

class _Captured(BaseException):
    """main() icindeki parser'i parse_args aninda yakalar; BaseException: main'deki 'except Exception' yutamaz."""

    def __init__(self, parser: argparse.ArgumentParser) -> None:
        super().__init__()
        self.parser = parser


def parser_from_main(main: Callable[[list[str]], object]) -> argparse.ArgumentParser | None:
    """main([]) icinde kurulan parser'i ilk parse_args/parse_known_args aninda yakalar; main'in geri kalani calismaz."""
    def capture(self: argparse.ArgumentParser, *_: object, **__: object) -> None:
        raise _Captured(self)

    with mock.patch.object(argparse.ArgumentParser, "parse_args", capture), \
            mock.patch.object(argparse.ArgumentParser, "parse_known_args", capture):
        try:
            main([])
        except _Captured as captured:
            return captured.parser
    return None


def load_parser(script: str) -> argparse.ArgumentParser:
    """Toolkit script'inin parser'i (build_parser()/_parser(), yoksa main() icindeki argparse). Kisaltma kapalidir:
    `--per-shee` bugun `--per-sheet` sayilir ama ayni onekli yeni secenek gelince komut kirilir."""
    module = importlib.import_module(script)
    if Path(getattr(module, "__file__", "") or "").resolve() != (SCRIPTS / f"{script}.py").resolve():
        raise CommandError(f"{script}: toolkit disi modul yuklendi ({getattr(module, '__file__', None)})")
    parser = None
    for name in ("build_parser", "_parser"):
        factory = getattr(module, name, None)
        if parser is None and callable(factory):
            parser = factory()
    main = getattr(module, "main", None)
    if parser is None and callable(main):
        parser = parser_from_main(main)
    if parser is None:
        raise CommandError(f"{script}: parser bulunamadi (build_parser/_parser yok, main argparse'a ulasmadi)")
    for each in (parser, *subcommands(parser).values()):  # her cagrida yeni kurulan, yalniz bize ait parser'lar
        each.allow_abbrev = False
    return parser


def subcommands(parser: argparse.ArgumentParser) -> dict[str, argparse.ArgumentParser]:
    """Alt komut adi -> alt parser."""
    found: dict[str, argparse.ArgumentParser] = {}
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            found.update(action.choices)
    return found


def option_actions(parsers: Iterable[argparse.ArgumentParser]) -> dict[str, argparse.Action]:
    """'--secenek' -> argparse Action (verilen parser'larin hepsinden)."""
    found: dict[str, argparse.Action] = {}
    for parser in parsers:
        for action in parser._actions:
            found.update(dict.fromkeys(action.option_strings, action))
    return found


def parse_quietly(parser: argparse.ArgumentParser, argv: list[str]) -> tuple[argparse.Namespace | None, str]:
    """(namespace, '') ya da (None, argparse hata satiri); usage/hata metni yakalanir."""
    err = io.StringIO()
    try:
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
            return parser.parse_args(argv), ""
    except SystemExit as stop:
        lines = err.getvalue().strip().splitlines()
        return None, lines[-1] if lines else f"SystemExit({stop.code})"
    except argparse.ArgumentError as exc:  # exit_on_error=False olan parser
        return None, str(exc)


def check_command(command: Command, variables: Mapping[str, str]) -> tuple[argparse.Namespace | None, list[str]]:
    """Komutun sorunlari: script toolkit'te yok, '& $PY' eksik, PowerShell/argparse hatasi. Bos liste = uyumlu."""
    where = f"{command.id}: {command.text}"
    if not _is_script(command.script):
        return None, [f"{where}\n  -> toolkit'te yok: scripts/{command.script}.py"]
    problems = []
    if command.kind == "tk" and not command.prefixed:
        problems.append(f"{where}\n  -> '& $PY $TK\\<script>.py' bicimi degil (PowerShell bu satiri calistiramaz)")
    try:
        argv = to_argv(command.args, variables)
        parser = load_parser(command.script)
    except CommandError as exc:
        return None, [*problems, f"{where}\n  -> {exc}"]
    namespace, error = parse_quietly(parser, argv)
    if error:
        problems.append(f"{where}\n  -> argparse: {error}\n  argv: {argv}")
    return namespace, problems


def help_problems(script: str) -> list[str]:
    """'--help' ve her alt komut icin '<alt> --help' 0 ile cikmali (ornek hata: yardim metninde kacissiz '%')."""
    parser = load_parser(script)
    problems = []
    for argv in [["--help"], *([name, "--help"] for name in subcommands(parser))]:
        out = io.StringIO()
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
                parser.parse_args(argv)
            problems.append(f"{script} {' '.join(argv)}: cikmadi")
        except SystemExit as stop:
            if stop.code not in (0, None) or "usage:" not in out.getvalue():
                problems.append(f"{script} {' '.join(argv)}: cikis {stop.code}")
        except Exception as exc:  # noqa: BLE001 - yardim bicimleme hatasi da bulgu
            problems.append(f"{script} {' '.join(argv)}: {type(exc).__name__}: {exc}")
    return problems


# --- satir ici anmalar ---

def option_mentions(skill: str, text: str) -> list[tuple[str, str, list[str]]]:
    """Kod blogu disindaki anmalar -> (konum, script, sozcukler): `claim_check --mode unit`, `phase_usage report
    --subagents`. Yalniz secenekli anma ayni cumledeki onceki script anmasina (`build_xlsx`, `inventory.py`,
    `impact.py $XLSX ...` dahil) baglanir; cumlesinde script anmasi olmayan yalniz secenekli anma kapsam disidir."""
    found = []
    for number, line, in_block in _lines(text):
        context: tuple[str, list[str]] | None = None  # (script, [alt komut])
        for match in [] if in_block else CODE_OR_STOP.finditer(line):
            piece = (match["code"] or "").strip()
            if not piece:
                context = None  # cumle sonu
                continue
            mention = SCRIPT_MENTION.match(piece)
            if mention and _is_script(mention["script"]):
                context = (mention["script"], [mention["sub"]] if mention["sub"] else [])
                words = context[1] + mention["words"].split()
                if words:
                    found.append((f"{skill}:L{number}", context[0], words))
            elif OPTION_MENTION.match(piece) and context:
                found.append((f"{skill}:L{number}", context[0], context[1] + piece.split()))
            else:
                context = _call_context(piece) or context
    return found


def _call_context(piece: str) -> tuple[str, list[str]] | None:
    call = TK_CALL.search(piece) or BARE_CALL.match(piece)
    return (call["script"], []) if call and _is_script(call["script"]) else None


def mention_problems(script: str, words: list[str]) -> list[str]:
    """Anilan alt komut parser'da olmali; her --secenek ana parser'da ya da anilan alt komutta (alt komut anilmadiysa
    herhangi birinde) olmali; choices'li secenegin degeri gecerli olmali."""
    parser = load_parser(script)
    subs = subcommands(parser)
    named = words[0] if words and not words[0].startswith("--") else None
    problems = []
    if named is not None and subs and named not in subs:
        problems.append(f"{script}: '{named}' alt komutu yok (alt komutlar: {sorted(subs)})")
    actions = option_actions([parser, subs[named]] if named in subs else [parser, *subs.values()])
    scope = f"'{named}' alt komutunda" if named in subs else "parser'da"
    for word, nxt in zip(words, [*words[1:], None]):
        action = actions.get(word) if word.startswith("--") else None
        if word.startswith("--") and action is None:
            problems.append(f"{script}: '{word}' secenegi {scope} yok")
        elif action is not None and action.choices and nxt and not nxt.startswith("--") \
                and nxt not in {str(choice) for choice in action.choices}:
            problems.append(f"{script} {word}: '{nxt}' gecersiz (secenekler: {sorted(map(str, action.choices))})")
    return problems


# --- paket ve ara dosya akisi ---

def package_writes(command: Command, namespace: argparse.Namespace, package: PureWindowsPath) -> list[str]:
    """PKG altina dusen her argparse degeri; yalniz READ_ONLY_DESTS (paket koku, teslim Excel'i) okuma sayilir."""
    found = []
    for dest, value in sorted(vars(namespace).items()):
        if dest in READ_ONLY_DESTS:
            continue
        for path in _path_values(value):
            if PureWindowsPath(path).is_relative_to(package):
                found.append(f"{command.id} {dest}={path}")
    return found


def _path_values(value: object) -> list[str]:
    items = value if isinstance(value, (list, tuple)) else [value]
    return [str(item) for item in items if isinstance(item, (str, PurePath))]


def flow_problems(commands: Sequence[Command], variables: Mapping[str, str]) -> list[str]:
    """Ara dosya zinciri: FLOW_INPUTS girdisi daha onceki bir komutun --out/--out-dir ciktisi ya da ajanin urettigi
    dosya (AGENT_FILES) olmali. PowerShell'e cevrilemeyen komut atlanir; onu check_command raporlar."""
    produced: set[PureWindowsPath] = set()
    problems = []
    for command in sorted(commands, key=lambda c: c.line):
        try:
            argv = to_argv(command.args, variables)
        except CommandError:
            continue
        for option, value in _option_values(argv, FLOW_INPUTS):
            path = PureWindowsPath(value)
            if path not in produced and path.name.lower() not in AGENT_FILES:
                problems.append(f"{command.id}: {option} {value} -> onceki hicbir komutun --out/--out-dir ciktisi "
                                f"degil (ajan dosyasi da degil: {sorted(AGENT_FILES)})")
        produced |= {PureWindowsPath(value) for _, value in _option_values(argv, FLOW_OUTPUTS)}
    return problems


def _option_values(argv: Sequence[str], options: Sequence[str]) -> list[tuple[str, str]]:
    """argv'deki `--secenek deger` ve `--secenek=deger` ciftleri (yalniz istenen secenekler)."""
    found = []
    for index, token in enumerate(argv):
        name, sep, value = token.partition("=")
        if name in options and sep:
            found.append((name, value))
        elif name in options and index + 1 < len(argv):
            found.append((name, argv[index + 1]))
    return found
