s = open('answers_t12.json', encoding='utf-8').read()
s = s.replace('["wiki-eindhoven-nl","effenaar","cafe-wilhelmina"]', '["wiki-eindhoven-nl","effenaar"]')
open('answers_t12.json', 'w', encoding='utf-8').write(s)

for p in ['answers_t6.json', 'answers_t8.json']:
    s = open(p, encoding='utf-8').read()
    s = s.replace('"rijksoverheid-minimumloon-qa"', '"rijksoverheid-minimumloon"')
    open(p, 'w', encoding='utf-8').write(s)
    print('patched', p)
