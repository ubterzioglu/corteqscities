import json, re, unicodedata, importlib.util

spec = importlib.util.spec_from_file_location('sel', 'select_photos.py')
# doğrudan dosyayı yamalamak yerine seçimi tekrar çalıştıracağız; burada sadece yamalar:
src = open('select_photos.py', encoding='utf-8').read()

src = src.replace(
"""def bad_file(x):
    t = x['title'].lower()
    return 'cropped logo' in t or t.endswith('.png') and 'kaart' in t""",
"""EXCLUDE_KW = {
 'genneper-parken': ['ijssportcentrum', 'indoor sportcentrum', 'tongelreep', 'high tech'],
}

def bad_file(x, slug=None):
    t = x['title'].lower()
    if 'cropped logo' in t:
        return True
    if t.endswith('.png'):
        return True
    for k in EXCLUDE_KW.get(slug or '', []):
        if k in t:
            return True
    return False""")

src = src.replace("def take(pool, kws, n, title_only=False):",
                  "def take(pool, kws, n, title_only=False, slug=None):")
src = src.replace("scored = [x for x in pool if match(x, kws, title_only) and not bad_file(x)]",
                  "scored = [x for x in pool if match(x, kws, title_only) and not bad_file(x, slug)]")
src = src.replace("base = re.sub(r'\\s*\\(\\d+\\)', '', x['title'])",
                  "base = ' '.join(norm(x['title']).split()[:5])")
src = src.replace("pick = take(p.get('usable', []), kws, 1, tonly)",
                  "pick = take(p.get('usable', []), kws, 1, tonly, cid)")
src = src.replace("got = take(p.get('usable', []), kws, 1)",
                  "got = take(p.get('usable', []), kws, 1, False, slug)")
src = src.replace("picks = take(pool, kws, target, slug in TITLE_ONLY)",
                  "picks = take(pool, kws, target, slug in TITLE_ONLY, slug)")
# kapak-doga önceliği: Autumn Karpendonkse
src = src.replace("('kapak-doga', ['kapak-dogal', 'mah-karpen2', 'karpendonkse-plas'], ['autumn karpendonkse', 'karpendonkse plas', 'genneper parken'], 'Şehrin yeşil yüzü', False),",
                  "('kapak-doga', ['kapak-dogal'], ['autumn karpendonkse'], 'Şehrin yeşil yüzü: Karpendonkse Plas', False),")
open('select_photos.py', 'w', encoding='utf-8').write(src)
print('patched select_photos.py')
