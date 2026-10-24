"""SEHIR_DENETIM_CHECKLIST.pdf metninden K01-K120'yi cikarir, yurutucu/oncelik/kapi atamasini ekler,
checks.yaml uretir. Kullanim: python -I build_checks_yaml.py <checklist.txt> <out.yaml>"""
import json
import re
import sys
from collections import Counter

# id -> (exec, sev, phase)   exec: S=script L=LLM+kaynak V=gorsel E=ortam(Drive/onizleme) M=surec/rapor
# phase: uretimde kapinin/kanitin uretildigi faz; "-" = yalniz denetim (ortam gerektirir)
A = {
 1:("E","P1","-"), 2:("S","P1","intake"), 3:("E","P1","-"), 4:("S","P1","deliver"), 5:("S","P2","deliver"),
 6:("M","-","intake"), 7:("M","-","intake"), 8:("S","P1","assemble"), 9:("S","P1","assemble"),
 10:("S","P1","assemble"), 11:("S","P1","assemble"), 12:("S","P1","assemble"), 13:("S","P1","assemble"),
 14:("S","P1","assemble"), 15:("S","P0","assemble"), 16:("S","P1","assemble"), 17:("S","P1","assemble"),
 18:("L","P1","answers"), 19:("L","P1","answers"), 20:("L","P1","places"), 21:("S","P1","assemble"),
 22:("S","P1","photos"), 23:("S","P1","photos"), 24:("S","P1","assemble"), 25:("L","P1","answers"),
 26:("L","P1","answers"), 27:("S","P1","answers"), 28:("L","P1","answers"), 29:("L","P0","answers"),
 30:("S","P1","answers"), 31:("L","P0","answers"), 32:("L","P2","answers"), 33:("S","P1","answers"),
 34:("L","P0","sources"), 35:("L","P0","sources"), 36:("L","P0","sources"), 37:("L","P0","answers"),
 38:("L","P1","places"), 39:("L","P1","places"), 40:("L","P1","answers"), 41:("L","P0","sources"),
 42:("L","P0","places"), 43:("S","P1","places"), 44:("L","P1","places"), 45:("S","P1","assemble"),
 46:("S","P1","places"), 47:("L","P1","places"), 48:("L","P2","answers"), 49:("S","P1","assemble"),
 50:("S","P1","sources"), 51:("L","P1","sources"), 52:("S","P2","sources"), 53:("L","P1","sources"),
 54:("L","P1","places"), 55:("L","P1","places"), 56:("S","P2","deliver"), 57:("S","P0","photos"),
 58:("S","P0","photos"), 59:("V","P0","photos"), 60:("V","P0","photos"), 61:("V","P0","photos"),
 62:("V","P0","photos"), 63:("S","P1","photos"), 64:("S","P0","photos"), 65:("V","P1","photos"),
 66:("S","P1","photos"), 67:("S","P0","photos"), 68:("S","P0","photos"), 69:("S","P1","photos"),
 70:("S","P1","photos"), 71:("L","P0","photos"), 72:("L","P0","photos"), 73:("S","P1","photos"),
 74:("V","P0","photos"), 75:("S","P1","photos"), 76:("S","P0","photos"), 77:("S","P1","assemble"),
 78:("S","P1","assemble"), 79:("S","P1","assemble"), 80:("S","P0","photos"), 81:("S","P1","photos"),
 82:("S","P1","deliver"), 83:("S","P1","deliver"), 84:("S","P1","deliver"), 85:("S","P1","assemble"),
 86:("S","P1","assemble"), 87:("S","P1","assemble"), 88:("S","P1","assemble"), 89:("S","P1","assemble"),
 90:("L","P0","sources"), 91:("L","P1","assemble"), 92:("E","P1","-"), 93:("E","P1","-"),
 94:("E","P1","-"), 95:("S","P0","assemble"), 96:("M","-","assemble"), 97:("S","P0","assemble"),
 98:("M","-","deliver"), 99:("S","P1","assemble"), 100:("S","-","deliver"), 101:("M","-","deliver"),
 102:("M","-","deliver"), 103:("E","P1","-"), 104:("S","P1","answers"), 105:("V","P1","photos"),
 106:("S","P0","photos"), 107:("S","P1","photos"), 108:("L","P1","places"), 109:("E","P1","-"),
 110:("E","P1","-"), 111:("E","P1","-"), 112:("E","P1","-"), 113:("M","P1","intake"),
 114:("S","P0","photos"), 115:("S","-","deliver"), 116:("M","-","deliver"), 117:("M","-","deliver"),
 118:("S","P1","assemble"), 119:("M","-","deliver"), 120:("M","-","deliver"),
}
# yalniz belirli ulke/sehirde gecerli kontroller
CONDITIONAL = {36: "D7/D8 kismi yalniz ulke=PT icin; diger ulkelerde bu kisim UYGULANMAZ, o ulkenin vize kurallari K35 ile denetlenir"}

# Kapsam disi kontroller (varsayilan scope = local: city-pack/city-audit bunlari calistirir)
#  drive-manual : Drive'a yukleme/bulut dogrulama Baris tarafindan manuel yapilir; skill calistirmaz, token harcamaz
#  preview-later: web onizleme dosyalar yuklendikten sonra yapilir; ileride ayri skill (city-preview) olabilir
SCOPE = {
    1: ("drive-manual", "Drive kok/klasor kimligi"),
    3: ("drive-manual", "Drive-yerel hash karsilastirmasi"),
    109: ("drive-manual", "Drive kimlikleri ve uc klasor"),
    110: ("drive-manual", "Bulut teslim dogrulamasi"),
    92: ("preview-later", "Masaustu/mobil gorunum"),
    93: ("preview-later", "Uctan uca kullanici akisi"),
    94: ("preview-later", "Web fotograf atfi"),
    103: ("preview-later", "Fotograf ustu uyari bandi (onizlemede)"),
    111: ("preview-later", "Yerel onizleme ile UAT/yonetim ayrimi"),
    112: ("preview-later", "Islevleri yeni kullanici verisiyle sinama"),
}

NOISE = re.compile(r"^(Corteqs · Şehir denetim kılavuzu|\d+$|120 KONTROL|===== PAGE)")
SECT = re.compile(r"^(\d\d) \| ")


def clean(block):
    out = []
    for ln in block.split("\n"):
        if SECT.match(ln):
            break
        if NOISE.match(ln):
            continue
        out.append(ln)
    return " ".join(x.strip() for x in out if x.strip())


def field(txt, name, nxt):
    m = re.search(name + r": (.*?)(?= " + nxt + r": |$)", txt)
    return m.group(1).strip() if m else ""


def main(src, dst):
    text = open(src, encoding="utf-8").read()
    sec_of = {}
    cur = 0
    for ln in text.split("\n"):
        m = SECT.match(ln)
        if m:
            cur = int(m.group(1))
        k = re.match(r"\[K(\d{2,3})\]", ln)
        if k:
            sec_of[int(k.group(1))] = cur
    parts = re.split(r"(?m)^\[K(\d{2,3})\] ", text)
    checks = {}
    for i in range(1, len(parts), 2):
        n = int(parts[i])
        body = parts[i + 1]
        first, _, rest = body.partition("\n")
        txt = clean(rest)
        checks[n] = {
            "title": first.strip(),
            "how": field(txt, "Nasıl", "Geçme"),
            "pass": field(txt, "Geçme", "Kanıt"),
            "evidence": re.sub(r"\s+", " ", txt.split("Kanıt:", 1)[1]).strip() if "Kanıt:" in txt else "",
        }
    missing = [n for n in range(1, 121) if n not in checks]
    assert not missing, f"cikarilamayan kontroller: {missing}"
    assert set(A) == set(range(1, 121)), "atama tablosu 120 kontrolu kapsamiyor"

    lines = [
        "# Corteqs sehir denetim kontrolleri (K01-K120) - makine okunur ozet",
        "# Kaynak: SEHIR_DENETIM_CHECKLIST.pdf (kilavuz 2.0, 22 Ekim 2026). exec/sev/phase atamalari TASLAK; Atinc onayi gerekir.",
        "# exec: S=script, L=LLM+kaynak, V=gorsel, E=ortam (Drive/onizleme/UAT), M=surec/rapor",
        "# sev: P0/P1/P2 kilavuzun tanimina gore oneri; '-' = bulgu uretmeyen surec kontrolu",
        "# phase: city-pack'te kanit/kapinin uretildigi faz; '-' = yalniz denetimde (ortam gerekir)",
        "# prod: gate = uretimde script kapisi; evidence = uretim kanit uretir, denetim LLM/gorselle teyit eder; none = uretimde yok",
        "checks:",
    ]
    for n in range(1, 121):
        ex, sev, ph = A[n]
        prod = "gate" if (ex == "S" and ph != "-") else ("evidence" if ex in "LV" and ph != "-" else "none")
        c = checks[n]
        lines += [
            f"- id: K{n:02d}",
            f"  sec: {sec_of[n]}",
            f"  title: {json.dumps(c['title'], ensure_ascii=False)}",
            f"  exec: {ex}",
            f"  sev: {json.dumps(sev)}",
            f"  phase: {json.dumps(ph)}",
            f"  prod: {prod}",
        ]
        if n in SCOPE:
            lines.append(f"  scope: {SCOPE[n][0]}")
        if n in CONDITIONAL:
            lines.append(f"  only_if: {json.dumps(CONDITIONAL[n], ensure_ascii=False)}")
        if ex in "LV":  # LLM/gorsel kontrollerde gecme kosulu gerekli; script kontrolleri kodda yasar
            lines.append(f"  pass: {json.dumps(c['pass'], ensure_ascii=False)}")
    open(dst, "w", encoding="utf-8").write("\n".join(lines) + "\n")

    ex_c = Counter(a[0] for a in A.values())
    sev_c = Counter(a[1] for a in A.values())
    prod_c = Counter(("gate" if (a[0] == "S" and a[2] != "-") else ("evidence" if a[0] in "LV" and a[2] != "-" else "none")) for a in A.values())
    print("exec:", dict(ex_c))
    print("sev:", dict(sev_c))
    print("prod:", dict(prod_c))
    print("faz dagilimi:", dict(Counter(a[2] for a in A.values())))
    print("kapsam:", dict(Counter(v[0] for v in SCOPE.values())), "| yerel (local):", 120 - len(SCOPE))
    local_e = [n for n in range(1, 121) if A[n][0] == "E" and n not in SCOPE]
    assert not local_e, f"kapsami atanmamis ortam kontrolu: {local_e}"
    print("bos pass (L/V):", [n for n in range(1, 121) if A[n][0] in "LV" and not checks[n]["pass"]])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
