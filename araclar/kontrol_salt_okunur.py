"""Corteqs v7 doğrulayıcıyı SALT OKUNUR çalıştırır (paket klasörüne dosya yazmaz).
Kullanım (araclar/ içinden):  python3 kontrol_salt_okunur.py <excel.xlsx> <paket_klasoru>
Not: Resmî okuyucu tekrarlı liste hücresinde (ör. source_ids) hata verir; burada tekrarlar atılıp sayılır ve raporlanır."""
import sys, collections
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'arac'))
import core.content_delivery.delivery_values as dv
orig = dv.parse_list; bad = []
def tolerant(value, sep):
    try: return orig(value, sep)
    except ValueError:
        bad.append(str(value)[:100]); out = []
        [out.append(i) for i in (x.strip() for x in str(value).split(sep)) if i and i not in out]; return out
dv.parse_list = tolerant; dv.PARSERS['id_list'] = lambda v: tolerant(v, ';')
from read_delivery_v7 import read
from delivery_tools import audit
from v7_validation import validate_files
wb = Path(sys.argv[1]); root = Path(sys.argv[2]).resolve()
data, prov, arch = read(wb)
st = validate_files(data, assets_root=root)
media = audit(root, data['photos'], prov, require_new_chain=True)
c = lambda m: m.split(':')[0]
print('SAYILAR', st['counts'])
print('tekrarlı liste hücresi:', len(bad))
print('YAPI hata', len(st['errors']), 'uyarı', len(st['warnings']))
print(' hata sınıfları', collections.Counter(map(c, st['errors'])).most_common())
print('MEDYA yapısal geçti:', media.get('structural_passed'), 'hata', len(media.get('errors', [])))
print('teknik tamam:', media.get('structural_passed') and not st['errors'])
