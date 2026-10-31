r"""Qwen isci (city-pack-hibrit): bir yazim gorevini Qwen API'sine verir, donen JSON'dan izinli JSONL dosyalarini yazar.

Kullanim:
  qwen_isci.py --gorev <ad> --mesaj <gorev_mesaji.md> --talimat <a.md> [<b.md> ...] [--girdi <dosya> ...]
               --kok <WORK\_is> --cikti <goreli\yol.jsonl> [<goreli\yol2.jsonl> ...]
               [--log-dir <WORK\_is\qwen>] [--dagilim <isci_dagilimi.json>] [--uzerine-yaz]
               [--kuru] [--sahte-yanit <api_yaniti.json>]

Akis: agents\qwen-ek-kurallar.md + talimat dosyalari sistem mesaji; gorev mesaji + girdi dosyalarinin icerigi
kullanici mesaji olur. Qwen'den tek JSON nesnesi beklenir:
  {"dosyalar": {"<goreli yol>": [{satir}, ...], ...}, "donus": {...}}
Yalniz --cikti ile izin verilen yollar yazilir (kok altinda, UTF-8, satir basina bir JSON). Hepsi ya da hicbiri:
izinsiz yol, nesne olmayan satir ya da --uzerine-yaz verilmeden var olan dosya varsa hicbir dosya yazilmaz.
Qwen dosya okuyamaz, internete cikamaz, komut calistiramaz: gordugu her sey bu mesajdadir.

Ciktilar (--log-dir, varsayilan <kok>\qwen): <gorev>.donus.json (Qwen'in donus nesnesi, yazilan satir sayilari,
token kullanimi, sure, bulgular) ve <gorev>.ham.txt (ham yanit metni).
API anahtari ortam degiskeninden okunur (dagilim: qwen.api_key_env, varsayilan QWEN_API_KEY); hicbir dosyaya yazilmaz.
--kuru: istegi kurar, boyutunu yazar, API'ye gitmez. --sahte-yanit: API yerine verilen chat/completions yanitini kullanir.
stdout tek satir JSON. Cikis: 0 yazildi / 1 Qwen yaniti gecersiz ya da API hatasi / 2 kullanim hatasi.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path, PurePath
from typing import Any

BETIK_DIR = Path(__file__).resolve().parent
SKILL_DIR = BETIK_DIR.parent
VARSAYILAN_DAGILIM = SKILL_DIR / "references" / "isci_dagilimi.json"
EK_KURALLAR = SKILL_DIR / "agents" / "qwen-ek-kurallar.md"
MAX_GIRDI_KARAKTER = 600_000
TEKRAR_BEKLE_SN = (30, 90)
MAX_BULGU = 20


class KullanimHatasi(Exception):
    """Cikis 2."""


class YanitHatasi(Exception):
    """Cikis 1."""


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Qwen yazim iscisi (city-pack-hibrit)")
    ap.add_argument("--gorev", required=True)
    ap.add_argument("--mesaj", required=True, type=Path)
    ap.add_argument("--talimat", nargs="+", required=True, type=Path)
    ap.add_argument("--girdi", nargs="*", default=[], type=Path)
    ap.add_argument("--kok", required=True, type=Path)
    ap.add_argument("--cikti", nargs="+", required=True)
    ap.add_argument("--log-dir", type=Path)
    ap.add_argument("--dagilim", type=Path, default=VARSAYILAN_DAGILIM)
    ap.add_argument("--uzerine-yaz", action="store_true")
    ap.add_argument("--kuru", action="store_true")
    ap.add_argument("--sahte-yanit", type=Path)
    return ap.parse_args(argv)


def oku(yol: Path) -> str:
    if not yol.is_file():
        raise KullanimHatasi(f"dosya yok: {yol}")
    return yol.read_text(encoding="utf-8-sig", errors="replace")


def izinli_yollar(kok: Path, ciktilar: list[str]) -> dict[str, Path]:
    kok = kok.resolve()
    izinli: dict[str, Path] = {}
    for c in ciktilar:
        p = PurePath(c.replace("\\", "/"))
        if p.is_absolute() or ".." in p.parts or p.suffix != ".jsonl":
            raise KullanimHatasi(f"--cikti goreli bir .jsonl yolu olmali (.. yok): {c}")
        hedef = (kok / Path(*p.parts)).resolve()
        if kok not in hedef.parents:
            raise KullanimHatasi(f"--cikti kok disinda: {c}")
        izinli[p.as_posix()] = hedef
    return izinli


def sistem_mesaji(talimatlar: list[Path]) -> str:
    parcalar = [oku(EK_KURALLAR)] + [oku(t) for t in talimatlar]
    return "\n\n---\n\n".join(parcalar)


def kullanici_mesaji(mesaj: Path, girdiler: list[Path], izinli: dict[str, Path]) -> str:
    dosyalar = [f'<dosya yol="{g}">\n{oku(g)}\n</dosya>' for g in girdiler]
    bicim = (
        "YANIT BICIMI: yalniz tek bir JSON nesnesi, oncesinde ve sonrasinda metin yok.\n"
        '{"dosyalar": {"<yol>": [ {satir}, ... ]}, "donus": { ...gorev mesajindaki donus alanlari... }}\n'
        "Izinli yollar (anahtar olarak aynen yaz): " + ", ".join(izinli)
    )
    return "\n\n".join([oku(mesaj), "## Verilen dosyalar", *dosyalar, bicim])


def ayarlar(dagilim: Path) -> dict[str, Any]:
    try:
        veri = json.loads(oku(dagilim))
        return dict(veri["qwen"])
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        raise KullanimHatasi(f"dagilim dosyasi okunamadi ({dagilim}): {e}") from e


def api_cagir(qwen: dict[str, Any], sistem: str, kullanici: str) -> dict[str, Any]:
    anahtar = os.environ.get(qwen.get("api_key_env", "QWEN_API_KEY"), "")
    if not anahtar:
        raise KullanimHatasi(f"API anahtari yok: ortam degiskeni {qwen.get('api_key_env', 'QWEN_API_KEY')}")
    govde = {
        "model": qwen["model"],
        "messages": [{"role": "system", "content": sistem}, {"role": "user", "content": kullanici}],
        "max_tokens": qwen.get("max_tokens", 32000),
        "temperature": qwen.get("temperature", 0.3),
        "response_format": {"type": "json_object"},
        **qwen.get("ek_govde", {}),
    }
    istek = urllib.request.Request(
        qwen["base_url"].rstrip("/") + "/chat/completions",
        data=json.dumps(govde, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {anahtar}"},
        method="POST",
    )
    return istek_gonder(istek, qwen.get("zaman_asimi_sn", 900))


def istek_gonder(istek: urllib.request.Request, zaman_asimi: int) -> dict[str, Any]:
    son_hata = ""
    for bekle in (0, *TEKRAR_BEKLE_SN):
        time.sleep(bekle)
        try:
            with urllib.request.urlopen(istek, timeout=zaman_asimi) as yanit:
                return json.loads(yanit.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            son_hata = f"HTTP {e.code}: {e.read()[:300].decode('utf-8', 'replace')}"
            if e.code != 429 and e.code < 500:
                break
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            son_hata = f"{type(e).__name__}: {e}"
    raise YanitHatasi(f"API hatasi: {son_hata}")


def icerik_ayikla(api_yaniti: dict[str, Any]) -> tuple[str, str, dict[str, Any]]:
    try:
        secim = api_yaniti["choices"][0]
        icerik = secim["message"]["content"] or ""
    except (KeyError, IndexError, TypeError) as e:
        raise YanitHatasi(f"API yaniti beklenen bicimde degil: {e}") from e
    return icerik, secim.get("finish_reason") or "", api_yaniti.get("usage") or {}


def json_coz(icerik: str) -> dict[str, Any]:
    metin = re.sub(r"^\s*```(?:json)?\s*|\s*```\s*$", "", icerik.strip())
    try:
        veri = json.loads(metin)
    except json.JSONDecodeError:
        bas, son = metin.find("{"), metin.rfind("}")
        if bas < 0 or son <= bas:
            raise YanitHatasi("yanit JSON degil")
        try:
            veri = json.loads(metin[bas : son + 1])
        except json.JSONDecodeError as e:
            raise YanitHatasi(f"yanit JSON degil: {e}") from e
    if not isinstance(veri, dict) or not isinstance(veri.get("dosyalar"), dict):
        raise YanitHatasi("yanitta 'dosyalar' nesnesi yok")
    return veri


def dosyalari_denetle(
    dosyalar: dict[str, Any], izinli: dict[str, Path], uzerine_yaz: bool
) -> tuple[dict[Path, list[dict[str, Any]]], list[str]]:
    yazilacak: dict[Path, list[dict[str, Any]]] = {}
    bulgular: list[str] = []
    for anahtar, satirlar in dosyalar.items():
        yol = PurePath(str(anahtar).replace("\\", "/")).as_posix()
        if yol not in izinli:
            bulgular.append(f"izinsiz_yol: {anahtar}")
            continue
        if not isinstance(satirlar, list) or not all(isinstance(s, dict) for s in satirlar):
            bulgular.append(f"satir_nesne_degil: {anahtar}")
            continue
        if izinli[yol].exists() and not uzerine_yaz:
            bulgular.append(f"dosya_var: {anahtar}")
            continue
        yazilacak[izinli[yol]] = satirlar
    return yazilacak, bulgular


def jsonl_yaz(hedef: Path, satirlar: list[dict[str, Any]]) -> None:
    hedef.parent.mkdir(parents=True, exist_ok=True)
    gecici = hedef.with_name(hedef.name + ".yaziliyor")
    metin = "".join(json.dumps(s, ensure_ascii=False) + "\n" for s in satirlar)
    gecici.write_text(metin, encoding="utf-8", newline="\n")
    os.replace(gecici, hedef)


def kayit_yaz(log_dir: Path, gorev: str, ham: str, kayit: dict[str, Any]) -> None:
    log_dir.mkdir(parents=True, exist_ok=True)
    (log_dir / f"{gorev}.ham.txt").write_text(ham, encoding="utf-8", newline="\n")
    (log_dir / f"{gorev}.donus.json").write_text(
        json.dumps(kayit, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n"
    )


def yaniti_isle(args: argparse.Namespace, izinli: dict[str, Path], api_yaniti: dict[str, Any]) -> tuple[int, dict]:
    icerik, bitis, kullanim = icerik_ayikla(api_yaniti)
    ozet: dict[str, Any] = {"gorev": args.gorev, "bitis": bitis, "kullanim": kullanim, "yazilan": {}, "bulgular": []}
    try:
        if bitis == "length":
            raise YanitHatasi("yanit max_tokens sinirinda kesildi (gorevi bol ya da max_tokens artir)")
        veri = json_coz(icerik)
        yazilacak, bulgular = dosyalari_denetle(veri["dosyalar"], izinli, args.uzerine_yaz)
        ozet["donus"] = veri.get("donus")
        ozet["eksik"] = sorted(set(izinli) - {PurePath(str(k).replace("\\", "/")).as_posix() for k in veri["dosyalar"]})
        if bulgular:
            ozet["bulgular"] = bulgular[:MAX_BULGU]
            raise YanitHatasi(f"{len(bulgular)} bulgu; hicbir dosya yazilmadi")
        for hedef, satirlar in yazilacak.items():
            jsonl_yaz(hedef, satirlar)
            ozet["yazilan"][hedef.relative_to(args.kok.resolve()).as_posix()] = len(satirlar)
        return 0, ozet
    except YanitHatasi as e:
        ozet["hata"] = str(e)
        return 1, ozet
    finally:
        kayit_yaz(args.log_dir or args.kok / "qwen", args.gorev, icerik, ozet)


def calistir(args: argparse.Namespace) -> tuple[int, dict]:
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", args.gorev):
        raise KullanimHatasi("--gorev yalniz harf, rakam, _ . - icerebilir")
    if not args.kok.is_dir():
        raise KullanimHatasi(f"--kok klasor degil: {args.kok}")
    izinli = izinli_yollar(args.kok, args.cikti)
    qwen = ayarlar(args.dagilim)
    sistem = sistem_mesaji(args.talimat)
    kullanici = kullanici_mesaji(args.mesaj, args.girdi, izinli)
    boyut = len(sistem) + len(kullanici)
    if boyut > qwen.get("max_girdi_karakter", MAX_GIRDI_KARAKTER):
        raise KullanimHatasi(f"girdi cok buyuk ({boyut} karakter); gorevi bol")
    if args.kuru:
        return 0, {"gorev": args.gorev, "kuru": True, "girdi_karakter": boyut, "model": qwen.get("model"),
                   "cikti": list(izinli)}
    t0 = time.monotonic()
    api_yaniti = json.loads(oku(args.sahte_yanit)) if args.sahte_yanit else api_cagir(qwen, sistem, kullanici)
    kod, ozet = yaniti_isle(args, izinli, api_yaniti)
    ozet.update({"model": qwen.get("model"), "sure_sn": round(time.monotonic() - t0, 1), "girdi_karakter": boyut})
    return kod, ozet


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        kod, ozet = calistir(args)
    except KullanimHatasi as e:
        kod, ozet = 2, {"gorev": args.gorev, "hata": str(e)}
    except YanitHatasi as e:
        kod, ozet = 1, {"gorev": args.gorev, "hata": str(e)}
    print(json.dumps(ozet, ensure_ascii=False))
    return kod


if __name__ == "__main__":
    sys.exit(main())
