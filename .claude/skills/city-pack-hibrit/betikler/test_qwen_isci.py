"""qwen_isci.py testleri: API'ye gitmez (--sahte-yanit / --kuru)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import qwen_isci  # noqa: E402

CIKTI = ["data/parcalar/Sözlük.sozluk.jsonl", "claims/sozluk.jsonl"]


def api_yaniti(icerik: str, bitis: str = "stop") -> dict:
    return {"choices": [{"message": {"content": icerik}, "finish_reason": bitis}],
            "usage": {"prompt_tokens": 100, "completion_tokens": 50}}


@pytest.fixture
def ortam(tmp_path: Path) -> dict:
    kok = tmp_path / "_is"
    kok.mkdir()
    mesaj = tmp_path / "mesaj.md"
    mesaj.write_text("Sözlük yaz.", encoding="utf-8")
    talimat = tmp_path / "rol.md"
    talimat.write_text("Rol.", encoding="utf-8")
    kaynak = tmp_path / "kaynak.txt"
    kaynak.write_text("Empadronamiento es el registro municipal.", encoding="utf-8")
    return {"tmp": tmp_path, "kok": kok, "mesaj": mesaj, "talimat": talimat, "kaynak": kaynak}


def calistir(ortam: dict, icerik: str | None, *ek: str, bitis: str = "stop") -> tuple[int, dict]:
    argv = ["--gorev", "sozluk", "--mesaj", str(ortam["mesaj"]), "--talimat", str(ortam["talimat"]),
            "--girdi", str(ortam["kaynak"]), "--kok", str(ortam["kok"]), "--cikti", *CIKTI, *ek]
    if icerik is not None:
        sahte = ortam["tmp"] / "yanit.json"
        sahte.write_text(json.dumps(api_yaniti(icerik, bitis), ensure_ascii=False), encoding="utf-8")
        argv += ["--sahte-yanit", str(sahte)]
    kod = qwen_isci.main(argv)
    kayit = ortam["kok"] / "qwen" / "sozluk.donus.json"
    return kod, json.loads(kayit.read_text(encoding="utf-8")) if kayit.exists() else {}


def gecerli_icerik() -> str:
    return json.dumps({
        "dosyalar": {
            "data/parcalar/Sözlük.sozluk.jsonl": [{"term_id": "x:term:001", "term": "Empadronamiento"}],
            "claims/sozluk.jsonl": [{"claim_id": "C-term-001-1", "quote": "registro municipal"}],
        },
        "donus": {"rows": 1},
    }, ensure_ascii=False)


def test_gecerli_yanit_dosyalari_yazar(ortam: dict) -> None:
    kod, kayit = calistir(ortam, gecerli_icerik())
    assert kod == 0
    satir = (ortam["kok"] / "data" / "parcalar" / "Sözlük.sozluk.jsonl").read_text(encoding="utf-8")
    assert json.loads(satir.splitlines()[0])["term"] == "Empadronamiento"
    assert kayit["yazilan"] == {"data/parcalar/Sözlük.sozluk.jsonl": 1, "claims/sozluk.jsonl": 1}
    assert kayit["donus"] == {"rows": 1}
    assert kayit["kullanim"]["completion_tokens"] == 50


def test_kod_citi_ve_ters_bolu_anahtar_kabul_edilir(ortam: dict) -> None:
    icerik = gecerli_icerik().replace("data/parcalar/", "data\\\\parcalar\\\\")
    kod, _ = calistir(ortam, "```json\n" + icerik + "\n```")
    assert kod == 0
    assert (ortam["kok"] / "claims" / "sozluk.jsonl").exists()


def test_izinsiz_yol_varsa_hicbir_dosya_yazilmaz(ortam: dict) -> None:
    veri = json.loads(gecerli_icerik())
    veri["dosyalar"]["data/Yanıtlar.jsonl"] = [{"a": 1}]
    kod, kayit = calistir(ortam, json.dumps(veri, ensure_ascii=False))
    assert kod == 1
    assert any(b.startswith("izinsiz_yol") for b in kayit["bulgular"])
    assert not (ortam["kok"] / "claims" / "sozluk.jsonl").exists()


def test_var_olan_dosya_uzerine_yaz_olmadan_ezilmez(ortam: dict) -> None:
    hedef = ortam["kok"] / "claims" / "sozluk.jsonl"
    hedef.parent.mkdir(parents=True)
    hedef.write_text("eski\n", encoding="utf-8")
    kod, kayit = calistir(ortam, gecerli_icerik())
    assert kod == 1 and hedef.read_text(encoding="utf-8") == "eski\n"
    assert "dosya_var: claims/sozluk.jsonl" in kayit["bulgular"]
    kod, _ = calistir(ortam, gecerli_icerik(), "--uzerine-yaz")
    assert kod == 0 and "C-term-001-1" in hedef.read_text(encoding="utf-8")


def test_satir_nesne_degilse_reddedilir(ortam: dict) -> None:
    veri = json.loads(gecerli_icerik())
    veri["dosyalar"]["claims/sozluk.jsonl"] = ["metin"]
    kod, kayit = calistir(ortam, json.dumps(veri))
    assert kod == 1 and "satir_nesne_degil: claims/sozluk.jsonl" in kayit["bulgular"]


def test_kesilen_yanit_hata_verir(ortam: dict) -> None:
    kod, kayit = calistir(ortam, gecerli_icerik(), bitis="length")
    assert kod == 1 and "kesildi" in kayit["hata"]
    assert (ortam["kok"] / "qwen" / "sozluk.ham.txt").exists()


def test_json_olmayan_yanit_hata_verir(ortam: dict) -> None:
    kod, kayit = calistir(ortam, "Üzgünüm, yapamam.")
    assert kod == 1 and "JSON" in kayit["hata"]


@pytest.mark.parametrize("yol", ["../disari.jsonl", "C:/abs.jsonl", "claims/sozluk.txt"])
def test_kotu_cikti_yolu_kullanim_hatasi(ortam: dict, yol: str, capsys: pytest.CaptureFixture) -> None:
    kod = qwen_isci.main(["--gorev", "g", "--mesaj", str(ortam["mesaj"]), "--talimat", str(ortam["talimat"]),
                          "--kok", str(ortam["kok"]), "--cikti", yol, "--kuru"])
    assert kod == 2
    assert "--cikti" in json.loads(capsys.readouterr().out)["hata"]


def test_kuru_mod_api_ye_gitmez_ve_girdiyi_icerir(ortam: dict, capsys: pytest.CaptureFixture,
                                                  monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(qwen_isci, "api_cagir", lambda *a: pytest.fail("API cagrildi"))
    kod = qwen_isci.main(["--gorev", "g", "--mesaj", str(ortam["mesaj"]), "--talimat", str(ortam["talimat"]),
                          "--girdi", str(ortam["kaynak"]), "--kok", str(ortam["kok"]), "--cikti", *CIKTI, "--kuru"])
    ozet = json.loads(capsys.readouterr().out)
    assert kod == 0 and ozet["kuru"] is True and ozet["girdi_karakter"] > 0


def test_anahtarsiz_api_kullanim_hatasi(ortam: dict, monkeypatch: pytest.MonkeyPatch,
                                        capsys: pytest.CaptureFixture) -> None:
    monkeypatch.delenv("QWEN_API_KEY", raising=False)
    kod = qwen_isci.main(["--gorev", "g", "--mesaj", str(ortam["mesaj"]), "--talimat", str(ortam["talimat"]),
                          "--kok", str(ortam["kok"]), "--cikti", *CIKTI])
    assert kod == 2 and "QWEN_API_KEY" in json.loads(capsys.readouterr().out)["hata"]


def test_mesaj_izinli_yollari_ve_kaynagi_tasir(ortam: dict) -> None:
    izinli = qwen_isci.izinli_yollar(ortam["kok"], CIKTI)
    metin = qwen_isci.kullanici_mesaji(ortam["mesaj"], [ortam["kaynak"]], izinli)
    assert "registro municipal" in metin and "claims/sozluk.jsonl" in metin
    assert "Qwen ek kuralları" in qwen_isci.sistem_mesaji([ortam["talimat"]])
