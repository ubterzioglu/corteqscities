"""Editoryal yuzde ve karar hesabi: kontrol listesi bolum 20 (K100, K101, K115, K116, K117).

Kullanim: editorial_score.py --input criteria.json --out score.json [--format json|md]
Girdi: criteria (25 alt olcut {code, passed, required, status ok|partial|not_applicable|not_checked|separate_stage,
reason}) VEYA categories (5 kategori katkisi) VEYA inventory_available=false (OLCULEMEDI); ortak: findings [{id,
priority, criteria?: [olcut kodu]}], coverage {cards|photos|critical_claims}. Hedef paydalari sabit (A1 240, B1 120,
B2 16, B3 12, B4 60, C1 250; E3 23, E5 5); hedef olcutu uygulanmaz sayilmaz. Fraction ile tam hesap, yuzde ASAGI.
Karar: P0 / D1 KALDI / P1 / eksik hedef -> DUZELTME; olculmeyen olcut, Atinc payda karari bekleyen uygulanmaz olcut,
bulguya baglanmamis KALDI birim veya kapsam eksigi -> KANIT EKSIK; aksi HAZIR. Sapma: E4 separate_stage 0 puan ve
alt sinir etiketi alir, kanit eksige dusurmez. Cikis 0 hazir / 1 hazir degil / 2 yapi hatasi; girdi degistirilmez.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import asdict, dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any, Sequence

import common

TOOL = "editorial_score"
CATEGORY_NAMES = {"A": "Bilgi kartları ve kaynaklar", "B": "Mekân, mahalle, rota ve sözlük",
                  "C": "Fotoğraf seçimi ve sunum", "D": "Lisans ve kanıtlar", "E": "Teknik teslim ve işlev"}
CATEGORY_WEIGHTS = {"A": 35, "B": 20, "C": 20, "D": 15, "E": 10}
CRITERION_WEIGHTS = {cat: weight // 5 for cat, weight in CATEGORY_WEIGHTS.items()}  # 7, 4, 4, 3, 2
CRITERIA_CODES = tuple(f"{cat}{i}" for cat in CATEGORY_WEIGHTS for i in range(1, 6))
TARGET_DENOMINATORS = {code: common.BERLIN_TARGET[key] for code, key in (("A1", "answers"), ("B1", "places"),
                       ("B2", "districts"), ("B3", "routes"), ("B4", "glossary"), ("C1", "photos"))}
FIXED_DENOMINATORS = {**TARGET_DENOMINATORS, "E3": 23, "E5": 5}
STATUS_TR = {"ok": "kontrol edildi", "partial": "kısmi", "not_applicable": "uygulanmaz",
             "not_checked": "kontrol edilemedi", "separate_stage": "ayrı aşama"}
SEPARATE_STAGE_CODES = frozenset({"E4"})
LICENSE_GATE_CODES = frozenset({"D1"})  # karar kurali 1: ucretsiz kullanim dayanagi yoklugu P0
PRIORITIES = ("P0", "P1", "P2")
COVERAGE_KEYS = (("cards", "kart"), ("photos", "fotoğraf"), ("critical_claims", "kritik iddia"))
Coverage = dict[str, tuple[int, int] | None]
Findings = dict[str, list[str]]
DECISION_FIX = "DÜZELTME GEREKLİ"
DECISION_EVIDENCE = "KARAR İÇİN KANIT EKSİK"
DECISION_READY = "ATINÇ’IN SON PAKET İNCELEMESİNE HAZIR"
NOT_MEASURED = "ÖLÇÜLEMEDİ"
LABEL_PARTIAL = "doğrulanan alt sınır, kısmi denetim"
LABEL_NOT_FINAL = "nihai değil"
LABEL_CATEGORY = "kategori toplamı modu"
NOTE_SEPARATE = "önizleme ve Drive kontrolleri ayrı aşamada"
DEVIATION_E4 = ("Sapma (bölüm 20 karar kuralı 3): E4 web işlevleri bu projede ayrı aşamadır (checks.yaml scope "
                "preview-later / drive-manual). E4 puanı 'kontrol edilemedi' gibi 0 alındı, ancak karar "
                "'kanıt eksik'e düşürülmedi; kararın yanına ayrı aşama notu eklendi.")
DEVIATION_CATEGORY = ("Kategori toplamı modu bölüm 20 hesabı değildir: 5 kategori katkısı doğrudan toplandı, 25 alt "
                      "ölçütün pay/paydası doğrulanamadı; bu yüzden karar en iyi durumda 'kanıt eksik' olur.")
FIXED_NOTES = (
    "Yüzde, kalan kısmın kesin yanlış olduğu anlamına gelmez; inceleme kapsamı, kullanılabilir içerik ve yönetim "
    "üretim yüzdesi aynı metrik değildir.", "KALDI ve KONTROL EDİLEMEDİ puan kazanmaz; ikisi durum sütununda ayrıdır.",
    "12 konu, ücretsiz gerçek fotoğraf, uyarı bandı olmaması ve zorunlu sözleşme şartları ayrı karar kapısıdır; "
    "açık bulgu (P0/P1) olarak girilmelidir.",
    "Yetkili insanın kabul/yayın kararı ayrı süreçtir; bu çıktı yayın onayı değildir.")


class InputError(Exception):
    """Girdi yapisi hatali: cikis kodu 2."""


@dataclass(frozen=True)
class Criterion:
    code: str
    status: str
    passed: int | None
    required: int | None
    ratio: Fraction
    reason: str
    note: str

    @property
    def weight(self) -> int:
        return CRITERION_WEIGHTS[self.code[0]]


def _count(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise InputError(f"{label}: negatif olmayan tam sayı olmalı ({value!r})")
    return value


def _num(value: Fraction) -> int | float:
    return value.numerator if value.denominator == 1 else round(float(value), 6)


def _measured_ratio(code: str, raw: dict[str, Any]) -> tuple[int, int, Fraction, str]:
    passed = _count(raw.get("passed"), f"{code}.passed")
    fixed = FIXED_DENOMINATORS.get(code)
    required = _count(raw.get("required", fixed), f"{code}.required")
    notes: list[str] = []
    if fixed is not None and required != fixed:
        notes.append(f"girdi paydası {required} yok sayıldı; sabit payda {fixed}")
        required = fixed
    if required == 0:
        return passed, 0, Fraction(0), "payda 0: oran ölçülemedi; uygulanmazsa gerekçeyle not_applicable olmalı"
    if passed > required:
        notes.append(f"pay {passed} > payda {required}; oran 1'e kırpıldı")
    return passed, required, min(Fraction(passed, required), Fraction(1)), "; ".join(notes)


def parse_criterion(raw: Any) -> Criterion:
    if not isinstance(raw, dict):
        raise InputError(f"ölçüt kaydı nesne olmalı: {raw!r}")
    code, status = raw.get("code"), raw.get("status")
    if code not in CRITERIA_CODES:
        raise InputError(f"bilinmeyen ölçüt kodu: {code!r}")
    if status not in STATUS_TR:
        raise InputError(f"{code}: geçersiz status {status!r} (izinli: {', '.join(STATUS_TR)})")
    reason = str(raw.get("reason") or "").strip()
    if status == "not_applicable" and not reason:
        raise InputError(f"{code}: uygulanmaz için gerekçe (reason) zorunlu")
    if status == "separate_stage" and code not in SEPARATE_STAGE_CODES:
        raise InputError(f"{code}: separate_stage yalnız {', '.join(sorted(SEPARATE_STAGE_CODES))} için geçerli")
    if status in ("ok", "partial"):
        passed, required, ratio, note = _measured_ratio(code, raw)
        return Criterion(code, status, passed, required, ratio, reason, note)
    given = raw.get("required")
    required = FIXED_DENOMINATORS.get(code, None if given is None else _count(given, f"{code}.required"))
    note = (f"hedef ölçütü uygulanmaz sayılmaz: sabit payda {required} (K117); eksik hedef"
            if status == "not_applicable" and code in TARGET_DENOMINATORS else "")
    return Criterion(code, status, None, required, Fraction(0), reason, note)


def parse_criteria(items: Any) -> tuple[Criterion, ...]:
    if not isinstance(items, list):
        raise InputError("criteria liste olmalı")
    parsed = [parse_criterion(item) for item in items]
    codes = [item.code for item in parsed]
    duplicates = sorted({code for code in codes if codes.count(code) > 1})
    missing = [code for code in CRITERIA_CODES if code not in codes]
    if duplicates or missing:
        raise InputError(f"25 ölçüt tam birer kez verilmeli; eksik: {missing}; yinelenen: {duplicates}")
    return tuple(sorted(parsed, key=lambda item: CRITERIA_CODES.index(item.code)))


def parse_categories(raw: Any) -> dict[str, Fraction]:
    if not isinstance(raw, dict) or set(raw) != set(CATEGORY_WEIGHTS):
        raise InputError("categories tam olarak A, B, C, D, E anahtarlarını içermeli")
    result: dict[str, Fraction] = {}
    for cat, weight in CATEGORY_WEIGHTS.items():
        value = raw[cat]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise InputError(f"categories.{cat}: sayı olmalı ({value!r})")
        score = Fraction(str(value))
        if not 0 <= score <= weight:
            raise InputError(f"categories.{cat}: 0..{weight} aralığında olmalı ({value})")
        result[cat] = score
    return result


def parse_findings(items: Any) -> tuple[Findings, frozenset[str]]:
    """Bulgulari oncelige gore toplar; ikinci deger bulgularin bagli oldugu (criteria) olcut kodlaridir."""
    items = [] if items is None else items
    if not isinstance(items, list):
        raise InputError("findings liste olmalı")
    pairs, linked = [], set()
    for item in items:
        if not isinstance(item, dict) or not str(item.get("id") or "").strip():
            raise InputError(f"bulgu kaydı {{id, priority}} olmalı: {item!r}")
        if item.get("priority") not in PRIORITIES:
            raise InputError(f"bulgu {item['id']}: priority P0, P1 veya P2 olmalı ({item.get('priority')!r})")
        links = item.get("criteria", [])
        if not isinstance(links, list) or any(code not in CRITERIA_CODES for code in links):
            raise InputError(f"bulgu {item['id']}: criteria ölçüt kodu listesi olmalı ({links!r})")
        pairs.append((item["priority"], str(item["id"]).strip()))
        linked.update(links)
    return {priority: sorted({fid for p, fid in pairs if p == priority}) for priority in PRIORITIES}, frozenset(linked)


def parse_coverage(raw: Any) -> Coverage:
    raw = {} if raw is None else raw
    if not isinstance(raw, dict):
        raise InputError("coverage nesne olmalı")
    result: Coverage = {}
    for key, _label in COVERAGE_KEYS:
        value = raw.get(key)
        if isinstance(value, dict):
            value = [value.get("reviewed"), value.get("total")]
        if value is not None and (not isinstance(value, list) or len(value) != 2):
            raise InputError(f"coverage.{key}: [incelenen, toplam] olmalı")
        pair = None if value is None else tuple(_count(v, f"coverage.{key}") for v in value)
        if pair is not None and pair[0] > pair[1]:
            raise InputError(f"coverage.{key}: incelenen {pair[0]} > toplam {pair[1]}")
        result[key] = pair
    return result


def coverage_gaps(coverage: Coverage) -> list[str]:
    return [f"kapsam ({label}): x/y verilmedi (K100)" for key, label in COVERAGE_KEYS if coverage[key] is None] + [
        f"kapsam ({label}): {coverage[key][0]}/{coverage[key][1]} kısmi" for key, label in COVERAGE_KEYS
        if coverage[key] is not None and coverage[key][0] < coverage[key][1]]


def classify(item: Criterion, linked: frozenset[str]) -> tuple[str, str] | None:
    """Olcutun karar etkisi (K116): unmeasured | target | gate | gap ve metni; etkisi yoksa None."""
    suffix = f" ({item.reason})" if item.reason else ""
    failed = item.required - item.passed if item.status == "ok" and item.required else 0
    if item.status in ("not_checked", "partial"):
        text = "kontrol edilemedi" if item.status == "not_checked" else "kısmi denetim"
        return "unmeasured", f"{item.code}: {text}{suffix}"
    if item.status == "ok" and item.required == 0:
        return "unmeasured", f"{item.code}: payda 0, oran ölçülemedi"
    if item.code in TARGET_DENOMINATORS and (item.status == "not_applicable" or failed > 0):
        return "target", item.code
    if item.status == "not_applicable":
        return "gap", f"{item.code}: bütün ölçüt uygulanmaz{suffix}; payda/yeniden dağıtım için Atınç kararı gerekir"
    if failed > 0 and item.code in LICENSE_GATE_CODES:
        return "gate", (f"{item.code}: {failed} dosyada ücretsiz ticari kullanım dayanağı doğrulanmadı "
                        f"({item.passed}/{item.required}, karar kuralı 1)")
    if failed > 0 and item.code not in linked:
        return "gap", (f"{item.code}: {failed} KALDI birim ({item.passed}/{item.required}) hiçbir bulguya bağlanmadı; "
                       "findings[].criteria ile öncelik (P0/P1/P2) girilmeli")
    return None


def _part(label: str, items: Sequence[str]) -> list[str]:
    return [f"{label}: {', '.join(items)}"] if items else []


def decide(findings: Findings, missing: list[str], gaps: list[str], gates: Sequence[str] = ()) -> tuple[str, str]:
    """Bolum 20 karar sirasi: puan ne olursa olsun engeller once gelir (K101, K116); D1 KALDI P0 kapisidir."""
    if findings["P0"] or gates:
        return DECISION_FIX, "; ".join(_part("açık P0", findings["P0"]) + _part("P0 kapısı", gates))
    if findings["P1"] or missing:
        return DECISION_FIX, "; ".join(_part("açık P1", findings["P1"]) + _part("eksik hedef", missing))
    if gaps:
        return DECISION_EVIDENCE, "kanıt eksik: " + "; ".join(gaps)
    return DECISION_READY, "açık P0/P1 yok; zorunlu hedefler ve denetimler tamam"


def cover_line(report: dict[str, Any]) -> str:
    percent, labels = report["editorial_percent"], report["labels"]
    text = NOT_MEASURED if percent is None else f"%{percent}" + (f" ({'; '.join(labels)})" if labels else "")
    scope = "; ".join(
        f"{label} {'?/?' if report['coverage'][key] is None else '{reviewed}/{total}'.format(**report['coverage'][key])}"
        for key, label in COVERAGE_KEYS)
    decision = report["decision"] + (f" ({report['decision_note']})" if report["decision_note"] else "")
    return f"Editoryal hazır olma: {text} | İnceleme kapsamı: {scope} | Karar: {decision}"


def _assemble(*, mode: str, raw: Fraction | None, max_possible: int | None, labels: list[str],
              categories: list[dict[str, Any]], criteria: list[dict[str, Any]], findings: Findings,
              coverage: Coverage, gaps: list[str], missing: list[str], note: str | None, deviations: list[str],
              gates: Sequence[str] = ()) -> dict[str, Any]:
    decision, reason = decide(findings, missing, gaps, gates)
    report = {
        "tool": TOOL, "mode": mode, "editorial_percent": None if raw is None else math.floor(raw),
        "raw_total": None if raw is None else _num(raw), "raw_total_exact": None if raw is None else str(raw),
        "max_possible": max_possible, "labels": labels, "categories": categories, "criteria": criteria,
        "coverage": {key: None if pair is None else {"reviewed": pair[0], "total": pair[1]}
                     for key, pair in coverage.items()},
        "open_findings": findings, "gates": list(gates), "missing_targets": missing, "evidence_gaps": gaps,
        "decision": decision, "decision_reason": reason, "decision_note": note,
        "deviations": deviations, "notes": list(FIXED_NOTES),
    }
    return {**report, "cover_line": cover_line(report)}


def _criterion_row(item: Criterion) -> dict[str, Any]:
    return {**asdict(item), "category": item.code[0], "weight": item.weight, "status_tr": STATUS_TR[item.status],
            "ratio": _num(item.ratio), "subscore": _num(item.weight * item.ratio)}


def _category_row(cat: str, score: Fraction) -> dict[str, Any]:
    return {"code": cat, "name": CATEGORY_NAMES[cat], "weight": CATEGORY_WEIGHTS[cat],
            "score": _num(score), "score_exact": str(score)}


def criteria_report(criteria: tuple[Criterion, ...], findings: Findings, linked: frozenset[str],
                    coverage: Coverage) -> dict[str, Any]:
    per_cat = {cat: sum((c.weight * c.ratio for c in criteria if c.code[0] == cat), Fraction(0))
               for cat in CATEGORY_WEIGHTS}
    effects = [effect for effect in (classify(c, linked) for c in criteria) if effect]
    kinds = {kind: [text for k, text in effects if k == kind] for kind in ("unmeasured", "target", "gate", "gap")}
    partial_cov = any(pair is not None and pair[0] < pair[1] for pair in coverage.values())
    separate = any(c.status == "separate_stage" for c in criteria)  # E4 olculmedi: yuzde alt sinirdir
    excluded = [c for c in criteria if c.status == "not_applicable" and c.code not in TARGET_DENOMINATORS]
    labels = ([LABEL_PARTIAL] if kinds["unmeasured"] or partial_cov or separate else []) + (
        [LABEL_NOT_FINAL] if any(c.status == "not_applicable" for c in criteria) else [])
    return _assemble(
        mode="criteria", raw=sum(per_cat.values(), Fraction(0)),
        max_possible=100 - sum(c.weight for c in excluded), labels=labels,
        categories=[_category_row(cat, score) for cat, score in per_cat.items()],
        criteria=[_criterion_row(c) for c in criteria], findings=findings, coverage=coverage,
        gaps=kinds["unmeasured"] + kinds["gap"] + coverage_gaps(coverage), missing=kinds["target"],
        note=NOTE_SEPARATE if separate else None, deviations=[DEVIATION_E4] if separate else [],
        gates=tuple(kinds["gate"]))


def category_report(scores: dict[str, Fraction], findings: Findings, coverage: Coverage) -> dict[str, Any]:
    gaps = ["alt ölçüt dökümü yok (kategori toplamı modu): 25 ölçüt pay/paydası doğrulanamadı"]
    return _assemble(
        mode="categories", raw=sum(scores.values(), Fraction(0)), max_possible=100, labels=[LABEL_CATEGORY],
        categories=[_category_row(cat, score) for cat, score in scores.items()], criteria=[],
        findings=findings, coverage=coverage, gaps=gaps + coverage_gaps(coverage), missing=[],
        note=NOTE_SEPARATE, deviations=[DEVIATION_CATEGORY])


def build_report(data: Any) -> dict[str, Any]:
    """Saf hesap: girdi sozlugunu degistirmez, ayni girdiye ayni raporu verir."""
    if not isinstance(data, dict):
        raise InputError("girdi kökü JSON nesnesi olmalı")
    findings, linked = parse_findings(data.get("findings"))
    coverage = parse_coverage(data.get("coverage"))
    inventory = data.get("inventory_available", True)
    if not isinstance(inventory, bool):
        raise InputError("inventory_available true/false olmalı")
    if not inventory:
        return _assemble(mode="not_measured", raw=None, max_possible=None, labels=[], categories=[], criteria=[],
                         findings=findings, coverage=coverage, gaps=["envanter çıkarılamadı: yüzde ÖLÇÜLEMEDİ"],
                         missing=[], note=None, deviations=[])
    if ("criteria" in data) == ("categories" in data):
        raise InputError("girdi 'criteria' (25 alt ölçüt) VEYA 'categories' (5 kategori) içermeli; ikisi birden değil")
    if "criteria" in data:
        return criteria_report(parse_criteria(data["criteria"]), findings, linked, coverage)
    return category_report(parse_categories(data["categories"]), findings, coverage)


def _oneline(text: Any) -> str:  # gerekce/not icindeki satir sonlari Markdown satirini bolmesin
    return " ".join(str(text).splitlines())


def _fmt(value: Any) -> str:
    if value is None:
        return "—"
    if isinstance(value, float):
        return f"{value:.4f}".rstrip("0").rstrip(".")
    return _oneline(value).replace("|", "\\|")


def render_markdown(report: dict[str, Any]) -> str:
    raw, names = report["raw_total"], {"P0": "Açık P0", "P1": "Açık P1", "P2": "P2 öneri"}
    findings = " | ".join(f"{names[p]}: {len(ids)}" + (f" ({', '.join(ids)})" if ids else "")
                          for p, ids in report["open_findings"].items())
    lines = [report["cover_line"], _oneline(findings), "",
             f"- Ham toplam: {_fmt(raw)} ({report['raw_total_exact']}) / en çok {report['max_possible']}; "
             "gösterilen yüzde aşağı yuvarlanır." if raw is not None else "- Envanter yok: hesap tablosu üretilmedi.",
             f"- Etiketler: {', '.join(report['labels']) or 'yok'}",
             f"- Karar gerekçesi: {_oneline(report['decision_reason'])}", ""]
    if report["criteria"]:
        lines += ["## Hesap tablosu (25 alt ölçüt)", "", "| Kod | Ağırlık | Geçen | Payda | Oran | Alt puan | Durum | "
                  "Gerekçe / not |", "|---|---|---|---|---|---|---|---|"]
        for r in report["criteria"]:
            cells = (r["code"], r["weight"], r["passed"], r["required"], r["ratio"], r["subscore"], r["status_tr"],
                     "; ".join(part for part in (r["reason"], r["note"]) if part))
            lines.append("| " + " | ".join(_fmt(cell) for cell in cells) + " |")
        lines += [""]
    if report["categories"]:
        lines += ["## Kategori toplamları", "", "| Kat. | Ad | Ağırlık | Puan |", "|---|---|---|---|"]
        lines += [f"| {c['code']} | {c['name']} | {c['weight']} | {_fmt(c['score'])} |" for c in report["categories"]]
        lines += [""]
    for title, key in (("P0 kapıları", "gates"), ("Eksik hedefler", "missing_targets"),
                       ("Kanıt boşlukları", "evidence_gaps"), ("Sapmalar", "deviations"), ("Notlar", "notes")):
        lines += [f"## {title}", "", *(f"- {_oneline(item)}" for item in report[key] or ["yok"]), ""]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    common.setup_utf8()
    parser = argparse.ArgumentParser(description="Editoryal yüzde ve karar (kontrol listesi bölüm 20).")
    parser.add_argument("--input", required=True, help="criteria.json (25 alt ölçüt veya 5 kategori)")
    parser.add_argument("--out", required=True, help="score.json (ayrıntılı rapor)")
    parser.add_argument("--format", choices=("json", "md"), default="json",
                        help="md: JSON'a ek olarak --out yanına aynı adla .md yazar")
    args = parser.parse_args(argv)
    out = Path(args.out)
    md_path = out.with_suffix(".md") if args.format == "md" else None
    try:
        if md_path is not None and out.suffix.lower() == ".md":
            raise InputError("--format md ile --out .md olamaz (JSON --out'a, Markdown yanına yazılır)")
        try:
            data = json.loads(Path(args.input).read_text(encoding="utf-8-sig"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise InputError(f"girdi okunamadı veya JSON değil: {exc}") from exc
        report = build_report(data)
    except InputError as exc:
        common.emit({"tool": TOOL, "error": str(exc)})
        return common.EXIT_USAGE
    common.write_json(out, report)
    if md_path is not None:
        md_path.write_text(render_markdown(report), encoding="utf-8")
    counts = {p.lower(): len(ids) for p, ids in report["open_findings"].items()}
    common.emit({"tool": TOOL, "mode": report["mode"], "percent": report["editorial_percent"],
                 "raw": report["raw_total"], "decision": report["decision"], "note": report["decision_note"],
                 "labels": report["labels"], **counts, "gates": len(report["gates"]),
                 "missing_targets": len(report["missing_targets"]), "gaps": len(report["evidence_gaps"]),
                 "out": str(out), "md": None if md_path is None else str(md_path)})
    return common.EXIT_OK if report["decision"] == DECISION_READY else common.EXIT_FINDINGS


if __name__ == "__main__":
    sys.exit(main())
