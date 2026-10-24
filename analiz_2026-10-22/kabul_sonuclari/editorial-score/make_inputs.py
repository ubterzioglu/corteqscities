"""Kabul girdilerini uretir ve editorial_score CLI'ini her biri icin calistirir (yalniz bu klasore yazar)."""
import ast
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOLKIT = Path(r"C:\temp_private\corteqs\0000_newera\corteqs-skills\toolkit")
SCRIPT = TOOLKIT / "scripts" / "editorial_score.py"
FIXED = {"A1": 240, "B1": 120, "B2": 16, "B3": 12, "B4": 60, "C1": 250, "E3": 23, "E5": 5}
CODES = [f"{c}{i}" for c in "ABCDE" for i in range(1, 6)]
COV = {"cards": [240, 240], "photos": [250, 250], "critical_claims": [40, 40]}


def crit(code, passed=None, required=None, status="ok", reason=""):
    req = FIXED.get(code, 10) if required is None else required
    return {"code": code, "passed": req if passed is None else passed, "required": req, "status": status, "reason": reason}


def rows(**over):
    return [over.get(c, crit(c)) for c in CODES]


pdf_over = {f"A{i}": crit(f"A{i}", 4, 5) for i in range(2, 6)}
pdf_over["A1"] = crit("A1", 192)
pdf_over.update({c: crit(c, 0) for c in ("B5", "C4", "C5", "D4", "D5", "E4", "E5")})
edge_709 = {f"E{i}": crit(f"E{i}", status="not_checked", reason="önizleme yok") for i in range(1, 6)}
edge_709.update({f"D{i}": crit(f"D{i}", 0) for i in range(1, 6)})
edge_709.update(C2=crit("C2", 0), B1=crit("B1", 117))

CASES = {
    "1a_pdf_ornek_kategori": {"categories": {"A": 28, "B": 16, "C": 12, "D": 9, "E": 6},
                              "findings": [{"id": "YANLIS-KAPAK", "priority": "P0"}], "coverage": COV},
    "1b_pdf_ornek_olcut": {"criteria": rows(**pdf_over), "findings": [{"id": "YANLIS-KAPAK", "priority": "P0"}],
                           "coverage": COV},
    "2_codex_eindhoven_kategori": {"categories": {"A": 18, "B": 11, "C": 14, "D": 9, "E": 3}, "findings": []},
    "3a_oran_kirpma": {"criteria": rows(A1=crit("A1", 300), A2=crit("A2", 12, 10)), "coverage": COV},
    "3b_payda_sifir": {"criteria": rows(B5=crit("B5", 0, 0)), "coverage": COV},
    "3c_tum_kategori_uygulanmaz": {"criteria": rows(**{f"E{i}": crit(f"E{i}", status="not_applicable",
                                                                     reason="gerekçe: örnek") for i in range(1, 6)}),
                                   "coverage": COV},
    "3d_ham_70_9": {"criteria": rows(**edge_709), "coverage": COV},
    "3e_e4_ayri_asama": {"criteria": rows(E4=crit("E4", status="separate_stage", reason="önizleme ayrı aşama")),
                         "coverage": COV},
    "3f_envanter_yok": {"inventory_available": False},
}


def long_functions(path: Path, limit: int = 50) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return [f"{n.name}:{n.end_lineno - n.lineno + 1}" for n in ast.walk(tree)
            if isinstance(n, ast.FunctionDef) and n.end_lineno - n.lineno + 1 >= limit]


def main():
    print("uzun_fonksiyonlar:", long_functions(SCRIPT))
    for name, data in CASES.items():
        src = HERE / f"{name}.input.json"
        src.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        out = HERE / f"{name}.score.json"
        proc = subprocess.run([sys.executable, str(SCRIPT), "--input", str(src), "--out", str(out), "--format", "md"],
                              capture_output=True, text=True, encoding="utf-8")
        summary = json.loads(proc.stdout)
        print(f"{name}: exit={proc.returncode} percent={summary['percent']} raw={summary['raw']} "
              f"decision={summary['decision']} note={summary['note']} labels={summary['labels']}")


if __name__ == "__main__":
    main()
