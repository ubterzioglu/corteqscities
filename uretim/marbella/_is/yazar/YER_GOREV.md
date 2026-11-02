# Yer ve sayfa yazarı görevi — Marbella (CITY-080)

Önce oku (bu sırayla): `/home/user/corteqscities/.claude/skills/city-pack/agents/ortak-kurallar.md`, `/home/user/corteqscities/.claude/skills/city-pack/agents/yer-yazari.md`, `/home/user/corteqscities/.claude/skills/city-pack/agents/mekan-yazari.md`. Alan anahtarları ve uzunluklar: `/home/user/corteqscities/.claude/skills/city-pack/references/contract_digest.md` §2. Yol ve biçimde ortak kurallar ve yer-yazari.md esastır; yalnız **kabuk farkı** aşağıda.

## Değerler
- `<city_id>` = `marbella`; şehir: Marbella, İspanya (Endülüs, Málaga ili, Costa del Sol; belediye: Marbella kenti, San Pedro Alcántara, Nueva Andalucía, Puerto Banús, Marbella Este/Las Chapas, Guadalmina)
- `<WORK>` = `/home/user/corteqscities/uretim/marbella`
- `<TK>` = `/home/user/corteqscities/corteqs-skills/toolkit/scripts`
- `<PY>` = `/home/user/venv/bin/python`
- `<tarih>` = `2026-10-28`; `<bbox>` = `36.40,36.62,-5.18,-4.62`
- **Hitap: `sen`** (okura 2. tekil; "siz" yok; bir kayıtta biçim karışmaz). Sözlük ve kapak/konu metinleri kişisiz olabilir.

## Kabuk (bu oturum Linux; ortak kurallardaki PowerShell yerine)
- PowerShell yok. Komutları Bash aracıyla, **her çağrıda tek komut**, tam yolla çalıştır; `cd`, `&&`, `;`, boru ve heredoc kullanma. Ortamı komutun başına ver: `PYTHONDONTWRITEBYTECODE=1 PYTHONUTF8=1 /home/user/venv/bin/python <TK>/add_sources.py ...`.
- Python işi için önce `.py` dosyasını Write ile `<TMP>` altına yaz, sonra `/home/user/venv/bin/python -I <TMP>/<dosya>.py` ile çalıştır. Klasör açmaya gerek yok (Write açar). Yollarda `/`.
- Kendi kontrolün (ortak kurallar §8): `/home/user/venv/bin/python <TK>/merge_package.py <WORK>/_is --city-id marbella --bbox=36.40,36.62,-5.18,-4.62 --data-out <TMP>/birlesik --out <TMP>/birlestir_rapor.json` (--data-out ve --out ŞART). Kendi parçanı ilgilendiren bulgu 0 olmalı.

## Kaynaklar
- Kaynak dizini: `<WORK>/_is/kaynak_dizini.jsonl` (`source_id`, `url`, `title`, `publisher`, `text_file`; `text_file` `<WORK>/_is/` altına göre göreli). Önce buradaki kaynakları kullan (yanıt kartlarının kaynakları dahil).
- Yeni kaynak gerekirse ortak kurallar §4 ile `add_sources` (klasör `snap_<gorev>-yazar<sira>`; Glob ile boş sırayı bul), **görev mesajındaki üst sınır kadar**. Yalnız resmî yayıncının derin sayfası; turizm portalı (turismo.marbella.es) ücret/saat/işlem kuralı kaynağı değildir; ticari site yok.
- **Erişim:** sede.marbella.es, malaga.es, sede.administracionespublicas.gob.es, mivau.gob.es, inclusion.gob.es, hidralia.es, puertobanus.com, museosdeandalucia.es, mgec.es, puertodeandalucia.es ERİŞİLEMEZ; hcs.es kopyası bozuk (gzip): deneme.
- Bellekten bilgi yok; her değişken iddia defterde (`<WORK>/_is/claims/<gorev>.jsonl`) birebir alıntıyla.

## Sınırlar
- **Alt ajan başlatma.** Geçici dosyalar yalnız görev mesajındaki `<TMP>` klasöründe. Yalnız görev mesajındaki dosyalara yaz.
- Kayıtları parça parça yaz: her 4–5 kayıtta bir dosyaya ekle (ana döngü 10 dk büyümeyen dosyayı takılmış sayar).
- Bütçe: görev mesajındaki süre ve araç çağrısı. Dolunca yazdıklarını tutarlı bırak ve dön.

## Dönüş (tek satır JSON; sayıları dosyadan say)
`{"gorev":"<gorev>","kayit":{"<Sekme>":N,...},"claims":N,"new_sources":N,"open":[...],"gaps":[...]}`
