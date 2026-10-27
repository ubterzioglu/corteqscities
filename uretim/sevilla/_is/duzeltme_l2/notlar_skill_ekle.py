"""_is/notlar_skill.md'ye bu düzeltme turunda (L2 sonrası d11/d12) görülen skill/araç sorunlarını ekler (kural 14).
Aynı satır zaten varsa eklemez.

Kullanım: python -I -X utf8 notlar_skill_ekle.py <WORK_is>
"""
import sys
from pathlib import Path

f = Path(sys.argv[1]) / "notlar_skill.md"
SATIRLAR = [
    "- 2026-10-27 | düzeltme (L2 sonrası d12) | fetch_snapshot PDF'ten metin çıkarmıyor (pypdf/fitz yok, ham .pdf saklanıyor): TUSSAM 2026 tarifesi (BOP Sevilla PDF'i) ve Cartuja ZBE ilanı kaynak yapılamadı, kartlarda tutar/rejim yok. | fetch_snapshot'a pypdf ile PDF metin çıkarma; add_sources must_contain'i bu metinde arasın.",
    "- 2026-10-27 | düzeltme (L2 sonrası d12) | merge_package ve add_sources 'python -I' ile 'No module named common' veriyor; editör -I'sız çalıştırdı. | Script'ler kendi klasörünü sys.path'e eklesin ya da ortak kurallar §8 komutu -I'sız yazılsın.",
    "- 2026-10-27 | düzeltme (L2 sonrası d12) | Kaynak kapasitesi (515 > 500): merge_package sayımı Bağlantılar adreslerini de sayıyor; yalnız source_ids'e bakan boşaltma betikleri 2 kaynak boşalttı ama sayım düşmedi. Editörler 23 kaynağı (iddia taşıyarak ya da ana olmayan ayrıntıyı çıkararak) boşalttı; mekân özetlerinden 25 ayrıntı iddiası çıktı. | Kapasite aracı (source_ids ∪ bağlantı adresi ∪ iddia kaynağı) araç kutusuna; editör/yazar eklemeleri baştan net 0 kotasıyla.",
    "- 2026-10-27 | düzeltme (L2 sonrası d12) | Açık-mı kapısı son turlardan beri çalıştırılmamıştı: 2 mekân taranmamış (Fibes, yeni Bermejales), 5 mekânın kanıt kaynağı önceki turlarda karttan çıkarılmış (kaynak_izi_yok), 3 'kartta belirt' kartında tarihli not yok. | Her düzeltme turunun KUR bloğuna acik_mi.py; kaynak boşaltma işi açık-mı kanıt kaynaklarını korusun.",
    "- 2026-10-27 | denetim (L2 sonrası d12) | Workflow betiğinde String.raw içinde '\\${' kaçış oldu, görev mesajındaki girdi yolu '${p}-d12_kartlar.jsonl' olarak kaldı; 7 denetçiden 4'ü çalışmadı (~10 dk kayıp). | Görev şablonlarında yol birleştirme [klasör, p + '…'].join('\\\\') ile; String.raw içinde '\\' ardından '${' yazılmaz.",
    "- 2026-10-26 | düzeltme (L2 sonrası d11) | Workflow ajanına SendMessage göndermek ajanı ikinci kez başlattı (aynı kimlik); durdurma ikisini birden kesti (~7 dk kayıp). | Workflow ajanına mesaj gönderilmez; düzeltme gerekirse yeni workflow.",
]
var = f.read_text(encoding="utf-8") if f.exists() else ""
yeni = [s for s in SATIRLAR if s not in var]
with f.open("a", encoding="utf-8") as h:
    for s in yeni:
        h.write(("" if var.endswith("\n") or not var else "\n") + s + "\n")
        var += s + "\n"
print({"eklenen": len(yeni)})
