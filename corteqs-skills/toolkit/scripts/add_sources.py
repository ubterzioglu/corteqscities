"""Yeni kaynak adreslerini alt klasore kopyalar, must_contain kanitini arar, gecenlere kaynak kimligi verir (A6; pilot: kaynak_ekle.py).

Kullanim:
  add_sources.py <is_klasoru> --candidates aday.jsonl --subdir snap_ek --topic kesif --city-id eindhoven
                 [--cache-dir <is>/cache] [--no-retry-transient] [--out <is>/<subdir>/eklenen.json]
aday.jsonl satiri: {"url", "must_contain": ["..."], "title", "publisher", "lang", "why"}
- fetch_snapshot surec icinde <is>/<subdir>'e calisir. --subdir 'snap_<ad>' olmali: ana snap/ klasorune ve onun
  index.jsonl'ine dokunulmaz.
- Kabul: kopya var, ince degil, soft-404 degil (200 donen 'sayfa yok' sayfasi; fetch_snapshot soft_404 bayragi) ve
  her must_contain ifadesi metinde (NFKC + bosluk + harf buyuklugu normalize). must_contain bossa yalniz kopya
  sartlari aranir; tek metin verilirse tek ifade sayilir.
- Gecen yeni adresler <is>/kaynak_dizini.jsonl ve <is>/kaynak_taslak.jsonl sonuna eklenir (eski satirlar bayt bayt
  korunur, ikili kip: dosya LF ise LF, CRLF ise CRLF kalir): kimlik <sehir>:kaynak:NNN, sehrin en buyuk numarasindan
  devam. Adres zaten kayitliysa mevcut kimlik kullanilir (dizine yeni satir yok); o kimligin taslak satiri yoksa
  (onceki kosu dizine yazip taslaga yazamadiysa) satir dizin satirindan kurulup taslaga eklenir (ozette
  draft_repaired). Dizin ve taslak indirmeden SONRA <is>/kaynak_dizini.lock kilidi altinda yeniden okunur: paralel
  calisan editorler ayni kimligi almaz. Kilit isletim sistemi dosya kilididir (Windows msvcrt, POSIX flock): sahibi
  yasadikca devralinmaz, kosu cokerse kendiliginden birakilir; kilit dosyasi silinmez (silmek baska surecin kilidini
  silme yarisini dogurur).
- Iki dosya birlikte degisir: once dizin, sonra taslak yazilir; taslak yazilamazsa (kalici kilit, disk hatasi,
  Ctrl+C) dizin eski baytlarina doner. Windows'ta dosya baska programda kisa sure acikken (antivirus, dizinleyici,
  Excel) yer degistirme (os.replace) PermissionError verir: 5 kez denenir (aralarda 0,1-0,5 sn); yine olmazsa cikis 2
  ve mesaj iki dosyanin son durumunu soyler. Geri alma da olmazsa mesaj dizinde kalan kimlikleri verir: ayni
  adaylarla yeniden kosu yeni kimlik vermez, eksik taslak satirini ekler.
- Onbellekteki gecici hatalar (429/5xx/ag) varsayilan olarak yeniden indirilir; --no-retry-transient: yalniz onbellek.
stdout tek satir JSON; --out: {map: {url: source_id}, rejected: [{url, why}], fetch: fetch_snapshot ozeti}.
cikis 0 hepsi gecti / 1 reddedilen var / 2 kullanim (okunamayan girdi, UTF-8 olmayan JSONL, yazilamayan cikti dahil).
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import re
import sys
import time
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterator

import fetch_snapshot
from common import EXIT_FINDINGS, EXIT_OK, EXIT_USAGE, emit, setup_utf8, write_json
from web_fetch import Transport, urllib_transport, utc_today

CITY_RE = re.compile(r"^[a-z0-9-]+\Z")
TOPIC_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*\Z")
SUBDIR_RE = re.compile(r"^snap_[A-Za-z0-9_-]+\Z")
INDEX_NAME = "kaynak_dizini.jsonl"
DRAFT_NAME = "kaynak_taslak.jsonl"
DETAIL_NAME = "eklenen.json"
LOCK_NAME = "kaynak_dizini.lock"
LOCK_TIMEOUT_SECONDS = 60.0  # kilitli bolum milisaniyeler surer; bu kadar bekleten kosu canli ve takilmis demektir
LOCK_POLL_SECONDS = 0.2
REPLACE_WAITS = (0.1, 0.2, 0.4, 0.5)  # erisim reddedilen os.replace denemeleri arasi: 5 deneme, en cok 1,2 sn
UNCHANGED = f"{INDEX_NAME} ve {DRAFT_NAME} kosudan onceki gibi"  # hata mesajinda iki dosyanin durumu
TITLE_MAX = 180
PUBLISHER_MAX = 120

if os.name == "nt":
    import msvcrt

    def _try_lock(descriptor: int) -> bool:
        """Dosyanin ilk baytina beklemesiz ozel kilit (Windows: tutamaca bagli, surec olunce birakilir)."""
        os.lseek(descriptor, 0, os.SEEK_SET)
        try:
            msvcrt.locking(descriptor, msvcrt.LK_NBLCK, 1)
        except OSError:
            return False
        return True

    def _unlock(descriptor: int) -> None:
        os.lseek(descriptor, 0, os.SEEK_SET)
        msvcrt.locking(descriptor, msvcrt.LK_UNLCK, 1)
else:  # pragma: no cover - POSIX; testler Windows'ta kosuyor
    import fcntl

    def _try_lock(descriptor: int) -> bool:
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            return False
        return True

    def _unlock(descriptor: int) -> None:
        fcntl.flock(descriptor, fcntl.LOCK_UN)


class UsageError(Exception):
    """Eksik/bozuk girdi ya da gecersiz arguman (cikis 2)."""


@dataclass(frozen=True)
class Job:
    work: Path
    out_dir: Path
    subdir: str
    topic: str
    city: str


@dataclass(frozen=True)
class Registration:
    added: dict[str, str]
    reused: dict[str, str]
    repaired: dict[str, str]  # reused'un taslak satiri eksik olanlari: satir dizin satirindan kuruldu
    rejected: list[dict[str, str]]
    index_rows: list[dict[str, Any]]
    draft_rows: list[dict[str, Any]]


def norm(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    return re.sub(r"\s+", " ", text).strip().casefold()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    try:
        with Path(path).open(encoding="utf-8-sig") as stream:
            for number, line in enumerate(stream, 1):
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError as error:
                    raise UsageError(f"{path}:{number}: gecersiz JSON ({error.msg})") from error
                if not isinstance(row, dict):
                    raise UsageError(f"{path}:{number}: nesne bekleniyor")
                rows.append(row)
    except UnicodeDecodeError as error:
        raise UsageError(f"{path}: UTF-8 degil ({error.reason})") from error
    return rows


@contextlib.contextmanager
def index_lock(work: Path, sleep: Callable[[float], None]) -> Iterator[None]:
    """Surecler arasi kilit: paralel editorler (B6) ayni kaynak kimligini almasin, birbirinin satirini ezmesin.

    Isletim sistemi kilidi oldugu icin 'bayat kilit' sezgisi ve devralma yok: canli sahip hic devre disi kalmaz, coken
    surecin kilidi kendiliginden birakilir. Dosya silinmez; her surec yalniz kendi tutamacinin kilidini acar."""
    lock = work / LOCK_NAME
    descriptor = os.open(lock, os.O_RDWR | os.O_CREAT, 0o644)
    try:
        deadline = time.monotonic() + LOCK_TIMEOUT_SECONDS
        while not _try_lock(descriptor):
            if time.monotonic() >= deadline:
                raise UsageError(f"kilit alinamadi: {lock} (baska add_sources kosusu suruyor)")
            sleep(LOCK_POLL_SECONDS)
        try:
            yield
        finally:
            _unlock(descriptor)
    finally:
        os.close(descriptor)


def _newline(data: bytes) -> bytes:
    """Dosyanin satir sonu (ilk satira gore: CRLF ya da LF); satir sonu yoksa LF."""
    end = data.find(b"\n")
    return b"\r\n" if end > 0 and data[end - 1:end] == b"\r" else b"\n"


def replace_retrying(source: Path, target: Path) -> None:
    """os.replace; Windows'ta dosya baska programda kisa sure acikken (antivirus, dizinleyici, Excel) gelen
    PermissionError (WinError 5: hedef acik, 32: kaynak acik) REPLACE_WAITS aralariyla yeniden denenir. Bekleme gercek
    zamanlidir (time.sleep): main'e verilen sleep testlerde bostur ve kilidi gecirmez. Son deneme de reddedilirse acik
    mesajli UsageError (cikis 2), hedef degismez; baska OSError beklemeden yukari gider."""
    for delay in REPLACE_WAITS:
        with contextlib.suppress(PermissionError):
            os.replace(source, target)
            return
        time.sleep(delay)
    try:
        os.replace(source, target)
    except PermissionError as error:
        raise UsageError(f"{target} yazilamadi: {len(REPLACE_WAITS) + 1} denemede de erisim reddedildi "
                         f"({error.strerror or error}); dosya baska programda acik olabilir (Excel, antivirus, "
                         "dizinleyici)") from error


def appended(old: bytes, rows: list[dict[str, Any]]) -> bytes:
    """Eski icerik bayt bayt korunur (ikili kip); yeni satirlar dosyanin satir sonuyla eklenir."""
    newline = _newline(old)
    if old and not old.endswith(b"\n"):
        old += newline
    return old + b"".join(json.dumps(r, ensure_ascii=False).encode("utf-8") + newline for r in rows)


def write_atomic(path: Path, data: bytes) -> None:
    """Gecici dosya + os.replace: yarim yazim olmaz, kilitli dosyada kisa yeniden deneme. Hata olursa hedef degismez,
    gecici dosya kalmaz."""
    temporary = path.with_name(path.name + ".tmp")
    try:
        temporary.write_bytes(data)
        replace_retrying(temporary, path)
    finally:
        with contextlib.suppress(OSError):  # basarida zaten tasindi; asil hata (varsa) yukari gider
            temporary.unlink(missing_ok=True)


def undo_index(index: Path, before: bytes, rows: list[dict[str, Any]]) -> str:
    """Taslak yazilamayinca dizini eski baytlarina dondurur; iki dosyanin son durumunu anlatan metni verir."""
    try:
        write_atomic(index, before)
    except (UsageError, OSError) as error:
        ids = ", ".join(str(r.get("source_id")) for r in rows)
        return (f"{DRAFT_NAME} degismedi; {INDEX_NAME} geri alinamadi ({error.__cause__ or error}): {ids} dizinde "
                "var, taslakta yok. Ayni adaylarla yeniden kosu yeni kimlik vermez, eksik taslak satirini ekler; "
                "dosyalar elle duzenlenmez")
    return f"{UNCHANGED} ({INDEX_NAME}'e yazilan satirlar geri alindi)"


def save(work: Path, result: Registration) -> None:
    """Once dizin, sonra taslak; iki dosya birlikte degisir. Dizin yazilamazsa hicbiri degismez; taslak yazilamazsa
    (kalici kilit, disk hatasi, Ctrl+C) dizin eski baytlarina doner. Hata mesaji iki dosyanin son durumunu soyler."""
    if not (result.index_rows or result.draft_rows):
        return
    index, draft = work / INDEX_NAME, work / DRAFT_NAME
    try:
        before = index.read_bytes()
        if result.index_rows:
            write_atomic(index, appended(before, result.index_rows))
    except (UsageError, OSError) as error:
        raise UsageError(f"{error}. Dosya durumu: {UNCHANGED}") from error
    try:
        write_atomic(draft, appended(draft.read_bytes(), result.draft_rows))
    except (UsageError, OSError) as error:
        state = undo_index(index, before, result.index_rows) if result.index_rows else UNCHANGED
        raise UsageError(f"{error}. Dosya durumu: {state}") from error
    except BaseException:  # Ctrl+C dahil: dizin yeni kimligi taslaksiz tutmasin
        if result.index_rows:
            undo_index(index, before, result.index_rows)
        raise


def load_candidates(path: Path) -> list[dict[str, Any]]:
    """Aday satirlari: url kirpilir; must_contain metin listesine cevrilir (tek metin = tek ifade)."""
    out = []
    for row in read_jsonl(path):
        link, must = row.get("url") or "", row.get("must_contain") or []
        must = [must] if isinstance(must, str) else must
        if not isinstance(link, str) or not isinstance(must, list) or not all(isinstance(m, str) for m in must):
            raise UsageError(f"{path}: url metin, must_contain metin listesi olmali ({row.get('url')!r})")
        out.append({**row, "url": link.strip(), "must_contain": must})
    return out


def next_number(rows: list[dict[str, Any]], city: str) -> int:
    """Bu sehrin '<sehir>:kaynak:NNN' kimliklerindeki en buyuk numara (yoksa 0); baska bicimler sayilmaz."""
    pattern = re.compile(rf"{re.escape(city)}:kaynak:(\d+)\Z")
    found = (pattern.match(str(r.get("source_id") or "")) for r in rows)
    return max((int(m.group(1)) for m in found if m), default=0)


def run_fetch(job: Job, urls_file: Path, cache_dir: Path, retry: bool, transport: Transport,
              sleep: Callable[[float], None], clock: Callable[[], str]) -> tuple[int, dict[str, Any]]:
    """fetch_snapshot'i surec icinde calistirir; ozet satiri stdout'a sizmaz, sozluk olarak doner."""
    argv = ["--urls", str(urls_file), "--out-dir", str(job.out_dir), "--cache-dir", str(cache_dir)]
    if retry:
        argv.append("--retry-transient")
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        code = fetch_snapshot.main(argv, transport=transport, sleep=sleep, clock=clock)
    lines = [line for line in buffer.getvalue().splitlines() if line.strip()]
    try:
        summary = json.loads(lines[-1]) if lines else {}
    except json.JSONDecodeError:
        summary = {"raw": lines[-1]}
    return code, summary


def judge(candidate: dict[str, Any], snap: dict[str, Any], out_dir: Path) -> str | None:
    """Ret gerekcesi; aday kabul edilirse None. Soft-404 must_contain bos olsa da reddedilir."""
    flags = snap.get("flags") or []
    if not snap.get("text_file") or "thin_text" in flags:
        return f"kopya yok/ince (status {snap.get('status')})"
    if "soft_404" in flags or snap.get("soft_404"):
        return f"soft-404: sayfa yok isareti ({snap.get('soft_404') or 'soft_404'}; status {snap.get('status')})"
    try:
        text = norm((out_dir / snap["text_file"]).read_text(encoding="utf-8"))
    except OSError as error:
        return f"kopya okunamadi ({type(error).__name__})"
    missing = [m for m in candidate["must_contain"] if norm(m) not in text]
    return f"kanit metinde yok: {missing}" if missing else None


def index_row(job: Job, sid: str, candidate: dict[str, Any], snap: dict[str, Any]) -> dict[str, Any]:
    """kaynak_dizini satiri (bicim pilotla ayni)."""
    return {"source_id": sid, "topic": job.topic, "url": candidate["url"], "final_url": snap.get("final_url"),
            "title": snap.get("title"), "publisher": candidate.get("publisher"), "lang": candidate.get("lang"),
            "text_file": os.path.join(job.out_dir, snap["text_file"]), "text_chars": snap["text_chars"],
            "html_file": os.path.join(job.subdir, snap["html_file"]), "html_sha256": snap["html_sha256"],
            "why": candidate.get("why", "")}


def draft_row(city: str, topic: str, sid: str, candidate: dict[str, Any], snap: dict[str, Any]) -> dict[str, Any]:
    """kaynak_taslak satiri (bicim pilotla ayni)."""
    return {"source_id": sid, "city_id": city,
            "title": (snap.get("title") or candidate.get("title") or "")[:TITLE_MAX],
            "publisher": (candidate.get("publisher") or "")[:PUBLISHER_MAX], "url": candidate["url"],
            "checked_on": str(snap.get("fetched_on") or "")[:10], "topic": f"{city}:{topic}",
            "summary": candidate.get("why", ""), "verified": "Hayır"}


def rebuilt_draft_row(job: Job, known: dict[str, Any], candidate: dict[str, Any],
                      snap: dict[str, Any]) -> dict[str, Any]:
    """Dizinde olup taslakta olmayan kimligin taslak satiri: dizin satirinin konusu, basligi, yayincisi ve notu esas
    (iki dosya ayni kaydi anlatsin); eksik alan ve tarih bu kosunun adayindan ve kopyasindan."""
    kept = {key: known[key] for key in ("publisher", "why") if known.get(key)}
    page = {**snap, "title": known.get("title") or snap.get("title")}
    topic = str(known.get("topic") or job.topic)
    return draft_row(job.city, topic, str(known["source_id"]), {**candidate, **kept}, page)


def register(job: Job, candidates: list[dict], snaps: dict[str, dict], index: list[dict],
             draft: list[dict]) -> Registration:
    """Yeni adres siradaki numarayi alir; kayitli adres mevcut kimligi. O kimligin taslak satiri yoksa (onceki kosu
    dizine yazip taslaga yazamadiysa) satir dizin satirindan kurulur: yeniden kosu iki dosyayi esitler."""
    by_url = {r.get("url"): r for r in index}
    drafted = {r.get("source_id") for r in draft}
    number = next_number(index, job.city)
    added, reused, repaired, rejected, index_rows, draft_rows, seen = {}, {}, {}, [], [], [], set()
    for candidate in candidates:
        link = candidate["url"]
        if not link or link in seen:
            continue
        seen.add(link)
        snap = snaps.get(link, {})
        why = judge(candidate, snap, job.out_dir)
        if why:
            rejected.append({"url": link, "why": why})
        elif link in by_url:
            reused[link] = by_url[link].get("source_id")
            if reused[link] and reused[link] not in drafted:
                repaired[link] = reused[link]
                draft_rows.append(rebuilt_draft_row(job, by_url[link], candidate, snap))
        else:
            number += 1
            added[link] = f"{job.city}:kaynak:{number:03d}"
            index_rows.append(index_row(job, added[link], candidate, snap))
            draft_rows.append(draft_row(job.city, job.topic, added[link], candidate, snap))
    return Registration(added, reused, repaired, rejected, index_rows, draft_rows)


def commit(job: Job, candidates: list[dict], snaps: dict[str, dict], sleep: Callable[[float], None]) -> Registration:
    """Kilit altinda: dizini ve taslagi indirmeden SONRA yeniden okur (numara guncel olsun), kimlik verir, yazar."""
    with index_lock(job.work, sleep):
        index, draft = read_jsonl(job.work / INDEX_NAME), read_jsonl(job.work / DRAFT_NAME)
        result = register(job, candidates, snaps, index, draft)
        save(job.work, result)
    return result


def make_job(args: argparse.Namespace) -> Job:
    work = Path(os.path.abspath(args.work))
    if not work.is_dir():
        raise UsageError(f"is klasoru yok: {work}")
    if not CITY_RE.match(args.city_id):
        raise UsageError("--city-id kucuk harf ASCII/rakam/tire olmali (or. eindhoven)")
    if not TOPIC_RE.match(args.topic):
        raise UsageError("--topic kucuk harf ASCII kimlik olmali (or. kesif, mahalle)")
    if not SUBDIR_RE.match(args.subdir):
        raise UsageError("--subdir 'snap_<ad>' bicimde tek klasor adi olmali (ana snap/ klasorune yazilmaz)")
    return Job(work, work / args.subdir, args.subdir, args.topic, args.city_id)


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Yeni kaynak adreslerini kopyalar, must_contain ile dogrular, kimlik verir")
    p.add_argument("work", help="is klasoru (_is): kaynak_dizini.jsonl ve kaynak_taslak.jsonl burada")
    p.add_argument("--candidates", required=True, type=Path,
                   help="aday.jsonl: {url, must_contain, publisher, why, ...}")
    p.add_argument("--subdir", required=True, help="kopya alt klasoru, 'snap_<ad>' (or. snap_mekan_ek)")
    p.add_argument("--topic", required=True, help="konu kimligi (or. kesif, mahalle)")
    p.add_argument("--city-id", required=True)
    p.add_argument("--cache-dir", type=Path, help="HTTP onbellegi (varsayilan <is>/cache)")
    p.add_argument("--retry-transient", action=argparse.BooleanOptionalAction, default=True,
                   help="onbellekteki 429/5xx/ag hatalarini yeniden indir (varsayilan acik)")
    p.add_argument("--out", type=Path, help="ayrinti JSON (varsayilan <is>/<subdir>/eklenen.json)")
    return p


def run(args: argparse.Namespace, transport: Transport, sleep: Callable[[float], None],
        clock: Callable[[], str]) -> int:
    job = make_job(args)
    for name in (INDEX_NAME, DRAFT_NAME):
        read_jsonl(job.work / name)  # ag oncesi hizli dogrulama; kimlik verirken kilit altinda yeniden okunur
    candidates = load_candidates(args.candidates)
    job.out_dir.mkdir(parents=True, exist_ok=True)
    urls = list(dict.fromkeys(c["url"] for c in candidates if c["url"]))
    urls_file = job.out_dir / "urls.txt"
    urls_file.write_text("".join(u + "\n" for u in urls), encoding="utf-8")
    cache_dir = Path(os.path.abspath(args.cache_dir or job.work / "cache"))
    code, fetched = run_fetch(job, urls_file, cache_dir, args.retry_transient, transport, sleep, clock)
    if code == EXIT_USAGE:
        raise UsageError(f"fetch_snapshot kullanim hatasi: {fetched}")
    snaps = {r.get("url"): r for r in read_jsonl(job.out_dir / fetch_snapshot.INDEX_NAME)}
    result = commit(job, candidates, snaps, sleep)
    out = Path(os.path.abspath(args.out or job.out_dir / DETAIL_NAME))
    write_json(out, {"map": {**result.reused, **result.added}, "rejected": result.rejected, "fetch": fetched})
    emit({"status": "findings" if result.rejected else "ok", "candidates": len(urls), "added": len(result.added),
          "reused": len(result.reused), "draft_repaired": len(result.repaired), "rejected": len(result.rejected),
          "requests_made": fetched.get("requests_made"), "cache_hits": fetched.get("cache_hits"),
          "out_dir": str(job.out_dir), "out": str(out)})
    return EXIT_FINDINGS if result.rejected else EXIT_OK


def main(argv: list[str] | None = None, transport: Transport = urllib_transport,
         sleep: Callable[[float], None] = time.sleep, clock: Callable[[], str] = utc_today) -> int:
    setup_utf8()
    try:
        args = _parser().parse_args(argv)
    except SystemExit as stop:
        return EXIT_USAGE if stop.code else EXIT_OK
    try:
        return run(args, transport, sleep, clock)
    except (UsageError, OSError, ValueError) as error:  # yakalanmazsa cikis 1 olur ve 'bulgu' ile karisir
        print(f"HATA: {error}", file=sys.stderr)
        return EXIT_USAGE


if __name__ == "__main__":
    raise SystemExit(main())
