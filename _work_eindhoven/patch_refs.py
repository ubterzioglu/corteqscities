import io

for p, pairs in [
    ('answers_t12.json', [
        ('["wiki-eindhoven-nl","gemeente-sport"]', '["wiki-eindhoven-nl","gemeente-fietsen"]'),
        ('["gemeente-sport","wiki-eindhoven-nl"]', '["gemeente-meedoenbijdrage","wiki-eindhoven-nl"]'),
        ('["effenaar","cafe-wilhelmina"]', '["effenaar","natlab"]'),
    ]),
    ('answers_t9.json', [
        ('["jeugdfonds","gemeente-meedoenbijdrage","gemeente-sport"]', '["jeugdfonds","gemeente-meedoenbijdrage"]'),
        ('["gemeente-meedoenbijdrage","gemeente-sport"]', '["gemeente-meedoenbijdrage"]'),
    ]),
]:
    s = open(p, encoding='utf-8').read()
    for a, b in pairs:
        s = s.replace(a, b)
    open(p, 'w', encoding='utf-8').write(s)
    print('patched', p)
